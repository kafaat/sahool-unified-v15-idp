"""Pydantic models for the Skill Router API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Skill(BaseModel):
    """Registry entry loaded from .claude/skills/index.yaml."""

    model_config = ConfigDict(extra="ignore")

    name: str
    description: str = ""
    triggers: list[str] = Field(default_factory=list)
    tenant_id: str = "*"
    deprecated: bool = False
    external: bool = False


class RouteRequest(BaseModel):
    query: str = Field(..., min_length=1)
    tenant_id: str = "default"
    top_k: int = Field(3, ge=1, le=10)


class RouteResult(BaseModel):
    skill: str
    score: float


class RouteResponse(BaseModel):
    results: list[RouteResult]
