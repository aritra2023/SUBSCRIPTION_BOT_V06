from __future__ import annotations

import logging

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

from keyboards.inline import history_prompt_keyboard, history_detail_keyboard
from services.subscription import get_user_transactions
from utils.helpers import format_date

logger = logging.getLogger(__name__)
router = Router(name="history")

_TYPE_LABELS = {
    "purchase": "🛒 ᴘᴜʀᴄʜᴀsᴇ",
    "topup": "💰 ᴛᴏᴘ-ᴜᴘ",
    "refund": "↩️ ʀᴇғᴜɴᴅ",
}


@router.callback_query(lambda c: c.data == "history")
async def cb_history(callback: CallbackQuery) -> None:
    """Send a new reply to the /start message with the history prompt."""
    text = (
        "✅ <b>ʏᴏᴜʀ ᴄᴏᴍᴘʟᴇᴛᴇ ᴘᴜʀᴄʜᴀsᴇ ʜɪsᴛᴏʀʏ ɪs ʀᴇᴀᴅʏ!</b>\n\n"
        "ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴠɪᴇᴡ ᴀʟʟ ʏᴏᴜʀ ᴘʀᴇᴠɪᴏᴜs ᴘᴜʀᴄʜᴀsᴇs, "
        "ᴀᴄᴛɪᴠᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴs, ᴀɴᴅ ᴇxᴘɪʀʏ ᴅᴀᴛᴇs."
    )
    if callback.message:
        await callback.message.reply(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=history_prompt_keyboard(),
        )
    await callback.answer()


@router.callback_query(lambda c: c.data == "view_history_detail")
async def cb_view_history_detail(callback: CallbackQuery) -> None:
    """Edit the prompt message to show the full transaction list."""
    user_id = callback.from_user.id if callback.from_user else 0
    transactions = await get_user_transactions(user_id, limit=10)

    if not transactions:
        text = (
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
        text = "\n".join(lines)

    try:
        if callback.message:
            await callback.message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=history_detail_keyboard(),
            )
    except Exception:
        pass

    await callback.answer()


@router.callback_query(lambda c: c.data == "history_close")
async def cb_history_close(callback: CallbackQuery) -> None:
    """Delete the history reply message."""
    try:
        if callback.message:
            await callback.message.delete()
    except Exception:
        pass
    await callback.answer()
