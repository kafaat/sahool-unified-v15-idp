"""
SAHOOL Task Service - خدمة إدارة المهام الزراعية
Port: 8103

Provides task management for agricultural operations:
- Task CRUD (create, read, update, delete)
- Task assignment and completion
- Evidence attachment (photos, notes)
- Task filtering and search
- NDVI-based task automation
- Astronomical calendar integration for optimal task scheduling
- Best day recommendations based on lunar cycles and mansions

Architecture:
- Routes: Separated into tasks, astronomical, and ndvi modules
- Exceptions: Custom domain-specific exceptions with bilingual support
- Cache: Redis-based with in-memory fallback for astronomical data
- Validators: Input validation with Pydantic and custom validators
- Utilities: Shared task creation and service integration logic
"""

import logging
import os
import sys
from contextlib import asynccontextmanager

try:
    import structlog
except ImportError:
    structlog = None  # type: ignore[assignment]

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ═══════════════════════════════════════════════════════════════════════════
# Configuration - التكوين
# ═══════════════════════════════════════════════════════════════════════════

SERVICE_NAME = "sahool-task-service"
SERVICE_PORT = int(os.getenv("PORT", "8103"))
SERVICE_VERSION = "16.0.0"

# Configure logging
# FIX: Use force=True to reset handlers and prevent double logging with uvicorn's default handlers
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)
# Suppress duplicate uvicorn access/error logs
logging.getLogger("uvicorn.access").propagate = False
if structlog is not None:
    logger = structlog.get_logger(__name__)
else:
    logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# Shared Middleware Imports - استيراد البرامج الوسيطة المشتركة
# ═══════════════════════════════════════════════════════════════════════════

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from shared.middleware import (
        RequestLoggingMiddleware,
        TenantContextMiddleware,
        setup_cors,
    )
    from shared.observability.middleware import ObservabilityMiddleware

    MIDDLEWARE_AVAILABLE = True
except ImportError:
    RequestLoggingMiddleware = None
    TenantContextMiddleware = None
    setup_cors = None
    ObservabilityMiddleware = None
    MIDDLEWARE_AVAILABLE = False

# Error handling
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    ERROR_HANDLING_AVAILABLE = True
except ImportError:
    setup_exception_handlers = None
    add_request_id_middleware = None
    ERROR_HANDLING_AVAILABLE = False

# Security headers
try:
    from shared.middleware.security_headers import setup_security_headers

    SECURITY_HEADERS_AVAILABLE = True
except ImportError:
    SECURITY_HEADERS_AVAILABLE = False

    def setup_security_headers(app):
        pass

# ═══════════════════════════════════════════════════════════════════════════
# Application Setup - إعداد التطبيق
# ═══════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager | مدير دورة حياة التطبيق"""
    logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION}...")

    # Initialize database
    logger.info("Initializing database...")
    try:
        from .database import init_database, init_demo_data_if_needed

        init_database(create_tables=True)
        init_demo_data_if_needed()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database: %s", type(e).__name__, exc_info=True)

    # Initialize NATS connection
    nats_url = os.getenv("NATS_URL", "nats://localhost:4222")
    safe_nats_url = str(nats_url).replace("\n", "").replace("\r", "")
    logger.info("Connecting to NATS at %s...", safe_nats_url)
    try:
        from .events import NatsPublisher
        from .events.nats_publisher import set_publisher

        publisher = NatsPublisher()
        connected = await publisher.connect(nats_url)
        if connected:
            set_publisher(publisher)
            app.state.nats_publisher = publisher
            logger.info("NATS connected: %s", safe_nats_url)
        else:
            app.state.nats_publisher = None
            logger.warning("NATS connection failed: %s", safe_nats_url)
    except ImportError:
        app.state.nats_publisher = None
        logger.warning("NATS events module not available")
    except Exception as e:
        app.state.nats_publisher = None
        logger.warning("NATS connection error: %s", type(e).__name__)

    # Initialize Redis cache
    logger.info("Initializing Redis cache...")
    try:
        from .cache import get_redis_client

        redis_client = await get_redis_client()
        if redis_client:
            logger.info("Redis cache connected")
        else:
            logger.info("Using in-memory cache (Redis unavailable)")
    except Exception as e:
        logger.warning("Redis connection error: %s, using in-memory cache", type(e).__name__)

    logger.info(f"{SERVICE_NAME} started on port {SERVICE_PORT}")

    yield

    # Shutdown | الإغلاق
    logger.info(f"Shutting down {SERVICE_NAME}...")

    # Close NATS connection
    if hasattr(app.state, "nats_publisher") and app.state.nats_publisher:
        try:
            await app.state.nats_publisher.close()
            logger.info("NATS connection closed")
        except Exception as e:
            logger.warning("Error closing NATS: %s", type(e).__name__)

    # Close Redis connection
    try:
        from .cache import close_redis

        await close_redis()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.warning("Error closing Redis: %s", type(e).__name__)

    # Close database connection
    try:
        from .database import close_database

        close_database()
        logger.info("Database connection closed")
    except Exception as e:
        logger.warning("Error closing database: %s", type(e).__name__)

    logger.info(f"{SERVICE_NAME} shutdown complete")


app = FastAPI(
    title="SAHOOL Task Service",
    description="Agricultural task management API with astronomical calendar integration",
    version=SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Setup unified error handling
if ERROR_HANDLING_AVAILABLE:
    if setup_exception_handlers:
        setup_exception_handlers(app)
    if add_request_id_middleware:
        add_request_id_middleware(app)

# CORS configuration
try:
    from shared.cors_config import CORS_SETTINGS

    app.add_middleware(CORSMiddleware, **CORS_SETTINGS)
except ImportError:
    ALLOWED_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "https://sahool.io,https://admin.sahool.io,http://localhost:3000",
    ).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Tenant-Id"],
    )

# Security headers
if SECURITY_HEADERS_AVAILABLE:
    setup_security_headers(app)

# Tenant context middleware - عزل المستأجرين
if TenantContextMiddleware:
    app.add_middleware(TenantContextMiddleware)

# ═══════════════════════════════════════════════════════════════════════════
# Custom Exception Handler - معالج الاستثناءات المخصص
# ═══════════════════════════════════════════════════════════════════════════

from .exceptions import TaskServiceError


@app.exception_handler(TaskServiceError)
async def task_service_error_handler(request: Request, exc: TaskServiceError):
    """
    Handle TaskServiceError exceptions with proper status codes and bilingual messages
    معالجة استثناءات خدمة المهام مع رموز الحالة المناسبة والرسائل ثنائية اللغة
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# Route Registration - تسجيل المسارات
# ═══════════════════════════════════════════════════════════════════════════

from .routes import astronomical_router, ndvi_router, tasks_router

# Register routers
app.include_router(tasks_router)
app.include_router(astronomical_router)
app.include_router(ndvi_router)


# ═══════════════════════════════════════════════════════════════════════════
# Health Check Endpoints - نقاط نهاية فحص الصحة
# ═══════════════════════════════════════════════════════════════════════════


@app.get("/healthz")
async def health_check():
    """Health check endpoint (liveness probe)"""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
    }


@app.get("/readyz")
async def readiness_check():
    """Kubernetes readiness probe - is the service ready to accept traffic?"""
    nats_status = "disconnected"
    if hasattr(app.state, "nats_publisher") and app.state.nats_publisher:
        nats_status = "connected" if app.state.nats_publisher.connected else "disconnected"

    # Check database connection with actual query
    db_ok = False
    try:
        from .database import engine

        if engine:
            from sqlalchemy import text

            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception as exc:
        logger.warning("Database readiness check failed: %s", type(exc).__name__)
        db_ok = False

    # Check Redis connection with actual ping
    redis_ok = False
    try:
        from .cache import get_redis_client

        redis_client = await get_redis_client()
        if redis_client:
            await redis_client.ping()
            redis_ok = True
    except Exception as exc:
        logger.debug("Redis availability check failed: %s", exc)

    is_ready = db_ok  # Database is required for readiness
    status_code = 200 if is_ready else 503

    from fastapi.responses import JSONResponse as _JSONResponse

    return _JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "checks": {
                "database": "connected" if db_ok else "disconnected",
                "nats": nats_status,
                "redis": "available" if redis_ok else "unavailable",
            },
        },
    )


@app.get("/health")
async def combined_health():
    """Combined health status"""
    liveness = await health_check()
    readiness = await readiness_check()
    return {
        **liveness,
        "ready": readiness["status"] == "ready",
        "checks": readiness["checks"],
    }


# ═══════════════════════════════════════════════════════════════════════════
# Lifecycle Events - أحداث دورة الحياة
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# Main Entry Point - نقطة الدخول الرئيسية
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")  # nosec B104 - binding to all interfaces required for Docker
    uvicorn.run(app, host=host, port=SERVICE_PORT)
