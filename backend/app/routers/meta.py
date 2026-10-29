"""Health, feature registry and plan table."""
from fastapi import APIRouter, HTTPException, Request

from .. import registry, tiers

router = APIRouter(prefix="/api", tags=["meta"])


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
