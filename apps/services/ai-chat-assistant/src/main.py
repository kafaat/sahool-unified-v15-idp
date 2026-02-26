"""
AI Chat Assistant - Main FastAPI application.
مساعد الشات الذكي - تطبيق FastAPI الرئيسي.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from shared.middleware.tenant_context import TenantContextMiddleware

from src.config import settings
from src.cache import cache_manager
from src.llm_client import llm_client
from src.events import event_handler

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - startup and shutdown logic.
    """
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME} v1.0.0...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Port: {settings.PORT}")

    try:
        # Initialize Redis cache
        logger.info("Connecting to Redis...")
        await cache_manager.connect()

        # Initialize LLM orchestrator client
        logger.info("Connecting to LLM Orchestrator...")
        await llm_client.connect()

        # Check orchestrator health
        is_healthy = await llm_client.health_check()
        if not is_healthy:
            logger.warning("LLM Orchestrator health check failed - service may not be available")

        # Initialize NATS event handler
        logger.info("Connecting to NATS...")
        await event_handler.connect()

        logger.info("✅ All services connected successfully")
        logger.info(f"🚀 {settings.SERVICE_NAME} is ready to serve!")

    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME}...")

    try:
        await event_handler.close()
        await llm_client.close()
        await cache_manager.close()
        logger.info("✅ All services closed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title="AI Chat Assistant",
    description="Lightweight AI assistant for SAHOOL chat services | مساعد الشات الذكي لخدمات سهول",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(TenantContextMiddleware)


# Health endpoints
@app.get("/healthz")
@app.get("/health/live")
async def health_check():
    """
    Liveness probe - checks if the service is running.
    مسبار الحياة - يتحقق من تشغيل الخدمة.
    """
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/readyz")
@app.get("/health/ready")
async def readiness_check():
    """
    Readiness probe - checks if the service is ready to serve requests.
    مسبار الجاهزية - يتحقق من جاهزية الخدمة لخدمة الطلبات.
    """
    # Check connections
    redis_connected = cache_manager.redis_client is not None
    nats_connected = await event_handler.is_connected()
    llm_healthy = await llm_client.health_check()

    is_ready = redis_connected and nats_connected and llm_healthy

    status_code = 200 if is_ready else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "service": settings.SERVICE_NAME,
            "checks": {
                "redis": "connected" if redis_connected else "disconnected",
                "nats": "connected" if nats_connected else "disconnected",
                "llm_orchestrator": "healthy" if llm_healthy else "unhealthy",
            },
        },
    )


@app.get("/health")
async def combined_health():
    """
    Combined health check.
    فحص الصحة المجمع.
    """
    # Get cache stats
    cache_stats = await cache_manager.get_stats()

    # Check connections
    redis_connected = cache_manager.redis_client is not None
    nats_connected = await event_handler.is_connected()
    llm_healthy = await llm_client.health_check()

    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "connections": {
            "redis": "connected" if redis_connected else "disconnected",
            "nats": "connected" if nats_connected else "disconnected",
            "llm_orchestrator": "healthy" if llm_healthy else "unhealthy",
        },
        "cache": cache_stats,
        "config": {
            "cache_enabled": settings.CACHE_ENABLED,
            "rate_limit_enabled": settings.RATE_LIMIT_ENABLED,
            "min_confidence": settings.MIN_CONFIDENCE_THRESHOLD,
        },
    }


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.
    نقطة نهاية مقاييس Prometheus.
    """
    # Get cache stats
    cache_stats = await cache_manager.get_stats()

    # Format as Prometheus metrics
    metrics_lines = [
        "# HELP ai_chat_cache_entries Total number of cached entries",
        "# TYPE ai_chat_cache_entries gauge",
        f"ai_chat_cache_entries {cache_stats.get('total_entries', 0)}",
        "",
        "# HELP ai_chat_cache_hits Total number of cache hits",
        "# TYPE ai_chat_cache_hits counter",
        f"ai_chat_cache_hits {cache_stats.get('total_hits', 0)}",
        "",
        "# HELP ai_chat_cache_hit_rate Average cache hit rate",
        "# TYPE ai_chat_cache_hit_rate gauge",
        f"ai_chat_cache_hit_rate {cache_stats.get('avg_hits_per_entry', 0)}",
    ]

    return "\n".join(metrics_lines)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with service information.
    """
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "description": "AI Chat Assistant for SAHOOL | مساعد الشات الذكي لسهول",
        "endpoints": {
            "health": {
                "liveness": "/healthz",
                "readiness": "/readyz",
                "combined": "/health",
            },
            "metrics": "/metrics",
        },
        "documentation": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )
