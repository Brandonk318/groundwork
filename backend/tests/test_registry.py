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
    assert len(registry.FEATURES) == 45
    assert [f.n for f in registry.FEATURES] == list(range(1, 46))
    assert len(registry.BY_ID) == 45  # ids unique


def test_side_counts_match_spec():
    assert Counter(f.side for f in registry.FEATURES) == registry.SIDES == {"reentry": 18, "recovery": 10, "own": 17}


def test_courses_listed_twice_one_module():
    mods = [f.to_dict()["module"] for f in registry.FEATURES]
    assert mods.count("courses") == 2
    assert len(set(mods)) == 44


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
    assert {f.status for f in registry.FEATURES} == {"stub"}


def test_resource_directory_excludes_food_housing():
    assert "NOT food/housing" in registry.get("resource_directory").name


def test_reentry_steps_not_invented():
    import json
    from pathlib import Path
    data = json.loads((Path(registry.__file__).parent / "data" / "reentry_steps.json").read_text())
    assert data["steps"] == []
    assert data["milestone_days"] == list(registry.MILESTONE_DAYS) == [30, 60, 90, 180, 365]
