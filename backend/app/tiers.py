"""Plans and what each includes. Every feature gate reads this file (pattern from Trade Circle's tiers.py).

Prices are NOT set: Brann decides. Features marked "unassigned" in the
registry are listed under neither plan until he does.
"""
from fastapi import HTTPException, status

from . import registry

TIER_ORDER = {"free": 0, "paid": 1}

PLANS = {
    "free": {"name": "Free", "price_cents": 0},
    "paid": {"name": "Paid", "price_cents": None},  # None = not decided yet. Never invent a price.
}


def features_for(tier: str) -> list[str]:
    return [f.id for f in registry.FEATURES if f.tier == tier]


def unassigned() -> list[str]:
    return [f.id for f in registry.FEATURES if f.tier == "unassigned"]


def plan_table() -> dict:
    return {
        "plans": PLANS,
        "free": features_for("free"),
        "paid": features_for("paid"),
        "unassigned": unassigned(),
    }


def has_access(user_tier: str, feature_id: str) -> bool:
    f = registry.get(feature_id)
    if f.always_free or f.tier == "free":
        return True
    if f.tier == "unassigned":
        return True  # open during the scaffold; gate once Brann assigns it
    return TIER_ORDER.get(user_tier, 0) >= TIER_ORDER[f.tier]


def require(user_tier: str, feature_id: str) -> None:
    if not has_access(user_tier, feature_id):
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, f"{feature_id} is on the paid plan")
