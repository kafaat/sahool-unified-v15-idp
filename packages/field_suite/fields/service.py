"""
SAHOOL Field Service
Business logic for field management
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from .models import Field, FieldBoundary, FieldStatus, SoilType, IrrigationType


class FieldService:
    """Service for field operations"""

    def __init__(self):
        # In-memory store (replace with repository)
        self._fields: dict[str, Field] = {}

    def create_field(
        self,
        tenant_id: str,
        farm_id: str,
        name: str,
        coordinates: list[tuple[float, float]],
        area_hectares: float,
        soil_type: SoilType = SoilType.LOAMY,
        irrigation_type: IrrigationType = IrrigationType.DRIP,
        name_ar: Optional[str] = None,
    ) -> Field:
        """Create a new field"""
        boundary = FieldBoundary.from_coordinates(coordinates)

        field_obj = Field.create(
            tenant_id=tenant_id,
            farm_id=farm_id,
            name=name,
            name_ar=name_ar,
            boundary=boundary,
            area_hectares=area_hectares,
            soil_type=soil_type,
            irrigation_type=irrigation_type,
        )

        self._fields[field_obj.id] = field_obj
        return field_obj

    def get_field(self, field_id: str) -> Optional[Field]:
        """Get field by ID"""
        return self._fields.get(field_id)

    def update_field_status(
        self,
        field_id: str,
        status: FieldStatus,
    ) -> Optional[Field]:
        """Update field status"""
        field_obj = self._fields.get(field_id)
        if field_obj:
            field_obj.status = status
            field_obj.updated_at = datetime.now(timezone.utc)
        return field_obj

    def assign_crop(
        self,
        field_id: str,
        crop_id: str,
    ) -> Optional[Field]:
        """Assign a crop to the field"""
        field_obj = self._fields.get(field_id)
        if field_obj:
            field_obj.current_crop_id = crop_id
            field_obj.status = FieldStatus.ACTIVE
            field_obj.updated_at = datetime.now(timezone.utc)
        return field_obj

    def clear_crop(self, field_id: str) -> Optional[Field]:
        """Clear the current crop from field"""
        field_obj = self._fields.get(field_id)
        if field_obj:
            field_obj.current_crop_id = None
            field_obj.status = FieldStatus.FALLOW
            field_obj.updated_at = datetime.now(timezone.utc)
        return field_obj

    def list_farm_fields(
        self,
        farm_id: str,
        status: Optional[FieldStatus] = None,
    ) -> list[Field]:
        """List all fields for a farm"""
        fields = [f for f in self._fields.values() if f.farm_id == farm_id]
        if status:
            fields = [f for f in fields if f.status == status]
        return fields

    def list_tenant_fields(
        self,
        tenant_id: str,
        status: Optional[FieldStatus] = None,
    ) -> list[Field]:
        """List all fields for a tenant"""
        fields = [f for f in self._fields.values() if f.tenant_id == tenant_id]
        if status:
            fields = [f for f in fields if f.status == status]
        return fields

    def get_total_area(self, farm_id: str) -> float:
        """Get total field area for a farm"""
        return sum(
            f.area_hectares for f in self._fields.values() if f.farm_id == farm_id
        )
