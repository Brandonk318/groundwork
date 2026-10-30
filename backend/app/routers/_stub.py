"""Builds a stub router for one feature group: each feature answers 501 with its registry entry
until its module is built. Replace a stub by adding a real route in the group's file."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .. import registry


def stub_router(group: str, exclude: set[str] | None = None) -> APIRouter:
    exclude = exclude or set()
    router = APIRouter(prefix=f"/api/{group}", tags=[group])
    for f in registry.FEATURES:
        if f.group != group or f.id in exclude:
            continue

        def make(feature=f):
            async def stub():
                return JSONResponse(status_code=501, content={"status": "stub", "feature": feature.to_dict()})
            stub.__name__ = f"stub_{feature.id}"
            return stub

        router.add_api_route(f"/{f.id}", make(), methods=["GET"], name=f"{group}:{f.id}")
    return router
