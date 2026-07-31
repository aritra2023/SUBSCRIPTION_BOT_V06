from __future__ import annotations

import logging
from typing import Any

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from filters.admin import IsAdmin
from keyboards.inline import admin_panel_keyboard, cancel_keyboard, back_main_keyboard
from services.subscription import (
    create_plan,
    get_active_plans,
    get_all_users,
    get_user_count,
    set_setting,
    topup_wallet,
)

logger = logging.getLogger(__name__)
router = Router(name="admin")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


class AdminStates(StatesGroup):
    waiting_for_banner = State()
    waiting_for_broadcast = State()
    waiting_for_topup_user = State()
    waiting_for_topup_amount = State()
    waiting_for_plan_data = State()


# ── Admin Panel ───────────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "<blockquote><b>⚙️ ADMIN PANEL — FLIX VERSE</b></blockquote>\n\nChoose an action:",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_panel_keyboard(),
    )


@router.callback_query(lambda c: c.data == "admin_cancel")
async def cb_admin_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if callback.message:
        await callback.message.edit_text(
            "<blockquote><b>⚙️ ADMIN PANEL — FLIX VERSE</b></blockquote>\n\nChoose an action:",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_panel_keyboard(),
        )
    await callback.answer("Cancelled.")


# ── Stats ─────────────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery) -> None:
    total_users = await get_user_count()
    plans = await get_active_plans()

    text = (
        "<blockquote><b>📊 BOT STATISTICS</b></blockquote>\n\n"
        f"<b>Total Users:</b> {total_users}\n"
        f"<b>Active Plans:</b> {len(plans)}\n\n"
        "<b>Plans:</b>\n"
    )
    for plan in plans:
        text += f"  • {plan['display_name']} — ₹{plan['price']}\n"

    if callback.message:
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=admin_panel_keyboard(),
        )
    await callback.answer()


# ── All Users ─────────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin_users")
async def cb_admin_users(callback: CallbackQuery) -> None:
    users = await get_all_users()
    if not users:
        text = "<blockquote><b>👥 USERS</b></blockquote>\n\nNo users yet."
    else:
        lines = [f"<blockquote><b>👥 USERS ({len(users)} total)</b></blockquote>\n"]
        for u in users[:20]:
            uname = f"@{u['username']}" if u.get("username") else "—"
            lines.append(f"• <b>{u['first_name']}</b> ({uname}) — ID: <code>{u['user_id']}</code>")
        if len(users) > 20:
            lines.append(f"\n<i>...and {len(users) - 20} more</i>")
        text = "\n".join(lines)

    if callback.message:
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=admin_panel_keyboard(),
        )
    await callback.answer()


# ── Set Banner ────────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin_set_banner")
async def cb_admin_set_banner(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message:
        await callback.message.edit_text(
            "<blockquote><b>🖼 SET BANNER IMAGE</b></blockquote>\n\nSend a photo to use as the /start banner.",
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_keyboard(),
        )
    await state.set_state(AdminStates.waiting_for_banner)
    await callback.answer()


@router.message(AdminStates.waiting_for_banner, F.photo)
async def handle_banner_photo(message: Message, state: FSMContext) -> None:
    if not message.photo:
        await message.answer("Please send a photo.", reply_markup=cancel_keyboard())
        return

    file_id = message.photo[-1].file_id
    await set_setting("banner_file_id", file_id)
    await state.clear()
    await message.answer(
        "✅ <b>Banner updated successfully!</b>\n\nNew /start banner is now active.",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_panel_keyboard(),
    )


# ── Broadcast ─────────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin_broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message:
        await callback.message.edit_text(
            "<blockquote><b>📢 BROADCAST</b></blockquote>\n\nSend the message you want to broadcast to all users.",
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_keyboard(),
        )
    await state.set_state(AdminStates.waiting_for_broadcast)
    await callback.answer()


@router.message(AdminStates.waiting_for_broadcast, F.text)
async def handle_broadcast_message(message: Message, state: FSMContext) -> None:
    from aiogram import Bot
    from loader import bot

    broadcast_text = message.text or ""
    users = await get_all_users()

    await state.clear()
    status_msg = await message.answer(f"📢 Broadcasting to {len(users)} users...")

    sent, failed = 0, 0
    for user in users:
        try:
            await bot.send_message(
                chat_id=user["user_id"],
                text=broadcast_text,
                parse_mode=ParseMode.HTML,
            )
            sent += 1
        except Exception:
            failed += 1

    await status_msg.edit_text(
        f"✅ Broadcast complete.\n\n<b>Sent:</b> {sent}\n<b>Failed:</b> {failed}",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_panel_keyboard(),
    )


# ── Manage Plans ──────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin_plans")
async def cb_admin_plans(callback: CallbackQuery, state: FSMContext) -> None:
    plans = await get_active_plans()
    lines = ["<blockquote><b>📦 PLANS</b></blockquote>\n"]
    for p in plans:
        lines.append(f"• <b>{p['display_name']}</b> — ₹{p['price']} / {p['duration_days']}d")

    lines.append("\n<i>Send /addplan to add a new plan.</i>")
    text = "\n".join(lines)

    if callback.message:
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=admin_panel_keyboard(),
        )
    await callback.answer()


@router.message(Command("addplan"))
async def cmd_add_plan(message: Message, state: FSMContext) -> None:
    await message.answer(
        "<blockquote><b>➕ ADD PLAN</b></blockquote>\n\n"
        "Send plan details in this exact format:\n\n"
        "<code>name|Display Name|price|duration_days|description</code>\n\n"
        "Example:\n"
        "<code>premium_1m|PREMIUM — 1 MONTH|499|30|Full access for 1 month</code>",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(AdminStates.waiting_for_plan_data)


@router.message(AdminStates.waiting_for_plan_data, F.text)
async def handle_plan_data(message: Message, state: FSMContext) -> None:
    text = message.text or ""
    parts = [p.strip() for p in text.split("|")]

    if len(parts) != 5:
        await message.answer("❌ Invalid format. Use: name|Display Name|price|days|description")
        return

    name, display_name, price_str, days_str, description = parts
    try:
        price = float(price_str)
        days = int(days_str)
    except ValueError:
        await message.answer("❌ Invalid price or days. They must be numbers.")
        return

    await create_plan(name, display_name, price, days, description)
    await state.clear()
    await message.answer(
        f"✅ <b>Plan created:</b> {display_name}\n₹{price} / {days} days",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_panel_keyboard(),
    )


# ── Topup Wallet ──────────────────────────────────────────────────────────────

@router.message(Command("topup"))
async def cmd_topup(message: Message, state: FSMContext) -> None:
    await message.answer(
        "<blockquote><b>💰 WALLET TOP-UP</b></blockquote>\n\n"
        "Send the user ID to top up:",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(AdminStates.waiting_for_topup_user)


@router.message(AdminStates.waiting_for_topup_user, F.text)
async def handle_topup_user(message: Message, state: FSMContext) -> None:
    try:
        user_id = int(message.text or "")
    except ValueError:
        await message.answer("❌ Invalid user ID. Send a numeric Telegram user ID.")
        return

    await state.update_data(topup_user_id=user_id)
    await message.answer(
        f"User ID: <code>{user_id}</code>\n\nNow send the top-up amount (e.g. <code>500</code>):",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(AdminStates.waiting_for_topup_amount)


@router.message(AdminStates.waiting_for_topup_amount, F.text)
async def handle_topup_amount(message: Message, state: FSMContext) -> None:
    try:
        amount = float(message.text or "")
    except ValueError:
        await message.answer("❌ Invalid amount. Send a number.")
        return

    data = await state.get_data()
    user_id = data.get("topup_user_id")
    await state.clear()

    await topup_wallet(user_id, amount, description=f"Admin top-up of ₹{amount}")
    await message.answer(
        f"✅ <b>Wallet topped up!</b>\n\nUser <code>{user_id}</code> received <b>₹{amount:.2f}</b>.",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_panel_keyboard(),
    )
