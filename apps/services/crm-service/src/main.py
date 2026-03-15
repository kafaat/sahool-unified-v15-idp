"""
SAHOOL Farmer CRM Service
==========================
Customer Relationship Management for farmers.

Inspired by: CordysCRM
Features:
- Farmer lifecycle management
- Harvest deal pipeline
- Interaction tracking
- Natural language queries (SQLBot-inspired)

Port: 8131
"""

import hashlib
import json
import os
import re
import sys
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime, timezone
from typing import Any
from uuid import uuid4

import redis.asyncio as redis_client
import structlog
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette import status

# Authentication imports
from shared.auth.dependencies import get_current_user
from shared.auth.models import User
from shared.middleware.tenant_context import TenantContextMiddleware

# Add project root to path
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
)

from shared.crm import (
    DealStage,
    Farmer,
    FarmerCRMService,
    FarmerQueryBot,
    FarmerStatus,
    HarvestDeal,
    Interaction,
    InteractionType,
)

# Service configuration
SERVICE_NAME = "crm-service"
SERVICE_NAME_AR = "خدمة إدارة علاقات المزارعين"
SERVICE_VERSION = "16.0.0"
SERVICE_PORT = 8131

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


class DuplicateResourceError(Exception):
    """Raised when attempting to create a duplicate resource"""

    def __init__(self, resource_type: str, identifier: str):
        self.resource_type = resource_type
        self.identifier = identifier
        self.message = f"{resource_type} already exists: {identifier}"
        super().__init__(self.message)


class InvalidQueryError(Exception):
    """Raised when a natural language query is invalid"""

    def __init__(self, reason: str):
        self.reason = reason
        self.message = f"Invalid query: {reason}"
        super().__init__(self.message)


def get_request_id(request: Request) -> str | None:
    """Extract or generate request ID from request"""
    return getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID")


# ═══════════════════════════════════════════════════════════════════════════════
# NLQ Security Configuration
# ═══════════════════════════════════════════════════════════════════════════════

# Maximum query length to prevent abuse
MAX_QUERY_LENGTH = 500

# Maximum results to return to prevent data exfiltration
MAX_RESULTS = 100


def sanitize_query(query: str) -> str:
    """
    Remove potentially dangerous patterns from NLQ queries.

    إزالة الأنماط الخطيرة المحتملة من استعلامات اللغة الطبيعية

    Args:
        query: Raw query string from user

    Returns:
        Sanitized query string with dangerous patterns removed
    """
    # Remove SQL-like keywords that could indicate injection attempts
    dangerous_patterns = [
        r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE)\b",
        r"[;\-\-]",  # SQL comment/injection patterns
        r"[\x00-\x1f]",  # Control characters
    ]
    sanitized = query
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
    return sanitized.strip()


def check_query_complexity(query: str) -> bool:
    """
    Check if query complexity is within acceptable limits to prevent DoS.

    التحقق من أن تعقيد الاستعلام ضمن الحدود المقبولة لمنع هجمات رفض الخدمة

    Args:
        query: Query string to check

    Returns:
        True if query complexity is acceptable, False otherwise
    """
    # Check for too many conditions (and/or in English and Arabic)
    condition_words = ["and", "or", "و", "أو"]
    condition_count = sum(query.lower().count(w) for w in condition_words)
    return condition_count <= 5


# ═══════════════════════════════════════════════════════════════════════════════
# Event Publishing Helper
# ═══════════════════════════════════════════════════════════════════════════════


async def publish_event(subject: str, data: dict) -> None:
    """
    Publish an event to NATS.

    نشر حدث إلى NATS

    Args:
        subject: Event subject (e.g., "sahool.tenant_id.crm.farmer.created")
        data: Event payload dictionary
    """
    if app.state.publisher:
        try:
            await app.state.publisher.publish(subject, json.dumps(data).encode())
            logger.info("event_published", subject=subject, event_type=data.get("event_type"))
        except Exception as e:
            logger.error("event_publish_failed", subject=subject, error=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Request/Response Models
# ═══════════════════════════════════════════════════════════════════════════════


class FarmerCreateRequest(BaseModel):
    """Request to create a farmer"""

    name: str = Field(..., min_length=2, max_length=100)
    name_ar: str | None = Field(None, max_length=100)
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    email: EmailStr | None = None
    national_id: str | None = None
    farm_location: str | None = None
    farm_location_ar: str | None = None
    farm_size_hectares: float | None = Field(None, ge=0)
    primary_crops: list[str] = []
    tenant_id: str


class FarmerUpdateRequest(BaseModel):
    """Request to update a farmer"""

    name: str | None = Field(None, min_length=2, max_length=100)
    name_ar: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, pattern=r"^\+?[0-9]{10,15}$")
    email: EmailStr | None = None
    farm_location: str | None = None
    farm_location_ar: str | None = None
    farm_size_hectares: float | None = Field(None, ge=0)
    primary_crops: list[str] | None = None
    farmer_status: str | None = None
    tags: list[str] | None = None


class FarmerResponse(BaseModel):
    """Farmer response model"""

    id: str
    name: str
    name_ar: str | None
    phone: str
    email: str | None
    national_id: str | None
    farm_location: str | None
    farm_location_ar: str | None
    farm_size_hectares: float | None
    primary_crops: list[str]
    status: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    last_interaction_at: datetime | None


class HarvestDealCreateRequest(BaseModel):
    """Request to create a harvest deal"""

    farmer_id: str
    crop_type: str
    crop_type_ar: str | None = None
    expected_quantity_tons: float = Field(..., gt=0)
    expected_harvest_date: date
    price_per_ton: float | None = Field(None, gt=0)
    notes: str | None = None
    notes_ar: str | None = None


class HarvestDealResponse(BaseModel):
    """Harvest deal response model"""

    id: str
    farmer_id: str
    crop_type: str
    crop_type_ar: str | None
    expected_quantity_tons: float
    actual_quantity_tons: float | None
    expected_harvest_date: date
    actual_harvest_date: date | None
    price_per_ton: float | None
    total_value: float | None
    stage: str
    notes: str | None
    notes_ar: str | None
    created_at: datetime
    updated_at: datetime


class InteractionCreateRequest(BaseModel):
    """Request to log an interaction"""

    farmer_id: str
    interaction_type: str = Field(..., description="Type: call, visit, whatsapp, sms, email")
    subject: str
    subject_ar: str | None = None
    notes: str | None = None
    notes_ar: str | None = None
    outcome: str | None = None
    follow_up_date: date | None = None


class InteractionResponse(BaseModel):
    """Interaction response model"""

    id: str
    farmer_id: str
    interaction_type: str
    subject: str
    subject_ar: str | None
    notes: str | None
    notes_ar: str | None
    outcome: str | None
    follow_up_date: date | None
    created_at: datetime
    created_by: str | None


class QueryRequest(BaseModel):
    """Natural language query request"""

    query: str = Field(..., description="Natural language query in English or Arabic")
    tenant_id: str


class QueryResponse(BaseModel):
    """Query response model"""

    query: str
    interpreted_as: str
    interpreted_as_ar: str | None
    results: list[dict[str, Any]]
    result_count: int
    execution_time_ms: int


class PipelineStatsResponse(BaseModel):
    """Pipeline statistics response"""

    total_deals: int
    total_value: float
    by_stage: dict[str, dict[str, Any]]
    conversion_rate: float
    average_deal_size: float


# ═══════════════════════════════════════════════════════════════════════════════
# In-memory storage (fallback when database is not available)
# ═══════════════════════════════════════════════════════════════════════════════

farmers: dict[str, Farmer] = {}
deals: dict[str, HarvestDeal] = {}
interactions: dict[str, Interaction] = {}

# Initialize services (for fallback mode)
crm_service = FarmerCRMService()
query_bot = FarmerQueryBot(crm_service)


# ═══════════════════════════════════════════════════════════════════════════════
# Database Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════


def get_crm_repo(request: Request):
    """Get CRM repository from app state."""
    return getattr(request.app.state, "crm_repo", None)


# ═══════════════════════════════════════════════════════════════════════════════
# Authentication Helpers
# ═══════════════════════════════════════════════════════════════════════════════


def validate_tenant_access(user: User, tenant_id: str) -> None:
    """
    Validate that the authenticated user has access to the specified tenant.
    Raises TenantAccessDeniedError if tenant_id does not match user's tenant_id.

    التحقق من أن المستخدم المصادق عليه لديه حق الوصول إلى المستأجر المحدد.
    """
    if user.tenant_id != tenant_id:
        raise TenantAccessDeniedError(tenant_id=tenant_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Lifespan Management
# ═══════════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("service_starting", service=SERVICE_NAME, version=SERVICE_VERSION)

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

    # Initialize database connection (if available)
    db_url = os.getenv("DATABASE_URL")
    # Enforce sslmode for non-development database connections
    if db_url and os.getenv("ENVIRONMENT", "development") != "development":
        if "sslmode" not in db_url:
            # Use sslmode=disable for PgBouncer (port 6432) which does not support SSL
            ssl_mode = "disable" if ":6432" in db_url else "require"
            db_url += f"?sslmode={ssl_mode}" if "?" not in db_url else f"&sslmode={ssl_mode}"
    if db_url:
        try:
            from pathlib import Path

            import asyncpg

            from .db import CRMRepository

            app.state.db_pool = await asyncpg.create_pool(
                db_url,
                min_size=2,
                max_size=10,
                command_timeout=60,
            )
            app.state.db_connected = True

            # Initialize CRM repository
            app.state.crm_repo = CRMRepository(app.state.db_pool)

            # Run migrations
            migrations_dir = Path(__file__).parent.parent / "migrations"
            if migrations_dir.exists():
                await app.state.crm_repo.run_migrations(str(migrations_dir))
                logger.info("database_migrations_completed")

            logger.info("database_connected_and_initialized")
        except Exception as e:
            logger.error("database_connection_failed", error=str(e))
            app.state.db_pool = None
            app.state.db_connected = False
            app.state.crm_repo = None
    else:
        app.state.db_pool = None
        app.state.db_connected = False
        app.state.crm_repo = None
        logger.warning("No DATABASE_URL configured, using in-memory storage")

    logger.info("service_ready", service=SERVICE_NAME, port=SERVICE_PORT)

    yield

    # Shutdown
    if hasattr(app.state, "redis") and app.state.redis:
        await app.state.redis.close()
    if hasattr(app.state, "publisher") and app.state.publisher:
        await app.state.publisher.close()
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
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
    title="SAHOOL Farmer CRM Service",
    description="Customer Relationship Management for farmers | إدارة علاقات المزارعين",
    version=SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup unified error handling
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    setup_exception_handlers(app)
    add_request_id_middleware(app)
except ImportError:
    pass

# ═══════════════════════════════════════════════════════════════════════════════
# Rate Limiting Configuration
# ═══════════════════════════════════════════════════════════════════════════════

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors (429)"""
    from fastapi.responses import JSONResponse

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
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors (400)"""
    from fastapi.responses import JSONResponse

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
async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
    """Handle resource not found errors (404)"""
    from fastapi.responses import JSONResponse

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
async def tenant_access_denied_handler(request: Request, exc: TenantAccessDeniedError):
    """Handle tenant access denied errors (403)"""
    from fastapi.responses import JSONResponse

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


@app.exception_handler(DuplicateResourceError)
async def duplicate_resource_handler(request: Request, exc: DuplicateResourceError):
    """Handle duplicate resource errors (409)"""
    from fastapi.responses import JSONResponse

    request_id = get_request_id(request)
    logger.warning(
        "duplicate_resource",
        path=request.url.path,
        request_id=request_id,
        resource_type=exc.resource_type,
        identifier=exc.identifier,
    )
    return JSONResponse(
        status_code=409,
        content=ErrorResponse(
            error="Resource already exists",
            error_ar="المورد موجود بالفعل",
            error_code="CONFLICT",
            detail=exc.message,
            request_id=request_id,
        ).model_dump(),
    )


@app.exception_handler(InvalidQueryError)
async def invalid_query_handler(request: Request, exc: InvalidQueryError):
    """Handle invalid query errors (400)"""
    from fastapi.responses import JSONResponse

    request_id = get_request_id(request)
    logger.warning(
        "invalid_query",
        path=request.url.path,
        request_id=request_id,
        reason=exc.reason,
    )
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error="Invalid query",
            error_ar="استعلام غير صالح",
            error_code="INVALID_QUERY",
            detail=exc.message,
            request_id=request_id,
        ).model_dump(),
    )


@app.exception_handler(ServiceUnavailableError)
async def service_unavailable_handler(request: Request, exc: ServiceUnavailableError):
    """Handle service unavailable errors (503)"""
    from fastapi.responses import JSONResponse

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
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format"""
    from fastapi.responses import JSONResponse

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
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions (500)"""
    from fastapi.responses import JSONResponse

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
def readiness():
    """Readiness probe"""
    return {
        "status": "ok",
        "database": getattr(app.state, "db_connected", False),
        "redis": getattr(app.state, "redis_connected", False),
        "nats": getattr(app.state, "nats_connected", False),
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
        "farmers_count": len(farmers),
        "deals_count": len(deals),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Farmer Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/api/v1/farmers", response_model=FarmerResponse, tags=["Farmers"])
@limiter.limit("30/minute")
async def create_farmer(
    request: Request,
    farmer_data: FarmerCreateRequest,
    user: User = Depends(get_current_user),
):
    """Create a new farmer | إنشاء مزارع جديد"""
    # Validate tenant access
    validate_tenant_access(user, farmer_data.tenant_id)

    crm_repo = get_crm_repo(request)

    if crm_repo:
        # Use database
        data = await crm_repo.farmers.create(
            tenant_id=farmer_data.tenant_id,
            name=farmer_data.name,
            name_ar=farmer_data.name_ar,
            phone=farmer_data.phone,
            email=farmer_data.email,
            national_id=farmer_data.national_id,
            farm_size_hectares=farmer_data.farm_size_hectares,
            location=farmer_data.farm_location,
            location_ar=farmer_data.farm_location_ar,
            crops=farmer_data.primary_crops,
        )

        # Publish farmer created event
        await publish_event(
            f"sahool.{farmer_data.tenant_id}.crm.farmer.created",
            {
                "event_type": "farmer.created",
                "farmer_id": data["id"],
                "tenant_id": farmer_data.tenant_id,
                "name": data["name"],
                "name_ar": data["name_ar"],
                "phone": data["phone"],
                "status": data["status"],
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        return FarmerResponse(
            id=data["id"],
            name=data["name"],
            name_ar=data["name_ar"],
            phone=data["phone"],
            email=data["email"],
            national_id=data["national_id"],
            farm_location=data["location"],
            farm_location_ar=data["location_ar"],
            farm_size_hectares=data["farm_size_hectares"],
            primary_crops=data["crops"] or [],
            status=data["status"],
            tags=data["tags"] or [],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            last_interaction_at=data["last_interaction_at"],
        )
    else:
        # Fallback to in-memory
        farmer_id = str(uuid4())
        now = datetime.now(UTC)

        farmer = Farmer(
            id=farmer_id,
            name=farmer_data.name,
            name_ar=farmer_data.name_ar,
            phone=farmer_data.phone,
            email=farmer_data.email,
            national_id=farmer_data.national_id,
            farm_location=farmer_data.farm_location,
            farm_location_ar=farmer_data.farm_location_ar,
            farm_size_hectares=farmer_data.farm_size_hectares,
            primary_crops=farmer_data.primary_crops,
            status=FarmerStatus.LEAD,
            tags=[],
            tenant_id=farmer_data.tenant_id,
            created_at=now,
            updated_at=now,
        )

        farmers[farmer_id] = farmer

        # Publish farmer created event
        await publish_event(
            f"sahool.{farmer.tenant_id}.crm.farmer.created",
            {
                "event_type": "farmer.created",
                "farmer_id": farmer.id,
                "tenant_id": farmer.tenant_id,
                "name": farmer.name,
                "name_ar": farmer.name_ar,
                "phone": farmer.phone,
                "status": farmer.status.value,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        return FarmerResponse(
            id=farmer.id,
            name=farmer.name,
            name_ar=farmer.name_ar,
            phone=farmer.phone,
            email=farmer.email,
            national_id=farmer.national_id,
            farm_location=farmer.farm_location,
            farm_location_ar=farmer.farm_location_ar,
            farm_size_hectares=farmer.farm_size_hectares,
            primary_crops=farmer.primary_crops,
            status=farmer.status.value,
            tags=farmer.tags,
            created_at=farmer.created_at,
            updated_at=farmer.updated_at,
            last_interaction_at=farmer.last_interaction_at,
        )


@app.get("/api/v1/farmers", response_model=list[FarmerResponse], tags=["Farmers"])
@limiter.limit("60/minute")
async def list_farmers(
    request: Request,
    tenant_id: str = Query(...),
    farmer_status: str | None = Query(None, alias="status"),
    search: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
):
    """List farmers | قائمة المزارعين"""
    # Validate tenant access
    validate_tenant_access(user, tenant_id)

    crm_repo = get_crm_repo(request)

    if crm_repo:
        # Use database
        farmers_data = await crm_repo.farmers.list(
            tenant_id=tenant_id,
            status=farmer_status,
            search=search,
            limit=limit,
            offset=offset,
        )

        return [
            FarmerResponse(
                id=f["id"],
                name=f["name"],
                name_ar=f["name_ar"],
                phone=f["phone"],
                email=f["email"],
                national_id=f["national_id"],
                farm_location=f["location"],
                farm_location_ar=f["location_ar"],
                farm_size_hectares=f["farm_size_hectares"],
                primary_crops=f["crops"] or [],
                status=f["status"],
                tags=f["tags"] or [],
                created_at=f["created_at"],
                updated_at=f["updated_at"],
                last_interaction_at=f["last_interaction_at"],
            )
            for f in farmers_data
        ]
    else:
        # Fallback to in-memory
        # Filter by tenant_id
        results = [f for f in farmers.values() if f.tenant_id == tenant_id]

        # Filter by status
        if farmer_status:
            results = [f for f in results if f.status.value == farmer_status]

        # Search by name or phone
        if search:
            search_lower = search.lower()
            results = [
                f
                for f in results
                if search_lower in f.name.lower() or (f.name_ar and search_lower in f.name_ar) or search in f.phone
            ]

        # Paginate
        results = results[offset : offset + limit]

        return [
            FarmerResponse(
                id=f.id,
                name=f.name,
                name_ar=f.name_ar,
                phone=f.phone,
                email=f.email,
                national_id=f.national_id,
                farm_location=f.farm_location,
                farm_location_ar=f.farm_location_ar,
                farm_size_hectares=f.farm_size_hectares,
                primary_crops=f.primary_crops,
                status=f.status.value,
                tags=f.tags,
                created_at=f.created_at,
                updated_at=f.updated_at,
                last_interaction_at=f.last_interaction_at,
            )
            for f in results
        ]


@app.get("/api/v1/farmers/{farmer_id}", response_model=FarmerResponse, tags=["Farmers"])
@limiter.limit("60/minute")
async def get_farmer(
    request: Request,
    farmer_id: str,
    tenant_id: str = Query(..., description="Tenant ID for isolation"),
    user: User = Depends(get_current_user),
):
    """Get farmer by ID | الحصول على مزارع بالمعرف"""
    # Validate tenant access from query parameter
    validate_tenant_access(user, tenant_id)

    # Try to get from cache first
    cache_key = f"crm:farmer:{tenant_id}:{farmer_id}"
    cached = await cache_get(cache_key)
    if cached:
        return FarmerResponse(**cached)

    crm_repo = get_crm_repo(request)

    if crm_repo:
        # Use database
        data = await crm_repo.farmers.get_by_id(farmer_id)
        if not data:
            raise ResourceNotFoundError(resource_type="Farmer", resource_id=farmer_id)

        # Verify farmer belongs to requested tenant
        if data["tenant_id"] != tenant_id:
            raise TenantAccessDeniedError(tenant_id=tenant_id)

        response = FarmerResponse(
            id=data["id"],
            name=data["name"],
            name_ar=data["name_ar"],
            phone=data["phone"],
            email=data["email"],
            national_id=data["national_id"],
            farm_location=data["location"],
            farm_location_ar=data["location_ar"],
            farm_size_hectares=data["farm_size_hectares"],
            primary_crops=data["crops"] or [],
            status=data["status"],
            tags=data["tags"] or [],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            last_interaction_at=data["last_interaction_at"],
        )
        # Cache the result
        await cache_set(cache_key, response.model_dump(), ttl=300)
        return response
    else:
        # Fallback to in-memory
        if farmer_id not in farmers:
            raise ResourceNotFoundError(resource_type="Farmer", resource_id=farmer_id)

        f = farmers[farmer_id]

        # Verify farmer belongs to requested tenant
        if f.tenant_id != tenant_id:
            raise TenantAccessDeniedError(tenant_id=tenant_id)

        response = FarmerResponse(
            id=f.id,
            name=f.name,
            name_ar=f.name_ar,
            phone=f.phone,
            email=f.email,
            national_id=f.national_id,
            farm_location=f.farm_location,
            farm_location_ar=f.farm_location_ar,
            farm_size_hectares=f.farm_size_hectares,
            primary_crops=f.primary_crops,
            status=f.status.value,
            tags=f.tags,
            created_at=f.created_at,
            updated_at=f.updated_at,
            last_interaction_at=f.last_interaction_at,
        )
        # Cache the result
        await cache_set(cache_key, response.model_dump(), ttl=300)
        return response


@app.patch("/api/v1/farmers/{farmer_id}", response_model=FarmerResponse, tags=["Farmers"])
@limiter.limit("60/minute")
async def update_farmer(
    request: Request,
    farmer_id: str,
    update_data: FarmerUpdateRequest,
    user: User = Depends(get_current_user),
):
    """Update farmer | تحديث مزارع"""
    crm_repo = get_crm_repo(request)

    if crm_repo:
        # Use database
        existing = await crm_repo.farmers.get_by_id(farmer_id)
        if not existing:
            raise ResourceNotFoundError(resource_type="Farmer", resource_id=farmer_id)

        # Validate tenant access
        validate_tenant_access(user, existing["tenant_id"])

        # Track old status for status change event
        old_status = existing["status"]

        # Build update dict from non-None fields
        update_dict = {}
        if update_data.name is not None:
            update_dict["name"] = update_data.name
        if update_data.name_ar is not None:
            update_dict["name_ar"] = update_data.name_ar
        if update_data.phone is not None:
            update_dict["phone"] = update_data.phone
        if update_data.email is not None:
            update_dict["email"] = update_data.email
        if update_data.farm_location is not None:
            update_dict["location"] = update_data.farm_location
        if update_data.farm_location_ar is not None:
            update_dict["location_ar"] = update_data.farm_location_ar
        if update_data.farm_size_hectares is not None:
            update_dict["farm_size_hectares"] = update_data.farm_size_hectares
        if update_data.primary_crops is not None:
            update_dict["crops"] = update_data.primary_crops
        if update_data.status is not None:
            update_dict["status"] = update_data.status
        if update_data.tags is not None:
            update_dict["tags"] = update_data.tags

        data = await crm_repo.farmers.update(farmer_id, update_dict)

        # Invalidate cache for this farmer
        await cache_delete(f"crm:farmer:{existing['tenant_id']}:{farmer_id}")

        # Publish farmer updated event
        await publish_event(
            f"sahool.{existing['tenant_id']}.crm.farmer.updated",
            {
                "event_type": "farmer.updated",
                "farmer_id": data["id"],
                "tenant_id": existing["tenant_id"],
                "name": data["name"],
                "name_ar": data["name_ar"],
                "status": data["status"],
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        # Publish status changed event if status was updated
        if update_data.status is not None and old_status != data["status"]:
            await publish_event(
                f"sahool.{existing['tenant_id']}.crm.farmer.status_changed",
                {
                    "event_type": "farmer.status_changed",
                    "farmer_id": data["id"],
                    "tenant_id": existing["tenant_id"],
                    "old_status": old_status,
                    "new_status": data["status"],
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

        return FarmerResponse(
            id=data["id"],
            name=data["name"],
            name_ar=data["name_ar"],
            phone=data["phone"],
            email=data["email"],
            national_id=data["national_id"],
            farm_location=data["location"],
            farm_location_ar=data["location_ar"],
            farm_size_hectares=data["farm_size_hectares"],
            primary_crops=data["crops"] or [],
            status=data["status"],
            tags=data["tags"] or [],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            last_interaction_at=data["last_interaction_at"],
        )
    else:
        # Fallback to in-memory
        if farmer_id not in farmers:
            raise ResourceNotFoundError(resource_type="Farmer", resource_id=farmer_id)

        f = farmers[farmer_id]

        # Validate tenant access
        validate_tenant_access(user, f.tenant_id)

        # Track old status for status change event
        old_status = f.status

        if update_data.name is not None:
            f.name = update_data.name
        if update_data.name_ar is not None:
            f.name_ar = update_data.name_ar
        if update_data.phone is not None:
            f.phone = update_data.phone
        if update_data.email is not None:
            f.email = update_data.email
        if update_data.farm_location is not None:
            f.farm_location = update_data.farm_location
        if update_data.farm_location_ar is not None:
            f.farm_location_ar = update_data.farm_location_ar
        if update_data.farm_size_hectares is not None:
            f.farm_size_hectares = update_data.farm_size_hectares
        if update_data.primary_crops is not None:
            f.primary_crops = update_data.primary_crops
        if update_data.status is not None:
            f.status = FarmerStatus(update_data.status)
        if update_data.tags is not None:
            f.tags = update_data.tags

        f.updated_at = datetime.now(UTC)

        # Invalidate cache for this farmer
        await cache_delete(f"crm:farmer:{f.tenant_id}:{farmer_id}")

        # Publish farmer updated event
        await publish_event(
            f"sahool.{f.tenant_id}.crm.farmer.updated",
            {
                "event_type": "farmer.updated",
                "farmer_id": f.id,
                "tenant_id": f.tenant_id,
                "name": f.name,
                "name_ar": f.name_ar,
                "status": f.status.value,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        # Publish status changed event if status was updated
        if update_data.status is not None and old_status != f.status:
            await publish_event(
                f"sahool.{f.tenant_id}.crm.farmer.status_changed",
                {
                    "event_type": "farmer.status_changed",
                    "farmer_id": f.id,
                    "tenant_id": f.tenant_id,
                    "old_status": old_status.value,
                    "new_status": f.status.value,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

        return FarmerResponse(
            id=f.id,
            name=f.name,
            name_ar=f.name_ar,
            phone=f.phone,
            email=f.email,
            national_id=f.national_id,
            farm_location=f.farm_location,
            farm_location_ar=f.farm_location_ar,
            farm_size_hectares=f.farm_size_hectares,
            primary_crops=f.primary_crops,
            status=f.status.value,
            tags=f.tags,
            created_at=f.created_at,
            updated_at=f.updated_at,
            last_interaction_at=f.last_interaction_at,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Harvest Deal Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/api/v1/deals", response_model=HarvestDealResponse, tags=["Deals"])
@limiter.limit("30/minute")
async def create_deal(
    request: Request,
    deal_data: HarvestDealCreateRequest,
    user: User = Depends(get_current_user),
):
    """Create a harvest deal | إنشاء صفقة حصاد"""
    crm_repo = get_crm_repo(request)

    if crm_repo:
        # Use database - first verify farmer exists
        farmer_data = await crm_repo.farmers.get_by_id(deal_data.farmer_id)
        if not farmer_data:
            raise ResourceNotFoundError(resource_type="Farmer", resource_id=deal_data.farmer_id)

        # Validate tenant access via farmer's tenant_id
        validate_tenant_access(user, farmer_data["tenant_id"])

        data = await crm_repo.deals.create(
            farmer_id=deal_data.farmer_id,
            crop_type=deal_data.crop_type,
            crop_type_ar=deal_data.crop_type_ar,
            expected_quantity_tons=deal_data.expected_quantity_tons,
            expected_harvest_date=deal_data.expected_harvest_date,
            price_per_ton=deal_data.price_per_ton,
            notes=deal_data.notes,
            notes_ar=deal_data.notes_ar,
        )

        # Invalidate pipeline stats cache
        await cache_delete(f"crm:pipeline_stats:{farmer_data['tenant_id']}")

        # Publish deal created event
        await publish_event(
            f"sahool.{farmer_data['tenant_id']}.crm.deal.created",
            {
                "event_type": "deal.created",
                "deal_id": data["id"],
                "farmer_id": data["farmer_id"],
                "tenant_id": farmer_data["tenant_id"],
                "crop_type": data["crop_type"],
                "crop_type_ar": data["crop_type_ar"],
                "expected_quantity_tons": data["expected_quantity_tons"],
                "expected_harvest_date": data["expected_harvest_date"].isoformat()
                if data["expected_harvest_date"]
                else None,
                "price_per_ton": data["price_per_ton"],
                "stage": data["stage"],
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        return HarvestDealResponse(
            id=data["id"],
            farmer_id=data["farmer_id"],
            crop_type=data["crop_type"],
            crop_type_ar=data["crop_type_ar"],
            expected_quantity_tons=data["expected_quantity_tons"],
            actual_quantity_tons=data["actual_quantity_tons"],
            expected_harvest_date=data["expected_harvest_date"],
            actual_harvest_date=data["actual_harvest_date"],
            price_per_ton=data["price_per_ton"],
            total_value=data["total_value"],
            stage=data["stage"],
            notes=data["notes"],
            notes_ar=data["notes_ar"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )
    else:
        # Fallback to in-memory
        if deal_data.farmer_id not in farmers:
            raise ResourceNotFoundError(resource_type="Farmer", resource_id=deal_data.farmer_id)

        # Validate tenant access via farmer's tenant_id
        farmer = farmers[deal_data.farmer_id]
        validate_tenant_access(user, farmer.tenant_id)

        deal_id = str(uuid4())
        now = datetime.now(UTC)

        deal = HarvestDeal(
            id=deal_id,
            farmer_id=deal_data.farmer_id,
            crop_type=deal_data.crop_type,
            crop_type_ar=deal_data.crop_type_ar,
            expected_quantity_tons=deal_data.expected_quantity_tons,
            expected_harvest_date=deal_data.expected_harvest_date,
            price_per_ton=deal_data.price_per_ton,
            stage=DealStage.PROSPECTING,
            notes=deal_data.notes,
            notes_ar=deal_data.notes_ar,
            created_at=now,
            updated_at=now,
        )

        deals[deal_id] = deal

        # Invalidate pipeline stats cache
        await cache_delete(f"crm:pipeline_stats:{farmer.tenant_id}")

        # Publish deal created event
        await publish_event(
            f"sahool.{farmer.tenant_id}.crm.deal.created",
            {
                "event_type": "deal.created",
                "deal_id": deal.id,
                "farmer_id": deal.farmer_id,
                "tenant_id": farmer.tenant_id,
                "crop_type": deal.crop_type,
                "crop_type_ar": deal.crop_type_ar,
                "expected_quantity_tons": deal.expected_quantity_tons,
                "expected_harvest_date": deal.expected_harvest_date.isoformat(),
                "price_per_ton": deal.price_per_ton,
                "stage": deal.stage.value,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        return HarvestDealResponse(
            id=deal.id,
            farmer_id=deal.farmer_id,
            crop_type=deal.crop_type,
            crop_type_ar=deal.crop_type_ar,
            expected_quantity_tons=deal.expected_quantity_tons,
            actual_quantity_tons=deal.actual_quantity_tons,
            expected_harvest_date=deal.expected_harvest_date,
            actual_harvest_date=deal.actual_harvest_date,
            price_per_ton=deal.price_per_ton,
            total_value=deal.total_value,
            stage=deal.stage.value,
            notes=deal.notes,
            notes_ar=deal.notes_ar,
            created_at=deal.created_at,
            updated_at=deal.updated_at,
        )


@app.get("/api/v1/deals", response_model=list[HarvestDealResponse], tags=["Deals"])
@limiter.limit("60/minute")
async def list_deals(
    request: Request,
    tenant_id: str = Query(...),
    farmer_id: str | None = Query(None),
    stage: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
):
    """List harvest deals | قائمة صفقات الحصاد"""
    # Validate tenant access
    validate_tenant_access(user, tenant_id)

    crm_repo = get_crm_repo(request)

    if crm_repo:
        # Use database
        deals_data = await crm_repo.deals.list(
            tenant_id=tenant_id,
            farmer_id=farmer_id,
            stage=stage,
            limit=limit,
        )

        return [
            HarvestDealResponse(
                id=d["id"],
                farmer_id=d["farmer_id"],
                crop_type=d["crop_type"],
                crop_type_ar=d["crop_type_ar"],
                expected_quantity_tons=d["expected_quantity_tons"],
                actual_quantity_tons=d["actual_quantity_tons"],
                expected_harvest_date=d["expected_harvest_date"],
                actual_harvest_date=d["actual_harvest_date"],
                price_per_ton=d["price_per_ton"],
                total_value=d["total_value"],
                stage=d["stage"],
                notes=d["notes"],
                notes_ar=d["notes_ar"],
                created_at=d["created_at"],
                updated_at=d["updated_at"],
            )
            for d in deals_data
        ]
    else:
        # Fallback to in-memory
        # Filter deals by tenant_id (via farmer's tenant_id)
        results = [d for d in deals.values() if d.farmer_id in farmers and farmers[d.farmer_id].tenant_id == tenant_id]

        if farmer_id:
            results = [d for d in results if d.farmer_id == farmer_id]
        if stage:
            results = [d for d in results if d.stage.value == stage]

        return [
            HarvestDealResponse(
                id=d.id,
                farmer_id=d.farmer_id,
                crop_type=d.crop_type,
                crop_type_ar=d.crop_type_ar,
                expected_quantity_tons=d.expected_quantity_tons,
                actual_quantity_tons=d.actual_quantity_tons,
                expected_harvest_date=d.expected_harvest_date,
                actual_harvest_date=d.actual_harvest_date,
                price_per_ton=d.price_per_ton,
                total_value=d.total_value,
                stage=d.stage.value,
                notes=d.notes,
                notes_ar=d.notes_ar,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in results[:limit]
        ]


@app.patch("/api/v1/deals/{deal_id}/stage", response_model=HarvestDealResponse, tags=["Deals"])
@limiter.limit("60/minute")
async def update_deal_stage(
    request: Request,
    deal_id: str,
    stage: str = Query(...),
    user: User = Depends(get_current_user),
):
    """Update deal stage | تحديث مرحلة الصفقة"""
    crm_repo = get_crm_repo(request)

    if crm_repo:
        # Use database
        deal_data = await crm_repo.deals.get_by_id(deal_id)
        if not deal_data:
            raise ResourceNotFoundError(resource_type="Deal", resource_id=deal_id)

        # Get farmer for tenant validation
        farmer_data = await crm_repo.farmers.get_by_id(deal_data["farmer_id"])
        if not farmer_data:
            raise ResourceNotFoundError(resource_type="Farmer", resource_id=deal_data["farmer_id"])
        validate_tenant_access(user, farmer_data["tenant_id"])

        # Track old stage for event
        old_stage = deal_data["stage"]

        # Update the deal stage
        data = await crm_repo.deals.update_stage(deal_id, stage)

        # Invalidate pipeline stats cache
        await cache_delete(f"crm:pipeline_stats:{farmer_data['tenant_id']}")

        # Publish deal stage advanced event
        await publish_event(
            f"sahool.{farmer_data['tenant_id']}.crm.deal.stage_advanced",
            {
                "event_type": "deal.stage_advanced",
                "deal_id": data["id"],
                "farmer_id": data["farmer_id"],
                "tenant_id": farmer_data["tenant_id"],
                "crop_type": data["crop_type"],
                "old_stage": old_stage,
                "new_stage": data["stage"],
                "expected_quantity_tons": data["expected_quantity_tons"],
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        return HarvestDealResponse(
            id=data["id"],
            farmer_id=data["farmer_id"],
            crop_type=data["crop_type"],
            crop_type_ar=data["crop_type_ar"],
            expected_quantity_tons=data["expected_quantity_tons"],
            actual_quantity_tons=data["actual_quantity_tons"],
            expected_harvest_date=data["expected_harvest_date"],
            actual_harvest_date=data["actual_harvest_date"],
            price_per_ton=data["price_per_ton"],
            total_value=data["total_value"],
            stage=data["stage"],
            notes=data["notes"],
            notes_ar=data["notes_ar"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )
    else:
        # Fallback to in-memory
        if deal_id not in deals:
            raise ResourceNotFoundError(resource_type="Deal", resource_id=deal_id)

        deal = deals[deal_id]

        # Validate tenant access via farmer's tenant_id
        if deal.farmer_id not in farmers:
            raise ResourceNotFoundError(resource_type="Farmer", resource_id=deal.farmer_id)
        farmer = farmers[deal.farmer_id]
        validate_tenant_access(user, farmer.tenant_id)

        # Track old stage for event
        old_stage = deal.stage

        deal.stage = DealStage(stage)
        deal.updated_at = datetime.now(UTC)

        # Invalidate pipeline stats cache
        await cache_delete(f"crm:pipeline_stats:{farmer.tenant_id}")

        # Publish deal stage advanced event
        await publish_event(
            f"sahool.{farmer.tenant_id}.crm.deal.stage_advanced",
            {
                "event_type": "deal.stage_advanced",
                "deal_id": deal.id,
                "farmer_id": deal.farmer_id,
                "tenant_id": farmer.tenant_id,
                "crop_type": deal.crop_type,
                "old_stage": old_stage.value,
                "new_stage": deal.stage.value,
                "expected_quantity_tons": deal.expected_quantity_tons,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        return HarvestDealResponse(
            id=deal.id,
            farmer_id=deal.farmer_id,
            crop_type=deal.crop_type,
            crop_type_ar=deal.crop_type_ar,
            expected_quantity_tons=deal.expected_quantity_tons,
            actual_quantity_tons=deal.actual_quantity_tons,
            expected_harvest_date=deal.expected_harvest_date,
            actual_harvest_date=deal.actual_harvest_date,
            price_per_ton=deal.price_per_ton,
            total_value=deal.total_value,
            stage=deal.stage.value,
            notes=deal.notes,
            notes_ar=deal.notes_ar,
            created_at=deal.created_at,
            updated_at=deal.updated_at,
        )


@app.get("/api/v1/deals/pipeline", response_model=PipelineStatsResponse, tags=["Deals"])
@limiter.limit("60/minute")
async def get_pipeline_stats(
    request: Request,
    tenant_id: str = Query(...),
    user: User = Depends(get_current_user),
):
    """Get pipeline statistics | إحصائيات خط الأنابيب"""
    # Validate tenant access
    validate_tenant_access(user, tenant_id)

    # Try to get from cache first
    cache_key = f"crm:pipeline_stats:{tenant_id}"
    cached = await cache_get(cache_key)
    if cached:
        return PipelineStatsResponse(**cached)

    crm_repo = get_crm_repo(request)

    stage_names_ar = {
        "prospecting": "استكشاف",
        "qualification": "تأهيل",
        "negotiation": "تفاوض",
        "contracted": "متعاقد",
        "delivered": "مسلم",
        "paid": "مدفوع",
        "closed_lost": "خسارة",
    }

    if crm_repo:
        # Use database
        stats = await crm_repo.deals.get_pipeline_stats(tenant_id=tenant_id)

        # Add Arabic names to by_stage
        by_stage = {}
        for stage_value, stage_data in stats.get("by_stage", {}).items():
            by_stage[stage_value] = {
                **stage_data,
                "name_ar": stage_names_ar.get(stage_value, stage_value),
            }

        response = PipelineStatsResponse(
            total_deals=stats.get("total_deals", 0),
            total_value=stats.get("total_value", 0.0),
            by_stage=by_stage,
            conversion_rate=stats.get("conversion_rate", 0.0),
            average_deal_size=stats.get("average_deal_size", 0.0),
        )
    else:
        # Fallback to in-memory
        # Filter deals by tenant_id (via farmer's tenant_id)
        all_deals = [
            d for d in deals.values() if d.farmer_id in farmers and farmers[d.farmer_id].tenant_id == tenant_id
        ]

        by_stage: dict[str, dict[str, Any]] = {}
        for stage in list(DealStage):
            stage_deals = [d for d in all_deals if d.stage == stage]
            total_value = sum((d.price_per_ton or 0) * d.expected_quantity_tons for d in stage_deals)
            by_stage[stage.value] = {
                "count": len(stage_deals),
                "total_value": total_value,
                "name_ar": stage_names_ar.get(stage.value, stage.value),
            }

        total_deals = len(all_deals)
        won_deals = len([d for d in all_deals if d.stage == DealStage.PAID])
        total_value = sum((d.price_per_ton or 0) * d.expected_quantity_tons for d in all_deals)

        response = PipelineStatsResponse(
            total_deals=total_deals,
            total_value=total_value,
            by_stage=by_stage,
            conversion_rate=(won_deals / total_deals * 100) if total_deals > 0 else 0,
            average_deal_size=(total_value / total_deals) if total_deals > 0 else 0,
        )

    # Cache the result (shorter TTL since deals change frequently)
    await cache_set(cache_key, response.model_dump(), ttl=60)

    return response


# ═══════════════════════════════════════════════════════════════════════════════
# Interaction Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/api/v1/interactions", response_model=InteractionResponse, tags=["Interactions"])
@limiter.limit("60/minute")
async def log_interaction(
    request: Request,
    interaction_data: InteractionCreateRequest,
    user: User = Depends(get_current_user),
):
    """Log an interaction with a farmer | تسجيل تفاعل مع مزارع"""
    crm_repo = get_crm_repo(request)

    if crm_repo:
        # Use database - first verify farmer exists
        farmer_data = await crm_repo.farmers.get_by_id(interaction_data.farmer_id)
        if not farmer_data:
            raise ResourceNotFoundError(resource_type="Farmer", resource_id=interaction_data.farmer_id)

        # Validate tenant access via farmer's tenant_id
        validate_tenant_access(user, farmer_data["tenant_id"])

        data = await crm_repo.interactions.create(
            farmer_id=interaction_data.farmer_id,
            interaction_type=interaction_data.interaction_type,
            subject=interaction_data.subject,
            subject_ar=interaction_data.subject_ar,
            notes=interaction_data.notes,
            notes_ar=interaction_data.notes_ar,
            outcome=interaction_data.outcome,
            follow_up_date=interaction_data.follow_up_date,
            created_by=user.id,
        )

        # Update farmer's last interaction
        await crm_repo.farmers.update(interaction_data.farmer_id, {"last_interaction_at": datetime.now(UTC)})

        # Publish interaction logged event
        await publish_event(
            f"sahool.{farmer_data['tenant_id']}.crm.interaction.logged",
            {
                "event_type": "interaction.logged",
                "interaction_id": data["id"],
                "farmer_id": data["farmer_id"],
                "tenant_id": farmer_data["tenant_id"],
                "interaction_type": data["interaction_type"],
                "subject": data["subject"],
                "subject_ar": data["subject_ar"],
                "outcome": data["outcome"],
                "follow_up_date": data["follow_up_date"].isoformat() if data["follow_up_date"] else None,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        return InteractionResponse(
            id=data["id"],
            farmer_id=data["farmer_id"],
            interaction_type=data["interaction_type"],
            subject=data["subject"],
            subject_ar=data["subject_ar"],
            notes=data["notes"],
            notes_ar=data["notes_ar"],
            outcome=data["outcome"],
            follow_up_date=data["follow_up_date"],
            created_at=data["created_at"],
            created_by=data["created_by"],
        )
    else:
        # Fallback to in-memory
        if interaction_data.farmer_id not in farmers:
            raise ResourceNotFoundError(resource_type="Farmer", resource_id=interaction_data.farmer_id)

        # Validate tenant access via farmer's tenant_id
        farmer = farmers[interaction_data.farmer_id]
        validate_tenant_access(user, farmer.tenant_id)

        interaction_id = str(uuid4())
        now = datetime.now(UTC)

        interaction = Interaction(
            id=interaction_id,
            farmer_id=interaction_data.farmer_id,
            interaction_type=InteractionType(interaction_data.interaction_type),
            subject=interaction_data.subject,
            subject_ar=interaction_data.subject_ar,
            notes=interaction_data.notes,
            notes_ar=interaction_data.notes_ar,
            outcome=interaction_data.outcome,
            follow_up_date=interaction_data.follow_up_date,
            created_at=now,
        )

        interactions[interaction_id] = interaction

        # Update farmer's last interaction
        farmers[interaction_data.farmer_id].last_interaction_at = now

        # Publish interaction logged event
        await publish_event(
            f"sahool.{farmer.tenant_id}.crm.interaction.logged",
            {
                "event_type": "interaction.logged",
                "interaction_id": interaction.id,
                "farmer_id": interaction.farmer_id,
                "tenant_id": farmer.tenant_id,
                "interaction_type": interaction.interaction_type.value,
                "subject": interaction.subject,
                "subject_ar": interaction.subject_ar,
                "outcome": interaction.outcome,
                "follow_up_date": interaction.follow_up_date.isoformat() if interaction.follow_up_date else None,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        return InteractionResponse(
            id=interaction.id,
            farmer_id=interaction.farmer_id,
            interaction_type=interaction.interaction_type.value,
            subject=interaction.subject,
            subject_ar=interaction.subject_ar,
            notes=interaction.notes,
            notes_ar=interaction.notes_ar,
            outcome=interaction.outcome,
            follow_up_date=interaction.follow_up_date,
            created_at=interaction.created_at,
            created_by=interaction.created_by,
        )


@app.get("/api/v1/interactions", response_model=list[InteractionResponse], tags=["Interactions"])
@limiter.limit("60/minute")
async def list_interactions(
    request: Request,
    farmer_id: str = Query(...),
    interaction_type: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
):
    """List interactions for a farmer | قائمة التفاعلات لمزارع"""
    crm_repo = get_crm_repo(request)

    if crm_repo:
        # Use database - first verify farmer exists
        farmer_data = await crm_repo.farmers.get_by_id(farmer_id)
        if not farmer_data:
            raise ResourceNotFoundError(resource_type="Farmer", resource_id=farmer_id)
        validate_tenant_access(user, farmer_data["tenant_id"])

        interactions_data = await crm_repo.interactions.list(
            farmer_id=farmer_id,
            interaction_type=interaction_type,
            limit=limit,
        )

        return [
            InteractionResponse(
                id=i["id"],
                farmer_id=i["farmer_id"],
                interaction_type=i["interaction_type"],
                subject=i["subject"],
                subject_ar=i["subject_ar"],
                notes=i["notes"],
                notes_ar=i["notes_ar"],
                outcome=i["outcome"],
                follow_up_date=i["follow_up_date"],
                created_at=i["created_at"],
                created_by=i["created_by"],
            )
            for i in interactions_data
        ]
    else:
        # Fallback to in-memory
        # Validate farmer exists and tenant access
        if farmer_id not in farmers:
            raise ResourceNotFoundError(resource_type="Farmer", resource_id=farmer_id)
        farmer = farmers[farmer_id]
        validate_tenant_access(user, farmer.tenant_id)

        results = [i for i in interactions.values() if i.farmer_id == farmer_id]

        if interaction_type:
            results = [i for i in results if i.interaction_type.value == interaction_type]

        # Sort by created_at descending
        results.sort(key=lambda x: x.created_at, reverse=True)

        return [
            InteractionResponse(
                id=i.id,
                farmer_id=i.farmer_id,
                interaction_type=i.interaction_type.value,
                subject=i.subject,
                subject_ar=i.subject_ar,
                notes=i.notes,
                notes_ar=i.notes_ar,
                outcome=i.outcome,
                follow_up_date=i.follow_up_date,
                created_at=i.created_at,
                created_by=i.created_by,
            )
            for i in results[:limit]
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# Natural Language Query Endpoint (SQLBot-inspired)
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/api/v1/query", response_model=QueryResponse, tags=["Query"])
@limiter.limit("10/minute")
async def natural_language_query(
    request: Request,
    query_data: QueryRequest,
    user: User = Depends(get_current_user),
):
    """
    Execute a natural language query (SQLBot-inspired)

    تنفيذ استعلام بلغة طبيعية

    Examples:
    - "Show me all active farmers"
    - "أرني جميع المزارعين النشطين"
    - "Farmers with farm size > 10 hectares"
    - "Deals in negotiation stage"
    """
    # Validate tenant access
    validate_tenant_access(user, query_data.tenant_id)

    import time

    start_time = time.time()

    # Security: Query length validation
    if len(query_data.query) > MAX_QUERY_LENGTH:
        raise InvalidQueryError(
            reason=f"Query too long. Maximum {MAX_QUERY_LENGTH} characters | الاستعلام طويل جداً. الحد الأقصى {MAX_QUERY_LENGTH} حرف"
        )

    # Security: Query complexity check to prevent DoS
    if not check_query_complexity(query_data.query):
        raise InvalidQueryError(
            reason="Query too complex. Maximum 5 conditions allowed | الاستعلام معقد جداً. الحد الأقصى 5 شروط"
        )

    # Security: Sanitize query to remove dangerous patterns
    sanitized_query = sanitize_query(query_data.query)
    query_lower = sanitized_query.lower()
    results: list[dict[str, Any]] = []
    interpreted_as = ""
    interpreted_as_ar = ""

    # Filter farmers by tenant_id
    tenant_farmers = {fid: f for fid, f in farmers.items() if f.tenant_id == query_data.tenant_id}
    # Filter deals by tenant_id (via farmer's tenant_id)
    tenant_deals = {
        did: d
        for did, d in deals.items()
        if d.farmer_id in farmers and farmers[d.farmer_id].tenant_id == query_data.tenant_id
    }

    # Parse query and execute
    if "active" in query_lower or "نشط" in query_data.query:
        interpreted_as = "SELECT * FROM farmers WHERE status = 'active'"
        interpreted_as_ar = "اختر جميع المزارعين حيث الحالة = نشط"
        results = [
            {
                "id": f.id,
                "name": f.name,
                "name_ar": f.name_ar,
                "status": f.status.value,
                "farm_size_hectares": f.farm_size_hectares,
            }
            for f in tenant_farmers.values()
            if f.status == FarmerStatus.ACTIVE
        ]

    elif "lead" in query_lower or "محتمل" in query_data.query:
        interpreted_as = "SELECT * FROM farmers WHERE status = 'lead'"
        interpreted_as_ar = "اختر جميع المزارعين حيث الحالة = محتمل"
        results = [
            {
                "id": f.id,
                "name": f.name,
                "name_ar": f.name_ar,
                "status": f.status.value,
            }
            for f in tenant_farmers.values()
            if f.status == FarmerStatus.LEAD
        ]

    elif "deal" in query_lower or "صفقة" in query_data.query:
        if "negotiation" in query_lower or "تفاوض" in query_data.query:
            interpreted_as = "SELECT * FROM deals WHERE stage = 'negotiation'"
            interpreted_as_ar = "اختر جميع الصفقات حيث المرحلة = تفاوض"
            results = [
                {
                    "id": d.id,
                    "crop_type": d.crop_type,
                    "expected_quantity_tons": d.expected_quantity_tons,
                    "stage": d.stage.value,
                }
                for d in tenant_deals.values()
                if d.stage == DealStage.NEGOTIATION
            ]
        else:
            interpreted_as = "SELECT * FROM deals"
            interpreted_as_ar = "اختر جميع الصفقات"
            results = [
                {
                    "id": d.id,
                    "crop_type": d.crop_type,
                    "expected_quantity_tons": d.expected_quantity_tons,
                    "stage": d.stage.value,
                }
                for d in tenant_deals.values()
            ]

    elif "farmer" in query_lower or "مزارع" in query_data.query:
        interpreted_as = "SELECT * FROM farmers"
        interpreted_as_ar = "اختر جميع المزارعين"
        results = [
            {
                "id": f.id,
                "name": f.name,
                "name_ar": f.name_ar,
                "status": f.status.value,
                "farm_size_hectares": f.farm_size_hectares,
            }
            for f in tenant_farmers.values()
        ]

    else:
        interpreted_as = "Unknown query pattern"
        interpreted_as_ar = "نمط استعلام غير معروف"

    # Security: Limit results to prevent data exfiltration
    truncated = False
    if len(results) > MAX_RESULTS:
        results = results[:MAX_RESULTS]
        truncated = True

    execution_time = int((time.time() - start_time) * 1000)

    # Security: Audit logging for NLQ queries
    logger.info(
        "nlq_query_executed",
        tenant_id=query_data.tenant_id,
        user_id=user.id,
        query_length=len(query_data.query),
        results_count=len(results),
        truncated=truncated,
        execution_time_ms=execution_time,
        query_hash=hashlib.sha256(query_data.query.encode()).hexdigest()[:16],
    )

    return QueryResponse(
        query=query_data.query,
        interpreted_as=interpreted_as,
        interpreted_as_ar=interpreted_as_ar,
        results=results,
        result_count=len(results),
        execution_time_ms=execution_time,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Metrics Endpoint
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Prometheus-compatible metrics"""
    return f"""# HELP crm_farmers_total Total number of farmers
# TYPE crm_farmers_total gauge
crm_farmers_total {len(farmers)}

# HELP crm_deals_total Total number of deals
# TYPE crm_deals_total gauge
crm_deals_total {len(deals)}

# HELP crm_interactions_total Total number of interactions
# TYPE crm_interactions_total counter
crm_interactions_total {len(interactions)}
"""


if __name__ == "__main__":
    import uvicorn

    # Use HOST env var for flexibility; 0.0.0.0 for containers, 127.0.0.1 for local dev
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=SERVICE_PORT)
