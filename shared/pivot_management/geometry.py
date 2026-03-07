"""
Pivot Circular Geometry - هندسة المحور الدائرية

Generate circular field boundaries, sector polygons, and annular span zones
for center pivot and linear move irrigation systems.

Provides the backend geometry that matches the mobile SpanZone models
(apps/mobile/lib/features/pivot_irrigation/domain/models/span_zone_models.dart).

Version: 1.0.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

# Earth constants
EARTH_RADIUS_M = 6371000.0


def _degrees_to_radians(deg: float) -> float:
    return deg * math.pi / 180.0


def _radians_to_degrees(rad: float) -> float:
    return rad * 180.0 / math.pi


def _destination_point(lon: float, lat: float, bearing_deg: float, distance_m: float) -> tuple[float, float]:
    """
    Calculate destination point given start, bearing, and distance.
    حساب نقطة الوصول بمعرفة البداية والاتجاه والمسافة.

    Uses Vincenty's direct formula (spherical approximation).

    Args:
        lon: Start longitude | خط الطول
        lat: Start latitude | خط العرض
        bearing_deg: Bearing in degrees (0=North, 90=East) | الاتجاه بالدرجات
        distance_m: Distance in meters | المسافة بالمتر

    Returns:
        (longitude, latitude) of destination point
    """
    lat1 = _degrees_to_radians(lat)
    lon1 = _degrees_to_radians(lon)
    bearing = _degrees_to_radians(bearing_deg)
    d = distance_m / EARTH_RADIUS_M

    lat2 = math.asin(math.sin(lat1) * math.cos(d) + math.cos(lat1) * math.sin(d) * math.cos(bearing))
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(d) * math.cos(lat1),
        math.cos(d) - math.sin(lat1) * math.sin(lat2),
    )

    return (_radians_to_degrees(lon2), _radians_to_degrees(lat2))


# =============================================================================
# Data Models - النماذج
# =============================================================================


@dataclass
class PivotGeometry:
    """
    Circular field boundary for a center pivot.
    حدود حقل دائرية لمحور مركزي.
    """

    center_lon: float
    center_lat: float
    radius_m: float
    boundary: list[tuple[float, float]]  # (lon, lat) closed polygon
    area_hectares: float
    perimeter_m: float
    num_points: int


@dataclass
class PivotSector:
    """
    A sector (pie slice) of a pivot circle.
    قطاع (شريحة دائرية) من دائرة المحور.
    """

    sector_id: str
    start_angle_deg: float  # 0 = North, clockwise
    end_angle_deg: float
    inner_radius_m: float  # 0 for full sector from center
    outer_radius_m: float
    boundary: list[tuple[float, float]]  # (lon, lat) closed polygon
    area_hectares: float


@dataclass
class SpanAnnulus:
    """
    Annular ring for a single span/tower.
    حلقة دائرية لبرج/ذراع واحد.

    Matches the mobile SpanConfiguration model.
    """

    span_number: int
    inner_radius_m: float
    outer_radius_m: float
    boundary: list[tuple[float, float]]  # (lon, lat) closed polygon
    area_hectares: float
    arc_length_m: float  # at outer radius


@dataclass
class PivotZoneGrid:
    """
    Complete zone grid for VRI control.
    شبكة مناطق كاملة للتحكم في VRI.

    Matches the mobile VRIZoneGrid model.
    """

    pivot_id: str
    center_lon: float
    center_lat: float
    radius_m: float
    span_count: int
    angular_divisions: int
    zones: list[PivotZoneCell] = field(default_factory=list)
    total_area_hectares: float = 0.0


@dataclass
class PivotZoneCell:
    """
    Single cell in the pivot zone grid (span x angle).
    خلية واحدة في شبكة مناطق المحور.
    """

    zone_id: str
    span_number: int
    angle_index: int
    start_angle_deg: float
    end_angle_deg: float
    inner_radius_m: float
    outer_radius_m: float
    boundary: list[tuple[float, float]]
    area_hectares: float
    application_rate_percent: float = 100.0
    ndvi_value: float | None = None


# =============================================================================
# Geometry Functions - وظائف الهندسة
# =============================================================================


def create_circular_field_boundary(
    center_lon: float,
    center_lat: float,
    radius_m: float,
    num_points: int = 72,
) -> PivotGeometry:
    """
    Create a circular field boundary polygon from center point and radius.
    إنشاء حدود حقل دائرية من نقطة المركز ونصف القطر.

    Generates a geodesically accurate circle on Earth's surface.

    Args:
        center_lon: Center longitude | خط طول المركز
        center_lat: Center latitude | خط عرض المركز
        radius_m: Radius in meters (typically 100-800m) | نصف القطر بالمتر
        num_points: Number of polygon vertices (default 72 = 5 degree steps)

    Returns:
        PivotGeometry with closed polygon boundary
    """
    if radius_m <= 0:
        raise ValueError("Radius must be positive | نصف القطر يجب أن يكون موجباً")
    if num_points < 8:
        raise ValueError("Minimum 8 points required | مطلوب 8 نقاط كحد أدنى")

    boundary = []
    angle_step = 360.0 / num_points

    for i in range(num_points):
        bearing = i * angle_step
        lon, lat = _destination_point(center_lon, center_lat, bearing, radius_m)
        boundary.append((lon, lat))

    # Close the polygon
    boundary.append(boundary[0])

    area_sqm = math.pi * radius_m**2
    area_hectares = area_sqm / 10000.0
    perimeter_m = 2 * math.pi * radius_m

    return PivotGeometry(
        center_lon=center_lon,
        center_lat=center_lat,
        radius_m=radius_m,
        boundary=boundary,
        area_hectares=area_hectares,
        perimeter_m=perimeter_m,
        num_points=num_points,
    )


def create_pivot_sector(
    center_lon: float,
    center_lat: float,
    start_angle_deg: float,
    end_angle_deg: float,
    outer_radius_m: float,
    inner_radius_m: float = 0.0,
    points_per_arc: int = 18,
) -> PivotSector:
    """
    Create a sector (pie slice) or annular sector polygon.
    إنشاء قطاع دائري أو قطاع حلقي.

    Args:
        center_lon: Center longitude | خط طول المركز
        center_lat: Center latitude | خط عرض المركز
        start_angle_deg: Start angle (0=North, clockwise) | زاوية البداية
        end_angle_deg: End angle | زاوية النهاية
        outer_radius_m: Outer radius | نصف القطر الخارجي
        inner_radius_m: Inner radius (0 for full sector) | نصف القطر الداخلي
        points_per_arc: Points per arc segment | نقاط لكل قوس

    Returns:
        PivotSector with boundary polygon
    """
    # Normalize angles
    sweep = end_angle_deg - start_angle_deg
    if sweep <= 0:
        sweep += 360.0

    # Calculate boundary points
    boundary = []
    angle_step = sweep / max(1, points_per_arc)

    if inner_radius_m > 0:
        # Annular sector: outer arc → inner arc (reversed) → close
        # Outer arc
        for i in range(points_per_arc + 1):
            bearing = start_angle_deg + i * angle_step
            lon, lat = _destination_point(center_lon, center_lat, bearing, outer_radius_m)
            boundary.append((lon, lat))

        # Inner arc (reversed)
        for i in range(points_per_arc, -1, -1):
            bearing = start_angle_deg + i * angle_step
            lon, lat = _destination_point(center_lon, center_lat, bearing, inner_radius_m)
            boundary.append((lon, lat))
    else:
        # Full sector from center
        boundary.append(_destination_point(center_lon, center_lat, start_angle_deg, 0.001))

        # Outer arc
        for i in range(points_per_arc + 1):
            bearing = start_angle_deg + i * angle_step
            lon, lat = _destination_point(center_lon, center_lat, bearing, outer_radius_m)
            boundary.append((lon, lat))

    # Close polygon
    boundary.append(boundary[0])

    # Calculate area
    sweep_rad = _degrees_to_radians(sweep)
    area_sqm = 0.5 * sweep_rad * (outer_radius_m**2 - inner_radius_m**2)
    area_hectares = area_sqm / 10000.0

    sector_id = f"sector_{int(start_angle_deg)}_{int(end_angle_deg)}"

    return PivotSector(
        sector_id=sector_id,
        start_angle_deg=start_angle_deg,
        end_angle_deg=end_angle_deg,
        inner_radius_m=inner_radius_m,
        outer_radius_m=outer_radius_m,
        boundary=boundary,
        area_hectares=area_hectares,
    )


def create_span_annulus(
    center_lon: float,
    center_lat: float,
    span_number: int,
    inner_radius_m: float,
    outer_radius_m: float,
    num_points: int = 72,
) -> SpanAnnulus:
    """
    Create an annular ring representing a single span/tower coverage area.
    إنشاء حلقة تمثل منطقة تغطية برج واحد.

    Args:
        center_lon: Center longitude
        center_lat: Center latitude
        span_number: Span/tower number (1-based)
        inner_radius_m: Inner radius of the ring
        outer_radius_m: Outer radius of the ring
        num_points: Points for circle approximation

    Returns:
        SpanAnnulus with boundary polygon
    """
    angle_step = 360.0 / num_points

    # Outer ring
    outer_points = []
    for i in range(num_points):
        bearing = i * angle_step
        lon, lat = _destination_point(center_lon, center_lat, bearing, outer_radius_m)
        outer_points.append((lon, lat))

    # Inner ring (reversed for proper polygon winding)
    inner_points = []
    for i in range(num_points - 1, -1, -1):
        bearing = i * angle_step
        lon, lat = _destination_point(center_lon, center_lat, bearing, inner_radius_m)
        inner_points.append((lon, lat))

    # Combine: outer → inner → close
    boundary = outer_points + [outer_points[0]] + inner_points + [inner_points[0], outer_points[0]]

    area_sqm = math.pi * (outer_radius_m**2 - inner_radius_m**2)
    area_hectares = area_sqm / 10000.0
    arc_length_m = 2 * math.pi * outer_radius_m

    return SpanAnnulus(
        span_number=span_number,
        inner_radius_m=inner_radius_m,
        outer_radius_m=outer_radius_m,
        boundary=boundary,
        area_hectares=area_hectares,
        arc_length_m=arc_length_m,
    )


def create_pivot_zone_grid(
    pivot_id: str,
    center_lon: float,
    center_lat: float,
    radius_m: float,
    span_count: int,
    angular_divisions: int = 36,
    span_lengths_m: list[float] | None = None,
    points_per_arc: int = 6,
) -> PivotZoneGrid:
    """
    Create a complete VRI zone grid for a pivot system.
    إنشاء شبكة مناطق VRI كاملة لنظام محوري.

    Divides the pivot circle into span_count radial rings
    and angular_divisions angular sectors, creating a grid
    of zones for variable rate irrigation control.

    Matches the mobile VRIZoneGrid/VRIZoneGridBuilder pattern.

    Args:
        pivot_id: Pivot identifier | معرف المحور
        center_lon: Center longitude | خط طول المركز
        center_lat: Center latitude | خط عرض المركز
        radius_m: Total pivot radius | نصف القطر الكلي
        span_count: Number of spans/towers | عدد الأبراج
        angular_divisions: Number of angular divisions (default 36 = 10 degrees)
        span_lengths_m: Custom span lengths (if None, equal division)
        points_per_arc: Points per arc for polygon generation

    Returns:
        PivotZoneGrid with all zone cells
    """
    if span_count < 1:
        raise ValueError("span_count must be >= 1")
    if angular_divisions < 4:
        raise ValueError("angular_divisions must be >= 4")

    # Calculate span boundaries
    if span_lengths_m and len(span_lengths_m) == span_count:
        radii = [0.0]
        cumulative = 0.0
        for length in span_lengths_m:
            cumulative += length
            radii.append(min(cumulative, radius_m))
    else:
        span_width = radius_m / span_count
        radii = [i * span_width for i in range(span_count + 1)]

    angular_step = 360.0 / angular_divisions

    zones = []
    total_area = 0.0

    for span_idx in range(span_count):
        inner_r = radii[span_idx]
        outer_r = radii[span_idx + 1]

        for angle_idx in range(angular_divisions):
            start_angle = angle_idx * angular_step
            end_angle = (angle_idx + 1) * angular_step

            # Create cell boundary polygon
            boundary = _create_annular_sector_boundary(
                center_lon,
                center_lat,
                start_angle,
                end_angle,
                inner_r,
                outer_r,
                points_per_arc,
            )

            # Calculate cell area
            sweep_rad = _degrees_to_radians(angular_step)
            cell_area_sqm = 0.5 * sweep_rad * (outer_r**2 - inner_r**2)
            cell_area_ha = cell_area_sqm / 10000.0
            total_area += cell_area_ha

            zone_id = f"zone_{span_idx}_{angle_idx}"

            cell = PivotZoneCell(
                zone_id=zone_id,
                span_number=span_idx + 1,
                angle_index=angle_idx,
                start_angle_deg=start_angle,
                end_angle_deg=end_angle,
                inner_radius_m=inner_r,
                outer_radius_m=outer_r,
                boundary=boundary,
                area_hectares=cell_area_ha,
            )
            zones.append(cell)

    return PivotZoneGrid(
        pivot_id=pivot_id,
        center_lon=center_lon,
        center_lat=center_lat,
        radius_m=radius_m,
        span_count=span_count,
        angular_divisions=angular_divisions,
        zones=zones,
        total_area_hectares=total_area,
    )


def _create_annular_sector_boundary(
    center_lon: float,
    center_lat: float,
    start_angle: float,
    end_angle: float,
    inner_r: float,
    outer_r: float,
    points_per_arc: int,
) -> list[tuple[float, float]]:
    """Create boundary polygon for an annular sector cell."""
    sweep = end_angle - start_angle
    if sweep <= 0:
        sweep += 360.0

    angle_step = sweep / max(1, points_per_arc)
    boundary = []

    if inner_r < 1.0:
        # Sector from center (first span)
        boundary.append(_destination_point(center_lon, center_lat, start_angle, 0.5))
        for i in range(points_per_arc + 1):
            bearing = start_angle + i * angle_step
            lon, lat = _destination_point(center_lon, center_lat, bearing, outer_r)
            boundary.append((lon, lat))
    else:
        # Annular sector
        for i in range(points_per_arc + 1):
            bearing = start_angle + i * angle_step
            lon, lat = _destination_point(center_lon, center_lat, bearing, outer_r)
            boundary.append((lon, lat))

        for i in range(points_per_arc, -1, -1):
            bearing = start_angle + i * angle_step
            lon, lat = _destination_point(center_lon, center_lat, bearing, inner_r)
            boundary.append((lon, lat))

    boundary.append(boundary[0])
    return boundary


# =============================================================================
# GeoJSON Export - تصدير GeoJSON
# =============================================================================


def pivot_geometry_to_geojson(pivot: PivotGeometry) -> dict:
    """
    Convert PivotGeometry to GeoJSON Feature.
    تحويل هندسة المحور إلى GeoJSON Feature.
    """
    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [pivot.boundary],
        },
        "properties": {
            "center_lon": pivot.center_lon,
            "center_lat": pivot.center_lat,
            "radius_m": pivot.radius_m,
            "area_hectares": round(pivot.area_hectares, 2),
            "perimeter_m": round(pivot.perimeter_m, 1),
            "type": "center_pivot",
        },
    }


def zone_grid_to_geojson(grid: PivotZoneGrid) -> dict:
    """
    Convert PivotZoneGrid to GeoJSON FeatureCollection.
    تحويل شبكة المناطق إلى GeoJSON FeatureCollection.

    Each zone cell becomes a Feature with properties for VRI control.
    """
    features = []
    for zone in grid.zones:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [zone.boundary],
            },
            "properties": {
                "zone_id": zone.zone_id,
                "span_number": zone.span_number,
                "angle_index": zone.angle_index,
                "start_angle": zone.start_angle_deg,
                "end_angle": zone.end_angle_deg,
                "inner_radius_m": zone.inner_radius_m,
                "outer_radius_m": zone.outer_radius_m,
                "area_hectares": round(zone.area_hectares, 4),
                "application_rate_percent": zone.application_rate_percent,
                "ndvi_value": zone.ndvi_value,
            },
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "pivot_id": grid.pivot_id,
            "center": [grid.center_lon, grid.center_lat],
            "radius_m": grid.radius_m,
            "span_count": grid.span_count,
            "angular_divisions": grid.angular_divisions,
            "total_area_hectares": round(grid.total_area_hectares, 2),
        },
    }
