"""
carbon-service — Agricultural carbon footprint (IPCC Tier 1)
خدمة البصمة الكربونية الزراعية — IPCC المستوى الأول

Port: 8195
Purpose: compute per-operation CO2e from fuel / fertiliser / machinery /
         sequestration inputs, aggregate into per-field and per-season
         totals, and expose dashboards to the advisory + web layers.

Architecture: stateless FastAPI; all state lives in the shared
field-management-service PostgreSQL DB (the tables the Phase-1 migration
added carbon columns to). This service is horizontally scalable and can
be killed / restarted without losing any state.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.logging_config import setup_logging
from shared.observability.tracing import setup_tracing

setup_logging("carbon-service")
logger = structlog.get_logger()
_tracer = setup_tracing("carbon-service")

PORT = int(os.getenv("PORT", "8195"))
SERVICE_NAME = "carbon-service"
SERVICE_VERSION = "16.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: DB pool + NATS. Shutdown: close both."""
    logger.info(f"Starting {SERVICE_NAME}...", version=SERVICE_VERSION)

    # ── Database ──────────────────────────────────────────────────────
    db_url = os.getenv("DATABASE_URL")
    if db_url and os.getenv("ENVIRONMENT", "development") != "development":
        if "sslmode" not in db_url:
            ssl_mode = "disable" if ":6432" in db_url else "require"
            sep = "&" if "?" in db_url else "?"
            db_url = f"{db_url}{sep}sslmode={ssl_mode}"
    app.state.db_pool = None
    app.state.db_connected = False
    if db_url:
        try:
            import asyncpg

            app.state.db_pool = await asyncpg.create_pool(
                db_url,
                min_size=2,
                max_size=10,
                statement_cache_size=0,
            )
            app.state.db_connected = True
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error("Failed to connect to database", error=str(e))

    # ── NATS (optional) ───────────────────────────────────────────────
    nats_url = os.getenv("NATS_URL")
    app.state.nc = None
    app.state.nats_connected = False
    if nats_url:
        try:
            import nats

            app.state.nc = await nats.connect(nats_url)
            app.state.nats_connected = True
            logger.info("NATS connection established", url=nats_url)

            # Start the subscriber that listens for new field operations
            # and auto-computes their carbon footprint.
            try:
                from src.events.operation_subscriber import (
                    start_operation_subscriber,
                )

                app.state.subscriber_task = await start_operation_subscriber(app.state.nc, app.state.db_pool)
                logger.info("Operation subscriber started")
            except Exception as sub_err:
                logger.warning(
                    "Failed to start operation subscriber",
                    error=str(sub_err),
                )
        except Exception as e:
            logger.error("Failed to connect to NATS", error=str(e))

    yield

    # ── Shutdown ──────────────────────────────────────────────────────
    logger.info(f"Shutting down {SERVICE_NAME}...")
    if hasattr(app.state, "subscriber_task") and app.state.subscriber_task:
        try:
            await app.state.subscriber_task.drain()
        except Exception as drain_err:
            # Draining a NATS subscription on shutdown is best-effort.
            # Any failure here (NATS already closed, connection reset,
            # etc.) is non-actionable — we log it for observability but
            # must not raise, otherwise the lifespan shutdown hangs and
            # Kubernetes kills the pod with a sigkill instead of a clean
            # sigterm. Downstream consumers dedupe on event_id anyway.
            logger.warning(
                "Failed to drain subscriber on shutdown",
                error=str(drain_err),
            )
    if app.state.db_pool:
        await app.state.db_pool.close()
    if app.state.nc:
        await app.state.nc.close()


app = FastAPI(
    title=SERVICE_NAME,
    description=("Agricultural carbon footprint (IPCC Tier 1) — خدمة البصمة الكربونية الزراعية"),
    version=SERVICE_VERSION,
    lifespan=lifespan,
)
_tracer.instrument_fastapi(app)

# ── CORS ──────────────────────────────────────────────────────────────
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "https://sahool.app,https://admin.sahool.app,http://localhost:3000,http://localhost:3001,http://localhost:3002",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "X-Tenant-Id",
        "X-Request-ID",
        "Idempotency-Key",
    ],
)

# ── Unified error handling (best-effort) ─────────────────────────────
try:
    from shared.errors_py import (  # type: ignore
        add_request_id_middleware,
        setup_exception_handlers,
    )

    setup_exception_handlers(app)
    add_request_id_middleware(app)
    logger.info("Unified error handling configured")
except ImportError:
    logger.warning("shared.errors_py not available, using defaults")

# ── Routers ───────────────────────────────────────────────────────────
try:
    from src.api.v1 import carbon

    app.include_router(carbon.router)
    logger.info("Carbon router registered")
except ImportError as e:
    logger.error("Failed to import carbon router", error=str(e))


# ── Health endpoints (platform-standard) ─────────────────────────────
@app.get("/healthz")
def healthz() -> dict:
    """Liveness probe."""
    return {"status": "ok", "service": SERVICE_NAME, "version": SERVICE_VERSION}


@app.get("/readyz")
def readyz() -> dict:
    """Readiness probe — reports DB + NATS connection state."""
    return {
        "status": "ok",
        "database": getattr(app.state, "db_connected", False),
        "nats": getattr(app.state, "nats_connected", False),
    }


@app.get("/health")
def health() -> dict:
    """Comprehensive health check."""
    db_ok = getattr(app.state, "db_connected", False)
    nats_ok = getattr(app.state, "nats_connected", False)
    overall = "ok" if db_ok else "degraded"
    return {
        "status": overall,
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "checks": {
            "database": "connected" if db_ok else "disconnected",
            "nats": "connected" if nats_ok else "disconnected",
        },
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics."""
    from fastapi.responses import PlainTextResponse

    db_up = 1 if getattr(app.state, "db_connected", False) else 0
    nats_up = 1 if getattr(app.state, "nats_connected", False) else 0
    text = (
        "# HELP carbon_service_up Service is up\n"
        "# TYPE carbon_service_up gauge\n"
        "carbon_service_up 1\n"
        "# HELP carbon_service_info Service version info\n"
        "# TYPE carbon_service_info gauge\n"
        f'carbon_service_info{{service="{SERVICE_NAME}",version="{SERVICE_VERSION}"}} 1\n'
        "# HELP carbon_service_db_up Database connection status\n"
        "# TYPE carbon_service_db_up gauge\n"
        f"carbon_service_db_up {db_up}\n"
        "# HELP carbon_service_nats_up NATS connection status\n"
        "# TYPE carbon_service_nats_up gauge\n"
        f"carbon_service_nats_up {nats_up}\n"
    )
    return PlainTextResponse(text)
