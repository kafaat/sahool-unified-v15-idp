"""
SAHOOL Agent Registry Service - Main Application
خدمة سجل وكلاء سهول - التطبيق الرئيسي

A2A Protocol-compliant agent registry service with FastAPI and Redis.
خدمة سجل وكلاء متوافقة مع بروتوكول A2A باستخدام FastAPI و Redis.
"""

import os
import sys
from contextlib import asynccontextmanager

import structlog
from fastapi import Depends, FastAPI, Header, HTTPException, status

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.middleware import (
    RequestLoggingMiddleware,
    TenantContextMiddleware,
    setup_cors,
)
from shared.observability.middleware import ObservabilityMiddleware

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import settings
from .storage import InMemoryStorage, RedisStorage

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from registry.agent_card import AgentCard
from registry.registry import AgentRegistry, RegistryConfig
from shared.errors_py import setup_exception_handlers, add_request_id_middleware

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()


# Request/Response Models
class RegisterAgentRequest(BaseModel):
    """Request to register an agent / طلب لتسجيل وكيل"""

    agent_card: AgentCard = Field(..., description="Agent card to register")


class DiscoverByTagsRequest(BaseModel):
    """Request to discover agents by tags / طلب لاكتشاف الوكلاء حسب العلامات"""

    tags: list[str] = Field(..., description="Tags to search for")


# Global state
app_state = {}


# API Key authentication
async def verify_api_key(x_api_key: str | None = Header(None)):
    """
    Verify API key for protected endpoints
    التحقق من مفتاح API لنقاط النهاية المحمية
    """
    if settings.require_api_key:
        if not x_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required"
            )
        if settings.api_key and x_api_key != settings.api_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key"
            )
    return x_api_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    مدير دورة حياة التطبيق
    """
    # Startup
    logger.info("agent_registry_service_starting", version="1.0.0")

    try:
        # Initialize storage
        if settings.redis_host and settings.environment == "production":
            # Use Redis in production
            redis_url = f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
            if settings.redis_password:
                redis_url = f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"

            storage = RedisStorage(
                redis_url=redis_url,
                key_prefix=settings.redis_prefix,
                ttl_seconds=settings.agent_ttl_seconds,
            )
            await storage.connect()
            logger.info("using_redis_storage")
        else:
            # Use in-memory storage for development
            storage = InMemoryStorage()
            logger.info("using_in_memory_storage")

        app_state["storage"] = storage

        # Initialize registry
        registry_config = RegistryConfig(
            health_check_interval_seconds=settings.health_check_interval_seconds,
            health_check_timeout_seconds=settings.health_check_timeout_seconds,
            enable_auto_discovery=settings.enable_auto_discovery,
            ttl_seconds=settings.agent_ttl_seconds,
        )

        registry = AgentRegistry(config=registry_config)
        await registry.start()

        app_state["registry"] = registry

        logger.info("agent_registry_service_started_successfully")

    except Exception as e:
        logger.error("agent_registry_service_startup_failed", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("agent_registry_service_shutting_down")

    registry = app_state.get("registry")
    if registry:
        await registry.stop()

    storage = app_state.get("storage")
    if storage and hasattr(storage, "close"):
        await storage.close()

    app_state.clear()


# Create FastAPI app
app = FastAPI(
    title="SAHOOL Agent Registry Service",
    description="A2A Protocol-compliant agent registry for SAHOOL platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# Add CORS middleware
cors_origins = settings.cors_origins.split(",") if settings.cors_origins else []
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Authorization",
        "Content-Type",
        "X-API-Key",
        "X-Request-ID",
    ],
)


# ============================================================================
# Health & Status Endpoints
# ============================================================================


@app.get("/healthz", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    نقطة فحص الصحة
    """
    storage = app_state.get("storage")
    storage_status = "healthy"

    # Check Redis connection if using Redis
    if isinstance(storage, RedisStorage):
        try:
            await storage._redis.ping()
        except Exception:
            storage_status = "unhealthy"

    return {
        "status": "healthy" if storage_status == "healthy" else "degraded",
        "service": settings.service_name,
        "version": "1.0.0",
        "storage": storage_status,
    }


@app.get("/v1/registry/stats", tags=["Registry"])
async def get_registry_stats():
    """
    Get registry statistics
    الحصول على إحصائيات السجل
    """
    registry = app_state.get("registry")
    if not registry:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Registry not initialized",
        )

    stats = registry.get_registry_stats()

    return {
        "status": "success",
        "stats": stats,
    }


# ============================================================================
# Agent Management Endpoints
# ============================================================================


@app.post(
    "/v1/registry/agents", tags=["Agents"], dependencies=[Depends(verify_api_key)]
)
async def register_agent(request: RegisterAgentRequest):
    """
    Register a new agent
    تسجيل وكيل جديد

    Requires API key authentication.
    يتطلب مصادقة مفتاح API.
    """
    try:
        registry = app_state.get("registry")
        storage = app_state.get("storage")

        if not registry or not storage:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not initialized",
            )

        # Register in registry (for indexing and discovery)
        await registry.register_agent(request.agent_card)

        # Persist to storage
        await storage.save_agent(request.agent_card)

        logger.info(
            "agent_registered_successfully",
            agent_id=request.agent_card.agent_id,
            version=request.agent_card.version,
        )

        return {
            "status": "success",
            "message": "Agent registered successfully",
            "agent_id": request.agent_card.agent_id,
        }

    except Exception as e:
        logger.error("register_agent_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@app.get("/v1/registry/agents/{agent_id}", tags=["Agents"])
async def get_agent(agent_id: str):
    """
    Get agent card by ID
    الحصول على بطاقة الوكيل بواسطة المعرف
    """
    try:
        storage = app_state.get("storage")
        if not storage:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not initialized",
            )

        agent_card = await storage.get_agent(agent_id)

        if not agent_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent not found: {agent_id}",
            )

        return agent_card.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_agent_failed", agent_id=agent_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@app.get("/v1/registry/agents", tags=["Agents"])
async def list_agents(
    status: str | None = None,
    category: str | None = None,
):
    """
    List all agents with optional filters
    قائمة بجميع الوكلاء مع مرشحات اختيارية
    """
    try:
        storage = app_state.get("storage")
        if not storage:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not initialized",
            )

        # Get all agents from storage
        all_agents = await storage.list_agents()

        # Apply filters
        agents = all_agents
        if status:
            agents = [a for a in agents if a.status == status]
        if category:
            agents = [a for a in agents if a.metadata.category == category]

        return {
            "status": "success",
            "agents": [a.to_dict() for a in agents],
            "total": len(agents),
        }

    except Exception as e:
        logger.error("list_agents_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@app.delete(
    "/v1/registry/agents/{agent_id}",
    tags=["Agents"],
    dependencies=[Depends(verify_api_key)],
)
async def deregister_agent(agent_id: str):
    """
    Deregister an agent
    إلغاء تسجيل وكيل

    Requires API key authentication.
    يتطلب مصادقة مفتاح API.
    """
    try:
        registry = app_state.get("registry")
        storage = app_state.get("storage")

        if not registry or not storage:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not initialized",
            )

        # Deregister from registry
        await registry.deregister_agent(agent_id)

        # Remove from storage
        deleted = await storage.delete_agent(agent_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent not found: {agent_id}",
            )

        logger.info("agent_deregistered_successfully", agent_id=agent_id)

        return {
            "status": "success",
            "message": "Agent deregistered successfully",
            "agent_id": agent_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("deregister_agent_failed", agent_id=agent_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


# ============================================================================
# Discovery Endpoints
# ============================================================================


@app.get("/v1/registry/discover/capability", tags=["Discovery"])
async def discover_by_capability(capability: str):
    """
    Discover agents by capability
    اكتشاف الوكلاء حسب القدرة
    """
    try:
        registry = app_state.get("registry")
        if not registry:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Registry not initialized",
            )

        agents = registry.discover_by_capability(capability)

        return {
            "status": "success",
            "capability": capability,
            "agents": [a.to_dict() for a in agents],
            "total": len(agents),
        }

    except Exception as e:
        logger.error(
            "discover_by_capability_failed", capability=capability, error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@app.get("/v1/registry/discover/skill", tags=["Discovery"])
async def discover_by_skill(skill: str):
    """
    Discover agents by skill
    اكتشاف الوكلاء حسب المهارة
    """
    try:
        registry = app_state.get("registry")
        if not registry:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Registry not initialized",
            )

        agents = registry.discover_by_skill(skill)

        return {
            "status": "success",
            "skill": skill,
            "agents": [a.to_dict() for a in agents],
            "total": len(agents),
        }

    except Exception as e:
        logger.error("discover_by_skill_failed", skill=skill, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@app.post("/v1/registry/discover/tags", tags=["Discovery"])
async def discover_by_tags(request: DiscoverByTagsRequest):
    """
    Discover agents by tags
    اكتشاف الوكلاء حسب العلامات
    """
    try:
        registry = app_state.get("registry")
        if not registry:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Registry not initialized",
            )

        agents = registry.discover_by_tags(request.tags)

        return {
            "status": "success",
            "tags": request.tags,
            "agents": [a.to_dict() for a in agents],
            "total": len(agents),
        }

    except Exception as e:
        logger.error("discover_by_tags_failed", tags=request.tags, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


# ============================================================================
# Health Check Endpoints
# ============================================================================


@app.get("/v1/registry/agents/{agent_id}/health", tags=["Health"])
async def check_agent_health(agent_id: str):
    """
    Check health of a specific agent
    فحص صحة وكيل محدد
    """
    try:
        registry = app_state.get("registry")
        if not registry:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Registry not initialized",
            )

        health_result = await registry.check_agent_health(agent_id)

        return health_result.model_dump()

    except Exception as e:
        logger.error("check_agent_health_failed", agent_id=agent_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@app.get("/v1/registry/health/all", tags=["Health"])
async def get_all_health_statuses():
    """
    Get health statuses of all agents
    الحصول على حالات صحة جميع الوكلاء
    """
    try:
        registry = app_state.get("registry")
        if not registry:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Registry not initialized",
            )

        health_statuses = registry.get_all_health_statuses()

        return {
            "status": "success",
            "health_statuses": {
                agent_id: health.model_dump()
                for agent_id, health in health_statuses.items()
            },
            "total": len(health_statuses),
        }

    except Exception as e:
        logger.error("get_all_health_statuses_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        log_level=settings.log_level.lower(),
        reload=False,
    )
