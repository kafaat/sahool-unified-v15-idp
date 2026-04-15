"""
Tests for shared/events/outbox.py — Transactional outbox pattern
"""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.events.outbox import (
    OutboxRelay,
    _MAX_RELAY_RETRIES,
    _SQL_INSERT_OUTBOX,
    _SQL_MARK_DLQ,
    _SQL_MARK_FAILED,
    _SQL_MARK_SENT,
    ensure_outbox_table,
    write_outbox_event,
)


class TestWriteOutboxEvent:
    """Tests for write_outbox_event helper."""

    @pytest.mark.asyncio
    async def test_inserts_event_with_all_fields(self):
        conn = AsyncMock()
        event_id = await write_outbox_event(
            conn,
            subject="sahool.field.created",
            payload='{"field_id": "f1"}',
            correlation_id="corr-123",
            tenant_id="tenant-abc",
            headers={"X-Source": "test"},
        )
        assert isinstance(event_id, str)
        assert len(event_id) == 36  # UUID format
        conn.execute.assert_awaited_once()
        call_args = conn.execute.call_args
        assert call_args[0][0] == _SQL_INSERT_OUTBOX
        assert call_args[0][2] == "sahool.field.created"
        assert call_args[0][3] == '{"field_id": "f1"}'
        assert call_args[0][4] == json.dumps({"X-Source": "test"})
        assert call_args[0][5] == "tenant-abc"
        assert call_args[0][6] == "corr-123"

    @pytest.mark.asyncio
    async def test_inserts_event_without_optional_fields(self):
        conn = AsyncMock()
        event_id = await write_outbox_event(
            conn,
            subject="sahool.weather.alert",
            payload='{}',
        )
        assert isinstance(event_id, str)
        call_args = conn.execute.call_args
        # headers_json should be None, tenant_id None, correlation_id None
        assert call_args[0][4] is None  # headers_json
        assert call_args[0][5] is None  # tenant_id
        assert call_args[0][6] is None  # correlation_id


class TestOutboxRelay:
    """Tests for the OutboxRelay background publisher."""

    def _make_relay(self, db_pool=None, publisher=None, poll_interval=0.01, batch_size=10):
        return OutboxRelay(
            db_pool=db_pool or MagicMock(),
            publisher=publisher or MagicMock(),
            poll_interval=poll_interval,
            batch_size=batch_size,
        )

    def test_initial_state(self):
        relay = self._make_relay()
        assert relay.published_count == 0
        assert relay.failed_count == 0
        assert relay._running is False
        assert relay._task is None

    @pytest.mark.asyncio
    async def test_start_sets_running(self):
        relay = self._make_relay()
        # Mock _loop to avoid actual polling
        relay._loop = AsyncMock()
        await relay.start()
        assert relay._running is True
        assert relay._task is not None
        # Clean up
        await relay.stop()

    @pytest.mark.asyncio
    async def test_start_idempotent(self):
        relay = self._make_relay()
        relay._loop = AsyncMock()
        await relay.start()
        task1 = relay._task
        await relay.start()  # Should not create a new task
        assert relay._task is task1
        await relay.stop()

    @pytest.mark.asyncio
    async def test_stop_cancels_task(self):
        relay = self._make_relay()
        relay._loop = AsyncMock()
        await relay.start()
        await relay.stop()
        assert relay._running is False

    @pytest.mark.asyncio
    async def test_relay_batch_returns_zero_when_no_pool(self):
        relay = self._make_relay(db_pool=None)
        relay._pool = None
        count = await relay._relay_batch()
        assert count == 0

    @pytest.mark.asyncio
    async def test_relay_batch_publishes_via_jetstream(self):
        """Test publishing via JetStream when available."""
        mock_row = {
            "id": "row-1",
            "subject": "sahool.field.created",
            "payload": '{"field_id": "f1"}',
            "headers_json": None,
            "tenant_id": "t1",
            "correlation_id": "c1",
            "retry_count": 0,
        }

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[mock_row])
        mock_conn.execute = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.acquire.return_value = mock_conn

        mock_js = AsyncMock()
        mock_publisher = MagicMock()
        mock_publisher._js = mock_js
        mock_publisher._nc = None

        relay = self._make_relay(db_pool=mock_pool, publisher=mock_publisher)
        count = await relay._relay_batch()

        assert count == 1
        assert relay.published_count == 1
        mock_js.publish.assert_awaited_once()
        mock_conn.execute.assert_any_await(_SQL_MARK_SENT, "row-1")

    @pytest.mark.asyncio
    async def test_relay_batch_publishes_via_nc_fallback(self):
        """Test publishing via core NATS when JetStream not available."""
        mock_row = {
            "id": "row-2",
            "subject": "sahool.test",
            "payload": "{}",
            "headers_json": '{"key": "val"}',
            "tenant_id": None,
            "correlation_id": None,
            "retry_count": 0,
        }

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[mock_row])
        mock_conn.execute = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.acquire.return_value = mock_conn

        mock_nc = AsyncMock()
        mock_publisher = MagicMock()
        mock_publisher._js = None
        mock_publisher._nc = mock_nc

        relay = self._make_relay(db_pool=mock_pool, publisher=mock_publisher)
        count = await relay._relay_batch()

        assert count == 1
        mock_nc.publish.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_relay_batch_marks_failed_on_error(self):
        """Test that publish failure increments retry count."""
        mock_row = {
            "id": "row-3",
            "subject": "sahool.fail",
            "payload": "{}",
            "headers_json": None,
            "tenant_id": None,
            "correlation_id": None,
            "retry_count": 0,  # Below max retries
        }

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[mock_row])
        mock_conn.execute = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.acquire.return_value = mock_conn

        mock_publisher = MagicMock()
        mock_publisher._js = None
        mock_publisher._nc = None  # No connection = RuntimeError

        relay = self._make_relay(db_pool=mock_pool, publisher=mock_publisher)
        count = await relay._relay_batch()

        assert count == 0
        assert relay.failed_count == 1
        # Should mark as failed (not DLQ since retry_count + 1 < _MAX_RELAY_RETRIES)
        execute_calls = mock_conn.execute.call_args_list
        failed_calls = [c for c in execute_calls if c[0][0] == _SQL_MARK_FAILED]
        assert len(failed_calls) == 1
        assert failed_calls[0][0][1] == "row-3"

    @pytest.mark.asyncio
    async def test_relay_batch_moves_to_dlq_after_max_retries(self):
        """Test that event is moved to DLQ after max retries."""
        mock_row = {
            "id": "row-4",
            "subject": "sahool.exhaust",
            "payload": "{}",
            "headers_json": None,
            "tenant_id": None,
            "correlation_id": None,
            "retry_count": _MAX_RELAY_RETRIES - 1,  # Will exceed on this attempt
        }

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[mock_row])
        mock_conn.execute = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.acquire.return_value = mock_conn

        mock_publisher = MagicMock()
        mock_publisher._js = None
        mock_publisher._nc = None

        relay = self._make_relay(db_pool=mock_pool, publisher=mock_publisher)
        count = await relay._relay_batch()

        assert count == 0
        assert relay.failed_count == 1
        # Should use DLQ SQL since retry_count + 1 >= _MAX_RELAY_RETRIES
        execute_calls = [c[0] for c in mock_conn.execute.call_args_list]
        dlq_calls = [c for c in execute_calls if c[0] == _SQL_MARK_DLQ]
        assert len(dlq_calls) == 1

    @pytest.mark.asyncio
    async def test_cleanup_sent_returns_zero_when_no_pool(self):
        relay = self._make_relay()
        relay._pool = None
        count = await relay.cleanup_sent()
        assert count == 0

    @pytest.mark.asyncio
    async def test_cleanup_sent_deletes_old_events(self):
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock(return_value="DELETE 5")
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.acquire.return_value = mock_conn

        relay = self._make_relay(db_pool=mock_pool)
        count = await relay.cleanup_sent()
        assert count == 5

    @pytest.mark.asyncio
    async def test_cleanup_sent_handles_no_result(self):
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock(return_value=None)
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.acquire.return_value = mock_conn

        relay = self._make_relay(db_pool=mock_pool)
        count = await relay.cleanup_sent()
        assert count == 0


class TestEnsureOutboxTable:
    """Tests for ensure_outbox_table."""

    @pytest.mark.asyncio
    async def test_noop_when_no_pool(self):
        await ensure_outbox_table(None)  # Should not raise

    @pytest.mark.asyncio
    async def test_creates_table(self):
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.acquire.return_value = mock_conn

        await ensure_outbox_table(mock_pool)
        mock_conn.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handles_error_gracefully(self):
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock(side_effect=RuntimeError("DB error"))
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        mock_pool = MagicMock()
        mock_pool.acquire.return_value = mock_conn

        # Should not raise, just log warning
        await ensure_outbox_table(mock_pool)
