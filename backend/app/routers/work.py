"""Work: job board, tracker, resume builder, interview coach, micro-gigs."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from .. import crisis_reply, moderation, safety
from ..deps import get_current_user
from ..providers import INTERVIEW_QUESTIONS, InterviewCoachProvider
from ..seed_data import JOBS
from ._stub import stub_router

router = stub_router("work", exclude={"job_board", "application_tracker", "resume_builder", "interview_coach", "micro_gigs"})
coach = InterviewCoachProvider()

class AppIn(BaseModel):
    job_id: str
    status: str = "applied"
class JobExp(BaseModel):
    title: str = ""
    company: str = ""
    summary: str = ""
class ResumeIn(BaseModel):
    full_name: str = Field(max_length=80)
    headline: str = ""
    summary: str = ""
    skills: list[str] = []
    experience: list[JobExp] = []
class AnswerIn(BaseModel):
    question_id: str
    answer: str = Field(min_length=1, max_length=3000)
class GigIn(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=1, max_length=2000)
    city: str = "Fort Worth"
    pay_note: str = "Pay discussed directly. Check parole conditions with your officer."
class GigApplyIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000)

def render_resume(doc):
    lines = [doc.get("full_name", ""), doc.get("headline", ""), "", doc.get("summary", ""), "", "Skills: " + ", ".join(doc.get("skills", []))]
    for j in doc.get("experience", []):
        lines += ["", f"{j.get('title','')} — {j.get('company','')}", j.get("summary", "")]
    return "\n".join(lines)

@router.get("/job_board")
async def jobs(second_chance: bool | None = None, q: str | None = None):
    items = JOBS
    if second_chance is not None: items = [j for j in items if j["second_chance"] == second_chance]
    if q: items = [j for j in items if q.lower() in (j["title"] + j["company"]).lower()]
    return {"jobs": items, "note": "Check parole or probation conditions with your officer before applying."}
@router.get("/job_board/{job_id}")
async def job(job_id: str):
    for j in JOBS:
        if j["id"] == job_id: return j
    raise HTTPException(404, "job not found")
@router.post("/application_tracker", status_code=201)
async def track(body: AppIn, request: Request, user=Depends(get_current_user)):
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "job_id": body.job_id, "status": body.status}
    await request.app.state.db.applications.insert_one(doc)
    return {k: v for k, v in doc.items()}
@router.get("/application_tracker")
async def list_apps(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.applications.find({"user_id": user["_id"]}).to_list(100)
    return {"applications": [{k: v for k, v in d.items()} for d in items]}

@router.post("/resume_builder", status_code=201)
async def create_resume(body: ResumeIn, request: Request, user=Depends(get_current_user)):
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], **body.model_dump(), "created_at": datetime.now(timezone.utc).isoformat()}
    doc["text"] = render_resume(doc)
    await request.app.state.db.resumes.insert_one(doc)
    return {k: v for k, v in doc.items()}
@router.get("/resume_builder")
async def list_resumes(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.resumes.find({"user_id": user["_id"]}).to_list(100)
    return {"resumes": [{k: v for k, v in d.items()} for d in items]}
@router.get("/resume_builder/{rid}")
async def get_resume(rid: str, request: Request, user=Depends(get_current_user)):
    d = await request.app.state.db.resumes.find_one({"_id": rid, "user_id": user["_id"]})
    if not d: raise HTTPException(404, "not found")
    return {k: v for k, v in d.items()}
@router.delete("/resume_builder/{rid}")
async def del_resume(rid: str, request: Request, user=Depends(get_current_user)):
    r = await request.app.state.db.resumes.delete_one({"_id": rid, "user_id": user["_id"]})
    if r.deleted_count == 0: raise HTTPException(404, "not found")
    return {"deleted": True}

@router.get("/interview_coach/questions")
async def questions(user=Depends(get_current_user)):
    return {"questions": [{"id": q["id"], "prompt": q["prompt"]} for q in INTERVIEW_QUESTIONS], "provider": coach.name}
@router.post("/interview_coach/sessions", status_code=201)
async def answer(body: AnswerIn, request: Request, user=Depends(get_current_user)):
    if body.question_id not in {q["id"] for q in INTERVIEW_QUESTIONS}: raise HTTPException(404, "unknown question")
    result = coach.score(body.question_id, body.answer)
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "question_id": body.question_id, "answer": body.answer, **result, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.interview_sessions.insert_one(doc)
    return {k: v for k, v in doc.items()}
@router.get("/interview_coach/sessions")
async def sessions(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.interview_sessions.find({"user_id": user["_id"]}).to_list(100)
    return {"sessions": [{k: v for k, v in d.items()} for d in items]}

@router.post("/micro_gigs", status_code=201)
async def create_gig(body: GigIn, request: Request, user=Depends(get_current_user)):
    mod = moderation.moderate_public(body.title + " " + body.description)
    _crisis = await crisis_reply.deliver(request.app.state.db, user["_id"], body.title + " " + body.description)
    if mod["decision"] == "remove": raise HTTPException(422, mod["reply"])
    status = "held" if mod["decision"] == "hold" else "published"
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "author_handle": user.get("handle"), **body.model_dump(), "status": status, "moderation": mod, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.micro_gigs.insert_one(doc)
    out = {k: v for k, v in doc.items() if k not in ("user_id",)}
    out["author"] = safety.public_member(user)
    return out
@router.get("/micro_gigs")
async def list_gigs(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.micro_gigs.find({"status": "published"}).to_list(100)
    out = []
    for d in items:
        x = {k: v for k, v in d.items()}
        x.pop("user_id", None)
        out.append(x)
    return {"gigs": out, "note": "Check parole or probation conditions with your officer. Phone numbers are never shown."}
@router.post("/micro_gigs/{gid}/apply", status_code=201)
async def apply_gig(gid: str, body: GigApplyIn, request: Request, user=Depends(get_current_user)):
    gig = await request.app.state.db.micro_gigs.find_one({"_id": gid, "status": "published"})
    if not gig: raise HTTPException(404, "gig not found")
    mod = moderation.moderate_public(body.message)
    _crisis = await crisis_reply.deliver(request.app.state.db, user["_id"], body.message)
    if mod["decision"] == "remove": raise HTTPException(422, mod["reply"])
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "gig_id": gid, "message": body.message, "moderation": mod}
    await request.app.state.db.gig_applications.insert_one(doc)
    return {"id": doc["_id"], "gig_id": gid, "applicant": safety.public_member(user)}
