def reg(client, handle="fuser", tier="free"):
    r = client.post("/api/auth/register", json={"handle": handle, "password": "password123", "tier": tier, "phone": "817-555-0100"})
    assert r.status_code == 201, r.text
    return r.json()
def auth(t): return {"Authorization": f"Bearer {t}"}

def test_groups_directory_sample_only(client):
    b = client.get("/api/support/community_groups_directory").json()
    assert b["sample"] is True and "not real listings" in b["note"]
    assert {g["kind"] for g in b["groups"]} >= {"recovery", "reentry", "faith"}
    assert all(g["sample"] is True for g in b["groups"]) and "817" not in str(b)
    assert all("phone" not in g for g in b["groups"])
    assert client.get("/api/support/community_groups_directory?kind=faith").json()["groups"][0]["city"] == "Fort Worth"

def test_carpool_optin_city_level_moderated(client):
    a = reg(client, "car_a"); b = reg(client, "car_b")
    r = client.post("/api/support/carpool_board/entries", json={"city": "Fort Worth", "meeting_source": "twelve_step", "meeting_id": "m1", "note": "Heading to the Monday meeting."}, headers=auth(a["token"]))
    assert r.status_code == 201, r.text
    assert r.json()["precision"] == "city" and "lat" not in str(r.json())
    g = client.post("/api/support/carpool_board/entries", json={"city": "Fort Worth", "meeting_source": "community_group", "meeting_id": "g1", "note": "See you there."}, headers=auth(a["token"]))
    assert g.status_code == 201
    assert client.post("/api/support/carpool_board/entries", json={"city": "X", "meeting_source": "twelve_step", "meeting_id": "nope"}, headers=auth(a["token"])).status_code == 404
    assert client.post("/api/support/carpool_board/entries", json={"city": "X", "meeting_source": "twelve_step", "meeting_id": "m1", "note": "sell drugs"}, headers=auth(a["token"])).status_code == 422
    lst = client.get("/api/support/carpool_board/entries?meeting_id=m1", headers=auth(b["token"])).json()["entries"]
    assert len(lst) == 1 and lst[0]["member"]["handle"] == "car_a" and "817-555" not in str(lst)
    assert "phone" not in str(lst)
    assert client.get("/api/support/carpool_board/matches?meeting_id=m1", headers=auth(b["token"])).json() == {"meeting_id": "m1", "carpool_count": 1}
    off = client.post("/api/support/carpool_board/entries", json={"city": "Fort Worth", "meeting_source": "twelve_step", "meeting_id": "m1", "opt_in": False}, headers=auth(a["token"]))
    assert off.json() == {"opt_in": False}
    assert client.get("/api/support/carpool_board/matches?meeting_id=m1", headers=auth(b["token"])).json()["carpool_count"] == 0

def test_needs_a_ride_fallback_secondary(client):
    a = reg(client, "fb_a"); b = reg(client, "fb_b")
    first = client.get("/api/support/needs_a_ride/fallback?meeting_id=m2", headers=auth(b["token"])).json()
    assert first == {"meeting_id": "m2", "carpool_count": 0, "show_fallback": True, "note": first["note"]}
    assert "carpool board first" in first["note"]
    client.post("/api/support/carpool_board/entries", json={"city": "Fort Worth", "meeting_source": "twelve_step", "meeting_id": "m2"}, headers=auth(a["token"]))
    second = client.get("/api/support/needs_a_ride/fallback?meeting_id=m2", headers=auth(b["token"])).json()
    assert second["show_fallback"] is False and second["carpool_count"] == 1

def test_ride_family_contacts_cap_quiet_verify(client):
    u = reg(client, "fam_u")
    ids = []
    for i in range(10):
        r = client.post("/api/support/needs_a_ride/family/contacts", json={"label": f"Driver {i}", "member_handle": "fam_u"}, headers=auth(u["token"]))
        assert r.status_code == 201, r.text
        ids.append(r.json()["_id"])
    assert client.post("/api/support/needs_a_ride/family/contacts", json={"label": "Extra"}, headers=auth(u["token"])).status_code == 422
    # quiet hours update
    q = client.patch(f"/api/support/needs_a_ride/family/contacts/{ids[0]}", json={"quiet_start": 0, "quiet_end": 23}, headers=auth(u["token"]))
    assert q.json()["quiet_start"] == 0 and q.json()["verified"] is False
    # unverified drivers cannot be pinged
    assert client.post("/api/support/needs_a_ride/family/ping/start", headers=auth(u["token"])).status_code == 422
    ap = client.post(f"/api/support/needs_a_ride/family/contacts/{ids[1]}/approve", json={"approved_by": "Mom", "relationship": "parent"}, headers=auth(u["token"]))
    assert ap.json()["verified"] is True and "phone" not in str(ap.json())
    ap2 = client.post(f"/api/support/needs_a_ride/family/contacts/{ids[2]}/approve", json={"approved_by": "Aunt Jo", "relationship": "aunt"}, headers=auth(u["token"]))
    assert ap2.status_code == 200
    start = client.post("/api/support/needs_a_ride/family/ping/start", headers=auth(u["token"])).json()
    assert start["status"] == "awaiting" and start["timeout_seconds"] == 120
    assert start["contact"]["label"] == "Driver 1"  # ids[0] is quiet 0-23, skipped
    assert client.post("/api/support/needs_a_ride/family/ping/next", json={"session_id": start["session_id"], "confirm": False}, headers=auth(u["token"])).status_code == 422
    nxt = client.post("/api/support/needs_a_ride/family/ping/next", json={"session_id": start["session_id"], "confirm": True}, headers=auth(u["token"])).json()
    assert nxt["contact"]["label"] == "Driver 2"
    st = client.get(f"/api/support/needs_a_ride/family/ping/{start['session_id']}", headers=auth(u["token"])).json()
    assert st["remaining"] == 0
    end = client.post("/api/support/needs_a_ride/family/ping/next", json={"session_id": start["session_id"], "confirm": True}, headers=auth(u["token"])).json()
    assert end["status"] == "done"
    assert client.delete(f"/api/support/needs_a_ride/family/contacts/{ids[9]}", headers=auth(u["token"])).status_code == 200

def test_housing_savings_goals_calc_plan(client):
    u = reg(client, "house_u")
    g = client.post("/api/journey/housing_savings/goals", json={"name": "Deposit", "target_cents": 120000, "saved_cents": 20000}, headers=auth(u["token"]))
    assert g.status_code == 201
    gid = g.json()["_id"]
    calc = client.post("/api/journey/housing_savings/calculator", json={"target_cents": 120000, "saved_cents": 20000, "monthly_cents": 25000}, headers=auth(u["token"])).json()
    assert calc == {"target_cents": 120000, "saved_cents": 20000, "monthly_cents": 25000, "remaining_cents": 100000, "months": 4}
    assert client.patch(f"/api/journey/housing_savings/goals/{gid}", json={"saved_cents": 45000}, headers=auth(u["token"])).json()["saved_cents"] == 45000
    plan = client.get("/api/journey/housing_savings/plan", headers=auth(u["token"])).json()
    assert len(plan["steps"]) == 5 and all(s["done"] is False for s in plan["steps"])
    assert "211" in plan["note"] and "does not provide housing" in plan["note"]
    assert "provider" not in str(plan).lower().replace("providers", "X") or "does not partner" in plan["note"]
    assert client.post("/api/journey/housing_savings/plan/check", json={"step_id": "hp1", "done": True}, headers=auth(u["token"])).status_code == 200
    plan2 = client.get("/api/journey/housing_savings/plan", headers=auth(u["token"])).json()
    assert plan2["steps"][0]["done"] is True
    assert client.post("/api/journey/housing_savings/plan/check", json={"step_id": "nope"}, headers=auth(u["token"])).status_code == 404
    assert client.delete(f"/api/journey/housing_savings/goals/{gid}", headers=auth(u["token"])).status_code == 200

def test_music_player_sample_off_in_academy(client):
    b = client.get("/api/platform/music_player/tracks").json()
    assert b["off_in_academy"] is True
    assert all(t["sample"] is True for t in b["tracks"])
    assert "streaming" in b["note"]

def test_hard_rules_and_wipe_cover_new_data(client):
    from app import tiers, wipe
    assert tiers.PLANS["paid"]["price_cents"] is None
    for coll in ("carpool_entries", "ride_contacts", "ride_ping_sessions", "savings_goals", "housing_plan"):
        assert coll in wipe.USER_COLLECTIONS
    u = reg(client, "wipe_f")
    client.post("/api/support/carpool_board/entries", json={"city": "Dallas", "meeting_source": "twelve_step", "meeting_id": "m1"}, headers=auth(u["token"]))
    client.post("/api/support/needs_a_ride/family/contacts", json={"label": "Dad"}, headers=auth(u["token"]))
    client.post("/api/journey/housing_savings/goals", json={"name": "Rent", "target_cents": 500}, headers=auth(u["token"]))
    w = client.post("/api/safety/data_wipe", headers=auth(u["token"])).json()
    assert w["counts"]["carpool_entries"] == 1 and w["counts"]["ride_contacts"] == 1 and w["counts"]["savings_goals"] == 1
