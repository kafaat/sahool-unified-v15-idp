import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/map/offline_map_manager.dart';

void main() {
  group('CacheStats', () {
    test('should create with required fields', () {
      const stats = CacheStats(
        sizeBytes: 1048576,
        tileCount: 100,
        zoomLevels: [10, 11, 12, 13],
      );

      expect(stats.sizeBytes, 1048576);
      expect(stats.tileCount, 100);
      expect(stats.zoomLevels, [10, 11, 12, 13]);
    });

    test('should calculate size in MB', () {
      const stats = CacheStats(
        sizeBytes: 10485760, // 10 MB
        tileCount: 500,
        zoomLevels: [10, 11, 12],
      );

      expect(stats.sizeMB, 10.0);
    });

    test('should format small sizes in bytes', () {
      const stats = CacheStats(
        sizeBytes: 500,
        tileCount: 1,
        zoomLevels: [10],
      );

      expect(stats.sizeFormatted, '500 B');
    });

    test('should format kilobyte sizes', () {
      const stats = CacheStats(
        sizeBytes: 15360, // 15 KB
        tileCount: 5,
        zoomLevels: [10],
      );

      expect(stats.sizeFormatted, '15.0 KB');
    });

    test('should format megabyte sizes', () {
      const stats = CacheStats(
        sizeBytes: 5242880, // 5 MB
        tileCount: 250,
        zoomLevels: [10, 11],
      );

      expect(stats.sizeFormatted, '5.0 MB');
    });

    test('should show zoom range for multiple levels', () {
      const stats = CacheStats(
        sizeBytes: 1000,
        tileCount: 10,
        zoomLevels: [10, 11, 12, 13, 14, 15, 16],
      );

      expect(stats.zoomRange, '10-16');
    });

    test('should show single zoom level', () {
      const stats = CacheStats(
        sizeBytes: 1000,
        tileCount: 10,
        zoomLevels: [12],
      );

      expect(stats.zoomRange, '12');
    });

    test('should show no zoom levels', () {
      const stats = CacheStats(
        sizeBytes: 0,
        tileCount: 0,
        zoomLevels: [],
      );

      expect(stats.zoomRange, 'لا يوجد');
    });

    test('should have meaningful toString', () {
      const stats = CacheStats(
        sizeBytes: 1048576,
        tileCount: 100,
        zoomLevels: [10, 16],
      );

      final str = stats.toString();
      expect(str, contains('CacheStats'));
      expect(str, contains('1.0 MB'));
      expect(str, contains('100'));
      expect(str, contains('10-16'));
    });

    test('should handle zero bytes', () {
      const stats = CacheStats(
        sizeBytes: 0,
        tileCount: 0,
        zoomLevels: [],
      );

      expect(stats.sizeMB, 0.0);
      expect(stats.sizeFormatted, '0 B');
    });

    test('should handle large sizes correctly', () {
      const stats = CacheStats(
        sizeBytes: 104857600, // 100 MB
        tileCount: 5000,
        zoomLevels: [8, 9, 10, 11, 12, 13, 14, 15, 16],
      );

      expect(stats.sizeMB, 100.0);
      expect(stats.sizeFormatted, '100.0 MB');
      expect(stats.zoomRange, '8-16');
    });
  });
}
