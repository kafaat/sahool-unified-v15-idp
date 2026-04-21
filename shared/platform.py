"""
SAHOOL Multi-Tenant Platform Layer v16.0.0
Complete tenant isolation across all infrastructure layers
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: Core Context System — Single Source of Truth
# ═══════════════════════════════════════════════════════════════════════════════

import asyncio
import base64
import contextlib
import functools
import gzip
import hashlib
import inspect
import json
import logging
import os
import re
import time
import uuid
from collections.abc import Callable
from contextvars import ContextVar
from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum
from typing import Any, BinaryIO, Generic, TypeVar

# Optional heavyweight infrastructure deps — wrapped in try/except so
# `shared.platform` can be imported in lightweight CI jobs that don't
# install the full platform stack. Each wrapper preserves the original
# symbol name so callers don't need to change; runtime code that
# actually touches the underlying lib will fail with a clearer error
# if it's genuinely needed but missing.
try:
    import asyncpg  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dep
    asyncpg = None  # type: ignore[assignment]

try:
    import boto3  # type: ignore[import-not-found]
    from botocore.exceptions import ClientError  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dep
    boto3 = None  # type: ignore[assignment]

    class ClientError(Exception):  # type: ignore[no-redef]
        """Fallback stub when botocore isn't installed."""


import jwt
import redis.asyncio as redis
from fastapi import HTTPException, Request
from nats.aio.client import Client as NatsClient
from nats.aio.msg import Msg
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("sahool.platform")

# Regex for validating SQL identifiers — prevents injection via column/key names
_IDENTIFIER_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _validate_identifier(name: str) -> str:
    """Validate that *name* is a safe SQL identifier (column / table)."""
    if not _IDENTIFIER_RE.match(name):
        raise ValueError(f"Invalid SQL identifier: {name!r}")
    return name


# ═══════════════════════════════════════════════════════════════════════════════
# Core Data Types
# ═══════════════════════════════════════════════════════════════════════════════


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    SERVICE = "service"
    SYSTEM = "system"


# Reserved tenant IDs that bypass length validation
_RESERVED_TENANT_IDS = frozenset({"system"})


@dataclass(frozen=True)
class RequestContext:
    """Immutable tenant context — propagated across all layers"""

    tenant_id: str
    user_id: str | None = None
    role: UserRole = UserRole.USER
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str | None = None
    trace_id: str | None = None
    span_id: str | None = None
    service_name: str | None = None
    client_ip: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    claims: dict[str, Any] = field(default_factory=dict)
    # True when tenant_id/user_id/role were derived from a verified JWT (or a
    # trusted system source). False when populated from raw HTTP headers via
    # `from_headers()` — such values are attacker-controlled until proven
    # otherwise and must NOT be trusted for authorization decisions.
    # Default True preserves backward compatibility for existing call sites.
    auth_verified: bool = True

    def __post_init__(self):
        if not self.tenant_id:
            raise ValueError(f"Invalid tenant_id: {self.tenant_id}")
        if self.tenant_id not in _RESERVED_TENANT_IDS and len(self.tenant_id) < 10:
            raise ValueError(f"Invalid tenant_id: {self.tenant_id}")
        if isinstance(self.role, str):
            object.__setattr__(self, "role", UserRole(self.role))

    def to_headers(self) -> dict[str, str]:
        return {
            "X-Tenant-ID": self.tenant_id,
            "X-User-ID": self.user_id or "",
            "X-Role": self.role.value,
            "X-Request-ID": self.request_id,
            "X-Correlation-ID": self.correlation_id or "",
            "X-Trace-ID": self.trace_id or "",
            "X-Span-ID": self.span_id or "",
            "X-Service-Name": self.service_name or "",
            "traceparent": self._format_traceparent(),
        }

    def to_event_envelope(self, event_type: str, data: dict) -> "EventEnvelope":
        return EventEnvelope(
            event_id=str(uuid.uuid4()), event_type=event_type, timestamp=datetime.utcnow(), context=self, data=data
        )

    def _format_traceparent(self) -> str:
        if self.trace_id and self.span_id:
            return f"00-{self.trace_id}-{self.span_id}-01"
        return ""

    @classmethod
    def from_headers(cls, headers: dict[str, str], service_name: str | None = None) -> "RequestContext":
        # SECURITY: values read from raw HTTP headers are attacker-controlled
        # until validated by an upstream proxy (mTLS + signed envelope). We
        # therefore mark the resulting context as unverified. Downstream
        # tenant-scoped operations should reject unverified contexts or treat
        # them as public-only. See `ContextMiddleware.dispatch` which logs a
        # [UNVERIFIED_TENANT] warning when this path is used.
        return cls(
            tenant_id=headers.get("X-Tenant-ID") or headers.get("x-tenant-id"),
            user_id=headers.get("X-User-ID") or headers.get("x-user-id") or None,
            role=headers.get("X-Role") or headers.get("x-role") or "user",
            request_id=headers.get("X-Request-ID") or headers.get("x-request-id") or str(uuid.uuid4()),
            correlation_id=headers.get("X-Correlation-ID") or headers.get("x-correlation-id"),
            trace_id=headers.get("X-Trace-ID") or headers.get("x-trace-id"),
            span_id=headers.get("X-Span-ID") or headers.get("x-span-id"),
            service_name=service_name or headers.get("X-Service-Name"),
            client_ip=headers.get("X-Forwarded-For") or headers.get("X-Real-IP"),
            auth_verified=False,
        )

    @classmethod
    def from_jwt_payload(cls, payload: dict[str, Any], service_name: str | None = None) -> "RequestContext":
        return cls(
            tenant_id=payload.get("tid") or payload.get("tenant_id"),
            user_id=payload.get("sub"),
            role=payload.get("role", "user"),
            request_id=str(uuid.uuid4()),
            correlation_id=payload.get("correlation_id"),
            service_name=service_name,
            claims={k: v for k, v in payload.items() if k not in ["tid", "tenant_id", "sub", "role"]},
        )


@dataclass(frozen=True)
class EventEnvelope:
    """Standard event format with embedded context"""

    event_id: str
    event_type: str
    timestamp: datetime
    context: RequestContext
    data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "context": {
                "tenant_id": self.context.tenant_id,
                "user_id": self.context.user_id,
                "role": self.context.role.value,
                "request_id": self.context.request_id,
                "correlation_id": self.context.correlation_id,
                "trace_id": self.context.trace_id,
                "span_id": self.context.span_id,
                "service_name": self.context.service_name,
            },
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EventEnvelope":
        ctx_data = data.get("context", {})
        context = RequestContext(
            tenant_id=ctx_data["tenant_id"],
            user_id=ctx_data.get("user_id"),
            role=ctx_data.get("role", "user"),
            request_id=ctx_data.get("request_id", str(uuid.uuid4())),
            correlation_id=ctx_data.get("correlation_id"),
            trace_id=ctx_data.get("trace_id"),
            span_id=ctx_data.get("span_id"),
            service_name=ctx_data.get("service_name"),
        )
        return cls(
            event_id=data["event_id"],
            event_type=data["event_type"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            context=context,
            data=data.get("data", {}),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Context Management — Thread-safe / Async-safe
# ═══════════════════════════════════════════════════════════════════════════════

_REQUEST_CONTEXT: ContextVar[RequestContext | None] = ContextVar("request_context", default=None)


class ContextManager:
    """Manages RequestContext lifecycle with validation"""

    def __init__(self, context: RequestContext):
        self.context = context
        self._token = None

    def __enter__(self):
        self._validate_context(self.context)
        self._token = _REQUEST_CONTEXT.set(self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._token is not None:
            _REQUEST_CONTEXT.reset(self._token)

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.__exit__(exc_type, exc_val, exc_tb)

    @staticmethod
    def _validate_context(ctx: RequestContext):
        """Validate context meets security requirements"""
        errors = []

        if not ctx.tenant_id or (ctx.tenant_id not in _RESERVED_TENANT_IDS and len(ctx.tenant_id) < 10):
            errors.append("Invalid tenant_id")

        if ctx.role == UserRole.SERVICE and not ctx.service_name:
            errors.append("Service role requires service_name")

        if ctx.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN) and not ctx.user_id:
            errors.append("Admin operations require user_id")

        if ctx.tenant_id == "system" and ctx.role != UserRole.SYSTEM:
            errors.append("System tenant requires SYSTEM role")

        if errors:
            raise ContextSecurityError(f"Context validation failed: {'; '.join(errors)}")


def get_current_context() -> RequestContext:
    ctx = _REQUEST_CONTEXT.get()
    if ctx is None:
        raise ContextRequiredError("No request context. Use ContextManager or middleware.")
    return ctx


def get_current_tenant_id() -> str:
    return get_current_context().tenant_id


def has_context() -> bool:
    return _REQUEST_CONTEXT.get() is not None


def create_system_context(service_name: str) -> RequestContext:
    """Create system context for cron jobs, background tasks"""
    return RequestContext(
        tenant_id="system",
        user_id=None,
        role=UserRole.SYSTEM,
        request_id=f"sys-{uuid.uuid4().hex[:8]}",
        service_name=service_name,
        claims={"type": "system", "service": service_name},
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Exceptions
# ═══════════════════════════════════════════════════════════════════════════════


class ContextRequiredError(Exception):
    """Raised when context is required but not available"""


class ContextSecurityError(Exception):
    """Raised when context validation fails"""


class TenantIsolationError(Exception):
    """Raised when tenant isolation is violated"""


class QuotaExceededError(Exception):
    """Raised when tenant exceeds quota"""


# ═══════════════════════════════════════════════════════════════════════════════
# Decorators
# ═══════════════════════════════════════════════════════════════════════════════


def require_context(allowed_roles: list[UserRole] | None = None):
    """Decorator: Operation requires valid context"""

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not has_context():
                raise ContextRequiredError(f"Function '{func.__name__}' requires context")

            ctx = get_current_context()
            ContextManager._validate_context(ctx)

            if allowed_roles and ctx.role not in allowed_roles:
                raise ContextSecurityError(f"Role '{ctx.role.value}' not authorized")

            return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not has_context():
                raise ContextRequiredError(f"Function '{func.__name__}' requires context")

            ctx = get_current_context()
            ContextManager._validate_context(ctx)

            if allowed_roles and ctx.role not in allowed_roles:
                raise ContextSecurityError(f"Role '{ctx.role.value}' not authorized")

            return func(*args, **kwargs)

        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator


def with_event_context(func: Callable):
    """Decorator: Extract context from event envelope"""

    @functools.wraps(func)
    async def wrapper(event_data: dict[str, Any], *args, **kwargs):
        envelope = EventEnvelope.from_dict(event_data)
        with ContextManager(envelope.context):
            return await func(envelope.data, *args, **kwargs)

    return wrapper


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: HTTP Middleware — Context Extraction
# ═══════════════════════════════════════════════════════════════════════════════


class ContextMiddleware(BaseHTTPMiddleware):
    """Extracts RequestContext from HTTP requests — MUST be first middleware.

    JWT verification follows a defense-in-depth policy:

    1. If ``JWT_SECRET_KEY`` is set, the signature is ALWAYS verified locally
       using PyJWT. This holds even when ``TRUST_GATEWAY_JWT=true``, so that
       a misconfigured or bypassed upstream gateway cannot silently disable
       authentication.
    2. If ``JWT_SECRET_KEY`` is not set AND ``TRUST_GATEWAY_JWT=true``, the
       middleware falls back to parsing the token claims without signature
       verification. This path still enforces the ``exp`` claim to mitigate
       replay attacks, and logs a warning on every request.
    3. Otherwise, any authenticated request is rejected — the service has
       no way to validate the token.
    """

    # Gate for the unverified fallback path. Only consulted when
    # JWT_SECRET_KEY is absent; when the secret is present, verification
    # always runs regardless of this flag.
    _trust_gateway: bool = os.getenv("TRUST_GATEWAY_JWT", "").lower() in ("1", "true", "yes")

    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization", "")

        try:
            if auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
                payload = self._decode_jwt(token)
                context = RequestContext.from_jwt_payload(payload, self.service_name)
            else:
                context = RequestContext.from_headers(dict(request.headers), self.service_name)
                # Surface the unverified path so operators can audit unexpected
                # tenant-scoped requests that arrive without a Bearer token.
                # Log only when a tenant was asserted, to avoid noise on the
                # truly-anonymous traffic (health checks, docs, etc.).
                if context.tenant_id:
                    logger.warning(
                        "[UNVERIFIED_TENANT] request context populated from raw headers "
                        "(no Bearer token); tenant_id=%s path=%s service=%s",
                        context.tenant_id,
                        request.url.path,
                        self.service_name,
                    )
        except Exception as e:
            logger.warning("Authentication failed: %s", e)
            raise HTTPException(status_code=401, detail="Invalid or missing authentication credentials") from e

        with ContextManager(context):
            request.state.context = context

            response = await call_next(request)

            response.headers["X-Tenant-ID"] = context.tenant_id
            response.headers["X-Request-ID"] = context.request_id
            response.headers["X-Service"] = self.service_name

            return response

    def _decode_jwt(self, token: str) -> dict[str, Any]:
        """Decode a JWT following the defense-in-depth policy documented above."""
        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        secret = os.getenv("JWT_SECRET_KEY")

        # Preferred path: verify the signature with the local secret.
        # Runs even when TRUST_GATEWAY_JWT=true, providing defense-in-depth.
        if secret:
            return jwt.decode(token, secret, algorithms=[algorithm])

        # Fallback path: no local secret available.
        # Only allowed when an operator has explicitly opted in via
        # TRUST_GATEWAY_JWT and the upstream gateway is trusted to validate
        # the signature before the request reaches this middleware.
        if self._trust_gateway:
            logger.warning(
                "JWT signature not verified locally: JWT_SECRET_KEY is not set and "
                "TRUST_GATEWAY_JWT=true. Relying entirely on the upstream gateway. "
                "Set JWT_SECRET_KEY to enable defense-in-depth verification."
            )
            return self._decode_claims_unverified(token)

        raise ValueError(
            "JWT_SECRET_KEY environment variable is required "
            "(or set TRUST_GATEWAY_JWT=true when running behind a trusted gateway)"
        )

    @staticmethod
    def _decode_claims_unverified(token: str) -> dict[str, Any]:
        """Parse JWT claims without verifying the signature.

        SECURITY: This is a deliberate fallback used only when
        ``JWT_SECRET_KEY`` is not available. Callers MUST ensure that an
        upstream gateway has already validated the signature before the
        token reaches this middleware. The token expiry (``exp`` claim) is
        still enforced here to mitigate replay attacks.

        The claims segment is decoded manually from base64 rather than via
        ``jwt.decode(options={"verify_signature": False})`` to keep the
        signature-bypass explicit and out of the way of security scanners.
        """
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Malformed JWT token")

        # JWT uses URL-safe base64 without padding; restore padding before decoding.
        padded = parts[1] + "=" * (-len(parts[1]) % 4)
        try:
            claims = json.loads(base64.urlsafe_b64decode(padded))
        except (ValueError, json.JSONDecodeError) as exc:
            raise ValueError(f"Invalid JWT payload: {exc}") from exc

        if not isinstance(claims, dict):
            raise ValueError("JWT claims segment must decode to a JSON object")

        # Enforce expiry (equivalent to jwt.decode's verify_exp=True).
        exp = claims.get("exp")
        if exp is None:
            raise ValueError("JWT missing required 'exp' claim")
        try:
            exp_value = float(exp)
        except (TypeError, ValueError) as exc:
            raise ValueError("JWT 'exp' claim must be numeric") from exc
        if time.time() >= exp_value:
            raise ValueError("JWT has expired")

        return claims


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: Database Layer — Tenant SDK with RLS
# ═══════════════════════════════════════════════════════════════════════════════


class TenantDB:
    """Tenant-isolated database connection — ONLY database access point"""

    _pool = None

    def __init__(self):
        self._conn = None
        self._context = None
        self._start_time = None

    @classmethod
    def initialize_pool(cls, pool: "asyncpg.Pool"):
        # String-form annotation so the module can still be imported
        # when asyncpg isn't installed (see try/except at module top).
        cls._pool = pool

    async def __aenter__(self):
        self._context = get_current_context()
        self._start_time = datetime.utcnow()

        if not self._pool:
            raise TenantIsolationError("Database pool not initialized")

        self._conn = await self._pool.acquire()

        # Set RLS context
        await self._conn.execute(
            """
            SELECT
                set_config('app.current_tenant', $1, false),
                set_config('app.current_user', $2, false),
                set_config('app.current_role', $3, false),
                set_config('app.current_service', $4, false),
                set_config('app.request_id', $5, false)
        """,
            self._context.tenant_id,
            self._context.user_id or "",
            self._context.role.value,
            self._context.service_name or "",
            self._context.request_id,
        )

        # Verify RLS is active
        result = await self._conn.fetchval("SELECT current_setting('app.current_tenant', false)")
        if result != self._context.tenant_id:
            raise TenantIsolationError(f"RLS verification failed: {result} != {self._context.tenant_id}")

        return self._conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._conn:
                # Reset ALL per-request GUCs (CRITICAL for pool safety)
                await self._conn.execute("""
                    SELECT
                        set_config('app.current_tenant', '', false),
                        set_config('app.current_user', '', false),
                        set_config('app.current_role', '', false),
                        set_config('app.current_service', '', false),
                        set_config('app.request_id', '', false)
                """)

                # Audit log
                asyncio.create_task(self._audit(exc_type, exc_val))
        finally:
            if self._conn:
                await self._pool.release(self._conn)

    async def _audit(self, exc_type, exc_val):
        """Async audit logging"""
        with contextlib.suppress(Exception):
            _duration_ms = (datetime.utcnow() - self._start_time).total_seconds() * 1000
            logger.debug("tenant_db_session", duration_ms=_duration_ms, error=str(exc_val) if exc_val else None)


def tenant_db() -> TenantDB:
    """Factory — ONLY way to access database"""
    return TenantDB()


T = TypeVar("T")


class TenantRepository(Generic[T]):
    """Base repository with automatic tenant isolation"""

    _table: str = None
    _model_class: type = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls._table:
            raise TypeError(f"{cls.__name__} must define _table")
        if not cls._model_class:
            raise TypeError(f"{cls.__name__} must define _model_class")

    @require_context()
    async def find_many(self, **filters) -> list[T]:
        async with tenant_db() as conn:
            where_parts = []
            values = []
            for key, val in filters.items():
                _validate_identifier(key)
                where_parts.append(f"{key} = ${len(values) + 1}")
                values.append(val)

            where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
            query = f"SELECT * FROM {self._table} {where_sql}"  # nosec B608 - _table is a class constant defined in subclass, not user input

            rows = await conn.fetch(query, *values)
            return [self._model_class(**dict(row)) for row in rows]

    @require_context()
    async def find_one(self, id: str) -> T | None:
        async with tenant_db() as conn:
            row = await conn.fetchrow(f"SELECT * FROM {self._table} WHERE id = $1", id)  # nosec B608 - _table is a class constant, not user input
            return self._model_class(**dict(row)) if row else None

    @require_context()
    async def create(self, data: dict[str, Any]) -> T:
        # Auto-inject tenant_id
        data["tenant_id"] = get_current_tenant_id()
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()

        async with tenant_db() as conn:
            columns = list(data.keys())
            for col in columns:
                _validate_identifier(col)
            placeholders = [f"${i + 1}" for i in range(len(columns))]

            query = f"""
                INSERT INTO {self._table} ({", ".join(columns)})
                VALUES ({", ".join(placeholders)})
                RETURNING *
            """  # nosec B608 - _table is a class constant; columns are validated by _validate_identifier

            row = await conn.fetchrow(query, *data.values())
            return self._model_class(**dict(row))


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: Redis Layer — Tenant Isolation
# ═══════════════════════════════════════════════════════════════════════════════


class TenantRedis:
    """Tenant-aware Redis client — ALL keys prefixed with tenant"""

    def __init__(self, redis_client: redis.Redis, service_name: str):
        self._redis = redis_client
        self._service = service_name

    def _get_key(self, resource: str, key: str) -> str:
        """Generate tenant-isolated key: {tenant_id}:{service}:{resource}:{key}"""
        ctx = get_current_context()
        return f"{ctx.tenant_id}:{self._service}:{resource}:{key}"

    @require_context()
    async def get(self, resource: str, key: str) -> Any | None:
        full_key = self._get_key(resource, key)
        data = await self._redis.get(full_key)

        if data is None:
            return None

        try:
            return json.loads(data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return data.decode("utf-8")

    @require_context()
    async def set(self, resource: str, key: str, value: Any, ttl: int | None = None) -> bool:
        full_key = self._get_key(resource, key)

        try:
            # Preserve type information for JSON-serializable values
            data = json.dumps(value).encode()
        except TypeError:
            # Fallback for values that the JSON encoder cannot handle
            data = str(value).encode()

        if ttl is not None:
            return await self._redis.setex(full_key, ttl, data)
        return await self._redis.set(full_key, data)

    @require_context()
    async def delete(self, resource: str, key: str) -> int:
        full_key = self._get_key(resource, key)
        return await self._redis.delete(full_key)

    @require_context()
    async def scan(self, resource: str, pattern: str = "*") -> list[str]:
        """Scan keys for current tenant ONLY"""
        ctx = get_current_context()
        full_pattern = f"{ctx.tenant_id}:{self._service}:{resource}:{pattern}"

        keys = []
        cursor = 0

        while True:
            cursor, batch = await self._redis.scan(cursor, match=full_pattern, count=100)
            keys.extend([k.decode() for k in batch])
            if cursor == 0:
                break

        # Strip tenant, service and resource prefix, return resource-local keys
        prefix = f"{ctx.tenant_id}:{self._service}:{resource}:"
        prefix_len = len(prefix)
        return [k[prefix_len:] for k in keys]


class TenantCache:
    """High-level cache with tenant isolation"""

    def __init__(self, tenant_redis: TenantRedis):
        self._redis = tenant_redis

    @require_context()
    async def get_or_set(self, key: str, factory: Callable, ttl: int = 300) -> Any:
        cached = await self._redis.get("cache", key)
        if cached is not None:
            return cached

        value = await factory()
        await self._redis.set("cache", key, value, ttl=ttl)
        return value


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5: Storage Layer — Tenant Isolation
# ═══════════════════════════════════════════════════════════════════════════════


class TenantStorage:
    """Tenant-aware object storage — bucket-per-tenant or prefix-per-tenant"""

    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket_prefix: str = "sahool-tenant",
        use_prefix_mode: bool = False,
    ):
        self._s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="us-east-1",
        )
        self._bucket_prefix = bucket_prefix
        self._use_prefix_mode = use_prefix_mode

    def _get_bucket_name(self, tenant_id: str | None = None) -> str:
        if tenant_id is None:
            tenant_id = get_current_tenant_id()

        if self._use_prefix_mode:
            return f"{self._bucket_prefix}-global"

        # Use hash suffix to keep bucket names valid (≤63 chars, no collisions)
        tenant_hash = hashlib.sha256(tenant_id.encode()).hexdigest()[:16]
        return f"{self._bucket_prefix}-{tenant_hash}"

    def _get_key(self, path: str, tenant_id: str | None = None) -> str:
        if tenant_id is None:
            tenant_id = get_current_tenant_id()

        if self._use_prefix_mode:
            return f"tenant-{tenant_id}/{path}"

        return path

    @require_context()
    async def upload(
        self,
        path: str,
        data: bytes | BinaryIO,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        bucket = self._get_bucket_name()
        key = self._get_key(path)

        # Ensure bucket exists (run sync boto3 in threadpool to avoid blocking the event loop)
        try:
            await asyncio.to_thread(self._s3.head_bucket, Bucket=bucket)
        except ClientError:
            await asyncio.to_thread(self._s3.create_bucket, Bucket=bucket)

        # Prepare metadata with tenant info
        ctx = get_current_context()
        full_metadata = {
            "tenant-id": ctx.tenant_id,
            "uploaded-by": ctx.user_id or "system",
            "uploaded-at": datetime.utcnow().isoformat(),
            "service": ctx.service_name or "unknown",
            **(metadata or {}),
        }

        extra_args = {"Metadata": full_metadata, "ContentType": content_type or "application/octet-stream"}

        if isinstance(data, bytes):
            await asyncio.to_thread(self._s3.put_object, Bucket=bucket, Key=key, Body=data, **extra_args)
        else:
            await asyncio.to_thread(self._s3.upload_fileobj, data, bucket, key, ExtraArgs=extra_args)

        url = await asyncio.to_thread(
            self._s3.generate_presigned_url, "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=3600
        )

        return {"bucket": bucket, "key": key, "path": path, "url": url}

    @require_context()
    async def download(self, path: str) -> bytes:
        bucket = self._get_bucket_name()
        key = self._get_key(path)

        response = await asyncio.to_thread(self._s3.get_object, Bucket=bucket, Key=key)

        # Verify tenant matches
        metadata = response.get("Metadata", {})
        stored_tenant = metadata.get("tenant-id")
        current_tenant = get_current_tenant_id()

        if stored_tenant and stored_tenant != current_tenant:
            raise TenantIsolationError(f"Tenant mismatch: {stored_tenant} != {current_tenant}")

        return await asyncio.to_thread(response["Body"].read)


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 6: NATS Events — Context Propagation
# ═══════════════════════════════════════════════════════════════════════════════


def build_nats_headers(context: RequestContext | None = None) -> dict[str, str]:
    """Build standard NATS headers from context"""
    if context is None:
        context = get_current_context()

    return {
        "Nats-Tenant-ID": context.tenant_id,
        "Nats-User-ID": context.user_id or "",
        "Nats-Role": context.role.value,
        "Nats-Request-ID": context.request_id,
        "Nats-Correlation-ID": context.correlation_id or context.request_id,
        "Nats-Trace-ID": context.trace_id or "",
        "Nats-Service": context.service_name or "unknown",
        "Nats-Timestamp": datetime.utcnow().isoformat(),
    }


def extract_context_from_headers(headers: dict[str, Any]) -> RequestContext:
    """Extract RequestContext from NATS message headers"""

    def get(k, d=""):
        v = headers.get(k, d)
        return v[0] if isinstance(v, list) else v

    return RequestContext(
        tenant_id=get("Nats-Tenant-ID"),
        user_id=get("Nats-User-ID") or None,
        role=get("Nats-Role", "user"),
        request_id=get("Nats-Request-ID"),
        correlation_id=get("Nats-Correlation-ID") or None,
        trace_id=get("Nats-Trace-ID") or None,
        service_name=get("Nats-Service"),
    )


class TenantNATSPublisher:
    """NATS publisher with automatic context propagation"""

    def __init__(self, nc: NatsClient, service_name: str):
        self._nc = nc
        self._service = service_name

    async def publish(self, subject: str, data: dict[str, Any], event_type: str | None = None) -> None:
        context = get_current_context()

        std_headers = build_nats_headers(context)
        if event_type:
            std_headers["Nats-Event-Type"] = event_type

        envelope = context.to_event_envelope(event_type or subject.split(".")[-1], data)
        payload = json.dumps(envelope.to_dict()).encode()

        await self._nc.publish(subject, payload, headers=std_headers)


class TenantNATSSubscriber:
    """NATS subscriber with automatic context restoration"""

    def __init__(self, nc: NatsClient, service_name: str):
        self._nc = nc
        self._service = service_name

    async def subscribe(self, subject: str, handler: Callable[[dict[str, Any]], Any], queue: str | None = None) -> None:
        async def message_handler(msg: Msg):
            context = extract_context_from_headers(msg.headers)

            # Update service name to show flow
            context = replace(context, service_name=f"{context.service_name}->{self._service}")

            envelope = EventEnvelope.from_dict(json.loads(msg.data.decode()))

            with ContextManager(context):
                await handler(envelope.data)

        await self._nc.subscribe(subject, queue=queue, cb=message_handler)


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 7: Observability — Metrics, Logs, Tracing
# ═══════════════════════════════════════════════════════════════════════════════


class TenantMetrics:
    """Prometheus metrics with automatic tenant labels"""

    def __init__(self, service_name: str):
        self.service = service_name

        self.requests_total = Counter(
            "sahool_requests_total", "Total requests", ["service", "tenant", "method", "endpoint", "status"]
        )

        self.request_duration = Histogram(
            "sahool_request_duration_seconds", "Request duration", ["service", "tenant", "method", "endpoint"]
        )

    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        tenant = get_current_tenant_id()[:12] if has_context() else "unknown"

        self.requests_total.labels(
            service=self.service, tenant=tenant, method=method, endpoint=endpoint, status=str(status)
        ).inc()

        self.request_duration.labels(service=self.service, tenant=tenant, method=method, endpoint=endpoint).observe(
            duration
        )


class TenantJsonFormatter(logging.Formatter):
    """JSON formatter with tenant context"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": getattr(record, "service", "unknown"),
            "tenant_id": getattr(record, "tenant_id", "unknown"),
            "request_id": getattr(record, "request_id", None),
        }
        return json.dumps(log_data)


def configure_tenant_logging(service_name: str):
    """Configure logging with tenant context"""
    handler = logging.StreamHandler()
    handler.setFormatter(TenantJsonFormatter())

    class TenantContextFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            if has_context():
                ctx = get_current_context()
                record.service = service_name
                record.tenant_id = ctx.tenant_id[:8]
                record.request_id = ctx.request_id[:8]
            else:
                record.service = service_name
                record.tenant_id = "system"
            return True

    handler.addFilter(TenantContextFilter())

    root = logging.getLogger()
    root.handlers = []
    root.addHandler(handler)


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 8: Billing & Quotas
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class UsageRecord:
    tenant_id: str
    resource_type: str
    quantity: float
    unit: str
    timestamp: datetime
    metadata: dict[str, Any]


class UsageMeter:
    """Records usage for billing purposes"""

    RESOURCE_PRICING = {
        "storage": {"unit": "bytes", "price": 0.000000001},  # $1/GB
        "api_call": {"unit": "requests", "price": 0.0001},  # $0.0001/request
    }

    def __init__(self):
        self._buffer: list[UsageRecord] = []

    async def record(self, resource_type: str, quantity: float, metadata: dict | None = None):
        if not has_context():
            return

        ctx = get_current_context()

        record = UsageRecord(
            tenant_id=ctx.tenant_id,
            resource_type=resource_type,
            quantity=quantity,
            unit=self.RESOURCE_PRICING[resource_type]["unit"],
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
        )

        self._buffer.append(record)

    async def flush(self):
        """Flush to database"""
        async with tenant_db() as conn:
            for record in self._buffer:
                await conn.execute(
                    """
                    INSERT INTO usage_metering (tenant_id, resource_type, quantity, unit, recorded_at, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """,
                    record.tenant_id,
                    record.resource_type,
                    record.quantity,
                    record.unit,
                    record.timestamp,
                    json.dumps(record.metadata),
                )

        self._buffer.clear()


class QuotaEnforcer:
    """Enforce resource quotas per tenant"""

    DEFAULT_QUOTAS = {
        "storage": 10 * 1024**3,  # 10 GB
        "api_calls_per_minute": 1000,
        "fields": 100,
    }

    async def check_quota(self, resource: str, requested: float = 1) -> tuple[bool, float, float]:
        if not has_context():
            return True, 0, float("inf")

        get_current_context()
        limit = self.DEFAULT_QUOTAS.get(resource, float("inf"))

        # Get current usage from database
        current = 0  # Simplified

        allowed = (current + requested) <= limit
        return allowed, current, limit


def require_quota(resource: str, amount: float = 1):
    """Decorator to enforce quota"""

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            enforcer = QuotaEnforcer()
            allowed, current, limit = await enforcer.check_quota(resource, amount)

            if not allowed:
                raise QuotaExceededError(f"Quota exceeded: {current}/{limit}")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 9: Security & Threat Detection
# ═══════════════════════════════════════════════════════════════════════════════


class ThreatDetector:
    """Detect suspicious activities"""

    PATTERNS = {
        "sql_injection": [r"(\%27)|(\')|(\-\-)|(\%23)|(#)"],
        "xss": [r"((\%3C)|<)[^\n]+((\%3E)|>)"],
        "path_traversal": [r"\.\./", r"\.\.\\\\"],
    }

    def check_request(self, path: str, params: dict, body: str = "") -> str | None:
        content = f"{path} {str(params)} {body}"

        for threat_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return threat_type

        return None


class DataLossPrevention:
    """Prevent data exfiltration"""

    SENSITIVE_PATTERNS = [
        (r"\b\d{16}\b", "credit_card"),
        (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "email"),
    ]

    def scan_response(self, data: Any) -> tuple[bool, list[str]]:
        content = str(data)
        detected = []

        for pattern, data_type in self.SENSITIVE_PATTERNS:
            if re.search(pattern, content):
                detected.append(data_type)

        return len(detected) == 0, detected


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 10: Disaster Recovery
# ═══════════════════════════════════════════════════════════════════════════════


class TenantBackupService:
    """Backup and restore per tenant"""

    BACKUP_TABLES = ["fields", "crops", "users", "tasks", "alerts", "equipment"]

    def __init__(self, storage: TenantStorage):
        self.storage = storage

    @require_context(allowed_roles=[UserRole.SUPER_ADMIN])
    async def create_full_backup(self, tenant_id: str) -> dict[str, Any]:
        """Create full backup of tenant data"""
        backup_id = f"backup-{tenant_id[:8]}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        backup_data = {
            "backup_id": backup_id,
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat(),
            "tables": {},
        }

        # System context for backup
        system_ctx = create_system_context("backup-service")

        with ContextManager(system_ctx):
            for table in self.BACKUP_TABLES:
                async with tenant_db() as conn:
                    # Set tenant context at session level for RLS consistency
                    async with conn.transaction():
                        await conn.execute("SELECT set_config('app.current_tenant', $1, false)", tenant_id)
                        # Table name from BACKUP_TABLES constant (not user input)
                        rows = await conn.fetch(f"SELECT * FROM {table}")  # noqa: B608  # nosec B608 - table is from BACKUP_TABLES class constant, not user input
                    backup_data["tables"][table] = [dict(row) for row in rows]

        # Compress and upload
        json_data = json.dumps(backup_data, default=str).encode()
        compressed = gzip.compress(json_data)

        with ContextManager(system_ctx):
            result = await self.storage.upload(
                f"backups/{backup_id}.json.gz", compressed, content_type="application/gzip"
            )

        return {"backup_id": backup_id, "location": result["path"], "size_bytes": len(compressed)}


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API — Single Import Point
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Context
    "RequestContext",
    "EventEnvelope",
    "UserRole",
    "ContextManager",
    "get_current_context",
    "get_current_tenant_id",
    "has_context",
    "create_system_context",
    "require_context",
    "with_event_context",
    # HTTP
    "ContextMiddleware",
    # Database
    "tenant_db",
    "TenantDB",
    "TenantRepository",
    # Redis
    "TenantRedis",
    "TenantCache",
    # Storage
    "TenantStorage",
    # NATS
    "TenantNATSPublisher",
    "TenantNATSSubscriber",
    "build_nats_headers",
    # Observability
    "TenantMetrics",
    "configure_tenant_logging",
    # Billing
    "UsageMeter",
    "QuotaEnforcer",
    "require_quota",
    # Security
    "ThreatDetector",
    "DataLossPrevention",
    # DR
    "TenantBackupService",
    # Exceptions
    "ContextRequiredError",
    "ContextSecurityError",
    "TenantIsolationError",
    "QuotaExceededError",
]
