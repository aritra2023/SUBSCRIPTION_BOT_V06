from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, TypedDict


class UserDoc(TypedDict, total=False):
    user_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    wallet_balance: float
    referral_points: int
    auto_renew: bool
    joined_at: datetime
    is_banned: bool
    is_blocked: bool


class DurationTier(TypedDict):
    minutes: int
    label: str
    price: float


class PlanDoc(TypedDict, total=False):
    name: str
    display_name: str
    description: str
    demo_link: str
    payment_proof_required: bool
    durations: list[DurationTier]
    channels: list[str]
    is_active: bool
    price: float
    duration_days: int


class SubscriptionDoc(TypedDict, total=False):
    user_id: int
    plan_name: str
    duration_minutes: int
    price_paid: float
    start_date: datetime
    end_date: datetime
    is_active: bool
    channels: list[str]
    joined_channels: list[int]   # indices of channels the user has already joined


class TransactionDoc(TypedDict, total=False):
    user_id: int
    amount: float
    type: str
    plan_name: Optional[str]
    description: str
    created_at: datetime
    status: str


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
