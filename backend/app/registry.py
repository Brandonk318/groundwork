"""The 45-feature registry: the single source of truth for what the app is.

Faithful to Brann's spec (2026-10-28): 18 reentry + 10 recovery + 17 own
additions = 45 entries. "courses" appears twice in the spec (reentry #14 and
own-addition #45); both entries stay in the registry and point at ONE module
(`module="courses"`). See docs/features.md for the overlap note.

How the 17 own additions were counted: "mood-triggered filters" + "daily reset
of filters" are one feature (`filters`, matching the spec's FREE-tier word
"filters"), and "time-limited locks" + "permanent locks" + "one reminder after
a month" are one feature (`locks`). Listing them separately gives 20, not 17.

tier:   "free" | "paid" | "unassigned" (Brann decides; never invent a price)
build:  "upgraded" (custom-built) | "stock" (ship from open-source modules)
status: "stub" until a module really works.

Safety flags:
  always_free  -> can never be gated by a plan (crisis button, relapse protocol)
  lock_exempt  -> locks and filters can never hide or block it
"""
from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Feature:
    n: int
    id: str
    name: str
    side: str  # reentry | recovery | own
    group: str  # router group under app/routers
    tier: str
    build: str = "stock"
    status: str = "stub"
    module: str = ""
    always_free: bool = False
    lock_exempt: bool = False
    notes: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["module"] = self.module or self.id
        return d


F = Feature
FEATURES: tuple[Feature, ...] = (
    # ---- REENTRY (18) ----
    F(1, "reentry_checklist", "33-step reentry checklist (milestones 30/60/90/180/365 days)", "reentry", "reentry", "unassigned",
      notes="Brann's 33 steps are NOT provided. Data lives in app/data/reentry_steps.json; never invent them."),
    F(2, "court_calendar", "Court-date calendar with reminders", "reentry", "reentry", "unassigned"),
    F(3, "job_board", "Job board filtered to second-chance employers", "reentry", "work", "unassigned"),
    F(4, "resume_builder", "Resume builder", "reentry", "work", "unassigned"),
    F(5, "interview_coach", "AI interview coach (mock sessions + scoring)", "reentry", "work", "unassigned"),
    F(6, "application_tracker", "Application tracker", "reentry", "work", "unassigned"),
    F(7, "document_vault", "Encrypted document vault (IDs, release papers)", "reentry", "safety", "paid",
      notes="Encrypted at rest with a per-user key envelope (app/vault_crypto.py)."),
    F(8, "data_wipe", "One-tap data wipe", "reentry", "safety", "unassigned", lock_exempt=True,
      notes="Really deletes: every user collection + crypto-shreds the vault key (app/wipe.py)."),
    F(9, "resource_directory", "Resource directory (legal aid, treatment, transit; NOT food/housing)", "reentry", "support", "free"),
    F(10, "mentorship", "Mentorship", "reentry", "support", "unassigned"),
    F(11, "twelve_step_locator", "Twelve-step meeting locator", "reentry", "support", "free"),
    F(12, "counseling_referrals", "Counseling referrals", "reentry", "support", "unassigned"),
    F(13, "community_feed", "Community feed (one feed for everyone)", "reentry", "community", "unassigned", build="upgraded"),
    F(14, "courses", "Courses", "reentry", "learning", "paid", module="courses",
      notes="Same module as #45. Reuses the Contractor Academy video pipeline + quiz engine."),
    F(15, "events", "Events", "reentry", "community", "unassigned"),
    F(16, "token_rewards", "Token rewards", "reentry", "journey", "unassigned",
      notes="In-app points ledger. Not cryptocurrency."),
    F(17, "read_aloud", "Read-aloud", "reentry", "platform", "free"),
    F(18, "multi_language", "Multi-language (en, es, fr, hi, vi, ar, tl, ht)", "reentry", "platform", "free"),
    # ---- RECOVERY (10) ----
    F(19, "mood_checkins", "Mood check-ins", "recovery", "wellbeing", "free"),
    F(20, "crisis_button", "Crisis button (988 + 911)", "recovery", "safety", "free", always_free=True, lock_exempt=True),
    F(21, "geolocation", "Geolocation (opt-in)", "recovery", "support", "unassigned"),
    F(22, "anonymous_posting", "Anonymous posting", "recovery", "community", "free"),
    F(23, "program_groups", "Program-specific groups", "recovery", "community", "unassigned"),
    F(24, "peer_messaging", "Peer messaging (no phone numbers exposed)", "recovery", "community", "free"),
    F(25, "milestone_celebrations", "Milestone celebrations", "recovery", "journey", "free"),
    F(26, "needs_a_ride", "Needs-a-ride", "recovery", "support", "unassigned"),
    F(27, "safe_call_contacts", "Sponsor / safe-call contacts one tap away", "recovery", "safety", "unassigned", lock_exempt=True),
    F(28, "virtual_meetings", "Virtual meetings", "recovery", "community", "unassigned"),
    # ---- OWN ADDITIONS (17) ----
    F(29, "video_posts", "Video posts", "own", "community", "paid",
      notes="Spec PAID item is 'video hosting'; mapped here. Confirm whether short clips stay free."),
    F(30, "photo_posts", "Photo posts", "own", "community", "unassigned"),
    F(31, "journey_portfolio", "Journey portfolio (private by default, shareable when ready)", "own", "journey", "paid", build="upgraded"),
    F(32, "ai_matching", "AI dating + friend matching (agents negotiate first; see why, override, rematch)", "own", "matching", "paid", build="upgraded"),
    F(33, "filters", "Mood-triggered filters + daily filter reset", "own", "wellbeing", "free", build="upgraded"),
    F(34, "locks", "Locks: time-limited (week/2wk/month), permanent, one reminder after a month", "own", "wellbeing", "unassigned"),
    F(35, "merch_rewards", "Merch rewards (discreet, limited drops per milestone; 30 + 90 day anchors)", "own", "journey", "unassigned"),
    F(36, "virtual_venue", "Virtual venue preview (Three.js/WebGL 3D walkthrough)", "own", "venue", "paid", build="upgraded"),
    F(37, "micro_gigs", "Micro-gig board", "own", "work", "unassigned"),
    F(38, "accountability_partners", "Peer accountability partners (matched 2-to-1)", "own", "support", "unassigned"),
    F(39, "relapse_protocol", "Relapse protocol (calm first 24 hours after a slip)", "own", "safety", "free", always_free=True, lock_exempt=True,
      notes="Free by the safety default, though the spec's FREE list doesn't name it."),
    F(40, "voice_notes", "Voice notes", "own", "community", "unassigned"),
    F(41, "anonymous_qa", "Anonymous Q&A (further-along members answer newcomers)", "own", "community", "unassigned"),
    F(42, "progress_share_card", "Progress share card (one image of journey stats)", "own", "journey", "unassigned"),
    F(43, "day_one_archive", "Day-one archive (sealed note/video, unlocks at a milestone)", "own", "journey", "unassigned"),
    F(44, "family_mode", "Family mode (separate login; member controls visibility)", "own", "family", "unassigned"),
    F(45, "courses_life_skills", "Courses: life skills (parole navigation, interviews, relapse prevention, small business)", "own", "learning", "paid",
      module="courses", notes="Same module as #14. Fresh curriculum on the academy engine."),
)

BY_ID = {f.id: f for f in FEATURES}
SIDES = {"reentry": 18, "recovery": 10, "own": 17}
GROUPS = sorted({f.group for f in FEATURES})
MILESTONE_DAYS = (30, 60, 90, 180, 365)


def all_features() -> list[dict]:
    return [f.to_dict() for f in FEATURES]


def get(feature_id: str) -> Feature:
    return BY_ID[feature_id]


def lock_exempt_ids() -> set[str]:
    return {f.id for f in FEATURES if f.lock_exempt}
