"""
YOLO26 Vision Service - Main Application.

FastAPI-based computer vision service for the SAHOOL agricultural platform.
Provides pest detection, disease detection, weed detection, plant counting,
ripeness classification, leaf segmentation, and object tracking.

Port: 8150
Version: 16.0.0
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

import structlog
import torch
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.endpoints import analysis, batch, detection, models
from src.api.schemas import ErrorResponse, HealthStatus, ReadinessStatus

try:
    from shared.middleware.tenant_context import TenantContextMiddleware

    TENANT_MIDDLEWARE_AVAILABLE = True
except ImportError:
    TENANT_MIDDLEWARE_AVAILABLE = False

from src.core.config import settings
from src.core.errors import VisionError, vision_error_handler
from src.models.yolo26_manager import ModelTask, YOLO26ModelManager, get_model_manager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if settings.is_production else structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


# =============================================================================
# Lifespan Context Manager
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown of resources:
    - Model manager initialization
    - Database connections (if configured)
    - NATS connections (if configured)
    - GPU verification
    """
    logger.info(
        "starting_yolo26_vision_service",
        version=settings.service_version,
        environment=settings.environment,
        device=settings.device,
    )

    # Initialize model manager
    try:
        manager = get_model_manager()
        app.state.model_manager = manager

        # Log GPU status
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            for i in range(gpu_count):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                logger.info(
                    "gpu_detected",
                    index=i,
                    name=gpu_name,
                    memory_gb=round(gpu_memory, 2),
                )
        else:
            logger.warning("no_gpu_detected", using="cpu")

        # Pre-load default models if in production
        if settings.is_production:
            logger.info("preloading_default_models")
            try:
                await manager.load_model(ModelTask.PEST_DETECTION, settings.default_model_variant)
                await manager.load_model(ModelTask.DISEASE_DETECTION, settings.default_model_variant)
                logger.info("default_models_preloaded")
            except Exception as e:
                logger.warning("model_preload_failed", error=str(e))

        app.state.models_loaded = True
        logger.info("model_manager_initialized")

    except Exception as e:
        logger.error("model_manager_init_failed", error=str(e))
        app.state.models_loaded = False

    # Initialize database connection (optional)
    app.state.db_connected = False
    if settings.database_url:
        try:
            import asyncpg

            app.state.db_pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=settings.db_pool_min_size,
                max_size=settings.db_pool_max_size,
            )
            app.state.db_connected = True
            logger.info("database_connected")
        except Exception as e:
            logger.warning("database_connection_failed", error=str(e))

    # Initialize NATS connection (optional)
    app.state.nats_connected = False
    if settings.nats_url:
        try:
            import nats

            app.state.nc = await nats.connect(settings.nats_url)
            app.state.nats_connected = True
            logger.info("nats_connected", url=settings.nats_url)
        except Exception as e:
            logger.warning("nats_connection_failed", error=str(e))

    logger.info(
        "yolo26_vision_service_started",
        host=settings.host,
        port=settings.port,
    )

    yield

    # Shutdown
    logger.info("shutting_down_yolo26_vision_service")

    # Close database connection
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
        logger.info("database_disconnected")

    # Close NATS connection
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()
        logger.info("nats_disconnected")

    # Clear model cache
    if hasattr(app.state, "model_manager") and app.state.model_manager:
        app.state.model_manager.clear_cache()
        logger.info("model_cache_cleared")

    logger.info("yolo26_vision_service_stopped")


# =============================================================================
# FastAPI Application
# =============================================================================


app = FastAPI(
    title="YOLO26 Vision Service",
    description="""
SAHOOL Agricultural Computer Vision Service powered by YOLO26.

## Features

### Detection
- **Pest Detection**: Identify 20+ agricultural pest species
- **Disease Detection**: Detect 30+ plant diseases
- **Weed Detection**: Identify common agricultural weeds

### Analysis
- **Plant Counting**: Count plants with density mapping
- **Ripeness Classification**: 5-stage fruit ripeness analysis
- **Leaf Segmentation**: Leaf area measurement and LAI estimation
- **Object Tracking**: Track objects with persistent IDs

## Bilingual Support
All class names are provided in both Arabic (العربية) and English.

## API Version
Current API version: v1
    """,
    version=settings.service_version,
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
)

# Setup unified error handling
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    setup_exception_handlers(app)
    add_request_id_middleware(app)
except ImportError:
    pass

# Register VisionError handler for structured bilingual error responses
app.add_exception_handler(VisionError, vision_error_handler)


# =============================================================================
# Middleware
# =============================================================================


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tenant context middleware
if TENANT_MIDDLEWARE_AVAILABLE:
    app.add_middleware(TenantContextMiddleware)


# Request ID Middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to response headers."""
    import uuid

    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests and responses."""
    import time

    start_time = time.perf_counter()

    # Log request
    logger.info(
        "request_received",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else "unknown",
    )

    response = await call_next(request)

    # Log response
    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2),
    )

    return response


# =============================================================================
# Exception Handlers
# =============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
            "message_ar": "حدث خطأ غير متوقع",
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    logger.warning("value_error", path=request.url.path, error=str(exc))

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
            "message": str(exc),
            "message_ar": "طلب غير صالح",
        },
    )


# =============================================================================
# Health Endpoints
# =============================================================================


@app.get(
    "/healthz",
    response_model=HealthStatus,
    tags=["health"],
    summary="Liveness probe",
    description="Returns service liveness status for Kubernetes health checks.",
)
@app.get("/health/live", response_model=HealthStatus, include_in_schema=False)
async def health_check() -> HealthStatus:
    """Liveness probe endpoint."""
    return HealthStatus(
        status="ok",
        service=settings.service_name,
        version=settings.service_version,
    )


@app.get(
    "/readyz",
    response_model=ReadinessStatus,
    tags=["health"],
    summary="Readiness probe",
    description="Returns service readiness status including component health.",
)
@app.get("/health/ready", response_model=ReadinessStatus, include_in_schema=False)
async def readiness_check(request: Request) -> ReadinessStatus:
    """Readiness probe endpoint."""
    models_loaded = getattr(request.app.state, "models_loaded", False)
    db_connected = getattr(request.app.state, "db_connected", False)
    nats_connected = getattr(request.app.state, "nats_connected", False)
    gpu_available = torch.cuda.is_available()

    # Check loaded models
    model_status = {}
    if hasattr(request.app.state, "model_manager"):
        manager = request.app.state.model_manager
        for model_key in manager.get_loaded_models():
            model_status[model_key] = True

    # Determine overall status
    overall_status = "ok"
    if not models_loaded:
        overall_status = "degraded"

    return ReadinessStatus(
        status=overall_status,
        database=db_connected,
        nats=nats_connected,
        redis=False,  # Not used in this service
        models_loaded=models_loaded,
        gpu_available=gpu_available,
        models=model_status,
    )


@app.get(
    "/health",
    tags=["health"],
    summary="Combined health check",
    description="Returns detailed health information for the service.",
)
async def combined_health(request: Request) -> dict:
    """Combined health check with detailed status."""
    gpu_info = None
    if hasattr(request.app.state, "model_manager"):
        manager = request.app.state.model_manager
        gpu_info = manager.gpu_memory_info

    return {
        "status": "ok",
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
        "database": getattr(request.app.state, "db_connected", False),
        "nats": getattr(request.app.state, "nats_connected", False),
        "models_loaded": getattr(request.app.state, "models_loaded", False),
        "gpu": {
            "available": torch.cuda.is_available(),
            "device": settings.device,
            "memory": gpu_info,
        },
    }


@app.get(
    "/metrics",
    tags=["health"],
    summary="Prometheus metrics",
    description="Returns Prometheus-compatible metrics.",
)
async def metrics(request: Request) -> str:
    """Prometheus metrics endpoint."""
    # Basic metrics (would integrate with prometheus_client in production)
    gpu_available = 1 if torch.cuda.is_available() else 0
    models_loaded = len(
        request.app.state.model_manager.get_loaded_models() if hasattr(request.app.state, "model_manager") else []
    )

    metrics_output = f"""# HELP yolo26_gpu_available GPU availability (1=available, 0=not)
# TYPE yolo26_gpu_available gauge
yolo26_gpu_available {gpu_available}

# HELP yolo26_models_loaded Number of loaded models
# TYPE yolo26_models_loaded gauge
yolo26_models_loaded {models_loaded}

# HELP yolo26_service_info Service information
# TYPE yolo26_service_info gauge
yolo26_service_info{{version="{settings.service_version}",environment="{settings.environment}"}} 1
"""

    from fastapi.responses import PlainTextResponse

    return PlainTextResponse(content=metrics_output, media_type="text/plain")


# =============================================================================
# API Info Endpoint
# =============================================================================


@app.get(
    "/",
    tags=["info"],
    summary="Service information",
    description="Returns basic service information.",
)
async def root() -> dict:
    """Service information endpoint."""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "description": "SAHOOL Agricultural Computer Vision Service powered by YOLO26",
        "description_ar": "خدمة الرؤية الحاسوبية الزراعية لمنصة سهول مدعومة بـ YOLO26",
        "endpoints": {
            "detection": {
                "pest": "/api/v1/detect/pest",
                "disease": "/api/v1/detect/disease",
                "weed": "/api/v1/detect/weed",
            },
            "analysis": {
                "plant_count": "/api/v1/count/plants",
                "ripeness": "/api/v1/classify/ripeness",
                "leaf_segmentation": "/api/v1/segment/leaf",
                "object_tracking": "/api/v1/track/objects",
            },
            "health": {
                "liveness": "/healthz",
                "readiness": "/readyz",
                "metrics": "/metrics",
            },
        },
        "documentation": "/docs" if not settings.is_production else None,
    }


# =============================================================================
# Include Routers
# =============================================================================


app.include_router(detection.router)
app.include_router(analysis.router)
app.include_router(batch.router)
app.include_router(models.router)


# =============================================================================
# Main Entry Point
# =============================================================================


def main():
    """Main entry point for running the service."""
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main()
