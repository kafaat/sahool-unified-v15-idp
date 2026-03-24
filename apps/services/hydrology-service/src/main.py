"""
SAHOOL Hydrology Service v16.0.0
خدمة الهيدرولوجيا - تحليل التصريف والتشبع المائي

Agricultural hydrological analysis service providing:
- Drainage network extraction using D8 flow direction
- Topographic Wetness Index (TWI) calculation
- Depression identification and waterlogging prediction
- Stream detection with Strahler ordering
- Basin/watershed delineation

Port: 8165

Integration:
- terrain-core-service: DEM data source
- weather-service: Rainfall data for waterlogging prediction
"""

import json
import os
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timezone

import asyncpg
import nats
import structlog
from fastapi import FastAPI

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.db.simple_migrations import Migration, SimpleMigrationRunner
from shared.errors_py import add_request_id_middleware, setup_exception_handlers
from shared.middleware.tenant_context import TenantContextMiddleware

from .api.endpoints.hydrology import router as hydrology_router
from .core.config import get_settings

# ---------------------------------------------------------------------------
# Database Migrations
# ---------------------------------------------------------------------------

MIGRATIONS = [
    Migration(
        version=1,
        description="Create hydrology_analyses table",
        up="""
            CREATE TABLE IF NOT EXISTS hydrology_analyses (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                field_id VARCHAR(255) NOT NULL,
                tenant_id VARCHAR(255),
                analysis_type VARCHAR(100) NOT NULL,
                result JSONB NOT NULL,
                dem_source VARCHAR(100),
                resolution_m FLOAT,
                analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(field_id, analysis_type, tenant_id)
            )
        """,
        down="DROP TABLE IF EXISTS hydrology_analyses",
    ),
    Migration(
        version=2,
        description="Add field_id and tenant_id indexes",
        up="""
            CREATE INDEX IF NOT EXISTS idx_hydrology_field_id
                ON hydrology_analyses(field_id);
            CREATE INDEX IF NOT EXISTS idx_hydrology_tenant_id
                ON hydrology_analyses(tenant_id);
        """,
        down="""
            DROP INDEX IF EXISTS idx_hydrology_tenant_id;
            DROP INDEX IF EXISTS idx_hydrology_field_id;
        """,
    ),
]

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
    Manage application lifecycle - startup and shutdown.
    إدارة دورة حياة التطبيق - البدء والإيقاف
    """
    settings = get_settings()

    # Startup
    logger.info(
        "Starting hydrology-service",
        version=settings.version,
        environment=settings.environment,
        port=settings.port,
    )

    # Database connection
    # Enforce sslmode for non-development database connections
    db_url = settings.database_url
    if db_url and os.getenv("ENVIRONMENT", "development") != "development":
        if "sslmode" not in db_url:
            # Use sslmode=disable for PgBouncer (port 6432) which does not support SSL
            ssl_mode = "disable" if ":6432" in db_url else "require"
            db_url += f"?sslmode={ssl_mode}" if "?" not in db_url else f"&sslmode={ssl_mode}"
    if db_url:
        try:
            app.state.db_pool = await asyncpg.create_pool(
                db_url,
                min_size=settings.db_pool_min_size,
                max_size=settings.db_pool_max_size,
            )
            logger.info("Connected to database")

            # Run versioned migrations
            migration_runner = SimpleMigrationRunner(
                app.state.db_pool, service_name="hydrology-service"
            )
            await migration_runner.run(MIGRATIONS)
            logger.info("Database migrations applied")

        except Exception as e:
            logger.warning(
                "Failed to connect to database",
                error=str(e),
                database_url=settings.database_url[:20] + "...",
            )
            app.state.db_pool = None
    else:
        app.state.db_pool = None
        logger.info("DATABASE_URL not configured, using in-memory storage")

    # NATS connection
    if settings.nats_url:
        try:
            app.state.nc = await nats.connect(settings.nats_url)
            logger.info("Connected to NATS", nats_url=settings.nats_url)
        except Exception as e:
            logger.warning("Failed to connect to NATS", error=str(e))
            app.state.nc = None
    else:
        app.state.nc = None
        logger.info("NATS_URL not configured, event publishing disabled")

    logger.info(
        "Hydrology service ready",
        port=settings.port,
        terrain_service=settings.terrain_service_url,
        weather_service=settings.weather_service_url,
    )

    yield

    # Shutdown
    logger.info("Shutting down hydrology-service...")

    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
        logger.info("Database connection closed")

    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()
        logger.info("NATS connection closed")

    logger.info("Hydrology service stopped")


# Create FastAPI application
app = FastAPI(
    title="SAHOOL Hydrology Service | خدمة الهيدرولوجيا",
    description="""
Agricultural hydrological analysis service for the SAHOOL platform.

خدمة التحليل الهيدرولوجي الزراعي لمنصة سهول.

## Features | الميزات

- **Drainage Network** | شبكة التصريف: Extract drainage channels using D8 algorithm
- **Wetness Analysis** | تحليل الرطوبة: Calculate Topographic Wetness Index (TWI)
- **Depression Detection** | كشف المنخفضات: Identify areas prone to waterlogging
- **Stream Detection** | كشف المجاري: Detect streams with Strahler ordering
- **Basin Delineation** | تحديد الأحواض: Delineate watershed boundaries

## Integration | التكامل

- terrain-core-service: DEM data source
- weather-service: Rainfall data for predictions
    """,
    version="16.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)
app.add_middleware(TenantContextMiddleware)

# Include routers
app.include_router(hydrology_router)


# ==============================================================================
# Health Check Endpoints
# ==============================================================================


@app.get("/healthz", tags=["Health"])
def health():
    """
    Health check endpoint (liveness probe).
    نقطة فحص الصحة (فحص الحياة)
    """
    return {
        "status": "ok",
        "service": "hydrology-service",
        "service_ar": "خدمة الهيدرولوجيا",
        "version": "16.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/readyz", tags=["Health"])
def readiness():
    """
    Kubernetes readiness probe - is the service ready to accept traffic?
    فحص الجاهزية - هل الخدمة جاهزة لاستقبال الطلبات؟
    """
    settings = get_settings()
    nats_connected = hasattr(app.state, "nc") and app.state.nc is not None
    db_connected = hasattr(app.state, "db_pool") and app.state.db_pool is not None

    return {
        "status": "ready",
        "service": "hydrology-service",
        "service_ar": "خدمة الهيدرولوجيا",
        "version": "16.0.0",
        "checks": {
            "nats": "connected" if nats_connected else "disconnected",
            "database": "connected" if db_connected else "disconnected",
            "terrain_service": settings.terrain_service_url,
            "weather_service": settings.weather_service_url,
        },
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/health", tags=["Health"])
def combined_health():
    """
    Combined health check endpoint.
    فحص صحة شامل
    """
    settings = get_settings()
    nats_connected = hasattr(app.state, "nc") and app.state.nc is not None
    db_connected = hasattr(app.state, "db_pool") and app.state.db_pool is not None

    all_healthy = True  # Core service is always healthy if responding

    return {
        "status": "healthy" if all_healthy else "degraded",
        "service": "hydrology-service",
        "version": "16.0.0",
        "environment": settings.environment,
        "components": {
            "api": {"status": "healthy"},
            "database": {
                "status": "healthy" if db_connected else "unavailable",
                "connected": db_connected,
            },
            "nats": {
                "status": "healthy" if nats_connected else "unavailable",
                "connected": nats_connected,
            },
        },
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/metrics", tags=["Health"])
def metrics():
    """
    Prometheus-compatible metrics endpoint.
    نقطة نهاية المقاييس المتوافقة مع بروميثيوس
    """
    from fastapi.responses import PlainTextResponse

    settings = get_settings()
    nats_connected = 1 if (hasattr(app.state, "nc") and app.state.nc) else 0
    db_connected = 1 if (hasattr(app.state, "db_pool") and app.state.db_pool) else 0

    metrics_output = f"""# HELP hydrology_service_up Service up status
# TYPE hydrology_service_up gauge
hydrology_service_up 1

# HELP hydrology_database_connected Database connection status
# TYPE hydrology_database_connected gauge
hydrology_database_connected {db_connected}

# HELP hydrology_nats_connected NATS connection status
# TYPE hydrology_nats_connected gauge
hydrology_nats_connected {nats_connected}

# HELP hydrology_service_info Service version info
# TYPE hydrology_service_info gauge
hydrology_service_info{{version="{settings.version}",environment="{settings.environment}"}} 1

# HELP hydrology_config_dem_resolution Default DEM resolution in meters
# TYPE hydrology_config_dem_resolution gauge
hydrology_config_dem_resolution {settings.default_dem_resolution}

# HELP hydrology_config_flow_threshold Flow accumulation threshold
# TYPE hydrology_config_flow_threshold gauge
hydrology_config_flow_threshold {settings.flow_accumulation_threshold}

# HELP hydrology_config_wetness_threshold TWI high wetness threshold
# TYPE hydrology_config_wetness_threshold gauge
hydrology_config_wetness_threshold {settings.wetness_index_high_threshold}
"""
    return PlainTextResponse(content=metrics_output, media_type="text/plain; charset=utf-8")


# ==============================================================================
# Event Publishing
# ==============================================================================


async def publish_event(subject: str, data: dict):
    """
    Publish event to NATS if connected.
    نشر حدث إلى NATS إذا كان متصلاً
    """
    if hasattr(app.state, "nc") and app.state.nc:
        try:
            await app.state.nc.publish(subject, json.dumps(data).encode())
            logger.debug("Published event", subject=subject)
        except Exception as e:
            logger.warning("Failed to publish event", subject=subject, error=str(e))


# ==============================================================================
# Database Helper Functions
# ==============================================================================


async def save_analysis(
    field_id: str,
    analysis_type: str,
    result: dict,
    tenant_id: str,
    dem_source: str | None = None,
    resolution_m: float | None = None,
) -> bool:
    """
    Save analysis result to database.
    حفظ نتيجة التحليل في قاعدة البيانات
    """
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        try:
            async with app.state.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO hydrology_analyses
                    (field_id, tenant_id, analysis_type, result, dem_source, resolution_m)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (field_id, analysis_type, tenant_id)
                    DO UPDATE SET
                        result = $4,
                        dem_source = $5,
                        resolution_m = $6,
                        analyzed_at = NOW()
                """,
                    field_id,
                    tenant_id,
                    analysis_type,
                    json.dumps(result),
                    dem_source,
                    resolution_m,
                )
            logger.debug("Saved analysis", field_id=field_id, analysis_type=analysis_type)
            return True
        except Exception as e:
            logger.warning(
                "Failed to save analysis",
                field_id=field_id,
                analysis_type=analysis_type,
                error=str(e),
            )
            return False
    return False


async def get_analysis(field_id: str, analysis_type: str, tenant_id: str) -> dict | None:
    """
    Retrieve analysis result from database with mandatory tenant isolation.
    استرجاع نتيجة التحليل من قاعدة البيانات مع عزل إلزامي للمستأجر
    """
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        try:
            async with app.state.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT result, analyzed_at, dem_source, resolution_m
                    FROM hydrology_analyses
                    WHERE field_id = $1 AND analysis_type = $2 AND tenant_id = $3
                """,
                    field_id,
                    analysis_type,
                    tenant_id,
                )

                if row:
                    data = json.loads(row["result"])
                    data["_metadata"] = {
                        "analyzed_at": row["analyzed_at"].isoformat(),
                        "dem_source": row["dem_source"],
                        "resolution_m": row["resolution_m"],
                    }
                    return data
        except Exception as e:
            logger.warning(
                "Failed to get analysis",
                field_id=field_id,
                analysis_type=analysis_type,
                error=str(e),
            )
    return None


# ==============================================================================
# Main Entry Point
# ==============================================================================


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port, log_level=settings.log_level.lower())
