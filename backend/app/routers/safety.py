"""Group: safety. Crisis button is WORKING (free, no login, never lockable). Others are stubs."""
import json
from pathlib import Path

from fastapi import Request

from .. import safety
from ._stub import stub_router

router = stub_router("safety")
DATA = Path(__file__).resolve().parent.parent / "data"


@router.get("/crisis", name="safety:crisis")
async def crisis(request: Request):
    return safety.crisis_payload(request.app.state.settings.app_name)


@router.get("/relapse_protocol/content", name="safety:relapse_content")
async def relapse_content():
    # Placeholder until Brann's wording + clinical review land; always carries 988/911.
    return json.loads((DATA / "relapse_protocol.json").read_text())
