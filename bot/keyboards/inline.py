from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.helpers import to_small_caps


# Duration options available for plans (days, display label)
DURATION_OPTIONS: list[tuple[int, str]] = [
    (15,    "15 ᴅᴀʏs"),
    (30,    "1 ᴍᴏɴᴛʜ"),
    (90,    "3 ᴍᴏɴᴛʜs"),
    (180,   "6 ᴍᴏɴᴛʜs"),
    (365,   "12 ᴍᴏɴᴛʜs"),
    (36500, "ʟɪғᴇᴛɪᴍᴇ"),
]


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="➲ ʙᴜʏ sᴜʙsᴄʀɪᴘᴛɪᴏɴ",
            callback_data="buy_subscription",
            style="success",
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
            style="danger",
        )
    )

    return builder.as_markup()


def buy_category_keyboard() -> InlineKeyboardMarkup:
    """Shown when user taps Buy Subscription — choose Bot or Channel."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="➲ ʙᴜʏ ʙᴏᴛ ᴘʀᴇᴍɪᴜᴍ",
            callback_data="buy_category_bot",
            style="danger",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="➲ ʙᴜʏ ᴄʜᴀɴɴᴇʟ ᴘʀᴇᴍɪᴜᴍ",
            callback_data="buy_category_channel",
            style="success",
        )
    )
    builder.row(
        InlineKeyboardButton(text="‹ ʙᴀᴄᴋ", callback_data="back_main"),
        InlineKeyboardButton(text="● ᴄʟᴏsᴇ ●", callback_data="help_close"),
    )
    return builder.as_markup()


def plans_keyboard(plans: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for plan in plans:
        builder.row(
            InlineKeyboardButton(
                text=f"‣ {to_small_caps(plan['display_name'])}",
                callback_data=f"plan_select:{plan['name']}",
                style="primary",
            )
        )

    builder.row(
        InlineKeyboardButton(text="« ʙᴀᴄᴋ", callback_data="buy_subscription", style="danger"),
    )

    return builder.as_markup()


def duration_keyboard(plan_name: str, durations: list[dict], demo_link: str = "") -> InlineKeyboardMarkup:
    """Shown after selecting a plan — pick a duration tier, 2 per row."""
    builder = InlineKeyboardBuilder()

    # Demo channel link at top as blue button
    if demo_link:
        builder.row(
            InlineKeyboardButton(text="ᴅᴇᴍᴏ ᴄʜᴀɴɴᴇʟ ⌞⌝", url=demo_link, style="primary"),
        )

    buttons = [
        InlineKeyboardButton(
            text=tier["label"],
            callback_data=f"plan_duration:{plan_name}:{tier['days']}",
            style="success",
        )
        for tier in durations
    ]

    # 2 buttons per row
    for i in range(0, len(buttons), 2):
        builder.row(*buttons[i : i + 2])

    builder.row(
        InlineKeyboardButton(text="« ʙᴀᴄᴋ", callback_data="buy_category_channel", style="danger"),
    )

    return builder.as_markup()


def subscription_activated_keyboard(
    channels: list[str],
    joined: set[int] | None = None,
) -> InlineKeyboardMarkup:
    """Shown after subscription is activated — join buttons (red once used) + back."""
    builder = InlineKeyboardBuilder()
    joined = joined or set()
    for i, _link in enumerate(channels):
        num = i + 1
        if i in joined:
            text = (
                f"🔴 ᴄʜᴀɴɴᴇʟ {num} — ᴀʟʀᴇᴀᴅʏ ᴊᴏɪɴᴇᴅ"
                if len(channels) > 1
                else "🔴 ᴀʟʀᴇᴀᴅʏ ᴊᴏɪɴᴇᴅ"
            )
        else:
            text = (
                f"➲ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ {num}"
                if len(channels) > 1
                else "➲ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ"
            )
        builder.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f"join_ch:{i}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="« ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ", callback_data="back_main"),
    )
    return builder.as_markup()


def confirm_plan_keyboard(plan_name: str, days: int, insufficient: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if insufficient:
        builder.row(
            InlineKeyboardButton(
                text="➲ ʀᴇᴄʜᴀʀɢᴇ ᴡᴀʟʟᴇᴛ",
                callback_data="wallet",
                style="success",
            ),
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="ᴄᴏɴғɪʀᴍ ᴘᴜʀᴄʜᴀsᴇ ✓",
                callback_data=f"plan_confirm:{plan_name}:{days}",
                style="success",
            ),
        )

    builder.row(
        InlineKeyboardButton(text="« ʙᴀᴄᴋ", callback_data=f"plan_select:{plan_name}", style="danger"),
    )

    return builder.as_markup()


def wallet_keyboard(auto_renew: bool = True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="➲ ᴀᴅᴅ ʙᴀʟᴀɴᴄᴇ", callback_data="add_balance", style="primary")
    )
    renew_label = "ᴏɴ" if auto_renew else "ᴏғғ"
    renew_style = "success" if auto_renew else "danger"
    builder.row(
        InlineKeyboardButton(
            text=f"ᴀᴜᴛᴏ-ʀᴇɴᴇᴡ: {renew_label}",
            callback_data="toggle_auto_renew",
            style=renew_style,
        )
    )
    builder.row(
        InlineKeyboardButton(text="‹ ʙᴀᴄᴋ", callback_data="back_main", style="primary"),
        InlineKeyboardButton(text="• sᴜᴘᴘᴏʀᴛ •", callback_data="support", style="primary"),
    )

    return builder.as_markup()


def history_prompt_keyboard() -> InlineKeyboardMarkup:
    """Shown when user taps History — leads to detail view."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🗂 ᴠɪᴇᴡ ʜɪsᴛᴏʀʏ",
            callback_data="view_history_detail",
            style="success",
        )
    )
    builder.row(
        InlineKeyboardButton(text="‹ ʙᴀᴄᴋ", callback_data="history_close", style="danger"),
    )
    return builder.as_markup()


def history_telegraph_keyboard(url: str) -> InlineKeyboardMarkup:
    """Shown after Telegraph page is created — open link + back."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="➲ ᴠɪᴇᴡ ʜɪsᴛᴏʀʏ",
            url=url,
            style="primary",
        )
    )
    builder.row(
        InlineKeyboardButton(text="‹ ʙᴀᴄᴋ", callback_data="history_close", style="danger"),
    )
    return builder.as_markup()


def history_detail_keyboard() -> InlineKeyboardMarkup:
    """Fallback: shown on the inline transaction list."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="‹ ʙᴀᴄᴋ", callback_data="history_close", style="danger"),
    )
    return builder.as_markup()


def back_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="« ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ", callback_data="back_main", style="primary"),
    )
    return builder.as_markup()


def help_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="ᴡᴀᴛᴄʜ ᴛᴜᴛᴏʀɪᴀʟ",
            url="https://t.me/FlixVersePremium",
            style="danger",
        )
    )
    builder.row(
        InlineKeyboardButton(text="‹ ʙᴀᴄᴋ", callback_data="back_main", style="primary"),
    )
    return builder.as_markup()


def no_plan_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="➲ ᴄʜᴇᴄᴋᴏᴜᴛ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs",
            callback_data="buy_subscription",
            style="success",
        )
    )
    builder.row(
        InlineKeyboardButton(text="➲ ʙᴀᴄᴋ", callback_data="back_main", style="primary"),
    )
    return builder.as_markup()


def admin_plan_list_keyboard(plans: list[dict]) -> InlineKeyboardMarkup:
    """List all plans as buttons — tap to manage."""
    builder = InlineKeyboardBuilder()
    for plan in plans:
        builder.row(
            InlineKeyboardButton(
                text=f"➠ {to_small_caps(plan['display_name'])}",
                callback_data=f"admin_plan:manage:{plan['name']}",
                style="success",
            )
        )
    builder.row(
        InlineKeyboardButton(text="‹ ʙᴀᴄᴋ", callback_data="admin_back", style="danger"),
    )
    return builder.as_markup()


def admin_plan_manage_keyboard(plan_name: str) -> InlineKeyboardMarkup:
    """Per-plan menu: edit name, desc, demo link, channels, prices, delete."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ ᴇᴅɪᴛ ɴᴀᴍᴇ", callback_data=f"admin_plan:edit_name:{plan_name}", style="primary"),
        InlineKeyboardButton(text="📝 ᴇᴅɪᴛ ᴅᴇsᴄ", callback_data=f"admin_plan:edit_desc:{plan_name}", style="primary"),
    )
    builder.row(
        InlineKeyboardButton(text="🔗 ᴇᴅɪᴛ ᴄʜᴀɴɴᴇʟs", callback_data=f"admin_plan:edit_channels:{plan_name}", style="primary"),
        InlineKeyboardButton(text="🎥 ᴇᴅɪᴛ ᴅᴇᴍᴏ ʟɪɴᴋ", callback_data=f"admin_plan:edit_demo:{plan_name}", style="primary"),
    )
    builder.row(
        InlineKeyboardButton(text="💰 ᴇᴅɪᴛ ᴘʀɪᴄᴇs", callback_data=f"admin_plan:edit_prices:{plan_name}", style="primary"),
    )
    builder.row(
        InlineKeyboardButton(text="🗑 ᴅᴇʟᴇᴛᴇ ᴘʟᴀɴ", callback_data=f"admin_plan:delete:{plan_name}", style="danger"),
    )
    builder.row(
        InlineKeyboardButton(text="‹ ʙᴀᴄᴋ", callback_data="admin_plans", style="primary"),
    )
    return builder.as_markup()


def admin_plan_channels_keyboard(plan_name: str, channels: list[str]) -> InlineKeyboardMarkup:
    """Channel management: add new / remove existing."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ", callback_data=f"admin_plan:ch_add:{plan_name}", style="success"),
    )
    for i, _ in enumerate(channels):
        builder.row(
            InlineKeyboardButton(
                text=f"❌ ʀᴇᴍᴏᴠᴇ #{i + 1}",
                callback_data=f"admin_plan:ch_rm:{plan_name}:{i}",
                style="danger",
            )
        )
    builder.row(
        InlineKeyboardButton(text="‹ ʙᴀᴄᴋ", callback_data=f"admin_plan:manage:{plan_name}", style="primary"),
    )
    return builder.as_markup()


def admin_plan_edit_prices_keyboard(plan_name: str, durations: list[dict]) -> InlineKeyboardMarkup:
    """Show each duration tier as a button to tap and edit its price."""
    builder = InlineKeyboardBuilder()
    for i, tier in enumerate(durations):
        builder.row(
            InlineKeyboardButton(
                text=f"✏️ {tier['label']} — ₹{tier['price']:.0f}",
                callback_data=f"admin_plan:ep_tier:{plan_name}:{i}",
                style="primary",
            )
        )
    builder.row(
        InlineKeyboardButton(text="‹ ʙᴀᴄᴋ", callback_data=f"admin_plan:manage:{plan_name}", style="primary"),
    )
    return builder.as_markup()


def admin_plan_delete_confirm_keyboard(plan_name: str) -> InlineKeyboardMarkup:
    """Confirm / cancel plan deletion."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ ʏᴇs, ᴅᴇʟᴇᴛᴇ", callback_data=f"admin_plan:delete_confirm:{plan_name}", style="danger"),
        InlineKeyboardButton(text="✖ ᴄᴀɴᴄᴇʟ", callback_data=f"admin_plan:manage:{plan_name}", style="primary"),
    )
    return builder.as_markup()


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="⇌ sᴛᴀᴛs ⇌", callback_data="admin_stats", style="primary"))
    builder.row(InlineKeyboardButton(text="⇌ ʙʀᴏᴀᴅᴄᴀsᴛ ⇌", callback_data="admin_broadcast", style="primary"))
    builder.row(InlineKeyboardButton(text="⇌ sᴇᴛ ʙᴀɴɴᴇʀ ⇌", callback_data="admin_set_banner", style="primary"))
    builder.row(InlineKeyboardButton(text="⇌ ᴍᴀɴᴀɢᴇ ᴘʟᴀɴs ⇌", callback_data="admin_plans", style="primary"))

    return builder.as_markup()


def broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ ʏᴇs, sᴇɴᴅ ᴛᴏ ᴀʟʟ", callback_data="broadcast_confirm", style="success"))
    builder.row(InlineKeyboardButton(text="‹ ʙᴀᴄᴋ", callback_data="admin_cancel", style="danger"))
    return builder.as_markup()


def back_to_admin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="‹ ʙᴀᴄᴋ", callback_data="admin_back", style="danger"))
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
