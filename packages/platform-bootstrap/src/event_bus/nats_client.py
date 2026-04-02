"""
SAHOOL Event Bus Client - NATS JetStream

Provides a singleton event bus for publishing and subscribing to domain events
across SAHOOL microservices using NATS JetStream for guaranteed delivery.

Usage:
    bus = await SAHOOLEventBus.get_instance()
    await bus.connect("nats://nats:4222", "my-service")
    await bus.publish_event("field", "sensor-data.received", {"moisture": 45.2})
"""

import json
import uuid
from datetime import datetime, UTC
from typing import Any, Callable, Optional

import nats
from nats.aio.client import Client as NATS
from nats.js import JetStreamContext


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

    def __init__(self) -> None:
        self.nc: NATS | None = None
        self.js: JetStreamContext | None = None
        self.service_name = "unknown"

    @classmethod
    async def get_instance(cls) -> "SAHOOLEventBus":
        if cls._instance is None:
            cls._instance = SAHOOLEventBus()
        return cls._instance

    async def connect(self, nats_url: str, service_name: str) -> None:
        """Connect to NATS server and initialize JetStream context."""
        self.service_name = service_name
        self.nc = await nats.connect(nats_url, name=service_name)
        self.js = self.nc.jetstream()

    async def publish_event(
        self,
        domain: str,
        action: str,
        data: dict[str, Any],
        tenant_id: str | None = None,
    ) -> None:
        """Publish a domain event to the SAHOOL event bus."""
        if self.js is None:
            raise RuntimeError("Event bus not connected. Call connect() first.")
        subject = f"SAHOOL.events.{domain}.{action}.v1"
        event = EventMessage(subject, data, self.service_name, tenant_id)
        await self.js.publish(subject, event.to_json())

    async def subscribe_events(
        self,
        domain: str,
        handler: Callable,
        durable: str | None = None,
    ) -> None:
        """Subscribe to domain events with a durable consumer."""
        if self.js is None:
            raise RuntimeError("Event bus not connected. Call connect() first.")
        subject = f"SAHOOL.events.{domain}.>"
        await self.js.subscribe(
            subject,
            durable=durable or f"{self.service_name}_{domain}",
            cb=handler,
        )

    async def close(self) -> None:
        """Close the NATS connection."""
        if self.nc:
            await self.nc.close()
            self.nc = None
            self.js = None
