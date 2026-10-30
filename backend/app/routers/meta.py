"""Health, feature registry, plan table, and auth (member/family/admin)."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from .. import registry, safety, security, tiers
from ..deps import get_current_user

router = APIRouter(prefix="/api", tags=["meta"])

class RegisterIn(BaseModel):
    handle: str = Field(min_length=2, max_length=40)
    password: str = Field(min_length=8, max_length=200)
    role: str = "member"
    phone: str | None = None
    tier: str = "free"

class LoginIn(BaseModel):
    handle: str
    password: str

@router.get("/health")
async def health(request: Request):
    return {"ok": True, "app": request.app.state.settings.app_name}

@router.get("/features")
async def features():
    return {"count": len(registry.FEATURES), "features": registry.all_features()}

@router.get("/features/{feature_id}")
async def feature(feature_id: str):
    if feature_id not in registry.BY_ID:
        raise HTTPException(404, "unknown feature")
    return registry.get(feature_id).to_dict()

@router.get("/plans")
async def plans():
    return tiers.plan_table()

@router.post("/auth/register", status_code=201)
async def register(body: RegisterIn, request: Request):
    if body.role not in security.ROLES:
        raise HTTPException(422, "invalid role")
    if body.tier not in ("free", "paid"):
        raise HTTPException(422, "invalid tier")
    db = request.app.state.db
    if await db.users.find_one({"handle": body.handle}):
        raise HTTPException(409, "handle taken")
    uid = uuid.uuid4().hex
    doc = {"_id": uid, "handle": body.handle, "password_hash": security.hash_password(body.password), "role": body.role, "tier": body.tier, "phone": body.phone}
    await db.users.insert_one(doc)
    token = security.make_token(request.app.state.settings.jwt_secret, uid, body.role, request.app.state.settings.token_ttl_minutes)
    return {"token": token, "user": safety.public_member(doc)}

@router.post("/auth/login")
async def login(body: LoginIn, request: Request):
    db = request.app.state.db
    user = await db.users.find_one({"handle": body.handle})
    if not user or not security.verify_password(user.get("password_hash"), body.password):
        raise HTTPException(401, "invalid credentials")
    token = security.make_token(request.app.state.settings.jwt_secret, user["_id"], user.get("role", "member"), request.app.state.settings.token_ttl_minutes)
    return {"token": token, "user": safety.public_member(user)}

@router.get("/auth/me")
async def me(user=Depends(get_current_user)):
    return safety.public_member(user)
