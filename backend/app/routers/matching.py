"""Matching: paid, deterministic local agent. Dating OFF until Brann sets min days (Q6). Exclusions before negotiation."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from .. import safety, tiers
from ..deps import get_current_user
from ..providers import MatcherAgent
from ._stub import stub_router

router = stub_router("matching", exclude={"ai_matching"})
agent = MatcherAgent()
DATING_MIN_DAYS = None  # pending Brann; dating stays OFF until set

class BriefIn(BaseModel):
    intent: str = Field(default="friend", pattern="^(friend|dating|both)$")
    interests: list[str] = []
    dealbreakers: list[str] = []
    must_haves: list[str] = []
    attributes: dict = {}
    friends_only: bool = False
    age_verified_18: bool = False
    days_in_recovery: int = 0
    blocked_handles: list[str] = []
    excluded_handles: list[str] = []  # sponsor/sponsee, mentor/mentee, no-contact: member-entered handles

async def _locked(request, user):
    items = await request.app.state.db.locks.find({"user_id": user["_id"], "target": "ai_matching"}).to_list(100)
    now = datetime.now(timezone.utc)
    return any(d.get("ends") is None or now < datetime.fromisoformat(d["ends"]) for d in items)

def _brief(doc, user):
    return {"handle": user.get("handle"), "intent": doc.get("intent", "friend"), "interests": doc.get("interests", []), "dealbreakers": doc.get("dealbreakers", []), "must_haves": doc.get("must_haves", []), "attributes": doc.get("attributes", {}), "friends_only": doc.get("friends_only", False), "age_verified_18": doc.get("age_verified_18", False), "days_in_recovery": doc.get("days_in_recovery", 0), "blocked_handles": doc.get("blocked_handles", []), "excluded_handles": doc.get("excluded_handles", [])}

def _exclusion(me: dict, other: dict) -> str | None:
    """Deterministic, before any provider call. Returns generic 'not_available' only."""
    if other["handle"] in me.get("blocked_handles", []) or me["handle"] in other.get("blocked_handles", []): return "not_available"
    if other["handle"] in me.get("excluded_handles", []) or me["handle"] in other.get("excluded_handles", []): return "not_available"
    # dating gate: dating OFF until min days configured
    wants_dating = me.get("intent") in ("dating", "both") or other.get("intent") in ("dating", "both")
    if wants_dating:
        if DATING_MIN_DAYS is None: return "not_available"
        if me.get("friends_only") or other.get("friends_only"): return "not_available"
        if not (me.get("age_verified_18") and other.get("age_verified_18")): return "not_available"
        if min(me.get("days_in_recovery", 0), other.get("days_in_recovery", 0)) < DATING_MIN_DAYS: return "not_available"
    return None

@router.post("/ai_matching/profile", status_code=201)
async def set_profile(body: BriefIn, request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "ai_matching")
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "handle": user.get("handle"), **body.model_dump(), "dating_enabled": False}
    await request.app.state.db.match_profiles.update_one({"user_id": user["_id"]}, {"$set": doc}, upsert=True)
    return {**doc, "dating_enabled": False, "note": "Dating is off until a minimum-days rule is set. Friend matching is on."}
@router.get("/ai_matching/profile")
async def get_profile(request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "ai_matching")
    d = await request.app.state.db.match_profiles.find_one({"user_id": user["_id"]})
    if not d: return {"profile": None, "dating_enabled": False}
    return {**{k: v for k, v in d.items()}, "dating_enabled": False}

@router.post("/ai_matching/run")
async def run(request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "ai_matching")
    if await _locked(request, user): raise HTTPException(423, "ai_matching is locked")
    me_doc = await request.app.state.db.match_profiles.find_one({"user_id": user["_id"]})
    if not me_doc: raise HTTPException(422, "set a matching profile first")
    me = _brief(me_doc, user)
    others = await request.app.state.db.match_profiles.find({"user_id": {"$ne": user["_id"]}}).to_list(100)
    users = {u["_id"]: u for u in await request.app.state.db.users.find({}).to_list(200)}
    await request.app.state.db.matches.delete_many({"user_id": user["_id"]})
    results = []
    for od in others:
        other_user = users.get(od["user_id"], {"handle": od.get("handle")})
        other = _brief(od, other_user)
        if _exclusion(me, other):
            dec = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "candidate_handle": other["handle"], "fit": "excluded", "reasons": ["not available"], "score": 0, "excluded": True}
            await request.app.state.db.match_decisions.insert_one(dec)
            results.append({"candidate": safety.public_member(other_user), "fit": "excluded", "reasons": ["not available"], "score": 0})
            continue
        decision = agent.negotiate(me, other)
        # Reasons only from viewer's own side
        reasons = []
        if decision["fit"] == "accept": reasons = [f"You share: {', '.join(decision['shared'])}" if decision["shared"] else "Your preferences line up."]
        else:
            if decision.get("a_blocks"): reasons = [f"You listed {x} as a dealbreaker." for x in decision["a_blocks"]]
            elif decision.get("b_blocks"): reasons = ["Your preferences do not line up with theirs."]
            else: reasons = ["Not enough shared interests yet."]
        dec = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "candidate_handle": other["handle"], "fit": decision["fit"], "reasons": reasons, "score": decision["score"], "excluded": False, "provider": decision["provider"]}
        await request.app.state.db.match_decisions.insert_one(dec)
        if decision["fit"] == "accept":
            m = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "candidate_handle": other["handle"], "score": decision["score"], "status": "suggested"}
            await request.app.state.db.matches.insert_one(m)
        results.append({"candidate": safety.public_member(other_user), "fit": decision["fit"], "reasons": reasons, "score": decision["score"]})
    return {"results": results, "dating_enabled": False, "provider": agent.name}
@router.get("/ai_matching/decisions")
async def decisions(request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "ai_matching")
    items = await request.app.state.db.match_decisions.find({"user_id": user["_id"]}).to_list(100)
    return {"decisions": [{k: v for k, v in d.items() if k != "user_id"} for d in items]}
@router.post("/ai_matching/override", status_code=201)
async def override(body: dict, request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "ai_matching")
    handle = (body or {}).get("candidate_handle", "")
    dec = await request.app.state.db.match_decisions.find_one({"user_id": user["_id"], "candidate_handle": handle})
    if not dec: raise HTTPException(404, "no decision for that candidate")
    if dec.get("excluded"): raise HTTPException(422, "not available")
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "candidate_handle": handle, "status": "intro_requested", "note": "Soft intro request sent. The other member must still accept. This is not an automatic match."}
    await request.app.state.db.match_overrides.insert_one(doc)
    return doc
@router.post("/ai_matching/rematch")
async def rematch(request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "ai_matching")
    await request.app.state.db.matches.delete_many({"user_id": user["_id"]})
    return await run(request, user)
