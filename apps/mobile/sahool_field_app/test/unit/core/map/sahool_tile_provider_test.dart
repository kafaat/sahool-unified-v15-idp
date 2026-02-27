/// SahoolTileProvider Tests
/// اختبارات مزود بلاطات الخريطة
///
/// Tests the P0 performance fix:
/// - Tile provider creation
/// - Cached tile image equality and hashing
/// - toString representation

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/map/sahool_tile_provider.dart';

void main() {
  group('SahoolTileProvider', () {
    test('should create with default store name', () {
      final provider = SahoolTileProvider();
      expect(provider.storeName, 'sahool_map_cache');
    });

    test('should create with custom store name', () {
      final provider = SahoolTileProvider(storeName: 'custom_cache');
      expect(provider.storeName, 'custom_cache');
    });
  });

  group('SahoolCachedTileImage', () {
    test('should implement equality based on url and coordinates', () {
      final a = SahoolCachedTileImage(
        url: 'https://tile.openstreetmap.org/10/512/340.png',
        x: 512,
        y: 340,
        z: 10,
        storeName: 'cache',
        dio: Dio(), // Not used in equality check
      );

      final b = SahoolCachedTileImage(
        url: 'https://tile.openstreetmap.org/10/512/340.png',
        x: 512,
        y: 340,
        z: 10,
        storeName: 'cache',
        dio: Dio(),
      );

      expect(a, equals(b));
      expect(a.hashCode, equals(b.hashCode));
    });

    test('should not be equal with different coordinates', () {
      final a = SahoolCachedTileImage(
        url: 'https://tile.openstreetmap.org/10/512/340.png',
        x: 512,
        y: 340,
        z: 10,
        storeName: 'cache',
        dio: Dio(),
      );

      final b = SahoolCachedTileImage(
        url: 'https://tile.openstreetmap.org/10/512/341.png',
        x: 512,
        y: 341,
        z: 10,
        storeName: 'cache',
        dio: Dio(),
      );

      expect(a, isNot(equals(b)));
    });

    test('should not be equal with different zoom levels', () {
      final a = SahoolCachedTileImage(
        url: 'https://tile.openstreetmap.org/10/512/340.png',
        x: 512,
        y: 340,
        z: 10,
        storeName: 'cache',
        dio: Dio(),
      );

      final b = SahoolCachedTileImage(
        url: 'https://tile.openstreetmap.org/11/512/340.png',
        x: 512,
        y: 340,
        z: 11,
        storeName: 'cache',
        dio: Dio(),
      );

      expect(a, isNot(equals(b)));
    });

    test('toString should include zoom and coordinates', () {
      final tile = SahoolCachedTileImage(
        url: 'https://example.com/10/512/340.png',
        x: 512,
        y: 340,
        z: 10,
        storeName: 'cache',
        dio: Dio(),
      );

      expect(tile.toString(), 'SahoolCachedTileImage(10/512/340)');
    });

    test('hashCode should be consistent with equals', () {
      final tile1 = SahoolCachedTileImage(
        url: 'https://example.com/5/16/11.png',
        x: 16,
        y: 11,
        z: 5,
        storeName: 'cache',
        dio: Dio(),
      );

      final tile2 = SahoolCachedTileImage(
        url: 'https://example.com/5/16/11.png',
        x: 16,
        y: 11,
        z: 5,
        storeName: 'cache',
        dio: Dio(),
      );

      // Equal objects must have equal hash codes
      expect(tile1 == tile2, isTrue);
      expect(tile1.hashCode == tile2.hashCode, isTrue);
    });

    test('identity equality should work', () {
      final tile = SahoolCachedTileImage(
        url: 'https://example.com/5/16/11.png',
        x: 16,
        y: 11,
        z: 5,
        storeName: 'cache',
        dio: Dio(),
      );

      expect(tile == tile, isTrue);
    });
  });
}
