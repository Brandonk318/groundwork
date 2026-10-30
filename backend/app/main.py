from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import Settings, load_settings
from .routers import (community, family, journey, learning, matching, meta, platform, reentry, safety,
                      support, venue, wellbeing, work)

ROUTERS = (meta, safety, reentry, work, support, community, journey, wellbeing, learning, matching, venue,
           family, platform)


def create_app(settings: Settings | None = None, db=None) -> FastAPI:
    settings = settings or load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if app.state.db is None:
            from motor.motor_asyncio import AsyncIOMotorClient

            app.state.db = AsyncIOMotorClient(settings.mongo_url, tz_aware=True)[settings.db_name]
        yield

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.settings = settings
    app.state.db = db
    for module in ROUTERS:
        app.include_router(module.router)
    app.include_router(journey.public_router)
    return app
