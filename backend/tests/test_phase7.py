"""Phase 7 gate: people features hold the safety invariants end to end."""
def reg(client, handle, role="member", tier="free"):
    r = client.post("/api/auth/register", json={"handle": handle, "password": "password123", "phone": "817-555-0100", "role": role, "tier": tier})
    assert r.status_code == 201, r.text
    return r.json()
def auth(t): return {"Authorization": f"Bearer {t}"}

def test_people_safety_invariants(client):
    a = reg(client, "p7_a"); b = reg(client, "p7_b"); fam = reg(client, "p7_fam", role="family")
    # geolocation: default off, city-only when on
    assert client.get("/api/support/geolocation/me", headers=auth(a["token"])).json() == {"opt_in": False, "city": None}
    client.post("/api/support/geolocation", json={"city": "Dallas", "lat": 32.78, "lng": -96.8, "opt_in": True}, headers=auth(a["token"]))
    seen = client.get("/api/support/geolocation/members", headers=auth(b["token"])).json()["members"]
    assert seen[0]["city"] == "Dallas" and "32.78" not in str(seen)
    # ride board: second viewer sees no phones, ever
    client.post("/api/support/needs_a_ride/requests", json={"from_city": "Dallas", "to_city": "Fort Worth", "notes": "Ride to meeting"}, headers=auth(a["token"]))
    blob = str(client.get("/api/support/needs_a_ride/requests", headers=auth(b["token"])).json())
    assert "817-555" not in blob and "phone" not in blob.lower().replace("phone numbers are never shown", "")
    # family: separate login works, everything default off, approvals explicit
    vis = client.get("/api/family/family_mode/visibility", headers=auth(a["token"])).json()
    assert vis["visibility"] == {"milestones": False, "appointments": False, "portfolio": False}
    assert vis["family_members"] == []
    assert client.post("/api/family/family_mode/family_members", json={"family_handle": "p7_fam"}, headers=auth(a["token"])).status_code == 201
    assert "p7_fam" in client.get("/api/family/family_mode/visibility", headers=auth(a["token"])).json()["family_members"]
    assert fam["user"]["role"] == "family"
