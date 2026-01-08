"""
SAHOOL Alert Service - Database Models
SQLAlchemy ORM models for alerts storage

نماذج قاعدة البيانات لخدمة التنبيهات
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()


class Alert(Base):
    """
    Alert storage model.

    Stores agricultural alerts and warnings for fields.
    Supports multi-tenancy, multiple alert types, severities, and statuses.
    """

    __tablename__ = "alerts"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Unique alert identifier",
    )

    # Multi-tenancy
    tenant_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        comment="Tenant that owns this alert",
    )

    # Field reference
    field_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Field this alert belongs to",
    )

    # Alert classification
    type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        comment="Alert type: weather, pest, disease, irrigation, etc.",
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Severity: critical, high, medium, low, info",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        comment="Status: active, acknowledged, dismissed, resolved, expired",
    )

    # Alert content (bilingual)
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Alert title in Arabic",
    )
    title_en: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Alert title in English",
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Alert message in Arabic",
    )
    message_en: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Alert message in English",
    )

    # Recommendations (stored as JSON arrays)
    recommendations: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Recommendations in Arabic",
    )
    recommendations_en: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Recommendations in English",
    )

    # Metadata
    metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Additional alert metadata",
    )

    # Source tracking
    source_service: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
        comment="Source service that created this alert",
    )
    correlation_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Correlation ID for tracking across services",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        comment="When the alert was created",
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the alert expires",
    )

    # Acknowledgment tracking
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the alert was acknowledged",
    )
    acknowledged_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="User who acknowledged the alert",
    )

    # Dismissal tracking
    dismissed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the alert was dismissed",
    )
    dismissed_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="User who dismissed the alert",
    )

    # Resolution tracking
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the alert was resolved",
    )
    resolved_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="User who resolved the alert",
    )
    resolution_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Resolution notes",
    )

    __table_args__ = (
        # Primary query pattern: field + status + created_at
        Index("ix_alerts_field_status", "field_id", "status", "created_at"),
        # Tenant-wide queries
        Index("ix_alerts_tenant_created", "tenant_id", "created_at"),
        # Type and severity filtering
        Index("ix_alerts_type_severity", "type", "severity"),
        # Active alerts query
        Index("ix_alerts_active", "status", "expires_at"),
        # Source tracking
        Index("ix_alerts_source", "source_service"),
    )

    def __repr__(self) -> str:
        return (
            f"<Alert(id={self.id}, field_id={self.field_id}, "
            f"type={self.type}, severity={self.severity}, status={self.status})>"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "field_id": self.field_id,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "type": self.type,
            "severity": self.severity,
            "status": self.status,
            "title": self.title,
            "title_en": self.title_en,
            "message": self.message,
            "message_en": self.message_en,
            "recommendations": self.recommendations or [],
            "recommendations_en": self.recommendations_en or [],
            "metadata": self.metadata or {},
            "source_service": self.source_service,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "acknowledged_at": (self.acknowledged_at.isoformat() if self.acknowledged_at else None),
            "acknowledged_by": self.acknowledged_by,
            "dismissed_at": (self.dismissed_at.isoformat() if self.dismissed_at else None),
            "dismissed_by": self.dismissed_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "resolution_note": self.resolution_note,
        }


class AlertRule(Base):
    """
    Alert rule configuration model.

    Defines automated alert rules based on conditions and thresholds.
    Rules can be enabled/disabled and have cooldown periods.
    """

    __tablename__ = "alert_rules"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Unique rule identifier",
    )

    # Multi-tenancy
    tenant_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        comment="Tenant that owns this rule",
    )

    # Field reference
    field_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Field this rule applies to",
    )

    # Rule naming (bilingual)
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Rule name in Arabic",
    )
    name_en: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Rule name in English",
    )

    # Rule status
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether the rule is active",
    )

    # Rule condition (stored as JSON)
    # Structure: {metric: str, operator: str, value: float, duration_minutes: int}
    condition: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Rule condition configuration",
    )

    # Alert configuration (stored as JSON)
    # Structure: {type: str, severity: str, title: str, title_en: str, message_template: str}
    alert_config: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Alert configuration for when rule triggers",
    )

    # Cooldown period
    cooldown_hours: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=24,
        comment="Hours to wait before triggering again",
    )

    # Tracking
    last_triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last time this rule triggered an alert",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        comment="When the rule was created",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        comment="When the rule was last updated",
    )

    __table_args__ = (
        # Field rules query
        Index("ix_alert_rules_field", "field_id", "enabled"),
        # Tenant rules query
        Index("ix_alert_rules_tenant", "tenant_id", "enabled"),
        # Active rules query
        Index("ix_alert_rules_enabled", "enabled", "last_triggered_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<AlertRule(id={self.id}, field_id={self.field_id}, "
            f"name={self.name}, enabled={self.enabled})>"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "field_id": self.field_id,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "name": self.name,
            "name_en": self.name_en,
            "enabled": self.enabled,
            "condition": self.condition,
            "alert_config": self.alert_config,
            "cooldown_hours": self.cooldown_hours,
            "last_triggered_at": (
                self.last_triggered_at.isoformat() if self.last_triggered_at else None
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
