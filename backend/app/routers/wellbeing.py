"""Wellbeing: mood check-ins, filters, locks. Crisis never blocked."""
import uuid
from datetime import date, datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from .. import locks as lock_policy, outbox
from ..deps import get_current_user
from ._stub import stub_router

router = stub_router("wellbeing", exclude={"mood_checkins", "filters", "locks"})

class MoodIn(BaseModel):
    mood: str = Field(max_length=32)
    note: str | None = Field(default=None, max_length=500)

class FilterIn(BaseModel):
    target: str

class LockIn(BaseModel):
    target: str
    kind: str

def _today():
    return date.today()

@router.post("/mood_checkins", status_code=201)
async def create_checkin(body: MoodIn, request: Request, user=Depends(get_current_user)):
    suggested = lock_policy.suggest_filters(body.mood)
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "mood": body.mood, "note": body.note, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.mood_checkins.insert_one(doc)
    out = {k: v for k, v in doc.items()}
    out["suggested_filters"] = suggested
    out["show_crisis"] = body.mood in lock_policy.ROUGH_MOODS
    return out

@router.get("/mood_checkins")
async def list_checkins(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.mood_checkins.find({"user_id": user["_id"]}).to_list(100)
    return {"checkins": [{k: v for k, v in d.items()} for d in items]}

@router.post("/filters", status_code=201)
async def add_filter(body: FilterIn, request: Request, user=Depends(get_current_user)):
    from ..safety import can_be_hidden
    if not can_be_hidden(body.target):
        raise HTTPException(422, f"{body.target} can never be filtered")
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "target": body.target, "set_on": _today().isoformat()}
    await request.app.state.db.filters.insert_one(doc)
    return {k: v for k, v in doc.items()}

@router.get("/filters")
async def list_filters(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.filters.find({"user_id": user["_id"]}).to_list(100)
    norm = []
    for d in items:
        x = {k: v for k, v in d.items()}
        try:
            x["set_on"] = date.fromisoformat(x["set_on"]) if isinstance(x.get("set_on"), str) else x.get("set_on")
        except Exception:
            pass
        norm.append(x)
    active = lock_policy.active_filters(norm, _today())
    active_ids = {a["_id"] for a in active}
    return {"filters": [{**{k: v for k, v in d.items()}, "set_on": str(d.get("set_on"))} for d in items], "active": [d.get("target") for d in items if d["_id"] in active_ids]}

@router.delete("/filters/{fid}")
async def del_filter(fid: str, request: Request, user=Depends(get_current_user)):
    r = await request.app.state.db.filters.delete_one({"_id": fid, "user_id": user["_id"]})
    if r.deleted_count == 0:
        raise HTTPException(404, "not found")
    return {"deleted": True}

@router.post("/locks", status_code=201)
async def add_lock(body: LockIn, request: Request, user=Depends(get_current_user)):
    try:
        lock = lock_policy.make_lock(body.target, body.kind, datetime.now(timezone.utc))
    except lock_policy.LockError as e:
        raise HTTPException(422, str(e))
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], **lock, "start": lock["start"].isoformat(), "ends": lock["ends"].isoformat() if lock["ends"] else None}
    await request.app.state.db.locks.insert_one(doc)
    if body.kind == "permanent":
        await outbox.enqueue(request.app.state.db, user["_id"], "inapp", "permanent_lock_reminder",
                             {"lock_id": doc["_id"], "target": body.target},
                             lock["start"] + timedelta(days=lock_policy.PERMANENT_REMINDER_DAYS))
    return {k: v for k, v in doc.items()}

@router.get("/locks")
async def list_locks(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.locks.find({"user_id": user["_id"]}).to_list(100)
    now = datetime.now(timezone.utc)
    out = []
    for d in items:
        x = {k: v for k, v in d.items()}
        ends = x.get("ends")
        x["active"] = (ends is None) or (now < datetime.fromisoformat(ends)) if ends else True
        out.append(x)
    return {"locks": out}

@router.delete("/locks/{lid}")
async def del_lock(lid: str, request: Request, user=Depends(get_current_user)):
    r = await request.app.state.db.locks.delete_one({"_id": lid, "user_id": user["_id"]})
    if r.deleted_count == 0:
        raise HTTPException(404, "not found")
    return {"deleted": True}

@router.post("/locks/{lid}/dont_remind")
async def dont_remind(lid: str, request: Request, user=Depends(get_current_user)):
    r = await request.app.state.db.locks.update_one({"_id": lid, "user_id": user["_id"]}, {"$set": {"dont_remind": True}})
    if r.matched_count == 0:
        raise HTTPException(404, "not found")
    return {"dont_remind": True}

@router.get("/locks/check/{feature_id}")
async def check_lock(feature_id: str, request: Request, user=Depends(get_current_user)):
    from .. import registry
    if feature_id in registry.lock_exempt_ids():
        return {"locked": False, "exempt": True}
    items = await request.app.state.db.locks.find({"user_id": user["_id"], "target": feature_id}).to_list(100)
    now = datetime.now(timezone.utc)
    locked = False
    for d in items:
        ends = d.get("ends")
        if ends is None or now < datetime.fromisoformat(ends):
            locked = True
    if locked:
        raise HTTPException(423, f"{feature_id} is locked")
    return {"locked": False}
