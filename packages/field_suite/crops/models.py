"""
SAHOOL Crop Models
Data models for crop management
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from enum import Enum
from uuid import uuid4


class CropType(str, Enum):
    """Crop type classification"""

    WHEAT = "wheat"
    BARLEY = "barley"
    CORN = "corn"
    RICE = "rice"
    COTTON = "cotton"
    COFFEE = "coffee"
    QAAT = "qaat"
    MANGO = "mango"
    BANANA = "banana"
    DATE_PALM = "date_palm"
    GRAPE = "grape"
    TOMATO = "tomato"
    ONION = "onion"
    POTATO = "potato"
    OTHER = "other"


class GrowthStage(str, Enum):
    """Crop growth stage"""

    PLANTING = "planting"
    GERMINATION = "germination"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    RIPENING = "ripening"
    HARVEST = "harvest"
    POST_HARVEST = "post_harvest"


@dataclass
class Crop:
    """Crop entity"""

    id: str
    tenant_id: str
    field_id: str
    crop_type: CropType
    variety: str | None
    variety_ar: str | None
    planting_date: date
    expected_harvest_date: date | None
    actual_harvest_date: date | None
    growth_stage: GrowthStage
    yield_estimate_kg: float | None
    actual_yield_kg: float | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        tenant_id: str,
        field_id: str,
        crop_type: CropType,
        planting_date: date,
        variety: str | None = None,
        variety_ar: str | None = None,
        expected_harvest_date: date | None = None,
    ) -> Crop:
        """Factory method to create a new crop"""
        now = datetime.now(UTC)
        return cls(
            id=str(uuid4()),
            tenant_id=tenant_id,
            field_id=field_id,
            crop_type=crop_type,
            variety=variety,
            variety_ar=variety_ar,
            planting_date=planting_date,
            expected_harvest_date=expected_harvest_date,
            actual_harvest_date=None,
            growth_stage=GrowthStage.PLANTING,
            yield_estimate_kg=None,
            actual_yield_kg=None,
            created_at=now,
            updated_at=now,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "crop_type": self.crop_type.value,
            "variety": self.variety,
            "variety_ar": self.variety_ar,
            "planting_date": self.planting_date.isoformat(),
            "expected_harvest_date": (
                self.expected_harvest_date.isoformat()
                if self.expected_harvest_date
                else None
            ),
            "actual_harvest_date": (
                self.actual_harvest_date.isoformat()
                if self.actual_harvest_date
                else None
            ),
            "growth_stage": self.growth_stage.value,
            "yield_estimate_kg": self.yield_estimate_kg,
            "actual_yield_kg": self.actual_yield_kg,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
