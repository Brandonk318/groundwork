def reg(client, handle="duser", tier="free"):
    r = client.post("/api/auth/register", json={"handle": handle, "password": "password123", "tier": tier, "phone": "817-555-0100"})
    assert r.status_code == 201, r.text
    return r.json()
def auth(t): return {"Authorization": f"Bearer {t}"}

def test_tokens_no_cash_value(client):
    u = reg(client)
    assert client.get("/api/journey/token_rewards", headers=auth(u["token"])).json()["balance"] == 0
    assert client.post("/api/journey/token_rewards/earn", json={"reason": "checkin", "points": 10}, headers=auth(u["token"])).json()["balance"] == 10
    r = client.post("/api/journey/token_rewards/redeem", json={"reason": "merch mark", "points": 4}, headers=auth(u["token"])).json()
    assert r["balance"] == 6 and r["cash_value_cents"] == 0
    assert client.post("/api/journey/token_rewards/redeem", json={"reason": "x", "points": 99}, headers=auth(u["token"])).status_code == 422
    b = client.get("/api/journey/token_rewards", headers=auth(u["token"])).json()
    assert b["cash_value"] is None and "no cash value" in b["note"]

def test_merch_discreet_and_gated_by_milestone(client):
    u = reg(client)
    items = client.get("/api/journey/merch_rewards", headers=auth(u["token"])).json()["items"]
    blob = str(items).lower()
    for banned in ("sober", "sobriety", "addict", "jail", "prison"):
        assert banned not in blob
    assert all(i["price_cents"] is None for i in items)
    assert client.post("/api/journey/merch_rewards/claim", json={"item_id": "mark-tee-30"}, headers=auth(u["token"])).status_code == 422
    client.post("/api/journey/milestone_celebrations", json={"kind": "sobriety", "start_date": "2020-01-01"}, headers=auth(u["token"]))
    assert client.post("/api/journey/merch_rewards/claim", json={"item_id": "mark-tee-30"}, headers=auth(u["token"])).status_code == 201

def test_share_card_and_archive(client):
    u = reg(client)
    client.post("/api/reentry/reentry_checklist/progress", json={"step_id": 1, "status": "done"}, headers=auth(u["token"]))
    card = client.post("/api/journey/progress_share_card", headers=auth(u["token"]))
    assert card.status_code == 201 and card.json()["stats"]["checklist_done"] == 1 and "<svg" in card.json()["svg"]
    seal = client.post("/api/journey/day_one_archive", json={"body": "Dear future me, keep going.", "unlock_day": 30}, headers=auth(u["token"]))
    assert seal.status_code == 201 and seal.json()["sealed"] is True
    arch = client.get("/api/journey/day_one_archive", headers=auth(u["token"])).json()["archive"]
    assert arch[0]["sealed"] is True and "body" not in arch[0]
    client.post("/api/journey/milestone_celebrations", json={"kind": "sobriety", "start_date": "2020-01-01"}, headers=auth(u["token"]))
    arch2 = client.get("/api/journey/day_one_archive", headers=auth(u["token"])).json()["archive"]
    assert arch2[0]["unlocked"] is True and arch2[0]["body"] == "Dear future me, keep going."
    assert client.post("/api/journey/day_one_archive", json={"body": "x", "unlock_day": 45}, headers=auth(u["token"])).status_code == 422
