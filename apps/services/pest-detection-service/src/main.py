"""
SAHOOL Pest Detection Service
خدمة كشف الآفات والأمراض

AI-powered pest detection service with Middle East pest database
and IPM (Integrated Pest Management) recommendations.
"""

import os
from contextlib import asynccontextmanager

import httpx
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.middleware.tenant_context import TenantContextMiddleware
from src.api.v1 import pests, scouts, thresholds, treatments

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger(__name__)

# Service configuration
SERVICE_NAME = "pest-detection-service"
SERVICE_VERSION = "16.0.0"
SERVICE_NAME_AR = "خدمة كشف الآفات"

# ═══════════════════════════════════════════════════════════════════════════════
# Feature Schema Definition (v1.0)
# تعريف مخطط المدخلات للكشف عن انحراف البيانات
# ═══════════════════════════════════════════════════════════════════════════════

FEATURE_SCHEMA = {
    "version": "1.0.0",
    "service": SERVICE_NAME,
    "features": {
        "image": {"type": "binary", "formats": ["jpeg", "png", "webp"], "max_size_mb": 50},
        "temperature_c": {"type": "float", "min": -10, "max": 60, "unit": "°C"},
        "humidity_pct": {"type": "float", "min": 0, "max": 100, "unit": "%"},
        "ndvi": {"type": "float", "min": -1.0, "max": 1.0, "unit": "index", "optional": True},
        "crop_type": {
            "type": "enum",
            "values": [
                "wheat",
                "sorghum",
                "tomato",
                "date_palm",
                "coffee",
                "mango",
                "citrus",
                "grape",
                "cotton",
                "sesame",
                "alfalfa",
            ],
        },
        "season": {"type": "enum", "values": ["spring", "summer", "fall", "winter"]},
        "latitude": {"type": "float", "min": -90, "max": 90, "unit": "degrees"},
        "longitude": {"type": "float", "min": -180, "max": 180, "unit": "degrees"},
        "confidence_threshold": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.25},
    },
    "quality_requirements": {
        "min_image_resolution_px": 320,
        "max_detection_latency_ms": 5000,
    },
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info(
        "service_starting",
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
    )

    # Initialize HTTP client for vision service
    vision_url = os.getenv("VISION_SERVICE_URL", "http://yolo26-vision-service:8150")
    app.state.vision_client = httpx.AsyncClient(
        base_url=vision_url,
        timeout=30.0,
    )

    # Initialize NATS connection (optional)
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            import nats

            app.state.nc = await nats.connect(nats_url)
            logger.info("nats_connected", url=nats_url)
        except Exception as e:
            logger.warning("nats_connection_failed", error=str(e))
            app.state.nc = None
    else:
        app.state.nc = None

    # Initialize Redis connection (optional)
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            import redis.asyncio as redis

            app.state.redis = redis.from_url(redis_url)
            logger.info("redis_connected", url=redis_url)
        except Exception as e:
            logger.warning("redis_connection_failed", error=str(e))
            app.state.redis = None
    else:
        app.state.redis = None

    logger.info("service_started", service=SERVICE_NAME)

    yield

    # Cleanup
    logger.info("service_stopping", service=SERVICE_NAME)

    if app.state.vision_client:
        await app.state.vision_client.aclose()

    if app.state.nc:
        await app.state.nc.close()

    if app.state.redis:
        await app.state.redis.close()

    logger.info("service_stopped", service=SERVICE_NAME)


# Create FastAPI app
app = FastAPI(
    title="SAHOOL Pest Detection Service",
    description="AI-powered pest detection with Middle East pest database | خدمة كشف الآفات بالذكاء الاصطناعي",
    version=SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup unified error handling
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    setup_exception_handlers(app)
    add_request_id_middleware(app)
except ImportError:
    pass

# CORS middleware
ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "https://sahool.io,https://admin.sahool.io,http://localhost:3000",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Tenant-Id", "X-Request-ID"],
)

# Tenant context middleware
app.add_middleware(TenantContextMiddleware)


@app.get("/v1/feature-schema", tags=["Schema"])
async def get_feature_schema():
    """Return the ML feature schema for data drift monitoring."""
    return FEATURE_SCHEMA


# Health endpoints
@app.get("/healthz", tags=["Health"])
async def liveness():
    """Kubernetes liveness probe."""
    return {"status": "ok"}


@app.get("/readyz", tags=["Health"])
async def readiness(request: Request):
    """Kubernetes readiness probe."""
    checks = {
        "vision_service": False,
        "nats": False,
        "redis": False,
    }

    # Check vision service
    try:
        if request.app.state.vision_client:
            response = await request.app.state.vision_client.get("/healthz")
            checks["vision_service"] = response.status_code == 200
    except Exception as e:
        logger.warning("vision_service_health_check_failed", error=str(e))

    # Check NATS
    if request.app.state.nc and request.app.state.nc.is_connected:
        checks["nats"] = True

    # Check Redis
    try:
        if request.app.state.redis:
            await request.app.state.redis.ping()
            checks["redis"] = True
    except Exception as e:
        logger.warning("redis_health_check_failed", error=str(e))

    all_ready = checks["vision_service"]  # Vision service is required
    status = "ok" if all_ready else "degraded"

    return {
        "status": status,
        "checks": checks,
    }


@app.get("/health", tags=["Health"])
async def health(request: Request):
    """Comprehensive health check."""
    readiness_result = await readiness(request)
    return {
        "service": SERVICE_NAME,
        "service_ar": SERVICE_NAME_AR,
        "version": SERVICE_VERSION,
        **readiness_result,
    }


@app.get("/metrics", tags=["Health"])
async def metrics():
    """Prometheus metrics endpoint."""
    from fastapi.responses import PlainTextResponse

    metrics_text = (
        "# HELP pest_detection_up Service is up\n"
        "# TYPE pest_detection_up gauge\n"
        "pest_detection_up 1\n"
        f"# HELP pest_detection_info Service version info\n"
        f"# TYPE pest_detection_info gauge\n"
        f'pest_detection_info{{service="{SERVICE_NAME}",version="{SERVICE_VERSION}"}} 1\n'
    )
    return PlainTextResponse(content=metrics_text, media_type="text/plain; version=0.0.4")


# Include API routers
app.include_router(pests.router, prefix="/api/v1", tags=["Pests | الآفات"])
app.include_router(scouts.router, prefix="/api/v1", tags=["Scouts | المسح الحقلي"])
app.include_router(thresholds.router, prefix="/api/v1", tags=["Thresholds | العتبات"])
app.include_router(treatments.router, prefix="/api/v1", tags=["Treatments | العلاج"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "error_ar": "خطأ داخلي في الخادم",
        },
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8125"))
    uvicorn.run(app, host="0.0.0.0", port=port)
