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
        """Fetch one batch, publish each row, and mark sent/failed."""
        published_count = 0
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                rows = await conn.fetch(_FETCH_SQL, batch_size)
                if not rows:
                    return 0

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
                        # NATS python client: publish(subject, payload, headers=...)
                        await nats_client.publish(
                            subject,
                            payload if isinstance(payload, bytes) else bytes(payload),
                            headers=headers if headers else None,
                        )
                        await conn.execute(_MARK_SENT_SQL, row_id)
                        published_count += 1
                    except Exception as exc:
                        await conn.execute(_MARK_FAILED_SQL, row_id)
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
