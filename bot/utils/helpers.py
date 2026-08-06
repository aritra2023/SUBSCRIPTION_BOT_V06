from __future__ import annotations

from datetime import datetime, timezone

_SMALL_CAPS: dict[str, str] = {
    "A": "ᴀ", "B": "ʙ", "C": "ᴄ", "D": "ᴅ", "E": "ᴇ", "F": "ғ", "G": "ɢ",
    "H": "ʜ", "I": "ɪ", "J": "ᴊ", "K": "ᴋ", "L": "ʟ", "M": "ᴍ", "N": "ɴ",
    "O": "ᴏ", "P": "ᴘ", "Q": "ǫ", "R": "ʀ", "S": "s", "T": "ᴛ", "U": "ᴜ",
    "V": "ᴠ", "W": "ᴡ", "X": "x", "Y": "ʏ", "Z": "ᴢ",
    "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ғ", "g": "ɢ",
    "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ",
    "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ", "s": "s", "t": "ᴛ", "u": "ᴜ",
    "v": "ᴠ", "w": "ᴡ", "x": "x", "y": "ʏ", "z": "ᴢ",
}


def to_small_caps(text: str) -> str:
    return "".join(_SMALL_CAPS.get(ch, ch) for ch in text)


def format_date(dt: datetime) -> str:
    return dt.strftime("%d %b %Y, %H:%M UTC")


def days_remaining(end_date: datetime) -> int:
    now = datetime.now(timezone.utc)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)
    delta = end_date - now
    return max(0, delta.days)


def mention_html(user_id: int, name: str) -> str:
    return f'<a href="tg://user?id={user_id}">{to_small_caps(name)}</a>'


def format_duration_mins(minutes: int) -> str:
    """Convert a duration in minutes to a human-readable small-caps label."""
    if minutes < 60:
        unit = "ᴍɪɴ" if minutes == 1 else "ᴍɪɴs"
        return f"{minutes} {unit}"
    if minutes < 1440:
        hrs = minutes / 60
        hrs_display = int(hrs) if hrs == int(hrs) else round(hrs, 1)
        unit = "ʜʀ" if hrs_display == 1 else "ʜʀs"
        return f"{hrs_display} {unit}"
    days = minutes / 1440
    days_display = int(days) if days == int(days) else round(days, 1)
    unit = "ᴅᴀʏ" if days_display == 1 else "ᴅᴀʏs"
    return f"{days_display} {unit}"
