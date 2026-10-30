"""Venue: placeholder grey-box preview (paid teaser for free)."""
from fastapi import APIRouter, Depends, Request
from .. import tiers
from ..deps import get_current_user
from ..seed_data import VENUE_STOPS
from ._stub import stub_router

router = stub_router("venue", exclude={"virtual_venue"})

@router.get("/virtual_venue")
async def venue(request: Request):
    return {"venue": {"name": "Virtual venue preview (placeholder)", "placeholder": True, "label": "Placeholder — grey-box room. Real venue photos have not been provided; this is not the real space.", "stops": VENUE_STOPS, "zero_proof": True, "alcohol_free": True}}

@router.get("/virtual_venue/preview")
async def preview(user=Depends(get_current_user)):
    paid = tiers.has_access(user.get("tier", "free"), "virtual_venue")
    return {"access": "full_placeholder" if paid else "teaser", "placeholder": True, "label": "Placeholder — grey-box room. Real venue photos have not been provided.", "stops": VENUE_STOPS if paid else VENUE_STOPS[:1]}
