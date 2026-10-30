"""Reentry: 33-step checklist (Brann's exact steps), per-user progress, custom steps, tips, court calendar."""
import uuid
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from .. import checklist as checklist_lib, moderation, outbox, registry, safety
from ..deps import get_current_user
from ._stub import stub_router

router = stub_router("reentry", exclude={"reentry_checklist", "court_calendar"})
CRISIS_LINKS = {"call_988": "tel:988", "text_988": "sms:988", "call_911": "tel:911"}

def _data():
    return checklist_lib.load_data()

def _validate_due(v):
    if v is None:
        return None
    try:
        date.fromisoformat(v)
    except Exception:
        raise HTTPException(422, "due_date must be YYYY-MM-DD")

class ProgressIn(BaseModel):
    step_id: int | None = None
    custom_id: str | None = None
    status: str = Field(default="done", pattern="^(done|in_progress|not_started)$")
    due_date: str | None = None
    priority: str | None = Field(default=None, pattern="^(low|normal|high)$")
    notes: str | None = Field(default=None, max_length=2000)

class CustomStepIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    section: str = "my_steps"
    due_date: str | None = None
    priority: str | None = Field(default=None, pattern="^(low|normal|high)$")
    notes: str | None = Field(default=None, max_length=2000)

class CourtIn(BaseModel):
    on: str
    court: str
    notes: str | None = None

class TipIn(BaseModel):
    body: str = Field(min_length=1, max_length=2000)

async def _progress_map(request, user):
    prog = await request.app.state.db.checklist_progress.find({"user_id": user["_id"]}).to_list(200)
    return {p["step_id"]: p for p in prog if "step_id" in p}

async def _merged(request, user):
    data = _data()
    pmap = await _progress_map(request, user)
    steps = []
    for s in data["steps"]:
        p = pmap.get(s["id"], {})
        step = {**s, "is_custom": False, "status": p.get("status", "not_started"), "due_date": p.get("due_date"), "priority": p.get("priority", "normal"), "notes": p.get("notes", "")}
        if s["id"] == 11:
            step["crisis_links"] = CRISIS_LINKS
        steps.append(step)
    customs = await request.app.state.db.checklist_custom_steps.find({"user_id": user["_id"]}).to_list(200)
    custom_steps = []
    for c in customs:
        x = {k: v for k, v in c.items()}
        x["is_custom"] = True
        custom_steps.append(x)
    done_ids = {s["id"] for s in steps if s["status"] == "done"}
    return data, steps, custom_steps, done_ids

@router.get("/reentry_checklist")
async def checklist(request: Request, user=Depends(get_current_user)):
    data, steps, custom_steps, done_ids = await _merged(request, user)
    sections = checklist_lib.section_progress(data, done_ids)
    return {"steps": steps, "custom_steps": custom_steps, "sections": sections, "section_progress": sections,
            "progress": {"done": len(done_ids), "total": len(steps), "percent": round(100 * len(done_ids) / len(steps)) if steps else 0},
            "celebrations": checklist_lib.celebrations_for(done_ids, data),
            "milestone_days": data.get("milestone_days", list(registry.MILESTONE_DAYS)),
            "crisis_links": CRISIS_LINKS, "status": data.get("_status", "")}

@router.get("/reentry_checklist/progress")
async def get_progress(request: Request, user=Depends(get_current_user)):
    data, steps, custom_steps, done_ids = await _merged(request, user)
    return {"sections": checklist_lib.section_progress(data, done_ids), "done": len(done_ids), "total": len(steps), "custom_steps": custom_steps}

@router.get("/reentry_checklist/celebrations")
async def get_celebrations(request: Request, user=Depends(get_current_user)):
    _, _, _, done_ids = await _merged(request, user)
    return {"celebrations": checklist_lib.celebrations_for(done_ids, _data())}

@router.post("/reentry_checklist/progress")
async def set_progress(body: ProgressIn, request: Request, user=Depends(get_current_user)):
    _validate_due(body.due_date)
    data = _data()
    db = request.app.state.db
    if body.custom_id:
        doc = await db.checklist_custom_steps.find_one({"_id": body.custom_id, "user_id": user["_id"]})
        if not doc:
            raise HTTPException(404, "custom step not found")
        updates = {"status": body.status}
        if body.due_date is not None: updates["due_date"] = body.due_date
        if body.priority is not None: updates["priority"] = body.priority
        if body.notes is not None: updates["notes"] = body.notes
        await db.checklist_custom_steps.update_one({"_id": body.custom_id}, {"$set": updates})
        _, _, _, done_ids = await _merged(request, user)
        return {"custom_id": body.custom_id, "status": body.status, "celebrations": checklist_lib.celebrations_for(done_ids, data)}
    if body.step_id is None:
        raise HTTPException(422, "step_id or custom_id required")
    ids = {s["id"] for s in data["steps"]}
    if body.step_id not in ids:
        raise HTTPException(404, "unknown step")
    before_data, _, _, before_done = await _merged(request, user)
    before = set(c["type"] + ":" + c.get("section", "") for c in checklist_lib.celebrations_for(before_done, data))
    fields = {"user_id": user["_id"], "step_id": body.step_id, "status": body.status, "due_date": body.due_date, "priority": body.priority or "normal", "notes": body.notes or "", "updated_at": datetime.now(timezone.utc).isoformat()}
    await db.checklist_progress.update_one({"user_id": user["_id"], "step_id": body.step_id}, {"$set": fields}, upsert=True)
    _, _, _, done_ids = await _merged(request, user)
    celebrations = checklist_lib.celebrations_for(done_ids, data)
    fired = [c for c in celebrations if (c["type"] + ":" + c.get("section", "")) not in before]
    return {"step_id": body.step_id, "status": body.status, "due_date": body.due_date, "priority": fields["priority"], "notes": fields["notes"], "celebrations": celebrations, "newly_fired": fired}

@router.post("/reentry_checklist/custom_steps", status_code=201)
async def add_custom(body: CustomStepIn, request: Request, user=Depends(get_current_user)):
    _validate_due(body.due_date)
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "id": None, "title": body.title, "section": body.section, "status": "not_started", "due_date": body.due_date, "priority": body.priority or "normal", "notes": body.notes or "", "is_custom": True}
    await request.app.state.db.checklist_custom_steps.insert_one(doc)
    return {k: v for k, v in doc.items()}

@router.delete("/reentry_checklist/custom_steps/{cid}")
async def del_custom(cid: str, request: Request, user=Depends(get_current_user)):
    r = await request.app.state.db.checklist_custom_steps.delete_one({"_id": cid, "user_id": user["_id"]})
    if r.deleted_count == 0:
        raise HTTPException(404, "custom step not found")
    return {"deleted": True}

@router.get("/reentry_checklist/steps/{step_id}/tips")
async def list_tips(step_id: int, request: Request, user=Depends(get_current_user)):
    data = _data()
    if step_id not in {s["id"] for s in data["steps"]}:
        raise HTTPException(404, "unknown step")
    items = await request.app.state.db.checklist_tips.find({"step_id": step_id, "status": "published"}).to_list(200)
    return {"tips": [safety.public_post({**d, "anonymous": True}) for d in items]}

@router.post("/reentry_checklist/steps/{step_id}/tips", status_code=201)
async def add_tip(step_id: int, body: TipIn, request: Request, user=Depends(get_current_user)):
    data = _data()
    if step_id not in {s["id"] for s in data["steps"]}:
        raise HTTPException(404, "unknown step")
    mod = moderation.moderate(body.body)
    if mod["decision"] == "remove":
        raise HTTPException(422, mod["reply"])
    status = "held" if mod["decision"] in ("hold", "crisis") else "published"
    doc = {"_id": uuid.uuid4().hex, "author_id": user["_id"], "author_handle": user.get("handle"), "step_id": step_id, "body": body.body, "anonymous": True, "status": status, "moderation": mod, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.checklist_tips.insert_one(doc)
    out = safety.public_post(doc)
    out["status"] = status
    return out

@router.get("/reentry_checklist/milestones")
async def milestones(user=Depends(get_current_user)):
    return {"milestone_days": list(registry.MILESTONE_DAYS)}

@router.post("/court_calendar", status_code=201)
async def add_court(body: CourtIn, request: Request, user=Depends(get_current_user)):
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "on": body.on, "court": body.court, "notes": body.notes}
    await request.app.state.db.court_dates.insert_one(doc)
    try:
        send_at = datetime.fromisoformat(body.on)
        if send_at.tzinfo is None:
            send_at = send_at.replace(tzinfo=timezone.utc)
    except Exception:
        send_at = datetime.now(timezone.utc)
    await outbox.enqueue(request.app.state.db, user["_id"], "inapp", "court_reminder",
                         {"court_date_id": doc["_id"], "court": body.court, "on": body.on}, send_at)
    return {k: v for k, v in doc.items()}

@router.get("/court_calendar")
async def list_court(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.court_dates.find({"user_id": user["_id"]}).to_list(100)
    return {"court_dates": [{k: v for k, v in d.items()} for d in items]}
