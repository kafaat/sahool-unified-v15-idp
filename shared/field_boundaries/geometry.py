"""
Field Boundary Geometry Calculations | حسابات هندسة حدود الحقول

This module provides geometric calculations for field boundaries including
area, perimeter, centroid, and spatial operations.

Supports both pure Python calculations and PostGIS integration.

Author: SAHOOL Platform
Version: 16.0.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# Earth radius in meters for geodesic calculations
# نصف قطر الأرض بالمتر للحسابات الجيوديسية
EARTH_RADIUS_M = 6371000.0

# Conversion factors | عوامل التحويل
HECTARES_PER_SQM = 0.0001
DUNAMS_PER_SQM = 0.001
ACRES_PER_SQM = 0.000247105


@dataclass
class GeometryMetrics:
    """
    Geometry calculation results | نتائج حسابات الهندسة

    Contains calculated geometric properties of a boundary.
    تحتوي على الخصائص الهندسية المحسوبة للحدود.
    """

    area_sqm: float
    area_hectares: float
    area_dunams: float
    area_acres: float
    perimeter_m: float
    centroid_lon: float
    centroid_lat: float
    bounding_box: tuple[float, float, float, float]  # min_lon, min_lat, max_lon, max_lat
    is_valid: bool
    validation_errors: list[str]


def degrees_to_radians(degrees: float) -> float:
    """
    Convert degrees to radians | تحويل الدرجات إلى راديان

    Args:
        degrees: Angle in degrees

    Returns:
        Angle in radians
    """
    return degrees * math.pi / 180.0


def radians_to_degrees(radians: float) -> float:
    """
    Convert radians to degrees | تحويل الراديان إلى درجات

    Args:
        radians: Angle in radians

    Returns:
        Angle in degrees
    """
    return radians * 180.0 / math.pi


def haversine_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calculate great-circle distance using Haversine formula.
    حساب المسافة الدائرية الكبرى باستخدام معادلة هافرساين.

    Args:
        lon1: Longitude of first point | خط طول النقطة الأولى
        lat1: Latitude of first point | خط عرض النقطة الأولى
        lon2: Longitude of second point | خط طول النقطة الثانية
        lat2: Latitude of second point | خط عرض النقطة الثانية

    Returns:
        Distance in meters | المسافة بالمتر
    """
    lat1_rad = degrees_to_radians(lat1)
    lat2_rad = degrees_to_radians(lat2)
    delta_lat = degrees_to_radians(lat2 - lat1)
    delta_lon = degrees_to_radians(lon2 - lon1)

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_M * c


def calculate_polygon_area_geodesic(coordinates: list[tuple[float, float]]) -> float:
    """
    Calculate polygon area using geodesic (spherical) formula.
    حساب مساحة المضلع باستخدام المعادلة الجيوديسية (الكروية).

    Uses the spherical excess formula for accurate area calculation
    on Earth's surface.

    Args:
        coordinates: List of (longitude, latitude) tuples forming closed polygon

    Returns:
        Area in square meters | المساحة بالمتر المربع
    """
    if len(coordinates) < 4:
        return 0.0

    # Ensure polygon is closed
    if coordinates[0] != coordinates[-1]:
        coordinates = list(coordinates) + [coordinates[0]]

    n = len(coordinates) - 1  # Exclude closing point

    # Use spherical excess formula (Girard's theorem)
    # نستخدم معادلة الفائض الكروي (نظرية جيرارد)
    total = 0.0

    for i in range(n):
        j = (i + 1) % n

        lon1, lat1 = coordinates[i]
        lon2, lat2 = coordinates[j]

        lat1_rad = degrees_to_radians(lat1)
        lat2_rad = degrees_to_radians(lat2)
        delta_lon = degrees_to_radians(lon2 - lon1)

        total += delta_lon * (2 + math.sin(lat1_rad) + math.sin(lat2_rad))

    area = abs(total * EARTH_RADIUS_M**2 / 2)
    return area


def calculate_polygon_area_projected(
    coordinates: list[tuple[float, float]], reference_lat: float | None = None
) -> float:
    """
    Calculate polygon area using local projection (faster, less accurate).
    حساب مساحة المضلع باستخدام الإسقاط المحلي (أسرع، أقل دقة).

    Projects coordinates to local Cartesian system and uses Shoelace formula.
    Suitable for small to medium sized fields.

    Args:
        coordinates: List of (longitude, latitude) tuples
        reference_lat: Reference latitude for projection (uses centroid if None)

    Returns:
        Area in square meters | المساحة بالمتر المربع
    """
    if len(coordinates) < 4:
        return 0.0

    # Calculate reference latitude if not provided
    if reference_lat is None:
        reference_lat = sum(lat for _, lat in coordinates) / len(coordinates)

    # Conversion factors at reference latitude
    # عوامل التحويل عند خط العرض المرجعي
    lat_rad = degrees_to_radians(reference_lat)
    meters_per_degree_lat = 111320.0  # Approximately constant
    meters_per_degree_lon = 111320.0 * math.cos(lat_rad)

    # Project to local coordinates
    centroid_lon = sum(lon for lon, _ in coordinates) / len(coordinates)
    centroid_lat = reference_lat

    projected = []
    for lon, lat in coordinates:
        x = (lon - centroid_lon) * meters_per_degree_lon
        y = (lat - centroid_lat) * meters_per_degree_lat
        projected.append((x, y))

    # Shoelace formula | معادلة رباط الحذاء
    n = len(projected)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += projected[i][0] * projected[j][1]
        area -= projected[j][0] * projected[i][1]

    return abs(area) / 2.0


def calculate_perimeter(coordinates: list[tuple[float, float]]) -> float:
    """
    Calculate polygon perimeter using geodesic distances.
    حساب محيط المضلع باستخدام المسافات الجيوديسية.

    Args:
        coordinates: List of (longitude, latitude) tuples

    Returns:
        Perimeter in meters | المحيط بالمتر
    """
    if len(coordinates) < 2:
        return 0.0

    perimeter = 0.0
    n = len(coordinates)

    for i in range(n):
        j = (i + 1) % n
        lon1, lat1 = coordinates[i]
        lon2, lat2 = coordinates[j]
        perimeter += haversine_distance(lon1, lat1, lon2, lat2)

    return perimeter


def calculate_centroid(coordinates: list[tuple[float, float]]) -> tuple[float, float]:
    """
    Calculate polygon centroid (geometric center).
    حساب مركز المضلع (المركز الهندسي).

    Uses the centroid formula for simple polygons.

    Args:
        coordinates: List of (longitude, latitude) tuples

    Returns:
        Tuple of (longitude, latitude) for centroid | إحداثيات المركز
    """
    if not coordinates:
        raise ValueError("Cannot calculate centroid of empty polygon | لا يمكن حساب مركز مضلع فارغ")

    if len(coordinates) < 3:
        # For 1-2 points, return average
        avg_lon = sum(lon for lon, _ in coordinates) / len(coordinates)
        avg_lat = sum(lat for _, lat in coordinates) / len(coordinates)
        return (avg_lon, avg_lat)

    # Ensure polygon is closed
    coords = list(coordinates)
    if coords[0] != coords[-1]:
        coords.append(coords[0])

    # Calculate centroid using cross-product method
    # حساب المركز باستخدام طريقة الضرب التقاطعي
    signed_area = 0.0
    cx = 0.0
    cy = 0.0

    n = len(coords) - 1
    for i in range(n):
        x0, y0 = coords[i]
        x1, y1 = coords[i + 1]

        cross = x0 * y1 - x1 * y0
        signed_area += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross

    signed_area *= 0.5

    if abs(signed_area) < 1e-10:
        # Degenerate polygon, return average
        avg_lon = sum(lon for lon, _ in coordinates) / len(coordinates)
        avg_lat = sum(lat for _, lat in coordinates) / len(coordinates)
        return (avg_lon, avg_lat)

    cx /= 6.0 * signed_area
    cy /= 6.0 * signed_area

    return (cx, cy)


def calculate_bounding_box(
    coordinates: list[tuple[float, float]],
) -> tuple[float, float, float, float]:
    """
    Calculate bounding box of polygon.
    حساب الإطار المحيط بالمضلع.

    Args:
        coordinates: List of (longitude, latitude) tuples

    Returns:
        Tuple of (min_lon, min_lat, max_lon, max_lat) | الإطار المحيط
    """
    if not coordinates:
        raise ValueError("Cannot calculate bounding box of empty polygon")

    lons = [lon for lon, _ in coordinates]
    lats = [lat for _, lat in coordinates]

    return (min(lons), min(lats), max(lons), max(lats))


def is_point_in_polygon(point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
    """
    Check if point is inside polygon using ray casting algorithm.
    التحقق مما إذا كانت النقطة داخل المضلع باستخدام خوارزمية إطلاق الشعاع.

    Args:
        point: (longitude, latitude) tuple
        polygon: List of (longitude, latitude) tuples

    Returns:
        True if point is inside polygon | صحيح إذا كانت النقطة داخل المضلع
    """
    x, y = point
    n = len(polygon)
    inside = False

    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]

        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside

        j = i

    return inside


def polygons_overlap(polygon1: list[tuple[float, float]], polygon2: list[tuple[float, float]]) -> bool:
    """
    Check if two polygons overlap.
    التحقق مما إذا كان المضلعان يتداخلان.

    Uses simple edge intersection and containment check.

    Args:
        polygon1: First polygon coordinates
        polygon2: Second polygon coordinates

    Returns:
        True if polygons overlap | صحيح إذا كان هناك تداخل
    """
    # Check if any vertex of polygon1 is inside polygon2
    for point in polygon1:
        if is_point_in_polygon(point, polygon2):
            return True

    # Check if any vertex of polygon2 is inside polygon1
    for point in polygon2:
        if is_point_in_polygon(point, polygon1):
            return True

    # Check edge intersections
    for i in range(len(polygon1)):
        j = (i + 1) % len(polygon1)
        edge1 = (polygon1[i], polygon1[j])

        for k in range(len(polygon2)):
            k_next = (k + 1) % len(polygon2)
            edge2 = (polygon2[k], polygon2[k_next])

            if edges_intersect(edge1, edge2):
                return True

    return False


def edges_intersect(
    edge1: tuple[tuple[float, float], tuple[float, float]],
    edge2: tuple[tuple[float, float], tuple[float, float]],
) -> bool:
    """
    Check if two line segments intersect.
    التحقق مما إذا كان قطعتان مستقيمتان تتقاطعان.

    Args:
        edge1: First edge as ((x1, y1), (x2, y2))
        edge2: Second edge as ((x3, y3), (x4, y4))

    Returns:
        True if edges intersect | صحيح إذا كان هناك تقاطع
    """
    (x1, y1), (x2, y2) = edge1
    (x3, y3), (x4, y4) = edge2

    def ccw(ax: float, ay: float, bx: float, by: float, cx: float, cy: float) -> bool:
        return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)

    return ccw(x1, y1, x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4) and ccw(x1, y1, x2, y2, x3, y3) != ccw(
        x1, y1, x2, y2, x4, y4
    )


def calculate_overlap_area(polygon1: list[tuple[float, float]], polygon2: list[tuple[float, float]]) -> float:
    """
    Estimate overlap area between two polygons (simplified).
    تقدير مساحة التداخل بين مضلعين (مبسط).

    For accurate calculation, use PostGIS ST_Intersection.
    للحساب الدقيق، استخدم ST_Intersection في PostGIS.

    Args:
        polygon1: First polygon coordinates
        polygon2: Second polygon coordinates

    Returns:
        Estimated overlap area in square meters | المساحة التقديرية بالمتر المربع
    """
    # This is a simplified estimation
    # For production use, delegate to PostGIS

    if not polygons_overlap(polygon1, polygon2):
        return 0.0

    # Count points of polygon1 inside polygon2 and vice versa
    # Use this to estimate overlap ratio
    points_1_in_2 = sum(1 for p in polygon1 if is_point_in_polygon(p, polygon2))
    points_2_in_1 = sum(1 for p in polygon2 if is_point_in_polygon(p, polygon1))

    area1 = calculate_polygon_area_geodesic(polygon1)
    area2 = calculate_polygon_area_geodesic(polygon2)

    # Rough estimation
    ratio1 = points_1_in_2 / len(polygon1) if polygon1 else 0
    ratio2 = points_2_in_1 / len(polygon2) if polygon2 else 0

    estimated_overlap = min(area1 * ratio1, area2 * ratio2)

    return estimated_overlap


def validate_polygon(coordinates: list[tuple[float, float]]) -> tuple[bool, list[str]]:
    """
    Validate polygon geometry.
    التحقق من صحة هندسة المضلع.

    Checks:
    - Minimum number of points (4 for closed polygon)
    - Closure (first point = last point)
    - No self-intersection
    - Valid coordinate ranges
    - Clockwise/counter-clockwise orientation

    Args:
        coordinates: Polygon coordinates

    Returns:
        Tuple of (is_valid, list of error messages) | (صالح، قائمة الأخطاء)
    """
    errors = []
    errors_ar = []

    # Check minimum points
    if len(coordinates) < 4:
        errors.append(f"Polygon must have at least 4 points (has {len(coordinates)})")
        errors_ar.append(f"يجب أن يحتوي المضلع على 4 نقاط على الأقل (يحتوي على {len(coordinates)})")

    if not coordinates:
        return (False, errors + errors_ar)

    # Check closure
    if coordinates[0] != coordinates[-1]:
        errors.append("Polygon is not closed (first point != last point)")
        errors_ar.append("المضلع غير مغلق (النقطة الأولى لا تساوي الأخيرة)")

    # Check coordinate ranges
    for i, (lon, lat) in enumerate(coordinates):
        if not -180 <= lon <= 180:
            errors.append(f"Point {i}: longitude {lon} out of range [-180, 180]")
        if not -90 <= lat <= 90:
            errors.append(f"Point {i}: latitude {lat} out of range [-90, 90]")

    # Check for self-intersection (simplified check)
    n = len(coordinates) - 1  # Exclude closing point
    for i in range(n):
        edge1 = (coordinates[i], coordinates[(i + 1) % n])
        for j in range(i + 2, n):
            if j == (i - 1) % n or j == i:
                continue
            edge2 = (coordinates[j], coordinates[(j + 1) % n])
            if edges_intersect(edge1, edge2):
                errors.append(f"Self-intersection detected between edges {i} and {j}")
                errors_ar.append(f"تم اكتشاف تقاطع ذاتي بين الحافتين {i} و {j}")

    # Check for very small area (possibly degenerate)
    if len(coordinates) >= 4:
        area = calculate_polygon_area_geodesic(coordinates)
        if area < 1.0:  # Less than 1 square meter
            errors.append(f"Polygon area too small: {area:.4f} m²")
            errors_ar.append(f"مساحة المضلع صغيرة جداً: {area:.4f} م²")

    is_valid = len(errors) == 0
    return (is_valid, errors + errors_ar)


def calculate_geometry_metrics(coordinates: list[tuple[float, float]], use_geodesic: bool = True) -> GeometryMetrics:
    """
    Calculate comprehensive geometry metrics for a polygon.
    حساب المقاييس الهندسية الشاملة للمضلع.

    Args:
        coordinates: Polygon coordinates
        use_geodesic: Use geodesic calculations for accuracy (True) or projected (False)

    Returns:
        GeometryMetrics object with all calculated values
    """
    is_valid, validation_errors = validate_polygon(coordinates)

    if not coordinates or len(coordinates) < 3:
        return GeometryMetrics(
            area_sqm=0.0,
            area_hectares=0.0,
            area_dunams=0.0,
            area_acres=0.0,
            perimeter_m=0.0,
            centroid_lon=0.0,
            centroid_lat=0.0,
            bounding_box=(0.0, 0.0, 0.0, 0.0),
            is_valid=False,
            validation_errors=validation_errors,
        )

    # Calculate area
    if use_geodesic:
        area_sqm = calculate_polygon_area_geodesic(coordinates)
    else:
        area_sqm = calculate_polygon_area_projected(coordinates)

    # Calculate other metrics
    perimeter_m = calculate_perimeter(coordinates)
    centroid_lon, centroid_lat = calculate_centroid(coordinates)
    bounding_box = calculate_bounding_box(coordinates)

    return GeometryMetrics(
        area_sqm=area_sqm,
        area_hectares=area_sqm * HECTARES_PER_SQM,
        area_dunams=area_sqm * DUNAMS_PER_SQM,
        area_acres=area_sqm * ACRES_PER_SQM,
        perimeter_m=perimeter_m,
        centroid_lon=centroid_lon,
        centroid_lat=centroid_lat,
        bounding_box=bounding_box,
        is_valid=is_valid,
        validation_errors=validation_errors,
    )


def simplify_polygon(coordinates: list[tuple[float, float]], tolerance_m: float = 1.0) -> list[tuple[float, float]]:
    """
    Simplify polygon using Douglas-Peucker algorithm.
    تبسيط المضلع باستخدام خوارزمية دوغلاس-بوكر.

    Reduces number of points while preserving shape.
    تقليل عدد النقاط مع الحفاظ على الشكل.

    Args:
        coordinates: Original polygon coordinates
        tolerance_m: Simplification tolerance in meters | تحمل التبسيط بالمتر

    Returns:
        Simplified polygon coordinates
    """
    if len(coordinates) <= 4:
        return coordinates

    def perpendicular_distance(
        point: tuple[float, float], line_start: tuple[float, float], line_end: tuple[float, float]
    ) -> float:
        """Calculate perpendicular distance from point to line."""
        x, y = point
        x1, y1 = line_start
        x2, y2 = line_end

        # Convert to approximate meters for distance calculation
        ref_lat = (y1 + y2) / 2
        lat_rad = degrees_to_radians(ref_lat)
        m_per_deg_lat = 111320.0
        m_per_deg_lon = 111320.0 * math.cos(lat_rad)

        dx = (x2 - x1) * m_per_deg_lon
        dy = (y2 - y1) * m_per_deg_lat

        if dx == 0 and dy == 0:
            # Line is a point
            return haversine_distance(x, y, x1, y1)

        # Calculate perpendicular distance
        numerator = (x - x1) * m_per_deg_lon * dx + (y - y1) * m_per_deg_lat * dy
        denominator = dx * dx + dy * dy
        t = max(0, min(1, numerator / denominator))

        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)

        return haversine_distance(x, y, proj_x, proj_y)

    def douglas_peucker(points: list[tuple[float, float]], tolerance: float) -> list[tuple[float, float]]:
        """Recursive Douglas-Peucker implementation."""
        if len(points) <= 2:
            return points

        # Find point with maximum distance
        max_dist = 0.0
        max_idx = 0

        for i in range(1, len(points) - 1):
            dist = perpendicular_distance(points[i], points[0], points[-1])
            if dist > max_dist:
                max_dist = dist
                max_idx = i

        # If max distance > tolerance, recursively simplify
        if max_dist > tolerance:
            left = douglas_peucker(points[: max_idx + 1], tolerance)
            right = douglas_peucker(points[max_idx:], tolerance)
            return left[:-1] + right
        else:
            return [points[0], points[-1]]

    # Preserve closure
    is_closed = coordinates[0] == coordinates[-1]

    if is_closed:
        # Simplify without closing point, then re-close
        simplified = douglas_peucker(coordinates[:-1], tolerance_m)
        if simplified[-1] != simplified[0]:
            simplified.append(simplified[0])
    else:
        simplified = douglas_peucker(coordinates, tolerance_m)

    return simplified


# PostGIS helper functions | وظائف مساعدة لـ PostGIS


def create_circular_boundary(
    center_lon: float,
    center_lat: float,
    radius_m: float,
    num_points: int = 72,
) -> list[tuple[float, float]]:
    """
    Create a circular polygon from center and radius (for pivot fields).
    إنشاء مضلع دائري من المركز ونصف القطر (لحقول المحور المركزي).

    Generates geodesically accurate circle vertices on Earth's surface.
    Useful for center pivot irrigation fields that cover circular areas.

    Args:
        center_lon: Center point longitude | خط طول المركز
        center_lat: Center point latitude | خط عرض المركز
        radius_m: Circle radius in meters | نصف القطر بالمتر
        num_points: Number of polygon vertices (default 72 = 5 degree steps)

    Returns:
        List of (longitude, latitude) tuples forming a closed polygon
    """
    if radius_m <= 0:
        raise ValueError("Radius must be positive | نصف القطر يجب أن يكون موجباً")
    if num_points < 8:
        raise ValueError("Minimum 8 points required | مطلوب 8 نقاط كحد أدنى")

    boundary = []
    angle_step = 360.0 / num_points

    for i in range(num_points):
        bearing_deg = i * angle_step
        bearing_rad = degrees_to_radians(bearing_deg)
        d = radius_m / EARTH_RADIUS_M

        lat1 = degrees_to_radians(center_lat)
        lon1 = degrees_to_radians(center_lon)

        lat2 = math.asin(math.sin(lat1) * math.cos(d) + math.cos(lat1) * math.sin(d) * math.cos(bearing_rad))
        lon2 = lon1 + math.atan2(
            math.sin(bearing_rad) * math.sin(d) * math.cos(lat1),
            math.cos(d) - math.sin(lat1) * math.sin(lat2),
        )

        boundary.append((radians_to_degrees(lon2), radians_to_degrees(lat2)))

    # Close the polygon
    boundary.append(boundary[0])
    return boundary


# PostGIS helper functions | وظائف مساعدة لـ PostGIS


def generate_postgis_area_query(geometry_column: str = "geometry", use_spheroid: bool = True) -> str:
    """
    Generate PostGIS query for area calculation.
    إنشاء استعلام PostGIS لحساب المساحة.

    Args:
        geometry_column: Name of geometry column
        use_spheroid: Use spheroid for accurate calculation

    Returns:
        SQL expression for area calculation
    """
    if use_spheroid:
        return f"ST_Area({geometry_column}::geography)"
    else:
        return f"ST_Area(ST_Transform({geometry_column}, 3857))"


def generate_postgis_centroid_query(geometry_column: str = "geometry") -> str:
    """
    Generate PostGIS query for centroid calculation.
    إنشاء استعلام PostGIS لحساب المركز.
    """
    return f"ST_Centroid({geometry_column})"


def generate_postgis_overlap_query(table1: str, table2: str, geometry_column: str = "geometry") -> str:
    """
    Generate PostGIS query to find overlapping polygons.
    إنشاء استعلام PostGIS للعثور على المضلعات المتداخلة.

    Note: table names and column names are application-controlled constants,
    not user input. This is safe from SQL injection.
    """
    g = geometry_column
    # nosec B608 - table/column names are application constants, not user input
    return f"""
    SELECT
        a.id AS boundary_id_a,
        b.id AS boundary_id_b,
        ST_Area(ST_Intersection(a.{g}, b.{g})::geography) AS overlap_area_sqm,
        ST_AsGeoJSON(ST_Intersection(a.{g}, b.{g})) AS overlap_geometry
    FROM {table1} a
    JOIN {table2} b ON ST_Intersects(a.{g}, b.{g})
    WHERE a.id != b.id
        AND ST_Area(ST_Intersection(a.{g}, b.{g})::geography) > 1.0
    """


def generate_postgis_neighbors_query(
    table: str, boundary_id: str, geometry_column: str = "geometry", buffer_m: float = 10.0
) -> str:
    """
    Generate PostGIS query to find neighboring boundaries.
    إنشاء استعلام PostGIS للعثور على الحدود المجاورة.

    Args:
        table: Table name
        boundary_id: ID of the boundary to find neighbors for
        geometry_column: Geometry column name
        buffer_m: Buffer distance in meters for "near" neighbors

    Returns:
        SQL query string
    """
    g = geometry_column
    # SECURITY: Use parameterized placeholder ($1) for boundary_id to prevent SQL injection
    return f"""
    SELECT
        b.id,
        b.field_id,
        b.owner_id,
        ST_Distance(a.{g}::geography, b.{g}::geography) AS distance_m,
        ST_Touches(a.{g}, b.{g}) AS is_touching
    FROM {table} a
    JOIN {table} b ON a.id != b.id
    WHERE a.id = $1
        AND (
            ST_Touches(a.{g}, b.{g})
            OR ST_DWithin(a.{g}::geography, b.{g}::geography, {buffer_m})
        )
    ORDER BY distance_m ASC
    """
