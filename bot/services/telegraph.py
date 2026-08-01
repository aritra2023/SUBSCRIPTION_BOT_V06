from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

import aiohttp

from services.subscription import get_setting, set_setting
from utils.helpers import format_date

logger = logging.getLogger(__name__)

_TELEGRAPH_API = "https://api.telegra.ph"


async def _get_or_create_token() -> str:
    """Return stored Telegraph access token, creating a new account if needed."""
    token = await get_setting("telegraph_token")
    if token:
        return token

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{_TELEGRAPH_API}/createAccount",
            params={
                "short_name": "FlixVerse",
                "author_name": "Flix Verse Premium",
                "author_url": "https://t.me/FlixVersePremium",
            },
        ) as resp:
            data = await resp.json()

    if not data.get("ok"):
        raise RuntimeError(f"Telegraph createAccount failed: {data}")

    token = data["result"]["access_token"]
    await set_setting("telegraph_token", token)
    logger.info("Telegraph account created and token saved.")
    return token


def _build_content(
    user_name: str,
    user_id: int,
    transactions: list[dict],
    active_sub: Optional[dict],
) -> list[dict[str, Any]]:
    """Build Telegraph page content nodes with small-caps styling."""
    from utils.helpers import to_small_caps
    nodes: list[dict[str, Any]] = []

    sc = to_small_caps  # shorthand

    # ── User info ──────────────────────────────────────────────────────────────
    nodes.append({"tag": "p", "children": [
        {"tag": "b", "children": [f"◈ {sc('User')} : {sc(user_name)}"]},
        {"tag": "br"},
        {"tag": "i", "children": [f"ɪᴅ : {user_id}"]},
    ]})
    nodes.append({"tag": "hr"})

    # ── Active subscription ────────────────────────────────────────────────────
    if active_sub:
        end = active_sub.get("end_date")
        end_str = format_date(end) if end else "—"
        if end:
            end_aware = end.replace(tzinfo=timezone.utc) if end.tzinfo is None else end
            remaining = max(0, (end_aware - datetime.now(timezone.utc)).days)
        else:
            remaining = 0
        plan_display = sc(active_sub.get("plan_name", "—"))
        nodes.append({"tag": "h4", "children": [f"✅ {sc('Active Subscription')}"]})
        nodes.append({"tag": "p", "children": [
            f"» {sc('Plan')}      :  {plan_display}", {"tag": "br"},
            f"» {sc('Expires')}   :  {end_str}", {"tag": "br"},
            f"» {sc('Remaining')} :  {remaining} {sc('days')}",
        ]})
        nodes.append({"tag": "hr"})

    # ── Transaction history ────────────────────────────────────────────────────
    _TYPE_ICONS = {"purchase": "🛒", "topup": "💰", "refund": "↩️"}

    if not transactions:
        nodes.append({"tag": "p", "children": [
            {"tag": "i", "children": [f"» {sc('No purchase history found.')}"]},
        ]})
    else:
        nodes.append({"tag": "h4", "children": [
            f"📋 {sc('Purchase History')}  ({len(transactions)})"
        ]})
        for txn in transactions:
            amount = txn.get("amount", 0.0)
            sign = "+" if amount > 0 else ""
            txn_type = txn.get("type", "transaction")
            icon = _TYPE_ICONS.get(txn_type, "📄")
            desc = txn.get("description", "")
            date_str = format_date(txn["created_at"]) if txn.get("created_at") else "—"

            nodes.append({"tag": "p", "children": [
                {"tag": "b", "children": [f"{icon}  {sc(txn_type.capitalize())}  —  {sign}₹{abs(amount):.2f}"]},
                {"tag": "br"},
                f"  {sc('Note')}  :  {desc}",
                {"tag": "br"},
                {"tag": "i", "children": [f"  {sc('Date')}  :  {date_str}"]},
            ]})

    # ── Footer ─────────────────────────────────────────────────────────────────
    nodes.append({"tag": "hr"})
    nodes.append({"tag": "p", "children": [
        {"tag": "i", "children": [
            f"◈ {sc('Flix Verse Premium Bot')}  •  "
            f"{datetime.now(timezone.utc).strftime('%d %b %Y, %H:%M')} UTC"
        ]}
    ]})

    return nodes


async def create_history_page(
    user_name: str,
    user_id: int,
    transactions: list[dict],
    active_sub: Optional[dict] = None,
) -> str:
    """Create a Telegraph page with the user's history and return its URL."""
    token = await _get_or_create_token()
    content = _build_content(user_name, user_id, transactions, active_sub)

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{_TELEGRAPH_API}/createPage",
            json={
                "access_token": token,
                "title": f"History: {user_name}",
                "author_name": "Flix Verse Premium",
                "author_url": "https://t.me/FlixVersePremium",
                "content": content,
                "return_content": False,
            },
        ) as resp:
            data = await resp.json()

    if not data.get("ok"):
        raise RuntimeError(f"Telegraph createPage failed: {data}")

    return data["result"]["url"]
