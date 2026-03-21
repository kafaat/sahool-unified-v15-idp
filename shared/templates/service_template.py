"""
Service Template with Comprehensive Observability & Security
قالب الخدمة مع المراقبة والأمان الشاملين

This template demonstrates best practices for integrating:
1. Health checks (liveness, readiness, startup)
2. Prometheus metrics
3. OpenTelemetry tracing
4. Structured logging with request IDs
5. Rate limiting
6. Secrets management
7. Request context propagation

Use this as a reference when enhancing existing services.
"""

# Observability imports
# NOTE: In production, install shared modules as a package instead of using sys.path
# This is a temporary solution for the template example
import sys
import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, "../../../../shared")

from middleware.rate_limit import RateLimiter, TierConfig

# Security imports
from security.config import (
    get_config,
    get_cors_origins,
    get_environment,
    get_log_level,
    is_production,
)

from observability import (
    HealthChecker,
    MetricsCollector,
    clear_request_context,
    create_health_router,
    create_metrics_router,
    get_trace_context,
    instrument_fastapi,
    set_request_context,
    setup_logging,
    setup_opentelemetry,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Service Configuration
# ═══════════════════════════════════════════════════════════════════════════════

SERVICE_NAME = "example-service"
SERVICE_VERSION = "1.0.0"
SERVICE_PORT = int(get_config("SERVICE_PORT", default="8000", cast_type=int))


# ═══════════════════════════════════════════════════════════════════════════════
# Initialize Components
# ═══════════════════════════════════════════════════════════════════════════════

# Logging
logger = setup_logging(
    SERVICE_NAME,
    level=get_log_level(),
    json_output=is_production(),
)

# Metrics
metrics = MetricsCollector(SERVICE_NAME)
metrics.set_info(
    version=SERVICE_VERSION,
    environment=get_environment(),
)

# Health Checker
health_checker = HealthChecker(SERVICE_NAME, SERVICE_VERSION)

# Rate Limiter
rate_limiter = RateLimiter(tier_config=TierConfig())


# ═══════════════════════════════════════════════════════════════════════════════
# Health Check Functions
# ═══════════════════════════════════════════════════════════════════════════════

# Example: Add health checks for dependencies
# Uncomment and customize based on your service's dependencies

# async def check_database_connection():
#     """Check if database is accessible"""
#     try:
#         # Test database connection
#         # await db.execute_query("SELECT 1")
#         return {"status": "healthy", "message": "Database OK"}
#     except Exception as e:
#         return {"status": "unhealthy", "message": f"Database error: {str(e)}"}

# async def check_redis_connection():
#     """Check if Redis is accessible"""
#     try:
#         # Test Redis connection
#         # await redis.ping()
#         return {"status": "healthy", "message": "Redis OK"}
#     except Exception as e:
#         return {"status": "unhealthy", "message": f"Redis error: {str(e)}"}


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI Lifespan
# ═══════════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown.
    مدير السياق لبدء التشغيل والإغلاق.
    """
    # Startup
    logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info(f"Environment: {get_environment()}")

    # Register health checks
    # health_checker.add_readiness_check("database", check_database_connection)
    # health_checker.add_readiness_check("redis", check_redis_connection)

    # Setup OpenTelemetry if configured
    otel_endpoint = get_config("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otel_endpoint:
        tracer = setup_opentelemetry(SERVICE_NAME, SERVICE_VERSION, otel_endpoint)
        if tracer:
            logger.info(f"OpenTelemetry configured with endpoint: {otel_endpoint}")

    logger.info(f"{SERVICE_NAME} started successfully")

    yield

    # Shutdown
    logger.info(f"Shutting down {SERVICE_NAME}")


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI Application
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title=SERVICE_NAME,
    description=f"{SERVICE_NAME} with comprehensive observability",
    version=SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if not is_production() else None,  # Disable docs in production
    redoc_url="/redoc" if not is_production() else None,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Middleware Configuration
# ═══════════════════════════════════════════════════════════════════════════════

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID and Context Middleware
@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """
    Add request ID and propagate context.
    إضافة معرف الطلب ونشر السياق.
    """
    # Generate or extract request ID
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    # Extract trace context if available
    trace_ctx = get_trace_context()

    # Set logging context
    set_request_context(
        request_id=request_id,
        tenant_id=request.headers.get("X-Tenant-ID"),
        user_id=request.headers.get("X-User-ID"),
    )

    # Log request
    logger.info(
        f"{request.method} {request.url.path}",
        request_id=request_id,
        trace_id=trace_ctx.get("trace_id"),
    )

    # Track active connections
    metrics.increment_active_connections()

    # Process request
    import time

    start_time = time.time()

    try:
        response = await call_next(request)

        # Record metrics
        duration = time.time() - start_time
        metrics.record_request(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            duration=duration,
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        # Add trace context to response headers
        if trace_ctx:
            response.headers["X-Trace-ID"] = trace_ctx.get("trace_id", "")

        return response

    except Exception as e:
        # Record error
        metrics.record_error(type(e).__name__)
        logger.error(f"Request failed: {str(e)}")
        raise

    finally:
        # Decrement active connections
        metrics.decrement_active_connections()

        # Clear logging context
        clear_request_context()


# ═══════════════════════════════════════════════════════════════════════════════
# Include Observability Routers
# ═══════════════════════════════════════════════════════════════════════════════

# Health endpoints
app.include_router(create_health_router(health_checker))

# Metrics endpoint
app.include_router(create_metrics_router(metrics.registry))


# ═══════════════════════════════════════════════════════════════════════════════
# Business Logic Routes
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "environment": get_environment(),
    }


@app.get("/api/example")
async def example_endpoint(request: Request):
    """
    Example API endpoint with rate limiting.
    نقطة API مثال مع تحديد المعدل.
    """
    # Apply rate limiting
    client_ip = request.client.host
    tier = "standard"  # Could be determined by API key or user subscription

    if not rate_limiter.check_rate_limit(client_ip, tier):
        logger.warning(f"Rate limit exceeded for {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
        )

    # Business logic here
    logger.info("Processing example request")

    return {
        "message": "Example response",
        "request_id": request.headers.get("X-Request-ID"),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Instrument FastAPI with OpenTelemetry
    otel_endpoint = get_config("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otel_endpoint:
        instrument_fastapi(app, SERVICE_NAME)

    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=SERVICE_PORT,
        log_level=get_log_level().lower(),
        access_log=not is_production(),  # Disable access log in production (use structured logging)
    )
