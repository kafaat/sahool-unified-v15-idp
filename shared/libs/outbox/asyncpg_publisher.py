"""
SAHOOL Outbox Publisher (asyncpg canonical API)
================================================
ناشر الصندوق الصادر — كتابة داخل المعاملة

Enqueues events into the ``outbox_messages`` table from within the caller's
open database transaction. The row commits atomically with the caller's
domain writes — if the transaction rolls back, the event is discarded, so
consumers never see an event for a state change that didn't persist.

A separate relay (:class:`shared.libs.outbox.relay.OutboxRelay`) reads
unpublished rows and pushes them to NATS.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

if TYPE_CHECKING:  # pragma: no cover
    import asyncpg

logger = logging.getLogger(__name__)


_INSERT_SQL = """
INSERT INTO outbox_messages (id, tenant_id, subject, payload, headers)
VALUES ($1, $2, $3, $4, $5::jsonb)
"""


class OutboxPublisher:
    """
    Writes outbox rows inside the caller's transaction.

    Usage — the caller MUST already be inside a transaction; the publisher
    does NOT open one of its own. This is what makes the pattern atomic:

        async with app.state.db_pool.acquire() as conn:
            async with conn.transaction():
                # ... domain writes (INSERT/UPDATE app tables) ...
                await outbox.enqueue(
                    conn,
                    subject="sahool.tenant.<tid>.field.created",
                    payload={"field_id": "f-123"},
                    tenant_id=tenant_id,
                )
                # both domain rows and outbox row commit together

    If you call ``enqueue`` without an open transaction, the outbox INSERT
    will still succeed, but you lose the atomicity guarantee — a crash
    between the domain write and the enqueue leaves the two tables in
    disagreement. Always wrap the pair in ``conn.transaction()``.
    """

    async def enqueue(
        self,
        conn: asyncpg.Connection,
        subject: str,
        payload: dict,
        tenant_id: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> UUID:
        """
        Insert a single outbox row.

        Args:
            conn: Open asyncpg connection, already inside a transaction
                  (``async with conn.transaction():``).
            subject: Full NATS subject (e.g. ``sahool.field.created``).
            payload: Event body; serialised with ``json.dumps`` to bytes.
            tenant_id: Tenant UUID string, or ``None`` for platform events.
            headers: Optional NATS headers; stored as JSONB.

        Returns:
            The UUID assigned to the new outbox row.
        """
        row_id = uuid4()
        payload_bytes = json.dumps(payload, separators=(",", ":"), default=str).encode("utf-8")
        headers_json = json.dumps(headers or {}, separators=(",", ":"))
        await conn.execute(
            _INSERT_SQL,
            row_id,
            tenant_id,
            subject,
            payload_bytes,
            headers_json,
        )
        logger.debug(
            "outbox_enqueued",
            extra={
                "outbox_id": str(row_id),
                "subject": subject,
                "tenant_id": tenant_id,
            },
        )
        return row_id
