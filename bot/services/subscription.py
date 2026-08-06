from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from database.db import get_db
from database.models import PlanDoc, SubscriptionDoc, TransactionDoc, UserDoc, now_utc
from utils.helpers import to_small_caps

logger = logging.getLogger(__name__)


# ── User ─────────────────────────────────────────────────────────────────────

async def get_or_create_user(user_id: int, first_name: str, username: Optional[str] = None, last_name: Optional[str] = None) -> UserDoc:
    db = get_db()
    user = await db.users.find_one({"user_id": user_id})
    if user is None:
        user: UserDoc = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "wallet_balance": 0.0,
            "referral_points": 0,
            "auto_renew": False,
            "joined_at": now_utc(),
            "is_banned": False,
        }
        await db.users.insert_one(dict(user))
        logger.info("New user registered: %d", user_id)
    else:
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"first_name": first_name, "username": username}},
        )
    return user


async def get_user(user_id: int) -> Optional[UserDoc]:
    db = get_db()
    return await db.users.find_one({"user_id": user_id})


async def get_all_users() -> list[UserDoc]:
    db = get_db()
    cursor = db.users.find({}, {"_id": 0})
    return await cursor.to_list(length=None)


async def get_user_count() -> int:
    return await get_db().users.count_documents({})


async def get_paid_user_count() -> int:
    """Count users with a currently active subscription."""
    now = now_utc()
    return await get_db().subscriptions.count_documents({"is_active": True, "end_date": {"$gt": now}})


async def get_blocked_user_count() -> int:
    """Count users who have blocked the bot."""
    return await get_db().users.count_documents({"is_blocked": True})


async def mark_user_blocked(user_id: int) -> None:
    await get_db().users.update_one({"user_id": user_id}, {"$set": {"is_blocked": True}})


async def mark_user_unblocked(user_id: int) -> None:
    await get_db().users.update_one({"user_id": user_id}, {"$set": {"is_blocked": False}})


# ── Plans ─────────────────────────────────────────────────────────────────────

async def get_active_plans() -> list[PlanDoc]:
    db = get_db()
    cursor = db.plans.find({"is_active": True}, {"_id": 0})
    return await cursor.to_list(length=None)


async def get_plan(name: str) -> Optional[PlanDoc]:
    return await get_db().plans.find_one({"name": name}, {"_id": 0})


async def create_plan(
    name: str,
    display_name: str,
    description: str,
    demo_link: str,
    payment_proof_required: bool,
    durations: list[dict],
    channels: list[str],
) -> None:
    db = get_db()
    plan = {
        "name": name,
        "display_name": display_name,
        "description": description,
        "demo_link": demo_link,
        "payment_proof_required": payment_proof_required,
        "durations": durations,
        "channels": channels,
        "is_active": True,
    }
    await db.plans.update_one({"name": name}, {"$set": plan}, upsert=True)
    logger.info("Plan created/updated: %s", name)


async def seed_default_plans() -> None:
    db = get_db()
    if await db.plans.count_documents({"is_active": True}, limit=1):
        return
    await create_plan(
        name="flix_premium",
        display_name="FLIX PREMIUM",
        description="Full access to all exclusive premium channels.",
        demo_link="",
        payment_proof_required=True,
        durations=[
            {"minutes": 43200,  "label": "1 ᴍᴏɴᴛʜ",  "price": 299.0},
            {"minutes": 129600, "label": "3 ᴍᴏɴᴛʜs", "price": 799.0},
            {"minutes": 259200, "label": "6 ᴍᴏɴᴛʜs", "price": 1499.0},
        ],
        channels=[],
    )
    logger.info("Default plan seeded")


# ── Subscriptions ─────────────────────────────────────────────────────────────

async def get_active_subscription(user_id: int) -> Optional[SubscriptionDoc]:
    """Returns the first active subscription (for renewal checks)."""
    db = get_db()
    now = now_utc()
    sub = await db.subscriptions.find_one(
        {"user_id": user_id, "is_active": True, "end_date": {"$gt": now}},
        {"_id": 0},
    )
    return sub


async def get_active_subscriptions(user_id: int) -> list[SubscriptionDoc]:
    """Returns ALL active subscriptions for a user."""
    db = get_db()
    now = now_utc()
    cursor = db.subscriptions.find(
        {"user_id": user_id, "is_active": True, "end_date": {"$gt": now}},
        {"_id": 0},
    )
    return await cursor.to_list(length=None)


async def purchase_subscription(
    user_id: int,
    plan: PlanDoc,
    duration_minutes: int,
    invite_links: list[str] | None = None,
) -> bool:
    db = get_db()
    user = await get_user(user_id)
    if user is None:
        return False

    # Find price for this duration tier
    durations = plan.get("durations") or []
    tier = next((d for d in durations if d["minutes"] == duration_minutes), None)
    if tier:
        price = tier["price"]
    elif duration_minutes == plan.get("duration_minutes"):
        price = plan.get("price", 0.0)
    else:
        return False

    balance = user.get("wallet_balance", 0.0)
    if balance < price:
        return False

    now = now_utc()

    # Check if user already has active sub for this SAME plan → extend it
    existing = await db.subscriptions.find_one(
        {"user_id": user_id, "plan_name": plan["name"], "is_active": True, "end_date": {"$gt": now}},
        {"_id": 0},
    )
    is_renewal = existing is not None

    duration_delta = timedelta(minutes=duration_minutes)
    if is_renewal:
        # Extend from existing end_date
        base = existing["end_date"]
        if base.tzinfo is None:
            base = base.replace(tzinfo=timezone.utc)
        end_date = base + duration_delta
    else:
        end_date = now + duration_delta

    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"wallet_balance": -price}},
    )

    update_fields: dict = {
        "user_id": user_id,
        "plan_name": plan["name"],
        "duration_minutes": duration_minutes,
        "price_paid": price,
        "start_date": now,
        "end_date": end_date,
        "is_active": True,
        "channels": invite_links if invite_links is not None else plan.get("channels", []),
    }

    # Each plan gets its own document; upsert by (user_id, plan_name)
    await db.subscriptions.update_one(
        {"user_id": user_id, "plan_name": plan["name"]},
        {"$set": update_fields},
        upsert=True,
    )

    txn: TransactionDoc = {
        "user_id": user_id,
        "amount": -price,
        "type": "purchase",
        "plan_name": plan["name"],
        "description": f"Purchased {plan['display_name']}",
        "created_at": now,
        "status": "completed",
    }
    await db.transactions.insert_one(dict(txn))
    logger.info("User %d purchased plan %s (%d mins)", user_id, plan["name"], duration_minutes)
    return True


# ── Transactions ──────────────────────────────────────────────────────────────

async def get_wallet_stats(user_id: int) -> tuple[float, int, float, int, float]:
    """Returns (today_amount, today_count, total_dep_amount, total_dep_count, total_spent)."""
    db = get_db()
    now = now_utc()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    today_cursor = db.transactions.find(
        {"user_id": user_id, "type": "topup", "created_at": {"$gte": today_start}}
    )
    today_txns = await today_cursor.to_list(length=None)
    today_amount = sum(t.get("amount", 0.0) for t in today_txns)
    today_count = len(today_txns)

    total_cursor = db.transactions.find({"user_id": user_id, "type": "topup"})
    total_txns = await total_cursor.to_list(length=None)
    total_dep_amount = sum(t.get("amount", 0.0) for t in total_txns)
    total_dep_count = len(total_txns)

    spent_cursor = db.transactions.find({"user_id": user_id, "type": "purchase"})
    spent_txns = await spent_cursor.to_list(length=None)
    total_spent = sum(abs(t.get("amount", 0.0)) for t in spent_txns)

    return today_amount, today_count, total_dep_amount, total_dep_count, total_spent


async def get_user_transactions(user_id: int, limit: int = 10) -> list[TransactionDoc]:
    db = get_db()
    cursor = db.transactions.find(
        {"user_id": user_id},
        {"_id": 0},
        sort=[("created_at", -1)],
    ).limit(limit)
    return await cursor.to_list(length=limit)


# ── Wallet ────────────────────────────────────────────────────────────────────

async def topup_wallet(user_id: int, amount: float, description: str = "Admin top-up") -> None:
    db = get_db()
    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"wallet_balance": amount}},
    )
    txn: TransactionDoc = {
        "user_id": user_id,
        "amount": amount,
        "type": "topup",
        "plan_name": None,
        "description": description,
        "created_at": now_utc(),
        "status": "completed",
    }
    await db.transactions.insert_one(dict(txn))


async def mark_channel_joined(user_id: int, channel_idx: int) -> None:
    """Record that the user has tapped the join button for channel at given index."""
    await get_db().subscriptions.update_one(
        {"user_id": user_id, "is_active": True},
        {"$addToSet": {"joined_channels": channel_idx}},
    )


async def deduct_wallet(user_id: int, amount: float, description: str = "Admin penalty") -> None:
    """Deduct balance from a user's wallet (penalty / correction)."""
    db = get_db()
    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"wallet_balance": -amount}},
    )
    txn: TransactionDoc = {
        "user_id": user_id,
        "amount": -amount,
        "type": "penalty",
        "plan_name": None,
        "description": description,
        "created_at": now_utc(),
        "status": "completed",
    }
    await db.transactions.insert_one(dict(txn))


# ── Auto-Renew ────────────────────────────────────────────────────────────────

async def _kick_from_channels(bot_instance, user_id: int, channels: list[str]) -> None:
    """Ban then immediately unban to kick user from each channel."""
    for ch in channels:
        try:
            chat_id: int | str = int(str(ch).strip())
        except ValueError:
            chat_id = str(ch).strip()
        try:
            await bot_instance.ban_chat_member(chat_id, user_id)
            await bot_instance.unban_chat_member(chat_id, user_id)
            logger.info("Kicked user %d from channel %s", user_id, ch)
        except Exception as e:
            logger.warning("Could not kick user %d from channel %s: %s", user_id, ch, e)


async def process_auto_renewals(bot_instance=None) -> list[dict]:
    db = get_db()
    now = now_utc()

    cursor = db.subscriptions.find({"is_active": True, "end_date": {"$lte": now}})
    expired = await cursor.to_list(length=None)

    results = []
    for sub in expired:
        user_id = sub["user_id"]
        plan_name = sub.get("plan_name")
        sub_duration_mins = sub.get("duration_minutes", 43200)

        user = await get_user(user_id)
        _plan_obj = await get_plan(plan_name) if plan_name else None
        if user is None or not user.get("auto_renew", False):
            await db.subscriptions.update_one(
                {"user_id": user_id}, {"$set": {"is_active": False}}
            )
            if bot_instance:
                plan_channel_ids = (_plan_obj or {}).get("channels", [])
                await _kick_from_channels(bot_instance, user_id, plan_channel_ids)
                plan_display = _plan_obj["display_name"] if _plan_obj else (plan_name or "Your Plan")
                try:
                    await bot_instance.send_message(
                        user_id,
                        f"<blockquote><b>⏰ {to_small_caps('Subscription Expired')}</b></blockquote>\n\n"
                        f"<b>{to_small_caps('Plan')}:</b> {to_small_caps(plan_display)}\n\n"
                        f"<blockquote>ℹ️ <i>{to_small_caps('Your premium access has ended. Renew your subscription anytime via')} /start {to_small_caps('to regain access.')} </i></blockquote>",
                        parse_mode="HTML",
                    )
                except Exception:
                    pass
            continue

        plan = await get_plan(plan_name) if plan_name else None
        if plan is None or not plan.get("is_active", False):
            await db.subscriptions.update_one(
                {"user_id": user_id}, {"$set": {"is_active": False}}
            )
            results.append({"user_id": user_id, "status": "no_plan"})
            continue

        # Find price for same duration tier
        durations = plan.get("durations") or []
        tier = next((d for d in durations if d["minutes"] == sub_duration_mins), None)
        if tier:
            price = tier["price"]
        elif sub_duration_mins == plan.get("duration_minutes"):
            price = plan.get("price", 0.0)
        elif durations:
            # Fallback: cheapest tier
            tier = min(durations, key=lambda d: d["price"])
            price = tier["price"]
            sub_duration_mins = tier["minutes"]
        else:
            await db.subscriptions.update_one(
                {"user_id": user_id}, {"$set": {"is_active": False}}
            )
            results.append({"user_id": user_id, "status": "no_plan"})
            continue

        balance = user.get("wallet_balance", 0.0)
        if balance < price:
            await db.subscriptions.update_one(
                {"user_id": user_id}, {"$set": {"is_active": False}}
            )
            if bot_instance:
                await _kick_from_channels(bot_instance, user_id, plan.get("channels", []))
            results.append({"user_id": user_id, "status": "insufficient_funds", "plan": plan, "price_paid": 0})
            logger.info("Auto-renew failed (low balance) for user %d", user_id)
        else:
            end_date = now + timedelta(minutes=sub_duration_mins)
            await db.users.update_one(
                {"user_id": user_id}, {"$inc": {"wallet_balance": -price}}
            )
            await db.subscriptions.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "plan_name": plan["name"],
                        "duration_minutes": sub_duration_mins,
                        "price_paid": price,
                        "start_date": now,
                        "end_date": end_date,
                        "is_active": True,
                    }
                },
            )
            txn: TransactionDoc = {
                "user_id": user_id,
                "amount": -price,
                "type": "purchase",
                "plan_name": plan["name"],
                "description": f"Auto-renewal: {plan['display_name']}",
                "created_at": now,
                "status": "completed",
            }
            await db.transactions.insert_one(dict(txn))
            # Notify user about auto-renewal debit
            if bot_instance:
                new_bal = (user.get("wallet_balance", 0.0) or 0.0) - price
                try:
                    await bot_instance.send_message(
                        user_id,
                        f"🔄 <b>ᴀᴜᴛᴏ-ʀᴇɴᴇᴡᴀʟ: ₹{price:.0f} ᴅᴇᴅᴜᴄᴛᴇᴅ</b>\n"
                        f"<b>ʙᴀʟᴀɴᴄᴇ: ₹{new_bal:.2f}</b>",
                        parse_mode="HTML",
                    )
                except Exception:
                    pass
            results.append({
                "user_id": user_id,
                "status": "renewed",
                "plan": plan,
                "end_date": end_date,
                "price_paid": price,
            })
            logger.info("Auto-renewed plan %s for user %d", plan["name"], user_id)

    return results


# ── Plan Management ───────────────────────────────────────────────────────────

async def delete_plan(name: str) -> None:
    """Soft-delete a plan by setting is_active=False."""
    await get_db().plans.update_one({"name": name}, {"$set": {"is_active": False}})
    logger.info("Plan deleted: %s", name)


async def update_plan_fields(name: str, fields: dict) -> None:
    """Update specific fields on a plan document."""
    await get_db().plans.update_one({"name": name}, {"$set": fields})
    logger.info("Plan %s updated: %s", name, list(fields.keys()))


# ── Settings ──────────────────────────────────────────────────────────────────

async def get_setting(key: str) -> Optional[str]:
    db = get_db()
    doc = await db.settings.find_one({"key": key})
    return doc["value"] if doc else None


async def set_setting(key: str, value: str) -> None:
    await get_db().settings.update_one(
        {"key": key},
        {"$set": {"key": key, "value": value}},
        upsert=True,
    )
