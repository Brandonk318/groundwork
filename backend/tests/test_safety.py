from datetime import date, datetime, timedelta

import pytest

from app import locks, registry, safety, tiers


def test_crisis_button_and_relapse_always_free():
    for fid in ("crisis_button", "relapse_protocol"):
        f = registry.get(fid)
        assert f.tier == "free" and f.always_free and f.lock_exempt
        assert tiers.has_access("free", fid)
        assert tiers.has_access("nonsense", fid)


def test_paid_feature_gated_for_free_user():
    assert not tiers.has_access("free", "document_vault")
    assert tiers.has_access("paid", "document_vault")


@pytest.mark.parametrize("kind", ["week", "two_weeks", "month", "permanent"])
@pytest.mark.parametrize("target", ["crisis_button", "relapse_protocol", "safe_call_contacts", "data_wipe"])
def test_crisis_cannot_be_locked(kind, target):
    with pytest.raises(locks.LockError):
        locks.make_lock(target, kind, datetime(2026, 10, 28))


def test_filters_never_hide_crisis():
    today = date(2026, 10, 28)
    fs = [{"target": "crisis_button", "set_on": today}, {"target": "community_feed", "set_on": today}]
    assert [f["target"] for f in locks.active_filters(fs, today)] == ["community_feed"]


def test_filters_reset_daily():
    today = date(2026, 10, 28)
    assert locks.active_filters([{"target": "community_feed", "set_on": today - timedelta(days=1)}], today) == []


def test_lock_durations():
    start = datetime(2026, 10, 1)
    for kind, days in {"week": 7, "two_weeks": 14, "month": 30}.items():
        lock = locks.make_lock("community_feed", kind, start)
        assert lock["ends"] == start + timedelta(days=days)
        assert locks.is_active(lock, start + timedelta(days=days - 1))
        assert not locks.is_active(lock, start + timedelta(days=days))


def test_permanent_lock_one_reminder_after_a_month():
    start = datetime(2026, 10, 1)
    lock = locks.make_lock("ai_matching", "permanent", start)
    assert not locks.reminder_due(lock, start + timedelta(days=29))
    assert locks.reminder_due(lock, start + timedelta(days=30))
    lock["reminded"] = True
    assert not locks.reminder_due(lock, start + timedelta(days=90))
    lock2 = dict(locks.make_lock("ai_matching", "permanent", start), dont_remind=True)
    assert not locks.reminder_due(lock2, start + timedelta(days=31))


def test_rough_day_suggests_filters():
    assert locks.suggest_filters("rough")
    assert locks.suggest_filters("good") == []


def test_no_phone_numbers_in_public_member():
    pub = safety.public_member({"_id": 1, "handle": "j", "phone": "817-555-0100", "email": "a@b.c"})
    assert pub == {"handle": "j"}


def test_anonymous_post_hides_author():
    pub = safety.public_post({"_id": 1, "body": "hi", "anonymous": True, "author_id": "u1", "author_handle": "j"})
    assert "author_id" not in pub and "author_handle" not in pub
    assert pub["author"] == {"display": "Anonymous"}


def test_crisis_route_no_login(client):
    r = client.get("/api/safety/crisis")
    assert r.status_code == 200
    ids = [x["id"] for x in r.json()["resources"]]
    assert ids == ["988", "911"]


def test_relapse_placeholder_carries_crisis_lines(client):
    body = client.get("/api/safety/relapse_protocol/content").json()
    assert body["always_show"] == {"crisis": "988", "emergency": "911"}
    assert body["steps"] == []
