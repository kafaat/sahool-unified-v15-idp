import 'dart:async';
import 'dart:io';
import 'dart:math' as math;
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

/// Enhanced Tile Downloader - تحميل بلاطات الخريطة المحسن
///
/// Features:
/// - Progress tracking - تتبع التقدم
/// - Pause/Resume support - دعم الإيقاف والاستمرار
/// - Batch downloading - التحميل بالدفعات
/// - Download size estimation - تقدير حجم التحميل
/// - Concurrent downloads - التحميل المتوازي
/// - Retry mechanism - آلية إعادة المحاولة
class TileDownloader {
  final Dio _dio;
  final String urlTemplate;
  final int maxConcurrent;
  final int maxRetries;

  // Download state
  bool _isPaused = false;
  bool _isCancelled = false;
  int _downloadedTiles = 0;
  int _failedTiles = 0;
  int _skippedTiles = 0;
  int _totalTiles = 0;

  // Stream controller for progress updates
  final StreamController<DownloadProgress> _progressController =
      StreamController<DownloadProgress>.broadcast();

  /// Stream of download progress updates
  Stream<DownloadProgress> get progressStream => _progressController.stream;

  TileDownloader({
    this.urlTemplate = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    this.maxConcurrent = 4,
    this.maxRetries = 3,
    Dio? dio,
  }) : _dio = dio ??
            Dio(BaseOptions(
              connectTimeout: const Duration(seconds: 10),
              receiveTimeout: const Duration(seconds: 15),
              sendTimeout: const Duration(seconds: 5),
              headers: {'User-Agent': 'SAHOOL-App/16.0.0'},
            ));

  /// Download tiles for a region - تحميل بلاطات منطقة
  ///
  /// [bounds] - Region bounds - حدود المنطقة
  /// [minZoom] - Minimum zoom level (default: 10)
  /// [maxZoom] - Maximum zoom level (default: 16)
  /// [storePath] - Storage path - مسار التخزين
  /// [onProgress] - Progress callback - دالة التقدم
  Future<DownloadResult> downloadRegion({
    required RegionBounds bounds,
    required String storePath,
    int minZoom = 10,
    int maxZoom = 16,
    void Function(DownloadProgress)? onProgress,
  }) async {
    _resetState();

    // Calculate all tiles needed
    final tiles = _calculateTilesForRegion(bounds, minZoom, maxZoom);
    _totalTiles = tiles.length;

    debugPrint(
        'Starting download: $_totalTiles tiles (zoom $minZoom-$maxZoom)');

    // Create store directory
    final storeDir = Directory(storePath);
    if (!await storeDir.exists()) {
      await storeDir.create(recursive: true);
    }

    // Download tiles in batches
    final batches = _splitIntoBatches(tiles, maxConcurrent);

    for (final batch in batches) {
      if (_isCancelled) break;

      // Wait while paused
      while (_isPaused && !_isCancelled) {
        await Future.delayed(const Duration(milliseconds: 100));
      }

      if (_isCancelled) break;

      // Download batch concurrently
      await Future.wait(
        batch.map((tile) => _downloadTile(tile, storePath)),
        eagerError: false,
      );

      // Report progress
      final progress = _createProgressSnapshot();
      _progressController.add(progress);
      onProgress?.call(progress);
    }

    return DownloadResult(
      totalTiles: _totalTiles,
      downloaded: _downloadedTiles,
      failed: _failedTiles,
      skipped: _skippedTiles,
      cancelled: _isCancelled,
      paused: _isPaused,
    );
  }

  /// Download a single tile - تحميل بلاطة واحدة
  Future<TileDownloadStatus> _downloadTile(
      TileCoordinate tile, String storePath) async {
    if (_isCancelled) return TileDownloadStatus.cancelled;

    final zoomDir = Directory('$storePath/${tile.z}');
    final file = File('${zoomDir.path}/${tile.x}_${tile.y}.png');

    // Skip if already exists
    if (await file.exists()) {
      _skippedTiles++;
      return TileDownloadStatus.exists;
    }

    // Ensure zoom directory exists
    if (!await zoomDir.exists()) {
      await zoomDir.create(recursive: true);
    }

    // Download with retry
    for (int attempt = 0; attempt < maxRetries; attempt++) {
      if (_isCancelled) return TileDownloadStatus.cancelled;

      try {
        final url = _buildTileUrl(tile);
        final response = await _dio.get<List<int>>(
          url,
          options: Options(responseType: ResponseType.bytes),
        );

        if (response.data != null && response.data!.isNotEmpty) {
          await file.writeAsBytes(response.data!);
          _downloadedTiles++;
          return TileDownloadStatus.downloaded;
        }
      } catch (e) {
        debugPrint(
            'Tile download failed (attempt ${attempt + 1}): ${tile.z}/${tile.x}/${tile.y} - $e');
        if (attempt == maxRetries - 1) {
          _failedTiles++;
          return TileDownloadStatus.failed;
        }
        await Future.delayed(Duration(milliseconds: 200 * (attempt + 1)));
      }
    }

    return TileDownloadStatus.failed;
  }

  /// Pause the download - إيقاف التحميل مؤقتاً
  void pause() {
    _isPaused = true;
    _progressController.add(_createProgressSnapshot());
  }

  /// Resume the download - استمرار التحميل
  void resume() {
    _isPaused = false;
    _progressController.add(_createProgressSnapshot());
  }

  /// Cancel the download - إلغاء التحميل
  void cancel() {
    _isCancelled = true;
    _progressController.add(_createProgressSnapshot());
  }

  /// Reset download state - إعادة تعيين حالة التحميل
  void _resetState() {
    _isPaused = false;
    _isCancelled = false;
    _downloadedTiles = 0;
    _failedTiles = 0;
    _skippedTiles = 0;
    _totalTiles = 0;
  }

  /// Build tile URL from template - بناء رابط البلاطة
  String _buildTileUrl(TileCoordinate tile) {
    return urlTemplate
        .replaceAll('{z}', '${tile.z}')
        .replaceAll('{x}', '${tile.x}')
        .replaceAll('{y}', '${tile.y}');
  }

  /// Calculate all tiles for a region - حساب كل البلاطات في منطقة
  List<TileCoordinate> _calculateTilesForRegion(
    RegionBounds bounds,
    int minZoom,
    int maxZoom,
  ) {
    final tiles = <TileCoordinate>[];

    for (int z = minZoom; z <= maxZoom; z++) {
      final tilesAtZoom = _getTilesInBounds(bounds, z);
      tiles.addAll(tilesAtZoom);
    }

    return tiles;
  }

  /// Get tiles within bounds at a specific zoom - البلاطات ضمن حدود عند مستوى تكبير
  List<TileCoordinate> _getTilesInBounds(RegionBounds bounds, int zoom) {
    final minTile = _latLngToTile(bounds.south, bounds.west, zoom);
    final maxTile = _latLngToTile(bounds.north, bounds.east, zoom);

    final tiles = <TileCoordinate>[];

    final minX = math.min(minTile.x, maxTile.x);
    final maxX = math.max(minTile.x, maxTile.x);
    final minY = math.min(minTile.y, maxTile.y);
    final maxY = math.max(minTile.y, maxTile.y);

    for (int x = minX; x <= maxX; x++) {
      for (int y = minY; y <= maxY; y++) {
        tiles.add(TileCoordinate(x: x, y: y, z: zoom));
      }
    }

    return tiles;
  }

  /// Convert lat/lng to tile coordinates - تحويل الإحداثيات إلى بلاطة
  TileCoordinate _latLngToTile(double lat, double lng, int zoom) {
    final n = math.pow(2, zoom).toInt();
    final x = ((lng + 180) / 360 * n).floor();
    final latRad = lat * math.pi / 180;
    final y = ((1 -
                math.log(math.tan(latRad) + 1 / math.cos(latRad)) / math.pi) /
            2 *
            n)
        .floor();

    return TileCoordinate(
      x: x.clamp(0, n - 1),
      y: y.clamp(0, n - 1),
      z: zoom,
    );
  }

  /// Split tiles into batches for concurrent download - تقسيم إلى دفعات
  List<List<TileCoordinate>> _splitIntoBatches(
      List<TileCoordinate> tiles, int batchSize) {
    final batches = <List<TileCoordinate>>[];

    for (int i = 0; i < tiles.length; i += batchSize) {
      batches.add(tiles.sublist(
        i,
        math.min(i + batchSize, tiles.length),
      ));
    }

    return batches;
  }

  /// Create a progress snapshot - إنشاء لقطة للتقدم
  DownloadProgress _createProgressSnapshot() {
    return DownloadProgress(
      totalTiles: _totalTiles,
      downloadedTiles: _downloadedTiles,
      failedTiles: _failedTiles,
      skippedTiles: _skippedTiles,
      isPaused: _isPaused,
      isCancelled: _isCancelled,
    );
  }

  /// Estimate tile count for a region - تقدير عدد البلاطات
  int estimateTileCount({
    required RegionBounds bounds,
    int minZoom = 10,
    int maxZoom = 16,
  }) {
    int count = 0;
    for (int z = minZoom; z <= maxZoom; z++) {
      count += _getTilesInBounds(bounds, z).length;
    }
    return count;
  }

  /// Estimate download size in MB - تقدير حجم التحميل بالميجابايت
  DownloadEstimate estimateDownloadSize({
    required RegionBounds bounds,
    int minZoom = 10,
    int maxZoom = 16,
    double avgTileSizeKb = 15.0, // Average tile size in KB
  }) {
    final tileCount = estimateTileCount(
      bounds: bounds,
      minZoom: minZoom,
      maxZoom: maxZoom,
    );

    final sizeKb = tileCount * avgTileSizeKb;
    final sizeMb = sizeKb / 1024;

    // Estimate time (assuming 4 tiles/second on average connection)
    final estimatedSeconds = tileCount / 4;

    return DownloadEstimate(
      tileCount: tileCount,
      estimatedSizeMb: sizeMb,
      estimatedDurationSeconds: estimatedSeconds.toInt(),
      minZoom: minZoom,
      maxZoom: maxZoom,
    );
  }

  /// Dispose resources - تحرير الموارد
  void dispose() {
    _progressController.close();
  }
}

/// Tile coordinate - إحداثيات البلاطة
class TileCoordinate {
  final int x;
  final int y;
  final int z;

  const TileCoordinate({
    required this.x,
    required this.y,
    required this.z,
  });

  @override
  String toString() => 'Tile($z/$x/$y)';

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is TileCoordinate && x == other.x && y == other.y && z == other.z;

  @override
  int get hashCode => Object.hash(x, y, z);
}

/// Region bounds - حدود المنطقة
class RegionBounds {
  final double south;
  final double west;
  final double north;
  final double east;

  const RegionBounds({
    required this.south,
    required this.west,
    required this.north,
    required this.east,
  });

  /// Center latitude - خط العرض المركزي
  double get centerLat => (south + north) / 2;

  /// Center longitude - خط الطول المركزي
  double get centerLng => (west + east) / 2;

  /// Width in degrees - العرض بالدرجات
  double get width => (east - west).abs();

  /// Height in degrees - الارتفاع بالدرجات
  double get height => (north - south).abs();

  /// Create from center and radius - إنشاء من المركز والنصف قطر
  factory RegionBounds.fromCenterRadius({
    required double centerLat,
    required double centerLng,
    required double radiusKm,
  }) {
    // Approximate conversion: 1 degree ~ 111km
    final latDelta = radiusKm / 111.0;
    final lngDelta = radiusKm / (111.0 * math.cos(centerLat * math.pi / 180));

    return RegionBounds(
      south: centerLat - latDelta,
      north: centerLat + latDelta,
      west: centerLng - lngDelta,
      east: centerLng + lngDelta,
    );
  }

  /// Expand bounds by a factor - توسيع الحدود
  RegionBounds expand(double factor) {
    final latExpand = height * (factor - 1) / 2;
    final lngExpand = width * (factor - 1) / 2;

    return RegionBounds(
      south: south - latExpand,
      north: north + latExpand,
      west: west - lngExpand,
      east: east + lngExpand,
    );
  }

  @override
  String toString() =>
      'RegionBounds(S:$south, W:$west, N:$north, E:$east)';

  Map<String, dynamic> toJson() => {
        'south': south,
        'west': west,
        'north': north,
        'east': east,
      };

  factory RegionBounds.fromJson(Map<String, dynamic> json) => RegionBounds(
        south: json['south'] as double,
        west: json['west'] as double,
        north: json['north'] as double,
        east: json['east'] as double,
      );
}

/// Download progress - تقدم التحميل
class DownloadProgress {
  final int totalTiles;
  final int downloadedTiles;
  final int failedTiles;
  final int skippedTiles;
  final bool isPaused;
  final bool isCancelled;

  const DownloadProgress({
    required this.totalTiles,
    required this.downloadedTiles,
    required this.failedTiles,
    required this.skippedTiles,
    required this.isPaused,
    required this.isCancelled,
  });

  /// Total processed tiles - البلاطات المعالجة
  int get processedTiles => downloadedTiles + failedTiles + skippedTiles;

  /// Progress percentage (0.0 to 1.0) - نسبة التقدم
  double get progress => totalTiles > 0 ? processedTiles / totalTiles : 0.0;

  /// Progress percentage (0 to 100) - نسبة التقدم المئوية
  int get progressPercent => (progress * 100).round();

  /// Is download complete - هل انتهى التحميل
  bool get isComplete => processedTiles >= totalTiles;

  /// Success rate - نسبة النجاح
  double get successRate =>
      processedTiles > 0
          ? (downloadedTiles + skippedTiles) / processedTiles
          : 0.0;

  @override
  String toString() =>
      'DownloadProgress($progressPercent% - $processedTiles/$totalTiles)';
}

/// Download result - نتيجة التحميل
class DownloadResult {
  final int totalTiles;
  final int downloaded;
  final int failed;
  final int skipped;
  final bool cancelled;
  final bool paused;

  const DownloadResult({
    required this.totalTiles,
    required this.downloaded,
    required this.failed,
    required this.skipped,
    required this.cancelled,
    required this.paused,
  });

  /// Successful tiles (downloaded + skipped) - البلاطات الناجحة
  int get successful => downloaded + skipped;

  /// Success rate - نسبة النجاح
  double get successRate => totalTiles > 0 ? successful / totalTiles : 0.0;

  /// Is success (>90% success rate) - هل نجح
  bool get isSuccess => successRate >= 0.9 && !cancelled;

  @override
  String toString() =>
      'DownloadResult(total:$totalTiles, downloaded:$downloaded, '
      'skipped:$skipped, failed:$failed, cancelled:$cancelled)';
}

/// Download estimate - تقدير التحميل
class DownloadEstimate {
  final int tileCount;
  final double estimatedSizeMb;
  final int estimatedDurationSeconds;
  final int minZoom;
  final int maxZoom;

  const DownloadEstimate({
    required this.tileCount,
    required this.estimatedSizeMb,
    required this.estimatedDurationSeconds,
    required this.minZoom,
    required this.maxZoom,
  });

  /// Formatted size string - الحجم المنسق
  String get formattedSize {
    if (estimatedSizeMb < 1) {
      return '${(estimatedSizeMb * 1024).toStringAsFixed(0)} KB';
    } else if (estimatedSizeMb < 1024) {
      return '${estimatedSizeMb.toStringAsFixed(1)} MB';
    } else {
      return '${(estimatedSizeMb / 1024).toStringAsFixed(2)} GB';
    }
  }

  /// Formatted duration string - المدة المنسقة
  String get formattedDuration {
    if (estimatedDurationSeconds < 60) {
      return '$estimatedDurationSeconds ثانية';
    } else if (estimatedDurationSeconds < 3600) {
      final minutes = estimatedDurationSeconds ~/ 60;
      return '$minutes دقيقة';
    } else {
      final hours = estimatedDurationSeconds ~/ 3600;
      final minutes = (estimatedDurationSeconds % 3600) ~/ 60;
      return '$hours ساعة و $minutes دقيقة';
    }
  }

  /// Formatted duration in English
  String get formattedDurationEn {
    if (estimatedDurationSeconds < 60) {
      return '$estimatedDurationSeconds seconds';
    } else if (estimatedDurationSeconds < 3600) {
      final minutes = estimatedDurationSeconds ~/ 60;
      return '$minutes minutes';
    } else {
      final hours = estimatedDurationSeconds ~/ 3600;
      final minutes = (estimatedDurationSeconds % 3600) ~/ 60;
      return '$hours hours $minutes minutes';
    }
  }

  @override
  String toString() =>
      'DownloadEstimate(tiles:$tileCount, size:$formattedSize, '
      'duration:$formattedDuration, zoom:$minZoom-$maxZoom)';
}

/// Tile download status - حالة تحميل البلاطة
enum TileDownloadStatus {
  downloaded, // Downloaded successfully - تم التحميل
  exists, // Already exists - موجود مسبقاً
  failed, // Failed to download - فشل التحميل
  cancelled, // Cancelled - تم الإلغاء
}
