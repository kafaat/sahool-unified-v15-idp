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

from __future__ import annotations

import logging
import re
from contextlib import asynccontextmanager
from contextvars import ContextVar
from dataclasses import dataclass

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

_UUID_REGEX = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)

# Context variable for tenant isolation (async-safe)
_tenant_context: ContextVar[TenantContext | None] = ContextVar("tenant_context", default=None)


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
    1. JWT token claim (tid)
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
            "/health",
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
        if hasattr(request.state, "principal"):
            principal = request.state.principal
            tenant_id = principal.get("tid")
            user_id = principal.get("sub")
            roles = principal.get("roles", [])

        # 2. Try X-Tenant-ID header
        if not tenant_id:
            tenant_id = request.headers.get("X-Tenant-ID")

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

        # Validate tenant ID format (must be a valid UUID)
        if tenant_id and not _UUID_REGEX.match(tenant_id):
            logger.warning(f"Invalid Tenant ID format: {tenant_id!r}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_tenant_id",
                    "message_en": "Invalid Tenant ID format. Must be a valid UUID.",
                    "message_ar": "تنسيق معرف المستأجر غير صالح. يجب أن يكون UUID صالحًا.",
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


def is_current_user_admin() -> bool:
    """
    Check if the current user has admin or super_admin role.

    Returns:
        bool: True if user is admin/super_admin
    """
    ctx = get_optional_tenant()
    if ctx is None or ctx.roles is None:
        return False
    return "admin" in ctx.roles or "super_admin" in ctx.roles


# ─────────────────────────────────────────────────────────────────────────────
# PostgreSQL session-level RLS enforcement
# تطبيق عزل المستأجر على مستوى جلسة PostgreSQL
# ─────────────────────────────────────────────────────────────────────────────


async def set_app_tenant(conn, tenant_id: str) -> None:
    """
    Set the PostgreSQL session variable used by RLS policies.

    This calls ``SET LOCAL app.current_tenant = '<tenant_id>'`` which makes
    the value visible to ``current_tenant_id()`` (defined in migration
    010_row_level_security.sql) and therefore to all RLS policies on the
    current transaction.

    Must be called *inside* an open transaction — ``SET LOCAL`` is
    automatically rolled back when the transaction ends.

    Args:
        conn:      An asyncpg connection (or compatible DB connection).
        tenant_id: The tenant UUID string for the current request.

    Example::

        async with pool.acquire() as conn:
            async with conn.transaction():
                await set_app_tenant(conn, tenant_id)
                rows = await conn.fetch("SELECT * FROM fields")
    """
    if not tenant_id:
        return
    # Use parameterized form to avoid any injection risk
    await conn.execute("SELECT set_config('app.current_tenant', $1, true)", tenant_id)


@asynccontextmanager
async def acquire_tenant_conn(pool, tenant_id: str):
    """
    Async context manager that acquires a pooled asyncpg connection and
    sets the session-level ``app.current_tenant`` variable for RLS.

    The tenant variable is set via ``SET LOCAL`` inside a transaction, so
    it is automatically cleared when the transaction finishes.

    Usage::

        async with acquire_tenant_conn(app.state.db_pool, tenant_id) as conn:
            rows = await conn.fetch("SELECT * FROM fields WHERE ...")

    Args:
        pool:      An asyncpg connection pool (``asyncpg.Pool``).
        tenant_id: Tenant UUID for the current request context.

    Yields:
        asyncpg connection with ``app.current_tenant`` already set.
    """
    async with pool.acquire() as conn:
        async with conn.transaction():
            await set_app_tenant(conn, tenant_id)
            yield conn
