"""Learning: courses + life-skills courses (one module, paid, DRAFT curriculum)."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from .. import tiers
from ..deps import get_current_user
from ..providers import COURSES
from ._stub import stub_router

router = stub_router("learning", exclude={"courses", "courses_life_skills"})

class QuizIn(BaseModel):
    course_id: str
    module_id: str
    answer: int
class ProgressIn(BaseModel):
    course_id: str
    module_id: str

def _find(course_id, module_id=None):
    c = next((x for x in COURSES if x["id"] == course_id), None)
    if not c: raise HTTPException(404, "course not found")
    if module_id is None: return c, None
    m = next((x for x in c["modules"] if x["id"] == module_id), None)
    if not m: raise HTTPException(404, "module not found")
    return c, m

@router.get("/courses")
async def catalog(user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "courses")
    return {"courses": COURSES, "draft": True}
@router.get("/courses_life_skills")
async def catalog2(user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "courses_life_skills")
    return {"courses": COURSES, "draft": True}
@router.get("/courses/{course_id}")
async def one(course_id: str, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "courses")
    c, _ = _find(course_id)
    return c
@router.post("/courses/progress", status_code=201)
async def progress(body: ProgressIn, request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "courses")
    _find(body.course_id, body.module_id)
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "course_id": body.course_id, "module_id": body.module_id, "status": "done"}
    await request.app.state.db.course_progress.update_one({"user_id": user["_id"], "course_id": body.course_id, "module_id": body.module_id}, {"$set": doc}, upsert=True)
    items = await request.app.state.db.course_progress.find({"user_id": user["_id"]}).to_list(200)
    return {"done_modules": [{"course_id": d["course_id"], "module_id": d["module_id"]} for d in items]}
@router.get("/courses_progress")
async def my_progress(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.course_progress.find({"user_id": user["_id"]}).to_list(200)
    return {"done_modules": [{"course_id": d["course_id"], "module_id": d["module_id"]} for d in items]}
@router.post("/courses/quiz")
async def quiz(body: QuizIn, request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "courses")
    _, m = _find(body.course_id, body.module_id)
    q = m["quiz"][0]
    correct = body.answer == q["answer"]
    return {"correct": correct, "answer": q["answer"], "score": 100 if correct else 0}
