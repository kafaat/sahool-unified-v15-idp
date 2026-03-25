"""
SAHOOL NATS Event Publisher
============================
ناشر أحداث NATS - نشر الأحداث بشكل آمن وموثوق

Async NATS publisher for publishing domain events across the SAHOOL platform.
Provides automatic serialization, validation, JetStream support, and error handling.

Usage:
    from shared.events.publisher import EventPublisher
    from shared.events.contracts import FieldCreatedEvent
    from shared.events.subjects import SAHOOL_FIELD_CREATED

    publisher = EventPublisher()
    await publisher.connect()

    event = FieldCreatedEvent(field_id=..., farm_id=..., name="Field 1")
    await publisher.publish_event(SAHOOL_FIELD_CREATED, event)

    await publisher.close()
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .contracts import BaseEvent

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# H4 + M1: Correlation & OTel Trace Propagation Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _get_current_correlation_id() -> str | None:
    """
    H4 fix: Extract correlation_id from the current HTTP request context.
    Works with shared.middleware.request_logging which stores correlation_id
    in contextvars or starlette request.state.
    """
    # Primary: shared.logging_config defines ContextVars set by middleware
    try:
        from shared.logging_config import correlation_id_var

        return correlation_id_var.get(None)
    except (ImportError, AttributeError):
        pass

    # Fallback: check if there's a thread-local or global correlation_id
    try:
        import threading

        local = getattr(threading, "_sahool_local", None)
        if local:
            return getattr(local, "correlation_id", None)
    except Exception:
        pass

    return None


def _get_otel_trace_context() -> tuple[str | None, str | None, str | None]:
    """
    M1 fix: Extract OTel trace_id, span_id, and tracestate from the current span.
    Returns (trace_id_hex, span_id_hex, tracestate_str) or (None, None, None).
    """
    try:
        from opentelemetry import trace

        current_span = trace.get_current_span()
        ctx = current_span.get_span_context()
        if ctx and ctx.trace_id != 0:
            trace_id = format(ctx.trace_id, "032x")
            span_id = format(ctx.span_id, "016x")
            # Extract tracestate if available
            tracestate = None
            if ctx.trace_state:
                tracestate = str(ctx.trace_state)
            return trace_id, span_id, tracestate
    except (ImportError, AttributeError, Exception):
        pass

    return None, None, None


def _get_current_tenant_id() -> str | None:
    """Extract tenant_id from the current request context (JWT tid claim)."""
    try:
        from shared.logging_config import tenant_id_var

        return tenant_id_var.get(None)
    except (ImportError, AttributeError):
        pass
    return None


def _build_nats_headers(event: BaseEvent) -> dict | None:
    """
    Build canonical NATS message headers for distributed tracing & routing.

    Headers (7 standard):
      - traceparent   (W3C Trace Context)
      - tracestate    (W3C, optional)
      - X-Correlation-ID
      - X-Causation-ID
      - X-Event-ID
      - X-Tenant-ID
      - X-Schema-Version

    Returns None if no headers are available (core NATS ignores None headers).
    """
    headers: dict[str, str] = {}

    # W3C traceparent
    if event.trace_id and event.span_id:
        traceparent = f"00-{event.trace_id}-{event.span_id}-01"
        headers["traceparent"] = traceparent

    # W3C tracestate (optional, propagated from OTel)
    tracestate = getattr(event, "_tracestate", None)
    if tracestate:
        headers["tracestate"] = tracestate

    # Correlation & causation chain
    if event.correlation_id:
        headers["X-Correlation-ID"] = event.correlation_id
    if event.causation_id:
        headers["X-Causation-ID"] = event.causation_id

    # Event identity
    if event.event_id:
        headers["X-Event-ID"] = event.event_id

    # Tenant scoping (from event field, populated from JWT tid claim)
    if event.tenant_id:
        headers["X-Tenant-ID"] = str(event.tenant_id)

    # Schema version for consumer compatibility checks
    if event.version:
        headers["X-Schema-Version"] = event.version

    return headers if headers else None


# NATS client - lazy import for optional dependency
_nats_available = False

try:
    import nats
    from nats.aio.client import Client as NATSClient
    from nats.js import JetStreamContext

    _nats_available = True
except ImportError:
    logger.warning("NATS package not installed. Install with: pip install nats-py")
    nats = None  # type: ignore[assignment]
    NATSClient = None
    JetStreamContext = None


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────


class PublisherConfig(BaseModel):
    """
    NATS publisher configuration.
    إعدادات ناشر NATS
    """

    servers: list[str] = Field(
        default_factory=lambda: [os.getenv("NATS_URL", "nats://localhost:4222")],
        description="NATS server URLs",
    )
    name: str = Field(
        default_factory=lambda: os.getenv("SERVICE_NAME", "sahool-publisher"),
        description="Publisher client name",
    )
    reconnect_time_wait: int = Field(default=2, description="Seconds between reconnect attempts")
    max_reconnect_attempts: int = Field(default=60, description="Maximum reconnect attempts")
    connect_timeout: int = Field(default=10, description="Connection timeout in seconds")

    # JetStream
    enable_jetstream: bool = Field(default=True, description="Enable JetStream for persistence")
    jetstream_domain: str | None = Field(
        default_factory=lambda: os.getenv("JETSTREAM_DOMAIN", "sahool"),
        description="JetStream domain (default: sahool)",
    )

    # Publishing options
    default_timeout: float = Field(default=5.0, description="Default publish timeout")
    max_pending_bytes: int = Field(default=10_000_000, description="Max pending bytes")

    # Retry configuration
    enable_retry: bool = Field(default=True, description="Enable automatic retries")
    max_retry_attempts: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=0.5, description="Delay between retries in seconds")

    # TLS Configuration
    tls_enabled: bool = Field(default=False, description="Enable TLS for NATS connection")
    tls_ca_path: str | None = Field(default=None, description="Path to CA certificate")
    tls_cert_path: str | None = Field(default=None, description="Path to client certificate")
    tls_key_path: str | None = Field(default=None, description="Path to client key")

    @model_validator(mode="after")
    def _load_tls_from_env(self) -> "PublisherConfig":
        if os.getenv("NATS_TLS_ENABLED", "").lower() in ("true", "1", "yes"):
            self.tls_enabled = True
            self.tls_ca_path = self.tls_ca_path or os.getenv("NATS_TLS_CA")
            self.tls_cert_path = self.tls_cert_path or os.getenv("NATS_TLS_CERT")
            self.tls_key_path = self.tls_key_path or os.getenv("NATS_TLS_KEY")
        return self


# ─────────────────────────────────────────────────────────────────────────────
# Event Publisher
# ─────────────────────────────────────────────────────────────────────────────


class EventPublisher:
    """
    NATS Event Publisher for SAHOOL platform.
    ناشر الأحداث عبر NATS لمنصة سهول

    Features:
    - Automatic JSON serialization from Pydantic models
    - JetStream support for guaranteed delivery
    - Automatic reconnection
    - Retry logic with exponential backoff
    - Event validation
    - Connection health monitoring
    """

    def __init__(
        self,
        config: PublisherConfig | None = None,
        service_name: str | None = None,
        service_version: str | None = None,
    ):
        """
        Initialize the event publisher.

        Args:
            config: Publisher configuration
            service_name: Name of the service using this publisher
            service_version: Version of the service
        """
        self.config = config or PublisherConfig()
        self.service_name = service_name or os.getenv("SERVICE_NAME", "unknown")
        self.service_version = service_version or os.getenv("SERVICE_VERSION", "0.0.0")

        self._nc: NATSClient | None = None
        self._js: JetStreamContext | None = None
        self._connected = False
        self._publish_count = 0
        self._error_count = 0

        # Reconnection message buffer (max 1000 messages)
        self._pending_buffer: list[tuple[str, bytes, float, bool, dict | None]] = []
        self._pending_buffer_max_size: int = 1000
        self._buffered_count = 0
        self._buffer_overflow_count = 0

    @property
    def is_connected(self) -> bool:
        """Check if connected to NATS."""
        return self._connected and self._nc is not None

    @property
    def stats(self) -> dict[str, Any]:
        """Get publisher statistics."""
        return {
            "connected": self._connected,
            "publish_count": self._publish_count,
            "error_count": self._error_count,
            "buffered_count": self._buffered_count,
            "pending_buffer_size": len(self._pending_buffer),
            "buffer_overflow_count": self._buffer_overflow_count,
            "service_name": self.service_name,
            "service_version": self.service_version,
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
            from shared.logging_config import sanitize_urls

            _safe_servers = sanitize_urls(self.config.servers)
            logger.info(f"Connecting to NATS: {_safe_servers}")

            connect_opts = {}
            if self.config.tls_enabled:
                import ssl
                tls_context = ssl.create_default_context()
                if self.config.tls_ca_path:
                    tls_context.load_verify_locations(self.config.tls_ca_path)
                if self.config.tls_cert_path and self.config.tls_key_path:
                    tls_context.load_cert_chain(self.config.tls_cert_path, self.config.tls_key_path)
                connect_opts["tls"] = tls_context

            self._nc = await nats.connect(
                servers=self.config.servers,
                name=self.config.name,
                reconnect_time_wait=self.config.reconnect_time_wait,
                max_reconnect_attempts=self.config.max_reconnect_attempts,
                error_cb=self._error_callback,
                disconnected_cb=self._disconnected_callback,
                reconnected_cb=self._reconnected_callback,
                closed_cb=self._closed_callback,
                **connect_opts,
            )

            # Enable JetStream if configured
            if self.config.enable_jetstream:
                self._js = self._nc.jetstream(domain=self.config.jetstream_domain)
                logger.info("✅ JetStream enabled")

            self._connected = True
            logger.info(f"✅ Connected to NATS: {_safe_servers}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to NATS: {e}")
            self._connected = False
            return False

    async def close(self):
        """
        Close NATS connection gracefully.
        إغلاق الاتصال بـ NATS بشكل آمن
        """
        if self._nc:
            try:
                await self._nc.drain()  # Graceful shutdown
                await self._nc.close()
                logger.info("🔌 NATS connection closed gracefully")
            except Exception as e:
                logger.error(f"Error closing NATS connection: {e}")
            finally:
                self._nc = None
                self._js = None
                self._connected = False

    # ─────────────────────────────────────────────────────────────────────────
    # Publishing Methods
    # ─────────────────────────────────────────────────────────────────────────

    async def publish_event(
        self,
        subject: str,
        event: BaseEvent,
        timeout: float | None = None,
        use_jetstream: bool | None = None,
    ) -> bool:
        """
        Publish an event to NATS.
        نشر حدث إلى NATS

        Args:
            subject: NATS subject to publish to
            event: Event object (must inherit from BaseEvent)
            timeout: Publish timeout (uses default if None)
            use_jetstream: Use JetStream for this message (uses config default if None)

        Returns:
            True if published successfully, False otherwise
        """
        if not self.is_connected:
            # Buffer the message for retry when reconnected instead of dropping
            return self._buffer_message(subject, event, timeout, use_jetstream)

        # ── Metadata enrichment ──────────────────────────────────────────
        if not event.source_service:
            event.source_service = self.service_name

        # H4: Auto-propagate correlation_id from HTTP entrypoint context.
        # Rule: correlation_id is created ONLY at HTTP entrypoint (middleware),
        #        never inside workers.  Workers inherit it from the inbound message.
        if not event.correlation_id:
            event.correlation_id = _get_current_correlation_id()

        # Tenant propagation: pull from request context if not set on event
        if not event.tenant_id:
            ctx_tenant = _get_current_tenant_id()
            if ctx_tenant:
                event.tenant_id = ctx_tenant

        # Warn if tenant_id is still missing (critical for multi-tenant isolation)
        if not event.tenant_id:
            logger.warning(
                "event_missing_tenant_id: subject=%s event_id=%s service=%s",
                subject,
                event.event_id,
                event.source_service,
            )

        # M1: Inject OTel trace context (trace_id, span_id, tracestate)
        if not event.trace_id:
            trace_id, span_id, tracestate = _get_otel_trace_context()
            if trace_id:
                event.trace_id = trace_id
            if span_id:
                event.span_id = span_id
            if tracestate:
                # Store tracestate transiently (not serialized in JSON, only in headers)
                event._tracestate = tracestate  # type: ignore[attr-defined]

        # Serialize event
        try:
            data = self._serialize_event(event)
        except (json.JSONDecodeError, TypeError, ValueError, AttributeError) as e:
            logger.error(f"Failed to serialize event: {e}")
            self._error_count += 1
            return False

        # Build NATS headers for trace propagation (M1 fix)
        headers = _build_nats_headers(event)

        # Publish
        timeout = timeout or self.config.default_timeout
        use_jetstream = use_jetstream if use_jetstream is not None else self.config.enable_jetstream

        try:
            if use_jetstream and self._js:
                await self._publish_jetstream(subject, data, timeout, headers=headers)
            else:
                await self._publish_core(subject, data, timeout, headers=headers)

            self._publish_count += 1
            logger.info(f"📤 Published event: {subject} (id={event.event_id}, service={self.service_name})")
            return True

        except Exception as e:
            logger.error(f"Failed to publish event to {subject}: {e}")
            self._error_count += 1

            # Retry if enabled
            if self.config.enable_retry:
                return await self._retry_publish(subject, data, timeout, use_jetstream, headers=headers)

            return False

    async def publish_events(
        self,
        events: list[tuple[str, BaseEvent]],
        use_jetstream: bool | None = None,
    ) -> int:
        """
        Publish multiple events in batch.
        نشر عدة أحداث دفعة واحدة

        Args:
            events: List of (subject, event) tuples
            use_jetstream: Use JetStream for all messages

        Returns:
            Number of successfully published events
        """
        success_count = 0

        for subject, event in events:
            if await self.publish_event(subject, event, use_jetstream=use_jetstream):
                success_count += 1
            else:
                logger.warning(f"Failed to publish event to {subject}")

        logger.info(f"Batch publish completed: {success_count}/{len(events)} successful")
        return success_count

    async def publish_json(
        self,
        subject: str,
        data: dict[str, Any],
        timeout: float | None = None,
    ) -> bool:
        """
        Publish raw JSON data to NATS.
        نشر بيانات JSON مباشرة

        Args:
            subject: NATS subject
            data: Dictionary to serialize
            timeout: Publish timeout

        Returns:
            True if published successfully
        """
        if not self.is_connected:
            logger.warning(f"Not connected to NATS. Cannot publish to {subject}")
            return False

        try:
            payload = json.dumps(data, default=str).encode("utf-8")
            timeout = timeout or self.config.default_timeout

            await asyncio.wait_for(self._nc.publish(subject, payload), timeout=timeout)

            self._publish_count += 1
            logger.debug(f"📤 Published JSON to {subject}: {len(payload)} bytes")
            return True

        except Exception as e:
            logger.error(f"Failed to publish JSON to {subject}: {e}")
            self._error_count += 1
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # Internal Methods
    # ─────────────────────────────────────────────────────────────────────────

    async def _publish_core(self, subject: str, data: bytes, timeout: float, headers: dict | None = None):
        """Publish using core NATS."""
        await asyncio.wait_for(
            self._nc.publish(subject, data, headers=headers),
            timeout=timeout,
        )

    async def _publish_jetstream(self, subject: str, data: bytes, timeout: float, headers: dict | None = None):
        """Publish using JetStream for guaranteed delivery."""
        ack = await asyncio.wait_for(
            self._js.publish(subject, data, headers=headers),
            timeout=timeout,
        )
        logger.debug(f"JetStream ACK: stream={ack.stream}, seq={ack.seq}")

    async def _retry_publish(
        self,
        subject: str,
        data: bytes,
        timeout: float,
        use_jetstream: bool,
        headers: dict | None = None,
    ) -> bool:
        """Retry publishing with exponential backoff."""
        for attempt in range(1, self.config.max_retry_attempts + 1):
            delay = self.config.retry_delay * (2 ** (attempt - 1))  # Exponential backoff
            await asyncio.sleep(delay)

            logger.info(f"Retry attempt {attempt}/{self.config.max_retry_attempts} for {subject}")

            try:
                if use_jetstream and self._js:
                    await self._publish_jetstream(subject, data, timeout, headers=headers)
                else:
                    await self._publish_core(subject, data, timeout, headers=headers)

                logger.info(f"✅ Retry successful on attempt {attempt}")
                self._publish_count += 1
                return True

            except Exception as e:
                logger.warning(f"Retry attempt {attempt} failed: {e}")

        logger.error(f"❌ All retry attempts exhausted for {subject}")
        return False

    def _serialize_event(self, event: BaseEvent) -> bytes:
        """Serialize event to JSON bytes."""
        return event.model_dump_json().encode("utf-8")

    # ─────────────────────────────────────────────────────────────────────────
    # Reconnection Message Buffer
    # ─────────────────────────────────────────────────────────────────────────

    def _buffer_message(
        self,
        subject: str,
        event: BaseEvent,
        timeout: float | None,
        use_jetstream: bool | None,
    ) -> bool:
        """
        Buffer a message for retry when reconnected instead of dropping it.
        تخزين الرسالة مؤقتا لإعادة المحاولة عند إعادة الاتصال

        Returns:
            True if buffered successfully, False if buffer is full
        """
        if len(self._pending_buffer) >= self._pending_buffer_max_size:
            self._buffer_overflow_count += 1
            logger.error(
                f"Pending buffer full ({self._pending_buffer_max_size}). "
                f"Dropping message for {subject}. "
                f"Overflow count: {self._buffer_overflow_count}"
            )
            self._error_count += 1
            return False

        # Serialize eagerly so we fail fast on bad data
        try:
            data = self._serialize_event(event)
        except (json.JSONDecodeError, TypeError, ValueError, AttributeError) as e:
            logger.error(f"Failed to serialize event for buffering: {e}")
            self._error_count += 1
            return False

        headers = _build_nats_headers(event)
        effective_timeout = timeout or self.config.default_timeout
        effective_js = use_jetstream if use_jetstream is not None else self.config.enable_jetstream

        self._pending_buffer.append((subject, data, effective_timeout, effective_js, headers))
        self._buffered_count += 1
        logger.warning(
            f"Buffered message for {subject} (buffer size: {len(self._pending_buffer)}). Will flush on reconnection."
        )
        return True

    async def _flush_buffer(self) -> int:
        """
        Flush all buffered messages after reconnection.
        إرسال جميع الرسائل المخزنة مؤقتا بعد إعادة الاتصال

        Returns:
            Number of successfully flushed messages
        """
        if not self._pending_buffer:
            return 0

        buffer_size = len(self._pending_buffer)
        logger.info(f"Flushing {buffer_size} buffered messages after reconnection")

        flushed = 0
        failed: list[tuple[str, bytes, float, bool, dict | None]] = []

        for subject, data, timeout, use_jetstream, headers in self._pending_buffer:
            try:
                if use_jetstream and self._js:
                    await self._publish_jetstream(subject, data, timeout, headers=headers)
                else:
                    await self._publish_core(subject, data, timeout, headers=headers)
                flushed += 1
                self._publish_count += 1
            except Exception as e:
                logger.warning(f"Failed to flush buffered message to {subject}: {e}")
                failed.append((subject, data, timeout, use_jetstream, headers))

        self._pending_buffer = failed

        logger.info(f"Buffer flush complete: {flushed}/{buffer_size} sent, {len(failed)} remaining")
        return flushed

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
        """Handle reconnection and flush buffered messages."""
        logger.info("✅ NATS reconnected successfully")
        self._connected = True

        # Re-initialize JetStream context after reconnection
        if self.config.enable_jetstream and self._nc:
            try:
                self._js = self._nc.jetstream(domain=self.config.jetstream_domain)
            except Exception as e:
                logger.warning(f"Failed to re-initialize JetStream after reconnection: {e}")

        # Flush buffered messages
        try:
            flushed = await self._flush_buffer()
            if flushed > 0:
                logger.info(f"Flushed {flushed} buffered messages after reconnection")
        except Exception as e:
            logger.error(f"Error flushing buffer after reconnection: {e}")

    async def _closed_callback(self):
        """Handle connection closure."""
        logger.info("🔌 NATS connection closed")
        self._connected = False

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

_publisher_instance: EventPublisher | None = None
_publisher_lock = asyncio.Lock()


async def get_publisher(
    service_name: str | None = None,
    service_version: str | None = None,
) -> EventPublisher:
    """
    Get or create the singleton publisher instance.
    الحصول على أو إنشاء ناشر الأحداث الوحيد
    Thread-safe with double-check locking.

    Args:
        service_name: Service name
        service_version: Service version

    Returns:
        EventPublisher instance
    """
    global _publisher_instance

    if _publisher_instance is not None:
        return _publisher_instance

    async with _publisher_lock:
        # Double-check after acquiring lock
        if _publisher_instance is None:
            instance = EventPublisher(
                service_name=service_name,
                service_version=service_version,
            )
            await instance.connect()
            _publisher_instance = instance

    return _publisher_instance


async def close_publisher():
    """Close the singleton publisher instance."""
    global _publisher_instance

    if _publisher_instance:
        await _publisher_instance.close()
        _publisher_instance = None


# ─────────────────────────────────────────────────────────────────────────────
# Convenience Functions
# ─────────────────────────────────────────────────────────────────────────────


async def publish_event(subject: str, event: BaseEvent) -> bool:
    """
    Convenience function to publish an event using the singleton publisher.

    Args:
        subject: NATS subject
        event: Event to publish

    Returns:
        True if published successfully
    """
    publisher = await get_publisher()
    return await publisher.publish_event(subject, event)


# ─────────────────────────────────────────────────────────────────────────────
# Correlation/Causation Chain Helper
# ─────────────────────────────────────────────────────────────────────────────


def chain_event(
    parent: BaseEvent | dict[str, Any],
    child: BaseEvent,
) -> BaseEvent:
    """
    Propagate correlation/causation from a parent (inbound) event to a child
    (outbound) event.  This is the canonical way to link events in a chain.

    Rules (Spec §2):
      - child.correlation_id = parent.correlation_id  (never changes)
      - child.causation_id   = parent.event_id        (links to direct cause)
      - child.event_id       = new uuid                (already set by default)

    Usage in handlers:
        from shared.events.publisher import chain_event

        inbound_event = ...   # deserialized from NATS
        outbound = SomeEvent(field_id=..., ...)
        chain_event(inbound_event, outbound)
        await publisher.publish_event(subject, outbound)
    """
    if isinstance(parent, dict):
        child.correlation_id = parent.get("correlation_id")
        child.causation_id = parent.get("event_id")
        tid = parent.get("trace_id")
        if tid:
            child.trace_id = tid
    else:
        child.correlation_id = parent.correlation_id
        child.causation_id = parent.event_id
        if parent.trace_id:
            child.trace_id = parent.trace_id
    return child
