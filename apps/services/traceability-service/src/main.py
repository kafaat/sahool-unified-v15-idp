"""
Traceability Service - خدمة التتبع
Product traceability and supply chain tracking
"""

import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - معالج دورة حياة التطبيق"""
    # Startup: Initialize connections
    logger.info("Starting traceability-service...", version="16.0.0")

    # Database connection
    db_url = os.getenv("DATABASE_URL")
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
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Configure via CORS_ORIGINS env var
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup unified error handling
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    setup_exception_handlers(app)
    add_request_id_middleware(app)
    logger.info("Unified error handling configured")
except ImportError:
    logger.warning("shared.errors_py not available, using default error handling")


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
    return {
        "service": "traceability-service",
        "version": "16.0.0",
        "note": "Prometheus metrics integration pending",
    }


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
