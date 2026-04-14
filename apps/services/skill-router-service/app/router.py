"""Routing endpoint — the public contract of skill-router-service."""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter

from app.loader import load_skills
from app.models import RouteRequest, RouteResponse, RouteResult
from app.scoring import filter_skills, score_skill

logger = logging.getLogger("skill-router")

router = APIRouter()

# Load once at startup. See ADR-010 — no hot reload in v0.
SKILLS = load_skills()
logger.info("skills_loaded", extra={"skill_count": len(SKILLS)})


@router.post("/api/v1/route", response_model=RouteResponse)
def route(req: RouteRequest) -> RouteResponse:
    t0 = time.perf_counter()
    logger.info(
        "routing_request",
        extra={"query": req.query, "tenant_id": req.tenant_id, "top_k": req.top_k},
    )

    candidates = filter_skills(SKILLS, req.tenant_id)
    logger.info(
        "tenant_filter_applied",
        extra={"tenant_id": req.tenant_id, "candidate_count": len(candidates)},
    )

    scored: list[tuple[str, float]] = []
    for s in candidates:
        value = score_skill(req.query, s)
        if value > 0:
            scored.append((s.name, value))

    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[: req.top_k]

    latency_ms = (time.perf_counter() - t0) * 1000
    logger.info(
        "routing_result",
        extra={
            "match_count": len(scored),
            "top": [{"skill": n, "score": round(v, 3)} for n, v in top],
            "latency_ms": round(latency_ms, 2),
        },
    )

    return RouteResponse(
        results=[RouteResult(skill=name, score=round(value, 3)) for name, value in top]
    )


@router.get("/api/v1/skills")
def list_skills() -> dict:
    """List all registered skills (debug / observability)."""
    return {
        "count": len(SKILLS),
        "skills": [
            {
                "name": s.name,
                "tenant_id": s.tenant_id,
                "deprecated": s.deprecated,
                "external": s.external,
                "trigger_count": len(s.triggers),
            }
            for s in SKILLS
        ],
    }
