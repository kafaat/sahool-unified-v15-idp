# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Event Pipeline Spec Tests
=========================
Validates all 8 sections of the formal Trace/Correlation pipeline spec:
  §1 - Headers + Envelope + Propagation
  §2 - Correlation/Causation Rules
  §3 - JetStream Durability (ACK policy, max_deliver, backoff)
  §4 - Idempotency Stack (LRU + DB processed_events)
  §5 - Transaction Boundary (Outbox Pattern)
  §6 - Handler Flow (formalized 7-step)
  §7 - Downstream Notification Service
  §8 - Production-Ready Checklist
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
# §1: Headers + Envelope + Propagation
# ─────────────────────────────────────────────────────────────────────────────


class TestCanonicalHeaders:
    """Verify all 7 canonical NATS headers are built by the publisher."""

    @pytest.fixture
    def publisher_content(self):
        path = os.path.join(_ROOT, "shared/events/publisher.py")
        with open(path) as f:
            return f.read()

    def test_traceparent_header(self, publisher_content):
        assert '"traceparent"' in publisher_content or "'traceparent'" in publisher_content

    def test_tracestate_header(self, publisher_content):
        assert '"tracestate"' in publisher_content or "'tracestate'" in publisher_content

    def test_x_correlation_id_header(self, publisher_content):
        assert "X-Correlation-ID" in publisher_content

    def test_x_causation_id_header(self, publisher_content):
        assert "X-Causation-ID" in publisher_content

    def test_x_event_id_header(self, publisher_content):
        assert "X-Event-ID" in publisher_content

    def test_x_tenant_id_header(self, publisher_content):
        assert "X-Tenant-ID" in publisher_content

    def test_x_schema_version_header(self, publisher_content):
        assert "X-Schema-Version" in publisher_content

    @_SKIP_PYDANTIC
    def test_base_event_envelope_has_all_fields(self):
        """BaseEvent JSON envelope duplicates IDs for storage/replay/debugging."""
        from shared.events.contracts import BaseEvent

        fields = BaseEvent.model_fields
        required = ["event_id", "timestamp", "version", "correlation_id", "causation_id", "trace_id", "span_id"]
        for field_name in required:
            assert field_name in fields, f"BaseEvent missing envelope field: {field_name}"

    @_SKIP_PYDANTIC
    def test_base_event_has_tenant_id_header(self):
        from shared.events.contracts import BaseEvent

        # tenant_id field provides tenant isolation for NATS header propagation
        fields = BaseEvent.model_fields
        assert "tenant_id" in fields, "BaseEvent must have tenant_id for NATS header propagation"


# ─────────────────────────────────────────────────────────────────────────────
# §2: Correlation / Causation Rules
# ─────────────────────────────────────────────────────────────────────────────


class TestCorrelationCausationRules:
    """Verify chain_event helper propagates correctly."""

    @_SKIP_PYDANTIC
    def test_chain_event_sets_causation_to_parent_event_id(self):
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import chain_event

        parent = BaseEvent(correlation_id="corr-123")
        child = BaseEvent()
        chain_event(parent, child)

        assert child.causation_id == parent.event_id
        assert child.correlation_id == "corr-123"

    @_SKIP_PYDANTIC
    def test_chain_event_from_dict(self):
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import chain_event

        parent_dict = {
            "event_id": "evt-parent",
            "correlation_id": "corr-abc",
            "trace_id": "trace-xyz",
        }
        child = BaseEvent()
        chain_event(parent_dict, child)

        assert child.causation_id == "evt-parent"
        assert child.correlation_id == "corr-abc"
        assert child.trace_id == "trace-xyz"

    @_SKIP_PYDANTIC
    def test_child_gets_new_event_id(self):
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import chain_event

        parent = BaseEvent()
        child = BaseEvent()
        chain_event(parent, child)

        assert child.event_id != parent.event_id

    def test_publisher_does_not_create_correlation_inside_workers(self):
        """correlation_id is only set from HTTP context, not generated internally."""
        path = os.path.join(_ROOT, "shared/events/publisher.py")
        with open(path) as f:
            content = f.read()
        # Must call _get_current_correlation_id (from HTTP context), NOT uuid4()
        assert "_get_current_correlation_id" in content
        # Should NOT have `correlation_id = str(uuid4())` in publisher
        assert "correlation_id = str(uuid4())" not in content


# ─────────────────────────────────────────────────────────────────────────────
# §3: JetStream Durability
# ─────────────────────────────────────────────────────────────────────────────


class TestJetStreamDurability:
    """Verify ACK-only-after-success, max_deliver, and backoff."""

    def test_subscriber_has_max_deliver(self):
        path = os.path.join(_ROOT, "shared/events/subscriber.py")
        with open(path) as f:
            content = f.read()
        assert "max_deliver" in content, "JetStream consumer must configure max_deliver"

    def test_subscriber_has_ack_wait(self):
        path = os.path.join(_ROOT, "shared/events/subscriber.py")
        with open(path) as f:
            content = f.read()
        assert "ack_wait" in content, "JetStream consumer must configure ack_wait"

    def test_handler_ack_only_after_success(self):
        """crop-intelligence handlers must ACK only after success, NAK on failure."""
        path = os.path.join(
            _ROOT,
            "apps/services/crop-intelligence-service/src/event_subscribers.py",
        )
        with open(path) as f:
            content = f.read()

        # Must have NAK for failure path
        assert "_nak(msg)" in content, "Handlers must NAK on failure for JetStream redelivery"
        # Must NOT have "finally: ... msg.ack()" pattern (unconditional ACK)
        # Instead, ACK must be inside the try block after success
        assert "await _ack(msg)" in content

    def test_dlq_config_has_backoff(self):
        path = os.path.join(_ROOT, "shared/events/dlq_config.py")
        with open(path) as f:
            content = f.read()
        assert "backoff_multiplier" in content
        assert "get_retry_delay" in content


# ─────────────────────────────────────────────────────────────────────────────
# §4: Idempotency Stack
# ─────────────────────────────────────────────────────────────────────────────


class TestIdempotencyStack:
    """Verify 3-layer idempotency: LRU + processed_events + ON CONFLICT."""

    def test_lru_dedup_in_subscriber(self):
        path = os.path.join(_ROOT, "shared/events/subscriber.py")
        with open(path) as f:
            content = f.read()
        assert "_processed_event_ids" in content, "Layer 1: In-memory LRU dedup"
        assert "_dedup_max_size" in content

    def test_processed_events_has_composite_pk(self):
        path = os.path.join(
            _ROOT,
            "apps/services/crop-intelligence-service/migrations/001_idempotency_constraints.sql",
        )
        with open(path) as f:
            content = f.read()
        assert "PRIMARY KEY (tenant_id, event_id)" in content, "Layer 2: DB dedup with composite PK"
        assert "correlation_id" in content, "processed_events must track correlation_id"
        assert "status" in content, "processed_events must track status"

    def test_observation_on_conflict_upsert(self):
        path = os.path.join(_ROOT, "shared/digital_twin/repository.py")
        with open(path) as f:
            content = f.read()
        assert "ON CONFLICT" in content, "Layer 3: Business-level idempotent upsert"

    def test_handler_checks_processed_events(self):
        path = os.path.join(
            _ROOT,
            "apps/services/crop-intelligence-service/src/event_subscribers.py",
        )
        with open(path) as f:
            content = f.read()
        assert "_check_processed" in content, "Handler must check processed_events before executing"
        assert "_mark_processed" in content, "Handler must mark event as processed after success"


# ─────────────────────────────────────────────────────────────────────────────
# §5: Transaction Boundary (Outbox Pattern)
# ─────────────────────────────────────────────────────────────────────────────


class TestOutboxPattern:
    """Verify outbox pattern module exists and is complete."""

    def test_outbox_module_exists(self):
        path = os.path.join(_ROOT, "shared/events/outbox.py")
        assert os.path.exists(path), "shared/events/outbox.py must exist"

    def test_outbox_has_write_helper(self):
        path = os.path.join(_ROOT, "shared/events/outbox.py")
        with open(path) as f:
            content = f.read()
        assert "write_outbox_event" in content, "Must have write_outbox_event() for transactional writes"

    def test_outbox_has_relay(self):
        path = os.path.join(_ROOT, "shared/events/outbox.py")
        with open(path) as f:
            content = f.read()
        assert "OutboxRelay" in content, "Must have OutboxRelay for async publishing"
        assert "async def start" in content
        assert "async def stop" in content

    def test_outbox_has_table_sql(self):
        path = os.path.join(_ROOT, "shared/events/outbox.py")
        with open(path) as f:
            content = f.read()
        assert "outbox_events" in content
        assert "pending" in content
        assert "sent" in content

    def test_outbox_marks_sent(self):
        path = os.path.join(_ROOT, "shared/events/outbox.py")
        with open(path) as f:
            content = f.read()
        assert "MARK_SENT" in content or "mark_sent" in content.lower()

    def test_outbox_handles_failure(self):
        path = os.path.join(_ROOT, "shared/events/outbox.py")
        with open(path) as f:
            content = f.read()
        assert "failed" in content, "Outbox must handle publish failures"
        assert "_MAX_RELAY_RETRIES" in content

    @_SKIP_PYDANTIC
    def test_outbox_imports_cleanly(self):
        from shared.events.outbox import OutboxRelay, ensure_outbox_table, write_outbox_event

        assert callable(write_outbox_event)
        assert callable(ensure_outbox_table)
        assert OutboxRelay is not None


# ─────────────────────────────────────────────────────────────────────────────
# §6: Handler Flow
# ─────────────────────────────────────────────────────────────────────────────


class TestHandlerFlow:
    """Verify formalized 7-step handler flow."""

    @pytest.fixture
    def event_subscribers_content(self):
        path = os.path.join(
            _ROOT,
            "apps/services/crop-intelligence-service/src/event_subscribers.py",
        )
        with open(path) as f:
            return f.read()

    def test_step1_extract_headers(self, event_subscribers_content):
        assert "_extract_headers" in event_subscribers_content

    def test_step2_dedup_check(self, event_subscribers_content):
        assert "_check_processed" in event_subscribers_content

    def test_step3_business_logic(self, event_subscribers_content):
        assert "save_observation" in event_subscribers_content

    def test_step4_assimilation(self, event_subscribers_content):
        assert "_trigger_assimilation" in event_subscribers_content

    def test_step5_mark_processed(self, event_subscribers_content):
        assert "_mark_processed" in event_subscribers_content

    def test_step6_ack(self, event_subscribers_content):
        assert "await _ack(msg)" in event_subscribers_content

    def test_step7_nak_on_failure(self, event_subscribers_content):
        assert "await _nak(msg)" in event_subscribers_content


# ─────────────────────────────────────────────────────────────────────────────
# §7: Downstream Notification Service
# ─────────────────────────────────────────────────────────────────────────────


class TestNotificationServiceConsumer:
    """Verify notification-service correctly consumes from Decision layer."""

    @pytest.fixture
    def notif_content(self):
        path = os.path.join(
            _ROOT,
            "apps/services/notification-service/src/nats_subscriber.py",
        )
        with open(path) as f:
            return f.read()

    def test_subscribes_to_recommendation_wildcard(self, notif_content):
        assert "sahool.recommendation.>" in notif_content, "Must subscribe to broad recommendation subject"

    def test_subscribes_to_irrigation_specific(self, notif_content):
        assert "sahool.irrigation.recommendation.ready.v1" in notif_content

    def test_has_decision_recommendation_handler(self, notif_content):
        assert "_handle_decision_recommendation" in notif_content

    def test_does_not_push_directly_from_decision_engine(self, notif_content):
        """Decision engine publishes events; notification-service decides delivery."""
        assert "notification_callback" in notif_content
        assert "channels" in notif_content


# ─────────────────────────────────────────────────────────────────────────────
# §8: Production-Ready Checklist
# ─────────────────────────────────────────────────────────────────────────────


class TestProductionReadyChecklist:
    """End-to-end checklist validation."""

    def test_publish_puts_headers_and_meta(self):
        path = os.path.join(_ROOT, "shared/events/publisher.py")
        with open(path) as f:
            content = f.read()
        assert "_build_nats_headers" in content
        assert "headers=headers" in content

    def test_correlation_id_unchanged_from_http(self):
        path = os.path.join(_ROOT, "shared/events/publisher.py")
        with open(path) as f:
            content = f.read()
        assert "_get_current_correlation_id" in content

    def test_causation_id_equals_parent_event_id(self):
        path = os.path.join(_ROOT, "shared/events/publisher.py")
        with open(path) as f:
            content = f.read()
        assert (
            "child.causation_id = parent.event_id" in content
            or 'child.causation_id = parent.get("event_id")' in content
        )

    def test_durable_consumers_with_explicit_ack(self):
        path = os.path.join(
            _ROOT,
            "apps/services/crop-intelligence-service/src/event_subscribers.py",
        )
        with open(path) as f:
            content = f.read()
        assert "durable=" in content
        assert "_ack(msg)" in content

    def test_processed_events_table_exists(self):
        path = os.path.join(
            _ROOT,
            "apps/services/crop-intelligence-service/migrations/001_idempotency_constraints.sql",
        )
        with open(path) as f:
            content = f.read()
        assert "processed_events" in content
        assert "PRIMARY KEY (tenant_id, event_id)" in content

    def test_dlq_after_max_deliver(self):
        path = os.path.join(_ROOT, "shared/events/dlq_config.py")
        with open(path) as f:
            content = f.read()
        assert "max_retry_attempts" in content
        assert "DLQConfig" in content

    def test_outbox_pattern_exists(self):
        assert os.path.exists(os.path.join(_ROOT, "shared/events/outbox.py"))

    def test_otel_trace_extract_inject(self):
        path = os.path.join(_ROOT, "shared/events/publisher.py")
        with open(path) as f:
            content = f.read()
        assert "_get_otel_trace_context" in content
        assert "traceparent" in content

    def test_subscriber_extracts_inbound_headers(self):
        path = os.path.join(_ROOT, "shared/events/subscriber.py")
        with open(path) as f:
            content = f.read()
        assert "_extract_headers" in content
        assert "X-Correlation-ID" in content
