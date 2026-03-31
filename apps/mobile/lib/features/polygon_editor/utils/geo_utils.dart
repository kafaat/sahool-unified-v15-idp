import 'dart:math' as math;
import 'package:latlong2/latlong.dart';

/// أدوات حسابية جغرافية للمضلعات
/// GIS Utilities for Polygon Operations
class GeoUtils {
  static const double _earthRadius = 6371000; // meters

  // ─────────────────────────────────────────────────────────────────
  // Area Calculation (Shoelace Formula + Spherical)
  // ─────────────────────────────────────────────────────────────────

  /// حساب المساحة بالأمتار المربعة
  /// Calculate area in square meters using corrected spherical formula
  static double calculateAreaSqMeters(List<LatLng> polygon) {
    if (polygon.length < 3) return 0;

    // Shoelace formula on a sphere (Girard's theorem approximation)
    // More accurate for agricultural field sizes than previous formula
    double total = 0;
    final n = polygon.length;

    for (int i = 0; i < n; i++) {
      final j = (i + 1) % n;
      final lat1 = _toRadians(polygon[i].latitude);
      final lat2 = _toRadians(polygon[j].latitude);
      final dLng = _toRadians(polygon[j].longitude - polygon[i].longitude);

      total += dLng * (2 + math.sin(lat1) + math.sin(lat2));
    }

    total = total.abs() * _earthRadius * _earthRadius / 2;
    return total;
  }

  /// التحقق من تقاطع المضلع مع نفسه
  /// Check if polygon edges self-intersect (bowtie/figure-8)
  static bool isSelfIntersecting(List<LatLng> polygon) {
    if (polygon.length < 4) return false;
    final n = polygon.length;

    for (int i = 0; i < n; i++) {
      final i2 = (i + 1) % n;
      for (int j = i + 2; j < n; j++) {
        final j2 = (j + 1) % n;
        if (i == j2) continue; // adjacent edges share a vertex
        if (_segmentsIntersect(
          polygon[i], polygon[i2],
          polygon[j], polygon[j2],
        )) {
          return true;
        }
      }
    }
    return false;
  }

  /// Check if two line segments intersect
  static bool _segmentsIntersect(LatLng a, LatLng b, LatLng c, LatLng d) {
    double cross(LatLng o, LatLng p, LatLng q) =>
        (p.longitude - o.longitude) * (q.latitude - o.latitude) -
        (p.latitude - o.latitude) * (q.longitude - o.longitude);

    final d1 = cross(c, d, a);
    final d2 = cross(c, d, b);
    final d3 = cross(a, b, c);
    final d4 = cross(a, b, d);

    if (((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) &&
        ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))) {
      return true;
    }
    return false;
  }

  /// التحقق من صحة الإحداثيات
  static bool isValidCoordinate(LatLng point) {
    return point.latitude >= -90 &&
        point.latitude <= 90 &&
        point.longitude >= -180 &&
        point.longitude <= 180;
  }

  /// التحقق من صحة كل نقاط المضلع
  static bool areAllCoordinatesValid(List<LatLng> polygon) {
    return polygon.every(isValidCoordinate);
  }

  /// حساب المساحة بالهكتار
  static double calculateAreaHectares(List<LatLng> polygon) {
    return calculateAreaSqMeters(polygon) / 10000;
  }

  /// حساب المساحة بالفدان (اليمني = 4200 م²)
  static double calculateAreaFeddan(List<LatLng> polygon) {
    return calculateAreaSqMeters(polygon) / 4200;
  }

  /// حساب المساحة بالفدان المصري (4200.83 م²)
  static double calculateAreaFeddanEgypt(List<LatLng> polygon) {
    return calculateAreaSqMeters(polygon) / 4200.83;
  }

  // ─────────────────────────────────────────────────────────────────
  // Centroid Calculation
  // ─────────────────────────────────────────────────────────────────

  /// حساب مركز المضلع
  static LatLng? calculateCentroid(List<LatLng> polygon) {
    if (polygon.isEmpty) return null;

    double sumLat = 0, sumLng = 0;
    for (final p in polygon) {
      sumLat += p.latitude;
      sumLng += p.longitude;
    }

    return LatLng(sumLat / polygon.length, sumLng / polygon.length);
  }

  // ─────────────────────────────────────────────────────────────────
  // Distance Calculations
  // ─────────────────────────────────────────────────────────────────

  /// حساب المسافة بين نقطتين بالأمتار (Haversine)
  static double distanceMeters(LatLng a, LatLng b) {
    final lat1 = _toRadians(a.latitude);
    final lat2 = _toRadians(b.latitude);
    final dLat = _toRadians(b.latitude - a.latitude);
    final dLng = _toRadians(b.longitude - a.longitude);

    final h = _haversin(dLat) + math.cos(lat1) * math.cos(lat2) * _haversin(dLng);
    return 2 * _earthRadius * math.asin(math.sqrt(h));
  }

  /// حساب محيط المضلع بالأمتار
  static double calculatePerimeter(List<LatLng> polygon) {
    if (polygon.length < 2) return 0;

    double perimeter = 0;
    for (int i = 0; i < polygon.length; i++) {
      final next = (i + 1) % polygon.length;
      perimeter += distanceMeters(polygon[i], polygon[next]);
    }
    return perimeter;
  }

  // ─────────────────────────────────────────────────────────────────
  // Snap to Vertex / Edge
  // ─────────────────────────────────────────────────────────────────

  /// البحث عن أقرب نقطة (Snap to Vertex)
  /// Returns index of nearest vertex within threshold, or null
  static int? findNearestVertex(
    LatLng point,
    List<LatLng> vertices, {
    double thresholdMeters = 20,
  }) {
    if (vertices.isEmpty) return null;

    int? nearestIndex;
    double nearestDist = double.infinity;

    for (int i = 0; i < vertices.length; i++) {
      final dist = distanceMeters(point, vertices[i]);
      if (dist < nearestDist && dist <= thresholdMeters) {
        nearestDist = dist;
        nearestIndex = i;
      }
    }

    return nearestIndex;
  }

  /// Snap نقطة إلى أقرب vertex
  static LatLng? snapToVertex(
    LatLng point,
    List<LatLng> vertices, {
    double thresholdMeters = 20,
  }) {
    final index = findNearestVertex(point, vertices, thresholdMeters: thresholdMeters);
    return index != null ? vertices[index] : null;
  }

  /// البحث عن أقرب حافة (Snap to Edge)
  /// Returns (edgeIndex, projectedPoint) or null
  static ({int edgeIndex, LatLng point})? findNearestEdge(
    LatLng point,
    List<LatLng> polygon, {
    double thresholdMeters = 20,
  }) {
    if (polygon.length < 2) return null;

    int? nearestEdgeIndex;
    LatLng? nearestPoint;
    double nearestDist = double.infinity;

    for (int i = 0; i < polygon.length; i++) {
      final j = (i + 1) % polygon.length;
      final projected = _projectPointOnSegment(point, polygon[i], polygon[j]);
      final dist = distanceMeters(point, projected);

      if (dist < nearestDist && dist <= thresholdMeters) {
        nearestDist = dist;
        nearestEdgeIndex = i;
        nearestPoint = projected;
      }
    }

    if (nearestEdgeIndex != null && nearestPoint != null) {
      return (edgeIndex: nearestEdgeIndex, point: nearestPoint);
    }
    return null;
  }

  /// Project point onto line segment
  static LatLng _projectPointOnSegment(LatLng p, LatLng a, LatLng b) {
    final ax = a.longitude, ay = a.latitude;
    final bx = b.longitude, by = b.latitude;
    final px = p.longitude, py = p.latitude;

    final abx = bx - ax, aby = by - ay;
    final apx = px - ax, apy = py - ay;

    final ab2 = abx * abx + aby * aby;
    if (ab2 == 0) return a; // a and b are same point

    var t = (apx * abx + apy * aby) / ab2;
    t = t.clamp(0.0, 1.0);

    return LatLng(ay + t * aby, ax + t * abx);
  }

  // ─────────────────────────────────────────────────────────────────
  // Point in Polygon
  // ─────────────────────────────────────────────────────────────────

  /// هل النقطة داخل المضلع؟ (Ray Casting Algorithm)
  static bool isPointInPolygon(LatLng point, List<LatLng> polygon) {
    if (polygon.length < 3) return false;

    bool inside = false;
    final px = point.longitude, py = point.latitude;
    final n = polygon.length;

    for (int i = 0, j = n - 1; i < n; j = i++) {
      final xi = polygon[i].longitude, yi = polygon[i].latitude;
      final xj = polygon[j].longitude, yj = polygon[j].latitude;

      if (((yi > py) != (yj > py)) && (px < (xj - xi) * (py - yi) / (yj - yi) + xi)) {
        inside = !inside;
      }
    }

    return inside;
  }

  // ─────────────────────────────────────────────────────────────────
  // Bounding Box
  // ─────────────────────────────────────────────────────────────────

  /// حساب الإطار المحيط
  static ({LatLng min, LatLng max})? getBoundingBox(List<LatLng> polygon) {
    if (polygon.isEmpty) return null;

    double minLat = double.infinity, maxLat = -double.infinity;
    double minLng = double.infinity, maxLng = -double.infinity;

    for (final p in polygon) {
      if (p.latitude < minLat) minLat = p.latitude;
      if (p.latitude > maxLat) maxLat = p.latitude;
      if (p.longitude < minLng) minLng = p.longitude;
      if (p.longitude > maxLng) maxLng = p.longitude;
    }

    return (
      min: LatLng(minLat, minLng),
      max: LatLng(maxLat, maxLng),
    );
  }

  // ─────────────────────────────────────────────────────────────────
  // Helpers
  // ─────────────────────────────────────────────────────────────────

  static double _toRadians(double degrees) => degrees * math.pi / 180;

  static double _haversin(double theta) {
    final h = math.sin(theta / 2);
    return h * h;
  }
}

/// وحدات المساحة
enum AreaUnit {
  squareMeters('م²', 1),
  hectares('هكتار', 0.0001),
  feddanYemen('فدان', 1 / 4200),
  feddanEgypt('فدان مصري', 1 / 4200.83),
  acres('إيكر', 0.000247105);

  final String label;
  final double factor; // multiply sqm by this

  const AreaUnit(this.label, this.factor);

  double convert(double sqMeters) => sqMeters * factor;
}

// ─────────────────────────────────────────────────────────────────
// GeoJSON Conversion Utilities
// تحويل البيانات لصيغة GeoJSON للتواصل مع PostGIS
// ─────────────────────────────────────────────────────────────────

/// تحويل قائمة نقاط إلى GeoJSON Polygon
/// PostGIS يتوقع: [Longitude, Latitude] (عكس جوجل مابس)
/// ويجب أن تكون الحلقة مغلقة (أول نقطة = آخر نقطة)
Map<String, dynamic> toGeoJsonPolygon(List<LatLng> points) {
  if (points.isEmpty) {
    return {
      'type': 'Polygon',
      'coordinates': [[]]
    };
  }

  // تحويل إلى [longitude, latitude] format
  final coordinates = points.map((p) => [p.longitude, p.latitude]).toList();

  // إغلاق المضلع إذا لم يكن مغلقاً
  if (coordinates.isNotEmpty &&
      (coordinates.first[0] != coordinates.last[0] ||
       coordinates.first[1] != coordinates.last[1])) {
    coordinates.add(List.from(coordinates.first));
  }

  return {
    'type': 'Polygon',
    'coordinates': [coordinates] // مصفوفة داخل مصفوفة (لأن المضلع قد يحتوي ثقوباً)
  };
}

/// تحويل نقطة إلى GeoJSON Point
Map<String, dynamic> toGeoJsonPoint(LatLng point) {
  return {
    'type': 'Point',
    'coordinates': [point.longitude, point.latitude]
  };
}

/// تحويل GeoJSON Polygon إلى قائمة نقاط
List<LatLng> fromGeoJsonPolygon(Map<String, dynamic> geoJson) {
  if (geoJson['type'] != 'Polygon' || geoJson['coordinates'] == null) {
    return [];
  }

  final coordinates = geoJson['coordinates'] as List;
  if (coordinates.isEmpty) return [];

  final ring = coordinates[0] as List; // أول حلقة (الحدود الخارجية)

  return ring.map<LatLng>((coord) {
    final c = coord as List;
    return LatLng(c[1] as double, c[0] as double); // [lon, lat] -> LatLng(lat, lon)
  }).toList();
}

/// تحويل GeoJSON Point إلى LatLng
LatLng? fromGeoJsonPoint(Map<String, dynamic> geoJson) {
  if (geoJson['type'] != 'Point' || geoJson['coordinates'] == null) {
    return null;
  }

  final coords = geoJson['coordinates'] as List;
  if (coords.length < 2) return null;

  return LatLng(coords[1] as double, coords[0] as double);
}

/// إنشاء Feature كامل للحقل
Map<String, dynamic> createFieldGeoJsonFeature({
  required String id,
  required String name,
  required String cropType,
  required String userId,
  required List<LatLng> boundary,
  Map<String, dynamic>? metadata,
}) {
  return {
    'type': 'Feature',
    'id': id,
    'geometry': toGeoJsonPolygon(boundary),
    'properties': {
      'id': id,
      'name': name,
      'cropType': cropType,
      'userId': userId,
      'area_hectares': GeoUtils.calculateAreaHectares(boundary),
      'perimeter_meters': GeoUtils.calculatePerimeter(boundary),
      ...?metadata,
    }
  };
}

/// تحويل حقل Drift إلى Payload جاهز للسيرفر
Map<String, dynamic> fieldToApiPayload({
  required String id,
  required String name,
  required String cropType,
  required String userId,
  required List<LatLng> boundary,
  String? tenantId,
  String? irrigationType,
  String? soilType,
  DateTime? plantingDate,
  DateTime? expectedHarvest,
  Map<String, dynamic>? metadata,
}) {
  return {
    'id': id,
    'name': name,
    'cropType': cropType,
    'userId': userId,
    'tenantId': tenantId ?? 'default',
    'boundary': toGeoJsonPolygon(boundary),
    'coordinates': boundary.map((p) => [p.longitude, p.latitude]).toList(),
    if (irrigationType != null) 'irrigationType': irrigationType,
    if (soilType != null) 'soilType': soilType,
    if (plantingDate != null) 'plantingDate': plantingDate.toIso8601String(),
    if (expectedHarvest != null) 'expectedHarvest': expectedHarvest.toIso8601String(),
    if (metadata != null) 'metadata': metadata,
  };
}

