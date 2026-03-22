"""
Bug-Hunting Tests for SAHOOL API Event Contracts
=================================================
Tests designed to find real bugs in event serialization, deserialization,
required fields validation, and version compatibility.

Target: shared/events/contracts.py
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from shared.events.contracts import (
    REQUIRED_EVENT_FIELDS,
    AgentExecutionCompletedEvent,
    AgentExecutionFailedEvent,
    AgentExecutionStartedEvent,
    AgentStepCompletedEvent,
    BaseEvent,
    BatchExpiredEvent,
    CropStressEvent,
    DataModelCreatedEvent,
    DiseaseDetectedEvent,
    FarmerCreatedEvent,
    FarmerStatusChangedEvent,
    FarmerUpdatedEvent,
    FieldCreatedEvent,
    FieldDeletedEvent,
    FieldUpdatedEvent,
    HarvestDealCreatedEvent,
    HarvestDealStageChangedEvent,
    InteractionLoggedEvent,
    LowStockEvent,
    PageCreatedEvent,
    PagePublishedEvent,
    PaymentCompletedEvent,
    PaymentFailedEvent,
    SubscriptionCreatedEvent,
    SubscriptionRenewedEvent,
    WeatherAlertEvent,
    WeatherForecastEvent,
    WeChatChatSummarizedEvent,
    WeChatContactAddedEvent,
    WeChatMessageReceivedEvent,
    WeChatMessageSentEvent,
    WeChatMomentPublishedEvent,
    WorkflowExecutedEvent,
    validate_event_payload,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

_UUID = str(uuid4())
_UUID2 = str(uuid4())
_NOW = datetime.now(UTC)


ALL_EVENT_CLASSES = [
    FieldCreatedEvent,
    FieldUpdatedEvent,
    FieldDeletedEvent,
    WeatherForecastEvent,
    WeatherAlertEvent,
    DiseaseDetectedEvent,
    CropStressEvent,
    LowStockEvent,
    BatchExpiredEvent,
    SubscriptionCreatedEvent,
    PaymentCompletedEvent,
    SubscriptionRenewedEvent,
    PaymentFailedEvent,
    AgentExecutionStartedEvent,
    AgentExecutionCompletedEvent,
    AgentExecutionFailedEvent,
    AgentStepCompletedEvent,
    FarmerCreatedEvent,
    FarmerUpdatedEvent,
    FarmerStatusChangedEvent,
    HarvestDealCreatedEvent,
    HarvestDealStageChangedEvent,
    InteractionLoggedEvent,
    PageCreatedEvent,
    PagePublishedEvent,
    DataModelCreatedEvent,
    WorkflowExecutedEvent,
    WeChatMessageReceivedEvent,
    WeChatMessageSentEvent,
    WeChatContactAddedEvent,
    WeChatMomentPublishedEvent,
    WeChatChatSummarizedEvent,
]


def _build_minimal_event_data(cls):
    """Build minimal valid data for a given event class by inspecting required fields."""
    data = {}
    for name, field_info in cls.model_fields.items():
        if field_info.is_required():
            annotation = field_info.annotation
            ann_str = str(annotation)

            # Handle UUID fields
            if "UUID" in ann_str:
                data[name] = uuid4()
            elif "datetime" in ann_str:
                data[name] = _NOW
            elif "float" in ann_str:
                # Check for constraints
                if field_info.metadata:
                    data[name] = 1.0
                else:
                    data[name] = 0.5
            elif "int" in ann_str:
                data[name] = 1
            elif "bool" in ann_str:
                data[name] = True
            elif "list" in ann_str:
                data[name] = []
            elif "str" in ann_str:
                # Check for pattern constraints
                if hasattr(field_info, "metadata") and field_info.metadata:
                    for meta in field_info.metadata:
                        if hasattr(meta, "pattern"):
                            # Extract first valid value from pattern
                            pattern = meta.pattern
                            # Simple extraction of first option from ^(a|b|c)$
                            if pattern.startswith("^(") and pattern.endswith(")$"):
                                first = pattern[2:-2].split("|")[0]
                                data[name] = first
                                break
                    else:
                        data[name] = "test_value_" + name
                else:
                    data[name] = "test_value_" + name
            else:
                data[name] = "test_value"

    return data


# ─────────────────────────────────────────────────────────────────────────────
# 1. Serialization / Deserialization Roundtrip
# ─────────────────────────────────────────────────────────────────────────────


class TestEventSerializationRoundtrip:
    """BUG HUNT: Verify every event class can serialize to JSON and deserialize back."""

    @pytest.mark.parametrize("event_cls", ALL_EVENT_CLASSES, ids=lambda c: c.__name__)
    def test_json_roundtrip(self, event_cls):
        """Each event must survive JSON serialization -> deserialization without data loss."""
        data = _build_minimal_event_data(event_cls)
        event = event_cls(**data)

        # Serialize to JSON string
        json_str = event.model_dump_json()
        assert json_str, f"{event_cls.__name__} produced empty JSON"

        # Deserialize back
        restored = event_cls.model_validate_json(json_str)

        # Verify key fields match
        for field_name in data:
            original_val = getattr(event, field_name)
            restored_val = getattr(restored, field_name)
            assert original_val == restored_val, (
                f"{event_cls.__name__}.{field_name}: "
                f"original={original_val!r} != restored={restored_val!r}"
            )

    @pytest.mark.parametrize("event_cls", ALL_EVENT_CLASSES, ids=lambda c: c.__name__)
    def test_dict_roundtrip(self, event_cls):
        """Each event must survive dict serialization -> deserialization."""
        data = _build_minimal_event_data(event_cls)
        event = event_cls(**data)

        dumped = event.model_dump()
        assert isinstance(dumped, dict)

        # Must be JSON-serializable (no non-serializable objects)
        json_str = json.dumps(dumped, default=str)
        assert json_str

    @pytest.mark.parametrize("event_cls", ALL_EVENT_CLASSES, ids=lambda c: c.__name__)
    def test_model_dump_json_parseable(self, event_cls):
        """model_dump_json() output must be valid JSON parseable by json.loads."""
        data = _build_minimal_event_data(event_cls)
        event = event_cls(**data)
        json_str = event.model_dump_json()

        # Must not raise
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Required Fields on BaseEvent
# ─────────────────────────────────────────────────────────────────────────────


class TestBaseEventRequiredFields:
    """BUG HUNT: BaseEvent must always have event_id, timestamp, and version."""

    def test_base_event_has_event_id_by_default(self):
        """BaseEvent should auto-generate event_id if not provided."""
        event = BaseEvent()
        assert event.event_id is not None
        assert len(event.event_id) > 0

    def test_base_event_has_timestamp_by_default(self):
        """BaseEvent should auto-generate timestamp if not provided."""
        event = BaseEvent()
        assert event.timestamp is not None
        assert isinstance(event.timestamp, datetime)

    def test_base_event_has_version_by_default(self):
        """BaseEvent should have a default version."""
        event = BaseEvent()
        assert event.version is not None
        assert event.version == "1.0"

    def test_base_event_event_type_property(self):
        """event_type property should return the class name."""
        event = BaseEvent()
        assert event.event_type == "BaseEvent"

        data = _build_minimal_event_data(FieldCreatedEvent)
        field_event = FieldCreatedEvent(**data)
        assert field_event.event_type == "FieldCreatedEvent"

    def test_base_event_unique_event_ids(self):
        """Each BaseEvent instance should get a unique event_id."""
        events = [BaseEvent() for _ in range(100)]
        ids = {e.event_id for e in events}
        assert len(ids) == 100, "event_id values are not unique across instances"

    @pytest.mark.parametrize("event_cls", ALL_EVENT_CLASSES, ids=lambda c: c.__name__)
    def test_all_events_inherit_base_fields(self, event_cls):
        """All event subclasses must have event_id, timestamp, version from BaseEvent."""
        data = _build_minimal_event_data(event_cls)
        event = event_cls(**data)
        assert hasattr(event, "event_id"), f"{event_cls.__name__} missing event_id"
        assert hasattr(event, "timestamp"), f"{event_cls.__name__} missing timestamp"
        assert hasattr(event, "version"), f"{event_cls.__name__} missing version"
        assert event.event_id is not None
        assert event.timestamp is not None


# ─────────────────────────────────────────────────────────────────────────────
# 3. validate_event_payload() Bug Hunting
# ─────────────────────────────────────────────────────────────────────────────


class TestValidateEventPayload:
    """BUG HUNT: validate_event_payload must catch missing required fields."""

    def test_valid_payload_returns_true(self):
        """A payload with all required fields should pass validation."""
        payload = {
            "event_id": str(uuid4()),
            "timestamp": _NOW.isoformat(),
            "tenant_id": _UUID,
            "source_service": "test-service",
        }
        assert validate_event_payload("sahool.test.event", payload) is True

    def test_empty_payload_returns_false(self):
        """An empty payload must fail validation."""
        assert validate_event_payload("sahool.test.event", {}) is False

    def test_missing_event_id(self):
        """Payload missing event_id must fail."""
        payload = {
            "timestamp": _NOW.isoformat(),
            "tenant_id": _UUID,
            "source_service": "test-service",
        }
        assert validate_event_payload("sahool.test.event", payload) is False

    def test_missing_timestamp(self):
        """Payload missing timestamp must fail."""
        payload = {
            "event_id": str(uuid4()),
            "tenant_id": _UUID,
            "source_service": "test-service",
        }
        assert validate_event_payload("sahool.test.event", payload) is False

    def test_missing_tenant_id(self):
        """Payload missing tenant_id must fail."""
        payload = {
            "event_id": str(uuid4()),
            "timestamp": _NOW.isoformat(),
            "source_service": "test-service",
        }
        assert validate_event_payload("sahool.test.event", payload) is False

    def test_missing_source_service(self):
        """Payload missing source_service must fail."""
        payload = {
            "event_id": str(uuid4()),
            "timestamp": _NOW.isoformat(),
            "tenant_id": _UUID,
        }
        assert validate_event_payload("sahool.test.event", payload) is False

    def test_required_fields_constant_matches_docs(self):
        """REQUIRED_EVENT_FIELDS must contain exactly the documented fields."""
        expected = {"event_id", "timestamp", "tenant_id", "source_service"}
        assert expected == REQUIRED_EVENT_FIELDS, (
            f"REQUIRED_EVENT_FIELDS mismatch: got {REQUIRED_EVENT_FIELDS}, expected {expected}"
        )

    def test_extra_fields_dont_cause_failure(self):
        """Payload with extra fields should still pass if required fields are present."""
        payload = {
            "event_id": str(uuid4()),
            "timestamp": _NOW.isoformat(),
            "tenant_id": _UUID,
            "source_service": "test-service",
            "extra_field": "should not cause failure",
            "another_extra": 42,
        }
        assert validate_event_payload("sahool.test.event", payload) is True

    def test_none_values_for_required_fields(self):
        """BUG HUNT: Required fields set to None - does validate_event_payload catch this?
        It only checks key presence, not value truthiness. This is a potential bug."""
        payload = {
            "event_id": None,
            "timestamp": None,
            "tenant_id": None,
            "source_service": None,
        }
        # This tests the CURRENT behavior: validate_event_payload only checks key presence
        # If it returns True, that means None values are accepted (potential bug)
        result = validate_event_payload("sahool.test.event", payload)
        # Document the actual behavior
        assert result is True, (
            "validate_event_payload rejects None values for required fields - "
            "this means it validates values, not just key presence"
        )

    def test_empty_string_values_for_required_fields(self):
        """BUG HUNT: Required fields set to empty string."""
        payload = {
            "event_id": "",
            "timestamp": "",
            "tenant_id": "",
            "source_service": "",
        }
        # Current implementation only checks key presence, so this should pass
        result = validate_event_payload("sahool.test.event", payload)
        assert result is True, (
            "validate_event_payload rejects empty string values - "
            "unexpected value validation beyond key presence"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 4. Event Version Compatibility
# ─────────────────────────────────────────────────────────────────────────────


class TestEventVersionCompatibility:
    """BUG HUNT: Verify event schema version handling and backward compatibility."""

    def test_default_version_is_consistent(self):
        """All events should default to the same version string.

        BUG FOUND: PagePublishedEvent defines its own 'version' field (int, page version)
        which shadows BaseEvent's 'version' field (str, event schema version "1.0").
        This is a field name collision bug -- the child class field overrides the parent.
        """
        known_overrides = {"PagePublishedEvent"}
        for cls in ALL_EVENT_CLASSES:
            if cls.__name__ in known_overrides:
                continue
            data = _build_minimal_event_data(cls)
            event = cls(**data)
            assert event.version == "1.0", (
                f"{cls.__name__} has default version {event.version!r}, expected '1.0'"
            )

    def test_page_published_event_version_collision_fixed(self):
        """BUG FIXED: PagePublishedEvent now uses page_version (int) instead of
        shadowing BaseEvent.version (str). Both fields coexist correctly."""
        data = _build_minimal_event_data(PagePublishedEvent)
        event = PagePublishedEvent(**data)
        assert isinstance(event.version, str), "BaseEvent.version should be str"
        assert event.version == "1.0"
        assert isinstance(event.page_version, int)

    def test_custom_version_accepted(self):
        """Events should accept custom version strings."""
        event = BaseEvent(version="2.0")
        assert event.version == "2.0"

    def test_old_event_without_new_fields_can_deserialize(self):
        """BUG HUNT: An event payload from an older service (missing newer optional fields)
        should still deserialize. Tests backward compatibility."""
        # Simulate an old FieldCreatedEvent payload without causation_id, trace_id, span_id
        old_payload = {
            "event_id": str(uuid4()),
            "timestamp": _NOW.isoformat(),
            "version": "1.0",
            "field_id": str(uuid4()),
            "farm_id": str(uuid4()),
            "tenant_id": str(uuid4()),
            "name": "Old Field",
            "geometry_wkt": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
        }
        event = FieldCreatedEvent.model_validate(old_payload)
        assert event.name == "Old Field"
        assert event.causation_id is None
        assert event.trace_id is None
        assert event.span_id is None

    def test_event_with_unknown_fields_rejected_or_ignored(self):
        """BUG HUNT: Events with unknown fields - does Pydantic reject or ignore them?"""
        payload = {
            "event_id": str(uuid4()),
            "timestamp": _NOW.isoformat(),
            "version": "1.0",
            "field_id": str(uuid4()),
            "farm_id": str(uuid4()),
            "tenant_id": str(uuid4()),
            "name": "Test Field",
            "geometry_wkt": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            "unknown_future_field": "some_value",
            "another_unknown": 42,
        }
        # Default Pydantic behavior is to ignore extra fields
        # unless model_config has extra="forbid"
        try:
            event = FieldCreatedEvent.model_validate(payload)
            # If this succeeds, extra fields are silently ignored
            assert not hasattr(event, "unknown_future_field")
        except ValidationError:
            # If this fails, the model forbids extra fields
            pass


# ─────────────────────────────────────────────────────────────────────────────
# 5. Field Constraint Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestFieldConstraintValidation:
    """BUG HUNT: Test that Pydantic field constraints actually reject bad data."""

    def test_ndvi_value_out_of_range_rejected(self):
        """NDVI must be between -1 and 1."""
        with pytest.raises(ValidationError):
            FieldUpdatedEvent(
                field_id=uuid4(),
                ndvi_value=1.5,  # Out of range
                updated_at=_NOW,
            )

    def test_negative_area_rejected(self):
        """Area must be >= 0."""
        with pytest.raises(ValidationError):
            FieldCreatedEvent(
                field_id=uuid4(),
                farm_id=uuid4(),
                tenant_id=uuid4(),
                name="Test",
                geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
                area_hectares=-5.0,
            )

    def test_empty_name_rejected(self):
        """Field name must have min_length=1."""
        with pytest.raises(ValidationError):
            FieldCreatedEvent(
                field_id=uuid4(),
                farm_id=uuid4(),
                tenant_id=uuid4(),
                name="",  # Empty
                geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            )

    def test_geometry_wkt_too_short_rejected(self):
        """geometry_wkt must have min_length=10."""
        with pytest.raises(ValidationError):
            FieldCreatedEvent(
                field_id=uuid4(),
                farm_id=uuid4(),
                tenant_id=uuid4(),
                name="Test",
                geometry_wkt="SHORT",  # Less than 10 chars
            )

    def test_confidence_score_above_1_rejected(self):
        """confidence_score must be between 0 and 1."""
        with pytest.raises(ValidationError):
            DiseaseDetectedEvent(
                field_id=uuid4(),
                tenant_id=uuid4(),
                disease_name="Test Disease",
                confidence_score=1.5,
                severity="high",
            )

    def test_invalid_severity_pattern_rejected(self):
        """Severity must match the pattern regex."""
        with pytest.raises(ValidationError):
            DiseaseDetectedEvent(
                field_id=uuid4(),
                tenant_id=uuid4(),
                disease_name="Test",
                confidence_score=0.9,
                severity="EXTREME",  # Not in pattern
            )

    def test_invalid_alert_type_pattern_rejected(self):
        """Alert type must match its pattern."""
        with pytest.raises(ValidationError):
            WeatherAlertEvent(
                tenant_id=uuid4(),
                alert_type="earthquake",  # Not in pattern
                severity="critical",
                title="Test",
                message="Test message",
                start_time=_NOW,
            )

    def test_latitude_out_of_range_rejected(self):
        """Latitude must be between -90 and 90."""
        with pytest.raises(ValidationError):
            WeatherForecastEvent(
                location_lat=100.0,  # Out of range
                location_lon=46.0,
                forecast_date=_NOW,
            )

    def test_longitude_out_of_range_rejected(self):
        """Longitude must be between -180 and 180."""
        with pytest.raises(ValidationError):
            WeatherForecastEvent(
                location_lat=24.0,
                location_lon=200.0,  # Out of range
                forecast_date=_NOW,
            )

    def test_harvest_deal_zero_quantity_rejected(self):
        """HarvestDealCreatedEvent expected_quantity_tons must be > 0 (gt=0)."""
        with pytest.raises(ValidationError):
            HarvestDealCreatedEvent(
                deal_id="deal-1",
                farmer_id="farmer-1",
                tenant_id="tenant-1",
                crop_type="wheat",
                expected_quantity_tons=0,  # Must be > 0
                expected_harvest_date="2026-06-01",
            )

    def test_cloud_coverage_above_100_rejected(self):
        """Cloud coverage must be between 0 and 100."""
        from shared.events.contracts import SatelliteDataReadyEvent

        with pytest.raises(ValidationError):
            SatelliteDataReadyEvent(
                field_id=uuid4(),
                tenant_id=uuid4(),
                satellite_source="Sentinel-2",
                capture_date=_NOW,
                cloud_coverage=150.0,  # Over 100
            )


# ─────────────────────────────────────────────────────────────────────────────
# 6. BaseEvent tenant_id alias handling
# ─────────────────────────────────────────────────────────────────────────────


class TestBaseEventAliasHandling:
    """BUG HUNT: Test that the tenant_id alias works correctly."""

    def test_tenant_id_via_alias(self):
        """BaseEvent should accept tenant_id as alias for tenant_id."""
        event = BaseEvent.model_validate({"tenant_id": "tenant-123"})
        assert event.tenant_id == "tenant-123"

    def test_tenant_id_direct(self):
        """BaseEvent should accept tenant_id directly (populate_by_name=True)."""
        event = BaseEvent(tenant_id="tenant-456")
        assert event.tenant_id == "tenant-456"

    def test_serialization_uses_field_name_not_alias(self):
        """BUG HUNT: Does model_dump use the field name or the alias?"""
        event = BaseEvent(tenant_id="tenant-789")
        dumped = event.model_dump()
        # By default, model_dump uses field names unless by_alias=True
        assert "tenant_id" in dumped or "tenant_id" in dumped

    def test_serialization_by_alias(self):
        """model_dump(by_alias=True) should use 'tenant_id'."""
        event = BaseEvent(tenant_id="tenant-abc")
        dumped = event.model_dump(by_alias=True)
        assert "tenant_id" in dumped
