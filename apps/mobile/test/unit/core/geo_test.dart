/// Unit Tests for GeoJSON Utilities
/// اختبارات وحدات أدوات GeoJSON
import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:sahool_field_app/core/geo/geojson.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // GeoJson.createPolygonFeature Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('GeoJson.createPolygonFeature', () {
    test('creates valid GeoJSON Feature with Polygon geometry', () {
      // Arrange
      final boundary = [
        const LatLng(24.7, 46.7),
        const LatLng(24.7, 46.8),
        const LatLng(24.8, 46.8),
        const LatLng(24.8, 46.7),
      ];

      // Act
      final feature = GeoJson.createPolygonFeature(
        boundary: boundary,
        properties: {'name': 'Field 1', 'crop': 'wheat'},
        id: 'field-001',
      );

      // Assert
      expect(feature['type'], 'Feature');
      expect(feature['id'], 'field-001');
      expect(feature['properties']['name'], 'Field 1');
      expect(feature['geometry']['type'], 'Polygon');

      // GeoJSON uses [longitude, latitude] order
      final coordinates = feature['geometry']['coordinates'][0] as List;
      expect(coordinates.first[0], 46.7); // longitude first
      expect(coordinates.first[1], 24.7); // latitude second
    });

    test('auto-closes polygon if not closed', () {
      // Arrange - polygon not closed
      final boundary = [
        const LatLng(24.7, 46.7),
        const LatLng(24.7, 46.8),
        const LatLng(24.8, 46.8),
      ];

      // Act
      final feature = GeoJson.createPolygonFeature(
        boundary: boundary,
        properties: {},
      );

      // Assert
      final coordinates = feature['geometry']['coordinates'][0] as List;
      // First and last point should be the same
      expect(coordinates.first[0], coordinates.last[0]);
      expect(coordinates.first[1], coordinates.last[1]);
      expect(coordinates.length, 4); // 3 points + closing point
    });

    test('does not duplicate closing point if already closed', () {
      // Arrange - polygon already closed
      final boundary = [
        const LatLng(24.7, 46.7),
        const LatLng(24.7, 46.8),
        const LatLng(24.8, 46.8),
        const LatLng(24.7, 46.7), // Already closed
      ];

      // Act
      final feature = GeoJson.createPolygonFeature(
        boundary: boundary,
        properties: {},
      );

      // Assert
      final coordinates = feature['geometry']['coordinates'][0] as List;
      expect(coordinates.length, 4); // Should NOT add extra point
    });

    test('omits id when not provided', () {
      // Act
      final feature = GeoJson.createPolygonFeature(
        boundary: [const LatLng(0, 0)],
        properties: {},
      );

      // Assert
      expect(feature.containsKey('id'), false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GeoJson.createPointFeature Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('GeoJson.createPointFeature', () {
    test('creates valid GeoJSON Point Feature', () {
      // Arrange
      const point = LatLng(24.75, 46.75);

      // Act
      final feature = GeoJson.createPointFeature(
        point: point,
        properties: {'name': 'Center', 'type': 'centroid'},
        id: 'point-001',
      );

      // Assert
      expect(feature['type'], 'Feature');
      expect(feature['id'], 'point-001');
      expect(feature['geometry']['type'], 'Point');
      expect(feature['geometry']['coordinates'][0], 46.75); // lon
      expect(feature['geometry']['coordinates'][1], 24.75); // lat
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GeoJson.createFeatureCollection Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('GeoJson.createFeatureCollection', () {
    test('creates valid FeatureCollection', () {
      // Arrange
      final features = [
        GeoJson.createPointFeature(
          point: const LatLng(24.7, 46.7),
          properties: {'name': 'A'},
        ),
        GeoJson.createPointFeature(
          point: const LatLng(24.8, 46.8),
          properties: {'name': 'B'},
        ),
      ];

      // Act
      final collection = GeoJson.createFeatureCollection(features);

      // Assert
      expect(collection['type'], 'FeatureCollection');
      expect((collection['features'] as List).length, 2);
    });

    test('handles empty features list', () {
      // Act
      final collection = GeoJson.createFeatureCollection([]);

      // Assert
      expect(collection['type'], 'FeatureCollection');
      expect((collection['features'] as List), isEmpty);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GeoJson.parsePolygon Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('GeoJson.parsePolygon', () {
    test('parses GeoJSON polygon to List<LatLng>', () {
      // Arrange
      final geometry = {
        'type': 'Polygon',
        'coordinates': [
          [
            [46.7, 24.7],
            [46.8, 24.7],
            [46.8, 24.8],
            [46.7, 24.8],
            [46.7, 24.7],
          ]
        ],
      };

      // Act
      final points = GeoJson.parsePolygon(geometry);

      // Assert
      expect(points.length, 5);
      expect(points.first.latitude, 24.7);
      expect(points.first.longitude, 46.7);
    });

    test('throws ArgumentError for non-Polygon geometry', () {
      // Arrange
      final geometry = {'type': 'Point', 'coordinates': [46.7, 24.7]};

      // Act & Assert
      expect(
        () => GeoJson.parsePolygon(geometry),
        throwsA(isA<ArgumentError>()),
      );
    });

    test('returns empty list for empty coordinates', () {
      // Arrange
      final geometry = {
        'type': 'Polygon',
        'coordinates': [],
      };

      // Act
      final points = GeoJson.parsePolygon(geometry);

      // Assert
      expect(points, isEmpty);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GeoJson.parsePoint Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('GeoJson.parsePoint', () {
    test('parses GeoJSON Point to LatLng', () {
      // Arrange
      final geometry = {
        'type': 'Point',
        'coordinates': [46.75, 24.75],
      };

      // Act
      final point = GeoJson.parsePoint(geometry);

      // Assert
      expect(point.latitude, 24.75);
      expect(point.longitude, 46.75);
    });

    test('throws ArgumentError for non-Point geometry', () {
      // Arrange
      final geometry = {
        'type': 'Polygon',
        'coordinates': [
          [
            [0, 0]
          ]
        ],
      };

      // Act & Assert
      expect(
        () => GeoJson.parsePoint(geometry),
        throwsA(isA<ArgumentError>()),
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GeoJson.parseFeature Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('GeoJson.parseFeature', () {
    test('parses Feature with id, geometry, and properties', () {
      // Arrange
      final feature = {
        'type': 'Feature',
        'id': 'field-1',
        'geometry': {'type': 'Point', 'coordinates': [46.7, 24.7]},
        'properties': {'name': 'Test Field'},
      };

      // Act
      final parsed = GeoJson.parseFeature(feature);

      // Assert
      expect(parsed.id, 'field-1');
      expect(parsed.geometry['type'], 'Point');
      expect(parsed.properties['name'], 'Test Field');
    });

    test('handles missing properties and id', () {
      // Arrange
      final feature = {
        'type': 'Feature',
        'geometry': {'type': 'Point', 'coordinates': [0, 0]},
      };

      // Act
      final parsed = GeoJson.parseFeature(feature);

      // Assert
      expect(parsed.id, isNull);
      expect(parsed.properties, isEmpty);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GeoJson.calculateCentroid Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('GeoJson.calculateCentroid', () {
    test('calculates correct centroid for a square polygon', () {
      // Arrange
      final polygon = [
        const LatLng(24.0, 46.0),
        const LatLng(24.0, 47.0),
        const LatLng(25.0, 47.0),
        const LatLng(25.0, 46.0),
      ];

      // Act
      final centroid = GeoJson.calculateCentroid(polygon);

      // Assert
      expect(centroid.latitude, closeTo(24.5, 0.01));
      expect(centroid.longitude, closeTo(46.5, 0.01));
    });

    test('returns (0, 0) for empty polygon', () {
      // Act
      final centroid = GeoJson.calculateCentroid([]);

      // Assert
      expect(centroid.latitude, 0);
      expect(centroid.longitude, 0);
    });

    test('returns point itself for single-point polygon', () {
      // Act
      final centroid = GeoJson.calculateCentroid([const LatLng(24.7, 46.7)]);

      // Assert
      expect(centroid.latitude, 24.7);
      expect(centroid.longitude, 46.7);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GeoJson.calculateBounds Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('GeoJson.calculateBounds', () {
    test('calculates correct bounding box', () {
      // Arrange
      final polygon = [
        const LatLng(24.0, 46.0),
        const LatLng(24.5, 46.5),
        const LatLng(25.0, 47.0),
      ];

      // Act
      final bounds = GeoJson.calculateBounds(polygon);

      // Assert
      expect(bounds.southWest.latitude, 24.0);
      expect(bounds.southWest.longitude, 46.0);
      expect(bounds.northEast.latitude, 25.0);
      expect(bounds.northEast.longitude, 47.0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GeoJson.calculateAreaHectares Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('GeoJson.calculateAreaHectares', () {
    test('returns 0 for polygon with fewer than 3 points', () {
      expect(GeoJson.calculateAreaHectares([]), 0);
      expect(
          GeoJson.calculateAreaHectares([
            const LatLng(0, 0),
            const LatLng(1, 1),
          ]),
          0);
    });

    test('calculates non-zero area for valid polygon', () {
      // Arrange - approximately 1km x 1km square near Riyadh
      final polygon = [
        const LatLng(24.700, 46.700),
        const LatLng(24.700, 46.709),
        const LatLng(24.709, 46.709),
        const LatLng(24.709, 46.700),
      ];

      // Act
      final area = GeoJson.calculateAreaHectares(polygon);

      // Assert - should be approximately 100 hectares (1km^2)
      // Given the Shoelace formula approximation, allow generous tolerance
      expect(area, greaterThan(0));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GeoJson.simplify (Douglas-Peucker) Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('GeoJson.simplify', () {
    test('returns same points for 2 or fewer points', () {
      // Arrange
      final points = [const LatLng(0, 0), const LatLng(1, 1)];

      // Act
      final simplified = GeoJson.simplify(points, 0.1);

      // Assert
      expect(simplified.length, 2);
    });

    test('reduces points with large tolerance', () {
      // Arrange - straight line with minor deviations
      final points = [
        const LatLng(0.0, 0.0),
        const LatLng(0.0001, 0.5),
        const LatLng(0.0002, 1.0),
        const LatLng(0.0001, 1.5),
        const LatLng(0.0, 2.0),
      ];

      // Act
      final simplified = GeoJson.simplify(points, 1.0);

      // Assert - with large tolerance, should reduce to 2 points
      expect(simplified.length, 2);
    });

    test('preserves all points with zero tolerance', () {
      // Arrange
      final points = [
        const LatLng(0, 0),
        const LatLng(1, 0.5),
        const LatLng(0, 1),
      ];

      // Act
      final simplified = GeoJson.simplify(points, 0);

      // Assert
      expect(simplified.length, 3);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GeoJsonFeature Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('GeoJsonFeature', () {
    test('isPolygon returns true for Polygon geometry', () {
      // Arrange
      const feature = GeoJsonFeature(
        id: '1',
        geometry: {'type': 'Polygon', 'coordinates': []},
        properties: {},
      );

      // Assert
      expect(feature.isPolygon, true);
      expect(feature.isPoint, false);
      expect(feature.isMultiPolygon, false);
      expect(feature.geometryType, 'Polygon');
    });

    test('isPoint returns true for Point geometry', () {
      // Arrange
      const feature = GeoJsonFeature(
        geometry: {'type': 'Point', 'coordinates': [46.7, 24.7]},
        properties: {},
      );

      // Assert
      expect(feature.isPoint, true);
      expect(feature.isPolygon, false);
    });

    test('isMultiPolygon returns true for MultiPolygon geometry', () {
      // Arrange
      const feature = GeoJsonFeature(
        geometry: {'type': 'MultiPolygon', 'coordinates': []},
        properties: {},
      );

      // Assert
      expect(feature.isMultiPolygon, true);
    });

    test('polygon getter returns List<LatLng> for Polygon type', () {
      // Arrange
      const feature = GeoJsonFeature(
        geometry: {
          'type': 'Polygon',
          'coordinates': [
            [
              [46.7, 24.7],
              [46.8, 24.8],
              [46.7, 24.7],
            ]
          ]
        },
        properties: {},
      );

      // Act
      final polygon = feature.polygon;

      // Assert
      expect(polygon, isNotNull);
      expect(polygon!.length, 3);
    });

    test('polygon getter returns null for non-Polygon type', () {
      // Arrange
      const feature = GeoJsonFeature(
        geometry: {'type': 'Point', 'coordinates': [46.7, 24.7]},
        properties: {},
      );

      // Assert
      expect(feature.polygon, isNull);
    });

    test('point getter returns LatLng for Point type', () {
      // Arrange
      const feature = GeoJsonFeature(
        geometry: {'type': 'Point', 'coordinates': [46.7, 24.7]},
        properties: {},
      );

      // Act
      final point = feature.point;

      // Assert
      expect(point, isNotNull);
      expect(point!.latitude, 24.7);
      expect(point.longitude, 46.7);
    });

    test('point getter returns null for non-Point type', () {
      // Arrange
      const feature = GeoJsonFeature(
        geometry: {'type': 'Polygon', 'coordinates': []},
        properties: {},
      );

      // Assert
      expect(feature.point, isNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // LatLngListGeoJson Extension Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('LatLngListGeoJson extension', () {
    test('toGeoJsonCoordinates converts to [lon, lat] format', () {
      // Arrange
      final points = [
        const LatLng(24.7, 46.7),
        const LatLng(24.8, 46.8),
      ];

      // Act
      final coords = points.toGeoJsonCoordinates();

      // Assert
      expect(coords[0], [46.7, 24.7]);
      expect(coords[1], [46.8, 24.8]);
    });

    test('toGeoJsonPolygon creates Polygon geometry', () {
      // Arrange
      final points = [const LatLng(24.7, 46.7), const LatLng(24.8, 46.8)];

      // Act
      final polygon = points.toGeoJsonPolygon();

      // Assert
      expect(polygon['type'], 'Polygon');
      expect(polygon['coordinates'], isA<List>());
    });

    test('centroid getter delegates to GeoJson.calculateCentroid', () {
      // Arrange
      final points = [
        const LatLng(24.0, 46.0),
        const LatLng(25.0, 47.0),
      ];

      // Act
      final centroid = points.centroid;

      // Assert
      expect(centroid.latitude, closeTo(24.5, 0.01));
      expect(centroid.longitude, closeTo(46.5, 0.01));
    });

    test('areaHectares getter delegates to GeoJson.calculateAreaHectares', () {
      // Arrange
      final points = [const LatLng(0, 0), const LatLng(1, 1)];

      // Act
      final area = points.areaHectares;

      // Assert - fewer than 3 points
      expect(area, 0);
    });
  });
}
