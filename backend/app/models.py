"""Pydantic model placeholders. Fill in per module as each one is built."""
from datetime import date, datetime

from pydantic import BaseModel, Field


class MoodCheckin(BaseModel):
    mood: str = Field(max_length=32)
    note: str | None = Field(default=None, max_length=500)


class Post(BaseModel):
    body: str = Field(max_length=5000)
    anonymous: bool = False
    group: str | None = None


class CourtDate(BaseModel):
    on: datetime
    court: str
    notes: str | None = None


class LockRequest(BaseModel):
    target: str
    kind: str  # week | two_weeks | month | permanent


class PortfolioItem(BaseModel):
    journey: str  # sobriety | release | business | custody | credit | trade | other
    title: str
    happened_on: date | None = None
    visibility: str = "private"  # PRIVATE by default


class FamilyVisibility(BaseModel):
    milestones: bool = False
    appointments: bool = False
