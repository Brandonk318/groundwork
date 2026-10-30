from collections import Counter

from app import registry, tiers

SPEC_FREE = {"crisis_button", "mood_checkins", "filters", "peer_messaging", "anonymous_posting",
             "milestone_celebrations", "twelve_step_locator", "resource_directory", "read_aloud", "multi_language"}
# relapse_protocol is free by the safety default
EXPECTED_FREE = SPEC_FREE | {"relapse_protocol"}
EXPECTED_PAID = {"ai_matching", "document_vault", "journey_portfolio", "video_posts", "courses",
                 "courses_life_skills", "virtual_venue"}
UPGRADED = {"journey_portfolio", "ai_matching", "community_feed", "filters", "virtual_venue"}


def test_exactly_45_features_in_spec_order():
    assert len(registry.FEATURES) == 49
    assert [f.n for f in registry.FEATURES] == list(range(1, 50))
    assert len(registry.BY_ID) == 49  # ids unique


def test_side_counts_match_spec():
    assert Counter(f.side for f in registry.FEATURES) == registry.SIDES == {"reentry": 18, "recovery": 10, "own": 21}


def test_courses_listed_twice_one_module():
    mods = [f.to_dict()["module"] for f in registry.FEATURES]
    assert mods.count("courses") == 2
    assert len(set(mods)) == 48


def test_phase3_addons_registered_working():
    for fid, group in (("carpool_board", "support"), ("community_groups_directory", "support"),
                       ("housing_savings", "journey"), ("music_player", "platform")):
        f = registry.get(fid)
        assert f.status == "working" and f.group == group and f.tier == "unassigned"


def test_tiers_match_spec():
    assert set(tiers.features_for("free")) == EXPECTED_FREE
    assert set(tiers.features_for("paid")) == EXPECTED_PAID
    assert set(tiers.unassigned()) == set(registry.BY_ID) - EXPECTED_FREE - EXPECTED_PAID
    assert all(f.tier in ("free", "paid", "unassigned") for f in registry.FEATURES)


def test_no_invented_prices():
    assert tiers.PLANS["paid"]["price_cents"] is None


def test_upgraded_vs_stock():
    assert {f.id for f in registry.FEATURES if f.build == "upgraded"} == UPGRADED
    assert all(f.build in ("upgraded", "stock") for f in registry.FEATURES)


def test_everything_is_a_stub():
    working = {f.id for f in registry.FEATURES if f.status == "working"}
    assert "crisis_button" in working and "mood_checkins" in working
    assert {f.status for f in registry.FEATURES} <= {"stub", "working"}


def test_resource_directory_excludes_food_housing():
    assert "NOT food/housing" in registry.get("resource_directory").name


EXPECTED_33 = [
    "Order your birth certificate", "Request your Social Security card", "Start the state ID application",
    "Set goals with your case manager", "Plan your ride home", "Line up one support contact",
    "Find a safe place to stay (call 211 or local housing resources)", "Find food for this week (call 211 or a local food pantry)",
    "Check your release papers and deadlines", "Confirm your first check-in date and conditions", "Save 988 and 911 in your phone",
    "Get your state ID", "Get a phone, email and free internet access", "Put every court date and check-in on a calendar", "Contact local reentry services",
    "Know your supervision conditions", "Check your fines, fees and restitution", "Check your driver's license status",
    "Enroll in Medicaid, and SNAP if you need it", "Get your health records", "Make a medication plan", "Book a doctor's appointment",
    "Book a mental health appointment", "Get a substance use evaluation", "Find a support group",
    "Build your resume", "Apply to second-chance employers", "Look into training or certificates",
    "Open a bank account and make a budget", "Start rebuilding your credit", "Reconnect with family, and handle child support if it applies",
    "Set a daily routine", "Set one long-term goal and celebrate your 90-day milestone",
]
EXPECTED_SECTIONS = [
    ("before_release", "Before release", [1, 2, 3, 4, 5, 6]), ("first_48_hours", "First 48 hours", [7, 8, 9, 10, 11]),
    ("first_week", "First week", [12, 13, 14, 15]), ("legal_and_supervision", "Legal and supervision", [16, 17, 18]),
    ("health", "Health", [19, 20, 21, 22, 23, 24, 25]), ("work", "Work", [26, 27, 28]), ("stability", "Stability", [29, 30, 31, 32, 33]),
]

def test_reentry_steps_are_branns_exact_33():
    import json
    from pathlib import Path
    data = json.loads((Path(registry.__file__).parent / "data" / "reentry_steps.json").read_text())
    assert [s["title"] for s in data["steps"]] == EXPECTED_33
    assert [s["id"] for s in data["steps"]] == list(range(1, 34))
    assert [(s["id"], s["title"], s["step_ids"]) for s in data["sections"]] == EXPECTED_SECTIONS
    for s in data["steps"]:
        sec = next(x for x in data["sections"] if x["id"] == s["section"])
        assert s["id"] in sec["step_ids"] and s["section_title"] == sec["title"]
    assert data["milestone_days"] == list(registry.MILESTONE_DAYS) == [30, 60, 90, 180, 365]
