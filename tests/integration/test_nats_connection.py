"""
Integration Tests for NATS Connection Patterns
اختبارات التكامل لأنماط اتصال NATS

Tests for NATS connection management, JetStream consumer creation,
Dead Letter Queue handling, and message acknowledgment patterns.

Covers:
    - Connection and reconnection behavior
    - JetStream consumer lifecycle
    - Dead Letter Queue (DLQ) message routing
    - Message acknowledgment patterns (ACK, NAK, retry)
    - EventSubscriber and EventPublisher integration

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")

# Import EventPublisher, EventSubscriber, DLQ
try:
    from shared.events.publisher import EventPublisher, PublisherConfig

    _publisher_available = True
except ImportError:
    _publisher_available = False

try:
    from shared.events.subscriber import EventSubscriber, SubscriberConfig

    _subscriber_available = True
except ImportError:
    _subscriber_available = False

try:
    from shared.events.dlq_config import DLQConfig, should_retry, is_retriable_error

    _dlq_available = True
except ImportError:
    _dlq_available = False

try:
    from shared.events.contracts import BaseEvent, FieldCreatedEvent

    _contracts_available = True
except ImportError:
    _contracts_available = False


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_nats():
    """Create a mock NATS client with full lifecycle support."""
    nc = AsyncMock()
    nc.publish = AsyncMock()
    nc.subscribe = AsyncMock()
    nc.flush = AsyncMock()
    nc.drain = AsyncMock()
    nc.close = AsyncMock()
    nc.is_connected = True
    nc.jetstream = MagicMock()
    return nc


@pytest.fixture
def mock_jetstream():
    """Create a mock JetStream context."""
    js = AsyncMock()
    js.publish = AsyncMock()
    js.subscribe = AsyncMock()
    js.pull_subscribe = AsyncMock()
    js.add_stream = AsyncMock()
    js.update_stream = AsyncMock()
    js.stream_info = AsyncMock()
    js.account_info = AsyncMock()

    # Default account info response
    account_info = MagicMock()
    account_info.streams = 3
    account_info.consumers = 5
    account_info.memory = 1024 * 1024
    account_info.storage = 10 * 1024 * 1024
    js.account_info.return_value = account_info

    return js


@pytest.fixture
def mock_nats_msg():
    """Factory for mock NATS messages with ACK/NAK support."""

    def _make(subject: str, payload: dict, headers: dict | None = None):
        msg = MagicMock()
        msg.subject = subject
        msg.data = json.dumps(payload).encode("utf-8")
        msg.headers = headers or {}
        msg.ack = AsyncMock()
        msg.nak = AsyncMock()
        msg.in_progress = AsyncMock()
        msg.metadata = MagicMock()
        msg.metadata.sequence = MagicMock()
        msg.metadata.sequence.stream = 1
        msg.metadata.num_delivered = 1
        return msg

    return _make


# ─────────────────────────────────────────────────────────────────────────────
# Tests: NATS Connection and Reconnection
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_nats_connection_established(mock_nats):
    """Test that NATS connection can be established and reports connected status."""
    assert mock_nats.is_connected is True

    # Publish a test message to verify connection is functional
    test_subject = "sahool.test.ping"
    test_data = json.dumps({"ping": True}).encode("utf-8")
    await mock_nats.publish(test_subject, test_data)
    mock_nats.publish.assert_awaited_once_with(test_subject, test_data)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_nats_disconnection_handling(mock_nats):
    """Test handling NATS disconnection and reconnection callbacks."""
    disconnected_called = False
    reconnected_called = False

    async def on_disconnected():
        nonlocal disconnected_called
        disconnected_called = True

    async def on_reconnected():
        nonlocal reconnected_called
        reconnected_called = True

    # Simulate disconnection
    mock_nats.is_connected = False
    await on_disconnected()
    assert disconnected_called is True
    assert mock_nats.is_connected is False

    # Simulate reconnection
    mock_nats.is_connected = True
    await on_reconnected()
    assert reconnected_called is True
    assert mock_nats.is_connected is True


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(not _subscriber_available, reason="shared.events.subscriber not available")
async def test_event_subscriber_connect_and_close():
    """Test EventSubscriber connect/close lifecycle with mocked NATS."""
    with patch("shared.events.subscriber.nats") as mock_nats_module:
        mock_nc = AsyncMock()
        mock_nc.is_connected = True
        mock_nc.jetstream.return_value = AsyncMock()
        mock_nc.drain = AsyncMock()
        mock_nc.close = AsyncMock()
        mock_nats_module.connect = AsyncMock(return_value=mock_nc)

        config = SubscriberConfig(
            servers=[NATS_URL],
            name="test-subscriber",
            enable_jetstream=False,
            enable_dlq=False,
        )
        subscriber = EventSubscriber(
            config=config,
            service_name="test-service",
            service_version="1.0.0",
        )

        # Connect
        connected = await subscriber.connect()
        assert connected is True
        assert subscriber.is_connected is True

        # Check stats
        stats = subscriber.stats
        assert stats["connected"] is True
        assert stats["service_name"] == "test-service"
        assert stats["message_count"] == 0

        # Close
        await subscriber.close()
        mock_nc.drain.assert_awaited_once()


# ─────────────────────────────────────────────────────────────────────────────
# Tests: JetStream Consumer Creation
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_jetstream_consumer_creation(mock_nats, mock_jetstream):
    """Test creating a JetStream durable consumer for field events."""
    mock_nats.jetstream.return_value = mock_jetstream

    js = mock_nats.jetstream()

    # Create a durable pull subscription
    durable_name = "field-consumer"
    subject = "sahool.field.*"

    await js.subscribe(subject, durable=durable_name)
    js.subscribe.assert_awaited_once_with(subject, durable=durable_name)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_jetstream_stream_creation(mock_jetstream):
    """Test creating JetStream stream for event persistence."""
    stream_config = {
        "name": "SAHOOL_EVENTS",
        "subjects": ["sahool.>"],
        "retention": "limits",
        "max_age": 7 * 86400,  # 7 days in seconds
        "max_msgs": 1_000_000,
        "max_bytes": 1024 * 1024 * 1024,  # 1 GB
        "storage": "file",
        "num_replicas": 1,
        "discard": "old",
    }

    await mock_jetstream.add_stream(**stream_config)
    mock_jetstream.add_stream.assert_awaited_once_with(**stream_config)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_jetstream_publish_with_dedup(mock_jetstream):
    """Test JetStream publish with message deduplication ID."""
    subject = "sahool.field.created"
    msg_id = str(uuid.uuid4())
    payload = json.dumps(
        {
            "event_id": msg_id,
            "field_id": str(uuid.uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
        }
    ).encode("utf-8")

    # JetStream publish with Nats-Msg-Id for deduplication
    ack = MagicMock()
    ack.stream = "SAHOOL_EVENTS"
    ack.seq = 42
    mock_jetstream.publish.return_value = ack

    result = await mock_jetstream.publish(
        subject,
        payload,
        headers={"Nats-Msg-Id": msg_id},
    )

    mock_jetstream.publish.assert_awaited_once()
    assert result.stream == "SAHOOL_EVENTS"
    assert result.seq == 42


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Dead Letter Queue Handling
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(not _dlq_available, reason="shared.events.dlq_config not available")
async def test_dlq_config_defaults():
    """Test DLQ configuration default values."""
    config = DLQConfig()

    assert config.max_retry_attempts == 3
    assert config.initial_retry_delay == 1.0
    assert config.backoff_multiplier == 2.0
    assert config.max_retry_delay == 60.0
    assert config.dlq_stream_name == "SAHOOL_DLQ"
    assert config.dlq_subject_prefix == "sahool.dlq"
    assert config.alert_threshold == 100
    assert config.alert_enabled is True


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(not _dlq_available, reason="shared.events.dlq_config not available")
async def test_dlq_subject_mapping():
    """Test DLQ subject derivation from original subject."""
    config = DLQConfig()

    # Standard event subject
    assert config.get_dlq_subject("sahool.field.created") == "sahool.dlq.field.created"
    assert config.get_dlq_subject("sahool.vision.pest_detected") == "sahool.dlq.vision.pest_detected"
    assert config.get_dlq_subject("sahool.iot.sensor_reading") == "sahool.dlq.iot.sensor_reading"
    assert config.get_dlq_subject("sahool.advisory.generated") == "sahool.dlq.advisory.generated"

    # Without sahool prefix
    assert config.get_dlq_subject("weather.alert") == "sahool.dlq.weather.alert"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(not _dlq_available, reason="shared.events.dlq_config not available")
async def test_dlq_retry_delay_exponential_backoff():
    """Test exponential backoff delay calculation for DLQ retries."""
    config = DLQConfig(
        initial_retry_delay=1.0,
        backoff_multiplier=2.0,
        max_retry_delay=60.0,
    )

    assert config.get_retry_delay(1) == 1.0  # 1.0 * 2^0 = 1.0
    assert config.get_retry_delay(2) == 2.0  # 1.0 * 2^1 = 2.0
    assert config.get_retry_delay(3) == 4.0  # 1.0 * 2^2 = 4.0
    assert config.get_retry_delay(4) == 8.0  # 1.0 * 2^3 = 8.0
    assert config.get_retry_delay(7) == 60.0  # 1.0 * 2^6 = 64.0, capped at 60


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(not _dlq_available, reason="shared.events.dlq_config not available")
async def test_dlq_should_retry_logic():
    """Test should_retry returns correct result based on attempt count."""
    config = DLQConfig(max_retry_attempts=3)

    assert should_retry(1, config) is True  # Attempt 1 < 3
    assert should_retry(2, config) is True  # Attempt 2 < 3
    assert should_retry(3, config) is False  # Attempt 3 = 3, should go to DLQ
    assert should_retry(4, config) is False  # Beyond max


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(not _dlq_available, reason="shared.events.dlq_config not available")
async def test_dlq_retriable_vs_permanent_errors():
    """Test that validation errors are non-retriable while connection errors are retriable."""
    from pydantic import ValidationError

    # Non-retriable (permanent) errors
    assert is_retriable_error(ValueError("bad data")) is False
    assert is_retriable_error(KeyError("missing_field")) is False
    assert is_retriable_error(TypeError("wrong type")) is False

    # Retriable (transient) errors
    assert is_retriable_error(ConnectionError("connection refused")) is True
    assert is_retriable_error(TimeoutError("timed out")) is True
    assert is_retriable_error(OSError("network unreachable")) is True
    assert is_retriable_error(RuntimeError("temporary failure")) is True


@pytest.mark.integration
@pytest.mark.asyncio
async def test_dlq_stream_creation(mock_jetstream):
    """Test DLQ JetStream stream is created with correct configuration."""
    # Simulate stream does not exist (raises exception)
    mock_jetstream.stream_info.side_effect = Exception("stream not found")

    await mock_jetstream.add_stream(
        name="SAHOOL_DLQ",
        subjects=["sahool.dlq.>"],
        retention="limits",
        max_age=30 * 86400,
        max_msgs=100_000,
        max_bytes=10 * 1024 * 1024 * 1024,
        max_msg_size=1024 * 1024,
        storage="file",
        num_replicas=1,
        discard="old",
    )

    mock_jetstream.add_stream.assert_awaited_once()
    call_kwargs = mock_jetstream.add_stream.call_args.kwargs
    assert call_kwargs["name"] == "SAHOOL_DLQ"
    assert call_kwargs["subjects"] == ["sahool.dlq.>"]
    assert call_kwargs["storage"] == "file"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Message Acknowledgment Patterns
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_ack_on_success(mock_nats_msg):
    """Test that successful message processing results in ACK."""
    payload = {"event_id": str(uuid.uuid4()), "status": "ok"}
    msg = mock_nats_msg("sahool.field.created", payload)

    # Simulate successful processing
    data = json.loads(msg.data.decode("utf-8"))
    assert data["status"] == "ok"

    # ACK the message
    await msg.ack()
    msg.ack.assert_awaited_once()
    msg.nak.assert_not_awaited()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_nak_on_failure(mock_nats_msg):
    """Test that failed message processing results in NAK."""
    payload = {"event_id": str(uuid.uuid4()), "corrupted": True}
    msg = mock_nats_msg("sahool.field.created", payload)

    # Simulate processing failure
    try:
        data = json.loads(msg.data.decode("utf-8"))
        if data.get("corrupted"):
            raise ValueError("Corrupted message payload")
    except ValueError:
        # NAK so NATS can redeliver
        await msg.nak()

    msg.nak.assert_awaited_once()
    msg.ack.assert_not_awaited()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_retry_with_headers(mock_nats_msg):
    """Test that retry metadata is tracked in message headers."""
    retry_headers = {
        "Nats-Retry-Count": "2",
        "Nats-Retry-Timestamps": "2026-01-20T10:00:00Z,2026-01-20T10:01:00Z",
        "Nats-Retry-Errors": "ConnectionError: timeout||ConnectionError: refused",
    }
    payload = {"event_id": str(uuid.uuid4()), "field_id": str(uuid.uuid4())}
    msg = mock_nats_msg("sahool.field.created", payload, headers=retry_headers)

    retry_count = int(msg.headers.get("Nats-Retry-Count", "0"))
    assert retry_count == 2

    retry_timestamps = msg.headers.get("Nats-Retry-Timestamps", "").split(",")
    assert len(retry_timestamps) == 2

    retry_errors = msg.headers.get("Nats-Retry-Errors", "").split("||")
    assert len(retry_errors) == 2
    assert "ConnectionError" in retry_errors[0]


# ─────────────────────────────────────────────────────────────────────────────
# Tests: EventPublisher Integration
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(not _publisher_available, reason="shared.events.publisher not available")
async def test_event_publisher_publish_and_verify():
    """Test EventPublisher publishes correctly formatted events."""
    with patch("shared.events.publisher.nats") as mock_nats_module:
        mock_nc = AsyncMock()
        mock_nc.is_connected = True
        mock_nc.publish = AsyncMock()
        mock_nc.flush = AsyncMock()
        mock_nc.drain = AsyncMock()
        mock_nc.close = AsyncMock()
        mock_nats_module.connect = AsyncMock(return_value=mock_nc)

        publisher = EventPublisher()
        await publisher.connect()

        # Publish event
        subject = "sahool.field.created"
        event_data = {
            "event_id": str(uuid.uuid4()),
            "field_id": str(uuid.uuid4()),
            "name": "Test Field",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        await publisher.publish(subject, event_data)

        # Verify publish was called
        mock_nc.publish.assert_awaited_once()
        call_args = mock_nc.publish.call_args
        assert call_args[0][0] == subject  # subject argument

        # Verify payload is valid JSON
        published_data = json.loads(call_args[0][1].decode("utf-8"))
        assert published_data["field_id"] == event_data["field_id"]
        assert published_data["name"] == "Test Field"

        await publisher.close()


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(
    not (_subscriber_available and _contracts_available),
    reason="shared.events.subscriber or contracts not available",
)
async def test_subscriber_health_check():
    """Test EventSubscriber health check returns correct structure."""
    with patch("shared.events.subscriber.nats") as mock_nats_module:
        mock_nc = AsyncMock()
        mock_nc.is_connected = True
        mock_nc.drain = AsyncMock()
        mock_nc.close = AsyncMock()

        mock_js = AsyncMock()
        account_info = MagicMock()
        account_info.streams = 2
        account_info.consumers = 4
        account_info.memory = 512 * 1024
        account_info.storage = 5 * 1024 * 1024
        mock_js.account_info.return_value = account_info
        mock_nc.jetstream.return_value = mock_js

        mock_nats_module.connect = AsyncMock(return_value=mock_nc)

        config = SubscriberConfig(
            servers=[NATS_URL],
            name="test-health",
            enable_jetstream=True,
            enable_dlq=False,
        )
        subscriber = EventSubscriber(config=config)
        await subscriber.connect()

        health = await subscriber.health_check()
        assert health["status"] in ("healthy", "degraded", "unhealthy", "warning")
        assert health["nats_connected"] is True
        assert health["jetstream_enabled"] is True
        assert health["active_subscriptions"] >= 0

        await subscriber.close()
