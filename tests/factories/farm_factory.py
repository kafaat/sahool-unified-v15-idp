"""
Farm Factory for Tests
======================
مصنع بيانات المزارع للاختبارات

Factory for generating test farm data with realistic values.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

# =============================================================================
# Farm Models
# =============================================================================


@dataclass
class FarmData:
    """Farm data model for testing."""

    id: str = field(default_factory=lambda: f"farm-{uuid4().hex[:8]}")
    name: str = "Test Farm"
    name_ar: str = "مزرعة اختبار"
    owner_id: str = field(default_factory=lambda: f"user-{uuid4().hex[:8]}")
    tenant_id: str = field(default_factory=lambda: f"tenant-{uuid4().hex[:8]}")
    total_area_hectares: float = 100.0
    location: dict = field(default_factory=lambda: {"lat": 24.7136, "lng": 46.6753})
    region: str = "Riyadh"
    region_ar: str = "الرياض"
    status: str = "active"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "owner_id": self.owner_id,
            "tenant_id": self.tenant_id,
            "total_area_hectares": self.total_area_hectares,
            "location": self.location,
            "region": self.region,
            "region_ar": self.region_ar,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }


# =============================================================================
# Farm Factory
# =============================================================================


class FarmFactory:
    """
    Factory for creating test farm instances.
    مصنع لإنشاء مزارع للاختبار
    """

    # Saudi Arabian regions with Arabic names
    REGIONS = [
        ("Riyadh", "الرياض"),
        ("Makkah", "مكة المكرمة"),
        ("Madinah", "المدينة المنورة"),
        ("Eastern Province", "المنطقة الشرقية"),
        ("Asir", "عسير"),
        ("Qassim", "القصيم"),
        ("Tabuk", "تبوك"),
        ("Hail", "حائل"),
        ("Jazan", "جازان"),
        ("Najran", "نجران"),
    ]

    # Sample farm names in English and Arabic
    FARM_NAMES = [
        ("Al-Rashid Farm", "مزرعة الراشد"),
        ("Green Valley Farm", "مزرعة الوادي الأخضر"),
        ("Desert Oasis Farm", "مزرعة واحة الصحراء"),
        ("Palm Grove Farm", "مزرعة بستان النخيل"),
        ("Sunrise Farm", "مزرعة الشروق"),
        ("Al-Faisal Agricultural", "الفيصل الزراعية"),
        ("Future Farms", "مزارع المستقبل"),
        ("Al-Waha Farm", "مزرعة الواحة"),
    ]

    _counter = 0

    @classmethod
    def create(
        cls,
        id: str | None = None,
        name: str | None = None,
        name_ar: str | None = None,
        owner_id: str | None = None,
        tenant_id: str | None = None,
        total_area_hectares: float | None = None,
        location: dict | None = None,
        region: str | None = None,
        region_ar: str | None = None,
        status: str = "active",
        **kwargs,
    ) -> FarmData:
        """
        Create a single farm instance.

        Args:
            id: Farm ID (auto-generated if not provided)
            name: Farm name in English
            name_ar: Farm name in Arabic
            owner_id: Owner user ID
            tenant_id: Tenant ID
            total_area_hectares: Total farm area
            location: GPS coordinates
            region: Region name
            region_ar: Region name in Arabic
            status: Farm status (active, inactive, pending)
            **kwargs: Additional metadata

        Returns:
            FarmData instance
        """
        cls._counter += 1

        # Select random region if not provided
        if region is None or region_ar is None:
            region_data = random.choice(cls.REGIONS)
            region = region_data[0]
            region_ar = region_data[1]

        # Select random farm name if not provided
        if name is None or name_ar is None:
            name_data = random.choice(cls.FARM_NAMES)
            name = f"{name_data[0]} #{cls._counter}"
            name_ar = f"{name_data[1]} #{cls._counter}"

        # Generate random location in Saudi Arabia if not provided
        if location is None:
            location = cls._generate_saudi_location()

        # Generate random area if not provided
        if total_area_hectares is None:
            total_area_hectares = round(random.uniform(10, 500), 2)

        return FarmData(
            id=id or f"farm-{uuid4().hex[:8]}",
            name=name,
            name_ar=name_ar,
            owner_id=owner_id or f"user-{uuid4().hex[:8]}",
            tenant_id=tenant_id or f"tenant-{uuid4().hex[:8]}",
            total_area_hectares=total_area_hectares,
            location=location,
            region=region,
            region_ar=region_ar,
            status=status,
            metadata=kwargs,
        )

    @classmethod
    def create_batch(cls, count: int, **kwargs) -> list[FarmData]:
        """
        Create multiple farm instances.

        Args:
            count: Number of farms to create
            **kwargs: Shared attributes for all farms

        Returns:
            List of FarmData instances
        """
        return [cls.create(**kwargs) for _ in range(count)]

    @classmethod
    def create_for_tenant(cls, tenant_id: str, count: int = 1) -> list[FarmData]:
        """
        Create farms for a specific tenant.

        Args:
            tenant_id: Tenant ID
            count: Number of farms to create

        Returns:
            List of FarmData instances
        """
        return [cls.create(tenant_id=tenant_id) for _ in range(count)]

    @classmethod
    def create_small_farm(cls, **kwargs) -> FarmData:
        """Create a small farm (< 50 hectares)."""
        return cls.create(total_area_hectares=round(random.uniform(5, 50), 2), **kwargs)

    @classmethod
    def create_large_farm(cls, **kwargs) -> FarmData:
        """Create a large farm (> 200 hectares)."""
        return cls.create(total_area_hectares=round(random.uniform(200, 1000), 2), **kwargs)

    @classmethod
    def _generate_saudi_location(cls) -> dict:
        """Generate random GPS coordinates within Saudi Arabia."""
        # Saudi Arabia bounding box (approximate)
        lat = round(random.uniform(17.0, 32.0), 6)
        lng = round(random.uniform(34.0, 56.0), 6)
        return {"lat": lat, "lng": lng}

    @classmethod
    def reset_counter(cls):
        """Reset the factory counter."""
        cls._counter = 0


# =============================================================================
# Convenience Functions
# =============================================================================


def create_farm(**kwargs) -> FarmData:
    """Convenience function to create a single farm."""
    return FarmFactory.create(**kwargs)


def create_farms(count: int, **kwargs) -> list[FarmData]:
    """Convenience function to create multiple farms."""
    return FarmFactory.create_batch(count, **kwargs)


def create_farm_dict(**kwargs) -> dict[str, Any]:
    """Create a farm and return as dictionary."""
    return FarmFactory.create(**kwargs).to_dict()


# =============================================================================
# Pytest Fixtures
# =============================================================================


def farm_factory():
    """Pytest fixture factory for creating farms."""
    return FarmFactory


def sample_farm():
    """Pytest fixture for a single sample farm."""
    return FarmFactory.create()


def sample_farms():
    """Pytest fixture for multiple sample farms."""
    return FarmFactory.create_batch(5)
