# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""agri-taxonomy-service — FastAPI entry point.

Phase 3.5 scaffold per ADR-012. Boots cleanly, exposes health / metrics,
and registers the v1 router. Domain handlers raise 501 until Phase 4.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .api.v1.taxonomy import router as taxonomy_router

SERVICE_NAME = os.getenv("SERVICE_NAME", "agri-taxonomy-service")
SERVICE_LAYER = os.getenv("SERVICE_LAYER", "intelligence")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "0.1.0")

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info(
        "service.startup",
        service=SERVICE_NAME,
        layer=SERVICE_LAYER,
        version=SERVICE_VERSION,
    )
    # Phase 4: connect to knowledge-graph (8140), NATS, load latest taxonomy snapshot.
    yield
    log.info("service.shutdown", service=SERVICE_NAME)


app = FastAPI(
    title=SERVICE_NAME,
    version=SERVICE_VERSION,
    lifespan=lifespan,
)

app.include_router(taxonomy_router, prefix="/api/v1/taxonomy", tags=["taxonomy"])


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness probe."""

    return {"status": "ok", "service": SERVICE_NAME, "version": SERVICE_VERSION}


@app.get("/readyz")
def readyz() -> dict[str, object]:
    """Readiness probe.

    Phase 4: replace the placeholder values with real checks against
    ``knowledge-graph`` (8140) and NATS.
    """

    return {
        "status": "ready",
        "service": SERVICE_NAME,
        "checks": {
            "knowledge_graph": True,  # placeholder (Phase 4)
            "nats": True,  # placeholder (Phase 4)
        },
    }


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": SERVICE_NAME,
        "layer": SERVICE_LAYER,
        "version": SERVICE_VERSION,
        "adr": "ADR-012",
    }
