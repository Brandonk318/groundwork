"""Outbox for reminders (court dates, permanent-lock reminder, milestones). Trade Circle pattern; stub.

Enqueue only. Delivery (SMS/email/push) is not wired: no provider accounts in the scaffold.
"""
from datetime import datetime


async def enqueue(db, user_id, channel: str, kind: str, payload: dict, send_at: datetime) -> None:
    await db.outbox.insert_one({"user_id": user_id, "channel": channel, "kind": kind, "payload": payload,
                                "status": "queued", "next_attempt_at": send_at})
