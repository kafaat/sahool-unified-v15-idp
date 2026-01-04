"""
SAHOOL Spatial ORM Models
SQLAlchemy models with PostGIS geometry support

Hierarchy: Farm → Field → Zone → SubZone
Each level has both WKT (for compatibility) and native PostGIS geometry columns.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()


class FarmORM(Base):
    """
    Farm ORM model with location data.

    Farms are the top-level container for fields.
    """

    __tablename__ = "farms"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Unique farm identifier",
    )
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Tenant that owns this farm",
    )
    name: Mapped[str] = mapped_column(
        String(140),
        nullable=False,
        comment="Farm name",
    )
    name_ar: Mapped[str | None] = mapped_column(
        String(140),
        nullable=True,
        comment="Farm name in Arabic",
    )
    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Farm center latitude",
    )
    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Farm center longitude",
    )
    total_area_hectares: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Total farm area in hectares",
    )
    owner_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        comment="User ID of farm owner",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        comment="Farm status: active, inactive, pending",
    )
    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Additional farm metadata",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    fields: Mapped[list[FieldORM]] = relationship(
        "FieldORM",
        back_populates="farm",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_farms_tenant", "tenant_id"),
        Index("ix_farms_owner", "owner_id"),
    )

    def __repr__(self) -> str:
        return f"<Farm(id={self.id}, name={self.name})>"


class FieldORM(Base):
    """
    Field ORM model with PostGIS geometry.

    Fields are subdivisions of farms and contain zones.
    The geometry is stored in both WKT (for compatibility) and
    native PostGIS format (for spatial queries).
    """

    __tablename__ = "fields"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Unique field identifier",
    )
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Tenant that owns this field",
    )
    farm_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False,
        comment="Parent farm ID",
    )
    name: Mapped[str] = mapped_column(
        String(140),
        nullable=False,
        comment="Field name",
    )
    name_ar: Mapped[str | None] = mapped_column(
        String(140),
        nullable=True,
        comment="Field name in Arabic",
    )
    # WKT for compatibility with non-PostGIS systems
    geometry_wkt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Field boundary as WKT POLYGON",
    )
    # Native PostGIS geometry column added via migration
    # geom: geometry(Polygon, 4326) - created via Alembic

    center_latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Field center latitude",
    )
    center_longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Field center longitude",
    )
    area_hectares: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Field area in hectares",
    )
    soil_type: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
        comment="Soil type: clay, sandy, loamy, etc.",
    )
    irrigation_type: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
        comment="Irrigation method: drip, sprinkler, etc.",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        comment="Field status: active, fallow, preparation, harvesting",
    )
    current_crop_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        comment="Current crop planted in this field",
    )
    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Additional field metadata",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    farm: Mapped[FarmORM] = relationship("FarmORM", back_populates="fields")
    zones: Mapped[list[ZoneORM]] = relationship(
        "ZoneORM",
        back_populates="field",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_fields_tenant", "tenant_id"),
        Index("ix_fields_farm", "farm_id"),
        # GIST index on geom column is created via migration
    )

    def __repr__(self) -> str:
        return f"<Field(id={self.id}, name={self.name}, farm_id={self.farm_id})>"


class ZoneORM(Base):
    """
    Zone ORM model with PostGIS geometry.

    Zones are subdivisions of fields for precision agriculture.
    """

    __tablename__ = "zones"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Unique zone identifier",
    )
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Tenant that owns this zone",
    )
    field_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("fields.id", ondelete="CASCADE"),
        nullable=False,
        comment="Parent field ID",
    )
    name: Mapped[str] = mapped_column(
        String(140),
        nullable=False,
        comment="Zone name",
    )
    name_ar: Mapped[str | None] = mapped_column(
        String(140),
        nullable=True,
        comment="Zone name in Arabic",
    )
    zone_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="management",
        comment="Zone type: irrigation, soil_type, ndvi_cluster, yield_zone, management, custom",
    )
    geometry_wkt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Zone boundary as WKT POLYGON",
    )
    center_latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Zone center latitude",
    )
    center_longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Zone center longitude",
    )
    area_hectares: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Zone area in hectares",
    )
    properties: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Zone properties: soil_ph, ndvi_avg, etc.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    field: Mapped[FieldORM] = relationship("FieldORM", back_populates="zones")
    sub_zones: Mapped[list[SubZoneORM]] = relationship(
        "SubZoneORM",
        back_populates="zone",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_zones_tenant", "tenant_id"),
        Index("ix_zones_field", "field_id"),
        Index("ix_zones_type", "zone_type"),
    )

    def __repr__(self) -> str:
        return f"<Zone(id={self.id}, name={self.name}, field_id={self.field_id})>"


class SubZoneORM(Base):
    """
    SubZone ORM model with PostGIS geometry.

    SubZones are the finest granularity for variable rate application.
    """

    __tablename__ = "sub_zones"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Unique sub-zone identifier",
    )
    tenant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Tenant that owns this sub-zone",
    )
    zone_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("zones.id", ondelete="CASCADE"),
        nullable=False,
        comment="Parent zone ID",
    )
    name: Mapped[str] = mapped_column(
        String(140),
        nullable=False,
        comment="Sub-zone name",
    )
    name_ar: Mapped[str | None] = mapped_column(
        String(140),
        nullable=True,
        comment="Sub-zone name in Arabic",
    )
    geometry_wkt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Sub-zone boundary as WKT POLYGON",
    )
    center_latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Sub-zone center latitude",
    )
    center_longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Sub-zone center longitude",
    )
    area_hectares: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Sub-zone area in hectares",
    )
    properties: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Sub-zone properties: sensor_ids, vra_settings, etc.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    zone: Mapped[ZoneORM] = relationship("ZoneORM", back_populates="sub_zones")

    __table_args__ = (
        Index("ix_subzones_tenant", "tenant_id"),
        Index("ix_subzones_zone", "zone_id"),
    )

    def __repr__(self) -> str:
        return f"<SubZone(id={self.id}, name={self.name}, zone_id={self.zone_id})>"
