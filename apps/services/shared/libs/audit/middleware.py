"""
SAHOOL Audit Middleware
FastAPI middleware for automatic audit context injection
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from contextvars import ContextVar
from dataclasses import dataclass
from uuid import UUID, uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Context variable for audit context
_audit_context: ContextVar[AuditContext | None] = ContextVar("audit_context", default=None)


@dataclass
class AuditContext:
    """
    Audit context for the current request.

    This context is automatically populated by the middleware
    and can be accessed from anywhere in the request handling chain.
    """

    tenant_id: UUID | None
    actor_id: UUID | None
    actor_type: str
    correlation_id: UUID
    ip: str | None
    user_agent: str | None

    @classmethod
    def get_current(cls) -> AuditContext | None:
        """Get the current audit context"""
        return _audit_context.get()

    @classmethod
    def set_current(cls, ctx: AuditContext) -> None:
        """Set the current audit context"""
        _audit_context.set(ctx)


def get_audit_context() -> AuditContext | None:
    """
    Get the current audit context.

    Returns:
        AuditContext if in a request context, None otherwise
    """
    return AuditContext.get_current()


class AuditContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts audit context from requests.

    This middleware:
    - Extracts tenant_id and actor_id from headers
    - Generates or extracts correlation_id
    - Captures client IP and user agent
    - Makes context available via ContextVar

    Usage:
        ```python
        from fastapi import FastAPI
        from shared.libs.audit.middleware import AuditContextMiddleware

        app = FastAPI()
        app.add_middleware(AuditContextMiddleware)
        ```

    Headers:
        - X-Tenant-Id: Tenant UUID
        - X-Actor-Id: User UUID
        - X-Correlation-Id: Request correlation ID
        - X-Forwarded-For: Client IP (if behind proxy)
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        # Extract tenant and actor from headers
        tenant_id_str = request.headers.get("X-Tenant-Id")
        actor_id_str = request.headers.get("X-Actor-Id")
        correlation_id_str = request.headers.get("X-Correlation-Id")

        # Parse UUIDs safely
        tenant_id = _parse_uuid(tenant_id_str)
        actor_id = _parse_uuid(actor_id_str)

        # Generate correlation ID if not provided
        if correlation_id_str:
            correlation_id = _parse_uuid(correlation_id_str) or uuid4()
        else:
            correlation_id = uuid4()

        # Get client IP (handle proxies)
        ip = self._get_client_ip(request)

        # Get user agent (truncated)
        user_agent = request.headers.get("User-Agent")
        if user_agent and len(user_agent) > 256:
            user_agent = user_agent[:253] + "..."

        # Create and set context
        ctx = AuditContext(
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_type="user" if actor_id else "system",
            correlation_id=correlation_id,
            ip=ip,
            user_agent=user_agent,
        )

        # Store in request state for easy access
        request.state.audit_ctx = ctx

        # Set context variable
        token = _audit_context.set(ctx)

        try:
            # Add correlation ID to response headers
            response = await call_next(request)
            response.headers["X-Correlation-Id"] = str(correlation_id)
            return response
        finally:
            # Reset context
            _audit_context.reset(token)

    def _get_client_ip(self, request: Request) -> str | None:
        """Extract client IP, handling proxies"""
        # Check X-Forwarded-For first (for proxied requests)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to direct client
        if request.client:
            return request.client.host

        return None


def _parse_uuid(value: str | None) -> UUID | None:
    """Safely parse a UUID string"""
    if not value:
        return None
    try:
        return UUID(value)
    except (ValueError, AttributeError):
        logger.warning(f"Invalid UUID: {value}")
        return None


# Alembic migration for audit_logs table
AUDIT_LOG_MIGRATION = """
-- Sprint 6: Create audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    actor_id UUID,
    actor_type VARCHAR(40) NOT NULL DEFAULT 'user',
    action VARCHAR(120) NOT NULL,
    resource_type VARCHAR(80) NOT NULL,
    resource_id VARCHAR(80) NOT NULL,
    correlation_id UUID NOT NULL,
    ip VARCHAR(64),
    user_agent VARCHAR(256),
    details_json TEXT NOT NULL DEFAULT '{}',
    prev_hash VARCHAR(64),
    entry_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version INTEGER NOT NULL DEFAULT 1
);

-- Indexes
CREATE INDEX IF NOT EXISTS ix_audit_tenant_created ON audit_logs (tenant_id, created_at);
CREATE INDEX IF NOT EXISTS ix_audit_resource ON audit_logs (resource_type, resource_id);
CREATE INDEX IF NOT EXISTS ix_audit_actor ON audit_logs (actor_id, created_at);
CREATE INDEX IF NOT EXISTS ix_audit_correlation ON audit_logs (correlation_id);

-- Prevent updates and deletes (audit is append-only)
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit logs are immutable and cannot be modified';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS audit_logs_no_update ON audit_logs;
CREATE TRIGGER audit_logs_no_update
    BEFORE UPDATE OR DELETE ON audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_modification();
"""
