"""Private crisis auto-reply: author-only, staff see nothing (Brann 2026-10-31)."""
import json, logging
import pytest
from app import crisis_reply, moderation, wipe

def reg(client, handle, role="member"):
    r = client.post("/api/auth/register", json={"handle": handle, "password": "password123", "tier": "free", "phone": "817-555-0199", "role": role})
    assert r.status_code == 201, r.text
    return r.json()
def auth(t): return {"Authorization": f"Bearer {t}"}

@pytest.mark.parametrize("text", ["I want to KILL MYSELF", "feeling suicidal tonight", "I think I'm going to overdose",
    "I don't want to wake up", "about to relapse right now", "been hurting myself again", "self-harm is back", "I just want to end it all", "better off dead"])
def test_matches_crisis_phrasing(text):
    assert crisis_reply.matches(text)

@pytest.mark.parametrize("text", ["Watched Suicide Squad last night", "Took the overdose prevention class, got a naloxone kit",
    "I'm dying to see my kids", "we killed it at the job fair", "Skillful mysel", "overdosage", "relapse prevention group was good", "suicidefree"])
def test_false_positive_guards(text):
    assert not crisis_reply.matches(text)

def test_anonymous_post_published_unaltered_author_gets_private_notice(client, db):
    a = reg(client, "cr_author"); b = reg(client, "cr_other")
    text = "Honestly I want to kill myself today"
    r = client.post("/api/community/anonymous_posting/posts", json={"body": text}, headers=auth(a["token"]))
    assert r.status_code == 201
    j = r.json()
    assert j["status"] == "published" and j["body"] == text
    n = j["private_notice"]
    ids = [x["id"] for x in n["resources"]]
    assert ids == ["988", "911", "741741"] and "HOME" in n["body"] and n["links"]["crisis_button"]
    assert "817-555" not in json.dumps(n)
    # stored post carries no crisis flag and no notice
    blob = json.dumps(client.get("/api/community/community_feed/posts", headers=auth(b["token"])).json())
    assert text in blob and "crisis" not in blob and "private_notice" not in blob and "needs_human\": true" not in blob
    assert "cr_author" not in blob
    # author-only inbox
    mine = client.get("/api/safety/private_inbox", headers=auth(a["token"])).json()["messages"]
    assert len(mine) == 1 and mine[0]["message"]["resources"][0]["id"] == "988"
    assert client.get("/api/safety/private_inbox", headers=auth(b["token"])).json()["messages"] == []
    assert client.post(f"/api/safety/private_inbox/{mine[0]['id']}/read", headers=auth(b["token"])).status_code == 404
    assert client.post(f"/api/safety/private_inbox/{mine[0]['id']}/read", headers=auth(a["token"])).status_code == 200
    assert client.get("/api/safety/private_inbox").status_code in (401, 403)

def test_inbox_entry_has_no_post_link(client, db):
    a = reg(client, "cr_link")
    client.post("/api/community/community_feed/posts", json={"body": "I might overdose tonight", "anonymous": True}, headers=auth(a["token"])).json()
    mine = client.get("/api/safety/private_inbox", headers=auth(a["token"])).json()["messages"]
    s = json.dumps(mine)
    assert "overdose tonight" not in s and "post" not in s.replace("posts", "")

def test_admin_sees_nothing(client):
    a = reg(client, "cr_member"); adm = reg(client, "cr_admin", role="admin")
    client.post("/api/community/anonymous_qa/questions", json={"body": "I'm suicidal and scared"}, headers=auth(a["token"]))
    client.post("/api/reentry/reentry_checklist/steps/1/tips", json={"body": "I want to die"}, headers=auth(a["token"]))
    assert client.get("/api/safety/private_inbox", headers=auth(adm["token"])).json()["messages"] == []
    for path in ("/api/community/community_feed/posts", "/api/community/anonymous_qa/questions", "/api/reentry/reentry_checklist/steps/1/tips"):
        blob = json.dumps(client.get(path, headers=auth(adm["token"])).json())
        assert "cr_member" not in blob and "private_notice" not in blob and "\"crisis\"" not in blob and "crisis_first" not in blob

def test_no_staff_or_admin_route_exposes_inbox(client):
    paths = list(client.app.openapi()["paths"])
    inbox = [p for p in paths if "inbox" in p or "crisis_reply" in p]
    assert sorted(inbox) == ["/api/safety/private_inbox", "/api/safety/private_inbox/{mid}/read"]
    assert not any("admin" in p or "moderation/queue" in p for p in paths)

def test_no_log_line_ties_trigger_to_user(client, caplog):
    caplog.set_level(logging.DEBUG)
    a = reg(client, "cr_logs")
    client.post("/api/community/community_feed/posts", json={"body": "thinking about suicide", "anonymous": True}, headers=auth(a["token"]))
    text = caplog.text.lower()
    assert "cr_logs" not in text and "suicide" not in text and "crisis" not in text

def test_moderate_public_drops_crisis_but_keeps_remove():
    assert moderation.moderate_public("I want to kill myself")["decision"] == "allow"
    assert moderation.moderate_public("I want to kill myself and sell drugs")["decision"] == "remove"
    assert moderation.moderate("I want to kill myself")["decision"] == "crisis"  # /moderation/check helper unchanged

def test_removed_post_still_gets_private_help(client):
    a = reg(client, "cr_removed")
    r = client.post("/api/community/community_feed/posts", json={"body": "i want to die, gonna buy drugs"}, headers=auth(a["token"]))
    assert r.status_code == 422
    assert len(client.get("/api/safety/private_inbox", headers=auth(a["token"])).json()["messages"]) == 1

def test_inbox_is_wiped():
    assert wipe.USER_COLLECTIONS["private_inbox"] == "user_id"

def test_crisis_copy_flagged_for_translation_review():
    n = crisis_reply.notice()
    assert n["locale"] == "en" and n["needs_translation_review"] is True and "Spanish" in n["body"]
