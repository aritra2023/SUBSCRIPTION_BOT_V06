from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.mongo import MongoStorage
import motor.motor_asyncio

from config import BOT_TOKEN, MONGO_URI, DB_NAME

_motor_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
_fsm_storage = MongoStorage(client=_motor_client, db_name=DB_NAME, collection_name="fsm_states")

bot: Bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp: Dispatcher = Dispatcher(storage=_fsm_storage)
