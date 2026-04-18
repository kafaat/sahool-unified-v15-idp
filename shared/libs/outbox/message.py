"""
SAHOOL Outbox Message (asyncpg canonical API)
==============================================
نموذج رسالة الصندوق الصادر — واجهة أساسية

Canonical asyncpg-based outbox message model for the transactional outbox
pattern. Rows live in the ``outbox_messages`` table (see ``migration.sql``).

This is the recommended API for new services. The SQLAlchemy-based
:class:`shared.libs.outbox.models.OutboxEvent` / :class:`OutboxWorker` API
remains available for services already using SQLAlchemy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class OutboxMessage:
    """
    A pending or published outbox row.

    Fields match the ``outbox_messages`` table column-for-column so rows
    fetched by :class:`OutboxRelay` can be passed around without further
    translation.

    Attributes:
        id: Primary key (UUID).
        created_at: Insertion timestamp (UTC).
        tenant_id: Tenant UUID string for multi-tenant scoping (nullable
            for platform-level events).
        subject: Full NATS subject (e.g. ``sahool.tenant.<tid>.field.created``).
        payload: Raw JSON-encoded payload bytes ready for ``nc.publish``.
        headers: Optional NATS headers (dict[str, str]).
        published_at: Set when the relay successfully publishes the row.
        retry_count: Number of failed publish attempts.
    """

    id: UUID = field(default_factory=uuid4)
    created_at: datetime | None = None
    tenant_id: str | None = None
    subject: str = ""
    payload: bytes = b""
    headers: dict[str, str] = field(default_factory=dict)
    published_at: datetime | None = None
    retry_count: int = 0
