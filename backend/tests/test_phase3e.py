def reg(client, handle="euser", tier="paid"):
    r = client.post("/api/auth/register", json={"handle": handle, "password": "password123", "tier": tier, "phone": "817-555-0100"})
    assert r.status_code == 201, r.text
    return r.json()
def auth(t): return {"Authorization": f"Bearer {t}"}
def profile(client, u, **kw):
    body = {"intent": "friend", "interests": ["music", "walking"], "dealbreakers": [], "attributes": {}, **kw}
    r = client.post("/api/matching/ai_matching/profile", json=body, headers=auth(u["token"]))
    assert r.status_code == 201, r.text
    return r.json()

def test_matching_paid_gate_and_friend_match(client):
    free = reg(client, "matchfree", tier="free")
    assert client.post("/api/matching/ai_matching/profile", json={"intent": "friend"}, headers=auth(free["token"])).status_code == 402
    a = reg(client, "match_a"); b = reg(client, "match_b")
    profile(client, a); profile(client, b)
    r = client.post("/api/matching/ai_matching/run", headers=auth(a["token"])).json()
    assert r["dating_enabled"] is False
    assert r["results"][0]["fit"] == "accept" and "music" in str(r["results"][0]["reasons"])
    assert "phone" not in str(r["results"])

def test_dealbreaker_reason_only_own_side(client):
    a = reg(client, "db_a"); b = reg(client, "db_b")
    profile(client, a, dealbreakers=["smoking"])
    profile(client, b, attributes={"habit": "smoking"})
    r = client.post("/api/matching/ai_matching/run", headers=auth(a["token"])).json()
    assert r["results"][0]["fit"] == "reject" and "You listed smoking" in str(r["results"][0]["reasons"])

def test_exclusions_before_agent_and_override_blocked(client):
    a = reg(client, "ex_a"); b = reg(client, "ex_b")
    profile(client, a, blocked_handles=["ex_b"]); profile(client, b)
    r = client.post("/api/matching/ai_matching/run", headers=auth(a["token"])).json()
    assert r["results"][0] == {"candidate": {"handle": "ex_b", "role": "member", "tier": "paid"}, "fit": "excluded", "reasons": ["not available"], "score": 0} or r["results"][0]["fit"] == "excluded"
    assert client.post("/api/matching/ai_matching/override", json={"candidate_handle": "ex_b"}, headers=auth(a["token"])).status_code == 422

def test_override_soft_intro_and_rematch_and_dating_off(client):
    a = reg(client, "ov_a"); b = reg(client, "ov_b")
    profile(client, a, interests=["music"], dealbreakers=["smoking"])
    profile(client, b, interests=["chess"], attributes={"habit": "smoking"})
    r = client.post("/api/matching/ai_matching/run", headers=auth(a["token"])).json()
    assert r["results"][0]["fit"] == "reject"
    o = client.post("/api/matching/ai_matching/override", json={"candidate_handle": "ov_b"}, headers=auth(a["token"]))
    assert o.status_code == 201 and o.json()["status"] == "intro_requested" and "must still accept" in o.json()["note"]
    assert client.post("/api/matching/ai_matching/rematch", headers=auth(a["token"])).status_code == 200
    # dating intent still excluded while min days unset
    c = reg(client, "date_c"); d = reg(client, "date_d")
    profile(client, c, intent="dating", age_verified_18=True, days_in_recovery=999)
    profile(client, d, intent="dating", age_verified_18=True, days_in_recovery=999)
    rc = client.post("/api/matching/ai_matching/run", headers=auth(c["token"])).json()
    assert all(x["fit"] == "excluded" for x in rc["results"] if x["candidate"].get("handle") == "date_d")

def test_matching_lock_respected(client):
    a = reg(client, "lockmatch")
    profile(client, a)
    client.post("/api/wellbeing/locks", json={"target": "ai_matching", "kind": "week"}, headers=auth(a["token"]))
    assert client.post("/api/matching/ai_matching/run", headers=auth(a["token"])).status_code == 423
    assert client.post("/api/wellbeing/locks", json={"target": "crisis_button", "kind": "week"}, headers=auth(a["token"])).status_code == 422
