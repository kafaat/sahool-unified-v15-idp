# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""agri-taxonomy-service — FastAPI entry point.

Phase 4 implementation per ADR-012. Boots a seeded in-memory taxonomy
store, exposes the v1 routes (``/version``, ``/nodes``, ``/search``,
``/fertilizers/.../forbidden``, ``/releases``), publishes release
events on NATS ``sahool.taxonomy.released.v{major}``, and serves the
standard ``/healthz`` / ``/readyz`` / ``/metrics`` endpoints.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .api.v1.taxonomy import router as taxonomy_router
from .nats_publisher import build_release_publisher
from .store import make_default_seed_store

SERVICE_NAME = os.getenv("SERVICE_NAME", "agri-taxonomy-service")
SERVICE_LAYER = os.getenv("SERVICE_LAYER", "intelligence")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "0.1.0")
NATS_URL = os.getenv("NATS_URL", "")

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info(
        "service.startup",
        service=SERVICE_NAME,
        layer=SERVICE_LAYER,
        version=SERVICE_VERSION,
        nats_configured=bool(NATS_URL),
    )
    publisher = build_release_publisher(NATS_URL or None)
    store = make_default_seed_store(publisher=publisher)
    # Cut the initial "seeded" release so reads return non-empty data.
    await store.publish_release(bump="minor")
    app.state.taxonomy_store = store
    app.state.release_publisher = publisher
    try:
        yield
    finally:
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
    """Readiness probe — reports whether the in-memory store is initialised."""

    store = getattr(app.state, "taxonomy_store", None)
    return {
        "status": "ready" if store is not None else "starting",
        "service": SERVICE_NAME,
        "checks": {
            "taxonomy_store": store is not None,
            "nats": bool(NATS_URL),
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
