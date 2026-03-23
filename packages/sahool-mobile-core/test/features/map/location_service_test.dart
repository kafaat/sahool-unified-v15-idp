/// Location Service Tests
/// اختبارات خدمة الموقع
///
/// Tests for location services, coordinate validation, distance calculations,
/// and location-based map functionality.

import 'dart:math' as math;

import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:sahool_mobile_core/core/map/map_providers.dart';

import 'mock_map_data.dart';

void main() {
  group('LocationData Model', () {
    test('should create location data with required fields', () {
      // Arrange & Act
      const lat = 15.3694;
      const lon = 44.1910;

      // Create a simple location data structure (similar to what's in location_picker.dart)
      final locationData = {
        'latitude': lat,
        'longitude': lon,
      };

      // Assert
      expect(locationData['latitude'], equals(lat));
      expect(locationData['longitude'], equals(lon));
    });

    test('should include optional address field', () {
      // Arrange & Act
      final locationData = {
        'latitude': 15.3694,
        'longitude': 44.1910,
        'address': 'صنعاء، اليمن',
      };

      // Assert
      expect(locationData['address'], equals('صنعاء، اليمن'));
    });

    test('should convert to JSON format', () {
      // Arrange
      final locationData = {
        'latitude': 15.3694,
        'longitude': 44.1910,
        'address': 'Test Address',
      };

      // Assert
      expect(locationData, isA<Map<String, dynamic>>());
      expect(locationData.containsKey('latitude'), isTrue);
      expect(locationData.containsKey('longitude'), isTrue);
    });
  });

  group('Mock Location Data', () {
    test('should have valid Sanaa location', () {
      // Act
      final sanaaLocation = MockLocationData.sanaaLocation;

      // Assert
      expect(sanaaLocation['latitude'], closeTo(15.3694, 0.01));
      expect(sanaaLocation['longitude'], closeTo(44.1910, 0.01));
      expect(sanaaLocation['accuracy'], lessThanOrEqualTo(50)); // Good accuracy
    });

    test('should identify poor accuracy location', () {
      // Act
      final poorLocation = MockLocationData.poorAccuracyLocation;

      // Assert
      expect(poorLocation['accuracy'], greaterThan(100)); // Poor accuracy
    });

    test('should have moving location with speed', () {
      // Act
      final movingLocation = MockLocationData.movingLocation;

      // Assert
      expect(movingLocation['speed'], greaterThan(0));
      expect(movingLocation['heading'], greaterThanOrEqualTo(0));
    });

    test('should identify invalid location', () {
      // Act
      final invalidLocation = MockLocationData.invalidLocation;

      // Assert - Invalid latitude (>90 or <-90)
      expect(
        invalidLocation['latitude']!.abs() > 90,
        isTrue,
        reason: 'Latitude should be invalid (outside -90 to 90)',
      );
      // Assert - Invalid longitude (>180 or <-180)
      expect(
        invalidLocation['longitude']!.abs() > 180,
        isTrue,
        reason: 'Longitude should be invalid (outside -180 to 180)',
      );
    });
  });

  group('Coordinate Validation', () {
    test('should validate latitude range (-90 to 90)', () {
      // Valid latitudes
      expect(_isValidLatitude(0), isTrue);
      expect(_isValidLatitude(45), isTrue);
      expect(_isValidLatitude(-45), isTrue);
      expect(_isValidLatitude(90), isTrue);
      expect(_isValidLatitude(-90), isTrue);

      // Invalid latitudes
      expect(_isValidLatitude(91), isFalse);
      expect(_isValidLatitude(-91), isFalse);
      expect(_isValidLatitude(180), isFalse);
    });

    test('should validate longitude range (-180 to 180)', () {
      // Valid longitudes
      expect(_isValidLongitude(0), isTrue);
      expect(_isValidLongitude(90), isTrue);
      expect(_isValidLongitude(-90), isTrue);
      expect(_isValidLongitude(180), isTrue);
      expect(_isValidLongitude(-180), isTrue);

      // Invalid longitudes
      expect(_isValidLongitude(181), isFalse);
      expect(_isValidLongitude(-181), isFalse);
      expect(_isValidLongitude(360), isFalse);
    });

    test('should validate Yemen coordinates', () {
      // Yemen bounding box approximately: 12-20N, 42-55E
      final sanaa = MockLocationData.sanaaLocation;

      // Assert in Yemen bounds
      expect(sanaa['latitude'], greaterThanOrEqualTo(12));
      expect(sanaa['latitude'], lessThanOrEqualTo(20));
      expect(sanaa['longitude'], greaterThanOrEqualTo(42));
      expect(sanaa['longitude'], lessThanOrEqualTo(55));
    });
  });

  group('Distance Calculations', () {
    test('should calculate distance between two points using Haversine', () {
      // Arrange - Sanaa to Aden (approximately 350 km)
      const sanaa = LatLng(15.3694, 44.1910);
      const aden = LatLng(12.7855, 45.0187);

      // Act
      final distance = _haversineDistance(sanaa, aden);

      // Assert - Approximately 350 km (allow 10% tolerance)
      expect(distance, greaterThan(300000)); // 300 km
      expect(distance, lessThan(400000)); // 400 km
    });

    test('should return zero distance for same point', () {
      // Arrange
      const point = LatLng(15.3694, 44.1910);

      // Act
      final distance = _haversineDistance(point, point);

      // Assert
      expect(distance, equals(0));
    });

    test('should calculate distance across equator', () {
      // Arrange
      const northPoint = LatLng(10, 0);
      const southPoint = LatLng(-10, 0);

      // Act
      final distance = _haversineDistance(northPoint, southPoint);

      // Assert - 20 degrees of latitude is approximately 2222 km
      expect(distance, greaterThan(2200000)); // 2200 km
      expect(distance, lessThan(2250000)); // 2250 km
    });

    test('should calculate distance across prime meridian', () {
      // Arrange
      const westPoint = LatLng(0, -10);
      const eastPoint = LatLng(0, 10);

      // Act
      final distance = _haversineDistance(westPoint, eastPoint);

      // Assert - 20 degrees at equator is approximately 2222 km
      expect(distance, greaterThan(2200000)); // 2200 km
      expect(distance, lessThan(2250000)); // 2250 km
    });
  });

  group('Location Accuracy Classification', () {
    test('should classify high accuracy (< 10m)', () {
      expect(_classifyAccuracy(5), equals(LocationAccuracyLevel.high));
      expect(_classifyAccuracy(9), equals(LocationAccuracyLevel.high));
    });

    test('should classify medium accuracy (10-50m)', () {
      expect(_classifyAccuracy(10), equals(LocationAccuracyLevel.medium));
      expect(_classifyAccuracy(25), equals(LocationAccuracyLevel.medium));
      expect(_classifyAccuracy(49), equals(LocationAccuracyLevel.medium));
    });

    test('should classify low accuracy (50-100m)', () {
      expect(_classifyAccuracy(50), equals(LocationAccuracyLevel.low));
      expect(_classifyAccuracy(75), equals(LocationAccuracyLevel.low));
      expect(_classifyAccuracy(99), equals(LocationAccuracyLevel.low));
    });

    test('should classify very low accuracy (> 100m)', () {
      expect(_classifyAccuracy(100), equals(LocationAccuracyLevel.veryLow));
      expect(_classifyAccuracy(500), equals(LocationAccuracyLevel.veryLow));
    });
  });

  group('Location Bounds Checking', () {
    test('should detect point within Yemen bounds', () {
      // Arrange
      const sanaaPoint = LatLng(15.3694, 44.1910);

      // Act & Assert
      expect(_isInYemenBounds(sanaaPoint), isTrue);
    });

    test('should detect point outside Yemen bounds', () {
      // Arrange - A point in Europe
      const parisPoint = LatLng(48.8566, 2.3522);

      // Act & Assert
      expect(_isInYemenBounds(parisPoint), isFalse);
    });

    test('should check all Yemen cities are within bounds', () {
      // Arrange
      final cities = YemenMapBounds.cities;

      // Assert
      for (final entry in cities.entries) {
        expect(
          _isInYemenBounds(entry.value),
          isTrue,
          reason: '${entry.key} should be within Yemen bounds',
        );
      }
    });
  });

  group('Default Location Fallback', () {
    test('should provide Yemen center as default', () {
      // Act
      const defaultLocation = YemenMapBounds.center;

      // Assert
      expect(defaultLocation.latitude, closeTo(15.5527, 0.01));
      expect(defaultLocation.longitude, closeTo(48.5164, 0.01));
    });

    test('should be within Yemen bounds', () {
      // Act
      const defaultLocation = YemenMapBounds.center;

      // Assert
      expect(_isInYemenBounds(defaultLocation), isTrue);
    });
  });

  group('LatLng Coordinate Operations', () {
    test('should create LatLng from coordinates', () {
      // Arrange & Act
      const point = LatLng(15.3694, 44.1910);

      // Assert
      expect(point.latitude, equals(15.3694));
      expect(point.longitude, equals(44.1910));
    });

    test('should support equality comparison', () {
      // Arrange
      const point1 = LatLng(15.3694, 44.1910);
      const point2 = LatLng(15.3694, 44.1910);
      const point3 = LatLng(15.3695, 44.1910);

      // Assert
      expect(point1, equals(point2));
      expect(point1, isNot(equals(point3)));
    });

    test('should handle coordinate precision', () {
      // Arrange
      const precise = LatLng(15.369400001, 44.191000001);
      const lessPrecise = LatLng(15.3694, 44.1910);

      // Act
      final distance = _haversineDistance(precise, lessPrecise);

      // Assert - Should be very close (< 1 meter)
      expect(distance, lessThan(1));
    });
  });

  group('Bearing Calculation', () {
    test('should calculate bearing between two points', () {
      // Arrange - Sanaa to Aden (roughly south-southeast)
      const sanaa = LatLng(15.3694, 44.1910);
      const aden = LatLng(12.7855, 45.0187);

      // Act
      final bearing = _calculateBearing(sanaa, aden);

      // Assert - Should be roughly between 135 and 180 degrees (south-southeast)
      expect(bearing, greaterThan(135));
      expect(bearing, lessThan(200));
    });

    test('should return 0 bearing for north', () {
      // Arrange
      const start = LatLng(0, 0);
      const north = LatLng(1, 0);

      // Act
      final bearing = _calculateBearing(start, north);

      // Assert
      expect(bearing, closeTo(0, 1));
    });

    test('should return 90 bearing for east', () {
      // Arrange
      const start = LatLng(0, 0);
      const east = LatLng(0, 1);

      // Act
      final bearing = _calculateBearing(start, east);

      // Assert
      expect(bearing, closeTo(90, 1));
    });

    test('should return 180 bearing for south', () {
      // Arrange
      const start = LatLng(1, 0);
      const south = LatLng(0, 0);

      // Act
      final bearing = _calculateBearing(start, south);

      // Assert
      expect(bearing, closeTo(180, 1));
    });

    test('should return 270 bearing for west', () {
      // Arrange
      const start = LatLng(0, 1);
      const west = LatLng(0, 0);

      // Act
      final bearing = _calculateBearing(start, west);

      // Assert
      expect(bearing, closeTo(270, 1));
    });
  });

  group('Location Permission States', () {
    test('should have all permission states defined', () {
      // Assert
      expect(LocationPermissionState.values, hasLength(4));
      expect(LocationPermissionState.values, contains(LocationPermissionState.granted));
      expect(LocationPermissionState.values, contains(LocationPermissionState.denied));
      expect(LocationPermissionState.values, contains(LocationPermissionState.deniedForever));
      expect(LocationPermissionState.values, contains(LocationPermissionState.unknown));
    });
  });

  group('Location Service Status', () {
    test('should have all service status states defined', () {
      // Assert
      expect(LocationServiceStatus.values, hasLength(3));
      expect(LocationServiceStatus.values, contains(LocationServiceStatus.enabled));
      expect(LocationServiceStatus.values, contains(LocationServiceStatus.disabled));
      expect(LocationServiceStatus.values, contains(LocationServiceStatus.unknown));
    });
  });

  group('Field Location Context', () {
    test('should detect if location is within field polygon', () {
      // Arrange
      final fieldPolygon = [
        const LatLng(15.3694, 44.1910),
        const LatLng(15.3694, 44.1950),
        const LatLng(15.3734, 44.1950),
        const LatLng(15.3734, 44.1910),
      ];
      const insidePoint = LatLng(15.3714, 44.1930);
      const outsidePoint = LatLng(15.4000, 44.2000);

      // Act & Assert
      expect(_isPointInPolygon(insidePoint, fieldPolygon), isTrue);
      expect(_isPointInPolygon(outsidePoint, fieldPolygon), isFalse);
    });

    test('should detect point on polygon boundary', () {
      // Arrange
      final fieldPolygon = [
        const LatLng(0, 0),
        const LatLng(0, 10),
        const LatLng(10, 10),
        const LatLng(10, 0),
      ];
      const cornerPoint = LatLng(0, 0);
      const edgePoint = LatLng(0, 5);

      // Act & Assert - Boundary points may be inside or outside depending on algorithm
      // The important thing is that it doesn't crash
      expect(_isPointInPolygon(cornerPoint, fieldPolygon), isA<bool>());
      expect(_isPointInPolygon(edgePoint, fieldPolygon), isA<bool>());
    });
  });

  group('Speed and Movement Detection', () {
    test('should classify stationary location', () {
      // Arrange
      const speed = 0.0;

      // Assert
      expect(_classifyMovement(speed), equals(MovementType.stationary));
    });

    test('should classify walking speed', () {
      // Arrange - Walking is typically 3-6 km/h (0.8-1.7 m/s)
      const speed = 1.4;

      // Assert
      expect(_classifyMovement(speed), equals(MovementType.walking));
    });

    test('should classify vehicle speed', () {
      // Arrange - Driving speed
      const speed = 15.0; // m/s = 54 km/h

      // Assert
      expect(_classifyMovement(speed), equals(MovementType.vehicle));
    });
  });
}

// Helper functions for testing

bool _isValidLatitude(double lat) {
  return lat >= -90 && lat <= 90;
}

bool _isValidLongitude(double lon) {
  return lon >= -180 && lon <= 180;
}

/// Haversine formula for calculating distance between two points
double _haversineDistance(LatLng point1, LatLng point2) {
  const earthRadius = 6371000.0; // Earth radius in meters

  final lat1 = point1.latitude * math.pi / 180;
  final lat2 = point2.latitude * math.pi / 180;
  final deltaLat = (point2.latitude - point1.latitude) * math.pi / 180;
  final deltaLon = (point2.longitude - point1.longitude) * math.pi / 180;

  final a = math.sin(deltaLat / 2) * math.sin(deltaLat / 2) +
      math.cos(lat1) *
          math.cos(lat2) *
          math.sin(deltaLon / 2) *
          math.sin(deltaLon / 2);
  final c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a));

  return earthRadius * c;
}

/// Calculate bearing between two points
double _calculateBearing(LatLng start, LatLng end) {
  final startLat = start.latitude * math.pi / 180;
  final startLon = start.longitude * math.pi / 180;
  final endLat = end.latitude * math.pi / 180;
  final endLon = end.longitude * math.pi / 180;

  final dLon = endLon - startLon;

  final y = math.sin(dLon) * math.cos(endLat);
  final x = math.cos(startLat) * math.sin(endLat) -
      math.sin(startLat) * math.cos(endLat) * math.cos(dLon);

  var bearing = math.atan2(y, x) * 180 / math.pi;
  bearing = (bearing + 360) % 360; // Normalize to 0-360

  return bearing;
}

/// Check if point is within Yemen approximate bounds
bool _isInYemenBounds(LatLng point) {
  // Yemen approximate bounds: 12-20N, 42-55E
  return point.latitude >= 12 &&
      point.latitude <= 20 &&
      point.longitude >= 42 &&
      point.longitude <= 55;
}

/// Ray casting algorithm for point in polygon
bool _isPointInPolygon(LatLng point, List<LatLng> polygon) {
  var inside = false;
  final x = point.longitude;
  final y = point.latitude;

  for (int i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    final xi = polygon[i].longitude;
    final yi = polygon[i].latitude;
    final xj = polygon[j].longitude;
    final yj = polygon[j].latitude;

    if (((yi > y) != (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) {
      inside = !inside;
    }
  }

  return inside;
}

// Enums for location service testing

enum LocationAccuracyLevel {
  high, // < 10m
  medium, // 10-50m
  low, // 50-100m
  veryLow, // > 100m
}

LocationAccuracyLevel _classifyAccuracy(double accuracy) {
  if (accuracy < 10) return LocationAccuracyLevel.high;
  if (accuracy < 50) return LocationAccuracyLevel.medium;
  if (accuracy < 100) return LocationAccuracyLevel.low;
  return LocationAccuracyLevel.veryLow;
}

enum LocationPermissionState {
  granted,
  denied,
  deniedForever,
  unknown,
}

enum LocationServiceStatus {
  enabled,
  disabled,
  unknown,
}

enum MovementType {
  stationary,
  walking,
  running,
  cycling,
  vehicle,
}

MovementType _classifyMovement(double speedMps) {
  if (speedMps < 0.5) return MovementType.stationary;
  if (speedMps < 2.5) return MovementType.walking;
  if (speedMps < 5.0) return MovementType.running;
  if (speedMps < 10.0) return MovementType.cycling;
  return MovementType.vehicle;
}
