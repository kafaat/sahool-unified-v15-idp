"""
SAHOOL Tenant Context Manager

Provides async context management for multi-tenant isolation using
PostgreSQL Row-Level Security (RLS). Sets app.current_tenant on the
database connection so RLS policies automatically filter by tenant.

Usage:
    async with TenantContext(tenant_id="123e4567-e89b-12d3-a456-426614174000", db_pool=pool) as ctx:
        # All queries within this block are scoped to this tenant
        rows = await ctx.conn.fetch("SELECT * FROM fields")
"""

import contextvars
import json
import logging
import uuid

_tenant_context: contextvars.ContextVar[str | None] = contextvars.ContextVar("tenant_id", default=None)


class TenantContext:
    """Async context manager for tenant-scoped database operations."""

    def __init__(self, tenant_id: str, db_pool=None):
        self.tenant_id = tenant_id
        self.db_pool = db_pool
        self.token: contextvars.Token | None = None
        self._conn = None

    @property
    def conn(self):
        """Return the acquired database connection (available inside the context)."""
        return self._conn

    async def __aenter__(self):
        self.token = _tenant_context.set(self.tenant_id)
        if self.db_pool:
            self._conn = await self.db_pool.acquire()
            # Use set_config() which is SQL-injection safe (takes text parameters)
            await self._conn.execute(
                "SELECT set_config('app.current_tenant', $1, true)",
                self.tenant_id,
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.token is not None:
            _tenant_context.reset(self.token)
        if self._conn is not None:
            try:
                await self._conn.execute(
                    "SELECT set_config('app.current_tenant', '', true)"
                )
            finally:
                await self.db_pool.release(self._conn)
                self._conn = None

    @staticmethod
    def get_current() -> str | None:
        """Get the current tenant ID from context."""
        return _tenant_context.get()

    @staticmethod
    def validate_tenant_id(tenant_id: str) -> bool:
        """Validate UUID format tenant ID."""
        try:
            uuid.UUID(tenant_id)
            return True
        except ValueError:
            return False


class TenantAwareNATS:
    """Adds tenant headers to all NATS messages automatically."""

    def __init__(self, event_bus, tenant_id: str):
        self.event_bus = event_bus
        self.tenant_id = tenant_id

    async def publish_event(self, domain: str, action: str, data: dict) -> None:
        """Publish with tenant context."""
        await self.event_bus.publish_event(
            domain=domain,
            action=action,
            data=data,
            tenant_id=self.tenant_id,
        )

    async def subscribe_events(self, domain: str, handler, **kwargs) -> None:
        """Subscribe with automatic tenant filtering.

        The handler receives a raw NATS ``Msg``; the JSON payload is parsed
        to extract and compare ``tenant_id`` before delegating.
        """

        async def wrapped_handler(msg):
            try:
                payload = json.loads(msg.data)
            except (json.JSONDecodeError, UnicodeDecodeError):
                logging.getLogger(__name__).warning(
                    "TenantAwareNATS: failed to decode message on %s (%d bytes)",
                    getattr(msg, "subject", "?"),
                    len(msg.data) if msg.data else 0,
                )
                return
            if payload.get("tenant_id") == self.tenant_id:
                await handler(msg)

        await self.event_bus.subscribe_events(
            domain=domain,
            handler=wrapped_handler,
            **kwargs,
        )
