"""
VRA to VRI Prescription Converter - محول وصفات VRA إلى VRI

Converts rectangular VRA prescription maps (from drone_integration/vra.py)
into radial VRI prescriptions compatible with center pivot zone control.

The converter maps grid-based VRA zones onto the radial span x angle
zone grid used by Valley ICON 5, AgSense, and similar pivot controllers.

Supports both:
- Speed Control VRI: single rate per angular sector (pivot speed adjustment)
- Zone Control VRI: independent rate per span x angle cell (valve control)

Version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from .geometry import (
    PivotZoneGrid,
    _destination_point,
)

# =============================================================================
# Models - النماذج
# =============================================================================


@dataclass
class VRIZone:
    """
    A single zone in a VRI prescription.
    منطقة واحدة في وصفة VRI.
    """

    zone_id: str
    span_number: int
    angle_index: int
    start_angle_deg: float
    end_angle_deg: float
    application_rate_percent: float  # 0-150%, 100 = normal
    depth_mm: float = 0.0  # target application depth
    ndvi_mean: float | None = None
    source_zone_type: str = ""  # original VRA zone type


@dataclass
class VRIPrescription:
    """
    Complete VRI prescription for a pivot.
    وصفة VRI كاملة لمحور.
    """

    prescription_id: str
    pivot_id: str
    name: str
    name_ar: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Grid dimensions
    span_count: int = 0
    angular_divisions: int = 0

    # Zones
    zones: list[VRIZone] = field(default_factory=list)

    # Control mode
    control_mode: str = "zone_control"  # "speed_control" or "zone_control"

    # Statistics
    avg_rate_percent: float = 100.0
    min_rate_percent: float = 0.0
    max_rate_percent: float = 150.0
    water_savings_percent: float = 0.0
    base_depth_mm: float = 25.0

    # Source info
    source_type: str = ""  # "ndvi", "vra_map", "soil_ec", "manual"
    source_id: str = ""

    def to_speed_control_table(self) -> list[dict]:
        """
        Convert to speed control table (rate per angular position).
        تحويل إلى جدول التحكم بالسرعة.

        Speed control uses a single rate for all spans at each angle.
        Returns list of {angle, speed_percent} entries.
        """
        if not self.zones:
            return []

        angle_rates: dict[int, list[float]] = {}
        for zone in self.zones:
            idx = zone.angle_index
            if idx not in angle_rates:
                angle_rates[idx] = []
            angle_rates[idx].append(zone.application_rate_percent)

        table = []
        for idx in sorted(angle_rates.keys()):
            rates = angle_rates[idx]
            avg_rate = sum(rates) / len(rates) if rates else 100.0
            start_angle = idx * (360.0 / self.angular_divisions)
            # Speed is inverse of rate: higher rate = slower speed
            speed_percent = round(100.0 * 100.0 / max(avg_rate, 1.0), 1)
            table.append(
                {
                    "angle_index": idx,
                    "start_angle": start_angle,
                    "application_rate_percent": round(avg_rate, 1),
                    "speed_percent": min(100.0, speed_percent),
                }
            )

        return table

    def to_zone_control_matrix(self) -> list[list[float]]:
        """
        Convert to zone control matrix [span][angle] of rate percentages.
        تحويل إلى مصفوفة التحكم بالمنطقة.
        """
        matrix = [[100.0] * self.angular_divisions for _ in range(self.span_count)]

        for zone in self.zones:
            span_idx = zone.span_number - 1
            angle_idx = zone.angle_index
            if 0 <= span_idx < self.span_count and 0 <= angle_idx < self.angular_divisions:
                matrix[span_idx][angle_idx] = zone.application_rate_percent

        return matrix


@dataclass
class VRIConverterConfig:
    """
    Configuration for VRA → VRI conversion.
    تكوين تحويل VRA إلى VRI.
    """

    # Rate mapping
    min_rate_percent: float = 0.0
    max_rate_percent: float = 150.0
    off_threshold_percent: float = 10.0  # below this = turn off

    # NDVI → rate conversion
    ndvi_low_threshold: float = 0.3
    ndvi_stressed_threshold: float = 0.45
    ndvi_medium_threshold: float = 0.6

    # Rates for each NDVI category (for irrigation: low NDVI = more water)
    ndvi_low_rate: float = 130.0  # stressed → needs more water
    ndvi_stressed_rate: float = 115.0
    ndvi_medium_rate: float = 100.0
    ndvi_high_rate: float = 85.0  # healthy → needs less water
    ndvi_bare_rate: float = 0.0  # bare soil → off

    # Smoothing
    smooth_adjacent: bool = True  # smooth extreme differences between neighbors

    # Base application
    base_depth_mm: float = 25.0  # base pivot application depth


# =============================================================================
# Converter Functions - وظائف التحويل
# =============================================================================


def ndvi_to_vri_prescription(
    pivot_id: str,
    zone_grid: PivotZoneGrid,
    ndvi_data: list[list[float]],
    ndvi_bounds: tuple[float, float, float, float],  # min_lon, min_lat, max_lon, max_lat
    config: VRIConverterConfig | None = None,
    name: str = "NDVI VRI Prescription",
    name_ar: str = "وصفة VRI من NDVI",
) -> VRIPrescription:
    """
    Convert NDVI raster data to VRI prescription for a pivot.
    تحويل بيانات NDVI النقطية إلى وصفة VRI لمحور.

    Samples NDVI values at each zone cell center and converts
    to application rate percentages.

    Args:
        pivot_id: Pivot identifier | معرف المحور
        zone_grid: Pre-built zone grid from create_pivot_zone_grid()
        ndvi_data: 2D array of NDVI values [row][col] | مصفوفة NDVI
        ndvi_bounds: Geographic bounds (min_lon, min_lat, max_lon, max_lat)
        config: Converter configuration | تكوين المحول
        name: Prescription name | اسم الوصفة
        name_ar: Prescription name in Arabic | اسم الوصفة بالعربية

    Returns:
        VRIPrescription with zone rates
    """
    cfg = config or VRIConverterConfig()

    if not ndvi_data or not ndvi_data[0]:
        raise ValueError("NDVI data cannot be empty | بيانات NDVI لا يمكن أن تكون فارغة")

    ndvi_rows = len(ndvi_data)
    ndvi_cols = len(ndvi_data[0])
    min_lon, min_lat, max_lon, max_lat = ndvi_bounds

    vri_zones = []
    rates = []

    for zone_cell in zone_grid.zones:
        # Calculate zone cell center
        mid_angle = (zone_cell.start_angle_deg + zone_cell.end_angle_deg) / 2.0
        mid_radius = (zone_cell.inner_radius_m + zone_cell.outer_radius_m) / 2.0

        center_lon, center_lat = _destination_point(
            zone_grid.center_lon,
            zone_grid.center_lat,
            mid_angle,
            mid_radius,
        )

        # Sample NDVI at cell center
        ndvi_value = _sample_ndvi(
            center_lon,
            center_lat,
            ndvi_data,
            ndvi_rows,
            ndvi_cols,
            min_lon,
            min_lat,
            max_lon,
            max_lat,
        )

        # Convert NDVI to application rate
        rate = _ndvi_to_rate(ndvi_value, cfg)

        vri_zone = VRIZone(
            zone_id=zone_cell.zone_id,
            span_number=zone_cell.span_number,
            angle_index=zone_cell.angle_index,
            start_angle_deg=zone_cell.start_angle_deg,
            end_angle_deg=zone_cell.end_angle_deg,
            application_rate_percent=rate,
            depth_mm=cfg.base_depth_mm * rate / 100.0,
            ndvi_mean=ndvi_value,
        )
        vri_zones.append(vri_zone)
        if rate > 0:
            rates.append(rate)

    # Calculate statistics
    avg_rate = sum(rates) / len(rates) if rates else 100.0
    min_rate = min(rates) if rates else 0.0
    max_rate = max(rates) if rates else 100.0
    water_savings = max(0.0, 100.0 - avg_rate)

    prescription_id = f"vri_{pivot_id}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"

    return VRIPrescription(
        prescription_id=prescription_id,
        pivot_id=pivot_id,
        name=name,
        name_ar=name_ar,
        span_count=zone_grid.span_count,
        angular_divisions=zone_grid.angular_divisions,
        zones=vri_zones,
        control_mode="zone_control",
        avg_rate_percent=round(avg_rate, 1),
        min_rate_percent=round(min_rate, 1),
        max_rate_percent=round(max_rate, 1),
        water_savings_percent=round(water_savings, 1),
        base_depth_mm=cfg.base_depth_mm,
        source_type="ndvi",
    )


def vra_to_vri_prescription(
    pivot_id: str,
    zone_grid: PivotZoneGrid,
    vra_zones: list[dict],
    config: VRIConverterConfig | None = None,
    name: str = "VRA-derived VRI Prescription",
    name_ar: str = "وصفة VRI من خريطة VRA",
) -> VRIPrescription:
    """
    Convert VRA prescription zones to VRI prescription for a pivot.
    تحويل مناطق وصفة VRA إلى وصفة VRI لمحور.

    Maps each VRA zone polygon onto the radial zone grid by checking
    which VRA zone each pivot cell center falls within.

    Args:
        pivot_id: Pivot identifier | معرف المحور
        zone_grid: Pre-built zone grid from create_pivot_zone_grid()
        vra_zones: List of VRA zone dicts with boundary, rate_l_ha, zone_type
        config: Converter configuration | تكوين المحول
        name: Prescription name | اسم الوصفة
        name_ar: Prescription name in Arabic | اسم الوصفة بالعربية

    Returns:
        VRIPrescription with zone rates
    """
    cfg = config or VRIConverterConfig()

    # Extract VRA zone boundaries and rates
    vra_polys = []
    for vz in vra_zones:
        boundary = vz.get("boundary", [])
        rate = vz.get("rate_l_ha", 0.0)
        base_rate = vz.get("base_rate_l_ha", 10.0)
        zone_type = vz.get("zone_type", "")

        # Convert absolute rate to percentage of base
        rate_percent = (rate / base_rate * 100.0) if base_rate > 0 else 100.0
        rate_percent = max(cfg.min_rate_percent, min(cfg.max_rate_percent, rate_percent))

        coords = []
        for point in boundary:
            if isinstance(point, dict):
                coords.append((point.get("lng", point.get("lon", 0)), point.get("lat", 0)))
            elif isinstance(point, (list, tuple)) and len(point) >= 2:
                coords.append((float(point[0]), float(point[1])))

        if coords:
            vra_polys.append((coords, rate_percent, zone_type))

    vri_zones = []
    rates = []

    for zone_cell in zone_grid.zones:
        mid_angle = (zone_cell.start_angle_deg + zone_cell.end_angle_deg) / 2.0
        mid_radius = (zone_cell.inner_radius_m + zone_cell.outer_radius_m) / 2.0

        center_lon, center_lat = _destination_point(
            zone_grid.center_lon,
            zone_grid.center_lat,
            mid_angle,
            mid_radius,
        )

        # Find which VRA zone this cell center falls in
        rate = 100.0  # default: full rate
        source_type = ""

        for poly_coords, poly_rate, poly_type in vra_polys:
            if _point_in_polygon_simple(center_lon, center_lat, poly_coords):
                rate = poly_rate
                source_type = poly_type
                break

        if rate < cfg.off_threshold_percent:
            rate = 0.0

        vri_zone = VRIZone(
            zone_id=zone_cell.zone_id,
            span_number=zone_cell.span_number,
            angle_index=zone_cell.angle_index,
            start_angle_deg=zone_cell.start_angle_deg,
            end_angle_deg=zone_cell.end_angle_deg,
            application_rate_percent=round(rate, 1),
            depth_mm=cfg.base_depth_mm * rate / 100.0,
            source_zone_type=source_type,
        )
        vri_zones.append(vri_zone)
        if rate > 0:
            rates.append(rate)

    avg_rate = sum(rates) / len(rates) if rates else 100.0
    min_rate = min(rates) if rates else 0.0
    max_rate = max(rates) if rates else 100.0
    water_savings = max(0.0, 100.0 - avg_rate)

    prescription_id = f"vri_{pivot_id}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"

    return VRIPrescription(
        prescription_id=prescription_id,
        pivot_id=pivot_id,
        name=name,
        name_ar=name_ar,
        span_count=zone_grid.span_count,
        angular_divisions=zone_grid.angular_divisions,
        zones=vri_zones,
        control_mode="zone_control",
        avg_rate_percent=round(avg_rate, 1),
        min_rate_percent=round(min_rate, 1),
        max_rate_percent=round(max_rate, 1),
        water_savings_percent=round(water_savings, 1),
        base_depth_mm=cfg.base_depth_mm,
        source_type="vra_map",
    )


# =============================================================================
# Internal Helpers - وظائف داخلية
# =============================================================================


def _sample_ndvi(
    lon: float,
    lat: float,
    ndvi_data: list[list[float]],
    rows: int,
    cols: int,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
) -> float:
    """Sample NDVI value at a geographic coordinate using nearest neighbor."""
    if max_lon <= min_lon or max_lat <= min_lat:
        return 0.5

    col = int((lon - min_lon) / (max_lon - min_lon) * cols)
    row = int((max_lat - lat) / (max_lat - min_lat) * rows)

    col = max(0, min(cols - 1, col))
    row = max(0, min(rows - 1, row))

    return ndvi_data[row][col]


def _ndvi_to_rate(ndvi: float, cfg: VRIConverterConfig) -> float:
    """Convert NDVI value to application rate percentage."""
    if ndvi < 0.1:
        return cfg.ndvi_bare_rate
    elif ndvi < cfg.ndvi_low_threshold:
        return cfg.ndvi_low_rate
    elif ndvi < cfg.ndvi_stressed_threshold:
        return cfg.ndvi_stressed_rate
    elif ndvi < cfg.ndvi_medium_threshold:
        return cfg.ndvi_medium_rate
    else:
        return cfg.ndvi_high_rate


def _point_in_polygon_simple(px: float, py: float, polygon: list[tuple[float, float]]) -> bool:
    """Ray casting point-in-polygon test."""
    n = len(polygon)
    inside = False
    j = n - 1

    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]

        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i

    return inside
