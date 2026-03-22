/// GeoJSON Parser Tests
/// اختبارات محلل GeoJSON
///
/// Tests for GeoJSON parsing, creation, and coordinate transformations.
/// Compatible with PostGIS integration.
library;

import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:sahool_field_app/core/geo/geojson.dart';

import 'mock_map_data.dart';

void main() {
  group('GeoJson - Polygon Feature Creation', () {
    test('should create valid polygon feature with properties', () {
      // Arrange
      final boundary = [
        const LatLng(15.3694, 44.1910),
        const LatLng(15.3694, 44.1950),
        const LatLng(15.3734, 44.1950),
        const LatLng(15.3734, 44.1910),
      ];
      final properties = {
        'name': 'حقل القمح',
        'crop_type': 'wheat',
        'area_hectares': 5.2,
      };

      // Act
      final feature = GeoJson.createPolygonFeature(
        boundary: boundary,
        properties: properties,
        id: 'field-001',
      );

      // Assert
      expect(feature['type'], equals('Feature'));
      expect(feature['id'], equals('field-001'));
      expect(feature['properties'], equals(properties));
      expect(feature['geometry']['type'], equals('Polygon'));

      final coordinates = feature['geometry']['coordinates'][0] as List;
      expect(coordinates.length, equals(5)); // Closed polygon (4 points + 1)

      // Verify GeoJSON coordinate order (longitude, latitude)
      expect(coordinates[0][0], equals(44.1910)); // longitude
      expect(coordinates[0][1], equals(15.3694)); // latitude
    });

    test('should automatically close polygon if not closed', () {
      // Arrange - Open polygon (first != last)
      final openBoundary = [
        const LatLng(15.3694, 44.1910),
        const LatLng(15.3694, 44.1950),
        const LatLng(15.3734, 44.1950),
        const LatLng(15.3734, 44.1910),
      ];

      // Act
      final feature = GeoJson.createPolygonFeature(
        boundary: openBoundary,
        properties: {},
      );

      // Assert
      final coordinates = feature['geometry']['coordinates'][0] as List;
      final firstPoint = coordinates.first;
      final lastPoint = coordinates.last;
      expect(firstPoint[0], equals(lastPoint[0])); // Same longitude
      expect(firstPoint[1], equals(lastPoint[1])); // Same latitude
    });

    test('should handle already closed polygon', () {
      // Arrange - Already closed polygon
      final closedBoundary = [
        const LatLng(15.3694, 44.1910),
        const LatLng(15.3694, 44.1950),
        const LatLng(15.3734, 44.1950),
        const LatLng(15.3734, 44.1910),
        const LatLng(15.3694, 44.1910), // Already closed
      ];

      // Act
      final feature = GeoJson.createPolygonFeature(
        boundary: closedBoundary,
        properties: {},
      );

      // Assert
      final coordinates = feature['geometry']['coordinates'][0] as List;
      expect(coordinates.length, equals(5)); // Should not add extra point
    });

    test('should create feature without id when not provided', () {
      // Arrange
      final boundary = [const LatLng(15.3694, 44.1910)];

      // Act
      final feature = GeoJson.createPolygonFeature(
        boundary: boundary,
        properties: {},
      );

      // Assert
      expect(feature.containsKey('id'), isFalse);
    });
  });

  group('GeoJson - Point Feature Creation', () {
    test('should create valid point feature', () {
      // Arrange
      const point = LatLng(15.3694, 44.1910);
      final properties = {'name': 'مركز الحقل', 'type': 'centroid'};

      // Act
      final feature = GeoJson.createPointFeature(
        point: point,
        properties: properties,
        id: 'point-001',
      );

      // Assert
      expect(feature['type'], equals('Feature'));
      expect(feature['id'], equals('point-001'));
      expect(feature['geometry']['type'], equals('Point'));

      final coordinates = feature['geometry']['coordinates'] as List;
      expect(coordinates[0], equals(44.1910)); // longitude
      expect(coordinates[1], equals(15.3694)); // latitude
    });
  });

  group('GeoJson - FeatureCollection Creation', () {
    test('should create valid feature collection', () {
      // Arrange
      final features = [
        GeoJson.createPointFeature(
          point: const LatLng(15.3694, 44.1910),
          properties: {'name': 'Point 1'},
        ),
        GeoJson.createPolygonFeature(
          boundary: [
            const LatLng(15.3694, 44.1910),
            const LatLng(15.3694, 44.1950),
            const LatLng(15.3734, 44.1950),
          ],
          properties: {'name': 'Polygon 1'},
        ),
      ];

      // Act
      final collection = GeoJson.createFeatureCollection(features);

      // Assert
      expect(collection['type'], equals('FeatureCollection'));
      expect(collection['features'], hasLength(2));
    });

    test('should create empty feature collection', () {
      // Act
      final collection = GeoJson.createFeatureCollection([]);

      // Assert
      expect(collection['type'], equals('FeatureCollection'));
      expect(collection['features'], isEmpty);
    });
  });

  group('GeoJson - Polygon Parsing', () {
    test('should parse valid polygon geometry', () {
      // Arrange
      final geometry = MockGeoJsonData.validPolygonFeature['geometry']
          as Map<String, dynamic>;

      // Act
      final points = GeoJson.parsePolygon(geometry);

      // Assert
      expect(points, isNotEmpty);
      expect(points.first.latitude, closeTo(15.3694, 0.0001));
      expect(points.first.longitude, closeTo(44.1910, 0.0001));
    });

    test('should throw for non-polygon geometry', () {
      // Arrange
      final pointGeometry = {'type': 'Point', 'coordinates': [44.0, 15.0]};

      // Act & Assert
      expect(
        () => GeoJson.parsePolygon(pointGeometry),
        throwsA(isA<ArgumentError>()),
      );
    });

    test('should return empty list for empty coordinates', () {
      // Arrange
      final emptyGeometry = {'type': 'Polygon', 'coordinates': []};

      // Act
      final points = GeoJson.parsePolygon(emptyGeometry);

      // Assert
      expect(points, isEmpty);
    });

    test('should handle polygon with holes (use outer ring only)', () {
      // Arrange
      final geometryWithHole = {
        'type': 'Polygon',
        'coordinates': [
          // Outer ring
          [
            [44.1910, 15.3694],
            [44.1950, 15.3694],
            [44.1950, 15.3734],
            [44.1910, 15.3734],
            [44.1910, 15.3694],
          ],
          // Inner ring (hole) - should be ignored
          [
            [44.1920, 15.3704],
            [44.1940, 15.3704],
            [44.1940, 15.3724],
            [44.1920, 15.3724],
            [44.1920, 15.3704],
          ],
        ],
      };

      // Act
      final points = GeoJson.parsePolygon(geometryWithHole);

      // Assert
      expect(points.length, equals(5)); // Only outer ring
    });
  });

  group('GeoJson - Point Parsing', () {
    test('should parse valid point geometry', () {
      // Arrange
      final geometry = MockGeoJsonData.validPointFeature['geometry']
          as Map<String, dynamic>;

      // Act
      final point = GeoJson.parsePoint(geometry);

      // Assert
      expect(point.latitude, closeTo(15.3714, 0.0001));
      expect(point.longitude, closeTo(44.1930, 0.0001));
    });

    test('should throw for non-point geometry', () {
      // Arrange
      final polygonGeometry = {
        'type': 'Polygon',
        'coordinates': [
          [[44.0, 15.0]]
        ],
      };

      // Act & Assert
      expect(
        () => GeoJson.parsePoint(polygonGeometry),
        throwsA(isA<ArgumentError>()),
      );
    });
  });

  group('GeoJson - Feature Parsing', () {
    test('should parse complete feature with all fields', () {
      // Act
      final feature = GeoJson.parseFeature(MockGeoJsonData.validPolygonFeature);

      // Assert
      expect(feature.id, equals('field-001'));
      expect(feature.geometryType, equals('Polygon'));
      expect(feature.properties['name'], equals('حقل القمح الشمالي'));
      expect(feature.properties['crop_type'], equals('wheat'));
      expect(feature.isPolygon, isTrue);
      expect(feature.isPoint, isFalse);
    });

    test('should handle feature without id', () {
      // Arrange
      final featureWithoutId = {
        'type': 'Feature',
        'properties': {'name': 'Test'},
        'geometry': {
          'type': 'Point',
          'coordinates': [44.0, 15.0],
        },
      };

      // Act
      final feature = GeoJson.parseFeature(featureWithoutId);

      // Assert
      expect(feature.id, isNull);
    });

    test('should handle feature without properties', () {
      // Arrange
      final featureWithoutProps = {
        'type': 'Feature',
        'geometry': {
          'type': 'Point',
          'coordinates': [44.0, 15.0],
        },
      };

      // Act
      final feature = GeoJson.parseFeature(featureWithoutProps);

      // Assert
      expect(feature.properties, isEmpty);
    });

    test('should access polygon from parsed feature', () {
      // Act
      final feature = GeoJson.parseFeature(MockGeoJsonData.validPolygonFeature);

      // Assert
      expect(feature.polygon, isNotNull);
      expect(feature.polygon!.length, greaterThanOrEqualTo(4));
    });

    test('should access point from parsed feature', () {
      // Act
      final feature = GeoJson.parseFeature(MockGeoJsonData.validPointFeature);

      // Assert
      expect(feature.point, isNotNull);
      expect(feature.point!.latitude, closeTo(15.3714, 0.0001));
    });
  });

  group('GeoJson - Centroid Calculation', () {
    test('should calculate centroid of square polygon', () {
      // Arrange
      final square = [
        const LatLng(0, 0),
        const LatLng(0, 10),
        const LatLng(10, 10),
        const LatLng(10, 0),
      ];

      // Act
      final centroid = GeoJson.calculateCentroid(square);

      // Assert
      expect(centroid.latitude, closeTo(5.0, 0.0001));
      expect(centroid.longitude, closeTo(5.0, 0.0001));
    });

    test('should calculate centroid of triangle', () {
      // Arrange
      final triangle = [
        const LatLng(0, 0),
        const LatLng(0, 6),
        const LatLng(6, 0),
      ];

      // Act
      final centroid = GeoJson.calculateCentroid(triangle);

      // Assert
      expect(centroid.latitude, closeTo(2.0, 0.0001));
      expect(centroid.longitude, closeTo(2.0, 0.0001));
    });

    test('should return origin for empty polygon', () {
      // Act
      final centroid = GeoJson.calculateCentroid([]);

      // Assert
      expect(centroid.latitude, equals(0.0));
      expect(centroid.longitude, equals(0.0));
    });

    test('should handle single point polygon', () {
      // Act
      final centroid = GeoJson.calculateCentroid([const LatLng(15.0, 44.0)]);

      // Assert
      expect(centroid.latitude, equals(15.0));
      expect(centroid.longitude, equals(44.0));
    });
  });

  group('GeoJson - Bounds Calculation', () {
    test('should calculate bounding box of polygon', () {
      // Arrange
      final polygon = [
        const LatLng(15.30, 44.10),
        const LatLng(15.30, 44.20),
        const LatLng(15.40, 44.20),
        const LatLng(15.40, 44.10),
      ];

      // Act
      final bounds = GeoJson.calculateBounds(polygon);

      // Assert
      expect(bounds.southWest.latitude, closeTo(15.30, 0.0001));
      expect(bounds.southWest.longitude, closeTo(44.10, 0.0001));
      expect(bounds.northEast.latitude, closeTo(15.40, 0.0001));
      expect(bounds.northEast.longitude, closeTo(44.20, 0.0001));
    });

    test('should handle single point for bounds', () {
      // Act
      final bounds = GeoJson.calculateBounds([const LatLng(15.0, 44.0)]);

      // Assert - Both corners should be the same point
      expect(bounds.southWest.latitude, equals(15.0));
      expect(bounds.southWest.longitude, equals(44.0));
      expect(bounds.northEast.latitude, equals(15.0));
      expect(bounds.northEast.longitude, equals(44.0));
    });

    test('should return zero bounds for empty polygon', () {
      // Act
      final bounds = GeoJson.calculateBounds([]);

      // Assert
      expect(bounds.southWest.latitude, equals(0.0));
      expect(bounds.southWest.longitude, equals(0.0));
    });
  });

  group('GeoJson - Area Calculation', () {
    test('should calculate area of rectangular field in hectares', () {
      // Arrange - Approximately 1km x 1km square near the equator
      final oneKmSquare = [
        const LatLng(0, 0),
        const LatLng(0, 0.009), // ~1km at equator
        const LatLng(0.009, 0.009),
        const LatLng(0.009, 0),
      ];

      // Act
      final area = GeoJson.calculateAreaHectares(oneKmSquare);

      // Assert - Should be approximately 100 hectares (1 km2)
      expect(area, closeTo(100, 10)); // Allow 10% tolerance
    });

    test('should return zero for invalid polygon (< 3 points)', () {
      // Act
      final area = GeoJson.calculateAreaHectares([
        const LatLng(0, 0),
        const LatLng(0, 1),
      ]);

      // Assert
      expect(area, equals(0));
    });

    test('should calculate area of typical Yemeni field', () {
      // Arrange - Small field in Sanaa area
      final field = [
        const LatLng(15.3694, 44.1910),
        const LatLng(15.3694, 44.1920),
        const LatLng(15.3704, 44.1920),
        const LatLng(15.3704, 44.1910),
      ];

      // Act
      final area = GeoJson.calculateAreaHectares(field);

      // Assert - Should be a small positive value
      expect(area, greaterThan(0));
      expect(area, lessThan(100)); // Reasonable field size
    });
  });

  group('GeoJson - Polygon Simplification', () {
    test('should simplify polygon with Douglas-Peucker algorithm', () {
      // Arrange - Polygon with many points
      final detailedPolygon = [
        const LatLng(0, 0),
        const LatLng(0.001, 0.001), // Small deviation
        const LatLng(0.002, 0.001), // Small deviation
        const LatLng(1, 0), // Main corner
        const LatLng(1.001, 1.001), // Small deviation
        const LatLng(1, 1), // Main corner
        const LatLng(0.001, 0.999), // Small deviation
        const LatLng(0, 1), // Main corner
      ];

      // Act
      final simplified = GeoJson.simplify(detailedPolygon, 0.01);

      // Assert
      expect(simplified.length, lessThan(detailedPolygon.length));
      expect(simplified.length, greaterThanOrEqualTo(2));
    });

    test('should not simplify polygon with 2 or fewer points', () {
      // Arrange
      final twoPoints = [
        const LatLng(0, 0),
        const LatLng(1, 1),
      ];

      // Act
      final simplified = GeoJson.simplify(twoPoints, 0.1);

      // Assert
      expect(simplified.length, equals(2));
    });

    test('should preserve corners with small tolerance', () {
      // Arrange - Square
      final square = [
        const LatLng(0, 0),
        const LatLng(0, 10),
        const LatLng(10, 10),
        const LatLng(10, 0),
      ];

      // Act
      final simplified = GeoJson.simplify(square, 0.001);

      // Assert - Should keep all corners with small tolerance
      expect(simplified.length, greaterThanOrEqualTo(2));
    });

    test('should aggressively simplify with large tolerance', () {
      // Arrange
      final polygon = [
        const LatLng(0, 0),
        const LatLng(0.1, 0.5),
        const LatLng(0.2, 1.0),
        const LatLng(0.8, 1.2),
        const LatLng(1, 1),
      ];

      // Act
      final simplified = GeoJson.simplify(polygon, 1.0);

      // Assert
      expect(simplified.length, equals(2)); // Just start and end
    });
  });

  group('GeoJsonFeature - Properties', () {
    test('should correctly identify polygon feature', () {
      // Act
      final feature = GeoJson.parseFeature(MockGeoJsonData.validPolygonFeature);

      // Assert
      expect(feature.isPolygon, isTrue);
      expect(feature.isPoint, isFalse);
      expect(feature.isMultiPolygon, isFalse);
    });

    test('should correctly identify point feature', () {
      // Act
      final feature = GeoJson.parseFeature(MockGeoJsonData.validPointFeature);

      // Assert
      expect(feature.isPolygon, isFalse);
      expect(feature.isPoint, isTrue);
      expect(feature.isMultiPolygon, isFalse);
    });

    test('should correctly identify MultiPolygon feature', () {
      // Act
      final feature = GeoJson.parseFeature(MockGeoJsonData.multiPolygonFeature);

      // Assert
      expect(feature.isPolygon, isFalse);
      expect(feature.isPoint, isFalse);
      expect(feature.isMultiPolygon, isTrue);
    });
  });

  group('LatLngList Extension - GeoJSON Conversion', () {
    test('should convert LatLng list to GeoJSON coordinates', () {
      // Arrange
      final points = [
        const LatLng(15.0, 44.0),
        const LatLng(15.1, 44.1),
      ];

      // Act
      final coordinates = points.toGeoJsonCoordinates();

      // Assert
      expect(coordinates[0], equals([44.0, 15.0])); // [lon, lat]
      expect(coordinates[1], equals([44.1, 15.1]));
    });

    test('should convert to GeoJSON Polygon geometry', () {
      // Arrange
      final points = [
        const LatLng(15.0, 44.0),
        const LatLng(15.0, 44.1),
        const LatLng(15.1, 44.0),
      ];

      // Act
      final geometry = points.toGeoJsonPolygon();

      // Assert
      expect(geometry['type'], equals('Polygon'));
      expect(geometry['coordinates'], isA<List>());
    });

    test('should calculate centroid via extension', () {
      // Arrange
      final square = [
        const LatLng(0, 0),
        const LatLng(0, 10),
        const LatLng(10, 10),
        const LatLng(10, 0),
      ];

      // Act
      final centroid = square.centroid;

      // Assert
      expect(centroid.latitude, closeTo(5.0, 0.0001));
      expect(centroid.longitude, closeTo(5.0, 0.0001));
    });

    test('should calculate bounds via extension', () {
      // Arrange
      final polygon = [
        const LatLng(15.30, 44.10),
        const LatLng(15.40, 44.20),
      ];

      // Act
      final bounds = polygon.bounds;

      // Assert
      expect(bounds.southWest.latitude, equals(15.30));
      expect(bounds.northEast.longitude, equals(44.20));
    });

    test('should calculate area via extension', () {
      // Arrange
      final field = [
        const LatLng(15.3694, 44.1910),
        const LatLng(15.3694, 44.1920),
        const LatLng(15.3704, 44.1920),
        const LatLng(15.3704, 44.1910),
      ];

      // Act
      final area = field.areaHectares;

      // Assert
      expect(area, greaterThan(0));
    });
  });

  group('GeoJson - Coordinate Order Validation', () {
    test('should use GeoJSON standard [longitude, latitude] order', () {
      // Arrange
      const point = LatLng(15.3694, 44.1910); // lat=15.3694, lon=44.1910

      // Act
      final feature = GeoJson.createPointFeature(
        point: point,
        properties: {},
      );

      // Assert
      final coords = feature['geometry']['coordinates'] as List;
      expect(coords[0], equals(44.1910)); // longitude FIRST
      expect(coords[1], equals(15.3694)); // latitude SECOND
    });

    test('should parse GeoJSON coordinates in correct order', () {
      // Arrange - GeoJSON with [longitude, latitude] order
      final geometry = {
        'type': 'Point',
        'coordinates': [44.1910, 15.3694], // [lon, lat]
      };

      // Act
      final point = GeoJson.parsePoint(geometry);

      // Assert
      expect(point.longitude, equals(44.1910));
      expect(point.latitude, equals(15.3694));
    });
  });

  group('GeoJson - JSON Serialization', () {
    test('should produce valid JSON string', () {
      // Arrange
      final feature = GeoJson.createPointFeature(
        point: const LatLng(15.0, 44.0),
        properties: {'name': 'Test'},
      );

      // Act
      final jsonString = jsonEncode(feature);
      final parsed = jsonDecode(jsonString);

      // Assert
      expect(parsed['type'], equals('Feature'));
      expect(parsed['geometry']['type'], equals('Point'));
    });

    test('should handle Arabic characters in properties', () {
      // Arrange
      final feature = GeoJson.createPointFeature(
        point: const LatLng(15.0, 44.0),
        properties: {
          'name': 'حقل القمح',
          'description': 'حقل في منطقة صنعاء',
        },
      );

      // Act
      final jsonString = jsonEncode(feature);
      final parsed = jsonDecode(jsonString);

      // Assert
      expect(parsed['properties']['name'], equals('حقل القمح'));
      expect(parsed['properties']['description'], equals('حقل في منطقة صنعاء'));
    });
  });

  group('GeoJson - Edge Cases', () {
    test('should handle polygon crossing the antimeridian', () {
      // Arrange - Polygon crossing 180 degrees longitude
      final crossingPolygon = [
        const LatLng(0, 179),
        const LatLng(0, -179),
        const LatLng(1, -179),
        const LatLng(1, 179),
      ];

      // Act
      final feature = GeoJson.createPolygonFeature(
        boundary: crossingPolygon,
        properties: {},
      );

      // Assert - Should still create valid GeoJSON
      expect(feature['geometry']['type'], equals('Polygon'));
      expect(feature['geometry']['coordinates'][0], hasLength(5));
    });

    test('should handle polygon near the poles', () {
      // Arrange - Polygon near north pole
      final polarPolygon = [
        const LatLng(89, 0),
        const LatLng(89, 90),
        const LatLng(89, 180),
        const LatLng(89, -90),
      ];

      // Act
      final feature = GeoJson.createPolygonFeature(
        boundary: polarPolygon,
        properties: {},
      );

      // Assert
      expect(feature['geometry']['type'], equals('Polygon'));
    });

    test('should handle very small polygon (precision test)', () {
      // Arrange - Very small polygon
      final tinyPolygon = [
        const LatLng(15.369400001, 44.191000001),
        const LatLng(15.369400001, 44.191000002),
        const LatLng(15.369400002, 44.191000002),
        const LatLng(15.369400002, 44.191000001),
      ];

      // Act
      final centroid = GeoJson.calculateCentroid(tinyPolygon);

      // Assert - Should maintain precision
      expect(centroid.latitude, closeTo(15.369400001, 0.0000001));
      expect(centroid.longitude, closeTo(44.191000001, 0.0000001));
    });
  });
}
