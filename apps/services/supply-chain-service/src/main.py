"""Supply Chain Service - FastAPI Application.

This service connects farmers to agricultural suppliers for auto-purchasing.
خدمة سلسلة التوريد - تربط المزارعين بموردي المستلزمات الزراعية للشراء التلقائي.
"""

import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.endpoints import (
    auto_purchase_router,
    orders_router,
    products_router,
    suppliers_router,
)
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
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown.

    Initializes database, NATS, and Redis connections on startup.
    Closes all connections on shutdown.
    """
    logger.info(
        "starting_service",
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        port=settings.PORT,
    )

    # Initialize database connection
    db_url = settings.DATABASE_URL
    if db_url:
        try:
            import asyncpg

            app.state.db_pool = await asyncpg.create_pool(
                db_url,
                min_size=settings.DB_MIN_CONNECTIONS,
                max_size=settings.DB_MAX_CONNECTIONS,
            )
            app.state.db_connected = True
            logger.info("database_connected")
        except Exception as e:
            logger.error("database_connection_failed", error=str(e))
            app.state.db_connected = False
    else:
        app.state.db_connected = False
        logger.warning("database_url_not_configured")

    # Initialize NATS connection
    nats_url = settings.NATS_URL
    if nats_url:
        try:
            import nats

            app.state.nc = await nats.connect(nats_url)
            app.state.nats_connected = True
            logger.info("nats_connected", url=nats_url)
        except Exception as e:
            logger.error("nats_connection_failed", error=str(e))
            app.state.nats_connected = False
    else:
        app.state.nats_connected = False
        logger.warning("nats_url_not_configured")

    # Initialize Redis connection
    redis_url = settings.REDIS_URL
    if redis_url:
        try:
            import redis.asyncio as redis

            app.state.redis = redis.from_url(
                redis_url,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
            )
            await app.state.redis.ping()
            app.state.redis_connected = True
            logger.info("redis_connected")
        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            app.state.redis_connected = False
    else:
        app.state.redis_connected = False
        logger.warning("redis_url_not_configured")

    logger.info("service_started", service=settings.SERVICE_NAME)

    yield

    # Shutdown: Close all connections
    logger.info("shutting_down_service", service=settings.SERVICE_NAME)

    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
        logger.info("database_disconnected")

    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()
        logger.info("nats_disconnected")

    if hasattr(app.state, "redis") and app.state.redis:
        await app.state.redis.close()
        logger.info("redis_disconnected")

    logger.info("service_stopped", service=settings.SERVICE_NAME)


# Create FastAPI application
app = FastAPI(
    title="Supply Chain Service | خدمة سلسلة التوريد",
    description="""
## Supply Chain Service

Connects farmers to agricultural suppliers for auto-purchasing based on advisory recommendations.

### Features | الميزات

- **Product Catalog** | كتالوج المنتجات: Browse agricultural supplies
- **Supplier Management** | إدارة الموردين: Find and compare suppliers
- **Order Management** | إدارة الطلبات: Create and track orders
- **Auto-Purchase** | الشراء التلقائي: Automatic purchasing from recommendations
- **Delivery Tracking** | تتبع التوصيل: Real-time delivery tracking

### API Endpoints | نقاط الوصول

- `/api/v1/products` - Product catalog operations
- `/api/v1/suppliers` - Supplier management
- `/api/v1/orders` - Order management
- `/api/v1/auto-purchase` - Auto-purchase features

---

## خدمة سلسلة التوريد

تربط المزارعين بموردي المستلزمات الزراعية للشراء التلقائي بناءً على التوصيات الاستشارية.
    """,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Tenant-ID"],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next: Any) -> Any:
    """Add request ID to all requests."""
    import uuid

    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


# Include routers
app.include_router(products_router)
app.include_router(suppliers_router)
app.include_router(orders_router)
app.include_router(auto_purchase_router)


# Health endpoints
@app.get(
    "/healthz",
    tags=["health"],
    summary="Liveness Probe | فحص الحياة",
    description="Check if the service is alive. فحص ما إذا كانت الخدمة حية.",
)
@app.get("/health/live", tags=["health"], include_in_schema=False)
async def health() -> dict[str, str]:
    """Liveness probe endpoint."""
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "service_ar": settings.SERVICE_NAME_AR,
        "version": settings.VERSION,
    }


@app.get(
    "/readyz",
    tags=["health"],
    summary="Readiness Probe | فحص الجاهزية",
    description="Check if the service is ready to accept traffic. "
    "فحص ما إذا كانت الخدمة جاهزة لاستقبال الطلبات.",
)
@app.get("/health/ready", tags=["health"], include_in_schema=False)
async def readiness(request: Request) -> dict[str, Any]:
    """Readiness probe endpoint."""
    db_connected = getattr(request.app.state, "db_connected", False)
    nats_connected = getattr(request.app.state, "nats_connected", False)
    redis_connected = getattr(request.app.state, "redis_connected", False)

    # Service is ready if critical dependencies are available
    # For this service, we can operate without all connections in development
    is_ready = True  # Adjust based on requirements

    status = "ok" if is_ready else "degraded"

    return {
        "status": status,
        "status_ar": "جاهز" if is_ready else "متدهور",
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "dependencies": {
            "database": db_connected,
            "nats": nats_connected,
            "redis": redis_connected,
        },
    }


@app.get(
    "/health",
    tags=["health"],
    summary="Health Check | فحص الصحة",
    description="Combined health check endpoint. نقطة فحص الصحة الشاملة.",
)
async def combined_health(request: Request) -> dict[str, Any]:
    """Combined health check endpoint."""
    liveness = await health()
    readiness_result = await readiness(request)

    return {
        **liveness,
        "ready": readiness_result["status"] == "ok",
        "dependencies": readiness_result.get("dependencies", {}),
    }


# Root endpoint
@app.get(
    "/",
    tags=["root"],
    summary="Service Info | معلومات الخدمة",
)
async def root() -> dict[str, str]:
    """Root endpoint with service information."""
    return {
        "service": settings.SERVICE_NAME,
        "service_ar": settings.SERVICE_NAME_AR,
        "version": settings.VERSION,
        "description": "Supply Chain Service - Connects farmers to agricultural suppliers",
        "description_ar": "خدمة سلسلة التوريد - تربط المزارعين بموردي المستلزمات الزراعية",
        "docs": "/docs",
        "health": "/health",
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions."""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        method=request.method,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "error_ar": "خطأ داخلي في الخادم",
            "message": "An unexpected error occurred",
            "message_ar": "حدث خطأ غير متوقع",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
