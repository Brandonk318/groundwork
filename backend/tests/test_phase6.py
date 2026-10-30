"""Phase 6: academy curriculum guardrails (course-generation skill)."""
from app.providers import COURSES

def reg(client, handle="phase6user", tier="paid"):
    r = client.post("/api/auth/register", json={"handle": handle, "password": "password123", "phone": "817-555-0100", "tier": tier})
    assert r.status_code == 201, r.text
    return r.json()
def auth(t): return {"Authorization": f"Bearer {t}"}

def test_all_tracks_draft_for_review():
    assert {c["id"] for c in COURSES} == {"parole_navigation", "job_interviews", "relapse_prevention", "small_business"}
    for c in COURSES:
        assert c["draft"] is True and "DRAFT" in c["title"]
        for m in c["modules"]:
            assert m["objective"] and m["quiz"]

def test_parole_content_defers_to_officer():
    pn = next(c for c in COURSES if c["id"] == "parole_navigation")
    assert "officer" in pn["modules"][0]["content"]
    sb = next(c for c in COURSES if c["id"] == "small_business")
    assert "officer" in sb["modules"][0]["content"]

def test_relapse_content_carries_crisis_line_not_advice():
    rp = next(c for c in COURSES if c["id"] == "relapse_prevention")
    assert "988" in rp["modules"][0]["content"] and "Not clinical advice" in rp["modules"][0]["content"]

def test_no_invented_prices_or_reentry_steps(client):
    u = reg(client)
    cat = client.get("/api/learning/courses", headers=auth(u["token"])).json()["courses"]
    assert cat == COURSES  # served exactly as authored; no invented figures
    assert all("33" not in m["content"] for c in cat for m in c["modules"])
    from app import tiers
    assert tiers.PLANS["paid"]["price_cents"] is None
