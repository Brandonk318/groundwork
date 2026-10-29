"""One-tap data wipe: actually deletes. Not a soft-delete, not a flag.

Every collection that holds member data MUST be listed in USER_COLLECTIONS
(field = the owner key). A test pins that wipe empties all of them.
Open question: any legal-hold / audit-log retention (see docs/open-questions.md).
"""
USER_COLLECTIONS = {
    "users": "_id",
    "vault_keys": "user_id",
    "vault_docs": "user_id",
    "checklist_progress": "user_id",
    "court_dates": "user_id",
    "applications": "user_id",
    "resumes": "user_id",
    "mood_checkins": "user_id",
    "filters": "user_id",
    "locks": "user_id",
    "posts": "author_id",
    "messages": "sender_id",
    "portfolio_items": "user_id",
    "day_one_archive": "user_id",
    "safe_contacts": "user_id",
    "family_links": "member_id",
    "outbox": "user_id",
}


async def wipe_user(db, user_id) -> dict:
    counts = {}
    for coll, field in USER_COLLECTIONS.items():
        res = await db[coll].delete_many({field: user_id})
        counts[coll] = res.deleted_count
    # Messages received by the member are removed too.
    res = await db.messages.delete_many({"recipient_id": user_id})
    counts["messages"] += res.deleted_count
    return counts
