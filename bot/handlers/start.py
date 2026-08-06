from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command
from filters.admin import IsAdmin
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode

from keyboards.inline import main_menu_keyboard
from services.subscription import get_or_create_user, get_setting
from utils.helpers import build_welcome_text, to_small_caps

logger = logging.getLogger(__name__)
router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = message.from_user
    if user is None:
        return

    await get_or_create_user(
        user_id=user.id,
        first_name=user.first_name,
        username=user.username,
        last_name=user.last_name,
    )

    text = build_welcome_text(user.id, user.first_name)
    keyboard = main_menu_keyboard()
    banner_file_id = await get_setting("banner_file_id")

    if banner_file_id:
        await message.reply_photo(
            photo=banner_file_id,
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
    else:
        await message.reply(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )


@router.callback_query(lambda c: c.data == "back_main")
async def cb_back_main(callback: CallbackQuery) -> None:
    user = callback.from_user
    if user is None:
        return

    text = build_welcome_text(user.id, user.first_name)
    keyboard = main_menu_keyboard()
    banner_file_id = await get_setting("banner_file_id")

    try:
        if callback.message and callback.message.photo and banner_file_id:
            await callback.message.edit_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        elif callback.message:
            await callback.message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
    except Exception:
        pass

    await callback.answer()


# ── Admin command fallback for non-admins ─────────────────────────────────────

_ADMIN_ONLY_MSG = (
    f"<blockquote><b>🔒 {to_small_caps('Admin Only')}</b></blockquote>\n\n"
    f"{to_small_caps('This command is restricted to admins only.')}"
)

@router.message(Command("admin", "addplan", "topup", "penalty"), ~IsAdmin())
async def cmd_admin_only_fallback(message: Message) -> None:
    await message.answer(_ADMIN_ONLY_MSG, parse_mode=ParseMode.HTML)
