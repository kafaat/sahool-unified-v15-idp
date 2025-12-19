"""
SAHOOL NDVI Models
SQLAlchemy ORM models for NDVI time-series storage

Sprint 8: Time-series storage with temporal indexing
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, Float, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, declarative_base, mapped_column


Base = declarative_base()


class NdviObservation(Base):
    """
    NDVI time-series observation.

    Stores individual NDVI readings per field per date.
    Supports:
    - Mean, P10, P90 percentiles
    - Cloud coverage percentage
    - Confidence score
    - Source tracking (sentinel2, gee, copernicus, etc.)
    """

    __tablename__ = "ndvi_observations"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Unique observation identifier",
    )

    # Multi-tenancy
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        comment="Tenant that owns this observation",
    )

    # Field reference
    field_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        comment="Field this observation belongs to",
    )

    # Observation date (not timestamp - one per day)
    obs_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Date of observation (YYYY-MM-DD)",
    )

    # NDVI values
    ndvi_mean: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Mean NDVI value for the field (-1 to 1)",
    )
    ndvi_min: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Minimum NDVI value in the field",
    )
    ndvi_max: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Maximum NDVI value in the field",
    )
    ndvi_std: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Standard deviation of NDVI values",
    )
    ndvi_p10: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="10th percentile NDVI",
    )
    ndvi_p90: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="90th percentile NDVI",
    )

    # Quality metrics
    cloud_coverage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Cloud coverage fraction (0.0 to 1.0)",
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Confidence score (0.0 to 1.0)",
    )
    pixel_count: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="Number of valid pixels used",
    )

    # Source tracking
    source: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        default="sentinel2",
        comment="Data source: sentinel2, gee, copernicus, mock",
    )
    scene_id: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Original scene/product identifier",
    )

    # Additional metadata
    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Additional observation metadata",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="When this record was created",
    )

    __table_args__ = (
        # Primary query pattern: field + date range
        Index("ix_ndvi_field_date", "field_id", "obs_date"),
        # Tenant-wide queries
        Index("ix_ndvi_tenant_date", "tenant_id", "obs_date"),
        # Source filtering
        Index("ix_ndvi_source", "source"),
        # Unique constraint: one observation per field per date per source
        Index(
            "uq_ndvi_field_date_source",
            "field_id",
            "obs_date",
            "source",
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<NdviObservation(field_id={self.field_id}, "
            f"date={self.obs_date}, ndvi={self.ndvi_mean:.3f})>"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "field_id": str(self.field_id),
            "obs_date": self.obs_date.isoformat(),
            "ndvi_mean": round(self.ndvi_mean, 4),
            "ndvi_min": round(self.ndvi_min, 4) if self.ndvi_min else None,
            "ndvi_max": round(self.ndvi_max, 4) if self.ndvi_max else None,
            "ndvi_std": round(self.ndvi_std, 4) if self.ndvi_std else None,
            "ndvi_p10": round(self.ndvi_p10, 4) if self.ndvi_p10 else None,
            "ndvi_p90": round(self.ndvi_p90, 4) if self.ndvi_p90 else None,
            "cloud_coverage": round(self.cloud_coverage, 4),
            "confidence": round(self.confidence, 4),
            "source": self.source,
            "created_at": self.created_at.isoformat(),
        }


class NdviAlert(Base):
    """
    NDVI alert/anomaly record.

    Stores detected anomalies and alerts for tracking and notification.
    """

    __tablename__ = "ndvi_alerts"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
    )
    field_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
    )
    observation_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        comment="Reference to triggering observation",
    )

    alert_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        comment="Type: anomaly_positive, anomaly_negative, threshold_breach, trend_alert",
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
        comment="Severity: low, medium, high, critical",
    )

    # Alert details
    current_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="NDVI value that triggered the alert",
    )
    threshold_value: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Threshold that was breached (if applicable)",
    )
    deviation_pct: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Percentage deviation from expected",
    )
    z_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Z-score for anomaly detection",
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Alert message",
    )
    message_ar: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Alert message in Arabic",
    )

    # Status tracking
    acknowledged: Mapped[bool] = mapped_column(
        default=False,
        comment="Whether alert has been acknowledged",
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    acknowledged_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("ix_ndvi_alerts_field", "field_id", "created_at"),
        Index("ix_ndvi_alerts_tenant", "tenant_id", "created_at"),
        Index("ix_ndvi_alerts_unacked", "tenant_id", "acknowledged"),
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "field_id": str(self.field_id),
            "alert_type": self.alert_type,
            "severity": self.severity,
            "current_value": self.current_value,
            "deviation_pct": self.deviation_pct,
            "message": self.message,
            "message_ar": self.message_ar,
            "acknowledged": self.acknowledged,
            "created_at": self.created_at.isoformat(),
        }
