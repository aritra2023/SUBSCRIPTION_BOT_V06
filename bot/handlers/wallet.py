from __future__ import annotations

import logging

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

from keyboards.inline import back_main_keyboard
from services.subscription import get_user

logger = logging.getLogger(__name__)
router = Router(name="wallet")


@router.callback_query(lambda c: c.data == "wallet")
async def cb_wallet(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else 0
    user = await get_user(user_id)
    balance = user.get("wallet_balance", 0.0) if user else 0.0

    text = (
        "<blockquote><b>💰 YOUR WALLET</b></blockquote>\n\n"
        f"<b>Available Balance:</b>  ₹{balance:.2f}\n\n"
        "To top up your wallet, contact the admin or use our payment gateway.\n\n"
        "<i>Use your balance to purchase any subscription plan.</i>"
    )

    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=back_main_keyboard(),
            )
        elif callback.message:
            await callback.message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=back_main_keyboard(),
            )
    except Exception:
        pass

    await callback.answer()
