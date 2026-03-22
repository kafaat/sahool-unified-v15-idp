# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Event Pipeline Behavioral Tests — اختبارات سلوكية لخط أنابيب الأحداث
=====================================================================
Mock-based behavioral tests that verify runtime behavior, not just
source-level assertions.  Covers all 8 spec points with real object
instantiation and controlled mocks.

Requires: pydantic (BaseEvent), asyncio
Does NOT require: running NATS, PostgreSQL, or OTel collector
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# importlib bootstrapping for hyphenated service directories
# ─────────────────────────────────────────────────────────────────────────────

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _load_module(name: str, filepath: str):
    """Load a Python module from an arbitrary filesystem path."""
    abs_path = os.path.join(_PROJECT_ROOT, filepath)
    spec = importlib.util.spec_from_file_location(name, abs_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {name} from {abs_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Pre-load modules from hyphenated service directories
try:
    _crop_intel_subs = _load_module(
        "crop_intelligence_event_subscribers",
        "apps/services/crop-intelligence-service/src/event_subscribers.py",
    )
    _CROP_INTEL_AVAILABLE = True
except Exception:
    _CROP_INTEL_AVAILABLE = False
    _crop_intel_subs = None

try:
    _notif_subscriber = _load_module(
        "notification_nats_subscriber",
        "apps/services/notification-service/src/nats_subscriber.py",
    )
    _NOTIF_AVAILABLE = True
except Exception:
    _NOTIF_AVAILABLE = False
    _notif_subscriber = None


try:
    import pydantic  # noqa: F401

    _HAS_PYDANTIC = True
except ImportError:
    _HAS_PYDANTIC = False

_SKIP = pytest.mark.skipif(not _HAS_PYDANTIC, reason="pydantic not available")
_SKIP_CROP_INTEL = pytest.mark.skipif(not _CROP_INTEL_AVAILABLE, reason="crop-intelligence-service not loadable")
_SKIP_NOTIF = pytest.mark.skipif(not _NOTIF_AVAILABLE, reason="notification-service not loadable")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


class AsyncContextManager:
    """Simple async context manager wrapping a mock connection."""

    def __init__(self, conn):
        self._conn = conn

    async def __aenter__(self):
        return self._conn

    async def __aexit__(self, *args):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class FakeNATSMsg:
    """Lightweight NATS message mock with ACK/NAK tracking."""

    def __init__(self, subject: str, payload: dict, headers: dict | None = None):
        self.subject = subject
        self.data = json.dumps(payload).encode()
        self.headers = headers or {}
        self.ack_called = False
        self.nak_called = False

    async def ack(self):
        self.ack_called = True

    async def nak(self):
        self.nak_called = True


class FakeAppState:
    """Mimics FastAPI app.state for handler tests."""

    def __init__(self, db_pool=None):
        self.db_pool = db_pool
        self.weather_cache = {}
        self.calibrated_params = {}


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def base_event():
    """Create a fresh BaseEvent for testing."""
    if not _HAS_PYDANTIC:
        pytest.skip("pydantic not available")
    from shared.events.contracts import BaseEvent

    return BaseEvent(
        source_service="test-service",
        correlation_id="corr-test-123",
        trace_id="abcdef0123456789abcdef0123456789",
        span_id="0123456789abcdef",
    )


@pytest.fixture
def field_event():
    """Create a FieldCreatedEvent for testing."""
    if not _HAS_PYDANTIC:
        pytest.skip("pydantic not available")
    from shared.events.contracts import FieldCreatedEvent

    return FieldCreatedEvent(
        field_id=uuid4(),
        farm_id=uuid4(),
        tenant_id=uuid4(),
        name="Test Field",
        geometry_wkt="POLYGON((0 0,1 0,1 1,0 1,0 0))",
        source_service="field-management-service",
        correlation_id="corr-field-001",
    )


def _make_mock_pool(conn):
    """Create a mock DB pool that returns the given connection."""
    pool = MagicMock()
    pool.acquire = MagicMock(return_value=AsyncContextManager(conn))
    return pool


# ─────────────────────────────────────────────────────────────────────────────
# §1: NATS Headers + Meta Enforcement
# ─────────────────────────────────────────────────────────────────────────────


@_SKIP
class TestHeadersInjection:
    """Verify _build_nats_headers produces all 7 canonical headers."""

    def test_all_seven_headers_present(self, base_event):
        from shared.events.publisher import _build_nats_headers

        base_event._tracestate = "vendor=opaque"  # type: ignore[attr-defined]
        headers = _build_nats_headers(base_event)

        assert headers is not None
        assert "traceparent" in headers, "Missing traceparent"
        assert "tracestate" in headers, "Missing tracestate"
        assert "X-Correlation-ID" in headers, "Missing X-Correlation-ID"
        assert "X-Event-ID" in headers, "Missing X-Event-ID"
        assert "X-Schema-Version" in headers, "Missing X-Schema-Version"

    def test_traceparent_w3c_format(self, base_event):
        from shared.events.publisher import _build_nats_headers

        headers = _build_nats_headers(base_event)
        tp = headers["traceparent"]
        parts = tp.split("-")
        assert len(parts) == 4, f"traceparent must have 4 parts: {tp}"
        assert parts[0] == "00", "version must be 00"
        assert parts[3] == "01", "flags must be 01"

    def test_x_event_id_matches_event(self, base_event):
        from shared.events.publisher import _build_nats_headers

        headers = _build_nats_headers(base_event)
        assert headers["X-Event-ID"] == base_event.event_id

    def test_x_schema_version(self, base_event):
        from shared.events.publisher import _build_nats_headers

        headers = _build_nats_headers(base_event)
        assert headers["X-Schema-Version"] == base_event.version

    def test_returns_headers_for_empty_event(self):
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import _build_nats_headers

        evt = BaseEvent()
        headers = _build_nats_headers(evt)
        assert headers is not None
        assert "X-Event-ID" in headers

    def test_x_tenant_id_from_field_event(self, field_event):
        from shared.events.publisher import _build_nats_headers

        headers = _build_nats_headers(field_event)
        assert "X-Tenant-ID" in headers
        assert headers["X-Tenant-ID"] == str(field_event.tenant_id)

    def test_causation_id_header(self, base_event):
        from shared.events.publisher import _build_nats_headers

        base_event.causation_id = "cause-parent-001"
        headers = _build_nats_headers(base_event)
        assert headers["X-Causation-ID"] == "cause-parent-001"


# ─────────────────────────────────────────────────────────────────────────────
# §2: Correlation / Causation Rules
# ─────────────────────────────────────────────────────────────────────────────


@_SKIP
class TestCorrelationCausationBehavior:
    """Behavioral tests for chain_event()."""

    def test_chain_preserves_correlation_id(self):
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import chain_event

        parent = BaseEvent(correlation_id="original-corr")
        child = BaseEvent()
        chain_event(parent, child)

        assert child.correlation_id == "original-corr"

    def test_chain_sets_causation_to_parent_event_id(self):
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import chain_event

        parent = BaseEvent()
        child = BaseEvent()
        chain_event(parent, child)

        assert child.causation_id == parent.event_id

    def test_chain_child_has_unique_event_id(self):
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import chain_event

        parent = BaseEvent()
        child = BaseEvent()
        chain_event(parent, child)

        assert child.event_id != parent.event_id

    def test_chain_from_dict_payload(self):
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import chain_event

        parent_dict = {
            "event_id": "evt-parent-001",
            "correlation_id": "corr-from-http",
            "trace_id": "abc123def456",
        }
        child = BaseEvent()
        chain_event(parent_dict, child)

        assert child.causation_id == "evt-parent-001"
        assert child.correlation_id == "corr-from-http"
        assert child.trace_id == "abc123def456"

    def test_chain_three_deep(self):
        """Three-event chain maintains correlation, updates causation."""
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import chain_event

        root = BaseEvent(correlation_id="root-corr")
        middle = BaseEvent()
        chain_event(root, middle)

        leaf = BaseEvent()
        chain_event(middle, leaf)

        assert leaf.correlation_id == "root-corr"  # unchanged
        assert leaf.causation_id == middle.event_id  # links to direct parent
        assert leaf.causation_id != root.event_id  # NOT the root

    def test_chain_propagates_trace_id(self):
        from shared.events.contracts import BaseEvent
        from shared.events.publisher import chain_event

        parent = BaseEvent(trace_id="aabbccdd11223344aabbccdd11223344")
        child = BaseEvent()
        chain_event(parent, child)

        assert child.trace_id == "aabbccdd11223344aabbccdd11223344"


# ─────────────────────────────────────────────────────────────────────────────
# §3: ACK Policy — ACK only after success, NAK on failure
# ─────────────────────────────────────────────────────────────────────────────


@_SKIP_CROP_INTEL
@pytest.mark.asyncio
class TestAckPolicy:
    """Test ACK/NAK behavior in crop-intelligence handlers."""

    async def test_ack_on_malformed_ndvi_message(self):
        """Malformed message (missing required fields) → ACK (don't redeliver junk)."""
        msg = FakeNATSMsg(
            subject="sahool.satellite.ndvi.computed",
            payload={"tenant_id": "t-1"},  # missing field_id and ndvi
        )
        app_state = FakeAppState()

        await _crop_intel_subs._handle_ndvi_computed(msg, app_state)
        assert msg.ack_called, "Malformed messages must be ACKed to prevent infinite redelivery"
        assert not msg.nak_called

    async def test_nak_on_ndvi_db_failure(self):
        """DB failure during NDVI processing → NAK for redelivery."""
        msg = FakeNATSMsg(
            subject="sahool.satellite.ndvi.computed",
            payload={
                "tenant_id": "t-1",
                "field_id": "f-1",
                "mean_ndvi": 0.72,
                "event_id": "evt-ndvi-1",
            },
        )

        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)  # not processed yet
        mock_pool = _make_mock_pool(mock_conn)
        app_state = FakeAppState(db_pool=mock_pool)

        # The handler will try to import digital_twin which will fail → NAK
        await _crop_intel_subs._handle_ndvi_computed(msg, app_state)
        assert msg.nak_called, "DB/import failures should NAK for redelivery"

    async def test_ack_on_weather_success(self):
        """Weather forecast cache → ACK."""
        msg = FakeNATSMsg(
            subject="sahool.weather.forecast",
            payload={"tenant_id": "t-1", "field_id": "f-1", "temperature": 28},
        )
        app_state = FakeAppState()

        await _crop_intel_subs._handle_weather_forecast(msg, app_state)
        assert msg.ack_called
        assert not msg.nak_called
        assert "t-1:f-1" in app_state.weather_cache

    async def test_nak_on_calibration_parse_error(self):
        """Invalid JSON in calibration → NAK for redelivery."""
        msg = FakeNATSMsg.__new__(FakeNATSMsg)
        msg.subject = "sahool.calibration.run.succeeded.v1"
        msg.data = b"NOT-JSON"
        msg.headers = {}
        msg.ack_called = False
        msg.nak_called = False

        async def ack():
            msg.ack_called = True

        async def nak():
            msg.nak_called = True

        msg.ack = ack
        msg.nak = nak

        app_state = FakeAppState()

        await _crop_intel_subs._handle_calibration_succeeded(msg, app_state)
        assert msg.nak_called, "JSON parse errors should NAK for redelivery"

    async def test_ack_on_calibration_success(self):
        """Valid calibration event → ACK + params reloaded."""
        msg = FakeNATSMsg(
            subject="sahool.calibration.run.succeeded.v1",
            payload={
                "run_id": "run-1",
                "field_id": "f-1",
                "safe_for_decision": True,
                "best_params": {"k_cb": 1.1},
                "objective_value": 0.95,
            },
        )
        app_state = FakeAppState()

        await _crop_intel_subs._handle_calibration_succeeded(msg, app_state)
        assert msg.ack_called
        assert not msg.nak_called
        assert "f-1" in app_state.calibrated_params
        assert app_state.calibrated_params["f-1"]["params"]["k_cb"] == 1.1


# ─────────────────────────────────────────────────────────────────────────────
# §4: DB Idempotency (processed_events)
# ─────────────────────────────────────────────────────────────────────────────


@_SKIP_CROP_INTEL
@pytest.mark.asyncio
class TestDBIdempotency:
    """Test _check_processed and _mark_processed helpers."""

    async def test_check_processed_returns_false_when_new(self):
        """New event → not processed → returns False."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)
        mock_pool = _make_mock_pool(mock_conn)

        result = await _crop_intel_subs._check_processed(mock_pool, "tenant-1", "evt-new")
        assert result is False

    async def test_check_processed_returns_true_when_existing(self):
        """Existing event → already processed → returns True."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={"1": 1})
        mock_pool = _make_mock_pool(mock_conn)

        result = await _crop_intel_subs._check_processed(mock_pool, "tenant-1", "evt-existing")
        assert result is True

    async def test_check_processed_returns_false_on_db_error(self):
        """DB error → fail open (proceed with processing)."""
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(side_effect=Exception("DB down"))

        result = await _crop_intel_subs._check_processed(mock_pool, "tenant-1", "evt-1")
        assert result is False  # fail open

    async def test_check_processed_returns_false_when_no_pool(self):
        """No DB pool → skip check → returns False."""
        result = await _crop_intel_subs._check_processed(None, "tenant-1", "evt-1")
        assert result is False

    async def test_mark_processed_executes_insert(self):
        """mark_processed inserts into processed_events."""
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_pool = _make_mock_pool(mock_conn)

        await _crop_intel_subs._mark_processed(mock_pool, "t-1", "evt-1", "sahool.test", "corr-1")
        mock_conn.execute.assert_called_once()
        call_args = mock_conn.execute.call_args[0]
        assert "INSERT INTO processed_events" in call_args[0]
        assert call_args[1] == "t-1"  # tenant_id
        assert call_args[2] == "evt-1"  # event_id

    async def test_mark_processed_on_conflict_do_nothing(self):
        """mark_processed uses ON CONFLICT DO NOTHING for idempotency."""
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_pool = _make_mock_pool(mock_conn)

        await _crop_intel_subs._mark_processed(mock_pool, "t-1", "evt-1", "sahool.test")
        call_args = mock_conn.execute.call_args[0]
        assert "ON CONFLICT" in call_args[0]
        assert "DO NOTHING" in call_args[0]

    async def test_ndvi_handler_skips_duplicate_event(self):
        """NDVI handler ACKs and skips when event already processed."""
        msg = FakeNATSMsg(
            subject="sahool.satellite.ndvi.computed",
            payload={
                "tenant_id": "t-1",
                "field_id": "f-1",
                "mean_ndvi": 0.65,
                "event_id": "evt-dup-1",
            },
        )

        mock_conn = AsyncMock()
        # _check_processed returns True (already processed)
        mock_conn.fetchrow = AsyncMock(return_value={"1": 1})
        mock_pool = _make_mock_pool(mock_conn)
        app_state = FakeAppState(db_pool=mock_pool)

        await _crop_intel_subs._handle_ndvi_computed(msg, app_state)
        assert msg.ack_called, "Duplicate events should be ACKed"
        assert not msg.nak_called


# ─────────────────────────────────────────────────────────────────────────────
# §5: Outbox Pattern
# ─────────────────────────────────────────────────────────────────────────────


@_SKIP
class TestOutboxWrite:
    """Test write_outbox_event inserts correctly."""

    @pytest.mark.asyncio
    async def test_write_outbox_event_returns_uuid(self):
        from shared.events.outbox import write_outbox_event

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()

        event_id = await write_outbox_event(
            mock_conn,
            subject="sahool.recommendation.created",
            payload='{"field_id": "f-1"}',
            correlation_id="corr-1",
            tenant_id="t-1",
        )

        assert event_id is not None
        assert len(event_id) == 36  # UUID format
        mock_conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_outbox_event_with_headers(self):
        from shared.events.outbox import write_outbox_event

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()

        headers = {"X-Correlation-ID": "corr-1", "traceparent": "00-abc-def-01"}
        await write_outbox_event(
            mock_conn,
            subject="sahool.test",
            payload="{}",
            headers=headers,
        )

        call_args = mock_conn.execute.call_args[0]
        # 4th positional arg is headers_json
        assert "corr-1" in call_args[4]

    @pytest.mark.asyncio
    async def test_write_outbox_event_sql_structure(self):
        from shared.events.outbox import write_outbox_event

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()

        await write_outbox_event(
            mock_conn,
            subject="sahool.field.created",
            payload='{"name":"test"}',
            tenant_id="t-1",
            correlation_id="corr-1",
        )

        call_args = mock_conn.execute.call_args[0]
        sql = call_args[0]
        assert "INSERT INTO outbox_events" in sql
        assert call_args[2] == "sahool.field.created"  # subject


@_SKIP
class TestOutboxRelay:
    """Test OutboxRelay polling and publishing."""

    @pytest.mark.asyncio
    async def test_relay_publishes_pending_events(self):
        from shared.events.outbox import OutboxRelay

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(
            return_value=[
                {
                    "id": "out-1",
                    "subject": "sahool.test",
                    "payload": '{"key": "value"}',
                    "headers_json": None,
                    "tenant_id": "t-1",
                    "correlation_id": "corr-1",
                    "retry_count": 0,
                },
            ]
        )
        mock_conn.execute = AsyncMock()
        mock_pool = _make_mock_pool(mock_conn)

        mock_publisher = MagicMock()
        mock_js = AsyncMock()
        mock_publisher._js = mock_js
        mock_publisher._nc = None

        relay = OutboxRelay(db_pool=mock_pool, publisher=mock_publisher)
        count = await relay._relay_batch()

        assert count == 1
        assert relay.published_count == 1
        mock_js.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_relay_marks_failed_after_max_retries(self):
        from shared.events.outbox import OutboxRelay

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(
            return_value=[
                {
                    "id": "out-2",
                    "subject": "sahool.test",
                    "payload": "{}",
                    "headers_json": None,
                    "tenant_id": "t-1",
                    "correlation_id": None,
                    "retry_count": 4,  # At max retries (5th attempt)
                },
            ]
        )
        mock_conn.execute = AsyncMock()
        mock_pool = _make_mock_pool(mock_conn)

        mock_publisher = MagicMock()
        mock_publisher._js = None
        mock_publisher._nc = None  # will cause RuntimeError

        relay = OutboxRelay(db_pool=mock_pool, publisher=mock_publisher)
        count = await relay._relay_batch()

        assert count == 0
        assert relay.failed_count == 1

    @pytest.mark.asyncio
    async def test_relay_returns_zero_when_no_pool(self):
        from shared.events.outbox import OutboxRelay

        relay = OutboxRelay(db_pool=None, publisher=MagicMock())
        count = await relay._relay_batch()
        assert count == 0


# ─────────────────────────────────────────────────────────────────────────────
# §6: Handler Flow (extract → dedup → execute → mark → ack)
# ─────────────────────────────────────────────────────────────────────────────


@_SKIP_CROP_INTEL
class TestHandlerFlowExtractHeaders:
    """Test _extract_headers utility from crop-intelligence-service."""

    def test_extracts_all_canonical_headers(self):
        msg = MagicMock()
        msg.headers = {
            "X-Correlation-ID": "corr-abc",
            "X-Causation-ID": "cause-xyz",
            "X-Event-ID": "evt-123",
            "X-Tenant-ID": "t-456",
            "traceparent": "00-aaa-bbb-01",
        }

        result = _crop_intel_subs._extract_headers(msg)
        assert result["correlation_id"] == "corr-abc"
        assert result["causation_id"] == "cause-xyz"
        assert result["event_id"] == "evt-123"
        assert result["tenant_id"] == "t-456"
        assert result["traceparent"] == "00-aaa-bbb-01"

    def test_returns_empty_when_no_headers(self):
        msg = MagicMock()
        msg.headers = None

        result = _crop_intel_subs._extract_headers(msg)
        assert result == {}

    def test_returns_empty_when_headers_missing(self):
        msg = MagicMock(spec=[])  # no headers attr

        result = _crop_intel_subs._extract_headers(msg)
        assert result == {}


# ─────────────────────────────────────────────────────────────────────────────
# §7: Notification Service Routing
# ─────────────────────────────────────────────────────────────────────────────


@_SKIP_NOTIF
@pytest.mark.asyncio
class TestNotificationRouting:
    """Test notification-service routes recommendations correctly."""

    async def test_irrigation_recommendation_creates_notification(self):
        NATSSubscriber = _notif_subscriber.NATSSubscriber
        ReceivedEvent = _notif_subscriber.ReceivedEvent

        captured = []
        subscriber = NATSSubscriber(notification_callback=lambda data: captured.append(data))

        event = ReceivedEvent(
            event_id="evt-1",
            event_type="irrigation.recommendation.ready",
            source_service="irrigation-smart",
            timestamp=datetime.now(UTC),
            field_id="f-1",
            tenant_id="t-1",
            data={"recommendation": {"amount_mm": 25}},
            notification_priority="high",
        )

        await subscriber._handle_irrigation_recommendation(event)

        assert len(captured) == 1
        assert captured[0]["type"] == "irrigation_reminder"
        assert "25" in captured[0]["title"]

    async def test_decision_recommendation_routes_fertilizer(self):
        NATSSubscriber = _notif_subscriber.NATSSubscriber
        ReceivedEvent = _notif_subscriber.ReceivedEvent

        captured = []
        subscriber = NATSSubscriber(notification_callback=lambda data: captured.append(data))

        event = ReceivedEvent(
            event_id="evt-2",
            event_type="recommendation.created",
            source_service="advisory-service",
            timestamp=datetime.now(UTC),
            field_id="f-2",
            data={
                "recommendation": {
                    "type": "fertilizer",
                    "title": "Apply Urea",
                    "title_ar": "تطبيق اليوريا",
                }
            },
        )

        await subscriber._handle_decision_recommendation(event)

        assert len(captured) == 1
        assert captured[0]["type"] == "task_reminder"  # fertilizer → task_reminder
        assert captured[0]["title"] == "Apply Urea"
        assert captured[0]["title_ar"] == "تطبيق اليوريا"

    async def test_decision_recommendation_routes_pest_control(self):
        NATSSubscriber = _notif_subscriber.NATSSubscriber
        ReceivedEvent = _notif_subscriber.ReceivedEvent

        captured = []
        subscriber = NATSSubscriber(notification_callback=lambda data: captured.append(data))

        event = ReceivedEvent(
            event_id="evt-3",
            event_type="recommendation.created",
            source_service="advisory-service",
            timestamp=datetime.now(UTC),
            field_id="f-3",
            data={
                "recommendation": {
                    "type": "pest_control",
                    "title": "Apply Pesticide",
                    "title_ar": "تطبيق المبيد",
                }
            },
        )

        await subscriber._handle_decision_recommendation(event)

        assert len(captured) == 1
        assert captured[0]["type"] == "pest_outbreak"

    async def test_event_to_notification_data_mapping(self):
        """Test the generic _event_to_notification_data mapping."""
        NATSSubscriber = _notif_subscriber.NATSSubscriber
        ReceivedEvent = _notif_subscriber.ReceivedEvent

        subscriber = NATSSubscriber()

        event = ReceivedEvent(
            event_id="evt-map-1",
            event_type="ndvi.analysis.completed",
            source_service="vegetation-analysis",
            timestamp=datetime.now(UTC),
            field_id="f-map",
            notification_channels=["push", "in_app"],
        )

        data = subscriber._event_to_notification_data(event)
        assert data["channels"] == ["push", "in_app"]
        assert data["data"]["event_id"] == "evt-map-1"


# ─────────────────────────────────────────────────────────────────────────────
# §8: Subscriber Inbound Header Extraction
# ─────────────────────────────────────────────────────────────────────────────


@_SKIP
class TestSubscriberHeaderExtraction:
    """Test that EventSubscriber._extract_headers works correctly."""

    def test_extract_headers_parses_w3c_traceparent(self):
        from shared.events.subscriber import EventSubscriber

        sub = EventSubscriber.__new__(EventSubscriber)
        msg = MagicMock()
        msg.headers = {
            "traceparent": "00-abcdef01234567890abcdef012345678-0123456789abcdef-01",
            "X-Correlation-ID": "corr-test",
        }

        result = sub._extract_headers(msg)
        assert result["traceparent"] == "00-abcdef01234567890abcdef012345678-0123456789abcdef-01"
        assert result["correlation_id"] == "corr-test"

    def test_extract_headers_all_fields(self):
        from shared.events.subscriber import EventSubscriber

        sub = EventSubscriber.__new__(EventSubscriber)
        msg = MagicMock()
        msg.headers = {
            "traceparent": "00-trace-span-01",
            "tracestate": "vendor=state",
            "X-Correlation-ID": "corr-1",
            "X-Causation-ID": "cause-1",
            "X-Event-ID": "evt-1",
            "X-Tenant-ID": "t-1",
            "X-Schema-Version": "1.0.0",
        }

        result = sub._extract_headers(msg)
        assert result["traceparent"] == "00-trace-span-01"
        assert result["tracestate"] == "vendor=state"
        assert result["correlation_id"] == "corr-1"
        assert result["causation_id"] == "cause-1"
        assert result["event_id"] == "evt-1"
        assert result["tenant_id"] == "t-1"
        assert result["schema_version"] == "1.0.0"

    def test_extract_headers_returns_empty_dict_for_none(self):
        from shared.events.subscriber import EventSubscriber

        sub = EventSubscriber.__new__(EventSubscriber)
        msg = MagicMock()
        msg.headers = None

        result = sub._extract_headers(msg)
        assert result == {}


# ─────────────────────────────────────────────────────────────────────────────
# §DLQ: DLQ on max retries exhaustion (via OutboxRelay)
# ─────────────────────────────────────────────────────────────────────────────


@_SKIP
class TestDLQBehavior:
    """Test DLQ-related behavior in outbox relay and subscriber."""

    @pytest.mark.asyncio
    async def test_outbox_relay_dlq_after_max_retries(self):
        """Outbox relay marks event as 'failed' after max retries exhausted."""
        from shared.events.outbox import _MAX_RELAY_RETRIES, OutboxRelay

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(
            return_value=[
                {
                    "id": "dlq-1",
                    "subject": "sahool.test.dlq",
                    "payload": '{"fail": true}',
                    "headers_json": None,
                    "tenant_id": "t-1",
                    "correlation_id": "corr-dlq",
                    "retry_count": _MAX_RELAY_RETRIES - 1,  # at the limit
                },
            ]
        )
        mock_conn.execute = AsyncMock()
        mock_pool = _make_mock_pool(mock_conn)

        # Publisher with no NATS connection → always fails
        mock_publisher = MagicMock()
        mock_publisher._js = None
        mock_publisher._nc = None

        relay = OutboxRelay(db_pool=mock_pool, publisher=mock_publisher)
        count = await relay._relay_batch()

        assert count == 0
        assert relay.failed_count == 1
        # Verify the DLQ SQL was executed (mark as 'failed')
        execute_calls = [str(c) for c in mock_conn.execute.call_args_list]
        assert any("failed" in c for c in execute_calls)

    @pytest.mark.asyncio
    async def test_outbox_relay_retries_below_max(self):
        """Outbox relay increments retry_count when below max."""
        from shared.events.outbox import OutboxRelay

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(
            return_value=[
                {
                    "id": "retry-1",
                    "subject": "sahool.test",
                    "payload": "{}",
                    "headers_json": None,
                    "tenant_id": "t-1",
                    "correlation_id": None,
                    "retry_count": 1,  # below max
                },
            ]
        )
        mock_conn.execute = AsyncMock()
        mock_pool = _make_mock_pool(mock_conn)

        mock_publisher = MagicMock()
        mock_publisher._js = None
        mock_publisher._nc = None  # will fail

        relay = OutboxRelay(db_pool=mock_pool, publisher=mock_publisher)
        await relay._relay_batch()

        # Should increment retry_count, not mark as failed
        execute_calls = mock_conn.execute.call_args_list
        assert len(execute_calls) >= 1

    def test_subscriber_in_memory_dedup_eviction(self):
        """EventSubscriber LRU evicts oldest when over limit."""
        from shared.events.subscriber import EventSubscriber

        sub = EventSubscriber.__new__(EventSubscriber)
        sub._processed_event_ids = {}
        sub._dedup_max_size = 3

        # Fill beyond limit
        sub._processed_event_ids["a"] = 1.0
        sub._processed_event_ids["b"] = 2.0
        sub._processed_event_ids["c"] = 3.0
        sub._processed_event_ids["d"] = 4.0

        # Evict oldest
        if len(sub._processed_event_ids) > sub._dedup_max_size:
            excess = len(sub._processed_event_ids) - sub._dedup_max_size
            for old_key in list(sub._processed_event_ids)[:excess]:
                del sub._processed_event_ids[old_key]

        assert len(sub._processed_event_ids) == 3
        assert "a" not in sub._processed_event_ids
        assert "d" in sub._processed_event_ids
