"""skill-router-service — ADR-010 Phase 1 entrypoint.

Routes user queries to the most relevant registered skills.
Binds the LLM + MCP + Skills layers with deterministic skill selection.

Port: 8205
Endpoints:
  POST /api/v1/route    — rank skills for a query
  GET  /api/v1/skills   — list all registered skills
  GET  /healthz         — liveness
  GET  /readyz          — readiness (fails loudly on YAML errors)
  GET  /metrics         — Prometheus metrics
"""

from __future__ import annotations

import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, generate_latest

from app.config import settings
from app.loader import load_skills
from app.router import SKILLS, router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("skill-router")

app = FastAPI(
    title="SAHOOL Skill Router",
    version=settings.SERVICE_VERSION,
)

REQUEST_COUNT = Counter(
    "skill_router_requests_total",
    "Total routing requests received by skill-router-service",
    ["path", "status"],
)

REQUEST_LATENCY = Histogram(
    "skill_router_latency_seconds",
    "Routing latency in seconds",
    ["path"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    REQUEST_COUNT.labels(path=request.url.path, status=response.status_code).inc()
    REQUEST_LATENCY.labels(path=request.url.path).observe(elapsed)
    return response


@app.get("/healthz")
def healthz() -> dict:
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
    }


@app.get("/readyz")
def readyz() -> dict:
    """Readiness probe — fails loudly if the registry YAML is broken."""
    try:
        skills = load_skills()
        return {
            "status": "ready" if skills else "degraded",
            "skills_loaded": len(skills),
            "skills_index_path": settings.SKILLS_INDEX_PATH,
        }
    except Exception as exc:
        logger.exception("readyz_failed")
        return {
            "status": "error",
            "error": str(exc),
            "skills_index_path": settings.SKILLS_INDEX_PATH,
        }


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type="text/plain")


app.include_router(router)

logger.info(
    "service_started",
    extra={
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "port": settings.PORT,
        "skill_count": len(SKILLS),
    },
)
