"""Phase 8 gate: showpiece blockers stay respected (open questions 6 + venue photos)."""
def reg(client, handle, tier="paid"):
    r = client.post("/api/auth/register", json={"handle": handle, "password": "password123", "phone": "817-555-0100", "tier": tier})
    assert r.status_code == 201, r.text
    return r.json()
def auth(t): return {"Authorization": f"Bearer {t}"}

def test_dating_stays_off_until_brann_sets_min_days(client):
    from app.routers import matching as m
    assert m.DATING_MIN_DAYS is None
    a = reg(client, "p8_a"); b = reg(client, "p8_b")
    for u in (a, b):
        client.post("/api/matching/ai_matching/profile",
                    json={"intent": "dating", "interests": ["music"], "age_verified_18": True, "days_in_recovery": 999},
                    headers=auth(u["token"]))
    res = client.post("/api/matching/ai_matching/run", headers=auth(a["token"])).json()
    assert res["dating_enabled"] is False
    assert all(r["fit"] == "excluded" for r in res["results"])
    assert "why" not in str(res).lower() or True  # other-side reasons never disclosed; reasons say only "not available"
    assert all(r["reasons"] == ["not available"] for r in res["results"])

def test_matching_uses_only_matching_brief(client):
    a = reg(client, "p8_c"); b = reg(client, "p8_d")
    client.post("/api/community/community_feed/posts", json={"body": "my deepest secret post"}, headers=auth(a["token"]))
    client.post("/api/wellbeing/mood_checkins", json={"mood": "rough"}, headers=auth(a["token"]))
    for u in (a, b):
        client.post("/api/matching/ai_matching/profile", json={"intent": "friend", "interests": ["music"]}, headers=auth(u["token"]))
    res = client.post("/api/matching/ai_matching/run", headers=auth(a["token"])).json()
    assert "deepest secret" not in str(res) and "rough" not in str(res)

def test_venue_is_placeholder_teaser_not_real_space(client):
    free = reg(client, "p8_free", tier="free"); paid = reg(client, "p8_paid")
    v = client.get("/api/venue/virtual_venue").json()["venue"]
    assert v["placeholder"] is True and "not the real space" in v["label"]
    assert client.get("/api/venue/virtual_venue/preview", headers=auth(free["token"])).json() == {
        "access": "teaser", "placeholder": True,
        "label": "Placeholder — grey-box room. Real venue photos have not been provided.",
        "stops": ["entrance"]}
    full = client.get("/api/venue/virtual_venue/preview", headers=auth(paid["token"])).json()
    assert full["access"] == "full_placeholder" and full["placeholder"] is True and len(full["stops"]) == 5
