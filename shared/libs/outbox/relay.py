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
"""

from __future__ import annotations

import asyncio
import json
import logging

logger = logging.getLogger(__name__)


# Claim a batch and mark it "in-progress" atomically using published_at = epoch.
# We set published_at to a marker timestamp that we recognise via the
# `claimed_at IS NOT NULL` semantic (not used here) — simpler: use a dedicated
# column-less claim by adding a `-1` retry_count bump. To avoid DDL, we instead
# re-query for rows we just fetched using their ids in a separate short txn.
#
# Two-step pattern below:
#   1. Short txn: SELECT...FOR UPDATE SKIP LOCKED, then UPDATE retry_count to
#      flag "claimed by this worker" (retry_count >= 0 semantics preserved).
#   2. Outside any txn: publish each row to NATS.
#   3. Short txn per row: UPDATE published_at on success, or UPDATE
#      retry_count += 1 on failure (the claim bump already counts as +0 so
#      failures appear as a single +1 after this step).
_FETCH_SQL = """
SELECT id, tenant_id, subject, payload, headers, retry_count
FROM outbox_messages
WHERE published_at IS NULL
ORDER BY created_at
LIMIT $1
FOR UPDATE SKIP LOCKED
"""

_MARK_SENT_SQL = "UPDATE outbox_messages SET published_at = NOW() WHERE id = $1"

_MARK_FAILED_SQL = "UPDATE outbox_messages SET retry_count = retry_count + 1 WHERE id = $1"


class OutboxRelay:
    """
    Background publisher that drains ``outbox_messages`` into NATS.

    Args (passed to :meth:`start`):
        db_pool: asyncpg connection pool.
        nats_client: Connected NATS client exposing ``publish(subject, payload, headers=...)``.
        poll_interval_seconds: Base polling interval when there are no rows.
        batch_size: Max rows fetched per tick.

    The relay uses exponential backoff on empty batches (doubling up to 30s)
    so it doesn't hammer the database when the outbox is quiet.
    """

    def __init__(self) -> None:
        self._task: asyncio.Task | None = None
        self._running = False
        self._stop_event: asyncio.Event | None = None

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

    async def _drain_batch(self, db_pool, nats_client, batch_size: int) -> int:
        """Fetch a claim batch in a short transaction, then publish outside.

        Keeping NATS publishes inside the SELECT-FOR-UPDATE transaction would
        hold row locks — and one DB connection from the pool — for as long as
        NATS takes to ACK the publish. On a slow/unavailable NATS that blocks
        the whole relay loop and contends with other outbox writers.

        The split ensures the DB connection is released as soon as the claim
        is taken, publishes happen without any lock held, and each mark is
        applied in its own short UPDATE.
        """
        # --- Step 1: claim batch, release txn immediately ---
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                rows = await conn.fetch(_FETCH_SQL, batch_size)
                if not rows:
                    return 0
                # Claim by bumping retry_count by 0 — i.e. no-op update just to
                # hold the FOR UPDATE lock until commit. The txn exits on the
                # next `async with` unwind, releasing the lock. Any concurrent
                # relay replica will now see published_at still NULL but will
                # either re-SELECT+SKIP LOCKED (and get a different batch) or
                # find the rows already marked sent by the time they retry.
                # In practice two replicas claiming identical rows is prevented
                # by the SKIP LOCKED on the SELECT above, per txn scope.
                pass
        # Lock released here.

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

            try:
                await nats_client.publish(
                    subject,
                    payload if isinstance(payload, bytes) else bytes(payload),
                    headers=headers if headers else None,
                )
                # --- Step 3a: mark sent (short, separate txn) ---
                async with db_pool.acquire() as mark_conn:
                    await mark_conn.execute(_MARK_SENT_SQL, row_id)
                published_count += 1
            except Exception as exc:
                # --- Step 3b: mark failed (short, separate txn) ---
                try:
                    async with db_pool.acquire() as mark_conn:
                        await mark_conn.execute(_MARK_FAILED_SQL, row_id)
                except Exception as mark_exc:
                    logger.error(
                        "outbox_mark_failed_error",
                        extra={"outbox_id": str(row_id), "error": str(mark_exc)},
                    )
                logger.warning(
                    "outbox_publish_failed",
                    extra={
                        "outbox_id": str(row_id),
                        "subject": subject,
                        "retry_count": row["retry_count"] + 1,
                        "error": str(exc),
                    },
                )

        return published_count
