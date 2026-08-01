from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from database.db import get_db
from database.models import PlanDoc, SubscriptionDoc, TransactionDoc, UserDoc, now_utc

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
            "auto_renew": True,
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
    existing = await get_active_plans()
    if existing:
        return
    await create_plan(
        name="flix_premium",
        display_name="FLIX PREMIUM",
        description="Full access to all exclusive premium channels.",
        demo_link="",
        payment_proof_required=True,
        durations=[
            {"days": 30,  "label": "1 ᴍᴏɴᴛʜ",   "price": 299.0},
            {"days": 90,  "label": "3 ᴍᴏɴᴛʜs",  "price": 799.0},
            {"days": 180, "label": "6 ᴍᴏɴᴛʜs",  "price": 1499.0},
        ],
        channels=[],
    )
    logger.info("Default plan seeded")


# ── Subscriptions ─────────────────────────────────────────────────────────────

async def get_active_subscription(user_id: int) -> Optional[SubscriptionDoc]:
    db = get_db()
    now = now_utc()
    sub = await db.subscriptions.find_one(
        {"user_id": user_id, "is_active": True, "end_date": {"$gt": now}},
        {"_id": 0},
    )
    return sub


async def purchase_subscription(user_id: int, plan: PlanDoc, duration_days: int) -> bool:
    db = get_db()
    user = await get_user(user_id)
    if user is None:
        return False

    # Find price for this duration tier
    durations = plan.get("durations") or []
    tier = next((d for d in durations if d["days"] == duration_days), None)
    if tier:
        price = tier["price"]
    elif duration_days == plan.get("duration_days"):
        price = plan.get("price", 0.0)
    else:
        return False

    balance = user.get("wallet_balance", 0.0)
    if balance < price:
        return False

    now = now_utc()
    end_date = now + timedelta(days=duration_days)

    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"wallet_balance": -price}},
    )
    await db.subscriptions.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "plan_name": plan["name"],
                "duration_days": duration_days,
                "price_paid": price,
                "start_date": now,
                "end_date": end_date,
                "is_active": True,
                "channels": plan.get("channels", []),
            }
        },
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
    logger.info("User %d purchased plan %s (%d days)", user_id, plan["name"], duration_days)
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

async def process_auto_renewals(bot_instance=None) -> list[dict]:
    db = get_db()
    now = now_utc()

    cursor = db.subscriptions.find({"is_active": True, "end_date": {"$lte": now}})
    expired = await cursor.to_list(length=None)

    results = []
    for sub in expired:
        user_id = sub["user_id"]
        plan_name = sub.get("plan_name")
        sub_duration_days = sub.get("duration_days", 30)

        user = await get_user(user_id)
        if user is None or not user.get("auto_renew", False):
            await db.subscriptions.update_one(
                {"user_id": user_id}, {"$set": {"is_active": False}}
            )
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
        tier = next((d for d in durations if d["days"] == sub_duration_days), None)
        if tier:
            price = tier["price"]
        elif sub_duration_days == plan.get("duration_days"):
            price = plan.get("price", 0.0)
        elif durations:
            # Fallback: cheapest tier
            tier = min(durations, key=lambda d: d["price"])
            price = tier["price"]
            sub_duration_days = tier["days"]
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
            results.append({"user_id": user_id, "status": "insufficient_funds", "plan": plan, "price_paid": 0})
            logger.info("Auto-renew failed (low balance) for user %d", user_id)
        else:
            end_date = now + timedelta(days=sub_duration_days)
            await db.users.update_one(
                {"user_id": user_id}, {"$inc": {"wallet_balance": -price}}
            )
            await db.subscriptions.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "plan_name": plan["name"],
                        "duration_days": sub_duration_days,
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
