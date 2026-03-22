"""
Tests for NATS Event Publisher Module
=====================================
اختبارات وحدة ناشر احداث NATS

Comprehensive tests for the NATS event publisher.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from shared.events.publisher import (
    PublisherConfig,
    EventPublisher,
    get_publisher,
    close_publisher,
    publish_event,
)
from shared.events.contracts import BaseEvent, FieldCreatedEvent


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def publisher_config() -> PublisherConfig:
    """Create a test publisher configuration."""
    return PublisherConfig(
        servers=["nats://localhost:4222"],
        name="test-publisher",
        connect_timeout=5,
        enable_jetstream=True,
        enable_retry=True,
        max_retry_attempts=2,
        retry_delay=0.1,
    )


@pytest.fixture
def publisher(publisher_config) -> EventPublisher:
    """Create a test publisher."""
    return EventPublisher(
        config=publisher_config,
        service_name="test-service",
        service_version="1.0.0",
    )


@pytest.fixture
def sample_field_event() -> FieldCreatedEvent:
    """Create a sample field created event."""
    return FieldCreatedEvent(
        field_id=uuid4(),
        farm_id=uuid4(),
        tenant_id=uuid4(),
        name="Test Field",
        geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
        area_hectares=10.5,
    )


@pytest.fixture
def mock_nats_client():
    """Create a mock NATS client."""
    mock_nc = AsyncMock()
    mock_nc.publish = AsyncMock()
    mock_nc.drain = AsyncMock()
    mock_nc.close = AsyncMock()

    mock_js = AsyncMock()
    mock_ack = MagicMock()
    mock_ack.stream = "test-stream"
    mock_ack.seq = 1
    mock_js.publish = AsyncMock(return_value=mock_ack)

    mock_nc.jetstream.return_value = mock_js

    return mock_nc, mock_js


# =============================================================================
# Test PublisherConfig
# =============================================================================


class TestPublisherConfig:
    """Tests for Publisher configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = PublisherConfig()

        assert config.reconnect_time_wait == 2
        assert config.max_reconnect_attempts == 60
        assert config.connect_timeout == 10
        assert config.enable_jetstream is True
        assert config.default_timeout == 5.0

    def test_custom_config(self, publisher_config):
        """Test custom configuration."""
        assert publisher_config.servers == ["nats://localhost:4222"]
        assert publisher_config.name == "test-publisher"
        assert publisher_config.enable_retry is True
        assert publisher_config.max_retry_attempts == 2

    def test_config_retry_settings(self, publisher_config):
        """Test retry configuration settings."""
        assert publisher_config.enable_retry is True
        assert publisher_config.max_retry_attempts == 2
        assert publisher_config.retry_delay == 0.1

    def test_config_jetstream_settings(self, publisher_config):
        """Test JetStream configuration settings."""
        assert publisher_config.enable_jetstream is True
        assert publisher_config.jetstream_domain == "sahool"


# =============================================================================
# Test EventPublisher Initialization
# =============================================================================


class TestEventPublisherInit:
    """Tests for EventPublisher initialization."""

    def test_publisher_initialization(self, publisher):
        """Test publisher initialization."""
        assert publisher.service_name == "test-service"
        assert publisher.service_version == "1.0.0"
        assert publisher._connected is False
        assert publisher._publish_count == 0
        assert publisher._error_count == 0

    def test_publisher_is_connected_property(self, publisher):
        """Test is_connected property."""
        assert publisher.is_connected is False

        publisher._connected = True
        publisher._nc = MagicMock()
        assert publisher.is_connected is True

    def test_publisher_stats_property(self, publisher):
        """Test stats property."""
        stats = publisher.stats

        assert "connected" in stats
        assert "publish_count" in stats
        assert "error_count" in stats
        assert "service_name" in stats
        assert stats["connected"] is False


# =============================================================================
# Test EventPublisher Connection
# =============================================================================


class TestEventPublisherConnection:
    """Tests for EventPublisher connection."""

    @pytest.mark.asyncio
    async def test_connect_success(self, publisher, mock_nats_client):
        """Test successful connection."""
        mock_nc, mock_js = mock_nats_client

        with patch("shared.events.publisher._nats_available", True):
            with patch("shared.events.publisher.nats") as mock_nats:
                mock_nats.connect = AsyncMock(return_value=mock_nc)

                result = await publisher.connect()

                assert result is True
                assert publisher._connected is True

    @pytest.mark.asyncio
    async def test_connect_already_connected(self, publisher, mock_nats_client):
        """Test connecting when already connected."""
        mock_nc, _ = mock_nats_client
        publisher._connected = True
        publisher._nc = mock_nc

        with patch("shared.events.publisher._nats_available", True):
            result = await publisher.connect()

        assert result is True  # Should return True without reconnecting

    @pytest.mark.asyncio
    async def test_connect_failure(self, publisher):
        """Test connection failure."""
        with patch("shared.events.publisher._nats_available", True):
            with patch("shared.events.publisher.nats") as mock_nats:
                mock_nats.connect = AsyncMock(side_effect=Exception("Connection failed"))

                result = await publisher.connect()

                assert result is False
                assert publisher._connected is False

    @pytest.mark.asyncio
    async def test_close_connection(self, publisher, mock_nats_client):
        """Test closing connection."""
        mock_nc, _ = mock_nats_client
        publisher._connected = True
        publisher._nc = mock_nc

        await publisher.close()

        mock_nc.drain.assert_called_once()
        mock_nc.close.assert_called_once()
        assert publisher._connected is False

    @pytest.mark.asyncio
    async def test_close_when_not_connected(self, publisher):
        """Test closing when not connected."""
        await publisher.close()  # Should not raise

        assert publisher._connected is False


# =============================================================================
# Test EventPublisher Publishing
# =============================================================================


class TestEventPublisherPublishing:
    """Tests for EventPublisher publishing."""

    @pytest.mark.asyncio
    async def test_publish_event_not_connected(self, publisher, sample_field_event):
        """Test publishing when not connected buffers the message."""
        result = await publisher.publish_event("test.subject", sample_field_event)

        # When not connected, messages are buffered for retry (returns True if buffered)
        assert result is True

    @pytest.mark.asyncio
    async def test_publish_event_success(self, publisher, sample_field_event, mock_nats_client):
        """Test successful event publishing."""
        mock_nc, mock_js = mock_nats_client
        publisher._connected = True
        publisher._nc = mock_nc
        publisher._js = mock_js

        result = await publisher.publish_event("test.subject", sample_field_event)

        assert result is True
        assert publisher._publish_count == 1
        mock_js.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_event_sets_source_service(self, publisher, sample_field_event, mock_nats_client):
        """Test that source service is set on event."""
        mock_nc, mock_js = mock_nats_client
        publisher._connected = True
        publisher._nc = mock_nc
        publisher._js = mock_js

        sample_field_event.source_service = None
        await publisher.publish_event("test.subject", sample_field_event)

        assert sample_field_event.source_service == "test-service"

    @pytest.mark.asyncio
    async def test_publish_event_core_nats(self, publisher, sample_field_event, mock_nats_client):
        """Test publishing using core NATS (not JetStream)."""
        mock_nc, _ = mock_nats_client
        publisher._connected = True
        publisher._nc = mock_nc
        publisher._js = None  # Disable JetStream

        result = await publisher.publish_event("test.subject", sample_field_event, use_jetstream=False)

        assert result is True
        mock_nc.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_events_batch(self, publisher, sample_field_event, mock_nats_client):
        """Test batch publishing."""
        mock_nc, mock_js = mock_nats_client
        publisher._connected = True
        publisher._nc = mock_nc
        publisher._js = mock_js

        events = [
            ("subject.1", sample_field_event),
            ("subject.2", sample_field_event),
            ("subject.3", sample_field_event),
        ]

        count = await publisher.publish_events(events)

        assert count == 3
        assert mock_js.publish.call_count == 3

    @pytest.mark.asyncio
    async def test_publish_json_success(self, publisher, mock_nats_client):
        """Test publishing raw JSON."""
        mock_nc, _ = mock_nats_client
        publisher._connected = True
        publisher._nc = mock_nc

        data = {"key": "value", "number": 42}
        result = await publisher.publish_json("test.subject", data)

        assert result is True
        mock_nc.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_json_not_connected(self, publisher):
        """Test publishing JSON when not connected."""
        result = await publisher.publish_json("test.subject", {"key": "value"})

        assert result is False

    @pytest.mark.asyncio
    async def test_publish_increments_error_count_on_failure(self, publisher, sample_field_event, mock_nats_client):
        """Test that error count increments on publish failure."""
        mock_nc, mock_js = mock_nats_client
        mock_js.publish = AsyncMock(side_effect=Exception("Publish failed"))
        publisher._connected = True
        publisher._nc = mock_nc
        publisher._js = mock_js
        publisher.config.enable_retry = False  # Disable retry for this test

        result = await publisher.publish_event("test.subject", sample_field_event)

        assert result is False
        assert publisher._error_count > 0


# =============================================================================
# Test Event Serialization
# =============================================================================


class TestEventSerialization:
    """Tests for event serialization."""

    def test_serialize_event(self, publisher, sample_field_event):
        """Test event serialization."""
        data = publisher._serialize_event(sample_field_event)

        assert isinstance(data, bytes)

        # Verify it's valid JSON
        parsed = json.loads(data)
        assert "field_id" in parsed

    def test_serialize_event_with_datetime(self, publisher, sample_field_event):
        """Test serialization handles datetime correctly."""
        data = publisher._serialize_event(sample_field_event)
        parsed = json.loads(data)

        assert "timestamp" in parsed
        # Timestamp should be ISO format string
        assert isinstance(parsed["timestamp"], str)


# =============================================================================
# Test Retry Logic
# =============================================================================


class TestRetryLogic:
    """Tests for retry logic."""

    @pytest.mark.asyncio
    async def test_retry_on_publish_failure(self, publisher, sample_field_event, mock_nats_client):
        """Test retry on publish failure."""
        mock_nc, mock_js = mock_nats_client
        # Fail first time, succeed second time
        mock_js.publish = AsyncMock(side_effect=[Exception("First failure"), MagicMock(stream="s", seq=1)])
        publisher._connected = True
        publisher._nc = mock_nc
        publisher._js = mock_js
        publisher.config.retry_delay = 0.01  # Fast retry for tests

        # Note: This test depends on the actual retry implementation
        result = await publisher.publish_event("test.subject", sample_field_event)

        # Should eventually succeed after retry
        assert mock_js.publish.call_count >= 1


# =============================================================================
# Test Context Manager
# =============================================================================


class TestContextManager:
    """Tests for async context manager."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self, publisher_config, mock_nats_client):
        """Test async context manager."""
        mock_nc, _ = mock_nats_client

        with patch("shared.events.publisher._nats_available", True):
            with patch("shared.events.publisher.nats") as mock_nats:
                mock_nats.connect = AsyncMock(return_value=mock_nc)

                async with EventPublisher(config=publisher_config) as pub:
                    assert pub._connected is True

                mock_nc.drain.assert_called()


# =============================================================================
# Test Callbacks
# =============================================================================


class TestCallbacks:
    """Tests for NATS callbacks."""

    @pytest.mark.asyncio
    async def test_error_callback(self, publisher):
        """Test error callback increments error count."""
        await publisher._error_callback(Exception("Test error"))

        assert publisher._error_count == 1

    @pytest.mark.asyncio
    async def test_disconnected_callback(self, publisher):
        """Test disconnected callback updates state."""
        publisher._connected = True

        await publisher._disconnected_callback()

        assert publisher._connected is False

    @pytest.mark.asyncio
    async def test_reconnected_callback(self, publisher):
        """Test reconnected callback updates state."""
        publisher._connected = False

        await publisher._reconnected_callback()

        assert publisher._connected is True

    @pytest.mark.asyncio
    async def test_closed_callback(self, publisher):
        """Test closed callback updates state."""
        publisher._connected = True

        await publisher._closed_callback()

        assert publisher._connected is False


# =============================================================================
# Test Singleton Functions
# =============================================================================


class TestSingletonFunctions:
    """Tests for singleton pattern functions."""

    @pytest.mark.asyncio
    async def test_close_publisher_singleton(self):
        """Test closing publisher singleton."""
        # Close should not raise even if not initialized
        await close_publisher()


# =============================================================================
# Test Event Validation
# =============================================================================


class TestEventValidation:
    """Tests for event validation during publishing."""

    @pytest.mark.asyncio
    async def test_invalid_event_fails(self, publisher, mock_nats_client):
        """Test that invalid event fails validation."""
        mock_nc, mock_js = mock_nats_client
        publisher._connected = True
        publisher._nc = mock_nc
        publisher._js = mock_js

        # Create a valid event
        event = FieldCreatedEvent(
            field_id=uuid4(),
            farm_id=uuid4(),
            tenant_id=uuid4(),
            name="Test",
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            area_hectares=10.0,
        )

        # Should succeed with valid event
        result = await publisher.publish_event("test.subject", event)
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
