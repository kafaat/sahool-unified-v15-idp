import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:sahool_field_app/features/polygon_editor/utils/geo_utils.dart';

void main() {
  // A roughly 1 hectare field near Sana'a, Yemen
  final testPolygon = [
    const LatLng(15.369, 44.191),
    const LatLng(15.369, 44.192),
    const LatLng(15.370, 44.192),
    const LatLng(15.370, 44.191),
  ];

  group('GeoUtils.distanceMeters', () {
    test('returns 0 for same point', () {
      const p = LatLng(15.369, 44.191);
      expect(GeoUtils.distanceMeters(p, p), closeTo(0, 0.1));
    });

    test('calculates known distance approximately', () {
      // ~111 km per degree of latitude
      const a = LatLng(15.0, 44.0);
      const b = LatLng(16.0, 44.0);
      final dist = GeoUtils.distanceMeters(a, b);
      expect(dist, closeTo(111000, 5000)); // ~111 km
    });
  });

  group('GeoUtils.calculateAreaSqMeters', () {
    test('returns 0 for less than 3 points', () {
      expect(GeoUtils.calculateAreaSqMeters([]), 0);
      expect(GeoUtils.calculateAreaSqMeters([const LatLng(15, 44)]), 0);
      expect(
        GeoUtils.calculateAreaSqMeters([const LatLng(15, 44), const LatLng(15.1, 44.1)]),
        0,
      );
    });

    test('returns positive area for valid polygon', () {
      final area = GeoUtils.calculateAreaSqMeters(testPolygon);
      expect(area, greaterThan(0));
    });
  });

  group('GeoUtils.calculateAreaHectares', () {
    test('converts sqm to hectares', () {
      final ha = GeoUtils.calculateAreaHectares(testPolygon);
      expect(ha, greaterThan(0));
      // Should be a small field
      expect(ha, lessThan(100));
    });
  });

  group('GeoUtils.calculateAreaFeddan', () {
    test('converts to Yemeni feddan (4200 m²)', () {
      final feddan = GeoUtils.calculateAreaFeddan(testPolygon);
      final sqm = GeoUtils.calculateAreaSqMeters(testPolygon);
      expect(feddan, closeTo(sqm / 4200, 0.1));
    });
  });

  group('GeoUtils.calculateCentroid', () {
    test('returns null for empty polygon', () {
      expect(GeoUtils.calculateCentroid([]), isNull);
    });

    test('returns center of polygon', () {
      final centroid = GeoUtils.calculateCentroid(testPolygon);
      expect(centroid, isNotNull);
      // Centroid should be near the center of the bounding box
      expect(centroid!.latitude, closeTo(15.3695, 0.001));
      expect(centroid.longitude, closeTo(44.1915, 0.001));
    });
  });

  group('GeoUtils.calculatePerimeter', () {
    test('returns 0 for less than 2 points', () {
      expect(GeoUtils.calculatePerimeter([]), 0);
      expect(GeoUtils.calculatePerimeter([const LatLng(15, 44)]), 0);
    });

    test('returns positive perimeter for polygon', () {
      final perimeter = GeoUtils.calculatePerimeter(testPolygon);
      expect(perimeter, greaterThan(0));
    });
  });

  group('GeoUtils.isPointInPolygon', () {
    test('returns false for less than 3 points', () {
      expect(GeoUtils.isPointInPolygon(const LatLng(15.369, 44.191), []), false);
    });

    test('returns true for point inside polygon', () {
      const inside = LatLng(15.3695, 44.1915);
      expect(GeoUtils.isPointInPolygon(inside, testPolygon), true);
    });

    test('returns false for point outside polygon', () {
      const outside = LatLng(15.5, 44.5);
      expect(GeoUtils.isPointInPolygon(outside, testPolygon), false);
    });
  });

  group('GeoUtils.getBoundingBox', () {
    test('returns null for empty polygon', () {
      expect(GeoUtils.getBoundingBox([]), isNull);
    });

    test('returns correct bounding box', () {
      final bbox = GeoUtils.getBoundingBox(testPolygon);
      expect(bbox, isNotNull);
      expect(bbox!.min.latitude, 15.369);
      expect(bbox.min.longitude, 44.191);
      expect(bbox.max.latitude, 15.370);
      expect(bbox.max.longitude, 44.192);
    });
  });

  group('GeoUtils.findNearestVertex', () {
    test('returns null for empty vertices', () {
      expect(GeoUtils.findNearestVertex(const LatLng(15, 44), []), isNull);
    });

    test('returns null when all vertices are beyond threshold', () {
      const farPoint = LatLng(16.0, 45.0); // ~160 km away
      expect(GeoUtils.findNearestVertex(farPoint, testPolygon), isNull);
    });

    test('returns index of nearest vertex within threshold', () {
      const nearFirst = LatLng(15.3690, 44.1910);
      final index = GeoUtils.findNearestVertex(
        nearFirst,
        testPolygon,
        thresholdMeters: 50,
      );
      expect(index, 0);
    });
  });

  group('GeoUtils.snapToVertex', () {
    test('returns null for empty vertices', () {
      expect(GeoUtils.snapToVertex(const LatLng(15, 44), []), isNull);
    });

    test('returns vertex when close enough', () {
      const nearPoint = LatLng(15.3690, 44.1910);
      final snapped = GeoUtils.snapToVertex(
        nearPoint,
        testPolygon,
        thresholdMeters: 50,
      );
      expect(snapped, testPolygon[0]);
    });
  });

  group('AreaUnit enum', () {
    test('has 5 area units', () {
      expect(AreaUnit.values, hasLength(5));
    });

    test('squareMeters factor is 1', () {
      expect(AreaUnit.squareMeters.factor, 1);
    });

    test('hectares converts correctly', () {
      expect(AreaUnit.hectares.convert(10000), closeTo(1.0, 0.001));
    });

    test('feddanYemen converts correctly (4200 m²)', () {
      expect(AreaUnit.feddanYemen.convert(4200), closeTo(1.0, 0.01));
    });

    test('has Arabic labels', () {
      expect(AreaUnit.squareMeters.label, 'م²');
      expect(AreaUnit.hectares.label, 'هكتار');
      expect(AreaUnit.feddanYemen.label, 'فدان');
    });
  });

  group('GeoJSON conversion', () {
    test('toGeoJsonPolygon creates valid GeoJSON', () {
      final geojson = toGeoJsonPolygon(testPolygon);
      expect(geojson['type'], 'Polygon');

      final coords = (geojson['coordinates'] as List)[0] as List;
      // Should be closed (first == last)
      expect(coords.length, 5); // 4 points + closing point
      expect(coords.first[0], coords.last[0]);
      expect(coords.first[1], coords.last[1]);

      // GeoJSON format: [longitude, latitude]
      expect(coords[0][0], 44.191); // longitude
      expect(coords[0][1], 15.369); // latitude
    });

    test('toGeoJsonPolygon handles empty list', () {
      final geojson = toGeoJsonPolygon([]);
      expect(geojson['type'], 'Polygon');
      expect((geojson['coordinates'] as List)[0], isEmpty);
    });

    test('fromGeoJsonPolygon parses coordinates', () {
      final geojson = {
        'type': 'Polygon',
        'coordinates': [
          [
            [44.191, 15.369],
            [44.192, 15.369],
            [44.192, 15.370],
            [44.191, 15.370],
            [44.191, 15.369],
          ]
        ],
      };

      final points = fromGeoJsonPolygon(geojson);
      expect(points, hasLength(5));
      expect(points[0].latitude, 15.369);
      expect(points[0].longitude, 44.191);
    });

    test('fromGeoJsonPolygon returns empty for invalid type', () {
      expect(fromGeoJsonPolygon({'type': 'Point'}), isEmpty);
    });

    test('toGeoJsonPoint creates valid Point', () {
      final geojson = toGeoJsonPoint(const LatLng(15.369, 44.191));
      expect(geojson['type'], 'Point');
      expect(geojson['coordinates'][0], 44.191);
      expect(geojson['coordinates'][1], 15.369);
    });

    test('fromGeoJsonPoint parses Point', () {
      final point = fromGeoJsonPoint({
        'type': 'Point',
        'coordinates': [44.191, 15.369],
      });
      expect(point, isNotNull);
      expect(point!.latitude, 15.369);
      expect(point.longitude, 44.191);
    });

    test('fromGeoJsonPoint returns null for invalid', () {
      expect(fromGeoJsonPoint({'type': 'Polygon'}), isNull);
      expect(fromGeoJsonPoint({'type': 'Point', 'coordinates': [44.0]}), isNull);
    });
  });
}
