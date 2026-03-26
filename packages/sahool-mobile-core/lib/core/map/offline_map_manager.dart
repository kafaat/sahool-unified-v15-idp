import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'map_downloader.dart';

/// Offline Map Manager - إدارة الخرائط المحلية
///
/// يوفر:
/// - معلومات عن حجم الكاش
/// - حذف الكاش
/// - قائمة المناطق المحملة
/// - تحميل مناطق جديدة
class OfflineMapManager {
  final String storeName;
  final MapDownloader _downloader;

  OfflineMapManager({
    this.storeName = 'sahool_map_cache',
    MapDownloader? downloader,
  }) : _downloader = downloader ?? MapDownloader(storeName: storeName);

  /// الحصول على مسار مجلد الكاش
  Future<String> getCachePath() async {
    final dir = await getApplicationDocumentsDirectory();
    return '${dir.path}/$storeName';
  }

  /// حساب حجم الكاش الحالي (بالبايت)
  Future<int> getCacheSize() async {
    final cachePath = await getCachePath();
    final cacheDir = Directory(cachePath);

    if (!await cacheDir.exists()) {
      return 0;
    }

    int totalSize = 0;
    await for (final entity in cacheDir.list(recursive: true)) {
      if (entity is File) {
        totalSize += await entity.length();
      }
    }

    return totalSize;
  }

  /// حجم الكاش بالميجابايت
  Future<double> getCacheSizeMB() async {
    final bytes = await getCacheSize();
    return bytes / (1024 * 1024);
  }

  /// حجم الكاش منسق للعرض
  Future<String> getCacheSizeFormatted() async {
    final bytes = await getCacheSize();

    if (bytes < 1024) {
      return '$bytes B';
    } else if (bytes < 1024 * 1024) {
      return '${(bytes / 1024).toStringAsFixed(1)} KB';
    } else if (bytes < 1024 * 1024 * 1024) {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    } else {
      return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(2)} GB';
    }
  }

  /// عدد البلاطات المحفوظة
  Future<int> getTileCount() async {
    final cachePath = await getCachePath();
    final cacheDir = Directory(cachePath);

    if (!await cacheDir.exists()) {
      return 0;
    }

    int count = 0;
    await for (final entity in cacheDir.list(recursive: true)) {
      if (entity is File && entity.path.endsWith('.png')) {
        count++;
      }
    }

    return count;
  }

  /// الحصول على إحصائيات الكاش
  Future<CacheStats> getCacheStats() async {
    final size = await getCacheSize();
    final tileCount = await getTileCount();
    final zoomLevels = await _getZoomLevels();

    return CacheStats(
      sizeBytes: size,
      tileCount: tileCount,
      zoomLevels: zoomLevels,
    );
  }

  /// مستويات التكبير المحفوظة
  Future<List<int>> _getZoomLevels() async {
    final cachePath = await getCachePath();
    final cacheDir = Directory(cachePath);

    if (!await cacheDir.exists()) {
      return [];
    }

    final levels = <int>[];
    await for (final entity in cacheDir.list()) {
      if (entity is Directory) {
        final name = entity.path.split('/').last;
        final zoom = int.tryParse(name);
        if (zoom != null) {
          levels.add(zoom);
        }
      }
    }

    levels.sort();
    return levels;
  }

  /// حذف كل الكاش
  Future<void> clearCache() async {
    final cachePath = await getCachePath();
    final cacheDir = Directory(cachePath);

    if (await cacheDir.exists()) {
      await cacheDir.delete(recursive: true);
      debugPrint('Map cache cleared');
    }
  }

  /// حذف كاش مستوى تكبير محدد
  Future<void> clearZoomLevel(int zoom) async {
    final cachePath = await getCachePath();
    final zoomDir = Directory('$cachePath/$zoom');

    if (await zoomDir.exists()) {
      await zoomDir.delete(recursive: true);
      debugPrint('Cleared zoom level $zoom');
    }
  }

  /// تحميل منطقة محددة
  Future<DownloadResult> downloadRegion({
    required LatLngBounds bounds,
    int minZoom = 10,
    int maxZoom = 16,
    Function(double progress)? onProgress,
  }) {
    return _downloader.downloadRegion(
      bounds: bounds,
      minZoom: minZoom,
      maxZoom: maxZoom,
      onProgress: onProgress,
    );
  }

  /// إلغاء التحميل الجاري
  void cancelDownload() {
    _downloader.cancel();
  }

  /// تقدير عدد البلاطات لمنطقة
  int estimateTileCount({
    required LatLngBounds bounds,
    int minZoom = 10,
    int maxZoom = 16,
  }) {
    return _downloader.estimateTileCount(
      bounds: bounds,
      minZoom: minZoom,
      maxZoom: maxZoom,
    );
  }

  /// تقدير حجم التحميل بالميجابايت
  double estimateDownloadSize({
    required LatLngBounds bounds,
    int minZoom = 10,
    int maxZoom = 16,
  }) {
    return _downloader.estimateSize(
      bounds: bounds,
      minZoom: minZoom,
      maxZoom: maxZoom,
    );
  }

  /// المناطق المعرفة مسبقاً (يمكن توسيعها)
  static const Map<String, LatLngBounds> predefinedRegions = {
    'صنعاء': LatLngBounds.sanaa,
    'ذمار': LatLngBounds.dhamar,
  };
}

/// إحصائيات الكاش
class CacheStats {
  final int sizeBytes;
  final int tileCount;
  final List<int> zoomLevels;

  const CacheStats({
    required this.sizeBytes,
    required this.tileCount,
    required this.zoomLevels,
  });

  double get sizeMB => sizeBytes / (1024 * 1024);

  String get sizeFormatted {
    if (sizeBytes < 1024) {
      return '$sizeBytes B';
    } else if (sizeBytes < 1024 * 1024) {
      return '${(sizeBytes / 1024).toStringAsFixed(1)} KB';
    } else {
      return '${sizeMB.toStringAsFixed(1)} MB';
    }
  }

  String get zoomRange {
    if (zoomLevels.isEmpty) return 'لا يوجد';
    if (zoomLevels.length == 1) return '${zoomLevels.first}';
    return '${zoomLevels.first}-${zoomLevels.last}';
  }

  @override
  String toString() =>
      'CacheStats(size: $sizeFormatted, tiles: $tileCount, zooms: $zoomRange)';
}
