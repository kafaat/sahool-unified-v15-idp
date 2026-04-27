"""
SAHOOL Outbox Relay (asyncpg canonical API)
============================================
مُرحِّل الصندوق الصادر — ناشر الخلفية

Background task that polls ``outbox_messages`` for unpublished rows and
pushes them to NATS. Uses ``FOR UPDATE SKIP LOCKED`` so multiple replicas
can safely run the relay without double-publishing.

Designed to be started from a FastAPI lifespan context and stopped on
shutdown. Failures increment ``retry_count`` and are logged; the relay
never crashes the service.

Dead-letter:
  Rows that reach ``_MAX_RETRIES`` failures are stamped with
  ``dead_lettered_at`` and permanently excluded from the relay's fetch
  query so they do not spin forever.  An operator can replay or inspect
  them via a direct query:

      SELECT * FROM outbox_messages WHERE dead_lettered_at IS NOT NULL;

Publish semantics:
  The relay tries JetStream ``js.publish`` first (returns a server-side
  PubAck confirming the message is durably stored in the stream).  If the
  NATS client does not expose a ``jetstream()`` method, or JetStream is
  not configured for the subject, it falls back to core NATS
  ``nc.publish``.  Both paths raise on failure, keeping the retry
  guarantee intact.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time

from .metrics import OUTBOX_METRICS

logger = logging.getLogger(__name__)

# Maximum publish attempts before a row is dead-lettered.
_MAX_RETRIES = 10

# Two-step claim+publish protocol (see README):
#   Step 1  SELECT ... FOR UPDATE SKIP LOCKED; UPDATE claimed_at/claimed_by
#           INSIDE the fetch transaction. Commit releases the row lock but
#           leaves the claim columns set, so a second relay's SELECT (which
#           filters out claimed rows) will skip this batch until the claim
#           expires (on worker crash).
#   Step 2  Publish each row to NATS WITHOUT holding any DB lock/connection.
#   Step 3  Per row, in its own short txn, mark sent or clear the claim so
#           it can be retried by any worker on the next tick.
#
# Claim TTL (_CLAIM_STALE_SECONDS) means a crashed worker's rows become
# eligible again automatically; no janitor needed.
_CLAIM_STALE_SECONDS = 120

_FETCH_SQL = """
WITH claimable AS (
    SELECT id
    FROM outbox_messages
    WHERE published_at IS NULL
      AND dead_lettered_at IS NULL
      AND (claimed_at IS NULL OR claimed_at < NOW() - ($2 || ' seconds')::INTERVAL)
    ORDER BY created_at
    LIMIT $1
    FOR UPDATE SKIP LOCKED
)
UPDATE outbox_messages AS o
SET claimed_at = NOW(), claimed_by = $3
FROM claimable
WHERE o.id = claimable.id
RETURNING o.id, o.tenant_id, o.subject, o.payload, o.headers, o.retry_count, o.replay_state
"""

_MARK_SENT_SQL = "UPDATE outbox_messages SET published_at = NOW(), claimed_at = NULL, claimed_by = NULL WHERE id = $1"

# Used when the relay successfully publishes a row that was under a replay
# attempt (replay_state = 'REPLAYING'): transition → 'RECOVERED'.
_MARK_SENT_RECOVERED_SQL = (
    "UPDATE outbox_messages"
    " SET published_at = NOW(), claimed_at = NULL, claimed_by = NULL,"
    "     replay_state = 'RECOVERED'"
    " WHERE id = $1"
)

# On transient failure: bump retry_count AND release the claim so another
# worker (or the same one on the next tick) can retry.
_MARK_FAILED_SQL = (
    "UPDATE outbox_messages SET retry_count = retry_count + 1, claimed_at = NULL, claimed_by = NULL WHERE id = $1"
)

# Poison-message dead-letter: stamp dead_lettered_at and release the claim.
# The row is excluded from all future relay fetches (see _FETCH_SQL filter).
_MARK_DLQ_SQL = (
    "UPDATE outbox_messages"
    " SET dead_lettered_at = NOW(), retry_count = retry_count + 1,"
    "     claimed_at = NULL, claimed_by = NULL"
    " WHERE id = $1"
)

# Used when a REPLAYING row exhausts retries a second time: transition →
# 'FAILED_FINAL'.  This signals a persistent delivery failure that replay
# cannot recover — operators must investigate the root cause.
_MARK_DLQ_FAILED_FINAL_SQL = (
    "UPDATE outbox_messages"
    " SET dead_lettered_at = NOW(), retry_count = retry_count + 1,"
    "     claimed_at = NULL, claimed_by = NULL, replay_state = 'FAILED_FINAL'"
    " WHERE id = $1"
)


class OutboxRelay:
    """
    Background publisher that drains ``outbox_messages`` into NATS.

    Args (passed to :meth:`start`):
        db_pool: asyncpg connection pool.
        nats_client: Connected NATS client exposing ``publish(subject, payload, headers=...)``.
            If the client also exposes ``jetstream()`` the relay will use
            ``js.publish`` for server-side PubAck confirmation.
        poll_interval_seconds: Base polling interval when there are no rows.
        batch_size: Max rows fetched per tick.
        worker_id: Identifier stored in ``claimed_by`` so a multi-replica
            deployment can attribute claims. Defaults to hostname+pid.

    The relay uses exponential backoff on empty batches (doubling up to 30s)
    so it doesn't hammer the database when the outbox is quiet.

    Multi-replica safety: claims are persisted atomically with the SELECT
    (see ``_FETCH_SQL``). A claim older than ``_CLAIM_STALE_SECONDS`` is
    treated as expired — so a crashed worker's rows become eligible again.

    Poison-message protection: after ``_MAX_RETRIES`` consecutive publish
    failures a row is dead-lettered and excluded from the relay permanently.
    """

    def __init__(self, worker_id: str | None = None) -> None:
        self._task: asyncio.Task | None = None
        self._running = False
        self._stop_event: asyncio.Event | None = None
        # Default worker_id is host:pid so logs can attribute the claim.
        if worker_id is None:
            import os as _os
            import socket as _socket

            worker_id = f"{_socket.gethostname()}:{_os.getpid()}"
        self._worker_id = worker_id

    async def start(
        self,
        db_pool,
        nats_client,
        poll_interval_seconds: float = 1.0,
        batch_size: int = 100,
    ) -> asyncio.Task:
        """Start the background relay loop. Idempotent."""
        if self._running and self._task and not self._task.done():
            return self._task

        self._running = True
        self._stop_event = asyncio.Event()
        self._task = asyncio.create_task(
            self._loop(db_pool, nats_client, poll_interval_seconds, batch_size),
            name="outbox-relay",
        )
        logger.info(
            "outbox_relay_started",
            extra={
                "poll_interval": poll_interval_seconds,
                "batch_size": batch_size,
            },
        )
        return self._task

    async def stop(self) -> None:
        """Signal the loop to exit and await its completion."""
        self._running = False
        if self._stop_event is not None:
            self._stop_event.set()
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                # Expected — .cancel() above just propagated; the awaited
                # task re-raises CancelledError to signal clean teardown.
                pass
        logger.info("outbox_relay_stopped")

    async def _loop(
        self,
        db_pool,
        nats_client,
        poll_interval: float,
        batch_size: int,
    ) -> None:
        """Main polling loop. Exponential backoff on empty batches."""
        backoff = poll_interval
        max_backoff = max(poll_interval, 30.0)
        while self._running:
            try:
                published = await self._drain_batch(db_pool, nats_client, batch_size)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                # Never crash — log and keep going
                logger.error(
                    "outbox_relay_error",
                    extra={"error": str(exc), "error_type": type(exc).__name__},
                    exc_info=True,
                )
                published = 0

            if published > 0:
                # Work found — reset backoff and poll again quickly
                backoff = poll_interval
            else:
                # Quiet — back off up to max
                backoff = min(backoff * 2, max_backoff)

            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=backoff)
                # stop() was called
                break
            except TimeoutError:
                continue

    @staticmethod
    async def _nats_publish(nats_client, subject: str, payload: bytes, headers: dict) -> str:
        """
        Publish to NATS, preferring JetStream ``js.publish`` (server-side PubAck)
        and falling back to core NATS ``nc.publish`` when JetStream is not
        available on the given client.

        Using ``js.publish`` means the server confirms the message is durably
        stored in the matching stream before we mark the outbox row as sent.
        Using ``nc.publish`` is fire-and-forget at the server level but still
        raises on connection failure — keeping the retry guarantee intact.

        Returns:
            ``"jetstream"`` when a server-side PubAck was received — the
            latency metric for this row measures full durable-delivery time.
            ``"core_nats"`` when falling back to core publish — the latency
            metric measures socket-write time only (fire-and-forget at broker
            level, not a delivery guarantee).
        """
        js = None
        try:
            js = nats_client.jetstream()
        except AttributeError:
            pass  # nats_client has no jetstream() method — fall through
        except Exception:
            pass  # JetStream context not available — fall through

        if js is not None:
            try:
                await js.publish(subject, payload, headers=headers if headers else None)
                return "jetstream"
            except Exception:
                # JetStream publish failed (e.g. no matching stream for subject).
                # Fall back to core NATS so the row is retried rather than lost.
                pass

        await nats_client.publish(
            subject,
            payload,
            headers=headers if headers else None,
        )
        return "core_nats"

    async def _drain_batch(self, db_pool, nats_client, batch_size: int) -> int:
        """Fetch a claim batch in a short transaction, then publish outside.

        Keeping NATS publishes inside the SELECT-FOR-UPDATE transaction would
        hold row locks — and one DB connection from the pool — for as long as
        NATS takes to ACK the publish. On a slow/unavailable NATS that blocks
        the whole relay loop and contends with other outbox writers.

        The split ensures the DB connection is released as soon as the claim
        is taken, publishes happen without any lock held, and each mark is
        applied in its own short UPDATE.

        Rows that exhaust ``_MAX_RETRIES`` attempts are dead-lettered so they
        do not spin in an infinite retry loop (poison-message protection).

        Prometheus counters (``outbox_messages_published_total``,
        ``outbox_publish_failures_total``, ``outbox_dead_lettered_total``)
        are updated on every drain tick.
        """
        # --- Step 1: claim batch atomically, release txn immediately ---
        # The SELECT ... FOR UPDATE SKIP LOCKED CTE + UPDATE writes
        # claimed_at/claimed_by so that after the transaction commits, a
        # second relay replica filtering `claimed_at IS NULL OR stale`
        # will skip these rows until the claim expires. This prevents
        # double-publish across replicas.
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                rows = await conn.fetch(_FETCH_SQL, batch_size, _CLAIM_STALE_SECONDS, self._worker_id)
                if not rows:
                    return 0
        # Lock released here; rows stay visibly "claimed" in the table.

        # --- Step 2: publish each row WITHOUT any DB lock held ---
        published_count = 0
        for row in rows:
            row_id = row["id"]
            subject = row["subject"]
            payload = row["payload"]
            headers = row["headers"] or {}
            if isinstance(headers, str):
                try:
                    headers = json.loads(headers)
                except (TypeError, ValueError):
                    headers = {}

            # Extract event_id from headers for structured logging.
            event_id = headers.get("X-Event-ID") or headers.get("event_id") or ""
            tenant_id = row.get("tenant_id") or ""

            # Replay lifecycle: rows reset by reset_dead_lettered() carry
            # replay_state = 'REPLAYING'.  On success they transition to
            # 'RECOVERED'; on final DLQ they transition to 'FAILED_FINAL'.
            row_replay_state = row.get("replay_state")

            try:
                t0 = time.monotonic()
                delivery_mode = await self._nats_publish(
                    nats_client,
                    subject,
                    payload if isinstance(payload, bytes) else bytes(payload),
                    headers,
                )
                publish_latency = time.monotonic() - t0
                # --- Step 3a: mark sent (short, separate txn) ---
                # When the row was under a replay attempt transition state →
                # RECOVERED so operators can track full lifecycle outcomes.
                mark_sent_sql = _MARK_SENT_RECOVERED_SQL if row_replay_state == "REPLAYING" else _MARK_SENT_SQL
                async with db_pool.acquire() as mark_conn:
                    await mark_conn.execute(mark_sent_sql, row_id)
                published_count += 1
                OUTBOX_METRICS.published(subject=subject)
                if row_replay_state == "REPLAYING":
                    OUTBOX_METRICS.replay_recovered(subject=subject)
                OUTBOX_METRICS.observe_publish_latency(subject=subject, duration_seconds=publish_latency)
                logger.debug(
                    "outbox_published",
                    extra={
                        "outbox_id": str(row_id),
                        "subject": subject,
                        "event_id": event_id,
                        "tenant_id": tenant_id,
                        "worker_id": self._worker_id,
                        "delivery_mode": delivery_mode,
                        "publish_latency_ms": round(publish_latency * 1000, 2),
                        "replay_state": row_replay_state,
                    },
                )
            except Exception as exc:
                current_retry = row["retry_count"] + 1
                reason = type(exc).__name__
                if current_retry >= _MAX_RETRIES:
                    # Poison message — dead-letter permanently.
                    # When the row was REPLAYING, mark it FAILED_FINAL so the
                    # persistent failure is visible in lifecycle metrics.
                    mark_dlq_sql = _MARK_DLQ_FAILED_FINAL_SQL if row_replay_state == "REPLAYING" else _MARK_DLQ_SQL
                    _dlq_marked = False
                    try:
                        async with db_pool.acquire() as mark_conn:
                            await mark_conn.execute(mark_dlq_sql, row_id)
                        _dlq_marked = True
                    except Exception as dlq_exc:
                        logger.error(
                            "outbox_dlq_mark_failed",
                            extra={
                                "outbox_id": str(row_id),
                                "event_id": event_id,
                                "subject": subject,
                                "tenant_id": tenant_id,
                                "worker_id": self._worker_id,
                                "error": str(dlq_exc),
                            },
                        )
                    # Emit metrics only after a successful DB update to avoid
                    # inflating DLQ counts when the row is still retryable.
                    if _dlq_marked:
                        OUTBOX_METRICS.dead_lettered(subject=subject)
                        if row_replay_state == "REPLAYING":
                            OUTBOX_METRICS.replay_failed_final(subject=subject)
                    logger.error(
                        "outbox_dead_lettered",
                        extra={
                            "outbox_id": str(row_id),
                            "subject": subject,
                            "event_id": event_id,
                            "tenant_id": tenant_id,
                            "retry_count": current_retry,
                            "worker_id": self._worker_id,
                            "error": str(exc),
                            "error_type": reason,
                            "replay_state": row_replay_state,
                        },
                    )
                else:
                    # --- Step 3b: transient failure — increment and release claim ---
                    _failed_marked = False
                    try:
                        async with db_pool.acquire() as mark_conn:
                            await mark_conn.execute(_MARK_FAILED_SQL, row_id)
                        _failed_marked = True
                    except Exception as mark_exc:
                        logger.error(
                            "outbox_mark_failed_error",
                            extra={
                                "outbox_id": str(row_id),
                                "event_id": event_id,
                                "subject": subject,
                                "tenant_id": tenant_id,
                                "worker_id": self._worker_id,
                                "error": str(mark_exc),
                            },
                        )
                    # Emit metric only after a successful DB update to avoid
                    # inflating failure rates when the row may still be claimed.
                    if _failed_marked:
                        OUTBOX_METRICS.failed(subject=subject, reason=reason)
                    logger.warning(
                        "outbox_publish_failed",
                        extra={
                            "outbox_id": str(row_id),
                            "subject": subject,
                            "event_id": event_id,
                            "tenant_id": tenant_id,
                            "retry_count": current_retry,
                            "worker_id": self._worker_id,
                            "error": str(exc),
                            "error_type": reason,
                        },
                    )

        return published_count
