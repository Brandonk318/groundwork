import json
from pathlib import Path
from app import checklist as cl

def reg(client, handle="p2user", tier="free"):
    r = client.post("/api/auth/register", json={"handle": handle, "password": "password123", "tier": tier, "phone": "817-555-0100"})
    assert r.status_code == 201, r.text
    return r.json()
def auth(t): return {"Authorization": f"Bearer {t}"}

TITLES = ["Order your birth certificate","Request your Social Security card","Start the state ID application","Set goals with your case manager","Plan your ride home","Line up one support contact","Find a safe place to stay (call 211 or local housing resources)","Find food for this week (call 211 or a local food pantry)","Check your release papers and deadlines","Confirm your first check-in date and conditions","Save 988 and 911 in your phone","Get your state ID","Get a phone, email and free internet access","Put every court date and check-in on a calendar","Contact local reentry services","Know your supervision conditions","Check your fines, fees and restitution","Check your driver's license status","Enroll in Medicaid, and SNAP if you need it","Get your health records","Make a medication plan","Book a doctor's appointment","Book a mental health appointment","Get a substance use evaluation","Find a support group","Build your resume","Apply to second-chance employers","Look into training or certificates","Open a bank account and make a budget","Start rebuilding your credit","Reconnect with family, and handle child support if it applies","Set a daily routine","Set one long-term goal and celebrate your 90-day milestone"]

def test_exact_33_seeded(client):
    u = reg(client)
    b = client.get("/api/reentry/reentry_checklist", headers=auth(u["token"])).json()
    assert [s["title"] for s in b["steps"]] == TITLES
    assert [s["id"] for s in b["steps"]] == list(range(1, 34))
    assert len(b["sections"]) == 7
    assert b["sections"][0] == {"id": "before_release", "title": "Before release", "step_ids": [1,2,3,4,5,6], "total": 6, "done": 0, "percent": 0, "complete": False}
    data = json.loads((Path(__file__).parent.parent / "app/data/reentry_steps.json").read_text())
    assert [s["title"] for s in data["steps"]] == TITLES

def test_progress_fields_and_per_section(client):
    u = reg(client)
    r = client.post("/api/reentry/reentry_checklist/progress", json={"step_id": 1, "status": "done", "due_date": "2026-11-01", "priority": "high", "notes": "bring papers"}, headers=auth(u["token"]))
    assert r.status_code == 200, r.text
    assert r.json()["due_date"] == "2026-11-01" and r.json()["priority"] == "high"
    assert {"type": "first_step", "label": "First step done"} in r.json()["celebrations"]
    assert r.json()["newly_fired"] and r.json()["newly_fired"][0]["type"] == "first_step"
    b = client.get("/api/reentry/reentry_checklist", headers=auth(u["token"])).json()
    s1 = b["steps"][0]
    assert s1["status"] == "done" and s1["notes"] == "bring papers"
    assert b["sections"][0]["done"] == 1 and b["sections"][0]["percent"] == 17
    assert b["progress"] == {"done": 1, "total": 33, "percent": 3}
    # bad due date / priority / unknown step
    assert client.post("/api/reentry/reentry_checklist/progress", json={"step_id": 1, "status": "done", "due_date": "Nov 1"}, headers=auth(u["token"])).status_code == 422
    assert client.post("/api/reentry/reentry_checklist/progress", json={"step_id": 99, "status": "done"}, headers=auth(u["token"])).status_code == 404
    assert client.post("/api/reentry/reentry_checklist/progress", json={"step_id": 1, "status": "done", "priority": "urgent"}, headers=auth(u["token"])).status_code == 422

def test_section_and_all_celebrations(client):
    u = reg(client)
    for i in range(1, 7):
        r = client.post("/api/reentry/reentry_checklist/progress", json={"step_id": i, "status": "done"}, headers=auth(u["token"]))
    assert any(c["type"] == "section_complete" and c["section"] == "before_release" for c in r.json()["celebrations"])
    assert any(c["type"] == "section_complete" for c in r.json()["newly_fired"])
    for i in range(7, 34):
        r = client.post("/api/reentry/reentry_checklist/progress", json={"step_id": i, "status": "done"}, headers=auth(u["token"]))
    assert any(c["type"] == "all_complete" for c in r.json()["celebrations"])
    cel = client.get("/api/reentry/reentry_checklist/celebrations", headers=auth(u["token"])).json()["celebrations"]
    assert cel[0]["type"] == "first_step" and cel[-1]["type"] == "all_complete" and len([c for c in cel if c["type"] == "section_complete"]) == 7

def test_celebration_logic_pure():
    data = cl.load_data()
    assert cl.celebrations_for(set(), data) == []
    assert cl.celebrations_for({1}, data)[0]["type"] == "first_step"
    assert cl.section_progress(data, {1,2,3,4,5,6})[0]["complete"] is True

def test_custom_steps_crud_and_progress(client):
    u = reg(client); other = reg(client, "other2")
    r = client.post("/api/reentry/reentry_checklist/custom_steps", json={"title": "Call my sister", "priority": "high", "due_date": "2026-11-02"}, headers=auth(u["token"]))
    assert r.status_code == 201, r.text
    cid = r.json()["_id"]
    b = client.get("/api/reentry/reentry_checklist", headers=auth(u["token"])).json()
    assert any(c["_id"] == cid for c in b["custom_steps"]) and len(b["steps"]) == 33
    assert client.post("/api/reentry/reentry_checklist/progress", json={"custom_id": cid, "status": "done", "notes": "called"}, headers=auth(other["token"])).status_code == 404
    assert client.post("/api/reentry/reentry_checklist/progress", json={"custom_id": cid, "status": "done", "notes": "called"}, headers=auth(u["token"])).status_code == 200
    assert client.delete(f"/api/reentry/reentry_checklist/custom_steps/{cid}", headers=auth(u["token"])).status_code == 200
    assert client.delete(f"/api/reentry/reentry_checklist/custom_steps/{cid}", headers=auth(u["token"])).status_code == 404

def test_progress_is_per_user(client):
    a = reg(client, "alice2"); b = reg(client, "bob2")
    client.post("/api/reentry/reentry_checklist/progress", json={"step_id": 1, "status": "done"}, headers=auth(a["token"]))
    bb = client.get("/api/reentry/reentry_checklist", headers=auth(b["token"])).json()
    assert bb["steps"][0]["status"] == "not_started" and bb["progress"]["done"] == 0

def test_step11_and_page_crisis_links(client):
    u = reg(client)
    b = client.get("/api/reentry/reentry_checklist", headers=auth(u["token"])).json()
    s11 = b["steps"][10]
    assert s11["id"] == 11 and s11["crisis_links"] == {"call_988": "tel:988", "text_988": "sms:988", "call_911": "tel:911"}
    assert b["crisis_links"]["call_988"] == "tel:988"
    assert client.get("/api/safety/crisis").status_code == 200

def test_housing_food_only_211_pointers(client):
    u = reg(client)
    b = client.get("/api/reentry/reentry_checklist", headers=auth(u["token"])).json()
    for sid in (7, 8):
        s = b["steps"][sid - 1]
        assert s["resource_pointer"] is True and s["resource"] == "211"
        assert "does not provide" in s["resource_note"] and "does not partner" in s["resource_note"]
        assert "provider" not in {k.lower() for k in s.keys() if k not in ("resource_note",)}
        assert not any(k in s for k in ("providers", "listings", "partnerships", "partner"))

def test_tips_anonymous_moderated_no_phone(client):
    a = reg(client, "tip_a"); b = reg(client, "tip_b")
    r = client.post("/api/reentry/reentry_checklist/steps/1/tips", json={"body": "Order early, it took two weeks for me."}, headers=auth(a["token"]))
    assert r.status_code == 201, r.text
    assert r.json()["author"] == {"display": "Anonymous"} and "author_id" not in r.json() and "author_handle" not in r.json()
    lst = client.get("/api/reentry/reentry_checklist/steps/1/tips", headers=auth(b["token"])).json()["tips"]
    assert lst and lst[0]["author"] == {"display": "Anonymous"}
    blob = json.dumps(lst)
    assert "817-555" not in blob and "tip_a" not in blob
    # moderation: remove blocked, crisis held (not published, carries human flag)
    assert client.post("/api/reentry/reentry_checklist/steps/1/tips", json={"body": "sell drugs here"}, headers=auth(a["token"])).status_code == 422
    held = client.post("/api/reentry/reentry_checklist/steps/1/tips", json={"body": "I want to kill myself"}, headers=auth(a["token"]))
    assert held.status_code == 201 and held.json()["status"] == "held" and held.json()["moderation"]["needs_human"] is True
    lst2 = client.get("/api/reentry/reentry_checklist/steps/1/tips", headers=auth(b["token"])).json()["tips"]
    assert len(lst2) == 1
    assert client.get("/api/reentry/reentry_checklist/steps/99/tips", headers=auth(a["token"])).status_code == 404
    assert client.post("/api/reentry/reentry_checklist/steps/99/tips", json={"body": "hi"}, headers=auth(a["token"])).status_code == 404

def test_checklist_not_locked_or_paywalled(client):
    # free user, and locked community feed still can use checklist; crisis/wipe remain exempt (pinned in phase1 too)
    u = reg(client, "free_check")
    client.post("/api/wellbeing/locks", json={"target": "community_feed", "kind": "permanent"}, headers=auth(u["token"]))
    client.post("/api/wellbeing/locks", json={"target": "reentry_checklist", "kind": "permanent"}, headers=auth(u["token"]))
    assert client.get("/api/reentry/reentry_checklist", headers=auth(u["token"])).status_code == 200
    assert client.post("/api/wellbeing/locks", json={"target": "crisis_button", "kind": "week"}, headers=auth(u["token"])).status_code == 422
    assert client.get("/api/plans").json()["paid"]  # no invented price check in registry tests; checklist is unassigned/open
    from app import tiers
    assert tiers.PLANS["paid"]["price_cents"] is None

def test_wipe_covers_new_collections(client):
    from app import wipe
    assert wipe.USER_COLLECTIONS["checklist_custom_steps"] == "user_id"
    assert wipe.USER_COLLECTIONS["checklist_tips"] == "author_id"
    assert wipe.USER_COLLECTIONS["checklist_progress"] == "user_id"
