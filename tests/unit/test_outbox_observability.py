"""
Unit tests for:

1. shared/libs/outbox/metrics.py — OUTBOX_METRICS façade (incl. latency histogram)
2. shared/libs/outbox/replay_tool.py — OutboxReplay helpers (incl. inspect + replayed_by)
3. Relay structured logging — logs carry event_id, subject, tenant_id, worker_id
4. Relay metrics integration — counters + latency histogram on publish/fail/DLQ
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone, UTC
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.libs.outbox.metrics import OUTBOX_METRICS
from shared.libs.outbox.relay import (
    _MARK_DLQ_SQL,
    _MARK_FAILED_SQL,
    _MARK_SENT_SQL,
    _MAX_RETRIES,
    OutboxRelay,
)
from shared.libs.outbox.replay_tool import OutboxReplay


# ---------------------------------------------------------------------------
# Helpers shared by relay tests
# ---------------------------------------------------------------------------


def _make_row(retry_count: int = 0, event_id: str | None = None, subject: str = "sahool.satellite.ndvi.computed"):
    _eid = event_id or str(uuid.uuid4())
    return {
        "id": uuid.uuid4(),
        "subject": subject,
        "payload": b'{"field_id":"f1","value":0.7}',
        "headers": f'{{"X-Event-ID":"{_eid}","X-Tenant-ID":"t-test"}}',
        "retry_count": retry_count,
        "tenant_id": "t-test",
    }


def _make_db_pool(rows=None, fetch_side_effect=None):
    conn = AsyncMock()
    tx = MagicMock()
    tx.__aenter__ = AsyncMock(return_value=None)
    tx.__aexit__ = AsyncMock(return_value=False)
    conn.transaction = MagicMock(return_value=tx)
    conn.fetch = AsyncMock(side_effect=fetch_side_effect) if fetch_side_effect else AsyncMock(return_value=rows or [])
    conn.execute = AsyncMock(return_value="UPDATE 1")
    pool = MagicMock()
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=conn)
    ctx.__aexit__ = AsyncMock(return_value=False)
    pool.acquire = MagicMock(return_value=ctx)
    return pool, conn


# ---------------------------------------------------------------------------
# 1. OUTBOX_METRICS façade — no-op when prometheus unavailable
# ---------------------------------------------------------------------------


class TestOutboxMetricsFacade:
    """
    The metrics façade must never raise regardless of whether
    prometheus_client is installed in the test environment.
    """

    def test_published_does_not_raise(self):
        OUTBOX_METRICS.published(subject="sahool.test")

    def test_failed_does_not_raise(self):
        OUTBOX_METRICS.failed(subject="sahool.test", reason="ConnectionError")

    def test_dead_lettered_does_not_raise(self):
        OUTBOX_METRICS.dead_lettered(subject="sahool.test")

    def test_set_pending_does_not_raise(self):
        OUTBOX_METRICS.set_pending(42)

    def test_available_is_bool(self):
        assert isinstance(OUTBOX_METRICS.available, bool)

    def test_published_called_with_prometheus_mock(self):
        """When prometheus_client is present, labels().inc() should be called."""
        mock_counter = MagicMock()
        mock_counter.labels.return_value = mock_counter

        import shared.libs.outbox.metrics as m

        original = m._published_counter
        m._published_counter = mock_counter
        try:
            OUTBOX_METRICS.published(subject="sahool.ndvi")
            mock_counter.labels.assert_called_once_with(subject="sahool.ndvi")
            mock_counter.inc.assert_called_once()
        finally:
            m._published_counter = original

    def test_failed_called_with_prometheus_mock(self):
        mock_counter = MagicMock()
        mock_counter.labels.return_value = mock_counter

        import shared.libs.outbox.metrics as m

        original = m._failures_counter
        m._failures_counter = mock_counter
        try:
            OUTBOX_METRICS.failed(subject="sahool.ndvi", reason="TimeoutError")
            mock_counter.labels.assert_called_once_with(subject="sahool.ndvi", reason="TimeoutError")
            mock_counter.inc.assert_called_once()
        finally:
            m._failures_counter = original

    def test_dead_lettered_called_with_prometheus_mock(self):
        mock_counter = MagicMock()
        mock_counter.labels.return_value = mock_counter

        import shared.libs.outbox.metrics as m

        original = m._dlq_counter
        m._dlq_counter = mock_counter
        try:
            OUTBOX_METRICS.dead_lettered(subject="sahool.ndvi")
            mock_counter.labels.assert_called_once_with(subject="sahool.ndvi")
            mock_counter.inc.assert_called_once()
        finally:
            m._dlq_counter = original

    def test_set_pending_called_with_prometheus_mock(self):
        mock_gauge = MagicMock()

        import shared.libs.outbox.metrics as m

        original = m._pending_gauge
        m._pending_gauge = mock_gauge
        try:
            OUTBOX_METRICS.set_pending(17)
            mock_gauge.set.assert_called_once_with(17)
        finally:
            m._pending_gauge = original


# ---------------------------------------------------------------------------
# 2. OutboxReplay — reset_dead_lettered SQL dispatch
# ---------------------------------------------------------------------------


class TestOutboxReplay:
    """Tests for OutboxReplay helper SQL routing."""

    @pytest.mark.asyncio
    async def test_reset_all_uses_correct_sql(self):
        """reset_dead_lettered() with no filters should reset ALL DLQ rows."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 3")

        count = await OutboxReplay.reset_dead_lettered(pool)

        assert count == 3
        sql_used = conn.execute.call_args[0][0]
        assert "dead_lettered_at = NULL" in sql_used
        assert "retry_count      = 0" in sql_used
        assert "$1" not in sql_used  # no parameter for "all" reset

    @pytest.mark.asyncio
    async def test_reset_by_subject_passes_subject_param(self):
        """reset_dead_lettered(subject=...) should filter by subject."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 1")

        count = await OutboxReplay.reset_dead_lettered(pool, subject="sahool.satellite.ndvi.computed")

        assert count == 1
        call_args = conn.execute.call_args[0]
        assert "AND subject = $1" in call_args[0]
        assert call_args[1] == "sahool.satellite.ndvi.computed"

    @pytest.mark.asyncio
    async def test_reset_by_ids_passes_id_list(self):
        """reset_dead_lettered(ids=[...]) should filter by id array."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 2")
        id1, id2 = str(uuid.uuid4()), str(uuid.uuid4())

        count = await OutboxReplay.reset_dead_lettered(pool, ids=[id1, id2])

        assert count == 2
        call_args = conn.execute.call_args[0]
        assert "AND id = ANY($1::uuid[])" in call_args[0]
        assert id1 in call_args[1]
        assert id2 in call_args[1]

    @pytest.mark.asyncio
    async def test_raises_if_both_subject_and_ids_given(self):
        """Providing both subject and ids must raise ValueError immediately."""
        pool, _ = _make_db_pool()
        with pytest.raises(ValueError, match="subject.*ids"):
            await OutboxReplay.reset_dead_lettered(
                pool,
                subject="sahool.ndvi",
                ids=["abc"],
            )

    @pytest.mark.asyncio
    async def test_count_dead_lettered_returns_integer(self):
        pool, conn = _make_db_pool()
        conn.fetchrow = AsyncMock(return_value={"n": 7})

        count = await OutboxReplay.count_dead_lettered(pool)

        assert count == 7

    @pytest.mark.asyncio
    async def test_list_dead_lettered_returns_dicts(self):
        pool, conn = _make_db_pool()
        row = {
            "id": uuid.uuid4(),
            "subject": "sahool.satellite.ndvi.computed",
            "tenant_id": "t-1",
            "retry_count": 10,
            "dead_lettered_at": "2026-04-01T00:00:00",
        }
        conn.fetch = AsyncMock(return_value=[row])

        rows = await OutboxReplay.list_dead_lettered(pool)

        assert len(rows) == 1
        assert rows[0]["subject"] == "sahool.satellite.ndvi.computed"
        assert rows[0]["retry_count"] == 10

    @pytest.mark.asyncio
    async def test_reset_returns_zero_on_no_rows(self):
        """When no rows match, UPDATE returns 'UPDATE 0' and count is 0."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 0")

        count = await OutboxReplay.reset_dead_lettered(pool)

        assert count == 0


# ---------------------------------------------------------------------------
# 3. Relay structured logging — event_id propagated through all log paths
# ---------------------------------------------------------------------------


class TestRelayStructuredLogging:
    """
    Verify that relay log records always carry the structured fields
    required for event_id-based tracing.
    """

    @pytest.mark.asyncio
    async def test_publish_success_logs_event_id(self):
        event_id = str(uuid.uuid4())
        row = _make_row(event_id=event_id)
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(return_value=None)
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.logger") as mock_log:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        # Find the outbox_published debug call
        debug_calls = [
            c for c in mock_log.debug.call_args_list if c[0][0] == "outbox_published"
        ]
        assert debug_calls, "Expected outbox_published log"
        extra = debug_calls[0][1]["extra"]
        assert extra["event_id"] == event_id
        assert extra["subject"] == row["subject"]
        assert extra["tenant_id"] == "t-test"
        assert extra["worker_id"] == "w-test"

    @pytest.mark.asyncio
    async def test_publish_failure_logs_event_id(self):
        event_id = str(uuid.uuid4())
        row = _make_row(retry_count=0, event_id=event_id)
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(side_effect=Exception("NATS down"))
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.logger") as mock_log:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        warning_calls = [
            c for c in mock_log.warning.call_args_list if c[0][0] == "outbox_publish_failed"
        ]
        assert warning_calls, "Expected outbox_publish_failed log"
        extra = warning_calls[0][1]["extra"]
        assert extra["event_id"] == event_id
        assert extra["subject"] == row["subject"]
        assert extra["tenant_id"] == "t-test"
        assert extra["worker_id"] == "w-test"
        assert "retry_count" in extra
        assert "error" in extra
        assert "error_type" in extra

    @pytest.mark.asyncio
    async def test_dlq_logs_event_id(self):
        event_id = str(uuid.uuid4())
        row = _make_row(retry_count=_MAX_RETRIES - 1, event_id=event_id)
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(side_effect=Exception("permanent error"))
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.logger") as mock_log:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        error_calls = [
            c for c in mock_log.error.call_args_list if c[0][0] == "outbox_dead_lettered"
        ]
        assert error_calls, "Expected outbox_dead_lettered log"
        extra = error_calls[0][1]["extra"]
        assert extra["event_id"] == event_id
        assert extra["subject"] == row["subject"]
        assert extra["tenant_id"] == "t-test"
        assert extra["worker_id"] == "w-test"
        assert extra["retry_count"] == _MAX_RETRIES
        assert "error" in extra
        assert "error_type" in extra


# ---------------------------------------------------------------------------
# 4. Relay metrics integration — OUTBOX_METRICS called correctly
# ---------------------------------------------------------------------------


class TestRelayMetricsIntegration:
    """OUTBOX_METRICS methods are called at the right points in the relay."""

    @pytest.mark.asyncio
    async def test_published_counter_incremented_on_success(self):
        row = _make_row()
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(return_value=None)
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.OUTBOX_METRICS") as mock_metrics:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        mock_metrics.published.assert_called_once_with(subject=row["subject"])
        mock_metrics.failed.assert_not_called()
        mock_metrics.dead_lettered.assert_not_called()

    @pytest.mark.asyncio
    async def test_failed_counter_incremented_on_transient_failure(self):
        row = _make_row(retry_count=0)
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(side_effect=Exception("NATS unavailable"))
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.OUTBOX_METRICS") as mock_metrics:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        mock_metrics.failed.assert_called_once_with(
            subject=row["subject"], reason="Exception"
        )
        mock_metrics.published.assert_not_called()
        mock_metrics.dead_lettered.assert_not_called()

    @pytest.mark.asyncio
    async def test_dlq_counter_incremented_on_max_retry(self):
        row = _make_row(retry_count=_MAX_RETRIES - 1)
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(side_effect=Exception("permanent"))
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.OUTBOX_METRICS") as mock_metrics:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        mock_metrics.dead_lettered.assert_called_once_with(subject=row["subject"])
        mock_metrics.published.assert_not_called()
        mock_metrics.failed.assert_not_called()

    @pytest.mark.asyncio
    async def test_reason_label_is_exception_class_name(self):
        """The 'reason' label in failed() should be the exception class name."""
        row = _make_row(retry_count=0)
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(side_effect=ConnectionRefusedError("refused"))
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.OUTBOX_METRICS") as mock_metrics:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        mock_metrics.failed.assert_called_once_with(
            subject=row["subject"], reason="ConnectionRefusedError"
        )


# ---------------------------------------------------------------------------
# 5. Latency histogram — observe_publish_latency façade + relay integration
# ---------------------------------------------------------------------------


class TestLatencyHistogramFacade:
    """The latency histogram façade must be safe in all environments."""

    def test_observe_does_not_raise(self):
        OUTBOX_METRICS.observe_publish_latency(subject="sahool.test", duration_seconds=0.042)

    def test_observe_called_with_prometheus_mock(self):
        mock_hist = MagicMock()
        mock_hist.labels.return_value = mock_hist

        import shared.libs.outbox.metrics as m

        original = m._latency_histogram
        m._latency_histogram = mock_hist
        try:
            OUTBOX_METRICS.observe_publish_latency(subject="sahool.ndvi", duration_seconds=0.015)
            mock_hist.labels.assert_called_once_with(subject="sahool.ndvi")
            mock_hist.observe.assert_called_once_with(0.015)
        finally:
            m._latency_histogram = original

    def test_observe_zero_does_not_raise(self):
        OUTBOX_METRICS.observe_publish_latency(subject="sahool.test", duration_seconds=0.0)

    def test_observe_large_value_does_not_raise(self):
        # Values outside bucket range are still valid observations
        OUTBOX_METRICS.observe_publish_latency(subject="sahool.test", duration_seconds=60.0)


class TestRelayLatencyIntegration:
    """Relay calls observe_publish_latency on successful publish."""

    @pytest.mark.asyncio
    async def test_latency_observed_on_success(self):
        """observe_publish_latency must be called exactly once on publish success."""
        row = _make_row()
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(return_value=None)
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.OUTBOX_METRICS") as mock_metrics:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        mock_metrics.observe_publish_latency.assert_called_once()
        call_kwargs = mock_metrics.observe_publish_latency.call_args[1]
        assert call_kwargs["subject"] == row["subject"]
        assert isinstance(call_kwargs["duration_seconds"], float)
        assert call_kwargs["duration_seconds"] >= 0

    @pytest.mark.asyncio
    async def test_latency_not_observed_on_failure(self):
        """observe_publish_latency must NOT be called when publish fails."""
        row = _make_row(retry_count=0)
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(side_effect=Exception("timeout"))
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.OUTBOX_METRICS") as mock_metrics:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        mock_metrics.observe_publish_latency.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_latency_ms_in_log_on_success(self):
        """Published log record must include publish_latency_ms field."""
        row = _make_row()
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(return_value=None)
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.logger") as mock_log:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        debug_calls = [c for c in mock_log.debug.call_args_list if c[0][0] == "outbox_published"]
        assert debug_calls, "Expected outbox_published log"
        extra = debug_calls[0][1]["extra"]
        assert "publish_latency_ms" in extra
        assert isinstance(extra["publish_latency_ms"], float)
        assert extra["publish_latency_ms"] >= 0


# ---------------------------------------------------------------------------
# 6. replayed_by audit trail — forensic log fields on reset
# ---------------------------------------------------------------------------


class TestReplayAuditTrail:
    """reset_dead_lettered() must include replayed_by in the audit log."""

    @pytest.mark.asyncio
    async def test_audit_log_contains_replayed_by(self):
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 2")

        with patch("shared.libs.outbox.replay_tool.logger") as mock_log:
            await OutboxReplay.reset_dead_lettered(pool, replayed_by="ops-team")

        info_calls = [c for c in mock_log.info.call_args_list if c[0][0] == "outbox_replay_reset"]
        assert info_calls, "Expected outbox_replay_reset log"
        extra = info_calls[0][1]["extra"]
        assert extra["replayed_by"] == "ops-team"

    @pytest.mark.asyncio
    async def test_audit_log_contains_replayed_at(self):
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 1")

        with patch("shared.libs.outbox.replay_tool.logger") as mock_log:
            await OutboxReplay.reset_dead_lettered(pool, replayed_by="automated-recovery")

        info_calls = [c for c in mock_log.info.call_args_list if c[0][0] == "outbox_replay_reset"]
        extra = info_calls[0][1]["extra"]
        assert "replayed_at" in extra
        # Must be a parseable ISO 8601 timestamp
        from datetime import datetime
        dt = datetime.fromisoformat(extra["replayed_at"])
        assert dt is not None

    @pytest.mark.asyncio
    async def test_audit_log_contains_filter_subject(self):
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 3")

        with patch("shared.libs.outbox.replay_tool.logger") as mock_log:
            await OutboxReplay.reset_dead_lettered(
                pool,
                subject="sahool.satellite.ndvi.computed",
                replayed_by="admin-ui",
            )

        info_calls = [c for c in mock_log.info.call_args_list if c[0][0] == "outbox_replay_reset"]
        extra = info_calls[0][1]["extra"]
        assert extra["filter_subject"] == "sahool.satellite.ndvi.computed"
        assert extra["replayed_by"] == "admin-ui"

    @pytest.mark.asyncio
    async def test_audit_log_contains_filter_ids(self):
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 1")
        id1 = str(uuid.uuid4())

        with patch("shared.libs.outbox.replay_tool.logger") as mock_log:
            await OutboxReplay.reset_dead_lettered(pool, ids=[id1], replayed_by="incident-response")

        info_calls = [c for c in mock_log.info.call_args_list if c[0][0] == "outbox_replay_reset"]
        extra = info_calls[0][1]["extra"]
        assert id1 in extra["filter_ids"]
        assert extra["replayed_by"] == "incident-response"

    @pytest.mark.asyncio
    async def test_default_replayed_by_is_system(self):
        """When replayed_by is omitted, the audit log records 'system'."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 0")

        with patch("shared.libs.outbox.replay_tool.logger") as mock_log:
            await OutboxReplay.reset_dead_lettered(pool)

        info_calls = [c for c in mock_log.info.call_args_list if c[0][0] == "outbox_replay_reset"]
        extra = info_calls[0][1]["extra"]
        assert extra["replayed_by"] == "system"


# ---------------------------------------------------------------------------
# 7. inspect_dead_lettered — dry-run summary
# ---------------------------------------------------------------------------


class TestInspectDeadLettered:
    """inspect_dead_lettered() returns aggregated summary without modifying rows."""

    @pytest.mark.asyncio
    async def test_returns_zero_total_when_no_rows(self):
        pool, conn = _make_db_pool()
        conn.fetch = AsyncMock(return_value=[])

        info = await OutboxReplay.inspect_dead_lettered(pool)

        assert info["total"] == 0
        assert info["by_subject"] == {}
        assert info["oldest_age_seconds"] is None

    @pytest.mark.asyncio
    async def test_returns_correct_totals_and_by_subject(self):
        pool, conn = _make_db_pool()
        now = datetime.now(tz=UTC)
        older = now - timedelta(hours=3)
        rows = [
            {"subject": "sahool.ndvi.computed", "n": 5, "oldest_dead_lettered_at": older},
            {"subject": "sahool.weather.updated", "n": 2, "oldest_dead_lettered_at": now - timedelta(hours=1)},
        ]
        conn.fetch = AsyncMock(return_value=rows)

        info = await OutboxReplay.inspect_dead_lettered(pool)

        assert info["total"] == 7
        assert info["by_subject"]["sahool.ndvi.computed"] == 5
        assert info["by_subject"]["sahool.weather.updated"] == 2

    @pytest.mark.asyncio
    async def test_oldest_age_seconds_reflects_oldest_row(self):
        pool, conn = _make_db_pool()
        now = datetime.now(tz=UTC)
        three_hours_ago = now - timedelta(hours=3)
        one_hour_ago = now - timedelta(hours=1)
        rows = [
            {"subject": "sahool.ndvi.computed", "n": 2, "oldest_dead_lettered_at": three_hours_ago},
            {"subject": "sahool.weather.updated", "n": 1, "oldest_dead_lettered_at": one_hour_ago},
        ]
        conn.fetch = AsyncMock(return_value=rows)

        info = await OutboxReplay.inspect_dead_lettered(pool)

        # Oldest row is 3h old; allow 10s tolerance for test execution time
        assert abs(info["oldest_age_seconds"] - 3 * 3600) < 10

    @pytest.mark.asyncio
    async def test_does_not_call_execute(self):
        """inspect must be read-only — must never call conn.execute."""
        pool, conn = _make_db_pool()
        conn.fetch = AsyncMock(return_value=[])
        conn.execute = AsyncMock()

        await OutboxReplay.inspect_dead_lettered(pool)

        conn.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_handles_naive_datetime(self):
        """inspect must handle naive datetimes returned by asyncpg gracefully."""
        pool, conn = _make_db_pool()
        naive_ts = datetime.now()  # no tzinfo
        rows = [{"subject": "sahool.ndvi.computed", "n": 1, "oldest_dead_lettered_at": naive_ts}]
        conn.fetch = AsyncMock(return_value=rows)

        info = await OutboxReplay.inspect_dead_lettered(pool)

        assert info["total"] == 1
        assert info["oldest_age_seconds"] is not None
        assert info["oldest_age_seconds"] >= 0


# ---------------------------------------------------------------------------
# 8. Replay counter metric — record_replay() façade + integration
# ---------------------------------------------------------------------------


class TestReplayMetric:
    """record_replay() must be safe in all environments and called on reset."""

    def test_record_replay_does_not_raise(self):
        OUTBOX_METRICS.record_replay(subject="sahool.ndvi.computed", reason="all", count=3)

    def test_record_replay_zero_count_does_not_raise(self):
        OUTBOX_METRICS.record_replay(subject="*", reason="all", count=0)

    def test_record_replay_called_with_prometheus_mock(self):
        mock_counter = MagicMock()
        mock_counter.labels.return_value = mock_counter

        import shared.libs.outbox.metrics as m

        original = m._replay_counter
        m._replay_counter = mock_counter
        try:
            OUTBOX_METRICS.record_replay(subject="sahool.test", reason="by_subject", count=5)
            mock_counter.labels.assert_called_once_with(subject="sahool.test", reason="by_subject")
            mock_counter.inc.assert_called_once_with(5)
        finally:
            m._replay_counter = original

    @pytest.mark.asyncio
    async def test_record_replay_called_on_reset_all(self):
        """reset_dead_lettered() without filter: subject='*', reason='all'."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 4")

        with patch("shared.libs.outbox.replay_tool.OUTBOX_METRICS") as mock_m:
            await OutboxReplay.reset_dead_lettered(pool)

        mock_m.record_replay.assert_called_once_with(subject="*", reason="all", count=4)

    @pytest.mark.asyncio
    async def test_record_replay_called_on_reset_by_subject(self):
        """reset_dead_lettered(subject=...) : subject=actual, reason='by_subject'."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 2")

        with patch("shared.libs.outbox.replay_tool.OUTBOX_METRICS") as mock_m:
            await OutboxReplay.reset_dead_lettered(pool, subject="sahool.ndvi.computed")

        mock_m.record_replay.assert_called_once_with(
            subject="sahool.ndvi.computed", reason="by_subject", count=2
        )

    @pytest.mark.asyncio
    async def test_record_replay_called_on_reset_by_ids(self):
        """reset_dead_lettered(ids=[...]) : subject='(ids)', reason='by_ids'."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 1")
        id1 = str(uuid.uuid4())

        with patch("shared.libs.outbox.replay_tool.OUTBOX_METRICS") as mock_m:
            await OutboxReplay.reset_dead_lettered(pool, ids=[id1])

        mock_m.record_replay.assert_called_once_with(subject="(ids)", reason="by_ids", count=1)

    @pytest.mark.asyncio
    async def test_record_replay_not_called_when_zero_rows_reset(self):
        """record_replay must be skipped when no rows were actually reset."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 0")

        with patch("shared.libs.outbox.replay_tool.OUTBOX_METRICS") as mock_m:
            await OutboxReplay.reset_dead_lettered(pool)

        mock_m.record_replay.assert_not_called()


# ---------------------------------------------------------------------------
# 9. Advisory lock — serialization of concurrent replay operations
# ---------------------------------------------------------------------------


class TestAdvisoryLock:
    """reset_dead_lettered() must acquire a pg_advisory_xact_lock before mutating rows."""

    @pytest.mark.asyncio
    async def test_advisory_lock_called_before_update(self):
        """The advisory lock SQL must be the first execute call in the transaction."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 1")

        await OutboxReplay.reset_dead_lettered(pool)

        calls = conn.execute.call_args_list
        # At least two execute calls: advisory lock + UPDATE
        assert len(calls) >= 2
        first_sql = calls[0][0][0]
        assert "pg_advisory_xact_lock" in first_sql

    @pytest.mark.asyncio
    async def test_update_sql_called_after_advisory_lock(self):
        """The UPDATE (or RESET) SQL must be the second execute call."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 3")

        await OutboxReplay.reset_dead_lettered(pool)

        calls = conn.execute.call_args_list
        second_sql = calls[1][0][0]
        # Should be the reset SQL (contains SET dead_lettered_at)
        assert "dead_lettered_at" in second_sql

    @pytest.mark.asyncio
    async def test_advisory_lock_called_inside_transaction(self):
        """Both the advisory lock and UPDATE must happen inside a transaction."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 2")

        await OutboxReplay.reset_dead_lettered(pool)

        # conn.transaction() must have been entered
        conn.transaction.assert_called()

    @pytest.mark.asyncio
    async def test_advisory_lock_subject_filter_still_correct(self):
        """Subject filter is still applied correctly even with the advisory lock."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 1")

        await OutboxReplay.reset_dead_lettered(pool, subject="sahool.test")

        calls = conn.execute.call_args_list
        # Second call is the UPDATE with subject filter
        update_call_args = calls[1][0]
        assert "AND subject = $1" in update_call_args[0]
        assert update_call_args[1] == "sahool.test"

    @pytest.mark.asyncio
    async def test_advisory_lock_ids_filter_still_correct(self):
        """IDs filter is still applied correctly even with the advisory lock."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 1")
        id1 = str(uuid.uuid4())

        await OutboxReplay.reset_dead_lettered(pool, ids=[id1])

        calls = conn.execute.call_args_list
        update_call_args = calls[1][0]
        assert "AND id = ANY($1::uuid[])" in update_call_args[0]
        assert id1 in update_call_args[1]


# ---------------------------------------------------------------------------
# 10. Delivery mode in relay log — JetStream vs core NATS discrimination
# ---------------------------------------------------------------------------


class TestDeliveryModeLog:
    """Published log record must carry delivery_mode to disambiguate latency semantics."""

    @pytest.mark.asyncio
    async def test_delivery_mode_present_in_published_log(self):
        """outbox_published log must always carry delivery_mode field."""
        row = _make_row()
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(return_value=None)
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.logger") as mock_log:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        debug_calls = [c for c in mock_log.debug.call_args_list if c[0][0] == "outbox_published"]
        assert debug_calls, "Expected outbox_published log"
        extra = debug_calls[0][1]["extra"]
        assert "delivery_mode" in extra
        assert extra["delivery_mode"] in ("jetstream", "core_nats")

    @pytest.mark.asyncio
    async def test_delivery_mode_is_core_nats_when_jetstream_absent(self):
        """When nats_client has no jetstream, delivery_mode must be 'core_nats'."""
        row = _make_row()
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(return_value=None)
        nats_client.jetstream = None  # force core NATS path

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.logger") as mock_log:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        debug_calls = [c for c in mock_log.debug.call_args_list if c[0][0] == "outbox_published"]
        assert debug_calls[0][1]["extra"]["delivery_mode"] == "core_nats"

    @pytest.mark.asyncio
    async def test_delivery_mode_is_jetstream_when_js_publish_succeeds(self):
        """When JetStream publish succeeds, delivery_mode must be 'jetstream'."""
        row = _make_row()
        pool, _ = _make_db_pool(rows=[row])

        js_ctx = AsyncMock()
        js_ctx.publish = AsyncMock(return_value=None)
        nats_client = AsyncMock()
        nats_client.jetstream = MagicMock(return_value=js_ctx)

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.logger") as mock_log:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        debug_calls = [c for c in mock_log.debug.call_args_list if c[0][0] == "outbox_published"]
        assert debug_calls, "Expected outbox_published log"
        assert debug_calls[0][1]["extra"]["delivery_mode"] == "jetstream"

    @pytest.mark.asyncio
    async def test_delivery_mode_falls_back_to_core_nats_when_js_publish_fails(self):
        """When JetStream publish fails and falls back, delivery_mode must be 'core_nats'."""
        row = _make_row()
        pool, _ = _make_db_pool(rows=[row])

        js_ctx = AsyncMock()
        js_ctx.publish = AsyncMock(side_effect=Exception("stream not found"))
        nats_client = AsyncMock()
        nats_client.jetstream = MagicMock(return_value=js_ctx)
        nats_client.publish = AsyncMock(return_value=None)

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.logger") as mock_log:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        debug_calls = [c for c in mock_log.debug.call_args_list if c[0][0] == "outbox_published"]
        assert debug_calls, "Expected outbox_published log after fallback"
        assert debug_calls[0][1]["extra"]["delivery_mode"] == "core_nats"


# ---------------------------------------------------------------------------
# 11. OutboxReplayGuard — sliding-window rate limiter
# ---------------------------------------------------------------------------

from shared.libs.outbox.replay_tool import OutboxReplayGuard, ReplayRateLimitExceeded


class TestReplayRateLimiter:
    """OutboxReplayGuard must enforce per-subject sliding-window limits."""

    @pytest.mark.asyncio
    async def test_allows_first_replay(self):
        guard = OutboxReplayGuard(max_replays=3, window_seconds=60)
        await guard.check("sahool.ndvi.computed")  # must not raise

    @pytest.mark.asyncio
    async def test_records_and_counts(self):
        guard = OutboxReplayGuard(max_replays=3, window_seconds=60)
        await guard.record("sahool.ndvi.computed")
        assert await guard.count_in_window("sahool.ndvi.computed") == 1

    @pytest.mark.asyncio
    async def test_blocks_after_max_replays(self):
        guard = OutboxReplayGuard(max_replays=2, window_seconds=60)
        await guard.record("sahool.ndvi.computed")
        await guard.record("sahool.ndvi.computed")
        with pytest.raises(ReplayRateLimitExceeded) as exc_info:
            await guard.check("sahool.ndvi.computed")
        err = exc_info.value
        assert err.subject == "sahool.ndvi.computed"
        assert err.replays_in_window == 2
        assert err.max_replays == 2

    @pytest.mark.asyncio
    async def test_is_per_subject(self):
        guard = OutboxReplayGuard(max_replays=1, window_seconds=60)
        await guard.record("sahool.ndvi.computed")
        # A different subject must still be allowed
        await guard.check("sahool.weather.updated")  # must not raise

    @pytest.mark.asyncio
    async def test_window_expiry_allows_replay(self):
        """After the window expires the counter resets."""
        import time

        guard = OutboxReplayGuard(max_replays=1, window_seconds=1)
        await guard.record("sahool.ndvi.computed")

        # Manually back-date the only entry so it falls outside the window
        async with guard._lock:
            guard._history["sahool.ndvi.computed"][0] = time.monotonic() - 2

        # Now the window should be clear
        await guard.check("sahool.ndvi.computed")  # must not raise

    @pytest.mark.asyncio
    async def test_reset_clears_subject(self):
        guard = OutboxReplayGuard(max_replays=1, window_seconds=60)
        await guard.record("sahool.ndvi.computed")
        guard.reset("sahool.ndvi.computed")
        await guard.check("sahool.ndvi.computed")  # must not raise after reset

    @pytest.mark.asyncio
    async def test_reset_all_clears_all_subjects(self):
        guard = OutboxReplayGuard(max_replays=1, window_seconds=60)
        await guard.record("sahool.ndvi.computed")
        await guard.record("sahool.weather.updated")
        guard.reset()
        await guard.check("sahool.ndvi.computed")  # must not raise
        await guard.check("sahool.weather.updated")  # must not raise

    def test_invalid_max_replays_raises(self):
        with pytest.raises(ValueError, match="max_replays"):
            OutboxReplayGuard(max_replays=0, window_seconds=60)

    def test_invalid_window_seconds_raises(self):
        with pytest.raises(ValueError, match="window_seconds"):
            OutboxReplayGuard(max_replays=3, window_seconds=0)

    def test_properties_exposed(self):
        guard = OutboxReplayGuard(max_replays=7, window_seconds=1800)
        assert guard.max_replays == 7
        assert guard.window_seconds == 1800

    @pytest.mark.asyncio
    async def test_count_in_window_empty_subject(self):
        guard = OutboxReplayGuard(max_replays=3, window_seconds=60)
        assert await guard.count_in_window("sahool.never.seen") == 0

    @pytest.mark.asyncio
    async def test_rate_limit_error_message_contains_subject(self):
        guard = OutboxReplayGuard(max_replays=1, window_seconds=60)
        await guard.record("sahool.ndvi.computed")
        with pytest.raises(ReplayRateLimitExceeded, match="sahool.ndvi.computed"):
            await guard.check("sahool.ndvi.computed")


# ---------------------------------------------------------------------------
# 12. ReplayGuard integration with reset_dead_lettered()
# ---------------------------------------------------------------------------


class TestReplayGuardIntegration:
    """reset_dead_lettered() must check the guard before the DB, record after."""

    @pytest.mark.asyncio
    async def test_guard_check_called_before_db(self):
        """DB must not be touched when the guard rejects the call."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 3")

        guard = OutboxReplayGuard(max_replays=1, window_seconds=60)
        await guard.record("sahool.ndvi.computed")  # exhaust limit

        with pytest.raises(ReplayRateLimitExceeded):
            await OutboxReplay.reset_dead_lettered(
                pool, subject="sahool.ndvi.computed", guard=guard
            )

        # No DB calls should have been made
        conn.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_guard_record_called_after_successful_reset(self):
        """guard.record() must be awaited after a successful reset."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 2")

        guard = OutboxReplayGuard(max_replays=5, window_seconds=3600)
        await OutboxReplay.reset_dead_lettered(
            pool, subject="sahool.ndvi.computed", guard=guard
        )

        assert await guard.count_in_window("sahool.ndvi.computed") == 1

    @pytest.mark.asyncio
    async def test_guard_not_recorded_when_zero_rows_reset(self):
        """guard.record() must NOT be called when count == 0 (no-op replay)."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 0")

        guard = OutboxReplayGuard(max_replays=5, window_seconds=3600)
        await OutboxReplay.reset_dead_lettered(
            pool, subject="sahool.ndvi.computed", guard=guard
        )

        assert await guard.count_in_window("sahool.ndvi.computed") == 0

    @pytest.mark.asyncio
    async def test_replay_blocked_metric_incremented_on_rate_limit(self):
        """outbox_replay_blocked_total must be incremented when guard blocks."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 1")

        guard = OutboxReplayGuard(max_replays=1, window_seconds=60)
        await guard.record("*")  # exhaust limit for all-replays key

        with patch("shared.libs.outbox.replay_tool.OUTBOX_METRICS") as mock_m:
            mock_m.replay_blocked = MagicMock()
            # reset_dead_lettered without subject/ids uses metric_subject="*"
            with pytest.raises(ReplayRateLimitExceeded):
                await OutboxReplay.reset_dead_lettered(pool, guard=guard)

        mock_m.replay_blocked.assert_called_once_with(subject="*", reason="rate_limit")

    @pytest.mark.asyncio
    async def test_no_guard_means_unlimited_replays(self):
        """Passing guard=None (default) must impose no rate limit."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 1")

        # Call ten times with no guard — must all succeed
        for _ in range(10):
            await OutboxReplay.reset_dead_lettered(pool)

    @pytest.mark.asyncio
    async def test_replay_blocked_facade_does_not_raise(self):
        """replay_blocked() must not raise even if Prometheus is absent."""
        OUTBOX_METRICS.replay_blocked(subject="sahool.test", reason="rate_limit")

    @pytest.mark.asyncio
    async def test_replay_blocked_called_with_prometheus_mock(self):
        """replay_blocked() must call the counter with correct labels."""
        mock_counter = MagicMock()
        mock_counter.labels.return_value = mock_counter

        import shared.libs.outbox.metrics as m

        original = m._replay_blocked_counter
        m._replay_blocked_counter = mock_counter
        try:
            OUTBOX_METRICS.replay_blocked(subject="sahool.test", reason="rate_limit")
            mock_counter.labels.assert_called_once_with(subject="sahool.test", reason="rate_limit")
            mock_counter.inc.assert_called_once()
        finally:
            m._replay_blocked_counter = original


# ---------------------------------------------------------------------------
# 13. DistributedReplayGovernor — DB-backed cluster-wide rate limiter
# ---------------------------------------------------------------------------

from shared.libs.outbox.replay_tool import DistributedReplayGovernor


def _make_governor_pool(count: int = 0):
    """Pool whose fetchrow returns {"n": count} and execute is a no-op."""
    conn = AsyncMock()
    tx = MagicMock()
    tx.__aenter__ = AsyncMock(return_value=None)
    tx.__aexit__ = AsyncMock(return_value=False)
    conn.transaction = MagicMock(return_value=tx)
    conn.fetchrow = AsyncMock(return_value={"n": count})
    conn.execute = AsyncMock(return_value=None)
    pool = MagicMock()
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=conn)
    ctx.__aexit__ = AsyncMock(return_value=False)
    pool.acquire = MagicMock(return_value=ctx)
    return pool, conn


class TestDistributedReplayGovernor:
    """DistributedReplayGovernor must enforce cluster-wide rate limits via DB."""

    @pytest.mark.asyncio
    async def test_check_allows_when_under_limit(self):
        pool, _ = _make_governor_pool(count=2)
        gov = DistributedReplayGovernor(pool, max_replays=5, window_seconds=3600)
        await gov.check("sahool.ndvi.computed")  # must not raise

    @pytest.mark.asyncio
    async def test_check_raises_when_at_limit(self):
        pool, _ = _make_governor_pool(count=5)
        gov = DistributedReplayGovernor(pool, max_replays=5, window_seconds=3600)
        with pytest.raises(ReplayRateLimitExceeded) as exc_info:
            await gov.check("sahool.ndvi.computed")
        assert exc_info.value.replays_in_window == 5
        assert exc_info.value.max_replays == 5

    @pytest.mark.asyncio
    async def test_check_raises_when_over_limit(self):
        pool, _ = _make_governor_pool(count=10)
        gov = DistributedReplayGovernor(pool, max_replays=3, window_seconds=60)
        with pytest.raises(ReplayRateLimitExceeded):
            await gov.check("sahool.weather.updated")

    @pytest.mark.asyncio
    async def test_check_acquires_advisory_lock(self):
        """check() must call pg_advisory_xact_lock inside a transaction."""
        from shared.libs.outbox.replay_tool import _GOVERNOR_LOCK_SQL
        pool, conn = _make_governor_pool(count=0)
        gov = DistributedReplayGovernor(pool, max_replays=5, window_seconds=3600)
        await gov.check("sahool.ndvi.computed")
        conn.execute.assert_awaited_once_with(_GOVERNOR_LOCK_SQL)

    @pytest.mark.asyncio
    async def test_check_passes_window_to_query(self):
        """check() must pass the configured window_seconds to the COUNT query."""
        from shared.libs.outbox.replay_tool import _GOVERNOR_COUNT_SQL
        pool, conn = _make_governor_pool(count=0)
        gov = DistributedReplayGovernor(pool, max_replays=5, window_seconds=1800)
        await gov.check("sahool.ndvi.computed")
        conn.fetchrow.assert_awaited_once_with(
            _GOVERNOR_COUNT_SQL, "sahool.ndvi.computed", 1800
        )

    @pytest.mark.asyncio
    async def test_record_inserts_ledger_row(self):
        """record() must INSERT into outbox_replay_ledger."""
        from shared.libs.outbox.replay_tool import _GOVERNOR_INSERT_SQL
        pool, conn = _make_governor_pool(count=0)
        gov = DistributedReplayGovernor(pool, max_replays=5, window_seconds=3600,
                                        instance_id="pod-0")
        await gov.record("sahool.ndvi.computed", replayed_by="ops")
        conn.execute.assert_awaited_once_with(
            _GOVERNOR_INSERT_SQL, "sahool.ndvi.computed", "ops", "pod-0"
        )

    @pytest.mark.asyncio
    async def test_count_in_window_returns_db_count(self):
        pool, _ = _make_governor_pool(count=3)
        gov = DistributedReplayGovernor(pool, max_replays=5, window_seconds=3600)
        result = await gov.count_in_window("sahool.ndvi.computed")
        assert result == 3

    @pytest.mark.asyncio
    async def test_count_in_window_returns_zero_on_empty(self):
        pool, conn = _make_governor_pool(count=0)
        conn.fetchrow = AsyncMock(return_value=None)  # fetchrow returns None for no rows
        gov = DistributedReplayGovernor(pool, max_replays=5, window_seconds=3600)
        result = await gov.count_in_window("sahool.ndvi.computed")
        assert result == 0

    def test_invalid_max_replays_raises(self):
        pool, _ = _make_governor_pool()
        with pytest.raises(ValueError, match="max_replays"):
            DistributedReplayGovernor(pool, max_replays=0, window_seconds=60)

    def test_invalid_window_seconds_raises(self):
        pool, _ = _make_governor_pool()
        with pytest.raises(ValueError, match="window_seconds"):
            DistributedReplayGovernor(pool, max_replays=3, window_seconds=0)

    def test_properties_exposed(self):
        pool, _ = _make_governor_pool()
        gov = DistributedReplayGovernor(pool, max_replays=10, window_seconds=7200)
        assert gov.max_replays == 10
        assert gov.window_seconds == 7200

    @pytest.mark.asyncio
    async def test_integration_with_reset_dead_lettered_blocked(self):
        """reset_dead_lettered() must not touch DLQ when governor rejects."""
        dlq_pool, dlq_conn = _make_db_pool()
        dlq_conn.execute = AsyncMock(return_value="UPDATE 3")

        gov_pool, _ = _make_governor_pool(count=5)
        gov = DistributedReplayGovernor(gov_pool, max_replays=5, window_seconds=3600)

        with pytest.raises(ReplayRateLimitExceeded):
            await OutboxReplay.reset_dead_lettered(
                dlq_pool, subject="sahool.ndvi.computed", guard=gov
            )

        # DLQ UPDATE must not have been called
        dlq_conn.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_integration_record_called_with_replayed_by(self):
        """governor.record() must receive the replayed_by from reset_dead_lettered."""
        dlq_pool, dlq_conn = _make_db_pool()
        dlq_conn.execute = AsyncMock(return_value="UPDATE 2")

        gov_pool, _ = _make_governor_pool(count=1)
        gov = DistributedReplayGovernor(gov_pool, max_replays=5, window_seconds=3600)
        gov.record = AsyncMock()

        await OutboxReplay.reset_dead_lettered(
            dlq_pool,
            subject="sahool.ndvi.computed",
            replayed_by="automated-recovery",
            guard=gov,
        )

        gov.record.assert_awaited_once_with(
            "sahool.ndvi.computed", replayed_by="automated-recovery"
        )


# ---------------------------------------------------------------------------
# 13. Replay Lifecycle State Machine — (A) REPLAYING / RECOVERED / FAILED_FINAL
# ---------------------------------------------------------------------------

from shared.libs.outbox.relay import _MARK_SENT_RECOVERED_SQL, _MARK_DLQ_FAILED_FINAL_SQL


class TestReplayLifecycleStateMachine:
    """Relay must transition replay_state correctly on publish success and DLQ."""

    # --- reset_dead_lettered sets replay_state = 'REPLAYING' ---

    @pytest.mark.asyncio
    async def test_reset_all_sets_replay_state_replaying(self):
        """reset_dead_lettered() must include replay_state = 'REPLAYING' in UPDATE."""
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 3")

        await OutboxReplay.reset_dead_lettered(pool)

        sql_used = conn.execute.call_args_list[1][0][0]  # second call = UPDATE
        assert "replay_state" in sql_used
        assert "'REPLAYING'" in sql_used

    @pytest.mark.asyncio
    async def test_reset_by_subject_sets_replay_state_replaying(self):
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 1")

        await OutboxReplay.reset_dead_lettered(pool, subject="sahool.ndvi.computed")

        sql_used = conn.execute.call_args_list[1][0][0]
        assert "replay_state" in sql_used
        assert "'REPLAYING'" in sql_used

    @pytest.mark.asyncio
    async def test_reset_by_ids_sets_replay_state_replaying(self):
        pool, conn = _make_db_pool()
        conn.execute = AsyncMock(return_value="UPDATE 2")
        id1, id2 = str(uuid.uuid4()), str(uuid.uuid4())

        await OutboxReplay.reset_dead_lettered(pool, ids=[id1, id2])

        sql_used = conn.execute.call_args_list[1][0][0]
        assert "replay_state" in sql_used
        assert "'REPLAYING'" in sql_used

    # --- relay uses RECOVERED SQL when replay_state == 'REPLAYING' ---

    @pytest.mark.asyncio
    async def test_relay_uses_recovered_sql_when_replaying(self):
        """On publish success, REPLAYING row must be marked with RECOVERED SQL."""
        row = _make_row()
        row["replay_state"] = "REPLAYING"
        pool, conn = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(return_value=None)
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        await relay._drain_batch(pool, nats_client, batch_size=10)

        # The execute call on the mark_conn must use the RECOVERED SQL
        executed_sqls = [str(call[0][0]) for call in conn.execute.call_args_list]
        assert any("RECOVERED" in sql for sql in executed_sqls)

    @pytest.mark.asyncio
    async def test_relay_uses_normal_sent_sql_when_not_replaying(self):
        """On publish success, non-REPLAYING row must NOT set replay_state."""
        row = _make_row()
        row["replay_state"] = None
        pool, conn = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(return_value=None)
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        await relay._drain_batch(pool, nats_client, batch_size=10)

        executed_sqls = [str(call[0][0]) for call in conn.execute.call_args_list]
        assert not any("RECOVERED" in sql for sql in executed_sqls)

    # --- relay uses FAILED_FINAL SQL when REPLAYING row hits max retries ---

    @pytest.mark.asyncio
    async def test_relay_uses_failed_final_sql_when_replaying_hits_max_retries(self):
        """REPLAYING row that exhausts retries must use FAILED_FINAL DLQ SQL."""
        row = _make_row(retry_count=_MAX_RETRIES - 1)
        row["replay_state"] = "REPLAYING"
        pool, conn = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(side_effect=Exception("permanent failure"))
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        await relay._drain_batch(pool, nats_client, batch_size=10)

        executed_sqls = [str(call[0][0]) for call in conn.execute.call_args_list]
        assert any("FAILED_FINAL" in sql for sql in executed_sqls)

    @pytest.mark.asyncio
    async def test_relay_uses_normal_dlq_sql_when_not_replaying(self):
        """Non-REPLAYING row at max retries must use standard DLQ SQL (no FAILED_FINAL)."""
        row = _make_row(retry_count=_MAX_RETRIES - 1)
        row["replay_state"] = None
        pool, conn = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(side_effect=Exception("permanent"))
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        await relay._drain_batch(pool, nats_client, batch_size=10)

        executed_sqls = [str(call[0][0]) for call in conn.execute.call_args_list]
        assert not any("FAILED_FINAL" in sql for sql in executed_sqls)

    # --- metrics emitted for lifecycle transitions ---

    @pytest.mark.asyncio
    async def test_replay_recovered_metric_emitted_on_replaying_success(self):
        row = _make_row()
        row["replay_state"] = "REPLAYING"
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(return_value=None)
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.OUTBOX_METRICS") as mock_metrics:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        mock_metrics.replay_recovered.assert_called_once_with(subject=row["subject"])

    @pytest.mark.asyncio
    async def test_replay_recovered_metric_not_emitted_for_normal_row(self):
        row = _make_row()
        row["replay_state"] = None
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(return_value=None)
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.OUTBOX_METRICS") as mock_metrics:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        mock_metrics.replay_recovered.assert_not_called()

    @pytest.mark.asyncio
    async def test_replay_failed_final_metric_emitted_on_replaying_dlq(self):
        row = _make_row(retry_count=_MAX_RETRIES - 1)
        row["replay_state"] = "REPLAYING"
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(side_effect=Exception("permanent"))
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.OUTBOX_METRICS") as mock_metrics:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        mock_metrics.replay_failed_final.assert_called_once_with(subject=row["subject"])

    @pytest.mark.asyncio
    async def test_replay_failed_final_metric_not_emitted_for_normal_dlq(self):
        row = _make_row(retry_count=_MAX_RETRIES - 1)
        row["replay_state"] = None
        pool, _ = _make_db_pool(rows=[row])

        nats_client = AsyncMock()
        nats_client.publish = AsyncMock(side_effect=Exception("permanent"))
        nats_client.jetstream = None

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.OUTBOX_METRICS") as mock_metrics:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        mock_metrics.replay_failed_final.assert_not_called()


# ---------------------------------------------------------------------------
# 14. New metrics façade — recovered / failed_final / policy_suppressed / gauge
# ---------------------------------------------------------------------------


class TestNewMetricsFacade:
    """New metrics added by the vNext control plane must be safe in all envs."""

    def test_replay_recovered_does_not_raise(self):
        OUTBOX_METRICS.replay_recovered(subject="sahool.test")

    def test_replay_failed_final_does_not_raise(self):
        OUTBOX_METRICS.replay_failed_final(subject="sahool.test")

    def test_replay_policy_suppressed_does_not_raise(self):
        OUTBOX_METRICS.replay_policy_suppressed(reason="dlq_growth")

    def test_set_governor_usage_does_not_raise(self):
        OUTBOX_METRICS.set_governor_usage(subject="sahool.test", utilization_pct=75.0)

    def test_replay_recovered_called_with_prometheus_mock(self):
        mock_counter = MagicMock()
        mock_counter.labels.return_value = mock_counter

        import shared.libs.outbox.metrics as m

        original = m._replay_recovered_counter
        m._replay_recovered_counter = mock_counter
        try:
            OUTBOX_METRICS.replay_recovered(subject="sahool.ndvi")
            mock_counter.labels.assert_called_once_with(subject="sahool.ndvi")
            mock_counter.inc.assert_called_once()
        finally:
            m._replay_recovered_counter = original

    def test_replay_failed_final_called_with_prometheus_mock(self):
        mock_counter = MagicMock()
        mock_counter.labels.return_value = mock_counter

        import shared.libs.outbox.metrics as m

        original = m._replay_failed_final_counter
        m._replay_failed_final_counter = mock_counter
        try:
            OUTBOX_METRICS.replay_failed_final(subject="sahool.ndvi")
            mock_counter.labels.assert_called_once_with(subject="sahool.ndvi")
            mock_counter.inc.assert_called_once()
        finally:
            m._replay_failed_final_counter = original

    def test_replay_policy_suppressed_called_with_prometheus_mock(self):
        mock_counter = MagicMock()
        mock_counter.labels.return_value = mock_counter

        import shared.libs.outbox.metrics as m

        original = m._replay_policy_suppressed_counter
        m._replay_policy_suppressed_counter = mock_counter
        try:
            OUTBOX_METRICS.replay_policy_suppressed(reason="success_rate_too_low")
            mock_counter.labels.assert_called_once_with(reason="success_rate_too_low")
            mock_counter.inc.assert_called_once()
        finally:
            m._replay_policy_suppressed_counter = original

    def test_set_governor_usage_called_with_prometheus_mock(self):
        mock_gauge = MagicMock()
        mock_gauge.labels.return_value = mock_gauge

        import shared.libs.outbox.metrics as m

        original = m._governor_usage_gauge
        m._governor_usage_gauge = mock_gauge
        try:
            OUTBOX_METRICS.set_governor_usage(subject="sahool.ndvi", utilization_pct=60.0)
            mock_gauge.labels.assert_called_once_with(subject="sahool.ndvi")
            mock_gauge.set.assert_called_once_with(60.0)
        finally:
            m._governor_usage_gauge = original


# ---------------------------------------------------------------------------
# 15. inspect_governor — read-only governor snapshot (C)
# ---------------------------------------------------------------------------



def _make_governor_inspect_pool(
    replays_in_window=0,
    oldest_replay_at=None,
    newest_replay_at=None,
    instances_seen=None,
):
    """Build a mock pool that returns a single fetchrow result for inspect_governor."""
    conn = AsyncMock()
    tx = MagicMock()
    tx.__aenter__ = AsyncMock(return_value=None)
    tx.__aexit__ = AsyncMock(return_value=False)
    conn.transaction = MagicMock(return_value=tx)
    conn.fetchrow = AsyncMock(
        return_value={
            "replays_in_window": replays_in_window,
            "oldest_replay_at": oldest_replay_at,
            "newest_replay_at": newest_replay_at,
            "instances_seen": instances_seen or [],
        }
    )
    conn.execute = AsyncMock(return_value=None)
    pool = MagicMock()
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=conn)
    ctx.__aexit__ = AsyncMock(return_value=False)
    pool.acquire = MagicMock(return_value=ctx)
    return pool, conn


class TestInspectGovernor:
    """inspect_governor() must return correct structured snapshot without modifying rows."""

    @pytest.mark.asyncio
    async def test_returns_zero_when_no_replays_in_window(self):
        pool, _ = _make_governor_inspect_pool(replays_in_window=0)

        info = await OutboxReplay.inspect_governor(pool, "sahool.ndvi.computed", 3600)

        assert info["replays_in_window"] == 0
        assert info["oldest_replay_at"] is None
        assert info["newest_replay_at"] is None

    @pytest.mark.asyncio
    async def test_returns_correct_replay_count(self):
        now = datetime.now(tz=UTC)
        pool, _ = _make_governor_inspect_pool(
            replays_in_window=3,
            oldest_replay_at=now - timedelta(hours=2),
            newest_replay_at=now - timedelta(minutes=30),
            instances_seen=["pod-0", "pod-1"],
        )

        info = await OutboxReplay.inspect_governor(pool, "sahool.ndvi.computed", 3600)

        assert info["replays_in_window"] == 3
        assert info["instances_seen"] == ["pod-0", "pod-1"]
        assert info["oldest_replay_at"] is not None
        assert info["newest_replay_at"] is not None

    @pytest.mark.asyncio
    async def test_computes_utilization_when_max_replays_given(self):
        pool, _ = _make_governor_inspect_pool(replays_in_window=3)

        info = await OutboxReplay.inspect_governor(
            pool, "sahool.ndvi.computed", 3600, max_replays=5
        )

        assert info["limit"] == 5
        assert info["utilization_pct"] == pytest.approx(60.0)
        assert info["is_blocked"] is False

    @pytest.mark.asyncio
    async def test_is_blocked_true_when_at_limit(self):
        pool, _ = _make_governor_inspect_pool(replays_in_window=5)

        info = await OutboxReplay.inspect_governor(
            pool, "sahool.ndvi.computed", 3600, max_replays=5
        )

        assert info["is_blocked"] is True
        assert info["utilization_pct"] == pytest.approx(100.0)

    @pytest.mark.asyncio
    async def test_limit_and_utilization_none_when_max_replays_not_given(self):
        pool, _ = _make_governor_inspect_pool(replays_in_window=2)

        info = await OutboxReplay.inspect_governor(pool, "sahool.ndvi.computed", 3600)

        assert info["limit"] is None
        assert info["utilization_pct"] is None
        assert info["is_blocked"] is None

    @pytest.mark.asyncio
    async def test_does_not_call_execute(self):
        """inspect_governor must never write to the database."""
        pool, conn = _make_governor_inspect_pool()

        await OutboxReplay.inspect_governor(pool, "sahool.ndvi.computed", 3600)

        conn.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_timestamps_returned_as_iso8601_strings(self):
        now = datetime.now(tz=UTC)
        pool, _ = _make_governor_inspect_pool(
            replays_in_window=1,
            oldest_replay_at=now - timedelta(hours=1),
            newest_replay_at=now,
        )

        info = await OutboxReplay.inspect_governor(pool, "sahool.ndvi.computed", 3600)

        assert isinstance(info["oldest_replay_at"], str)
        assert isinstance(info["newest_replay_at"], str)
        # Must be parseable ISO 8601
        datetime.fromisoformat(info["oldest_replay_at"])
        datetime.fromisoformat(info["newest_replay_at"])


# ---------------------------------------------------------------------------
# 16. Replay Governance Policy Engine — (B)
# ---------------------------------------------------------------------------

from shared.libs.outbox.replay_policy import ReplayPolicy, PolicyDecision, ReplayPolicyEngine


def _make_policy_pool(dlq_count=0, recovered_count=0, failed_final_count=0):
    """Build a mock pool returning three fetchrow results for policy evaluate().

    The side_effect order matches ReplayPolicyEngine.evaluate()'s query order:
    1. _POLICY_DLQ_COUNT_SQL  → {"n": dlq_count}
    2. _POLICY_RECOVERED_COUNT_SQL → {"n": recovered_count}
    3. _POLICY_FAILED_FINAL_COUNT_SQL → {"n": failed_final_count}
    """
    conn = AsyncMock()
    tx = MagicMock()
    tx.__aenter__ = AsyncMock(return_value=None)
    tx.__aexit__ = AsyncMock(return_value=False)
    conn.transaction = MagicMock(return_value=tx)
    conn.fetchrow = AsyncMock(side_effect=[
        {"n": dlq_count},
        {"n": recovered_count},
        {"n": failed_final_count},
    ])
    conn.execute = AsyncMock(return_value=None)
    pool = MagicMock()
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=conn)
    ctx.__aexit__ = AsyncMock(return_value=False)
    pool.acquire = MagicMock(return_value=ctx)
    return pool


class TestReplayPolicyEngine:
    """ReplayPolicyEngine must correctly evaluate health signals and return decisions."""

    @pytest.mark.asyncio
    async def test_allows_when_no_dlq_and_no_history(self):
        """With no DLQ rows and no replay outcomes, policy must allow."""
        pool = _make_policy_pool(dlq_count=0, recovered_count=0, failed_final_count=0)
        engine = ReplayPolicyEngine()

        decision = await engine.evaluate(pool)

        assert decision.allowed is True
        assert decision.reason == "ok"

    @pytest.mark.asyncio
    async def test_allows_when_dlq_below_threshold(self):
        """DLQ count below threshold (10/min * 5min window = 50 rows) must allow."""
        # window=300s, threshold=10/min → 50 rows/window allowed before suppression
        pool = _make_policy_pool(dlq_count=30, recovered_count=5, failed_final_count=1)
        engine = ReplayPolicyEngine(ReplayPolicy(dlq_growth_threshold=10.0, evaluate_window_seconds=300))

        decision = await engine.evaluate(pool)

        assert decision.allowed is True

    @pytest.mark.asyncio
    async def test_suppresses_when_dlq_exceeds_threshold(self):
        """DLQ growth rate >= threshold must suppress replay."""
        # threshold=10/min, window=300s → 50 rows/window = exactly threshold
        # Use 51 rows to exceed the threshold
        pool = _make_policy_pool(dlq_count=51, recovered_count=0, failed_final_count=0)
        engine = ReplayPolicyEngine(ReplayPolicy(dlq_growth_threshold=10.0, evaluate_window_seconds=300))

        decision = await engine.evaluate(pool)

        assert decision.allowed is False
        assert decision.reason == "dlq_growth"

    @pytest.mark.asyncio
    async def test_suppresses_when_success_rate_below_floor(self):
        """Success rate below floor must suppress replay."""
        # 1 recovered, 9 failed_final → success_rate = 10% < 20% floor
        pool = _make_policy_pool(dlq_count=0, recovered_count=1, failed_final_count=9)
        engine = ReplayPolicyEngine(ReplayPolicy(dlq_growth_threshold=100.0, success_rate_floor=0.20))

        decision = await engine.evaluate(pool)

        assert decision.allowed is False
        assert decision.reason == "success_rate_too_low"

    @pytest.mark.asyncio
    async def test_allows_when_success_rate_at_or_above_floor(self):
        """Success rate >= floor must allow."""
        # 2 recovered, 8 failed_final → success_rate = 20% == floor
        pool = _make_policy_pool(dlq_count=0, recovered_count=2, failed_final_count=8)
        engine = ReplayPolicyEngine(ReplayPolicy(dlq_growth_threshold=100.0, success_rate_floor=0.20))

        decision = await engine.evaluate(pool)

        assert decision.allowed is True

    @pytest.mark.asyncio
    async def test_skips_success_rate_check_when_no_terminal_outcomes(self):
        """When total_terminal == 0, success rate check must be skipped (no false suppression)."""
        pool = _make_policy_pool(dlq_count=0, recovered_count=0, failed_final_count=0)
        engine = ReplayPolicyEngine(ReplayPolicy(success_rate_floor=1.0))  # impossible floor

        decision = await engine.evaluate(pool)

        assert decision.allowed is True

    @pytest.mark.asyncio
    async def test_dlq_check_takes_priority_over_success_rate(self):
        """DLQ growth suppression is checked first; success_rate is only checked when DLQ is healthy."""
        # Extremely high DLQ growth — should suppress with dlq_growth reason
        pool = _make_policy_pool(dlq_count=999, recovered_count=10, failed_final_count=0)
        engine = ReplayPolicyEngine(ReplayPolicy(dlq_growth_threshold=1.0, evaluate_window_seconds=60))

        decision = await engine.evaluate(pool)

        assert decision.allowed is False
        assert decision.reason == "dlq_growth"  # not success_rate_too_low


class TestGovernorPolicyIntegration:
    """DistributedReplayGovernor must route through policy before the COUNT query."""

    def _make_governor_db_pool(self, count_in_window=0):
        """Pool that handles governor's own check() calls (advisory lock + COUNT)."""
        conn = AsyncMock()
        tx = MagicMock()
        tx.__aenter__ = AsyncMock(return_value=None)
        tx.__aexit__ = AsyncMock(return_value=False)
        conn.transaction = MagicMock(return_value=tx)
        conn.fetchrow = AsyncMock(return_value={"n": count_in_window})
        conn.execute = AsyncMock(return_value=None)
        pool = MagicMock()
        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(return_value=conn)
        ctx.__aexit__ = AsyncMock(return_value=False)
        pool.acquire = MagicMock(return_value=ctx)
        return pool

    @pytest.mark.asyncio
    async def test_governor_raises_rate_limit_exceeded_with_policy_reason_when_policy_suppresses(self):
        pool = self._make_governor_db_pool()
        policy_engine = AsyncMock(spec=ReplayPolicyEngine)
        policy_engine.evaluate = AsyncMock(
            return_value=PolicyDecision(allowed=False, reason="dlq_growth")
        )
        governor = DistributedReplayGovernor(pool, max_replays=5, window_seconds=3600, policy=policy_engine)

        with pytest.raises(ReplayRateLimitExceeded) as exc_info:
            await governor.check("sahool.ndvi.computed")

        err = exc_info.value
        assert err.policy_reason == "dlq_growth"
        assert "policy" in str(err).lower() or "suppressed" in str(err).lower()

    @pytest.mark.asyncio
    async def test_governor_proceeds_to_count_when_policy_allows(self):
        """When policy allows, governor must still enforce the sliding-window count."""
        pool = self._make_governor_db_pool(count_in_window=0)
        policy_engine = AsyncMock(spec=ReplayPolicyEngine)
        policy_engine.evaluate = AsyncMock(
            return_value=PolicyDecision(allowed=True, reason="ok")
        )
        governor = DistributedReplayGovernor(pool, max_replays=5, window_seconds=3600, policy=policy_engine)

        # Must not raise when count=0 and policy allows
        await governor.check("sahool.ndvi.computed")  # no exception

        policy_engine.evaluate.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_governor_skips_policy_when_none(self):
        """When no policy is set, governor must only enforce the sliding-window count."""
        pool = self._make_governor_db_pool(count_in_window=0)
        governor = DistributedReplayGovernor(pool, max_replays=5, window_seconds=3600, policy=None)

        await governor.check("sahool.ndvi.computed")  # must not raise

    @pytest.mark.asyncio
    async def test_reset_dead_lettered_emits_policy_suppressed_metric_on_policy_block(self):
        """reset_dead_lettered must emit replay_policy_suppressed metric when policy blocks."""
        dlq_pool, dlq_conn = _make_db_pool()
        dlq_conn.execute = AsyncMock(return_value="UPDATE 0")

        governor = AsyncMock(spec=DistributedReplayGovernor)
        governor.check = AsyncMock(
            side_effect=ReplayRateLimitExceeded(
                subject="*",
                replays_in_window=0,
                max_replays=5,
                window_seconds=3600,
                policy_reason="success_rate_too_low",
            )
        )

        with patch("shared.libs.outbox.replay_tool.OUTBOX_METRICS") as mock_m:
            with pytest.raises(ReplayRateLimitExceeded):
                await OutboxReplay.reset_dead_lettered(dlq_pool, guard=governor)

        mock_m.replay_blocked.assert_called_once_with(subject="*", reason="policy")
        mock_m.replay_policy_suppressed.assert_called_once_with(reason="success_rate_too_low")

    @pytest.mark.asyncio
    async def test_reset_dead_lettered_does_not_emit_policy_suppressed_for_rate_limit_block(self):
        """When blocked by rate limit (not policy), policy_suppressed must NOT be emitted."""
        dlq_pool, dlq_conn = _make_db_pool()
        dlq_conn.execute = AsyncMock(return_value="UPDATE 0")

        governor = AsyncMock(spec=DistributedReplayGovernor)
        governor.check = AsyncMock(
            side_effect=ReplayRateLimitExceeded(
                subject="*",
                replays_in_window=5,
                max_replays=5,
                window_seconds=3600,
                policy_reason=None,  # rate-limit, not policy
            )
        )

        with patch("shared.libs.outbox.replay_tool.OUTBOX_METRICS") as mock_m:
            with pytest.raises(ReplayRateLimitExceeded):
                await OutboxReplay.reset_dead_lettered(dlq_pool, guard=governor)

        mock_m.replay_blocked.assert_called_once_with(subject="*", reason="rate_limit")
        mock_m.replay_policy_suppressed.assert_not_called()
