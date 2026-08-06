from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import aiohttp

from services.subscription import get_setting, set_setting
from utils.helpers import format_date, to_small_caps

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
                "short_name": "PremiumVerse",
                "author_name": "Premium Verse Premium",
                "author_url": "https://t.me/PremiumVersePremium",
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
) -> list[dict[str, Any]]:
    """Build Telegraph page content nodes with small-caps styling."""
    nodes: list[dict[str, Any]] = []

    sc = to_small_caps  # shorthand

    # ── User info ──────────────────────────────────────────────────────────────
    nodes.append({"tag": "p", "children": [
        {"tag": "b", "children": [f"◈ {sc('User')} : {sc(user_name)}"]},
        {"tag": "br"},
        {"tag": "i", "children": [f"ɪᴅ : {user_id}"]},
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
            f"◈ {sc('Premium Verse Premium Bot')}  •  "
            f"{datetime.now(timezone.utc).strftime('%d %b %Y, %H:%M')} UTC"
        ]}
    ]})

    return nodes


async def create_history_page(
    user_name: str,
    user_id: int,
    transactions: list[dict],
) -> str:
    """Create a Telegraph page with the user's history and return its URL."""
    token = await _get_or_create_token()
    content = _build_content(user_name, user_id, transactions)

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{_TELEGRAPH_API}/createPage",
            json={
                "access_token": token,
                "title": f"History: {user_name}",
                "author_name": "Premium Verse Premium",
                "author_url": "https://t.me/PremiumVersePremium",
                "content": content,
                "return_content": False,
            },
        ) as resp:
            data = await resp.json()

    if not data.get("ok"):
        raise RuntimeError(f"Telegraph createPage failed: {data}")

    return data["result"]["url"]
