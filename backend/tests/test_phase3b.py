def reg(client, handle="buser", tier="free"):
    r = client.post("/api/auth/register", json={"handle": handle, "password": "password123", "tier": tier, "phone": "817-555-0100"})
    assert r.status_code == 201, r.text
    return r.json()
def auth(t): return {"Authorization": f"Bearer {t}"}

def test_mentorship_no_phone(client):
    m = reg(client, "mentor1"); s = reg(client, "mentee1")
    client.post("/api/support/mentorship/profile", json={"role": "mentor", "topics": ["jobs"], "bio": "Here to help."}, headers=auth(m["token"]))
    lst = client.get("/api/support/mentorship/mentors", headers=auth(s["token"])).json()["mentors"]
    assert lst[0]["handle"] == "mentor1" and "phone" not in lst[0]["member"]
    r = client.post("/api/support/mentorship/requests", json={"mentor_handle": "mentor1", "message": "Can we talk weekly?"}, headers=auth(s["token"]))
    assert r.status_code == 201 and "phone" not in r.json()["requester"]
    assert client.post("/api/support/mentorship/requests", json={"mentor_handle": "nope", "message": "hi"}, headers=auth(s["token"])).status_code == 404

def test_geolocation_optin_coarse_only(client):
    a = reg(client, "geo_a"); b = reg(client, "geo_b")
    assert client.get("/api/support/geolocation/me", headers=auth(a["token"])).json() == {"opt_in": False, "city": None}
    r = client.post("/api/support/geolocation", json={"city": "Fort Worth", "lat": 32.7555123, "lng": -97.3308765, "opt_in": True}, headers=auth(a["token"]))
    assert r.json() == {"opt_in": True, "city": "Fort Worth", "precision": "city"}
    members = client.get("/api/support/geolocation/members", headers=auth(b["token"])).json()["members"]
    assert members[0]["city"] == "Fort Worth" and "lat" not in str(members) and "lng" not in str(members) and "32.75" not in str(members)
    client.delete("/api/support/geolocation", headers=auth(a["token"]))
    assert client.get("/api/support/geolocation/members", headers=auth(b["token"])).json()["members"] == []

def test_needs_a_ride_no_phone_moderated(client):
    a = reg(client, "ride_a"); b = reg(client, "ride_b")
    r = client.post("/api/support/needs_a_ride/requests", json={"from_city": "Fort Worth", "to_city": "Dallas", "on": "2026-11-03", "notes": "Ride to a meeting."}, headers=auth(a["token"]))
    assert r.status_code == 201 and "phone" not in r.json()["requester"]
    lst = client.get("/api/support/needs_a_ride/requests", headers=auth(b["token"])).json()
    assert "817-555" not in str(lst)
    assert client.post("/api/support/needs_a_ride/requests", json={"from_city": "X", "to_city": "Y", "notes": "sell drugs"}, headers=auth(a["token"])).status_code == 422
    off = client.post("/api/support/needs_a_ride/offers", json={"request_id": r.json()["_id"], "message": "I can drive."}, headers=auth(b["token"]))
    assert off.status_code == 201 and "phone" not in off.json()["offerer"]

def test_accountability_groups_of_three(client):
    users = [reg(client, f"acc{i}") for i in range(3)]
    last = None
    for u in users:
        last = client.post("/api/support/accountability_partners/join", json={"goals": ["check in weekly"]}, headers=auth(u["token"]))
        assert last.status_code == 201
    g = client.get("/api/support/accountability_partners/my_group", headers=auth(users[0]["token"])).json()
    assert g["complete"] is True and len(g["members"]) == 3
    assert all("phone" not in m for m in g["members"])
    # rejoin is idempotent
    again = client.post("/api/support/accountability_partners/join", json={"goals": []}, headers=auth(users[0]["token"])).json()
    assert again["group_id"] == g["group"]
