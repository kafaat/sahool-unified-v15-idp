/// Map Controller Tests
/// اختبارات وحدة التحكم في الخريطة
///
/// Tests for map providers, tile loading, field polygon rendering,
/// and flutter_map integration.

import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_mobile_core/core/map/map_providers.dart';
import 'package:sahool_mobile_core/core/map/sahool_tile_provider.dart';

import 'mock_map_data.dart';

// Mock classes
class MockDio extends Mock implements Dio {}

class MockResponse<T> extends Mock implements Response<T> {}

void main() {
  group('MapProvider Enum', () {
    test('should have all expected provider types', () {
      expect(MapProvider.values, hasLength(6));
      expect(MapProvider.values, contains(MapProvider.maplibre));
      expect(MapProvider.values, contains(MapProvider.openStreetMap));
      expect(MapProvider.values, contains(MapProvider.mapbox));
      expect(MapProvider.values, contains(MapProvider.google));
      expect(MapProvider.values, contains(MapProvider.sahoolTiles));
      expect(MapProvider.values, contains(MapProvider.satellite));
    });
  });

  group('MapStyle Enum', () {
    test('should have all expected style types', () {
      expect(MapStyle.values, hasLength(8));
      expect(MapStyle.values, contains(MapStyle.streets));
      expect(MapStyle.values, contains(MapStyle.satellite));
      expect(MapStyle.values, contains(MapStyle.satelliteStreets));
      expect(MapStyle.values, contains(MapStyle.outdoors));
      expect(MapStyle.values, contains(MapStyle.light));
      expect(MapStyle.values, contains(MapStyle.dark));
      expect(MapStyle.values, contains(MapStyle.terrain));
      expect(MapStyle.values, contains(MapStyle.agricultural));
    });
  });

  group('MapProviderConfig', () {
    test('should create provider config with all required fields', () {
      // Arrange & Act
      const config = MapProviderConfig(
        provider: MapProvider.openStreetMap,
        name: 'OpenStreetMap',
        nameAr: 'خرائط الشوارع المفتوحة',
        tileUrl: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution: '(c) OpenStreetMap contributors',
      );

      // Assert
      expect(config.provider, equals(MapProvider.openStreetMap));
      expect(config.name, equals('OpenStreetMap'));
      expect(config.nameAr, equals('خرائط الشوارع المفتوحة'));
      expect(config.tileUrl, contains('{z}'));
      expect(config.tileUrl, contains('{x}'));
      expect(config.tileUrl, contains('{y}'));
      expect(config.attribution, isNotEmpty);
    });

    test('should have correct default values', () {
      // Arrange & Act
      const config = MapProviderConfig(
        provider: MapProvider.openStreetMap,
        name: 'Test',
        nameAr: 'اختبار',
        tileUrl: 'https://example.com/{z}/{x}/{y}.png',
        attribution: 'Test',
      );

      // Assert
      expect(config.minZoom, equals(1));
      expect(config.maxZoom, equals(19));
      expect(config.requiresApiKey, isFalse);
      expect(config.supportsOffline, isTrue);
      expect(config.supportsVector, isFalse);
      expect(config.apiKey, isNull);
      expect(config.styleUrl, isNull);
    });

    test('should support custom zoom range', () {
      // Arrange & Act
      const config = MapProviderConfig(
        provider: MapProvider.mapbox,
        name: 'Mapbox',
        nameAr: 'ماب بوكس',
        tileUrl: 'https://api.mapbox.com/...',
        attribution: 'Mapbox',
        minZoom: 3,
        maxZoom: 22,
      );

      // Assert
      expect(config.minZoom, equals(3));
      expect(config.maxZoom, equals(22));
    });

    test('should indicate API key requirement', () {
      // Arrange & Act
      const config = MapProviderConfig(
        provider: MapProvider.mapbox,
        name: 'Mapbox',
        nameAr: 'ماب بوكس',
        tileUrl: 'https://api.mapbox.com/...',
        attribution: 'Mapbox',
        requiresApiKey: true,
        apiKey: 'test-api-key',
      );

      // Assert
      expect(config.requiresApiKey, isTrue);
      expect(config.apiKey, equals('test-api-key'));
    });
  });

  group('SahoolMapProviders - Free Providers', () {
    test('should provide MapLibre OSM configuration', () {
      // Act
      final config = SahoolMapProviders.maplibreOsm;

      // Assert
      expect(config.provider, equals(MapProvider.maplibre));
      expect(config.requiresApiKey, isFalse);
      expect(config.supportsOffline, isTrue);
      expect(config.supportsVector, isTrue);
      expect(config.tileUrl, isNotEmpty);
    });

    test('should provide MapLibre Protomaps configuration', () {
      // Act
      final config = SahoolMapProviders.maplibreProtomaps;

      // Assert
      expect(config.provider, equals(MapProvider.maplibre));
      expect(config.requiresApiKey, isFalse);
      expect(config.tileUrl, contains('protomaps'));
    });

    test('should provide standard OpenStreetMap configuration', () {
      // Act
      final config = SahoolMapProviders.openStreetMap;

      // Assert
      expect(config.provider, equals(MapProvider.openStreetMap));
      expect(config.tileUrl, contains('tile.openstreetmap.org'));
      expect(config.attribution, contains('OpenStreetMap'));
    });

    test('should provide OSM Humanitarian configuration', () {
      // Act
      final config = SahoolMapProviders.osmHot;

      // Assert
      expect(config.provider, equals(MapProvider.openStreetMap));
      expect(config.tileUrl, contains('hot'));
      expect(config.attribution, contains('HOT'));
    });

    test('should provide ESRI Satellite configuration', () {
      // Act
      final config = SahoolMapProviders.esriSatellite;

      // Assert
      expect(config.provider, equals(MapProvider.satellite));
      expect(config.tileUrl, contains('arcgisonline'));
      expect(config.requiresApiKey, isFalse);
    });

    test('should provide Stadia Maps configuration', () {
      // Act
      final config = SahoolMapProviders.stadiaMaps;

      // Assert
      expect(config.tileUrl, contains('stadiamaps'));
      expect(config.maxZoom, equals(20));
    });

    test('should list all free providers', () {
      // Act
      final providers = SahoolMapProviders.freeProviders;

      // Assert
      expect(providers, hasLength(6));
      for (final provider in providers) {
        expect(provider.requiresApiKey, isFalse);
      }
    });
  });

  group('SahoolMapProviders - Default Providers', () {
    test('should have default provider', () {
      // Act
      final defaultProvider = SahoolMapProviders.defaultProvider;

      // Assert
      expect(defaultProvider, isNotNull);
      expect(defaultProvider.requiresApiKey, isFalse);
    });

    test('should have default satellite provider', () {
      // Act
      final satelliteProvider = SahoolMapProviders.defaultSatellite;

      // Assert
      expect(satelliteProvider, isNotNull);
      expect(satelliteProvider.provider, equals(MapProvider.satellite));
    });
  });

  group('SahoolMapProviders - Premium Providers', () {
    test('should create Mapbox Streets config with API key', () {
      // Arrange
      const apiKey = 'pk.test123';

      // Act
      final config = SahoolMapProviders.mapbox(apiKey);

      // Assert
      expect(config.provider, equals(MapProvider.mapbox));
      expect(config.requiresApiKey, isTrue);
      expect(config.apiKey, equals(apiKey));
      expect(config.tileUrl, contains(apiKey));
      expect(config.maxZoom, equals(22));
    });

    test('should create Mapbox Satellite config with API key', () {
      // Arrange
      const apiKey = 'pk.test456';

      // Act
      final config = SahoolMapProviders.mapboxSatellite(apiKey);

      // Assert
      expect(config.provider, equals(MapProvider.mapbox));
      expect(config.tileUrl, contains('satellite'));
      expect(config.tileUrl, contains(apiKey));
    });

    test('should create SAHOOL custom tiles config', () {
      // Arrange
      const baseUrl = 'https://tiles.sahool.app';

      // Act
      final config = SahoolMapProviders.sahoolTiles(baseUrl);

      // Assert
      expect(config.provider, equals(MapProvider.sahoolTiles));
      expect(config.tileUrl, contains(baseUrl));
      expect(config.tileUrl, contains('{z}/{x}/{y}'));
      expect(config.requiresApiKey, isFalse);
    });
  });

  group('YemenMapBounds', () {
    test('should have correct Yemen center coordinates', () {
      // Act
      const center = YemenMapBounds.center;

      // Assert - Yemen is approximately at 15.5N, 48.5E
      expect(center.latitude, closeTo(15.5527, 0.01));
      expect(center.longitude, closeTo(48.5164, 0.01));
    });

    test('should have valid bounding box', () {
      // Assert
      expect(YemenMapBounds.southWest.latitude, lessThan(YemenMapBounds.center.latitude));
      expect(YemenMapBounds.northEast.latitude, greaterThan(YemenMapBounds.center.latitude));
      expect(YemenMapBounds.southWest.longitude, lessThan(YemenMapBounds.center.longitude));
      expect(YemenMapBounds.northEast.longitude, greaterThan(YemenMapBounds.center.longitude));
    });

    test('should have reasonable zoom defaults', () {
      // Assert
      expect(YemenMapBounds.defaultZoom, equals(6.0));
      expect(YemenMapBounds.minZoom, lessThan(YemenMapBounds.defaultZoom));
      expect(YemenMapBounds.maxZoom, greaterThan(YemenMapBounds.defaultZoom));
    });

    test('should have major Yemen cities', () {
      // Act
      final cities = YemenMapBounds.cities;

      // Assert
      expect(cities.keys, contains('sanaa'));
      expect(cities.keys, contains('aden'));
      expect(cities.keys, contains('taiz'));
      expect(cities.keys, contains('hodeidah'));
      expect(cities.keys, contains('mukalla'));
      expect(cities.keys, contains('ibb'));
      expect(cities.keys, contains('dhamar'));
    });

    test('should have Sanaa at correct coordinates', () {
      // Act
      final sanaa = YemenMapBounds.cities['sanaa'];

      // Assert - Sanaa is approximately at 15.37N, 44.19E
      expect(sanaa, isNotNull);
      expect(sanaa!.latitude, closeTo(15.37, 0.1));
      expect(sanaa.longitude, closeTo(44.19, 0.1));
    });

    test('should have Aden at correct coordinates', () {
      // Act
      final aden = YemenMapBounds.cities['aden'];

      // Assert - Aden is approximately at 12.79N, 45.02E
      expect(aden, isNotNull);
      expect(aden!.latitude, closeTo(12.79, 0.1));
      expect(aden.longitude, closeTo(45.02, 0.1));
    });
  });

  group('SahoolTileProvider', () {
    test('should create with default store name', () {
      // Act
      final provider = SahoolTileProvider();

      // Assert
      expect(provider.storeName, equals('sahool_map_cache'));
    });

    test('should create with custom store name', () {
      // Act
      final provider = SahoolTileProvider(storeName: 'custom_cache');

      // Assert
      expect(provider.storeName, equals('custom_cache'));
    });

    test('should accept custom Dio instance', () {
      // Arrange
      final mockDio = MockDio();

      // Act
      final provider = SahoolTileProvider(dio: mockDio);

      // Assert
      expect(provider, isNotNull);
    });
  });

  group('SahoolCachedTileImage', () {
    test('should create with correct parameters', () {
      // Arrange
      final mockDio = MockDio();

      // Act
      final tileImage = SahoolCachedTileImage(
        url: 'https://tile.openstreetmap.org/10/619/427.png',
        x: 619,
        y: 427,
        z: 10,
        storeName: 'test_cache',
        dio: mockDio,
      );

      // Assert
      expect(tileImage.url, contains('619'));
      expect(tileImage.x, equals(619));
      expect(tileImage.y, equals(427));
      expect(tileImage.z, equals(10));
      expect(tileImage.storeName, equals('test_cache'));
    });

    test('should implement equality based on coordinates', () {
      // Arrange
      final mockDio = MockDio();

      final image1 = SahoolCachedTileImage(
        url: 'https://example.com/10/619/427.png',
        x: 619,
        y: 427,
        z: 10,
        storeName: 'cache',
        dio: mockDio,
      );

      final image2 = SahoolCachedTileImage(
        url: 'https://example.com/10/619/427.png',
        x: 619,
        y: 427,
        z: 10,
        storeName: 'cache',
        dio: mockDio,
      );

      final image3 = SahoolCachedTileImage(
        url: 'https://example.com/10/620/427.png',
        x: 620, // Different x
        y: 427,
        z: 10,
        storeName: 'cache',
        dio: mockDio,
      );

      // Assert
      expect(image1, equals(image2));
      expect(image1, isNot(equals(image3)));
    });

    test('should have consistent hash codes', () {
      // Arrange
      final mockDio = MockDio();

      final image1 = SahoolCachedTileImage(
        url: 'https://example.com/10/619/427.png',
        x: 619,
        y: 427,
        z: 10,
        storeName: 'cache',
        dio: mockDio,
      );

      final image2 = SahoolCachedTileImage(
        url: 'https://example.com/10/619/427.png',
        x: 619,
        y: 427,
        z: 10,
        storeName: 'cache',
        dio: mockDio,
      );

      // Assert
      expect(image1.hashCode, equals(image2.hashCode));
    });

    test('should produce readable string representation', () {
      // Arrange
      final mockDio = MockDio();

      final image = SahoolCachedTileImage(
        url: 'https://example.com/10/619/427.png',
        x: 619,
        y: 427,
        z: 10,
        storeName: 'cache',
        dio: mockDio,
      );

      // Act
      final str = image.toString();

      // Assert
      expect(str, equals('SahoolCachedTileImage(10/619/427)'));
    });
  });

  group('Tile URL Generation', () {
    test('should generate correct OSM tile URL', () {
      // Arrange
      const template = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
      const z = 10;
      const x = 619;
      const y = 427;

      // Act
      final url = template
          .replaceAll('{z}', z.toString())
          .replaceAll('{x}', x.toString())
          .replaceAll('{y}', y.toString());

      // Assert
      expect(url, equals('https://tile.openstreetmap.org/10/619/427.png'));
    });

    test('should generate correct ESRI satellite tile URL', () {
      // Arrange
      // Note: ESRI uses {z}/{y}/{x} order
      const template =
          'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
      const z = 10;
      const x = 619;
      const y = 427;

      // Act
      final url = template
          .replaceAll('{z}', z.toString())
          .replaceAll('{x}', x.toString())
          .replaceAll('{y}', y.toString());

      // Assert
      expect(
        url,
        equals(
          'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/10/427/619',
        ),
      );
    });

    test('should handle Mapbox URL with API key', () {
      // Arrange
      const apiKey = 'pk.test123';
      final template = SahoolMapProviders.mapbox(apiKey).tileUrl;

      // Assert
      expect(template, contains(apiKey));
      expect(template, contains('api.mapbox.com'));
    });
  });

  group('Field Polygon Rendering Data', () {
    test('should have valid mock field polygon', () {
      // Act
      final coords = MockCoordinates.fieldPolygon;

      // Assert
      expect(coords, hasLength(5)); // Closed polygon
      expect(coords.first, equals(coords.last)); // First == Last
    });

    test('should convert coordinates to LatLng list', () {
      // Arrange
      final coords = MockCoordinates.fieldPolygon;

      // Act
      final points = coords
          .map((c) => LatLng(c[1], c[0])) // [lon, lat] -> LatLng(lat, lon)
          .toList();

      // Assert
      expect(points, hasLength(5));
      expect(points.first.latitude, closeTo(15.3694, 0.0001));
      expect(points.first.longitude, closeTo(44.1910, 0.0001));
    });

    test('should handle open polygon (auto-close)', () {
      // Arrange
      final openCoords = MockCoordinates.fieldPolygonOpen;

      // Assert
      expect(openCoords, hasLength(4));
      expect(openCoords.first, isNot(equals(openCoords.last)));
    });

    test('should identify invalid polygon (too few points)', () {
      // Arrange
      final invalidCoords = MockCoordinates.invalidPolygon;

      // Assert
      expect(invalidCoords, hasLength(2)); // Not enough for polygon
    });
  });

  group('Map Provider Switching', () {
    test('should be able to switch between free providers', () {
      // Arrange
      final providers = SahoolMapProviders.freeProviders;

      // Assert - All providers should be valid
      for (final provider in providers) {
        expect(provider.tileUrl, isNotEmpty);
        expect(provider.attribution, isNotEmpty);
        expect(provider.name, isNotEmpty);
        expect(provider.nameAr, isNotEmpty);
      }
    });

    test('should distinguish street and satellite providers', () {
      // Arrange
      final streetProvider = SahoolMapProviders.openStreetMap;
      final satelliteProvider = SahoolMapProviders.esriSatellite;

      // Assert
      expect(streetProvider.provider, equals(MapProvider.openStreetMap));
      expect(satelliteProvider.provider, equals(MapProvider.satellite));
    });
  });

  group('Coordinate Validation', () {
    test('should validate Yemen coordinates are in valid range', () {
      // Arrange
      final cities = YemenMapBounds.cities;

      // Assert - All cities should be within valid lat/lng range
      for (final city in cities.values) {
        expect(city.latitude, greaterThanOrEqualTo(-90));
        expect(city.latitude, lessThanOrEqualTo(90));
        expect(city.longitude, greaterThanOrEqualTo(-180));
        expect(city.longitude, lessThanOrEqualTo(180));
      }
    });

    test('should validate mock coordinates are in Yemen', () {
      // Assert - Yemen is roughly 12-20N, 42-55E
      expect(MockCoordinates.sanaaLat, greaterThan(12));
      expect(MockCoordinates.sanaaLat, lessThan(20));
      expect(MockCoordinates.sanaaLon, greaterThan(42));
      expect(MockCoordinates.sanaaLon, lessThan(55));
    });
  });

  group('Attribution Requirements', () {
    test('all free providers should have attribution', () {
      // Arrange
      final providers = SahoolMapProviders.freeProviders;

      // Assert
      for (final provider in providers) {
        expect(provider.attribution, isNotEmpty);
        expect(provider.attribution.length, greaterThan(5));
      }
    });

    test('OSM attribution should mention OpenStreetMap', () {
      // Act
      final osmConfig = SahoolMapProviders.openStreetMap;

      // Assert
      expect(
        osmConfig.attribution.toLowerCase(),
        contains('openstreetmap'),
      );
    });
  });
}
