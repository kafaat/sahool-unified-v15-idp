"""
Traceability Service - خدمة التتبع
Product traceability and supply chain tracking
"""

import os
from contextlib import asynccontextmanager

import structlog
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from shared.middleware.tenant_context import TenantContextMiddleware

    TENANT_MIDDLEWARE_AVAILABLE = True
except ImportError:
    TENANT_MIDDLEWARE_AVAILABLE = False

try:
    from shared.auth.dependencies import enforce_tenant, get_current_user
    from shared.auth.models import User

    AUTH_AVAILABLE = True
except ImportError:  # pragma: no cover - defensive fallback for partial installs
    AUTH_AVAILABLE = False
    from fastapi import HTTPException, status

    class User:  # type: ignore[no-redef]
        tenant_id: str | None = None
        roles: list[str] = []

    async def get_current_user() -> User:  # type: ignore[no-redef]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication module unavailable",
        )

    def enforce_tenant(user, requested_tenant_id=None):  # type: ignore[no-redef]
        """Fallback enforce_tenant that mirrors shared.auth.enforce_tenant."""
        user_tenant = getattr(user, "tenant_id", None)
        if not user_tenant and not requested_tenant_id:
            raise HTTPException(status_code=400, detail="Tenant context is required but not available")
        if requested_tenant_id:
            roles = getattr(user, "roles", None) or []
            if "super_admin" in roles:
                return requested_tenant_id
            if user_tenant and user_tenant != requested_tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: tenant mismatch",
                )
            return requested_tenant_id
        return user_tenant


from shared.logging_config import setup_logging
from shared.observability.tracing import setup_tracing

setup_logging("traceability-service")
logger = structlog.get_logger()
_tracer = setup_tracing("traceability-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - معالج دورة حياة التطبيق"""
    # Startup: Initialize connections
    logger.info("Starting traceability-service...", version="16.0.0")

    # Database connection
    db_url = os.getenv("DATABASE_URL")
    # Enforce sslmode for non-development database connections
    if db_url and os.getenv("ENVIRONMENT", "development") != "development":
        if "sslmode" not in db_url:
            # Use sslmode=disable for PgBouncer (port 6432) which does not support SSL
            ssl_mode = "disable" if ":6432" in db_url else "require"
            db_url += f"?sslmode={ssl_mode}" if "?" not in db_url else f"&sslmode={ssl_mode}"
    if db_url:
        try:
            import asyncpg

            from shared.db.ssl import enforce_ssl_mode

            app.state.db_pool = await asyncpg.create_pool(
                enforce_ssl_mode(db_url),
                min_size=2,
                max_size=10,
                statement_cache_size=0,  # PgBouncer transaction mode compatibility
            )
            app.state.db_connected = True
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error("Failed to connect to database", error=str(e))
            app.state.db_connected = False
    else:
        app.state.db_connected = False
        logger.warning("DATABASE_URL not set, running without database")

    # NATS connection
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            import nats

            app.state.nc = await nats.connect(nats_url)
            app.state.nats_connected = True
            logger.info("NATS connection established", url=nats_url)
        except Exception as e:
            logger.error("Failed to connect to NATS", error=str(e))
            app.state.nats_connected = False
    else:
        app.state.nats_connected = False
        logger.warning("NATS_URL not set, running without NATS")

    # Start the field-event blockchain anchoring subscriber. Uses the
    # same NATS connection + db pool (if available) we just opened.
    app.state.field_event_subscriber = None
    if getattr(app.state, "nats_connected", False):
        try:
            from src.anchoring import FieldEventSubscriber

            app.state.field_event_subscriber = FieldEventSubscriber(
                nats_client=app.state.nc,
                db_pool=getattr(app.state, "db_pool", None),
            )
            await app.state.field_event_subscriber.start()
            logger.info("Field event anchoring subscriber started")
        except Exception as e:
            logger.error("Failed to start field event subscriber", error=str(e))

    yield

    # Shutdown: Close connections
    logger.info("Shutting down traceability-service...")

    # Stop the anchoring subscriber FIRST so no new messages arrive
    # while the NATS connection is being torn down.
    if getattr(app.state, "field_event_subscriber", None) is not None:
        try:
            await app.state.field_event_subscriber.stop()
            logger.info("Field event anchoring subscriber stopped")
        except Exception as e:
            logger.warning("Failed to stop anchoring subscriber", error=str(e))

    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
        logger.info("Database connection pool closed")

    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()
        logger.info("NATS connection closed")


app = FastAPI(
    title="Traceability Service",
    description="Product traceability and supply chain tracking - تتبع المنتجات وسلسلة التوريد",
    version="16.0.0",
    lifespan=lifespan,
)
_tracer.instrument_fastapi(app)

# Setup CORS
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

# Setup unified error handling
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    setup_exception_handlers(app)
    add_request_id_middleware(app)
    logger.info("Unified error handling configured")
except ImportError:
    logger.warning("shared.errors_py not available, using default error handling")

# Tenant context middleware
if TENANT_MIDDLEWARE_AVAILABLE:
    app.add_middleware(TenantContextMiddleware)


# Include API routers
try:
    from src.api.v1 import batches

    app.include_router(batches.router)
    logger.info("API routers registered")
except ImportError as e:
    logger.error("Failed to import API routers", error=str(e))


# ---------------------------------------------------------------------------
# Blockchain anchor inspection endpoints
# نقاط نهاية فحص سلسلة التتبع
# ---------------------------------------------------------------------------


@app.get("/api/v1/traceability/anchors/{tenant_id}/{field_id}")
async def list_anchors(
    tenant_id: str,
    field_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Return the in-memory chain of anchored events for a given
    (tenant, field). Useful for debugging and for the loan-
    verification / export-certificate flows that need to show
    the immutable activity log to auditors.

    Requires authentication. Non-super_admin users can only read their own
    tenant's chain (enforced via `shared.auth.enforce_tenant`).
    """
    validated_tenant = enforce_tenant(current_user, tenant_id)
    subscriber = getattr(app.state, "field_event_subscriber", None)
    if subscriber is None:
        return {
            "success": True,
            "data": {
                "tenant_id": validated_tenant,
                "field_id": field_id,
                "anchors": [],
                "length": 0,
                "subscriber_enabled": False,
            },
        }
    anchors = subscriber.get_chain(validated_tenant, field_id)
    return {
        "success": True,
        "data": {
            "tenant_id": validated_tenant,
            "field_id": field_id,
            "anchors": [a.to_dict() for a in anchors],
            "length": len(anchors),
            "subscriber_enabled": True,
        },
    }


@app.get("/api/v1/traceability/anchors/{tenant_id}/{field_id}/verify")
async def verify_anchors(
    tenant_id: str,
    field_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Re-compute every hash in the field's chain and confirm it
    matches. Returns ``valid: true`` only if the chain is untampered.

    Requires authentication and tenant match (or super_admin).
    """
    validated_tenant = enforce_tenant(current_user, tenant_id)
    subscriber = getattr(app.state, "field_event_subscriber", None)
    if subscriber is None:
        return {
            "success": True,
            "data": {
                "tenant_id": validated_tenant,
                "field_id": field_id,
                "valid": True,
                "subscriber_enabled": False,
            },
        }
    valid = subscriber.verify_chain(validated_tenant, field_id)
    anchors = subscriber.get_chain(validated_tenant, field_id)
    return {
        "success": True,
        "data": {
            "tenant_id": validated_tenant,
            "field_id": field_id,
            "valid": valid,
            "length": len(anchors),
            "head_hash": anchors[-1].hash if anchors else None,
            "subscriber_enabled": True,
        },
    }


@app.get("/api/v1/traceability/anchors/stats")
async def anchor_stats(current_user: User = Depends(get_current_user)):
    """Expose subscriber stats for Prometheus scrapers / ops. Requires authentication."""
    subscriber = getattr(app.state, "field_event_subscriber", None)
    if subscriber is None:
        return {
            "success": True,
            "data": {
                "subscriber_enabled": False,
                "messages_received": 0,
                "anchors_created": 0,
                "events_ignored": 0,
                "errors": 0,
            },
        }
    return {
        "success": True,
        "data": {"subscriber_enabled": True, **subscriber.stats},
    }


@app.get("/healthz")
def health():
    """Liveness probe - فحص الحياة"""
    return {"status": "ok", "service": "traceability-service", "version": "16.0.0"}


@app.get("/readyz")
def readiness():
    """Readiness probe - فحص الجاهزية"""
    return {
        "status": "ok",
        "database": getattr(app.state, "db_connected", False),
        "nats": getattr(app.state, "nats_connected", False),
    }


@app.get("/health")
def comprehensive_health():
    """Comprehensive health check - فحص صحي شامل"""
    db_status = getattr(app.state, "db_connected", False)
    nats_status = getattr(app.state, "nats_connected", False)
    overall_status = "ok" if (db_status and nats_status) else "degraded"

    return {
        "status": overall_status,
        "service": "traceability-service",
        "version": "16.0.0",
        "checks": {
            "database": "connected" if db_status else "disconnected",
            "nats": "connected" if nats_status else "disconnected",
        },
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from fastapi.responses import PlainTextResponse

    db_up = 1 if getattr(app.state, "db_connected", False) else 0
    nats_up = 1 if getattr(app.state, "nats_connected", False) else 0
    metrics_text = (
        "# HELP traceability_service_up Service is up\n"
        "# TYPE traceability_service_up gauge\n"
        "traceability_service_up 1\n"
        "# HELP traceability_service_info Service version info\n"
        "# TYPE traceability_service_info gauge\n"
        'traceability_service_info{service="traceability-service",version="16.0.0"} 1\n'
        "# HELP traceability_service_db_up Database connection status\n"
        "# TYPE traceability_service_db_up gauge\n"
        f"traceability_service_db_up {db_up}\n"
        "# HELP traceability_service_nats_up NATS connection status\n"
        "# TYPE traceability_service_nats_up gauge\n"
        f"traceability_service_nats_up {nats_up}\n"
    )
    return PlainTextResponse(content=metrics_text, media_type="text/plain; version=0.0.4")


@app.get("/")
def root():
    """Root endpoint - نقطة نهاية الجذر"""
    return {
        "service": "traceability-service",
        "version": "16.0.0",
        "description": "Product traceability and supply chain tracking - تتبع المنتجات وسلسلة التوريد",
        "documentation": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "8123")))  # nosec B104
