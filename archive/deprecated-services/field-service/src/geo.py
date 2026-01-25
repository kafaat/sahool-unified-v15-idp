"""
SAHOOL Field Service - Geo-spatial Utilities
وظائف الحسابات الجغرافية
"""

import math
from typing import Any


def calculate_polygon_area(coordinates: list[list[list[float]]]) -> float:
    """
    حساب مساحة المضلع بالهكتار
    باستخدام صيغة Shoelace مع تحويل الإحداثيات

    Args:
        coordinates: إحداثيات المضلع [[lng, lat], ...]

    Returns:
        المساحة بالهكتار
    """
    if not coordinates or not coordinates[0]:
        return 0.0

    outer_ring = coordinates[0]
    n = len(outer_ring)
    if n < 4:
        return 0.0

    # تحويل الإحداثيات إلى متر باستخدام تقريب عند خط الاستواء
    # 1 درجة ≈ 111,320 متر عند خط الاستواء
    METERS_PER_DEGREE_LAT = 111320
    METERS_PER_DEGREE_LNG = 111320  # تقريب، يتغير حسب خط العرض

    # حساب مركز المضلع لتحديد معامل التحويل
    avg_lat = sum(p[1] for p in outer_ring) / n
    lng_scale = math.cos(math.radians(avg_lat))

    # تحويل إلى متر
    points_meters = []
    for lng, lat in outer_ring:
        x = lng * METERS_PER_DEGREE_LNG * lng_scale
        y = lat * METERS_PER_DEGREE_LAT
        points_meters.append((x, y))

    # صيغة Shoelace
    area = 0.0
    for i in range(n - 1):
        j = (i + 1) % (n - 1)
        area += points_meters[i][0] * points_meters[j][1]
        area -= points_meters[j][0] * points_meters[i][1]

    area = abs(area) / 2.0

    # تحويل من متر مربع إلى هكتار (1 هكتار = 10,000 متر مربع)
    return area / 10000.0


def calculate_centroid(coordinates: list[list[list[float]]]) -> tuple[float, float]:
    """
    حساب مركز المضلع

    Returns:
        (lat, lng)
    """
    if not coordinates or not coordinates[0]:
        return (0.0, 0.0)

    outer_ring = coordinates[0]
    n = len(outer_ring) - 1  # استبعاد نقطة الإغلاق

    if n < 1:
        return (0.0, 0.0)

    lng_sum = sum(p[0] for p in outer_ring[:n])
    lat_sum = sum(p[1] for p in outer_ring[:n])

    return (lat_sum / n, lng_sum / n)


def is_polygon_closed(coordinates: list[list[list[float]]]) -> bool:
    """التحقق من أن المضلع مغلق"""
    if not coordinates or not coordinates[0]:
        return False

    outer_ring = coordinates[0]
    if len(outer_ring) < 4:
        return False

    return outer_ring[0] == outer_ring[-1]


def validate_polygon(
    coordinates: list[list[list[float]]],
) -> tuple[bool, str | None]:
    """
    التحقق من صحة المضلع

    Returns:
        (is_valid, error_message)
    """
    if not coordinates:
        return False, "المضلع فارغ"

    if not coordinates[0]:
        return False, "الحلقة الخارجية فارغة"

    outer_ring = coordinates[0]

    if len(outer_ring) < 4:
        return False, "يجب أن تحتوي الحلقة على 4 نقاط على الأقل"

    if outer_ring[0] != outer_ring[-1]:
        return False, "المضلع غير مغلق"

    # التحقق من صحة الإحداثيات
    for point in outer_ring:
        if len(point) < 2:
            return False, "نقطة غير صالحة"
        lng, lat = point[0], point[1]
        if not (-180 <= lng <= 180):
            return False, f"خط الطول غير صالح: {lng}"
        if not (-90 <= lat <= 90):
            return False, f"خط العرض غير صالح: {lat}"

    return True, None


def check_polygon_overlap(
    polygon1: list[list[list[float]]], polygon2: list[list[list[float]]]
) -> tuple[bool, float]:
    """
    فحص تداخل مضلعين

    Returns:
        (has_overlap, overlap_area_hectares)

    ملاحظة: تنفيذ مبسط - للإنتاج استخدم Shapely
    """
    # تنفيذ مبسط: فحص إذا كان مركز أحدهما داخل الآخر
    center1 = calculate_centroid(polygon1)
    center2 = calculate_centroid(polygon2)

    is_center1_in_poly2 = point_in_polygon(center1, polygon2)
    is_center2_in_poly1 = point_in_polygon(center2, polygon1)

    if is_center1_in_poly2 or is_center2_in_poly1:
        # تقدير مساحة التداخل كنسبة من الأصغر
        area1 = calculate_polygon_area(polygon1)
        area2 = calculate_polygon_area(polygon2)
        estimated_overlap = min(area1, area2) * 0.5
        return True, estimated_overlap

    return False, 0.0


def point_in_polygon(point: tuple[float, float], polygon: list[list[list[float]]]) -> bool:
    """
    فحص إذا كانت النقطة داخل المضلع
    باستخدام خوارزمية Ray Casting

    Args:
        point: (lat, lng)
        polygon: إحداثيات المضلع
    """
    if not polygon or not polygon[0]:
        return False

    lat, lng = point
    outer_ring = polygon[0]
    n = len(outer_ring) - 1

    inside = False
    j = n - 1

    for i in range(n):
        lng_i, lat_i = outer_ring[i][0], outer_ring[i][1]
        lng_j, lat_j = outer_ring[j][0], outer_ring[j][1]

        if ((lat_i > lat) != (lat_j > lat)) and (
            lng < (lng_j - lng_i) * (lat - lat_i) / (lat_j - lat_i) + lng_i
        ):
            inside = not inside

        j = i

    return inside


def distance_between_points(point1: tuple[float, float], point2: tuple[float, float]) -> float:
    """
    حساب المسافة بين نقطتين بالكيلومتر
    باستخدام صيغة Haversine

    Args:
        point1: (lat, lng)
        point2: (lat, lng)
    """
    R = 6371  # نصف قطر الأرض بالكيلومتر

    lat1, lng1 = math.radians(point1[0]), math.radians(point1[1])
    lat2, lng2 = math.radians(point2[0]), math.radians(point2[1])

    dlat = lat2 - lat1
    dlng = lng2 - lng1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def polygon_to_kml(
    field_id: str,
    field_name: str,
    coordinates: list[list[list[float]]],
    description: str | None = None,
) -> str:
    """
    تحويل المضلع إلى صيغة KML

    Returns:
        نص KML
    """
    if not coordinates or not coordinates[0]:
        return ""

    outer_ring = coordinates[0]

    # تحويل الإحداثيات إلى صيغة KML (lng,lat,altitude)
    coord_str = " ".join(f"{p[0]},{p[1]},0" for p in outer_ring)

    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>SAHOOL Field Export</name>
    <Placemark>
      <name>{field_name}</name>
      <description>{description or f"Field ID: {field_id}"}</description>
      <Style>
        <LineStyle>
          <color>ff00ff00</color>
          <width>2</width>
        </LineStyle>
        <PolyStyle>
          <color>4000ff00</color>
        </PolyStyle>
      </Style>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>{coord_str}</coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>"""

    return kml


def polygon_to_geojson(
    field_id: str,
    field_name: str,
    coordinates: list[list[list[float]]],
    properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    تحويل المضلع إلى صيغة GeoJSON Feature

    Returns:
        GeoJSON Feature object
    """
    props = properties or {}
    props.update(
        {
            "field_id": field_id,
            "name": field_name,
        }
    )

    return {
        "type": "Feature",
        "properties": props,
        "geometry": {
            "type": "Polygon",
            "coordinates": coordinates,
        },
    }
