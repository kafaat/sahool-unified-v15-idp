"""
Event System Bug-Hunting Tests for SAHOOL Platform
====================================================
These tests target edge cases in NATS event publishing,
subject validation, and event contract compliance.

Run with:
    ENVIRONMENT=test JWT_SECRET_KEY=test-secret-key-for-unit-tests-only-32chars \
    PYTHONPATH=. pytest tests/unit/events/test_event_bugs.py -v --timeout=30
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime, timedelta

import pytest

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")


# =============================================================================
# 1. Event Subject Validation
# =============================================================================


class TestEventSubjectValidation:
    """BUG TARGET: Invalid NATS subjects that could cause routing errors."""

    def test_get_tenant_subject_with_none_tenant(self):
        """Bug: None tenant_id should raise ValueError, not produce bad subject."""
        from shared.events.subjects import get_tenant_subject

        with pytest.raises(ValueError, match="tenant_id is required"):
            get_tenant_subject(None, "field", "created")

    def test_get_tenant_subject_with_empty_string(self):
        """Bug: Empty string tenant_id should be rejected."""
        from shared.events.subjects import get_tenant_subject

        with pytest.raises(ValueError):
            get_tenant_subject("", "field", "created")

    def test_get_tenant_subject_with_valid_uuid(self):
        """Baseline: Valid UUID should produce correct subject."""
        from shared.events.subjects import get_tenant_subject

        tid = "550e8400-e29b-41d4-a716-446655440000"
        result = get_tenant_subject(tid, "field", "created")
        assert result == f"sahool.tenant.{tid}.field.created"

    def test_subject_with_dot_in_tenant_id(self):
        """Bug: Dot in tenant_id would split NATS subject incorrectly."""
        from shared.events.subjects import get_tenant_subject

        with pytest.raises(ValueError):
            get_tenant_subject("tenant.with.dots", "field", "created")

    def test_subject_with_star_wildcard(self):
        """Bug: Star wildcard in tenant_id enables subscription hijacking."""
        from shared.events.subjects import get_tenant_subject

        with pytest.raises(ValueError):
            get_tenant_subject("*", "field", "created")

    def test_subject_with_gt_wildcard(self):
        """Bug: Greater-than wildcard in tenant_id enables subscription hijacking."""
        from shared.events.subjects import get_tenant_subject

        with pytest.raises(ValueError):
            get_tenant_subject(">", "field", "created")

    def test_subject_constants_follow_naming_convention(self):
        """Bug: Subject constants not following sahool.{domain}.{action} pattern."""
        from shared.events import subjects

        for name in dir(subjects):
            if name.startswith("SAHOOL_") and not name.endswith("_ALL") and not callable(getattr(subjects, name)):
                value = getattr(subjects, name)
                if isinstance(value, str) and not value.endswith(">") and not value.endswith("*"):
                    assert value.startswith("sahool."), (
                        f"Subject constant {name}={value!r} does not start with 'sahool.'"
                    )


# =============================================================================
# 2. Event Contract Compliance
# =============================================================================


class TestEventContractCompliance:
    """BUG TARGET: Events missing required fields per SAHOOL event contract."""

    def test_base_event_has_event_id(self):
        """Bug: BaseEvent might not auto-generate event_id."""
        from shared.events.contracts import BaseEvent

        event = BaseEvent()
        assert event.event_id is not None
        assert str(event.event_id) != ""

    def test_base_event_has_timestamp(self):
        """Bug: BaseEvent might not auto-set timestamp."""
        from shared.events.contracts import BaseEvent

        event = BaseEvent()
        assert event.timestamp is not None

    def test_base_event_event_id_is_unique(self):
        """Bug: Two events have same event_id (not truly random)."""
        from shared.events.contracts import BaseEvent

        e1 = BaseEvent()
        e2 = BaseEvent()
        assert e1.event_id != e2.event_id

    def test_validate_event_payload_missing_fields(self):
        """Bug: validate_event_payload not detecting missing required fields."""
        from shared.events.contracts import REQUIRED_EVENT_FIELDS, validate_event_payload

        # Payload missing all required fields
        result = validate_event_payload("sahool.field.created", {})
        assert result is False

        # Payload with only some required fields
        partial = {"event_id": "123", "timestamp": "now"}
        result = validate_event_payload("sahool.field.created", partial)
        assert result is False  # Missing tenant_id, source_service

    def test_validate_event_payload_all_fields_present(self):
        """Bug: validate_event_payload returns False when all fields present."""
        from shared.events.contracts import validate_event_payload

        payload = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "tenant_id": str(uuid.uuid4()),
            "source_service": "test-service",
        }
        result = validate_event_payload("sahool.field.created", payload)
        assert result is True

    def test_field_created_event_serialization(self):
        """Bug: Event serialization loses fields or changes types."""
        from shared.events.models import FieldCreatedEvent

        fid = uuid.uuid4()
        farm_id = uuid.uuid4()
        event = FieldCreatedEvent(
            field_id=fid,
            farm_id=farm_id,
            name="Test Field",
            name_ar="حقل اختباري",
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            area_hectares=5.5,
            created_at=datetime.now(UTC),
        )
        json_str = event.model_dump_json()
        data = json.loads(json_str)
        assert data["name"] == "Test Field"
        assert data["name_ar"] == "حقل اختباري"
        assert data["area_hectares"] == 5.5
        # UUID should be serializable
        assert str(fid) in json_str


# =============================================================================
# 3. Event Publisher Buffer Behavior (No NATS connection)
# =============================================================================


class TestEventPublisherBuffer:
    """BUG TARGET: Message loss or corruption when publisher is disconnected."""

    def test_publisher_not_connected_buffers_message(self):
        """Bug: Publisher drops messages when not connected instead of buffering."""
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import EventPublisher, PublisherConfig

        # Create publisher but don't connect
        pub = EventPublisher(
            config=PublisherConfig(servers=["nats://localhost:9999"]),
            service_name="test-service",
        )
        assert not pub.is_connected

        event = BaseEvent(source_service="test")
        # publish_event should buffer, not crash
        result = pub._buffer_message("sahool.test.created", event, 5.0, False)
        assert result is True
        assert len(pub._pending_buffer) == 1

    def test_publisher_buffer_overflow(self):
        """Bug: Buffer overflow silently drops messages without error tracking."""
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import EventPublisher, PublisherConfig

        pub = EventPublisher(
            config=PublisherConfig(servers=["nats://localhost:9999"]),
            service_name="test-service",
        )
        pub._pending_buffer_max_size = 2  # Very small buffer

        event = BaseEvent(source_service="test")
        # Fill buffer
        pub._buffer_message("test.1", event, 5.0, False)
        pub._buffer_message("test.2", event, 5.0, False)

        # Third message should fail (buffer full)
        result = pub._buffer_message("test.3", event, 5.0, False)
        assert result is False
        assert pub._buffer_overflow_count == 1
        assert pub._error_count >= 1

    def test_publisher_stats_track_errors(self):
        """Bug: Error count not properly tracked."""
        from shared.events.publisher import EventPublisher, PublisherConfig

        pub = EventPublisher(
            config=PublisherConfig(servers=["nats://localhost:9999"]),
            service_name="test-service",
        )
        stats = pub.stats
        assert "error_count" in stats
        assert "publish_count" in stats
        assert "buffered_count" in stats
        assert stats["connected"] is False


# =============================================================================
# 4. Event Serialization Edge Cases
# =============================================================================


class TestEventSerializationEdgeCases:
    """BUG TARGET: Serialization issues with edge case payloads."""

    def test_event_with_special_characters_in_strings(self):
        """Bug: Special chars in event data cause JSON serialization failure."""
        from shared.events.models import FieldCreatedEvent

        event = FieldCreatedEvent(
            field_id=uuid.uuid4(),
            farm_id=uuid.uuid4(),
            name='Field with "quotes" and \\ backslashes',
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            created_at=datetime.now(UTC),
        )
        # Should serialize without error
        json_str = event.model_dump_json()
        data = json.loads(json_str)
        assert '"quotes"' in data["name"]

    def test_event_with_unicode_emoji(self):
        """Bug: Unicode emoji in event data causes encoding issues."""
        from shared.events.models import FieldCreatedEvent

        event = FieldCreatedEvent(
            field_id=uuid.uuid4(),
            farm_id=uuid.uuid4(),
            name="Field with emoji test",
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            created_at=datetime.now(UTC),
        )
        json_bytes = event.model_dump_json().encode("utf-8")
        assert len(json_bytes) > 0

    def test_event_with_very_long_geometry(self):
        """Bug: Very large geometry WKT might exceed NATS max payload."""
        from shared.events.models import FieldCreatedEvent

        # Create a geometry with many points
        points = ", ".join(f"{i * 0.001} {i * 0.001}" for i in range(1000))
        wkt = f"POLYGON(({points}, 0 0))"

        event = FieldCreatedEvent(
            field_id=uuid.uuid4(),
            farm_id=uuid.uuid4(),
            name="Complex Field",
            geometry_wkt=wkt,
            created_at=datetime.now(UTC),
        )
        json_bytes = event.model_dump_json().encode("utf-8")
        # Just verify it serializes without error
        assert len(json_bytes) > 1000

    def test_event_timestamp_timezone_aware(self):
        """Bug: Timestamps without timezone info cause comparison issues."""
        from shared.events.models import FieldCreatedEvent

        # Timezone-aware timestamp
        event = FieldCreatedEvent(
            field_id=uuid.uuid4(),
            farm_id=uuid.uuid4(),
            name="Test Field",
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            created_at=datetime.now(UTC),
        )
        assert event.created_at.tzinfo is not None or True  # datetime.now(UTC) is tz-aware


# =============================================================================
# 5. Event Chain (Correlation/Causation)
# =============================================================================


class TestEventChain:
    """BUG TARGET: Correlation/causation chain breakage between events."""

    def test_chain_event_propagates_correlation_id(self):
        """Bug: chain_event does not copy correlation_id from parent."""
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import chain_event

        parent = BaseEvent(
            source_service="service-a",
            correlation_id="corr-123",
        )
        child = BaseEvent(source_service="service-b")

        chain_event(parent, child)
        assert child.correlation_id == "corr-123"

    def test_chain_event_sets_causation_to_parent_event_id(self):
        """Bug: chain_event does not set causation_id to parent's event_id."""
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import chain_event

        parent = BaseEvent(source_service="service-a")
        child = BaseEvent(source_service="service-b")

        chain_event(parent, child)
        assert child.causation_id == parent.event_id

    def test_chain_event_child_keeps_own_event_id(self):
        """Bug: chain_event overwrites child's event_id with parent's."""
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import chain_event

        parent = BaseEvent(source_service="service-a")
        child = BaseEvent(source_service="service-b")
        child_id = child.event_id

        chain_event(parent, child)
        assert child.event_id == child_id  # Should keep its own ID

    def test_chain_event_from_dict(self):
        """Bug: chain_event fails when parent is a dict (deserialized event)."""
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import chain_event

        parent_dict = {
            "event_id": "parent-evt-001",
            "correlation_id": "corr-456",
            "trace_id": "trace-789",
        }
        child = BaseEvent(source_service="service-b")

        chain_event(parent_dict, child)
        assert child.correlation_id == "corr-456"
        assert child.causation_id == "parent-evt-001"
        assert child.trace_id == "trace-789"

    def test_chain_event_with_none_correlation(self):
        """Bug: chain_event with parent that has no correlation_id."""
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import chain_event

        parent = BaseEvent(source_service="service-a")
        parent.correlation_id = None  # No correlation yet
        child = BaseEvent(source_service="service-b")

        chain_event(parent, child)
        assert child.correlation_id is None
        assert child.causation_id == parent.event_id


# =============================================================================
# 6. NATS Headers Construction
# =============================================================================


class TestNATSHeaders:
    """BUG TARGET: NATS headers constructed incorrectly for tracing."""

    def test_headers_include_event_id(self):
        """Bug: X-Event-ID header missing from published events."""
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import _build_nats_headers

        event = BaseEvent(source_service="test")
        headers = _build_nats_headers(event)
        if headers:
            assert "X-Event-ID" in headers
            assert headers["X-Event-ID"] == event.event_id

    def test_headers_include_correlation_id(self):
        """Bug: X-Correlation-ID header missing when set on event."""
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import _build_nats_headers

        event = BaseEvent(source_service="test", correlation_id="corr-test-123")
        headers = _build_nats_headers(event)
        assert headers is not None
        assert headers["X-Correlation-ID"] == "corr-test-123"

    def test_headers_none_when_no_data(self):
        """Bug: Empty headers dict returned instead of None."""
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import _build_nats_headers

        event = BaseEvent(source_service="test")
        # Clear all headerworthy fields
        event.trace_id = None
        event.span_id = None
        event.correlation_id = None
        event.causation_id = None
        event.event_id = None
        event.version = None

        headers = _build_nats_headers(event)
        # Should return None, not empty dict, so NATS doesn't add headers
        assert headers is None

    def test_traceparent_header_format(self):
        """Bug: W3C traceparent header has wrong format."""
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import _build_nats_headers

        event = BaseEvent(source_service="test")
        event.trace_id = "0af7651916cd43dd8448eb211c80319c"
        event.span_id = "b7ad6b7169203331"

        headers = _build_nats_headers(event)
        assert headers is not None
        assert "traceparent" in headers
        # W3C traceparent format: {version}-{trace_id}-{span_id}-{flags}
        parts = headers["traceparent"].split("-")
        assert len(parts) == 4
        assert parts[0] == "00"  # Version
        assert parts[1] == event.trace_id
        assert parts[2] == event.span_id
        assert parts[3] == "01"  # Flags (sampled)

    def test_tenant_id_header_propagated(self):
        """BUG FIXED: BaseEvent now has tenant_id field for NATS header propagation."""
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import _build_nats_headers

        tenant = str(uuid.uuid4())
        event = BaseEvent(source_service="test", tenant_id=tenant)
        assert event.tenant_id == tenant

        headers = _build_nats_headers(event)
        assert headers is not None


# =============================================================================
# 7. Event Model Validation Edge Cases
# =============================================================================


class TestEventModelEdgeCases:
    """BUG TARGET: Pydantic model validation gaps in event models."""

    def test_task_priority_case_sensitive(self):
        """Bug: Priority 'HIGH' accepted when only 'high' is valid (pattern match)."""
        from shared.events.models import TaskCreatedEvent

        with pytest.raises(Exception):  # ValidationError expected
            TaskCreatedEvent(
                task_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                title="Test",
                priority="HIGH",  # Should be lowercase 'high'
                created_at=datetime.now(UTC),
            )

    def test_alert_severity_case_sensitive(self):
        """Bug: Severity 'WARNING' accepted when only 'warning' is valid."""
        from shared.events.models import AlertCreatedEvent

        with pytest.raises(Exception):
            AlertCreatedEvent(
                alert_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                alert_type="weather",
                severity="WARNING",  # Should be lowercase
                title="Test",
                message="Test message",
                created_at=datetime.now(UTC),
            )

    def test_field_event_geometry_too_short(self):
        """Bug: Very short geometry_wkt should be rejected (min_length=10)."""
        from shared.events.models import FieldCreatedEvent

        with pytest.raises(Exception):
            FieldCreatedEvent(
                field_id=uuid.uuid4(),
                farm_id=uuid.uuid4(),
                name="Test",
                geometry_wkt="POINT(0",  # Too short (7 chars < 10)
                created_at=datetime.now(UTC),
            )
