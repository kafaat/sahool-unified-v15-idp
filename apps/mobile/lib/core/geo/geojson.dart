import 'dart:convert';
import 'dart:math' as math;
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

/// GeoJSON Utilities for PostGIS Integration
///
/// Converts Flutter map data to/from GeoJSON format
/// Compatible with PostGIS ST_GeomFromGeoJSON
class GeoJson {
  /// Create a GeoJSON Feature for a polygon field
  ///
  /// [boundary] - List of LatLng points defining the polygon
  /// [properties] - Additional properties (name, crop_type, etc.)
  ///
  /// Returns a GeoJSON Feature object ready for PostGIS
  static Map<String, dynamic> createPolygonFeature({
    required List<LatLng> boundary,
    required Map<String, dynamic> properties,
    String? id,
  }) {
    // Ensure polygon is closed (first point == last point)
    final closedBoundary = _ensureClosedPolygon(boundary);

    return {
      'type': 'Feature',
      if (id != null) 'id': id,
      'properties': properties,
      'geometry': {
        'type': 'Polygon',
        'coordinates': [
          // GeoJSON uses [longitude, latitude] order
          closedBoundary.map((p) => [p.longitude, p.latitude]).toList(),
        ],
      },
    };
  }

  /// Create a GeoJSON Feature for a point (e.g., field centroid)
  static Map<String, dynamic> createPointFeature({
    required LatLng point,
    required Map<String, dynamic> properties,
    String? id,
  }) {
    return {
      'type': 'Feature',
      if (id != null) 'id': id,
      'properties': properties,
      'geometry': {
        'type': 'Point',
        'coordinates': [point.longitude, point.latitude],
      },
    };
  }

  /// Create a GeoJSON FeatureCollection from multiple fields
  static Map<String, dynamic> createFeatureCollection(
    List<Map<String, dynamic>> features,
  ) {
    return {
      'type': 'FeatureCollection',
      'features': features,
    };
  }

  /// Parse a GeoJSON Polygon geometry to List<LatLng>
  static List<LatLng> parsePolygon(Map<String, dynamic> geometry) {
    if (geometry['type'] != 'Polygon') {
      throw ArgumentError('Expected Polygon geometry, got ${geometry['type']}');
    }

    final coordinates = geometry['coordinates'] as List;
    if (coordinates.isEmpty) return [];

    // Get the outer ring (first array)
    final outerRing = coordinates[0] as List;

    return outerRing.map((coord) {
      final c = coord as List;
      // GeoJSON: [longitude, latitude]
      return LatLng(
        (c[1] as num).toDouble(),
        (c[0] as num).toDouble(),
      );
    }).toList();
  }

  /// Parse a GeoJSON Point geometry to LatLng
  static LatLng parsePoint(Map<String, dynamic> geometry) {
    if (geometry['type'] != 'Point') {
      throw ArgumentError('Expected Point geometry, got ${geometry['type']}');
    }

    final coordinates = geometry['coordinates'] as List;
    return LatLng(
      (coordinates[1] as num).toDouble(),
      (coordinates[0] as num).toDouble(),
    );
  }

  /// Parse a GeoJSON Feature to extract geometry and properties
  static GeoJsonFeature parseFeature(Map<String, dynamic> feature) {
    final geometry = feature['geometry'] as Map<String, dynamic>;
    final properties = feature['properties'] as Map<String, dynamic>? ?? {};
    final id = feature['id']?.toString();

    return GeoJsonFeature(
      id: id,
      geometry: geometry,
      properties: properties,
    );
  }

  /// Calculate the centroid of a polygon
  static LatLng calculateCentroid(List<LatLng> polygon) {
    if (polygon.isEmpty) return const LatLng(0, 0);

    double sumLat = 0;
    double sumLng = 0;

    for (final point in polygon) {
      sumLat += point.latitude;
      sumLng += point.longitude;
    }

    return LatLng(
      sumLat / polygon.length,
      sumLng / polygon.length,
    );
  }

  /// Calculate the bounding box of a polygon
  static LatLngBounds calculateBounds(List<LatLng> polygon) {
    if (polygon.isEmpty) {
      return LatLngBounds(const LatLng(0, 0), const LatLng(0, 0));
    }

    double minLat = double.infinity;
    double maxLat = double.negativeInfinity;
    double minLng = double.infinity;
    double maxLng = double.negativeInfinity;

    for (final point in polygon) {
      minLat = math.min(minLat, point.latitude);
      maxLat = math.max(maxLat, point.latitude);
      minLng = math.min(minLng, point.longitude);
      maxLng = math.max(maxLng, point.longitude);
    }

    return LatLngBounds(
      LatLng(minLat, minLng),
      LatLng(maxLat, maxLng),
    );
  }

  /// Calculate area in hectares using Shoelace formula
  /// Approximate calculation suitable for agricultural fields
  static double calculateAreaHectares(List<LatLng> polygon) {
    if (polygon.length < 3) return 0;

    // Ensure polygon is closed
    final closed = _ensureClosedPolygon(polygon);

    // Calculate area using Shoelace formula with latitude correction
    double area = 0;
    final n = closed.length;

    for (int i = 0; i < n - 1; i++) {
      final p1 = closed[i];
      final p2 = closed[i + 1];

      // Convert to approximate meters using latitude
      final latCorrection = math.cos(p1.latitude * math.pi / 180);

      area += (p2.longitude - p1.longitude) *
          latCorrection *
          (p2.latitude + p1.latitude);
    }

    // Convert from degrees² to hectares
    // 1 degree ≈ 111,319 meters at equator
    final areaM2 = (area.abs() / 2) * 111319 * 111319;
    return areaM2 / 10000; // Convert m² to hectares
  }

  /// Ensure polygon is closed (first point == last point)
  static List<LatLng> _ensureClosedPolygon(List<LatLng> polygon) {
    if (polygon.isEmpty) return polygon;

    final first = polygon.first;
    final last = polygon.last;

    if (first.latitude != last.latitude || first.longitude != last.longitude) {
      return [...polygon, first];
    }

    return polygon;
  }

  /// Simplify polygon using Douglas-Peucker algorithm
  /// Useful for reducing data size before sync
  static List<LatLng> simplify(List<LatLng> polygon, double tolerance) {
    if (polygon.length <= 2) return polygon;
    return _douglasPeucker(polygon, tolerance);
  }

  static List<LatLng> _douglasPeucker(List<LatLng> points, double epsilon) {
    double dmax = 0;
    int index = 0;

    for (int i = 1; i < points.length - 1; i++) {
      final d = _perpendicularDistance(
        points[i],
        points.first,
        points.last,
      );
      if (d > dmax) {
        index = i;
        dmax = d;
      }
    }

    if (dmax > epsilon) {
      final left = _douglasPeucker(points.sublist(0, index + 1), epsilon);
      final right = _douglasPeucker(points.sublist(index), epsilon);
      return [...left.sublist(0, left.length - 1), ...right];
    } else {
      return [points.first, points.last];
    }
  }

  static double _perpendicularDistance(LatLng point, LatLng start, LatLng end) {
    final dx = end.longitude - start.longitude;
    final dy = end.latitude - start.latitude;

    final mag = math.sqrt(dx * dx + dy * dy);
    if (mag == 0) return 0;

    final u = ((point.longitude - start.longitude) * dx +
            (point.latitude - start.latitude) * dy) /
        (mag * mag);

    final closestX = start.longitude + u * dx;
    final closestY = start.latitude + u * dy;

    final ddx = point.longitude - closestX;
    final ddy = point.latitude - closestY;

    return math.sqrt(ddx * ddx + ddy * ddy);
  }
}

/// Parsed GeoJSON Feature
class GeoJsonFeature {
  final String? id;
  final Map<String, dynamic> geometry;
  final Map<String, dynamic> properties;

  const GeoJsonFeature({
    this.id,
    required this.geometry,
    required this.properties,
  });

  String get geometryType => geometry['type'] as String;

  bool get isPolygon => geometryType == 'Polygon';
  bool get isPoint => geometryType == 'Point';
  bool get isMultiPolygon => geometryType == 'MultiPolygon';

  List<LatLng>? get polygon => isPolygon ? GeoJson.parsePolygon(geometry) : null;
  LatLng? get point => isPoint ? GeoJson.parsePoint(geometry) : null;
}

/// Extension for easy GeoJSON conversion
extension LatLngListGeoJson on List<LatLng> {
  /// Convert to GeoJSON coordinates format [[lon, lat], ...]
  List<List<double>> toGeoJsonCoordinates() {
    return map((p) => [p.longitude, p.latitude]).toList();
  }

  /// Convert to GeoJSON Polygon geometry
  Map<String, dynamic> toGeoJsonPolygon() {
    return {
      'type': 'Polygon',
      'coordinates': [toGeoJsonCoordinates()],
    };
  }

  /// Calculate centroid
  LatLng get centroid => GeoJson.calculateCentroid(this);

  /// Calculate bounds
  LatLngBounds get bounds => GeoJson.calculateBounds(this);

  /// Calculate area in hectares
  double get areaHectares => GeoJson.calculateAreaHectares(this);
}
