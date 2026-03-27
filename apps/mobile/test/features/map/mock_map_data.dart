/// Mock Map Data for Testing
/// بيانات وهمية للخرائط للاختبارات
///
/// This file contains mock GeoJSON data, coordinates, and other
/// test fixtures for map-related unit tests.
library;

import 'dart:convert';
import 'dart:typed_data';

/// Mock GeoJSON data for testing
class MockGeoJsonData {
  /// Valid polygon feature representing a field in Yemen
  static const Map<String, dynamic> validPolygonFeature = {
    'type': 'Feature',
    'id': 'field-001',
    'properties': {
      'name': 'حقل القمح الشمالي',
      'name_en': 'North Wheat Field',
      'crop_type': 'wheat',
      'area_hectares': 5.2,
      'status': 'active',
    },
    'geometry': {
      'type': 'Polygon',
      'coordinates': [
        [
          [44.1910, 15.3694], // lon, lat - Sanaa area
          [44.1950, 15.3694],
          [44.1950, 15.3734],
          [44.1910, 15.3734],
          [44.1910, 15.3694], // Closed polygon
        ],
      ],
    },
  };

  /// Valid point feature representing a field centroid
  static const Map<String, dynamic> validPointFeature = {
    'type': 'Feature',
    'id': 'centroid-001',
    'properties': {
      'name': 'مركز الحقل',
      'type': 'centroid',
    },
    'geometry': {
      'type': 'Point',
      'coordinates': [44.1930, 15.3714], // lon, lat
    },
  };

  /// Valid FeatureCollection with multiple fields
  static const Map<String, dynamic> validFeatureCollection = {
    'type': 'FeatureCollection',
    'features': [
      validPolygonFeature,
      {
        'type': 'Feature',
        'id': 'field-002',
        'properties': {
          'name': 'حقل الشعير',
          'crop_type': 'barley',
          'area_hectares': 3.8,
        },
        'geometry': {
          'type': 'Polygon',
          'coordinates': [
            [
              [44.2010, 15.3694],
              [44.2050, 15.3694],
              [44.2050, 15.3734],
              [44.2010, 15.3734],
              [44.2010, 15.3694],
            ],
          ],
        },
      },
    ],
  };

  /// MultiPolygon feature (complex field with holes)
  static const Map<String, dynamic> multiPolygonFeature = {
    'type': 'Feature',
    'id': 'field-complex',
    'properties': {
      'name': 'حقل معقد',
      'has_holes': true,
    },
    'geometry': {
      'type': 'MultiPolygon',
      'coordinates': [
        [
          [
            [44.1910, 15.3694],
            [44.1950, 15.3694],
            [44.1950, 15.3734],
            [44.1910, 15.3734],
            [44.1910, 15.3694],
          ],
        ],
        [
          [
            [44.2010, 15.3800],
            [44.2050, 15.3800],
            [44.2050, 15.3840],
            [44.2010, 15.3840],
            [44.2010, 15.3800],
          ],
        ],
      ],
    },
  };

  /// Invalid GeoJSON - missing type
  static const Map<String, dynamic> invalidMissingType = {
    'id': 'invalid-001',
    'properties': {},
    'geometry': {
      'type': 'Point',
      'coordinates': [44.0, 15.0],
    },
  };

  /// Invalid GeoJSON - wrong geometry type
  static const Map<String, dynamic> invalidWrongGeometry = {
    'type': 'Feature',
    'geometry': {
      'type': 'InvalidType',
      'coordinates': [44.0, 15.0],
    },
  };

  /// Invalid GeoJSON - empty coordinates
  static const Map<String, dynamic> invalidEmptyCoordinates = {
    'type': 'Feature',
    'geometry': {
      'type': 'Polygon',
      'coordinates': [],
    },
  };

  /// Invalid GeoJSON - malformed coordinates
  static const Map<String, dynamic> invalidMalformedCoordinates = {
    'type': 'Feature',
    'geometry': {
      'type': 'Polygon',
      'coordinates': [
        [
          'not a number',
          'also not a number',
        ],
      ],
    },
  };

  /// GeoJSON string for parsing tests
  static String get validPolygonJson => jsonEncode(validPolygonFeature);
  static String get validPointJson => jsonEncode(validPointFeature);
  static String get validCollectionJson => jsonEncode(validFeatureCollection);
  static String get invalidJson => '{ invalid json }';
}

/// Mock coordinate data for testing
class MockCoordinates {
  /// Sanaa city center
  static const double sanaaLat = 15.3694;
  static const double sanaaLon = 44.1910;

  /// Aden city center
  static const double adenLat = 12.7855;
  static const double adenLon = 45.0187;

  /// Taiz city center
  static const double taizLat = 13.5789;
  static const double taizLon = 44.0219;

  /// Dhamar region
  static const double dhamarLat = 14.5500;
  static const double dhamarLon = 44.4000;

  /// Field polygon coordinates (closed)
  static const List<List<double>> fieldPolygon = [
    [44.1910, 15.3694],
    [44.1950, 15.3694],
    [44.1950, 15.3734],
    [44.1910, 15.3734],
    [44.1910, 15.3694],
  ];

  /// Field polygon not closed (for testing closure logic)
  static const List<List<double>> fieldPolygonOpen = [
    [44.1910, 15.3694],
    [44.1950, 15.3694],
    [44.1950, 15.3734],
    [44.1910, 15.3734],
  ];

  /// Triangle polygon (minimum valid polygon)
  static const List<List<double>> trianglePolygon = [
    [44.1910, 15.3694],
    [44.1950, 15.3694],
    [44.1930, 15.3734],
    [44.1910, 15.3694],
  ];

  /// Invalid polygon (only 2 points)
  static const List<List<double>> invalidPolygon = [
    [44.1910, 15.3694],
    [44.1950, 15.3694],
  ];

  /// Bounds for Sanaa region
  static const Map<String, double> sanaaBounds = {
    'south': 15.30,
    'west': 44.15,
    'north': 15.45,
    'east': 44.25,
  };

  /// Bounds for Dhamar region
  static const Map<String, double> dhamarBounds = {
    'south': 14.50,
    'west': 44.35,
    'north': 14.60,
    'east': 44.45,
  };
}

/// Mock tile data for testing
class MockTileData {
  /// Sample tile coordinates
  static const int sampleZoom = 10;
  static const int sampleX = 619;
  static const int sampleY = 427;

  /// Tile URL templates
  static const String osmUrlTemplate =
      'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  static const String esriSatelliteTemplate =
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';

  /// Expected tile URL for sample coordinates
  static String get expectedOsmUrl =>
      'https://tile.openstreetmap.org/$sampleZoom/$sampleX/$sampleY.png';

  /// Minimal valid PNG bytes (1x1 transparent pixel)
  static Uint8List get transparentPng => Uint8List.fromList([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, // PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52, // IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
        0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41, // IDAT chunk
        0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
        0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, // IEND chunk
        0x42, 0x60, 0x82,
      ]);

  /// Invalid image bytes
  static Uint8List get invalidImageBytes => Uint8List.fromList([
        0x00, 0x00, 0x00, 0x00, // Not a valid image
      ]);

  /// Tile coordinate to URL helper
  static String buildOsmTileUrl(int z, int x, int y) {
    return osmUrlTemplate
        .replaceAll('{z}', z.toString())
        .replaceAll('{x}', x.toString())
        .replaceAll('{y}', y.toString());
  }

  /// Zoom level test cases
  static const List<int> validZoomLevels = [1, 5, 10, 15, 18];
  static const List<int> invalidZoomLevels = [-1, 0, 25, 100];
}

/// Mock download result data
class MockDownloadData {
  /// Successful download result
  static const Map<String, dynamic> successfulDownload = {
    'totalTiles': 100,
    'downloaded': 95,
    'skipped': 5,
    'failed': 0,
    'cancelled': false,
  };

  /// Partial download result (with failures)
  static const Map<String, dynamic> partialDownload = {
    'totalTiles': 100,
    'downloaded': 80,
    'skipped': 10,
    'failed': 10,
    'cancelled': false,
  };

  /// Cancelled download result
  static const Map<String, dynamic> cancelledDownload = {
    'totalTiles': 100,
    'downloaded': 30,
    'skipped': 0,
    'failed': 0,
    'cancelled': true,
  };

  /// Cache statistics
  static const Map<String, dynamic> cacheStats = {
    'sizeBytes': 52428800, // 50 MB
    'tileCount': 3500,
    'zoomLevels': [10, 11, 12, 13, 14, 15, 16],
  };
}

/// Mock location data for testing
class MockLocationData {
  /// Current location in Sanaa
  static const Map<String, double> sanaaLocation = {
    'latitude': 15.3694,
    'longitude': 44.1910,
    'accuracy': 10.0,
    'altitude': 2250.0,
    'speed': 0.0,
    'heading': 0.0,
  };

  /// Location with poor accuracy
  static const Map<String, double> poorAccuracyLocation = {
    'latitude': 15.3694,
    'longitude': 44.1910,
    'accuracy': 500.0,
    'altitude': 2250.0,
    'speed': 0.0,
    'heading': 0.0,
  };

  /// Moving location (in a vehicle)
  static const Map<String, double> movingLocation = {
    'latitude': 15.3700,
    'longitude': 44.1920,
    'accuracy': 15.0,
    'altitude': 2255.0,
    'speed': 40.0,
    'heading': 45.0,
  };

  /// Invalid location (out of bounds)
  static const Map<String, double> invalidLocation = {
    'latitude': 91.0, // Invalid: latitude must be -90 to 90
    'longitude': 181.0, // Invalid: longitude must be -180 to 180
    'accuracy': -1.0, // Invalid: accuracy must be positive
  };
}

/// Mock map provider configurations
class MockMapProviders {
  static const Map<String, dynamic> osmProvider = {
    'name': 'OpenStreetMap',
    'nameAr': 'خرائط الشوارع المفتوحة',
    'tileUrl': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    'attribution': '(c) OpenStreetMap contributors',
    'maxZoom': 19,
    'requiresApiKey': false,
    'supportsOffline': true,
  };

  static const Map<String, dynamic> esriSatelliteProvider = {
    'name': 'ESRI Satellite',
    'nameAr': 'صور الأقمار الصناعية - ESRI',
    'tileUrl':
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    'attribution': '(c) Esri, Maxar, Earthstar Geographics',
    'maxZoom': 18,
    'requiresApiKey': false,
    'supportsOffline': true,
  };

  static const Map<String, dynamic> mapboxProvider = {
    'name': 'Mapbox Streets',
    'nameAr': 'خرائط ماب بوكس',
    'tileUrl':
        'https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{z}/{x}/{y}?access_token={apiKey}',
    'attribution': '(c) Mapbox (c) OpenStreetMap',
    'maxZoom': 22,
    'requiresApiKey': true,
    'supportsOffline': true,
  };
}
