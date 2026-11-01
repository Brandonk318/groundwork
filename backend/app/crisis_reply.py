"""Private crisis auto-reply (Brann's decision, 2026-10-31; open question #3).

When a post, comment, tip, question, answer or message matches crisis phrasing,
the AUTHOR (and only the author) gets a private in-app crisis resource message.

Anonymity rule, pinned by tests/test_crisis_reply.py:
- The post is NOT blocked, held or altered because of a crisis match.
- No staff-visible flag: the stored post carries no crisis decision, no needs_human.
- No moderation queue entry, no admin endpoint, no log or analytics line.
- The inbox entry holds no post id and no post text, only the resource message,
  and is readable solely by its owner via /api/safety/private_inbox.
Crisis copy is English (Spanish 988 option noted); other locales need human
review before translation (open question #9).
"""
import re
import uuid
from datetime import datetime, timezone

# Case-insensitive, word-boundary patterns.
_PATTERNS = [
    r"\bkill(ing)?\s+my\s*self\b",
    r"\bsuicid(e|al)\b",
    r"\bend(ing)?\s+(my|it)\s+(life|all)\b",
    r"\b(want|wanna|going)\s+(to\s+)?die\b",
    r"\bdon'?t\s+want\s+to\s+(be\s+alive|live|wake\s+up)\b",
    r"\b(hurt|cut|harm)(ing)?\s+my\s*self\b",
    r"\bself[\s-]?harm\b",
    r"\bover\s?dos(e|ed|ing)\b",
    r"\bod'?(ed|ing)\b",
    r"\b(about|going|gonna|fixing)\s+to\s+(use|relapse|shoot\s+up)\b",
    r"\brelaps(e|ing)\s+(tonight|right\s+now|now)\b",
    r"\bno\s+reason\s+to\s+live\b",
    r"\bbetter\s+off\s+dead\b",
]
# False-positive guards: phrases removed before matching.
_GUARDS = [
    r"\bsuicide\s+squad\b",
    r"\bsuicide\s+prevention\b",
    r"\bnaloxone\b.*\boverdose\s+(training|kit|class)\b",
    r"\boverdose\s+(training|kit|class|awareness|prevention)\b",
    r"\b(want|going)\s+to\s+die\s+(laughing|of\s+laughter)\b",
    r"\bdying\s+to\s+\w+\b",
]
_RX = re.compile("|".join(_PATTERNS), re.IGNORECASE)
_GUARD_RX = re.compile("|".join(_GUARDS), re.IGNORECASE)

MESSAGE = {
    "locale": "en",
    "needs_translation_review": True,  # open question #9: human review before any other locale
    "title": "You are not alone",
    "body": ("We noticed your words and wanted you to have this, privately. Only you can see this message. "
             "Call or text 988 (Suicide & Crisis Lifeline, press 2 for Spanish / en espanol). "
             "If you are in immediate danger, call 911. You can also text HOME to 741741 (Crisis Text Line). "
             "For overdose, call 911 and use naloxone if available."),
    "resources": [
        {"id": "988", "label": "Call or text 988", "tel": "tel:988", "sms": "sms:988"},
        {"id": "911", "label": "Emergency: 911", "tel": "tel:911"},
        {"id": "741741", "label": "Text HOME to 741741", "sms": "sms:741741?body=HOME"},
    ],
    "links": {"crisis_button": "/safety", "safe_contacts": "/safety#safe-contacts"},
}


def matches(text: str) -> bool:
    cleaned = _GUARD_RX.sub(" ", text or "")
    return bool(_RX.search(cleaned))


def notice() -> dict:
    return {**MESSAGE, "resources": [dict(r) for r in MESSAGE["resources"]], "links": dict(MESSAGE["links"]), "private": True}


async def deliver(db, user_id: str, text: str) -> dict | None:
    """Store an author-only inbox entry. No post id, no post text, no logging."""
    if not matches(text):
        return None
    doc = {"_id": uuid.uuid4().hex, "user_id": user_id, "kind": "crisis_resources",
           "message": notice(), "read": False, "created_at": datetime.now(timezone.utc).isoformat()}
    await db.private_inbox.insert_one(doc)
    return {**notice(), "inbox_id": doc["_id"]}
