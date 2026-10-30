"""Journey: milestones (free), portfolio (paid, private by default)."""
import uuid
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from .. import registry, tiers
from ..deps import get_current_user
from ..seed_data import HOUSING_PLAN_STEPS
from ._stub import stub_router

router = stub_router("journey", exclude={"milestone_celebrations", "journey_portfolio", "token_rewards", "merch_rewards", "progress_share_card", "day_one_archive", "housing_savings"})

class MilestoneIn(BaseModel):
    kind: str = "sobriety"
    start_date: str

class PortfolioIn(BaseModel):
    journey: str = "sobriety"
    title: str = Field(min_length=1, max_length=120)
    story: str = Field(default="", max_length=5000)
    happened_on: str | None = None
    milestone_day: int | None = None
    media: list[dict] = []
    show_dates: bool = False
    visibility: str = "private"
class PortfolioPatch(BaseModel):
    title: str | None = Field(default=None, max_length=120)
    story: str | None = Field(default=None, max_length=5000)
    happened_on: str | None = None
    milestone_day: int | None = None
    show_dates: bool | None = None
    visibility: str | None = None
class ReorderIn(BaseModel):
    order: list[str] = Field(min_length=1)
class ShareIn(BaseModel):
    item_id: str
    revoke: bool = False
VISIBILITIES = ("private", "family", "members", "link")

def _days(start: str):
    try:
        d = date.fromisoformat(start)
    except Exception:
        raise HTTPException(422, "start_date must be YYYY-MM-DD")
    return (date.today() - d).days

def _reached(days: int):
    return [m for m in registry.MILESTONE_DAYS if days >= m]

def _next(days: int):
    for m in registry.MILESTONE_DAYS:
        if days < m:
            return m
    return None

@router.post("/milestone_celebrations", status_code=201)
async def create_ms(body: MilestoneIn, request: Request, user=Depends(get_current_user)):
    days = _days(body.start_date)
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "kind": body.kind, "start_date": body.start_date, "days": days, "reached": _reached(days), "next": _next(days), "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.milestones.insert_one(doc)
    return {k: v for k, v in doc.items()}

@router.get("/milestone_celebrations")
async def list_ms(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.milestones.find({"user_id": user["_id"]}).to_list(100)
    out = []
    for d in items:
        x = {k: v for k, v in d.items()}
        days = _days(x["start_date"])
        x["days"] = days; x["reached"] = _reached(days); x["next"] = _next(days)
        out.append(x)
    return {"milestones": out, "milestone_days": list(registry.MILESTONE_DAYS)}

@router.post("/journey_portfolio/items", status_code=201)
async def add_item(body: PortfolioIn, request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "journey_portfolio")
    if body.visibility not in VISIBILITIES:
        raise HTTPException(422, "invalid visibility")
    if body.happened_on is not None:
        try: date.fromisoformat(body.happened_on)
        except Exception: raise HTTPException(422, "happened_on must be YYYY-MM-DD")
    if body.milestone_day is not None and body.milestone_day not in registry.MILESTONE_DAYS:
        raise HTTPException(422, "milestone_day must be a milestone day")
    existing = await request.app.state.db.portfolio_items.find({"user_id": user["_id"]}).to_list(500)
    pos = max([d.get("position", 0) for d in existing], default=-1) + 1
    # Media keys reference media_store uploads, which strip EXIF/GPS on save (app/media.py); never re-expose metadata here.
    media = [{"kind": m.get("kind", ""), "key": m.get("key", "")} for m in body.media]
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "journey": body.journey, "title": body.title, "story": body.story,
           "happened_on": body.happened_on, "milestone_day": body.milestone_day, "media": media, "show_dates": body.show_dates,
           "visibility": "private" if body.visibility == "link" else body.visibility,
           "position": pos, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.portfolio_items.insert_one(doc)
    return {k: v for k, v in doc.items()}

@router.get("/journey_portfolio/items")
async def list_items(request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "journey_portfolio")
    items = await request.app.state.db.portfolio_items.find({"user_id": user["_id"]}).to_list(500)
    items.sort(key=lambda d: (d.get("position", 0), d.get("created_at", "")))
    return {"items": [{k: v for k, v in d.items()} for d in items]}

@router.patch("/journey_portfolio/items/{item_id}")
async def patch_item(item_id: str, body: PortfolioPatch, request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "journey_portfolio")
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if "visibility" in updates and updates["visibility"] not in VISIBILITIES:
        raise HTTPException(422, "invalid visibility")
    if "happened_on" in updates:
        try: date.fromisoformat(updates["happened_on"])
        except Exception: raise HTTPException(422, "happened_on must be YYYY-MM-DD")
    if "milestone_day" in updates and updates["milestone_day"] not in registry.MILESTONE_DAYS:
        raise HTTPException(422, "milestone_day must be a milestone day")
    if not updates:
        raise HTTPException(422, "nothing to update")
    r = await request.app.state.db.portfolio_items.update_one({"_id": item_id, "user_id": user["_id"]}, {"$set": updates})
    if r.matched_count == 0:
        raise HTTPException(404, "item not found")
    d = await request.app.state.db.portfolio_items.find_one({"_id": item_id})
    return {k: v for k, v in d.items()}

@router.delete("/journey_portfolio/items/{item_id}")
async def delete_item(item_id: str, request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "journey_portfolio")
    await request.app.state.db.portfolio_shares.delete_many({"item_id": item_id, "user_id": user["_id"]})
    r = await request.app.state.db.portfolio_items.delete_one({"_id": item_id, "user_id": user["_id"]})
    if r.deleted_count == 0:
        raise HTTPException(404, "item not found")
    return {"deleted": True}

@router.post("/journey_portfolio/reorder")
async def reorder(body: ReorderIn, request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "journey_portfolio")
    mine = {d["_id"] for d in await request.app.state.db.portfolio_items.find({"user_id": user["_id"]}).to_list(500)}
    if set(body.order) != mine:
        raise HTTPException(422, "order must list every item exactly once")
    for pos, iid in enumerate(body.order):
        await request.app.state.db.portfolio_items.update_one({"_id": iid}, {"$set": {"position": pos}})
    return {"order": body.order}

def _public_item(d: dict) -> dict:
    out = {"id": d["_id"], "journey": d.get("journey"), "title": d.get("title"), "story": d.get("story"),
           "media": d.get("media", []), "milestone_day": d.get("milestone_day"),
           "visibility": d.get("visibility"), "noindex": True}
    if d.get("show_dates"):
        out["happened_on"] = d.get("happened_on")
    return out

@router.post("/journey_portfolio/share", status_code=201)
async def share_mint(body: ShareIn, request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "journey_portfolio")
    item = await request.app.state.db.portfolio_items.find_one({"_id": body.item_id, "user_id": user["_id"]})
    if not item:
        raise HTTPException(404, "item not found")
    if body.revoke:
        await request.app.state.db.portfolio_shares.delete_many({"item_id": body.item_id, "user_id": user["_id"]})
        await request.app.state.db.portfolio_items.update_one({"_id": body.item_id}, {"$set": {"visibility": "private"}})
        return {"revoked": True, "item_id": body.item_id}
    token = uuid.uuid4().hex + uuid.uuid4().hex
    await request.app.state.db.portfolio_items.update_one({"_id": body.item_id}, {"$set": {"visibility": "link"}})
    await request.app.state.db.portfolio_shares.insert_one(
        {"_id": uuid.uuid4().hex, "user_id": user["_id"], "item_id": body.item_id, "token": token,
         "created_at": datetime.now(timezone.utc).isoformat()})
    return {"item_id": body.item_id, "token": token, "url": f"/p/{token}"}

@router.get("/journey_portfolio/family")
async def family_view(request: Request, user=Depends(get_current_user), member_handle: str = ""):
    member = await request.app.state.db.users.find_one({"handle": member_handle})
    if not member:
        raise HTTPException(404, "member not found")
    link = await request.app.state.db.family_links.find_one({"member_id": member["_id"]})
    vis = (link or {}).get("visibility", {})
    approved = (link or {}).get("family_members", [])
    if not vis.get("portfolio") or user["_id"] not in approved and user.get("handle") not in approved:
        raise HTTPException(404, "not shared")
    items = await request.app.state.db.portfolio_items.find({"user_id": member["_id"], "visibility": "family"}).to_list(200)
    return {"items": [_public_item(d) for d in items]}

public_router = APIRouter()

@public_router.get("/p/{token}")
async def shared_view(token: str, request: Request):
    share = await request.app.state.db.portfolio_shares.find_one({"token": token})
    if not share:
        raise HTTPException(404, "link not found")
    item = await request.app.state.db.portfolio_items.find_one({"_id": share["item_id"]})
    if not item or item.get("visibility") != "link":
        raise HTTPException(404, "link not found")
    return JSONResponse(content={"item": _public_item(item)}, headers={"X-Robots-Tag": "noindex"})

@router.get("/journey_portfolio/suggestions")
async def suggestions(request: Request, user=Depends(get_current_user)):
    tiers.require(user.get("tier", "free"), "journey_portfolio")
    days = await _max_days(request, user)
    reached = _reached(days)
    have = {d.get("milestone_day") for d in await request.app.state.db.portfolio_items.find({"user_id": user["_id"]}).to_list(500)}
    return {"suggestions": [{"milestone_day": m, "title": f"Day {m}: add a portfolio item", "auto_published": False}
                            for m in reached if m not in have], "note": "Suggestions only. Nothing is published until you add it."}

# --- Phase 3 journey ---
MERCH = [
    {"id": "mark-tee-30", "name": "Foundation Tee — One Mark", "milestone_day": 30, "code": "one stripe at the hem", "price_cents": None, "visible_text": "GROUNDWORK"},
    {"id": "mark-hoodie-90", "name": "Foundation Hoodie — Three Marks", "milestone_day": 90, "code": "three stripes at the hem", "price_cents": None, "visible_text": "GROUNDWORK"},
    {"id": "mark-cap-180", "name": "Foundation Cap — Circle Mark", "milestone_day": 180, "code": "small circle at the hem", "price_cents": None, "visible_text": "GROUNDWORK"},
]
BANNED_VISIBLE = ("sober", "sobriety", "recovery", "addict", "jail", "prison", "clean time")

class EarnIn(BaseModel):
    reason: str = Field(min_length=1, max_length=80)
    points: int = Field(ge=1, le=1000)
class ClaimIn(BaseModel):
    item_id: str
class ArchiveIn(BaseModel):
    body: str = Field(min_length=1, max_length=5000)
    unlock_day: int = Field(default=30)

async def _balance(request, user):
    items = await request.app.state.db.token_ledger.find({"user_id": user["_id"]}).to_list(500)
    return sum(d.get("points", 0) for d in items), items
async def _max_days(request, user):
    items = await request.app.state.db.milestones.find({"user_id": user["_id"]}).to_list(100)
    best = 0
    for d in items:
        try: best = max(best, _days(d["start_date"]))
        except Exception: pass
    # checklist all-done also counts as progression without dates
    return best

@router.get("/token_rewards")
async def balance(request: Request, user=Depends(get_current_user)):
    bal, items = await _balance(request, user)
    return {"balance": bal, "cash_value_cents": 0, "cash_value": None, "note": "Tokens have no cash value.", "ledger": [{k: v for k, v in d.items()} for d in items]}
@router.post("/token_rewards/earn", status_code=201)
async def earn(body: EarnIn, request: Request, user=Depends(get_current_user)):
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "reason": body.reason, "points": body.points, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.token_ledger.insert_one(doc)
    bal, _ = await _balance(request, user)
    return {"balance": bal, "cash_value_cents": 0, "entry": {k: v for k, v in doc.items()}}
@router.post("/token_rewards/redeem", status_code=201)
async def redeem(body: EarnIn, request: Request, user=Depends(get_current_user)):
    bal, _ = await _balance(request, user)
    if body.points > bal: raise HTTPException(422, "not enough tokens")
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "reason": body.reason, "points": -body.points, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.token_ledger.insert_one(doc)
    bal2, _ = await _balance(request, user)
    return {"balance": bal2, "cash_value_cents": 0}

@router.get("/merch_rewards")
async def merch(request: Request, user=Depends(get_current_user)):
    days = await _max_days(request, user)
    out = []
    for m in MERCH:
        assert not any(b in (m["name"] + m["visible_text"]).lower() for b in BANNED_VISIBLE)
        out.append({**m, "eligible": days >= m["milestone_day"], "days": days})
    return {"items": out, "note": "Coded marks only. No wording or dates are printed on the outside."}
@router.post("/merch_rewards/claim", status_code=201)
async def claim(body: ClaimIn, request: Request, user=Depends(get_current_user)):
    item = next((m for m in MERCH if m["id"] == body.item_id), None)
    if not item: raise HTTPException(404, "item not found")
    days = await _max_days(request, user)
    if days < item["milestone_day"]: raise HTTPException(422, "milestone not reached yet")
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "item_id": item["id"], "price_cents": None, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.merch_claims.insert_one(doc)
    return {"claim": {k: v for k, v in doc.items()}, "item": item}

@router.post("/progress_share_card", status_code=201)
async def share_card(request: Request, user=Depends(get_current_user)):
    days = await _max_days(request, user)
    prog = await request.app.state.db.checklist_progress.find({"user_id": user["_id"], "status": "done"}).to_list(200)
    bal, _ = await _balance(request, user)
    stats = {"checklist_done": len(prog), "checklist_total": 33, "days": days, "tokens": bal}
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='600' height='315'><rect width='600' height='315' fill='#173f35'/><text x='30' y='70' fill='white' font-size='28'>My progress</text><text x='30' y='120' fill='white' font-size='20'>Checklist steps done: {stats['checklist_done']} / 33</text><text x='30' y='155' fill='white' font-size='20'>Days: {days}</text><text x='30' y='190' fill='white' font-size='20'>Tokens: {bal}</text></svg>"
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "stats": stats, "svg": svg, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.share_cards.insert_one(doc)
    return {k: v for k, v in doc.items()}
@router.get("/progress_share_card")
async def my_cards(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.share_cards.find({"user_id": user["_id"]}).to_list(100)
    return {"cards": [{k: v for k, v in d.items()} for d in items]}

@router.post("/day_one_archive", status_code=201)
async def seal(body: ArchiveIn, request: Request, user=Depends(get_current_user)):
    if body.unlock_day not in (30, 60, 90, 180, 365): raise HTTPException(422, "unlock_day must be a milestone day")
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], "body": body.body, "unlock_day": body.unlock_day, "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.day_one_archive.insert_one(doc)
    return {"id": doc["_id"], "sealed": True, "unlock_day": body.unlock_day}
@router.get("/day_one_archive")
async def my_archive(request: Request, user=Depends(get_current_user)):
    days = await _max_days(request, user)
    items = await request.app.state.db.day_one_archive.find({"user_id": user["_id"]}).to_list(100)
    out = []
    for d in items:
        unlocked = days >= d.get("unlock_day", 30)
        x = {"id": d["_id"], "unlock_day": d.get("unlock_day"), "sealed": not unlocked, "unlocked": unlocked}
        if unlocked: x["body"] = d.get("body")
        out.append(x)
    return {"archive": out, "days": days}

# --- Housing savings (211 pointers only; never provides housing) ---
class SavingsGoalIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    target_cents: int = Field(ge=1)
    saved_cents: int = Field(default=0, ge=0)
class SavingsUpdate(BaseModel):
    saved_cents: int = Field(ge=0)
class PlanCheckIn(BaseModel):
    step_id: str
    done: bool = True
class SavingsCalcIn(BaseModel):
    target_cents: int = Field(ge=1)
    saved_cents: int = Field(ge=0)
    monthly_cents: int = Field(ge=1)

HOUSING_NOTE = "Groundwork does not provide housing and does not partner with housing providers. For local help, call 211."

@router.get("/housing_savings/goals")
async def goal_list(request: Request, user=Depends(get_current_user)):
    items = await request.app.state.db.savings_goals.find({"user_id": user["_id"]}).to_list(100)
    return {"goals": [{k: v for k, v in d.items() if k != "user_id"} for d in items], "note": HOUSING_NOTE}
@router.post("/housing_savings/goals", status_code=201)
async def goal_add(body: SavingsGoalIn, request: Request, user=Depends(get_current_user)):
    doc = {"_id": uuid.uuid4().hex, "user_id": user["_id"], **body.model_dump(), "created_at": datetime.now(timezone.utc).isoformat()}
    await request.app.state.db.savings_goals.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "user_id"}
@router.patch("/housing_savings/goals/{gid}")
async def goal_update(gid: str, body: SavingsUpdate, request: Request, user=Depends(get_current_user)):
    r = await request.app.state.db.savings_goals.update_one({"_id": gid, "user_id": user["_id"]}, {"$set": {"saved_cents": body.saved_cents}})
    if r.matched_count == 0:
        raise HTTPException(404, "goal not found")
    d = await request.app.state.db.savings_goals.find_one({"_id": gid})
    return {k: v for k, v in d.items() if k != "user_id"}
@router.delete("/housing_savings/goals/{gid}")
async def goal_delete(gid: str, request: Request, user=Depends(get_current_user)):
    r = await request.app.state.db.savings_goals.delete_one({"_id": gid, "user_id": user["_id"]})
    if r.deleted_count == 0:
        raise HTTPException(404, "goal not found")
    return {"deleted": True}
@router.post("/housing_savings/calculator")
async def savings_calc(body: SavingsCalcIn, user=Depends(get_current_user)):
    # All figures come from the member's own inputs; nothing is invented.
    remaining = max(0, body.target_cents - body.saved_cents)
    months = (remaining + body.monthly_cents - 1) // body.monthly_cents if remaining else 0
    return {"target_cents": body.target_cents, "saved_cents": body.saved_cents, "monthly_cents": body.monthly_cents,
            "remaining_cents": remaining, "months": months}
@router.get("/housing_savings/plan")
async def plan_get(request: Request, user=Depends(get_current_user)):
    checks = await request.app.state.db.housing_plan.find({"user_id": user["_id"]}).to_list(50)
    done = {c["step_id"] for c in checks if c.get("done")}
    return {"steps": [{**s, "done": s["id"] in done} for s in HOUSING_PLAN_STEPS], "note": HOUSING_NOTE}
@router.post("/housing_savings/plan/check")
async def plan_check(body: PlanCheckIn, request: Request, user=Depends(get_current_user)):
    if body.step_id not in {s["id"] for s in HOUSING_PLAN_STEPS}:
        raise HTTPException(404, "plan step not found")
    await request.app.state.db.housing_plan.update_one(
        {"user_id": user["_id"], "step_id": body.step_id},
        {"$set": {"user_id": user["_id"], "step_id": body.step_id, "done": body.done}}, upsert=True)
    return {"step_id": body.step_id, "done": body.done}
