from __future__ import annotations

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

from config import ADMIN_ID
from database.db import get_db
from keyboards.inline import add_balance_keyboard, gift_card_keyboard, wallet_keyboard
from services.subscription import get_user, get_wallet_stats
from utils.helpers import to_small_caps

router = Router(name="wallet")


def _wallet_text(first_name: str, user_id: int, balance: float, referral_points: int,
                 today_amount: float, today_count: int,
                 total_dep_amount: float, total_dep_count: int,
                 total_spent: float) -> str:
    name_sc = to_small_caps(first_name)
    return (
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


@router.callback_query(lambda c: c.data == "wallet")
async def cb_wallet(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else 0
    first_name = callback.from_user.first_name if callback.from_user else ""

    user = await get_user(user_id)
    balance = user.get("wallet_balance", 0.0) if user else 0.0
    referral_points = user.get("referral_points", 0) if user else 0
    auto_renew = user.get("auto_renew", True) if user else True

    stats = await get_wallet_stats(user_id)
    text = _wallet_text(first_name, user_id, balance, referral_points, *stats)

    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(caption=text, reply_markup=wallet_keyboard(auto_renew))
        elif callback.message:
            await callback.message.edit_text(text=text, reply_markup=wallet_keyboard(auto_renew))
    except Exception:
        pass

    await callback.answer()


@router.callback_query(lambda c: c.data == "toggle_auto_renew")
async def cb_toggle_auto_renew(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else 0
    first_name = callback.from_user.first_name if callback.from_user else ""

    user = await get_user(user_id)
    new_val = not (user.get("auto_renew", True) if user else True)

    await get_db().users.update_one({"user_id": user_id}, {"$set": {"auto_renew": new_val}})

    balance = user.get("wallet_balance", 0.0) if user else 0.0
    referral_points = user.get("referral_points", 0) if user else 0
    stats = await get_wallet_stats(user_id)
    text = _wallet_text(first_name, user_id, balance, referral_points, *stats)

    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(caption=text, reply_markup=wallet_keyboard(new_val))
        elif callback.message:
            await callback.message.edit_text(text=text, reply_markup=wallet_keyboard(new_val))
    except Exception:
        pass

    await callback.answer("ᴀᴜᴛᴏ-ʀᴇɴᴇᴡ " + ("ᴏɴ ✅" if new_val else "ᴏғғ ❌"))


# ── Add Balance — Payment Method Selection ────────────────────────────────────

@router.callback_query(lambda c: c.data == "add_balance")
async def cb_add_balance(callback: CallbackQuery) -> None:
    text = (
        "<blockquote><b>➲ sᴇʟᴇᴄᴛ ᴘᴀʏᴍᴇɴᴛ ᴍᴇᴛʜᴏᴅ</b></blockquote>\n\n"
        "ᴄʜᴏᴏsᴇ ʜᴏᴡ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴄʜᴀʀɢᴇ ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ:"
    )
    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=add_balance_keyboard(),
            )
        elif callback.message:
            await callback.message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=add_balance_keyboard(),
            )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(lambda c: c.data == "recharge_upi")
async def cb_recharge_upi(callback: CallbackQuery) -> None:
    await callback.answer(
        "⚡ ᴜᴘɪ ᴘᴀʏᴍᴇɴᴛ ᴄᴏᴍɪɴɢ sᴏᴏɴ!\nᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʙᴀᴄᴋ ʟᴀᴛᴇʀ.",
        show_alert=True,
    )


@router.callback_query(lambda c: c.data == "recharge_crypto")
async def cb_recharge_crypto(callback: CallbackQuery) -> None:
    await callback.answer(
        "₿ ᴄʀʏᴘᴛᴏ ᴘᴀʏᴍᴇɴᴛ ᴄᴏᴍɪɴɢ sᴏᴏɴ!\nᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʙᴀᴄᴋ ʟᴀᴛᴇʀ.",
        show_alert=True,
    )


@router.callback_query(lambda c: c.data == "recharge_gift_card")
async def cb_recharge_gift_card(callback: CallbackQuery) -> None:
    text = (
        "<blockquote><b>ᴀᴍᴀᴢᴏɴ ɢɪғᴛ ᴄᴀʀᴅ ʀᴇᴄʜᴀʀɢᴇ</b></blockquote>\n\n"
        "➲ sᴇɴᴅ ʏᴏᴜʀ <b>16-ᴅɪɢɪᴛ ɢɪғᴛ ᴄᴀʀᴅ ᴄᴏᴅᴇ</b> ᴛᴏ ᴀᴅᴍɪɴ.\n\n"
        "<blockquote>ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ ᴡɪʟʟ ʙᴇ ʀᴇᴄʜᴀʀɢᴇᴅ ɪɴsᴛᴀɴᴛʟʏ. ✅</blockquote>"
    )
    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=gift_card_keyboard(ADMIN_ID),
            )
        elif callback.message:
            await callback.message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=gift_card_keyboard(ADMIN_ID),
            )
    except Exception:
        pass
    await callback.answer()
