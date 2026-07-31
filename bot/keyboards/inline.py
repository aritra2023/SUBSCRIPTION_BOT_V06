from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="Ↄ ʙᴜʏ sᴜʙsᴄʀɪᴘᴛɪᴏɴ",
            callback_data="buy_subscription",
        )
    )
    builder.row(
        InlineKeyboardButton(text="• ᴠɪᴇᴡ ᴘʟᴀɴ •", callback_data="view_plan"),
        InlineKeyboardButton(text="• ʜᴇʟᴘ •", callback_data="help"),
    )
    builder.row(
        InlineKeyboardButton(text="• ʜɪsᴛᴏʀʏ •", callback_data="history"),
        InlineKeyboardButton(text="• sᴜᴘᴘᴏʀᴛ •", callback_data="support"),
    )
    builder.row(
        InlineKeyboardButton(
            text="Ↄ ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ",
            callback_data="wallet",
        )
    )

    return builder.as_markup()


def plans_keyboard(plans: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for plan in plans:
        builder.row(
            InlineKeyboardButton(
                text=f"💎 {plan['display_name']} — ₹{plan['price']} / {plan['duration_days']}d",
                callback_data=f"plan_select:{plan['name']}",
            )
        )

    builder.row(
        InlineKeyboardButton(text="« BACK", callback_data="back_main"),
    )

    return builder.as_markup()


def confirm_plan_keyboard(plan_name: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="✅ CONFIRM PURCHASE", callback_data=f"plan_confirm:{plan_name}"),
    )
    builder.row(
        InlineKeyboardButton(text="« BACK", callback_data="buy_subscription"),
    )

    return builder.as_markup()


def wallet_keyboard(auto_renew: bool = True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="Ↄ ᴀᴅᴅ ʙᴀʟᴀɴᴄᴇ", callback_data="add_balance")
    )
    renew_label = "ᴏɴ" if auto_renew else "ᴏғғ"
    builder.row(
        InlineKeyboardButton(
            text=f"🟢 ᴀᴜᴛᴏ-ʀᴇɴᴇᴡ: {renew_label}",
            callback_data="toggle_auto_renew",
        )
    )
    builder.row(
        InlineKeyboardButton(text="‹ ʙᴀᴄᴋ", callback_data="back_main"),
        InlineKeyboardButton(text="• sᴜᴘᴘᴏʀᴛ • ↗", callback_data="support"),
    )

    return builder.as_markup()


def back_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="« BACK TO MENU", callback_data="back_main"),
    )
    return builder.as_markup()


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="👥 ALL USERS", callback_data="admin_users"),
        InlineKeyboardButton(text="📊 STATS", callback_data="admin_stats"),
    )
    builder.row(
        InlineKeyboardButton(text="📢 BROADCAST", callback_data="admin_broadcast"),
        InlineKeyboardButton(text="🖼 SET BANNER", callback_data="admin_set_banner"),
    )
    builder.row(
        InlineKeyboardButton(text="📦 MANAGE PLANS", callback_data="admin_plans"),
    )

    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✖ CANCEL", callback_data="admin_cancel"),
    )
    return builder.as_markup()
