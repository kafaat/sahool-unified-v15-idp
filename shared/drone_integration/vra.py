"""
SAHOOL Variable Rate Application (VRA) Module - وحدة التطبيق بالمعدل المتغير

Generate prescription maps for variable rate application based on:
- NDVI/vegetation indices | مؤشرات الغطاء النباتي
- Soil maps | خرائط التربة
- Yield data | بيانات المحصول
- Pest/disease hotspots | بؤر الآفات والأمراض

Supports multiple classification methods and export formats.

Version: 1.0.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from .models import (
    BoundingBox,
    Coordinate,
    PrescriptionMap,
    VRAZone,
    VRAZoneType,
    generate_id,
)

# ==============================================================================
# Constants and Configuration - الثوابت والتكوين
# ==============================================================================


class ClassificationMethod(StrEnum):
    """Method for classifying zones - طريقة تصنيف المناطق"""

    QUANTILE = "quantile"  # Equal count per zone | عدد متساوٍ لكل منطقة
    EQUAL_INTERVAL = "equal_interval"  # Equal range per zone | نطاق متساوٍ لكل منطقة
    JENKS = "jenks"  # Natural breaks | فواصل طبيعية
    MANUAL = "manual"  # User-defined thresholds | عتبات محددة من المستخدم
    STANDARD_DEVIATION = "std_dev"  # Based on std deviation | بناءً على الانحراف المعياري


class VRASourceType(StrEnum):
    """Source data type for VRA - نوع البيانات المصدر"""

    NDVI = "ndvi"  # Normalized Difference Vegetation Index | مؤشر الغطاء النباتي
    LAI = "lai"  # Leaf Area Index | مؤشر مساحة الورقة
    YIELD = "yield"  # Historical yield data | بيانات المحصول التاريخية
    SOIL_EC = "soil_ec"  # Soil electrical conductivity | موصلية التربة الكهربائية
    SOIL_OM = "soil_om"  # Soil organic matter | المادة العضوية في التربة
    SOIL_N = "soil_n"  # Soil nitrogen | نيتروجين التربة
    SOIL_P = "soil_p"  # Soil phosphorus | فوسفور التربة
    SOIL_K = "soil_k"  # Soil potassium | بوتاسيوم التربة
    PEST = "pest"  # Pest pressure map | خريطة ضغط الآفات
    WEED = "weed"  # Weed density map | خريطة كثافة الأعشاب
    THERMAL = "thermal"  # Thermal imagery | الصور الحرارية
    CUSTOM = "custom"  # Custom data source | مصدر بيانات مخصص


class RateAdjustmentMode(StrEnum):
    """How to adjust rates in zones - كيفية ضبط المعدلات في المناطق"""

    PROPORTIONAL = "proportional"  # Rate proportional to index | معدل متناسب مع المؤشر
    INVERSE = "inverse"  # Rate inverse to index | معدل عكسي للمؤشر
    THRESHOLD = "threshold"  # On/off at threshold | تشغيل/إيقاف عند العتبة
    CUSTOM = "custom"  # Custom function | دالة مخصصة


# Default NDVI zone thresholds
DEFAULT_NDVI_ZONES = {
    VRAZoneType.LOW_VIGOR: (0.0, 0.3),
    VRAZoneType.STRESSED: (0.3, 0.45),
    VRAZoneType.MEDIUM_VIGOR: (0.45, 0.6),
    VRAZoneType.HIGH_VIGOR: (0.6, 1.0),
}

# Rate multipliers by zone type (fertilizer application)
DEFAULT_RATE_MULTIPLIERS = {
    VRAZoneType.LOW_VIGOR: 1.5,  # 150% of base rate
    VRAZoneType.STRESSED: 1.25,  # 125% of base rate
    VRAZoneType.MEDIUM_VIGOR: 1.0,  # 100% of base rate
    VRAZoneType.HIGH_VIGOR: 0.75,  # 75% of base rate
    VRAZoneType.WEED_PATCH: 1.5,  # Higher herbicide rate
    VRAZoneType.PEST_HOTSPOT: 1.5,  # Higher pesticide rate
    VRAZoneType.BARE_SOIL: 0.0,  # No application
    VRAZoneType.WATER_BODY: 0.0,  # No application (exclusion)
    VRAZoneType.EXCLUSION: 0.0,  # No application (exclusion)
}


# ==============================================================================
# Configuration Classes - فئات التكوين
# ==============================================================================


@dataclass
class VRAConfig:
    """Configuration for VRA map generation - تكوين إنشاء خريطة VRA"""

    # Source data
    source_type: VRASourceType = VRASourceType.NDVI

    # Classification
    classification_method: ClassificationMethod = ClassificationMethod.QUANTILE
    zone_count: int = 5  # Number of zones to generate

    # Rate adjustment
    adjustment_mode: RateAdjustmentMode = RateAdjustmentMode.PROPORTIONAL
    base_rate_l_ha: float = 10.0  # Base application rate
    min_rate_l_ha: float = 0.0  # Minimum rate
    max_rate_l_ha: float = 30.0  # Maximum rate

    # Custom thresholds (for manual classification)
    custom_thresholds: list[float] = field(default_factory=list)

    # Zone type mapping
    zone_type_thresholds: dict[VRAZoneType, tuple[float, float]] = field(
        default_factory=lambda: DEFAULT_NDVI_ZONES.copy()
    )

    # Rate multipliers
    rate_multipliers: dict[VRAZoneType, float] = field(default_factory=lambda: DEFAULT_RATE_MULTIPLIERS.copy())

    # Exclusion zones
    exclude_water_bodies: bool = True
    exclude_buffer_zones: bool = True
    buffer_distance_m: float = 10.0

    # Smoothing
    smooth_zones: bool = True
    min_zone_area_ha: float = 0.01  # Minimum zone size (100 m2)


@dataclass
class GridCell:
    """Single cell in a raster grid - خلية واحدة في الشبكة النقطية"""

    row: int
    col: int
    center: Coordinate
    value: float
    zone_type: VRAZoneType | None = None
    rate_l_ha: float = 0.0

    def to_dict(self) -> dict:
        return {
            "row": self.row,
            "col": self.col,
            "lat": self.center.lat,
            "lng": self.center.lng,
            "value": self.value,
            "zone_type": self.zone_type.value if self.zone_type else None,
            "rate_l_ha": self.rate_l_ha,
        }


@dataclass
class VRARasterData:
    """Raster data for VRA processing - بيانات نقطية لمعالجة VRA"""

    # Grid properties
    rows: int
    cols: int
    cell_size_m: float

    # Bounds
    bounds: BoundingBox

    # Data
    cells: list[list[GridCell]]  # 2D grid of cells

    # Statistics
    min_value: float = 0.0
    max_value: float = 1.0
    mean_value: float = 0.5
    std_value: float = 0.1
    valid_cell_count: int = 0

    # Metadata
    source_type: VRASourceType = VRASourceType.NDVI
    capture_date: datetime | None = None
    no_data_value: float = -999.0

    def get_cell(self, lat: float, lng: float) -> GridCell | None:
        """Get cell at geographic coordinate"""
        if not self.bounds:
            return None

        col = int((lng - self.bounds.min_lng) / self._lng_cell_size())
        row = int((self.bounds.max_lat - lat) / self._lat_cell_size())

        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.cells[row][col]
        return None

    def _lat_cell_size(self) -> float:
        """Get cell size in latitude degrees"""
        return (self.bounds.max_lat - self.bounds.min_lat) / self.rows

    def _lng_cell_size(self) -> float:
        """Get cell size in longitude degrees"""
        return (self.bounds.max_lng - self.bounds.min_lng) / self.cols


# ==============================================================================
# VRA Generator - مولد VRA
# ==============================================================================


class VRAGenerator:
    """
    Variable Rate Application map generator.
    مولد خرائط التطبيق بالمعدل المتغير.

    Generates prescription maps from vegetation indices, soil data,
    or other spatial data sources for precision agriculture applications.
    """

    def __init__(self, config: VRAConfig | None = None):
        """
        Initialize VRA generator.

        Args:
            config: VRA configuration | تكوين VRA
        """
        self.config = config or VRAConfig()

    def generate_from_ndvi_grid(
        self,
        field_id: str,
        tenant_id: str,
        ndvi_data: list[list[float]],
        bounds: BoundingBox,
        cell_size_m: float = 10.0,
        name: str = "NDVI Prescription Map",
        name_ar: str = "خريطة وصفة NDVI",
        product_name: str = "",
        product_name_ar: str = "",
    ) -> PrescriptionMap:
        """
        Generate VRA prescription map from NDVI grid data.
        إنشاء خريطة وصفة VRA من بيانات شبكة NDVI.

        Args:
            field_id: Field identifier | معرف الحقل
            tenant_id: Tenant identifier | معرف المستأجر
            ndvi_data: 2D array of NDVI values | مصفوفة ثنائية البعد لقيم NDVI
            bounds: Geographic bounds of data | الحدود الجغرافية للبيانات
            cell_size_m: Cell size in meters | حجم الخلية بالمتر
            name: Map name | اسم الخريطة
            name_ar: Map name in Arabic | اسم الخريطة بالعربية
            product_name: Product name | اسم المنتج
            product_name_ar: Product name in Arabic | اسم المنتج بالعربية

        Returns:
            PrescriptionMap | خريطة الوصفة
        """
        rows = len(ndvi_data)
        len(ndvi_data[0]) if rows > 0 else 0

        # Convert to raster data structure
        raster = self._create_raster_from_array(
            data=ndvi_data, bounds=bounds, cell_size_m=cell_size_m, source_type=VRASourceType.NDVI
        )

        # Classify cells into zones
        self._classify_cells(raster)

        # Apply rate calculation
        self._calculate_rates(raster)

        # Convert classified cells to VRA zones
        zones = self._cells_to_zones(raster, bounds)

        # Calculate statistics
        total_area_ha = sum(z.area_ha for z in zones)
        total_volume_l = sum(z.area_ha * z.rate_l_ha for z in zones)
        rates = [z.rate_l_ha for z in zones if z.rate_l_ha > 0]

        # Create prescription map
        prescription_map = PrescriptionMap(
            id=generate_id("vrm"),
            tenant_id=tenant_id,
            field_id=field_id,
            name=name,
            name_ar=name_ar,
            zones=zones,
            total_area_ha=total_area_ha,
            base_rate_l_ha=self.config.base_rate_l_ha,
            product_name=product_name,
            product_name_ar=product_name_ar,
            source_type=self.config.source_type.value,
            source_date=datetime.now(UTC),
            zone_count=len(zones),
            classification_method=self.config.classification_method.value,
            min_rate_l_ha=min(rates) if rates else 0,
            max_rate_l_ha=max(rates) if rates else 0,
            avg_rate_l_ha=sum(rates) / len(rates) if rates else 0,
            total_volume_l=total_volume_l,
        )

        return prescription_map

    def generate_from_points(
        self,
        field_id: str,
        tenant_id: str,
        points: list[dict],
        boundary: list[Coordinate],
        cell_size_m: float = 10.0,
        value_field: str = "value",
        name: str = "Point Prescription Map",
        name_ar: str = "خريطة وصفة النقاط",
    ) -> PrescriptionMap:
        """
        Generate VRA prescription map from point samples.
        إنشاء خريطة وصفة VRA من عينات نقطية.

        Uses inverse distance weighting (IDW) interpolation.

        Args:
            field_id: Field identifier | معرف الحقل
            tenant_id: Tenant identifier | معرف المستأجر
            points: List of points with lat, lng, and value | قائمة النقاط
            boundary: Field boundary | حدود الحقل
            cell_size_m: Output cell size | حجم خلية الإخراج
            value_field: Name of value field in points | اسم حقل القيمة
            name: Map name | اسم الخريطة
            name_ar: Map name in Arabic | اسم الخريطة بالعربية

        Returns:
            PrescriptionMap | خريطة الوصفة
        """
        # Get bounds from boundary
        bounds = self._get_bounds_from_boundary(boundary)

        # Create interpolated grid
        rows = int((bounds.max_lat - bounds.min_lat) * 111320 / cell_size_m)
        cols = int(
            (bounds.max_lng - bounds.min_lng)
            * 111320
            * math.cos(math.radians((bounds.min_lat + bounds.max_lat) / 2))
            / cell_size_m
        )

        rows = max(1, rows)
        cols = max(1, cols)

        # IDW interpolation
        grid = []
        lat_step = (bounds.max_lat - bounds.min_lat) / rows
        lng_step = (bounds.max_lng - bounds.min_lng) / cols

        for r in range(rows):
            row_data = []
            cell_lat = bounds.max_lat - (r + 0.5) * lat_step

            for c in range(cols):
                cell_lng = bounds.min_lng + (c + 0.5) * lng_step

                # Check if cell is inside boundary
                cell_coord = Coordinate(lat=cell_lat, lng=cell_lng)
                if self._point_in_polygon(cell_coord, boundary):
                    value = self._idw_interpolate(cell_lat, cell_lng, points, value_field)
                else:
                    value = self.config.min_rate_l_ha  # No data outside boundary

                row_data.append(value)

            grid.append(row_data)

        return self.generate_from_ndvi_grid(
            field_id=field_id,
            tenant_id=tenant_id,
            ndvi_data=grid,
            bounds=bounds,
            cell_size_m=cell_size_m,
            name=name,
            name_ar=name_ar,
        )

    def generate_weed_map(
        self,
        field_id: str,
        tenant_id: str,
        weed_detections: list[dict],
        boundary: list[Coordinate],
        cell_size_m: float = 5.0,
        base_rate_l_ha: float = 10.0,
        hotspot_multiplier: float = 2.0,
        name: str = "Weed Map",
        name_ar: str = "خريطة الأعشاب",
    ) -> PrescriptionMap:
        """
        Generate VRA map for weed control from detection points.
        إنشاء خريطة VRA لمكافحة الأعشاب من نقاط الكشف.

        Args:
            field_id: Field identifier | معرف الحقل
            tenant_id: Tenant identifier | معرف المستأجر
            weed_detections: List of weed detection points | قائمة نقاط كشف الأعشاب
            boundary: Field boundary | حدود الحقل
            cell_size_m: Output cell size | حجم خلية الإخراج
            base_rate_l_ha: Base herbicide rate | معدل مبيد الأعشاب الأساسي
            hotspot_multiplier: Rate multiplier for hotspots | مضاعف المعدل للبؤر
            name: Map name | اسم الخريطة
            name_ar: Map name in Arabic | اسم الخريطة بالعربية

        Returns:
            PrescriptionMap | خريطة الوصفة
        """
        # Configure for weed mapping
        weed_config = VRAConfig(
            source_type=VRASourceType.WEED,
            classification_method=ClassificationMethod.MANUAL,
            base_rate_l_ha=base_rate_l_ha,
            adjustment_mode=RateAdjustmentMode.THRESHOLD,
            zone_count=3,
            custom_thresholds=[0.3, 0.7],
        )

        original_config = self.config
        self.config = weed_config

        # Convert detections to density grid
        bounds = self._get_bounds_from_boundary(boundary)
        rows = int((bounds.max_lat - bounds.min_lat) * 111320 / cell_size_m)
        cols = int(
            (bounds.max_lng - bounds.min_lng)
            * 111320
            * math.cos(math.radians((bounds.min_lat + bounds.max_lat) / 2))
            / cell_size_m
        )

        rows = max(1, rows)
        cols = max(1, cols)

        # Calculate weed density per cell
        grid = [[0.0 for _ in range(cols)] for _ in range(rows)]
        lat_step = (bounds.max_lat - bounds.min_lat) / rows
        lng_step = (bounds.max_lng - bounds.min_lng) / cols

        for detection in weed_detections:
            det_lat = detection.get("lat", 0)
            det_lng = detection.get("lng", 0)
            density = detection.get("density", 1.0)

            r = int((bounds.max_lat - det_lat) / lat_step)
            c = int((det_lng - bounds.min_lng) / lng_step)

            if 0 <= r < rows and 0 <= c < cols:
                grid[r][c] += density

        # Normalize to 0-1
        max_density = max(max(row) for row in grid) or 1.0
        grid = [[v / max_density for v in row] for row in grid]

        # Generate prescription map
        prescription = self.generate_from_ndvi_grid(
            field_id=field_id,
            tenant_id=tenant_id,
            ndvi_data=grid,
            bounds=bounds,
            cell_size_m=cell_size_m,
            name=name,
            name_ar=name_ar,
        )

        # Reclassify zones for weed control
        for zone in prescription.zones:
            if zone.ndvi_mean and zone.ndvi_mean > 0.7:
                zone.zone_type = VRAZoneType.WEED_PATCH
                zone.rate_l_ha = base_rate_l_ha * hotspot_multiplier
                zone.label_en = "High Weed Density"
                zone.label_ar = "كثافة أعشاب عالية"
            elif zone.ndvi_mean and zone.ndvi_mean > 0.3:
                zone.zone_type = VRAZoneType.MEDIUM_VIGOR
                zone.rate_l_ha = base_rate_l_ha
                zone.label_en = "Medium Weed Density"
                zone.label_ar = "كثافة أعشاب متوسطة"
            else:
                zone.zone_type = VRAZoneType.LOW_VIGOR
                zone.rate_l_ha = base_rate_l_ha * 0.5
                zone.label_en = "Low Weed Density"
                zone.label_ar = "كثافة أعشاب منخفضة"

        # Recalculate totals
        prescription.total_volume_l = sum(z.area_ha * z.rate_l_ha for z in prescription.zones)

        self.config = original_config
        return prescription

    def generate_fertilizer_map(
        self,
        field_id: str,
        tenant_id: str,
        ndvi_data: list[list[float]],
        bounds: BoundingBox,
        base_rate_kg_ha: float = 100.0,
        fertilizer_name: str = "Urea 46%",
        fertilizer_name_ar: str = "يوريا 46%",
        cell_size_m: float = 10.0,
        name: str = "Fertilizer Prescription",
        name_ar: str = "وصفة التسميد",
    ) -> PrescriptionMap:
        """
        Generate fertilizer VRA map from NDVI data.
        إنشاء خريطة VRA للتسميد من بيانات NDVI.

        Lower NDVI = higher fertilizer rate (inverse relationship).

        Args:
            field_id: Field identifier | معرف الحقل
            tenant_id: Tenant identifier | معرف المستأجر
            ndvi_data: 2D NDVI grid | شبكة NDVI ثنائية البعد
            bounds: Geographic bounds | الحدود الجغرافية
            base_rate_kg_ha: Base fertilizer rate kg/ha | معدل التسميد الأساسي
            fertilizer_name: Fertilizer name | اسم السماد
            fertilizer_name_ar: Fertilizer name in Arabic | اسم السماد بالعربية
            cell_size_m: Cell size | حجم الخلية
            name: Map name | اسم الخريطة
            name_ar: Map name in Arabic | اسم الخريطة بالعربية

        Returns:
            PrescriptionMap | خريطة الوصفة
        """
        # Configure for fertilizer (inverse NDVI relationship)
        fert_config = VRAConfig(
            source_type=VRASourceType.NDVI,
            classification_method=ClassificationMethod.QUANTILE,
            base_rate_l_ha=base_rate_kg_ha,
            adjustment_mode=RateAdjustmentMode.INVERSE,
            zone_count=5,
            rate_multipliers={
                VRAZoneType.LOW_VIGOR: 1.5,
                VRAZoneType.STRESSED: 1.25,
                VRAZoneType.MEDIUM_VIGOR: 1.0,
                VRAZoneType.HIGH_VIGOR: 0.75,
                VRAZoneType.BARE_SOIL: 0.0,
                VRAZoneType.EXCLUSION: 0.0,
            },
        )

        original_config = self.config
        self.config = fert_config

        prescription = self.generate_from_ndvi_grid(
            field_id=field_id,
            tenant_id=tenant_id,
            ndvi_data=ndvi_data,
            bounds=bounds,
            cell_size_m=cell_size_m,
            name=name,
            name_ar=name_ar,
            product_name=fertilizer_name,
            product_name_ar=fertilizer_name_ar,
        )

        # Add recommendations to zones
        for zone in prescription.zones:
            if zone.zone_type == VRAZoneType.LOW_VIGOR:
                zone.recommendation_en = "Apply high rate to boost plant growth"
                zone.recommendation_ar = "طبق معدلاً عالياً لتعزيز نمو النبات"
            elif zone.zone_type == VRAZoneType.STRESSED:
                zone.recommendation_en = "Moderate increase to address stress"
                zone.recommendation_ar = "زيادة معتدلة لمعالجة الإجهاد"
            elif zone.zone_type == VRAZoneType.MEDIUM_VIGOR:
                zone.recommendation_en = "Standard application rate"
                zone.recommendation_ar = "معدل التطبيق القياسي"
            elif zone.zone_type == VRAZoneType.HIGH_VIGOR:
                zone.recommendation_en = "Reduce rate - vigorous growth"
                zone.recommendation_ar = "خفض المعدل - نمو قوي"

        self.config = original_config
        return prescription

    # ==========================================================================
    # Internal Methods - الأساليب الداخلية
    # ==========================================================================

    def _create_raster_from_array(
        self,
        data: list[list[float]],
        bounds: BoundingBox,
        cell_size_m: float,
        source_type: VRASourceType,
    ) -> VRARasterData:
        """Create VRARasterData from 2D array"""
        rows = len(data)
        cols = len(data[0]) if rows > 0 else 0

        lat_step = (bounds.max_lat - bounds.min_lat) / rows if rows > 0 else 0
        lng_step = (bounds.max_lng - bounds.min_lng) / cols if cols > 0 else 0

        cells = []
        all_values = []

        for r in range(rows):
            row_cells = []
            for c in range(cols):
                value = data[r][c]
                center = Coordinate(
                    lat=bounds.max_lat - (r + 0.5) * lat_step,
                    lng=bounds.min_lng + (c + 0.5) * lng_step,
                )

                cell = GridCell(row=r, col=c, center=center, value=value)
                row_cells.append(cell)

                if value != -999.0:  # Skip no-data
                    all_values.append(value)

            cells.append(row_cells)

        # Calculate statistics
        min_val = min(all_values) if all_values else 0
        max_val = max(all_values) if all_values else 1
        mean_val = sum(all_values) / len(all_values) if all_values else 0.5
        std_val = (
            math.sqrt(sum((v - mean_val) ** 2 for v in all_values) / len(all_values)) if len(all_values) > 1 else 0
        )

        return VRARasterData(
            rows=rows,
            cols=cols,
            cell_size_m=cell_size_m,
            bounds=bounds,
            cells=cells,
            min_value=min_val,
            max_value=max_val,
            mean_value=mean_val,
            std_value=std_val,
            valid_cell_count=len(all_values),
            source_type=source_type,
        )

    def _classify_cells(self, raster: VRARasterData) -> None:
        """Classify cells into zone types based on configuration"""
        method = self.config.classification_method
        zone_count = self.config.zone_count

        # Get all valid values
        values = [cell.value for row in raster.cells for cell in row if cell.value != raster.no_data_value]

        if not values:
            return

        values_sorted = sorted(values)
        n = len(values_sorted)

        # Calculate thresholds based on method
        if method == ClassificationMethod.QUANTILE:
            thresholds = [values_sorted[int(i * n / zone_count)] for i in range(1, zone_count)]
        elif method == ClassificationMethod.EQUAL_INTERVAL:
            interval = (raster.max_value - raster.min_value) / zone_count
            thresholds = [raster.min_value + i * interval for i in range(1, zone_count)]
        elif method == ClassificationMethod.STANDARD_DEVIATION:
            thresholds = [raster.mean_value + (i - zone_count // 2) * raster.std_value for i in range(1, zone_count)]
        elif method == ClassificationMethod.MANUAL:
            thresholds = self.config.custom_thresholds
        else:  # JENKS - simplified approximation
            thresholds = self._calculate_jenks_breaks(values_sorted, zone_count)

        # Assign zone types to cells
        zone_types = list(self.config.zone_type_thresholds.keys())

        for row in raster.cells:
            for cell in row:
                if cell.value == raster.no_data_value:
                    cell.zone_type = VRAZoneType.EXCLUSION
                    continue

                # Find zone by threshold
                zone_idx = 0
                for t in thresholds:
                    if cell.value >= t:
                        zone_idx += 1

                # Map to zone type based on value
                if self.config.source_type == VRASourceType.NDVI:
                    cell.zone_type = self._ndvi_to_zone_type(cell.value)
                elif zone_idx < len(zone_types):
                    cell.zone_type = zone_types[zone_idx]
                else:
                    cell.zone_type = VRAZoneType.MEDIUM_VIGOR

    def _ndvi_to_zone_type(self, ndvi: float) -> VRAZoneType:
        """Map NDVI value to zone type"""
        if ndvi < 0.1:
            return VRAZoneType.BARE_SOIL
        elif ndvi < 0.3:
            return VRAZoneType.LOW_VIGOR
        elif ndvi < 0.45:
            return VRAZoneType.STRESSED
        elif ndvi < 0.6:
            return VRAZoneType.MEDIUM_VIGOR
        else:
            return VRAZoneType.HIGH_VIGOR

    def _calculate_rates(self, raster: VRARasterData) -> None:
        """Calculate application rates for cells"""
        base_rate = self.config.base_rate_l_ha
        mode = self.config.adjustment_mode
        multipliers = self.config.rate_multipliers

        for row in raster.cells:
            for cell in row:
                if cell.zone_type == VRAZoneType.EXCLUSION:
                    cell.rate_l_ha = 0.0
                    continue

                multiplier = multipliers.get(cell.zone_type, 1.0)

                if mode == RateAdjustmentMode.PROPORTIONAL:
                    # Rate proportional to value
                    cell.rate_l_ha = base_rate * multiplier
                elif mode == RateAdjustmentMode.INVERSE:
                    # Rate inverse to value (for fertilizer based on NDVI)
                    cell.rate_l_ha = base_rate * multiplier
                elif mode == RateAdjustmentMode.THRESHOLD:
                    # On/off at threshold
                    cell.rate_l_ha = base_rate if cell.value > 0.3 else 0.0
                else:
                    cell.rate_l_ha = base_rate * multiplier

                # Apply limits
                cell.rate_l_ha = max(self.config.min_rate_l_ha, min(self.config.max_rate_l_ha, cell.rate_l_ha))

    def _cells_to_zones(self, raster: VRARasterData, bounds: BoundingBox) -> list[VRAZone]:
        """Convert classified cells to VRA zones"""
        zones = []
        zone_cells: dict[VRAZoneType, list[GridCell]] = {}

        # Group cells by zone type
        for row in raster.cells:
            for cell in row:
                if cell.zone_type not in zone_cells:
                    zone_cells[cell.zone_type] = []
                zone_cells[cell.zone_type].append(cell)

        # Create zone for each type
        lat_step = (bounds.max_lat - bounds.min_lat) / raster.rows
        lng_step = (bounds.max_lng - bounds.min_lng) / raster.cols
        cell_area_m2 = raster.cell_size_m**2

        for zone_type, cells in zone_cells.items():
            if not cells:
                continue

            # Calculate zone statistics
            values = [c.value for c in cells if c.value != -999.0]
            rates = [c.rate_l_ha for c in cells]

            ndvi_mean = sum(values) / len(values) if values else None
            ndvi_std = (
                math.sqrt(sum((v - ndvi_mean) ** 2 for v in values) / len(values))
                if values and len(values) > 1 and ndvi_mean
                else None
            )

            avg_rate = sum(rates) / len(rates) if rates else 0
            area_ha = len(cells) * cell_area_m2 / 10000

            # Create simplified boundary (convex hull approximation)
            boundary = self._create_zone_boundary(cells, lat_step, lng_step)

            # Get zone labels
            label_en, label_ar = self._get_zone_labels(zone_type)

            zone = VRAZone(
                id=generate_id("vrz"),
                zone_type=zone_type,
                boundary=boundary,
                area_ha=area_ha,
                centroid=self._calculate_centroid(cells),
                rate_l_ha=avg_rate,
                rate_percent=(avg_rate / self.config.base_rate_l_ha * 100) if self.config.base_rate_l_ha > 0 else 100,
                ndvi_mean=ndvi_mean,
                ndvi_std=ndvi_std,
                source_date=datetime.now(UTC),
                label_en=label_en,
                label_ar=label_ar,
            )

            zones.append(zone)

        return zones

    def _create_zone_boundary(self, cells: list[GridCell], lat_step: float, lng_step: float) -> list[Coordinate]:
        """Create simplified boundary polygon for zone cells"""
        if not cells:
            return []

        # Get all cell corners
        points = set()
        half_lat = lat_step / 2
        half_lng = lng_step / 2

        for cell in cells:
            lat, lng = cell.center.lat, cell.center.lng
            points.add((lat - half_lat, lng - half_lng))
            points.add((lat - half_lat, lng + half_lng))
            points.add((lat + half_lat, lng - half_lng))
            points.add((lat + half_lat, lng + half_lng))

        # Create convex hull (simplified)
        points_list = list(points)
        hull = self._convex_hull(points_list)

        return [Coordinate(lat=p[0], lng=p[1]) for p in hull]

    def _convex_hull(self, points: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Calculate convex hull using Graham scan"""
        if len(points) < 3:
            return points

        # Find lowest point
        start = min(points, key=lambda p: (p[0], p[1]))
        points = sorted(
            points,
            key=lambda p: (
                math.atan2(p[1] - start[1], p[0] - start[0]),
                (p[0] - start[0]) ** 2 + (p[1] - start[1]) ** 2,
            ),
        )

        hull = []
        for p in points:
            while len(hull) > 1 and self._cross(hull[-2], hull[-1], p) <= 0:
                hull.pop()
            hull.append(p)

        return hull

    def _cross(self, o: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
        """Cross product for convex hull"""
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def _calculate_centroid(self, cells: list[GridCell]) -> Coordinate:
        """Calculate centroid of cells"""
        if not cells:
            return Coordinate(lat=0, lng=0)

        lat_sum = sum(c.center.lat for c in cells)
        lng_sum = sum(c.center.lng for c in cells)
        n = len(cells)

        return Coordinate(lat=lat_sum / n, lng=lng_sum / n)

    def _get_zone_labels(self, zone_type: VRAZoneType) -> tuple[str, str]:
        """Get English and Arabic labels for zone type"""
        labels = {
            VRAZoneType.HIGH_VIGOR: ("High Vigor", "نمو قوي"),
            VRAZoneType.MEDIUM_VIGOR: ("Medium Vigor", "نمو متوسط"),
            VRAZoneType.LOW_VIGOR: ("Low Vigor", "نمو ضعيف"),
            VRAZoneType.STRESSED: ("Stressed", "إجهاد"),
            VRAZoneType.WEED_PATCH: ("Weed Patch", "بقعة أعشاب"),
            VRAZoneType.PEST_HOTSPOT: ("Pest Hotspot", "بؤرة آفات"),
            VRAZoneType.BARE_SOIL: ("Bare Soil", "تربة مكشوفة"),
            VRAZoneType.WATER_BODY: ("Water Body", "مسطح مائي"),
            VRAZoneType.EXCLUSION: ("Exclusion Zone", "منطقة استبعاد"),
        }
        return labels.get(zone_type, ("Unknown", "غير معروف"))

    def _calculate_jenks_breaks(self, values: list[float], n_classes: int) -> list[float]:
        """Calculate Jenks natural breaks (simplified)"""
        if len(values) <= n_classes:
            return sorted(set(values))

        # Simplified: use quantiles as approximation
        n = len(values)
        return [values[int(i * n / n_classes)] for i in range(1, n_classes)]

    def _get_bounds_from_boundary(self, boundary: list[Coordinate]) -> BoundingBox:
        """Get bounding box from boundary polygon"""
        lats = [c.lat for c in boundary]
        lngs = [c.lng for c in boundary]

        return BoundingBox(min_lat=min(lats), max_lat=max(lats), min_lng=min(lngs), max_lng=max(lngs))

    def _point_in_polygon(self, point: Coordinate, polygon: list[Coordinate]) -> bool:
        """Check if point is inside polygon"""
        n = len(polygon)
        inside = False

        j = n - 1
        for i in range(n):
            if ((polygon[i].lat > point.lat) != (polygon[j].lat > point.lat)) and (
                point.lng
                < (polygon[j].lng - polygon[i].lng) * (point.lat - polygon[i].lat) / (polygon[j].lat - polygon[i].lat)
                + polygon[i].lng
            ):
                inside = not inside
            j = i

        return inside

    def _idw_interpolate(
        self, lat: float, lng: float, points: list[dict], value_field: str, power: float = 2.0
    ) -> float:
        """Inverse distance weighting interpolation"""
        if not points:
            return 0.0

        weights = []
        values = []

        for p in points:
            p_lat = p.get("lat", 0)
            p_lng = p.get("lng", 0)
            p_val = p.get(value_field, 0)

            # Calculate distance
            dlat = (lat - p_lat) * 111320
            dlng = (lng - p_lng) * 111320 * math.cos(math.radians(lat))
            dist = math.sqrt(dlat**2 + dlng**2)

            if dist < 0.001:  # Very close, use this value
                return p_val

            weight = 1.0 / (dist**power)
            weights.append(weight)
            values.append(p_val)

        total_weight = sum(weights)
        if total_weight == 0:
            return 0.0

        return sum(w * v for w, v in zip(weights, values)) / total_weight


# ==============================================================================
# Convenience Functions - دوال مساعدة
# ==============================================================================


def create_ndvi_prescription(
    field_id: str,
    tenant_id: str,
    ndvi_grid: list[list[float]],
    bounds: BoundingBox,
    base_rate_l_ha: float = 10.0,
    name: str = "NDVI Prescription",
    name_ar: str = "وصفة NDVI",
) -> PrescriptionMap:
    """
    Create a prescription map from NDVI data.
    إنشاء خريطة وصفة من بيانات NDVI.

    Args:
        field_id: Field identifier | معرف الحقل
        tenant_id: Tenant identifier | معرف المستأجر
        ndvi_grid: 2D NDVI values | قيم NDVI ثنائية البعد
        bounds: Geographic bounds | الحدود الجغرافية
        base_rate_l_ha: Base application rate | معدل التطبيق الأساسي
        name: Map name | اسم الخريطة
        name_ar: Map name in Arabic | اسم الخريطة بالعربية

    Returns:
        PrescriptionMap | خريطة الوصفة
    """
    config = VRAConfig(
        source_type=VRASourceType.NDVI,
        base_rate_l_ha=base_rate_l_ha,
        zone_count=5,
    )

    generator = VRAGenerator(config)

    return generator.generate_from_ndvi_grid(
        field_id=field_id,
        tenant_id=tenant_id,
        ndvi_data=ndvi_grid,
        bounds=bounds,
        name=name,
        name_ar=name_ar,
    )


def create_spot_spray_map(
    field_id: str,
    tenant_id: str,
    detection_points: list[dict],
    boundary: list[Coordinate],
    detection_type: str = "weed",
    base_rate_l_ha: float = 5.0,
    name: str = "Spot Spray Map",
    name_ar: str = "خريطة الرش النقطي",
) -> PrescriptionMap:
    """
    Create a spot spray map from detection points.
    إنشاء خريطة رش نقطي من نقاط الكشف.

    Args:
        field_id: Field identifier | معرف الحقل
        tenant_id: Tenant identifier | معرف المستأجر
        detection_points: List of detection points | قائمة نقاط الكشف
        boundary: Field boundary | حدود الحقل
        detection_type: Type of detection (weed, pest) | نوع الكشف
        base_rate_l_ha: Base rate for detections | المعدل الأساسي للكشف
        name: Map name | اسم الخريطة
        name_ar: Map name in Arabic | اسم الخريطة بالعربية

    Returns:
        PrescriptionMap | خريطة الوصفة
    """
    generator = VRAGenerator()

    if detection_type == "weed":
        return generator.generate_weed_map(
            field_id=field_id,
            tenant_id=tenant_id,
            weed_detections=detection_points,
            boundary=boundary,
            base_rate_l_ha=base_rate_l_ha,
            name=name,
            name_ar=name_ar,
        )
    else:
        # Generic spot spray
        return generator.generate_from_points(
            field_id=field_id,
            tenant_id=tenant_id,
            points=detection_points,
            boundary=boundary,
            value_field="density",
            name=name,
            name_ar=name_ar,
        )


def export_prescription_to_shapefile(prescription: PrescriptionMap, output_path: str) -> dict:
    """
    Export prescription map to Shapefile format.
    تصدير خريطة الوصفة إلى تنسيق Shapefile.

    Note: Requires fiona and shapely libraries.

    Args:
        prescription: Prescription map to export | خريطة الوصفة للتصدير
        output_path: Output file path | مسار ملف الإخراج

    Returns:
        Dict with export status | قاموس بحالة التصدير
    """
    try:
        import fiona
        from shapely.geometry import Polygon, mapping

        schema = {
            "geometry": "Polygon",
            "properties": {
                "zone_id": "str",
                "zone_type": "str",
                "rate_l_ha": "float",
                "rate_pct": "float",
                "area_ha": "float",
                "ndvi_mean": "float",
                "label_en": "str",
                "label_ar": "str",
            },
        }

        with fiona.open(output_path, "w", driver="ESRI Shapefile", crs="EPSG:4326", schema=schema) as output:
            for zone in prescription.zones:
                if len(zone.boundary) < 3:
                    continue

                polygon = Polygon([(c.lng, c.lat) for c in zone.boundary])

                output.write(
                    {
                        "geometry": mapping(polygon),
                        "properties": {
                            "zone_id": zone.id,
                            "zone_type": zone.zone_type.value,
                            "rate_l_ha": zone.rate_l_ha,
                            "rate_pct": zone.rate_percent,
                            "area_ha": zone.area_ha,
                            "ndvi_mean": zone.ndvi_mean or 0,
                            "label_en": zone.label_en,
                            "label_ar": zone.label_ar,
                        },
                    }
                )

        return {
            "success": True,
            "message_en": f"Exported to {output_path}",
            "message_ar": f"تم التصدير إلى {output_path}",
            "zone_count": len(prescription.zones),
        }

    except ImportError:
        return {
            "success": False,
            "message_en": "Fiona and Shapely libraries required for Shapefile export",
            "message_ar": "مكتبات Fiona و Shapely مطلوبة لتصدير Shapefile",
        }
    except Exception as e:
        return {
            "success": False,
            "message_en": f"Export failed: {str(e)}",
            "message_ar": f"فشل التصدير: {str(e)}",
        }
