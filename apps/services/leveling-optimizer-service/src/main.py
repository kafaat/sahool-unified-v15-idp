"""
Leveling Optimizer Service - Main Application

خدمة تحسين التسوية - التطبيق الرئيسي

This service provides optimal field leveling calculations for agricultural
land preparation, including:
- Cut/fill volume calculations
- Optimal grade plane computation
- Equipment recommendations
- Cost estimation in SAR

Version: 16.0.0
Port: 8170
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from shared.middleware.tenant_context import TenantContextMiddleware

    TENANT_MIDDLEWARE_AVAILABLE = True
except ImportError:
    TENANT_MIDDLEWARE_AVAILABLE = False

from .api.endpoints import leveling
from .api.schemas import ErrorResponse, HealthResponse, ReadinessResponse
from .core.config import settings

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
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    مدير السياق لأحداث البدء والإيقاف
    """
    # Startup
    logger.info(
        "service_starting",
        service=settings.SERVICE_NAME,
        service_ar=settings.SERVICE_NAME_AR,
        version=settings.VERSION,
        port=settings.PORT,
    )

    # Initialize database connection if configured
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
            logger.info("database_connected", url=db_url[:20] + "...")
        except Exception as e:
            logger.warning("database_connection_failed", error=str(e))
            app.state.db_pool = None
            app.state.db_connected = False
    else:
        app.state.db_pool = None
        app.state.db_connected = False
        logger.info("database_not_configured")

    # Initialize NATS connection if configured
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            import nats

            app.state.nc = await nats.connect(nats_url)
            app.state.nats_connected = True
            logger.info("nats_connected", url=nats_url)
        except Exception as e:
            logger.warning("nats_connection_failed", error=str(e))
            app.state.nc = None
            app.state.nats_connected = False
    else:
        app.state.nc = None
        app.state.nats_connected = False
        logger.info("nats_not_configured")

    logger.info(
        "service_started",
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
    )

    yield

    # Shutdown
    logger.info("service_stopping", service=settings.SERVICE_NAME)

    # Close database connection
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
        logger.info("database_disconnected")

    # Close NATS connection
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()
        logger.info("nats_disconnected")

    logger.info("service_stopped", service=settings.SERVICE_NAME)


# Create FastAPI application
app = FastAPI(
    title="Leveling Optimizer Service | خدمة تحسين التسوية",
    description="""
Agricultural field leveling optimization service for the SAHOOL platform.

خدمة تحسين تسوية الحقول الزراعية لمنصة سهول

## Features | الميزات

- **Cut/Fill Volume Calculation** | حساب أحجام القطع والردم
- **Optimal Grade Plane Computation** | حساب مستوى الميل الأمثل
- **Equipment Recommendations** | توصيات المعدات
- **Cost Estimation in SAR** | تقدير التكلفة بالريال السعودي
- **Leveling Simulation** | محاكاة التسوية

## Leveling Methods | طرق التسوية

- Single Plane | مستوى واحد
- Dual Plane | مستويين
- Contour Leveling | تسوية كنتورية
- Bench/Terrace | مصاطب

## Optimization Priorities | أولويات التحسين

- Minimize Cost | تقليل التكلفة
- Minimize Earthwork | تقليل الحفريات
- Optimal Drainage | تصريف مثالي
- Irrigation Efficiency | كفاءة الري
    """,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Setup unified error handling
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    setup_exception_handlers(app)
    add_request_id_middleware(app)
except ImportError:
    pass

# Add CORS middleware
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
if TENANT_MIDDLEWARE_AVAILABLE:
    app.add_middleware(TenantContextMiddleware)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests for tracing."""
    import uuid

    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    request_id = getattr(request.state, "request_id", None)

    logger.error(
        "unhandled_exception",
        error=str(exc),
        request_id=request_id,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "error_ar": "خطأ داخلي في الخادم",
            "detail": str(exc) if settings.DEBUG else None,
            "request_id": request_id,
        },
    )


# Include routers
app.include_router(leveling.router)


# Health endpoints
@app.get(
    "/healthz",
    response_model=HealthResponse,
    tags=["Health | الصحة"],
    summary="Liveness probe | فحص الحياة",
)
@app.get(
    "/health/live",
    response_model=HealthResponse,
    tags=["Health | الصحة"],
    summary="Liveness probe (alias) | فحص الحياة (بديل)",
)
async def health():
    """
    Liveness probe endpoint.

    نقطة نهاية فحص الحياة
    """
    return HealthResponse(
        status="ok",
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        timestamp=datetime.utcnow(),
    )


@app.get(
    "/readyz",
    response_model=ReadinessResponse,
    tags=["Health | الصحة"],
    summary="Readiness probe | فحص الجاهزية",
)
@app.get(
    "/health/ready",
    response_model=ReadinessResponse,
    tags=["Health | الصحة"],
    summary="Readiness probe (alias) | فحص الجاهزية (بديل)",
)
async def readiness(request: Request):
    """
    Readiness probe endpoint.

    نقطة نهاية فحص الجاهزية
    """
    db_connected = getattr(request.app.state, "db_connected", False)
    nats_connected = getattr(request.app.state, "nats_connected", False)

    # Service is ready if core functionality works
    # Database and NATS are optional for basic leveling calculations
    status = "ok"

    return ReadinessResponse(
        status=status,
        database=db_connected,
        nats=nats_connected,
        checks={
            "algorithms": True,  # Core algorithms always available
            "config": True,  # Configuration loaded
        },
    )


@app.get(
    "/health",
    tags=["Health | الصحة"],
    summary="Combined health status | حالة الصحة الشاملة",
)
async def combined_health(request: Request):
    """
    Combined health status endpoint.

    نقطة نهاية حالة الصحة الشاملة
    """
    db_connected = getattr(request.app.state, "db_connected", False)
    nats_connected = getattr(request.app.state, "nats_connected", False)

    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "service_ar": settings.SERVICE_NAME_AR,
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": "connected" if db_connected else "not_configured",
            "nats": "connected" if nats_connected else "not_configured",
            "algorithms": "available",
        },
    }


@app.get(
    "/metrics",
    tags=["Health | الصحة"],
    summary="Prometheus metrics | مقاييس بروميثيوس",
)
async def metrics(request: Request):
    """
    Prometheus-compatible metrics endpoint.
    نقطة نهاية المقاييس المتوافقة مع بروميثيوس
    """
    from fastapi.responses import PlainTextResponse

    db_connected = 1 if getattr(request.app.state, "db_connected", False) else 0
    nats_connected = 1 if getattr(request.app.state, "nats_connected", False) else 0

    metrics_output = f"""# HELP leveling_service_up Service up status
# TYPE leveling_service_up gauge
leveling_service_up 1

# HELP leveling_database_connected Database connection status
# TYPE leveling_database_connected gauge
leveling_database_connected {db_connected}

# HELP leveling_nats_connected NATS connection status
# TYPE leveling_nats_connected gauge
leveling_nats_connected {nats_connected}

# HELP leveling_algorithms_available Core algorithms available
# TYPE leveling_algorithms_available gauge
leveling_algorithms_available 1

# HELP leveling_service_info Service version info
# TYPE leveling_service_info gauge
leveling_service_info{{version="{settings.VERSION}",service="{settings.SERVICE_NAME}"}} 1

# HELP leveling_equipment_cost_sar Equipment costs in SAR per hour
# TYPE leveling_equipment_cost_sar gauge
leveling_equipment_cost_sar{{equipment="bulldozer"}} {settings.BULLDOZER_COST_PER_HOUR}
leveling_equipment_cost_sar{{equipment="scraper"}} {settings.SCRAPER_COST_PER_HOUR}
leveling_equipment_cost_sar{{equipment="grader"}} {settings.GRADER_COST_PER_HOUR}
leveling_equipment_cost_sar{{equipment="laser_leveler"}} {settings.LASER_LEVELER_COST_PER_HOUR}
leveling_equipment_cost_sar{{equipment="excavator"}} {settings.EXCAVATOR_COST_PER_HOUR}
"""
    return PlainTextResponse(content=metrics_output, media_type="text/plain; charset=utf-8")


@app.get(
    "/",
    tags=["Root | الجذر"],
    summary="Service information | معلومات الخدمة",
)
async def root():
    """
    Root endpoint with service information.

    نقطة النهاية الجذرية مع معلومات الخدمة
    """
    return {
        "service": settings.SERVICE_NAME,
        "service_ar": settings.SERVICE_NAME_AR,
        "version": settings.VERSION,
        "description": "Agricultural field leveling optimization service",
        "description_ar": "خدمة تحسين تسوية الحقول الزراعية",
        "documentation": "/docs",
        "health": "/healthz",
        "readiness": "/readyz",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
