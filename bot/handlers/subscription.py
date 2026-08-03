from __future__ import annotations

import logging

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID
from loader import bot

from keyboards.inline import (
    back_main_keyboard,
    buy_category_keyboard,
    confirm_plan_keyboard,
    duration_keyboard,
    help_keyboard,
    no_plan_keyboard,
    plans_keyboard,
    subscription_activated_keyboard,
)
from services.subscription import (
    get_active_plans,
    get_active_subscription,
    get_plan,
    get_user,
    purchase_subscription,
)
from utils.helpers import format_date, days_remaining, to_small_caps

logger = logging.getLogger(__name__)
router = Router(name="subscription")


# ── Buy Subscription — Category Selection ─────────────────────────────────────

@router.callback_query(lambda c: c.data == "buy_subscription")
async def cb_buy_subscription(callback: CallbackQuery) -> None:
    text = (
        "<blockquote>➤ <b>sᴇʟᴇᴄᴛ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴛʏᴘᴇ</b> \"\n\n"
        "<i>➣ ᴄʜᴏᴏsᴇ ᴡʜᴀᴛ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴜʙsᴄʀɪʙᴇ ᴛᴏ:</i></blockquote>\n\n"
        "◍ <b>ʙᴏᴛ ᴘʀᴇᴍɪᴜᴍ</b> <i>(ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ)</i>\n"
        "• sᴜʙsᴄʀɪʙᴇ ᴛᴏ ᴏᴜʀ ᴀʟʟ ᴛʜᴇ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ʟɪᴋᴇ ᴄᴏʀɴ,ʜᴇɴᴛᴀɪ sɪᴍɪʟᴀʀ ʙᴏᴛs\n\n"
        "◍ <b>ᴄʜᴀɴɴᴇʟs ᴘʀᴇᴍɪᴜᴍ</b>\n"
        "• sᴜʙsᴄʀɪʙᴇ ᴛᴏ sᴘᴇᴄɪғɪᴄ ᴘʀᴇᴍɪᴜᴍ ᴄʜᴀɴɴᴇʟs ʟɪᴋᴇ 'ᴍᴏᴠɪᴇs ʙᴏᴛ ᴅᴀᴛᴀʙᴀsᴇ' ᴏʀ 'ᴄᴏʀɴ ғɪʟᴇs ᴅᴀᴛᴀʙᴀsᴇ'.\n"
        "▸ ɢᴇᴛ ᴛᴇᴍᴘᴏʀᴀʀʏ ɪɴᴠɪᴛᴇ ʟɪɴᴋs ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ.\n\n"
        "<blockquote>◍ <b>ɴᴏᴛᴇ:</b> ᴘʟᴇᴀsᴇ ᴛʀʏ ᴄʜᴀɴɴᴇʟ ᴘʀᴇᴍɪᴜᴍ ᴀs ʙᴏᴛ sᴜʙsᴄʀɪᴘᴛɪᴏɴs ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ!</blockquote>"
    )
    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=buy_category_keyboard(),
            )
        elif callback.message:
            await callback.message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=buy_category_keyboard(),
            )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(lambda c: c.data == "buy_category_bot")
async def cb_buy_category_bot(callback: CallbackQuery) -> None:
    await callback.answer(
        "🚧 ʙᴏᴛ ᴘʀᴇᴍɪᴜᴍ ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ.\nᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʙᴀᴄᴋ ʟᴀᴛᴇʀ.",
        show_alert=True,
    )


@router.callback_query(lambda c: c.data == "buy_category_channel")
async def cb_buy_category_channel(callback: CallbackQuery) -> None:
    plans = await get_active_plans()

    if not plans:
        await callback.answer("⚠️ ɴᴏ ᴘʟᴀɴs ᴀᴠᴀɪʟᴀʙʟᴇ ʀɪɢʜᴛ ɴᴏᴡ.", show_alert=True)
        return

    text = (
        "<blockquote>◍ <b>sᴇʟᴇᴄᴛ ᴄʜᴀɴɴᴇʟs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ</b></blockquote>\n\n"
        "<i>➲ ᴄʜᴏᴏsᴇ ᴛʜᴇ ᴄʜᴀɴɴᴇʟs ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴜʙsᴄʀɪʙᴇ ᴛᴏ:</i>\n\n"
        "<i>ʜɪ ᴛʜᴇʀᴇ! ᴛʜᴇʀᴇ ᴀʀᴇ ǫᴜɪᴛᴇ ᴀ ғᴇᴡ ᴘʀᴇᴍɪᴜᴍ ᴄʜᴀɴɴᴇʟs ᴀᴠᴀɪʟᴀʙʟᴇ - ɢᴇᴛ ɪɴsᴛᴀɴᴛ ᴀᴄᴄᴇss ᴛᴏ ᴇxᴄʟᴜsɪᴠᴇ ᴄᴏɴᴛᴇɴᴛ ᴡɪᴛʜᴏᴜᴛ ᴀᴅs ᴀɴᴅ ᴜɴʟɪᴍɪᴛᴇᴅ ɪɴᴠɪᴛᴇ ʟɪɴᴋs.</i>\n\n"
        "<blockquote>➲ <b>ᴛɪᴘ:</b> ᴄʜᴏᴏsᴇ <b>ᴄᴏᴍʙᴏ</b> ᴏʀ <b>ᴍᴜʟᴛɪᴘʟᴇ ᴄʜᴀɴɴᴇʟs</b> ᴛᴏ ɢᴇᴛ ᴜᴘ ᴛᴏ <b>60% ᴏғғ!</b>\n"
        "ᴇᴀʀɴ ᴘʀᴇᴠᴇʀsᴇ ᴘᴏɪɴᴛs ᴏɴ ᴇᴠᴇʀʏ ᴘᴜʀᴄʜᴀsᴇ!</blockquote>"
    )
    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=plans_keyboard(plans),
            )
        elif callback.message:
            await callback.message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=plans_keyboard(plans),
            )
    except Exception:
        pass
    await callback.answer()


# ── Plan Detail ───────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("plan_select:"))
async def cb_plan_select(callback: CallbackQuery) -> None:
    plan_name = callback.data.split(":", 1)[1]  # type: ignore[union-attr]
    plan = await get_plan(plan_name)

    if not plan:
        await callback.answer("ᴘʟᴀɴ ɴᴏᴛ ғᴏᴜɴᴅ.", show_alert=True)
        return

    durations = plan.get("durations", [])
    regular = [d for d in durations if d.get("days", 0) < 36500]
    lifetime = next((d for d in durations if d.get("days", 0) >= 36500), None)

    # Header — plan name
    plan_name_sc = to_small_caps(plan['display_name'])
    text = f"<blockquote>✦ <b>{plan_name_sc}</b></blockquote>\n"

    # Regular duration prices
    if regular:
        price_lines = "\n".join(f"◍ {d['label']}: ₹{d['price']:.0f}" for d in regular)
        text += f"<blockquote>{price_lines}</blockquote>\n\n"

    # Lifetime + payment methods + instructions — each in its own blockquote
    footer = ""
    if lifetime:
        footer += f"<blockquote>≡ ʟɪғᴇᴛɪᴍᴇ: ₹{lifetime['price']:.0f} (ᴘᴀʏ ᴏɴᴄᴇ, ᴜsᴇ ғᴏʀᴇᴠᴇʀ)</blockquote>\n"
    footer += (
        "<blockquote>⧗ ᴘᴀʏᴍᴇɴᴛ ᴍᴇᴛʜᴏᴅs: ᴘᴀʏᴛᴍ, ɢᴘᴀʏ, ᴘʜᴏɴᴇᴘᴇ, ᴜᴘɪ &amp; ǫʀ ᴄᴏᴅᴇ</blockquote>\n"
        "<blockquote>◍ ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴀғᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ!\n"
        "◍ ᴀғᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴜs sᴄʀᴇᴇɴsʜᴏᴛ &amp; ɢᴇᴛ ᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴄʜᴀɴɴᴇʟ ᴏʀ ʙᴏᴛ ᴀᴄᴄᴇss ɪɴsᴛᴀɴᴛʟʏ ᴡɪᴛʜᴏᴜᴛ ᴅᴇʟᴀʏ</blockquote>"
    )
    text += footer

    # Duration keyboard if plan has tiers, else legacy single-tier confirm
    demo_link = plan.get("demo_link", "") or ""
    if durations:
        keyboard = duration_keyboard(plan_name, durations, demo_link=demo_link)
    else:
        keyboard = confirm_plan_keyboard(plan_name, plan.get("duration_days", 30))

    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(
                caption=text, parse_mode=ParseMode.HTML, reply_markup=keyboard
            )
        elif callback.message:
            await callback.message.edit_text(
                text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard
            )
    except Exception:
        pass

    await callback.answer()


# ── Duration Select ───────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("plan_duration:"))
async def cb_plan_duration(callback: CallbackQuery) -> None:
    _, plan_name, days_str = (callback.data or "").split(":", 2)  # type: ignore[union-attr]
    days = int(days_str)
    plan = await get_plan(plan_name)

    if not plan:
        await callback.answer("ᴘʟᴀɴ ɴᴏᴛ ғᴏᴜɴᴅ.", show_alert=True)
        return

    durations = plan.get("durations", [])
    tier = next((d for d in durations if d["days"] == days), None)
    if not tier:
        await callback.answer("ᴅᴜʀᴀᴛɪᴏɴ ɴᴏᴛ ғᴏᴜɴᴅ.", show_alert=True)
        return

    user_id = callback.from_user.id if callback.from_user else 0
    user = await get_user(user_id)
    balance = user.get("wallet_balance", 0.0) if user else 0.0
    price = tier["price"]

    plan_desc = (plan.get("description") or "").strip()
    text = f"<blockquote><b>{to_small_caps(plan['display_name'])}</b></blockquote>\n\n"
    if plan_desc:
        text += f"{plan_desc}\n\n"
    text += (
        f"<blockquote>"
        f"➲ <b>ᴘʟᴀɴ:</b> {to_small_caps(plan['display_name'])}\n"
        f"➲ <b>ᴅᴜʀᴀᴛɪᴏɴ:</b> {tier['label']}\n"
        f"➲ <b>ᴘʀɪᴄᴇ:</b> ₹{price:.0f}\n"
        f"➲ <b>ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ:</b> ₹{balance:.2f}"
        f"</blockquote>\n"
    )

    insufficient = balance < price
    if not insufficient:
        text += (
            "<blockquote>✓ <i>\"sᴜғғɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ ɪɴ ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ. "
            "ʏᴏᴜ ᴄᴀɴ ᴘᴜʀᴄʜᴀsᴇ ʙᴇʟᴏᴡ ʙʏ ᴄʟɪᴄᴋɪɴɢ ᴄᴏɴғɪʀᴍ ᴘᴜʀᴄʜᴀsᴇ.\"</i></blockquote>"
        )
    else:
        shortfall = price - balance
        text += (
            f"<blockquote>⚠️ <i>\"ɪɴsᴜғғɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ ɪɴ ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ. "
            f"ʏᴏᴜ ɴᴇᴇᴅ ₹{shortfall:.2f} ᴍᴏʀᴇ ᴛᴏ ᴄᴏᴍᴘʟᴇᴛᴇ ᴛʜɪs ᴘᴜʀᴄʜᴀsᴇ. "
            f"ᴘʟᴇᴀsᴇ ʀᴇᴄʜᴀʀɢᴇ ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.\"</i></blockquote>"
        )

    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=confirm_plan_keyboard(plan_name, days, insufficient=insufficient),
            )
        elif callback.message:
            await callback.message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=confirm_plan_keyboard(plan_name, days, insufficient=insufficient),
            )
    except Exception:
        pass

    await callback.answer()


# ── Confirm Purchase ──────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("plan_confirm:"))
async def cb_plan_confirm(callback: CallbackQuery) -> None:
    _, plan_name, days_str = (callback.data or "").split(":", 2)  # type: ignore[union-attr]
    days = int(days_str)
    plan = await get_plan(plan_name)
    user_id = callback.from_user.id if callback.from_user else 0

    if not plan:
        await callback.answer("ᴘʟᴀɴ ɴᴏᴛ ғᴏᴜɴᴅ.", show_alert=True)
        return

    # Generate fresh one-time invite links before purchase
    raw_channels = plan.get("channels", [])
    invite_links: list[str] = []
    for ch in raw_channels:
        try:
            link_obj = await bot.create_chat_invite_link(ch, member_limit=1)
            invite_links.append(link_obj.invite_link)
        except Exception:
            invite_links.append(str(ch))  # fallback to stored value

    success = await purchase_subscription(user_id, plan, days, invite_links=invite_links)

    if success:
        durations = plan.get("durations", [])
        tier = next((d for d in durations if d["days"] == days), None)
        duration_label = tier["label"] if tier else f"{days} ᴅᴀʏs"
        price = tier["price"] if tier else plan.get("price", 0)

        channels = invite_links

        text = (
            f"<blockquote><b>✓ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!</b></blockquote>\n\n"
            f"<b>ᴘʟᴀɴ:</b> {plan['display_name']}\n"
            f"<b>ᴅᴜʀᴀᴛɪᴏɴ:</b> {duration_label}\n"
            f"<b>ᴀᴍᴏᴜɴᴛ ᴘᴀɪᴅ:</b> ₹{price:.0f}\n\n"
            f"<blockquote>⚠️ <i>ᴛʜɪs ɪɴᴠɪᴛᴇ ʟɪɴᴋ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴊᴏɪɴᴇᴅ ᴏɴᴄᴇ. ᴏɴᴄᴇ ʏᴏᴜ ʜᴀᴠᴇ ᴊᴏɪɴᴇᴅ, ᴛʜᴇ ʟɪɴᴋ ᴡɪʟʟ ᴇxᴘɪʀᴇ ᴀɴᴅ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜsᴇᴅ ᴀɢᴀɪɴ.</i></blockquote>"
        )
        activated_keyboard = subscription_activated_keyboard(channels) if channels else back_main_keyboard()

        # Notify admin about the purchase
        fu = callback.from_user
        user_name = fu.first_name if fu else str(user_id)
        username_tag = (f" (@{fu.username})" if fu and fu.username else "")
        user_info = await get_user(user_id)
        remaining_balance = user_info.get("wallet_balance", 0.0) if user_info else 0.0
        try:
            await bot.send_message(
                ADMIN_ID,
                f"<blockquote>🛒 <b>ɴᴇᴡ ᴘᴜʀᴄʜᴀsᴇ ᴀʟᴇʀᴛ</b></blockquote>\n\n"
                f"👤 <b>ᴜsᴇʀ:</b> {user_name}{username_tag}\n"
                f"🆔 <b>ɪᴅ:</b> <code>{user_id}</code>\n"
                f"📦 <b>ᴘʟᴀɴ:</b> {plan['display_name']}\n"
                f"⏱ <b>ᴅᴜʀᴀᴛɪᴏɴ:</b> {duration_label}\n"
                f"💵 <b>ᴘᴀɪᴅ:</b> ₹{price:.0f}\n"
                f"💼 <b>ʀᴇᴍᴀɪɴɪɴɢ ʙᴀʟᴀɴᴄᴇ:</b> ₹{remaining_balance:.2f}",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass
    else:
        text = (
            "<blockquote><b>❌ ᴘᴜʀᴄʜᴀsᴇ ғᴀɪʟᴇᴅ</b></blockquote>\n\n"
            "ɪɴsᴜғғɪᴄɪᴇɴᴛ ᴡᴀʟʟᴇᴛ ʙᴀʟᴀɴᴄᴇ.\n"
            "ᴘʟᴇᴀsᴇ ᴛᴏᴘ ᴜᴘ ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ."
        )

    reply_kb = activated_keyboard if success else back_main_keyboard()
    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(
                caption=text, parse_mode=ParseMode.HTML, reply_markup=reply_kb
            )
        elif callback.message:
            await callback.message.edit_text(
                text=text, parse_mode=ParseMode.HTML, reply_markup=reply_kb
            )
    except Exception:
        pass

    await callback.answer()


# ── View Plan ─────────────────────────────────────────────────────────────────

async def _send_view_plan(user_id: int, first_name: str, message: Message) -> None:
    """Shared logic for /myplan command and view_plan callback."""
    sub = await get_active_subscription(user_id)

    if sub:
        end_date = sub["end_date"]
        remaining = days_remaining(end_date)
        channels = sub.get("channels", [])
        channel_links = (
            "\n".join(f'• <a href="{c}">ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ</a>' for c in channels)
            if channels else ""
        )
        text = (
            "<blockquote><b>📋 ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ</b></blockquote>\n\n"
            f"<b>ᴘʟᴀɴ:</b> {sub['plan_name'].upper()}\n"
            f"<b>sᴛᴀᴛᴜs:</b> ✅ ᴀᴄᴛɪᴠᴇ\n"
            f"<b>ᴇxᴘɪʀᴇs:</b> {format_date(end_date)}\n"
            f"<b>ʀᴇᴍᴀɪɴɪɴɢ:</b> {remaining} ᴅᴀʏ(s)\n"
        )
        if channel_links:
            text += f"\n<b>ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟs:</b>\n{channel_links}"
        keyboard = back_main_keyboard()
    else:
        text = (
            f"<b>ʜᴇʏ {first_name},</b>\n\n"
            "ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ.\n"
            "ʙᴜʏ ᴏᴜʀ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴛᴏ ᴇɴᴊᴏʏ ᴘʀᴇᴍɪᴜᴍ ʙᴇɴᴇғɪᴛs."
        )
        keyboard = no_plan_keyboard()

    try:
        if message.photo:
            await message.edit_caption(
                caption=text, parse_mode=ParseMode.HTML, reply_markup=keyboard
            )
        else:
            await message.edit_text(
                text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard
            )
    except Exception:
        await message.answer(text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.message(Command("myplan"))
async def cmd_myplan(message: Message) -> None:
    user = message.from_user
    if user is None:
        return
    await _send_view_plan(user.id, user.first_name, message)


@router.callback_query(lambda c: c.data == "view_plan")
async def cb_view_plan(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else 0
    first_name = callback.from_user.first_name if callback.from_user else "ᴛʜᴇʀᴇ"
    if callback.message:
        await _send_view_plan(user_id, first_name, callback.message)
    await callback.answer()


# ── Help ──────────────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "help")
async def cb_help(callback: CallbackQuery) -> None:
    text = (
        "<blockquote><b>ᴀʙᴏᴜᴛ ᴛʜɪs ʙᴏᴛ</b>\n\n"
        "ɪ ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ <b>ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ</b> ᴅᴇsɪɢɴᴇᴅ ᴛᴏ ɢʀᴀɴᴛ "
        "ʏᴏᴜ ɪɴsᴛᴀɴᴛ ᴀᴄᴄᴇss ᴛᴏ ᴇxᴄʟᴜsɪᴠᴇ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ʙᴏᴛs!</blockquote>\n\n"
        "<blockquote><b>\" ʜᴏᴡ ɪᴛ ᴡᴏʀᴋs \"</b>\n\n"
        "• sᴇʟᴇᴄᴛ ʏᴏᴜʀ ғᴀᴠᴏʀɪᴛᴇ ʙᴏᴛs ᴏʀ ᴄʜᴏᴏsᴇ ᴀ <b>ᴄᴏᴍʙᴏ ᴘʟᴀɴ</b> ғᴏʀ ᴍᴀssɪᴠᴇ ᴅɪsᴄᴏᴜɴᴛs.\n\n"
        "• ᴘᴀʏ ᴠɪᴀ ᴜᴘɪ/ǫʀ ᴀɴᴅ sᴇɴᴅ ᴛʜᴇ sᴄʀᴇᴇɴsʜᴏᴛ.\n\n"
        "• ᴏɴᴄᴇ ᴠᴇʀɪғɪᴇᴅ, ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ɪs ᴀᴄᴛɪᴠᴀᴛᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴀᴄʀᴏss ᴀʟʟ sᴇʟᴇᴄᴛᴇᴅ ʙᴏᴛs ᴀɴᴅ ᴄʜᴀɴɴᴇʟs!!</blockquote>\n\n"
        "<blockquote><b>\" ᴜsᴇғᴜʟ ᴄᴏᴍᴍᴀɴᴅs \"</b>\n\n"
        "/start — ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ\n"
        "/myplan — ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴs ᴀɴᴅ ᴇxᴘɪʀʏ</blockquote>\n\n"
        '◈ ᴏᴡɴᴇʀ: <a href="https://t.me/Anonymous"><b>ᴀɴᴏɴʏᴍᴏᴜs</b></a>'
    )

    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=help_keyboard(),
            )
        elif callback.message:
            await callback.message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=help_keyboard(),
            )
    except Exception:
        pass

    await callback.answer()


# ── Help Close ────────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "help_close")
async def cb_help_close(callback: CallbackQuery) -> None:
    try:
        if callback.message:
            await callback.message.delete()
    except Exception:
        pass
    await callback.answer()


# ── Support ───────────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "support")
async def cb_support(callback: CallbackQuery) -> None:
    text = (
        "<blockquote><b>🛟 sᴜᴘᴘᴏʀᴛ — ғʟɪx ᴠᴇʀsᴇ</b></blockquote>\n\n"
        "ɴᴇᴇᴅ ʜᴇʟᴘ? ᴏᴜʀ sᴜᴘᴘᴏʀᴛ ᴛᴇᴀᴍ ɪs ʜᴇʀᴇ ғᴏʀ ʏᴏᴜ.\n\n"
        "📩 <b>ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ:</b> @FlixVerseSupport\n"
        "⏰ <b>ʀᴇsᴘᴏɴsᴇ ᴛɪᴍᴇ:</b> ᴡɪᴛʜɪɴ 24 ʜᴏᴜʀs\n\n"
        "ᴘʟᴇᴀsᴇ ᴅᴇsᴄʀɪʙᴇ ʏᴏᴜʀ ɪssᴜᴇ ᴄʟᴇᴀʀʟʏ ᴡʜᴇɴ ᴄᴏɴᴛᴀᴄᴛɪɴɢ sᴜᴘᴘᴏʀᴛ."
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
