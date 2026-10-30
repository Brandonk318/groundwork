import base64
def reg(client, handle="cuser", tier="free"):
    r = client.post("/api/auth/register", json={"handle": handle, "password": "password123", "tier": tier, "phone": "817-555-0100"})
    assert r.status_code == 201, r.text
    return r.json()
def auth(t): return {"Authorization": f"Bearer {t}"}
def b64(b): return base64.b64encode(b).decode()

def test_events_groups_meetings(client):
    u = reg(client); v = reg(client, "c2")
    e = client.post("/api/community/events", json={"title": "Community picnic", "on": "2026-11-10", "city": "Fort Worth"}, headers=auth(u["token"]))
    assert e.status_code == 201
    assert client.post(f"/api/community/events/{e.json()['_id']}/rsvp", headers=auth(v["token"])).json()["count"] == 1
    g = client.post("/api/community/program_groups", json={"name": "AA newcomers", "program": "AA"}, headers=auth(u["token"]))
    assert client.post(f"/api/community/program_groups/{g.json()['_id']}/join", headers=auth(v["token"])).json()["members"] == 2
    m = client.post("/api/community/virtual_meetings", json={"title": "Evening check-in", "on": "2026-11-10"}, headers=auth(u["token"]))
    assert m.status_code == 201 and m.json()["join_path"].startswith("/meet/")

def test_media_limits_and_paid_video(client, tmp_path, monkeypatch):
    monkeypatch.setenv("GW_MEDIA_DIR", str(tmp_path))
    free = reg(client, "mediafree"); paid = reg(client, "mediapaid", tier="paid")
    ok = client.post("/api/community/photo_posts", json={"filename": "a.png", "content_type": "image/png", "data_b64": b64(b"\x89PNG fake"), "caption": "garden"}, headers=auth(free["token"]))
    assert ok.status_code == 201, ok.text
    assert ok.json()["exif_stripped"] is True and "data_b64" not in ok.json()
    assert client.post("/api/community/photo_posts", json={"filename": "a.txt", "content_type": "text/plain", "data_b64": b64(b"hi")}, headers=auth(free["token"])).status_code == 422
    assert client.post("/api/community/video_posts", json={"filename": "v.mp4", "content_type": "video/mp4", "data_b64": b64(b"video")}, headers=auth(free["token"])).status_code == 402
    vid = client.post("/api/community/video_posts", json={"filename": "v.mp4", "content_type": "video/mp4", "data_b64": b64(b"video")}, headers=auth(paid["token"]))
    assert vid.status_code == 201
    voice = client.post("/api/community/voice_notes", json={"filename": "n.webm", "content_type": "audio/webm", "data_b64": b64(b"audio")}, headers=auth(free["token"]))
    assert voice.status_code == 201
    # oversize photo >5MB rejected without storing huge test payload in db (use sparse check via limit unit)
    from app import media
    try:
        media.save_upload("u", "photo", "x.png", "image/png", b64(b"x" * (5*1024*1024+1)))
        assert False
    except ValueError as e:
        assert "too large" in str(e)
    assert len(client.get("/api/community/media_posts", headers=auth(free["token"])).json()["media"]) == 2

def test_anonymous_qa(client):
    a = reg(client, "qa_a"); b = reg(client, "qa_b")
    q = client.post("/api/community/anonymous_qa/questions", json={"body": "How did you handle your first week?"}, headers=auth(a["token"]))
    assert q.status_code == 201 and q.json()["author"] == {"display": "Anonymous"}
    lst = client.get("/api/community/anonymous_qa/questions", headers=auth(b["token"])).json()["questions"]
    assert "qa_a" not in str(lst) and "817-555" not in str(lst)
    ans = client.post(f"/api/community/anonymous_qa/questions/{q.json()['id']}/answers", json={"body": "One day at a time helped me."}, headers=auth(b["token"]))
    assert ans.status_code == 201 and ans.json()["author"] == {"display": "Anonymous"}
    lst2 = client.get("/api/community/anonymous_qa/questions", headers=auth(a["token"])).json()["questions"]
    assert lst2[0]["answers"] and lst2[0]["answers"][0]["body"] == "One day at a time helped me."
    assert client.post("/api/community/anonymous_qa/questions", json={"body": "sell drugs"}, headers=auth(a["token"])).status_code == 422
