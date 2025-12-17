"""
SAHOOL Field Models
Data models for field management
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4


class FieldStatus(str, Enum):
    """Field operational status"""

    ACTIVE = "active"
    FALLOW = "fallow"
    PREPARATION = "preparation"
    HARVESTING = "harvesting"


class SoilType(str, Enum):
    """Soil classification"""

    CLAY = "clay"
    SANDY = "sandy"
    LOAMY = "loamy"
    SILTY = "silty"
    PEATY = "peaty"
    CHALKY = "chalky"


class IrrigationType(str, Enum):
    """Irrigation method"""

    DRIP = "drip"
    SPRINKLER = "sprinkler"
    FLOOD = "flood"
    FURROW = "furrow"
    RAINFED = "rainfed"


@dataclass
class FieldBoundary:
    """Field geographic boundary (polygon)"""

    coordinates: list[tuple[float, float]]  # List of (lat, lon) pairs
    center_latitude: float
    center_longitude: float

    def to_dict(self) -> dict:
        return {
            "coordinates": self.coordinates,
            "center_latitude": self.center_latitude,
            "center_longitude": self.center_longitude,
        }

    @classmethod
    def from_coordinates(cls, coordinates: list[tuple[float, float]]) -> FieldBoundary:
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


@dataclass
class Field:
    """Field entity"""

    id: str
    tenant_id: str
    farm_id: str
    name: str
    name_ar: Optional[str]
    boundary: FieldBoundary
    area_hectares: float
    soil_type: SoilType
    irrigation_type: IrrigationType
    status: FieldStatus
    current_crop_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        tenant_id: str,
        farm_id: str,
        name: str,
        boundary: FieldBoundary,
        area_hectares: float,
        soil_type: SoilType = SoilType.LOAMY,
        irrigation_type: IrrigationType = IrrigationType.DRIP,
        name_ar: Optional[str] = None,
    ) -> Field:
        """Factory method to create a new field"""
        now = datetime.now(timezone.utc)
        return cls(
            id=str(uuid4()),
            tenant_id=tenant_id,
            farm_id=farm_id,
            name=name,
            name_ar=name_ar,
            boundary=boundary,
            area_hectares=area_hectares,
            soil_type=soil_type,
            irrigation_type=irrigation_type,
            status=FieldStatus.PREPARATION,
            current_crop_id=None,
            created_at=now,
            updated_at=now,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "boundary": self.boundary.to_dict(),
            "area_hectares": self.area_hectares,
            "soil_type": self.soil_type.value,
            "irrigation_type": self.irrigation_type.value,
            "status": self.status.value,
            "current_crop_id": self.current_crop_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
