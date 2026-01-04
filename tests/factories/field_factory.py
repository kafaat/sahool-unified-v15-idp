"""
SAHOOL Field Test Factory
Generates consistent test field data
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4


@dataclass
class TestField:
    """Test field data model"""

    id: str
    tenant_id: str
    name: str
    name_ar: str | None
    area_hectares: float
    crop_type: str | None
    geometry: dict | None
    metadata: dict
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "area_hectares": self.area_hectares,
            "crop_type": self.crop_type,
            "geometry": self.geometry,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def to_create_dict(self) -> dict:
        """Convert to creation payload (without id and timestamps)"""
        return {
            "tenant_id": self.tenant_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "area_hectares": self.area_hectares,
            "crop_type": self.crop_type,
            "geometry": self.geometry,
            "metadata": self.metadata,
        }


def make_field(**overrides) -> TestField:
    """
    Create a test field with default values.
    Override any field by passing keyword arguments.

    Example:
        field = make_field(name="Custom Field", area_hectares=100.0)
    """
    now = datetime.now(UTC)

    defaults = {
        "id": str(uuid4()),
        "tenant_id": "test-tenant-001",
        "name": "Test Field",
        "name_ar": "حقل اختبار",
        "area_hectares": 25.0,
        "crop_type": "wheat",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [[45.0, 15.0], [45.1, 15.0], [45.1, 15.1], [45.0, 15.1], [45.0, 15.0]]
            ],
        },
        "metadata": {},
        "created_at": now,
        "updated_at": now,
    }

    defaults.update(overrides)
    return TestField(**defaults)


def make_wheat_field(**overrides) -> TestField:
    """Create a wheat field"""
    defaults = {
        "name": "Wheat Field",
        "name_ar": "حقل القمح",
        "crop_type": "wheat",
        "area_hectares": 50.0,
    }
    defaults.update(overrides)
    return make_field(**defaults)


def make_coffee_field(**overrides) -> TestField:
    """Create a coffee field (typical for Yemen)"""
    defaults = {
        "name": "Coffee Terrace",
        "name_ar": "مدرج البن",
        "crop_type": "coffee",
        "area_hectares": 5.0,  # Typically smaller terraced fields
        "metadata": {"region": "Haraz", "altitude": 1800},
    }
    defaults.update(overrides)
    return make_field(**defaults)


def make_qat_field(**overrides) -> TestField:
    """Create a qat field"""
    defaults = {
        "name": "Qat Field",
        "name_ar": "حقل القات",
        "crop_type": "qat",
        "area_hectares": 3.0,
    }
    defaults.update(overrides)
    return make_field(**defaults)


def make_large_farm(**overrides) -> TestField:
    """Create a large commercial farm"""
    defaults = {
        "name": "Commercial Farm",
        "name_ar": "مزرعة تجارية",
        "area_hectares": 500.0,
        "crop_type": "mixed",
        "metadata": {"irrigation": "drip", "mechanized": True},
    }
    defaults.update(overrides)
    return make_field(**defaults)
