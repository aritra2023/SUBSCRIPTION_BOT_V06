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
        "<blockquote><b>⚙️ ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ — ғʟɪx ᴠᴇʀsᴇ</b></blockquote>\n\nᴄʜᴏᴏsᴇ ᴀɴ ᴀᴄᴛɪᴏɴ:",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_panel_keyboard(),
    )


@router.callback_query(lambda c: c.data == "admin_cancel")
async def cb_admin_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if callback.message:
        await callback.message.edit_text(
            "<blockquote><b>⚙️ ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ — ғʟɪx ᴠᴇʀsᴇ</b></blockquote>\n\nᴄʜᴏᴏsᴇ ᴀɴ ᴀᴄᴛɪᴏɴ:",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_panel_keyboard(),
        )
    await callback.answer("ᴄᴀɴᴄᴇʟʟᴇᴅ.")


# ── Stats ─────────────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery) -> None:
    total_users = await get_user_count()
    plans = await get_active_plans()

    text = (
        "<blockquote><b>📊 ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs</b></blockquote>\n\n"
        f"<b>ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> {total_users}\n"
        f"<b>ᴀᴄᴛɪᴠᴇ ᴘʟᴀɴs:</b> {len(plans)}\n\n"
        "<b>ᴘʟᴀɴs:</b>\n"
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
        text = "<blockquote><b>👥 ᴜsᴇʀs</b></blockquote>\n\nɴᴏ ᴜsᴇʀs ʏᴇᴛ."
    else:
        lines = [f"<blockquote><b>👥 ᴜsᴇʀs ({len(users)} ᴛᴏᴛᴀʟ)</b></blockquote>\n"]
        for u in users[:20]:
            uname = f"@{u['username']}" if u.get("username") else "—"
            lines.append(f"• <b>{u['first_name']}</b> ({uname}) — ɪᴅ: <code>{u['user_id']}</code>")
        if len(users) > 20:
            lines.append(f"\n<i>...ᴀɴᴅ {len(users) - 20} ᴍᴏʀᴇ</i>")
        text = "\n".join(lines)

    if callback.message:
        await callback.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=admin_panel_keyboard())
    await callback.answer()


# ── Set Banner ────────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin_set_banner")
async def cb_admin_set_banner(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message:
        await callback.message.edit_text(
            "<blockquote><b>🖼 sᴇᴛ ʙᴀɴɴᴇʀ ɪᴍᴀɢᴇ</b></blockquote>\n\nsᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ ᴛᴏ ᴜsᴇ ᴀs ᴛʜᴇ /start ʙᴀɴɴᴇʀ.",
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_keyboard(),
        )
    await state.set_state(AdminStates.waiting_for_banner)
    await callback.answer()


@router.message(AdminStates.waiting_for_banner, F.photo)
async def handle_banner_photo(message: Message, state: FSMContext) -> None:
    if not message.photo:
        await message.answer("ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ.", reply_markup=cancel_keyboard())
        return
    file_id = message.photo[-1].file_id
    await set_setting("banner_file_id", file_id)
    await state.clear()
    await message.answer(
        "✅ <b>ʙᴀɴɴᴇʀ ᴜᴘᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\n\nɴᴇᴡ /start ʙᴀɴɴᴇʀ ɪs ɴᴏᴡ ᴀᴄᴛɪᴠᴇ.",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_panel_keyboard(),
    )


# ── Broadcast ─────────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin_broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message:
        await callback.message.edit_text(
            "<blockquote><b>📢 ʙʀᴏᴀᴅᴄᴀsᴛ</b></blockquote>\n\nsᴇɴᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ᴀʟʟ ᴜsᴇʀs.",
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
    status_msg = await message.answer(f"📢 ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴛᴏ {len(users)} ᴜsᴇʀs...")
    sent, failed = 0, 0
    for user in users:
        try:
            await bot.send_message(chat_id=user["user_id"], text=broadcast_text, parse_mode=ParseMode.HTML)
            sent += 1
        except Exception:
            failed += 1
    await status_msg.edit_text(
        f"✅ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ.\n\n<b>sᴇɴᴛ:</b> {sent}\n<b>ғᴀɪʟᴇᴅ:</b> {failed}",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_panel_keyboard(),
    )


# ── Manage Plans ──────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin_plans")
async def cb_admin_plans(callback: CallbackQuery) -> None:
    plans = await get_active_plans()
    lines = ["<blockquote><b>📦 ᴘʟᴀɴs</b></blockquote>\n"]
    for p in plans:
        durations = p.get("durations", [])
        if durations:
            tiers = ", ".join(f"{d['label']} ₹{d['price']:.0f}" for d in durations)
        else:
            tiers = f"₹{p.get('price', '?')} / {p.get('duration_days', '?')}d"
        lines.append(f"• <b>{p['display_name']}</b>\n  {tiers}")
    lines.append("\n<i>sᴇɴᴅ /addplan ᴛᴏ ᴀᴅᴅ ᴀ ɴᴇᴡ ᴘʟᴀɴ.</i>")

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
        "<blockquote><b>➕ ᴀᴅᴅ ᴘʟᴀɴ — sᴛᴇᴘ 1/6</b></blockquote>\n\n"
        "ᴇɴᴛᴇʀ ᴛʜᴇ ᴘʟᴀɴ <b>ᴅɪsᴘʟᴀʏ ɴᴀᴍᴇ</b>:\n\n"
        "<i>ᴇxᴀᴍᴘʟᴇ: FLIX PREMIUM</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(AdminStates.addplan_name)


@router.message(StateFilter(AdminStates.addplan_name), F.text)
async def handle_addplan_name(message: Message, state: FSMContext) -> None:
    display_name = (message.text or "").strip()
    if not display_name:
        await message.answer("❌ ɴᴀᴍᴇ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ. ᴛʀʏ ᴀɢᴀɪɴ.")
        return
    internal_name = re.sub(r"[^a-z0-9_]", "", display_name.lower().replace(" ", "_"))
    if not internal_name:
        internal_name = "plan_" + str(abs(hash(display_name)))[:6]
    await state.update_data(display_name=display_name, name=internal_name)
    await message.answer(
        "<blockquote><b>➕ ᴀᴅᴅ ᴘʟᴀɴ — sᴛᴇᴘ 2/6</b></blockquote>\n\n"
        "ᴇɴᴛᴇʀ ᴛʜᴇ ᴘʟᴀɴ <b>ᴅᴇsᴄʀɪᴘᴛɪᴏɴ</b>:",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(AdminStates.addplan_description)


# ── Add Plan — Step 2: Description ───────────────────────────────────────────

@router.message(StateFilter(AdminStates.addplan_description), F.text)
async def handle_addplan_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=(message.text or "").strip())
    await message.answer(
        "<blockquote><b>➕ ᴀᴅᴅ ᴘʟᴀɴ — sᴛᴇᴘ 3/6</b></blockquote>\n\n"
        "ᴇɴᴛᴇʀ ᴀ <b>ᴅᴇᴍᴏ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋ</b> (e.g. <code>t.me/+xxx</code>):\n\n"
        "<i>sᴇɴᴅ <code>skip</code> ᴛᴏ ʟᴇᴀᴠᴇ ᴇᴍᴘᴛʏ.</i>",
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
        "<blockquote><b>➕ ᴀᴅᴅ ᴘʟᴀɴ — sᴛᴇᴘ 4/6</b></blockquote>\n\n"
        "sʜᴏᴜʟᴅ ᴜsᴇʀs ʙᴇ ʀᴇǫᴜɪʀᴇᴅ ᴛᴏ sᴇɴᴅ ᴀ <b>ᴘᴀʏᴍᴇɴᴛ ᴘʀᴏᴏғ sᴄʀᴇᴇɴsʜᴏᴛ</b>?",
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
            "<blockquote><b>➕ ᴀᴅᴅ ᴘʟᴀɴ — sᴛᴇᴘ 5/6</b></blockquote>\n\n"
            "sᴇʟᴇᴄᴛ ᴡʜɪᴄʜ <b>ᴅᴜʀᴀᴛɪᴏɴ ᴏᴘᴛɪᴏɴs</b> ᴛᴏ ᴏғғᴇʀ.\n"
            "ᴛᴀᴘ ᴛᴏ ᴛᴏɢɢʟᴇ ✅, ᴛʜᴇɴ ᴘʀᴇss <b>ᴅᴏɴᴇ</b>:",
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
        await callback.answer("⚠️ sᴇʟᴇᴄᴛ ᴀᴛ ʟᴇᴀsᴛ ᴏɴᴇ ᴅᴜʀᴀᴛɪᴏɴ!", show_alert=True)
        return

    selected.sort()
    label_map = {days: label for days, label in DURATION_OPTIONS}
    durations_to_price = [{"days": d, "label": label_map.get(d, f"{d}d")} for d in selected]

    await state.update_data(durations_to_price=durations_to_price, duration_prices=[], pricing_index=0)
    first = durations_to_price[0]

    if callback.message:
        await callback.message.edit_text(
            f"<blockquote><b>➕ ᴀᴅᴅ ᴘʟᴀɴ — sᴛᴇᴘ 6/6</b></blockquote>\n\n"
            f"ᴇɴᴛᴇʀ ᴘʀɪᴄᴇ ғᴏʀ <b>{first['label']}</b> (₹):",
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
        await message.answer("❌ ɪɴᴠᴀʟɪᴅ ᴘʀɪᴄᴇ. sᴇɴᴅ ᴀ ᴘᴏsɪᴛɪᴠᴇ ɴᴜᴍʙᴇʀ (e.g. 299).")
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
            f"<blockquote><b>➕ ᴀᴅᴅ ᴘʟᴀɴ — ᴘʀɪᴄɪɴɢ</b></blockquote>\n\n"
            f"ᴇɴᴛᴇʀ ᴘʀɪᴄᴇ ғᴏʀ <b>{nxt['label']}</b> (₹):",
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_keyboard(),
        )
    else:
        await state.update_data(duration_prices=duration_prices, pricing_index=idx, channels=[])
        await message.answer(
            "<blockquote><b>➕ ᴀᴅᴅ ᴘʟᴀɴ — ᴄʜᴀɴɴᴇʟs</b></blockquote>\n\n"
            "sᴇɴᴅ <b>ᴄʜᴀɴɴᴇʟ ɪɴᴠɪᴛᴇ ʟɪɴᴋ(s)</b> ᴏɴᴇ ʙʏ ᴏɴᴇ.\n"
            "ᴡʜᴇɴ ᴅᴏɴᴇ, sᴇɴᴅ <code>done</code>.\n\n"
            "<i>ᴄʜᴀɴɴᴇʟs ᴀᴅᴅᴇᴅ: 0</i>",
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
            f"✅ <b>ᴘʟᴀɴ ᴄʀᴇᴀᴛᴇᴅ:</b> {data['display_name']}\n\n"
            f"<b>ᴅᴜʀᴀᴛɪᴏɴs:</b>\n{tiers_text}\n\n"
            f"<b>ᴄʜᴀɴɴᴇʟs:</b> {len(channels)}\n"
            f"<b>ᴘᴀʏᴍᴇɴᴛ ᴘʀᴏᴏғ:</b> {'ʏᴇs' if data.get('payment_proof_required') else 'ɴᴏ'}",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_panel_keyboard(),
        )
    else:
        channels.append(text)
        await state.update_data(channels=channels)
        await message.answer(
            f"✅ ʟɪɴᴋ ᴀᴅᴅᴇᴅ. <i>ᴄʜᴀɴɴᴇʟs ᴀᴅᴅᴇᴅ: {len(channels)}</i>\n\n"
            "sᴇɴᴅ ᴀɴᴏᴛʜᴇʀ ʟɪɴᴋ ᴏʀ <code>done</code> ᴛᴏ ғɪɴɪsʜ.",
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_keyboard(),
        )


# ── Topup Wallet ──────────────────────────────────────────────────────────────

@router.message(Command("topup"))
async def cmd_topup(message: Message, state: FSMContext) -> None:
    await message.answer(
        "<blockquote><b>💰 ᴡᴀʟʟᴇᴛ ᴛᴏᴘ-ᴜᴘ</b></blockquote>\n\n"
        "sᴇɴᴅ ᴛʜᴇ ᴜsᴇʀ ɪᴅ ᴛᴏ ᴛᴏᴘ ᴜᴘ:",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(AdminStates.waiting_for_topup_user)


@router.message(AdminStates.waiting_for_topup_user, F.text)
async def handle_topup_user(message: Message, state: FSMContext) -> None:
    try:
        user_id = int(message.text or "")
    except ValueError:
        await message.answer("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ. sᴇɴᴅ ᴀ ɴᴜᴍᴇʀɪᴄ ᴛᴇʟᴇɢʀᴀᴍ ᴜsᴇʀ ɪᴅ.")
        return
    await state.update_data(topup_user_id=user_id)
    await message.answer(
        f"ᴜsᴇʀ ɪᴅ: <code>{user_id}</code>\n\nɴᴏᴡ sᴇɴᴅ ᴛʜᴇ ᴛᴏᴘ-ᴜᴘ ᴀᴍᴏᴜɴᴛ (e.g. <code>500</code>):",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(AdminStates.waiting_for_topup_amount)


@router.message(AdminStates.waiting_for_topup_amount, F.text)
async def handle_topup_amount(message: Message, state: FSMContext) -> None:
    try:
        amount = float(message.text or "")
    except ValueError:
        await message.answer("❌ ɪɴᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ. sᴇɴᴅ ᴀ ɴᴜᴍʙᴇʀ.")
        return
    data = await state.get_data()
    user_id = data.get("topup_user_id")
    await state.clear()
    await topup_wallet(user_id, amount, description=f"ᴀᴅᴍɪɴ ᴛᴏᴘ-ᴜᴘ ᴏғ ₹{amount}")
    await message.answer(
        f"✅ <b>ᴡᴀʟʟᴇᴛ ᴛᴏᴘᴘᴇᴅ ᴜᴘ!</b>\n\nᴜsᴇʀ <code>{user_id}</code> ʀᴇᴄᴇɪᴠᴇᴅ <b>₹{amount:.2f}</b>.",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_panel_keyboard(),
    )
