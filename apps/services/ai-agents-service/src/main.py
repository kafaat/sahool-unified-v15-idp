"""
SAHOOL AI Agents Service
=========================
Autonomous AI agents for agricultural intelligence.

Inspired by: Dexter, OpenCode, Claude Code patterns
Features:
- Task decomposition and execution
- Agricultural research agents
- Farm advisory agents (Plan/Execute modes)
- Self-validation with retry logic

Port: 8130
"""

import json
import os
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timezone
from typing import Any
from uuid import uuid4

import redis.asyncio as redis_client
import structlog
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Add project root to path
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
)

# Initialize structured logger and tracing
from shared.logging_config import setup_logging
from shared.observability.tracing import setup_tracing

setup_logging("ai-agents-service")
logger = structlog.get_logger()
_tracer = setup_tracing("ai-agents-service")

from shared.ai.agents import (
    AgentMode,
    AgriculturalResearchAgent,
    FarmAdvisorAgent,
    PlannerAgent,
)
from shared.auth.dependencies import get_current_user
from shared.auth.models import User
from shared.events.contracts import (
    AgentExecutionCompletedEvent,
    AgentExecutionFailedEvent,
    AgentExecutionStartedEvent,
)
from shared.middleware.tenant_context import TenantContextMiddleware

# Database layer
from . import db

# Service configuration
SERVICE_NAME = "ai-agents-service"
SERVICE_NAME_AR = "خدمة الوكلاء الذكية"
SERVICE_VERSION = "16.0.0"
SERVICE_PORT = 8130

# NATS subjects for agent events
NATS_AGENT_EXECUTION_STARTED = "sahool.agent.execution.started"
NATS_AGENT_EXECUTION_COMPLETED = "sahool.agent.execution.completed"
NATS_AGENT_EXECUTION_FAILED = "sahool.agent.execution.failed"

# Valid agent types for upfront validation
VALID_AGENT_TYPES = {"farm_advisor", "research", "planner"}


# ═══════════════════════════════════════════════════════════════════════════════
# Error Response Model & Custom Exceptions
# ═══════════════════════════════════════════════════════════════════════════════


class ErrorResponse(BaseModel):
    """Standardized error response model"""

    error: str
    error_ar: str | None = None
    error_code: str
    detail: str | None = None
    request_id: str | None = None


class ServiceUnavailableError(Exception):
    """Raised when a required service (DB, NATS) is unavailable"""

    def __init__(self, service: str, message: str = "Service unavailable"):
        self.service = service
        self.message = message
        super().__init__(self.message)


class AgentExecutionError(Exception):
    """Raised when agent execution fails"""

    def __init__(self, agent_type: str, message: str, execution_id: str | None = None):
        self.agent_type = agent_type
        self.message = message
        self.execution_id = execution_id
        super().__init__(self.message)


class ResourceNotFoundError(Exception):
    """Raised when a requested resource is not found"""

    def __init__(self, resource_type: str, resource_id: str):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.message = f"{resource_type} not found: {resource_id}"
        super().__init__(self.message)


class TenantAccessDeniedError(Exception):
    """Raised when tenant access is denied"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.message = "Access denied: tenant mismatch"
        super().__init__(self.message)


def get_request_id(request: Request) -> str | None:
    """Extract or generate request ID from request"""
    return getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID")


# ═══════════════════════════════════════════════════════════════════════════════
# Rate Limiting Configuration
# ═══════════════════════════════════════════════════════════════════════════════

# Rate limits based on tiers from CLAUDE.md:
# - Free tier: 30 req/min
# - Standard: 60 req/min
# - Premium: 120 req/min
# - Internal: 1000 req/min
# Default to Standard tier (60 req/min) for most endpoints

limiter = Limiter(key_func=get_remote_address)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded errors (429)"""
    request_id = get_request_id(request)
    logger.warning(
        "rate_limit_exceeded",
        path=request.url.path,
        request_id=request_id,
        detail=str(exc.detail),
    )
    return JSONResponse(
        status_code=429,
        content=ErrorResponse(
            error="Rate limit exceeded",
            error_ar="تم تجاوز الحد الأقصى للطلبات",
            error_code="RATE_LIMIT_EXCEEDED",
            detail=str(exc.detail),
            request_id=request_id,
        ).model_dump(),
        headers={"Retry-After": "60"},
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Request/Response Models
# ═══════════════════════════════════════════════════════════════════════════════


class AgentExecuteRequest(BaseModel):
    """Request to execute an agent task"""

    task: str = Field(..., description="Task description in natural language")
    task_ar: str | None = Field(None, description="Task description in Arabic")
    agent_type: str = Field("farm_advisor", description="Agent type: farm_advisor, research, planner")
    mode: str = Field("hybrid", description="Execution mode: plan, execute, hybrid")
    context: dict[str, Any] | None = Field(None, description="Additional context for the agent")
    tenant_id: str = Field(..., description="Tenant ID for multi-tenancy")
    field_id: str | None = Field(None, description="Optional field ID for field-specific tasks")
    farm_id: str | None = Field(None, description="Optional farm ID")
    max_steps: int = Field(50, ge=1, le=100, description="Maximum execution steps")
    timeout_seconds: int = Field(300, ge=30, le=600, description="Execution timeout")


class AgentStep(BaseModel):
    """Single step in agent execution"""

    step_number: int
    action: str
    action_ar: str | None = None
    tool_used: str | None = None
    result: dict[str, Any] | None = None
    timestamp: datetime
    duration_ms: int | None = None


class AgentExecuteResponse(BaseModel):
    """Response from agent execution"""

    execution_id: str
    tenant_id: str
    agent_type: str
    mode: str
    task: str
    status: str  # running, completed, failed, timeout
    state: str  # idle, planning, executing, validating, completed, error
    steps: list[AgentStep] = []
    final_result: dict[str, Any] | None = None
    error: str | None = None
    started_at: datetime
    completed_at: datetime | None = None
    total_duration_ms: int | None = None


class AgentListItem(BaseModel):
    """Agent type information"""

    agent_type: str
    name: str
    name_ar: str
    description: str
    description_ar: str
    supported_modes: list[str]
    available_tools: list[str]


class ExecutionStatusResponse(BaseModel):
    """Status of an ongoing execution"""

    execution_id: str
    status: str
    state: str
    current_step: int
    total_steps: int
    progress_percent: float
    last_action: str | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# In-memory execution store (fallback when database is unavailable)
# ═══════════════════════════════════════════════════════════════════════════════

executions: dict[str, AgentExecuteResponse] = {}


def _use_database() -> bool:
    """Check if database is available for persistence."""
    return db.get_pool() is not None


# ═══════════════════════════════════════════════════════════════════════════════
# Lifespan Management
# ═══════════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("service_starting", service=SERVICE_NAME, version=SERVICE_VERSION)

    # Initialize database connection pool
    pool = await db.init_pool()
    if pool:
        app.state.db_connected = True
        # Ensure schema exists
        await db.ensure_schema()
    else:
        app.state.db_connected = False
        logger.warning("database_unavailable", detail="running without database persistence, using in-memory store")

    # Initialize Redis connection (if available)
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            app.state.redis = redis_client.from_url(redis_url, decode_responses=True)
            app.state.redis_connected = True
            logger.info("redis_connected", url=redis_url)
        except Exception as e:
            logger.warning("redis_connection_failed", error=str(e))
            app.state.redis = None
            app.state.redis_connected = False
    else:
        app.state.redis = None
        app.state.redis_connected = False

    # Initialize NATS publisher (if available)
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            from shared.events.publisher import get_publisher

            app.state.publisher = await get_publisher(service_name=SERVICE_NAME, service_version=SERVICE_VERSION)
            app.state.nats_connected = True
            logger.info("nats_connected", url=nats_url)
        except Exception as e:
            logger.warning("nats_connection_failed", error=str(e))
            app.state.publisher = None
            app.state.nats_connected = False
    else:
        app.state.publisher = None
        app.state.nats_connected = False

    logger.info("service_ready", service=SERVICE_NAME, port=SERVICE_PORT)

    yield

    # Shutdown
    await db.close_pool()
    if hasattr(app.state, "redis") and app.state.redis:
        await app.state.redis.close()
    if hasattr(app.state, "publisher") and app.state.publisher:
        await app.state.publisher.close()
    logger.info("service_shutdown_complete", service=SERVICE_NAME)


# ═══════════════════════════════════════════════════════════════════════════════
# Redis Cache Helpers
# ═══════════════════════════════════════════════════════════════════════════════


async def cache_get(key: str) -> dict | None:
    """Get value from Redis cache."""
    if hasattr(app.state, "redis") and app.state.redis:
        try:
            data = await app.state.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning("cache_get_error", key=key, error=str(e))
    return None


async def cache_set(key: str, value: dict, ttl: int = 300):
    """Set value in Redis cache with TTL (default 5 minutes)."""
    if hasattr(app.state, "redis") and app.state.redis:
        try:
            await app.state.redis.setex(key, ttl, json.dumps(value, default=str))
        except Exception as e:
            logger.warning("cache_set_error", key=key, error=str(e))


async def cache_delete(key: str):
    """Delete value from Redis cache."""
    if hasattr(app.state, "redis") and app.state.redis:
        try:
            await app.state.redis.delete(key)
        except Exception as e:
            logger.warning("cache_delete_error", key=key, error=str(e))


async def cache_delete_pattern(pattern: str):
    """Delete all keys matching a pattern from Redis cache."""
    if hasattr(app.state, "redis") and app.state.redis:
        try:
            keys = []
            async for key in app.state.redis.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                await app.state.redis.delete(*keys)
        except Exception as e:
            logger.warning("cache_delete_pattern_error", pattern=pattern, error=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI Application
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="SAHOOL AI Agents Service",
    description="Autonomous AI agents for agricultural intelligence | وكلاء ذكاء اصطناعي مستقلين للذكاء الزراعي",
    version=SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)
_tracer.instrument_fastapi(app)

# Setup unified error handling
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    setup_exception_handlers(app)
    add_request_id_middleware(app)
except ImportError:
    pass

# Configure rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


# ═══════════════════════════════════════════════════════════════════════════════
# Request ID Middleware
# ═══════════════════════════════════════════════════════════════════════════════


@app.middleware("http")
async def ensure_request_id(request: Request, call_next):
    """Ensure request ID header is present for tracing (fallback if shared middleware not loaded)"""
    if not hasattr(request.state, "request_id"):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = getattr(request.state, "request_id", str(uuid4()))
    return response


# ═══════════════════════════════════════════════════════════════════════════════
# Exception Handlers
# ═══════════════════════════════════════════════════════════════════════════════


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle validation errors (400)"""
    request_id = get_request_id(request)
    logger.warning(
        "validation_error",
        path=request.url.path,
        request_id=request_id,
        error=str(exc),
    )
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error="Validation error",
            error_ar="خطأ في التحقق",
            error_code="VALIDATION_ERROR",
            detail=str(exc),
            request_id=request_id,
        ).model_dump(),
    )


@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError) -> JSONResponse:
    """Handle resource not found errors (404)"""
    request_id = get_request_id(request)
    logger.info(
        "resource_not_found",
        path=request.url.path,
        request_id=request_id,
        resource_type=exc.resource_type,
        resource_id=exc.resource_id,
    )
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="Resource not found",
            error_ar="المورد غير موجود",
            error_code="NOT_FOUND",
            detail=exc.message,
            request_id=request_id,
        ).model_dump(),
    )


@app.exception_handler(TenantAccessDeniedError)
async def tenant_access_denied_handler(request: Request, exc: TenantAccessDeniedError) -> JSONResponse:
    """Handle tenant access denied errors (403)"""
    request_id = get_request_id(request)
    logger.warning(
        "tenant_access_denied",
        path=request.url.path,
        request_id=request_id,
        tenant_id=exc.tenant_id,
    )
    return JSONResponse(
        status_code=403,
        content=ErrorResponse(
            error="Access denied",
            error_ar="تم رفض الوصول",
            error_code="FORBIDDEN",
            detail="Tenant mismatch | عدم تطابق المستأجر",
            request_id=request_id,
        ).model_dump(),
    )


@app.exception_handler(ServiceUnavailableError)
async def service_unavailable_handler(request: Request, exc: ServiceUnavailableError) -> JSONResponse:
    """Handle service unavailable errors (503)"""
    request_id = get_request_id(request)
    logger.error(
        "service_unavailable",
        path=request.url.path,
        request_id=request_id,
        service=exc.service,
        error=exc.message,
    )
    return JSONResponse(
        status_code=503,
        content=ErrorResponse(
            error="Service unavailable",
            error_ar="الخدمة غير متاحة",
            error_code="SERVICE_UNAVAILABLE",
            detail=f"{exc.service} is unavailable",
            request_id=request_id,
        ).model_dump(),
    )


@app.exception_handler(AgentExecutionError)
async def agent_execution_error_handler(request: Request, exc: AgentExecutionError) -> JSONResponse:
    """Handle agent execution errors (500)"""
    request_id = get_request_id(request)
    logger.error(
        "agent_execution_error",
        path=request.url.path,
        request_id=request_id,
        agent_type=exc.agent_type,
        execution_id=exc.execution_id,
        error=exc.message,
    )
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Agent execution failed",
            error_ar="فشل تنفيذ الوكيل",
            error_code="AGENT_EXECUTION_ERROR",
            detail=exc.message,
            request_id=request_id,
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent format"""
    request_id = get_request_id(request)
    error_codes = {
        400: ("BAD_REQUEST", "طلب غير صالح"),
        401: ("UNAUTHORIZED", "غير مصرح"),
        403: ("FORBIDDEN", "ممنوع"),
        404: ("NOT_FOUND", "غير موجود"),
        429: ("RATE_LIMIT_EXCEEDED", "تم تجاوز الحد"),
        500: ("INTERNAL_ERROR", "خطأ داخلي"),
        503: ("SERVICE_UNAVAILABLE", "الخدمة غير متاحة"),
    }
    error_code, error_ar = error_codes.get(exc.status_code, ("ERROR", "خطأ"))

    if exc.status_code >= 500:
        logger.error(
            "http_exception",
            status_code=exc.status_code,
            path=request.url.path,
            request_id=request_id,
            detail=exc.detail,
        )
    else:
        logger.warning(
            "http_exception",
            status_code=exc.status_code,
            path=request.url.path,
            request_id=request_id,
            detail=exc.detail,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=str(exc.detail),
            error_ar=error_ar,
            error_code=error_code,
            detail=str(exc.detail),
            request_id=request_id,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions (500)"""
    request_id = get_request_id(request)
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        request_id=request_id,
        error=str(exc),
        error_type=type(exc).__name__,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            error_ar="خطأ داخلي في الخادم",
            error_code="INTERNAL_ERROR",
            detail="An unexpected error occurred",
            request_id=request_id,
        ).model_dump(),
    )


# Get allowed origins from environment
cors_origins = [
    o.strip() for o in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Tenant-ID"],
)

# Tenant context middleware - عزل المستأجرين
app.add_middleware(TenantContextMiddleware)


# ═══════════════════════════════════════════════════════════════════════════════
# Health Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/healthz", tags=["Health"])
def health():
    """Liveness probe"""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "service_ar": SERVICE_NAME_AR,
        "version": SERVICE_VERSION,
    }


@app.get("/readyz", tags=["Health"])
async def readiness():
    """Readiness probe"""
    active_count = 0
    if _use_database():
        active_count = await db.count_active_executions()
    else:
        active_count = len([e for e in executions.values() if e.status == "running"])

    return {
        "status": "ok",
        "database": getattr(app.state, "db_connected", False),
        "redis": getattr(app.state, "redis_connected", False),
        "nats": getattr(app.state, "nats_connected", False),
        "executions_active": active_count,
    }


@app.get("/health", tags=["Health"])
async def health_detailed():
    """Detailed health status"""
    if _use_database():
        counts = await db.get_execution_counts()
        active_executions = counts.get("running", 0)
        total_executions = counts.get("total", 0)
    else:
        active_executions = len([e for e in executions.values() if e.status == "running"])
        total_executions = len(executions)

    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "service_ar": SERVICE_NAME_AR,
        "version": SERVICE_VERSION,
        "database_connected": getattr(app.state, "db_connected", False),
        "redis_connected": getattr(app.state, "redis_connected", False),
        "nats_connected": getattr(app.state, "nats_connected", False),
        "active_executions": active_executions,
        "total_executions": total_executions,
        "available_agents": ["farm_advisor", "research", "planner"],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Agent Management Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/v1/agents", response_model=list[AgentListItem], tags=["Agents"])
@limiter.limit("60/minute")
async def list_agents(request: Request, user: User = Depends(get_current_user)):
    """List available agent types | قائمة أنواع الوكلاء المتاحة"""
    cache_key = f"ai_agents:{user.tenant_id}:agent_list"

    # Try to get from cache
    cached = await cache_get(cache_key)
    if cached:
        return [AgentListItem(**item) for item in cached]

    agents = [
        AgentListItem(
            agent_type="farm_advisor",
            name="Farm Advisor Agent",
            name_ar="وكيل المستشار الزراعي",
            description="Dual-mode agent for farm advisory with Plan and Execute modes",
            description_ar="وكيل ثنائي الوضع للاستشارات الزراعية مع وضعي التخطيط والتنفيذ",
            supported_modes=["plan", "execute", "hybrid"],
            available_tools=[
                "fetch_satellite_data",
                "fetch_weather_data",
                "fetch_sensor_data",
                "analyze_crop_health",
                "generate_recommendations",
                "schedule_irrigation",
                "create_task",
            ],
        ),
        AgentListItem(
            agent_type="research",
            name="Agricultural Research Agent",
            name_ar="وكيل البحث الزراعي",
            description="Specialized agent for agricultural data analysis and research",
            description_ar="وكيل متخصص لتحليل البيانات الزراعية والبحث",
            supported_modes=["execute", "hybrid"],
            available_tools=[
                "fetch_satellite_data",
                "fetch_weather_data",
                "fetch_sensor_data",
                "analyze_crop_health",
                "calculate_irrigation_need",
                "diagnose_crop_issue",
            ],
        ),
        AgentListItem(
            agent_type="planner",
            name="Planner Agent",
            name_ar="وكيل التخطيط",
            description="Read-only planning agent for task analysis and recommendations",
            description_ar="وكيل تخطيط للقراءة فقط لتحليل المهام والتوصيات",
            supported_modes=["plan"],
            available_tools=["fetch_satellite_data", "fetch_weather_data", "analyze_crop_health"],
        ),
    ]

    # Cache the result (longer TTL since agent list is static)
    await cache_set(cache_key, [a.model_dump() for a in agents], ttl=3600)

    return agents


@app.post("/api/v1/agents/execute", response_model=AgentExecuteResponse, tags=["Agents"])
@limiter.limit("10/minute")  # Stricter limit for resource-intensive endpoint
async def execute_agent(
    request: Request,
    agent_request: AgentExecuteRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
):
    """
    Execute an agent task

    تنفيذ مهمة الوكيل

    - **task**: Task description in natural language
    - **agent_type**: Type of agent (farm_advisor, research, planner)
    - **mode**: Execution mode (plan, execute, hybrid)
    - **context**: Additional context for the agent

    Rate limit: 10 requests/minute (resource intensive)
    """
    # Validate tenant_id matches authenticated user
    if user.tenant_id != agent_request.tenant_id:
        raise TenantAccessDeniedError(tenant_id=agent_request.tenant_id)

    # Validate agent type upfront to fail fast
    if agent_request.agent_type not in VALID_AGENT_TYPES:
        raise ValueError(
            f"Invalid agent_type: '{agent_request.agent_type}'. Must be one of: {', '.join(sorted(VALID_AGENT_TYPES))}"
        )

    execution_id = str(uuid4())
    started_at = datetime.now(UTC)
    initial_state = "planning" if agent_request.mode in ["plan", "hybrid"] else "executing"

    # Create initial response
    response = AgentExecuteResponse(
        execution_id=execution_id,
        tenant_id=agent_request.tenant_id,
        agent_type=agent_request.agent_type,
        mode=agent_request.mode,
        task=agent_request.task,
        status="running",
        state=initial_state,
        started_at=started_at,
    )

    # Persist to database or fallback to in-memory
    if _use_database():
        await db.create_execution(
            execution_id=execution_id,
            agent_type=agent_request.agent_type,
            mode=agent_request.mode,
            goal=agent_request.task,
            tenant_id=agent_request.tenant_id,
            field_id=agent_request.field_id,
            farm_id=agent_request.farm_id,
        )

    # Also keep in-memory for fast access during execution
    executions[execution_id] = response

    # Execute in background
    background_tasks.add_task(
        _execute_agent_task,
        execution_id,
        agent_request,
    )

    return response


async def _execute_agent_task(execution_id: str, request: AgentExecuteRequest):
    """Background task to execute agent"""
    response = executions[execution_id]

    # Publish execution started event
    if hasattr(app.state, "publisher") and app.state.publisher:
        try:
            await app.state.publisher.publish_event(
                NATS_AGENT_EXECUTION_STARTED,
                AgentExecutionStartedEvent(
                    execution_id=execution_id,
                    agent_type=request.agent_type,
                    tenant_id=request.tenant_id,
                    task=request.task,
                    mode=request.mode,
                    field_id=request.field_id,
                    farm_id=request.farm_id,
                ),
            )
        except Exception as e:
            logger.warning("nats_publish_failed", event="started", error=str(e))

    try:
        # Select agent type
        if request.agent_type == "farm_advisor":
            mode = AgentMode.HYBRID
            if request.mode == "plan":
                mode = AgentMode.PLAN
            elif request.mode == "execute":
                mode = AgentMode.EXECUTE

            agent = FarmAdvisorAgent(
                agent_id=execution_id,
                mode=mode,
                max_steps=request.max_steps,
                timeout_seconds=request.timeout_seconds,
            )
        elif request.agent_type == "research":
            agent = AgriculturalResearchAgent(
                agent_id=execution_id,
                max_steps=request.max_steps,
                timeout_seconds=request.timeout_seconds,
            )
        elif request.agent_type == "planner":
            agent = PlannerAgent(
                agent_id=execution_id,
                max_steps=request.max_steps,
                timeout_seconds=request.timeout_seconds,
            )
        else:
            raise ValueError(f"Unknown agent type: {request.agent_type}")

        # Build context
        context = request.context or {}
        if request.field_id:
            context["field_id"] = request.field_id
        if request.farm_id:
            context["farm_id"] = request.farm_id
        context["tenant_id"] = request.tenant_id

        # Execute agent
        result = await agent.run(request.task, context)

        # Update response with results
        response.status = "completed" if result.get("success") else "failed"
        response.state = "completed"
        response.final_result = result
        response.completed_at = datetime.now(UTC)

        if response.started_at and response.completed_at:
            response.total_duration_ms = int((response.completed_at - response.started_at).total_seconds() * 1000)

        # Convert agent steps to response format
        if hasattr(agent, "steps"):
            for i, step in enumerate(agent.steps):
                response.steps.append(
                    AgentStep(
                        step_number=i + 1,
                        action=step.get("action", "unknown"),
                        action_ar=step.get("action_ar"),
                        tool_used=step.get("tool"),
                        result=step.get("result"),
                        timestamp=step.get("timestamp", datetime.now(UTC)),
                        duration_ms=step.get("duration_ms"),
                    )
                )

        logger.info(
            "agent_execution_completed",
            execution_id=execution_id,
            agent_type=request.agent_type,
            status=response.status,
            duration_ms=response.total_duration_ms,
        )

    except ValueError as e:
        # Handle validation errors (e.g., unknown agent type)
        response.status = "failed"
        response.state = "error"
        response.error = f"Validation error: {str(e)}"
        response.completed_at = datetime.now(UTC)
        logger.warning(
            "agent_validation_error",
            execution_id=execution_id,
            agent_type=request.agent_type,
            error=str(e),
        )

    except TimeoutError as e:
        # Handle timeout errors
        response.status = "timeout"
        response.state = "error"
        response.error = f"Execution timeout: {str(e)}"
        response.completed_at = datetime.now(UTC)
        logger.warning(
            "agent_execution_timeout",
            execution_id=execution_id,
            agent_type=request.agent_type,
            timeout_seconds=request.timeout_seconds,
        )

    except ConnectionError as e:
        # Handle connection errors (e.g., database, external services)
        response.status = "failed"
        response.state = "error"
        response.error = f"Connection error: {str(e)}"
        response.completed_at = datetime.now(UTC)
        logger.error(
            "agent_connection_error",
            execution_id=execution_id,
            agent_type=request.agent_type,
            error=str(e),
        )

    except Exception as e:
        # Handle all other unexpected errors
        response.status = "failed"
        response.state = "error"
        response.error = f"Unexpected error: {type(e).__name__}"
        response.completed_at = datetime.now(UTC)
        logger.error(
            "agent_execution_error",
            execution_id=execution_id,
            agent_type=request.agent_type,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )

    finally:
        # Always calculate duration if we have timestamps
        if response.started_at and response.completed_at:
            response.total_duration_ms = int((response.completed_at - response.started_at).total_seconds() * 1000)

        # Persist final state to database
        if _use_database():
            await db.update_execution(
                execution_id=execution_id,
                status=response.status,
                state=response.state,
                result=response.final_result,
                steps=[s.model_dump() for s in response.steps] if response.steps else [],
                error=response.error,
                completed_at=response.completed_at,
                total_duration_ms=response.total_duration_ms,
                tenant_id=request.tenant_id,
            )

        # Publish completion/failure event
        if hasattr(app.state, "publisher") and app.state.publisher:
            try:
                if response.status == "completed":
                    await app.state.publisher.publish_event(
                        NATS_AGENT_EXECUTION_COMPLETED,
                        AgentExecutionCompletedEvent(
                            execution_id=execution_id,
                            agent_type=request.agent_type,
                            tenant_id=request.tenant_id,
                            status=response.status,
                            total_steps=len(response.steps),
                            duration_ms=response.total_duration_ms or 0,
                            result_summary=response.final_result.get("summary") if response.final_result else None,
                        ),
                    )
                else:
                    # Failed, timeout, or other non-success status
                    await app.state.publisher.publish_event(
                        NATS_AGENT_EXECUTION_FAILED,
                        AgentExecutionFailedEvent(
                            execution_id=execution_id,
                            agent_type=request.agent_type,
                            tenant_id=request.tenant_id,
                            error_type=response.status,
                            error_message=response.error or "Unknown error",
                            failed_at_step=len(response.steps) if response.steps else None,
                            duration_ms=response.total_duration_ms or 0,
                        ),
                    )
            except Exception as e:
                logger.warning("nats_publish_failed", event="completed/failed", error=str(e))


@app.get("/api/v1/agents/executions/{execution_id}", response_model=AgentExecuteResponse, tags=["Agents"])
@limiter.limit("60/minute")
async def get_execution(
    request: Request,
    execution_id: str,
    user: User = Depends(get_current_user),
):
    """Get execution status and results | الحصول على حالة ونتائج التنفيذ"""
    # First check in-memory store (fast path for recent executions)
    if execution_id in executions:
        execution = executions[execution_id]
        # Validate tenant_id matches authenticated user
        if user.tenant_id != execution.tenant_id:
            raise TenantAccessDeniedError(tenant_id=execution.tenant_id)
        return execution

    # Then check database for persisted executions
    if _use_database():
        db_exec = await db.get_execution(execution_id, tenant_id=user.tenant_id)
        if db_exec:
            # Validate tenant access
            if user.tenant_id != db_exec.get("tenant_id"):
                raise TenantAccessDeniedError(tenant_id=db_exec.get("tenant_id", "unknown"))
            # Convert database record to response model
            return AgentExecuteResponse(
                execution_id=db_exec.get("id", execution_id),
                tenant_id=db_exec.get("tenant_id", ""),
                agent_type=db_exec.get("agent_type", ""),
                mode=db_exec.get("mode", "hybrid"),
                task=db_exec.get("goal", ""),
                status=db_exec.get("status", "unknown"),
                state=db_exec.get("state", "unknown"),
                steps=[AgentStep(**s) for s in db_exec.get("steps", [])] if db_exec.get("steps") else [],
                final_result=db_exec.get("result"),
                error=db_exec.get("error"),
                started_at=db_exec.get("created_at", datetime.now(UTC)),
                completed_at=db_exec.get("completed_at"),
                total_duration_ms=db_exec.get("total_duration_ms"),
            )

    raise ResourceNotFoundError(resource_type="Execution", resource_id=execution_id)


@app.get(
    "/api/v1/agents/executions/{execution_id}/status",
    response_model=ExecutionStatusResponse,
    tags=["Agents"],
)
@limiter.limit("60/minute")
async def get_execution_status(
    request: Request,
    execution_id: str,
    user: User = Depends(get_current_user),
):
    """Get brief execution status | الحصول على حالة التنفيذ المختصرة"""
    cache_key = f"ai_agents:{user.tenant_id}:execution_status:{execution_id}"

    # Try to get from cache (only for completed/failed executions)
    cached = await cache_get(cache_key)
    if cached:
        # Verify tenant access
        if user.tenant_id != cached.get("tenant_id"):
            raise TenantAccessDeniedError(tenant_id=cached.get("tenant_id", "unknown"))
        return ExecutionStatusResponse(**cached)

    if execution_id not in executions:
        raise ResourceNotFoundError(resource_type="Execution", resource_id=execution_id)

    execution = executions[execution_id]
    # Validate tenant_id matches authenticated user
    if user.tenant_id != execution.tenant_id:
        raise TenantAccessDeniedError(tenant_id=execution.tenant_id)

    total_steps = len(execution.steps) or 1
    current_step = len(execution.steps)

    response = ExecutionStatusResponse(
        execution_id=execution_id,
        status=execution.status,
        state=execution.state,
        current_step=current_step,
        total_steps=total_steps,
        progress_percent=(current_step / total_steps) * 100 if total_steps > 0 else 0,
        last_action=execution.steps[-1].action if execution.steps else None,
    )

    # Cache completed/failed executions (they won't change)
    if execution.status in ["completed", "failed", "cancelled", "timeout"]:
        cache_data = response.model_dump()
        cache_data["tenant_id"] = execution.tenant_id
        await cache_set(cache_key, cache_data, ttl=3600)

    return response


@app.delete("/api/v1/agents/executions/{execution_id}", tags=["Agents"])
@limiter.limit("60/minute")
async def cancel_execution(
    request: Request,
    execution_id: str,
    user: User = Depends(get_current_user),
):
    """Cancel a running execution | إلغاء تنفيذ قيد التشغيل"""
    if execution_id not in executions:
        raise ResourceNotFoundError(resource_type="Execution", resource_id=execution_id)

    execution = executions[execution_id]
    # Validate tenant_id matches authenticated user
    if user.tenant_id != execution.tenant_id:
        raise TenantAccessDeniedError(tenant_id=execution.tenant_id)

    if execution.status == "running":
        execution.status = "cancelled"
        execution.state = "cancelled"
        execution.completed_at = datetime.now(UTC)
        # Invalidate cache for this execution
        await cache_delete(f"ai_agents:{user.tenant_id}:execution_status:{execution_id}")
        return {"message": "Execution cancelled", "execution_id": execution_id}

    return {"message": "Execution already completed", "execution_id": execution_id}


@app.get("/api/v1/agents/executions", response_model=list[AgentExecuteResponse], tags=["Agents"])
@limiter.limit("60/minute")
async def list_executions(
    request: Request,
    tenant_id: str = Query(..., description="Filter by tenant ID"),
    status: str | None = Query(None, description="Filter by status"),
    agent_type: str | None = Query(None, description="Filter by agent type"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    user: User = Depends(get_current_user),
):
    """List recent executions | قائمة التنفيذات الأخيرة"""
    # Validate tenant_id matches authenticated user
    if user.tenant_id != tenant_id:
        raise TenantAccessDeniedError(tenant_id=tenant_id)

    # Try to get from database first for complete history
    if _use_database():
        db_results = await db.list_executions(
            tenant_id=tenant_id,
            status=status,
            agent_type=agent_type,
            limit=limit,
            offset=offset,
        )
        # Convert database records to response models
        return [
            AgentExecuteResponse(
                execution_id=r.get("id", ""),
                tenant_id=r.get("tenant_id", ""),
                agent_type=r.get("agent_type", ""),
                mode=r.get("mode", "hybrid"),
                task=r.get("goal", ""),
                status=r.get("status", "unknown"),
                state=r.get("state", "unknown"),
                steps=[AgentStep(**s) for s in r.get("steps", [])] if r.get("steps") else [],
                final_result=r.get("result"),
                error=r.get("error"),
                started_at=r.get("created_at", datetime.now(UTC)),
                completed_at=r.get("completed_at"),
                total_duration_ms=r.get("total_duration_ms"),
            )
            for r in db_results
        ]

    # Fallback to in-memory store
    results = [e for e in executions.values() if e.tenant_id == tenant_id]

    # Filter by status if provided
    if status:
        results = [e for e in results if e.status == status]

    # Filter by agent_type if provided
    if agent_type:
        results = [e for e in results if e.agent_type == agent_type]

    # Sort by started_at descending
    results.sort(key=lambda x: x.started_at, reverse=True)

    # Apply pagination
    return results[offset : offset + limit]


# ═══════════════════════════════════════════════════════════════════════════════
# Quick Action Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


class QuickAnalysisRequest(BaseModel):
    """Quick analysis request"""

    field_id: str
    tenant_id: str
    analysis_type: str = Field("crop_health", description="Type: crop_health, irrigation, yield")


class QuickAnalysisResponse(BaseModel):
    """Quick analysis response"""

    field_id: str
    analysis_type: str
    summary: str
    summary_ar: str
    recommendations: list[dict[str, Any]]
    confidence: float
    timestamp: datetime


@app.post("/api/v1/agents/quick/analyze", response_model=QuickAnalysisResponse, tags=["Quick Actions"])
@limiter.limit("60/minute")
async def quick_analyze(
    request: Request,
    analysis_request: QuickAnalysisRequest,
    user: User = Depends(get_current_user),
):
    """
    Quick field analysis without full agent execution

    تحليل سريع للحقل بدون تنفيذ الوكيل الكامل
    """
    # Validate tenant_id matches authenticated user
    if user.tenant_id != analysis_request.tenant_id:
        raise TenantAccessDeniedError(tenant_id=analysis_request.tenant_id)

    # Simulated quick analysis (replace with actual implementation)
    return QuickAnalysisResponse(
        field_id=analysis_request.field_id,
        analysis_type=analysis_request.analysis_type,
        summary=f"Quick {analysis_request.analysis_type} analysis completed for field {analysis_request.field_id}",
        summary_ar=f"تم إكمال تحليل {analysis_request.analysis_type} السريع للحقل {analysis_request.field_id}",
        recommendations=[
            {
                "action": "Monitor soil moisture",
                "action_ar": "مراقبة رطوبة التربة",
                "priority": "medium",
                "reason": "Soil moisture levels are within normal range",
            }
        ],
        confidence=0.85,
        timestamp=datetime.now(UTC),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Metrics Endpoint
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Prometheus-compatible metrics"""
    total = len(executions)
    running = len([e for e in executions.values() if e.status == "running"])
    completed = len([e for e in executions.values() if e.status == "completed"])
    failed = len([e for e in executions.values() if e.status == "failed"])

    return f"""# HELP ai_agents_executions_total Total number of agent executions
# TYPE ai_agents_executions_total counter
ai_agents_executions_total {total}

# HELP ai_agents_executions_running Currently running executions
# TYPE ai_agents_executions_running gauge
ai_agents_executions_running {running}

# HELP ai_agents_executions_completed Completed executions
# TYPE ai_agents_executions_completed counter
ai_agents_executions_completed {completed}

# HELP ai_agents_executions_failed Failed executions
# TYPE ai_agents_executions_failed counter
ai_agents_executions_failed {failed}
"""


if __name__ == "__main__":
    import uvicorn

    # Use HOST env var for flexibility; 0.0.0.0 for containers, 127.0.0.1 for local dev
    host = os.getenv("HOST", "0.0.0.0")  # nosec B104 - binding to all interfaces required for Docker container
    uvicorn.run(app, host=host, port=SERVICE_PORT)
