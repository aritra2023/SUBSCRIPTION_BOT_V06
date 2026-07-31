from __future__ import annotations

from datetime import datetime, timezone


def format_date(dt: datetime) -> str:
    return dt.strftime("%d %b %Y, %H:%M UTC")


def days_remaining(end_date: datetime) -> int:
    now = datetime.now(timezone.utc)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)
    delta = end_date - now
    return max(0, delta.days)


def mention_html(user_id: int, name: str) -> str:
    return f'<a href="tg://user?id={user_id}">{name}</a>'
