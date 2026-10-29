"""Filters and locks (registry #33 filters, #34 locks). Pure policy, no I/O yet.

- Mood-triggered filters: a rough-day check-in SUGGESTS filters; the member accepts.
- Filters reset daily (member's local day).
- Locks: week / two weeks / month, or permanent.
- Permanent locks: ONE reminder 30 days after the lock, unless "don't remind again".
- Nothing here can ever hide a lock-exempt feature (crisis button etc.).
"""
from datetime import date, datetime, timedelta

from .safety import can_be_hidden

LOCK_DURATIONS = {"week": 7, "two_weeks": 14, "month": 30}
PERMANENT_REMINDER_DAYS = 30
ROUGH_MOODS = {"rough", "struggling", "craving"}


class LockError(ValueError):
    pass


def make_lock(target: str, kind: str, start: datetime) -> dict:
    if not can_be_hidden(target):
        raise LockError(f"{target} can never be locked")
    if kind == "permanent":
        return {"target": target, "kind": kind, "start": start, "ends": None, "reminded": False, "dont_remind": False}
    if kind not in LOCK_DURATIONS:
        raise LockError(f"unknown lock kind {kind!r}")
    return {"target": target, "kind": kind, "start": start, "ends": start + timedelta(days=LOCK_DURATIONS[kind]),
            "reminded": False, "dont_remind": False}


def is_active(lock: dict, now: datetime) -> bool:
    return lock["ends"] is None or now < lock["ends"]


def reminder_due(lock: dict, now: datetime) -> bool:
    return (lock["kind"] == "permanent" and not lock["reminded"] and not lock["dont_remind"]
            and now >= lock["start"] + timedelta(days=PERMANENT_REMINDER_DAYS))


def suggest_filters(mood: str) -> list[str]:
    """Rough day -> suggest (not force) filters. Suggestions are placeholders for Brann's filter list."""
    return ["hide_triggering_content", "quiet_dms"] if mood in ROUGH_MOODS else []


def active_filters(filters: list[dict], today: date) -> list[dict]:
    """Daily reset: filters set on an earlier day no longer apply."""
    return [f for f in filters if f["set_on"] == today and can_be_hidden(f.get("target", ""))]
