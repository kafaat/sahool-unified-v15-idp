"""
SAHOOL GeoJSON Utilities Module
===============================
Provides comprehensive GeoJSON handling for terrain-related services.

مودول أدوات GeoJSON

Features:
- GeoJSON parsing and validation
- Coordinate transformation utilities
- Feature collection helpers
- Area/perimeter calculation for geometries
- Simplified geometry output generation

Usage:
    from shared.terrain.geojson_utils import (
        parse_geojson_polygon,
        validate_geojson_feature,
        create_feature_collection,
        calculate_polygon_area,
        simplify_coordinates,
    )

Author: SAHOOL Platform
Version: 16.0.0
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Literal

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Earth radius in meters for geodesic calculations
EARTH_RADIUS_M = 6371000.0

# Supported geometry types
GEOJSON_TYPES = {"Point", "LineString", "Polygon", "MultiPoint", "MultiLineString", "MultiPolygon"}

# Coordinate precision (decimal places)
DEFAULT_PRECISION = 6


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class GeoJSONGeometry:
    """Parsed GeoJSON geometry with metadata."""

    type: str
    coordinates: list[Any]
    bbox: tuple[float, float, float, float] | None = None
    area_sqm: float | None = None
    perimeter_m: float | None = None
    centroid: tuple[float, float] | None = None
    is_valid: bool = True
    validation_errors: list[str] = field(default_factory=list)


@dataclass
class GeoJSONFeature:
    """Parsed GeoJSON feature with properties."""

    type: Literal["Feature"] = "Feature"
    geometry: GeoJSONGeometry | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    id: str | int | None = None
    bbox: tuple[float, float, float, float] | None = None


@dataclass
class GeoJSONFeatureCollection:
    """Parsed GeoJSON feature collection."""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[GeoJSONFeature] = field(default_factory=list)
    bbox: tuple[float, float, float, float] | None = None
    crs: dict[str, Any] | None = None


# =============================================================================
# Parsing Functions
# =============================================================================


def parse_geojson_geometry(data: dict[str, Any]) -> GeoJSONGeometry:
    """
    Parse a GeoJSON geometry object.
    تحليل كائن هندسة GeoJSON.

    Args:
        data: GeoJSON geometry dictionary

    Returns:
        GeoJSONGeometry with parsed data and computed metrics
    """
    geom_type = data.get("type", "")
    coordinates = data.get("coordinates", [])

    if geom_type not in GEOJSON_TYPES:
        return GeoJSONGeometry(
            type=geom_type,
            coordinates=coordinates,
            is_valid=False,
            validation_errors=[f"Invalid geometry type: {geom_type}"],
        )

    # Calculate metrics based on geometry type
    geometry = GeoJSONGeometry(type=geom_type, coordinates=coordinates)

    try:
        if geom_type == "Polygon":
            geometry.bbox = calculate_bbox_polygon(coordinates)
            geometry.area_sqm = calculate_polygon_area_geodesic(coordinates)
            geometry.perimeter_m = calculate_polygon_perimeter(coordinates)
            geometry.centroid = calculate_polygon_centroid(coordinates)
        elif geom_type == "Point":
            lon, lat = coordinates[:2]
            geometry.bbox = (lon, lat, lon, lat)
            geometry.centroid = (lon, lat)
        elif geom_type == "LineString":
            geometry.bbox = calculate_bbox_linestring(coordinates)
            geometry.perimeter_m = calculate_linestring_length(coordinates)
            geometry.centroid = calculate_linestring_centroid(coordinates)
        elif geom_type == "MultiPolygon":
            geometry.bbox = calculate_bbox_multipolygon(coordinates)
            geometry.area_sqm = sum(calculate_polygon_area_geodesic(poly) for poly in coordinates)

        geometry.is_valid = True
    except Exception as e:
        geometry.is_valid = False
        geometry.validation_errors.append(str(e))
        logger.warning(f"Error parsing GeoJSON geometry: {e}")

    return geometry


def parse_geojson_feature(data: dict[str, Any]) -> GeoJSONFeature:
    """
    Parse a GeoJSON feature object.
    تحليل كائن ميزة GeoJSON.

    Args:
        data: GeoJSON feature dictionary

    Returns:
        GeoJSONFeature with parsed geometry and properties
    """
    geometry_data = data.get("geometry")
    geometry = parse_geojson_geometry(geometry_data) if geometry_data else None

    return GeoJSONFeature(
        type="Feature",
        geometry=geometry,
        properties=data.get("properties", {}),
        id=data.get("id"),
        bbox=geometry.bbox if geometry else None,
    )


def parse_geojson_feature_collection(data: dict[str, Any]) -> GeoJSONFeatureCollection:
    """
    Parse a GeoJSON feature collection.
    تحليل مجموعة ميزات GeoJSON.

    Args:
        data: GeoJSON feature collection dictionary

    Returns:
        GeoJSONFeatureCollection with parsed features
    """
    features = [parse_geojson_feature(f) for f in data.get("features", [])]

    # Calculate overall bounding box
    bbox = None
    if features:
        all_bboxes = [f.bbox for f in features if f.bbox]
        if all_bboxes:
            bbox = merge_bboxes(all_bboxes)

    return GeoJSONFeatureCollection(
        type="FeatureCollection",
        features=features,
        bbox=bbox,
        crs=data.get("crs"),
    )


# =============================================================================
# Creation Functions
# =============================================================================


def create_point(
    lon: float,
    lat: float,
    properties: dict[str, Any] | None = None,
    feature_id: str | int | None = None,
) -> dict[str, Any]:
    """
    Create a GeoJSON Point feature.
    إنشاء ميزة نقطة GeoJSON.

    Args:
        lon: Longitude
        lat: Latitude
        properties: Optional feature properties
        feature_id: Optional feature ID

    Returns:
        GeoJSON Feature dictionary
    """
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [round(lon, DEFAULT_PRECISION), round(lat, DEFAULT_PRECISION)],
        },
        "properties": properties or {},
    }
    if feature_id is not None:
        feature["id"] = feature_id
    return feature


def create_linestring(
    coordinates: list[tuple[float, float]],
    properties: dict[str, Any] | None = None,
    feature_id: str | int | None = None,
) -> dict[str, Any]:
    """
    Create a GeoJSON LineString feature.
    إنشاء ميزة خط GeoJSON.

    Args:
        coordinates: List of (lon, lat) tuples
        properties: Optional feature properties
        feature_id: Optional feature ID

    Returns:
        GeoJSON Feature dictionary
    """
    coords = [[round(lon, DEFAULT_PRECISION), round(lat, DEFAULT_PRECISION)] for lon, lat in coordinates]
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": coords,
        },
        "properties": properties or {},
    }
    if feature_id is not None:
        feature["id"] = feature_id
    return feature


def create_polygon(
    coordinates: list[tuple[float, float]],
    properties: dict[str, Any] | None = None,
    feature_id: str | int | None = None,
    ensure_closed: bool = True,
) -> dict[str, Any]:
    """
    Create a GeoJSON Polygon feature.
    إنشاء ميزة مضلع GeoJSON.

    Args:
        coordinates: List of (lon, lat) tuples forming the exterior ring
        properties: Optional feature properties
        feature_id: Optional feature ID
        ensure_closed: Ensure the ring is closed

    Returns:
        GeoJSON Feature dictionary
    """
    coords = [[round(lon, DEFAULT_PRECISION), round(lat, DEFAULT_PRECISION)] for lon, lat in coordinates]

    # Ensure the polygon is closed
    if ensure_closed and coords and coords[0] != coords[-1]:
        coords.append(coords[0])

    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [coords],  # Exterior ring
        },
        "properties": properties or {},
    }
    if feature_id is not None:
        feature["id"] = feature_id
    return feature


def create_feature_collection(
    features: list[dict[str, Any]],
    include_bbox: bool = True,
) -> dict[str, Any]:
    """
    Create a GeoJSON FeatureCollection.
    إنشاء مجموعة ميزات GeoJSON.

    Args:
        features: List of GeoJSON Feature dictionaries
        include_bbox: Calculate and include overall bounding box

    Returns:
        GeoJSON FeatureCollection dictionary
    """
    collection = {
        "type": "FeatureCollection",
        "features": features,
    }

    if include_bbox and features:
        bboxes = []
        for f in features:
            geom = f.get("geometry", {})
            coords = geom.get("coordinates", [])
            geom_type = geom.get("type", "")

            if geom_type == "Polygon" and coords:
                bboxes.append(calculate_bbox_polygon(coords))
            elif geom_type == "LineString" and coords:
                bboxes.append(calculate_bbox_linestring(coords))
            elif geom_type == "Point" and len(coords) >= 2:
                bboxes.append((coords[0], coords[1], coords[0], coords[1]))

        if bboxes:
            collection["bbox"] = list(merge_bboxes(bboxes))

    return collection


# =============================================================================
# Calculation Functions
# =============================================================================


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * math.pi / 180.0


def haversine_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calculate great-circle distance using Haversine formula.
    حساب المسافة الدائرية الكبرى باستخدام معادلة هافرساين.

    Args:
        lon1, lat1: First point coordinates
        lon2, lat2: Second point coordinates

    Returns:
        Distance in meters
    """
    lat1_rad = degrees_to_radians(lat1)
    lat2_rad = degrees_to_radians(lat2)
    delta_lat = degrees_to_radians(lat2 - lat1)
    delta_lon = degrees_to_radians(lon2 - lon1)

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_M * c


def calculate_polygon_area_geodesic(coordinates: list[list[Any]]) -> float:
    """
    Calculate polygon area using geodesic formula.
    حساب مساحة المضلع باستخدام المعادلة الجيوديسية.

    Args:
        coordinates: GeoJSON polygon coordinates (list of rings)

    Returns:
        Area in square meters
    """
    if not coordinates or not coordinates[0]:
        return 0.0

    # Use exterior ring only for now
    ring = coordinates[0]
    if len(ring) < 4:
        return 0.0

    n = len(ring) - 1  # Exclude closing point
    total = 0.0

    for i in range(n):
        j = (i + 1) % n
        lon1, lat1 = ring[i][:2]
        lon2, lat2 = ring[j][:2]

        lat1_rad = degrees_to_radians(lat1)
        lat2_rad = degrees_to_radians(lat2)
        delta_lon = degrees_to_radians(lon2 - lon1)

        total += delta_lon * (2 + math.sin(lat1_rad) + math.sin(lat2_rad))

    area = abs(total * EARTH_RADIUS_M**2 / 2)
    return area


def calculate_polygon_perimeter(coordinates: list[list[Any]]) -> float:
    """
    Calculate polygon perimeter.
    حساب محيط المضلع.

    Args:
        coordinates: GeoJSON polygon coordinates

    Returns:
        Perimeter in meters
    """
    if not coordinates or not coordinates[0]:
        return 0.0

    ring = coordinates[0]
    if len(ring) < 2:
        return 0.0

    perimeter = 0.0
    n = len(ring)

    for i in range(n):
        j = (i + 1) % n
        lon1, lat1 = ring[i][:2]
        lon2, lat2 = ring[j][:2]
        perimeter += haversine_distance(lon1, lat1, lon2, lat2)

    return perimeter


def calculate_polygon_centroid(coordinates: list[list[Any]]) -> tuple[float, float] | None:
    """
    Calculate polygon centroid.
    حساب مركز المضلع.

    Args:
        coordinates: GeoJSON polygon coordinates

    Returns:
        (longitude, latitude) tuple or None
    """
    if not coordinates or not coordinates[0]:
        return None

    ring = coordinates[0]
    if len(ring) < 3:
        return None

    # Simple average of coordinates (approximation)
    n = len(ring) - 1  # Exclude closing point
    sum_lon = sum(ring[i][0] for i in range(n))
    sum_lat = sum(ring[i][1] for i in range(n))

    return (sum_lon / n, sum_lat / n)


def calculate_linestring_length(coordinates: list[list[float]]) -> float:
    """
    Calculate LineString length.
    حساب طول الخط.

    Args:
        coordinates: GeoJSON LineString coordinates

    Returns:
        Length in meters
    """
    if len(coordinates) < 2:
        return 0.0

    length = 0.0
    for i in range(len(coordinates) - 1):
        lon1, lat1 = coordinates[i][:2]
        lon2, lat2 = coordinates[i + 1][:2]
        length += haversine_distance(lon1, lat1, lon2, lat2)

    return length


def calculate_linestring_centroid(coordinates: list[list[float]]) -> tuple[float, float] | None:
    """
    Calculate LineString centroid (midpoint).
    حساب مركز الخط.

    Args:
        coordinates: GeoJSON LineString coordinates

    Returns:
        (longitude, latitude) tuple or None
    """
    if not coordinates:
        return None

    n = len(coordinates)
    sum_lon = sum(c[0] for c in coordinates)
    sum_lat = sum(c[1] for c in coordinates)

    return (sum_lon / n, sum_lat / n)


# =============================================================================
# Bounding Box Functions
# =============================================================================


def calculate_bbox_polygon(coordinates: list[list[Any]]) -> tuple[float, float, float, float]:
    """
    Calculate bounding box for a polygon.
    حساب الإطار المحيط بالمضلع.

    Args:
        coordinates: GeoJSON polygon coordinates

    Returns:
        (min_lon, min_lat, max_lon, max_lat)
    """
    if not coordinates or not coordinates[0]:
        return (0.0, 0.0, 0.0, 0.0)

    ring = coordinates[0]
    lons = [c[0] for c in ring]
    lats = [c[1] for c in ring]

    return (min(lons), min(lats), max(lons), max(lats))


def calculate_bbox_linestring(coordinates: list[list[float]]) -> tuple[float, float, float, float]:
    """
    Calculate bounding box for a LineString.
    حساب الإطار المحيط بالخط.

    Args:
        coordinates: GeoJSON LineString coordinates

    Returns:
        (min_lon, min_lat, max_lon, max_lat)
    """
    if not coordinates:
        return (0.0, 0.0, 0.0, 0.0)

    lons = [c[0] for c in coordinates]
    lats = [c[1] for c in coordinates]

    return (min(lons), min(lats), max(lons), max(lats))


def calculate_bbox_multipolygon(
    coordinates: list[list[list[Any]]],
) -> tuple[float, float, float, float]:
    """
    Calculate bounding box for a MultiPolygon.
    حساب الإطار المحيط بالمضلع المتعدد.

    Args:
        coordinates: GeoJSON MultiPolygon coordinates

    Returns:
        (min_lon, min_lat, max_lon, max_lat)
    """
    if not coordinates:
        return (0.0, 0.0, 0.0, 0.0)

    bboxes = [calculate_bbox_polygon(poly) for poly in coordinates]
    return merge_bboxes(bboxes)


def merge_bboxes(
    bboxes: list[tuple[float, float, float, float]],
) -> tuple[float, float, float, float]:
    """
    Merge multiple bounding boxes into one.
    دمج عدة إطارات محيطة في واحد.

    Args:
        bboxes: List of bounding boxes

    Returns:
        Merged bounding box
    """
    if not bboxes:
        return (0.0, 0.0, 0.0, 0.0)

    min_lon = min(b[0] for b in bboxes)
    min_lat = min(b[1] for b in bboxes)
    max_lon = max(b[2] for b in bboxes)
    max_lat = max(b[3] for b in bboxes)

    return (min_lon, min_lat, max_lon, max_lat)


# =============================================================================
# Simplification Functions
# =============================================================================


def simplify_coordinates(
    coordinates: list[list[float]],
    tolerance_m: float = 1.0,
    preserve_topology: bool = True,
) -> list[list[float]]:
    """
    Simplify coordinates using Douglas-Peucker algorithm.
    تبسيط الإحداثيات باستخدام خوارزمية دوغلاس-بوكر.

    Args:
        coordinates: List of [lon, lat] coordinates
        tolerance_m: Simplification tolerance in meters
        preserve_topology: Ensure polygon closure is preserved

    Returns:
        Simplified coordinates
    """
    if len(coordinates) <= 4:
        return coordinates

    def perpendicular_distance(
        point: list[float],
        line_start: list[float],
        line_end: list[float],
    ) -> float:
        """Calculate perpendicular distance from point to line."""
        x, y = point[:2]
        x1, y1 = line_start[:2]
        x2, y2 = line_end[:2]

        if x1 == x2 and y1 == y2:
            return haversine_distance(x, y, x1, y1)

        # Project point onto line and calculate distance
        ref_lat = (y1 + y2) / 2
        lat_rad = degrees_to_radians(ref_lat)
        m_per_deg_lat = 111320.0
        m_per_deg_lon = 111320.0 * math.cos(lat_rad)

        dx = (x2 - x1) * m_per_deg_lon
        dy = (y2 - y1) * m_per_deg_lat

        numerator = abs((x - x1) * m_per_deg_lon * dy - (y - y1) * m_per_deg_lat * dx)
        denominator = math.sqrt(dx * dx + dy * dy)

        if denominator == 0:
            return haversine_distance(x, y, x1, y1)

        return numerator / denominator

    def douglas_peucker(points: list[list[float]], tolerance: float) -> list[list[float]]:
        """Recursive Douglas-Peucker implementation."""
        if len(points) <= 2:
            return points

        max_dist = 0.0
        max_idx = 0

        for i in range(1, len(points) - 1):
            dist = perpendicular_distance(points[i], points[0], points[-1])
            if dist > max_dist:
                max_dist = dist
                max_idx = i

        if max_dist > tolerance:
            left = douglas_peucker(points[: max_idx + 1], tolerance)
            right = douglas_peucker(points[max_idx:], tolerance)
            return left[:-1] + right
        else:
            return [points[0], points[-1]]

    # Check if closed ring
    is_closed = (
        preserve_topology
        and len(coordinates) >= 3
        and coordinates[0][0] == coordinates[-1][0]
        and coordinates[0][1] == coordinates[-1][1]
    )

    if is_closed:
        simplified = douglas_peucker(coordinates[:-1], tolerance_m)
        if simplified[-1] != simplified[0]:
            simplified.append(simplified[0])
    else:
        simplified = douglas_peucker(coordinates, tolerance_m)

    return simplified


def round_coordinates(
    coordinates: list[Any],
    precision: int = DEFAULT_PRECISION,
) -> list[Any]:
    """
    Round coordinate values to specified precision.
    تقريب قيم الإحداثيات إلى الدقة المحددة.

    Args:
        coordinates: GeoJSON coordinates (any depth)
        precision: Number of decimal places

    Returns:
        Coordinates with rounded values
    """
    if isinstance(coordinates, (int, float)):
        return round(coordinates, precision)
    elif isinstance(coordinates, list):
        return [round_coordinates(c, precision) for c in coordinates]
    return coordinates


# =============================================================================
# Conversion Functions
# =============================================================================


def geometry_to_wkt(geometry: dict[str, Any]) -> str:
    """
    Convert GeoJSON geometry to WKT format.
    تحويل هندسة GeoJSON إلى تنسيق WKT.

    Args:
        geometry: GeoJSON geometry object

    Returns:
        WKT string
    """
    geom_type = geometry.get("type", "")
    coords = geometry.get("coordinates", [])

    if geom_type == "Point":
        lon, lat = coords[:2]
        return f"POINT({lon} {lat})"

    elif geom_type == "LineString":
        points = ", ".join(f"{c[0]} {c[1]}" for c in coords)
        return f"LINESTRING({points})"

    elif geom_type == "Polygon":
        rings = []
        for ring in coords:
            points = ", ".join(f"{c[0]} {c[1]}" for c in ring)
            rings.append(f"({points})")
        return f"POLYGON({', '.join(rings)})"

    elif geom_type == "MultiPolygon":
        polygons = []
        for poly in coords:
            rings = []
            for ring in poly:
                points = ", ".join(f"{c[0]} {c[1]}" for c in ring)
                rings.append(f"({points})")
            polygons.append(f"({', '.join(rings)})")
        return f"MULTIPOLYGON({', '.join(polygons)})"

    return ""


def wkt_to_geometry(wkt: str) -> dict[str, Any] | None:
    """
    Convert WKT string to GeoJSON geometry (basic implementation).
    تحويل سلسلة WKT إلى هندسة GeoJSON.

    Args:
        wkt: Well-Known Text string

    Returns:
        GeoJSON geometry dict or None
    """
    import re

    wkt = wkt.strip()

    # Point
    point_match = re.match(r"POINT\s*\(\s*([\d.-]+)\s+([\d.-]+)\s*\)", wkt, re.I)
    if point_match:
        lon, lat = map(float, point_match.groups())
        return {"type": "Point", "coordinates": [lon, lat]}

    # LineString
    line_match = re.match(r"LINESTRING\s*\((.+)\)", wkt, re.I)
    if line_match:
        coords_str = line_match.group(1)
        coords = []
        for pair in coords_str.split(","):
            parts = pair.strip().split()
            if len(parts) >= 2:
                coords.append([float(parts[0]), float(parts[1])])
        return {"type": "LineString", "coordinates": coords}

    # Polygon (simple case)
    poly_match = re.match(r"POLYGON\s*\(\((.+)\)\)", wkt, re.I)
    if poly_match:
        coords_str = poly_match.group(1)
        coords = []
        for pair in coords_str.split(","):
            parts = pair.strip().split()
            if len(parts) >= 2:
                coords.append([float(parts[0]), float(parts[1])])
        return {"type": "Polygon", "coordinates": [coords]}

    return None


# =============================================================================
# Export all functions
# =============================================================================

__all__ = [
    # Data classes
    "GeoJSONGeometry",
    "GeoJSONFeature",
    "GeoJSONFeatureCollection",
    # Parsing
    "parse_geojson_geometry",
    "parse_geojson_feature",
    "parse_geojson_feature_collection",
    # Creation
    "create_point",
    "create_linestring",
    "create_polygon",
    "create_feature_collection",
    # Calculation
    "haversine_distance",
    "calculate_polygon_area_geodesic",
    "calculate_polygon_perimeter",
    "calculate_polygon_centroid",
    "calculate_linestring_length",
    "calculate_linestring_centroid",
    # Bounding box
    "calculate_bbox_polygon",
    "calculate_bbox_linestring",
    "calculate_bbox_multipolygon",
    "merge_bboxes",
    # Simplification
    "simplify_coordinates",
    "round_coordinates",
    # Conversion
    "geometry_to_wkt",
    "wkt_to_geometry",
    # Constants
    "EARTH_RADIUS_M",
    "DEFAULT_PRECISION",
    "GEOJSON_TYPES",
]
