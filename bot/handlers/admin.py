from __future__ import annotations

import logging
import re

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters.admin import IsAdmin
from keyboards.inline import (
    DURATION_OPTIONS,
    admin_duration_select_keyboard,
    admin_panel_keyboard,
    cancel_keyboard,
)
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
    # Add plan flow
    addplan_name = State()
    addplan_description = State()
    addplan_demo_link = State()
    addplan_payment_proof = State()
    addplan_durations = State()
    addplan_pricing = State()
    addplan_channels = State()


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
        durations = plan.get("durations", [])
        if durations:
            price_range = f"₹{min(d['price'] for d in durations):.0f}–₹{max(d['price'] for d in durations):.0f}"
        else:
            price_range = f"₹{plan.get('price', 0)}"
        text += f"  • {plan['display_name']} — {price_range}\n"

    if callback.message:
        await callback.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=admin_panel_keyboard())
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
        await callback.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=admin_panel_keyboard())
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
            "<blockquote><b>📢 BROADCAST</b></blockquote>\n\nSend the message to broadcast to all users.",
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_keyboard(),
        )
    await state.set_state(AdminStates.waiting_for_broadcast)
    await callback.answer()


@router.message(AdminStates.waiting_for_broadcast, F.text)
async def handle_broadcast_message(message: Message, state: FSMContext) -> None:
    from loader import bot
    broadcast_text = message.text or ""
    users = await get_all_users()
    await state.clear()
    status_msg = await message.answer(f"📢 Broadcasting to {len(users)} users...")
    sent, failed = 0, 0
    for user in users:
        try:
            await bot.send_message(chat_id=user["user_id"], text=broadcast_text, parse_mode=ParseMode.HTML)
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
async def cb_admin_plans(callback: CallbackQuery) -> None:
    plans = await get_active_plans()
    lines = ["<blockquote><b>📦 PLANS</b></blockquote>\n"]
    for p in plans:
        durations = p.get("durations", [])
        if durations:
            tiers = ", ".join(f"{d['label']} ₹{d['price']:.0f}" for d in durations)
        else:
            tiers = f"₹{p.get('price', '?')} / {p.get('duration_days', '?')}d"
        lines.append(f"• <b>{p['display_name']}</b>\n  {tiers}")
    lines.append("\n<i>Send /addplan to add a new plan.</i>")

    if callback.message:
        await callback.message.edit_text(
            "\n".join(lines), parse_mode=ParseMode.HTML, reply_markup=admin_panel_keyboard()
        )
    await callback.answer()


# ── Add Plan — Step 1: Name ───────────────────────────────────────────────────

@router.message(Command("addplan"))
async def cmd_add_plan(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "<blockquote><b>➕ ADD PLAN — Step 1/6</b></blockquote>\n\n"
        "Enter the plan <b>display name</b>:\n\n"
        "<i>Example: FLIX PREMIUM</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(AdminStates.addplan_name)


@router.message(StateFilter(AdminStates.addplan_name), F.text)
async def handle_addplan_name(message: Message, state: FSMContext) -> None:
    display_name = (message.text or "").strip()
    if not display_name:
        await message.answer("❌ Name cannot be empty. Try again.")
        return
    internal_name = re.sub(r"[^a-z0-9_]", "", display_name.lower().replace(" ", "_"))
    if not internal_name:
        internal_name = "plan_" + str(abs(hash(display_name)))[:6]
    await state.update_data(display_name=display_name, name=internal_name)
    await message.answer(
        "<blockquote><b>➕ ADD PLAN — Step 2/6</b></blockquote>\n\n"
        "Enter the plan <b>description</b>:",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(AdminStates.addplan_description)


# ── Add Plan — Step 2: Description ───────────────────────────────────────────

@router.message(StateFilter(AdminStates.addplan_description), F.text)
async def handle_addplan_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=(message.text or "").strip())
    await message.answer(
        "<blockquote><b>➕ ADD PLAN — Step 3/6</b></blockquote>\n\n"
        "Enter a <b>demo channel link</b> (e.g. <code>t.me/+xxx</code>):\n\n"
        "<i>Send <code>skip</code> to leave empty.</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(AdminStates.addplan_demo_link)


# ── Add Plan — Step 3: Demo Link ──────────────────────────────────────────────

@router.message(StateFilter(AdminStates.addplan_demo_link), F.text)
async def handle_addplan_demo_link(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    demo_link = "" if raw.lower() == "skip" else raw
    await state.update_data(demo_link=demo_link)

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ ʏᴇs (ʀᴇᴄᴏᴍᴍᴇɴᴅᴇᴅ)", callback_data="addplan_proof:yes", style="success"),
        InlineKeyboardButton(text="❌ ɴᴏ", callback_data="addplan_proof:no", style="danger"),
    )
    builder.row(InlineKeyboardButton(text="✖ ᴄᴀɴᴄᴇʟ", callback_data="admin_cancel", style="danger"))

    await message.answer(
        "<blockquote><b>➕ ADD PLAN — Step 4/6</b></blockquote>\n\n"
        "Should users be required to send a <b>payment proof screenshot</b>?",
        parse_mode=ParseMode.HTML,
        reply_markup=builder.as_markup(),
    )
    await state.set_state(AdminStates.addplan_payment_proof)


# ── Add Plan — Step 4: Payment Proof ─────────────────────────────────────────

@router.callback_query(StateFilter(AdminStates.addplan_payment_proof), F.data.startswith("addplan_proof:"))
async def cb_addplan_payment_proof(callback: CallbackQuery, state: FSMContext) -> None:
    payment_proof = (callback.data or "").split(":")[1] == "yes"
    await state.update_data(payment_proof_required=payment_proof, selected_durations=[])
    if callback.message:
        await callback.message.edit_text(
            "<blockquote><b>➕ ADD PLAN — Step 5/6</b></blockquote>\n\n"
            "Select which <b>duration options</b> to offer.\n"
            "Tap to toggle ✅, then press <b>Done</b>:",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_duration_select_keyboard([]),
        )
    await state.set_state(AdminStates.addplan_durations)
    await callback.answer()


# ── Add Plan — Step 5: Duration Toggle ───────────────────────────────────────

@router.callback_query(StateFilter(AdminStates.addplan_durations), F.data.startswith("adm_dur:"))
async def cb_addplan_duration_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    days = int((callback.data or "").split(":")[1])
    data = await state.get_data()
    selected: list[int] = data.get("selected_durations", [])
    if days in selected:
        selected.remove(days)
    else:
        selected.append(days)
    await state.update_data(selected_durations=selected)
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=admin_duration_select_keyboard(selected))
    await callback.answer()


@router.callback_query(StateFilter(AdminStates.addplan_durations), F.data == "adm_dur_done")
async def cb_addplan_duration_done(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    selected: list[int] = data.get("selected_durations", [])
    if not selected:
        await callback.answer("⚠️ Select at least one duration!", show_alert=True)
        return

    selected.sort()
    label_map = {days: label for days, label in DURATION_OPTIONS}
    durations_to_price = [{"days": d, "label": label_map.get(d, f"{d}d")} for d in selected]

    await state.update_data(durations_to_price=durations_to_price, duration_prices=[], pricing_index=0)
    first = durations_to_price[0]

    if callback.message:
        await callback.message.edit_text(
            f"<blockquote><b>➕ ADD PLAN — Step 6/6</b></blockquote>\n\n"
            f"Enter price for <b>{first['label']}</b> (₹):",
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_keyboard(),
        )
    await state.set_state(AdminStates.addplan_pricing)
    await callback.answer()


# ── Add Plan — Step 6: Pricing ────────────────────────────────────────────────

@router.message(StateFilter(AdminStates.addplan_pricing), F.text)
async def handle_addplan_pricing(message: Message, state: FSMContext) -> None:
    try:
        price = float((message.text or "").strip())
        if price < 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Invalid price. Send a positive number (e.g. 299).")
        return

    data = await state.get_data()
    durations_to_price: list[dict] = data["durations_to_price"]
    duration_prices: list[dict] = data.get("duration_prices", [])
    idx: int = data.get("pricing_index", 0)

    current = durations_to_price[idx]
    duration_prices.append({"days": current["days"], "label": current["label"], "price": price})
    idx += 1

    if idx < len(durations_to_price):
        await state.update_data(duration_prices=duration_prices, pricing_index=idx)
        nxt = durations_to_price[idx]
        await message.answer(
            f"<blockquote><b>➕ ADD PLAN — Pricing</b></blockquote>\n\n"
            f"Enter price for <b>{nxt['label']}</b> (₹):",
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_keyboard(),
        )
    else:
        await state.update_data(duration_prices=duration_prices, pricing_index=idx, channels=[])
        await message.answer(
            "<blockquote><b>➕ ADD PLAN — Channels</b></blockquote>\n\n"
            "Send <b>channel invite link(s)</b> one by one.\n"
            "When done, send <code>done</code>.\n\n"
            "<i>Channels added: 0</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_keyboard(),
        )
        await state.set_state(AdminStates.addplan_channels)


# ── Add Plan — Channels ────────────────────────────────────────────────────────

@router.message(StateFilter(AdminStates.addplan_channels), F.text)
async def handle_addplan_channels(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    data = await state.get_data()
    channels: list[str] = data.get("channels", [])

    if text.lower() == "done":
        await create_plan(
            name=data["name"],
            display_name=data["display_name"],
            description=data.get("description", ""),
            demo_link=data.get("demo_link", ""),
            payment_proof_required=data.get("payment_proof_required", True),
            durations=data["duration_prices"],
            channels=channels,
        )
        await state.clear()
        tiers_text = "\n".join(
            f"  • {d['label']} — ₹{d['price']:.0f}" for d in data["duration_prices"]
        )
        await message.answer(
            f"✅ <b>Plan created:</b> {data['display_name']}\n\n"
            f"<b>Durations:</b>\n{tiers_text}\n\n"
            f"<b>Channels:</b> {len(channels)}\n"
            f"<b>Payment Proof:</b> {'Yes' if data.get('payment_proof_required') else 'No'}",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_panel_keyboard(),
        )
    else:
        channels.append(text)
        await state.update_data(channels=channels)
        await message.answer(
            f"✅ Link added. <i>Channels added: {len(channels)}</i>\n\n"
            "Send another link or <code>done</code> to finish.",
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_keyboard(),
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
