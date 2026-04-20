# LINT-OPT-OUT: logging  # copilot-api uses structlog with custom JSON processors (see below)
"""
SAHOOL Copilot API - Main Application
التطبيق الرئيسي لـ Copilot API

Unified AI-powered assistant for SAHOOL platform operations.
Supports multiple LLM providers with offline-first architecture.

Features:
- Multi-provider LLM support (Ollama, Claude, OpenAI, Gemini, DeepSeek)
- RAG with Qdrant vector search
- Tool guardrails for security
- Agent routing for specialized tasks
- Bilingual support (Arabic/English)

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import httpx
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.middleware.tenant_context import TenantContextMiddleware

from .api.v1 import chat_router, health_router, rag_router, tools_router
from .api.v1.encyclopedia import router as encyclopedia_router
from .api.v1.services_rec import router as services_rec_router
from .core.config import Settings, get_settings
from .db import close_db, init_db
from .rag import get_rag_service

# Import security middleware - SecurityHeadersMiddleware (H-01)
try:
    from shared.middleware.security_headers import SecurityHeadersMiddleware, setup_security_headers

    HAS_SECURITY_HEADERS = True
except ImportError:
    HAS_SECURITY_HEADERS = False

# Import Observability middleware (H-02)
try:
    from shared.observability.middleware import ObservabilityMiddleware

    HAS_OBSERVABILITY = True
except ImportError:
    HAS_OBSERVABILITY = False

# Import InputSanitizationMiddleware (H-19)
try:
    from shared.middleware.input_sanitizer import InputSanitizationMiddleware

    HAS_INPUT_SANITIZATION = True
except ImportError:
    HAS_INPUT_SANITIZATION = False

# Import TokenRevocationMiddleware (C-08)
try:
    from shared.auth.revocation_middleware import TokenRevocationMiddleware

    HAS_REVOCATION = True
except ImportError:
    HAS_REVOCATION = False

# Import shared RateLimiter (H-04 - replaces in-memory defaultdict)
try:
    from shared.middleware.rate_limit import RateLimiter, rate_limit_middleware

    HAS_RATE_LIMITER = True
except ImportError:
    HAS_RATE_LIMITER = False

# Import AI Audit Logger for comprehensive logging
try:
    from shared.ai.audit import AIAuditLogger, get_audit_logger

    HAS_AUDIT = True
except ImportError:
    HAS_AUDIT = False
    AIAuditLogger = None

# Import FixOps integration
try:
    from tools.fixops.orchestrator import FixOpsConfig, FixOpsOrchestrator

    HAS_FIXOPS = True
except ImportError:
    HAS_FIXOPS = False
    FixOpsOrchestrator = None

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
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

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    معالج دورة حياة التطبيق
    """
    settings = get_settings()

    # Validate JWT configuration at startup (not at import time)
    from .api.deps import validate_jwt_config

    validate_jwt_config(settings.environment)

    logger.info(
        "Starting Copilot API",
        version="16.0.0",
        mode=settings.copilot_mode,
        environment=settings.environment,
    )

    # Initialize RAG service
    try:
        rag_service = get_rag_service()
        await rag_service.initialize()
        logger.info("RAG service initialized")
    except Exception as e:
        logger.warning("RAG service initialization failed", error=str(e))

    # Initialize AI Audit Logger
    app.state.audit_logger = None
    if HAS_AUDIT:
        try:
            app.state.audit_logger = get_audit_logger()
            logger.info("AI Audit Logger initialized")
        except Exception as e:
            logger.warning("AI Audit Logger initialization failed", error=str(e))

    # Initialize FixOps Orchestrator
    app.state.fixops = None
    if HAS_FIXOPS:
        try:
            app.state.fixops = FixOpsOrchestrator(
                FixOpsConfig(
                    dry_run=settings.environment != "production",
                )
            )
            logger.info("FixOps Orchestrator initialized")
        except Exception as e:
            logger.warning("FixOps initialization failed", error=str(e))

    # Initialize Chat History Database
    # تهيئة قاعدة بيانات سجل المحادثات
    app.state.chat_db_ready = False
    try:
        db_ok = await init_db(settings.database_url)
        app.state.chat_db_ready = db_ok
        if db_ok:
            logger.info("Chat history database initialized")
        else:
            logger.warning("Chat history database not available, persistence disabled")
    except Exception as e:
        logger.warning("Chat history database initialization failed", error=str(e))

    # Initialize NATS connection
    # تهيئة اتصال NATS
    app.state.nc = None
    if settings.nats_url:
        try:
            import nats

            app.state.nc = await nats.connect(
                settings.nats_url,
                connect_timeout=5,
                max_reconnect_attempts=3,
            )
            import re

            safe_url = re.sub(r"://[^@]+@", "://***@", settings.nats_url) if settings.nats_url else ""
            logger.info("NATS connected", url=safe_url)
        except Exception as e:
            logger.warning("NATS connection failed, events disabled", error=str(e))

    # Initialize shared HTTP client for service-to-service calls
    # تهيئة عميل HTTP مشترك للاتصالات بين الخدمات
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0, connect=5.0),
        limits=httpx.Limits(max_connections=50, max_keepalive_connections=10),
    )

    # Store settings in app state
    app.state.settings = settings

    yield

    # Cleanup: close shared HTTP client
    # تنظيف: إغلاق عميل HTTP المشترك
    if app.state.http_client:
        await app.state.http_client.aclose()

    # Cleanup: close NATS connection
    # تنظيف: إغلاق اتصال NATS
    if app.state.nc:
        try:
            await app.state.nc.close()
        except Exception as e:
            logger.warning("Error closing NATS connection", error=str(e))

    # Cleanup: close chat history database pool
    # تنظيف: إغلاق تجمع اتصالات قاعدة بيانات سجل المحادثات
    await close_db()

    logger.info("Shutting down Copilot API")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    إنشاء وتكوين تطبيق FastAPI
    """
    settings = get_settings()

    app = FastAPI(
        title="SAHOOL Copilot API",
        description="""
        مساعد SAHOOL الذكي - Copilot API

        Unified AI-powered assistant for SAHOOL platform.
        Supports code analysis, agricultural advisory, and operations management.

        ## Features
        - 🤖 Multi-provider LLM (Ollama, Claude, OpenAI, Gemini, DeepSeek)
        - 📚 RAG with Qdrant vector search
        - 🔒 Tool guardrails for security
        - 🌍 Bilingual (Arabic/English)
        - 🔌 Offline-first architecture
        """,
        version="16.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Setup unified error handling (includes request ID middleware)
    _has_shared_errors = False
    try:
        from shared.errors_py import add_request_id_middleware as _add_req_id
        from shared.errors_py import setup_exception_handlers as _setup_exc

        _setup_exc(app)
        _add_req_id(app)
        _has_shared_errors = True
    except ImportError:
        pass

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID", "X-Tenant-ID"],
    )

    # Observability middleware - distributed tracing (H-02)
    if HAS_OBSERVABILITY:
        app.add_middleware(
            ObservabilityMiddleware,
            service_name="copilot-api",
        )

    # Tenant context middleware
    app.add_middleware(TenantContextMiddleware)

    # Input sanitization middleware - XSS/injection protection (H-19)
    if HAS_INPUT_SANITIZATION:
        app.add_middleware(InputSanitizationMiddleware)

    # Rate limiting middleware - shared, distributed (H-04)
    # rate_limit_middleware is a function (request, call_next), not a class — use middleware() not add_middleware()
    if HAS_RATE_LIMITER:
        app.middleware("http")(rate_limit_middleware)

    # Token revocation middleware - blocks revoked JWT tokens (C-08)
    if HAS_REVOCATION:
        app.add_middleware(
            TokenRevocationMiddleware,
            exempt_paths=["/healthz", "/health", "/readyz", "/docs", "/redoc", "/openapi.json", "/", "/info"],
        )

    # Security headers middleware - X-Frame-Options, CSP, etc. (H-01)
    if HAS_SECURITY_HEADERS:
        setup_security_headers(app)

    # Fallback request ID middleware (only if shared.errors_py not available)
    if not _has_shared_errors:

        @app.middleware("http")
        async def add_request_id(request: Request, call_next):
            import uuid

            request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
            request.state.request_id = request_id
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

    # Exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(
            "Unhandled exception",
            error=str(exc),
            path=request.url.path,
            request_id=getattr(request.state, "request_id", "unknown"),
        )
        # Only expose exception details in development debug mode, never in production/staging
        show_detail = settings.debug and settings.environment in ("development", "test")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "error_ar": "خطأ داخلي في الخادم",
                "detail": str(exc) if show_detail else None,
            },
        )

    # Health endpoints (registered first so they take precedence over health_router aliases)
    @app.get("/healthz", tags=["Health"])
    async def healthz():
        return {"status": "ok", "service": "copilot-api", "version": "16.0.0"}

    @app.get("/readyz", tags=["Health"])
    async def readyz():
        return {"status": "ok", "service": "copilot-api", "version": "16.0.0"}

    # Include routers (health_router provides /health/live, /health/ready with full status detail)
    app.include_router(health_router)
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(tools_router, prefix="/api/v1")
    app.include_router(rag_router, prefix="/api/v1")
    app.include_router(encyclopedia_router, prefix="/api/v1")
    app.include_router(services_rec_router, prefix="/api/v1")

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "service": "copilot-api",
            "name": "SAHOOL Copilot API",
            "name_ar": "واجهة برمجة Copilot لسهول",
            "version": "16.0.0",
            "status": "running",
            "docs": "/docs",
            "health": "/healthz",
            "readiness": "/readyz",
        }

    # Info endpoint
    @app.get("/info")
    async def info(request: Request):
        settings = get_settings()
        return {
            "service": "copilot-api",
            "version": "16.0.0",
            "mode": settings.copilot_mode,
            "environment": settings.environment,
            "features": {
                "rag": True,
                "guardrails": True,
                "multi_llm": True,
                "offline_first": True,
                "bilingual": True,
                "audit_logging": getattr(request.app.state, "audit_logger", None) is not None,
                "fixops": getattr(request.app.state, "fixops", None) is not None,
            },
            "integrations": {
                "ai_audit": HAS_AUDIT,
                "fixops": HAS_FIXOPS,
                "auto_fix_engine": HAS_FIXOPS,
            },
            "llm_providers": _get_available_providers(settings),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    return app


def _get_available_providers(settings: Settings) -> list[dict]:
    """Get list of available LLM providers"""
    providers = []

    # Ollama (primary, offline)
    providers.append(
        {
            "name": "Ollama",
            "type": "local",
            "model": settings.ollama_model,
            "priority": 1,
            "available": True,  # Would check connectivity
        }
    )

    # Claude (if API key available)
    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append(
            {
                "name": "Claude",
                "type": "cloud",
                "model": "claude-3-5-sonnet",
                "priority": 2,
                "available": settings.enable_external,
            }
        )

    # OpenAI (if configured)
    if settings.external_llm_api_key and "openai" in (settings.external_llm_base_url or ""):
        providers.append(
            {
                "name": "OpenAI",
                "type": "cloud",
                "model": settings.external_llm_model,
                "priority": 3,
                "available": settings.enable_external,
            }
        )

    # Gemini (if API key available)
    if os.getenv("GOOGLE_API_KEY"):
        providers.append(
            {
                "name": "Gemini",
                "type": "cloud",
                "model": "gemini-1.5-pro",
                "priority": 4,
                "available": settings.enable_external,
            }
        )

    # DeepSeek (if configured)
    if os.getenv("DEEPSEEK_API_KEY"):
        providers.append(
            {
                "name": "DeepSeek",
                "type": "cloud",
                "model": "deepseek-coder",
                "priority": 5,
                "available": settings.enable_external,
            }
        )

    return providers


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=not settings.is_production,
        workers=settings.workers if settings.is_production else 1,
        log_level=settings.log_level.lower(),
    )
