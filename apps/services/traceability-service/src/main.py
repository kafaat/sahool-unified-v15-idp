"""
Traceability Service - خدمة التتبع
Product traceability and supply chain tracking
"""

import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.middleware.tenant_context import TenantContextMiddleware

logger = structlog.get_logger()


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
            db_url += "?sslmode=require" if "?" not in db_url else "&sslmode=require"
    if db_url:
        try:
            import asyncpg

            app.state.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
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

    yield

    # Shutdown: Close connections
    logger.info("Shutting down traceability-service...")

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
app.add_middleware(TenantContextMiddleware)


# Include API routers
try:
    from src.api.v1 import batches

    app.include_router(batches.router)
    logger.info("API routers registered")
except ImportError as e:
    logger.error("Failed to import API routers", error=str(e))


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
        '# HELP traceability_service_info Service version info\n'
        '# TYPE traceability_service_info gauge\n'
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

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8123")))
