"""
Variable Rate Application (VRA) Maps Module | وحدة خرائط التطبيق المتغير المعدل

Generates precision agriculture maps that divide fields into management zones
based on NDVI, soil data, and terrain analysis.

Competitive reference: Trimble, OneSoil, Climate FieldView
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class ZoneType(StrEnum):
    """Management zone classification | تصنيف مناطق الإدارة"""

    HIGH_PRODUCTIVITY = "high_productivity"  # إنتاجية عالية
    MEDIUM_PRODUCTIVITY = "medium_productivity"  # إنتاجية متوسطة
    LOW_PRODUCTIVITY = "low_productivity"  # إنتاجية منخفضة
    STRESSED = "stressed"  # مجهدة
    WATER_LOGGED = "water_logged"  # مشبعة بالماء
    SALINE = "saline"  # ملحية


class ApplicationType(StrEnum):
    """VRA application types | أنواع التطبيق المتغير"""

    FERTILIZER = "fertilizer"  # سماد
    SEED = "seed"  # بذور
    PESTICIDE = "pesticide"  # مبيد
    IRRIGATION = "irrigation"  # ري
    LIME = "lime"  # جير


class ExportFormat(StrEnum):
    """VRA map export formats | صيغ تصدير خرائط VRA"""

    GEOJSON = "geojson"
    SHAPEFILE = "shapefile"
    CSV = "csv"
    ISOXML = "isoxml"  # ISO 11783 for equipment
    PRESCRIPTION = "prescription"  # Generic prescription map


# Equipment compatibility
EQUIPMENT_FORMATS = {
    "john_deere": ExportFormat.SHAPEFILE,
    "agco": ExportFormat.ISOXML,
    "cnh": ExportFormat.SHAPEFILE,
    "trimble": ExportFormat.SHAPEFILE,
    "topcon": ExportFormat.SHAPEFILE,
    "raven": ExportFormat.SHAPEFILE,
    "generic": ExportFormat.GEOJSON,
}


# Default fertilizer rates by zone (kg/ha)
DEFAULT_FERTILIZER_RATES = {
    ZoneType.HIGH_PRODUCTIVITY: {
        "nitrogen": 180,
        "phosphorus": 60,
        "potassium": 80,
    },
    ZoneType.MEDIUM_PRODUCTIVITY: {
        "nitrogen": 140,
        "phosphorus": 45,
        "potassium": 60,
    },
    ZoneType.LOW_PRODUCTIVITY: {
        "nitrogen": 200,
        "phosphorus": 70,
        "potassium": 90,
    },
    ZoneType.STRESSED: {
        "nitrogen": 100,
        "phosphorus": 50,
        "potassium": 50,
    },
    ZoneType.WATER_LOGGED: {
        "nitrogen": 80,
        "phosphorus": 30,
        "potassium": 40,
    },
    ZoneType.SALINE: {
        "nitrogen": 120,
        "phosphorus": 40,
        "potassium": 100,
    },
}

# Zone labels in Arabic
ZONE_LABELS_AR = {
    ZoneType.HIGH_PRODUCTIVITY: "إنتاجية عالية",
    ZoneType.MEDIUM_PRODUCTIVITY: "إنتاجية متوسطة",
    ZoneType.LOW_PRODUCTIVITY: "إنتاجية منخفضة",
    ZoneType.STRESSED: "مجهدة",
    ZoneType.WATER_LOGGED: "مشبعة بالماء",
    ZoneType.SALINE: "ملحية",
}


@dataclass
class ManagementZone:
    """A management zone within a field | منطقة إدارية داخل الحقل"""

    zone_id: str = ""
    zone_type: ZoneType = ZoneType.MEDIUM_PRODUCTIVITY
    zone_label: str = ""
    zone_label_ar: str = ""
    area_hectares: float = 0.0
    area_percent: float = 0.0
    ndvi_mean: float = 0.0
    ndvi_std: float = 0.0
    soil_organic_matter: float = 0.0
    soil_ph: float = 7.0
    elevation_m: float = 0.0
    slope_percent: float = 0.0
    recommended_rates: dict[str, float] = field(default_factory=dict)
    geometry: dict | None = None  # GeoJSON geometry


@dataclass
class VRAPrescription:
    """VRA prescription for a field | وصفة VRA للحقل"""

    prescription_id: str = ""
    field_id: str = ""
    tenant_id: str = ""
    application_type: ApplicationType = ApplicationType.FERTILIZER
    crop_type: str = ""
    crop_type_ar: str = ""
    zones: list[ManagementZone] = field(default_factory=list)
    total_area_hectares: float = 0.0
    total_product_kg: float = 0.0
    cost_estimate_sar: float = 0.0
    savings_vs_uniform_percent: float = 0.0
    created_at: str = ""
    message: str = ""
    message_ar: str = ""


class VRAMapGenerator:
    """Generates Variable Rate Application maps from NDVI and soil data.

    يولّد خرائط التطبيق المتغير المعدل من بيانات NDVI والتربة.
    """

    # NDVI thresholds for zone classification
    NDVI_THRESHOLDS = {
        ZoneType.HIGH_PRODUCTIVITY: (0.65, 1.0),
        ZoneType.MEDIUM_PRODUCTIVITY: (0.45, 0.65),
        ZoneType.LOW_PRODUCTIVITY: (0.30, 0.45),
        ZoneType.STRESSED: (0.15, 0.30),
    }

    def __init__(self, num_zones: int = 5):
        """Initialize VRA generator.

        Args:
            num_zones: Number of management zones (3-7 recommended)
        """
        self.num_zones = max(3, min(7, num_zones))

    def classify_zone(self, ndvi: float, soil_ec: float = 0.0, waterlog_risk: float = 0.0) -> ZoneType:
        """Classify a pixel/area into a management zone.

        تصنيف نقطة/منطقة إلى منطقة إدارية.
        """
        if waterlog_risk > 0.7:
            return ZoneType.WATER_LOGGED
        if soil_ec > 4.0:  # dS/m threshold for salinity
            return ZoneType.SALINE

        for zone_type, (low, high) in self.NDVI_THRESHOLDS.items():
            if low <= ndvi < high:
                return zone_type

        if ndvi >= 0.65:
            return ZoneType.HIGH_PRODUCTIVITY
        return ZoneType.STRESSED

    def calculate_rates(
        self,
        zone_type: ZoneType,
        application_type: ApplicationType,
        soil_test: dict | None = None,
        target_yield: float = 0.0,
    ) -> dict[str, float]:
        """Calculate application rates for a zone.

        حساب معدلات التطبيق لمنطقة.
        """
        base_rates = DEFAULT_FERTILIZER_RATES.get(zone_type, {})

        if application_type == ApplicationType.SEED:
            # Seed rate adjustments (seeds/ha)
            seed_multipliers = {
                ZoneType.HIGH_PRODUCTIVITY: 1.1,
                ZoneType.MEDIUM_PRODUCTIVITY: 1.0,
                ZoneType.LOW_PRODUCTIVITY: 0.9,
                ZoneType.STRESSED: 0.8,
                ZoneType.WATER_LOGGED: 0.7,
                ZoneType.SALINE: 0.85,
            }
            base_seed_rate = 150  # kg/ha for wheat
            multiplier = seed_multipliers.get(zone_type, 1.0)
            return {"seed_rate_kg_ha": round(base_seed_rate * multiplier, 1)}

        if application_type == ApplicationType.IRRIGATION:
            # Irrigation rate adjustments (mm)
            irrigation_base = {
                ZoneType.HIGH_PRODUCTIVITY: 25,
                ZoneType.MEDIUM_PRODUCTIVITY: 30,
                ZoneType.LOW_PRODUCTIVITY: 35,
                ZoneType.STRESSED: 40,
                ZoneType.WATER_LOGGED: 10,
                ZoneType.SALINE: 45,  # Leaching requirement
            }
            return {"irrigation_mm": irrigation_base.get(zone_type, 30)}

        # Adjust fertilizer rates based on soil test
        adjusted = dict(base_rates)
        if soil_test:
            if soil_test.get("nitrogen_ppm", 0) > 30:
                adjusted["nitrogen"] = adjusted.get("nitrogen", 0) * 0.8
            if soil_test.get("phosphorus_ppm", 0) > 20:
                adjusted["phosphorus"] = adjusted.get("phosphorus", 0) * 0.7
            if soil_test.get("potassium_ppm", 0) > 200:
                adjusted["potassium"] = adjusted.get("potassium", 0) * 0.6

        return {k: round(v, 1) for k, v in adjusted.items()}

    def estimate_savings(self, zones: list[ManagementZone], uniform_rate: dict[str, float]) -> float:
        """Estimate savings of VRA vs uniform application.

        تقدير التوفير من VRA مقابل التطبيق الموحد.
        """
        total_area = sum(z.area_hectares for z in zones)
        if total_area <= 0:
            return 0.0

        uniform_total = sum(rate * total_area for rate in uniform_rate.values())
        vra_total = sum(sum(z.recommended_rates.values()) * z.area_hectares for z in zones)

        if uniform_total <= 0:
            return 0.0

        return round(((uniform_total - vra_total) / uniform_total) * 100, 1)

    def generate_prescription(
        self,
        field_id: str,
        tenant_id: str,
        ndvi_grid: list[dict],
        application_type: ApplicationType = ApplicationType.FERTILIZER,
        crop_type: str = "wheat",
        crop_type_ar: str = "قمح",
        soil_test: dict | None = None,
    ) -> VRAPrescription:
        """Generate a VRA prescription from NDVI data grid.

        توليد وصفة VRA من شبكة بيانات NDVI.

        Args:
            field_id: Field identifier
            tenant_id: Tenant identifier
            ndvi_grid: List of dicts with keys: ndvi, area_ha, soil_ec, waterlog_risk
            application_type: Type of application
            crop_type: Crop type (English)
            crop_type_ar: Crop type (Arabic)
            soil_test: Optional soil test results
        """
        # Classify zones
        zone_map: dict[ZoneType, list[dict]] = {}
        for pixel in ndvi_grid:
            zone_type = self.classify_zone(
                pixel.get("ndvi", 0.0),
                pixel.get("soil_ec", 0.0),
                pixel.get("waterlog_risk", 0.0),
            )
            zone_map.setdefault(zone_type, []).append(pixel)

        total_area = sum(p.get("area_ha", 0.0) for p in ndvi_grid)
        zones = []
        total_product = 0.0

        for i, (zone_type, pixels) in enumerate(zone_map.items()):
            zone_area = sum(p.get("area_ha", 0.0) for p in pixels)
            zone_ndvi_values = [p.get("ndvi", 0.0) for p in pixels]
            mean_ndvi = sum(zone_ndvi_values) / len(zone_ndvi_values) if zone_ndvi_values else 0.0

            rates = self.calculate_rates(zone_type, application_type, soil_test)
            zone_product = sum(rates.values()) * zone_area
            total_product += zone_product

            zones.append(
                ManagementZone(
                    zone_id=f"Z{i + 1:02d}",
                    zone_type=zone_type,
                    zone_label=zone_type.value.replace("_", " ").title(),
                    zone_label_ar=ZONE_LABELS_AR.get(zone_type, ""),
                    area_hectares=round(zone_area, 2),
                    area_percent=round((zone_area / total_area * 100) if total_area > 0 else 0, 1),
                    ndvi_mean=round(mean_ndvi, 3),
                    recommended_rates=rates,
                )
            )

        # Cost estimate (approximate: 2.5 SAR/kg for fertilizer)
        cost_per_kg = 2.5
        cost_estimate = total_product * cost_per_kg

        # Calculate savings vs uniform
        uniform_rate = DEFAULT_FERTILIZER_RATES.get(ZoneType.MEDIUM_PRODUCTIVITY, {})
        savings = self.estimate_savings(zones, uniform_rate)

        return VRAPrescription(
            prescription_id=f"VRA-{field_id}-{datetime.now().strftime('%Y%m%d')}",
            field_id=field_id,
            tenant_id=tenant_id,
            application_type=application_type,
            crop_type=crop_type,
            crop_type_ar=crop_type_ar,
            zones=zones,
            total_area_hectares=round(total_area, 2),
            total_product_kg=round(total_product, 1),
            cost_estimate_sar=round(cost_estimate, 2),
            savings_vs_uniform_percent=savings,
            created_at=datetime.now(UTC).isoformat(),
            message=f"VRA prescription generated with {len(zones)} zones, estimated {savings}% savings",
            message_ar=f"تم إنشاء وصفة VRA بـ {len(zones)} مناطق، توفير مقدر {savings}%",
        )

    def export_geojson(self, prescription: VRAPrescription) -> dict:
        """Export prescription as GeoJSON FeatureCollection.

        تصدير الوصفة كمجموعة ميزات GeoJSON.
        """
        features = []
        for zone in prescription.zones:
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "zone_id": zone.zone_id,
                        "zone_type": zone.zone_type.value,
                        "zone_label": zone.zone_label,
                        "zone_label_ar": zone.zone_label_ar,
                        "area_hectares": zone.area_hectares,
                        "ndvi_mean": zone.ndvi_mean,
                        **zone.recommended_rates,
                    },
                    "geometry": zone.geometry,
                }
            )

        return {
            "type": "FeatureCollection",
            "properties": {
                "prescription_id": prescription.prescription_id,
                "field_id": prescription.field_id,
                "application_type": prescription.application_type.value,
                "crop_type": prescription.crop_type,
                "total_area_hectares": prescription.total_area_hectares,
                "total_product_kg": prescription.total_product_kg,
                "savings_percent": prescription.savings_vs_uniform_percent,
            },
            "features": features,
        }
