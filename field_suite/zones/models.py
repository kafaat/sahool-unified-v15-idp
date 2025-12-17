"""
SAHOOL Zone Models
Data models for zone and sub-zone management (precision agriculture)

Hierarchy: Farm → Field → Zone → SubZone
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4


class ZoneType(str, Enum):
    """Zone classification type"""

    IRRIGATION = "irrigation"
    SOIL_TYPE = "soil_type"
    NDVI_CLUSTER = "ndvi_cluster"
    YIELD_ZONE = "yield_zone"
    MANAGEMENT = "management"
    CUSTOM = "custom"


@dataclass
class ZoneBoundary:
    """Zone geographic boundary (polygon)"""

    coordinates: list[tuple[float, float]]  # List of (lat, lon) pairs
    center_latitude: float
    center_longitude: float

    def to_dict(self) -> dict:
        return {
            "coordinates": self.coordinates,
            "center_latitude": self.center_latitude,
            "center_longitude": self.center_longitude,
        }

    def to_wkt(self) -> str:
        """Convert to WKT POLYGON format"""
        if not self.coordinates:
            raise ValueError("Coordinates list cannot be empty")

        # Ensure polygon is closed (first point == last point)
        coords = list(self.coordinates)
        if coords[0] != coords[-1]:
            coords.append(coords[0])

        # WKT format: POLYGON((lon lat, lon lat, ...))
        coord_str = ", ".join(f"{lon} {lat}" for lat, lon in coords)
        return f"POLYGON(({coord_str}))"

    @classmethod
    def from_coordinates(cls, coordinates: list[tuple[float, float]]) -> ZoneBoundary:
        """Create boundary from coordinate list, calculating center"""
        if not coordinates:
            raise ValueError("Coordinates list cannot be empty")

        avg_lat = sum(c[0] for c in coordinates) / len(coordinates)
        avg_lon = sum(c[1] for c in coordinates) / len(coordinates)

        return cls(
            coordinates=coordinates,
            center_latitude=avg_lat,
            center_longitude=avg_lon,
        )

    @classmethod
    def from_wkt(cls, wkt: str) -> ZoneBoundary:
        """Parse WKT POLYGON to ZoneBoundary"""
        import re

        # Extract coordinates from POLYGON((lon lat, lon lat, ...))
        match = re.search(r"POLYGON\s*\(\((.*?)\)\)", wkt, re.IGNORECASE)
        if not match:
            raise ValueError(f"Invalid WKT polygon: {wkt}")

        coord_str = match.group(1)
        pairs = coord_str.split(",")

        coordinates = []
        for pair in pairs:
            parts = pair.strip().split()
            if len(parts) >= 2:
                lon, lat = float(parts[0]), float(parts[1])
                coordinates.append((lat, lon))

        return cls.from_coordinates(coordinates)


@dataclass
class Zone:
    """
    Zone entity - subdivision of a Field.

    Zones allow precision agriculture by dividing fields into
    management units based on soil type, irrigation, NDVI clustering, etc.
    """

    id: str
    tenant_id: str
    field_id: str
    name: str
    name_ar: Optional[str]
    zone_type: ZoneType
    boundary: ZoneBoundary
    area_hectares: float
    properties: dict  # Flexible metadata (soil_ph, ndvi_avg, etc.)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        tenant_id: str,
        field_id: str,
        name: str,
        zone_type: ZoneType,
        boundary: ZoneBoundary,
        area_hectares: float,
        name_ar: Optional[str] = None,
        properties: Optional[dict] = None,
    ) -> Zone:
        """Factory method to create a new zone"""
        now = datetime.now(timezone.utc)
        return cls(
            id=str(uuid4()),
            tenant_id=tenant_id,
            field_id=field_id,
            name=name,
            name_ar=name_ar,
            zone_type=zone_type,
            boundary=boundary,
            area_hectares=area_hectares,
            properties=properties or {},
            created_at=now,
            updated_at=now,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "zone_type": self.zone_type.value,
            "boundary": self.boundary.to_dict(),
            "area_hectares": self.area_hectares,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class SubZone:
    """
    SubZone entity - finest granularity subdivision.

    SubZones are used for:
    - Variable rate application (VRA)
    - Micro-irrigation control
    - Sensor placement areas
    - Targeted interventions
    """

    id: str
    tenant_id: str
    zone_id: str
    name: str
    name_ar: Optional[str]
    boundary: ZoneBoundary
    area_hectares: float
    properties: dict  # sensor_ids, vra_settings, etc.
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        tenant_id: str,
        zone_id: str,
        name: str,
        boundary: ZoneBoundary,
        area_hectares: float,
        name_ar: Optional[str] = None,
        properties: Optional[dict] = None,
    ) -> SubZone:
        """Factory method to create a new sub-zone"""
        now = datetime.now(timezone.utc)
        return cls(
            id=str(uuid4()),
            tenant_id=tenant_id,
            zone_id=zone_id,
            name=name,
            name_ar=name_ar,
            boundary=boundary,
            area_hectares=area_hectares,
            properties=properties or {},
            created_at=now,
            updated_at=now,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "zone_id": self.zone_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "boundary": self.boundary.to_dict(),
            "area_hectares": self.area_hectares,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
