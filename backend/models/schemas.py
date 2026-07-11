"""Pydantic request/response schemas."""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ── Prediction ────────────────────────────────────────
class PlayerInput(BaseModel):
    name: str
    batting_pos: int = Field(ge=1, le=11)
    role: Optional[str] = "BAT"   # BAT / WK / ALLR / BOWL


class PredictRequest(BaseModel):
    venue: str
    opponent: str
    season: int = 2025
    is_home: bool = True
    lineup: List[PlayerInput]


class Playing11Request(BaseModel):
    venue: str
    opponent: str
    season: int = 2025
    is_home: bool = True
    squad: List[PlayerInput]
