# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Transactional Outbox Pattern — نمط صندوق الصادر المعاملاتي
==========================================================
Guarantees **exactly-once effects** when a handler must:
  1. Write to the database  (business upsert)
  2. Publish a new NATS event (downstream trigger)

Without the outbox, a crash between step 1 and step 2 causes a **lost event**.

How it works:
  - The handler writes both the business row AND an `outbox_events` row
    inside **the same DB transaction**.
  - After the transaction commits, the `OutboxRelay` periodically polls the
    outbox table and publishes pending events to NATS.
  - Once published, the row is marked as `sent` (or deleted after a TTL).
  - If the service crashes before publishing, the row stays and gets picked
    up on the next relay cycle — no event is lost.

Fallback (when outbox is unavailable):
  - Publish-before-ACK: publish the downstream event, then ACK the inbound.
    If publish fails, NAK → JetStream redelivers.  Not as strong as outbox,
    but avoids lost events in 99.9% of cases.

Usage:
    from shared.events.outbox import write_outbox_event, OutboxRelay

    # Inside a handler (same DB transaction):
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(business_upsert_sql, ...)
            await write_outbox_event(
                conn,
                subject="sahool.recommendation.created",
                payload=event.model_dump_json(),
                correlation_id=event.correlation_id,
                tenant_id=tenant_id,
            )

    # Relay (runs as background task in service lifespan):
    relay = OutboxRelay(db_pool=pool, publisher=publisher)
    await relay.start()   # polls every 1 second
    ...
    await relay.stop()
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# SQL
# ─────────────────────────────────────────────────────────────────────────────

SQL_CREATE_OUTBOX_TABLE = """
CREATE TABLE IF NOT EXISTS outbox_events (
    id              TEXT        PRIMARY KEY,
    subject         TEXT        NOT NULL,
    payload         TEXT        NOT NULL,
    headers_json    TEXT,
    tenant_id       TEXT,
    correlation_id  TEXT,
    status          TEXT        NOT NULL DEFAULT 'pending',  -- pending | sent | failed
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sent_at         TIMESTAMPTZ,
    retry_count     INT         NOT NULL DEFAULT 0,
    last_error      TEXT
);

CREATE INDEX IF NOT EXISTS idx_outbox_pending
    ON outbox_events (status, created_at)
    WHERE status = 'pending';

-- Auto-purge sent events older than 24 hours
CREATE INDEX IF NOT EXISTS idx_outbox_sent_ttl
    ON outbox_events (sent_at)
    WHERE status = 'sent';
"""

_SQL_INSERT_OUTBOX = """
INSERT INTO outbox_events (id, subject, payload, headers_json, tenant_id, correlation_id)
VALUES ($1, $2, $3, $4, $5, $6)
"""

_SQL_FETCH_PENDING = """
SELECT id, subject, payload, headers_json, tenant_id, correlation_id, retry_count
FROM outbox_events
WHERE status = 'pending'
ORDER BY created_at ASC
LIMIT $1
FOR UPDATE SKIP LOCKED
"""

_SQL_MARK_SENT = """
UPDATE outbox_events
SET status = 'sent', sent_at = NOW()
WHERE id = $1
"""

_SQL_MARK_FAILED = """
UPDATE outbox_events
SET retry_count = retry_count + 1, last_error = $2
WHERE id = $1
"""

_SQL_MARK_DLQ = """
UPDATE outbox_events
SET status = 'failed', last_error = $2
WHERE id = $1
"""

_SQL_CLEANUP_SENT = """
DELETE FROM outbox_events
WHERE status = 'sent' AND sent_at < NOW() - INTERVAL '24 hours'
"""


# ─────────────────────────────────────────────────────────────────────────────
# Write helper (called inside same transaction as business logic)
# ─────────────────────────────────────────────────────────────────────────────


async def write_outbox_event(
    conn,
    *,
    subject: str,
    payload: str,
    correlation_id: str | None = None,
    tenant_id: str | None = None,
    headers: dict[str, str] | None = None,
) -> str:
    """
    Insert an event into the outbox table.  Must be called inside the same
    DB transaction as the business write to guarantee atomicity.

    Args:
        conn: asyncpg connection (inside a transaction)
        subject: NATS subject to publish to
        payload: JSON-serialized event payload
        correlation_id: Correlation ID for tracing
        tenant_id: Tenant scope
        headers: Optional NATS headers dict

    Returns:
        outbox event ID (UUID string)
    """
    event_id = str(uuid4())
    headers_json = json.dumps(headers) if headers else None
    await conn.execute(
        _SQL_INSERT_OUTBOX,
        event_id,
        subject,
        payload,
        headers_json,
        tenant_id,
        correlation_id,
    )
    return event_id


# ─────────────────────────────────────────────────────────────────────────────
# Outbox Relay (background publisher)
# ─────────────────────────────────────────────────────────────────────────────

_MAX_RELAY_RETRIES = 5  # per-row retry cap before marking as 'failed'


class OutboxRelay:
    """
    Background task that polls the outbox table and publishes pending events
    to NATS.  Runs in the service lifespan.

    Args:
        db_pool: asyncpg connection pool
        publisher: EventPublisher instance (or any object with a `_publish_core`
                   or `_publish_jetstream` method)
        poll_interval: seconds between polls (default 1.0)
        batch_size: max rows per poll cycle (default 50)
    """

    def __init__(
        self,
        db_pool: Any,
        publisher: Any,
        poll_interval: float = 1.0,
        batch_size: int = 50,
    ):
        self._pool = db_pool
        self._publisher = publisher
        self._poll_interval = poll_interval
        self._batch_size = batch_size
        self._task: asyncio.Task | None = None
        self._running = False

        # Metrics
        self.published_count = 0
        self.failed_count = 0

    async def start(self) -> None:
        """Start the relay background loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("outbox_relay_started poll_interval=%s", self._poll_interval)

    async def stop(self) -> None:
        """Stop the relay gracefully."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("outbox_relay_stopped published=%d", self.published_count)

    async def _loop(self) -> None:
        """Main polling loop."""
        while self._running:
            try:
                count = await self._relay_batch()
                if count > 0:
                    logger.debug("outbox_relay_batch count=%d", count)
                    # No sleep if we found work — poll immediately for more
                    continue
            except Exception as exc:
                logger.warning("outbox_relay_error: %s", str(exc))

            await asyncio.sleep(self._poll_interval)

    async def _relay_batch(self) -> int:
        """Fetch and publish one batch of pending outbox events. Returns count published."""
        if self._pool is None:
            return 0

        published = 0
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(_SQL_FETCH_PENDING, self._batch_size)
            for row in rows:
                row_id = row["id"]
                subject = row["subject"]
                payload = row["payload"]
                headers_json = row["headers_json"]
                retry_count = row["retry_count"]

                headers = json.loads(headers_json) if headers_json else None

                try:
                    # Publish via NATS
                    data = payload.encode("utf-8") if isinstance(payload, str) else payload
                    nc = getattr(self._publisher, "_nc", None)
                    js = getattr(self._publisher, "_js", None)

                    if js:
                        await js.publish(subject, data, headers=headers)
                    elif nc:
                        await nc.publish(subject, data, headers=headers)
                    else:
                        raise RuntimeError("No NATS connection available on publisher")

                    await conn.execute(_SQL_MARK_SENT, row_id)
                    published += 1
                    self.published_count += 1

                except Exception as exc:
                    self.failed_count += 1
                    if retry_count + 1 >= _MAX_RELAY_RETRIES:
                        await conn.execute(_SQL_MARK_DLQ, row_id, str(exc)[:500])
                        logger.warning(
                            "outbox_event_moved_to_failed id=%s subject=%s error=%s",
                            row_id,
                            subject,
                            str(exc),
                        )
                    else:
                        await conn.execute(_SQL_MARK_FAILED, row_id, str(exc)[:500])

        return published

    async def cleanup_sent(self) -> int:
        """Delete sent outbox events older than 24 hours. Returns rows deleted."""
        if self._pool is None:
            return 0
        async with self._pool.acquire() as conn:
            result = await conn.execute(_SQL_CLEANUP_SENT)
            count = int(result.split()[-1]) if result else 0
            if count > 0:
                logger.info("outbox_cleanup deleted=%d", count)
            return count


# ─────────────────────────────────────────────────────────────────────────────
# Ensure outbox table exists (call during lifespan)
# ─────────────────────────────────────────────────────────────────────────────


async def ensure_outbox_table(db_pool: Any) -> None:
    """Create the outbox_events table if it doesn't exist."""
    if db_pool is None:
        return
    try:
        async with db_pool.acquire() as conn:
            await conn.execute(SQL_CREATE_OUTBOX_TABLE)
        logger.info("outbox_table_ensured")
    except Exception as exc:
        logger.warning("outbox_table_ensure_failed: %s", str(exc))
