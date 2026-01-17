"""
اختبارات مشترك الأحداث NATS
NATS Event Subscriber Tests

Tests for the SAHOOL platform event subscriber module.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from uuid import uuid4

# Import the module under test
from shared.events.subscriber import (
    EventSubscriber,
    SubscriberConfig,
    Subscription,
    get_subscriber,
    close_subscriber,
)
from shared.events.contracts import BaseEvent


# ─────────────────────────────────────────────────────────────────────────────
# Test Fixtures
# ─────────────────────────────────────────────────────────────────────────────


class SampleEvent(BaseEvent):
    """Sample event for testing."""

    field_id: str
    field_name: str
    action: str = "created"


@pytest.fixture
def subscriber_config():
    """Create a test subscriber configuration."""
    return SubscriberConfig(
        servers=["nats://localhost:4222"],
        name="test-subscriber",
        enable_jetstream=False,
        enable_dlq=False,
        enable_error_retry=False,
        max_concurrent_messages=5,
    )


@pytest.fixture
def sample_event_data():
    """Create sample event data as dict."""
    return {
        "event_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tenant_id": "tenant-001",
        "source_service": "test-service",
        "field_id": "field-123",
        "field_name": "Test Field",
        "action": "created",
    }


@pytest.fixture
def subscriber(subscriber_config):
    """Create a subscriber instance for testing."""
    return EventSubscriber(
        config=subscriber_config,
        service_name="test-service",
        service_version="1.0.0",
    )


# ─────────────────────────────────────────────────────────────────────────────
# SubscriberConfig Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSubscriberConfig:
    """Tests for SubscriberConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = SubscriberConfig()

        assert config.reconnect_time_wait == 2
        assert config.max_reconnect_attempts == 60
        assert config.connect_timeout == 10
        assert config.enable_jetstream is True
        assert config.enable_error_retry is True
        assert config.max_error_retries == 3
        assert config.max_concurrent_messages == 10
        assert config.enable_dlq is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = SubscriberConfig(
            servers=["nats://custom:4222"],
            name="custom-subscriber",
            enable_jetstream=False,
            max_concurrent_messages=20,
            enable_dlq=False,
        )

        assert config.servers == ["nats://custom:4222"]
        assert config.name == "custom-subscriber"
        assert config.enable_jetstream is False
        assert config.max_concurrent_messages == 20
        assert config.enable_dlq is False

    def test_config_from_env(self, monkeypatch):
        """Test configuration from environment variables."""
        monkeypatch.setenv("NATS_URL", "nats://env-server:4222")
        monkeypatch.setenv("SERVICE_NAME", "env-service")

        config = SubscriberConfig()

        assert "nats://env-server:4222" in config.servers
        assert config.name == "env-service"


# ─────────────────────────────────────────────────────────────────────────────
# Subscription Model Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSubscriptionModel:
    """Tests for Subscription model."""

    def test_subscription_creation(self):
        """Test subscription model creation."""

        async def handler(event):
            pass

        sub = Subscription(
            subject="test.subject",
            handler=handler,
            event_class=SampleEvent,
            queue_group="test-group",
            durable_name="test-durable",
            auto_ack=True,
        )

        assert sub.subject == "test.subject"
        assert sub.handler == handler
        assert sub.event_class == SampleEvent
        assert sub.queue_group == "test-group"
        assert sub.durable_name == "test-durable"
        assert sub.auto_ack is True

    def test_subscription_defaults(self):
        """Test subscription default values."""

        def handler(event):
            pass

        sub = Subscription(subject="test.subject", handler=handler)

        assert sub.event_class is None
        assert sub.queue_group is None
        assert sub.durable_name is None
        assert sub.auto_ack is True


# ─────────────────────────────────────────────────────────────────────────────
# EventSubscriber Initialization Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventSubscriberInit:
    """Tests for EventSubscriber initialization."""

    def test_init_with_defaults(self):
        """Test subscriber initialization with defaults."""
        subscriber = EventSubscriber()

        assert subscriber.config is not None
        assert subscriber.service_name is not None
        assert subscriber._connected is False
        assert subscriber._nc is None
        assert subscriber._js is None
        assert len(subscriber._subscriptions) == 0
        assert len(subscriber._handlers) == 0

    def test_init_with_config(self, subscriber_config):
        """Test subscriber initialization with custom config."""
        subscriber = EventSubscriber(
            config=subscriber_config,
            service_name="my-service",
            service_version="2.0.0",
        )

        assert subscriber.config == subscriber_config
        assert subscriber.service_name == "my-service"
        assert subscriber.service_version == "2.0.0"

    def test_is_connected_false_initially(self, subscriber):
        """Test that subscriber is not connected initially."""
        assert subscriber.is_connected is False

    def test_stats_initial_values(self, subscriber):
        """Test initial statistics values."""
        stats = subscriber.stats

        assert stats["connected"] is False
        assert stats["message_count"] == 0
        assert stats["error_count"] == 0
        assert stats["dlq_count"] == 0
        assert stats["retry_count"] == 0
        assert stats["active_subscriptions"] == 0
        assert stats["service_name"] == "test-service"
        assert stats["service_version"] == "1.0.0"


# ─────────────────────────────────────────────────────────────────────────────
# EventSubscriber Connection Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventSubscriberConnection:
    """Tests for EventSubscriber connection management."""

    @pytest.mark.asyncio
    async def test_connect_without_nats_library(self, subscriber):
        """Test connection attempt when NATS library is unavailable."""
        with patch("shared.events.subscriber._nats_available", False):
            result = await subscriber.connect()
            assert result is False
            assert subscriber.is_connected is False

    @pytest.mark.asyncio
    async def test_connect_already_connected(self, subscriber):
        """Test connection when already connected."""
        subscriber._connected = True
        subscriber._nc = MagicMock()

        result = await subscriber.connect()

        assert result is True

    @pytest.mark.asyncio
    async def test_connect_success(self, subscriber):
        """Test successful connection to NATS."""
        mock_nc = AsyncMock()

        with patch("shared.events.subscriber._nats_available", True):
            with patch("shared.events.subscriber.nats") as mock_nats:
                mock_nats.connect = AsyncMock(return_value=mock_nc)

                result = await subscriber.connect()

                assert result is True
                assert subscriber.is_connected is True

    @pytest.mark.asyncio
    async def test_connect_failure(self, subscriber):
        """Test connection failure."""
        with patch("shared.events.subscriber._nats_available", True):
            with patch("shared.events.subscriber.nats") as mock_nats:
                mock_nats.connect = AsyncMock(side_effect=Exception("Connection failed"))

                result = await subscriber.connect()

                assert result is False
                assert subscriber.is_connected is False

    @pytest.mark.asyncio
    async def test_close_connection(self, subscriber):
        """Test closing the NATS connection."""
        mock_nc = AsyncMock()
        subscriber._nc = mock_nc
        subscriber._connected = True

        await subscriber.close()

        mock_nc.drain.assert_called_once()
        mock_nc.close.assert_called_once()
        assert subscriber._nc is None
        assert subscriber._connected is False

    @pytest.mark.asyncio
    async def test_close_unsubscribes_all(self, subscriber):
        """Test that close unsubscribes from all subjects."""
        mock_nc = AsyncMock()
        mock_sub1 = AsyncMock()
        mock_sub2 = AsyncMock()

        subscriber._nc = mock_nc
        subscriber._connected = True
        subscriber._subscriptions = [mock_sub1, mock_sub2]

        await subscriber.close()

        mock_sub1.unsubscribe.assert_called_once()
        mock_sub2.unsubscribe.assert_called_once()
        assert len(subscriber._subscriptions) == 0


# ─────────────────────────────────────────────────────────────────────────────
# EventSubscriber Subscription Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventSubscriberSubscription:
    """Tests for EventSubscriber subscription functionality."""

    @pytest.mark.asyncio
    async def test_subscribe_not_connected(self, subscriber):
        """Test subscribing when not connected."""

        async def handler(event):
            pass

        result = await subscriber.subscribe("test.subject", handler)

        assert result is False

    @pytest.mark.asyncio
    async def test_subscribe_success(self, subscriber):
        """Test successful subscription."""
        mock_nc = AsyncMock()
        mock_sub = AsyncMock()
        mock_nc.subscribe = AsyncMock(return_value=mock_sub)

        subscriber._nc = mock_nc
        subscriber._connected = True

        async def handler(event):
            pass

        result = await subscriber.subscribe(
            "test.subject",
            handler,
            event_class=SampleEvent,
            queue_group="test-group",
        )

        assert result is True
        assert len(subscriber._subscriptions) == 1
        assert "test.subject" in subscriber._handlers

    @pytest.mark.asyncio
    async def test_subscribe_multiple(self, subscriber):
        """Test subscribing to multiple subjects."""
        mock_nc = AsyncMock()
        mock_sub = AsyncMock()
        mock_nc.subscribe = AsyncMock(return_value=mock_sub)

        subscriber._nc = mock_nc
        subscriber._connected = True

        async def handler(event):
            pass

        subscriptions = [
            {"subject": "test.subject.1", "handler": handler},
            {"subject": "test.subject.2", "handler": handler},
            {"subject": "test.subject.3", "handler": handler},
        ]

        count = await subscriber.subscribe_multiple(subscriptions)

        assert count == 3
        assert len(subscriber._subscriptions) == 3

    @pytest.mark.asyncio
    async def test_unsubscribe(self, subscriber):
        """Test unsubscribing from a subject."""
        mock_nc = AsyncMock()
        mock_sub = AsyncMock()
        mock_nc.subscribe = AsyncMock(return_value=mock_sub)

        subscriber._nc = mock_nc
        subscriber._connected = True

        async def handler(event):
            pass

        await subscriber.subscribe("test.subject", handler)

        result = await subscriber.unsubscribe("test.subject")

        assert result is True
        assert "test.subject" not in subscriber._handlers

    @pytest.mark.asyncio
    async def test_unsubscribe_not_found(self, subscriber):
        """Test unsubscribing from non-existent subject."""
        result = await subscriber.unsubscribe("nonexistent.subject")

        assert result is False


# ─────────────────────────────────────────────────────────────────────────────
# EventSubscriber Message Handling Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventSubscriberMessageHandling:
    """Tests for message handling functionality."""

    @pytest.mark.asyncio
    async def test_deserialize_message_to_event(self, subscriber, sample_event_data):
        """Test deserializing message to event object."""
        data = json.dumps(sample_event_data)

        event = await subscriber._deserialize_message(data, SampleEvent)

        assert isinstance(event, SampleEvent)
        assert event.field_id == "field-123"
        assert event.field_name == "Test Field"
        assert event.action == "created"

    @pytest.mark.asyncio
    async def test_deserialize_message_to_dict(self, subscriber, sample_event_data):
        """Test deserializing message to dictionary."""
        data = json.dumps(sample_event_data)

        result = await subscriber._deserialize_message(data, None)

        assert isinstance(result, dict)
        assert result["field_id"] == "field-123"

    @pytest.mark.asyncio
    async def test_deserialize_invalid_json(self, subscriber):
        """Test deserializing invalid JSON."""
        with pytest.raises(json.JSONDecodeError):
            await subscriber._deserialize_message("invalid json", None)

    @pytest.mark.asyncio
    async def test_deserialize_validation_error(self, subscriber):
        """Test deserializing with validation error."""
        # Missing required fields
        data = json.dumps({"invalid": "data"})

        with pytest.raises(Exception):
            await subscriber._deserialize_message(data, SampleEvent)

    @pytest.mark.asyncio
    async def test_acknowledge_message(self, subscriber):
        """Test message acknowledgment."""
        mock_msg = AsyncMock()
        mock_msg.ack = AsyncMock()

        await subscriber._acknowledge_message(mock_msg)

        mock_msg.ack.assert_called_once()

    @pytest.mark.asyncio
    async def test_nack_message(self, subscriber):
        """Test negative acknowledgment."""
        mock_msg = AsyncMock()
        mock_msg.nak = AsyncMock()

        await subscriber._nack_message(mock_msg)

        mock_msg.nak.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# EventSubscriber Handler Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventSubscriberHandler:
    """Tests for message handler execution."""

    @pytest.mark.asyncio
    async def test_message_handler_success(self, subscriber, sample_event_data):
        """Test successful message handling."""
        received_events = []

        async def handler(event):
            received_events.append(event)

        mock_msg = MagicMock()
        mock_msg.subject = "test.subject"
        mock_msg.data = json.dumps(sample_event_data).encode("utf-8")
        mock_msg.headers = None
        mock_msg.ack = AsyncMock()

        subscription = Subscription(
            subject="test.subject",
            handler=handler,
            event_class=SampleEvent,
            auto_ack=True,
        )

        subscriber._nc = MagicMock()
        subscriber._connected = True

        await subscriber._message_handler(mock_msg, subscription)

        assert len(received_events) == 1
        assert subscriber._message_count == 1

    @pytest.mark.asyncio
    async def test_message_handler_sync_handler(self, subscriber, sample_event_data):
        """Test message handling with synchronous handler."""
        received_events = []

        def handler(event):
            received_events.append(event)

        mock_msg = MagicMock()
        mock_msg.subject = "test.subject"
        mock_msg.data = json.dumps(sample_event_data).encode("utf-8")
        mock_msg.headers = None
        mock_msg.ack = AsyncMock()

        subscription = Subscription(
            subject="test.subject",
            handler=handler,
            event_class=SampleEvent,
            auto_ack=True,
        )

        subscriber._nc = MagicMock()
        subscriber._connected = True

        await subscriber._message_handler(mock_msg, subscription)

        assert len(received_events) == 1

    @pytest.mark.asyncio
    async def test_message_handler_error(self, subscriber, sample_event_data):
        """Test message handling with handler error."""

        async def handler(event):
            raise ValueError("Handler error")

        mock_msg = MagicMock()
        mock_msg.subject = "test.subject"
        mock_msg.data = json.dumps(sample_event_data).encode("utf-8")
        mock_msg.headers = None
        mock_msg.nak = AsyncMock()

        subscription = Subscription(
            subject="test.subject",
            handler=handler,
            event_class=SampleEvent,
            auto_ack=True,
        )

        subscriber._nc = MagicMock()
        subscriber._connected = True
        subscriber.config.enable_dlq = False
        subscriber.config.enable_error_retry = False

        await subscriber._message_handler(mock_msg, subscription)

        assert subscriber._error_count == 1


# ─────────────────────────────────────────────────────────────────────────────
# EventSubscriber Retry Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventSubscriberRetry:
    """Tests for retry functionality."""

    @pytest.mark.asyncio
    async def test_retry_max_exceeded(self, subscriber, sample_event_data):
        """Test retry when max attempts exceeded."""
        mock_msg = MagicMock()
        mock_msg.subject = "test.subject"
        mock_msg.data = json.dumps(sample_event_data).encode("utf-8")
        mock_msg.nak = AsyncMock()

        subscriber.config.max_error_retries = 2

        async def handler(event):
            pass

        subscription = Subscription(
            subject="test.subject", handler=handler, event_class=SampleEvent
        )

        # Attempt beyond max
        await subscriber._retry_message(mock_msg, subscription, attempt=3)

        mock_msg.nak.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# EventSubscriber Context Manager Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventSubscriberContextManager:
    """Tests for context manager support."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self, subscriber_config):
        """Test async context manager entry and exit."""
        subscriber = EventSubscriber(config=subscriber_config)

        with patch("shared.events.subscriber._nats_available", True):
            with patch("shared.events.subscriber.nats") as mock_nats:
                mock_nc = AsyncMock()
                mock_nats.connect = AsyncMock(return_value=mock_nc)

                async with subscriber as s:
                    assert s.is_connected is True

                mock_nc.drain.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# Singleton Instance Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSingletonSubscriber:
    """Tests for singleton subscriber instance."""

    @pytest.mark.asyncio
    async def test_get_subscriber_creates_instance(self):
        """Test that get_subscriber creates a new instance."""
        with patch("shared.events.subscriber._subscriber_instance", None):
            with patch("shared.events.subscriber._nats_available", True):
                with patch("shared.events.subscriber.nats") as mock_nats:
                    mock_nc = AsyncMock()
                    mock_nats.connect = AsyncMock(return_value=mock_nc)

                    subscriber = await get_subscriber(
                        service_name="test", service_version="1.0"
                    )

                    assert subscriber is not None

    @pytest.mark.asyncio
    async def test_close_subscriber(self):
        """Test closing the singleton subscriber."""
        mock_subscriber = AsyncMock()

        with patch("shared.events.subscriber._subscriber_instance", mock_subscriber):
            await close_subscriber()
            mock_subscriber.close.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# Callback Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventSubscriberCallbacks:
    """Tests for NATS callbacks."""

    @pytest.mark.asyncio
    async def test_error_callback(self, subscriber):
        """Test error callback increments error count."""
        await subscriber._error_callback(Exception("Test error"))

        assert subscriber._error_count == 1

    @pytest.mark.asyncio
    async def test_disconnected_callback(self, subscriber):
        """Test disconnected callback updates state."""
        subscriber._connected = True

        await subscriber._disconnected_callback()

        assert subscriber._connected is False

    @pytest.mark.asyncio
    async def test_reconnected_callback(self, subscriber):
        """Test reconnected callback updates state."""
        subscriber._connected = False

        await subscriber._reconnected_callback()

        assert subscriber._connected is True

    @pytest.mark.asyncio
    async def test_closed_callback(self, subscriber):
        """Test closed callback updates state."""
        subscriber._connected = True

        await subscriber._closed_callback()

        assert subscriber._connected is False
