"""Community: feed, anonymous posting, peer messaging (no phone numbers)."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from .. import crisis_reply, moderation, safety
from ..deps import get_current_user
from ._stub import stub_router

router = stub_router("community", exclude={"community_feed", "anonymous_posting", "peer_messaging", "events", "program_groups", "virtual_meetings", "video_posts", "photo_posts", "voice_notes", "anonymous_qa"})

class PostIn(BaseModel):
    body: str = Field(min_length=1, max_length=5000)
    anonymous: bool = False
    group: str | None = None

class MsgIn(BaseModel):
    recipient_id: str
    body: str = Field(min_length=1, max_length=5000)

async def _locked(request, user, fid):
    if fid in __import__("app.registry", fromlist=["lock_exempt_ids"]).lock_exempt_ids():
        return False
    items = await request.app.state.db.locks.find({"user_id": user["_id"], "target": fid}).to_list(100)
    now = datetime.now(timezone.utc)
    for d in items:
        ends = d.get("ends")
        if ends is None or now < datetime.fromisoformat(ends):
            return True
    return False

class ModIn(BaseModel):
    body: str = Field(min_length=1, max_length=5000)

@router.post("/moderation/check")
async def mod_check(body: ModIn, user=Depends(get_current_user)):
    return moderation.moderate(body.body)

@router.post("/community_feed/posts", status_code=201)
async def create_post(body: PostIn, request: Request, user=Depends(get_current_user)):
    if await _locked(request, user, "community_feed"):
        raise HTTPException(423, "community_feed is locked")
    mod = moderation.moderate_public(body.body)
    _crisis = await crisis_reply.deliver(request.app.state.db, user["_id"], body.body)
    if mod["decision"] == "remove":
        raise HTTPException(422, mod["reply"])
    status = "held" if mod["decision"] == "hold" else "published"
    doc = {"_id": uuid.uuid4().hex, "author_id": user["_id"], "author_handle": user.get("handle"), "body": body.body, "anonymous": body.anonymous, "group": body.group, "status": status, "moderation": mod, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.posts.insert_one(doc)
    out = safety.public_post(doc)
    if _crisis: out["private_notice"] = _crisis  # author's own response only; never stored on the post
    return out

@router.get("/community_feed/posts")
async def list_posts(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.posts.find({"status": "published"}).to_list(100)
    return {"posts": [safety.public_post(d) for d in items]}

@router.post("/anonymous_posting/posts", status_code=201)
async def anon_post(body: PostIn, request: Request, user=Depends(get_current_user)):
    body.anonymous = True
    return await create_post(body, request, user)

@router.get("/members")
async def members(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.users.find({"_id": {"$ne": user["_id"]}}).to_list(100)
    return {"members": [safety.public_member(d) for d in items]}

@router.post("/peer_messaging/messages", status_code=201)
async def send_msg(body: MsgIn, request: Request, user=Depends(get_current_user)):
    if await _locked(request, user, "peer_messaging"):
        raise HTTPException(423, "peer_messaging is locked")
    recip = await request.app.state.db.users.find_one({"_id": body.recipient_id}) or await request.app.state.db.users.find_one({"handle": body.recipient_id})
    if not recip:
        raise HTTPException(404, "recipient not found")
    body_recipient_id = recip["_id"]
    mod = moderation.moderate_public(body.body)
    _crisis = await crisis_reply.deliver(request.app.state.db, user["_id"], body.body)
    if mod["decision"] == "remove":
        raise HTTPException(422, mod["reply"])
    doc = {"_id": uuid.uuid4().hex, "sender_id": user["_id"], "recipient_id": body_recipient_id, "body": body.body, "moderation": mod, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.messages.insert_one(doc)
    return {"id": doc["_id"], "recipient": safety.public_member(recip), "sender": safety.public_member(user), "body": body.body, "created_at": doc["created_at"]}

@router.get("/peer_messaging/messages")
async def list_msgs(request: Request, user=Depends(get_current_user)):
    sent = await request.app.state.db.messages.find({"sender_id": user["_id"]}).to_list(100)
    recv = await request.app.state.db.messages.find({"recipient_id": user["_id"]}).to_list(100)
    allm = sent + recv
    return {"messages": [{k: v for k, v in d.items()} for d in allm]}

@router.get("/peer_messaging/conversation/{other_id}")
async def convo(other_id: str, request: Request, user=Depends(get_current_user)):
    other = await request.app.state.db.users.find_one({"_id": other_id}) or await request.app.state.db.users.find_one({"handle": other_id})
    if other:
        other_id = other["_id"]
    if not other:
        raise HTTPException(404, "not found")
    sent = await request.app.state.db.messages.find({"sender_id": user["_id"], "recipient_id": other_id}).to_list(100)
    recv = await request.app.state.db.messages.find({"sender_id": other_id, "recipient_id": user["_id"]}).to_list(100)
    msgs = sorted(sent + recv, key=lambda d: d.get("created_at", ""))
    return {"with": safety.public_member(other), "messages": [{k: v for k, v in d.items()} for d in msgs]}

# --- Phase 3 community ---
from .. import media as media_lib, tiers as tiers_lib

class EventIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    on: str = ""
    city: str = "Fort Worth"
    description: str = ""
class GroupIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    program: str = "general"
    description: str = ""
class MeetingIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    on: str = ""
class UploadIn(BaseModel):
    filename: str = "upload"
    content_type: str
    data_b64: str
    caption: str = ""
class QaQIn(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
class QaAIn(BaseModel):
    body: str = Field(min_length=1, max_length=2000)

def _mod_or_422(text):
    mod = moderation.moderate_public(text)
    if mod["decision"] == "remove": raise HTTPException(422, mod["reply"])
    return mod, ("held" if mod["decision"] == "hold" else "published")

@router.post("/events", status_code=201)
async def create_event(body: EventIn, request: Request, user=Depends(get_current_user)):
    mod, status = _mod_or_422(body.title + " " + body.description)
    _crisis = await crisis_reply.deliver(request.app.state.db, user["_id"], body.title + " " + body.description)
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], **body.model_dump(), "status": status, "moderation": mod}
    await request.app.state.db.events.insert_one(doc)
    return {k: v for k, v in doc.items()}
@router.get("/events")
async def list_events(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.events.find({"status": "published"}).to_list(100)
    return {"events": [{k: v for k, v in d.items()} for d in items]}
@router.post("/events/{eid}/rsvp", status_code=201)
async def rsvp(eid: str, request: Request, user=Depends(get_current_user)):
    ev = await request.app.state.db.events.find_one({"_id": eid, "status": "published"})
    if not ev: raise HTTPException(404, "event not found")
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "event_id": eid}
    await request.app.state.db.event_rsvps.update_one({"user_id": user["_id"], "event_id": eid}, {"$set": doc}, upsert=True)
    count = await request.app.state.db.event_rsvps.count_documents({"event_id": eid})
    return {"event_id": eid, "rsvp": True, "count": count}

@router.post("/program_groups", status_code=201)
async def create_group(body: GroupIn, request: Request, user=Depends(get_current_user)):
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], **body.model_dump()}
    await request.app.state.db.program_groups.insert_one(doc)
    await request.app.state.db.group_memberships.insert_one({"_id": uuid.uuid4().hex, "user_id": user["_id"], "group_id": doc["_id"]})
    return {k: v for k, v in doc.items()}
@router.get("/program_groups")
async def list_groups(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.program_groups.find({}).to_list(100)
    out = []
    for d in items:
        x = {k: v for k, v in d.items()}
        x["members"] = await request.app.state.db.group_memberships.count_documents({"group_id": d["_id"]})
        out.append(x)
    return {"groups": out}
@router.post("/program_groups/{gid}/join", status_code=201)
async def join_group(gid: str, request: Request, user=Depends(get_current_user)):
    g = await request.app.state.db.program_groups.find_one({"_id": gid})
    if not g: raise HTTPException(404, "group not found")
    await request.app.state.db.group_memberships.update_one({"user_id": user["_id"], "group_id": gid}, {"$set": {"user_id": user["_id"], "group_id": gid}}, upsert=True)
    return {"group_id": gid, "joined": True, "members": await request.app.state.db.group_memberships.count_documents({"group_id": gid})}

@router.post("/virtual_meetings", status_code=201)
async def create_meeting(body: MeetingIn, request: Request, user=Depends(get_current_user)):
    room = uuid.uuid4().hex[:12]
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], **body.model_dump(), "room": room, "join_path": f"/meet/{room}", "provider": "local-room-placeholder"}
    await request.app.state.db.virtual_meetings.insert_one(doc)
    return {k: v for k, v in doc.items()}
@router.get("/virtual_meetings")
async def list_meetings2(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.virtual_meetings.find({}).to_list(100)
    return {"meetings": [{k: v for k, v in d.items()} for d in items]}

async def _upload(kind, fid, body: UploadIn, request, user):
    if fid == "video_posts": tiers_lib.require(user.get("tier", "free"), "video_posts")
    try:
        meta = media_lib.save_upload(user["_id"], kind, body.filename, body.content_type, body.data_b64)
    except ValueError as e:
        raise HTTPException(422, str(e))
    mod, status = _mod_or_422(body.caption or "media")
    _crisis = await crisis_reply.deliver(request.app.state.db, user["_id"], body.caption or "media")
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "kind": kind, "feature": fid, "caption": body.caption, **meta, "status": status, "moderation": mod, "created_at": datetime.now(timezone.utc).isoformat()}
    # never persist raw base64 in DB
    await request.app.state.db.media_posts.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "user_id"}
@router.post("/photo_posts", status_code=201)
async def photo(body: UploadIn, request: Request, user=Depends(get_current_user)): return await _upload("photo", "photo_posts", body, request, user)
@router.post("/video_posts", status_code=201)
async def video(body: UploadIn, request: Request, user=Depends(get_current_user)): return await _upload("video", "video_posts", body, request, user)
@router.post("/voice_notes", status_code=201)
async def voice(body: UploadIn, request: Request, user=Depends(get_current_user)): return await _upload("voice", "voice_notes", body, request, user)
@router.get("/media_posts")
async def my_media(request: Request, user=Depends(get_current_user), kind: str | None = None):
    q = {"user_id": user["_id"]}
    if kind: q["kind"] = kind
    items = await request.app.state.db.media_posts.find(q).to_list(100)
    return {"media": [{k: v for k, v in d.items() if k != "user_id"} for d in items]}

@router.post("/anonymous_qa/questions", status_code=201)
async def qa_q(body: QaQIn, request: Request, user=Depends(get_current_user)):
    mod, status = _mod_or_422(body.body)
    _crisis = await crisis_reply.deliver(request.app.state.db, user["_id"], body.body)
    doc = {"_id": uuid.uuid4().hex, "author_id": user["_id"], "author_handle": user.get("handle"), "body": body.body, "anonymous": True, "status": status, "moderation": mod, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.qa_questions.insert_one(doc)
    out = safety.public_post(doc); out["status"] = status; out["id"] = doc["_id"]
    if _crisis: out["private_notice"] = _crisis
    return out
@router.get("/anonymous_qa/questions")
async def qa_list(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.qa_questions.find({"status": "published"}).to_list(100)
    out = []
    for d in items:
        x = safety.public_post(d); x["id"] = d["_id"]
        answers = await request.app.state.db.qa_answers.find({"question_id": d["_id"], "status": "published"}).to_list(100)
        x["answers"] = [{**safety.public_post({**a, "anonymous": True}), "id": a["_id"]} for a in answers]
        out.append(x)
    return {"questions": out}
@router.post("/anonymous_qa/questions/{qid}/answers", status_code=201)
async def qa_a(qid: str, body: QaAIn, request: Request, user=Depends(get_current_user)):
    q = await request.app.state.db.qa_questions.find_one({"_id": qid, "status": "published"})
    if not q: raise HTTPException(404, "question not found")
    mod, status = _mod_or_422(body.body)
    _crisis = await crisis_reply.deliver(request.app.state.db, user["_id"], body.body)
    doc = {"_id": uuid.uuid4().hex, "author_id": user["_id"], "author_handle": user.get("handle"), "question_id": qid, "body": body.body, "anonymous": True, "status": status, "moderation": mod, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.qa_answers.insert_one(doc)
    out = safety.public_post(doc); out["status"] = status; out["id"] = doc["_id"]
    if _crisis: out["private_notice"] = _crisis
    return out
