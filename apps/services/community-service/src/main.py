"""
SAHOOL Community Service - خدمة المجتمع الزراعي
================================================
Rocket.Chat integration for farmer community messaging.
Bridges SAHOOL platform with self-hosted Rocket.Chat for:
- Agricultural topic channels (irrigation, diseases, market prices)
- Cooperative group management
- AI-powered advisory bots
- Community announcements and alerts

Port: 8133
"""

VERSION = "16.0.0"

import json
import os
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime, UTC
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
import structlog
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
SHARED_PATH = Path("/app/shared")
if not SHARED_PATH.exists():
    SHARED_PATH = Path(__file__).parent.parent.parent / "shared"
if str(SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(SHARED_PATH))

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Tenant middleware (optional import)
# ---------------------------------------------------------------------------
try:
    from shared.middleware.tenant_context import TenantContextMiddleware

    TENANT_MIDDLEWARE_AVAILABLE = True
except ImportError:
    TENANT_MIDDLEWARE_AVAILABLE = False

# ---------------------------------------------------------------------------
# Unified error handling (optional import)
# ---------------------------------------------------------------------------
try:
    from shared.errors_py import (
        add_request_id_middleware,
        setup_exception_handlers,
    )

    ERROR_HANDLING_AVAILABLE = True
except ImportError:
    ERROR_HANDLING_AVAILABLE = False

# ---------------------------------------------------------------------------
# Auth (optional import)
# ---------------------------------------------------------------------------
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

    class User(BaseModel):  # type: ignore[no-redef]
        id: str = "anonymous"
        username: str = "anonymous"
        email: str = "anonymous@sahool.app"
        tenant_id: str = "default"
        roles: list[str] = []

    async def get_current_user() -> User:  # type: ignore[misc]
        return User()


# ---------------------------------------------------------------------------
# Rate limiting (optional)
# ---------------------------------------------------------------------------
try:
    from slowapi import Limiter
    from slowapi.errors import RateLimitExceeded
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address)
    RATE_LIMIT_AVAILABLE = True
except ImportError:
    RATE_LIMIT_AVAILABLE = False

# ---------------------------------------------------------------------------
# Prometheus metrics (optional)
# ---------------------------------------------------------------------------
try:
    from prometheus_client import Counter, Histogram, generate_latest

    METRICS_AVAILABLE = True
    MESSAGES_POSTED = Counter(
        "community_messages_posted_total",
        "Total messages posted via community service",
        ["channel_type"],
    )
    CHANNELS_CREATED = Counter(
        "community_channels_created_total",
        "Total channels created",
    )
    ADVISORY_POSTED = Counter(
        "community_advisory_posted_total",
        "Total advisory bot messages posted",
        ["advisory_type"],
    )
    RC_REQUEST_DURATION = Histogram(
        "community_rocketchat_request_seconds",
        "Rocket.Chat API request duration",
        ["method", "endpoint"],
    )
    TENANT_SETUPS = Counter(
        "community_tenant_setups_total",
        "Total tenant workspace setups",
    )
except ImportError:
    METRICS_AVAILABLE = False

# ===========================================================================
# Default agricultural channels
# ===========================================================================
DEFAULT_AGRI_CHANNELS = [
    {
        "name": "irrigation",
        "name_ar": "الري",
        "description": "Irrigation scheduling and water management",
        "description_ar": "جدولة الري وإدارة المياه",
        "topic": "💧 Irrigation",
    },
    {
        "name": "crop-diseases",
        "name_ar": "أمراض-المحاصيل",
        "description": "Crop disease identification and treatment",
        "description_ar": "تحديد ومعالجة أمراض المحاصيل",
        "topic": "🌾 Crop Health",
    },
    {
        "name": "market-prices",
        "name_ar": "أسعار-السوق",
        "description": "Agricultural market prices and trading",
        "description_ar": "أسعار السوق الزراعي والتداول",
        "topic": "📊 Market",
    },
    {
        "name": "weather-alerts",
        "name_ar": "تنبيهات-الطقس",
        "description": "Weather forecasts and alerts",
        "description_ar": "توقعات الطقس والتنبيهات",
        "topic": "⛅ Weather",
    },
    {
        "name": "pest-management",
        "name_ar": "إدارة-الآفات",
        "description": "Pest identification and IPM strategies",
        "description_ar": "تحديد الآفات واستراتيجيات الإدارة المتكاملة",
        "topic": "🐛 Pest Control",
    },
    {
        "name": "equipment",
        "name_ar": "المعدات",
        "description": "Equipment sharing and maintenance tips",
        "description_ar": "مشاركة المعدات ونصائح الصيانة",
        "topic": "🚜 Equipment",
    },
    {
        "name": "best-practices",
        "name_ar": "أفضل-الممارسات",
        "description": "Agricultural best practices and knowledge sharing",
        "description_ar": "أفضل الممارسات الزراعية ومشاركة المعرفة",
        "topic": "📚 Knowledge",
    },
    {
        "name": "announcements",
        "name_ar": "الإعلانات",
        "description": "Platform announcements and updates",
        "description_ar": "إعلانات المنصة والتحديثات",
        "topic": "📢 Announcements",
        "read_only": True,
    },
]

# Channel name to advisory type mapping for bot routing
ADVISORY_CHANNEL_MAP = {
    "irrigation": "irrigation",
    "crop-diseases": "crop-diseases",
    "pest-management": "pest-management",
    "weather-alerts": "weather-alerts",
    "market-prices": "market-prices",
    "best-practices": "best-practices",
}


# ===========================================================================
# Pydantic models
# ===========================================================================
class ChannelCreate(BaseModel):
    """Create a new community channel | إنشاء قناة مجتمع جديدة"""

    name: str = Field(..., min_length=2, max_length=64, description="Channel name (English)")
    name_ar: str | None = Field(None, description="Channel name (Arabic) | اسم القناة بالعربية")
    description: str | None = Field(None, max_length=500, description="Channel description")
    description_ar: str | None = Field(None, max_length=500, description="وصف القناة بالعربية")
    topic: str | None = Field(None, max_length=200)
    members: list[str] = Field(default_factory=list, description="Initial member usernames")
    read_only: bool = Field(False, description="Read-only channel | قناة للقراءة فقط")


class ChannelResponse(BaseModel):
    """Channel information | معلومات القناة"""

    id: str
    name: str
    name_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    topic: str | None = None
    members_count: int = 0
    read_only: bool = False
    created_at: str | None = None


class MessagePost(BaseModel):
    """Post a message to a channel | نشر رسالة في قناة"""

    channel_id: str = Field(..., description="Target channel ID or name")
    text: str = Field(..., min_length=1, max_length=5000, description="Message text | نص الرسالة")
    alias: str | None = Field(None, description="Display name override")
    emoji: str | None = Field(None, description="Avatar emoji")
    attachments: list[dict[str, Any]] | None = Field(None, description="Message attachments")


class MessageResponse(BaseModel):
    """Message information | معلومات الرسالة"""

    id: str
    channel_id: str
    text: str
    user: str | None = None
    timestamp: str | None = None


class MessageSearchRequest(BaseModel):
    """Search messages in a channel | البحث في رسائل القناة"""

    channel_id: str = Field(..., description="Channel ID to search in")
    query: str = Field(..., min_length=1, max_length=200, description="Search query | نص البحث")


class UserSyncRequest(BaseModel):
    """Sync a SAHOOL user to Rocket.Chat | مزامنة مستخدم سهول مع روكيت شات"""

    email: str = Field(..., description="User email")
    name: str = Field(..., description="Display name | الاسم المعروض")
    username: str = Field(..., description="Username")
    password: str | None = Field(None, description="Password (generated if empty)")
    roles: list[str] = Field(default_factory=lambda: ["user"], description="Rocket.Chat roles")
    avatar_url: str | None = Field(None, description="Avatar URL")


class UserSyncResponse(BaseModel):
    """User sync result | نتيجة مزامنة المستخدم"""

    rc_user_id: str
    username: str
    synced: bool = True


class AdvisoryBotMessage(BaseModel):
    """Post an advisory bot message | نشر رسالة بوت استشاري"""

    advisory_type: str = Field(
        ...,
        description="Advisory type: irrigation | crop-diseases | pest-management | weather-alerts | market-prices | best-practices",
    )
    text: str = Field(..., min_length=1, max_length=5000, description="Advisory text | نص الاستشارة")
    text_ar: str | None = Field(None, max_length=5000, description="Arabic advisory text | النص بالعربية")
    severity: str | None = Field(None, description="Alert severity: info | warning | critical")
    source: str | None = Field(None, description="Advisory source service")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class AlertBotMessage(BaseModel):
    """Post a weather/pest alert | نشر تنبيه طقس/آفات"""

    alert_type: str = Field(
        ...,
        description="Alert type: weather | pest | disease | frost | flood | heatwave",
    )
    title: str = Field(..., max_length=200, description="Alert title | عنوان التنبيه")
    title_ar: str | None = Field(None, max_length=200, description="Arabic title | العنوان بالعربية")
    text: str = Field(..., min_length=1, max_length=5000, description="Alert body | نص التنبيه")
    text_ar: str | None = Field(None, max_length=5000, description="Arabic alert body | النص بالعربية")
    severity: str = Field("warning", description="Severity: info | warning | critical")
    affected_area: str | None = Field(None, description="Affected geographic area")
    expires_at: str | None = Field(None, description="Alert expiry ISO timestamp")


class TenantSetupRequest(BaseModel):
    """Initialize tenant community workspace | تهيئة مساحة عمل المجتمع للمستأجر"""

    tenant_id: str = Field(..., description="Tenant UUID")
    tenant_name: str = Field(..., description="Tenant display name | اسم المستأجر")
    admin_username: str | None = Field(None, description="Tenant admin username")
    admin_email: str | None = Field(None, description="Tenant admin email")
    extra_channels: list[ChannelCreate] = Field(
        default_factory=list,
        description="Additional channels beyond defaults",
    )


class TenantSetupResponse(BaseModel):
    """Tenant setup result | نتيجة تهيئة المستأجر"""

    tenant_id: str
    channels_created: int
    channels: list[ChannelResponse]
    admin_synced: bool = False


class MemberInfo(BaseModel):
    """Channel member information | معلومات عضو القناة"""

    user_id: str
    username: str
    name: str | None = None
    status: str | None = None


class HistoryMessage(BaseModel):
    """Historical message | رسالة تاريخية"""

    id: str
    text: str
    user: str | None = None
    username: str | None = None
    timestamp: str | None = None
    pinned: bool = False


# ===========================================================================
# Rocket.Chat client
# ===========================================================================
class RocketChatClient:
    """Async wrapper around Rocket.Chat REST API v1."""

    def __init__(self, base_url: str, admin_user: str, admin_password: str):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/v1"
        self.admin_user = admin_user
        self.admin_password = admin_password
        self._auth_token: str | None = None
        self._user_id: str | None = None
        self._client: httpx.AsyncClient | None = None

    async def init(self) -> None:
        """Initialize HTTP client and authenticate."""
        self._client = httpx.AsyncClient(timeout=30.0)
        await self.login(self.admin_user, self.admin_password)

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._auth_token and self._user_id:
            headers["X-Auth-Token"] = self._auth_token
            headers["X-User-Id"] = self._user_id
        return headers

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        """Execute an authenticated request to Rocket.Chat API."""
        if not self._client:
            raise RuntimeError("RocketChatClient not initialized - call init() first")

        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        start = time.monotonic()
        try:
            response = await self._client.request(
                method,
                url,
                json=data,
                params=params,
                headers=self._headers(),
            )
            duration = time.monotonic() - start
            if METRICS_AVAILABLE:
                RC_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

            if response.status_code >= 400:
                body = response.text
                logger.error(
                    "rocketchat_api_error",
                    status=response.status_code,
                    endpoint=endpoint,
                    body=body[:500],
                )
                raise HTTPException(
                    status_code=502,
                    detail=f"Rocket.Chat API error: {response.status_code} - {body[:200]}",
                )
            return response.json()
        except httpx.RequestError as exc:
            logger.error("rocketchat_connection_error", endpoint=endpoint, error=str(exc))
            raise HTTPException(
                status_code=502,
                detail=f"Cannot reach Rocket.Chat at {self.base_url}: {exc}",
            ) from exc

    # -----------------------------------------------------------------------
    # Authentication
    # -----------------------------------------------------------------------
    async def login(self, username: str, password: str) -> tuple[str, str]:
        """Authenticate with Rocket.Chat and store credentials."""
        result = await self._request("POST", "login", data={"user": username, "password": password})
        data = result.get("data", {})
        self._auth_token = data.get("authToken", "")
        self._user_id = data.get("userId", "")
        logger.info("rocketchat_authenticated", user_id=self._user_id)
        return self._auth_token, self._user_id

    # -----------------------------------------------------------------------
    # Channels
    # -----------------------------------------------------------------------
    async def create_channel(
        self,
        name: str,
        description: str = "",
        members: list[str] | None = None,
        read_only: bool = False,
    ) -> dict:
        """Create a public channel."""
        payload: dict[str, Any] = {
            "name": name,
            "readOnly": read_only,
        }
        if members:
            payload["members"] = members
        result = await self._request("POST", "channels.create", data=payload)
        channel = result.get("channel", {})

        # Set description and topic
        if description and channel.get("_id"):
            await self._request(
                "POST",
                "channels.setDescription",
                data={"roomId": channel["_id"], "description": description},
            )
        return channel

    async def get_channels(self, count: int = 100, offset: int = 0) -> list[dict]:
        """List public channels."""
        result = await self._request(
            "GET",
            "channels.list",
            params={"count": count, "offset": offset},
        )
        return result.get("channels", [])

    async def add_user_to_channel(self, channel_id: str, user_id: str) -> dict:
        """Add a user to a channel."""
        return await self._request(
            "POST",
            "channels.invite",
            data={"roomId": channel_id, "userId": user_id},
        )

    async def remove_user_from_channel(self, channel_id: str, user_id: str) -> dict:
        """Remove a user from a channel."""
        return await self._request(
            "POST",
            "channels.kick",
            data={"roomId": channel_id, "userId": user_id},
        )

    async def get_channel_history(
        self,
        channel_id: str,
        count: int = 50,
        oldest: str | None = None,
    ) -> list[dict]:
        """Get channel message history."""
        params: dict[str, Any] = {"roomId": channel_id, "count": count}
        if oldest:
            params["oldest"] = oldest
        result = await self._request("GET", "channels.history", params=params)
        return result.get("messages", [])

    async def get_channel_members(self, channel_id: str, count: int = 100) -> list[dict]:
        """Get members of a channel."""
        result = await self._request(
            "GET",
            "channels.members",
            params={"roomId": channel_id, "count": count},
        )
        return result.get("members", [])

    async def pin_message(self, message_id: str) -> dict:
        """Pin a message."""
        return await self._request("POST", "chat.pinMessage", data={"messageId": message_id})

    async def search_messages(self, channel_id: str, query: str) -> list[dict]:
        """Search messages in a channel."""
        result = await self._request(
            "GET",
            "chat.search",
            params={"roomId": channel_id, "searchText": query},
        )
        return result.get("messages", [])

    # -----------------------------------------------------------------------
    # Messages
    # -----------------------------------------------------------------------
    async def post_message(
        self,
        channel: str,
        text: str,
        alias: str | None = None,
        emoji: str | None = None,
        attachments: list[dict] | None = None,
    ) -> dict:
        """Post a message to a channel (by name or ID)."""
        payload: dict[str, Any] = {"channel": channel, "text": text}
        if alias:
            payload["alias"] = alias
        if emoji:
            payload["emoji"] = emoji
        if attachments:
            payload["attachments"] = attachments
        result = await self._request("POST", "chat.postMessage", data=payload)
        return result.get("message", {})

    # -----------------------------------------------------------------------
    # Users
    # -----------------------------------------------------------------------
    async def create_user(
        self,
        email: str,
        name: str,
        username: str,
        password: str,
        roles: list[str] | None = None,
    ) -> dict:
        """Create a new Rocket.Chat user."""
        payload: dict[str, Any] = {
            "email": email,
            "name": name,
            "username": username,
            "password": password,
            "roles": roles or ["user"],
            "verified": True,
        }
        result = await self._request("POST", "users.create", data=payload)
        return result.get("user", {})

    async def set_user_avatar(self, user_id: str, avatar_url: str) -> dict:
        """Set a user's avatar by URL."""
        return await self._request(
            "POST",
            "users.setAvatar",
            data={"userId": user_id, "avatarUrl": avatar_url},
        )


# ===========================================================================
# NATS event helper
# ===========================================================================
async def publish_event(app: FastAPI, subject: str, payload: dict) -> None:
    """Publish a NATS event if connected."""
    nc = getattr(app.state, "nc", None)
    if nc:
        try:
            data = json.dumps(
                {**payload, "timestamp": datetime.now(UTC).isoformat(), "service": "community-service"},
            ).encode()
            await nc.publish(subject, data)
            logger.debug("nats_event_published", subject=subject)
        except Exception as exc:
            logger.error("nats_publish_error", subject=subject, error=str(exc))


# ===========================================================================
# Lifespan
# ===========================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting community-service...", version=VERSION)

    # ---- Rocket.Chat client ------------------------------------------------
    rc_url = os.getenv("ROCKETCHAT_URL", "http://rocketchat:3000")
    rc_user = os.getenv("ROCKETCHAT_ADMIN_USER", "")
    rc_pass = os.getenv("ROCKETCHAT_ADMIN_PASSWORD", "")
    if rc_user and rc_pass:
        try:
            rc = RocketChatClient(rc_url, rc_user, rc_pass)
            await rc.init()
            app.state.rc = rc
            app.state.rc_connected = True
            logger.info("Rocket.Chat client initialized", url=rc_url)
        except Exception as exc:
            logger.error("Failed to connect to Rocket.Chat", error=str(exc))
            app.state.rc = None
            app.state.rc_connected = False
    else:
        app.state.rc = None
        app.state.rc_connected = False
        logger.warning("ROCKETCHAT_ADMIN_USER/PASSWORD not set, Rocket.Chat integration disabled")

    # ---- Database -----------------------------------------------------------
    db_url = os.getenv("DATABASE_URL")
    if db_url and os.getenv("ENVIRONMENT", "development") != "development":
        if "sslmode" not in db_url:
            db_url += "?sslmode=require" if "?" not in db_url else "&sslmode=require"
    if db_url:
        try:
            import asyncpg

            app.state.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
            app.state.db_connected = True
            logger.info("Database connection pool created")
        except Exception as exc:
            logger.error("Failed to connect to database", error=str(exc))
            app.state.db_connected = False
    else:
        app.state.db_connected = False
        logger.warning("DATABASE_URL not set, running without database")

    # ---- Redis --------------------------------------------------------------
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            import redis.asyncio as aioredis

            app.state.redis = aioredis.from_url(redis_url, decode_responses=True)
            await app.state.redis.ping()
            app.state.redis_connected = True
            logger.info("Redis connection established")
        except Exception as exc:
            logger.error("Failed to connect to Redis", error=str(exc))
            app.state.redis = None
            app.state.redis_connected = False
    else:
        app.state.redis = None
        app.state.redis_connected = False
        logger.warning("REDIS_URL not set, running without Redis")

    # ---- NATS ---------------------------------------------------------------
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            import nats as nats_lib

            app.state.nc = await nats_lib.connect(nats_url)
            app.state.nats_connected = True
            logger.info("NATS connection established", url=nats_url)
        except Exception as exc:
            logger.error("Failed to connect to NATS", error=str(exc))
            app.state.nc = None
            app.state.nats_connected = False
    else:
        app.state.nc = None
        app.state.nats_connected = False
        logger.warning("NATS_URL not set, running without NATS")

    yield

    # ---- Shutdown -----------------------------------------------------------
    logger.info("Shutting down community-service...")
    rc_client = getattr(app.state, "rc", None)
    if rc_client:
        await rc_client.close()
        logger.info("Rocket.Chat client closed")
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
        logger.info("Database connection pool closed")
    if getattr(app.state, "redis", None):
        await app.state.redis.close()
        logger.info("Redis connection closed")
    if getattr(app.state, "nc", None):
        await app.state.nc.close()
        logger.info("NATS connection closed")


# ===========================================================================
# FastAPI application
# ===========================================================================
app = FastAPI(
    title="SAHOOL Community Service",
    description="Rocket.Chat integration for farmer community messaging - خدمة المجتمع الزراعي",
    version=VERSION,
    lifespan=lifespan,
)

# CORS
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "https://sahool.app,https://admin.sahool.app,http://localhost:3000",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Tenant-Id", "X-Request-ID"],
)

# Tenant middleware
if TENANT_MIDDLEWARE_AVAILABLE:
    app.add_middleware(TenantContextMiddleware)

# Error handling
if ERROR_HANDLING_AVAILABLE:
    setup_exception_handlers(app)
    add_request_id_middleware(app)

# Rate limiter
if RATE_LIMIT_AVAILABLE:
    from slowapi import _rate_limit_exceeded_handler

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ===========================================================================
# Helper: get Rocket.Chat client from request
# ===========================================================================
def get_rc(request: Request) -> RocketChatClient:
    rc = getattr(request.app.state, "rc", None)
    if not rc or not getattr(request.app.state, "rc_connected", False):
        raise HTTPException(
            status_code=503,
            detail="Rocket.Chat integration not available | تكامل روكيت شات غير متاح",
        )
    return rc


# ===========================================================================
# Health endpoints
# ===========================================================================
@app.get("/healthz", tags=["Health"])
def healthz():
    """Liveness probe."""
    return {"status": "ok", "service": "community-service", "version": VERSION}


@app.get("/readyz", tags=["Health"])
def readyz():
    """Readiness probe."""
    return {
        "status": "ok",
        "rocketchat": getattr(app.state, "rc_connected", False),
        "database": getattr(app.state, "db_connected", False),
        "redis": getattr(app.state, "redis_connected", False),
        "nats": getattr(app.state, "nats_connected", False),
    }


@app.get("/health", tags=["Health"])
def health():
    """Combined health status."""
    rc_ok = getattr(app.state, "rc_connected", False)
    db_ok = getattr(app.state, "db_connected", False)
    return {
        "status": "ok" if rc_ok else "degraded",
        "service": "community-service",
        "version": VERSION,
        "components": {
            "rocketchat": rc_ok,
            "database": db_ok,
            "redis": getattr(app.state, "redis_connected", False),
            "nats": getattr(app.state, "nats_connected", False),
        },
    }


# ===========================================================================
# Metrics endpoint
# ===========================================================================
@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Prometheus metrics endpoint."""
    if METRICS_AVAILABLE:
        from fastapi.responses import PlainTextResponse

        return PlainTextResponse(generate_latest().decode(), media_type="text/plain; charset=utf-8")
    return {"message": "prometheus-client not installed"}


# ===========================================================================
# Tenant setup
# ===========================================================================
@app.post("/api/v1/community/setup-tenant", response_model=TenantSetupResponse, tags=["Tenant"])
async def setup_tenant(
    request: Request,
    body: TenantSetupRequest,
    user: User = Depends(get_current_user),
):
    """
    Initialize tenant community workspace - تهيئة مساحة عمل المجتمع للمستأجر

    Creates all default agricultural channels for a tenant and optionally syncs
    an admin user to Rocket.Chat.
    """
    rc = get_rc(request)
    created_channels: list[ChannelResponse] = []
    prefix = f"t-{body.tenant_id[:8]}-"

    # Create default channels with tenant prefix
    for ch_def in DEFAULT_AGRI_CHANNELS:
        ch_name = f"{prefix}{ch_def['name']}"
        description = f"{ch_def['description']} | {ch_def['description_ar']}"
        try:
            channel = await rc.create_channel(
                name=ch_name,
                description=description,
                read_only=ch_def.get("read_only", False),
            )
            created_channels.append(
                ChannelResponse(
                    id=channel.get("_id", ""),
                    name=ch_name,
                    name_ar=ch_def.get("name_ar"),
                    description=ch_def.get("description"),
                    description_ar=ch_def.get("description_ar"),
                    topic=ch_def.get("topic"),
                    read_only=ch_def.get("read_only", False),
                )
            )
            if METRICS_AVAILABLE:
                CHANNELS_CREATED.inc()
        except HTTPException:
            logger.warning("channel_creation_failed", channel=ch_name)

    # Create extra channels
    for extra in body.extra_channels:
        ch_name = f"{prefix}{extra.name}"
        try:
            channel = await rc.create_channel(
                name=ch_name,
                description=extra.description or "",
                members=extra.members,
                read_only=extra.read_only,
            )
            created_channels.append(
                ChannelResponse(
                    id=channel.get("_id", ""),
                    name=ch_name,
                    name_ar=extra.name_ar,
                    description=extra.description,
                    description_ar=extra.description_ar,
                    topic=extra.topic,
                    read_only=extra.read_only,
                )
            )
            if METRICS_AVAILABLE:
                CHANNELS_CREATED.inc()
        except HTTPException:
            logger.warning("extra_channel_creation_failed", channel=ch_name)

    # Sync admin user
    admin_synced = False
    if body.admin_username and body.admin_email:
        try:
            await rc.create_user(
                email=body.admin_email,
                name=body.tenant_name,
                username=body.admin_username,
                password=uuid4().hex[:16],
                roles=["admin"],
            )
            admin_synced = True
        except HTTPException:
            logger.warning("admin_sync_failed", username=body.admin_username)

    if METRICS_AVAILABLE:
        TENANT_SETUPS.inc()

    await publish_event(
        request.app,
        "sahool.community.tenant_setup",
        {
            "tenant_id": body.tenant_id,
            "channels_created": len(created_channels),
            "admin_synced": admin_synced,
            "user_id": user.id,
        },
    )

    return TenantSetupResponse(
        tenant_id=body.tenant_id,
        channels_created=len(created_channels),
        channels=created_channels,
        admin_synced=admin_synced,
    )


# ===========================================================================
# Channels
# ===========================================================================
@app.post("/api/v1/community/channels", response_model=ChannelResponse, tags=["Channels"])
async def create_channel(
    request: Request,
    body: ChannelCreate,
    user: User = Depends(get_current_user),
):
    """Create a community channel | إنشاء قناة مجتمع"""
    rc = get_rc(request)
    description = body.description or ""
    if body.description_ar:
        description = f"{description} | {body.description_ar}"
    channel = await rc.create_channel(
        name=body.name,
        description=description,
        members=body.members,
        read_only=body.read_only,
    )
    if METRICS_AVAILABLE:
        CHANNELS_CREATED.inc()

    await publish_event(
        request.app,
        "sahool.community.channel_created",
        {"channel_id": channel.get("_id", ""), "name": body.name, "user_id": user.id},
    )
    return ChannelResponse(
        id=channel.get("_id", ""),
        name=channel.get("name", body.name),
        name_ar=body.name_ar,
        description=body.description,
        description_ar=body.description_ar,
        topic=body.topic,
        members_count=len(body.members),
        read_only=body.read_only,
    )


@app.get("/api/v1/community/channels", tags=["Channels"])
async def list_channels(
    request: Request,
    count: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
):
    """List community channels | عرض قنوات المجتمع"""
    rc = get_rc(request)
    channels = await rc.get_channels(count=count, offset=offset)
    return {
        "channels": [
            {
                "id": ch.get("_id", ""),
                "name": ch.get("name", ""),
                "description": ch.get("description", ""),
                "topic": ch.get("topic", ""),
                "members_count": ch.get("usersCount", 0),
                "read_only": ch.get("ro", False),
            }
            for ch in channels
        ],
        "count": len(channels),
    }


@app.post("/api/v1/community/channels/{channel_id}/join", tags=["Channels"])
async def join_channel(
    request: Request,
    channel_id: str,
    user: User = Depends(get_current_user),
):
    """Join a community channel | الانضمام إلى قناة"""
    rc = get_rc(request)
    # Use the SAHOOL user ID as Rocket.Chat user lookup
    await rc.add_user_to_channel(channel_id, user.id)

    await publish_event(
        request.app,
        "sahool.community.user_joined",
        {"channel_id": channel_id, "user_id": user.id},
    )
    return {"status": "joined", "channel_id": channel_id, "user_id": user.id}


@app.post("/api/v1/community/channels/{channel_id}/leave", tags=["Channels"])
async def leave_channel(
    request: Request,
    channel_id: str,
    user: User = Depends(get_current_user),
):
    """Leave a community channel | مغادرة قناة"""
    rc = get_rc(request)
    await rc.remove_user_from_channel(channel_id, user.id)
    return {"status": "left", "channel_id": channel_id, "user_id": user.id}


@app.get("/api/v1/community/channels/{channel_id}/members", tags=["Channels"])
async def get_channel_members(
    request: Request,
    channel_id: str,
    count: int = Query(100, ge=1, le=500),
    user: User = Depends(get_current_user),
):
    """Get channel members | عرض أعضاء القناة"""
    rc = get_rc(request)
    members = await rc.get_channel_members(channel_id, count=count)
    return {
        "members": [
            MemberInfo(
                user_id=m.get("_id", ""),
                username=m.get("username", ""),
                name=m.get("name"),
                status=m.get("status"),
            ).model_dump()
            for m in members
        ],
        "count": len(members),
    }


# ===========================================================================
# Messages
# ===========================================================================
@app.post("/api/v1/community/messages", response_model=MessageResponse, tags=["Messages"])
async def post_message(
    request: Request,
    body: MessagePost,
    user: User = Depends(get_current_user),
):
    """Post a message to a channel | نشر رسالة في قناة"""
    rc = get_rc(request)
    msg = await rc.post_message(
        channel=body.channel_id,
        text=body.text,
        alias=body.alias,
        emoji=body.emoji,
        attachments=body.attachments,
    )
    if METRICS_AVAILABLE:
        MESSAGES_POSTED.labels(channel_type="user").inc()

    await publish_event(
        request.app,
        "sahool.community.message_posted",
        {"channel_id": body.channel_id, "message_id": msg.get("_id", ""), "user_id": user.id},
    )
    return MessageResponse(
        id=msg.get("_id", ""),
        channel_id=body.channel_id,
        text=body.text,
        user=user.username,
        timestamp=msg.get("ts"),
    )


@app.get("/api/v1/community/channels/{channel_id}/history", tags=["Messages"])
async def get_channel_history(
    request: Request,
    channel_id: str,
    count: int = Query(50, ge=1, le=200),
    oldest: str | None = Query(None, description="ISO timestamp for oldest message"),
    user: User = Depends(get_current_user),
):
    """Get channel message history | عرض سجل رسائل القناة"""
    rc = get_rc(request)
    messages = await rc.get_channel_history(channel_id, count=count, oldest=oldest)
    return {
        "messages": [
            HistoryMessage(
                id=m.get("_id", ""),
                text=m.get("msg", ""),
                user=m.get("u", {}).get("name"),
                username=m.get("u", {}).get("username"),
                timestamp=m.get("ts"),
                pinned=m.get("pinned", False),
            ).model_dump()
            for m in messages
        ],
        "count": len(messages),
    }


@app.post("/api/v1/community/messages/search", tags=["Messages"])
async def search_messages(
    request: Request,
    body: MessageSearchRequest,
    user: User = Depends(get_current_user),
):
    """Search messages in a channel | البحث في رسائل القناة"""
    rc = get_rc(request)
    messages = await rc.search_messages(body.channel_id, body.query)
    return {
        "messages": [
            {
                "id": m.get("_id", ""),
                "text": m.get("msg", ""),
                "user": m.get("u", {}).get("username"),
                "timestamp": m.get("ts"),
            }
            for m in messages
        ],
        "count": len(messages),
        "query": body.query,
    }


# ===========================================================================
# User sync
# ===========================================================================
@app.post("/api/v1/community/users/sync", response_model=UserSyncResponse, tags=["Users"])
async def sync_user(
    request: Request,
    body: UserSyncRequest,
    user: User = Depends(get_current_user),
):
    """Sync a SAHOOL user to Rocket.Chat | مزامنة مستخدم سهول مع روكيت شات"""
    rc = get_rc(request)
    password = body.password or uuid4().hex[:16]
    rc_user = await rc.create_user(
        email=body.email,
        name=body.name,
        username=body.username,
        password=password,
        roles=body.roles,
    )

    rc_user_id = rc_user.get("_id", "")
    if body.avatar_url and rc_user_id:
        try:
            await rc.set_user_avatar(rc_user_id, body.avatar_url)
        except HTTPException:
            logger.warning("avatar_set_failed", user_id=rc_user_id)

    return UserSyncResponse(
        rc_user_id=rc_user_id,
        username=body.username,
        synced=True,
    )


# ===========================================================================
# Bot endpoints
# ===========================================================================
@app.post("/api/v1/community/bots/advisory", tags=["Bots"])
async def post_advisory(
    request: Request,
    body: AdvisoryBotMessage,
    user: User = Depends(get_current_user),
):
    """
    Post advisory bot message to relevant channel.
    نشر رسالة بوت استشاري في القناة المناسبة
    """
    rc = get_rc(request)
    channel_name = ADVISORY_CHANNEL_MAP.get(body.advisory_type, "best-practices")

    # Build bilingual message
    severity_emoji = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}.get(body.severity or "info", "ℹ️")
    text_parts = [f"{severity_emoji} **Advisory | استشارة**"]
    text_parts.append(body.text)
    if body.text_ar:
        text_parts.append(f"\n---\n{body.text_ar}")
    if body.source:
        text_parts.append(f"\n_Source: {body.source}_")

    full_text = "\n".join(text_parts)

    msg = await rc.post_message(
        channel=channel_name,
        text=full_text,
        alias="SAHOOL Advisory Bot",
        emoji=":robot:",
    )

    if METRICS_AVAILABLE:
        ADVISORY_POSTED.labels(advisory_type=body.advisory_type).inc()
        MESSAGES_POSTED.labels(channel_type="advisory_bot").inc()

    await publish_event(
        request.app,
        "sahool.community.advisory_posted",
        {
            "advisory_type": body.advisory_type,
            "channel": channel_name,
            "message_id": msg.get("_id", ""),
            "severity": body.severity,
            "user_id": user.id,
        },
    )
    return {
        "status": "posted",
        "channel": channel_name,
        "message_id": msg.get("_id", ""),
        "advisory_type": body.advisory_type,
    }


@app.post("/api/v1/community/bots/alert", tags=["Bots"])
async def post_alert(
    request: Request,
    body: AlertBotMessage,
    user: User = Depends(get_current_user),
):
    """
    Post weather/pest alert to relevant channel.
    نشر تنبيه طقس/آفات في القناة المناسبة
    """
    rc = get_rc(request)

    # Route alert to appropriate channel
    alert_channel_map = {
        "weather": "weather-alerts",
        "frost": "weather-alerts",
        "flood": "weather-alerts",
        "heatwave": "weather-alerts",
        "pest": "pest-management",
        "disease": "crop-diseases",
    }
    channel_name = alert_channel_map.get(body.alert_type, "announcements")

    severity_emoji = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}.get(body.severity, "⚠️")

    text_parts = [f"{severity_emoji} **{body.title}**"]
    if body.title_ar:
        text_parts[0] += f" | **{body.title_ar}**"
    text_parts.append(body.text)
    if body.text_ar:
        text_parts.append(f"\n---\n{body.text_ar}")
    if body.affected_area:
        text_parts.append(f"\n📍 Area: {body.affected_area}")
    if body.expires_at:
        text_parts.append(f"\n⏰ Expires: {body.expires_at}")

    full_text = "\n".join(text_parts)

    msg = await rc.post_message(
        channel=channel_name,
        text=full_text,
        alias="SAHOOL Alert System",
        emoji=":warning:",
    )

    if METRICS_AVAILABLE:
        MESSAGES_POSTED.labels(channel_type="alert_bot").inc()

    await publish_event(
        request.app,
        "sahool.community.alert_posted",
        {
            "alert_type": body.alert_type,
            "severity": body.severity,
            "channel": channel_name,
            "message_id": msg.get("_id", ""),
            "affected_area": body.affected_area,
            "user_id": user.id,
        },
    )
    return {
        "status": "posted",
        "channel": channel_name,
        "message_id": msg.get("_id", ""),
        "alert_type": body.alert_type,
        "severity": body.severity,
    }


# ===========================================================================
# Entrypoint
# ===========================================================================
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8133"))
    uvicorn.run("src.main:app", host=host, port=port, reload=True)
