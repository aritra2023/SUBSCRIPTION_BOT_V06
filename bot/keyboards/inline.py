from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="Ↄ BUY SUBSCRIPTION",
            callback_data="buy_subscription",
        )
    )
    builder.row(
        InlineKeyboardButton(text="• VIEW PLAN •", callback_data="view_plan"),
        InlineKeyboardButton(text="• HELP •", callback_data="help"),
    )
    builder.row(
        InlineKeyboardButton(text="🎬 HISTORY", callback_data="history"),
        InlineKeyboardButton(text="• SUPPORT • ↗", callback_data="support"),
    )
    builder.row(
        InlineKeyboardButton(
            text="Ↄ YOUR WALLET",
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
