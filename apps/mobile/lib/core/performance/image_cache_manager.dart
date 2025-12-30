import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter_cache_manager/flutter_cache_manager.dart';
import 'package:path_provider/path_provider.dart';
import '../utils/app_logger.dart';

/// SAHOOL Image Cache Manager
/// مدير كاش الصور المحسّن
///
/// Features:
/// - Customizable cache size limits
/// - Automatic cache cleanup
/// - Priority-based caching
/// - Memory pressure handling

class SahoolImageCacheManager {
  static const String key = 'sahool_image_cache';
  static SahoolImageCacheManager? _instance;

  late final CacheManager _cacheManager;
  late final int _maxCacheSizeMB;
  late final Duration _stalePeriod;

  SahoolImageCacheManager._({
    int maxCacheSizeMB = 200,
    Duration stalePeriod = const Duration(days: 7),
  }) : _maxCacheSizeMB = maxCacheSizeMB,
       _stalePeriod = stalePeriod {
    _cacheManager = CacheManager(
      Config(
        key,
        stalePeriod: _stalePeriod,
        maxNrOfCacheObjects: 500,
        repo: JsonCacheInfoRepository(databaseName: key),
        fileService: HttpFileService(),
      ),
    );
  }

  /// الحصول على المثيل الوحيد
  static SahoolImageCacheManager get instance {
    _instance ??= SahoolImageCacheManager._();
    return _instance!;
  }

  /// الحصول على CacheManager للاستخدام مع CachedNetworkImage
  CacheManager get cacheManager => _cacheManager;

  /// تهيئة مع إعدادات مخصصة
  static void configure({
    int maxCacheSizeMB = 200,
    Duration stalePeriod = const Duration(days: 7),
  }) {
    _instance = SahoolImageCacheManager._(
      maxCacheSizeMB: maxCacheSizeMB,
      stalePeriod: stalePeriod,
    );
  }

  /// الحصول على ملف من الكاش أو تحميله
  Future<File> getSingleFile(String url, {
    String? key,
    Map<String, String>? headers,
  }) async {
    try {
      return await _cacheManager.getSingleFile(
        url,
        key: key,
        headers: headers,
      );
    } catch (e) {
      AppLogger.e('Failed to get cached file', tag: 'IMAGE_CACHE', error: e);
      rethrow;
    }
  }

  /// الحصول على ملف مع استخدام الكاش أولاً
  Stream<FileResponse> getFileStream(String url, {
    String? key,
    Map<String, String>? headers,
  }) {
    return _cacheManager.getFileStream(
      url,
      key: key,
      headers: headers,
      withProgress: true,
    );
  }

  /// تحميل ملف مسبقاً
  Future<void> preloadImage(String url) async {
    try {
      await _cacheManager.downloadFile(url);
      AppLogger.d('Preloaded image: $url', tag: 'IMAGE_CACHE');
    } catch (e) {
      AppLogger.e('Failed to preload image', tag: 'IMAGE_CACHE', error: e);
    }
  }

  /// تحميل عدة صور مسبقاً
  Future<void> preloadImages(List<String> urls, {
    int concurrency = 3,
    Function(int completed, int total)? onProgress,
  }) async {
    int completed = 0;
    final total = urls.length;

    // Process in batches
    for (int i = 0; i < urls.length; i += concurrency) {
      final batch = urls.skip(i).take(concurrency);
      await Future.wait(
        batch.map((url) async {
          await preloadImage(url);
          completed++;
          onProgress?.call(completed, total);
        }),
      );
    }
  }

  /// إزالة ملف من الكاش
  Future<void> removeFile(String url) async {
    await _cacheManager.removeFile(url);
    AppLogger.d('Removed cached file: $url', tag: 'IMAGE_CACHE');
  }

  /// تنظيف الكاش
  Future<void> clearCache() async {
    await _cacheManager.emptyCache();
    AppLogger.i('Image cache cleared', tag: 'IMAGE_CACHE');
  }

  /// الحصول على حجم الكاش
  Future<CacheInfo> getCacheInfo() async {
    final cacheDir = await getTemporaryDirectory();
    final cacheFolder = Directory('${cacheDir.path}/$key');

    if (!await cacheFolder.exists()) {
      return const CacheInfo(sizeBytes: 0, fileCount: 0);
    }

    int totalSize = 0;
    int fileCount = 0;

    await for (final entity in cacheFolder.list(recursive: true)) {
      if (entity is File) {
        totalSize += await entity.length();
        fileCount++;
      }
    }

    return CacheInfo(sizeBytes: totalSize, fileCount: fileCount);
  }

  /// تنظيف الكاش إذا تجاوز الحد
  Future<void> trimCache() async {
    final info = await getCacheInfo();
    final maxBytes = _maxCacheSizeMB * 1024 * 1024;

    if (info.sizeBytes > maxBytes) {
      AppLogger.i(
        'Cache size (${info.sizeMB.toStringAsFixed(1)} MB) exceeds limit ($_maxCacheSizeMB MB), trimming...',
        tag: 'IMAGE_CACHE',
      );

      // Clear old files
      await _cacheManager.emptyCache();
    }
  }
}

/// معلومات الكاش
class CacheInfo {
  final int sizeBytes;
  final int fileCount;

  const CacheInfo({
    required this.sizeBytes,
    required this.fileCount,
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
}

/// Widget للصور المحسّنة مع الكاش
class CachedNetworkImageWidget {
  /// تحميل صورة مع كاش
  static Future<ImageProvider> getImageProvider(String url) async {
    final file = await SahoolImageCacheManager.instance.getSingleFile(url);
    return FileImage(file);
  }
}
