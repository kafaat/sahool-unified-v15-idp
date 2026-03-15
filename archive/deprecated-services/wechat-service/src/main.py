"""
SAHOOL WeChat Integration Service
=================================
WeChat messaging and social integration for farmers.

Features:
- Message fetching and sending
- Contact management
- Moments publishing
- Chat summarization (AI-powered)
- Chat insights extraction

Port: 8135
"""

import json
import os
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timezone
from enum import Enum, StrEnum
from typing import Any
from uuid import uuid4

import redis.asyncio as redis_client
import structlog
from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Authentication imports
from shared.auth.dependencies import get_current_user
from shared.auth.models import User
from shared.errors_py import setup_exception_handlers, add_request_id_middleware as shared_add_request_id_middleware
from shared.middleware.tenant_context import TenantContextMiddleware

# Add project root to path
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
)

# Service configuration
SERVICE_NAME = "wechat-service"
SERVICE_NAME_AR = "خدمة تكامل ويتشات"
SERVICE_VERSION = "16.0.0"
SERVICE_PORT = 8135

# Logger
logger = structlog.get_logger()


# ===============================================================================
# Enums
# ===============================================================================


class MessageType(StrEnum):
    """WeChat message types"""

    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"
    LOCATION = "location"
    LINK = "link"
    FILE = "file"
    MINI_PROGRAM = "mini_program"


class ContactType(StrEnum):
    """WeChat contact types"""

    FRIEND = "friend"
    GROUP = "group"
    OFFICIAL_ACCOUNT = "official_account"
    MINI_PROGRAM = "mini_program"


class MomentVisibility(StrEnum):
    """WeChat moment visibility options"""

    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"
    SELECTED = "selected"


class InsightType(StrEnum):
    """Chat insight types"""

    SENTIMENT = "sentiment"
    TOPIC = "topic"
    ACTION_ITEMS = "action_items"
    QUESTIONS = "questions"
    KEY_DECISIONS = "key_decisions"


# ===============================================================================
# Error Response Model & Custom Exceptions
# ===============================================================================


class ErrorResponse(BaseModel):
    """Standardized error response model | نموذج استجابة الخطأ الموحد"""

    error: str
    error_ar: str | None = None
    error_code: str
    detail: str | None = None
    request_id: str | None = None


class ServiceUnavailableError(Exception):
    """Raised when a required service (DB, NATS, WeChat API) is unavailable"""

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


class WeChatAPIError(Exception):
    """Raised when WeChat API returns an error"""

    def __init__(self, error_code: str, message: str, message_ar: str | None = None):
        self.error_code = error_code
        self.message = message
        self.message_ar = message_ar or message
        super().__init__(self.message)


class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""

    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        self.message = f"Rate limit exceeded. Retry after {retry_after} seconds"
        super().__init__(self.message)


class InvalidInputError(Exception):
    """Raised when input validation fails"""

    def __init__(self, field: str, reason: str, reason_ar: str | None = None):
        self.field = field
        self.reason = reason
        self.reason_ar = reason_ar or reason
        self.message = f"Invalid input for {field}: {reason}"
        super().__init__(self.message)


def get_request_id(request: Request) -> str | None:
    """Extract or generate request ID from request"""
    return getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID")


# ===============================================================================
# Event Publishing Helper
# ===============================================================================


async def publish_event(subject: str, data: dict) -> None:
    """
    Publish an event to NATS.

    نشر حدث إلى NATS

    Args:
        subject: Event subject (e.g., "sahool.tenant_id.wechat.message.sent")
        data: Event payload dictionary
    """
    if app.state.publisher:
        try:
            await app.state.publisher.publish(subject, json.dumps(data).encode())
            logger.info("event_published", subject=subject, event_type=data.get("event_type"))
        except Exception as e:
            logger.error("event_publish_failed", subject=subject, error=str(e))


# ===============================================================================
# Request/Response Models
# ===============================================================================


# --- Message Models ---
class MessageFetchRequest(BaseModel):
    """Request to fetch messages from a chat | طلب جلب الرسائل من محادثة"""

    chat_id: str = Field(..., description="WeChat chat/group ID | معرف المحادثة")
    tenant_id: str = Field(..., description="Tenant ID | معرف المستأجر")
    limit: int = Field(50, ge=1, le=200, description="Maximum messages to fetch | الحد الأقصى للرسائل")
    before_timestamp: datetime | None = Field(
        None, description="Fetch messages before this time | جلب الرسائل قبل هذا الوقت"
    )
    after_timestamp: datetime | None = Field(
        None, description="Fetch messages after this time | جلب الرسائل بعد هذا الوقت"
    )
    message_types: list[MessageType] | None = Field(
        None, description="Filter by message types | تصفية حسب أنواع الرسائل"
    )


class MessageResponse(BaseModel):
    """Message response model | نموذج استجابة الرسالة"""

    id: str
    chat_id: str
    sender_id: str
    sender_name: str | None = None
    sender_name_ar: str | None = None
    message_type: MessageType
    content: str
    content_ar: str | None = None
    media_url: str | None = None
    timestamp: datetime
    is_from_self: bool = False
    reply_to_id: str | None = None
    metadata: dict[str, Any] | None = None


class MessageFetchResponse(BaseModel):
    """Response for message fetch | استجابة جلب الرسائل"""

    chat_id: str
    messages: list[MessageResponse]
    total_count: int
    has_more: bool
    oldest_timestamp: datetime | None = None
    newest_timestamp: datetime | None = None


class MessageSendRequest(BaseModel):
    """Request to send a message | طلب إرسال رسالة"""

    chat_id: str = Field(..., description="Target chat/group ID | معرف المحادثة المستهدفة")
    tenant_id: str = Field(..., description="Tenant ID | معرف المستأجر")
    message_type: MessageType = Field(MessageType.TEXT, description="Message type | نوع الرسالة")
    content: str = Field(..., min_length=1, max_length=10000, description="Message content | محتوى الرسالة")
    media_url: str | None = Field(None, description="Media URL for non-text messages | رابط الوسائط")
    reply_to_id: str | None = Field(None, description="Message ID to reply to | معرف الرسالة للرد عليها")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata | بيانات إضافية")


class MessageSendResponse(BaseModel):
    """Response for message send | استجابة إرسال الرسالة"""

    id: str
    chat_id: str
    message_type: MessageType
    content: str
    timestamp: datetime
    status: str
    status_ar: str


# --- Contact Models ---
class ContactAddRequest(BaseModel):
    """Request to add a contact | طلب إضافة جهة اتصال"""

    wechat_id: str = Field(..., description="WeChat ID or phone number | معرف ويتشات أو رقم الهاتف")
    tenant_id: str = Field(..., description="Tenant ID | معرف المستأجر")
    contact_type: ContactType = Field(ContactType.FRIEND, description="Contact type | نوع جهة الاتصال")
    greeting_message: str | None = Field(None, max_length=500, description="Friend request message | رسالة طلب الصداقة")
    greeting_message_ar: str | None = Field(None, max_length=500, description="Greeting in Arabic | الترحيب بالعربية")
    notes: str | None = Field(None, max_length=1000, description="Personal notes | ملاحظات شخصية")
    tags: list[str] | None = Field(None, description="Contact tags | وسوم جهة الاتصال")


class ContactResponse(BaseModel):
    """Contact response model | نموذج استجابة جهة الاتصال"""

    id: str
    wechat_id: str
    nickname: str | None = None
    nickname_ar: str | None = None
    avatar_url: str | None = None
    contact_type: ContactType
    status: str
    status_ar: str
    notes: str | None = None
    tags: list[str]
    added_at: datetime


# --- Moment Models ---
class MomentPublishRequest(BaseModel):
    """Request to publish a moment | طلب نشر لحظة"""

    tenant_id: str = Field(..., description="Tenant ID | معرف المستأجر")
    content: str = Field(..., min_length=1, max_length=2000, description="Moment text content | محتوى النص")
    content_ar: str | None = Field(None, max_length=2000, description="Content in Arabic | المحتوى بالعربية")
    media_urls: list[str] | None = Field(None, max_length=9, description="Media URLs (max 9) | روابط الوسائط")
    location: str | None = Field(None, description="Location tag | علامة الموقع")
    location_ar: str | None = Field(None, description="Location in Arabic | الموقع بالعربية")
    visibility: MomentVisibility = Field(MomentVisibility.FRIENDS, description="Visibility setting | إعداد الرؤية")
    visible_to: list[str] | None = Field(
        None,
        description="Specific user IDs if visibility is 'selected' | معرفات المستخدمين المحددين",
    )
    link_url: str | None = Field(None, description="Link to attach | رابط للإرفاق")
    link_title: str | None = Field(None, description="Link title | عنوان الرابط")


class MomentResponse(BaseModel):
    """Moment response model | نموذج استجابة اللحظة"""

    id: str
    content: str
    content_ar: str | None = None
    media_urls: list[str]
    location: str | None = None
    location_ar: str | None = None
    visibility: MomentVisibility
    link_url: str | None = None
    link_title: str | None = None
    published_at: datetime
    likes_count: int = 0
    comments_count: int = 0
    status: str
    status_ar: str


# --- Chat Analysis Models ---
class ChatSummarizeRequest(BaseModel):
    """Request to summarize a chat | طلب تلخيص المحادثة"""

    chat_id: str = Field(..., description="Chat ID to summarize | معرف المحادثة للتلخيص")
    tenant_id: str = Field(..., description="Tenant ID | معرف المستأجر")
    time_range_hours: int = Field(24, ge=1, le=168, description="Hours of chat to summarize | ساعات المحادثة للتلخيص")
    max_messages: int = Field(500, ge=10, le=2000, description="Maximum messages to analyze | الحد الأقصى للرسائل")
    language: str = Field("en", description="Output language (en/ar/both) | لغة المخرجات")
    include_participants: bool = Field(True, description="Include participant summary | تضمين ملخص المشاركين")
    include_timeline: bool = Field(False, description="Include activity timeline | تضمين الجدول الزمني")


class ParticipantSummary(BaseModel):
    """Participant summary in chat | ملخص المشارك في المحادثة"""

    user_id: str
    name: str | None = None
    name_ar: str | None = None
    message_count: int
    sentiment_score: float | None = None
    key_contributions: list[str] = []
    key_contributions_ar: list[str] = []


class ChatSummaryResponse(BaseModel):
    """Chat summary response | استجابة ملخص المحادثة"""

    chat_id: str
    time_range_start: datetime
    time_range_end: datetime
    total_messages: int
    summary: str
    summary_ar: str | None = None
    key_topics: list[str]
    key_topics_ar: list[str] | None = None
    action_items: list[str]
    action_items_ar: list[str] | None = None
    participants: list[ParticipantSummary] | None = None
    sentiment_overview: str | None = None
    sentiment_overview_ar: str | None = None
    generated_at: datetime


class ChatInsightsRequest(BaseModel):
    """Request to extract chat insights | طلب استخراج رؤى المحادثة"""

    chat_id: str = Field(..., description="Chat ID | معرف المحادثة")
    tenant_id: str = Field(..., description="Tenant ID | معرف المستأجر")
    insight_types: list[InsightType] = Field(
        default=[InsightType.SENTIMENT, InsightType.TOPIC, InsightType.ACTION_ITEMS],
        description="Types of insights to extract | أنواع الرؤى للاستخراج",
    )
    time_range_hours: int = Field(24, ge=1, le=168, description="Hours to analyze | ساعات التحليل")
    language: str = Field("en", description="Output language (en/ar/both) | لغة المخرجات")


class InsightItem(BaseModel):
    """Single insight item | عنصر رؤية واحد"""

    insight_type: InsightType
    title: str
    title_ar: str | None = None
    description: str
    description_ar: str | None = None
    confidence: float = Field(ge=0, le=1)
    related_messages: list[str] = []
    metadata: dict[str, Any] | None = None


class ChatInsightsResponse(BaseModel):
    """Chat insights response | استجابة رؤى المحادثة"""

    chat_id: str
    time_range_start: datetime
    time_range_end: datetime
    total_messages_analyzed: int
    insights: list[InsightItem]
    overall_sentiment: float | None = Field(None, ge=-1, le=1)
    sentiment_label: str | None = None
    sentiment_label_ar: str | None = None
    generated_at: datetime


# ===============================================================================
# In-memory storage (for development/testing)
# ===============================================================================

messages: dict[str, list[MessageResponse]] = {}
contacts: dict[str, ContactResponse] = {}
moments: dict[str, MomentResponse] = {}
chat_summaries: dict[str, ChatSummaryResponse] = {}


# ===============================================================================
# Authentication Helpers
# ===============================================================================


def validate_tenant_access(user: User, tenant_id: str) -> None:
    """
    Validate that the authenticated user has access to the specified tenant.
    Raises TenantAccessDeniedError if tenant_id does not match user's tenant_id.

    التحقق من أن المستخدم المصادق عليه لديه حق الوصول إلى المستأجر المحدد.
    """
    if user.tenant_id != tenant_id:
        raise TenantAccessDeniedError(tenant_id=tenant_id)


def _enforce_tenant(user: User, requested_tenant_id: str) -> None:
    """Validate JWT tenant matches the requested tenant."""
    if user.tenant_id and user.tenant_id != requested_tenant_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "tenant_mismatch",
                "message_ar": "لا يمكنك الوصول إلى بيانات مستأجر آخر",
                "message_en": "Cannot access another tenant's data",
            },
        )


# ===============================================================================
# Lifespan Management
# ===============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager | مدير دورة حياة التطبيق"""
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

    # Initialize Database connection (if available)
    db_url = os.getenv("DATABASE_URL")
    # Enforce sslmode for non-development database connections
    if db_url and os.getenv("ENVIRONMENT", "development") != "development":
        if "sslmode" not in db_url:
            db_url += "?sslmode=require" if "?" not in db_url else "&sslmode=require"
    if db_url:
        try:
            import asyncpg

            app.state.db_pool = await asyncpg.create_pool(
                db_url,
                min_size=2,
                max_size=10,
                command_timeout=60,
            )
            app.state.db_connected = True
            logger.info("database_connected")
        except Exception as e:
            logger.error("database_connection_failed", error=str(e))
            app.state.db_pool = None
            app.state.db_connected = False
    else:
        app.state.db_pool = None
        app.state.db_connected = False
        logger.warning("No DATABASE_URL configured, using in-memory storage")

    # WeChat API configuration
    app.state.wechat_app_id = os.getenv("WECHAT_APP_ID")
    app.state.wechat_app_secret = os.getenv("WECHAT_APP_SECRET")  # gitleaks:allow
    app.state.wechat_configured = bool(app.state.wechat_app_id and app.state.wechat_app_secret)

    if not app.state.wechat_configured:
        logger.warning("WeChat API not configured (WECHAT_APP_ID/WECHAT_APP_SECRET missing)")

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


# ===============================================================================
# Redis Cache Helpers
# ===============================================================================


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


# ===============================================================================
# FastAPI Application
# ===============================================================================

app = FastAPI(
    title="SAHOOL WeChat Integration Service",
    description="WeChat messaging and social integration for farmers | تكامل ويتشات للمراسلة والتواصل الاجتماعي للمزارعين",
    version=SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup unified error handling
setup_exception_handlers(app)
shared_add_request_id_middleware(app)


# ===============================================================================
# Rate Limiting Configuration
# ===============================================================================

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


# ===============================================================================
# Request ID Middleware
# ===============================================================================


@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Add request ID to all requests for tracing | إضافة معرف الطلب لجميع الطلبات للتتبع"""
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ===============================================================================
# Exception Handlers
# ===============================================================================


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors (400)"""
    from fastapi.responses import JSONResponse

    request_id = get_request_id(request)
    logger.warning("validation_error", path=request.url.path, request_id=request_id, error=str(exc))
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


@app.exception_handler(WeChatAPIError)
async def wechat_api_error_handler(request: Request, exc: WeChatAPIError):
    """Handle WeChat API errors (502)"""
    from fastapi.responses import JSONResponse

    request_id = get_request_id(request)
    logger.error(
        "wechat_api_error",
        path=request.url.path,
        request_id=request_id,
        error_code=exc.error_code,
        error=exc.message,
    )
    return JSONResponse(
        status_code=502,
        content=ErrorResponse(
            error=f"WeChat API error: {exc.message}",
            error_ar=f"خطأ في واجهة ويتشات: {exc.message_ar}",
            error_code=f"WECHAT_{exc.error_code}",
            detail=exc.message,
            request_id=request_id,
        ).model_dump(),
    )


@app.exception_handler(InvalidInputError)
async def invalid_input_handler(request: Request, exc: InvalidInputError):
    """Handle invalid input errors (400)"""
    from fastapi.responses import JSONResponse

    request_id = get_request_id(request)
    logger.warning(
        "invalid_input",
        path=request.url.path,
        request_id=request_id,
        field=exc.field,
        reason=exc.reason,
    )
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error=f"Invalid input: {exc.reason}",
            error_ar=f"إدخال غير صالح: {exc.reason_ar}",
            error_code="INVALID_INPUT",
            detail=f"Field: {exc.field}",
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
        502: ("BAD_GATEWAY", "بوابة غير صالحة"),
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


# CORS middleware
cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Tenant-ID"],
)

# Tenant context middleware
app.add_middleware(TenantContextMiddleware)


# ===============================================================================
# Health Endpoints
# ===============================================================================


@app.get("/healthz", tags=["Health"])
def health():
    """Liveness probe | فحص الحيوية"""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "service_ar": SERVICE_NAME_AR,
        "version": SERVICE_VERSION,
    }


@app.get("/readyz", tags=["Health"])
def readiness():
    """Readiness probe | فحص الجاهزية"""
    return {
        "status": "ok",
        "database": getattr(app.state, "db_connected", False),
        "redis": getattr(app.state, "redis_connected", False),
        "nats": getattr(app.state, "nats_connected", False),
        "wechat_configured": getattr(app.state, "wechat_configured", False),
    }


@app.get("/health", tags=["Health"])
def health_detailed():
    """Detailed health status | حالة الصحة المفصلة"""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "service_ar": SERVICE_NAME_AR,
        "version": SERVICE_VERSION,
        "database_connected": getattr(app.state, "db_connected", False),
        "redis_connected": getattr(app.state, "redis_connected", False),
        "nats_connected": getattr(app.state, "nats_connected", False),
        "wechat_configured": getattr(app.state, "wechat_configured", False),
        "messages_count": sum(len(m) for m in messages.values()),
        "contacts_count": len(contacts),
        "moments_count": len(moments),
    }


# ===============================================================================
# Message Endpoints
# ===============================================================================


@app.post("/api/v1/messages/fetch", response_model=MessageFetchResponse, tags=["Messages"])
@limiter.limit("60/minute")
async def fetch_messages(
    request: Request,
    fetch_request: MessageFetchRequest,
    user: User = Depends(get_current_user),
):
    """
    Fetch messages from a WeChat chat or group.

    جلب الرسائل من محادثة أو مجموعة ويتشات

    - Supports filtering by time range and message types
    - Returns messages in chronological order
    - Pagination via before_timestamp/after_timestamp
    """
    # Validate tenant access
    _enforce_tenant(user, fetch_request.tenant_id)

    chat_id = fetch_request.chat_id

    # Try cache first
    cache_key = f"wechat:messages:{fetch_request.tenant_id}:{chat_id}"
    await cache_get(cache_key)

    # Simulate fetching messages (in production, call WeChat API)
    if chat_id not in messages:
        # Generate sample messages for demo
        now = datetime.now(UTC)
        messages[chat_id] = [
            MessageResponse(
                id=str(uuid4()),
                chat_id=chat_id,
                sender_id="user_001",
                sender_name="Ahmed",
                sender_name_ar="أحمد",
                message_type=MessageType.TEXT,
                content="Hello, how is the wheat crop doing?",
                content_ar="مرحبا، كيف حال محصول القمح؟",
                timestamp=now,
                is_from_self=False,
            ),
        ]

    chat_messages = messages.get(chat_id, [])

    # Apply filters
    filtered_messages = chat_messages
    if fetch_request.before_timestamp:
        filtered_messages = [m for m in filtered_messages if m.timestamp < fetch_request.before_timestamp]
    if fetch_request.after_timestamp:
        filtered_messages = [m for m in filtered_messages if m.timestamp > fetch_request.after_timestamp]
    if fetch_request.message_types:
        filtered_messages = [m for m in filtered_messages if m.message_type in fetch_request.message_types]

    # Apply limit
    limited_messages = filtered_messages[: fetch_request.limit]

    # Publish event
    await publish_event(
        f"sahool.tenant.{fetch_request.tenant_id}.wechat.messages_fetched",
        {
            "event_type": "messages.fetched",
            "chat_id": chat_id,
            "tenant_id": fetch_request.tenant_id,
            "message_count": len(limited_messages),
            "user_id": user.id,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )

    return MessageFetchResponse(
        chat_id=chat_id,
        messages=limited_messages,
        total_count=len(filtered_messages),
        has_more=len(filtered_messages) > fetch_request.limit,
        oldest_timestamp=min(m.timestamp for m in limited_messages) if limited_messages else None,
        newest_timestamp=max(m.timestamp for m in limited_messages) if limited_messages else None,
    )


@app.post("/api/v1/messages/send", response_model=MessageSendResponse, tags=["Messages"])
@limiter.limit("30/minute")
async def send_message(
    request: Request,
    send_request: MessageSendRequest,
    user: User = Depends(get_current_user),
):
    """
    Send a message to a WeChat chat or group.

    إرسال رسالة إلى محادثة أو مجموعة ويتشات

    - Supports text, image, voice, video, location, link messages
    - Can reply to a specific message
    - Returns message ID and status
    """
    # Validate tenant access
    _enforce_tenant(user, send_request.tenant_id)

    # Validate media URL for non-text messages
    if send_request.message_type != MessageType.TEXT and not send_request.media_url:
        raise InvalidInputError(
            field="media_url",
            reason="Media URL is required for non-text messages",
            reason_ar="رابط الوسائط مطلوب للرسائل غير النصية",
        )

    # Create message
    message_id = str(uuid4())
    now = datetime.now(UTC)

    new_message = MessageResponse(
        id=message_id,
        chat_id=send_request.chat_id,
        sender_id=user.id,
        sender_name=user.email,
        message_type=send_request.message_type,
        content=send_request.content,
        media_url=send_request.media_url,
        timestamp=now,
        is_from_self=True,
        reply_to_id=send_request.reply_to_id,
        metadata=send_request.metadata,
    )

    # Store message
    if send_request.chat_id not in messages:
        messages[send_request.chat_id] = []
    messages[send_request.chat_id].append(new_message)

    # Invalidate cache
    await cache_delete(f"wechat:messages:{send_request.tenant_id}:{send_request.chat_id}")

    # Publish event
    await publish_event(
        f"sahool.tenant.{send_request.tenant_id}.wechat.message_sent",
        {
            "event_type": "message.sent",
            "message_id": message_id,
            "chat_id": send_request.chat_id,
            "tenant_id": send_request.tenant_id,
            "message_type": send_request.message_type.value,
            "user_id": user.id,
            "timestamp": now.isoformat(),
        },
    )

    logger.info(
        "message_sent",
        message_id=message_id,
        chat_id=send_request.chat_id,
        tenant_id=send_request.tenant_id,
        message_type=send_request.message_type.value,
    )

    return MessageSendResponse(
        id=message_id,
        chat_id=send_request.chat_id,
        message_type=send_request.message_type,
        content=send_request.content,
        timestamp=now,
        status="sent",
        status_ar="تم الإرسال",
    )


# ===============================================================================
# Contact Endpoints
# ===============================================================================


@app.post("/api/v1/contacts/add", response_model=ContactResponse, tags=["Contacts"])
@limiter.limit("20/minute")
async def add_contact(
    request: Request,
    add_request: ContactAddRequest,
    user: User = Depends(get_current_user),
):
    """
    Add a new WeChat contact (friend request).

    إضافة جهة اتصال ويتشات جديدة (طلب صداقة)

    - Send friend request with optional greeting message
    - Add to groups or follow official accounts
    - Add notes and tags for organization
    """
    # Validate tenant access
    _enforce_tenant(user, add_request.tenant_id)

    # Check if contact already exists
    contact_key = f"{add_request.tenant_id}:{add_request.wechat_id}"
    if contact_key in contacts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Contact already exists: {add_request.wechat_id}",
        )

    # Create contact
    contact_id = str(uuid4())
    now = datetime.now(UTC)

    new_contact = ContactResponse(
        id=contact_id,
        wechat_id=add_request.wechat_id,
        nickname=None,  # Will be populated when request is accepted
        contact_type=add_request.contact_type,
        status="pending",
        status_ar="قيد الانتظار",
        notes=add_request.notes,
        tags=add_request.tags or [],
        added_at=now,
    )

    # Store contact
    contacts[contact_key] = new_contact

    # Publish event
    await publish_event(
        f"sahool.tenant.{add_request.tenant_id}.wechat.contact_added",
        {
            "event_type": "contact.added",
            "contact_id": contact_id,
            "wechat_id": add_request.wechat_id,
            "tenant_id": add_request.tenant_id,
            "contact_type": add_request.contact_type.value,
            "user_id": user.id,
            "timestamp": now.isoformat(),
        },
    )

    logger.info(
        "contact_added",
        contact_id=contact_id,
        wechat_id=add_request.wechat_id,
        tenant_id=add_request.tenant_id,
        contact_type=add_request.contact_type.value,
    )

    return new_contact


# ===============================================================================
# Moments Endpoints
# ===============================================================================


@app.post("/api/v1/moments/publish", response_model=MomentResponse, tags=["Moments"])
@limiter.limit("10/minute")
async def publish_moment(
    request: Request,
    publish_request: MomentPublishRequest,
    user: User = Depends(get_current_user),
):
    """
    Publish a new moment to WeChat Moments.

    نشر لحظة جديدة في لحظات ويتشات

    - Support text, images, and video
    - Set visibility (public, friends, private, or selected users)
    - Add location tags
    - Attach links with titles
    """
    # Validate tenant access
    _enforce_tenant(user, publish_request.tenant_id)

    # Validate visibility
    if publish_request.visibility == MomentVisibility.SELECTED and not publish_request.visible_to:
        raise InvalidInputError(
            field="visible_to",
            reason="User IDs required when visibility is 'selected'",
            reason_ar="معرفات المستخدمين مطلوبة عند اختيار 'محدد'",
        )

    # Create moment
    moment_id = str(uuid4())
    now = datetime.now(UTC)

    new_moment = MomentResponse(
        id=moment_id,
        content=publish_request.content,
        content_ar=publish_request.content_ar,
        media_urls=publish_request.media_urls or [],
        location=publish_request.location,
        location_ar=publish_request.location_ar,
        visibility=publish_request.visibility,
        link_url=publish_request.link_url,
        link_title=publish_request.link_title,
        published_at=now,
        likes_count=0,
        comments_count=0,
        status="published",
        status_ar="تم النشر",
    )

    # Store moment
    moment_key = f"{publish_request.tenant_id}:{moment_id}"
    moments[moment_key] = new_moment

    # Publish event
    await publish_event(
        f"sahool.tenant.{publish_request.tenant_id}.wechat.moment_published",
        {
            "event_type": "moment.published",
            "moment_id": moment_id,
            "tenant_id": publish_request.tenant_id,
            "visibility": publish_request.visibility.value,
            "has_media": bool(publish_request.media_urls),
            "media_count": len(publish_request.media_urls) if publish_request.media_urls else 0,
            "user_id": user.id,
            "timestamp": now.isoformat(),
        },
    )

    logger.info(
        "moment_published",
        moment_id=moment_id,
        tenant_id=publish_request.tenant_id,
        visibility=publish_request.visibility.value,
    )

    return new_moment


# ===============================================================================
# Chat Analysis Endpoints
# ===============================================================================


@app.post("/api/v1/chat/summarize", response_model=ChatSummaryResponse, tags=["Chat Analysis"])
@limiter.limit("10/minute")
async def summarize_chat(
    request: Request,
    summarize_request: ChatSummarizeRequest,
    user: User = Depends(get_current_user),
):
    """
    Generate an AI-powered summary of a chat conversation.

    إنشاء ملخص للمحادثة باستخدام الذكاء الاصطناعي

    - Summarize key topics and discussions
    - Extract action items
    - Analyze participant contributions
    - Support multiple output languages
    """
    # Validate tenant access
    _enforce_tenant(user, summarize_request.tenant_id)

    chat_id = summarize_request.chat_id
    now = datetime.now(UTC)

    # Calculate time range
    from datetime import timedelta

    time_range_start = now - timedelta(hours=summarize_request.time_range_hours)

    # Get messages for analysis
    chat_messages = messages.get(chat_id, [])
    filtered_messages = [m for m in chat_messages if m.timestamp >= time_range_start][: summarize_request.max_messages]

    # Generate summary (in production, use AI model)
    participants = []
    if summarize_request.include_participants:
        # Aggregate participant data
        participant_map: dict[str, dict] = {}
        for msg in filtered_messages:
            if msg.sender_id not in participant_map:
                participant_map[msg.sender_id] = {
                    "user_id": msg.sender_id,
                    "name": msg.sender_name,
                    "name_ar": msg.sender_name_ar,
                    "message_count": 0,
                    "key_contributions": [],
                    "key_contributions_ar": [],
                }
            participant_map[msg.sender_id]["message_count"] += 1

        participants = [ParticipantSummary(**p) for p in participant_map.values()]

    # Generate bilingual summary
    summary_en = "The conversation covered agricultural topics including crop health and irrigation scheduling."
    summary_ar = "تناولت المحادثة مواضيع زراعية تشمل صحة المحاصيل وجدولة الري."

    key_topics_en = ["Crop health monitoring", "Irrigation scheduling", "Weather forecast"]
    key_topics_ar = ["مراقبة صحة المحاصيل", "جدولة الري", "توقعات الطقس"]

    action_items_en = ["Check soil moisture levels", "Schedule irrigation for next week"]
    action_items_ar = ["فحص مستويات رطوبة التربة", "جدولة الري للأسبوع القادم"]

    summary_response = ChatSummaryResponse(
        chat_id=chat_id,
        time_range_start=time_range_start,
        time_range_end=now,
        total_messages=len(filtered_messages),
        summary=summary_en,
        summary_ar=summary_ar if summarize_request.language in ["ar", "both"] else None,
        key_topics=key_topics_en,
        key_topics_ar=key_topics_ar if summarize_request.language in ["ar", "both"] else None,
        action_items=action_items_en,
        action_items_ar=action_items_ar if summarize_request.language in ["ar", "both"] else None,
        participants=participants if summarize_request.include_participants else None,
        sentiment_overview="Generally positive with constructive discussions",
        sentiment_overview_ar="إيجابي بشكل عام مع نقاشات بناءة"
        if summarize_request.language in ["ar", "both"]
        else None,
        generated_at=now,
    )

    # Cache summary
    cache_key = f"wechat:summary:{summarize_request.tenant_id}:{chat_id}"
    await cache_set(cache_key, summary_response.model_dump(), ttl=600)  # 10 min cache

    # Publish event
    await publish_event(
        f"sahool.tenant.{summarize_request.tenant_id}.wechat.chat_summarized",
        {
            "event_type": "chat.summarized",
            "chat_id": chat_id,
            "tenant_id": summarize_request.tenant_id,
            "messages_analyzed": len(filtered_messages),
            "time_range_hours": summarize_request.time_range_hours,
            "user_id": user.id,
            "timestamp": now.isoformat(),
        },
    )

    logger.info(
        "chat_summarized",
        chat_id=chat_id,
        tenant_id=summarize_request.tenant_id,
        messages_analyzed=len(filtered_messages),
    )

    return summary_response


@app.post("/api/v1/chat/insights", response_model=ChatInsightsResponse, tags=["Chat Analysis"])
@limiter.limit("10/minute")
async def get_chat_insights(
    request: Request,
    insights_request: ChatInsightsRequest,
    user: User = Depends(get_current_user),
):
    """
    Extract AI-powered insights from a chat conversation.

    استخراج رؤى من المحادثة باستخدام الذكاء الاصطناعي

    - Sentiment analysis
    - Topic extraction
    - Action item detection
    - Question identification
    - Key decision tracking
    """
    # Validate tenant access
    _enforce_tenant(user, insights_request.tenant_id)

    chat_id = insights_request.chat_id
    now = datetime.now(UTC)

    # Calculate time range
    from datetime import timedelta

    time_range_start = now - timedelta(hours=insights_request.time_range_hours)

    # Get messages for analysis
    chat_messages = messages.get(chat_id, [])
    filtered_messages = [m for m in chat_messages if m.timestamp >= time_range_start]

    # Generate insights (in production, use AI model)
    insights = []

    if InsightType.SENTIMENT in insights_request.insight_types:
        insights.append(
            InsightItem(
                insight_type=InsightType.SENTIMENT,
                title="Overall Positive Sentiment",
                title_ar="مشاعر إيجابية بشكل عام",
                description="The conversation maintains a positive and collaborative tone throughout.",
                description_ar="تحافظ المحادثة على نبرة إيجابية وتعاونية طوال الوقت.",
                confidence=0.85,
                related_messages=[],
            )
        )

    if InsightType.TOPIC in insights_request.insight_types:
        insights.append(
            InsightItem(
                insight_type=InsightType.TOPIC,
                title="Agricultural Advisory",
                title_ar="الإرشاد الزراعي",
                description="Main discussion topic revolves around crop management and irrigation.",
                description_ar="يدور موضوع النقاش الرئيسي حول إدارة المحاصيل والري.",
                confidence=0.92,
                related_messages=[],
            )
        )

    if InsightType.ACTION_ITEMS in insights_request.insight_types:
        insights.append(
            InsightItem(
                insight_type=InsightType.ACTION_ITEMS,
                title="Follow-up Required",
                title_ar="متابعة مطلوبة",
                description="Check soil moisture levels before next irrigation cycle.",
                description_ar="فحص مستويات رطوبة التربة قبل دورة الري التالية.",
                confidence=0.78,
                related_messages=[],
            )
        )

    if InsightType.QUESTIONS in insights_request.insight_types:
        insights.append(
            InsightItem(
                insight_type=InsightType.QUESTIONS,
                title="Unanswered Question",
                title_ar="سؤال بدون إجابة",
                description="When should the fertilizer be applied?",
                description_ar="متى يجب تطبيق السماد؟",
                confidence=0.88,
                related_messages=[],
            )
        )

    if InsightType.KEY_DECISIONS in insights_request.insight_types:
        insights.append(
            InsightItem(
                insight_type=InsightType.KEY_DECISIONS,
                title="Decision Made",
                title_ar="قرار تم اتخاذه",
                description="Agreed to schedule irrigation for Tuesday morning.",
                description_ar="تم الاتفاق على جدولة الري لصباح يوم الثلاثاء.",
                confidence=0.95,
                related_messages=[],
            )
        )

    insights_response = ChatInsightsResponse(
        chat_id=chat_id,
        time_range_start=time_range_start,
        time_range_end=now,
        total_messages_analyzed=len(filtered_messages),
        insights=insights,
        overall_sentiment=0.65,
        sentiment_label="Positive",
        sentiment_label_ar="إيجابي" if insights_request.language in ["ar", "both"] else None,
        generated_at=now,
    )

    # Publish event
    await publish_event(
        f"sahool.tenant.{insights_request.tenant_id}.wechat.chat_insights_extracted",
        {
            "event_type": "chat.insights_extracted",
            "chat_id": chat_id,
            "tenant_id": insights_request.tenant_id,
            "messages_analyzed": len(filtered_messages),
            "insights_count": len(insights),
            "insight_types": [i.value for i in insights_request.insight_types],
            "user_id": user.id,
            "timestamp": now.isoformat(),
        },
    )

    logger.info(
        "chat_insights_extracted",
        chat_id=chat_id,
        tenant_id=insights_request.tenant_id,
        messages_analyzed=len(filtered_messages),
        insights_count=len(insights),
    )

    return insights_response


# ===============================================================================
# Metrics Endpoint
# ===============================================================================


@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Prometheus-compatible metrics | مقاييس متوافقة مع Prometheus"""
    total_messages = sum(len(m) for m in messages.values())
    return f"""# HELP wechat_messages_total Total number of messages
# TYPE wechat_messages_total gauge
wechat_messages_total {total_messages}

# HELP wechat_contacts_total Total number of contacts
# TYPE wechat_contacts_total gauge
wechat_contacts_total {len(contacts)}

# HELP wechat_moments_total Total number of moments
# TYPE wechat_moments_total gauge
wechat_moments_total {len(moments)}

# HELP wechat_chats_total Total number of chats
# TYPE wechat_chats_total gauge
wechat_chats_total {len(messages)}
"""


if __name__ == "__main__":
    import uvicorn

    # Use HOST env var for flexibility; 0.0.0.0 for containers, 127.0.0.1 for local dev
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=SERVICE_PORT)
