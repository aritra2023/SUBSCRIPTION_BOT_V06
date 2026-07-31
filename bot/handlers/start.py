from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode

from keyboards.inline import main_menu_keyboard
from services.subscription import get_or_create_user, get_setting
from utils.helpers import mention_html

logger = logging.getLogger(__name__)
router = Router(name="start")


def _build_welcome_text(user_id: int, first_name: str) -> str:
    mention = mention_html(user_id, first_name)
    return (
        f"<blockquote expandable>ʜɪ ᴛʜᴇʀᴇ, {mention}!</blockquote>\n"
        f"<blockquote expandable>ɪ ᴀᴍ ᴘʀᴇᴍɪᴜᴍ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʙᴏᴛ ғᴏʀ ғʟɪx ᴠᴇʀsᴇ.</blockquote>\n"
        f"<blockquote expandable>❝ɪ ᴄᴀɴ ɢᴇᴛ ʏᴏᴜ ɪɴsᴛᴀɴᴛ ᴀᴄᴄᴇss ᴛᴏ ᴏᴜʀ ᴇxᴄʟᴜsɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴄʜᴀɴɴᴇʟs ʀɪɢʜᴛ ᴀᴡᴀʏ!!❞</blockquote>\n"
        f"<blockquote expandable>― ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ᴛᴏ sᴇᴇ ᴏᴜʀ ᴘʟᴀɴs!</blockquote>"
    )


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

    text = _build_welcome_text(user.id, user.first_name)
    keyboard = main_menu_keyboard()
    banner_file_id = await get_setting("banner_file_id")

    if banner_file_id:
        await message.answer_photo(
            photo=banner_file_id,
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )
    else:
        await message.answer(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )


@router.callback_query(lambda c: c.data == "back_main")
async def cb_back_main(callback: CallbackQuery) -> None:
    user = callback.from_user
    if user is None:
        return

    text = _build_welcome_text(user.id, user.first_name)
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
