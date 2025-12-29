"""
SAHOOL Dead Letter Queue (DLQ) Consumer
Monitors and processes failed events from the DLQ

Features:
- Subscribe to all DLQ subjects: sahool.dlq.>
- Store failed events in database for analysis
- Provide retry mechanism for DLQ events
- Alert on critical failures
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional, Callable, Awaitable
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# NATS client - lazy import
_nats_available = False

try:
    import nats
    from nats.aio.client import Client as NATSClient
    _nats_available = True
except ImportError:
    logger.warning("NATS package not installed. DLQ consumer disabled.")
    NATSClient = None


class DLQAction(Enum):
    """Actions that can be taken on DLQ events"""
    STORE = "store"  # Store for analysis
    RETRY = "retry"  # Retry original processing
    DISCARD = "discard"  # Discard permanently
    ALERT = "alert"  # Alert operations team


class DLQEvent(BaseModel):
    """Dead letter queue event model"""
    event_id: str
    original_subject: str
    event_type: str
    source_service: str
    tenant_id: Optional[str] = None
    field_id: Optional[str] = None
    farmer_id: Optional[str] = None

    # Error context
    error_message: str
    error_type: str
    stack_trace: Optional[str] = None

    # Retry context
    retry_count: int
    max_retries: int
    first_attempt_at: datetime
    last_attempt_at: datetime

    # Original data
    original_data: dict[str, Any]
    original_headers: dict[str, str] = Field(default_factory=dict)

    # DLQ metadata
    dlq_timestamp: datetime
    dlq_reason: str

    @classmethod
    def from_json(cls, data: bytes) -> DLQEvent:
        """Parse DLQ event from JSON bytes"""
        payload = json.loads(data.decode('utf-8'))
        return cls(
            event_id=payload["event_id"],
            original_subject=payload["original_subject"],
            event_type=payload["event_type"],
            source_service=payload["source_service"],
            tenant_id=payload.get("tenant_id"),
            field_id=payload.get("field_id"),
            farmer_id=payload.get("farmer_id"),
            error_message=payload["error_message"],
            error_type=payload["error_type"],
            stack_trace=payload.get("stack_trace"),
            retry_count=payload["retry_count"],
            max_retries=payload["max_retries"],
            first_attempt_at=datetime.fromisoformat(payload["first_attempt_at"]),
            last_attempt_at=datetime.fromisoformat(payload["last_attempt_at"]),
            original_data=payload["original_data"],
            original_headers=payload.get("original_headers", {}),
            dlq_timestamp=datetime.fromisoformat(payload["dlq_timestamp"]),
            dlq_reason=payload["dlq_reason"],
        )


class DLQConsumerConfig(BaseModel):
    """DLQ consumer configuration"""
    servers: list[str] = Field(default_factory=lambda: ["nats://localhost:4222"])
    name: str = Field(default="sahool-dlq-consumer")

    # DLQ subject pattern
    dlq_subject: str = Field(default="sahool.dlq.>")

    # Storage
    store_in_db: bool = Field(default=True)

    # Alerting
    alert_on_critical: bool = Field(default=True)
    critical_error_types: list[str] = Field(default_factory=lambda: [
        "DatabaseError",
        "ValidationError",
        "AuthenticationError",
    ])

    # Auto-retry
    auto_retry_enabled: bool = Field(default=False)
    auto_retry_delay_hours: int = Field(default=24)


class DLQConsumer:
    """
    Dead Letter Queue Consumer

    Monitors DLQ subjects and processes failed events.

    Usage:
        consumer = DLQConsumer()
        await consumer.connect()

        async def handler(event: DLQEvent) -> DLQAction:
            # Analyze failed event
            print(f"Failed event: {event.event_id} - {event.error_message}")

            # Store in database
            await store_failed_event(event)

            return DLQAction.STORE

        await consumer.subscribe(handler)
        await consumer.start()
    """

    def __init__(self, config: Optional[DLQConsumerConfig] = None):
        self.config = config or DLQConsumerConfig()
        self._nc: Optional[NATSClient] = None
        self._connected = False
        self._running = False
        self._subscription = None
        self._handler: Optional[Callable[[DLQEvent], Awaitable[DLQAction]]] = None

    @property
    def is_connected(self) -> bool:
        return self._connected and self._nc is not None

    async def connect(self) -> bool:
        """Connect to NATS server"""
        if not _nats_available:
            logger.warning("NATS not available. DLQ consumer disabled.")
            return False

        try:
            self._nc = await nats.connect(servers=self.config.servers, name=self.config.name)
            self._connected = True
            logger.info(f"✅ DLQ Consumer connected: {self.config.servers}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect DLQ consumer: {e}")
            return False

    async def close(self):
        """Close NATS connection"""
        self._running = False

        if self._subscription:
            try:
                await self._subscription.unsubscribe()
            except Exception as e:
                logger.warning(f"Error unsubscribing from DLQ: {e}")

        if self._nc:
            await self._nc.close()
            self._connected = False
            logger.info("🔌 DLQ Consumer connection closed")

    async def subscribe(
        self,
        handler: Callable[[DLQEvent], Awaitable[DLQAction]],
        subject: Optional[str] = None,
    ):
        """
        Subscribe to DLQ subjects

        Args:
            handler: Async function to process DLQ events
            subject: Subject pattern (default: sahool.dlq.>)
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to NATS. Call connect() first.")

        subject = subject or self.config.dlq_subject
        self._handler = handler

        try:
            self._subscription = await self._nc.subscribe(subject, cb=self._message_callback)
            logger.info(f"📥 Subscribed to DLQ: {subject}")
        except Exception as e:
            logger.error(f"Failed to subscribe to DLQ: {e}")
            raise

    async def _message_callback(self, msg):
        """Process incoming DLQ messages"""
        try:
            # Parse DLQ event
            event = DLQEvent.from_json(msg.data)

            logger.warning(
                f"💀 DLQ Event received: {event.event_type} "
                f"(event_id={event.event_id}, error={event.error_type})"
            )

            # Call handler
            if self._handler:
                action = await self._handler(event)

                # Execute action
                await self._execute_action(event, action)
            else:
                # Default action: log
                logger.error(
                    f"DLQ Event (no handler): {event.event_id} "
                    f"error={event.error_message}"
                )

        except Exception as e:
            logger.error(f"Error processing DLQ message: {e}", exc_info=True)

    async def _execute_action(self, event: DLQEvent, action: DLQAction):
        """Execute action on DLQ event"""
        if action == DLQAction.STORE:
            await self._store_event(event)

        elif action == DLQAction.RETRY:
            await self._retry_event(event)

        elif action == DLQAction.ALERT:
            await self._alert_on_event(event)

        elif action == DLQAction.DISCARD:
            logger.info(f"Discarding DLQ event: {event.event_id}")

    async def _store_event(self, event: DLQEvent):
        """Store failed event in database"""
        # TODO: Implement database storage
        # This should store the event in a failed_events table
        logger.info(f"📦 Storing DLQ event: {event.event_id}")

        # Example implementation (requires database connection):
        # async with db.session() as session:
        #     failed_event = FailedEventModel(
        #         event_id=event.event_id,
        #         event_type=event.event_type,
        #         source_service=event.source_service,
        #         error_message=event.error_message,
        #         error_type=event.error_type,
        #         retry_count=event.retry_count,
        #         original_data=event.original_data,
        #         dlq_timestamp=event.dlq_timestamp,
        #     )
        #     session.add(failed_event)
        #     await session.commit()

    async def _retry_event(self, event: DLQEvent):
        """Retry processing of failed event"""
        logger.info(f"🔄 Retrying DLQ event: {event.event_id}")

        try:
            # Republish to original subject
            data = json.dumps(event.original_data).encode('utf-8')
            await self._nc.publish(event.original_subject, data)

            logger.info(
                f"✅ DLQ event republished: {event.event_id} -> {event.original_subject}"
            )
        except Exception as e:
            logger.error(f"Failed to retry DLQ event {event.event_id}: {e}")

    async def _alert_on_event(self, event: DLQEvent):
        """Send alert for critical DLQ event"""
        logger.error(
            f"🚨 CRITICAL DLQ EVENT: {event.event_id} "
            f"error_type={event.error_type} "
            f"error_message={event.error_message}"
        )

        # TODO: Implement alerting (Slack, email, PagerDuty, etc.)
        # Example:
        # await send_slack_alert(
        #     channel="#alerts",
        #     message=f"DLQ Event: {event.event_id}\n"
        #             f"Error: {event.error_message}\n"
        #             f"Service: {event.source_service}"
        # )

    async def start(self):
        """Start DLQ consumer"""
        if not self.is_connected:
            raise RuntimeError("Not connected to NATS. Call connect() first.")

        if not self._subscription:
            raise RuntimeError("Not subscribed to DLQ. Call subscribe() first.")

        self._running = True
        logger.info("🚀 DLQ Consumer started")

        # Keep running
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("DLQ Consumer cancelled")
        finally:
            self._running = False


# Default DLQ handler implementation
async def default_dlq_handler(event: DLQEvent) -> DLQAction:
    """
    Default DLQ event handler

    Logs the event and returns STORE action
    """
    logger.error(
        f"DLQ Event: {event.event_type} "
        f"(id={event.event_id}, error={event.error_message})"
    )

    # Check if critical error
    critical_errors = ["DatabaseError", "ValidationError", "AuthenticationError"]
    if event.error_type in critical_errors:
        return DLQAction.ALERT

    return DLQAction.STORE


# Convenience function
async def start_dlq_consumer(
    handler: Optional[Callable[[DLQEvent], Awaitable[DLQAction]]] = None,
    config: Optional[DLQConsumerConfig] = None,
) -> DLQConsumer:
    """
    Convenience function to start DLQ consumer

    Args:
        handler: Optional DLQ event handler (default: default_dlq_handler)
        config: Optional consumer configuration

    Returns:
        Running DLQConsumer instance

    Example:
        async def my_dlq_handler(event: DLQEvent) -> DLQAction:
            # Custom processing
            return DLQAction.STORE

        consumer = await start_dlq_consumer(my_dlq_handler)
    """
    handler = handler or default_dlq_handler

    consumer = DLQConsumer(config)
    await consumer.connect()
    await consumer.subscribe(handler)

    # Start in background
    asyncio.create_task(consumer.start())

    return consumer
