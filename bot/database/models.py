from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, TypedDict


class UserDoc(TypedDict, total=False):
    user_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    wallet_balance: float
    joined_at: datetime
    is_banned: bool


class PlanDoc(TypedDict, total=False):
    name: str
    display_name: str
    price: float
    duration_days: int
    description: str
    is_active: bool


class SubscriptionDoc(TypedDict, total=False):
    user_id: int
    plan_name: str
    start_date: datetime
    end_date: datetime
    is_active: bool
    channels: list[str]


class TransactionDoc(TypedDict, total=False):
    user_id: int
    amount: float
    type: str          # "purchase", "topup", "refund"
    plan_name: Optional[str]
    description: str
    created_at: datetime
    status: str        # "completed", "pending", "failed"


class SettingsDoc(TypedDict, total=False):
    key: str
    value: str


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
