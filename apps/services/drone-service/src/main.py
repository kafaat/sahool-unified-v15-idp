"""
drone-service - Drone integration and management - تكامل وإدارة الطائرات المسيرة
"""

import os
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

try:
    from shared.middleware.tenant_context import TenantContextMiddleware

    TENANT_MIDDLEWARE_AVAILABLE = True
except ImportError:
    TENANT_MIDDLEWARE_AVAILABLE = False

try:
    from shared.middleware.security_headers import setup_security_headers

    SECURITY_HEADERS_AVAILABLE = True
except ImportError:
    SECURITY_HEADERS_AVAILABLE = False

from shared.logging_config import setup_logging
from shared.observability.tracing import setup_tracing

setup_logging("drone-service")
logger = structlog.get_logger()
_tracer = setup_tracing("drone-service")

# ─────────────────────────────────────────────────────────────────────────────
# Prometheus metrics counters (simple in-process)
# ─────────────────────────────────────────────────────────────────────────────
_metrics = {
    "requests_total": 0,
    "requests_errors": 0,
    "request_duration_sum": 0.0,
    "request_duration_count": 0,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - معالج دورة حياة التطبيق"""
    logger.info("Starting drone-service...", version="16.0.0")

    # Database connection
    app.state.db_connected = False
    db_url = os.getenv("DATABASE_URL")
    if db_url and os.getenv("ENVIRONMENT", "development") != "development":
        if "sslmode" not in db_url:
            # Use sslmode=disable for PgBouncer (port 6432) which does not support SSL
            ssl_mode = "disable" if ":6432" in db_url else "require"
            db_url += f"?sslmode={ssl_mode}" if "?" not in db_url else f"&sslmode={ssl_mode}"
    if db_url:
        try:
            import asyncpg

            app.state.db_pool = await asyncpg.create_pool(
                db_url,
                min_size=2,
                max_size=10,
                statement_cache_size=0,  # PgBouncer transaction mode compatibility
            )
            app.state.db_connected = True
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error("Failed to connect to database", error=str(e))
            app.state.db_pool = None
    else:
        app.state.db_pool = None
        logger.warning("DATABASE_URL not set, running without database")

    # NATS connection & publisher
    app.state.nats_connected = False
    app.state.publisher = None
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            from src.events import DronePublisher, subscribe_cross_service_events

            publisher = DronePublisher(nats_url)
            await publisher.connect()
            app.state.nc = publisher.nc
            app.state.publisher = publisher
            app.state.nats_connected = True
            logger.info("NATS connection established", url=nats_url)

            # Subscribe to cross-service events
            try:
                app.state.pending_detections = []
                await subscribe_cross_service_events(app.state.nc, app.state)
            except Exception as e:
                logger.warning("Cross-service event subscription failed", error=str(e))

        except Exception as e:
            logger.error("Failed to connect to NATS", error=str(e))
            app.state.nc = None
    else:
        app.state.nc = None
        logger.warning("NATS_URL not set, running without NATS")

    yield

    # Shutdown
    logger.info("Shutting down drone-service...")

    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
        logger.info("Database connection pool closed")

    if getattr(app.state, "publisher", None):
        await app.state.publisher.close()
        logger.info("Drone publisher closed")
    elif hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()
        logger.info("NATS connection closed")


app = FastAPI(
    title="drone-service",
    description="Drone integration and management - تكامل وإدارة الطائرات المسيرة",
    version="16.0.0",
    lifespan=lifespan,
)
_tracer.instrument_fastapi(app)

# CORS
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "https://sahool.app,https://admin.sahool.app,http://localhost:3000",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Tenant-Id", "X-Request-ID"],
)

# Unified error handling
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    setup_exception_handlers(app)
    add_request_id_middleware(app)
except ImportError:
    pass  # shared.errors_py is optional; service works without unified error handling

if SECURITY_HEADERS_AVAILABLE:
    setup_security_headers(app)

if TENANT_MIDDLEWARE_AVAILABLE:
    app.add_middleware(TenantContextMiddleware)


# Metrics middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next) -> Response:
    """Collect request metrics for Prometheus."""
    if request.url.path in ("/metrics", "/healthz", "/readyz"):
        return await call_next(request)

    start = time.time()
    _metrics["requests_total"] += 1

    try:
        response = await call_next(request)
        if response.status_code >= 400:
            _metrics["requests_errors"] += 1
        return response
    except Exception:
        _metrics["requests_errors"] += 1
        raise
    finally:
        duration = time.time() - start
        _metrics["request_duration_sum"] += duration
        _metrics["request_duration_count"] += 1


# Include API routers
try:
    from src.api.v1 import drones, flights, missions, vra

    app.include_router(drones.router)
    app.include_router(flights.router)
    app.include_router(missions.router)
    app.include_router(vra.router)
    logger.info("API routers registered")
except ImportError as e:
    logger.error("Failed to import API routers", error=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Health & Metrics Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/healthz")
def health():
    """Liveness probe - فحص الحياة"""
    return {"status": "ok", "service": "drone-service", "version": "16.0.0"}


@app.get("/readyz")
def readiness():
    """Readiness probe - فحص الجاهزية.

    In production/staging, ALL critical dependencies must be up for the
    service to accept traffic. Dev only requires at least one so local
    runs without real infra still succeed.
    """
    from fastapi.responses import JSONResponse

    env = os.getenv("ENVIRONMENT", "development").lower()
    db_ok = getattr(app.state, "db_connected", False)
    nats_ok = getattr(app.state, "nats_connected", False)

    checks = {
        "database": "connected" if db_ok else "disconnected",
        "nats": "connected" if nats_ok else "disconnected",
    }

    if env in ("production", "prod", "staging"):
        is_ready = db_ok and nats_ok
    else:
        is_ready = db_ok or nats_ok

    if not is_ready:
        return JSONResponse(
            content={"status": "not_ready", "service": "drone-service", "version": "16.0.0", "checks": checks},
            status_code=503,
        )

    return {"status": "ready", "service": "drone-service", "version": "16.0.0", "checks": checks}


@app.get("/health")
def comprehensive_health():
    """Comprehensive health check - فحص صحي شامل"""
    db_status = getattr(app.state, "db_connected", False)
    nats_status = getattr(app.state, "nats_connected", False)
    overall = "ok" if db_status or nats_status else "degraded"

    return {
        "status": overall,
        "service": "drone-service",
        "version": "16.0.0",
        "checks": {
            "database": "connected" if db_status else "disconnected",
            "nats": "connected" if nats_status else "disconnected",
        },
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    db_up = 1 if getattr(app.state, "db_connected", False) else 0
    nats_up = 1 if getattr(app.state, "nats_connected", False) else 0
    avg_dur = (
        _metrics["request_duration_sum"] / _metrics["request_duration_count"]
        if _metrics["request_duration_count"] > 0
        else 0
    )

    lines = [
        "# HELP drone_service_info Service version info",
        "# TYPE drone_service_info gauge",
        'drone_service_info{service="drone-service",version="16.0.0"} 1',
        "# HELP drone_service_up Service is up",
        "# TYPE drone_service_up gauge",
        "drone_service_up 1",
        "# HELP drone_service_db_up Database connection status",
        "# TYPE drone_service_db_up gauge",
        f"drone_service_db_up {db_up}",
        "# HELP drone_service_nats_up NATS connection status",
        "# TYPE drone_service_nats_up gauge",
        f"drone_service_nats_up {nats_up}",
        "# HELP drone_service_requests_total Total HTTP requests",
        "# TYPE drone_service_requests_total counter",
        f"drone_service_requests_total {_metrics['requests_total']}",
        "# HELP drone_service_requests_errors_total Total HTTP errors",
        "# TYPE drone_service_requests_errors_total counter",
        f"drone_service_requests_errors_total {_metrics['requests_errors']}",
        "# HELP drone_service_request_duration_seconds_avg Average request duration",
        "# TYPE drone_service_request_duration_seconds_avg gauge",
        f"drone_service_request_duration_seconds_avg {avg_dur:.6f}",
    ]

    return PlainTextResponse(content="\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")


@app.get("/")
def root():
    """Root endpoint - نقطة نهاية الجذر"""
    return {
        "service": "drone-service",
        "version": "16.0.0",
        "description": "Drone integration and management - تكامل وإدارة الطائرات المسيرة",
        "documentation": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8126")))  # nosec B104 - binding to all interfaces required for Docker container
