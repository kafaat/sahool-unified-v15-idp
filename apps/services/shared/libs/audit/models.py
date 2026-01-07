"""
SAHOOL Audit Models
SQLAlchemy models for append-only audit logging with hash chain
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()


class AuditLog(Base):
    """
    Append-only audit log with hash chain for tamper evidence.

    RULES:
    - NEVER update existing rows
    - NEVER delete rows (soft-delete only via separate mechanism)
    - Always insert new entries
    - Hash chain provides tamper detection

    The hash chain works by including the previous entry's hash in the
    current entry's hash calculation, creating a linked chain that
    would be broken if any entry is modified.
    """

    __tablename__ = "audit_logs"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Unique audit entry identifier",
    )

    # Multi-tenancy
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Tenant that owns this audit entry",
    )

    # Actor information
    actor_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        comment="User or service that performed the action",
    )
    actor_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="user",
        comment="Type of actor: user, service, system",
    )

    # Action details
    action: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        comment="Action performed (e.g., 'field.create', 'user.login')",
    )
    resource_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        comment="Type of resource affected (e.g., 'field', 'user')",
    )
    resource_id: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        comment="ID of the affected resource",
    )

    # Request context
    correlation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        comment="Request correlation ID for tracing",
    )
    ip: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="Client IP address",
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
        comment="Client user agent (truncated)",
    )

    # Additional details (JSON)
    details_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="{}",
        comment="Additional details as JSON (PII redacted)",
    )

    # Hash chain for tamper evidence
    prev_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="Hash of previous entry (null for first entry)",
    )
    entry_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="SHA-256 hash of this entry's canonical form",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        comment="When the action occurred",
    )

    # Schema version for future migrations
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Audit log schema version",
    )

    __table_args__ = (
        # Index for querying by tenant and time
        Index("ix_audit_tenant_created", "tenant_id", "created_at"),
        # Index for querying by resource
        Index("ix_audit_resource", "resource_type", "resource_id"),
        # Index for querying by actor
        Index("ix_audit_actor", "actor_id", "created_at"),
        # Index for correlation tracing
        Index("ix_audit_correlation", "correlation_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, action={self.action}, "
            f"resource={self.resource_type}/{self.resource_id})>"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "actor_id": str(self.actor_id) if self.actor_id else None,
            "actor_type": self.actor_type,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "correlation_id": str(self.correlation_id),
            "ip": self.ip,
            "created_at": self.created_at.isoformat(),
        }
