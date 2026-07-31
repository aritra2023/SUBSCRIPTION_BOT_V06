from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.types import BotCommand

from database.db import close_db, init_db
from handlers import admin, history, start, subscription, wallet
from loader import bot, dp
from middlewares.db import DatabaseMiddleware
from services.subscription import process_auto_renewals, seed_default_plans
from utils.helpers import to_small_caps

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


async def auto_renew_loop() -> None:
    """Runs every hour — processes expired subscriptions that have auto-renew on."""
    await asyncio.sleep(60)  # wait a minute after startup before first check
    while True:
        try:
            results = await process_auto_renewals()
            for r in results:
                uid = r["user_id"]
                status = r["status"]
                plan = r.get("plan", {})
                plan_name_sc = to_small_caps(plan.get("display_name", ""))
                if status == "renewed":
                    end = r["end_date"].strftime("%d %b %Y")
                    await bot.send_message(
                        uid,
                        f"✅ <b>ᴀᴜᴛᴏ-ʀᴇɴᴇᴡᴀʟ sᴜᴄᴄᴇssғᴜʟ</b>\n\n"
                        f"➲ ᴘʟᴀɴ : <b>{plan_name_sc}</b>\n"
                        f"➲ ₹<b>{plan.get('price', 0):.2f}</b> ᴅᴇᴅᴜᴄᴛᴇᴅ ғʀᴏᴍ ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ\n"
                        f"➲ ᴠᴀʟɪᴅ ᴛɪʟʟ : <b>{end}</b>",
                        parse_mode="HTML",
                    )
                elif status == "insufficient_funds":
                    await bot.send_message(
                        uid,
                        f"⚠️ <b>ᴀᴜᴛᴏ-ʀᴇɴᴇᴡᴀʟ ғᴀɪʟᴇᴅ</b>\n\n"
                        f"➲ ᴘʟᴀɴ : <b>{plan_name_sc}</b>\n"
                        f"➲ ɪɴsᴜғғɪᴄɪᴇɴᴛ ᴡᴀʟʟᴇᴛ ʙᴀʟᴀɴᴄᴇ.\n\n"
                        f"ᴘʟᴇᴀsᴇ ᴀᴅᴅ ғᴜɴᴅs ᴀɴᴅ ʀᴇɴᴇᴡ ᴍᴀɴᴜᴀʟʟʏ.",
                        parse_mode="HTML",
                    )
        except Exception as exc:
            logger.error("Auto-renew loop error: %s", exc)
        await asyncio.sleep(3600)  # check every hour


async def main() -> None:
    register_middlewares()
    register_routers()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Starting polling...")
    asyncio.create_task(auto_renew_loop())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
