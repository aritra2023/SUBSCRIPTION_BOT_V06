from __future__ import annotations

import logging

import motor.motor_asyncio
from pymongo import ASCENDING, DESCENDING

from config import DB_NAME

logger = logging.getLogger(__name__)

_db: motor.motor_asyncio.AsyncIOMotorDatabase | None = None


async def init_db(client: motor.motor_asyncio.AsyncIOMotorClient) -> None:
    global _db
    _db = client[DB_NAME]
    await _create_indexes()
    logger.info("MongoDB connected: %s", DB_NAME)


def get_db() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not initialised. Call init_db() first.")
    return _db


async def _create_indexes() -> None:
    db = get_db()
    await db.users.create_index([("user_id", ASCENDING)], unique=True)
    await db.subscriptions.create_index([("user_id", ASCENDING)])
    await db.subscriptions.create_index([("end_date", ASCENDING)])
    await db.plans.create_index([("name", ASCENDING)], unique=True)
    await db.transactions.create_index([("user_id", ASCENDING)])
    await db.transactions.create_index([("created_at", DESCENDING)])
