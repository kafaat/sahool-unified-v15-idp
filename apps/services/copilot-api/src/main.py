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
from datetime import UTC, datetime, timezone

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from shared.middleware.tenant_context import TenantContextMiddleware

from .api.v1 import chat_router, health_router, rag_router, tools_router
from .core.config import Settings, get_settings
from .db import init_db, close_db
from .rag import get_rag_service

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

    # Store settings in app state
    app.state.settings = settings

    yield

    # Cleanup: close chat history database pool
    # تنظيف: إغلاق تجمع اتصالات قاعدة بيانات سجل المحادثات
    await close_db()

    # Cleanup
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

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(TenantContextMiddleware)

    # Request ID middleware
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
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "error_ar": "خطأ داخلي في الخادم",
                "detail": str(exc) if settings.debug else None,
            },
        )

    # Include routers
    app.include_router(health_router)
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(tools_router, prefix="/api/v1")
    app.include_router(rag_router, prefix="/api/v1")

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
