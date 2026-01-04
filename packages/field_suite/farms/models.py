"""
SAHOOL Farm Models
Data models for farm management
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class FarmStatus(str, Enum):
    """Farm operational status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


@dataclass
class FarmLocation:
    """Farm geographic location"""

    latitude: float
    longitude: float
    address: str | None = None
    address_ar: str | None = None
    region: str | None = None
    governorate: str | None = None

    def to_dict(self) -> dict:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "address_ar": self.address_ar,
            "region": self.region,
            "governorate": self.governorate,
        }


@dataclass
class Farm:
    """Farm entity"""

    id: str
    tenant_id: str
    name: str
    name_ar: str | None
    location: FarmLocation
    total_area_hectares: float
    status: FarmStatus
    owner_id: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        location: FarmLocation,
        total_area_hectares: float,
        owner_id: str,
        name_ar: str | None = None,
    ) -> Farm:
        """Factory method to create a new farm"""
        now = datetime.now(UTC)
        return cls(
            id=str(uuid4()),
            tenant_id=tenant_id,
            name=name,
            name_ar=name_ar,
            location=location,
            total_area_hectares=total_area_hectares,
            status=FarmStatus.PENDING,
            owner_id=owner_id,
            created_at=now,
            updated_at=now,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "location": self.location.to_dict(),
            "total_area_hectares": self.total_area_hectares,
            "status": self.status.value,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
