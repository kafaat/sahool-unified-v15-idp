"""
SAHOOL Equipment Service - Database Models
SQLAlchemy ORM models for equipment, maintenance, and alerts storage

نماذج قاعدة البيانات لخدمة إدارة المعدات
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()


class Equipment(Base):
    """
    Equipment storage model.

    Stores agricultural equipment and assets (tractors, pumps, drones, harvesters).
    Supports multi-tenancy, location tracking, and maintenance scheduling.
    """

    __tablename__ = "equipment"

    equipment_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        comment="Unique equipment identifier",
    )

    # Multi-tenancy
    tenant_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Tenant that owns this equipment",
    )

    # Basic information (bilingual)
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Equipment name",
    )
    name_ar: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Equipment name in Arabic",
    )

    # Equipment classification
    equipment_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Equipment type: tractor, pump, drone, harvester, sprayer, pivot, sensor, vehicle, other",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="operational",
        index=True,
        comment="Status: operational, maintenance, inactive, repair",
    )

    # Equipment details
    brand: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Equipment brand/manufacturer",
    )
    model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Equipment model",
    )
    serial_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        comment="Serial number (unique)",
    )
    year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Manufacturing year",
    )

    # Purchase information
    purchase_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Purchase date",
    )
    purchase_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Purchase price",
    )

    # Location information
    field_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Field ID where equipment is located",
    )
    location_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Location name (e.g., 'Northern Field - Sector C')",
    )

    # Specifications
    horsepower: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Engine horsepower",
    )
    fuel_capacity_liters: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 2),
        nullable=True,
        comment="Fuel tank capacity in liters",
    )

    # Telemetry data
    current_fuel_percent: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Current fuel level percentage",
    )
    current_hours: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Current operating hours",
    )
    current_lat: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
        comment="Current latitude",
    )
    current_lon: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
        comment="Current longitude",
    )

    # Maintenance scheduling
    last_maintenance_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last maintenance date",
    )
    next_maintenance_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Next scheduled maintenance date",
    )
    next_maintenance_hours: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Next maintenance at this hour reading",
    )

    # QR code for easy identification
    qr_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        comment="QR code for equipment registration",
    )

    # Additional metadata
    extra_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        name="metadata",  # Map to existing column name in database
        comment="Additional equipment metadata (JSON)",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        comment="When the equipment was registered",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        comment="When the equipment was last updated",
    )

    __table_args__ = (
        # Primary query pattern: tenant + status
        Index("ix_equipment_tenant_status", "tenant_id", "status"),
        # Equipment type queries
        Index("ix_equipment_type_status", "equipment_type", "status"),
        # Field-based queries
        Index("ix_equipment_field_status", "field_id", "status"),
        # Maintenance scheduling queries
        Index("ix_equipment_next_maintenance", "next_maintenance_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Equipment(equipment_id={self.equipment_id}, name={self.name}, "
            f"type={self.equipment_type}, status={self.status})>"
        )


class MaintenanceRecord(Base):
    """
    Maintenance record storage model.

    Tracks all maintenance activities performed on equipment.
    """

    __tablename__ = "equipment_maintenance"

    record_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        comment="Unique maintenance record identifier",
    )

    equipment_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Equipment ID this maintenance was performed on",
    )

    # Maintenance details
    maintenance_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type: oil_change, filter_change, tire_check, battery_check, calibration, general_service, repair, other",
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Maintenance description",
    )
    description_ar: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Maintenance description in Arabic",
    )

    # Who and when
    performed_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Person or company who performed the maintenance",
    )
    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="When the maintenance was performed",
    )

    # Cost tracking
    cost: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Maintenance cost",
    )

    # Additional details
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Additional notes",
    )
    parts_replaced: Mapped[list | None] = mapped_column(
        ARRAY(String),
        nullable=True,
        comment="List of parts replaced",
    )

    __table_args__ = (
        # Equipment maintenance history
        Index("ix_maintenance_equipment_date", "equipment_id", "performed_at"),
        # Maintenance type analysis
        Index("ix_maintenance_type", "maintenance_type", "performed_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<MaintenanceRecord(record_id={self.record_id}, equipment_id={self.equipment_id}, "
            f"type={self.maintenance_type})>"
        )


class MaintenanceAlert(Base):
    """
    Maintenance alert storage model.

    Stores alerts for upcoming or overdue equipment maintenance.
    """

    __tablename__ = "equipment_alerts"

    alert_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        comment="Unique alert identifier",
    )

    equipment_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Equipment ID this alert is for",
    )

    equipment_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Equipment name (denormalized for convenience)",
    )

    # Alert details
    maintenance_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of maintenance needed",
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Alert description",
    )
    description_ar: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Alert description in Arabic",
    )

    # Priority
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Priority: low, medium, high, critical",
    )

    # Due dates
    due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Due date (if time-based)",
    )
    due_hours: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Due at this hour reading (if hours-based)",
    )

    # Status
    is_overdue: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether the maintenance is overdue",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        comment="When the alert was created",
    )

    __table_args__ = (
        # Overdue alerts
        Index("ix_alerts_overdue", "is_overdue", "priority"),
        # Equipment alerts
        Index("ix_alerts_equipment_due", "equipment_id", "due_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<MaintenanceAlert(alert_id={self.alert_id}, equipment_id={self.equipment_id}, "
            f"priority={self.priority}, is_overdue={self.is_overdue})>"
        )
