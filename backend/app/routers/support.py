"""Support: resources, meetings, mentorship, geolocation (opt-in coarse), rides, accountability."""
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from .. import crisis_reply, moderation, safety
from ..deps import get_current_user
from ..seed_data import COMMUNITY_GROUPS, MEETINGS, RESOURCES
from ._stub import stub_router

router = stub_router("support", exclude={"resource_directory", "twelve_step_locator", "counseling_referrals", "mentorship", "geolocation", "needs_a_ride", "accountability_partners", "carpool_board", "community_groups_directory"})
ALLOWED = {"legal_aid", "treatment", "transit"}

class MentorIn(BaseModel):
    role: str = Field(pattern="^(mentor|mentee)$")
    topics: list[str] = []
    bio: str = ""
class MentorReqIn(BaseModel):
    mentor_handle: str
    message: str = Field(min_length=1, max_length=1000)
class LocationIn(BaseModel):
    city: str = Field(min_length=1, max_length=80)
    lat: float | None = None
    lng: float | None = None
    opt_in: bool = True
class RideIn(BaseModel):
    from_city: str = Field(max_length=80)
    to_city: str = Field(max_length=80)
    on: str = ""
    notes: str = ""
class RideOfferIn(BaseModel):
    request_id: str
    message: str = Field(min_length=1, max_length=1000)
class PartnerIn(BaseModel):
    goals: list[str] = []
    pace: str = "weekly"
class CarpoolIn(BaseModel):
    city: str = Field(min_length=1, max_length=80)
    meeting_source: str = Field(pattern="^(twelve_step|community_group)$")
    meeting_id: str = Field(min_length=1, max_length=32)
    note: str = Field(default="", max_length=500)
    opt_in: bool = True
class RideContactIn(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    member_handle: str | None = None
    quiet_start: int | None = Field(default=None, ge=0, le=23)
    quiet_end: int | None = Field(default=None, ge=0, le=23)
class RideContactPatch(BaseModel):
    label: str | None = Field(default=None, max_length=80)
    quiet_start: int | None = Field(default=None, ge=0, le=23)
    quiet_end: int | None = Field(default=None, ge=0, le=23)
class DriverApprovalIn(BaseModel):
    approved_by: str = Field(min_length=1, max_length=80)
    relationship: str = Field(min_length=1, max_length=80)
class PingNextIn(BaseModel):
    session_id: str
    confirm: bool = False
PING_TIMEOUT_SECONDS = 120
MAX_RIDE_CONTACTS = 10
# TODO: how to verify a non-parent approving adult for a rider with no guardian.
# Driver approval currently records who approved (name + relationship) but does
# not verify them. Do not invent a verification flow until Brann decides it.

@router.get("/resource_directory")
async def resources(category: str | None = None):
    if category and category in ("food", "housing"): raise HTTPException(422, "resource directory does not cover food or housing")
    if category and category not in ALLOWED: raise HTTPException(422, "unknown category")
    return {"resources": [r for r in RESOURCES if not category or r["category"] == category], "categories": sorted(ALLOWED), "excludes": ["food", "housing"]}
@router.get("/twelve_step_locator")
async def meetings(program: str | None = None, day: str | None = None, online: bool | None = None):
    items = MEETINGS
    if program: items = [m for m in items if m["program"].lower() == program.lower()]
    if day: items = [m for m in items if m["day"].lower() == day.lower()]
    if online is not None: items = [m for m in items if m["online"] == online]
    return {"meetings": items}
@router.get("/counseling_referrals")
async def counseling(): return {"referrals": [r for r in RESOURCES if r["category"] == "treatment"]}

@router.post("/mentorship/profile", status_code=201)
async def mentor_profile(body: MentorIn, request: Request, user=Depends(get_current_user)):
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "handle": user.get("handle"), **body.model_dump()}
    await request.app.state.db.mentors.update_one({"user_id": user["_id"]}, {"$set": doc}, upsert=True)
    return {**doc, "public": safety.public_member(user)}
@router.get("/mentorship/mentors")
async def mentors(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.mentors.find({"role": "mentor", "user_id": {"$ne": user["_id"]}}).to_list(100)
    users = {u["_id"]: u for u in await request.app.state.db.users.find({}).to_list(200)}
    out = []
    for d in items:
        out.append({"handle": d.get("handle"), "topics": d.get("topics", []), "bio": d.get("bio", ""), "member": safety.public_member(users.get(d["user_id"], {}))})
    return {"mentors": out}
@router.post("/mentorship/requests", status_code=201)
async def mentor_req(body: MentorReqIn, request: Request, user=Depends(get_current_user)):
    mod = moderation.moderate_public(body.message)
    _crisis = await crisis_reply.deliver(request.app.state.db, user["_id"], body.message)
    if mod["decision"] == "remove": raise HTTPException(422, mod["reply"])
    mentor = await request.app.state.db.mentors.find_one({"handle": body.mentor_handle, "role": "mentor"})
    if not mentor: raise HTTPException(404, "mentor not found")
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "mentor_user_id": mentor["user_id"], "message": body.message, "moderation": mod}
    await request.app.state.db.mentorship_requests.insert_one(doc)
    return {"id": doc["_id"], "mentor_handle": body.mentor_handle, "requester": safety.public_member(user)}

@router.post("/geolocation")
async def set_location(body: LocationIn, request: Request, user=Depends(get_current_user)):
    if not body.opt_in:
        await request.app.state.db.locations.delete_one({"user_id": user["_id"]})
        return {"opt_in": False, "city": None}
    # Coarse only: keep city, discard precise coordinates (round away entirely).
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "city": body.city, "opt_in": True, "precision": "city"}
    await request.app.state.db.locations.update_one({"user_id": user["_id"]}, {"$set": doc}, upsert=True)
    return {"opt_in": True, "city": body.city, "precision": "city"}
@router.get("/geolocation/me")
async def my_location(request: Request, user=Depends(get_current_user)):
    d = await request.app.state.db.locations.find_one({"user_id": user["_id"]})
    if not d: return {"opt_in": False, "city": None}
    return {"opt_in": True, "city": d.get("city"), "precision": "city"}
@router.get("/geolocation/members")
async def member_locations(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.locations.find({"user_id": {"$ne": user["_id"]}}).to_list(100)
    users = {u["_id"]: u for u in await request.app.state.db.users.find({}).to_list(200)}
    return {"members": [{"member": safety.public_member(users.get(d["user_id"], {})), "city": d.get("city")} for d in items]}
@router.delete("/geolocation")
async def clear_location(request: Request, user=Depends(get_current_user)):
    await request.app.state.db.locations.delete_one({"user_id": user["_id"]})
    return {"opt_in": False}

@router.post("/needs_a_ride/requests", status_code=201)
async def ride_req(body: RideIn, request: Request, user=Depends(get_current_user)):
    mod = moderation.moderate_public(body.notes)
    _crisis = await crisis_reply.deliver(request.app.state.db, user["_id"], body.notes)
    if mod["decision"] == "remove": raise HTTPException(422, mod["reply"])
    status = "held" if mod["decision"] == "hold" else "published"
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], **body.model_dump(), "status": status, "moderation": mod, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.ride_requests.insert_one(doc)
    return {**{k: v for k, v in doc.items() if k != "user_id"}, "requester": safety.public_member(user)}
@router.get("/needs_a_ride/requests")
async def ride_list(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.ride_requests.find({"status": "published"}).to_list(100)
    users = {u["_id"]: u for u in await request.app.state.db.users.find({}).to_list(200)}
    return {"requests": [{**{k: v for k, v in d.items() if k != "user_id"}, "requester": safety.public_member(users.get(d["user_id"], {}))} for d in items], "note": "Phone numbers are never shown. Meet in a public place."}
@router.post("/needs_a_ride/offers", status_code=201)
async def ride_offer(body: RideOfferIn, request: Request, user=Depends(get_current_user)):
    req = await request.app.state.db.ride_requests.find_one({"_id": body.request_id, "status": "published"})
    if not req: raise HTTPException(404, "request not found")
    mod = moderation.moderate_public(body.message)
    _crisis = await crisis_reply.deliver(request.app.state.db, user["_id"], body.message)
    if mod["decision"] == "remove": raise HTTPException(422, mod["reply"])
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "request_id": body.request_id, "message": body.message, "moderation": mod}
    await request.app.state.db.ride_offers.insert_one(doc)
    return {"id": doc["_id"], "request_id": body.request_id, "offerer": safety.public_member(user)}

def _meeting_exists(source: str, meeting_id: str) -> bool:
    if source == "twelve_step":
        return any(m["id"] == meeting_id for m in MEETINGS)
    return any(g["id"] == meeting_id for g in COMMUNITY_GROUPS)

def _in_quiet_hours(contact: dict, now_hour: int) -> bool:
    start, end = contact.get("quiet_start"), contact.get("quiet_end")
    if start is None or end is None:
        return False
    if start <= end:
        return start <= now_hour < end
    return now_hour >= start or now_hour < end

@router.get("/community_groups_directory")
async def group_directory(kind: str | None = None, city: str | None = None):
    items = COMMUNITY_GROUPS
    if kind:
        items = [g for g in items if g["kind"] == kind]
    if city:
        items = [g for g in items if g["city"].lower() == city.lower()]
    return {"groups": items, "sample": True, "note": "Sample data only. These are not real listings."}

@router.post("/carpool_board/entries", status_code=201)
async def carpool_add(body: CarpoolIn, request: Request, user=Depends(get_current_user)):
    if not _meeting_exists(body.meeting_source, body.meeting_id):
        raise HTTPException(404, "meeting not found")
    if not body.opt_in:
        await request.app.state.db.carpool_entries.delete_one({"user_id": user["_id"], "meeting_source": body.meeting_source, "meeting_id": body.meeting_id})
        return {"opt_in": False}
    mod = moderation.moderate_public(body.note)
    _crisis = await crisis_reply.deliver(request.app.state.db, user["_id"], body.note)
    if mod["decision"] == "remove":
        raise HTTPException(422, mod["reply"])
    status = "held" if mod["decision"] == "hold" else "published"
    # City-level only: no lat/lng accepted or stored.
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "city": body.city, "precision": "city",
           "meeting_source": body.meeting_source, "meeting_id": body.meeting_id, "note": body.note,
           "status": status, "moderation": mod, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.carpool_entries.update_one(
        {"user_id": user["_id"], "meeting_source": body.meeting_source, "meeting_id": body.meeting_id},
        {"$set": doc}, upsert=True)
    return {**{k: v for k, v in doc.items() if k != "user_id"}, "member": safety.public_member(user)}

@router.get("/carpool_board/entries")
async def carpool_list(request: Request, user=Depends(get_current_user), meeting_id: str | None = None, city: str | None = None):
    q: dict = {"status": "published"}
    if meeting_id:
        q["meeting_id"] = meeting_id
    if city:
        q["city"] = city
    items = await request.app.state.db.carpool_entries.find(q).to_list(200)
    users = {u["_id"]: u for u in await request.app.state.db.users.find({}).to_list(200)}
    return {"entries": [{**{k: v for k, v in d.items() if k != "user_id"}, "member": safety.public_member(users.get(d["user_id"], {}))} for d in items],
            "note": "Opt-in, city-level only. Connect through in-app peer messaging. Phone numbers are never shown."}

@router.get("/carpool_board/matches")
async def carpool_matches(request: Request, user=Depends(get_current_user), meeting_id: str = ""):
    count = await request.app.state.db.carpool_entries.count_documents({"status": "published", "meeting_id": meeting_id, "user_id": {"$ne": user["_id"]}})
    return {"meeting_id": meeting_id, "carpool_count": count}

@router.get("/needs_a_ride/fallback")
async def ride_fallback(request: Request, user=Depends(get_current_user), meeting_id: str = ""):
    count = await request.app.state.db.carpool_entries.count_documents({"status": "published", "meeting_id": meeting_id, "user_id": {"$ne": user["_id"]}})
    return {"meeting_id": meeting_id, "carpool_count": count, "show_fallback": count == 0,
            "note": "Check the carpool board first. Needs a Ride is the backup when nobody is heading that way."}

@router.post("/needs_a_ride/family/contacts", status_code=201)
async def ride_contact_add(body: RideContactIn, request: Request, user=Depends(get_current_user)):
    existing = await request.app.state.db.ride_contacts.count_documents({"user_id": user["_id"]})
    if existing >= MAX_RIDE_CONTACTS:
        raise HTTPException(422, f"up to {MAX_RIDE_CONTACTS} ride contacts")
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "label": body.label, "member_handle": body.member_handle,
           "verified": False, "approved_by": None, "relationship": None,
           "quiet_start": body.quiet_start, "quiet_end": body.quiet_end,
           "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.ride_contacts.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "user_id"}

@router.get("/needs_a_ride/family/contacts")
async def ride_contact_list(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.ride_contacts.find({"user_id": user["_id"]}).to_list(20)
    now_hour = datetime.now(timezone.utc).hour
    out = []
    for d in items:
        x = {k: v for k, v in d.items() if k != "user_id"}
        x["quiet_now"] = _in_quiet_hours(d, now_hour)
        out.append(x)
    return {"contacts": out, "max": MAX_RIDE_CONTACTS}

@router.patch("/needs_a_ride/family/contacts/{cid}")
async def ride_contact_patch(cid: str, body: RideContactPatch, request: Request, user=Depends(get_current_user)):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(422, "nothing to update")
    r = await request.app.state.db.ride_contacts.update_one({"_id": cid, "user_id": user["_id"]}, {"$set": updates})
    if r.matched_count == 0:
        raise HTTPException(404, "contact not found")
    d = await request.app.state.db.ride_contacts.find_one({"_id": cid})
    return {k: v for k, v in d.items() if k != "user_id"}

@router.delete("/needs_a_ride/family/contacts/{cid}")
async def ride_contact_delete(cid: str, request: Request, user=Depends(get_current_user)):
    r = await request.app.state.db.ride_contacts.delete_one({"_id": cid, "user_id": user["_id"]})
    if r.deleted_count == 0:
        raise HTTPException(404, "contact not found")
    return {"deleted": True}

@router.post("/needs_a_ride/family/contacts/{cid}/approve")
async def ride_contact_approve(cid: str, body: DriverApprovalIn, request: Request, user=Depends(get_current_user)):
    r = await request.app.state.db.ride_contacts.update_one(
        {"_id": cid, "user_id": user["_id"]},
        {"$set": {"verified": True, "approved_by": body.approved_by, "relationship": body.relationship}})
    if r.matched_count == 0:
        raise HTTPException(404, "contact not found")
    d = await request.app.state.db.ride_contacts.find_one({"_id": cid})
    return {k: v for k, v in d.items() if k != "user_id"}

@router.post("/needs_a_ride/family/ping/start", status_code=201)
async def ping_start(request: Request, user=Depends(get_current_user)):
    contacts = await request.app.state.db.ride_contacts.find({"user_id": user["_id"], "verified": True}).to_list(20)
    contacts.sort(key=lambda d: d.get("created_at", ""))
    now_hour = datetime.now(timezone.utc).hour
    queue = [c["_id"] for c in contacts if not _in_quiet_hours(c, now_hour)]
    if not queue:
        raise HTTPException(422, "no verified driver available right now")
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "queue": queue, "index": 0,
           "pinged_at": datetime.now(timezone.utc).isoformat(), "timeout_seconds": PING_TIMEOUT_SECONDS,
           "status": "awaiting", "pings": [queue[0]]}
    await request.app.state.db.ride_ping_sessions.insert_one(doc)
    first = await request.app.state.db.ride_contacts.find_one({"_id": queue[0]})
    return {"session_id": doc["_id"], "status": "awaiting", "contact": {k: v for k, v in first.items() if k != "user_id"},
            "timeout_seconds": PING_TIMEOUT_SECONDS}

@router.get("/needs_a_ride/family/ping/{sid}")
async def ping_status(sid: str, request: Request, user=Depends(get_current_user)):
    s = await request.app.state.db.ride_ping_sessions.find_one({"_id": sid, "user_id": user["_id"]})
    if not s:
        raise HTTPException(404, "ping session not found")
    if s["status"] == "awaiting":
        pinged = datetime.fromisoformat(s["pinged_at"])
        if datetime.now(timezone.utc) >= pinged + timedelta(seconds=s["timeout_seconds"]):
            await request.app.state.db.ride_ping_sessions.update_one({"_id": sid}, {"$set": {"status": "timeout"}})
            s["status"] = "timeout"
    contact = await request.app.state.db.ride_contacts.find_one({"_id": s["queue"][s["index"]]})
    return {"session_id": sid, "status": s["status"], "contact": {k: v for k, v in contact.items() if k != "user_id"},
            "remaining": len(s["queue"]) - s["index"] - 1}

@router.post("/needs_a_ride/family/ping/next")
async def ping_next(body: PingNextIn, request: Request, user=Depends(get_current_user)):
    if not body.confirm:
        raise HTTPException(422, "confirm before pinging the next contact")
    s = await request.app.state.db.ride_ping_sessions.find_one({"_id": body.session_id, "user_id": user["_id"]})
    if not s:
        raise HTTPException(404, "ping session not found")
    if s["index"] + 1 >= len(s["queue"]):
        await request.app.state.db.ride_ping_sessions.update_one({"_id": body.session_id}, {"$set": {"status": "done"}})
        return {"session_id": body.session_id, "status": "done", "contact": None}
    nxt = s["index"] + 1
    await request.app.state.db.ride_ping_sessions.update_one(
        {"_id": body.session_id},
        {"$set": {"index": nxt, "pinged_at": datetime.now(timezone.utc).isoformat(), "status": "awaiting"},
         "$push": {"pings": s["queue"][nxt]}})
    contact = await request.app.state.db.ride_contacts.find_one({"_id": s["queue"][nxt]})
    return {"session_id": body.session_id, "status": "awaiting", "contact": {k: v for k, v in contact.items() if k != "user_id"}}

@router.post("/accountability_partners/join", status_code=201)
async def join_partners(body: PartnerIn, request: Request, user=Depends(get_current_user)):
    existing = await request.app.state.db.accountability.find_one({"user_id": user["_id"]})
    if existing: return {k: v for k, v in existing.items()}
    waiting = await request.app.state.db.accountability.find({"group_complete": False}).to_list(100)
    # group 2-to-1 support: 3 members per group
    group_id = waiting[0]["group_id"] if waiting and len(waiting) < 3 else uuid.uuid4().hex
    members_in_group = [w for w in waiting if w["group_id"] == group_id]
    complete = len(members_in_group) + 1 >= 3
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "handle": user.get("handle"), "group_id": group_id, "goals": body.goals, "pace": body.pace, "group_complete": complete}
    await request.app.state.db.accountability.insert_one(doc)
    if complete:
        await request.app.state.db.accountability.update_many({"group_id": group_id}, {"$set": {"group_complete": True}})
    return {k: v for k, v in doc.items()}
@router.get("/accountability_partners/my_group")
async def my_group(request: Request, user=Depends(get_current_user)):
    me = await request.app.state.db.accountability.find_one({"user_id": user["_id"]})
    if not me: return {"group": None, "members": []}
    items = await request.app.state.db.accountability.find({"group_id": me["group_id"]}).to_list(10)
    users = {u["_id"]: u for u in await request.app.state.db.users.find({}).to_list(200)}
    return {"group": me["group_id"], "complete": me.get("group_complete", False), "members": [safety.public_member(users.get(d["user_id"], {})) for d in items]}
