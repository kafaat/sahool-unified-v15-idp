# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Architecture Conformance Tests
==============================
Tests validating the critical architecture fixes from the conformance audit:
  C1 - Durable consumers + ensure_streams() in crop-intelligence-service
  C2 - JetStream stream definitions
  C3 - Event_id deduplication in subscriber
  C4 - Observation idempotent upsert
  C5 - BaseEvent causation_id / trace_id / span_id fields
  H1 - Irrigation recommendation consumer in notification-service
  H3 - NDVI observation → assimilation trigger chain
  H4 - Correlation_id auto-propagation in publisher
  M1 - OTel trace context injection in NATS headers
"""

from __future__ import annotations

import os

import pytest

try:
    import pydantic  # noqa: F401

    _HAS_PYDANTIC = True
except ImportError:
    _HAS_PYDANTIC = False

_SKIP_PYDANTIC = pytest.mark.skipif(not _HAS_PYDANTIC, reason="pydantic not available")
_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


# ─────────────────────────────────────────────────────────────────────────────
# C5: BaseEvent has causation_id, trace_id, span_id
# ─────────────────────────────────────────────────────────────────────────────


class TestBaseEventEnvelope:
    """Verify the canonical BaseEvent envelope is complete."""

    @_SKIP_PYDANTIC
    def test_base_event_has_causation_id(self):
        from shared.events.contracts import BaseEvent

        fields = BaseEvent.model_fields
        assert "causation_id" in fields, "BaseEvent must have causation_id for event chaining"

    @_SKIP_PYDANTIC
    def test_base_event_has_trace_id(self):
        from shared.events.contracts import BaseEvent

        fields = BaseEvent.model_fields
        assert "trace_id" in fields, "BaseEvent must have trace_id for OTel correlation"

    @_SKIP_PYDANTIC
    def test_base_event_has_span_id(self):
        from shared.events.contracts import BaseEvent

        fields = BaseEvent.model_fields
        assert "span_id" in fields, "BaseEvent must have span_id for OTel correlation"

    @_SKIP_PYDANTIC
    def test_base_event_causation_id_optional(self):
        from shared.events.contracts import BaseEvent

        evt = BaseEvent()
        assert evt.causation_id is None
        assert evt.trace_id is None
        assert evt.span_id is None

    @_SKIP_PYDANTIC
    def test_base_event_causation_id_set(self):
        from shared.events.contracts import BaseEvent

        parent = BaseEvent()
        child = BaseEvent(
            causation_id=parent.event_id,
            correlation_id=parent.correlation_id or parent.event_id,
        )
        assert child.causation_id == parent.event_id

    @_SKIP_PYDANTIC
    def test_base_event_has_event_id_auto_generated(self):
        from shared.events.contracts import BaseEvent

        a = BaseEvent()
        b = BaseEvent()
        assert a.event_id != b.event_id, "event_id should be unique per instance"

    @_SKIP_PYDANTIC
    def test_child_event_inherits_envelope_fields(self):
        from shared.events.contracts import FieldCreatedEvent
        from uuid import uuid4

        evt = FieldCreatedEvent(
            field_id=uuid4(),
            farm_id=uuid4(),
            tenant_id=uuid4(),
            name="Test",
            geometry_wkt="POLYGON((0 0,1 0,1 1,0 1,0 0))",
            causation_id="parent-event-123",
            trace_id="00-abc123-def456-01",
        )
        assert evt.causation_id == "parent-event-123"
        assert evt.trace_id == "00-abc123-def456-01"


# ─────────────────────────────────────────────────────────────────────────────
# C2: JetStream stream definitions
# ─────────────────────────────────────────────────────────────────────────────


class TestJetStreamStreams:
    """Verify JetStream stream definitions are complete (file-level checks for pydantic-free env)."""

    @pytest.fixture
    def streams_content(self):
        path = os.path.join(_ROOT, "shared/events/streams.py")
        with open(path) as f:
            return f.read()

    def test_streams_module_exists(self, streams_content):
        assert "STREAMS" in streams_content
        assert "ensure_streams" in streams_content
        assert "StreamDef" in streams_content

    def test_all_domains_have_streams(self, streams_content):
        expected = [
            "SAHOOL_FIELD",
            "SAHOOL_WEATHER",
            "SAHOOL_INTELLIGENCE",
            "SAHOOL_VISION",
            "SAHOOL_TERRAIN",
            "SAHOOL_EDGE",
            "SAHOOL_BUSINESS",
            "SAHOOL_AGENT",
        ]
        for name in expected:
            assert name in streams_content, f"Missing stream definition: {name}"

    def test_field_stream_covers_satellite(self, streams_content):
        assert "sahool.satellite" in streams_content, "SAHOOL_FIELD must cover satellite subjects"
        assert "sahool.field" in streams_content, "SAHOOL_FIELD must cover field subjects"

    def test_intelligence_stream_covers_calibration(self, streams_content):
        assert "sahool.calibration" in streams_content
        assert "sahool.irrigation" in streams_content

    def test_streams_have_dedup_window(self, streams_content):
        assert "duplicate_window_seconds" in streams_content, "Streams must define dedup window"

    def test_business_stream_has_long_retention(self, streams_content):
        # 90 days = 90 * 86400 = 7776000
        assert "90 * 86400" in streams_content, "Business stream needs 90-day retention for audit"


# ─────────────────────────────────────────────────────────────────────────────
# C1: Durable consumers in crop-intelligence-service
# ─────────────────────────────────────────────────────────────────────────────


class TestDurableConsumers:
    """Verify crop-intelligence-service uses durable consumers."""

    def test_event_subscribers_has_durable_names(self):
        source_path = os.path.join(
            _ROOT,
            "apps/services/crop-intelligence-service/src/event_subscribers.py",
        )
        with open(source_path) as f:
            content = f.read()

        assert "durable=" in content, "event_subscribers.py must use durable= param"
        assert "_DURABLE_NDVI" in content, "Must define durable name for NDVI consumer"
        assert "_DURABLE_CALIBRATION" in content, "Must define durable name for calibration consumer"
        assert "_DURABLE_WEATHER" in content, "Must define durable name for weather consumer"

    def test_event_subscribers_has_queue_group(self):
        source_path = os.path.join(
            _ROOT,
            "apps/services/crop-intelligence-service/src/event_subscribers.py",
        )
        with open(source_path) as f:
            content = f.read()

        assert "queue=" in content, "Must use queue group for load-balanced consumption"

    def test_handlers_ack_messages(self):
        source_path = os.path.join(
            _ROOT,
            "apps/services/crop-intelligence-service/src/event_subscribers.py",
        )
        with open(source_path) as f:
            content = f.read()

        assert "msg.ack()" in content, "Handlers must explicitly ACK JetStream messages"

    def test_calibration_handler_reloads_params(self):
        source_path = os.path.join(
            _ROOT,
            "apps/services/crop-intelligence-service/src/event_subscribers.py",
        )
        with open(source_path) as f:
            content = f.read()

        assert "calibrated_params" in content, "Calibration handler must reload params into app_state"

    def test_weather_handler_caches_forecast(self):
        source_path = os.path.join(
            _ROOT,
            "apps/services/crop-intelligence-service/src/event_subscribers.py",
        )
        with open(source_path) as f:
            content = f.read()

        assert "weather_cache" in content, "Weather handler must cache forecast in app_state"


# ─────────────────────────────────────────────────────────────────────────────
# C3: Event_id deduplication in subscriber
# ─────────────────────────────────────────────────────────────────────────────


class TestEventIdDedup:
    """Verify in-memory event_id deduplication in EventSubscriber."""

    def test_subscriber_has_dedup_dict(self):
        source_path = os.path.join(_ROOT, "shared/events/subscriber.py")
        with open(source_path) as f:
            content = f.read()

        assert "_processed_event_ids" in content, "Subscriber must track processed event_ids"

    def test_subscriber_stats_include_dedup(self):
        source_path = os.path.join(_ROOT, "shared/events/subscriber.py")
        with open(source_path) as f:
            content = f.read()

        assert "dedup_hit_count" in content, "Stats must include dedup_hit_count"


# ─────────────────────────────────────────────────────────────────────────────
# C4: Observation idempotent upsert
# ─────────────────────────────────────────────────────────────────────────────


class TestObservationIdempotency:
    """Verify field_observation uses ON CONFLICT upsert."""

    def test_observation_sql_uses_on_conflict(self):
        source_path = os.path.join(_ROOT, "shared/digital_twin/repository.py")
        with open(source_path) as f:
            content = f.read()

        assert "ON CONFLICT" in content, "field_observation INSERT must use ON CONFLICT"
        assert "DO UPDATE SET" in content, "Must upsert on conflict, not ignore"

    def test_migration_exists(self):
        migration_path = os.path.join(
            _ROOT,
            "apps/services/crop-intelligence-service/migrations/001_idempotency_constraints.sql",
        )
        assert os.path.exists(migration_path), "Idempotency migration must exist"

        with open(migration_path) as f:
            content = f.read()

        assert "uq_field_observation_natural_key" in content
        assert "processed_events" in content


# ─────────────────────────────────────────────────────────────────────────────
# H1: Irrigation recommendation consumer in notification-service
# ─────────────────────────────────────────────────────────────────────────────


class TestIrrigationConsumer:
    """Verify notification-service consumes irrigation recommendation events."""

    @pytest.fixture
    def notif_subscriber_content(self):
        path = os.path.join(
            _ROOT,
            "apps/services/notification-service/src/nats_subscriber.py",
        )
        with open(path) as f:
            return f.read()

    def test_subscribes_to_irrigation_recommendation(self, notif_subscriber_content):
        assert "sahool.irrigation.recommendation.ready.v1" in notif_subscriber_content, (
            "notification-service must subscribe to irrigation recommendation subject"
        )

    def test_has_irrigation_handler(self, notif_subscriber_content):
        assert "_handle_irrigation_recommendation" in notif_subscriber_content, (
            "Must have dedicated handler for irrigation recommendations"
        )

    def test_handler_creates_notification(self, notif_subscriber_content):
        assert "irrigation_reminder" in notif_subscriber_content, (
            "Handler must create irrigation_reminder notification type"
        )


# ─────────────────────────────────────────────────────────────────────────────
# H3: NDVI observation → assimilation trigger chain
# ─────────────────────────────────────────────────────────────────────────────


class TestAssimilationChain:
    """Verify NDVI handler triggers assimilation after observation save."""

    @pytest.fixture
    def event_subscribers_content(self):
        path = os.path.join(
            _ROOT,
            "apps/services/crop-intelligence-service/src/event_subscribers.py",
        )
        with open(path) as f:
            return f.read()

    def test_ndvi_handler_triggers_assimilation(self, event_subscribers_content):
        assert "_trigger_assimilation" in event_subscribers_content, (
            "NDVI handler must trigger assimilation after observation save"
        )

    def test_assimilation_uses_pipeline(self, event_subscribers_content):
        assert "TwinPipeline" in event_subscribers_content, "Assimilation trigger must use TwinPipeline"

    def test_assimilation_is_best_effort(self, event_subscribers_content):
        # Must not fail the handler on assimilation error
        assert "assimilation_trigger_failed" in event_subscribers_content, (
            "Assimilation must log failure without failing the handler"
        )


# ─────────────────────────────────────────────────────────────────────────────
# H4: Correlation_id auto-propagation in publisher
# ─────────────────────────────────────────────────────────────────────────────


class TestCorrelationPropagation:
    """Verify publisher auto-propagates correlation_id from HTTP context."""

    @pytest.fixture
    def publisher_content(self):
        path = os.path.join(_ROOT, "shared/events/publisher.py")
        with open(path) as f:
            return f.read()

    def test_publisher_propagates_correlation_id(self, publisher_content):
        assert "_get_current_correlation_id" in publisher_content, (
            "Publisher must auto-extract correlation_id from HTTP context"
        )

    def test_publisher_sets_correlation_id_on_event(self, publisher_content):
        assert "event.correlation_id" in publisher_content, (
            "Publisher must set correlation_id on event before publishing"
        )


# ─────────────────────────────────────────────────────────────────────────────
# M1: OTel trace context injection in NATS headers
# ─────────────────────────────────────────────────────────────────────────────


class TestOTelTraceInjection:
    """Verify publisher injects OTel trace context into NATS message headers."""

    @pytest.fixture
    def publisher_content(self):
        path = os.path.join(_ROOT, "shared/events/publisher.py")
        with open(path) as f:
            return f.read()

    def test_publisher_extracts_otel_context(self, publisher_content):
        assert "_get_otel_trace_context" in publisher_content, (
            "Publisher must extract OTel trace context from current span"
        )

    def test_publisher_builds_nats_headers(self, publisher_content):
        assert "_build_nats_headers" in publisher_content, "Publisher must build NATS headers with trace context"

    def test_publisher_injects_traceparent(self, publisher_content):
        assert "traceparent" in publisher_content, "Publisher must inject W3C traceparent header"

    def test_publisher_passes_headers_to_publish(self, publisher_content):
        assert "headers=headers" in publisher_content, (
            "Publisher must pass headers to _publish_core and _publish_jetstream"
        )


# ─────────────────────────────────────────────────────────────────────────────
# C1 Completion: ensure_streams() called in service lifespan
# ─────────────────────────────────────────────────────────────────────────────


class TestEnsureStreamsCalled:
    """Verify crop-intelligence-service calls ensure_streams() on startup."""

    def test_main_calls_ensure_streams(self):
        path = os.path.join(
            _ROOT,
            "apps/services/crop-intelligence-service/src/main.py",
        )
        with open(path) as f:
            content = f.read()

        assert "ensure_streams" in content, "main.py must call ensure_streams() during startup"
        assert "from shared.events.streams import ensure_streams" in content, (
            "Must import ensure_streams from shared.events.streams"
        )
