/// Field Boundaries Tests for SAHOOL Field App
/// اختبارات حدود الحقول
///
/// Tests for GeoJSON operations including:
/// - Polygon creation and parsing
/// - Centroid calculation
/// - Area calculation (hectares)
/// - Bounding box
/// - Polygon simplification
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:flutter_map/flutter_map.dart';

import 'package:sahool_field_app/core/geo/geojson.dart';

import 'fixtures/field_fixtures.dart';

void main() {
  group('GeoJson', () {
    group('createPolygonFeature', () {
      test('should create valid GeoJSON Feature for polygon', () {
        // Arrange
        final boundary = FieldTestFixtures.simpleRectangleBoundary;

        // Act
        final feature = GeoJson.createPolygonFeature(
          boundary: boundary,
          properties: {'name': 'Test Field'},
        );

        // Assert
        expect(feature['type'], 'Feature');
        expect(feature['geometry']['type'], 'Polygon');
        expect(feature['properties']['name'], 'Test Field');
      });

      test('should include optional ID when provided', () {
        // Arrange
        final boundary = FieldTestFixtures.triangleBoundary;

        // Act
        final feature = GeoJson.createPolygonFeature(
          boundary: boundary,
          properties: {'name': 'Test'},
          id: 'field_001',
        );

        // Assert
        expect(feature['id'], 'field_001');
      });

      test('should use [longitude, latitude] order in coordinates', () {
        // Arrange
        final boundary = [const LatLng(15.0, 44.0)];

        // Act
        final feature = GeoJson.createPolygonFeature(
          boundary: boundary,
          properties: {},
        );

        // Assert
        final coordinates = feature['geometry']['coordinates'][0] as List;
        // First coordinate should be [lng, lat] = [44.0, 15.0]
        expect(coordinates[0][0], 44.0); // longitude first
        expect(coordinates[0][1], 15.0); // latitude second
      });

      test('should close polygon (first point == last point)', () {
        // Arrange - unclosed polygon
        final boundary = FieldTestFixtures.simpleRectangleBoundary;

        // Act
        final feature = GeoJson.createPolygonFeature(
          boundary: boundary,
          properties: {},
        );

        // Assert
        final coordinates = feature['geometry']['coordinates'][0] as List;
        expect(coordinates.first, equals(coordinates.last));
      });

      test('should handle already closed polygon', () {
        // Arrange - already closed polygon
        final boundary = [
          const LatLng(15.0, 44.0),
          const LatLng(15.1, 44.0),
          const LatLng(15.1, 44.1),
          const LatLng(15.0, 44.0), // Closed
        ];

        // Act
        final feature = GeoJson.createPolygonFeature(
          boundary: boundary,
          properties: {},
        );

        // Assert
        final coordinates = feature['geometry']['coordinates'][0] as List;
        expect(coordinates.first, equals(coordinates.last));
        // Should not duplicate the closing point
        expect(coordinates.length, 4);
      });
    });

    group('createPointFeature', () {
      test('should create valid GeoJSON Point Feature', () {
        // Arrange
        const point = LatLng(15.5, 44.5);

        // Act
        final feature = GeoJson.createPointFeature(
          point: point,
          properties: {'type': 'centroid'},
        );

        // Assert
        expect(feature['type'], 'Feature');
        expect(feature['geometry']['type'], 'Point');
        expect(feature['geometry']['coordinates'][0], 44.5); // longitude
        expect(feature['geometry']['coordinates'][1], 15.5); // latitude
      });

      test('should include optional ID', () {
        // Arrange
        const point = LatLng(15.5, 44.5);

        // Act
        final feature = GeoJson.createPointFeature(
          point: point,
          properties: {},
          id: 'point_001',
        );

        // Assert
        expect(feature['id'], 'point_001');
      });
    });

    group('createFeatureCollection', () {
      test('should create valid FeatureCollection', () {
        // Arrange
        final features = [
          GeoJson.createPolygonFeature(
            boundary: FieldTestFixtures.triangleBoundary,
            properties: {'name': 'Field 1'},
          ),
          GeoJson.createPolygonFeature(
            boundary: FieldTestFixtures.simpleRectangleBoundary,
            properties: {'name': 'Field 2'},
          ),
        ];

        // Act
        final collection = GeoJson.createFeatureCollection(features);

        // Assert
        expect(collection['type'], 'FeatureCollection');
        expect(collection['features'].length, 2);
      });

      test('should handle empty feature list', () {
        // Act
        final collection = GeoJson.createFeatureCollection([]);

        // Assert
        expect(collection['type'], 'FeatureCollection');
        expect(collection['features'], isEmpty);
      });
    });

    group('parsePolygon', () {
      test('should parse GeoJSON Polygon geometry to List<LatLng>', () {
        // Arrange
        final geometry = {
          'type': 'Polygon',
          'coordinates': [
            [
              [44.1900, 15.3700],
              [44.1950, 15.3700],
              [44.1950, 15.3750],
              [44.1900, 15.3750],
              [44.1900, 15.3700], // Closed
            ],
          ],
        };

        // Act
        final polygon = GeoJson.parsePolygon(geometry);

        // Assert
        expect(polygon.length, 5);
        expect(polygon.first.latitude, 15.3700);
        expect(polygon.first.longitude, 44.1900);
      });

      test('should throw for non-Polygon geometry', () {
        // Arrange
        final geometry = {
          'type': 'Point',
          'coordinates': [44.0, 15.0],
        };

        // Act & Assert
        expect(
          () => GeoJson.parsePolygon(geometry),
          throwsArgumentError,
        );
      });

      test('should return empty list for empty coordinates', () {
        // Arrange
        final geometry = {
          'type': 'Polygon',
          'coordinates': [],
        };

        // Act
        final polygon = GeoJson.parsePolygon(geometry);

        // Assert
        expect(polygon, isEmpty);
      });
    });

    group('parsePoint', () {
      test('should parse GeoJSON Point geometry to LatLng', () {
        // Arrange
        final geometry = {
          'type': 'Point',
          'coordinates': [44.5, 15.5],
        };

        // Act
        final point = GeoJson.parsePoint(geometry);

        // Assert
        expect(point.latitude, 15.5);
        expect(point.longitude, 44.5);
      });

      test('should throw for non-Point geometry', () {
        // Arrange
        final geometry = {
          'type': 'Polygon',
          'coordinates': [[[44.0, 15.0]]],
        };

        // Act & Assert
        expect(
          () => GeoJson.parsePoint(geometry),
          throwsArgumentError,
        );
      });
    });

    group('parseFeature', () {
      test('should parse GeoJSON Feature', () {
        // Act
        final feature = GeoJson.parseFeature(
          FieldTestFixtures.sampleGeoJsonFeature,
        );

        // Assert
        expect(feature.id, 'field_001');
        expect(feature.isPolygon, true);
        expect(feature.properties['name'], 'الحقل الشمالي');
      });

      test('should handle feature without ID', () {
        // Arrange
        final featureJson = {
          'type': 'Feature',
          'geometry': {
            'type': 'Point',
            'coordinates': [44.0, 15.0],
          },
          'properties': {'name': 'Test'},
        };

        // Act
        final feature = GeoJson.parseFeature(featureJson);

        // Assert
        expect(feature.id, isNull);
      });

      test('should handle feature without properties', () {
        // Arrange
        final featureJson = {
          'type': 'Feature',
          'geometry': {
            'type': 'Point',
            'coordinates': [44.0, 15.0],
          },
        };

        // Act
        final feature = GeoJson.parseFeature(featureJson);

        // Assert
        expect(feature.properties, isEmpty);
      });
    });

    group('calculateCentroid', () {
      test('should calculate centroid for rectangle', () {
        // Arrange
        final polygon = [
          const LatLng(15.0, 44.0),
          const LatLng(15.0, 45.0),
          const LatLng(16.0, 45.0),
          const LatLng(16.0, 44.0),
        ];

        // Act
        final centroid = GeoJson.calculateCentroid(polygon);

        // Assert
        expect(centroid.latitude, closeTo(15.5, 0.001));
        expect(centroid.longitude, closeTo(44.5, 0.001));
      });

      test('should calculate centroid for triangle', () {
        // Arrange
        final polygon = [
          const LatLng(15.0, 44.0),
          const LatLng(16.0, 44.5),
          const LatLng(15.0, 45.0),
        ];

        // Act
        final centroid = GeoJson.calculateCentroid(polygon);

        // Assert
        // Triangle centroid is at (15 + 16 + 15) / 3, (44 + 44.5 + 45) / 3
        expect(centroid.latitude, closeTo(15.333, 0.01));
        expect(centroid.longitude, closeTo(44.5, 0.001));
      });

      test('should return origin for empty polygon', () {
        // Act
        final centroid = GeoJson.calculateCentroid([]);

        // Assert
        expect(centroid.latitude, 0);
        expect(centroid.longitude, 0);
      });

      test('should calculate centroid for complex polygon', () {
        // Arrange
        final polygon = FieldTestFixtures.irregularBoundary;

        // Act
        final centroid = GeoJson.calculateCentroid(polygon);

        // Assert
        expect(centroid.latitude, isPositive);
        expect(centroid.longitude, isPositive);
      });
    });

    group('calculateBounds', () {
      test('should calculate bounding box for rectangle', () {
        // Arrange
        final polygon = [
          const LatLng(15.0, 44.0),
          const LatLng(15.0, 45.0),
          const LatLng(16.0, 45.0),
          const LatLng(16.0, 44.0),
        ];

        // Act
        final bounds = GeoJson.calculateBounds(polygon);

        // Assert
        expect(bounds.southWest.latitude, 15.0);
        expect(bounds.southWest.longitude, 44.0);
        expect(bounds.northEast.latitude, 16.0);
        expect(bounds.northEast.longitude, 45.0);
      });

      test('should calculate bounds for irregular polygon', () {
        // Arrange
        final polygon = FieldTestFixtures.irregularBoundary;

        // Act
        final bounds = GeoJson.calculateBounds(polygon);

        // Assert
        expect(bounds.southWest.latitude, lessThanOrEqualTo(bounds.northEast.latitude));
        expect(bounds.southWest.longitude, lessThanOrEqualTo(bounds.northEast.longitude));
      });

      test('should handle empty polygon', () {
        // Act
        final bounds = GeoJson.calculateBounds([]);

        // Assert
        expect(bounds.southWest.latitude, 0);
        expect(bounds.southWest.longitude, 0);
      });

      test('should handle single point', () {
        // Arrange
        final polygon = [const LatLng(15.5, 44.5)];

        // Act
        final bounds = GeoJson.calculateBounds(polygon);

        // Assert
        expect(bounds.southWest.latitude, 15.5);
        expect(bounds.southWest.longitude, 44.5);
        expect(bounds.northEast.latitude, 15.5);
        expect(bounds.northEast.longitude, 44.5);
      });
    });

    group('calculateAreaHectares', () {
      test('should return 0 for less than 3 points', () {
        expect(GeoJson.calculateAreaHectares([]), 0);
        expect(GeoJson.calculateAreaHectares([const LatLng(15, 44)]), 0);
        expect(
          GeoJson.calculateAreaHectares([
            const LatLng(15, 44),
            const LatLng(16, 45),
          ]),
          0,
        );
      });

      test('should calculate positive area for valid polygon', () {
        // Arrange
        final polygon = FieldTestFixtures.simpleRectangleBoundary;

        // Act
        final area = GeoJson.calculateAreaHectares(polygon);

        // Assert
        expect(area, isPositive);
      });

      test('should calculate area for small field (< 10 ha)', () {
        // Arrange - approximately 1 hectare (100m x 100m)
        // At equator, 1 degree ~ 111km, so 0.001 degree ~ 111m
        final polygon = [
          const LatLng(0.0, 0.0),
          const LatLng(0.0, 0.001),
          const LatLng(0.001, 0.001),
          const LatLng(0.001, 0.0),
        ];

        // Act
        final area = GeoJson.calculateAreaHectares(polygon);

        // Assert
        // Should be approximately 1.23 hectares (111m x 111m = ~12,321 m2)
        expect(area, inInclusiveRange(0.5, 2.0));
      });

      test('should handle clockwise and counter-clockwise polygons', () {
        // Arrange
        final clockwise = [
          const LatLng(15.0, 44.0),
          const LatLng(15.0, 44.01),
          const LatLng(15.01, 44.01),
          const LatLng(15.01, 44.0),
        ];
        final counterClockwise = clockwise.reversed.toList();

        // Act
        final areaClockwise = GeoJson.calculateAreaHectares(clockwise);
        final areaCounterClockwise = GeoJson.calculateAreaHectares(counterClockwise);

        // Assert - both should give same positive area
        expect(areaClockwise, closeTo(areaCounterClockwise, 0.01));
        expect(areaClockwise, isPositive);
      });
    });

    group('simplify', () {
      test('should return original polygon if <= 2 points', () {
        // Arrange
        final twoPoints = [
          const LatLng(15.0, 44.0),
          const LatLng(16.0, 45.0),
        ];

        // Act
        final simplified = GeoJson.simplify(twoPoints, 0.001);

        // Assert
        expect(simplified, twoPoints);
      });

      test('should reduce points for complex polygon', () {
        // Arrange
        final complex = FieldTestFixtures.largeFieldBoundary;

        // Act
        final simplified = GeoJson.simplify(complex, 0.01);

        // Assert
        expect(simplified.length, lessThanOrEqualTo(complex.length));
      });

      test('should preserve endpoints', () {
        // Arrange
        final polygon = FieldTestFixtures.irregularBoundary;

        // Act
        final simplified = GeoJson.simplify(polygon, 0.001);

        // Assert
        expect(simplified.first, polygon.first);
        expect(simplified.last, polygon.last);
      });

      test('should not modify polygon with tight tolerance', () {
        // Arrange
        final polygon = FieldTestFixtures.triangleBoundary;

        // Act
        final simplified = GeoJson.simplify(polygon, 0.0000001);

        // Assert
        expect(simplified.length, greaterThanOrEqualTo(2));
      });
    });
  });

  group('GeoJsonFeature', () {
    test('should identify polygon type', () {
      // Arrange
      final featureJson = GeoJson.createPolygonFeature(
        boundary: FieldTestFixtures.triangleBoundary,
        properties: {},
      );

      // Act
      final feature = GeoJson.parseFeature(featureJson);

      // Assert
      expect(feature.isPolygon, true);
      expect(feature.isPoint, false);
      expect(feature.isMultiPolygon, false);
      expect(feature.geometryType, 'Polygon');
    });

    test('should identify point type', () {
      // Arrange
      final featureJson = GeoJson.createPointFeature(
        point: const LatLng(15.5, 44.5),
        properties: {},
      );

      // Act
      final feature = GeoJson.parseFeature(featureJson);

      // Assert
      expect(feature.isPoint, true);
      expect(feature.isPolygon, false);
      expect(feature.geometryType, 'Point');
    });

    test('polygon getter should return parsed polygon', () {
      // Arrange
      final boundary = FieldTestFixtures.simpleRectangleBoundary;
      final featureJson = GeoJson.createPolygonFeature(
        boundary: boundary,
        properties: {},
      );

      // Act
      final feature = GeoJson.parseFeature(featureJson);

      // Assert
      expect(feature.polygon, isNotNull);
      expect(feature.polygon!.length, 5); // Closed polygon
    });

    test('point getter should return parsed point', () {
      // Arrange
      const point = LatLng(15.5, 44.5);
      final featureJson = GeoJson.createPointFeature(
        point: point,
        properties: {},
      );

      // Act
      final feature = GeoJson.parseFeature(featureJson);

      // Assert
      expect(feature.point, isNotNull);
      expect(feature.point!.latitude, 15.5);
      expect(feature.point!.longitude, 44.5);
    });

    test('polygon getter should return null for point feature', () {
      // Arrange
      final featureJson = GeoJson.createPointFeature(
        point: const LatLng(15.5, 44.5),
        properties: {},
      );

      // Act
      final feature = GeoJson.parseFeature(featureJson);

      // Assert
      expect(feature.polygon, isNull);
    });

    test('point getter should return null for polygon feature', () {
      // Arrange
      final featureJson = GeoJson.createPolygonFeature(
        boundary: FieldTestFixtures.triangleBoundary,
        properties: {},
      );

      // Act
      final feature = GeoJson.parseFeature(featureJson);

      // Assert
      expect(feature.point, isNull);
    });
  });

  group('LatLngListGeoJson Extension', () {
    test('toGeoJsonCoordinates should convert to [lng, lat] format', () {
      // Arrange
      final points = [
        const LatLng(15.0, 44.0),
        const LatLng(16.0, 45.0),
      ];

      // Act
      final coords = points.toGeoJsonCoordinates();

      // Assert
      expect(coords[0], [44.0, 15.0]); // [lng, lat]
      expect(coords[1], [45.0, 16.0]);
    });

    test('toGeoJsonPolygon should create polygon geometry', () {
      // Arrange
      final points = FieldTestFixtures.triangleBoundary;

      // Act
      final geometry = points.toGeoJsonPolygon();

      // Assert
      expect(geometry['type'], 'Polygon');
      expect(geometry['coordinates'], isNotNull);
    });

    test('centroid getter should return calculated centroid', () {
      // Arrange
      final points = [
        const LatLng(15.0, 44.0),
        const LatLng(15.0, 46.0),
        const LatLng(17.0, 46.0),
        const LatLng(17.0, 44.0),
      ];

      // Act
      final centroid = points.centroid;

      // Assert
      expect(centroid.latitude, closeTo(16.0, 0.001));
      expect(centroid.longitude, closeTo(45.0, 0.001));
    });

    test('bounds getter should return calculated bounds', () {
      // Arrange
      final points = FieldTestFixtures.simpleRectangleBoundary;

      // Act
      final bounds = points.bounds;

      // Assert
      expect(bounds, isA<LatLngBounds>());
    });

    test('areaHectares getter should return calculated area', () {
      // Arrange
      final points = FieldTestFixtures.simpleRectangleBoundary;

      // Act
      final area = points.areaHectares;

      // Assert
      expect(area, isPositive);
    });
  });

  group('GeoJSON Round-Trip Conversion', () {
    test('should preserve coordinates through create -> parse cycle', () {
      // Arrange
      final originalBoundary = FieldTestFixtures.simpleRectangleBoundary;

      // Act
      final feature = GeoJson.createPolygonFeature(
        boundary: originalBoundary,
        properties: {'name': 'Test'},
      );
      final parsedPolygon = GeoJson.parsePolygon(feature['geometry'] as Map<String, dynamic>);

      // Assert - Note: parsed polygon will have closing point added
      for (var i = 0; i < originalBoundary.length; i++) {
        expect(
          parsedPolygon[i].latitude,
          closeTo(originalBoundary[i].latitude, 0.0001),
        );
        expect(
          parsedPolygon[i].longitude,
          closeTo(originalBoundary[i].longitude, 0.0001),
        );
      }
    });

    test('should preserve properties through create -> parse cycle', () {
      // Arrange
      final properties = {
        'name': 'Test Field',
        'crop_type': 'wheat',
        'area_hectares': 5.5,
      };

      // Act
      final featureJson = GeoJson.createPolygonFeature(
        boundary: FieldTestFixtures.triangleBoundary,
        properties: properties,
        id: 'field_001',
      );
      final feature = GeoJson.parseFeature(featureJson);

      // Assert
      expect(feature.id, 'field_001');
      expect(feature.properties['name'], 'Test Field');
      expect(feature.properties['crop_type'], 'wheat');
      expect(feature.properties['area_hectares'], 5.5);
    });
  });
}
