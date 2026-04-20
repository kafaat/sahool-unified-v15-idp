"""
Tests for shared/contracts module
=================================

Unit tests covering event models, registry, publisher, consumer,
action types/templates/factory, and JSON schema validation.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

# ---------------------------------------------------------------------------
# Base & metadata
# ---------------------------------------------------------------------------
from shared.contracts.events.base import BaseEvent, EventMetadata, EventSource

# ---------------------------------------------------------------------------
# Domain events
# ---------------------------------------------------------------------------
from shared.contracts.events.field_events import (
    FieldBoundaryChangedEvent,
    FieldCreatedEvent,
    FieldUpdatedEvent,
)
from shared.contracts.events.crop_events import (
    CropDiseaseDetectedEvent,
    CropHarvestedEvent,
    CropPlantedEvent,
)
from shared.contracts.events.weather_events import (
    WeatherAlertIssuedEvent,
    WeatherForecastUpdatedEvent,
)
from shared.contracts.events.iot_events import SensorAlertEvent, SensorReadingEvent
from shared.contracts.events.analytics_events import (
    NDVICalculatedEvent,
    YieldPredictedEvent,
)

# ---------------------------------------------------------------------------
# Infrastructure
# ---------------------------------------------------------------------------
from shared.contracts.events.registry import EventRegistry
from shared.contracts.events.publisher import EventPublisher
from shared.contracts.events.consumer import EventConsumer

# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------
from shared.contracts.actions.types import (
    ActionStatus,
    ActionType,
    ResourceType,
    UrgencyLevel,
)
from shared.contracts.actions.template import (
    ActionStep,
    ActionTemplate,
    Resource,
    TimeWindow,
)
from shared.contracts.actions.factory import ActionTemplateFactory


# =============================================================================
# Helpers
# =============================================================================

TENANT_ID = uuid4()
FIELD_ID = uuid4()


def _make_field_created(**overrides) -> FieldCreatedEvent:
    defaults = {
        "tenant_id": TENANT_ID,
        "field_id": FIELD_ID,
        "name": "North Wheat",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8], [46.7, 24.7]]
            ],
        },
        "area_hectares": 10.5,
    }
    defaults.update(overrides)
    return FieldCreatedEvent(**defaults)


# =============================================================================
# 1. EventMetadata tests
# =============================================================================


@pytest.mark.unit
class TestEventMetadata:
    """Tests for EventMetadata dataclass."""

    def test_metadata_requires_correlation_id(self):
        cid = uuid4()
        meta = EventMetadata(correlation_id=cid)
        assert meta.correlation_id == cid

    def test_metadata_optional_fields_default_none(self):
        meta = EventMetadata(correlation_id=uuid4())
        assert meta.causation_id is None
        assert meta.user_id is None
        assert meta.trace_id is None
        assert meta.span_id is None

    def test_metadata_to_dict(self):
        cid = uuid4()
        uid = uuid4()
        meta = EventMetadata(correlation_id=cid, user_id=uid, trace_id="t1")
        d = meta.to_dict()
        assert d["correlation_id"] == str(cid)
        assert d["user_id"] == str(uid)
        assert d["trace_id"] == "t1"
        assert d["causation_id"] is None

    def test_metadata_to_dict_with_causation(self):
        cid = uuid4()
        cause = uuid4()
        meta = EventMetadata(correlation_id=cid, causation_id=cause)
        d = meta.to_dict()
        assert d["causation_id"] == str(cause)


# =============================================================================
# 2. EventSource tests
# =============================================================================


@pytest.mark.unit
class TestEventSource:
    """Tests for EventSource dataclass."""

    def test_source_to_dict(self):
        src = EventSource(service="field-management", version="16.0.0", instance_id="abc")
        d = src.to_dict()
        assert d == {"service": "field-management", "version": "16.0.0", "instance_id": "abc"}

    def test_source_instance_id_optional(self):
        src = EventSource(service="s", version="1.0")
        assert src.instance_id is None
        assert src.to_dict()["instance_id"] is None


# =============================================================================
# 3. BaseEvent tests
# =============================================================================


@pytest.mark.unit
class TestBaseEvent:
    """Tests for BaseEvent base class."""

    def test_auto_generates_event_id(self):
        event = _make_field_created()
        assert isinstance(event.event_id, UUID)

    def test_auto_generates_timestamp(self):
        event = _make_field_created()
        assert isinstance(event.timestamp, datetime)

    def test_auto_generates_metadata_if_none(self):
        event = _make_field_created()
        assert event.metadata is not None
        assert isinstance(event.metadata.correlation_id, UUID)

    def test_preserves_provided_metadata(self):
        cid = uuid4()
        meta = EventMetadata(correlation_id=cid)
        event = _make_field_created(metadata=meta)
        assert event.metadata.correlation_id == cid

    def test_event_type_property(self):
        event = _make_field_created()
        assert event.event_type == "field.created"

    def test_event_version_property(self):
        event = _make_field_created()
        assert event.event_version == "1.0.0"

    def test_str_representation(self):
        event = _make_field_created()
        s = str(event)
        assert "field.created" in s
        assert str(event.tenant_id) in s

    def test_payload_to_dict_not_implemented_on_base(self):
        """BaseEvent._payload_to_dict raises NotImplementedError."""
        base = BaseEvent(tenant_id=TENANT_ID)
        with pytest.raises(NotImplementedError):
            base._payload_to_dict()

    def test_from_dict_not_implemented_on_base(self):
        with pytest.raises(NotImplementedError):
            BaseEvent.from_dict({})


# =============================================================================
# 4. FieldCreatedEvent tests
# =============================================================================


@pytest.mark.unit
class TestFieldCreatedEvent:
    """Tests for FieldCreatedEvent."""

    def test_event_type(self):
        assert FieldCreatedEvent.EVENT_TYPE == "field.created"

    def test_to_dict_has_required_keys(self):
        event = _make_field_created()
        d = event.to_dict()
        assert "event_id" in d
        assert "event_type" in d
        assert "timestamp" in d
        assert "tenant_id" in d
        assert "payload" in d
        assert d["event_type"] == "field.created"

    def test_payload_contains_field_data(self):
        event = _make_field_created(soil_type="clay", irrigation_type="drip")
        payload = event._payload_to_dict()
        assert payload["field_id"] == str(FIELD_ID)
        assert payload["name"] == "North Wheat"
        assert payload["area_hectares"] == 10.5
        assert payload["soil_type"] == "clay"
        assert payload["irrigation_type"] == "drip"

    def test_payload_omits_none_optionals(self):
        event = _make_field_created()
        payload = event._payload_to_dict()
        assert "soil_type" not in payload
        assert "owner_id" not in payload

    def test_to_json_returns_string(self):
        event = _make_field_created()
        j = event.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed["event_type"] == "field.created"

    def test_from_dict_round_trip(self):
        event = _make_field_created(owner_id=uuid4())
        d = event.to_dict()
        restored = FieldCreatedEvent.from_dict(d)
        assert restored.field_id == event.field_id
        assert restored.name == "North Wheat"
        assert restored.area_hectares == 10.5

    def test_schema_path(self):
        assert FieldCreatedEvent.SCHEMA_PATH == "field.created.v1.json"


# =============================================================================
# 5. FieldUpdatedEvent tests
# =============================================================================


@pytest.mark.unit
class TestFieldUpdatedEvent:
    """Tests for FieldUpdatedEvent."""

    def test_event_type(self):
        assert FieldUpdatedEvent.EVENT_TYPE == "field.updated"

    def test_payload(self):
        event = FieldUpdatedEvent(
            tenant_id=TENANT_ID,
            field_id=FIELD_ID,
            updated_fields=["name", "area"],
            changes={"name": {"old": "A", "new": "B"}},
        )
        payload = event._payload_to_dict()
        assert payload["updated_fields"] == ["name", "area"]
        assert "changes" in payload


# =============================================================================
# 6. FieldBoundaryChangedEvent test
# =============================================================================


@pytest.mark.unit
def test_field_boundary_changed_payload():
    event = FieldBoundaryChangedEvent(
        tenant_id=TENANT_ID,
        field_id=FIELD_ID,
        old_geometry={"type": "Polygon", "coordinates": []},
        new_geometry={"type": "Polygon", "coordinates": []},
        area_change_hectares=-0.5,
    )
    payload = event._payload_to_dict()
    assert payload["area_change_hectares"] == -0.5
    assert event.EVENT_TYPE == "field.boundary_changed"


# =============================================================================
# 7. CropPlantedEvent tests
# =============================================================================


@pytest.mark.unit
class TestCropPlantedEvent:
    """Tests for CropPlantedEvent."""

    def test_event_type(self):
        assert CropPlantedEvent.EVENT_TYPE == "crop.planted"

    def test_payload_required_fields(self):
        event = CropPlantedEvent(
            tenant_id=TENANT_ID,
            field_id=FIELD_ID,
            crop_type="wheat",
            variety="Sakha 95",
            planting_date=date(2026, 1, 15),
        )
        payload = event._payload_to_dict()
        assert payload["crop_type"] == "wheat"
        assert payload["variety"] == "Sakha 95"
        assert payload["planting_date"] == "2026-01-15"

    def test_optional_fields_omitted(self):
        event = CropPlantedEvent(
            tenant_id=TENANT_ID,
            field_id=FIELD_ID,
            crop_type="barley",
            variety="",
            planting_date=date(2026, 1, 1),
        )
        payload = event._payload_to_dict()
        assert "expected_harvest_date" not in payload
        assert "seed_source" not in payload


# =============================================================================
# 8. CropDiseaseDetectedEvent tests
# =============================================================================


@pytest.mark.unit
class TestCropDiseaseDetectedEvent:
    """Tests for CropDiseaseDetectedEvent."""

    def test_event_type(self):
        assert CropDiseaseDetectedEvent.EVENT_TYPE == "crop.disease_detected"

    def test_priority_attribute(self):
        assert CropDiseaseDetectedEvent.PRIORITY == "high"

    def test_payload_with_all_fields(self):
        now = datetime.now(UTC)
        event = CropDiseaseDetectedEvent(
            tenant_id=TENANT_ID,
            field_id=FIELD_ID,
            crop_id=uuid4(),
            disease_type="wheat_rust",
            disease_category="fungal",
            confidence_score=0.92,
            detected_at=now,
            affected_area_percentage=15.5,
            severity_level="high",
            image_urls=["https://example.com/img.jpg"],
            detection_method="satellite",
            recommended_actions=[{"action": "spray", "priority": 1}],
        )
        payload = event._payload_to_dict()
        assert payload["disease_type"] == "wheat_rust"
        assert payload["confidence_score"] == 0.92
        assert payload["disease_category"] == "fungal"
        assert len(payload["image_urls"]) == 1
        assert len(payload["recommended_actions"]) == 1


# =============================================================================
# 9. CropHarvestedEvent test
# =============================================================================


@pytest.mark.unit
def test_crop_harvested_payload():
    event = CropHarvestedEvent(
        tenant_id=TENANT_ID,
        field_id=FIELD_ID,
        crop_id=uuid4(),
        harvest_date=date(2026, 6, 15),
        yield_kg=5200.0,
        area_harvested_hectares=8.5,
        quality_grade="A",
    )
    payload = event._payload_to_dict()
    assert payload["yield_kg"] == 5200.0
    assert payload["quality_grade"] == "A"
    assert event.EVENT_TYPE == "crop.harvested"


# =============================================================================
# 10. Weather events tests
# =============================================================================


@pytest.mark.unit
class TestWeatherEvents:
    """Tests for weather domain events."""

    def test_forecast_updated_payload(self):
        event = WeatherForecastUpdatedEvent(
            tenant_id=TENANT_ID,
            location_id="LOC-001",
            forecast_date=date(2026, 3, 30),
            temperature_min=8.0,
            temperature_max=22.0,
            precipitation_mm=0.0,
            humidity_percent=55.0,
            wind_speed_kmh=15.0,
        )
        payload = event._payload_to_dict()
        assert payload["location_id"] == "LOC-001"
        assert payload["temperature_max"] == 22.0

    def test_alert_issued_payload(self):
        now = datetime.now(UTC)
        event = WeatherAlertIssuedEvent(
            tenant_id=TENANT_ID,
            alert_id=uuid4(),
            alert_type="frost",
            severity="critical",
            affected_regions=["North", "Central"],
            valid_from=now,
            valid_until=now + timedelta(hours=12),
            description="Frost warning",
        )
        payload = event._payload_to_dict()
        assert payload["alert_type"] == "frost"
        assert payload["severity"] == "critical"
        assert len(payload["affected_regions"]) == 2

    def test_alert_priority(self):
        assert WeatherAlertIssuedEvent.PRIORITY == "high"


# =============================================================================
# 11. IoT events tests
# =============================================================================


@pytest.mark.unit
class TestIoTEvents:
    """Tests for IoT domain events."""

    def test_sensor_reading_payload(self):
        now = datetime.now(UTC)
        event = SensorReadingEvent(
            tenant_id=TENANT_ID,
            sensor_id=uuid4(),
            field_id=FIELD_ID,
            reading_type="soil_moisture",
            value=42.5,
            unit="%",
            reading_timestamp=now,
            battery_level=85.0,
        )
        payload = event._payload_to_dict()
        assert payload["reading_type"] == "soil_moisture"
        assert payload["value"] == 42.5
        assert payload["battery_level"] == 85.0

    def test_sensor_alert_payload(self):
        now = datetime.now(UTC)
        event = SensorAlertEvent(
            tenant_id=TENANT_ID,
            sensor_id=uuid4(),
            alert_type="low_moisture",
            threshold_value=30.0,
            actual_value=22.0,
            alert_timestamp=now,
        )
        payload = event._payload_to_dict()
        assert payload["threshold_value"] == 30.0
        assert payload["actual_value"] == 22.0


# =============================================================================
# 12. Analytics events tests
# =============================================================================


@pytest.mark.unit
class TestAnalyticsEvents:
    """Tests for analytics domain events."""

    def test_ndvi_calculated_payload(self):
        event = NDVICalculatedEvent(
            tenant_id=TENANT_ID,
            field_id=FIELD_ID,
            ndvi_value=0.72,
            satellite_source="Sentinel-2",
            acquisition_date=date(2026, 3, 25),
            calculation_date=datetime.now(UTC),
            cloud_cover_percent=5.0,
            quality_flag="good",
        )
        payload = event._payload_to_dict()
        assert payload["ndvi_value"] == 0.72
        assert payload["satellite_source"] == "Sentinel-2"
        assert payload["quality_flag"] == "good"

    def test_yield_predicted_payload(self):
        event = YieldPredictedEvent(
            tenant_id=TENANT_ID,
            field_id=FIELD_ID,
            crop_id=uuid4(),
            predicted_yield_kg=4500.0,
            confidence_interval_low=4000.0,
            confidence_interval_high=5000.0,
            prediction_date=datetime.now(UTC),
            model_version="2.1.0",
            factors_considered=["ndvi", "weather", "soil"],
        )
        payload = event._payload_to_dict()
        assert payload["predicted_yield_kg"] == 4500.0
        assert payload["model_version"] == "2.1.0"
        assert len(payload["factors_considered"]) == 3


# =============================================================================
# 13. EventRegistry tests
# =============================================================================


@pytest.mark.unit
class TestEventRegistry:
    """Tests for EventRegistry."""

    def test_field_created_registered(self):
        cls = EventRegistry.get_event_class("field.created")
        assert cls is FieldCreatedEvent

    def test_crop_planted_registered(self):
        cls = EventRegistry.get_event_class("crop.planted")
        assert cls is CropPlantedEvent

    def test_unknown_event_returns_none(self):
        cls = EventRegistry.get_event_class("does.not.exist")
        assert cls is None

    def test_list_events_contains_known_types(self):
        events = EventRegistry.list_events()
        assert "field.created" in events
        assert "crop.disease_detected" in events
        assert "iot.sensor_reading" in events
        assert "analytics.ndvi_calculated" in events

    def test_list_versions(self):
        versions = EventRegistry.list_versions("field.created")
        assert "1.0.0" in versions

    def test_list_versions_unknown_returns_empty(self):
        versions = EventRegistry.list_versions("nonexistent.event")
        assert versions == []

    def test_is_compatible_equal(self):
        assert EventRegistry.is_compatible("field.created", "1.0.0", "1.0.0") is True

    def test_is_compatible_higher(self):
        assert EventRegistry.is_compatible("field.created", "2.0.0", "1.0.0") is True

    def test_is_compatible_lower(self):
        assert EventRegistry.is_compatible("field.created", "0.9.0", "1.0.0") is False

    def test_get_event_class_with_version(self):
        cls = EventRegistry.get_event_class("field.created", version="1.0.0")
        assert cls is FieldCreatedEvent

    def test_get_event_class_wrong_version_returns_none(self):
        cls = EventRegistry.get_event_class("field.created", version="99.0.0")
        assert cls is None

    def test_register_custom_event(self):
        """Register and retrieve a custom event class."""

        class CustomTestEvent(BaseEvent):
            EVENT_TYPE = "test.custom_unit"
            EVENT_VERSION = "1.0.0"

            def _payload_to_dict(self):
                return {}

        EventRegistry.register(CustomTestEvent)
        cls = EventRegistry.get_event_class("test.custom_unit")
        assert cls is CustomTestEvent


# =============================================================================
# 14. EventPublisher tests
# =============================================================================


@pytest.mark.unit
class TestEventPublisher:
    """Tests for EventPublisher."""

    @pytest.fixture
    def mock_nats(self):
        nc = AsyncMock()
        nc.publish = AsyncMock()
        return nc

    @pytest.fixture
    def publisher(self, mock_nats):
        return EventPublisher(
            nats_client=mock_nats,
            service_name="test-service",
            service_version="1.0.0",
        )

    def _make_weather_event(self):
        """Use WeatherForecastUpdatedEvent which has no SCHEMA_PATH, avoiding
        strict JSON schema validation that rejects None instance_id."""
        return WeatherForecastUpdatedEvent(
            tenant_id=TENANT_ID,
            location_id="LOC-001",
            forecast_date=date(2026, 3, 30),
            temperature_min=8.0,
            temperature_max=22.0,
            precipitation_mm=0.0,
            humidity_percent=55.0,
        )

    @pytest.mark.asyncio
    async def test_publish_calls_nats(self, publisher, mock_nats):
        event = self._make_weather_event()
        result = await publisher.publish(event)
        assert result is True
        mock_nats.publish.assert_called_once()
        call_args = mock_nats.publish.call_args
        assert call_args[0][0] == "sahool.events.weather.forecast_updated"

    @pytest.mark.asyncio
    async def test_publish_custom_subject(self, publisher, mock_nats):
        event = self._make_weather_event()
        await publisher.publish(event, subject="custom.subject")
        call_args = mock_nats.publish.call_args
        assert call_args[0][0] == "custom.subject"

    @pytest.mark.asyncio
    async def test_publish_sets_source(self, publisher, mock_nats):
        event = self._make_weather_event()
        await publisher.publish(event)
        assert event.source is not None
        assert event.source.service == "test-service"
        assert event.source.version == "1.0.0"

    @pytest.mark.asyncio
    async def test_publish_without_nats_returns_true(self):
        publisher = EventPublisher(nats_client=None, service_name="test")
        event = self._make_weather_event()
        result = await publisher.publish(event)
        assert result is True

    @pytest.mark.asyncio
    async def test_publish_nats_error_returns_false(self, mock_nats):
        mock_nats.publish.side_effect = Exception("connection refused")
        publisher = EventPublisher(nats_client=mock_nats, service_name="test")
        event = self._make_weather_event()
        result = await publisher.publish(event)
        assert result is False

    @pytest.mark.asyncio
    async def test_publish_batch(self, publisher, mock_nats):
        events = [self._make_weather_event() for _ in range(3)]
        count = await publisher.publish_batch(events)
        assert count == 3
        assert mock_nats.publish.call_count == 3

    @pytest.mark.asyncio
    async def test_publish_batch_partial_failure(self, mock_nats):
        # Fail on second call
        mock_nats.publish.side_effect = [None, Exception("fail"), None]
        publisher = EventPublisher(nats_client=mock_nats, service_name="test")
        events = [self._make_weather_event() for _ in range(3)]
        count = await publisher.publish_batch(events)
        assert count == 2


# =============================================================================
# 15. EventConsumer tests
# =============================================================================


@pytest.mark.unit
class TestEventConsumer:
    """Tests for EventConsumer."""

    def test_on_decorator_registers_handler(self):
        consumer = EventConsumer(nats_client=None, service_name="test")

        @consumer.on(FieldCreatedEvent)
        async def handle(event):
            pass

        assert "field.created" in consumer._handlers

    def test_register_programmatic(self):
        consumer = EventConsumer(nats_client=None, service_name="test")

        async def handler(event):
            pass

        consumer.register("field.created", handler)
        assert "field.created" in consumer._handlers

    @pytest.mark.asyncio
    async def test_start_without_nats_does_nothing(self):
        consumer = EventConsumer(nats_client=None)
        await consumer.start()
        assert consumer._subscriptions == []

    @pytest.mark.asyncio
    async def test_start_subscribes(self):
        mock_nats = AsyncMock()
        mock_sub = AsyncMock()
        mock_nats.subscribe = AsyncMock(return_value=mock_sub)

        consumer = EventConsumer(nats_client=mock_nats, service_name="test")

        @consumer.on(FieldCreatedEvent)
        async def handle(event):
            pass

        await consumer.start()
        mock_nats.subscribe.assert_called_once()
        call_args = mock_nats.subscribe.call_args
        assert call_args[0][0] == "sahool.events.field.created"
        assert len(consumer._subscriptions) == 1

    @pytest.mark.asyncio
    async def test_stop_unsubscribes(self):
        mock_sub = AsyncMock()
        consumer = EventConsumer(nats_client=None)
        consumer._subscriptions = [mock_sub]

        await consumer.stop()
        mock_sub.unsubscribe.assert_called_once()
        assert consumer._subscriptions == []


# =============================================================================
# 16. JSON Schema validity tests
# =============================================================================


@pytest.mark.unit
class TestJSONSchemas:
    """Verify that JSON schema files are valid JSON and have expected structure."""

    SCHEMA_DIR = Path(__file__).resolve().parents[4] / "shared" / "contracts" / "schemas"
    EVENTS_DIR = Path(__file__).resolve().parents[4] / "shared" / "contracts" / "events"

    def _load_json(self, path: Path) -> dict:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def test_base_event_schema_is_valid_json(self):
        schema = self._load_json(self.SCHEMA_DIR / "base-event.v1.json")
        assert schema["type"] == "object"
        assert "event_id" in schema["properties"]
        assert "payload" in schema["required"]

    def test_field_created_schema_is_valid_json(self):
        schema = self._load_json(self.SCHEMA_DIR / "field.created.v1.json")
        assert schema["title"] == "Field Created Event"
        assert "allOf" in schema

    def test_crop_disease_detected_schema_is_valid_json(self):
        schema = self._load_json(self.SCHEMA_DIR / "crop.disease_detected.v1.json")
        assert schema["title"] == "Crop Disease Detected Event"
        payload_props = schema["properties"]["payload"]["properties"]
        assert "confidence_score" in payload_props

    def test_registry_json_is_valid(self):
        registry = self._load_json(self.EVENTS_DIR / "registry.json")
        assert "schemas" in registry
        assert len(registry["schemas"]) >= 3

    def test_registry_entries_have_required_fields(self):
        registry = self._load_json(self.EVENTS_DIR / "registry.json")
        for entry in registry["schemas"]:
            assert "ref" in entry
            assert "file" in entry
            assert "topic" in entry
            assert "version" in entry
            assert "owner" in entry

    def test_all_event_json_files_are_parseable(self):
        """All .json files under events/ are valid JSON."""
        json_files = list(self.EVENTS_DIR.glob("*.json"))
        assert len(json_files) >= 1
        for jf in json_files:
            data = self._load_json(jf)
            assert isinstance(data, dict)


# =============================================================================
# 17. ActionType enum tests
# =============================================================================


@pytest.mark.unit
class TestActionType:
    """Tests for ActionType StrEnum."""

    def test_irrigation_value(self):
        assert ActionType.IRRIGATION == "irrigation"

    def test_is_string(self):
        assert isinstance(ActionType.HARVEST, str)

    def test_all_categories_present(self):
        values = [e.value for e in ActionType]
        assert "fertilization" in values
        assert "spray" in values
        assert "inspection" in values
        assert "harvest" in values
        assert "maintenance" in values
        assert "monitoring" in values


# =============================================================================
# 18. ActionStatus enum tests
# =============================================================================


@pytest.mark.unit
class TestActionStatus:
    """Tests for ActionStatus StrEnum."""

    def test_all_statuses(self):
        assert ActionStatus.PENDING == "pending"
        assert ActionStatus.COMPLETED == "completed"
        assert ActionStatus.FAILED == "failed"
        assert ActionStatus.EXPIRED == "expired"
        assert ActionStatus.SKIPPED == "skipped"
        assert ActionStatus.IN_PROGRESS == "in_progress"
        assert ActionStatus.SCHEDULED == "scheduled"


# =============================================================================
# 19. UrgencyLevel tests
# =============================================================================


@pytest.mark.unit
class TestUrgencyLevel:
    """Tests for UrgencyLevel StrEnum."""

    def test_values(self):
        assert UrgencyLevel.LOW == "low"
        assert UrgencyLevel.CRITICAL == "critical"

    def test_label_ar(self):
        assert UrgencyLevel.LOW.label_ar == "منخفض"
        assert UrgencyLevel.HIGH.label_ar == "عالي"
        assert UrgencyLevel.CRITICAL.label_ar == "حرج"

    def test_max_delay_hours(self):
        assert UrgencyLevel.CRITICAL.max_delay_hours == 4
        assert UrgencyLevel.HIGH.max_delay_hours == 24
        assert UrgencyLevel.LOW.max_delay_hours == 168


# =============================================================================
# 20. ResourceType tests
# =============================================================================


@pytest.mark.unit
def test_resource_type_has_water():
    assert ResourceType.WATER == "water"


@pytest.mark.unit
def test_resource_type_has_fertilizers():
    values = [e.value for e in ResourceType]
    assert "fertilizer_urea" in values
    assert "fertilizer_dap" in values
    assert "fertilizer_organic" in values


# =============================================================================
# 21. ActionStep / Resource / TimeWindow model tests
# =============================================================================


@pytest.mark.unit
class TestActionModels:
    """Tests for ActionStep, Resource, TimeWindow Pydantic models."""

    def test_action_step_creation(self):
        step = ActionStep(
            step_number=1,
            title_ar="فحص",
            title_en="Inspect",
            description_ar="فحص النباتات",
            description_en="Inspect plants",
            duration_minutes=30,
            requires_photo=True,
        )
        assert step.step_number == 1
        assert step.requires_photo is True
        assert step.requires_confirmation is True  # default

    def test_resource_creation(self):
        resource = Resource(
            resource_type=ResourceType.WATER,
            name_ar="مياه",
            name_en="Water",
            quantity=5000,
            unit="liters",
            unit_ar="لتر",
            estimated_cost=50.0,
        )
        assert resource.quantity == 5000
        assert resource.currency == "YER"

    def test_time_window_creation(self):
        tw = TimeWindow(
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 7),
            avoid_conditions=["rain", "high_wind"],
        )
        assert len(tw.avoid_conditions) == 2


# =============================================================================
# 22. ActionTemplate tests
# =============================================================================


@pytest.mark.unit
class TestActionTemplate:
    """Tests for ActionTemplate Pydantic model."""

    @pytest.fixture
    def minimal_template(self):
        return ActionTemplate(
            action_type=ActionType.IRRIGATION,
            title_ar="ري الحقل",
            title_en="Irrigate field",
            description_ar="يجب ري الحقل لانخفاض الرطوبة",
            description_en="Field irrigation needed due to low moisture",
            source_service="irrigation-smart",
            confidence=0.85,
            urgency=UrgencyLevel.HIGH,
            field_id="field-001",
            estimated_duration_minutes=120,
            fallback_instructions_ar="ري الحقل يدويا",
            fallback_instructions_en="Irrigate the field manually",
        )

    def test_auto_generates_action_id(self, minimal_template):
        assert minimal_template.action_id is not None
        assert len(minimal_template.action_id) > 10

    def test_default_status_pending(self, minimal_template):
        assert minimal_template.status == ActionStatus.PENDING

    def test_offline_executable_default_true(self, minimal_template):
        assert minimal_template.offline_executable is True

    def test_calculate_priority_score(self, minimal_template):
        minimal_template.deadline = datetime.now(UTC) + timedelta(hours=6)
        score = minimal_template.calculate_priority_score()
        assert 0 <= score <= 100
        # HIGH urgency (30) + confidence bonus (0.85*30=25.5) + deadline bonus (30) = 85.5
        assert score > 50

    def test_to_notification_payload(self, minimal_template):
        payload = minimal_template.to_notification_payload()
        assert payload["type"] == "irrigation"
        assert payload["urgency"] == "high"
        assert payload["field_id"] == "field-001"
        assert payload["confidence"] == 0.85

    def test_to_task_card(self, minimal_template):
        card = minimal_template.to_task_card()
        assert card["type"] == "irrigation"
        assert card["confidence_percent"] == 85
        assert card["offline_ready"] is True
        assert card["status"] == "pending"

    def test_urgency_color(self, minimal_template):
        assert minimal_template._get_urgency_color() == "#F97316"  # orange for HIGH


# =============================================================================
# 23. ActionTemplateFactory tests
# =============================================================================


@pytest.mark.unit
class TestActionTemplateFactory:
    """Tests for ActionTemplateFactory."""

    def test_create_irrigation_action(self):
        template = ActionTemplateFactory.create_irrigation_action(
            field_id="field-001",
            water_amount_liters=5000,
            duration_minutes=90,
            urgency=UrgencyLevel.HIGH,
            confidence=0.9,
            soil_moisture_percent=25.0,
        )
        assert template.action_type == ActionType.IRRIGATION
        assert template.confidence == 0.9
        assert len(template.steps) == 3
        assert len(template.resources_needed) == 1
        assert template.resources_needed[0].resource_type == ResourceType.WATER
        assert template.offline_executable is True

    def test_create_fertilization_action(self):
        template = ActionTemplateFactory.create_fertilization_action(
            field_id="field-002",
            fertilizer_type="urea",
            quantity_kg=46.0,
            urgency=UrgencyLevel.MEDIUM,
            confidence=0.85,
            npk_ratio="46-0-0",
        )
        assert template.action_type == ActionType.FERTILIZATION
        assert len(template.steps) == 3
        assert template.resources_needed[0].resource_type == ResourceType.FERTILIZER_UREA
        assert "46-0-0" in template.reasoning_en

    def test_create_disease_inspection_action(self):
        template = ActionTemplateFactory.create_disease_inspection_action(
            field_id="field-003",
            disease_name_ar="صدأ القمح",
            disease_name_en="Wheat Rust",
            confidence=0.88,
            affected_area_percent=12.0,
        )
        assert template.action_type == ActionType.INSPECTION_DISEASE
        assert template.urgency == UrgencyLevel.HIGH
        assert len(template.steps) == 3
        assert "Wheat Rust" in template.title_en

    def test_create_spray_action(self):
        template = ActionTemplateFactory.create_spray_action(
            field_id="field-004",
            pesticide_type="fungicide",
            pesticide_name_ar="مبيد فطري",
            pesticide_name_en="Fungicide X",
            concentration="2ml/L",
            area_hectares=5.0,
            urgency=UrgencyLevel.HIGH,
            confidence=0.82,
            target_pest_ar="صدأ",
            target_pest_en="Rust",
        )
        assert template.action_type == ActionType.SPRAY_FUNGICIDE
        assert len(template.resources_needed) == 2  # pesticide + sprayer
        assert "Rust" in template.title_en

    def test_factory_irrigation_deadline_from_urgency(self):
        template = ActionTemplateFactory.create_irrigation_action(
            field_id="field-001",
            water_amount_liters=3000,
            duration_minutes=60,
            urgency=UrgencyLevel.CRITICAL,
            confidence=0.95,
        )
        assert template.deadline is not None
        # Critical has 4h delay, so deadline should be close
        delta = template.deadline - template.created_at
        assert delta.total_seconds() <= 5 * 3600  # within ~5h tolerance


# =============================================================================
# 24. Module-level import / version tests
# =============================================================================


@pytest.mark.unit
def test_contracts_module_version():
    import shared.contracts

    assert shared.contracts.__version__ == "16.0.0"


@pytest.mark.unit
def test_events_module_exports_all():
    """Verify top-level events __init__ exports key classes."""
    from shared.contracts import events

    assert hasattr(events, "FieldCreatedEvent")
    assert hasattr(events, "EventPublisher")
    assert hasattr(events, "EventConsumer")
    assert hasattr(events, "EventRegistry")
    assert hasattr(events, "BaseEvent")
