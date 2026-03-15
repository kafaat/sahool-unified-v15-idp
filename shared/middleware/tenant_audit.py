"""
SAHOOL Cross-Tenant Access Audit Middleware
============================================
تدقيق الوصول بين المستأجرين

Logs all admin cross-tenant access for security compliance.
When an admin user accesses resources belonging to a different tenant,
this middleware records the event for audit purposes.

Usage:
    from shared.middleware.tenant_audit import TenantAuditMiddleware

    app.add_middleware(TenantAuditMiddleware)
"""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger("sahool.tenant_audit")


@dataclass
class CrossTenantAuditEntry:
    """Audit entry for cross-tenant access events."""

    timestamp: str
    user_id: str
    user_tenant_id: str
    accessed_tenant_id: str
    method: str
    path: str
    status_code: int | None = None
    duration_ms: float | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    roles: list[str] = field(default_factory=list)


class TenantAuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware that detects and logs cross-tenant admin access.

    When an admin user's JWT tenant_id differs from the X-Tenant-ID header
    (or the tenant being accessed), the access is logged as a cross-tenant event.
    """

    def __init__(self, app, audit_callback=None):
        """
        Args:
            app: ASGI application
            audit_callback: Optional async callable for custom audit storage.
                            Receives CrossTenantAuditEntry as argument.
                            If None, logs to structured logger only.
        """
        super().__init__(app)
        self.audit_callback = audit_callback

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.monotonic()

        # Extract tenant info from JWT and header
        user_tenant_id = None
        user_id = None
        roles: list[str] = []

        if hasattr(request.state, "principal"):
            principal = request.state.principal
            user_tenant_id = principal.get("tid")
            user_id = principal.get("sub")
            roles = principal.get("roles", [])

        # The tenant being accessed (from header or path)
        accessed_tenant_id = request.headers.get("X-Tenant-ID")

        # If no cross-tenant access, proceed normally
        if (
            not user_tenant_id
            or not accessed_tenant_id
            or user_tenant_id == accessed_tenant_id
        ):
            return await call_next(request)

        # Cross-tenant access detected - this should only be allowed for admins
        is_admin = "admin" in roles or "super_admin" in roles

        response = await call_next(request)
        duration_ms = (time.monotonic() - start_time) * 1000

        entry = CrossTenantAuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_id=user_id or "unknown",
            user_tenant_id=user_tenant_id,
            accessed_tenant_id=accessed_tenant_id,
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            roles=roles,
        )

        # Log with structured data
        log_data = asdict(entry)
        if is_admin:
            logger.warning(
                "Cross-tenant admin access: user=%s from_tenant=%s to_tenant=%s path=%s",
                user_id,
                user_tenant_id,
                accessed_tenant_id,
                request.url.path,
                extra={"audit": log_data},
            )
        else:
            # Non-admin cross-tenant access should have been blocked by guard
            logger.error(
                "SECURITY: Non-admin cross-tenant access attempt: user=%s from=%s to=%s path=%s",
                user_id,
                user_tenant_id,
                accessed_tenant_id,
                request.url.path,
                extra={"audit": log_data},
            )

        # Custom audit callback (e.g., write to audit table, send to NATS)
        if self.audit_callback:
            try:
                await self.audit_callback(entry)
            except Exception as exc:
                logger.error("Failed to execute audit callback: %s", exc)

        return response
