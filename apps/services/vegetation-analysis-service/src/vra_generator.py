"""
SAHOOL Satellite Service - Variable Rate Application (VRA) Prescription Maps
خدمة خرائط التطبيق المتغير المعدل (VRA)

Generate prescription maps for variable-rate application of:
- Fertilizers (تسميد متغير المعدل)
- Seeds (بذار متغير المعدل)
- Lime (جير متغير المعدل)
- Pesticides (مبيدات متغيرة المعدل)
- Irrigation (ري متغير المعدل)

Based on NDVI zones, yield maps, soil analysis, or combined factors.
Similar to OneSoil VRA capabilities.
"""

import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================


class VRAType(Enum):
    """Types of variable rate application"""

    FERTILIZER = "fertilizer"  # تسميد
    SEED = "seed"  # بذار
    LIME = "lime"  # جير
    PESTICIDE = "pesticide"  # مبيدات
    IRRIGATION = "irrigation"  # ري


class ZoneMethod(Enum):
    """Methods for creating management zones"""

    NDVI_BASED = "ndvi"  # Zones from NDVI
    YIELD_BASED = "yield"  # Zones from yield map
    SOIL_BASED = "soil"  # Zones from soil analysis
    COMBINED = "combined"  # Multi-factor


class ZoneLevel(Enum):
    """Zone classification levels"""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class ManagementZone:
    """
    Management zone for variable rate application
    منطقة إدارة للتطبيق المتغير المعدل
    """

    zone_id: int
    zone_name: str  # "High", "Medium", "Low"
    zone_name_ar: str  # "عالي", "متوسط", "منخفض"
    zone_level: ZoneLevel

    # Zone characteristics
    ndvi_range: tuple[float, float]
    area_ha: float
    percentage: float  # % of total field area

    # Geometry
    centroid: tuple[float, float]  # (lon, lat)
    polygon: list[list[tuple[float, float]]]  # GeoJSON-style coordinates

    # Application rate
    recommended_rate: float
    unit: str  # kg/ha, seeds/ha, L/ha, mm/ha

    # Additional info
    total_product: float  # Total product needed for this zone
    color: str  # Hex color for visualization


@dataclass
class PrescriptionMap:
    """
    Complete prescription map for variable rate application
    خريطة وصفة التطبيق المتغير المعدل
    """

    id: str
    field_id: str
    vra_type: VRAType
    created_at: datetime

    # Input parameters
    target_rate: float  # Average target rate
    min_rate: float
    max_rate: float
    unit: str  # kg/ha, seeds/ha, L/ha

    # Zone configuration
    num_zones: int
    zone_method: ZoneMethod
    zones: list[ManagementZone]

    # Field statistics
    total_area_ha: float
    total_product_needed: float

    # Savings analysis
    flat_rate_product: float  # Product needed for flat rate
    savings_percent: float  # % savings vs. flat rate
    savings_amount: float  # Actual product saved
    cost_savings: float | None = None  # Cost savings if price provided

    # Export URLs
    shapefile_url: str | None = None
    geojson_url: str | None = None
    isoxml_url: str | None = None

    # Metadata
    notes: str | None = None
    notes_ar: str | None = None

    # Data-source transparency. When the NDVI zone layer was synthesised
    # (no real satellite data available), both fields flag the farmer and
    # downstream UI that this prescription must NOT be applied to the
    # field without acknowledgement. Climate FieldView / OneSoil refuse
    # to publish prescriptions lacking real imagery; we surface the
    # warning instead of silently fabricating one.
    is_synthetic: bool = False
    data_warning_en: str | None = None
    data_warning_ar: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["vra_type"] = self.vra_type.value
        data["zone_method"] = self.zone_method.value
        data["created_at"] = self.created_at.isoformat()
        for zone in data["zones"]:
            zone["zone_level"] = zone["zone_level"]
        return data


@dataclass
class ZoneStatistics:
    """Statistics for a zone classification"""

    num_zones: int
    zones: list[ManagementZone]
    total_area_ha: float
    ndvi_mean: float
    ndvi_std: float
    ndvi_min: float
    ndvi_max: float
    # True when the zones were fabricated by the fallback generator
    # (no real NDVI raster available). Surfaces to PrescriptionMap so the
    # API contract can warn downstream consumers.
    is_synthetic: bool = False


# =============================================================================
# VRA Generator
# =============================================================================


class VRAGenerator:
    """
    Generate Variable Rate Application prescription maps
    مولد خرائط التطبيق المتغير المعدل

    Features:
    - NDVI-based zone classification
    - 3-zone or 5-zone management
    - Multiple VRA types (fertilizer, seed, lime, pesticide, irrigation)
    - Savings calculation vs. flat rate
    - Export to GeoJSON, Shapefile, ISO-XML
    """

    # Zone classification thresholds (NDVI-based)
    # Thresholds divide NDVI range into equal or optimal percentiles
    ZONE_THRESHOLDS = {
        3: {"low": (0.0, 0.4), "medium": (0.4, 0.6), "high": (0.6, 1.0)},
        5: {
            "very_low": (0.0, 0.3),
            "low": (0.3, 0.45),
            "medium": (0.45, 0.55),
            "high": (0.55, 0.7),
            "very_high": (0.7, 1.0),
        },
    }

    # Rate adjustments by zone (multiplier of target rate)
    # Based on precision agriculture best practices
    RATE_ADJUSTMENTS = {
        VRAType.FERTILIZER: {
            # More fertilizer to low-vigor areas, less to high-vigor
            ZoneLevel.VERY_LOW: 1.3,
            ZoneLevel.LOW: 1.15,
            ZoneLevel.MEDIUM: 1.0,
            ZoneLevel.HIGH: 0.85,
            ZoneLevel.VERY_HIGH: 0.7,
        },
        VRAType.SEED: {
            # More seeds to high-potential areas, less to poor areas
            ZoneLevel.VERY_LOW: 0.8,
            ZoneLevel.LOW: 0.9,
            ZoneLevel.MEDIUM: 1.0,
            ZoneLevel.HIGH: 1.1,
            ZoneLevel.VERY_HIGH: 1.15,
        },
        VRAType.LIME: {
            # Assume low NDVI = acidic soil needing more lime
            ZoneLevel.VERY_LOW: 1.4,
            ZoneLevel.LOW: 1.2,
            ZoneLevel.MEDIUM: 1.0,
            ZoneLevel.HIGH: 0.8,
            ZoneLevel.VERY_HIGH: 0.6,
        },
        VRAType.PESTICIDE: {
            # Target high-vigor areas where pests thrive
            ZoneLevel.VERY_LOW: 0.7,
            ZoneLevel.LOW: 0.85,
            ZoneLevel.MEDIUM: 1.0,
            ZoneLevel.HIGH: 1.15,
            ZoneLevel.VERY_HIGH: 1.25,
        },
        VRAType.IRRIGATION: {
            # More water to low-vigor (water-stressed) areas
            ZoneLevel.VERY_LOW: 1.3,
            ZoneLevel.LOW: 1.15,
            ZoneLevel.MEDIUM: 1.0,
            ZoneLevel.HIGH: 0.85,
            ZoneLevel.VERY_HIGH: 0.75,
        },
    }

    # Zone colors for visualization
    ZONE_COLORS = {
        3: {
            "low": "#d62728",  # Red
            "medium": "#ff7f0e",  # Orange
            "high": "#2ca02c",  # Green
        },
        5: {
            "very_low": "#d62728",  # Red
            "low": "#ff7f0e",  # Orange
            "medium": "#ffdd00",  # Yellow
            "high": "#98df8a",  # Light green
            "very_high": "#2ca02c",  # Dark green
        },
    }

    # Arabic zone names
    ZONE_NAMES_AR = {
        "very_low": "منخفض جداً",
        "low": "منخفض",
        "medium": "متوسط",
        "high": "عالي",
        "very_high": "عالي جداً",
    }

    def __init__(self, multi_provider=None):
        """
        Initialize VRA Generator

        Args:
            multi_provider: MultiSatelliteService instance for fetching NDVI data
        """
        self.multi_provider = multi_provider
        # SECURITY (2026-04-21 audit): keyed on (tenant_id, prescription_id)
        # — not prescription_id alone — so a guessed/leaked prescription UUID
        # from tenant A cannot be read or deleted by tenant B via
        # get_prescription / delete_prescription / export endpoints.
        # Callers MUST supply tenant_id (derived from JWT at the router).
        self._prescription_store: dict[tuple[str, str], PrescriptionMap] = {}

    async def generate_prescription(
        self,
        field_id: str,
        latitude: float,
        longitude: float,
        vra_type: VRAType,
        target_rate: float,
        unit: str,
        tenant_id: str,
        num_zones: int = 3,
        zone_method: ZoneMethod = ZoneMethod.NDVI_BASED,
        min_rate: float | None = None,
        max_rate: float | None = None,
        date: datetime | None = None,
        product_price_per_unit: float | None = None,
        notes: str | None = None,
        notes_ar: str | None = None,
    ) -> PrescriptionMap:
        """
        Generate VRA prescription map based on NDVI zones.

        Args:
            field_id: Field identifier
            latitude: Field center latitude
            longitude: Field center longitude
            vra_type: Type of VRA (fertilizer, seed, etc.)
            target_rate: Average target application rate
            unit: Unit of measurement (kg/ha, seeds/ha, L/ha, mm/ha)
            tenant_id: **Required.** Owning tenant for this prescription.
                Must come from the authenticated caller's JWT
                (``user.tenant_id``) — never accepted from the
                request body or a query parameter. Used as half of
                the ``(tenant_id, prescription_id)`` composite
                storage key so cross-tenant reads are impossible
                at the dict layer (2026-04-21 audit #1).
            num_zones: Number of management zones (3 or 5)
            zone_method: Method for zone creation
            min_rate: Minimum application rate (optional)
            max_rate: Maximum application rate (optional)
            date: Date for NDVI data (defaults to most recent)
            product_price_per_unit: Price per unit for cost savings calculation
            notes: Additional notes (English)
            notes_ar: Additional notes (Arabic)

        Returns:
            PrescriptionMap with zones and recommendations

        Algorithm:
        1. Fetch NDVI image for field
        2. Classify pixels into management zones
        3. Calculate zone statistics and geometry
        4. Assign application rates based on zone and VRA type
        5. Calculate savings vs. flat rate
        6. Generate GeoJSON prescription
        """
        logger.info(f"Generating VRA prescription for field {field_id}, type={vra_type.value}, zones={num_zones}")

        # Validate inputs
        if num_zones not in [3, 5]:
            raise ValueError("num_zones must be 3 or 5")

        # Set default min/max rates if not provided
        if min_rate is None:
            min_rate = target_rate * 0.5
        if max_rate is None:
            max_rate = target_rate * 1.5

        # Step 1: Classify field into management zones
        zones_stats = await self.classify_zones(
            field_id=field_id,
            latitude=latitude,
            longitude=longitude,
            num_zones=num_zones,
            date=date,
        )

        # Step 2: Calculate application rates for each zone
        zones_with_rates = []
        for zone in zones_stats.zones:
            rate = self.calculate_zone_rate(
                zone_level=zone.zone_level,
                target_rate=target_rate,
                vra_type=vra_type,
                min_rate=min_rate,
                max_rate=max_rate,
            )

            # Update zone with rate and total product
            zone.recommended_rate = rate
            zone.unit = unit
            zone.total_product = rate * zone.area_ha

            zones_with_rates.append(zone)

        # Step 3: Calculate totals and savings
        total_area_ha = zones_stats.total_area_ha
        total_product_needed = sum(z.total_product for z in zones_with_rates)
        flat_rate_product = target_rate * total_area_ha

        savings_amount = flat_rate_product - total_product_needed
        savings_percent = (savings_amount / flat_rate_product * 100) if flat_rate_product > 0 else 0

        cost_savings = None
        if product_price_per_unit is not None:
            cost_savings = savings_amount * product_price_per_unit

        # Step 4: Create prescription map
        is_synthetic = bool(getattr(zones_stats, "is_synthetic", False))
        warning_en = (
            (
                "Prescription generated from synthetic NDVI zones — no real "
                "satellite imagery was available. Do NOT apply to the field "
                "without independent verification."
            )
            if is_synthetic
            else None
        )
        warning_ar = (
            (
                "تم إنشاء الوصفة من مناطق NDVI افتراضية — لم تتوفر صور أقمار "
                "صناعية حقيقية. لا تطبق على الحقل دون تحقق مستقل."
            )
            if is_synthetic
            else None
        )

        prescription = PrescriptionMap(
            id=str(uuid.uuid4()),
            field_id=field_id,
            vra_type=vra_type,
            created_at=datetime.now(),
            target_rate=target_rate,
            min_rate=min_rate,
            max_rate=max_rate,
            unit=unit,
            num_zones=num_zones,
            zone_method=zone_method,
            zones=zones_with_rates,
            total_area_ha=total_area_ha,
            total_product_needed=total_product_needed,
            flat_rate_product=flat_rate_product,
            savings_percent=round(savings_percent, 2),
            savings_amount=round(savings_amount, 2),
            cost_savings=round(cost_savings, 2) if cost_savings else None,
            notes=notes,
            notes_ar=notes_ar,
            is_synthetic=is_synthetic,
            data_warning_en=warning_en,
            data_warning_ar=warning_ar,
        )

        # Store prescription under the (tenant_id, prescription_id) composite
        # key so cross-tenant reads are impossible at the dict layer.
        self._prescription_store[(tenant_id, prescription.id)] = prescription

        logger.info(
            f"VRA prescription generated: tenant={tenant_id}, id={prescription.id}, savings={savings_percent:.1f}%"
        )

        return prescription

    async def classify_zones(
        self,
        field_id: str,
        latitude: float,
        longitude: float,
        num_zones: int = 3,
        date: datetime | None = None,
    ) -> ZoneStatistics:
        """
        Classify field into management zones based on NDVI

        Args:
            field_id: Field identifier
            latitude: Field center latitude
            longitude: Field center longitude
            num_zones: Number of zones (3 or 5)
            date: Date for NDVI data

        Returns:
            ZoneStatistics with classified zones
        """
        logger.info(f"Classifying field {field_id} into {num_zones} zones")

        # Try multi_provider first — pulls a real NDVI point from
        # Sentinel Hub / Copernicus STAC / NASA Earthdata. The ndvi value
        # is then used as the zone-mean; min/max/std are derived with a
        # small uniform spread around it. This is still coarser than
        # pixel-level k-means binning (which requires the field polygon
        # + rasterio), but it replaces the hardcoded 0.55 with a value
        # that actually reflects the field's current vigour.
        ndvi_mean = 0.55
        ndvi_std = 0.15
        ndvi_min = 0.25
        ndvi_max = 0.85
        real_ndvi = False
        provider_name = ""

        if self.multi_provider is not None:
            try:
                # Import the enum lazily + defensively (works whether
                # vra_generator is loaded as a package submodule or as a
                # top-level module in tests).
                try:
                    from .multi_provider import SatelliteType as _MPSatelliteType
                except ImportError:
                    from multi_provider import SatelliteType as _MPSatelliteType

                acq = date.date() if isinstance(date, datetime) else None
                result = await self.multi_provider.get_indices(
                    lat=latitude,
                    lon=longitude,
                    acquisition_date=acq,
                    satellite=_MPSatelliteType.SENTINEL2,
                )
                if result and getattr(result, "data", None):
                    ndvi_center = float(result.data.ndvi)
                    # Derive per-zone band with a conservative spread
                    # around the measured value — still coarser than
                    # real k-means but anchored in reality.
                    ndvi_mean = ndvi_center
                    ndvi_std = 0.1
                    ndvi_min = max(0.0, ndvi_center - 0.2)
                    ndvi_max = min(1.0, ndvi_center + 0.2)
                    real_ndvi = not bool(getattr(result, "is_simulated", True))
                    provider_name = getattr(result, "provider", "") or ""
            except Exception as e:
                # stdlib logger: f-string, not kwargs.
                logger.warning(f"vra_real_ndvi_fetch_failed field_id={field_id} error={e}")

        if not real_ndvi:
            # Either no multi_provider, or it returned simulated data.
            # Surface the synthetic flag so downstream (PrescriptionMap,
            # mobile UI) can refuse to dispatch the prescription.
            logger.warning(
                "vra_synthetic_zones_generated",
                extra={
                    "field_id": field_id,
                    "reason": (
                        "classify_zones produced synthetic zones — no real NDVI raster available from any provider"
                    ),
                    "provider_seen": provider_name or "none",
                },
            )

        # Get zone thresholds
        thresholds = self.ZONE_THRESHOLDS[num_zones]

        # Create management zones
        zones = []
        zone_id = 1

        # Simulated field area (in real implementation, get from field data)
        total_area_ha = 10.0  # 10 hectares

        # Create zones based on thresholds
        if num_zones == 3:
            zone_configs = [
                ("low", ZoneLevel.LOW, 0.25),
                ("medium", ZoneLevel.MEDIUM, 0.50),
                ("high", ZoneLevel.HIGH, 0.25),
            ]
        else:  # 5 zones
            zone_configs = [
                ("very_low", ZoneLevel.VERY_LOW, 0.15),
                ("low", ZoneLevel.LOW, 0.20),
                ("medium", ZoneLevel.MEDIUM, 0.30),
                ("high", ZoneLevel.HIGH, 0.20),
                ("very_high", ZoneLevel.VERY_HIGH, 0.15),
            ]

        for zone_name, zone_level, area_pct in zone_configs:
            zone_area = total_area_ha * area_pct

            # Get NDVI range for this zone
            ndvi_range = thresholds[zone_name]

            # Create simplified polygon (in reality, this would be actual field geometry)
            # For simulation, create a rectangular zone
            offset = zone_id * 0.001
            polygon = [
                [
                    [longitude - 0.002 + offset, latitude - 0.002],
                    [longitude + 0.002 + offset, latitude - 0.002],
                    [longitude + 0.002 + offset, latitude + 0.002],
                    [longitude - 0.002 + offset, latitude + 0.002],
                    [longitude - 0.002 + offset, latitude - 0.002],
                ]
            ]

            centroid = (longitude + offset, latitude)

            zone = ManagementZone(
                zone_id=zone_id,
                zone_name=zone_name.replace("_", " ").title(),
                zone_name_ar=self.ZONE_NAMES_AR[zone_name],
                zone_level=zone_level,
                ndvi_range=ndvi_range,
                area_ha=round(zone_area, 2),
                percentage=round(area_pct * 100, 1),
                centroid=centroid,
                polygon=polygon,
                recommended_rate=0.0,  # Will be set later
                unit="",  # Will be set later
                total_product=0.0,  # Will be calculated later
                color=self.ZONE_COLORS[num_zones][zone_name],
            )

            zones.append(zone)
            zone_id += 1

        # Even when NDVI is from a real provider, the polygons + area
        # remain synthetic (no real field-geometry integration yet). So
        # is_synthetic stays True until rasterio + field polygons land.
        # Prescription consumers use this to show the bilingual warning.
        return ZoneStatistics(
            num_zones=num_zones,
            zones=zones,
            total_area_ha=total_area_ha,
            ndvi_mean=ndvi_mean,
            ndvi_std=ndvi_std,
            ndvi_min=ndvi_min,
            ndvi_max=ndvi_max,
            is_synthetic=True,
        )

    def calculate_zone_rate(
        self,
        zone_level: ZoneLevel,
        target_rate: float,
        vra_type: VRAType,
        min_rate: float,
        max_rate: float,
    ) -> float:
        """
        Calculate application rate for a zone

        Args:
            zone_level: Zone classification level
            target_rate: Average target rate
            vra_type: Type of VRA
            min_rate: Minimum allowed rate
            max_rate: Maximum allowed rate

        Returns:
            Calculated application rate for the zone
        """
        # Get adjustment factor for this zone and VRA type
        adjustment = self.RATE_ADJUSTMENTS[vra_type].get(zone_level, 1.0)

        # Calculate rate
        rate = target_rate * adjustment

        # Clamp to min/max
        rate = max(min_rate, min(rate, max_rate))

        return round(rate, 2)

    def calculate_savings(
        self, zones: list[ManagementZone], target_rate: float, total_area: float
    ) -> tuple[float, float, float]:
        """
        Calculate savings vs. flat rate application

        Args:
            zones: List of management zones with rates
            target_rate: Flat rate that would be applied uniformly
            total_area: Total field area

        Returns:
            Tuple of (total_vra_product, flat_rate_product, savings_percent)
        """
        total_vra_product = sum(z.recommended_rate * z.area_ha for z in zones)
        flat_rate_product = target_rate * total_area

        savings_amount = flat_rate_product - total_vra_product
        savings_percent = (savings_amount / flat_rate_product * 100) if flat_rate_product > 0 else 0

        return total_vra_product, flat_rate_product, savings_percent

    def to_geojson(self, prescription: PrescriptionMap) -> dict[str, Any]:
        """
        Convert prescription to GeoJSON FeatureCollection

        Args:
            prescription: Prescription map to convert

        Returns:
            GeoJSON FeatureCollection with zones as features
        """
        features = []

        for zone in prescription.zones:
            feature = {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": zone.polygon},
                "properties": {
                    "zone_id": zone.zone_id,
                    "zone_name": zone.zone_name,
                    "zone_name_ar": zone.zone_name_ar,
                    "zone_level": zone.zone_level.value,
                    "ndvi_min": zone.ndvi_range[0],
                    "ndvi_max": zone.ndvi_range[1],
                    "area_ha": zone.area_ha,
                    "percentage": zone.percentage,
                    "rate": zone.recommended_rate,
                    "unit": zone.unit,
                    "total_product": zone.total_product,
                    "color": zone.color,
                },
            }
            features.append(feature)

        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "properties": {
                "prescription_id": prescription.id,
                "field_id": prescription.field_id,
                "vra_type": prescription.vra_type.value,
                "created_at": prescription.created_at.isoformat(),
                "target_rate": prescription.target_rate,
                "unit": prescription.unit,
                "total_area_ha": prescription.total_area_ha,
                "total_product": prescription.total_product_needed,
                "savings_percent": prescription.savings_percent,
            },
        }

        return geojson

    def to_shapefile_data(self, prescription: PrescriptionMap) -> dict[str, Any]:
        """
        Convert prescription to Shapefile-compatible data structure

        Args:
            prescription: Prescription map to convert

        Returns:
            Dictionary with shapefile data structure
        """
        # In a real implementation, this would use a library like pyshp or fiona
        # to create actual .shp, .shx, .dbf files
        # For now, return structured data that could be converted

        features = []
        for zone in prescription.zones:
            features.append(
                {
                    "geometry": {"type": "Polygon", "coordinates": zone.polygon},
                    "properties": {
                        "ZONE_ID": zone.zone_id,
                        "ZONE_NAME": zone.zone_name,
                        "ZONE_AR": zone.zone_name_ar,
                        "RATE": zone.recommended_rate,
                        "UNIT": zone.unit,
                        "AREA_HA": zone.area_ha,
                        "TOTAL_PROD": zone.total_product,
                    },
                }
            )

        return {
            "type": "shapefile",
            "crs": "EPSG:4326",
            "features": features,
            "metadata": {
                "prescription_id": prescription.id,
                "field_id": prescription.field_id,
                "vra_type": prescription.vra_type.value,
                "created": prescription.created_at.isoformat(),
            },
        }

    def to_isoxml(self, prescription: PrescriptionMap) -> str:
        """
        Convert prescription to ISO-XML format (ISOBUS Task Data)

        Args:
            prescription: Prescription map to convert

        Returns:
            ISO-XML string compatible with ISOBUS equipment
        """
        # Simplified ISO-XML structure
        # Full implementation would follow ISO 11783-10 standard

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ISO11783_TaskData VersionMajor="4" VersionMinor="0" ManagementSoftwareManufacturer="SAHOOL" ManagementSoftwareVersion="1.0">
  <Task TaskDesignator="{prescription.vra_type.value}_{prescription.field_id}" TaskStatus="1">
    <TreatmentZone TreatmentZoneCode="1" TreatmentZoneDesignator="VRA Prescription">
"""

        for zone in prescription.zones:
            xml += f"""      <ProcessDataVariable ProcessDataValue="{zone.recommended_rate}" ProcessDataDDI="0006">
        <Polygon PolygonType="1">
"""
            # Add polygon points
            if zone.polygon:
                for ring in zone.polygon:
                    for point in ring:
                        lon, lat = point
                        xml += f'          <Point PointEast="{lon}" PointNorth="{lat}"/>\n'

            xml += """        </Polygon>
      </ProcessDataVariable>
"""

        xml += """    </TreatmentZone>
  </Task>
</ISO11783_TaskData>
"""

        return xml

    async def get_prescription(self, prescription_id: str, tenant_id: str) -> PrescriptionMap | None:
        """
        Get a prescription by ID, scoped to the caller's tenant.

        Returns None when the prescription either doesn't exist OR
        belongs to a different tenant — same 404 either way, no
        enumeration oracle.
        """
        return self._prescription_store.get((tenant_id, prescription_id))

    async def get_field_prescriptions(self, field_id: str, tenant_id: str, limit: int = 10) -> list[PrescriptionMap]:
        """
        Get all prescriptions for a field, scoped to the caller's tenant.
        """
        prescriptions = [
            p for (t, _pid), p in self._prescription_store.items() if t == tenant_id and p.field_id == field_id
        ]

        # Sort by creation date (newest first)
        prescriptions.sort(key=lambda p: p.created_at, reverse=True)

        return prescriptions[:limit]

    async def delete_prescription(self, prescription_id: str, tenant_id: str) -> bool:
        """
        Delete a prescription, scoped to the caller's tenant.

        Returns False when the prescription is missing OR belongs to a
        different tenant — no cross-tenant delete, no enumeration oracle.
        """
        key = (tenant_id, prescription_id)
        if key in self._prescription_store:
            del self._prescription_store[key]
            return True
        return False
