from __future__ import annotations

import logging

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

from keyboards.inline import (
    back_main_keyboard,
    confirm_plan_keyboard,
    duration_keyboard,
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


# ── Buy Subscription ──────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "buy_subscription")
async def cb_buy_subscription(callback: CallbackQuery) -> None:
    plans = await get_active_plans()

    if not plans:
        await callback.answer("⚠️ No plans available right now.", show_alert=True)
        return

    text = (
        "<blockquote><b>💎 CHOOSE YOUR PLAN</b></blockquote>\n\n"
        "Select a subscription plan below to get instant access to all premium channels."
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
        await callback.answer("Plan not found.", show_alert=True)
        return

    durations = plan.get("durations", [])

    lines = [f"<blockquote><b>💎 {plan['display_name']}</b></blockquote>\n"]
    if plan.get("description"):
        lines.append(f"{plan['description']}\n")
    if plan.get("demo_link"):
        lines.append(f'📺 <a href="{plan["demo_link"]}">View Demo Channel</a>\n')

    if durations:
        lines.append("\n<b>Available Durations:</b>")
        for tier in durations:
            lines.append(f"  ⏱ {tier['label']} — ₹{tier['price']:.0f}")

    if plan.get("payment_proof_required", True):
        lines.append("\n📸 <i>Payment proof required after purchase.</i>")

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
        await callback.answer("Plan not found.", show_alert=True)
        return

    durations = plan.get("durations", [])
    tier = next((d for d in durations if d["days"] == days), None)
    if not tier:
        await callback.answer("Duration not found.", show_alert=True)
        return

    user_id = callback.from_user.id if callback.from_user else 0
    user = await get_user(user_id)
    balance = user.get("wallet_balance", 0.0) if user else 0.0
    price = tier["price"]

    text = (
        f"<blockquote><b>📋 CONFIRM PURCHASE</b></blockquote>\n\n"
        f"<b>Plan:</b> {plan['display_name']}\n"
        f"<b>Duration:</b> {tier['label']}\n"
        f"<b>Price:</b> ₹{price:.0f}\n"
        f"<b>Your Wallet:</b> ₹{balance:.2f}\n\n"
    )

    if balance >= price:
        text += "✅ <b>Sufficient balance.</b> Confirm purchase below."
    else:
        shortfall = price - balance
        text += f"⚠️ <b>Insufficient balance.</b> You need ₹{shortfall:.2f} more.\nPlease top up your wallet first."

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
        await callback.answer("Plan not found.", show_alert=True)
        return

    success = await purchase_subscription(user_id, plan, days)

    if success:
        durations = plan.get("durations", [])
        tier = next((d for d in durations if d["days"] == days), None)
        duration_label = tier["label"] if tier else f"{days} days"
        price = tier["price"] if tier else plan.get("price", 0)

        channels = plan.get("channels", [])
        channel_links = (
            "\n".join(f'• <a href="{c}">Join Channel</a>' for c in channels)
            if channels else ""
        )

        text = (
            f"<blockquote><b>✅ SUBSCRIPTION ACTIVATED!</b></blockquote>\n\n"
            f"<b>Plan:</b> {plan['display_name']}\n"
            f"<b>Duration:</b> {duration_label}\n"
            f"<b>Amount Paid:</b> ₹{price:.0f}\n\n"
            f"Welcome to <b>FLIX VERSE</b> Premium! 🎉\n"
        )
        if channel_links:
            text += f"\n<b>Your Channels:</b>\n{channel_links}"
    else:
        text = (
            "<blockquote><b>❌ PURCHASE FAILED</b></blockquote>\n\n"
            "Insufficient wallet balance.\n"
            "Please top up your wallet and try again."
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

@router.callback_query(lambda c: c.data == "view_plan")
async def cb_view_plan(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else 0
    sub = await get_active_subscription(user_id)

    if sub:
        end_date = sub["end_date"]
        remaining = days_remaining(end_date)
        channels = sub.get("channels", [])
        channel_links = (
            "\n".join(f'• <a href="{c}">Join Channel</a>' for c in channels)
            if channels else ""
        )

        text = (
            "<blockquote><b>📋 YOUR CURRENT PLAN</b></blockquote>\n\n"
            f"<b>Plan:</b> {sub['plan_name'].upper()}\n"
            f"<b>Status:</b> ✅ Active\n"
            f"<b>Expires:</b> {format_date(end_date)}\n"
            f"<b>Remaining:</b> {remaining} day(s)\n"
        )
        if channel_links:
            text += f"\n<b>Your Channels:</b>\n{channel_links}"
    else:
        text = (
            "<blockquote><b>📋 YOUR CURRENT PLAN</b></blockquote>\n\n"
            "❌ <b>No active subscription.</b>\n\n"
            "Purchase a plan to get instant access to exclusive premium channels."
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


# ── Help ──────────────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "help")
async def cb_help(callback: CallbackQuery) -> None:
    text = (
        "<blockquote><b>ABOUT THIS BOT</b></blockquote>\n\n"
        "I AM AN ADVANCED <b>PREMIUM MANAGEMENT BOT</b> DESIGNED TO GRANT "
        "YOU INSTANT ACCESS TO EXCLUSIVE CHANNELS AND BOTS!\n\n"
        "✦ HOW IT WORKS ✦\n\n"
        "• SELECT YOUR FAVORITE BOTS OR CHOOSE A <b>COMBO PLAN</b> FOR MASSIVE DISCOUNTS.\n"
        "• PAY VIA UPI/QR AND SEND THE SCREENSHOT USING /bought.\n"
        "• ONCE VERIFIED, YOUR PREMIUM IS ACTIVATED AUTOMATICALLY ACROSS ALL SELECTED BOTS!!\n\n"
        "◈ OWNER: ToBi"
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


# ── Support ───────────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "support")
async def cb_support(callback: CallbackQuery) -> None:
    text = (
        "<blockquote><b>🛟 SUPPORT — FLIX VERSE</b></blockquote>\n\n"
        "Need help? Our support team is here for you.\n\n"
        "📩 <b>Contact Admin:</b> @FlixVerseSupport\n"
        "⏰ <b>Response Time:</b> Within 24 hours\n\n"
        "Please describe your issue clearly when contacting support."
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
