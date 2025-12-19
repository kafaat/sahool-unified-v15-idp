"""
Event Publisher
===============

Provides a unified interface for publishing domain events.
"""

import json
import logging
from typing import Optional
from .base import BaseEvent

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    Publishes domain events to the message broker.

    Usage:
        publisher = EventPublisher(nats_client)
        await publisher.publish(FieldCreatedEvent(...))
    """

    def __init__(self, nats_client=None, service_name: str = "unknown", service_version: str = "0.0.0"):
        self._nats = nats_client
        self._service_name = service_name
        self._service_version = service_version

    async def publish(self, event: BaseEvent, subject: Optional[str] = None) -> bool:
        """
        Publish an event to the message broker.

        Args:
            event: The domain event to publish
            subject: Optional custom subject (defaults to event type)

        Returns:
            True if published successfully
        """
        if not subject:
            subject = f"sahool.events.{event.event_type}"

        # Add source information
        from .base import EventSource
        event.source = EventSource(
            service=self._service_name,
            version=self._service_version,
        )

        # Validate event
        if not event.validate():
            logger.error(f"Event validation failed: {event}")
            return False

        try:
            payload = event.to_json().encode()

            if self._nats:
                await self._nats.publish(subject, payload)
                logger.info(f"Published event: {event.event_type} (id={event.event_id})")
            else:
                # Fallback: log event for debugging
                logger.warning(f"No NATS client - logging event: {event}")

            return True

        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False

    async def publish_batch(self, events: list[BaseEvent]) -> int:
        """Publish multiple events, returns count of successful publishes"""
        success_count = 0
        for event in events:
            if await self.publish(event):
                success_count += 1
        return success_count
