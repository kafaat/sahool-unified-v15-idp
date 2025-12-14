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
  /// Calculate area in square meters using spherical excess formula
  static double calculateAreaSqMeters(List<LatLng> polygon) {
    if (polygon.length < 3) return 0;

    // Use spherical excess formula for accurate geodetic area
    double total = 0;
    final n = polygon.length;

    for (int i = 0; i < n; i++) {
      final j = (i + 1) % n;
      final k = (i + 2) % n;

      total += _toRadians(polygon[j].longitude - polygon[i].longitude) *
          (2 + math.sin(_toRadians(polygon[i].latitude)) +
              math.sin(_toRadians(polygon[j].latitude)));
    }

    total = total.abs() * _earthRadius * _earthRadius / 2;
    return total;
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
