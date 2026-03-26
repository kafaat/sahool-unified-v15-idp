"""
Crop Factory for Tests
======================
مصنع بيانات المحاصيل للاختبارات

Factory for generating test crop data with realistic values.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from typing import Any
from uuid import uuid4

# =============================================================================
# Crop Models
# =============================================================================


@dataclass
class CropData:
    """Crop data model for testing."""

    id: str = field(default_factory=lambda: f"crop-{uuid4().hex[:8]}")
    field_id: str = field(default_factory=lambda: f"field-{uuid4().hex[:8]}")
    crop_type: str = "wheat"
    crop_type_ar: str = "قمح"
    variety: str = "Sakha 95"
    variety_ar: str = "سخا 95"
    planting_date: date = field(default_factory=lambda: date.today())
    expected_harvest_date: date = field(default_factory=lambda: date.today() + timedelta(days=120))
    growth_stage: str = "vegetative"
    growth_stage_ar: str = "مرحلة النمو الخضري"
    area_hectares: float = 10.0
    expected_yield_tons: float = 5.0
    status: str = "active"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "field_id": self.field_id,
            "crop_type": self.crop_type,
            "crop_type_ar": self.crop_type_ar,
            "variety": self.variety,
            "variety_ar": self.variety_ar,
            "planting_date": self.planting_date.isoformat(),
            "expected_harvest_date": self.expected_harvest_date.isoformat(),
            "growth_stage": self.growth_stage,
            "growth_stage_ar": self.growth_stage_ar,
            "area_hectares": self.area_hectares,
            "expected_yield_tons": self.expected_yield_tons,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


# =============================================================================
# Crop Types Database
# =============================================================================


CROP_TYPES = {
    "wheat": {
        "name": "Wheat",
        "name_ar": "قمح",
        "varieties": [
            ("Sakha 95", "سخا 95"),
            ("Giza 171", "جيزة 171"),
            ("Sids 14", "سدس 14"),
        ],
        "growth_days": 120,
        "yield_per_hectare": (4.0, 7.0),
        "seasons": ["winter"],
    },
    "barley": {
        "name": "Barley",
        "name_ar": "شعير",
        "varieties": [
            ("Giza 123", "جيزة 123"),
            ("Giza 2000", "جيزة 2000"),
        ],
        "growth_days": 100,
        "yield_per_hectare": (3.0, 5.0),
        "seasons": ["winter"],
    },
    "date_palm": {
        "name": "Date Palm",
        "name_ar": "نخيل",
        "varieties": [
            ("Khalas", "خلاص"),
            ("Sukkari", "سكري"),
            ("Ajwa", "عجوة"),
            ("Medjool", "مجدول"),
        ],
        "growth_days": 180,
        "yield_per_hectare": (8.0, 15.0),
        "seasons": ["summer"],
    },
    "tomato": {
        "name": "Tomato",
        "name_ar": "طماطم",
        "varieties": [
            ("Strain B", "سلالة ب"),
            ("Super Marmande", "سوبر مارماند"),
            ("Castle Rock", "كاسل روك"),
        ],
        "growth_days": 90,
        "yield_per_hectare": (30.0, 60.0),
        "seasons": ["spring", "fall"],
    },
    "cucumber": {
        "name": "Cucumber",
        "name_ar": "خيار",
        "varieties": [
            ("Beit Alpha", "بيت ألفا"),
            ("Marketmore", "ماركتمور"),
        ],
        "growth_days": 60,
        "yield_per_hectare": (25.0, 40.0),
        "seasons": ["spring", "summer"],
    },
    "alfalfa": {
        "name": "Alfalfa",
        "name_ar": "برسيم حجازي",
        "varieties": [
            ("Siriver", "سيريفر"),
            ("Local", "محلي"),
        ],
        "growth_days": 365,  # Perennial
        "yield_per_hectare": (15.0, 25.0),
        "seasons": ["year_round"],
    },
}

GROWTH_STAGES = [
    ("germination", "مرحلة الإنبات"),
    ("seedling", "مرحلة البادرة"),
    ("vegetative", "مرحلة النمو الخضري"),
    ("flowering", "مرحلة الإزهار"),
    ("fruiting", "مرحلة الإثمار"),
    ("ripening", "مرحلة النضج"),
    ("harvest", "مرحلة الحصاد"),
]


# =============================================================================
# Crop Factory
# =============================================================================


class CropFactory:
    """
    Factory for creating test crop instances.
    مصنع لإنشاء محاصيل للاختبار
    """

    _counter = 0

    @classmethod
    def create(
        cls,
        id: str | None = None,
        field_id: str | None = None,
        crop_type: str | None = None,
        variety: str | None = None,
        planting_date: date | None = None,
        growth_stage: str | None = None,
        area_hectares: float | None = None,
        **kwargs,
    ) -> CropData:
        """
        Create a single crop instance.

        Args:
            id: Crop ID (auto-generated if not provided)
            field_id: Field ID
            crop_type: Type of crop (wheat, barley, etc.)
            variety: Crop variety
            planting_date: Planting date
            growth_stage: Current growth stage
            area_hectares: Planted area
            **kwargs: Additional metadata

        Returns:
            CropData instance
        """
        cls._counter += 1

        # Select random crop type if not provided
        if crop_type is None:
            crop_type = random.choice(list(CROP_TYPES.keys()))

        crop_info = CROP_TYPES[crop_type]

        # Select variety
        if variety is None:
            variety_data = random.choice(crop_info["varieties"])
            variety = variety_data[0]
            variety_ar = variety_data[1]
        else:
            # Find Arabic name for provided variety
            variety_ar = variety
            for v in crop_info["varieties"]:
                if v[0] == variety:
                    variety_ar = v[1]
                    break

        # Set planting date
        if planting_date is None:
            planting_date = date.today() - timedelta(days=random.randint(0, 60))

        # Calculate expected harvest date
        expected_harvest_date = planting_date + timedelta(days=crop_info["growth_days"])

        # Select growth stage
        if growth_stage is None:
            stage_data = random.choice(GROWTH_STAGES)
            growth_stage = stage_data[0]
            growth_stage_ar = stage_data[1]
        else:
            growth_stage_ar = growth_stage
            for s in GROWTH_STAGES:
                if s[0] == growth_stage:
                    growth_stage_ar = s[1]
                    break

        # Calculate area
        if area_hectares is None:
            area_hectares = round(random.uniform(1, 50), 2)

        # Calculate expected yield
        yield_range = crop_info["yield_per_hectare"]
        expected_yield_tons = round(area_hectares * random.uniform(yield_range[0], yield_range[1]), 2)

        return CropData(
            id=id or f"crop-{uuid4().hex[:8]}",
            field_id=field_id or f"field-{uuid4().hex[:8]}",
            crop_type=crop_type,
            crop_type_ar=crop_info["name_ar"],
            variety=variety,
            variety_ar=variety_ar,
            planting_date=planting_date,
            expected_harvest_date=expected_harvest_date,
            growth_stage=growth_stage,
            growth_stage_ar=growth_stage_ar,
            area_hectares=area_hectares,
            expected_yield_tons=expected_yield_tons,
            metadata=kwargs,
        )

    @classmethod
    def create_batch(cls, count: int, **kwargs) -> list[CropData]:
        """Create multiple crop instances."""
        return [cls.create(**kwargs) for _ in range(count)]

    @classmethod
    def create_wheat(cls, **kwargs) -> CropData:
        """Create wheat crop."""
        return cls.create(crop_type="wheat", **kwargs)

    @classmethod
    def create_barley(cls, **kwargs) -> CropData:
        """Create barley crop."""
        return cls.create(crop_type="barley", **kwargs)

    @classmethod
    def create_date_palm(cls, **kwargs) -> CropData:
        """Create date palm crop."""
        return cls.create(crop_type="date_palm", **kwargs)

    @classmethod
    def create_tomato(cls, **kwargs) -> CropData:
        """Create tomato crop."""
        return cls.create(crop_type="tomato", **kwargs)

    @classmethod
    def create_for_field(cls, field_id: str, count: int = 1) -> list[CropData]:
        """Create crops for a specific field."""
        return [cls.create(field_id=field_id) for _ in range(count)]

    @classmethod
    def get_available_crop_types(cls) -> list[str]:
        """Get list of available crop types."""
        return list(CROP_TYPES.keys())

    @classmethod
    def get_crop_info(cls, crop_type: str) -> dict | None:
        """Get information about a crop type."""
        return CROP_TYPES.get(crop_type)

    @classmethod
    def reset_counter(cls):
        """Reset the factory counter."""
        cls._counter = 0


# =============================================================================
# Convenience Functions
# =============================================================================


def create_crop(**kwargs) -> CropData:
    """Convenience function to create a single crop."""
    return CropFactory.create(**kwargs)


def create_crops(count: int, **kwargs) -> list[CropData]:
    """Convenience function to create multiple crops."""
    return CropFactory.create_batch(count, **kwargs)


def create_crop_dict(**kwargs) -> dict[str, Any]:
    """Create a crop and return as dictionary."""
    return CropFactory.create(**kwargs).to_dict()
