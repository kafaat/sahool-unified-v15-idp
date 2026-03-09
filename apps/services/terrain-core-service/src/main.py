"""
SAHOOL Terrain Core Service v16.0.0
خدمة تحليل التضاريس الأساسية - سهول

Main FastAPI application for terrain analysis providing:
- DEM processing from 4 sources (Copernicus, SRTM, ALOS, Local)
- 7 terrain indicators (slope, aspect, flow, TWI, curvature, contours)
- Irrigation suitability recommendations based on terrain

Port: 8185
"""

import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timezone
from pathlib import Path

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add paths for shared module imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

# Try to import shared error handling
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    SHARED_ERRORS_AVAILABLE = True
except ImportError:
    SHARED_ERRORS_AVAILABLE = False

from shared.middleware.tenant_context import TenantContextMiddleware

# Local imports
from .algorithms.dem_processor import DEMProcessor, DEMSource
from .algorithms.terrain_indicators import TerrainIndicatorCalculator
from .api.endpoints.terrain import router as terrain_router
from .core.config import settings

# Configure standard library logging (required for structlog.stdlib processors)
logging.basicConfig(
    format="%(message)s",
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
)

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
    Manage application lifecycle - startup and shutdown
    إدارة دورة حياة التطبيق - بدء التشغيل والإيقاف
    """
    # =========================================================================
    # Startup
    # =========================================================================
    logger.info(
        "Starting terrain-core-service",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        port=settings.PORT,
    )

    # Create temp and cache directories
    temp_dir = Path(settings.TEMP_DIR)
    temp_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = Path(settings.DEM_CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Directories initialized", temp_dir=str(temp_dir), cache_dir=str(cache_dir))

    # Initialize DEM Processor
    try:
        app.state.dem_processor = DEMProcessor(
            cache_dir=str(cache_dir),
            default_source=DEMSource(settings.DEFAULT_DEM_SOURCE.value),
            default_resolution_m=settings.DEFAULT_RESOLUTION_M,
            default_crs=settings.DEFAULT_CRS,
        )
        logger.info(
            "DEM processor initialized",
            default_source=settings.DEFAULT_DEM_SOURCE.value,
            default_resolution=settings.DEFAULT_RESOLUTION_M,
        )
    except Exception as e:
        logger.error("Failed to initialize DEM processor", error=str(e))
        app.state.dem_processor = None

    # Initialize Terrain Calculator
    try:
        app.state.terrain_calculator = TerrainIndicatorCalculator(
            cell_size_m=settings.DEFAULT_RESOLUTION_M,
        )
        logger.info("Terrain calculator initialized")
    except Exception as e:
        logger.error("Failed to initialize terrain calculator", error=str(e))
        app.state.terrain_calculator = None

    # Database connection (optional for caching terrain results)
    db_url = os.getenv("DATABASE_URL")
    # Enforce sslmode for non-development database connections
    if db_url and os.getenv("ENVIRONMENT", "development") != "development":
        if "sslmode" not in db_url:
            db_url += "?sslmode=require" if "?" not in db_url else "&sslmode=require"
    if db_url:
        try:
            import asyncpg

            app.state.db_pool = await asyncpg.create_pool(
                db_url,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
            )
            logger.info("Connected to database")
        except Exception as e:
            logger.warning("Failed to connect to database", error=str(e))
            app.state.db_pool = None
    else:
        app.state.db_pool = None
        logger.info("DATABASE_URL not configured, result caching disabled")

    # NATS connection for events
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            import nats

            app.state.nc = await nats.connect(nats_url)
            logger.info("Connected to NATS", nats_url=nats_url)
        except Exception as e:
            logger.warning("Failed to connect to NATS", error=str(e))
            app.state.nc = None
    else:
        app.state.nc = None
        logger.info("NATS_URL not configured, event publishing disabled")

    logger.info("terrain-core-service startup complete")

    yield

    # =========================================================================
    # Shutdown
    # =========================================================================
    logger.info("Shutting down terrain-core-service...")

    # Close DEM processor HTTP client
    if hasattr(app.state, "dem_processor") and app.state.dem_processor:
        await app.state.dem_processor.close()
        logger.info("DEM processor closed")

    # Close database pool
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
        logger.info("Database connection closed")

    # Close NATS connection
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()
        logger.info("NATS connection closed")

    logger.info("terrain-core-service shutdown complete")


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="SAHOOL Terrain Core Service | خدمة تحليل التضاريس",
    description="""
## Terrain Analysis Service for Agricultural Applications
خدمة تحليل التضاريس للتطبيقات الزراعية

Provides comprehensive terrain analysis from Digital Elevation Models (DEMs):

### DEM Sources | مصادر بيانات الارتفاعات
- **Copernicus DEM** (30m/90m) - Global coverage
- **NASA SRTM** (30m/90m) - 60°N to 56°S
- **ALOS World 3D** (30m) - Global coverage
- **Local Upload** - User-provided GeoTIFF files

### Terrain Indicators | مؤشرات التضاريس
1. **Slope** (الميل) - Using Horn's method
2. **Aspect** (الجانب) - Slope direction
3. **Flow Direction** (اتجاه التدفق) - D8 algorithm
4. **Flow Accumulation** (تراكم التدفق) - Contributing area
5. **TWI** (مؤشر الرطوبة الطبوغرافية) - Topographic Wetness Index
6. **Curvature** (الانحناء) - Plan and profile curvature
7. **Contours** (خطوط الكنتور) - Elevation isolines

### Agricultural Applications | التطبيقات الزراعية
- Irrigation suitability assessment
- Erosion risk evaluation
- Water flow analysis
- Terrain-based zone delineation
    """,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "terrain | التضاريس",
            "description": "Terrain analysis endpoints | نقاط نهاية تحليل التضاريس",
        },
        {
            "name": "health | الصحة",
            "description": "Health check endpoints | نقاط نهاية فحص الصحة",
        },
    ],
)

# =============================================================================
# Middleware
# =============================================================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Tenant-ID"],
)

# Setup unified error handling if available
if SHARED_ERRORS_AVAILABLE:
    setup_exception_handlers(app)
    add_request_id_middleware(app)
else:
    logger.warning("shared.errors_py not available, using basic error handling")

# Tenant context middleware
app.add_middleware(TenantContextMiddleware)

if not SHARED_ERRORS_AVAILABLE:

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception", error=str(exc), path=request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "error_ar": "خطأ داخلي في الخادم",
                "detail": str(exc) if settings.DEBUG else "An error occurred",
            },
        )


# =============================================================================
# Health Check Endpoints
# =============================================================================


@app.get(
    "/healthz",
    tags=["health | الصحة"],
    summary="Liveness probe | فحص الحياة",
)
def health():
    """
    Health check endpoint (liveness probe)
    نقطة نهاية فحص الصحة (فحص الحياة)
    """
    return {
        "status": "ok",
        "service": "terrain-core-service",
        "service_ar": "خدمة تحليل التضاريس",
        "version": settings.VERSION,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get(
    "/readyz",
    tags=["health | الصحة"],
    summary="Readiness probe | فحص الجاهزية",
)
def readiness():
    """
    Kubernetes readiness probe - is the service ready to accept traffic?
    فحص جاهزية Kubernetes - هل الخدمة جاهزة لاستقبال الطلبات؟
    """
    dem_processor_ready = hasattr(app.state, "dem_processor") and app.state.dem_processor is not None
    terrain_calc_ready = hasattr(app.state, "terrain_calculator") and app.state.terrain_calculator is not None
    nats_connected = hasattr(app.state, "nc") and app.state.nc is not None
    db_connected = hasattr(app.state, "db_pool") and app.state.db_pool is not None

    # Service is ready if core components are initialized
    is_ready = dem_processor_ready and terrain_calc_ready

    return {
        "status": "ready" if is_ready else "not_ready",
        "service": "terrain-core-service",
        "version": settings.VERSION,
        "checks": {
            "dem_processor": "ready" if dem_processor_ready else "not_ready",
            "terrain_calculator": "ready" if terrain_calc_ready else "not_ready",
            "nats": "connected" if nats_connected else "disconnected",
            "database": "connected" if db_connected else "disconnected",
        },
        "config": {
            "default_dem_source": settings.DEFAULT_DEM_SOURCE.value,
            "default_resolution_m": settings.DEFAULT_RESOLUTION_M,
            "default_crs": settings.DEFAULT_CRS,
        },
    }


@app.get(
    "/health",
    tags=["health | الصحة"],
    summary="Combined health status | حالة الصحة المجمعة",
)
def health_combined():
    """Combined health and readiness status | حالة الصحة والجاهزية المجمعة"""
    readiness_status = readiness()
    return {
        **health(),
        "ready": readiness_status["status"] == "ready",
        "checks": readiness_status["checks"],
    }


@app.get(
    "/metrics",
    tags=["health | الصحة"],
    summary="Prometheus metrics | مقاييس بروميثيوس",
)
def metrics():
    """
    Prometheus-compatible metrics endpoint.
    نقطة نهاية المقاييس المتوافقة مع بروميثيوس
    """
    from fastapi.responses import PlainTextResponse

    # Basic service metrics in Prometheus format
    dem_processor_ready = 1 if (hasattr(app.state, "dem_processor") and app.state.dem_processor) else 0
    terrain_calc_ready = 1 if (hasattr(app.state, "terrain_calculator") and app.state.terrain_calculator) else 0
    nats_connected = 1 if (hasattr(app.state, "nc") and app.state.nc) else 0
    db_connected = 1 if (hasattr(app.state, "db_pool") and app.state.db_pool) else 0

    metrics_output = f"""# HELP terrain_service_up Service up status
# TYPE terrain_service_up gauge
terrain_service_up 1

# HELP terrain_dem_processor_ready DEM processor ready status
# TYPE terrain_dem_processor_ready gauge
terrain_dem_processor_ready {dem_processor_ready}

# HELP terrain_calculator_ready Terrain calculator ready status
# TYPE terrain_calculator_ready gauge
terrain_calculator_ready {terrain_calc_ready}

# HELP terrain_nats_connected NATS connection status
# TYPE terrain_nats_connected gauge
terrain_nats_connected {nats_connected}

# HELP terrain_database_connected Database connection status
# TYPE terrain_database_connected gauge
terrain_database_connected {db_connected}

# HELP terrain_service_info Service version info
# TYPE terrain_service_info gauge
terrain_service_info{{version="{settings.VERSION}",dem_source="{settings.DEFAULT_DEM_SOURCE.value}"}} 1
"""
    return PlainTextResponse(content=metrics_output, media_type="text/plain; charset=utf-8")


# =============================================================================
# Include Routers
# =============================================================================

app.include_router(terrain_router)


# =============================================================================
# Root Endpoint
# =============================================================================


@app.get("/", include_in_schema=False)
def root():
    """Root endpoint redirect to docs | نقطة النهاية الجذرية للتوجيه إلى الوثائق"""
    return {
        "service": "terrain-core-service",
        "service_ar": "خدمة تحليل التضاريس",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "health_url": "/healthz",
        "endpoints": {
            "analyze": "/api/v1/terrain/analyze",
            "slope": "/api/v1/terrain/slope/{field_id}",
            "flow": "/api/v1/terrain/flow/{field_id}",
            "twi": "/api/v1/terrain/twi/{field_id}",
            "contours": "/api/v1/terrain/contours/{field_id}",
            "sources": "/api/v1/terrain/sources",
        },
    }


# =============================================================================
# Event Publishing Helper
# =============================================================================


async def publish_event(subject: str, data: dict):
    """Publish event to NATS if connected | نشر حدث إلى NATS إذا كان متصلاً"""
    if hasattr(app.state, "nc") and app.state.nc:
        try:
            full_subject = f"{settings.NATS_SUBJECT_PREFIX}.{subject}"
            await app.state.nc.publish(full_subject, json.dumps(data).encode())
            logger.debug("Published event", subject=full_subject)
        except Exception as e:
            logger.warning("Failed to publish event", subject=subject, error=str(e))


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
