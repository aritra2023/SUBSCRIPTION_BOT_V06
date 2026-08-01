from __future__ import annotations

import logging
from datetime import datetime, timezone

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

from keyboards.inline import wallet_keyboard
from services.subscription import get_user, get_wallet_stats
from utils.helpers import to_small_caps

logger = logging.getLogger(__name__)
router = Router(name="wallet")


@router.callback_query(lambda c: c.data == "wallet")
async def cb_wallet(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else 0
    first_name = callback.from_user.first_name if callback.from_user else ""

    user = await get_user(user_id)
    balance = user.get("wallet_balance", 0.0) if user else 0.0
    referral_points = user.get("referral_points", 0) if user else 0
    auto_renew = user.get("auto_renew", True) if user else True

    today_amount, today_count, total_dep_amount, total_dep_count, total_spent = (
        await get_wallet_stats(user_id)
    )

    name_sc = to_small_caps(first_name)

    text = (
        f"➲ ɴᴀᴍᴇ : <b>{name_sc}</b>\n"
        f"➲ ᴜsᴇʀ ɪᴅ : <a href=\"tg://user?id={user_id}\">{user_id}</a>\n"
        f"➲ ʙᴀʟᴀɴᴄᴇ : <b>₹{balance:.2f}</b>\n"
        f"➲ ʀᴇғᴇʀʀᴀʟ ᴘᴏɪɴᴛs : <b>{referral_points}</b>\n\n"
        f"<blockquote expandable><b>➲ ᴛᴏᴅᴀʏ ʏᴏᴜ ᴅᴇᴘᴏsɪᴛᴇᴅ: ₹{today_amount:.2f}</b>\n"
        f"▸ ᴛʜʀᴏᴜɢʜ <b>{today_count}</b> ᴛʀᴀɴsᴀᴄᴛɪᴏɴs.</blockquote>\n"
        f"<blockquote expandable><b>➲ ᴛᴏᴛᴀʟ ʏᴏᴜ ᴅᴇᴘᴏsɪᴛᴇᴅ: ₹{total_dep_amount:.2f}</b>\n"
        f"▸ ᴛʜʀᴏᴜɢʜ <b>{total_dep_count}</b> ᴛʀᴀɴsᴀᴄᴛɪᴏɴs.</blockquote>\n\n"
        f"➲ ᴛᴏᴛᴀʟ ʏᴏᴜ sᴘᴇɴᴛ: ₹{total_spent:.2f}"
    )

    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=wallet_keyboard(auto_renew),
            )
        elif callback.message:
            await callback.message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=wallet_keyboard(auto_renew),
            )
    except Exception:
        pass

    await callback.answer()


@router.callback_query(lambda c: c.data == "toggle_auto_renew")
async def cb_toggle_auto_renew(callback: CallbackQuery) -> None:
    from database.db import get_db
    user_id = callback.from_user.id if callback.from_user else 0
    first_name = callback.from_user.first_name if callback.from_user else ""

    user = await get_user(user_id)
    current = user.get("auto_renew", True) if user else True
    new_val = not current

    db = get_db()
    await db.users.update_one({"user_id": user_id}, {"$set": {"auto_renew": new_val}})

    # Re-fetch fresh data and rebuild wallet view inline
    balance = user.get("wallet_balance", 0.0) if user else 0.0
    referral_points = user.get("referral_points", 0) if user else 0

    today_amount, today_count, total_dep_amount, total_dep_count, total_spent = (
        await get_wallet_stats(user_id)
    )

    name_sc = to_small_caps(first_name)

    text = (
        f"➲ ɴᴀᴍᴇ : <b>{name_sc}</b>\n"
        f"➲ ᴜsᴇʀ ɪᴅ : <a href=\"tg://user?id={user_id}\">{user_id}</a>\n"
        f"➲ ʙᴀʟᴀɴᴄᴇ : <b>₹{balance:.2f}</b>\n"
        f"➲ ʀᴇғᴇʀʀᴀʟ ᴘᴏɪɴᴛs : <b>{referral_points}</b>\n\n"
        f"<blockquote expandable><b>➲ ᴛᴏᴅᴀʏ ʏᴏᴜ ᴅᴇᴘᴏsɪᴛᴇᴅ: ₹{today_amount:.2f}</b>\n"
        f"▸ ᴛʜʀᴏᴜɢʜ <b>{today_count}</b> ᴛʀᴀɴsᴀᴄᴛɪᴏɴs.</blockquote>\n"
        f"<blockquote expandable><b>➲ ᴛᴏᴛᴀʟ ʏᴏᴜ ᴅᴇᴘᴏsɪᴛᴇᴅ: ₹{total_dep_amount:.2f}</b>\n"
        f"▸ ᴛʜʀᴏᴜɢʜ <b>{total_dep_count}</b> ᴛʀᴀɴsᴀᴄᴛɪᴏɴs.</blockquote>\n\n"
        f"➲ ᴛᴏᴛᴀʟ ʏᴏᴜ sᴘᴇɴᴛ: ₹{total_spent:.2f}"
    )

    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=wallet_keyboard(new_val),
            )
        elif callback.message:
            await callback.message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=wallet_keyboard(new_val),
            )
    except Exception:
        pass

    await callback.answer("ᴀᴜᴛᴏ-ʀᴇɴᴇᴡ " + ("ᴏɴ ✅" if new_val else "ᴏғғ ❌"))


@router.callback_query(lambda c: c.data == "add_balance")
async def cb_add_balance(callback: CallbackQuery) -> None:
    await callback.answer(
        "ᴛᴏ ᴀᴅᴅ ʙᴀʟᴀɴᴄᴇ, ᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ᴀᴅᴍɪɴ ᴏʀ ᴜsᴇ ᴛʜᴇ ᴘᴀʏᴍᴇɴᴛ ʟɪɴᴋ.",
        show_alert=True,
    )
