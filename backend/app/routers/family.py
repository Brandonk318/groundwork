"""Family mode: member controls visibility; every share defaults off."""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from ..deps import get_current_user
from ._stub import stub_router

router = stub_router("family", exclude={"family_mode"})

class VisIn(BaseModel):
    milestones: bool = False
    appointments: bool = False
    portfolio: bool = False

class ApproveIn(BaseModel):
    family_handle: str = Field(min_length=1, max_length=40)

def _vis(doc):
    base = {"milestones": False, "appointments": False, "portfolio": False}
    base.update((doc or {}).get("visibility", {}))
    return base

@router.get("/family_mode/visibility")
async def get_vis(request: Request, user=Depends(get_current_user)):
    doc = await request.app.state.db.family_links.find_one({"member_id": user["_id"]})
    if not doc:
        return {"visibility": {"milestones": False, "appointments": False, "portfolio": False}, "family_members": []}
    return {"visibility": _vis(doc), "family_members": doc.get("family_members", [])}

@router.put("/family_mode/visibility")
async def put_vis(body: VisIn, request: Request, user=Depends(get_current_user)):
    vis = body.model_dump()
    await request.app.state.db.family_links.update_one({"member_id": user["_id"]}, {"$set": {"member_id": user["_id"], "visibility": vis}}, upsert=True)
    return {"visibility": vis}

@router.post("/family_mode/family_members", status_code=201)
async def approve_member(body: ApproveIn, request: Request, user=Depends(get_current_user)):
    fam = await request.app.state.db.users.find_one({"handle": body.family_handle, "role": "family"})
    if not fam:
        raise HTTPException(404, "family account not found")
    # Note: mongomock-motor $addToSet with $each is avoided for compat; store both id and handle plainly.
    await request.app.state.db.family_links.update_one(
        {"member_id": user["_id"]},
        {"$set": {"member_id": user["_id"]}}, upsert=True)
    await request.app.state.db.family_links.update_one(
        {"member_id": user["_id"]},
        {"$addToSet": {"family_members": fam["_id"]}})
    await request.app.state.db.family_links.update_one(
        {"member_id": user["_id"]},
        {"$addToSet": {"family_members": body.family_handle}})
    doc = await request.app.state.db.family_links.find_one({"member_id": user["_id"]})
    return {"family_members": doc.get("family_members", [])}
