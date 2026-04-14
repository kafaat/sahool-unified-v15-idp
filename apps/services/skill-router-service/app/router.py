"""Routing endpoint — the public contract of skill-router-service."""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter
from prometheus_client import Counter

from app.loader import load_skills
from app.models import RouteRequest, RouteResponse, RouteResult
from app.scoring import filter_skills, score_skill

logger = logging.getLogger("skill-router")


def _sanitize(value: str, max_len: int = 200) -> str:
    """Defuse control characters in user input before it reaches log output.

    Prevents log-injection attacks (CodeQL py/log-injection) where a malicious
    payload could embed newlines to forge additional log lines.
    """
    if not isinstance(value, str):
        value = str(value)
    cleaned = value.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len] + "...[truncated]"
    return cleaned

# Low-confidence threshold: empirically, <3.0 means single-keyword hit only.
# Tune after collecting production data per ADR-010.
LOW_CONFIDENCE_THRESHOLD = 3.0

# Metrics that surface routing gaps (ADR-010 feedback loop).
ROUTE_NO_MATCH = Counter(
    "skill_router_no_match_total",
    "Routing queries that returned zero matching skills",
    ["tenant_id"],
)
ROUTE_LOW_CONFIDENCE = Counter(
    "skill_router_low_confidence_total",
    "Routing queries where top score < LOW_CONFIDENCE_THRESHOLD",
    ["tenant_id"],
)

router = APIRouter()

# Load once at startup. See ADR-010 — no hot reload in v0.
SKILLS = load_skills()
logger.info("skills_loaded", extra={"skill_count": len(SKILLS)})


@router.post("/api/v1/route", response_model=RouteResponse)
def route(req: RouteRequest) -> RouteResponse:
    t0 = time.perf_counter()
    safe_query = _sanitize(req.query)
    safe_tenant = _sanitize(req.tenant_id, max_len=64)
    logger.info(
        "routing_request",
        extra={"query": safe_query, "tenant_id": safe_tenant, "top_k": req.top_k},
    )

    candidates = filter_skills(SKILLS, req.tenant_id)
    logger.info(
        "tenant_filter_applied",
        extra={"tenant_id": safe_tenant, "candidate_count": len(candidates)},
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

    # Surface routing gaps for Iteration 2+ decisions.
    if not scored:
        ROUTE_NO_MATCH.labels(tenant_id=req.tenant_id).inc()
        logger.warning(
            "routing_gap",
            extra={
                "kind": "no_match",
                "query": safe_query,
                "tenant_id": safe_tenant,
            },
        )
    elif top and top[0][1] < LOW_CONFIDENCE_THRESHOLD:
        ROUTE_LOW_CONFIDENCE.labels(tenant_id=req.tenant_id).inc()
        logger.warning(
            "routing_gap",
            extra={
                "kind": "low_confidence",
                "query": safe_query,
                "tenant_id": safe_tenant,
                "top_skill": top[0][0],
                "top_score": round(top[0][1], 3),
                "threshold": LOW_CONFIDENCE_THRESHOLD,
            },
        )

    return RouteResponse(results=[RouteResult(skill=name, score=round(value, 3)) for name, value in top])


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
