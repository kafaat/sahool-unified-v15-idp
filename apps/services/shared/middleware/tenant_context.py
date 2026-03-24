"""
SAHOOL Tenant Context Middleware
================================
Middleware for extracting and managing tenant context in multi-tenant SaaS environment.

Features:
- Extracts tenant_id from JWT or X-Tenant-ID header
- Provides async context for tenant isolation
- Supports tenant-scoped database queries
- Logs with tenant context for observability

Usage:
    from shared.middleware.tenant_context import (
        TenantContextMiddleware,
        get_current_tenant,
        TenantContext,
    )

    app.add_middleware(TenantContextMiddleware)

    @app.get("/resources")
    async def get_resources():
        tenant = get_current_tenant()
        # Query with tenant isolation
        return await db.query(Resource).filter(tenant_id=tenant.id).all()
"""

import logging
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

# Context variable for tenant isolation (async-safe)
_tenant_context: ContextVar[Optional["TenantContext"]] = ContextVar("tenant_context", default=None)


@dataclass
class TenantContext:
    """
    Immutable tenant context for the current request.

    Attributes:
        id: The unique tenant identifier
        user_id: The authenticated user's ID (if available)
        roles: List of user roles (if available)
    """

    id: str
    user_id: str | None = None
    roles: list[str] | None = None

    def has_role(self, role: str) -> bool:
        """Check if the current user has a specific role."""
        return role in (self.roles or [])


def get_current_tenant() -> TenantContext:
    """
    Get the current tenant context.

    Raises:
        RuntimeError: If called outside of a request context

    Returns:
        TenantContext: The current tenant context
    """
    ctx = _tenant_context.get()
    if ctx is None:
        raise RuntimeError("Tenant context not available. Ensure TenantContextMiddleware is configured.")
    return ctx


def get_current_tenant_id() -> str:
    """
    Get the current tenant ID (convenience function).

    Returns:
        str: The current tenant ID
    """
    return get_current_tenant().id


def get_optional_tenant() -> TenantContext | None:
    """
    Get the current tenant context if available, otherwise None.

    Returns:
        Optional[TenantContext]: The current tenant context or None
    """
    return _tenant_context.get()


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts tenant context from requests and makes it
    available throughout the request lifecycle.

    Priority order for tenant_id extraction:
    1. JWT token claim (tenant_id or tid for cross-language compatibility)
    2. X-Tenant-ID header
    3. Query parameter (for webhooks)

    Configuration:
        - require_tenant: If True, returns 400 for missing tenant (default: True)
        - allow_query_param: If True, allows ?tenant_id= parameter (default: False)
        - exempt_paths: List of paths that don't require tenant (e.g., /healthz)
    """

    def __init__(
        self,
        app,
        require_tenant: bool = True,
        allow_query_param: bool = False,
        exempt_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.require_tenant = require_tenant
        self.allow_query_param = allow_query_param
        self.exempt_paths = exempt_paths or [
            "/healthz",
            "/readyz",
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)

        # Extract tenant context
        tenant_id = None
        user_id = None
        roles = None

        # 1. Try JWT (from request.state if auth middleware ran first)
        # SECURITY: JWT is the trusted source for tenant_id. The `tid` claim
        # is set during authentication and cannot be forged by the caller.
        if hasattr(request.state, "principal"):
            principal = request.state.principal
            tenant_id = principal.get("tenant_id") or principal.get("tid")
            user_id = principal.get("sub")
            roles = principal.get("roles", [])

        # 2. Try X-Tenant-ID header (fallback, with deprecation warning)
        # SECURITY: The header can be set by any caller and is NOT validated
        # against JWT claims. This fallback exists only for backward
        # compatibility and should be removed once all clients migrate to
        # JWT-based tenant identification.
        header_tenant_id = request.headers.get("X-Tenant-ID")

        if tenant_id:
            # JWT tenant takes precedence; warn if header differs
            if header_tenant_id and header_tenant_id != tenant_id:
                logger.warning(
                    "X-Tenant-ID header (%s) differs from JWT tenant (%s); "
                    "using JWT value. This may indicate a misconfigured client.",
                    header_tenant_id,
                    tenant_id,
                )
        elif header_tenant_id:
            # No JWT tenant -- accept header with deprecation warning
            logger.warning(
                "Tenant resolved from X-Tenant-ID header (deprecated); "
                "migrate to JWT-based tenant. header_tenant_id=%s path=%s",
                header_tenant_id,
                request.url.path,
            )
            tenant_id = header_tenant_id

        # 3. Try query parameter (if allowed)
        if not tenant_id and self.allow_query_param:
            tenant_id = request.query_params.get("tenant_id")

        # Validate tenant presence
        if not tenant_id and self.require_tenant:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "missing_tenant",
                    "message_en": "Tenant ID is required",
                    "message_ar": "معرف المستأجر مطلوب",
                },
            )

        # Set context
        if tenant_id:
            ctx = TenantContext(id=tenant_id, user_id=user_id, roles=roles)
            token = _tenant_context.set(ctx)

            # Also attach to request.state for compatibility
            request.state.tenant_id = tenant_id
            request.state.tenant_context = ctx

            # Add to logging context
            logger.debug(f"Tenant context set: tenant_id={tenant_id}, user_id={user_id}")

            try:
                response = await call_next(request)
                return response
            finally:
                _tenant_context.reset(token)
        else:
            return await call_next(request)


# ─────────────────────────────────────────────────────────────────────────────
# Database Query Helpers
# ─────────────────────────────────────────────────────────────────────────────


def tenant_filter(model_class):
    """
    Return a filter condition for tenant isolation.

    Usage with SQLAlchemy:
        query = session.query(Field).filter(tenant_filter(Field))

    Usage with Tortoise ORM:
        fields = await Field.filter(**tenant_filter_dict())
    """
    return model_class.tenant_id == get_current_tenant_id()


def tenant_filter_dict() -> dict:
    """
    Return a dict filter for tenant isolation.

    Usage:
        fields = await Field.filter(**tenant_filter_dict())
    """
    return {"tenant_id": get_current_tenant_id()}
