"""Agent Schema 定义"""
from pydantic import BaseModel, Field
from typing import Literal


class PlanRequest(BaseModel):
    city: str
    days: int = Field(default=3, ge=1, le=7)
    style: list[str] = []
    budget: Literal["low", "medium", "high"] = "medium"
    companions: str = "独自"
    force_refresh: bool = False
    user_id: str | None = None


class AskRequest(BaseModel):
    session_id: str | None = None
    question: str = Field(min_length=1, max_length=500)
    user_id: str | None = None
