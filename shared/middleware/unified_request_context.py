"""
Unified Request Context Middleware
وسيط سياق الطلب الموحد

Enforces mandatory request context headers across all services:
- X-Tenant-ID: Tenant identifier (from JWT tid claim or header)
- X-Correlation-ID: Request correlation for distributed tracing
- traceparent: W3C Trace Context propagation header
- X-Request-ID: Unique request identifier

This middleware combines and enhances:
- shared/middleware/tenant_context.py (tenant isolation)
- shared/observability/middleware.py (tracing)

Every outgoing response includes these headers for end-to-end observability.

Usage:
    from shared.middleware.unified_request_context import (
        UnifiedRequestContextMiddleware,
        get_request_context,
    )

    app.add_middleware(UnifiedRequestContextMiddleware)

    @app.get("/endpoint")
    async def handler():
        ctx = get_request_context()
        # ctx.tenant_id, ctx.correlation_id, ctx.trace_id, ctx.request_id
"""

from __future__ import annotations

import logging
import uuid
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

# Context variable for unified request context (async-safe)
_request_context: ContextVar["RequestContext | None"] = ContextVar(
    "unified_request_context", default=None
)


@dataclass(frozen=True)
class RequestContext:
    """
    Immutable unified request context.
    سياق طلب موحد غير قابل للتغيير.

    Contains all mandatory context that must flow through every request
    in the SAHOOL platform for observability and tenant isolation.
    """

    request_id: str
    correlation_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    roles: list[str] | None = None
    trace_id: str | None = None
    span_id: str | None = None
    environment: str = "development"

    def to_headers(self) -> dict[str, str]:
        """Generate headers to propagate context to downstream services."""
        headers = {
            "X-Request-ID": self.request_id,
            "X-Correlation-ID": self.correlation_id,
        }
        if self.tenant_id:
            headers["X-Tenant-ID"] = self.tenant_id
        if self.trace_id:
            headers["traceparent"] = f"00-{self.trace_id}-{self.span_id or '0' * 16}-01"
        return headers

    def to_log_context(self) -> dict[str, Any]:
        """Generate structured logging context."""
        ctx: dict[str, Any] = {
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
        }
        if self.tenant_id:
            ctx["tenant_id"] = self.tenant_id
        if self.user_id:
            ctx["user_id"] = self.user_id
        if self.trace_id:
            ctx["trace_id"] = self.trace_id
        return ctx


def get_request_context() -> RequestContext:
    """
    Get the current unified request context.

    Raises:
        RuntimeError: If called outside of a request context.
    """
    ctx = _request_context.get()
    if ctx is None:
        raise RuntimeError(
            "Request context not available. Ensure UnifiedRequestContextMiddleware is configured."
        )
    return ctx


def get_optional_request_context() -> RequestContext | None:
    """Get the current request context if available, otherwise None."""
    return _request_context.get()


class UnifiedRequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts and enforces unified request context.
    وسيط يستخرج ويفرض سياق الطلب الموحد.

    Combines tenant context, correlation ID, and trace propagation
    into a single middleware for all SAHOOL services.

    Configuration:
        require_tenant: If True, returns 400 for missing tenant_id (default: True)
        require_correlation: If True, generates correlation_id if missing (default: True)
        exempt_paths: Paths that skip tenant requirement (health, docs)
        environment: Current environment name
    """

    def __init__(
        self,
        app,
        require_tenant: bool = True,
        require_correlation: bool = True,
        exempt_paths: list[str] | None = None,
        environment: str = "development",
    ):
        super().__init__(app)
        self.require_tenant = require_tenant
        self.require_correlation = require_correlation
        self.exempt_paths = exempt_paths or [
            "/healthz",
            "/readyz",
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/favicon.ico",
        ]
        self.environment = environment

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)

        # Extract request ID
        request_id = (
            request.headers.get("X-Request-ID")
            or str(uuid.uuid4())
        )

        # Extract correlation ID (generate if missing)
        correlation_id = (
            request.headers.get("X-Correlation-ID")
            or request.headers.get("X-Request-ID")
            or str(uuid.uuid4())
        )

        # Extract tenant context
        tenant_id = None
        user_id = None
        roles = None

        # Priority 1: JWT token (from auth middleware)
        if hasattr(request.state, "principal"):
            principal = request.state.principal
            tenant_id = principal.get("tid")
            user_id = principal.get("sub")
            roles = principal.get("roles", [])

        # Priority 2: X-Tenant-ID header (from Kong or upstream)
        if not tenant_id:
            tenant_id = request.headers.get("X-Tenant-ID")

        # Validate tenant presence
        if not tenant_id and self.require_tenant:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "missing_tenant_context",
                    "message_en": "Tenant ID is required. Provide via JWT or X-Tenant-ID header.",
                    "message_ar": "معرف المستأجر مطلوب. قدمه عبر JWT أو رأس X-Tenant-ID.",
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                },
            )

        # Extract trace context (W3C traceparent)
        trace_id = None
        span_id = None
        traceparent = request.headers.get("traceparent")
        if traceparent:
            parts = traceparent.split("-")
            if len(parts) >= 3:
                trace_id = parts[1]
                span_id = parts[2]

        # Build unified context
        ctx = RequestContext(
            request_id=request_id,
            correlation_id=correlation_id,
            tenant_id=tenant_id,
            user_id=user_id,
            roles=roles,
            trace_id=trace_id,
            span_id=span_id,
            environment=self.environment,
        )

        # Set context var
        token = _request_context.set(ctx)

        # Attach to request.state for compatibility with existing code
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        if tenant_id:
            request.state.tenant_id = tenant_id
            request.state.tenant_context = ctx

        try:
            response = await call_next(request)

            # Add context headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id
            if tenant_id:
                response.headers["X-Tenant-ID"] = tenant_id

            return response
        finally:
            _request_context.reset(token)
