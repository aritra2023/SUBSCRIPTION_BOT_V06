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


# ── Plans ─────────────────────────────────────────────────────────────────────

async def get_active_plans() -> list[PlanDoc]:
    db = get_db()
    cursor = db.plans.find({"is_active": True}, {"_id": 0})
    return await cursor.to_list(length=None)


async def get_plan(name: str) -> Optional[PlanDoc]:
    return await get_db().plans.find_one({"name": name}, {"_id": 0})


async def create_plan(name: str, display_name: str, price: float, duration_days: int, description: str) -> None:
    db = get_db()
    plan: PlanDoc = {
        "name": name,
        "display_name": display_name,
        "price": price,
        "duration_days": duration_days,
        "description": description,
        "is_active": True,
    }
    await db.plans.update_one({"name": name}, {"$set": dict(plan)}, upsert=True)


async def seed_default_plans() -> None:
    existing = await get_active_plans()
    if existing:
        return
    defaults = [
        ("basic_1m",  "BASIC — 1 MONTH",  299.0,  30,  "Access to basic premium channels for 1 month."),
        ("standard_3m", "STANDARD — 3 MONTHS", 799.0, 90,  "Access to all standard channels for 3 months."),
        ("premium_6m", "PREMIUM — 6 MONTHS", 1499.0, 180, "Full access to all premium + exclusive channels."),
    ]
    for name, display, price, days, desc in defaults:
        await create_plan(name, display, price, days, desc)
    logger.info("Default plans seeded")


# ── Subscriptions ─────────────────────────────────────────────────────────────

async def get_active_subscription(user_id: int) -> Optional[SubscriptionDoc]:
    db = get_db()
    now = now_utc()
    sub = await db.subscriptions.find_one(
        {"user_id": user_id, "is_active": True, "end_date": {"$gt": now}},
        {"_id": 0},
    )
    return sub


async def purchase_subscription(user_id: int, plan: PlanDoc) -> bool:
    db = get_db()
    user = await get_user(user_id)
    if user is None:
        return False

    price = plan["price"]
    balance = user.get("wallet_balance", 0.0)
    if balance < price:
        return False

    now = now_utc()
    end_date = now + timedelta(days=plan["duration_days"])

    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"wallet_balance": -price}},
    )
    await db.subscriptions.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "plan_name": plan["name"],
                "start_date": now,
                "end_date": end_date,
                "is_active": True,
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
    logger.info("User %d purchased plan %s", user_id, plan["name"])
    return True


# ── Transactions ──────────────────────────────────────────────────────────────

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
