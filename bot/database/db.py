from __future__ import annotations

import logging
from typing import Any, Optional

import motor.motor_asyncio
from pymongo import ASCENDING, DESCENDING

from config import MONGO_URI, DB_NAME

logger = logging.getLogger(__name__)

_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
_db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None


async def init_db() -> None:
    global _client, _db
    _client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    _db = _client[DB_NAME]
    await _create_indexes()
    logger.info("MongoDB connected: %s", DB_NAME)


async def close_db() -> None:
    if _client:
        _client.close()
        logger.info("MongoDB connection closed")


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
