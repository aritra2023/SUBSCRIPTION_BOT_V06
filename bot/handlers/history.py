from __future__ import annotations

import logging

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

from keyboards.inline import history_telegraph_keyboard, history_detail_keyboard, main_menu_keyboard
from services.subscription import get_user_transactions, get_setting
from services.telegraph import create_history_page
from utils.helpers import build_welcome_text, format_date

logger = logging.getLogger(__name__)
router = Router(name="history")

_TYPE_LABELS = {
    "purchase": "🛒 ᴘᴜʀᴄʜᴀsᴇ",
    "topup":    "💰 ᴛᴏᴘ-ᴜᴘ",
    "refund":   "↩️ ʀᴇғᴜɴᴅ",
    "penalty":  "⚠️ ᴘᴇɴᴀʟᴛʏ",
}


@router.callback_query(lambda c: c.data == "history")
async def cb_history(callback: CallbackQuery) -> None:
    """Show loading in-message, create Telegraph page, then show Open button."""
    await callback.answer()  # ack immediately — no popup

    loading_text = "⧖ <b>ɢᴇɴᴇʀᴀᴛɪɴɢ ʏᴏᴜʀ ʜɪsᴛᴏʀʏ ᴘᴀɢᴇ . . .</b>"

    # Step 1 — show loading state in the message
    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(
                caption=loading_text,
                parse_mode=ParseMode.HTML,
            )
        elif callback.message:
            await callback.message.edit_text(
                text=loading_text,
                parse_mode=ParseMode.HTML,
            )
    except Exception:
        pass

    user = callback.from_user
    user_id = user.id if user else 0
    user_name = user.first_name if user else "User"

    # Step 2 — fetch data + create Telegraph page
    transactions = await get_user_transactions(user_id, limit=20)

    try:
        telegraph_url = await create_history_page(
            user_name=user_name,
            user_id=user_id,
            transactions=transactions,
        )
        ready_text = (
            "📖 <b>ʜɪsᴛᴏʀʏ ᴘᴀɢᴇ ɪs ʀᴇᴀᴅʏ!</b>\n\n"
            "ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʏᴏᴜʀ ᴄᴏᴍᴘʟᴇᴛᴇ ᴘᴜʀᴄʜᴀsᴇ ʜɪsᴛᴏʀʏ."
        )
        keyboard = history_telegraph_keyboard(telegraph_url)
    except Exception as e:
        logger.error("Telegraph page creation failed: %s", e)
        # Fallback — show inline list
        if not transactions:
            ready_text = (
                "<blockquote><b>🎬 ᴛʀᴀɴsᴀᴄᴛɪᴏɴ ʜɪsᴛᴏʀʏ</b></blockquote>\n\n"
                "ɴᴏ ᴛʀᴀɴsᴀᴄᴛɪᴏɴs ғᴏᴜɴᴅ.\n\n"
                "<i>ʏᴏᴜʀ ᴘᴜʀᴄʜᴀsᴇ ᴀɴᴅ ᴡᴀʟʟᴇᴛ ᴀᴄᴛɪᴠɪᴛʏ ᴡɪʟʟ ᴀᴘᴘᴇᴀʀ ʜᴇʀᴇ.</i>"
            )
        else:
            lines = ["<blockquote><b>🎬 ᴛʀᴀɴsᴀᴄᴛɪᴏɴ ʜɪsᴛᴏʀʏ</b></blockquote>\n"]
            for txn in transactions:
                label = _TYPE_LABELS.get(txn.get("type", ""), "📄 ᴛʀᴀɴsᴀᴄᴛɪᴏɴ")
                amount = txn.get("amount", 0.0)
                sign = "+" if amount > 0 else ""
                date_str = format_date(txn["created_at"]) if txn.get("created_at") else "—"
                desc = txn.get("description", "")
                lines.append(
                    f"<b>{label}</b>\n"
                    f"  ᴀᴍᴏᴜɴᴛ: {sign}₹{abs(amount):.2f}\n"
                    f"  {desc}\n"
                    f"  <i>{date_str}</i>\n"
                )
            ready_text = "\n".join(lines)
        keyboard = history_detail_keyboard()

    # Step 3 — update message with result
    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(
                caption=ready_text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        elif callback.message:
            await callback.message.edit_text(
                text=ready_text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
    except Exception:
        pass


@router.callback_query(lambda c: c.data == "history_close")
async def cb_history_close(callback: CallbackQuery) -> None:
    """Go back to the main menu from history."""
    user = callback.from_user
    if user is None:
        await callback.answer()
        return

    text = build_welcome_text(user.id, user.first_name)
    banner_file_id = await get_setting("banner_file_id")

    try:
        if callback.message and callback.message.photo and banner_file_id:
            await callback.message.edit_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=main_menu_keyboard(),
            )
        elif callback.message:
            await callback.message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=main_menu_keyboard(),
            )
    except Exception:
        pass
    await callback.answer()
