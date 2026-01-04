"""
SAHOOL Crop Service
Business logic for crop management
"""

from __future__ import annotations

from datetime import UTC, date, datetime

from .models import Crop, CropType, GrowthStage


class CropService:
    """Service for crop operations"""

    def __init__(self):
        # In-memory store (replace with repository)
        self._crops: dict[str, Crop] = {}

    def create_crop(
        self,
        tenant_id: str,
        field_id: str,
        crop_type: CropType,
        planting_date: date,
        variety: str | None = None,
        variety_ar: str | None = None,
        expected_harvest_date: date | None = None,
    ) -> Crop:
        """Create a new crop planting"""
        crop = Crop.create(
            tenant_id=tenant_id,
            field_id=field_id,
            crop_type=crop_type,
            planting_date=planting_date,
            variety=variety,
            variety_ar=variety_ar,
            expected_harvest_date=expected_harvest_date,
        )

        self._crops[crop.id] = crop
        return crop

    def get_crop(self, crop_id: str) -> Crop | None:
        """Get crop by ID"""
        return self._crops.get(crop_id)

    def update_growth_stage(
        self,
        crop_id: str,
        stage: GrowthStage,
    ) -> Crop | None:
        """Update crop growth stage"""
        crop = self._crops.get(crop_id)
        if crop:
            crop.growth_stage = stage
            crop.updated_at = datetime.now(UTC)
        return crop

    def update_yield_estimate(
        self,
        crop_id: str,
        yield_estimate_kg: float,
    ) -> Crop | None:
        """Update crop yield estimate"""
        crop = self._crops.get(crop_id)
        if crop:
            crop.yield_estimate_kg = yield_estimate_kg
            crop.updated_at = datetime.now(UTC)
        return crop

    def record_harvest(
        self,
        crop_id: str,
        actual_yield_kg: float,
        harvest_date: date | None = None,
    ) -> Crop | None:
        """Record crop harvest"""
        crop = self._crops.get(crop_id)
        if crop:
            crop.actual_harvest_date = harvest_date or date.today()
            crop.actual_yield_kg = actual_yield_kg
            crop.growth_stage = GrowthStage.POST_HARVEST
            crop.updated_at = datetime.now(UTC)
        return crop

    def list_field_crops(
        self,
        field_id: str,
        include_harvested: bool = False,
    ) -> list[Crop]:
        """List all crops for a field"""
        crops = [c for c in self._crops.values() if c.field_id == field_id]
        if not include_harvested:
            crops = [c for c in crops if c.growth_stage != GrowthStage.POST_HARVEST]
        return crops

    def list_tenant_crops(
        self,
        tenant_id: str,
        crop_type: CropType | None = None,
        stage: GrowthStage | None = None,
    ) -> list[Crop]:
        """List all crops for a tenant"""
        crops = [c for c in self._crops.values() if c.tenant_id == tenant_id]
        if crop_type:
            crops = [c for c in crops if c.crop_type == crop_type]
        if stage:
            crops = [c for c in crops if c.growth_stage == stage]
        return crops

    def get_active_crop_for_field(self, field_id: str) -> Crop | None:
        """Get the currently active crop for a field"""
        active_crops = [
            c
            for c in self._crops.values()
            if c.field_id == field_id and c.growth_stage != GrowthStage.POST_HARVEST
        ]
        # Return the most recently planted crop if multiple exist
        if active_crops:
            return max(active_crops, key=lambda c: c.planting_date)
        return None
