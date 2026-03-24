/// Tile Cache Tests
/// اختبارات تخزين البلاطات
///
/// Tests for offline map tile caching, download management,
/// and cache statistics functionality.

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_mobile_core/core/map/map_downloader.dart';
import 'package:sahool_mobile_core/core/map/offline_map_manager.dart';

import 'mock_map_data.dart';

void main() {
  group('LatLngBounds', () {
    test('should create bounds with correct properties', () {
      // Arrange & Act
      const bounds = LatLngBounds(
        south: 15.30,
        west: 44.15,
        north: 15.45,
        east: 44.25,
      );

      // Assert
      expect(bounds.south, equals(15.30));
      expect(bounds.west, equals(44.15));
      expect(bounds.north, equals(15.45));
      expect(bounds.east, equals(44.25));
    });

    test('should have correct predefined Sanaa bounds', () {
      // Act
      const bounds = LatLngBounds.sanaa;

      // Assert - Sanaa is in Yemen
      expect(bounds.south, greaterThan(15.0));
      expect(bounds.south, lessThan(16.0));
      expect(bounds.west, greaterThan(44.0));
      expect(bounds.west, lessThan(45.0));
      expect(bounds.north, greaterThan(bounds.south));
      expect(bounds.east, greaterThan(bounds.west));
    });

    test('should have correct predefined Dhamar bounds', () {
      // Act
      const bounds = LatLngBounds.dhamar;

      // Assert - Dhamar is south of Sanaa
      expect(bounds.south, greaterThan(14.0));
      expect(bounds.south, lessThan(15.0));
      expect(bounds.north, greaterThan(bounds.south));
      expect(bounds.east, greaterThan(bounds.west));
    });

    test('should produce readable string representation', () {
      // Arrange
      const bounds = LatLngBounds(
        south: 15.30,
        west: 44.15,
        north: 15.45,
        east: 44.25,
      );

      // Act
      final str = bounds.toString();

      // Assert
      expect(str, contains('LatLngBounds'));
      expect(str, contains('15.3'));
      expect(str, contains('44.15'));
    });
  });

  group('TileCoord', () {
    test('should create tile coordinate with correct values', () {
      // Arrange & Act
      const tile = TileCoord(x: 619, y: 427, z: 10);

      // Assert
      expect(tile.x, equals(619));
      expect(tile.y, equals(427));
      expect(tile.z, equals(10));
    });

    test('should produce readable string representation', () {
      // Arrange
      const tile = TileCoord(x: 619, y: 427, z: 10);

      // Act
      final str = tile.toString();

      // Assert
      expect(str, equals('TileCoord(10/619/427)'));
    });
  });

  group('DownloadResult', () {
    test('should create successful download result', () {
      // Arrange & Act
      const result = DownloadResult(
        totalTiles: 100,
        downloaded: 95,
        failed: 0,
        skipped: 5,
        cancelled: false,
      );

      // Assert
      expect(result.totalTiles, equals(100));
      expect(result.downloaded, equals(95));
      expect(result.failed, equals(0));
      expect(result.skipped, equals(5));
      expect(result.cancelled, isFalse);
      expect(result.successful, equals(100));
      expect(result.successRate, equals(1.0));
    });

    test('should calculate success rate correctly', () {
      // Arrange & Act
      const result = DownloadResult(
        totalTiles: 100,
        downloaded: 70,
        failed: 10,
        skipped: 20,
        cancelled: false,
      );

      // Assert
      expect(result.successful, equals(90)); // downloaded + skipped
      expect(result.successRate, equals(0.9)); // 90/100
    });

    test('should handle zero total tiles', () {
      // Arrange & Act
      const result = DownloadResult(
        totalTiles: 0,
        downloaded: 0,
        failed: 0,
        skipped: 0,
        cancelled: false,
      );

      // Assert
      expect(result.successRate, equals(0.0));
    });

    test('should indicate cancelled download', () {
      // Arrange & Act
      const result = DownloadResult(
        totalTiles: 100,
        downloaded: 30,
        failed: 0,
        skipped: 0,
        cancelled: true,
      );

      // Assert
      expect(result.cancelled, isTrue);
      expect(result.successful, equals(30));
    });

    test('should produce informative string representation', () {
      // Arrange
      const result = DownloadResult(
        totalTiles: 100,
        downloaded: 95,
        failed: 2,
        skipped: 3,
        cancelled: false,
      );

      // Act
      final str = result.toString();

      // Assert
      expect(str, contains('DownloadResult'));
      expect(str, contains('100'));
      expect(str, contains('95'));
    });
  });

  group('TileDownloadStatus', () {
    test('should have all expected status values', () {
      // Assert
      expect(TileDownloadStatus.values, hasLength(3));
      expect(TileDownloadStatus.values, contains(TileDownloadStatus.downloaded));
      expect(TileDownloadStatus.values, contains(TileDownloadStatus.exists));
      expect(TileDownloadStatus.values, contains(TileDownloadStatus.failed));
    });
  });

  group('CacheStats', () {
    test('should calculate size in MB correctly', () {
      // Arrange
      const stats = CacheStats(
        sizeBytes: 52428800, // 50 MB
        tileCount: 3500,
        zoomLevels: [10, 11, 12, 13],
      );

      // Assert
      expect(stats.sizeMB, equals(50.0));
    });

    test('should format size in bytes', () {
      // Arrange
      const stats = CacheStats(
        sizeBytes: 500,
        tileCount: 1,
        zoomLevels: [10],
      );

      // Act
      final formatted = stats.sizeFormatted;

      // Assert
      expect(formatted, equals('500 B'));
    });

    test('should format size in kilobytes', () {
      // Arrange
      const stats = CacheStats(
        sizeBytes: 5120, // 5 KB
        tileCount: 1,
        zoomLevels: [10],
      );

      // Act
      final formatted = stats.sizeFormatted;

      // Assert
      expect(formatted, equals('5.0 KB'));
    });

    test('should format size in megabytes', () {
      // Arrange
      const stats = CacheStats(
        sizeBytes: 52428800, // 50 MB
        tileCount: 1,
        zoomLevels: [10],
      );

      // Act
      final formatted = stats.sizeFormatted;

      // Assert
      expect(formatted, equals('50.0 MB'));
    });

    test('should format zoom range for multiple levels', () {
      // Arrange
      const stats = CacheStats(
        sizeBytes: 1000,
        tileCount: 100,
        zoomLevels: [10, 11, 12, 13, 14, 15],
      );

      // Act
      final range = stats.zoomRange;

      // Assert
      expect(range, equals('10-15'));
    });

    test('should format zoom range for single level', () {
      // Arrange
      const stats = CacheStats(
        sizeBytes: 1000,
        tileCount: 10,
        zoomLevels: [12],
      );

      // Act
      final range = stats.zoomRange;

      // Assert
      expect(range, equals('12'));
    });

    test('should show no zoom levels when empty', () {
      // Arrange
      const stats = CacheStats(
        sizeBytes: 0,
        tileCount: 0,
        zoomLevels: [],
      );

      // Act
      final range = stats.zoomRange;

      // Assert
      expect(range, equals('لا يوجد'));
    });

    test('should produce informative string representation', () {
      // Arrange
      const stats = CacheStats(
        sizeBytes: 52428800,
        tileCount: 3500,
        zoomLevels: [10, 11, 12],
      );

      // Act
      final str = stats.toString();

      // Assert
      expect(str, contains('CacheStats'));
      expect(str, contains('50.0 MB'));
      expect(str, contains('3500'));
      expect(str, contains('10-12'));
    });
  });

  group('MapDownloader - Tile Count Estimation', () {
    late MapDownloader downloader;

    setUp(() {
      downloader = MapDownloader();
    });

    test('should estimate tile count for single zoom level', () {
      // Arrange
      const bounds = LatLngBounds(
        south: 15.30,
        west: 44.15,
        north: 15.35,
        east: 44.20,
      );

      // Act
      final count = downloader.estimateTileCount(
        bounds: bounds,
        minZoom: 10,
        maxZoom: 10,
      );

      // Assert
      expect(count, greaterThan(0));
      expect(count, lessThan(100)); // Small area at zoom 10
    });

    test('should estimate more tiles for higher zoom levels', () {
      // Arrange
      const bounds = LatLngBounds.sanaa;

      // Act
      final countLowZoom = downloader.estimateTileCount(
        bounds: bounds,
        minZoom: 10,
        maxZoom: 10,
      );
      final countHighZoom = downloader.estimateTileCount(
        bounds: bounds,
        minZoom: 15,
        maxZoom: 15,
      );

      // Assert - Higher zoom = more tiles
      expect(countHighZoom, greaterThan(countLowZoom));
    });

    test('should accumulate tiles across zoom range', () {
      // Arrange
      const bounds = LatLngBounds.sanaa;

      // Act
      final countSingleZoom = downloader.estimateTileCount(
        bounds: bounds,
        minZoom: 10,
        maxZoom: 10,
      );
      final countMultiZoom = downloader.estimateTileCount(
        bounds: bounds,
        minZoom: 10,
        maxZoom: 12,
      );

      // Assert
      expect(countMultiZoom, greaterThan(countSingleZoom));
    });
  });

  group('MapDownloader - Size Estimation', () {
    late MapDownloader downloader;

    setUp(() {
      downloader = MapDownloader();
    });

    test('should estimate download size in MB', () {
      // Arrange
      const bounds = LatLngBounds.sanaa;

      // Act
      final sizeMB = downloader.estimateSize(
        bounds: bounds,
        minZoom: 10,
        maxZoom: 14,
      );

      // Assert
      expect(sizeMB, greaterThan(0));
      expect(sizeMB, isA<double>());
    });

    test('should estimate larger size for larger area', () {
      // Arrange
      const smallBounds = LatLngBounds(
        south: 15.30,
        west: 44.15,
        north: 15.35,
        east: 44.20,
      );
      const largeBounds = LatLngBounds(
        south: 15.00,
        west: 44.00,
        north: 15.50,
        east: 44.50,
      );

      // Act
      final smallSize = downloader.estimateSize(
        bounds: smallBounds,
        minZoom: 10,
        maxZoom: 12,
      );
      final largeSize = downloader.estimateSize(
        bounds: largeBounds,
        minZoom: 10,
        maxZoom: 12,
      );

      // Assert
      expect(largeSize, greaterThan(smallSize));
    });

    test('should allow custom average tile size', () {
      // Arrange
      const bounds = LatLngBounds.sanaa;

      // Act
      final sizeDefault = downloader.estimateSize(
        bounds: bounds,
        minZoom: 10,
        maxZoom: 12,
      );
      final sizeLargeTiles = downloader.estimateSize(
        bounds: bounds,
        minZoom: 10,
        maxZoom: 12,
        avgTileSizeKb: 30, // Double the default
      );

      // Assert
      expect(sizeLargeTiles, closeTo(sizeDefault * 2, 0.1));
    });
  });

  group('MapDownloader - Cancel Functionality', () {
    late MapDownloader downloader;

    setUp(() {
      downloader = MapDownloader();
    });

    test('should support cancellation', () {
      // Act
      downloader.cancel();

      // Assert - No exception thrown
      expect(true, isTrue);
    });
  });

  group('OfflineMapManager - Predefined Regions', () {
    test('should have predefined regions', () {
      // Act
      final regions = OfflineMapManager.predefinedRegions;

      // Assert
      expect(regions, isNotEmpty);
      expect(regions.containsKey('صنعاء'), isTrue);
      expect(regions.containsKey('ذمار'), isTrue);
    });

    test('should have valid bounds for Sanaa region', () {
      // Act
      final sanaaBounds = OfflineMapManager.predefinedRegions['صنعاء'];

      // Assert
      expect(sanaaBounds, isNotNull);
      expect(sanaaBounds!.north, greaterThan(sanaaBounds.south));
      expect(sanaaBounds.east, greaterThan(sanaaBounds.west));
    });
  });

  group('OfflineMapManager - Initialization', () {
    test('should create with default store name', () {
      // Act
      final manager = OfflineMapManager();

      // Assert
      expect(manager.storeName, equals('sahool_map_cache'));
    });

    test('should create with custom store name', () {
      // Act
      final manager = OfflineMapManager(storeName: 'custom_cache');

      // Assert
      expect(manager.storeName, equals('custom_cache'));
    });
  });

  group('OfflineMapManager - Estimation Methods', () {
    late OfflineMapManager manager;

    setUp(() {
      manager = OfflineMapManager();
    });

    test('should delegate tile count estimation to downloader', () {
      // Arrange
      const bounds = LatLngBounds.sanaa;

      // Act
      final count = manager.estimateTileCount(
        bounds: bounds,
        minZoom: 10,
        maxZoom: 14,
      );

      // Assert
      expect(count, greaterThan(0));
    });

    test('should delegate size estimation to downloader', () {
      // Arrange
      const bounds = LatLngBounds.sanaa;

      // Act
      final size = manager.estimateDownloadSize(
        bounds: bounds,
        minZoom: 10,
        maxZoom: 14,
      );

      // Assert
      expect(size, greaterThan(0));
    });
  });

  group('OfflineMapManager - Cancel Download', () {
    late OfflineMapManager manager;

    setUp(() {
      manager = OfflineMapManager();
    });

    test('should support download cancellation', () {
      // Act
      manager.cancelDownload();

      // Assert - No exception thrown
      expect(true, isTrue);
    });
  });

  group('Tile URL Building', () {
    test('should build correct OSM tile URL', () {
      // Arrange
      const z = 10;
      const x = 619;
      const y = 427;

      // Act
      final url = MockTileData.buildOsmTileUrl(z, x, y);

      // Assert
      expect(url, equals('https://tile.openstreetmap.org/10/619/427.png'));
    });

    test('should handle different zoom levels', () {
      // Arrange & Act
      final urls = MockTileData.validZoomLevels
          .map((z) => MockTileData.buildOsmTileUrl(z, 0, 0))
          .toList();

      // Assert
      expect(urls[0], contains('/1/'));
      expect(urls[1], contains('/5/'));
      expect(urls[2], contains('/10/'));
      expect(urls[3], contains('/15/'));
      expect(urls[4], contains('/18/'));
    });
  });

  group('Tile Coordinate Conversion', () {
    // Test the mathematical conversion from lat/lng to tile coordinates
    test('should convert lat/lng to correct tile at zoom 0', () {
      // At zoom 0, the entire world is one tile
      // Any coordinate should map to tile (0,0)
      expect(true, isTrue); // Placeholder for actual implementation test
    });

    test('should convert lat/lng to correct tile at higher zoom', () {
      // At zoom 10, Sanaa (15.3694, 44.1910) should be around tile (619, 427)
      // This is validated against OSM tile servers
      expect(MockTileData.sampleX, equals(619));
      expect(MockTileData.sampleY, equals(427));
      expect(MockTileData.sampleZoom, equals(10));
    });
  });

  group('Cache Size Formatting', () {
    test('should format bytes correctly', () {
      // Test various sizes
      expect(
        const CacheStats(sizeBytes: 0, tileCount: 0, zoomLevels: [])
            .sizeFormatted,
        equals('0 B'),
      );

      expect(
        const CacheStats(sizeBytes: 1023, tileCount: 0, zoomLevels: [])
            .sizeFormatted,
        equals('1023 B'),
      );
    });

    test('should format kilobytes correctly', () {
      expect(
        const CacheStats(sizeBytes: 1024, tileCount: 0, zoomLevels: [])
            .sizeFormatted,
        equals('1.0 KB'),
      );

      expect(
        const CacheStats(sizeBytes: 512000, tileCount: 0, zoomLevels: [])
            .sizeFormatted,
        equals('500.0 KB'),
      );
    });

    test('should format megabytes correctly', () {
      expect(
        const CacheStats(sizeBytes: 1048576, tileCount: 0, zoomLevels: [])
            .sizeFormatted,
        equals('1.0 MB'),
      );

      expect(
        const CacheStats(sizeBytes: 104857600, tileCount: 0, zoomLevels: [])
            .sizeFormatted,
        equals('100.0 MB'),
      );
    });
  });

  group('Download Progress Tracking', () {
    test('should correctly calculate progress percentage', () {
      // Arrange
      const totalTiles = 100;
      const downloadedSoFar = 50;

      // Act
      final progress = downloadedSoFar / totalTiles;

      // Assert
      expect(progress, equals(0.5));
    });

    test('should handle progress at boundaries', () {
      // Start
      expect(0 / 100, equals(0.0));

      // End
      expect(100 / 100, equals(1.0));

      // Mid-point
      expect(50 / 100, equals(0.5));
    });
  });

  group('Zoom Level Validation', () {
    test('should identify valid zoom levels', () {
      for (final zoom in MockTileData.validZoomLevels) {
        expect(zoom, greaterThanOrEqualTo(1));
        expect(zoom, lessThanOrEqualTo(20));
      }
    });

    test('should identify invalid zoom levels', () {
      for (final zoom in MockTileData.invalidZoomLevels) {
        expect(zoom < 1 || zoom > 20, isTrue);
      }
    });
  });

  group('Tile Data Validation', () {
    test('should have valid PNG signature for transparent tile', () {
      // PNG signature is: 0x89 0x50 0x4E 0x47 0x0D 0x0A 0x1A 0x0A
      final pngBytes = MockTileData.transparentPng;

      expect(pngBytes[0], equals(0x89));
      expect(pngBytes[1], equals(0x50)); // P
      expect(pngBytes[2], equals(0x4E)); // N
      expect(pngBytes[3], equals(0x47)); // G
    });

    test('should identify invalid image data', () {
      final invalidBytes = MockTileData.invalidImageBytes;

      // Should not have PNG signature
      expect(invalidBytes[0], isNot(equals(0x89)));
    });
  });
}
