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
    "portfolio_shares": "user_id",
    "day_one_archive": "user_id",
    "safe_contacts": "user_id",
    "family_links": "member_id",
    "outbox": "user_id",
    "private_inbox": "user_id",
    "milestones": "user_id",
    "checklist_custom_steps": "user_id",
    "checklist_tips": "author_id",
    "interview_sessions": "user_id",
    "micro_gigs": "user_id",
    "gig_applications": "user_id",
    "course_progress": "user_id",
    "mentors": "user_id",
    "mentorship_requests": "user_id",
    "locations": "user_id",
    "ride_requests": "user_id",
    "ride_offers": "user_id",
    "accountability": "user_id",
    "events": "user_id",
    "event_rsvps": "user_id",
    "program_groups": "user_id",
    "group_memberships": "user_id",
    "virtual_meetings": "user_id",
    "media_posts": "user_id",
    "qa_questions": "author_id",
    "qa_answers": "author_id",
    "token_ledger": "user_id",
    "merch_claims": "user_id",
    "share_cards": "user_id",
    "match_profiles": "user_id",
    "matches": "user_id",
    "match_decisions": "user_id",
    "match_overrides": "user_id",
    "carpool_entries": "user_id",
    "ride_contacts": "user_id",
    "ride_ping_sessions": "user_id",
    "savings_goals": "user_id",
    "housing_plan": "user_id",
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
