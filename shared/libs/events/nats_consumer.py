"""
SAHOOL NATS Consumer with Dead Letter Queue (DLQ) Support
Handles event consumption with automatic retry and DLQ routing for failed messages

Field-First Architecture:
- NATS → consumer → processing → DLQ (on failure)
- Automatic retry with exponential backoff
- Failed events routed to sahool.dlq.{event_type} after max retries
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Optional, Awaitable
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# NATS client - lazy import for optional dependency
_nats_available = False

try:
    import nats
    from nats.aio.client import Client as NATSClient
    from nats.js import JetStreamContext
    from nats.js.api import ConsumerConfig, DeliverPolicy, AckPolicy
    _nats_available = True
except ImportError:
    logger.warning("NATS package not installed. NATS consumption disabled.")
    NATSClient = None
    JetStreamContext = None


class ProcessingResult(Enum):
    """Result of message processing"""
    SUCCESS = "success"
    RETRY = "retry"
    DEAD_LETTER = "dead_letter"


@dataclass
class ConsumerContext:
    """Context passed to message handlers"""
    subject: str
    data: bytes
    headers: dict[str, str]
    attempt: int
    max_retries: int


class NATSConsumerConfig(BaseModel):
    """NATS consumer configuration"""
    servers: list[str] = Field(default_factory=lambda: ["nats://localhost:4222"])
    name: str = Field(default="sahool-consumer")
    stream_name: str = Field(default="SAHOOL_EVENTS")
    consumer_name: str = Field(default="default-consumer")

    # Subscription config
    subject_filter: str = Field(default="sahool.analysis.*")
    durable: bool = Field(default=True)

    # Retry config
    max_retries: int = Field(default=3)
    retry_delay_seconds: int = Field(default=5)
    exponential_backoff: bool = Field(default=True)

    # DLQ config
    dlq_enabled: bool = Field(default=True)
    dlq_subject_prefix: str = Field(default="sahool.dlq")

    # Connection config
    reconnect_time_wait: int = Field(default=2)
    max_reconnect_attempts: int = Field(default=60)


class FailedEvent(BaseModel):
    """Model for failed events sent to DLQ"""
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
    dlq_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    dlq_reason: str = "max_retries_exceeded"

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps({
            "event_id": self.event_id,
            "original_subject": self.original_subject,
            "event_type": self.event_type,
            "source_service": self.source_service,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "farmer_id": self.farmer_id,
            "error_message": self.error_message,
            "error_type": self.error_type,
            "stack_trace": self.stack_trace,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "first_attempt_at": self.first_attempt_at.isoformat(),
            "last_attempt_at": self.last_attempt_at.isoformat(),
            "original_data": self.original_data,
            "original_headers": self.original_headers,
            "dlq_timestamp": self.dlq_timestamp.isoformat(),
            "dlq_reason": self.dlq_reason,
        })


class NATSConsumer:
    """
    NATS Consumer with Dead Letter Queue support

    Features:
    - Automatic retry with exponential backoff
    - DLQ routing after max retries
    - Error context preservation
    - Message acknowledgement handling

    Usage:
        consumer = NATSConsumer(config)
        await consumer.connect()

        async def handler(ctx: ConsumerContext) -> ProcessingResult:
            # Process message
            data = json.loads(ctx.data)
            # ... do work ...
            return ProcessingResult.SUCCESS

        await consumer.subscribe(handler)
        await consumer.start()
    """

    def __init__(self, config: Optional[NATSConsumerConfig] = None):
        self.config = config or NATSConsumerConfig()
        self._nc: Optional[NATSClient] = None
        self._js: Optional[JetStreamContext] = None
        self._connected = False
        self._running = False
        self._subscriptions = []
        self._message_handlers: list[tuple[str, Callable]] = []

    @property
    def is_connected(self) -> bool:
        return self._connected and self._nc is not None

    async def connect(self) -> bool:
        """Connect to NATS server"""
        if not _nats_available:
            logger.warning("NATS not available. Consumer disabled.")
            return False

        try:
            self._nc = await nats.connect(
                servers=self.config.servers,
                name=self.config.name,
                reconnect_time_wait=self.config.reconnect_time_wait,
                max_reconnect_attempts=self.config.max_reconnect_attempts,
                error_cb=self._error_callback,
                disconnected_cb=self._disconnected_callback,
                reconnected_cb=self._reconnected_callback,
            )
            self._js = self._nc.jetstream()
            self._connected = True
            logger.info(f"✅ NATS Consumer connected: {self.config.servers}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect NATS consumer: {e}")
            return False

    async def close(self):
        """Close NATS connection"""
        self._running = False

        # Unsubscribe from all subscriptions
        for sub in self._subscriptions:
            try:
                await sub.unsubscribe()
            except Exception as e:
                logger.warning(f"Error unsubscribing: {e}")

        if self._nc:
            await self._nc.close()
            self._connected = False
            logger.info("🔌 NATS Consumer connection closed")

    async def _error_callback(self, e):
        logger.error(f"NATS Consumer error: {e}")

    async def _disconnected_callback(self):
        logger.warning("NATS Consumer disconnected")
        self._connected = False

    async def _reconnected_callback(self):
        logger.info("NATS Consumer reconnected")
        self._connected = True

    async def subscribe(
        self,
        handler: Callable[[ConsumerContext], Awaitable[ProcessingResult]],
        subject: Optional[str] = None,
        stream_name: Optional[str] = None,
        consumer_name: Optional[str] = None,
    ):
        """
        Subscribe to a NATS subject with a message handler

        Args:
            handler: Async function that processes messages
            subject: Subject filter (default: from config)
            stream_name: Stream name (default: from config)
            consumer_name: Consumer name (default: from config)
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to NATS. Call connect() first.")

        subject = subject or self.config.subject_filter
        stream_name = stream_name or self.config.stream_name
        consumer_name = consumer_name or self.config.consumer_name

        try:
            # Create or get the stream
            try:
                await self._js.stream_info(stream_name)
                logger.info(f"Using existing stream: {stream_name}")
            except Exception:
                # Stream doesn't exist, create it
                from nats.js.api import StreamConfig
                stream_config = StreamConfig(
                    name=stream_name,
                    subjects=[f"sahool.>"],  # All sahool subjects
                )
                await self._js.add_stream(stream_config)
                logger.info(f"Created stream: {stream_name}")

            # Subscribe with pull-based consumer
            consumer_config = ConsumerConfig(
                durable_name=consumer_name if self.config.durable else None,
                ack_policy=AckPolicy.EXPLICIT,
                deliver_policy=DeliverPolicy.ALL,
            )

            psub = await self._js.pull_subscribe(
                subject,
                durable=consumer_name if self.config.durable else None,
                stream=stream_name,
            )

            self._subscriptions.append(psub)
            self._message_handlers.append((subject, handler))

            logger.info(
                f"📥 Subscribed to {subject} "
                f"(stream={stream_name}, consumer={consumer_name})"
            )

        except Exception as e:
            logger.error(f"Failed to subscribe to {subject}: {e}")
            raise

    async def start(self):
        """Start consuming messages"""
        if not self.is_connected:
            raise RuntimeError("Not connected to NATS. Call connect() first.")

        if not self._subscriptions:
            raise RuntimeError("No subscriptions. Call subscribe() first.")

        self._running = True
        logger.info("🚀 NATS Consumer started")

        # Start processing loop for each subscription
        tasks = []
        for sub, (subject, handler) in zip(self._subscriptions, self._message_handlers):
            task = asyncio.create_task(self._process_subscription(sub, handler, subject))
            tasks.append(task)

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Consumer cancelled")
        finally:
            self._running = False

    async def _process_subscription(self, subscription, handler, subject: str):
        """Process messages from a subscription"""
        retry_attempts: dict[str, int] = {}
        first_attempts: dict[str, datetime] = {}

        while self._running:
            try:
                # Fetch messages in batch
                msgs = await subscription.fetch(batch=10, timeout=5)

                for msg in msgs:
                    msg_id = msg.headers.get("Nats-Msg-Id", "unknown") if msg.headers else "unknown"

                    # Track retry attempts
                    if msg_id not in retry_attempts:
                        retry_attempts[msg_id] = 0
                        first_attempts[msg_id] = datetime.now(timezone.utc)

                    attempt = retry_attempts[msg_id]

                    try:
                        # Create context
                        ctx = ConsumerContext(
                            subject=msg.subject,
                            data=msg.data,
                            headers=dict(msg.headers) if msg.headers else {},
                            attempt=attempt,
                            max_retries=self.config.max_retries,
                        )

                        # Call handler
                        result = await handler(ctx)

                        if result == ProcessingResult.SUCCESS:
                            await msg.ack()
                            retry_attempts.pop(msg_id, None)
                            first_attempts.pop(msg_id, None)
                            logger.debug(f"✅ Message processed: {msg.subject}")

                        elif result == ProcessingResult.RETRY:
                            if attempt < self.config.max_retries:
                                await msg.nak()
                                retry_attempts[msg_id] += 1

                                # Exponential backoff
                                if self.config.exponential_backoff:
                                    delay = self.config.retry_delay_seconds * (2 ** attempt)
                                else:
                                    delay = self.config.retry_delay_seconds

                                logger.warning(
                                    f"⚠️ Retry scheduled (attempt {attempt + 1}/{self.config.max_retries}) "
                                    f"for {msg.subject}, delay={delay}s"
                                )
                                await asyncio.sleep(delay)
                            else:
                                # Max retries exceeded - send to DLQ
                                await self._send_to_dlq(msg, ctx, retry_attempts[msg_id], first_attempts[msg_id])
                                await msg.ack()  # ACK to remove from stream
                                retry_attempts.pop(msg_id, None)
                                first_attempts.pop(msg_id, None)

                        elif result == ProcessingResult.DEAD_LETTER:
                            # Immediate DLQ routing
                            await self._send_to_dlq(msg, ctx, retry_attempts[msg_id], first_attempts[msg_id])
                            await msg.ack()
                            retry_attempts.pop(msg_id, None)
                            first_attempts.pop(msg_id, None)

                    except Exception as e:
                        logger.error(f"Error processing message from {msg.subject}: {e}", exc_info=True)

                        if attempt < self.config.max_retries:
                            await msg.nak()
                            retry_attempts[msg_id] += 1
                        else:
                            # Send to DLQ on error after max retries
                            try:
                                await self._send_to_dlq(
                                    msg,
                                    ConsumerContext(
                                        subject=msg.subject,
                                        data=msg.data,
                                        headers=dict(msg.headers) if msg.headers else {},
                                        attempt=attempt,
                                        max_retries=self.config.max_retries,
                                    ),
                                    retry_attempts[msg_id],
                                    first_attempts[msg_id],
                                    error=e,
                                )
                            except Exception as dlq_error:
                                logger.error(f"Failed to send to DLQ: {dlq_error}")

                            await msg.ack()
                            retry_attempts.pop(msg_id, None)
                            first_attempts.pop(msg_id, None)

            except asyncio.TimeoutError:
                # No messages available, continue
                continue
            except Exception as e:
                logger.error(f"Error in subscription loop: {e}", exc_info=True)
                await asyncio.sleep(1)

    async def _send_to_dlq(
        self,
        msg,
        ctx: ConsumerContext,
        retry_count: int,
        first_attempt: datetime,
        error: Optional[Exception] = None,
    ):
        """Send failed message to Dead Letter Queue"""
        if not self.config.dlq_enabled:
            logger.warning(f"DLQ disabled. Discarding failed message: {msg.subject}")
            return

        try:
            # Parse original data
            try:
                data = json.loads(msg.data.decode('utf-8'))
            except Exception:
                data = {"raw_data": msg.data.decode('utf-8', errors='replace')}

            # Extract event type from subject (e.g., sahool.analysis.ndvi_computed -> ndvi_computed)
            subject_parts = msg.subject.split('.')
            event_type = subject_parts[-1] if len(subject_parts) > 0 else "unknown"

            # Create failed event
            failed_event = FailedEvent(
                event_id=data.get("event_id", ctx.headers.get("Nats-Msg-Id", "unknown")),
                original_subject=msg.subject,
                event_type=event_type,
                source_service=data.get("source_service", "unknown"),
                tenant_id=data.get("tenant_id"),
                field_id=data.get("field_id"),
                farmer_id=data.get("farmer_id"),
                error_message=str(error) if error else "Max retries exceeded",
                error_type=type(error).__name__ if error else "MaxRetriesExceeded",
                stack_trace=None,  # Could add traceback.format_exc() here
                retry_count=retry_count,
                max_retries=self.config.max_retries,
                first_attempt_at=first_attempt,
                last_attempt_at=datetime.now(timezone.utc),
                original_data=data,
                original_headers=ctx.headers,
            )

            # DLQ subject: sahool.dlq.{event_type}
            dlq_subject = f"{self.config.dlq_subject_prefix}.{event_type}"
            dlq_data = failed_event.to_json().encode('utf-8')

            # Publish to DLQ
            await self._nc.publish(dlq_subject, dlq_data)

            logger.error(
                f"💀 Message sent to DLQ: {dlq_subject} "
                f"(event_id={failed_event.event_id}, retries={retry_count})"
            )

        except Exception as e:
            logger.error(f"Failed to send message to DLQ: {e}", exc_info=True)


# Convenience function for creating and starting a consumer
async def start_consumer(
    handler: Callable[[ConsumerContext], Awaitable[ProcessingResult]],
    config: Optional[NATSConsumerConfig] = None,
    subject: Optional[str] = None,
) -> NATSConsumer:
    """
    Convenience function to create, connect, and start a consumer

    Args:
        handler: Message processing function
        config: Optional consumer configuration
        subject: Optional subject filter

    Returns:
        Running NATSConsumer instance

    Example:
        async def my_handler(ctx: ConsumerContext) -> ProcessingResult:
            data = json.loads(ctx.data)
            # Process data...
            return ProcessingResult.SUCCESS

        consumer = await start_consumer(my_handler)
    """
    consumer = NATSConsumer(config)
    await consumer.connect()
    await consumer.subscribe(handler, subject=subject)

    # Start in background
    asyncio.create_task(consumer.start())

    return consumer
