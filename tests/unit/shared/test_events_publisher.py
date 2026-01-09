"""
اختبارات ناشر الأحداث NATS
NATS Event Publisher Tests

Tests for the SAHOOL platform event publisher module.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from uuid import uuid4

# Import the module under test
from shared.events.publisher import (
    EventPublisher,
    PublisherConfig,
    get_publisher,
    close_publisher,
    publish_event,
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
def publisher_config():
    """Create a test publisher configuration."""
    return PublisherConfig(
        servers=["nats://localhost:4222"],
        name="test-publisher",
        enable_jetstream=False,
        enable_retry=False,
        max_retry_attempts=2,
        retry_delay=0.1,
        default_timeout=1.0,
    )


@pytest.fixture
def sample_event():
    """Create a sample event for testing."""
    return SampleEvent(
        field_id="field-123",
        field_name="Test Field",
        action="created",
        tenant_id="tenant-001",
        source_service="test-service",
    )


@pytest.fixture
def publisher(publisher_config):
    """Create a publisher instance for testing."""
    return EventPublisher(
        config=publisher_config,
        service_name="test-service",
        service_version="1.0.0",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PublisherConfig Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestPublisherConfig:
    """Tests for PublisherConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = PublisherConfig()

        assert config.reconnect_time_wait == 2
        assert config.max_reconnect_attempts == 60
        assert config.connect_timeout == 10
        assert config.enable_jetstream is True
        assert config.default_timeout == 5.0
        assert config.enable_retry is True
        assert config.max_retry_attempts == 3
        assert config.retry_delay == 0.5

    def test_custom_config(self):
        """Test custom configuration values."""
        config = PublisherConfig(
            servers=["nats://custom:4222"],
            name="custom-publisher",
            enable_jetstream=False,
            max_retry_attempts=5,
        )

        assert config.servers == ["nats://custom:4222"]
        assert config.name == "custom-publisher"
        assert config.enable_jetstream is False
        assert config.max_retry_attempts == 5

    def test_config_from_env(self, monkeypatch):
        """Test configuration from environment variables."""
        monkeypatch.setenv("NATS_URL", "nats://env-server:4222")
        monkeypatch.setenv("SERVICE_NAME", "env-service")

        config = PublisherConfig()

        assert "nats://env-server:4222" in config.servers
        assert config.name == "env-service"


# ─────────────────────────────────────────────────────────────────────────────
# EventPublisher Initialization Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventPublisherInit:
    """Tests for EventPublisher initialization."""

    def test_init_with_defaults(self):
        """Test publisher initialization with defaults."""
        publisher = EventPublisher()

        assert publisher.config is not None
        assert publisher.service_name is not None
        assert publisher._connected is False
        assert publisher._nc is None
        assert publisher._js is None

    def test_init_with_config(self, publisher_config):
        """Test publisher initialization with custom config."""
        publisher = EventPublisher(
            config=publisher_config,
            service_name="my-service",
            service_version="2.0.0",
        )

        assert publisher.config == publisher_config
        assert publisher.service_name == "my-service"
        assert publisher.service_version == "2.0.0"

    def test_is_connected_false_initially(self, publisher):
        """Test that publisher is not connected initially."""
        assert publisher.is_connected is False

    def test_stats_initial_values(self, publisher):
        """Test initial statistics values."""
        stats = publisher.stats

        assert stats["connected"] is False
        assert stats["publish_count"] == 0
        assert stats["error_count"] == 0
        assert stats["service_name"] == "test-service"
        assert stats["service_version"] == "1.0.0"


# ─────────────────────────────────────────────────────────────────────────────
# EventPublisher Connection Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventPublisherConnection:
    """Tests for EventPublisher connection management."""

    @pytest.mark.asyncio
    async def test_connect_without_nats_library(self, publisher):
        """Test connection attempt when NATS library is unavailable."""
        with patch("shared.events.publisher._nats_available", False):
            result = await publisher.connect()
            assert result is False
            assert publisher.is_connected is False

    @pytest.mark.asyncio
    async def test_connect_already_connected(self, publisher):
        """Test connection when already connected."""
        publisher._connected = True
        publisher._nc = MagicMock()

        result = await publisher.connect()

        assert result is True

    @pytest.mark.asyncio
    async def test_connect_success(self, publisher):
        """Test successful connection to NATS."""
        mock_nc = AsyncMock()

        with patch("shared.events.publisher._nats_available", True):
            with patch("shared.events.publisher.nats") as mock_nats:
                mock_nats.connect = AsyncMock(return_value=mock_nc)

                result = await publisher.connect()

                assert result is True
                assert publisher.is_connected is True

    @pytest.mark.asyncio
    async def test_connect_failure(self, publisher):
        """Test connection failure."""
        with patch("shared.events.publisher._nats_available", True):
            with patch("shared.events.publisher.nats") as mock_nats:
                mock_nats.connect = AsyncMock(side_effect=Exception("Connection failed"))

                result = await publisher.connect()

                assert result is False
                assert publisher.is_connected is False

    @pytest.mark.asyncio
    async def test_close_connection(self, publisher):
        """Test closing the NATS connection."""
        mock_nc = AsyncMock()
        publisher._nc = mock_nc
        publisher._connected = True

        await publisher.close()

        mock_nc.drain.assert_called_once()
        mock_nc.close.assert_called_once()
        assert publisher._nc is None
        assert publisher._connected is False


# ─────────────────────────────────────────────────────────────────────────────
# EventPublisher Publishing Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventPublisherPublish:
    """Tests for EventPublisher publishing functionality."""

    @pytest.mark.asyncio
    async def test_publish_event_not_connected(self, publisher, sample_event):
        """Test publishing when not connected."""
        result = await publisher.publish_event("test.subject", sample_event)

        assert result is False

    @pytest.mark.asyncio
    async def test_publish_event_success(self, publisher, sample_event):
        """Test successful event publishing."""
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock()
        publisher._nc = mock_nc
        publisher._connected = True

        result = await publisher.publish_event("test.subject", sample_event)

        assert result is True
        assert publisher._publish_count == 1
        mock_nc.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_event_sets_source_service(self, publisher, sample_event):
        """Test that source service is set on event."""
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock()
        publisher._nc = mock_nc
        publisher._connected = True
        sample_event.source_service = None

        await publisher.publish_event("test.subject", sample_event)

        assert sample_event.source_service == "test-service"

    @pytest.mark.asyncio
    async def test_publish_event_validation_failure(self, publisher):
        """Test publishing with invalid event data."""
        mock_nc = AsyncMock()
        publisher._nc = mock_nc
        publisher._connected = True

        # Create an event that will fail validation
        invalid_event = MagicMock(spec=BaseEvent)
        invalid_event.source_service = "test"
        invalid_event.model_validate = MagicMock(side_effect=ValueError("Invalid"))
        invalid_event.model_dump = MagicMock(return_value={})

        result = await publisher.publish_event("test.subject", invalid_event)

        assert result is False
        assert publisher._error_count == 1

    @pytest.mark.asyncio
    async def test_publish_events_batch(self, publisher, sample_event):
        """Test batch event publishing."""
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock()
        publisher._nc = mock_nc
        publisher._connected = True

        events = [
            ("test.subject.1", sample_event),
            ("test.subject.2", sample_event),
            ("test.subject.3", sample_event),
        ]

        count = await publisher.publish_events(events)

        assert count == 3
        assert publisher._publish_count == 3

    @pytest.mark.asyncio
    async def test_publish_json_success(self, publisher):
        """Test publishing raw JSON data."""
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock()
        publisher._nc = mock_nc
        publisher._connected = True

        data = {"field_id": "123", "action": "update"}

        result = await publisher.publish_json("test.subject", data)

        assert result is True
        assert publisher._publish_count == 1

    @pytest.mark.asyncio
    async def test_publish_json_not_connected(self, publisher):
        """Test publishing JSON when not connected."""
        data = {"field_id": "123"}

        result = await publisher.publish_json("test.subject", data)

        assert result is False


# ─────────────────────────────────────────────────────────────────────────────
# EventPublisher JetStream Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventPublisherJetStream:
    """Tests for JetStream publishing functionality."""

    @pytest.mark.asyncio
    async def test_publish_with_jetstream(self, sample_event):
        """Test publishing with JetStream enabled."""
        config = PublisherConfig(enable_jetstream=True)
        publisher = EventPublisher(config=config)

        mock_nc = AsyncMock()
        mock_js = AsyncMock()
        mock_ack = MagicMock()
        mock_ack.stream = "test-stream"
        mock_ack.seq = 1
        mock_js.publish = AsyncMock(return_value=mock_ack)

        publisher._nc = mock_nc
        publisher._js = mock_js
        publisher._connected = True

        result = await publisher.publish_event("test.subject", sample_event)

        assert result is True
        mock_js.publish.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# EventPublisher Retry Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventPublisherRetry:
    """Tests for retry functionality."""

    @pytest.mark.asyncio
    async def test_retry_on_failure(self, sample_event):
        """Test retry logic on publish failure."""
        config = PublisherConfig(
            enable_jetstream=False,
            enable_retry=True,
            max_retry_attempts=2,
            retry_delay=0.01,
        )
        publisher = EventPublisher(config=config)

        mock_nc = AsyncMock()
        # First call fails, second succeeds
        mock_nc.publish = AsyncMock(side_effect=[Exception("Failed"), None])

        publisher._nc = mock_nc
        publisher._connected = True

        result = await publisher.publish_event("test.subject", sample_event)

        # Should succeed after retry
        assert result is True


# ─────────────────────────────────────────────────────────────────────────────
# EventPublisher Context Manager Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventPublisherContextManager:
    """Tests for context manager support."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self, publisher_config):
        """Test async context manager entry and exit."""
        publisher = EventPublisher(config=publisher_config)

        with patch("shared.events.publisher._nats_available", True):
            with patch("shared.events.publisher.nats") as mock_nats:
                mock_nc = AsyncMock()
                mock_nats.connect = AsyncMock(return_value=mock_nc)

                async with publisher as p:
                    assert p.is_connected is True

                mock_nc.drain.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# Singleton Instance Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSingletonPublisher:
    """Tests for singleton publisher instance."""

    @pytest.mark.asyncio
    async def test_get_publisher_creates_instance(self):
        """Test that get_publisher creates a new instance."""
        with patch("shared.events.publisher._publisher_instance", None):
            with patch("shared.events.publisher._nats_available", True):
                with patch("shared.events.publisher.nats") as mock_nats:
                    mock_nc = AsyncMock()
                    mock_nats.connect = AsyncMock(return_value=mock_nc)

                    publisher = await get_publisher(
                        service_name="test", service_version="1.0"
                    )

                    assert publisher is not None

    @pytest.mark.asyncio
    async def test_close_publisher(self):
        """Test closing the singleton publisher."""
        mock_publisher = AsyncMock()

        with patch("shared.events.publisher._publisher_instance", mock_publisher):
            await close_publisher()
            mock_publisher.close.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# Event Serialization Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventSerialization:
    """Tests for event serialization."""

    def test_serialize_event(self, publisher, sample_event):
        """Test event serialization to JSON bytes."""
        serialized = publisher._serialize_event(sample_event)

        assert isinstance(serialized, bytes)

        # Deserialize and verify
        data = json.loads(serialized.decode("utf-8"))
        assert data["field_id"] == "field-123"
        assert data["field_name"] == "Test Field"
        assert data["action"] == "created"

    def test_serialize_event_includes_metadata(self, publisher, sample_event):
        """Test that serialized event includes metadata."""
        serialized = publisher._serialize_event(sample_event)
        data = json.loads(serialized.decode("utf-8"))

        assert "event_id" in data
        assert "timestamp" in data
        assert "tenant_id" in data
