"""
SAHOOL Low-Code Engine Service
===============================
Low-code application development platform for agricultural apps.

Inspired by: Alibaba LowCode Engine, NocoBase
Features:
- Material Protocol for components
- Data Model System
- Page & Block System
- Plugin Architecture
- AI-powered component suggestions

Port: 8132
"""

import json
import os
import sys
from contextlib import asynccontextmanager
from typing import Any
from datetime import datetime
from uuid import uuid4

import redis.asyncio as redis_client
import structlog
from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Authentication imports
from shared.auth.dependencies import get_current_user
from shared.auth.models import User

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from shared.lowcode import (
    LowCodeEngine,
    ComponentCategory,
    DataModel,
    FieldDefinition,
    FieldType,
    PageDefinition,
    BlockConfig,
    AIComponentSuggester,
)

# Service configuration
SERVICE_NAME = "lowcode-engine"
SERVICE_NAME_AR = "محرك التطوير منخفض الكود"
SERVICE_VERSION = "16.0.0"
SERVICE_PORT = 8132

# Logger
logger = structlog.get_logger()


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


class ResourceNotFoundError(Exception):
    """Raised when a requested resource is not found"""
    def __init__(self, resource_type: str, resource_id: str = ""):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.message = f"{resource_type} not found"
        super().__init__(self.message)


class TenantAccessDeniedError(Exception):
    """Raised when tenant access is denied"""
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.message = "Access denied: tenant mismatch"
        super().__init__(self.message)


class InvalidBlockConfigError(Exception):
    """Raised when a block configuration is invalid"""
    def __init__(self, block_id: str, reason: str):
        self.block_id = block_id
        self.reason = reason
        self.message = f"Invalid block configuration for {block_id}: {reason}"
        super().__init__(self.message)


def get_request_id(request: Request) -> str | None:
    """Extract or generate request ID from request"""
    return getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID")


# ═══════════════════════════════════════════════════════════════════════════════
# Request/Response Models
# ═══════════════════════════════════════════════════════════════════════════════

class ComponentResponse(BaseModel):
    """Component material response"""
    component_id: str
    name: str
    name_ar: str | None
    category: str
    description: str | None
    description_ar: str | None
    props: list[dict[str, Any]]
    slots: list[dict[str, Any]]
    events: list[dict[str, Any]]
    is_container: bool
    icon: str | None = None


class DataModelCreateRequest(BaseModel):
    """Request to create a data model"""
    name: str = Field(..., min_length=1, max_length=100)
    name_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    fields: list[dict[str, Any]]
    tenant_id: str


class DataModelResponse(BaseModel):
    """Data model response"""
    id: str
    name: str
    name_ar: str | None
    description: str | None
    description_ar: str | None
    fields: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class PageCreateRequest(BaseModel):
    """Request to create a page"""
    name: str = Field(..., min_length=1, max_length=100)
    name_ar: str | None = None
    description: str | None = None
    route: str = Field(..., pattern=r"^/[a-z0-9\-/]*$")
    blocks: list[dict[str, Any]] = []
    data_model_id: str | None = None
    tenant_id: str


class PageResponse(BaseModel):
    """Page response"""
    id: str
    name: str
    name_ar: str | None
    description: str | None
    route: str
    blocks: list[dict[str, Any]]
    data_model_id: str | None
    is_published: bool
    version: int
    created_at: datetime
    updated_at: datetime


class PageRenderResponse(BaseModel):
    """Rendered page response"""
    page_id: str
    name: str
    route: str
    rendered_blocks: list[dict[str, Any]]
    data: dict[str, Any] | None


class AISuggestionRequest(BaseModel):
    """Request for AI component suggestions"""
    description: str = Field(..., min_length=10, description="Page description in natural language")
    description_ar: str | None = None
    context: dict[str, Any] | None = None


class AISuggestionResponse(BaseModel):
    """AI suggestion response"""
    suggestions: list[dict[str, Any]]
    reasoning: str
    reasoning_ar: str | None
    confidence: float


# ═══════════════════════════════════════════════════════════════════════════════
# Internal Storage Dataclasses
# These match the API format (id, field_type, component_name) for easier response handling
# ═══════════════════════════════════════════════════════════════════════════════

from dataclasses import dataclass as internal_dataclass, field as internal_field


@internal_dataclass
class InternalFieldDefinition:
    """Internal field definition matching API format."""
    name: str
    name_ar: str | None = None
    field_type: str = "text"
    required: bool = False
    default_value: Any = None
    options: list[str] | None = None
    validation: dict[str, Any] | None = None


@internal_dataclass
class InternalDataModel:
    """Internal data model matching API format (uses 'id' instead of 'model_id')."""
    id: str
    name: str
    name_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    fields: list[dict[str, Any]] = internal_field(default_factory=list)
    created_at: datetime = internal_field(default_factory=datetime.utcnow)
    updated_at: datetime = internal_field(default_factory=datetime.utcnow)


@internal_dataclass
class InternalBlock:
    """Internal block config matching API format (uses 'id' and 'component_name')."""
    id: str
    component_name: str
    props: dict[str, Any] = internal_field(default_factory=dict)
    children: list[dict[str, Any]] = internal_field(default_factory=list)
    conditions: dict[str, Any] | None = None
    loop: dict[str, Any] | None = None


@internal_dataclass
class InternalPage:
    """Internal page definition matching API format (uses 'id' instead of 'page_id')."""
    id: str
    name: str
    name_ar: str | None = None
    description: str | None = None
    route: str = "/"
    blocks: list[InternalBlock] = internal_field(default_factory=list)
    data_model_id: str | None = None
    is_published: bool = False
    version: int = 1
    created_at: datetime = internal_field(default_factory=datetime.utcnow)
    updated_at: datetime = internal_field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════════
# In-memory storage (replace with database in production)
# ═══════════════════════════════════════════════════════════════════════════════

data_models: dict[str, InternalDataModel] = {}
pages: dict[str, InternalPage] = {}

# Initialize Low-Code Engine (includes built-in components)
lowcode_engine = LowCodeEngine(tenant_id="sahool")
ai_suggester = AIComponentSuggester(lowcode_engine)


# ═══════════════════════════════════════════════════════════════════════════════
# Lifespan Management
# ═══════════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")

    # Initialize Redis connection (if available)
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            app.state.redis = redis_client.from_url(redis_url, decode_responses=True)
            app.state.redis_connected = True
            print(f"✅ Redis connected: {redis_url}")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
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
            app.state.publisher = await get_publisher(
                service_name=SERVICE_NAME,
                service_version=SERVICE_VERSION
            )
            app.state.nats_connected = True
            print(f"✅ NATS connected: {nats_url}")
        except Exception as e:
            print(f"⚠️ NATS connection failed: {e}")
            app.state.publisher = None
            app.state.nats_connected = False
    else:
        app.state.publisher = None
        app.state.nats_connected = False

    # Initialize database connection (if available)
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        try:
            import asyncpg
            app.state.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
            app.state.db_connected = True
            print(f"✅ Database connected")
        except Exception as e:
            print(f"⚠️ Database connection failed: {e}")
            app.state.db_pool = None
            app.state.db_connected = False
    else:
        app.state.db_pool = None
        app.state.db_connected = False

    print(f"✅ {SERVICE_NAME} ready on port {SERVICE_PORT}")
    print(f"📦 Registered {len(lowcode_engine.list_components())} components")

    yield

    # Shutdown
    if hasattr(app.state, "redis") and app.state.redis:
        await app.state.redis.close()
    if hasattr(app.state, "publisher") and app.state.publisher:
        await app.state.publisher.close()
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
    print(f"👋 {SERVICE_NAME} shutdown complete")


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
    title="SAHOOL Low-Code Engine",
    description="Low-code application development platform | منصة تطوير التطبيقات منخفضة الكود",
    version=SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ═══════════════════════════════════════════════════════════════════════════════
# Rate Limiting Configuration
# ═══════════════════════════════════════════════════════════════════════════════

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


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


app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


# ═══════════════════════════════════════════════════════════════════════════════
# Request ID Middleware
# ═══════════════════════════════════════════════════════════════════════════════

@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Add request ID to all requests for tracing"""
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
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


@app.exception_handler(InvalidBlockConfigError)
async def invalid_block_config_handler(request: Request, exc: InvalidBlockConfigError) -> JSONResponse:
    """Handle invalid block configuration errors (400)"""
    request_id = get_request_id(request)
    logger.warning(
        "invalid_block_config",
        path=request.url.path,
        request_id=request_id,
        block_id=exc.block_id,
        reason=exc.reason,
    )
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error="Invalid block configuration",
            error_ar="تكوين كتلة غير صالح",
            error_code="INVALID_BLOCK_CONFIG",
            detail=exc.message,
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


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent format"""
    request_id = get_request_id(request)
    error_codes = {
        400: ("BAD_REQUEST", "طلب غير صالح"),
        401: ("UNAUTHORIZED", "غير مصرح"),
        403: ("FORBIDDEN", "ممنوع"),
        404: ("NOT_FOUND", "غير موجود"),
        409: ("CONFLICT", "تعارض"),
        429: ("RATE_LIMIT_EXCEEDED", "تم تجاوز الحد"),
        500: ("INTERNAL_ERROR", "خطأ داخلي"),
        503: ("SERVICE_UNAVAILABLE", "الخدمة غير متاحة"),
    }
    error_code, error_ar = error_codes.get(exc.status_code, ("ERROR", "خطأ"))

    if exc.status_code >= 500:
        logger.error("http_exception", status_code=exc.status_code, path=request.url.path, request_id=request_id, detail=exc.detail)
    else:
        logger.warning("http_exception", status_code=exc.status_code, path=request.url.path, request_id=request_id, detail=exc.detail)

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


# CORS middleware - Get allowed origins from environment
cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Tenant-ID"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# Tenant Validation Helper
# ═══════════════════════════════════════════════════════════════════════════════

def validate_tenant_access(user: User, tenant_id: str) -> None:
    """
    Validate that user has access to the specified tenant.
    Raises TenantAccessDeniedError if tenant_id doesn't match user's tenant.
    """
    if user.tenant_id and user.tenant_id != tenant_id:
        raise TenantAccessDeniedError(tenant_id=tenant_id)


# ═══════════════════════════════════════════════════════════════════════════════
# NATS Event Publishing
# ═══════════════════════════════════════════════════════════════════════════════

async def publish_event(subject: str, data: dict) -> None:
    """
    Publish an event to NATS.

    Args:
        subject: NATS subject (e.g., sahool.{tenant_id}.lowcode.page.created)
        data: Event payload data
    """
    if hasattr(app.state, "publisher") and app.state.publisher:
        try:
            await app.state.publisher.publish(
                subject,
                json.dumps(data).encode()
            )
            logger.info("event_published", subject=subject)
        except Exception as e:
            logger.error("event_publish_failed", subject=subject, error=str(e))


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
def readiness():
    """Readiness probe"""
    return {
        "status": "ok",
        "database": getattr(app.state, "db_connected", False),
        "redis": getattr(app.state, "redis_connected", False),
        "nats": getattr(app.state, "nats_connected", False),
        "components_loaded": len(lowcode_engine.list_components()) > 0,
    }


@app.get("/health", tags=["Health"])
def health_detailed():
    """Detailed health status"""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "service_ar": SERVICE_NAME_AR,
        "version": SERVICE_VERSION,
        "database_connected": getattr(app.state, "db_connected", False),
        "redis_connected": getattr(app.state, "redis_connected", False),
        "nats_connected": getattr(app.state, "nats_connected", False),
        "components_count": len(lowcode_engine.list_components()),
        "data_models_count": len(data_models),
        "pages_count": len(pages),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Component Material Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/components", response_model=list[ComponentResponse], tags=["Components"])
async def list_components(
    category: str | None = Query(None, description="Filter by category"),
):
    """List available components | قائمة المكونات المتاحة"""
    cache_key = f"lowcode:components:{category or 'all'}"

    # Try to get from cache first
    cached = await cache_get(cache_key)
    if cached:
        return [ComponentResponse(**c) for c in cached]

    components = lowcode_engine.list_components()

    if category:
        components = [c for c in components if c.category.value == category]

    result = [
        ComponentResponse(
            component_id=c.component_id,
            name=c.name,
            name_ar=c.name_ar,
            category=c.category.value,
            description=c.description,
            description_ar=c.description_ar,
            props=[{"name": p.name, "type": p.type, "default": p.default} for p in c.props],
            slots=[{"name": s.name, "title": s.name_ar} for s in c.slots],
            events=[{"name": e.name, "description": e.description} for e in c.events],
            is_container=c.is_container,
            icon=c.icon,
        )
        for c in components
    ]

    # Cache the result (longer TTL since components are static)
    await cache_set(cache_key, [r.model_dump() for r in result], ttl=3600)

    return result


@app.get("/api/v1/components/categories", tags=["Components"])
def list_categories():
    """List component categories | قائمة فئات المكونات"""
    return [
        {
            "value": cat.value,
            "name": cat.value.replace("_", " ").title(),
            "name_ar": {
                "form": "نموذج",
                "display": "عرض",
                "layout": "تخطيط",
                "chart": "رسم بياني",
                "agricultural": "زراعي",
                "navigation": "تنقل",
                "data": "بيانات",
            }.get(cat.value, cat.value),
        }
        for cat in ComponentCategory
    ]


@app.get("/api/v1/components/{component_name}", response_model=ComponentResponse, tags=["Components"])
def get_component(component_name: str):
    """Get component by name | الحصول على مكون بالاسم"""
    component = lowcode_engine.get_component(component_name)

    if not component:
        raise ResourceNotFoundError(resource_type="Component", resource_id=component_name)

    return ComponentResponse(
        component_id=component.component_id,
        name=component.name,
        name_ar=component.name_ar,
        category=component.category.value,
        description=component.description,
        description_ar=component.description_ar,
        props=[{"name": p.name, "type": p.type, "default": p.default} for p in component.props],
        slots=[{"name": s.name, "title": s.name_ar} for s in component.slots],
        events=[{"name": e.name, "description": e.description} for e in component.events],
        is_container=component.is_container,
        icon=component.icon,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Data Model Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/models", response_model=DataModelResponse, tags=["Data Models"])
async def create_data_model(request: DataModelCreateRequest):
    """Create a data model | إنشاء نموذج بيانات"""
    model_id = str(uuid4())
    now = datetime.utcnow()

    # Parse fields - keep as dict for internal storage
    fields = []
    for field_data in request.fields:
        field_dict = {
            "name": field_data["name"],
            "name_ar": field_data.get("name_ar"),
            "field_type": field_data.get("field_type", "text"),
            "required": field_data.get("required", False),
            "default_value": field_data.get("default_value"),
            "options": field_data.get("options"),
            "validation": field_data.get("validation"),
        }
        fields.append(field_dict)

    model = InternalDataModel(
        id=model_id,
        name=request.name,
        name_ar=request.name_ar,
        description=request.description,
        description_ar=request.description_ar,
        fields=fields,
        created_at=now,
        updated_at=now,
    )

    data_models[model_id] = model

    return DataModelResponse(
        id=model.id,
        name=model.name,
        name_ar=model.name_ar,
        description=model.description,
        description_ar=model.description_ar,
        fields=model.fields,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


@app.get("/api/v1/models", response_model=list[DataModelResponse], tags=["Data Models"])
def list_data_models(
    tenant_id: str = Query(...),
    limit: int = Query(50, ge=1, le=200),
):
    """List data models | قائمة نماذج البيانات"""
    results = list(data_models.values())[:limit]

    return [
        DataModelResponse(
            id=m.id,
            name=m.name,
            name_ar=m.name_ar,
            description=m.description,
            description_ar=m.description_ar,
            fields=m.fields,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        for m in results
    ]


@app.get("/api/v1/models/{model_id}", response_model=DataModelResponse, tags=["Data Models"])
def get_data_model(model_id: str):
    """Get data model by ID | الحصول على نموذج بيانات بالمعرف"""
    if model_id not in data_models:
        raise ResourceNotFoundError(resource_type="Data model", resource_id=model_id)

    m = data_models[model_id]
    return DataModelResponse(
        id=m.id,
        name=m.name,
        name_ar=m.name_ar,
        description=m.description,
        description_ar=m.description_ar,
        fields=m.fields,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Page Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/pages", response_model=PageResponse, tags=["Pages"])
async def create_page(request: PageCreateRequest):
    """Create a page | إنشاء صفحة"""
    page_id = str(uuid4())
    now = datetime.utcnow()

    # Parse blocks using internal format
    blocks = []
    for block_data in request.blocks:
        block = InternalBlock(
            id=block_data.get("id", str(uuid4())),
            component_name=block_data["component_name"],
            props=block_data.get("props", {}),
            children=block_data.get("children", []),
            conditions=block_data.get("conditions"),
            loop=block_data.get("loop"),
        )
        blocks.append(block)

    page = InternalPage(
        id=page_id,
        name=request.name,
        name_ar=request.name_ar,
        description=request.description,
        route=request.route,
        blocks=blocks,
        data_model_id=request.data_model_id,
        is_published=False,
        version=1,
        created_at=now,
        updated_at=now,
    )

    pages[page_id] = page

    return PageResponse(
        id=page.id,
        name=page.name,
        name_ar=page.name_ar,
        description=page.description,
        route=page.route,
        blocks=[{"id": b.id, "component_name": b.component_name, "props": b.props, "children": b.children} for b in page.blocks],
        data_model_id=page.data_model_id,
        is_published=page.is_published,
        version=page.version,
        created_at=page.created_at,
        updated_at=page.updated_at,
    )


@app.get("/api/v1/pages", response_model=list[PageResponse], tags=["Pages"])
def list_pages(
    tenant_id: str = Query(...),
    is_published: bool | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """List pages | قائمة الصفحات"""
    results = list(pages.values())

    if is_published is not None:
        results = [p for p in results if p.is_published == is_published]

    return [
        PageResponse(
            id=p.id,
            name=p.name,
            name_ar=p.name_ar,
            description=p.description,
            route=p.route,
            blocks=[{"id": b.id, "component_name": b.component_name, "props": b.props, "children": b.children} for b in p.blocks],
            data_model_id=p.data_model_id,
            is_published=p.is_published,
            version=p.version,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in results[:limit]
    ]


@app.get("/api/v1/pages/{page_id}", response_model=PageResponse, tags=["Pages"])
async def get_page(page_id: str):
    """Get page by ID | الحصول على صفحة بالمعرف"""
    cache_key = f"lowcode:page:{page_id}"

    # Try to get from cache first
    cached = await cache_get(cache_key)
    if cached:
        return PageResponse(**cached)

    if page_id not in pages:
        raise ResourceNotFoundError(resource_type="Page", resource_id=page_id)

    p = pages[page_id]
    response = PageResponse(
        id=p.id,
        name=p.name,
        name_ar=p.name_ar,
        description=p.description,
        route=p.route,
        blocks=[{"id": b.id, "component_name": b.component_name, "props": b.props, "children": b.children} for b in p.blocks],
        data_model_id=p.data_model_id,
        is_published=p.is_published,
        version=p.version,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )

    # Cache the result
    await cache_set(cache_key, response.model_dump(), ttl=300)

    return response


@app.post("/api/v1/pages/{page_id}/publish", response_model=PageResponse, tags=["Pages"])
async def publish_page(page_id: str):
    """Publish a page | نشر صفحة"""
    if page_id not in pages:
        raise ResourceNotFoundError(resource_type="Page", resource_id=page_id)

    p = pages[page_id]
    p.is_published = True
    p.updated_at = datetime.utcnow()

    # Invalidate cache for this page
    await cache_delete(f"lowcode:page:{page_id}")

    return PageResponse(
        id=p.id,
        name=p.name,
        name_ar=p.name_ar,
        description=p.description,
        route=p.route,
        blocks=[{"id": b.id, "component_name": b.component_name, "props": b.props, "children": b.children} for b in p.blocks],
        data_model_id=p.data_model_id,
        is_published=p.is_published,
        version=p.version,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


@app.get("/api/v1/pages/{page_id}/render", response_model=PageRenderResponse, tags=["Pages"])
def render_page(page_id: str, data: str | None = Query(None)):
    """
    Render a page with data

    عرض صفحة مع البيانات
    """
    if page_id not in pages:
        raise ResourceNotFoundError(resource_type="Page", resource_id=page_id)

    p = pages[page_id]

    # Render blocks (simplified)
    rendered_blocks = []
    for block in p.blocks:
        component = lowcode_engine.get_component(block.component_name)
        rendered_blocks.append({
            "id": block.id,
            "component_name": block.component_name,
            "component_title": component.name if component else block.component_name,
            "component_title_ar": component.name_ar if component else None,
            "props": block.props,
            "children": block.children,
        })

    return PageRenderResponse(
        page_id=p.id,
        name=p.name,
        route=p.route,
        rendered_blocks=rendered_blocks,
        data=None,  # Would load from data model
    )


# ═══════════════════════════════════════════════════════════════════════════════
# AI Suggestion Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/ai/suggest", response_model=AISuggestionResponse, tags=["AI"])
async def suggest_components(request: AISuggestionRequest):
    """
    AI-powered component suggestions based on page description

    اقتراحات مكونات مدعومة بالذكاء الاصطناعي بناءً على وصف الصفحة
    """
    # Simple keyword-based suggestion
    suggestions = []
    desc_lower = request.description.lower()

    # Map keywords to components
    keyword_components = {
        ("map", "field", "location", "حقل", "موقع"): "field_map",
        ("crop", "plant", "محصول", "نبات"): "crop_selector",
        ("irrigation", "water", "ري", "ماء"): "irrigation_scheduler",
        ("sensor", "reading", "مستشعر", "قراءة"): "sensor_display",
        ("health", "ndvi", "صحة"): "crop_health_card",
        ("advisor", "recommendation", "مستشار", "توصية"): "ai_advisor",
    }

    for keywords, component_id in keyword_components.items():
        if any(kw in desc_lower or kw in request.description for kw in keywords):
            component = lowcode_engine.get_component(component_id)
            if component:
                suggestions.append({
                    "component_id": component_id,
                    "component_name": component.name,
                    "component_name_ar": component.name_ar,
                    "confidence": 0.85,
                    "reason": f"Matches keywords in description",
                })

    return AISuggestionResponse(
        suggestions=suggestions,
        reasoning=f"Based on your description, I recommend these components for building a {request.description[:50]}...",
        reasoning_ar=f"بناءً على وصفك، أوصي بهذه المكونات لبناء {request.description_ar or request.description[:50]}...",
        confidence=0.85 if suggestions else 0.5,
    )


@app.get("/api/v1/ai/templates", tags=["AI"])
def list_templates():
    """List available page templates | قائمة قوالب الصفحات المتاحة"""
    return [
        {
            "id": "field-dashboard",
            "name": "Field Dashboard",
            "name_ar": "لوحة تحكم الحقل",
            "description": "Dashboard showing field health, weather, and irrigation status",
            "description_ar": "لوحة تحكم تعرض صحة الحقل والطقس وحالة الري",
            "components": ["field_map", "sensor_display", "crop_health_card", "ai_advisor"],
        },
        {
            "id": "farm-overview",
            "name": "Farm Overview",
            "name_ar": "نظرة عامة على المزرعة",
            "description": "Overview of all fields in a farm with key metrics",
            "description_ar": "نظرة عامة على جميع الحقول في المزرعة مع المقاييس الرئيسية",
            "components": ["field_map", "crop_selector", "sensor_display"],
        },
        {
            "id": "irrigation-planner",
            "name": "Irrigation Planner",
            "name_ar": "مخطط الري",
            "description": "Plan and schedule irrigation for fields",
            "description_ar": "تخطيط وجدولة الري للحقول",
            "components": ["irrigation_scheduler", "sensor_display", "ai_advisor"],
        },
    ]


@app.post("/api/v1/ai/generate-page", response_model=PageResponse, tags=["AI"])
async def generate_page_from_template(
    template_id: str = Query(...),
    name: str = Query(...),
    name_ar: str | None = Query(None),
    tenant_id: str = Query(...),
):
    """
    Generate a page from a template

    إنشاء صفحة من قالب
    """
    templates = {
        "field-dashboard": {
            "components": ["field_map", "sensor_display", "crop_health_card", "ai_advisor"],
            "route": "/dashboard/field",
        },
        "farm-overview": {
            "components": ["field_map", "crop_selector", "sensor_display"],
            "route": "/dashboard/farm",
        },
        "irrigation-planner": {
            "components": ["irrigation_scheduler", "sensor_display", "ai_advisor"],
            "route": "/irrigation/plan",
        },
    }

    if template_id not in templates:
        raise ResourceNotFoundError(resource_type="Template", resource_id=template_id)

    template = templates[template_id]
    page_id = str(uuid4())
    now = datetime.utcnow()

    # Generate blocks from template using internal format
    blocks = []
    for comp_name in template["components"]:
        block = InternalBlock(
            id=str(uuid4()),
            component_name=comp_name,
            props={},
            children=[],
        )
        blocks.append(block)

    page = InternalPage(
        id=page_id,
        name=name,
        name_ar=name_ar,
        description=f"Generated from template: {template_id}",
        route=f"{template['route']}/{page_id[:8]}",
        blocks=blocks,
        is_published=False,
        version=1,
        created_at=now,
        updated_at=now,
    )

    pages[page_id] = page

    return PageResponse(
        id=page.id,
        name=page.name,
        name_ar=page.name_ar,
        description=page.description,
        route=page.route,
        blocks=[{"id": b.id, "component_name": b.component_name, "props": b.props, "children": b.children} for b in page.blocks],
        data_model_id=page.data_model_id,
        is_published=page.is_published,
        version=page.version,
        created_at=page.created_at,
        updated_at=page.updated_at,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Metrics Endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Prometheus-compatible metrics"""
    return f"""# HELP lowcode_components_total Total number of registered components
# TYPE lowcode_components_total gauge
lowcode_components_total {len(lowcode_engine.list_components())}

# HELP lowcode_data_models_total Total number of data models
# TYPE lowcode_data_models_total gauge
lowcode_data_models_total {len(data_models)}

# HELP lowcode_pages_total Total number of pages
# TYPE lowcode_pages_total gauge
lowcode_pages_total {len(pages)}

# HELP lowcode_pages_published Published pages
# TYPE lowcode_pages_published gauge
lowcode_pages_published {len([p for p in pages.values() if p.is_published])}
"""


if __name__ == "__main__":
    import uvicorn
    # Use HOST env var for flexibility; 0.0.0.0 for containers, 127.0.0.1 for local dev
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=SERVICE_PORT)
