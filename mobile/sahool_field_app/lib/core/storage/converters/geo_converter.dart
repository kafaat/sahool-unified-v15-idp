import 'dart:convert';
import 'package:drift/drift.dart';
import 'package:latlong2/latlong.dart';

/// GeoPolygon TypeConverter for Drift
///
/// Converts List<LatLng> <-> JSON String for SQLite storage
/// Uses GeoJSON coordinate order: [longitude, latitude]
///
/// Example:
///   Dart: [LatLng(15.369, 44.191), LatLng(15.370, 44.192)]
///   SQLite: "[[44.191,15.369],[44.192,15.370]]"
class GeoPolygonConverter extends TypeConverter<List<LatLng>, String> {
  const GeoPolygonConverter();

  @override
  List<LatLng> fromSql(String fromDb) {
    if (fromDb.isEmpty) return [];

    try {
      final List<dynamic> jsonList = jsonDecode(fromDb);
      return jsonList.map((point) {
        if (point is List && point.length >= 2) {
          // GeoJSON format: [longitude, latitude]
          final lon = (point[0] as num).toDouble();
          final lat = (point[1] as num).toDouble();
          return LatLng(lat, lon);
        }
        return const LatLng(0, 0);
      }).toList();
    } catch (e) {
      print('GeoPolygonConverter: Failed to parse polygon: $e');
      return [];
    }
  }

  @override
  String toSql(List<LatLng> value) {
    if (value.isEmpty) return '[]';

    // Convert to GeoJSON coordinate order: [[lon, lat], [lon, lat], ...]
    final jsonList = value.map((p) => [p.longitude, p.latitude]).toList();
    return jsonEncode(jsonList);
  }
}

/// GeoPoint TypeConverter for single point storage
///
/// Converts LatLng <-> JSON String for SQLite storage
/// Example:
///   Dart: LatLng(15.369, 44.191)
///   SQLite: "[44.191,15.369]"
class GeoPointConverter extends TypeConverter<LatLng?, String?> {
  const GeoPointConverter();

  @override
  LatLng? fromSql(String? fromDb) {
    if (fromDb == null || fromDb.isEmpty) return null;

    try {
      final List<dynamic> point = jsonDecode(fromDb);
      if (point.length >= 2) {
        // GeoJSON format: [longitude, latitude]
        final lon = (point[0] as num).toDouble();
        final lat = (point[1] as num).toDouble();
        return LatLng(lat, lon);
      }
      return null;
    } catch (e) {
      print('GeoPointConverter: Failed to parse point: $e');
      return null;
    }
  }

  @override
  String? toSql(LatLng? value) {
    if (value == null) return null;
    return jsonEncode([value.longitude, value.latitude]);
  }
}

/// GeoBounds TypeConverter for bounding box storage
///
/// Converts LatLngBounds <-> JSON String
/// Example:
///   Dart: LatLngBounds(sw, ne)
///   SQLite: "[[sw_lon,sw_lat],[ne_lon,ne_lat]]"
class GeoBoundsConverter extends TypeConverter<LatLngBounds?, String?> {
  const GeoBoundsConverter();

  @override
  LatLngBounds? fromSql(String? fromDb) {
    if (fromDb == null || fromDb.isEmpty) return null;

    try {
      final List<dynamic> bounds = jsonDecode(fromDb);
      if (bounds.length >= 2) {
        final sw = bounds[0] as List;
        final ne = bounds[1] as List;
        return LatLngBounds(
          LatLng((sw[1] as num).toDouble(), (sw[0] as num).toDouble()),
          LatLng((ne[1] as num).toDouble(), (ne[0] as num).toDouble()),
        );
      }
      return null;
    } catch (e) {
      print('GeoBoundsConverter: Failed to parse bounds: $e');
      return null;
    }
  }

  @override
  String? toSql(LatLngBounds? value) {
    if (value == null) return null;
    return jsonEncode([
      [value.southWest.longitude, value.southWest.latitude],
      [value.northEast.longitude, value.northEast.latitude],
    ]);
  }
}
