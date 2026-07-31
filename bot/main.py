from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.types import BotCommand

from database.db import close_db, init_db
from handlers import admin, history, start, subscription, wallet
from loader import bot, dp
from middlewares.db import DatabaseMiddleware
from services.subscription import seed_default_plans

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start",  description="Start the bot"),
        BotCommand(command="admin",  description="Admin panel (admin only)"),
        BotCommand(command="addplan", description="Add a subscription plan (admin only)"),
        BotCommand(command="topup",  description="Top up user wallet (admin only)"),
    ]
    await bot.set_my_commands(commands)


async def on_startup() -> None:
    await init_db()
    await seed_default_plans()
    await set_bot_commands(bot)
    me = await bot.get_me()
    logger.info("Bot started: @%s (ID: %d)", me.username, me.id)


async def on_shutdown() -> None:
    await close_db()
    await bot.session.close()
    logger.info("Bot stopped gracefully")


def register_routers() -> None:
    dp.include_router(start.router)
    dp.include_router(subscription.router)
    dp.include_router(wallet.router)
    dp.include_router(history.router)
    dp.include_router(admin.router)


def register_middlewares() -> None:
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())


async def main() -> None:
    register_middlewares()
    register_routers()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Starting polling...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
