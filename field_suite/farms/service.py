"""
SAHOOL Farm Service
Business logic for farm management
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from .models import Farm, FarmLocation, FarmStatus


class FarmService:
    """Service for farm operations"""

    def __init__(self):
        # In-memory store (replace with repository)
        self._farms: dict[str, Farm] = {}

    def create_farm(
        self,
        tenant_id: str,
        name: str,
        latitude: float,
        longitude: float,
        total_area_hectares: float,
        owner_id: str,
        name_ar: Optional[str] = None,
        address: Optional[str] = None,
        address_ar: Optional[str] = None,
        region: Optional[str] = None,
        governorate: Optional[str] = None,
    ) -> Farm:
        """Create a new farm"""
        location = FarmLocation(
            latitude=latitude,
            longitude=longitude,
            address=address,
            address_ar=address_ar,
            region=region,
            governorate=governorate,
        )

        farm = Farm.create(
            tenant_id=tenant_id,
            name=name,
            name_ar=name_ar,
            location=location,
            total_area_hectares=total_area_hectares,
            owner_id=owner_id,
        )

        self._farms[farm.id] = farm
        return farm

    def get_farm(self, farm_id: str) -> Optional[Farm]:
        """Get farm by ID"""
        return self._farms.get(farm_id)

    def update_farm_status(
        self,
        farm_id: str,
        status: FarmStatus,
    ) -> Optional[Farm]:
        """Update farm status"""
        farm = self._farms.get(farm_id)
        if farm:
            farm.status = status
            farm.updated_at = datetime.now(timezone.utc)
        return farm

    def activate_farm(self, farm_id: str) -> Optional[Farm]:
        """Activate a farm"""
        return self.update_farm_status(farm_id, FarmStatus.ACTIVE)

    def deactivate_farm(self, farm_id: str) -> Optional[Farm]:
        """Deactivate a farm"""
        return self.update_farm_status(farm_id, FarmStatus.INACTIVE)

    def list_tenant_farms(
        self,
        tenant_id: str,
        status: Optional[FarmStatus] = None,
    ) -> list[Farm]:
        """List all farms for a tenant"""
        farms = [f for f in self._farms.values() if f.tenant_id == tenant_id]
        if status:
            farms = [f for f in farms if f.status == status]
        return farms

    def list_owner_farms(
        self,
        owner_id: str,
        status: Optional[FarmStatus] = None,
    ) -> list[Farm]:
        """List all farms owned by a user"""
        farms = [f for f in self._farms.values() if f.owner_id == owner_id]
        if status:
            farms = [f for f in farms if f.status == status]
        return farms
