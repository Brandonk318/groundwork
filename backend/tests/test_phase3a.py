def reg(client, handle="auser", tier="free"):
    r = client.post("/api/auth/register", json={"handle": handle, "password": "password123", "tier": tier, "phone": "817-555-0100"})
    assert r.status_code == 201, r.text
    return r.json()
def auth(t): return {"Authorization": f"Bearer {t}"}

def test_resume_builder(client):
    u = reg(client)
    r = client.post("/api/work/resume_builder", json={"full_name": "Alex R", "headline": "Roofing helper", "summary": "Reliable.", "skills": ["roofing", "safety"], "experience": [{"title": "Helper", "company": "Local crew", "summary": "Helped finish jobs."}]}, headers=auth(u["token"]))
    assert r.status_code == 201 and "Roofing helper" in r.json()["text"] and "roofing" in r.json()["text"]
    rid = r.json()["_id"]
    assert client.get(f"/api/work/resume_builder/{rid}", headers=auth(u["token"])).status_code == 200
    other = reg(client, "otherA")
    assert client.get(f"/api/work/resume_builder/{rid}", headers=auth(other["token"])).status_code == 404
    assert client.delete(f"/api/work/resume_builder/{rid}", headers=auth(u["token"])).status_code == 200

def test_interview_coach_deterministic(client):
    u = reg(client)
    qs = client.get("/api/work/interview_coach/questions", headers=auth(u["token"])).json()
    assert len(qs["questions"]) == 3 and qs["provider"] == "deterministic-local-v1"
    weak = client.post("/api/work/interview_coach/sessions", json={"question_id": "q1", "answer": "I dunno."}, headers=auth(u["token"])).json()
    strong = client.post("/api/work/interview_coach/sessions", json={"question_id": "q1", "answer": "For example, I helped finish a roof safely, learned to check materials twice, and the result was the crew finished on time because I stayed reliable."}, headers=auth(u["token"])).json()
    assert strong["score"] > weak["score"]
    again = client.post("/api/work/interview_coach/sessions", json={"question_id": "q1", "answer": "For example, I helped finish a roof safely, learned to check materials twice, and the result was the crew finished on time because I stayed reliable."}, headers=auth(u["token"])).json()
    assert again["score"] == strong["score"]

def test_micro_gigs_no_phone_moderated(client):
    u = reg(client); v = reg(client, "gig2")
    r = client.post("/api/work/micro_gigs", json={"title": "Yard cleanup help", "description": "One afternoon of yard work."}, headers=auth(u["token"]))
    assert r.status_code == 201 and "phone" not in r.json()["author"]
    lst = client.get("/api/work/micro_gigs", headers=auth(v["token"])).json()["gigs"]
    assert lst and "817-555" not in str(lst)
    assert client.post("/api/work/micro_gigs", json={"title": "sell drugs fast", "description": "sell drugs"}, headers=auth(u["token"])).status_code == 422
    app = client.post(f"/api/work/micro_gigs/{r.json()['_id']}/apply", json={"message": "I can help Saturday."}, headers=auth(v["token"]))
    assert app.status_code == 201 and "phone" not in app.json()["applicant"]

def test_courses_paid_gate_and_quiz(client):
    free = reg(client, "freeC"); paid = reg(client, "paidC", tier="paid")
    assert client.get("/api/learning/courses", headers=auth(free["token"])).status_code == 402
    cat = client.get("/api/learning/courses", headers=auth(paid["token"])).json()
    assert {c["id"] for c in cat["courses"]} >= {"parole_navigation", "job_interviews", "relapse_prevention", "small_business"}
    assert all(c["draft"] for c in cat["courses"])
    rp = next(c for c in cat["courses"] if c["id"] == "relapse_prevention")
    assert "988" in rp["modules"][0]["content"]
    q = client.post("/api/learning/courses/quiz", json={"course_id": "job_interviews", "module_id": "ji1", "answer": 0}, headers=auth(paid["token"])).json()
    assert q["correct"] is True
    assert client.get("/api/learning/courses_life_skills", headers=auth(paid["token"])).status_code == 200
    assert client.post("/api/learning/courses/progress", json={"course_id": "parole_navigation", "module_id": "pn1"}, headers=auth(paid["token"])).status_code == 201
