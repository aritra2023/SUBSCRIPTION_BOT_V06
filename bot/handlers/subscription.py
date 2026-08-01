from __future__ import annotations

import logging

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards.inline import (
    back_main_keyboard,
    buy_category_keyboard,
    confirm_plan_keyboard,
    duration_keyboard,
    help_keyboard,
    no_plan_keyboard,
    plans_keyboard,
)
from services.subscription import (
    get_active_plans,
    get_active_subscription,
    get_plan,
    get_user,
    purchase_subscription,
)
from utils.helpers import format_date, days_remaining

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
        "<blockquote><b>💎 ᴄʜᴏᴏsᴇ ʏᴏᴜʀ ᴘʟᴀɴ</b></blockquote>\n\n"
        "sᴇʟᴇᴄᴛ ᴀ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴘʟᴀɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ɪɴsᴛᴀɴᴛ ᴀᴄᴄᴇss ᴛᴏ ᴀʟʟ ᴘʀᴇᴍɪᴜᴍ ᴄʜᴀɴɴᴇʟs."
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

    lines = [f"<blockquote><b>💎 {plan['display_name']}</b></blockquote>\n"]
    if plan.get("description"):
        lines.append(f"{plan['description']}\n")
    if plan.get("demo_link"):
        lines.append(f'📺 <a href="{plan["demo_link"]}">ᴠɪᴇᴡ ᴅᴇᴍᴏ ᴄʜᴀɴɴᴇʟ</a>\n')

    if durations:
        lines.append("\n<b>ᴀᴠᴀɪʟᴀʙʟᴇ ᴅᴜʀᴀᴛɪᴏɴs:</b>")
        for tier in durations:
            lines.append(f"  ⏱ {tier['label']} — ₹{tier['price']:.0f}")

    if plan.get("payment_proof_required", True):
        lines.append("\n📸 <i>ᴘᴀʏᴍᴇɴᴛ ᴘʀᴏᴏғ ʀᴇǫᴜɪʀᴇᴅ ᴀғᴛᴇʀ ᴘᴜʀᴄʜᴀsᴇ.</i>")

    text = "\n".join(lines)

    # Duration keyboard if plan has tiers, else legacy single-tier confirm
    if durations:
        keyboard = duration_keyboard(plan_name, durations)
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

    text = (
        f"<blockquote><b>📋 ᴄᴏɴғɪʀᴍ ᴘᴜʀᴄʜᴀsᴇ</b></blockquote>\n\n"
        f"<b>ᴘʟᴀɴ:</b> {plan['display_name']}\n"
        f"<b>ᴅᴜʀᴀᴛɪᴏɴ:</b> {tier['label']}\n"
        f"<b>ᴘʀɪᴄᴇ:</b> ₹{price:.0f}\n"
        f"<b>ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ:</b> ₹{balance:.2f}\n\n"
    )

    if balance >= price:
        text += "✅ <b>sᴜғғɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ.</b> ᴄᴏɴғɪʀᴍ ᴘᴜʀᴄʜᴀsᴇ ʙᴇʟᴏᴡ."
    else:
        shortfall = price - balance
        text += f"⚠️ <b>ɪɴsᴜғғɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ.</b> ʏᴏᴜ ɴᴇᴇᴅ ₹{shortfall:.2f} ᴍᴏʀᴇ.\nᴘʟᴇᴀsᴇ ᴛᴏᴘ ᴜᴘ ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ ғɪʀsᴛ."

    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=confirm_plan_keyboard(plan_name, days),
            )
        elif callback.message:
            await callback.message.edit_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=confirm_plan_keyboard(plan_name, days),
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

    success = await purchase_subscription(user_id, plan, days)

    if success:
        durations = plan.get("durations", [])
        tier = next((d for d in durations if d["days"] == days), None)
        duration_label = tier["label"] if tier else f"{days} ᴅᴀʏs"
        price = tier["price"] if tier else plan.get("price", 0)

        channels = plan.get("channels", [])
        channel_links = (
            "\n".join(f'• <a href="{c}">ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ</a>' for c in channels)
            if channels else ""
        )

        text = (
            f"<blockquote><b>✅ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!</b></blockquote>\n\n"
            f"<b>ᴘʟᴀɴ:</b> {plan['display_name']}\n"
            f"<b>ᴅᴜʀᴀᴛɪᴏɴ:</b> {duration_label}\n"
            f"<b>ᴀᴍᴏᴜɴᴛ ᴘᴀɪᴅ:</b> ₹{price:.0f}\n\n"
            f"ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b>ғʟɪx ᴠᴇʀsᴇ</b> ᴘʀᴇᴍɪᴜᴍ! 🎉\n"
        )
        if channel_links:
            text += f"\n<b>ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟs:</b>\n{channel_links}"
    else:
        text = (
            "<blockquote><b>❌ ᴘᴜʀᴄʜᴀsᴇ ғᴀɪʟᴇᴅ</b></blockquote>\n\n"
            "ɪɴsᴜғғɪᴄɪᴇɴᴛ ᴡᴀʟʟᴇᴛ ʙᴀʟᴀɴᴄᴇ.\n"
            "ᴘʟᴇᴀsᴇ ᴛᴏᴘ ᴜᴘ ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ."
        )

    try:
        if callback.message and callback.message.photo:
            await callback.message.edit_caption(
                caption=text, parse_mode=ParseMode.HTML, reply_markup=back_main_keyboard()
            )
        elif callback.message:
            await callback.message.edit_text(
                text=text, parse_mode=ParseMode.HTML, reply_markup=back_main_keyboard()
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
