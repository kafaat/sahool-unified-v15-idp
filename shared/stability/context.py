"""
SAHOOL Unified Request Context
================================
سياق الطلب الموحد لمنصة سهول

Provides a single RequestContext object that consolidates:
- Tenant ID (from JWT tid claim / X-Tenant-ID header)
- Correlation ID (X-Correlation-ID / X-Request-ID / auto-generated)
- Trace context (W3C traceparent / OpenTelemetry)
- User identity (user_id, roles)
- Service metadata (service_name, service_version)

This replaces the fragmented approach where context was scattered across
request.state, multiple ContextVars, and separate middleware.

Usage:
    from shared.stability.context import UnifiedContextMiddleware, get_request_context

    # In main.py - replace separate middleware with single unified one:
    app.add_middleware(
        UnifiedContextMiddleware,
        service_name="field-management-service",
        service_version="16.0.0",
        require_tenant=False,
    )

    # In handlers:
    @app.get("/api/v1/fields")
    async def list_fields(request: Request):
        ctx = get_request_context()
        logger.info("listing fields", tenant_id=ctx.tenant_id, correlation_id=ctx.correlation_id)

    # In event publishers (auto-propagation):
    event = FieldCreatedEvent(field_id="...")
    ctx = get_optional_context()
    if ctx:
        ctx.enrich_event(event)

    # In HTTP client calls (propagate headers downstream):
    ctx = get_request_context()
    headers = ctx.to_propagation_headers()
    await httpx.get("http://service/api", headers=headers)
"""

from __future__ import annotations

import logging
import time
import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

# Single context variable for the entire request context
_request_context: ContextVar[RequestContext | None] = ContextVar("sahool_request_context", default=None)


@dataclass(frozen=False)
class RequestContext:
    """
    Unified request context that consolidates all cross-cutting concerns.
    سياق الطلب الموحد الذي يجمع جميع الاهتمامات المشتركة.

    This is the single source of truth for:
    - Who is making the request (user_id, roles)
    - Which tenant it belongs to (tenant_id)
    - How to trace it (correlation_id, trace_id, span_id)
    - Which service is handling it (service_name, service_version)
    """

    # Identity
    correlation_id: str = ""
    request_id: str = ""

    # Tenant isolation
    tenant_id: str | None = None

    # User identity
    user_id: str | None = None
    roles: list[str] = field(default_factory=list)

    # W3C Trace Context
    trace_id: str | None = None
    span_id: str | None = None
    traceparent: str | None = None

    # Service metadata
    service_name: str = ""
    service_version: str = ""

    # Request metadata
    http_method: str = ""
    http_path: str = ""
    start_time: float = 0.0

    def to_propagation_headers(self) -> dict[str, str]:
        """
        Generate HTTP headers to propagate context to downstream services.
        توليد رؤوس HTTP لنشر السياق إلى الخدمات اللاحقة.

        Returns a dict suitable for httpx/aiohttp/requests calls.
        """
        headers: dict[str, str] = {
            "X-Correlation-ID": self.correlation_id,
            "X-Request-ID": self.request_id,
        }

        if self.tenant_id:
            headers["X-Tenant-ID"] = self.tenant_id
        if self.user_id:
            headers["X-User-ID"] = self.user_id
        if self.traceparent:
            headers["traceparent"] = self.traceparent
        elif self.trace_id and self.span_id:
            headers["traceparent"] = f"00-{self.trace_id}-{self.span_id}-01"

        return headers

    def to_nats_headers(self) -> dict[str, str]:
        """
        Generate NATS message headers for event propagation.
        توليد رؤوس رسائل NATS لنشر الأحداث.
        """
        headers: dict[str, str] = {}

        if self.correlation_id:
            headers["X-Correlation-ID"] = self.correlation_id
        if self.tenant_id:
            headers["X-Tenant-ID"] = self.tenant_id
        if self.trace_id and self.span_id:
            headers["traceparent"] = f"00-{self.trace_id}-{self.span_id}-01"

        return headers

    def enrich_event(self, event: Any) -> None:
        """
        Enrich a BaseEvent with context from this request.
        إثراء حدث بالسياق من هذا الطلب.

        Automatically propagates correlation_id, tenant_id, and trace context
        to outbound events. This ensures end-to-end traceability.
        """
        if hasattr(event, "correlation_id") and not event.correlation_id:
            event.correlation_id = self.correlation_id
        if hasattr(event, "tenant_id_header") and not event.tenant_id_header:
            event.tenant_id_header = self.tenant_id
        if hasattr(event, "trace_id") and not event.trace_id and self.trace_id:
            event.trace_id = self.trace_id
        if hasattr(event, "span_id") and not event.span_id and self.span_id:
            event.span_id = self.span_id

    def to_log_context(self) -> dict[str, Any]:
        """
        Return a dict suitable for structured logging.
        """
        ctx: dict[str, Any] = {
            "correlationId": self.correlation_id,
            "requestId": self.request_id,
            "service": self.service_name,
        }
        if self.tenant_id:
            ctx["tenantId"] = self.tenant_id
        if self.user_id:
            ctx["userId"] = self.user_id
        if self.trace_id:
            ctx["traceId"] = self.trace_id
        return ctx

    @property
    def elapsed_ms(self) -> float:
        """Calculate elapsed time since request start."""
        if self.start_time:
            return (time.perf_counter() - self.start_time) * 1000
        return 0.0

    def has_role(self, role: str) -> bool:
        """Check if the current user has a specific role."""
        return role in self.roles


def get_request_context() -> RequestContext:
    """
    Get the current request context. Raises if not in a request scope.

    Returns:
        RequestContext: The current request context

    Raises:
        RuntimeError: If called outside of a request context
    """
    ctx = _request_context.get()
    if ctx is None:
        raise RuntimeError("Request context not available. Ensure UnifiedContextMiddleware is configured.")
    return ctx


def get_optional_context() -> RequestContext | None:
    """
    Get the current request context if available, otherwise None.
    Useful in code that may run both inside and outside HTTP request scope.
    """
    return _request_context.get()


def set_context_for_worker(
    correlation_id: str,
    tenant_id: str | None = None,
    trace_id: str | None = None,
    service_name: str = "",
) -> RequestContext:
    """
    Manually set request context for background workers / event handlers
    that don't go through HTTP middleware.

    Args:
        correlation_id: The correlation ID from the inbound event
        tenant_id: Tenant ID from the event
        trace_id: Trace ID from the event
        service_name: Name of this worker service

    Returns:
        The created RequestContext
    """
    ctx = RequestContext(
        correlation_id=correlation_id,
        request_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        trace_id=trace_id,
        service_name=service_name,
        start_time=time.perf_counter(),
    )
    _request_context.set(ctx)
    return ctx


def clear_context() -> None:
    """Clear the current request context. Call in finally blocks for workers."""
    _request_context.set(None)


# ─────────────────────────────────────────────────────────────────────────────
# Backward-compatibility bridge to existing ContextVars
# ─────────────────────────────────────────────────────────────────────────────


def _sync_to_legacy_contextvars(ctx: RequestContext) -> None:
    """
    Sync the unified context to legacy ContextVars used by existing modules
    (shared.logging_config, shared.middleware.tenant_context).
    This ensures backward compatibility during migration.
    """
    try:
        from shared.logging_config import correlation_id_var, tenant_id_var, user_id_var

        correlation_id_var.set(ctx.correlation_id)
        if ctx.tenant_id:
            tenant_id_var.set(ctx.tenant_id)
        if ctx.user_id:
            user_id_var.set(ctx.user_id)
    except ImportError:
        pass

    try:
        import structlog

        structlog.contextvars.bind_contextvars(
            correlationId=ctx.correlation_id,
            traceId=ctx.trace_id or ctx.correlation_id,
            tenantId=ctx.tenant_id,
            userId=ctx.user_id,
            service=ctx.service_name,
        )
    except (ImportError, AttributeError):
        pass


def _clear_legacy_contextvars() -> None:
    """Clear legacy ContextVars."""
    try:
        from shared.logging_config import correlation_id_var, tenant_id_var, user_id_var

        correlation_id_var.set(None)
        tenant_id_var.set(None)
        user_id_var.set(None)
    except ImportError:
        pass

    try:
        import structlog

        structlog.contextvars.clear_contextvars()
    except (ImportError, AttributeError):
        pass


# ─────────────────────────────────────────────────────────────────────────────
# OTel trace extraction
# ─────────────────────────────────────────────────────────────────────────────


def _extract_otel_trace() -> tuple[str | None, str | None]:
    """Extract trace_id and span_id from the current OTel span."""
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        span_ctx = span.get_span_context()
        if span_ctx and span_ctx.trace_id != 0:
            return format(span_ctx.trace_id, "032x"), format(span_ctx.span_id, "016x")
    except (ImportError, AttributeError):
        pass
    return None, None


# ─────────────────────────────────────────────────────────────────────────────
# Unified Context Middleware
# ─────────────────────────────────────────────────────────────────────────────

_EXEMPT_PATHS = frozenset(
    {
        "/healthz",
        "/readyz",
        "/livez",
        "/health",
        "/health/live",
        "/health/ready",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json",
    }
)


class UnifiedContextMiddleware(BaseHTTPMiddleware):
    """
    Single middleware that replaces separate request_id, correlation_id,
    tenant_context, and request_logging middleware with one unified implementation.

    الوسيط الموحد الذي يستبدل الوسائط المنفصلة بتنفيذ واحد.

    Execution order (this single middleware handles all):
    1. Extract/generate correlation_id + request_id
    2. Extract tenant from JWT or X-Tenant-ID header
    3. Extract user identity from JWT
    4. Extract W3C trace context
    5. Create unified RequestContext
    6. Set in ContextVar + sync to legacy vars
    7. Process request
    8. Add propagation headers to response
    9. Clean up context

    Configuration:
        service_name: Name of this service (required)
        service_version: Version of this service (default: "16.0.0")
        require_tenant: If True, return 400 for missing tenant (default: False)
        exempt_paths: Additional paths to skip (health checks always skipped)
    """

    def __init__(
        self,
        app,
        service_name: str,
        service_version: str = "16.0.0",
        require_tenant: bool = False,
        exempt_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.service_name = service_name
        self.service_version = service_version
        self.require_tenant = require_tenant
        self.exempt_paths = _EXEMPT_PATHS | set(exempt_paths or [])

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        # ── 1. Correlation ID ──
        correlation_id = (
            request.headers.get("X-Correlation-ID") or request.headers.get("X-Request-ID") or str(uuid.uuid4())
        )
        request_id = request.headers.get("X-Request-ID") or correlation_id

        # ── 2. Tenant ID ──
        tenant_id = None
        user_id = None
        roles: list[str] = []

        # From JWT (if auth middleware already decoded it)
        if hasattr(request.state, "principal"):
            principal = request.state.principal
            tenant_id = principal.get("tid")
            user_id = principal.get("sub")
            roles = principal.get("roles", [])

        # Fallback: X-Tenant-ID header
        if not tenant_id:
            tenant_id = request.headers.get("X-Tenant-ID")

        # From existing request.state (set by other middleware)
        if not user_id and hasattr(request.state, "user_id"):
            user_id = request.state.user_id

        # ── 3. Validate tenant ──
        if not tenant_id and self.require_tenant:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": {
                        "code": "MISSING_TENANT",
                        "message": "Tenant ID is required",
                        "message_ar": "معرف المستأجر مطلوب",
                    },
                },
            )

        # ── 4. W3C Trace Context ──
        traceparent = request.headers.get("traceparent")
        trace_id = None
        span_id = None

        if traceparent:
            # Parse W3C traceparent: 00-{trace_id}-{span_id}-{flags}
            parts = traceparent.split("-")
            if len(parts) >= 3:
                trace_id = parts[1]
                span_id = parts[2]
        else:
            # Try OTel
            trace_id, span_id = _extract_otel_trace()

        # ── 5. Build unified context ──
        ctx = RequestContext(
            correlation_id=correlation_id,
            request_id=request_id,
            tenant_id=tenant_id,
            user_id=user_id,
            roles=roles,
            trace_id=trace_id,
            span_id=span_id,
            traceparent=traceparent,
            service_name=self.service_name,
            service_version=self.service_version,
            http_method=request.method,
            http_path=request.url.path,
            start_time=time.perf_counter(),
        )

        # ── 6. Set context ──
        token = _request_context.set(ctx)

        # Backward compatibility: sync to legacy ContextVars
        _sync_to_legacy_contextvars(ctx)

        # Also set on request.state for compatibility with existing code
        request.state.correlation_id = correlation_id
        request.state.request_id = request_id
        request.state.tenant_id = tenant_id
        request.state.user_id = user_id
        request.state.sahool_context = ctx

        try:
            response = await call_next(request)

            # ── 8. Propagation headers on response ──
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Request-ID"] = request_id
            if trace_id and span_id:
                response.headers["traceparent"] = f"00-{trace_id}-{span_id}-01"

            return response

        finally:
            # ── 9. Cleanup ──
            _request_context.reset(token)
            _clear_legacy_contextvars()
