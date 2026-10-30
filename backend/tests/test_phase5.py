from datetime import datetime, timezone

def reg(client, handle="phase5user"):
    r = client.post("/api/auth/register", json={"handle": handle, "password": "password123", "phone": "817-555-0100"})
    assert r.status_code == 201, r.text
    return r.json()
def auth(t): return {"Authorization": f"Bearer {t}"}

def test_court_date_queues_outbox_reminder(client, db):
    from app import outbox as outbox_mod
    u = reg(client)
    r = client.post("/api/reentry/court_calendar", json={"on": "2026-12-01T09:00:00", "court": "County Court"}, headers=auth(u["token"]))
    assert r.status_code == 201, r.text
    import asyncio
    rows = asyncio.run(db.outbox.find({"kind": "court_reminder"}).to_list(10))
    assert len(rows) == 1 and rows[0]["status"] == "queued" and rows[0]["payload"]["court"] == "County Court"
    assert rows[0]["channel"] == "inapp"
    assert outbox_mod  # module importable; delivery stays unwired by design

def test_permanent_lock_queues_one_reminder(client, db):
    import asyncio
    u = reg(client)
    r = client.post("/api/wellbeing/locks", json={"target": "community_feed", "kind": "permanent"}, headers=auth(u["token"]))
    assert r.status_code == 201, r.text
    rows = asyncio.run(db.outbox.find({"kind": "permanent_lock_reminder"}).to_list(10))
    assert len(rows) == 1
    sent_at = rows[0]["next_attempt_at"]
    if sent_at.tzinfo is None:
        sent_at = sent_at.replace(tzinfo=timezone.utc)
    start = datetime.fromisoformat(r.json()["start"])
    assert (sent_at.date() - start.date()).days == 30  # date math; stored datetimes lose sub-second precision
    # time-limited locks queue nothing
    client.post("/api/wellbeing/locks", json={"target": "peer_messaging", "kind": "week"}, headers=auth(u["token"]))
    rows2 = asyncio.run(db.outbox.find({}).to_list(10))
    assert len(rows2) == 1

def test_outbox_entries_wiped_with_user(client, db):
    import asyncio
    u = reg(client, "phase5wipe")
    client.post("/api/reentry/court_calendar", json={"on": "2026-12-01", "court": "Court"}, headers=auth(u["token"]))
    assert asyncio.run(db.outbox.count_documents({})) >= 1
    w = client.post("/api/safety/data_wipe", headers=auth(u["token"]))
    assert w.status_code == 200 and w.json()["counts"]["outbox"] >= 1
