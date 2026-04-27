"""
Unit tests for:

1. shared/libs/outbox/metrics.py — OUTBOX_METRICS façade
2. shared/libs/outbox/replay_tool.py — OutboxReplay helpers
3. Relay structured logging — logs carry event_id, subject, tenant_id, worker_id
4. Relay metrics integration — counters increment on publish/fail/DLQ
"""

from __future__ import annotations

import uuid
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
        del nats_client.jetstream

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
        del nats_client.jetstream

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
        del nats_client.jetstream

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
        del nats_client.jetstream

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
        del nats_client.jetstream

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
        del nats_client.jetstream

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
        del nats_client.jetstream

        relay = OutboxRelay(worker_id="w-test")
        with patch("shared.libs.outbox.relay.OUTBOX_METRICS") as mock_metrics:
            await relay._drain_batch(pool, nats_client, batch_size=10)

        mock_metrics.failed.assert_called_once_with(
            subject=row["subject"], reason="ConnectionRefusedError"
        )
