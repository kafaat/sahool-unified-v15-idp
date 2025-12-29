"""
SAHOOL Dead Letter Queue Database Models
SQLAlchemy models for storing and querying failed events

This provides persistent storage for DLQ events to enable:
- Historical analysis of failures
- Retry mechanisms
- Failure pattern detection
- Operational dashboards
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

try:
    from sqlalchemy import (
        Column,
        String,
        Integer,
        DateTime,
        Text,
        JSON,
        Index,
        Boolean,
    )
    from sqlalchemy.dialects.postgresql import UUID as PGUUID
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import Mapped, mapped_column
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False


if HAS_SQLALCHEMY:
    Base = declarative_base()

    class FailedEventModel(Base):
        """
        Database model for failed events in DLQ

        Table: failed_events

        Stores complete context about events that failed processing
        and were routed to the Dead Letter Queue.
        """

        __tablename__ = "failed_events"

        # Primary key
        id: Mapped[UUID] = mapped_column(
            PGUUID(as_uuid=True),
            primary_key=True,
            default=uuid4,
        )

        # Event identification
        event_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
        event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
        original_subject: Mapped[str] = mapped_column(String(255), nullable=False)

        # Source context
        source_service: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
        tenant_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
        field_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
        farmer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

        # Error context
        error_message: Mapped[str] = mapped_column(Text, nullable=False)
        error_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
        stack_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

        # Retry context
        retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
        max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
        first_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
        last_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

        # Original data (JSONB for PostgreSQL)
        original_data: Mapped[dict] = mapped_column(JSON, nullable=False)
        original_headers: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

        # DLQ metadata
        dlq_timestamp: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
            index=True,
        )
        dlq_reason: Mapped[str] = mapped_column(String(100), nullable=False, default="max_retries_exceeded")

        # Processing status
        status: Mapped[str] = mapped_column(
            String(50),
            nullable=False,
            default="pending",
            index=True,
        )  # pending, retried, resolved, discarded
        resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
        resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

        # Alerting
        alert_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
        alert_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

        # Audit timestamps
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
        )

        # Indexes for common queries
        __table_args__ = (
            Index("idx_failed_events_event_type_status", "event_type", "status"),
            Index("idx_failed_events_source_service_status", "source_service", "status"),
            Index("idx_failed_events_dlq_timestamp", "dlq_timestamp"),
            Index("idx_failed_events_tenant_status", "tenant_id", "status"),
            Index("idx_failed_events_error_type", "error_type"),
        )

        def __repr__(self) -> str:
            return (
                f"<FailedEvent("
                f"id={self.id}, "
                f"event_id={self.event_id}, "
                f"event_type={self.event_type}, "
                f"error_type={self.error_type}, "
                f"status={self.status}"
                f")>"
            )

        @classmethod
        def from_dlq_event(cls, event) -> FailedEventModel:
            """
            Create FailedEventModel from DLQEvent

            Args:
                event: DLQEvent instance from dlq_consumer

            Returns:
                FailedEventModel instance
            """
            return cls(
                event_id=event.event_id,
                event_type=event.event_type,
                original_subject=event.original_subject,
                source_service=event.source_service,
                tenant_id=event.tenant_id,
                field_id=event.field_id,
                farmer_id=event.farmer_id,
                error_message=event.error_message,
                error_type=event.error_type,
                stack_trace=event.stack_trace,
                retry_count=event.retry_count,
                max_retries=event.max_retries,
                first_attempt_at=event.first_attempt_at,
                last_attempt_at=event.last_attempt_at,
                original_data=event.original_data,
                original_headers=event.original_headers,
                dlq_timestamp=event.dlq_timestamp,
                dlq_reason=event.dlq_reason,
            )

        def to_dict(self) -> dict:
            """Convert to dictionary"""
            return {
                "id": str(self.id),
                "event_id": self.event_id,
                "event_type": self.event_type,
                "original_subject": self.original_subject,
                "source_service": self.source_service,
                "tenant_id": self.tenant_id,
                "field_id": self.field_id,
                "farmer_id": self.farmer_id,
                "error_message": self.error_message,
                "error_type": self.error_type,
                "stack_trace": self.stack_trace,
                "retry_count": self.retry_count,
                "max_retries": self.max_retries,
                "first_attempt_at": self.first_attempt_at.isoformat(),
                "last_attempt_at": self.last_attempt_at.isoformat(),
                "original_data": self.original_data,
                "original_headers": self.original_headers,
                "dlq_timestamp": self.dlq_timestamp.isoformat(),
                "dlq_reason": self.dlq_reason,
                "status": self.status,
                "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
                "resolution_notes": self.resolution_notes,
                "alert_sent": self.alert_sent,
                "alert_sent_at": self.alert_sent_at.isoformat() if self.alert_sent_at else None,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
            }


    # Migration script (for reference)
    CREATE_TABLE_SQL = """
    -- Dead Letter Queue failed events table
    CREATE TABLE IF NOT EXISTS failed_events (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

        -- Event identification
        event_id VARCHAR(255) NOT NULL,
        event_type VARCHAR(100) NOT NULL,
        original_subject VARCHAR(255) NOT NULL,

        -- Source context
        source_service VARCHAR(100) NOT NULL,
        tenant_id VARCHAR(255),
        field_id VARCHAR(255),
        farmer_id VARCHAR(255),

        -- Error context
        error_message TEXT NOT NULL,
        error_type VARCHAR(100) NOT NULL,
        stack_trace TEXT,

        -- Retry context
        retry_count INTEGER NOT NULL DEFAULT 0,
        max_retries INTEGER NOT NULL DEFAULT 3,
        first_attempt_at TIMESTAMPTZ NOT NULL,
        last_attempt_at TIMESTAMPTZ NOT NULL,

        -- Original data (JSONB for better querying)
        original_data JSONB NOT NULL,
        original_headers JSONB NOT NULL DEFAULT '{}'::jsonb,

        -- DLQ metadata
        dlq_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        dlq_reason VARCHAR(100) NOT NULL DEFAULT 'max_retries_exceeded',

        -- Processing status
        status VARCHAR(50) NOT NULL DEFAULT 'pending',
        resolved_at TIMESTAMPTZ,
        resolution_notes TEXT,

        -- Alerting
        alert_sent BOOLEAN NOT NULL DEFAULT FALSE,
        alert_sent_at TIMESTAMPTZ,

        -- Audit timestamps
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    -- Indexes
    CREATE INDEX idx_failed_events_event_id ON failed_events(event_id);
    CREATE INDEX idx_failed_events_event_type ON failed_events(event_type);
    CREATE INDEX idx_failed_events_source_service ON failed_events(source_service);
    CREATE INDEX idx_failed_events_tenant_id ON failed_events(tenant_id);
    CREATE INDEX idx_failed_events_field_id ON failed_events(field_id);
    CREATE INDEX idx_failed_events_farmer_id ON failed_events(farmer_id);
    CREATE INDEX idx_failed_events_error_type ON failed_events(error_type);
    CREATE INDEX idx_failed_events_status ON failed_events(status);
    CREATE INDEX idx_failed_events_dlq_timestamp ON failed_events(dlq_timestamp);
    CREATE INDEX idx_failed_events_event_type_status ON failed_events(event_type, status);
    CREATE INDEX idx_failed_events_source_service_status ON failed_events(source_service, status);
    CREATE INDEX idx_failed_events_tenant_status ON failed_events(tenant_id, status);

    -- Trigger to update updated_at timestamp
    CREATE OR REPLACE FUNCTION update_failed_events_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER trigger_failed_events_updated_at
        BEFORE UPDATE ON failed_events
        FOR EACH ROW
        EXECUTE FUNCTION update_failed_events_updated_at();

    -- Comments
    COMMENT ON TABLE failed_events IS 'Dead Letter Queue - stores failed events for analysis and retry';
    COMMENT ON COLUMN failed_events.status IS 'pending, retried, resolved, discarded';
    COMMENT ON COLUMN failed_events.dlq_reason IS 'Reason for DLQ routing: max_retries_exceeded, validation_error, etc.';
    """

else:
    # Placeholder if SQLAlchemy is not available
    FailedEventModel = None
    CREATE_TABLE_SQL = None
