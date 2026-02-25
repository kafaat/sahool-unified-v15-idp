import 'dart:convert';
import 'dart:math' show cos, pi;
import 'package:drift/drift.dart';
import 'package:latlong2/latlong.dart';
import '../../utils/app_logger.dart';

/// GeoPolygon TypeConverter for Drift
///
/// Converts List<LatLng> <-> JSON String for SQLite storage
/// Uses GeoJSON coordinate order: [longitude, latitude]
///
/// Example:
///   Dart: [LatLng(15.369, 44.191), LatLng(15.370, 44.192)]
///   SQLite: "[[44.191,15.369],[44.192,15.370]]"
///
/// Includes validation:
/// - Latitude must be between -90 and 90
/// - Longitude must be between -180 and 180
/// - Invalid coordinates are logged and skipped
class GeoPolygonConverter extends TypeConverter<List<LatLng>, String> {
  const GeoPolygonConverter();

  /// Validate coordinate bounds
  static bool _isValidCoordinate(double lat, double lon) {
    return lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
  }

  /// Validate latitude
  static double _clampLatitude(double lat) {
    return lat.clamp(-90.0, 90.0);
  }

  /// Validate longitude
  static double _clampLongitude(double lon) {
    // Handle wrap-around for longitude
    while (lon > 180) {
      lon -= 360;
    }
    while (lon < -180) {
      lon += 360;
    }
    return lon;
  }

  @override
  List<LatLng> fromSql(String fromDb) {
    if (fromDb.isEmpty) return [];

    try {
      final dynamic decoded = jsonDecode(fromDb);
      if (decoded is! List) {
        AppLogger.w('Invalid polygon format - expected array',
            tag: 'GeoPolygonConverter');
        return [];
      }

      final List<LatLng> result = [];
      for (final point in decoded) {
        if (point is List && point.length >= 2) {
          // GeoJSON format: [longitude, latitude]
          final lon = (point[0] as num).toDouble();
          final lat = (point[1] as num).toDouble();

          // Validate coordinates
          if (!_isValidCoordinate(lat, lon)) {
            AppLogger.w(
              'Invalid coordinate bounds, clamping',
              tag: 'GeoPolygonConverter',
              data: {'lat': lat, 'lon': lon},
            );
          }

          result.add(LatLng(_clampLatitude(lat), _clampLongitude(lon)));
        }
      }
      return result;
    } catch (e, stackTrace) {
      AppLogger.e(
        'Failed to parse polygon',
        tag: 'GeoPolygonConverter',
        error: e,
        stackTrace: stackTrace,
      );
      return [];
    }
  }

  @override
  String toSql(List<LatLng> value) {
    if (value.isEmpty) return '[]';

    // Convert to GeoJSON coordinate order: [[lon, lat], [lon, lat], ...]
    // Also validate on write
    final jsonList = value.map((p) {
      final lat = _clampLatitude(p.latitude);
      final lon = _clampLongitude(p.longitude);
      return [lon, lat];
    }).toList();
    return jsonEncode(jsonList);
  }
}

/// GeoPoint TypeConverter for single point storage
///
/// Converts LatLng <-> JSON String for SQLite storage
/// Example:
///   Dart: LatLng(15.369, 44.191)
///   SQLite: "[44.191,15.369]"
///
/// Includes coordinate validation and bounds clamping
class GeoPointConverter extends TypeConverter<LatLng?, String?> {
  const GeoPointConverter();

  @override
  LatLng? fromSql(String? fromDb) {
    if (fromDb == null || fromDb.isEmpty) return null;

    try {
      final dynamic decoded = jsonDecode(fromDb);
      if (decoded is! List || decoded.length < 2) {
        AppLogger.w('Invalid point format - expected [lon, lat]',
            tag: 'GeoPointConverter');
        return null;
      }

      // GeoJSON format: [longitude, latitude]
      final lon = (decoded[0] as num).toDouble();
      final lat = (decoded[1] as num).toDouble();

      // Validate and clamp coordinates
      if (!GeoPolygonConverter._isValidCoordinate(lat, lon)) {
        AppLogger.w(
          'Invalid coordinate bounds, clamping',
          tag: 'GeoPointConverter',
          data: {'lat': lat, 'lon': lon},
        );
      }

      return LatLng(
        GeoPolygonConverter._clampLatitude(lat),
        GeoPolygonConverter._clampLongitude(lon),
      );
    } catch (e, stackTrace) {
      AppLogger.e(
        'Failed to parse point',
        tag: 'GeoPointConverter',
        error: e,
        stackTrace: stackTrace,
      );
      return null;
    }
  }

  @override
  String? toSql(LatLng? value) {
    if (value == null) return null;

    // Validate on write
    final lat = GeoPolygonConverter._clampLatitude(value.latitude);
    final lon = GeoPolygonConverter._clampLongitude(value.longitude);

    return jsonEncode([lon, lat]);
  }
}

/// Utility class for GeoJSON operations
///
/// Provides helper methods for working with GeoJSON data
class GeoJsonUtils {
  GeoJsonUtils._();

  /// Parse a GeoJSON Polygon to List<LatLng>
  ///
  /// GeoJSON Polygon format:
  /// ```json
  /// {
  ///   "type": "Polygon",
  ///   "coordinates": [[[lon, lat], [lon, lat], ...]]
  /// }
  /// ```
  static List<LatLng> parsePolygon(Map<String, dynamic> geoJson) {
    try {
      if (geoJson['type'] != 'Polygon') {
        AppLogger.w('Expected Polygon type',
            tag: 'GeoJsonUtils', data: {'type': geoJson['type']});
        return [];
      }

      final coordinates = geoJson['coordinates'];
      if (coordinates is! List || coordinates.isEmpty) {
        return [];
      }

      // GeoJSON polygon has an outer ring as the first element
      final outerRing = coordinates[0];
      if (outerRing is! List) {
        return [];
      }

      return outerRing.map<LatLng>((coord) {
        if (coord is List && coord.length >= 2) {
          final lon = (coord[0] as num).toDouble();
          final lat = (coord[1] as num).toDouble();
          return LatLng(
            GeoPolygonConverter._clampLatitude(lat),
            GeoPolygonConverter._clampLongitude(lon),
          );
        }
        return const LatLng(0, 0);
      }).toList();
    } catch (e) {
      AppLogger.e('Failed to parse GeoJSON polygon',
          tag: 'GeoJsonUtils', error: e);
      return [];
    }
  }

  /// Parse a GeoJSON Point to LatLng
  ///
  /// GeoJSON Point format:
  /// ```json
  /// {
  ///   "type": "Point",
  ///   "coordinates": [lon, lat]
  /// }
  /// ```
  static LatLng? parsePoint(Map<String, dynamic> geoJson) {
    try {
      if (geoJson['type'] != 'Point') {
        AppLogger.w('Expected Point type',
            tag: 'GeoJsonUtils', data: {'type': geoJson['type']});
        return null;
      }

      final coordinates = geoJson['coordinates'];
      if (coordinates is! List || coordinates.length < 2) {
        return null;
      }

      final lon = (coordinates[0] as num).toDouble();
      final lat = (coordinates[1] as num).toDouble();

      return LatLng(
        GeoPolygonConverter._clampLatitude(lat),
        GeoPolygonConverter._clampLongitude(lon),
      );
    } catch (e) {
      AppLogger.e('Failed to parse GeoJSON point',
          tag: 'GeoJsonUtils', error: e);
      return null;
    }
  }

  /// Convert List<LatLng> to GeoJSON Polygon
  static Map<String, dynamic> toGeoJsonPolygon(List<LatLng> points) {
    final coordinates = points
        .map((p) => [
              GeoPolygonConverter._clampLongitude(p.longitude),
              GeoPolygonConverter._clampLatitude(p.latitude),
            ])
        .toList();

    // Ensure polygon is closed (first point == last point)
    if (coordinates.isNotEmpty && coordinates.first != coordinates.last) {
      coordinates.add(coordinates.first);
    }

    return {
      'type': 'Polygon',
      'coordinates': [coordinates],
    };
  }

  /// Convert LatLng to GeoJSON Point
  static Map<String, dynamic> toGeoJsonPoint(LatLng point) {
    return {
      'type': 'Point',
      'coordinates': [
        GeoPolygonConverter._clampLongitude(point.longitude),
        GeoPolygonConverter._clampLatitude(point.latitude),
      ],
    };
  }

  /// Calculate centroid of a polygon
  static LatLng? calculateCentroid(List<LatLng> points) {
    if (points.isEmpty) return null;

    double sumLat = 0;
    double sumLon = 0;

    for (final point in points) {
      sumLat += point.latitude;
      sumLon += point.longitude;
    }

    return LatLng(sumLat / points.length, sumLon / points.length);
  }

  /// Calculate approximate area in hectares using Shoelace formula
  ///
  /// Note: This is an approximation and works best for small polygons
  /// away from the poles. For more accurate results, use a proper
  /// geodesic calculation library.
  static double calculateAreaHectares(List<LatLng> points) {
    if (points.length < 3) return 0;

    // Close the polygon if not already closed
    final closed = List<LatLng>.from(points);
    if (closed.first.latitude != closed.last.latitude ||
        closed.first.longitude != closed.last.longitude) {
      closed.add(closed.first);
    }

    // Shoelace formula for area in square degrees
    double area = 0;
    for (int i = 0; i < closed.length - 1; i++) {
      area += closed[i].longitude * closed[i + 1].latitude;
      area -= closed[i + 1].longitude * closed[i].latitude;
    }
    area = area.abs() / 2;

    // Convert square degrees to square meters (approximate)
    // 1 degree lat = ~111km, 1 degree lon varies by latitude
    final avgLat =
        closed.map((p) => p.latitude).reduce((a, b) => a + b) / closed.length;
    final latFactor = 111320.0; // meters per degree latitude
    final lonFactor =
        111320.0 * cos(avgLat * pi / 180); // meters per degree longitude

    final areaSquareMeters = area * latFactor * lonFactor;

    // Convert to hectares (1 hectare = 10,000 square meters)
    return areaSquareMeters / 10000;
  }
}
