# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
SAHOOL WhatsApp Bot Service - Main API Service
خدمة روبوت واتساب - الخدمة الرئيسية

This service handles WhatsApp messaging for SAHOOL farmers using
the WhatsApp Business API (Cloud API).

Features:
- Webhook for receiving WhatsApp messages
- Forward farmer queries to llm-orchestrator-service
- Support Arabic and English
- Handle images for crop disease detection
- Interactive menus for common actions
- Session management for context

Port: 8240
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

from .api.endpoints import router as webhook_router
from .core.config import settings
from .handlers import MessageHandler
from .utils import SessionManager, WhatsAppClient

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger(__name__)


# Optional imports
try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.info("Redis not available - running without session management")

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
        "whatsapp_bot_service_starting",
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

    # Initialize Redis for session management
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
            )
            app.state.db_connected = True
            logger.info("database_connected")
        except Exception as e:
            logger.warning("database_connection_failed", error=str(e))
            app.state.db_pool = None
    else:
        logger.info("database_not_configured")

    # Initialize session manager
    app.state.session_manager = SessionManager(
        redis_client=app.state.redis_client,
        session_ttl=settings.session_ttl,
        context_limit=settings.context_messages_limit,
    )

    # Initialize WhatsApp client
    app.state.whatsapp_client = WhatsAppClient(
        access_token=settings.whatsapp_token,
        phone_number_id=settings.whatsapp_phone_id,
        api_version=settings.whatsapp_api_version,
    )

    # Initialize message handler
    app.state.message_handler = MessageHandler(
        whatsapp_client=app.state.whatsapp_client,
        session_manager=app.state.session_manager,
        llm_orchestrator_url=settings.llm_orchestrator_url,
        vision_service_url=settings.vision_service_url,
        default_language=settings.default_language,
    )

    # Check WhatsApp configuration
    if settings.whatsapp_configured:
        logger.info(
            "whatsapp_configured",
            phone_id=settings.whatsapp_phone_id[:8] + "...",
        )
    else:
        logger.warning(
            "whatsapp_not_configured",
            message="Set WHATSAPP_TOKEN and WHATSAPP_PHONE_ID environment variables",
        )

    logger.info(
        "whatsapp_bot_service_ready",
        version=VERSION,
        port=settings.port,
        redis=app.state.redis_connected,
        nats=app.state.nats_connected,
        database=app.state.db_connected,
        whatsapp=settings.whatsapp_configured,
    )

    yield

    # Shutdown
    logger.info("whatsapp_bot_service_shutting_down")

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

    logger.info("whatsapp_bot_service_stopped")


# Create FastAPI app
app = FastAPI(
    title="SAHOOL WhatsApp Bot Service",
    title_ar="خدمة روبوت واتساب سهول",
    description="""
    WhatsApp messaging service for SAHOOL farmers.
    خدمة رسائل واتساب لمزارعي سهول.

    **Features / الميزات:**
    - Receive and respond to farmer messages | استقبال والرد على رسائل المزارعين
    - Forward queries to AI advisory | إحالة الاستفسارات إلى المستشار الذكي
    - Handle crop images for disease detection | معالجة صور المحاصيل لكشف الأمراض
    - Interactive menus and buttons | قوائم وأزرار تفاعلية
    - Bilingual support (Arabic/English) | دعم ثنائي اللغة (عربي/إنجليزي)
    - Session context management | إدارة سياق الجلسات

    **Supported Message Types / أنواع الرسائل المدعومة:**
    - Text messages | رسائل نصية
    - Image messages | رسائل صور
    - Location messages | رسائل مواقع
    - Interactive button responses | ردود الأزرار التفاعلية
    """,
    version=VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

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

# Tenant context middleware - عزل المستأجرين
# /webhook is exempt: Meta sends webhooks externally without tenant headers
# مسار /webhook معفى: Meta ترسل webhooks خارجياً بدون ترويسة المستأجر
if TENANT_MIDDLEWARE_AVAILABLE:
    app.add_middleware(
        TenantContextMiddleware,
        exempt_paths=[
            "/healthz",
            "/readyz",
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/webhook",
            "/",
        ],
    )

# Include routers
app.include_router(webhook_router)


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
        "service": "whatsapp-bot-service",
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

    # Check WhatsApp configuration
    whatsapp_status = "configured" if settings.whatsapp_configured else "not_configured"

    # Service is ready even without optional connections
    return {
        "status": "ready",
        "service": "whatsapp-bot-service",
        "version": VERSION,
        "checks": {
            "service": "ready",
            "whatsapp": whatsapp_status,
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
        "service": "SAHOOL WhatsApp Bot",
        "service_ar": "روبوت واتساب سهول",
        "version": VERSION,
        "description_en": "WhatsApp messaging service for SAHOOL farmers",
        "description_ar": "خدمة رسائل واتساب لمزارعي سهول",
        "endpoints": {
            "webhook_verify": "GET /webhook",
            "webhook_receive": "POST /webhook",
            "send_message": "POST /api/v1/send",
            "send_template": "POST /api/v1/send-template",
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
