"""
SAHOOL NATS Event Subscriber
=============================
مشترك أحداث NATS - استقبال ومعالجة الأحداث بشكل موثوق

Async NATS subscriber for consuming domain events across the SAHOOL platform.
Provides automatic deserialization, validation, error handling, and JetStream support.

Usage:
    from shared.events.subscriber import EventSubscriber
    from shared.events.contracts import FieldCreatedEvent
    from shared.events.subjects import SAHOOL_FIELD_CREATED

    subscriber = EventSubscriber()
    await subscriber.connect()

    async def handle_field_created(event: FieldCreatedEvent):
        print(f"New field created: {event.name}")

    await subscriber.subscribe(
        SAHOOL_FIELD_CREATED,
        handle_field_created,
        event_class=FieldCreatedEvent
    )

    # Keep running
    await subscriber.run()
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from collections.abc import Callable
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from .contracts import BaseEvent
from .dlq_config import (
    DLQConfig,
    create_dlq_streams,
)

logger = logging.getLogger(__name__)

# NATS client - lazy import for optional dependency
_nats_available = False

try:
    import nats
    from nats.aio.client import Client as NATSClient
    from nats.aio.msg import Msg
    from nats.js import JetStreamContext

    _nats_available = True
except ImportError:
    logger.warning("NATS package not installed. Install with: pip install nats-py")
    NATSClient = None
    Msg = None
    JetStreamContext = None


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────


class SubscriberConfig(BaseModel):
    """
    NATS subscriber configuration.
    إعدادات مشترك NATS
    """

    servers: list[str] = Field(
        default_factory=lambda: [os.getenv("NATS_URL", "nats://localhost:4222")],
        description="NATS server URLs",
    )
    name: str = Field(
        default_factory=lambda: os.getenv("SERVICE_NAME", "sahool-subscriber"),
        description="Subscriber client name",
    )
    reconnect_time_wait: int = Field(default=2, description="Seconds between reconnect attempts")
    max_reconnect_attempts: int = Field(default=60, description="Maximum reconnect attempts")
    connect_timeout: int = Field(default=10, description="Connection timeout in seconds")

    # JetStream
    enable_jetstream: bool = Field(default=True, description="Use JetStream consumers")
    jetstream_domain: str | None = Field(None, description="JetStream domain")

    # Error handling (DEPRECATED - use dlq_config instead)
    enable_error_retry: bool = Field(default=True, description="Retry failed messages")
    max_error_retries: int = Field(default=3, description="Maximum error retries per message")
    error_retry_delay: float = Field(default=1.0, description="Delay between error retries")

    # Performance
    max_concurrent_messages: int = Field(
        default=10, description="Max concurrent message processing"
    )
    pending_messages_limit: int = Field(default=1000, description="Pending messages limit")

    # Dead Letter Queue
    enable_dlq: bool = Field(
        default=True, description="Enable Dead Letter Queue for failed messages"
    )
    dlq_config: DLQConfig | None = Field(
        None, description="DLQ configuration (uses defaults if None)"
    )


class Subscription(BaseModel):
    """
    Represents a NATS subscription.
    يمثل اشتراك NATS
    """

    subject: str = Field(..., description="NATS subject")
    handler: Any = Field(..., description="Message handler function")
    event_class: type[BaseEvent] | None = Field(None, description="Expected event class")
    queue_group: str | None = Field(None, description="Queue group for load balancing")
    durable_name: str | None = Field(None, description="Durable consumer name (JetStream)")
    auto_ack: bool = Field(default=True, description="Automatically acknowledge messages")

    class Config:
        arbitrary_types_allowed = True


# ─────────────────────────────────────────────────────────────────────────────
# Event Subscriber
# ─────────────────────────────────────────────────────────────────────────────


class EventSubscriber:
    """
    NATS Event Subscriber for SAHOOL platform.
    مشترك الأحداث عبر NATS لمنصة سهول

    Features:
    - Automatic JSON deserialization to Pydantic models
    - JetStream support for guaranteed delivery
    - Automatic reconnection
    - Error handling and retry logic
    - Queue groups for load balancing
    - Durable consumers
    - Message acknowledgment
    """

    def __init__(
        self,
        config: SubscriberConfig | None = None,
        service_name: str | None = None,
        service_version: str | None = None,
    ):
        """
        Initialize the event subscriber.

        Args:
            config: Subscriber configuration
            service_name: Name of the service using this subscriber
            service_version: Version of the service
        """
        self.config = config or SubscriberConfig()
        self.service_name = service_name or os.getenv("SERVICE_NAME", "unknown")
        self.service_version = service_version or os.getenv("SERVICE_VERSION", "0.0.0")

        self._nc: NATSClient | None = None
        self._js: JetStreamContext | None = None
        self._connected = False

        self._subscriptions: list[Any] = []
        self._handlers: dict[str, Subscription] = {}

        # Statistics
        self._message_count = 0
        self._error_count = 0
        self._dlq_count = 0
        self._retry_count = 0
        self._processing_semaphore = asyncio.Semaphore(self.config.max_concurrent_messages)

        # DLQ configuration
        self._dlq_config = self.config.dlq_config or DLQConfig()
        self._dlq_initialized = False

    @property
    def is_connected(self) -> bool:
        """Check if connected to NATS."""
        return self._connected and self._nc is not None

    @property
    def stats(self) -> dict[str, Any]:
        """Get subscriber statistics."""
        return {
            "connected": self._connected,
            "message_count": self._message_count,
            "error_count": self._error_count,
            "dlq_count": self._dlq_count,
            "retry_count": self._retry_count,
            "active_subscriptions": len(self._subscriptions),
            "service_name": self.service_name,
            "service_version": self.service_version,
            "dlq_enabled": self.config.enable_dlq,
        }

    async def connect(self) -> bool:
        """
        Connect to NATS server.
        الاتصال بخادم NATS

        Returns:
            True if connected successfully, False otherwise
        """
        if not _nats_available:
            logger.error("NATS library not available. Install with: pip install nats-py")
            return False

        if self.is_connected:
            logger.info("Already connected to NATS")
            return True

        try:
            logger.info(f"Connecting to NATS: {self.config.servers}")

            self._nc = await nats.connect(
                servers=self.config.servers,
                name=self.config.name,
                reconnect_time_wait=self.config.reconnect_time_wait,
                max_reconnect_attempts=self.config.max_reconnect_attempts,
                error_cb=self._error_callback,
                disconnected_cb=self._disconnected_callback,
                reconnected_cb=self._reconnected_callback,
                closed_cb=self._closed_callback,
                pending_size=self.config.pending_messages_limit,
            )

            # Enable JetStream if configured
            if self.config.enable_jetstream:
                self._js = self._nc.jetstream(domain=self.config.jetstream_domain)
                logger.info("✅ JetStream enabled")

                # Initialize DLQ streams if enabled
                if self.config.enable_dlq and not self._dlq_initialized:
                    try:
                        await create_dlq_streams(self._js, self._dlq_config)
                        self._dlq_initialized = True
                        logger.info(
                            f"✅ DLQ initialized (max retries: {self._dlq_config.max_retry_attempts})"
                        )
                    except Exception as e:
                        logger.warning(f"⚠️  Failed to initialize DLQ: {e}")

            self._connected = True
            logger.info(f"✅ Connected to NATS: {self.config.servers}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to NATS: {e}")
            self._connected = False
            return False

    async def close(self):
        """
        Close NATS connection and unsubscribe from all subjects.
        إغلاق الاتصال وإلغاء جميع الاشتراكات
        """
        logger.info("Closing NATS subscriber...")

        # Unsubscribe from all subjects
        for sub in self._subscriptions:
            try:
                await sub.unsubscribe()
            except Exception as e:
                logger.warning(f"Error unsubscribing: {e}")

        self._subscriptions.clear()
        self._handlers.clear()

        # Close connection
        if self._nc:
            try:
                await self._nc.drain()
                await self._nc.close()
                logger.info("🔌 NATS connection closed gracefully")
            except Exception as e:
                logger.error(f"Error closing NATS connection: {e}")
            finally:
                self._nc = None
                self._js = None
                self._connected = False

    # ─────────────────────────────────────────────────────────────────────────
    # Subscription Methods
    # ─────────────────────────────────────────────────────────────────────────

    async def subscribe(
        self,
        subject: str,
        handler: Callable,
        event_class: type[BaseEvent] | None = None,
        queue_group: str | None = None,
        durable_name: str | None = None,
        auto_ack: bool = True,
    ) -> bool:
        """
        Subscribe to a NATS subject.
        الاشتراك في موضوع NATS

        Args:
            subject: NATS subject to subscribe to (supports wildcards like "sahool.field.*")
            handler: Async function to handle messages
            event_class: Expected Pydantic event class for automatic deserialization
            queue_group: Queue group name for load balancing
            durable_name: Durable consumer name for JetStream
            auto_ack: Automatically acknowledge messages after processing

        Returns:
            True if subscribed successfully
        """
        if not self.is_connected:
            logger.error(f"Not connected to NATS. Cannot subscribe to {subject}")
            return False

        try:
            subscription = Subscription(
                subject=subject,
                handler=handler,
                event_class=event_class,
                queue_group=queue_group,
                durable_name=durable_name,
                auto_ack=auto_ack,
            )

            # Use JetStream if enabled and durable_name provided
            if self.config.enable_jetstream and durable_name and self._js:
                sub = await self._subscribe_jetstream(subscription)
            else:
                sub = await self._subscribe_core(subscription)

            self._subscriptions.append(sub)
            self._handlers[subject] = subscription

            logger.info(f"✅ Subscribed to {subject} (queue={queue_group}, durable={durable_name})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to subscribe to {subject}: {e}")
            return False

    async def subscribe_multiple(
        self,
        subscriptions: list[dict[str, Any]],
    ) -> int:
        """
        Subscribe to multiple subjects at once.
        الاشتراك في عدة موضوعات دفعة واحدة

        Args:
            subscriptions: List of subscription configurations

        Returns:
            Number of successful subscriptions
        """
        success_count = 0

        for sub_config in subscriptions:
            if await self.subscribe(**sub_config):
                success_count += 1

        logger.info(f"Subscribed to {success_count}/{len(subscriptions)} subjects")
        return success_count

    async def unsubscribe(self, subject: str) -> bool:
        """
        Unsubscribe from a subject.
        إلغاء الاشتراك من موضوع

        Args:
            subject: Subject to unsubscribe from

        Returns:
            True if unsubscribed successfully
        """
        if subject not in self._handlers:
            logger.warning(f"No subscription found for {subject}")
            return False

        try:
            # Find and unsubscribe
            for i, sub in enumerate(self._subscriptions):
                # Note: NATS subscriptions don't expose subject directly
                # We rely on maintaining order
                try:
                    await sub.unsubscribe()
                    self._subscriptions.pop(i)
                    del self._handlers[subject]
                    logger.info(f"✅ Unsubscribed from {subject}")
                    return True
                except:
                    continue

            return False

        except Exception as e:
            logger.error(f"Error unsubscribing from {subject}: {e}")
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # Internal Subscription Methods
    # ─────────────────────────────────────────────────────────────────────────

    async def _subscribe_core(self, subscription: Subscription):
        """Subscribe using core NATS."""
        return await self._nc.subscribe(
            subscription.subject,
            queue=subscription.queue_group,
            cb=lambda msg: asyncio.create_task(self._message_handler(msg, subscription)),
        )

    async def _subscribe_jetstream(self, subscription: Subscription):
        """Subscribe using JetStream for durable consumers."""
        return await self._js.subscribe(
            subscription.subject,
            durable=subscription.durable_name,
            cb=lambda msg: asyncio.create_task(self._message_handler(msg, subscription)),
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Message Handling
    # ─────────────────────────────────────────────────────────────────────────

    async def _message_handler(self, msg: Msg, subscription: Subscription):
        """
        Handle incoming NATS message with DLQ support.
        معالجة رسالة NATS الواردة مع دعم قائمة الرسائل الفاشلة
        """
        async with self._processing_semaphore:
            # Get retry count from message headers
            retry_count = 0
            retry_timestamps = []
            retry_errors = []

            if hasattr(msg, "headers") and msg.headers:
                retry_count = int(msg.headers.get("Nats-Retry-Count", "0"))
                retry_timestamps_str = msg.headers.get("Nats-Retry-Timestamps", "")
                retry_errors_str = msg.headers.get("Nats-Retry-Errors", "")

                if retry_timestamps_str:
                    retry_timestamps = retry_timestamps_str.split(",")
                if retry_errors_str:
                    retry_errors = retry_errors_str.split("||")

            try:
                subject = msg.subject
                data = msg.data.decode("utf-8")

                logger.debug(
                    f"📨 Received message on {subject}: {len(data)} bytes (retry: {retry_count})"
                )

                # Deserialize message
                event = await self._deserialize_message(data, subscription.event_class)

                # Call handler
                if asyncio.iscoroutinefunction(subscription.handler):
                    await subscription.handler(event)
                else:
                    subscription.handler(event)

                # Acknowledge message
                if subscription.auto_ack:
                    await self._acknowledge_message(msg)

                self._message_count += 1
                logger.debug(f"✅ Processed message on {subject}")

            except Exception as e:
                logger.error(f"❌ Error processing message on {msg.subject}: {e}")
                self._error_count += 1

                # Record retry attempt
                retry_timestamps.append(datetime.utcnow().isoformat())
                retry_errors.append(str(e)[:200])  # Truncate error message

                # Check if we should retry or move to DLQ
                if self.config.enable_dlq and self._dlq_config:
                    # Use DLQ logic
                    await self._handle_failed_message_with_dlq(
                        msg=msg,
                        subscription=subscription,
                        error=e,
                        retry_count=retry_count,
                        retry_timestamps=retry_timestamps,
                        retry_errors=retry_errors,
                    )
                elif self.config.enable_error_retry:
                    # Legacy retry logic (deprecated)
                    await self._retry_message(msg, subscription, attempt=1)
                else:
                    # NAK the message if using JetStream
                    await self._nack_message(msg)

    async def _deserialize_message(
        self,
        data: str,
        event_class: type[BaseEvent] | None,
    ) -> BaseEvent | dict[str, Any]:
        """
        Deserialize message data to event object or dictionary.
        تحويل البيانات إلى كائن حدث أو قاموس
        """
        try:
            json_data = json.loads(data)

            if event_class:
                # Deserialize to Pydantic model
                return event_class(**json_data)
            else:
                # Return raw dictionary
                return json_data

        except ValidationError as e:
            logger.error(f"Event validation failed: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            raise

    async def _acknowledge_message(self, msg: Msg):
        """Acknowledge message (JetStream only)."""
        if hasattr(msg, "ack"):
            try:
                await msg.ack()
            except Exception as e:
                logger.warning(f"Failed to ACK message: {e}")

    async def _nack_message(self, msg: Msg):
        """Negative acknowledge message (JetStream only)."""
        if hasattr(msg, "nak"):
            try:
                await msg.nak()
            except Exception as e:
                logger.warning(f"Failed to NAK message: {e}")

    async def _retry_message(
        self,
        msg: Msg,
        subscription: Subscription,
        attempt: int,
    ):
        """Retry processing a failed message."""
        if attempt > self.config.max_error_retries:
            logger.error(f"Max retries exceeded for message on {msg.subject}")
            await self._nack_message(msg)
            return

        delay = self.config.error_retry_delay * attempt
        logger.info(f"Retrying message (attempt {attempt}) after {delay}s")

        await asyncio.sleep(delay)

        try:
            data = msg.data.decode("utf-8")
            event = await self._deserialize_message(data, subscription.event_class)

            if asyncio.iscoroutinefunction(subscription.handler):
                await subscription.handler(event)
            else:
                subscription.handler(event)

            await self._acknowledge_message(msg)
            logger.info(f"✅ Retry successful on attempt {attempt}")

        except Exception as e:
            logger.error(f"Retry attempt {attempt} failed: {e}")
            await self._retry_message(msg, subscription, attempt + 1)

    # ─────────────────────────────────────────────────────────────────────────
    # Callbacks
    # ─────────────────────────────────────────────────────────────────────────

    async def _error_callback(self, e):
        """Handle NATS errors."""
        logger.error(f"❌ NATS error: {e}")
        self._error_count += 1

    async def _disconnected_callback(self):
        """Handle disconnection."""
        logger.warning("⚠️  NATS disconnected - will attempt to reconnect")
        self._connected = False

    async def _reconnected_callback(self):
        """Handle reconnection."""
        logger.info("✅ NATS reconnected successfully")
        self._connected = True

    async def _closed_callback(self):
        """Handle connection closure."""
        logger.info("🔌 NATS connection closed")
        self._connected = False

    # ─────────────────────────────────────────────────────────────────────────
    # Run Loop
    # ─────────────────────────────────────────────────────────────────────────

    async def run(self):
        """
        Keep the subscriber running indefinitely.
        الحفاظ على تشغيل المشترك بشكل مستمر

        This method blocks until interrupted or connection is closed.
        """
        logger.info("🚀 Subscriber running... Press Ctrl+C to stop")

        try:
            while self.is_connected:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Subscriber stopped by user")
        except KeyboardInterrupt:
            logger.info("Subscriber stopped by keyboard interrupt")
        finally:
            await self.close()

    # ─────────────────────────────────────────────────────────────────────────
    # Context Manager Support
    # ─────────────────────────────────────────────────────────────────────────

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# ─────────────────────────────────────────────────────────────────────────────
# Singleton Instance (optional convenience)
# ─────────────────────────────────────────────────────────────────────────────

_subscriber_instance: EventSubscriber | None = None


async def get_subscriber(
    service_name: str | None = None,
    service_version: str | None = None,
) -> EventSubscriber:
    """
    Get or create the singleton subscriber instance.
    الحصول على أو إنشاء مشترك الأحداث الوحيد

    Args:
        service_name: Service name
        service_version: Service version

    Returns:
        EventSubscriber instance
    """
    global _subscriber_instance

    if _subscriber_instance is None:
        _subscriber_instance = EventSubscriber(
            service_name=service_name,
            service_version=service_version,
        )
        await _subscriber_instance.connect()

    return _subscriber_instance


async def close_subscriber():
    """Close the singleton subscriber instance."""
    global _subscriber_instance

    if _subscriber_instance:
        await _subscriber_instance.close()
        _subscriber_instance = None


# ─────────────────────────────────────────────────────────────────────────────
# Add DLQ Methods to EventSubscriber
# ─────────────────────────────────────────────────────────────────────────────

# Import and add DLQ methods to EventSubscriber
try:
    from . import subscriber_dlq

    subscriber_dlq.add_dlq_methods_to_subscriber(EventSubscriber)
except Exception as e:
    logger.warning(f"Failed to add DLQ methods to EventSubscriber: {e}")
