"""
SAHOOL Event Bus Client - NATS JetStream

Provides a singleton event bus for publishing and subscribing to domain events
across SAHOOL microservices using NATS JetStream for guaranteed delivery.

Usage:
    bus = await SAHOOLEventBus.get_instance()
    await bus.connect("nats://nats:4222", "my-service")
    await bus.publish_event("field", "sensor-data.received", {"moisture": 45.2})
"""

import asyncio
import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any, Callable, Optional

import nats
from nats.aio.client import Client as NATS
from nats.js import JetStreamContext

logger = logging.getLogger(__name__)

# Subject prefix must match NATS ACLs in config/nats/nats.conf (lowercase)
_SUBJECT_PREFIX = "sahool"

# Allowed message types to prevent arbitrary subject injection
_ALLOWED_MESSAGE_TYPES = frozenset({"events", "commands", "registry", "health", "audit"})


class EventMessage:
    """Structured event message for the SAHOOL event bus."""

    def __init__(
        self,
        subject: str,
        data: dict[str, Any],
        source: str,
        tenant_id: str | None = None,
    ):
        self.subject = subject
        self.data = data
        self.event_id = str(uuid.uuid4())
        self.timestamp = datetime.now(UTC)
        self.source = source
        self.tenant_id = tenant_id
        self.version = "v1"

    def to_json(self) -> bytes:
        return json.dumps(
            {
                "event_id": self.event_id,
                "timestamp": self.timestamp.isoformat(),
                "source": self.source,
                "data": self.data,
                "tenant_id": self.tenant_id,
                "version": self.version,
            },
            default=str,
        ).encode()


class SAHOOLEventBus:
    """Singleton NATS JetStream event bus for SAHOOL platform."""

    _instance: Optional["SAHOOLEventBus"] = None
    # Class-level lock so all coroutines share one lock object.
    # asyncio.Lock() is safe to create at import time in Python >=3.10.
    _lock: asyncio.Lock = asyncio.Lock()

    def __init__(self) -> None:
        self.nc: NATS | None = None
        self.js: JetStreamContext | None = None
        self.service_name = "unknown"

    @classmethod
    async def get_instance(cls) -> "SAHOOLEventBus":
        async with cls._lock:
            if cls._instance is None:
                cls._instance = SAHOOLEventBus()
        return cls._instance

    async def connect(self, nats_url: str, service_name: str) -> None:
        """Connect to NATS server and initialize JetStream context.

        Configures automatic reconnection so transient network failures
        do not permanently sever the event bus connection.
        """
        self.service_name = service_name
        try:
            self.nc = await nats.connect(
                nats_url,
                name=service_name,
                max_reconnect_attempts=60,
                reconnect_time_wait=2,
                reconnected_cb=self._on_reconnected,
                disconnected_cb=self._on_disconnected,
                error_cb=self._on_error,
            )
            self.js = self.nc.jetstream()
        except Exception as exc:
            raise ConnectionError(f"Failed to connect {service_name} to NATS at {nats_url}: {exc}") from exc

    async def _on_reconnected(self) -> None:
        logger.info("NATS reconnected for service=%s", self.service_name)

    async def _on_disconnected(self) -> None:
        logger.warning("NATS disconnected for service=%s", self.service_name)

    async def _on_error(self, exc: Exception) -> None:
        logger.error("NATS error for service=%s: %s", self.service_name, exc)

    async def publish_event(
        self,
        domain: str,
        action: str,
        data: dict[str, Any],
        tenant_id: str | None = None,
        *,
        message_type: str = "events",
    ) -> None:
        """Publish a domain event to the SAHOOL event bus.

        Args:
            domain: The domain area (e.g. "field", "weather", "ai").
            action: The action name (e.g. "sensor-data.received").
            data: The event payload.
            tenant_id: Optional tenant ID for multi-tenant isolation.
            message_type: The bus type - "events", "commands", "registry",
                          "health", or "audit".  Defaults to "events".
        """
        if self.js is None:
            raise RuntimeError("Event bus not connected. Call connect() first.")
        if message_type not in _ALLOWED_MESSAGE_TYPES:
            raise ValueError(f"Invalid message_type '{message_type}'. Allowed: {sorted(_ALLOWED_MESSAGE_TYPES)}")
        subject = f"{_SUBJECT_PREFIX}.{message_type}.{domain}.{action}.v1"
        event = EventMessage(subject, data, self.service_name, tenant_id)
        try:
            await self.js.publish(subject, event.to_json())
        except Exception as exc:
            logger.error("Failed to publish event to %s: %s", subject, exc)
            raise

    async def subscribe_events(
        self,
        domain: str,
        handler: Callable,
        durable: str | None = None,
        *,
        message_type: str = "events",
    ) -> None:
        """Subscribe to domain events with a durable consumer.

        Args:
            domain: The domain area to subscribe to.
            handler: Async callback receiving a NATS ``Msg``.
            durable: Optional durable consumer name.
            message_type: The bus type - "events", "commands", "registry",
                          "health", or "audit".  Defaults to "events".
        """
        if self.js is None:
            raise RuntimeError("Event bus not connected. Call connect() first.")
        subject = f"{_SUBJECT_PREFIX}.{message_type}.{domain}.>"
        await self.js.subscribe(
            subject,
            durable=durable or f"{self.service_name}_{domain}",
            cb=handler,
        )

    async def close(self) -> None:
        """Close the NATS connection and reset the singleton.

        After calling close(), a subsequent ``get_instance()`` will create
        a fresh ``SAHOOLEventBus`` that must be connected again via
        ``connect()``.
        """
        if self.nc:
            await self.nc.close()
            self.nc = None
            self.js = None
        # Reset singleton so next get_instance() creates a fresh bus
        SAHOOLEventBus._instance = None
