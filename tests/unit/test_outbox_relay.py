"""
Unit tests for shared/libs/outbox/relay.py — OutboxRelay

Validates four failure modes that must hold in production:

1. NATS failure → row stays in outbox (retry invariant)
2. max-retry exhaustion → row dead-lettered (no infinite loop)
3. FOR UPDATE SKIP LOCKED prevents duplicate publication across workers
4. JetStream publish used when available; core NATS fallback otherwise

All tests are fully offline — no real database or NATS connection needed.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from shared.libs.outbox.relay import (
    _FETCH_SQL,
    _MARK_DLQ_SQL,
    _MARK_FAILED_SQL,
    _MARK_SENT_SQL,
    _MAX_RETRIES,
    OutboxRelay,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_row(retry_count: int = 0) -> dict:
    """Return a fake outbox_messages row."""
    return {
        "id": uuid.uuid4(),
        "subject": "sahool.satellite.ndvi.computed",
        "payload": b'{"field_id":"f1","value":0.7}',
        "headers": '{"X-Event-ID":"evt-001"}',
        "retry_count": retry_count,
        "tenant_id": "tenant-test",
    }


def _make_db_pool(rows=None, fetch_side_effect=None):
    """
    Build a mock asyncpg pool that returns *rows* from conn.fetch() and
    supports repeated ``acquire()`` calls (one per mark operation).

    ``pool.acquire()`` returns a new MagicMock conn each time it is used as
    an async context manager, so each acquire() call is independent.
    """
    conn = AsyncMock()
    tx = MagicMock()
    tx.__aenter__ = AsyncMock(return_value=None)
    tx.__aexit__ = AsyncMock(return_value=False)
    conn.transaction = MagicMock(return_value=tx)
    if fetch_side_effect:
        conn.fetch = AsyncMock(side_effect=fetch_side_effect)
    else:
        conn.fetch = AsyncMock(return_value=rows or [])
    conn.execute = AsyncMock(return_value=None)

    # Each call to pool.acquire().__aenter__ returns conn (shared for fetch),
    # subsequent mark-conn acquires also return the same mock which is fine
    # for unit tests (we only assert execute was called with correct SQL).
    pool = MagicMock()
    acquire_ctx = MagicMock()
    acquire_ctx.__aenter__ = AsyncMock(return_value=conn)
    acquire_ctx.__aexit__ = AsyncMock(return_value=False)
    pool.acquire = MagicMock(return_value=acquire_ctx)
    return pool, conn


# ---------------------------------------------------------------------------
# 1. NATS failure → row stays in outbox
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_nats_failure_marks_failed_not_sent():
    """
    When NATS publish raises, the row must be marked FAILED (retry_count++)
    and must NOT be marked SENT.
    """
    row = _make_row(retry_count=0)
    pool, conn = _make_db_pool(rows=[row])

    nats_client = AsyncMock()
    nats_client.publish = AsyncMock(side_effect=Exception("NATS connection refused"))
    # No jetstream() method — falls straight to nc.publish
    del nats_client.jetstream

    relay = OutboxRelay(worker_id="test-worker")
    published = await relay._drain_batch(pool, nats_client, batch_size=10)

    assert published == 0

    # Collect all execute calls
    execute_calls = [c[0][0] for c in conn.execute.call_args_list]
    assert any(_MARK_FAILED_SQL in sql for sql in execute_calls), (
        "Expected MARK_FAILED SQL but got: " + str(execute_calls)
    )
    assert not any(_MARK_SENT_SQL in sql for sql in execute_calls), (
        "Row must NOT be marked sent on NATS failure"
    )
    assert not any(_MARK_DLQ_SQL in sql for sql in execute_calls), (
        "Row with retry_count=0 must not be dead-lettered yet"
    )


# ---------------------------------------------------------------------------
# 2. Max-retry exhaustion → dead-letter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_max_retry_dead_letters_row():
    """
    A row whose ``retry_count`` is already ``_MAX_RETRIES - 1`` must be
    dead-lettered (``_MARK_DLQ_SQL``) on the next publish failure — not just
    incremented and retried again.
    """
    row = _make_row(retry_count=_MAX_RETRIES - 1)
    pool, conn = _make_db_pool(rows=[row])

    nats_client = AsyncMock()
    nats_client.publish = AsyncMock(side_effect=Exception("permanent NATS error"))
    del nats_client.jetstream

    relay = OutboxRelay(worker_id="test-worker")
    published = await relay._drain_batch(pool, nats_client, batch_size=10)

    assert published == 0

    execute_calls = [c[0][0] for c in conn.execute.call_args_list]
    assert any(_MARK_DLQ_SQL in sql for sql in execute_calls), (
        "Row at max retries must be dead-lettered"
    )
    assert not any(_MARK_FAILED_SQL in sql for sql in execute_calls), (
        "Dead-lettered row must not also be marked failed"
    )
    assert not any(_MARK_SENT_SQL in sql for sql in execute_calls), (
        "Dead-lettered row must not be marked sent"
    )


@pytest.mark.asyncio
async def test_below_max_retry_uses_mark_failed():
    """
    A row with retry_count = _MAX_RETRIES - 2 (one below the threshold)
    must use _MARK_FAILED_SQL, not _MARK_DLQ_SQL.
    """
    row = _make_row(retry_count=_MAX_RETRIES - 2)
    pool, conn = _make_db_pool(rows=[row])

    nats_client = AsyncMock()
    nats_client.publish = AsyncMock(side_effect=Exception("transient error"))
    del nats_client.jetstream

    relay = OutboxRelay(worker_id="test-worker")
    await relay._drain_batch(pool, nats_client, batch_size=10)

    execute_calls = [c[0][0] for c in conn.execute.call_args_list]
    assert any(_MARK_FAILED_SQL in sql for sql in execute_calls)
    assert not any(_MARK_DLQ_SQL in sql for sql in execute_calls)


# ---------------------------------------------------------------------------
# 3. FOR UPDATE SKIP LOCKED prevents duplicate publication
# ---------------------------------------------------------------------------


def test_fetch_sql_contains_skip_locked():
    """
    The _FETCH_SQL must contain ``FOR UPDATE SKIP LOCKED`` to prevent two
    concurrent relay workers from claiming the same batch of rows.
    """
    assert "FOR UPDATE SKIP LOCKED" in _FETCH_SQL


def test_fetch_sql_excludes_dead_lettered_rows():
    """
    The _FETCH_SQL must filter out dead-lettered rows so they are never
    retried after exhausting max attempts.
    """
    assert "dead_lettered_at IS NULL" in _FETCH_SQL


def test_fetch_sql_excludes_already_published():
    """
    The _FETCH_SQL must filter out already-published rows.
    """
    assert "published_at IS NULL" in _FETCH_SQL


@pytest.mark.asyncio
async def test_two_drain_batches_on_same_row_do_not_double_publish():
    """
    Simulates two concurrent relay workers both attempting to drain the same
    row. The second call returns an empty batch (mimicking SKIP LOCKED
    excluding already-claimed rows), so the total published count is 1.
    """
    row = _make_row(retry_count=0)

    # First call returns the row; second call returns empty (SKIP LOCKED effect)
    fetch_calls = [[row], []]
    call_index = {"n": 0}

    async def _fetch_side_effect(*args, **kwargs):
        result = fetch_calls[call_index["n"]]
        call_index["n"] = min(call_index["n"] + 1, len(fetch_calls) - 1)
        return result

    pool, conn = _make_db_pool(fetch_side_effect=_fetch_side_effect)

    nats_client = AsyncMock()
    nats_client.publish = AsyncMock(return_value=None)
    del nats_client.jetstream

    relay1 = OutboxRelay(worker_id="worker-1")
    relay2 = OutboxRelay(worker_id="worker-2")

    published_1 = await relay1._drain_batch(pool, nats_client, batch_size=10)
    published_2 = await relay2._drain_batch(pool, nats_client, batch_size=10)

    assert published_1 == 1
    assert published_2 == 0  # SKIP LOCKED: second worker got nothing

    # nc.publish called exactly once across both workers
    assert nats_client.publish.await_count == 1


# ---------------------------------------------------------------------------
# 4. JetStream publish preferred; nc.publish fallback
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_jetstream_publish_used_when_available():
    """
    When nats_client.jetstream() is available and js.publish succeeds, the
    relay must use js.publish (not nc.publish) to get server-side PubAck.
    """
    row = _make_row()
    pool, conn = _make_db_pool(rows=[row])

    mock_js = AsyncMock()
    mock_js.publish = AsyncMock(return_value=MagicMock(stream="SAHOOL_INTELLIGENCE", seq=1))

    nats_client = AsyncMock()
    nats_client.jetstream = MagicMock(return_value=mock_js)
    nats_client.publish = AsyncMock()  # must NOT be called

    relay = OutboxRelay(worker_id="test-worker")
    published = await relay._drain_batch(pool, nats_client, batch_size=10)

    assert published == 1
    mock_js.publish.assert_awaited_once()
    nats_client.publish.assert_not_awaited()

    execute_calls = [c[0][0] for c in conn.execute.call_args_list]
    assert any(_MARK_SENT_SQL in sql for sql in execute_calls)


@pytest.mark.asyncio
async def test_fallback_to_nc_publish_when_no_jetstream():
    """
    When nats_client has no jetstream() method (AttributeError), the relay
    must fall back to nc.publish.
    """
    row = _make_row()
    pool, conn = _make_db_pool(rows=[row])

    nats_client = AsyncMock()
    nats_client.publish = AsyncMock(return_value=None)
    del nats_client.jetstream  # simulate client without JetStream support

    relay = OutboxRelay(worker_id="test-worker")
    published = await relay._drain_batch(pool, nats_client, batch_size=10)

    assert published == 1
    nats_client.publish.assert_awaited_once()

    execute_calls = [c[0][0] for c in conn.execute.call_args_list]
    assert any(_MARK_SENT_SQL in sql for sql in execute_calls)


@pytest.mark.asyncio
async def test_fallback_to_nc_publish_when_jetstream_publish_fails():
    """
    When js.publish raises (e.g. no matching stream for the subject), the
    relay falls back to nc.publish so the row is still published.
    """
    row = _make_row()
    pool, conn = _make_db_pool(rows=[row])

    mock_js = AsyncMock()
    mock_js.publish = AsyncMock(side_effect=Exception("no stream for subject"))

    nats_client = AsyncMock()
    nats_client.jetstream = MagicMock(return_value=mock_js)
    nats_client.publish = AsyncMock(return_value=None)

    relay = OutboxRelay(worker_id="test-worker")
    published = await relay._drain_batch(pool, nats_client, batch_size=10)

    # nc.publish fallback used, row marked sent
    assert published == 1
    nats_client.publish.assert_awaited_once()

    execute_calls = [c[0][0] for c in conn.execute.call_args_list]
    assert any(_MARK_SENT_SQL in sql for sql in execute_calls)


# ---------------------------------------------------------------------------
# 5. Empty batch returns 0
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_empty_batch_returns_zero():
    """When outbox is empty, _drain_batch must return 0 without touching NATS."""
    pool, conn = _make_db_pool(rows=[])

    nats_client = AsyncMock()
    nats_client.publish = AsyncMock()
    del nats_client.jetstream

    relay = OutboxRelay(worker_id="test-worker")
    published = await relay._drain_batch(pool, nats_client, batch_size=10)

    assert published == 0
    nats_client.publish.assert_not_awaited()


# ---------------------------------------------------------------------------
# 6. Successful publish marks row sent
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_successful_publish_marks_row_sent():
    """Happy-path: publish succeeds → _MARK_SENT_SQL, NOT _MARK_FAILED_SQL."""
    row = _make_row()
    pool, conn = _make_db_pool(rows=[row])

    nats_client = AsyncMock()
    nats_client.publish = AsyncMock(return_value=None)
    del nats_client.jetstream

    relay = OutboxRelay(worker_id="test-worker")
    published = await relay._drain_batch(pool, nats_client, batch_size=10)

    assert published == 1
    execute_calls = [c[0][0] for c in conn.execute.call_args_list]
    assert any(_MARK_SENT_SQL in sql for sql in execute_calls)
    assert not any(_MARK_FAILED_SQL in sql for sql in execute_calls)
    assert not any(_MARK_DLQ_SQL in sql for sql in execute_calls)


# ---------------------------------------------------------------------------
# 7. MAX_RETRIES constant is defined and reasonable
# ---------------------------------------------------------------------------


def test_max_retries_is_positive_integer():
    assert isinstance(_MAX_RETRIES, int)
    assert _MAX_RETRIES > 0
