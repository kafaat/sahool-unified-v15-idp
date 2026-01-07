"""
Unit Tests for Shared Event System
Tests event publishing, subscribing, and event contracts
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.events.contracts import BaseEvent
from shared.events.models import EventMetadata, EventPriority, EventStatus
from shared.events.publisher import EventPublisher, PublisherConfig


# ═══════════════════════════════════════════════════════════════════════════
# Mock Event Classes
# ═══════════════════════════════════════════════════════════════════════════


class TestEvent(BaseEvent):
    """Test event for unit tests"""

    test_field: str
    test_number: int


class FieldCreatedEvent(BaseEvent):
    """Field created event"""

    field_id: str
    farm_id: str
    name: str
    area_hectares: float


class CropPlantedEvent(BaseEvent):
    """Crop planted event"""

    field_id: str
    crop_type: str
    planting_date: str
    expected_harvest_date: str


# ═══════════════════════════════════════════════════════════════════════════
# Publisher Config Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestPublisherConfig:
    """Test PublisherConfig"""

    def test_default_config(self):
        """Test default publisher configuration"""
        config = PublisherConfig()
        assert config.servers == ["nats://localhost:4222"]
        assert config.enable_jetstream is True
        assert config.enable_retry is True
        assert config.max_retry_attempts == 3

    @patch.dict("os.environ", {"NATS_URL": "nats://test-server:4222", "SERVICE_NAME": "test-service"})
    def test_config_from_env(self):
        """Test configuration from environment variables"""
        config = PublisherConfig()
        assert "nats://test-server:4222" in config.servers
        assert config.name == "test-service"

    def test_custom_config(self):
        """Test custom configuration"""
        config = PublisherConfig(
            servers=["nats://server1:4222", "nats://server2:4222"],
            name="custom-publisher",
            enable_jetstream=False,
            max_retry_attempts=5,
        )
        assert len(config.servers) == 2
        assert config.name == "custom-publisher"
        assert config.enable_jetstream is False
        assert config.max_retry_attempts == 5


# ═══════════════════════════════════════════════════════════════════════════
# Base Event Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestBaseEvent:
    """Test BaseEvent model"""

    def test_create_base_event(self):
        """Test creating base event"""
        event = TestEvent(test_field="value", test_number=42)

        assert event.test_field == "value"
        assert event.test_number == 42
        assert event.event_id is not None
        assert isinstance(event.timestamp, datetime)
        assert event.event_type == "TestEvent"

    def test_event_with_metadata(self):
        """Test event with custom metadata"""
        event = TestEvent(
            test_field="value",
            test_number=42,
            source_service="test-service",
            correlation_id="corr-123",
        )

        assert event.source_service == "test-service"
        assert event.correlation_id == "corr-123"

    def test_event_serialization(self):
        """Test event can be serialized to JSON"""
        event = TestEvent(test_field="value", test_number=42)
        json_str = event.model_dump_json()

        assert isinstance(json_str, str)
        assert "test_field" in json_str
        assert "event_id" in json_str

    def test_event_deserialization(self):
        """Test event can be deserialized from JSON"""
        event_data = {
            "event_id": "test-id-123",
            "timestamp": datetime.now().isoformat(),
            "event_type": "TestEvent",
            "test_field": "value",
            "test_number": 42,
        }

        event = TestEvent(**event_data)
        assert event.test_field == "value"
        assert event.event_id == "test-id-123"


# ═══════════════════════════════════════════════════════════════════════════
# Event Publisher Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestEventPublisher:
    """Test EventPublisher class"""

    @pytest.fixture
    def config(self):
        """Create test publisher config"""
        return PublisherConfig(
            servers=["nats://localhost:4222"], name="test-publisher", enable_jetstream=True
        )

    @pytest.fixture
    def publisher(self, config):
        """Create EventPublisher instance"""
        return EventPublisher(config=config, service_name="test-service", service_version="1.0.0")

    def test_publisher_creation(self, publisher):
        """Test creating publisher"""
        assert publisher.service_name == "test-service"
        assert publisher.service_version == "1.0.0"
        assert publisher.is_connected is False

    def test_publisher_stats(self, publisher):
        """Test getting publisher stats"""
        stats = publisher.stats

        assert "connected" in stats
        assert "publish_count" in stats
        assert "error_count" in stats
        assert stats["service_name"] == "test-service"

    @pytest.mark.asyncio
    @patch("shared.events.publisher._nats_available", True)
    @patch("shared.events.publisher.nats")
    async def test_publisher_connect_success(self, mock_nats, publisher):
        """Test successful connection to NATS"""
        mock_nc = AsyncMock()
        mock_nc.jetstream = MagicMock()
        mock_nats.connect = AsyncMock(return_value=mock_nc)

        result = await publisher.connect()

        assert result is True
        assert publisher.is_connected is True
        mock_nats.connect.assert_called_once()

    @pytest.mark.asyncio
    @patch("shared.events.publisher._nats_available", False)
    async def test_publisher_connect_no_nats(self, publisher):
        """Test connection fails when NATS not available"""
        result = await publisher.connect()

        assert result is False
        assert publisher.is_connected is False

    @pytest.mark.asyncio
    @patch("shared.events.publisher._nats_available", True)
    @patch("shared.events.publisher.nats")
    async def test_publisher_connect_failure(self, mock_nats, publisher):
        """Test connection failure"""
        mock_nats.connect = AsyncMock(side_effect=Exception("Connection failed"))

        result = await publisher.connect()

        assert result is False
        assert publisher.is_connected is False

    @pytest.mark.asyncio
    @patch("shared.events.publisher._nats_available", True)
    @patch("shared.events.publisher.nats")
    async def test_publisher_close(self, mock_nats, publisher):
        """Test closing publisher connection"""
        # Setup mock connection
        mock_nc = AsyncMock()
        mock_nc.jetstream = MagicMock()
        mock_nats.connect = AsyncMock(return_value=mock_nc)

        await publisher.connect()
        await publisher.close()

        assert publisher.is_connected is False
        mock_nc.drain.assert_called_once()
        mock_nc.close.assert_called_once()

    @pytest.mark.asyncio
    @patch("shared.events.publisher._nats_available", True)
    @patch("shared.events.publisher.nats")
    async def test_publish_event_success(self, mock_nats, publisher):
        """Test publishing event successfully"""
        # Setup mock connection
        mock_nc = AsyncMock()
        mock_js = AsyncMock()
        mock_nc.jetstream = MagicMock(return_value=mock_js)
        mock_js.publish = AsyncMock()
        mock_nats.connect = AsyncMock(return_value=mock_nc)

        await publisher.connect()
        publisher._js = mock_js

        event = TestEvent(test_field="value", test_number=42)
        result = await publisher.publish_event("test.subject", event)

        assert result is True
        assert publisher.stats["publish_count"] == 1

    @pytest.mark.asyncio
    async def test_publish_event_not_connected(self, publisher):
        """Test publishing when not connected"""
        event = TestEvent(test_field="value", test_number=42)
        result = await publisher.publish_event("test.subject", event)

        assert result is False

    @pytest.mark.asyncio
    @patch("shared.events.publisher._nats_available", True)
    @patch("shared.events.publisher.nats")
    async def test_publish_event_validation_failure(self, mock_nats, publisher):
        """Test publishing event with validation error"""
        # Setup mock connection
        mock_nc = AsyncMock()
        mock_nc.jetstream = MagicMock()
        mock_nats.connect = AsyncMock(return_value=mock_nc)

        await publisher.connect()

        # Create invalid event (missing required field)
        with pytest.raises(Exception):
            event = TestEvent(test_field="value")  # Missing test_number

    @pytest.mark.asyncio
    @patch("shared.events.publisher._nats_available", True)
    @patch("shared.events.publisher.nats")
    async def test_publish_multiple_events(self, mock_nats, publisher):
        """Test publishing multiple events"""
        # Setup mock connection
        mock_nc = AsyncMock()
        mock_js = AsyncMock()
        mock_nc.jetstream = MagicMock(return_value=mock_js)
        mock_js.publish = AsyncMock()
        mock_nats.connect = AsyncMock(return_value=mock_nc)

        await publisher.connect()
        publisher._js = mock_js

        events = [
            ("subject1", TestEvent(test_field="value1", test_number=1)),
            ("subject2", TestEvent(test_field="value2", test_number=2)),
            ("subject3", TestEvent(test_field="value3", test_number=3)),
        ]

        success_count = await publisher.publish_events(events)

        assert success_count == 3
        assert publisher.stats["publish_count"] == 3

    @pytest.mark.asyncio
    @patch("shared.events.publisher._nats_available", True)
    @patch("shared.events.publisher.nats")
    async def test_publish_json(self, mock_nats, publisher):
        """Test publishing raw JSON data"""
        # Setup mock connection
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock()
        mock_nats.connect = AsyncMock(return_value=mock_nc)

        await publisher.connect()

        data = {"key": "value", "number": 42}
        result = await publisher.publish_json("test.subject", data)

        assert result is True
        mock_nc.publish.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════
# Context Manager Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestPublisherContextManager:
    """Test EventPublisher as context manager"""

    @pytest.mark.asyncio
    @patch("shared.events.publisher._nats_available", True)
    @patch("shared.events.publisher.nats")
    async def test_context_manager(self, mock_nats):
        """Test using publisher as async context manager"""
        mock_nc = AsyncMock()
        mock_nc.jetstream = MagicMock()
        mock_nats.connect = AsyncMock(return_value=mock_nc)

        config = PublisherConfig(servers=["nats://localhost:4222"])

        async with EventPublisher(config=config) as publisher:
            assert publisher.is_connected is True

        # Should be closed after exiting context
        assert publisher.is_connected is False


# ═══════════════════════════════════════════════════════════════════════════
# Event Metadata Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestEventMetadata:
    """Test EventMetadata model"""

    def test_event_priority_enum(self):
        """Test EventPriority enum"""
        assert EventPriority.LOW.value == "low"
        assert EventPriority.MEDIUM.value == "medium"
        assert EventPriority.HIGH.value == "high"
        assert EventPriority.CRITICAL.value == "critical"

    def test_event_status_enum(self):
        """Test EventStatus enum"""
        assert EventStatus.PENDING.value == "pending"
        assert EventStatus.PROCESSING.value == "processing"
        assert EventStatus.COMPLETED.value == "completed"
        assert EventStatus.FAILED.value == "failed"


# ═══════════════════════════════════════════════════════════════════════════
# Domain Event Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestDomainEvents:
    """Test domain-specific events"""

    def test_field_created_event(self):
        """Test FieldCreatedEvent"""
        event = FieldCreatedEvent(
            field_id="field-123", farm_id="farm-456", name="North Field", area_hectares=50.5
        )

        assert event.field_id == "field-123"
        assert event.farm_id == "farm-456"
        assert event.name == "North Field"
        assert event.area_hectares == 50.5
        assert event.event_type == "FieldCreatedEvent"

    def test_crop_planted_event(self):
        """Test CropPlantedEvent"""
        event = CropPlantedEvent(
            field_id="field-123",
            crop_type="wheat",
            planting_date="2024-01-01",
            expected_harvest_date="2024-06-01",
        )

        assert event.field_id == "field-123"
        assert event.crop_type == "wheat"
        assert event.planting_date == "2024-01-01"


# ═══════════════════════════════════════════════════════════════════════════
# Event Serialization Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestEventSerialization:
    """Test event serialization and deserialization"""

    def test_serialize_event_to_json(self):
        """Test serializing event to JSON"""
        event = TestEvent(test_field="value", test_number=42, source_service="test-service")

        json_data = event.model_dump_json()

        assert isinstance(json_data, str)
        assert "test_field" in json_data
        assert "test_number" in json_data
        assert "source_service" in json_data

    def test_deserialize_event_from_json(self):
        """Test deserializing event from JSON"""
        json_data = {
            "event_id": "evt-123",
            "timestamp": datetime.now().isoformat(),
            "event_type": "TestEvent",
            "source_service": "test-service",
            "test_field": "value",
            "test_number": 42,
        }

        event = TestEvent(**json_data)

        assert event.event_id == "evt-123"
        assert event.test_field == "value"
        assert event.test_number == 42

    def test_event_round_trip(self):
        """Test serializing and deserializing event"""
        original = TestEvent(test_field="value", test_number=42)

        # Serialize
        json_str = original.model_dump_json()

        # Deserialize
        import json

        data = json.loads(json_str)
        restored = TestEvent(**data)

        assert restored.event_id == original.event_id
        assert restored.test_field == original.test_field
        assert restored.test_number == original.test_number


# ═══════════════════════════════════════════════════════════════════════════
# Retry Logic Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestRetryLogic:
    """Test event publishing retry logic"""

    @pytest.mark.asyncio
    @patch("shared.events.publisher._nats_available", True)
    @patch("shared.events.publisher.nats")
    async def test_retry_on_failure(self, mock_nats):
        """Test retry logic when publishing fails"""
        mock_nc = AsyncMock()
        mock_js = AsyncMock()
        mock_nc.jetstream = MagicMock(return_value=mock_js)

        # First call fails, second succeeds
        mock_js.publish = AsyncMock(
            side_effect=[Exception("Network error"), AsyncMock(stream="test", seq=1)]
        )

        mock_nats.connect = AsyncMock(return_value=mock_nc)

        config = PublisherConfig(enable_retry=True, max_retry_attempts=3, retry_delay=0.1)
        publisher = EventPublisher(config=config)

        await publisher.connect()
        publisher._js = mock_js

        event = TestEvent(test_field="value", test_number=42)
        result = await publisher.publish_event("test.subject", event, use_jetstream=True)

        assert result is True
        assert mock_js.publish.call_count == 2  # Initial + 1 retry

    @pytest.mark.asyncio
    @patch("shared.events.publisher._nats_available", True)
    @patch("shared.events.publisher.nats")
    async def test_retry_exhausted(self, mock_nats):
        """Test when all retry attempts are exhausted"""
        mock_nc = AsyncMock()
        mock_js = AsyncMock()
        mock_nc.jetstream = MagicMock(return_value=mock_js)

        # Always fail
        mock_js.publish = AsyncMock(side_effect=Exception("Network error"))

        mock_nats.connect = AsyncMock(return_value=mock_nc)

        config = PublisherConfig(enable_retry=True, max_retry_attempts=2, retry_delay=0.1)
        publisher = EventPublisher(config=config)

        await publisher.connect()
        publisher._js = mock_js

        event = TestEvent(test_field="value", test_number=42)
        result = await publisher.publish_event("test.subject", event, use_jetstream=True)

        assert result is False
        assert publisher.stats["error_count"] > 0


# ═══════════════════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestEventSystemIntegration:
    """Test integrated event system scenarios"""

    @pytest.mark.asyncio
    @patch("shared.events.publisher._nats_available", True)
    @patch("shared.events.publisher.nats")
    async def test_publish_multiple_event_types(self, mock_nats):
        """Test publishing different event types"""
        mock_nc = AsyncMock()
        mock_js = AsyncMock()
        mock_nc.jetstream = MagicMock(return_value=mock_js)
        mock_js.publish = AsyncMock()
        mock_nats.connect = AsyncMock(return_value=mock_nc)

        publisher = EventPublisher()
        await publisher.connect()
        publisher._js = mock_js

        # Publish different event types
        field_event = FieldCreatedEvent(
            field_id="field-1", farm_id="farm-1", name="Field 1", area_hectares=50.0
        )

        crop_event = CropPlantedEvent(
            field_id="field-1",
            crop_type="wheat",
            planting_date="2024-01-01",
            expected_harvest_date="2024-06-01",
        )

        result1 = await publisher.publish_event("sahool.field.created", field_event)
        result2 = await publisher.publish_event("sahool.crop.planted", crop_event)

        assert result1 is True
        assert result2 is True
        assert publisher.stats["publish_count"] == 2

    @pytest.mark.asyncio
    @patch("shared.events.publisher._nats_available", True)
    @patch("shared.events.publisher.nats")
    async def test_event_correlation(self, mock_nats):
        """Test event correlation with correlation IDs"""
        mock_nc = AsyncMock()
        mock_js = AsyncMock()
        mock_nc.jetstream = MagicMock(return_value=mock_js)
        mock_js.publish = AsyncMock()
        mock_nats.connect = AsyncMock(return_value=mock_nc)

        publisher = EventPublisher()
        await publisher.connect()
        publisher._js = mock_js

        correlation_id = "corr-123"

        # Create related events with same correlation ID
        event1 = FieldCreatedEvent(
            field_id="field-1",
            farm_id="farm-1",
            name="Field 1",
            area_hectares=50.0,
            correlation_id=correlation_id,
        )

        event2 = CropPlantedEvent(
            field_id="field-1",
            crop_type="wheat",
            planting_date="2024-01-01",
            expected_harvest_date="2024-06-01",
            correlation_id=correlation_id,
        )

        await publisher.publish_event("sahool.field.created", event1)
        await publisher.publish_event("sahool.crop.planted", event2)

        # Both events should have same correlation ID
        assert event1.correlation_id == correlation_id
        assert event2.correlation_id == correlation_id
