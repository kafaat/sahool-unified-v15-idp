"""
SAHOOL Outbox Models
SQLAlchemy models for the transactional outbox pattern
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()


class OutboxEvent(Base):
    """
    Outbox event table for reliable event publishing.

    Events are written to this table within the same transaction as
    business data changes, then asynchronously published to the message
    bus by a separate worker.

    This implements the transactional outbox pattern to ensure:
    - At-least-once delivery
    - Events are never lost if the message bus is unavailable
    - Consistency between database state and published events
    """

    __tablename__ = "outbox_events"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Event metadata
    event_type: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Event type (e.g., 'field.created')",
    )
    event_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Event schema version",
    )
    schema_ref: Mapped[str] = mapped_column(
        String(240),
        nullable=False,
        comment="Schema reference (e.g., 'events.field.created:v1')",
    )

    # Multi-tenancy and tracing
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        comment="Tenant that owns this event",
    )
    correlation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        comment="Correlation ID for request tracing",
    )

    # Payload (full envelope as JSON)
    payload_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Full event envelope as JSON",
    )

    # Publishing status
    published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the event has been published",
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the event was published",
    )

    # Retry tracking
    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of publish attempts",
    )
    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Last error message if publish failed",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        comment="When the event was created",
    )

    __table_args__ = (
        # Index for efficient polling of unpublished events
        Index(
            "ix_outbox_published_created",
            "published",
            "created_at",
        ),
        # Index for tenant-specific queries
        Index(
            "ix_outbox_tenant_created",
            "tenant_id",
            "created_at",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<OutboxEvent(id={self.id}, type={self.event_type}, "
            f"published={self.published})>"
        )
