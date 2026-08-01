from __future__ import annotations

import motor.motor_asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.mongo import MongoStorage

from config import BOT_TOKEN, DB_NAME, MONGO_URI

motor_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
_fsm_storage = MongoStorage(client=motor_client, db_name=DB_NAME, collection_name="fsm_states")

bot: Bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp: Dispatcher = Dispatcher(storage=_fsm_storage)
