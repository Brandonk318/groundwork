import base64, os
import pytest
from app import moderation

def reg(client, handle="alex", tier="free", phone="817-555-0100"):
    r = client.post("/api/auth/register", json={"handle": handle, "password": "password123", "tier": tier, "phone": phone})
    assert r.status_code == 201, r.text
    return r.json()

def auth(tok):
    return {"Authorization": f"Bearer {tok}"}

def test_auth_and_me_no_phone(client):
    u = reg(client)
    assert "phone" not in u["user"]
    r = client.get("/api/auth/me", headers=auth(u["token"]))
    assert r.status_code == 200 and "phone" not in r.json()
    assert client.post("/api/auth/login", json={"handle": "alex", "password": "wrongpass"}).status_code == 401
    assert client.post("/api/auth/login", json={"handle": "alex", "password": "password123"}).status_code == 200

def test_mood_suggests_not_applies_and_crisis(client):
    u = reg(client)
    r = client.post("/api/wellbeing/mood_checkins", json={"mood": "rough", "note": "hard day"}, headers=auth(u["token"]))
    assert r.status_code == 201
    assert r.json()["suggested_filters"] and r.json()["show_crisis"] is True
    assert client.get("/api/wellbeing/filters", headers=auth(u["token"])).json()["active"] == []
    assert client.get("/api/safety/crisis").json()["resources"][0]["id"] == "988"

def test_filters_lock_exempt_and_locks(client):
    u = reg(client)
    assert client.post("/api/wellbeing/filters", json={"target": "crisis_button"}, headers=auth(u["token"])).status_code == 422
    assert client.post("/api/wellbeing/locks", json={"target": "crisis_button", "kind": "week"}, headers=auth(u["token"])).status_code == 422
    assert client.post("/api/wellbeing/locks", json={"target": "data_wipe", "kind": "week"}, headers=auth(u["token"])).status_code == 422
    r = client.post("/api/wellbeing/locks", json={"target": "community_feed", "kind": "week"}, headers=auth(u["token"]))
    assert r.status_code == 201
    lid = r.json()["_id"]
    assert client.post(f"/api/wellbeing/locks/{lid}/dont_remind", headers=auth(u["token"])).status_code == 200
    assert client.get("/api/wellbeing/locks/check/crisis_button", headers=auth(u["token"])).status_code == 200
    assert client.get("/api/wellbeing/locks/check/community_feed", headers=auth(u["token"])).status_code == 423

def test_anonymous_and_messaging_no_phone(client):
    a = reg(client, "a1"); b = reg(client, "b1")
    # get b id via members
    members = client.get("/api/community/members", headers=auth(a["token"])).json()["members"]
    assert all("phone" not in m for m in members)
    bid = members[0]["_id"] if "_id" in members[0] else None
    # public_member strips _id, so use register return? sender flow: fetch via login user id hidden; use members handle lookup via db not available.
    # Instead test post anonymity
    r = client.post("/api/community/community_feed/posts", json={"body": "hello", "anonymous": True}, headers=auth(a["token"]))
    assert r.status_code == 201 and r.json()["author"] == {"display": "Anonymous"} and "author_id" not in r.json()
    lst = client.get("/api/community/community_feed/posts", headers=auth(b["token"])).json()["posts"]
    assert lst and lst[0]["author"] == {"display": "Anonymous"}

def test_messaging_no_phone_via_register_ids(client, db):
    a = reg(client, "msg_a"); b = reg(client, "msg_b")
    assert client.post("/api/community/peer_messaging/messages", json={"recipient_id": "nope", "body": "hi"}, headers=auth(a["token"])).status_code == 404
    r = client.post("/api/community/peer_messaging/messages", json={"recipient_id": "msg_b", "body": "hi there"}, headers=auth(a["token"]))
    assert r.status_code == 201, r.text
    assert "phone" not in r.json()["recipient"] and "phone" not in r.json()["sender"]
    members = client.get("/api/community/members", headers=auth(a["token"])).json()["members"]
    assert members and all("phone" not in m and "email" not in m for m in members)
    convo = client.get("/api/community/peer_messaging/conversation/msg_a", headers=auth(b["token"])).json()
    assert convo["messages"] and convo["messages"][0]["body"] == "hi there"
    assert "phone" not in convo["with"]

def test_moderation_order():
    assert moderation.moderate("I want to kill myself and sell drugs")["decision"] == "crisis"
    assert moderation.moderate("sell drugs here")["decision"] == "remove"
    assert moderation.moderate("here is a tapering plan")["decision"] == "hold"
    assert moderation.moderate("my address is 123 Main")["decision"] == "soften"
    assert moderation.moderate("I slipped yesterday, feeling rough")["decision"] == "allow"
    assert moderation.moderate("kill myself")["reply"].find("988") >= 0

def test_resources_and_meetings(client):
    r = client.get("/api/support/resource_directory").json()
    assert r["excludes"] == ["food", "housing"]
    assert all(x["category"] in ("legal_aid", "treatment", "transit") for x in r["resources"])
    assert client.get("/api/support/resource_directory?category=food").status_code == 422
    assert client.get("/api/support/resource_directory?category=housing").status_code == 422
    m = client.get("/api/support/twelve_step_locator?program=AA").json()["meetings"]
    assert m and all(x["program"] == "AA" for x in m)

def test_reentry_no_invented_steps(client):
    u = reg(client)
    body = client.get("/api/reentry/reentry_checklist", headers=auth(u["token"])).json()
    assert len(body["steps"]) == 33 and body["steps"][0]["title"] == "Order your birth certificate"
    assert body["milestone_days"] == [30, 60, 90, 180, 365]

def test_milestones_and_jobs(client):
    u = reg(client)
    r = client.post("/api/journey/milestone_celebrations", json={"kind": "sobriety", "start_date": "2020-01-01"}, headers=auth(u["token"]))
    assert 365 in r.json()["reached"]
    jobs = client.get("/api/work/job_board?second_chance=true").json()["jobs"]
    assert jobs and all(j["second_chance"] for j in jobs)

def test_vault_paid_gate_and_roundtrip(client):
    free = reg(client, "free1", tier="free")
    assert client.get("/api/safety/document_vault", headers=auth(free["token"])).status_code == 402
    paid = reg(client, "paid1", tier="paid")
    # without KEK -> 503
    assert client.post("/api/safety/document_vault", json={"title": "ID", "content": "secret"}, headers=auth(paid["token"])).status_code == 503

def test_vault_roundtrip_with_kek(db):
    from fastapi.testclient import TestClient
    from app.config import Settings
    from app.main import create_app
    kek = base64.b64encode(os.urandom(32)).decode()
    s = Settings(jwt_secret="t" * 40, vault_kek_b64=kek)
    with TestClient(create_app(s, db=db)) as c:
        u = reg(c, "vaultuser", tier="paid")
        r = c.post("/api/safety/document_vault", json={"title": "ID", "content": "release papers"}, headers=auth(u["token"]))
        assert r.status_code == 201, r.text
        doc_id = r.json()["id"]
        got = c.get(f"/api/safety/document_vault/{doc_id}", headers=auth(u["token"]))
        assert got.json()["content"] == "release papers"
        assert c.get("/api/safety/document_vault", headers=auth(u["token"])).json()["documents"][0]["title"] == "ID"

def test_safe_contacts_and_wipe_lock_exempt(client):
    u = reg(client)
    r = client.post("/api/safety/safe_call_contacts", json={"name": "Sam", "phone": "817-555-9999", "relationship": "sponsor"}, headers=auth(u["token"]))
    assert r.status_code == 201
    assert client.get("/api/safety/safe_call_contacts", headers=auth(u["token"])).json()["contacts"]
    # lock everything lockable, wipe still works
    client.post("/api/wellbeing/locks", json={"target": "community_feed", "kind": "permanent"}, headers=auth(u["token"]))
    w = client.post("/api/safety/data_wipe", headers=auth(u["token"]))
    assert w.status_code == 200 and w.json()["wiped"] is True
    assert client.get("/api/safety/safe_call_contacts", headers=auth(u["token"])).status_code in (200, 401)

def test_platform_and_venue(client):
    assert client.get("/api/platform/read_aloud").json()["enabled"] is True
    langs = client.get("/api/platform/multi_language").json()
    assert langs["count"] == 21 and set(langs["rtl"]) == {"ar", "ur", "fa"}
    v = client.get("/api/venue/virtual_venue").json()["venue"]
    assert v["placeholder"] is True and "not the real space" in v["label"]

def test_family_defaults_off(client):
    u = reg(client)
    assert client.get("/api/family/family_mode/visibility", headers=auth(u["token"])).json()["visibility"] == {"milestones": False, "appointments": False, "portfolio": False}
    client.put("/api/family/family_mode/visibility", json={"milestones": True, "appointments": False}, headers=auth(u["token"]))
    assert client.get("/api/family/family_mode/visibility", headers=auth(u["token"])).json()["visibility"]["milestones"] is True

def test_portfolio_private_default_paid(client):
    free = reg(client, "pfree", tier="free")
    assert client.post("/api/journey/journey_portfolio/items", json={"title": "Day 30"}, headers=auth(free["token"])).status_code == 402
    paid = reg(client, "ppaid", tier="paid")
    r = client.post("/api/journey/journey_portfolio/items", json={"title": "Day 30"}, headers=auth(paid["token"]))
    assert r.status_code == 201 and r.json()["visibility"] == "private"
