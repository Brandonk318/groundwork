def reg(client, handle="juser", tier="paid", role="member"):
    r = client.post("/api/auth/register", json={"handle": handle, "password": "password123", "tier": tier, "phone": "817-555-0100", "role": role})
    assert r.status_code == 201, r.text
    return r.json()
def auth(t): return {"Authorization": f"Bearer {t}"}

def test_portfolio_private_by_default_and_owner_crud(client):
    u = reg(client)
    r = client.post("/api/journey/journey_portfolio/items", json={"title": "Day 30", "journey": "sobriety"}, headers=auth(u["token"]))
    assert r.status_code == 201, r.text
    assert r.json()["visibility"] == "private" and r.json()["position"] == 0
    iid = r.json()["_id"]
    # link visibility on create stays private until an explicit share
    r2 = client.post("/api/journey/journey_portfolio/items", json={"title": "Day 60", "visibility": "link"}, headers=auth(u["token"]))
    assert r2.json()["visibility"] == "private"
    # bad inputs
    assert client.post("/api/journey/journey_portfolio/items", json={"title": "x", "visibility": "public"}, headers=auth(u["token"])).status_code == 422
    assert client.post("/api/journey/journey_portfolio/items", json={"title": "x", "happened_on": "tomorrow"}, headers=auth(u["token"])).status_code == 422
    assert client.post("/api/journey/journey_portfolio/items", json={"title": "x", "milestone_day": 45}, headers=auth(u["token"])).status_code == 422
    # patch + bad patch + other-owner 404
    v = reg(client, "journey_victim")
    assert client.patch(f"/api/journey/journey_portfolio/items/{iid}", json={"title": "Day 30 edited", "visibility": "family"}, headers=auth(u["token"])).json()["title"] == "Day 30 edited"
    assert client.patch(f"/api/journey/journey_portfolio/items/{iid}", json={"visibility": "everyone"}, headers=auth(u["token"])).status_code == 422
    assert client.patch(f"/api/journey/journey_portfolio/items/{iid}", json={"title": "hijack"}, headers=auth(v["token"])).status_code == 404
    assert client.delete(f"/api/journey/journey_portfolio/items/{iid}", headers=auth(v["token"])).status_code == 404
    assert client.delete(f"/api/journey/journey_portfolio/items/{iid}", headers=auth(u["token"])).json() == {"deleted": True}
    # paid gate still enforced
    free = reg(client, "jfree", tier="free")
    assert client.get("/api/journey/journey_portfolio/items", headers=auth(free["token"])).status_code == 402

def test_reorder_and_position(client):
    u = reg(client)
    ids = [client.post("/api/journey/journey_portfolio/items", json={"title": f"t{i}"}, headers=auth(u["token"])).json()["_id"] for i in range(3)]
    rev = list(reversed(ids))
    assert client.post("/api/journey/journey_portfolio/reorder", json={"order": rev}, headers=auth(u["token"])).json() == {"order": rev}
    got = [d["_id"] for d in client.get("/api/journey/journey_portfolio/items", headers=auth(u["token"])).json()["items"]]
    assert got == rev
    assert client.post("/api/journey/journey_portfolio/reorder", json={"order": rev[:2]}, headers=auth(u["token"])).status_code == 422

def test_link_share_view_revoke_noindex_dates(client):
    u = reg(client)
    iid = client.post("/api/journey/journey_portfolio/items", json={"title": "Release day", "happened_on": "2024-05-01"}, headers=auth(u["token"])).json()["_id"]
    s = client.post("/api/journey/journey_portfolio/share", json={"item_id": iid}, headers=auth(u["token"])).json()
    assert s["url"] == f"/p/{s['token']}"
    assert client.post("/api/journey/journey_portfolio/share", json={"item_id": "nope"}, headers=auth(u["token"])).status_code == 404
    view = client.get(f"/p/{s['token']}")
    assert view.status_code == 200 and view.headers["x-robots-tag"] == "noindex"
    assert "happened_on" not in view.json()["item"] and view.json()["item"]["noindex"] is True
    # opt in to dates
    client.patch(f"/api/journey/journey_portfolio/items/{iid}", json={"show_dates": True}, headers=auth(u["token"]))
    view2 = client.get(f"/p/{s['token']}")
    assert view2.json()["item"]["happened_on"] == "2024-05-01"
    assert client.get("/p/deadbeef").status_code == 404
    # revoke: link dies and item returns to private
    assert client.post("/api/journey/journey_portfolio/share", json={"item_id": iid, "revoke": True}, headers=auth(u["token"])).json()["revoked"] is True
    assert client.get(f"/p/{s['token']}").status_code == 404
    mine = client.get("/api/journey/journey_portfolio/items", headers=auth(u["token"])).json()["items"]
    assert next(d for d in mine if d["_id"] == iid)["visibility"] == "private"

def test_family_view_only_after_grant_and_family_items(client):
    m = reg(client, "jfam_member")
    fam = reg(client, "jfam_login", role="family")
    outsider = reg(client, "jfam_out", role="family")
    iid = client.post("/api/journey/journey_portfolio/items", json={"title": "Family news", "visibility": "family"}, headers=auth(m["token"])).json()["_id"]
    assert client.get("/api/journey/journey_portfolio/family?member_handle=jfam_member", headers=auth(fam["token"])).status_code == 404
    assert client.post("/api/family/family_mode/family_members", json={"family_handle": "nobody"}, headers=auth(m["token"])).status_code == 404
    client.post("/api/family/family_mode/family_members", json={"family_handle": "jfam_login"}, headers=auth(m["token"]))
    assert client.get("/api/journey/journey_portfolio/family?member_handle=jfam_member", headers=auth(fam["token"])).status_code == 404
    client.put("/api/family/family_mode/visibility", json={"milestones": False, "appointments": False, "portfolio": True}, headers=auth(m["token"]))
    got = client.get("/api/journey/journey_portfolio/family?member_handle=jfam_member", headers=auth(fam["token"])).json()["items"]
    assert [d["id"] for d in got] == [iid] and "happened_on" not in got[0]
    assert client.get("/api/journey/journey_portfolio/family?member_handle=jfam_member", headers=auth(outsider["token"])).status_code == 404
    assert client.get("/api/journey/journey_portfolio/family?member_handle=ghost", headers=auth(fam["token"])).status_code == 404
    # private items never leak to family
    priv = client.post("/api/journey/journey_portfolio/items", json={"title": "Just mine"}, headers=auth(m["token"])).json()["_id"]
    got2 = client.get("/api/journey/journey_portfolio/family?member_handle=jfam_member", headers=auth(fam["token"])).json()["items"]
    assert priv not in [d["id"] for d in got2]

def test_suggestions_from_milestones_never_autopublish(client):
    u = reg(client)
    assert client.get("/api/journey/journey_portfolio/suggestions", headers=auth(u["token"])).json()["suggestions"] == []
    client.post("/api/journey/milestone_celebrations", json={"kind": "sobriety", "start_date": "2020-01-01"}, headers=auth(u["token"]))
    sug = client.get("/api/journey/journey_portfolio/suggestions", headers=auth(u["token"])).json()
    assert [s["milestone_day"] for s in sug["suggestions"]] == [30, 60, 90, 180, 365]
    assert all(s["auto_published"] is False for s in sug["suggestions"])
    assert client.get("/api/journey/journey_portfolio/items", headers=auth(u["token"])).json()["items"] == []
    iid = client.post("/api/journey/journey_portfolio/items", json={"title": "Day 30", "milestone_day": 30}, headers=auth(u["token"])).json()["_id"]
    assert iid
    sug2 = client.get("/api/journey/journey_portfolio/suggestions", headers=auth(u["token"])).json()
    assert 30 not in [s["milestone_day"] for s in sug2["suggestions"]]

def test_wipe_removes_portfolio_and_shares(client):
    from app import wipe
    assert wipe.USER_COLLECTIONS["portfolio_shares"] == "user_id"
    u = reg(client, "jwipe")
    iid = client.post("/api/journey/journey_portfolio/items", json={"title": "x"}, headers=auth(u["token"])).json()["_id"]
    tok = client.post("/api/journey/journey_portfolio/share", json={"item_id": iid}, headers=auth(u["token"])).json()["token"]
    w = client.post("/api/safety/data_wipe", headers=auth(u["token"])).json()
    assert w["counts"]["portfolio_items"] == 1 and w["counts"]["portfolio_shares"] == 1
    assert client.get(f"/p/{tok}").status_code == 404
