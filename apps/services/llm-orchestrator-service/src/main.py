# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
SAHOOL LLM Orchestrator Service - Main API Service
خدمة تنسيق نماذج اللغة الكبيرة - الخدمة الرئيسية

This service intelligently orchestrates all SAHOOL AI agents,
routing user requests to appropriate agents and combining results.

Port: 8164
"""

# Service version - single source of truth
VERSION = "16.0.0"

import os
import sys
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.errors_py import add_request_id_middleware, setup_exception_handlers

from .agents.executor import AgentExecutor
from .api.endpoints import integrations as integrations_module
from .api.endpoints import router as orchestrator_router
from .api.endpoints import training as training_module
from .api.endpoints.integrations import router as integrations_router
from .api.endpoints.training import router as training_router
from .core.config import settings
from .integrations import CrewService, MLService, NLPService, SatelliteService
from .training import AGLTrainer, FeedbackCollector

# Configure structured logging (replaces stdlib logging init)
from shared.logging_config import setup_logging

setup_logging("llm-orchestrator-service")
logger = structlog.get_logger(__name__)

# OpenTelemetry tracing (must be called before FastAPI instrumentation)
from shared.observability.tracing import setup_tracing

_tracer = setup_tracing("llm-orchestrator-service")


# Optional imports
try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.info("Redis not available - running without cache")

try:
    import nats

    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False
    logger.info("NATS not available - running without events")

try:
    import asyncpg

    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    logger.info("asyncpg not available - running without database")

# Security headers middleware
try:
    from shared.middleware.security_headers import setup_security_headers

    SECURITY_HEADERS_AVAILABLE = True
except ImportError:
    SECURITY_HEADERS_AVAILABLE = False

    def setup_security_headers(app):
        pass


try:
    from shared.middleware.tenant_context import TenantContextMiddleware

    TENANT_MIDDLEWARE_AVAILABLE = True
except ImportError:
    TENANT_MIDDLEWARE_AVAILABLE = False

# Observability middleware (H-25)
try:
    from shared.observability.middleware import ObservabilityMiddleware

    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False

# Input sanitization middleware (H-25)
try:
    from shared.middleware.input_sanitizer import InputSanitizationMiddleware

    INPUT_SANITIZATION_AVAILABLE = True
except ImportError:
    INPUT_SANITIZATION_AVAILABLE = False

# Token revocation middleware (H-25)
try:
    from shared.auth.revocation_middleware import TokenRevocationMiddleware

    REVOCATION_AVAILABLE = True
except ImportError:
    REVOCATION_AVAILABLE = False

# Rate limiting middleware (H-05)
try:
    from shared.middleware.rate_limit import RateLimiter, rate_limit_middleware

    RATE_LIMIT_AVAILABLE = True
except ImportError:
    RATE_LIMIT_AVAILABLE = False


# Authentication imports
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    from fastapi import HTTPException as _HTTPException

    class User:  # type: ignore[no-redef]
        id: str = ""
        tenant_id: str | None = None

    async def get_current_user():
        """Placeholder when auth not available"""
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    مدير دورة حياة التطبيق.
    """
    # Startup
    logger.info(
        "llm_orchestrator_service_starting",
        version=VERSION,
        port=settings.port,
        environment=settings.environment,
    )

    # Initialize connection status flags
    app.state.redis_connected = False
    app.state.nats_connected = False
    app.state.db_connected = False
    app.state.redis_client = None
    app.state.nc = None
    app.state.db_pool = None
    app.state.executor = None

    # Initialize Redis for caching
    if REDIS_AVAILABLE and settings.redis_url:
        try:
            app.state.redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await app.state.redis_client.ping()
            app.state.redis_connected = True
            logger.info("redis_connected", url=settings.redis_url)
        except Exception as e:
            logger.warning("redis_connection_failed", error=str(e))
            app.state.redis_client = None
    else:
        logger.info("redis_not_configured")

    # Initialize NATS for events
    if NATS_AVAILABLE and settings.nats_url:
        try:
            app.state.nc = await nats.connect(settings.nats_url)
            app.state.nats_connected = True
            logger.info("nats_connected", url=settings.nats_url)
        except Exception as e:
            logger.warning("nats_connection_failed", error=str(e))
            app.state.nc = None
    else:
        logger.info("nats_not_configured")

    # Initialize PostgreSQL database connection
    if ASYNCPG_AVAILABLE and settings.database_url:
        try:
            app.state.db_pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=settings.db_pool_min_size,
                max_size=settings.db_pool_max_size,
                statement_cache_size=0,  # PgBouncer transaction mode
            )
            app.state.db_connected = True
            logger.info("database_connected")
        except Exception as e:
            logger.warning("database_connection_failed", error=str(e))
            app.state.db_pool = None
    else:
        logger.info("database_not_configured")

    # Initialize agent executor
    app.state.executor = AgentExecutor(
        redis_client=app.state.redis_client,
    )

    # Initialize Agent Lightning trainer
    app.state.trainer = AGLTrainer(
        enabled=os.getenv("AGL_ENABLED", "false").lower() == "true",
    )
    training_module.trainer = app.state.trainer

    # Initialize feedback collector
    app.state.feedback_collector = FeedbackCollector()
    training_module.feedback_collector = app.state.feedback_collector

    # Check AGL availability
    if app.state.trainer.enabled:
        await app.state.trainer.check_availability()

    # Initialize integration services (AraBERT, Sentinel, AgML, CrewAI)
    app.state.nlp_service = NLPService()
    app.state.satellite_service = SatelliteService()
    app.state.ml_service = MLService()
    app.state.crew_service = CrewService()

    # Initialize services asynchronously
    await app.state.nlp_service.initialize()
    await app.state.satellite_service.initialize()
    await app.state.ml_service.initialize()
    await app.state.crew_service.initialize()

    # Wire up integrations module
    integrations_module.nlp_service = app.state.nlp_service
    integrations_module.satellite_service = app.state.satellite_service
    integrations_module.ml_service = app.state.ml_service
    integrations_module.crew_service = app.state.crew_service

    logger.info(
        "llm_orchestrator_service_ready",
        version=VERSION,
        port=settings.port,
        redis=app.state.redis_connected,
        nats=app.state.nats_connected,
        database=app.state.db_connected,
        integrations=["nlp", "satellite", "ml", "crew"],
    )

    yield

    # Shutdown
    logger.info("llm_orchestrator_service_shutting_down")

    # Close executor
    if app.state.executor:
        await app.state.executor.close()

    # Close Redis connection
    if app.state.redis_client:
        await app.state.redis_client.close()
        logger.info("redis_disconnected")

    # Close NATS connection
    if app.state.nc:
        await app.state.nc.close()
        logger.info("nats_disconnected")

    # Close database pool
    if app.state.db_pool:
        await app.state.db_pool.close()
        logger.info("database_disconnected")

    logger.info("llm_orchestrator_service_stopped")


# Create FastAPI app
app = FastAPI(
    title="SAHOOL LLM Orchestrator Service",
    title_ar="خدمة تنسيق نماذج اللغة الكبيرة",
    description="""
    Intelligent orchestration of SAHOOL AI agents.

    **Features / الميزات:**
    - Intent classification (Arabic/English) | تصنيف النوايا (عربي/إنجليزي)
    - Parallel agent execution | تنفيذ الوكلاء بالتوازي
    - Response synthesis | تجميع الاستجابات
    - Automated action recommendations | توصيات الإجراءات التلقائية

    **Supported Intents / النوايا المدعومة:**
    - Crop disease diagnosis | تشخيص أمراض المحاصيل
    - Irrigation queries | استفسارات الري
    - Fertilizer advice | نصائح الأسمدة
    - Pest detection | كشف الآفات
    - Weather queries | استفسارات الطقس
    - Yield prediction | تنبؤ الإنتاجية
    - Field analysis | تحليل الحقول
    - Terrain analysis | تحليل التضاريس
    - And more... | والمزيد...
    """,
    version=VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Instrument FastAPI with OpenTelemetry
_tracer.instrument_fastapi(app)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# Add CORS middleware
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

# Observability middleware - distributed tracing (H-25)
if OBSERVABILITY_AVAILABLE:
    app.add_middleware(
        ObservabilityMiddleware,
        service_name="llm-orchestrator-service",
    )

# Tenant context middleware - عزل المستأجرين
if TENANT_MIDDLEWARE_AVAILABLE:
    app.add_middleware(TenantContextMiddleware)

# Input sanitization middleware (H-25)
if INPUT_SANITIZATION_AVAILABLE:
    app.add_middleware(InputSanitizationMiddleware)

# Rate limiting middleware (H-05)
if RATE_LIMIT_AVAILABLE:
    app.add_middleware(rate_limit_middleware)

# Token revocation middleware (H-25)
if REVOCATION_AVAILABLE:
    app.add_middleware(
        TokenRevocationMiddleware,
        exempt_paths=["/healthz", "/health", "/readyz", "/docs", "/redoc", "/openapi.json"],
    )

# Include routers
app.include_router(orchestrator_router)
app.include_router(training_router)
app.include_router(integrations_router)


# ============================================================================
# Health Check Endpoints
# ============================================================================


@app.get("/healthz", tags=["Health"])
def health():
    """
    Health check endpoint (liveness probe).
    نقطة فحص الصحة (فحص الحياة).
    """
    return {
        "status": "ok",
        "service": "llm-orchestrator-service",
        "version": VERSION,
    }


@app.get("/readyz", tags=["Health"])
def readiness():
    """
    Kubernetes readiness probe - is the service ready to accept traffic?
    فحص جاهزية Kubernetes - هل الخدمة جاهزة لاستقبال الحركة؟
    """
    redis_connected = getattr(app.state, "redis_connected", False)
    nats_connected = getattr(app.state, "nats_connected", False)
    db_connected = getattr(app.state, "db_connected", False)

    # Determine status strings
    if redis_connected:
        redis_status = "connected"
    elif settings.redis_url:
        redis_status = "disconnected"
    else:
        redis_status = "not_configured"

    if nats_connected:
        nats_status = "connected"
    elif settings.nats_url:
        nats_status = "disconnected"
    else:
        nats_status = "not_configured"

    if db_connected:
        db_status = "connected"
    elif settings.database_url:
        db_status = "disconnected"
    else:
        db_status = "not_configured"

    # Service is ready even without optional connections
    return {
        "status": "ready",
        "service": "llm-orchestrator-service",
        "version": VERSION,
        "checks": {
            "service": "ready",
            "redis": redis_status,
            "nats": nats_status,
            "database": db_status,
        },
    }


@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint with service information.
    نقطة الجذر مع معلومات الخدمة.
    """
    return {
        "service": "SAHOOL LLM Orchestrator",
        "service_ar": "خدمة تنسيق نماذج اللغة الكبيرة",
        "version": VERSION,
        "description_en": "Intelligent orchestration of SAHOOL AI agents",
        "description_ar": "تنسيق ذكي لوكلاء الذكاء الاصطناعي في سهول",
        "endpoints": {
            "orchestrate": "/api/v1/orchestrate",
            "orchestrate_image": "/api/v1/orchestrate/image",
            "plans": "/api/v1/orchestrate/plans",
            "execute_action": "/api/v1/orchestrate/execute-action",
            "agents": "/api/v1/agents",
            "agents_health": "/api/v1/agents/health",
            "training_start": "/api/v1/training/start",
            "training_jobs": "/api/v1/training/jobs",
            "feedback": "/api/v1/training/feedback",
            "feedback_statistics": "/api/v1/training/feedback/statistics",
            "nlp_process": "/api/v1/integrations/nlp/process",
            "satellite_ndvi": "/api/v1/integrations/satellite/ndvi",
            "satellite_crop_health": "/api/v1/integrations/satellite/crop-health",
            "ml_datasets": "/api/v1/integrations/ml/datasets",
            "crew_query": "/api/v1/integrations/crew/query",
            "crew_agents": "/api/v1/integrations/crew/agents",
            "health": "/healthz",
            "readiness": "/readyz",
            "docs": "/docs",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=settings.is_development,
    )
