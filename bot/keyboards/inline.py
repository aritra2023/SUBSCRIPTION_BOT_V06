from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Duration options available for plans (days, display label)
DURATION_OPTIONS: list[tuple[int, str]] = [
    (15,    "15 ᴅᴀʏs"),
    (30,    "1 ᴍᴏɴᴛʜ"),
    (90,    "3 ᴍᴏɴᴛʜs"),
    (180,   "6 ᴍᴏɴᴛʜs"),
    (36500, "ʟɪғᴇᴛɪᴍᴇ"),
]


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="➲ ʙᴜʏ sᴜʙsᴄʀɪᴘᴛɪᴏɴ",
            callback_data="buy_subscription",
            style="primary",
        )
    )
    builder.row(
        InlineKeyboardButton(text="• ᴠɪᴇᴡ ᴘʟᴀɴ •", callback_data="view_plan", style="primary"),
        InlineKeyboardButton(text="• ʜᴇʟᴘ •", callback_data="help", style="primary"),
    )
    builder.row(
        InlineKeyboardButton(text="• ʜɪsᴛᴏʀʏ •", callback_data="history", style="primary"),
        InlineKeyboardButton(text="• sᴜᴘᴘᴏʀᴛ •", callback_data="support", style="primary"),
    )
    builder.row(
        InlineKeyboardButton(
            text="➲ ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ",
            callback_data="wallet",
            style="primary",
        )
    )

    return builder.as_markup()


def plans_keyboard(plans: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for plan in plans:
        durations = plan.get("durations", [])
        if durations:
            min_price = min(d["price"] for d in durations)
            price_str = f"₹{min_price:.0f}+"
        elif plan.get("price"):
            price_str = f"₹{plan['price']}"
        else:
            price_str = ""

        builder.row(
            InlineKeyboardButton(
                text=f"💎 {plan['display_name']} — {price_str}",
                callback_data=f"plan_select:{plan['name']}",
                style="primary",
            )
        )

    builder.row(
        InlineKeyboardButton(text="« ʙᴀᴄᴋ", callback_data="back_main", style="primary"),
    )

    return builder.as_markup()


def duration_keyboard(plan_name: str, durations: list[dict]) -> InlineKeyboardMarkup:
    """Shown to user after selecting a plan — pick a duration tier."""
    builder = InlineKeyboardBuilder()

    for tier in durations:
        builder.row(
            InlineKeyboardButton(
                text=f"⏱ {tier['label']} — ₹{tier['price']:.0f}",
                callback_data=f"plan_duration:{plan_name}:{tier['days']}",
                style="primary",
            )
        )

    builder.row(
        InlineKeyboardButton(text="« ʙᴀᴄᴋ", callback_data="buy_subscription", style="primary"),
    )

    return builder.as_markup()


def confirm_plan_keyboard(plan_name: str, days: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="✅ ᴄᴏɴғɪʀᴍ ᴘᴜʀᴄʜᴀsᴇ",
            callback_data=f"plan_confirm:{plan_name}:{days}",
            style="success",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="« ʙᴀᴄᴋ", callback_data=f"plan_select:{plan_name}", style="primary"),
    )

    return builder.as_markup()


def wallet_keyboard(auto_renew: bool = True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="➲ ᴀᴅᴅ ʙᴀʟᴀɴᴄᴇ", callback_data="add_balance", style="success")
    )
    renew_emoji = "🟢" if auto_renew else "🔴"
    renew_label = "ᴏɴ" if auto_renew else "ᴏғғ"
    builder.row(
        InlineKeyboardButton(
            text=f"{renew_emoji} ᴀᴜᴛᴏ-ʀᴇɴᴇᴡ: {renew_label}",
            callback_data="toggle_auto_renew",
            style="primary",
        )
    )
    builder.row(
        InlineKeyboardButton(text="‹ ʙᴀᴄᴋ", callback_data="back_main", style="primary"),
        InlineKeyboardButton(text="• sᴜᴘᴘᴏʀᴛ •", callback_data="support", style="primary"),
    )

    return builder.as_markup()


def back_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="« ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ", callback_data="back_main", style="primary"),
    )
    return builder.as_markup()


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="👥 ᴀʟʟ ᴜsᴇʀs", callback_data="admin_users", style="primary"),
        InlineKeyboardButton(text="📊 sᴛᴀᴛs", callback_data="admin_stats", style="primary"),
    )
    builder.row(
        InlineKeyboardButton(text="📢 ʙʀᴏᴀᴅᴄᴀsᴛ", callback_data="admin_broadcast", style="primary"),
        InlineKeyboardButton(text="🖼 sᴇᴛ ʙᴀɴɴᴇʀ", callback_data="admin_set_banner", style="primary"),
    )
    builder.row(
        InlineKeyboardButton(text="📦 ᴍᴀɴᴀɢᴇ ᴘʟᴀɴs", callback_data="admin_plans", style="primary"),
    )

    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✖ ᴄᴀɴᴄᴇʟ", callback_data="admin_cancel", style="danger"),
    )
    return builder.as_markup()


def admin_duration_select_keyboard(selected: list[int]) -> InlineKeyboardMarkup:
    """Multi-select keyboard for admin to choose which duration tiers to offer."""
    builder = InlineKeyboardBuilder()

    for days, label in DURATION_OPTIONS:
        check = "✅" if days in selected else "☑️"
        builder.row(
            InlineKeyboardButton(
                text=f"{check} {label}",
                callback_data=f"adm_dur:{days}",
                style="primary",
            )
        )

    builder.row(
        InlineKeyboardButton(text="✅ ᴅᴏɴᴇ", callback_data="adm_dur_done", style="success"),
        InlineKeyboardButton(text="✖ ᴄᴀɴᴄᴇʟ", callback_data="admin_cancel", style="danger"),
    )

    return builder.as_markup()
