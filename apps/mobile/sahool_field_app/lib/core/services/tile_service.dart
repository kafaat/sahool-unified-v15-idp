import 'dart:typed_data';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:latlong2/latlong.dart';
import '../utils/app_logger.dart';
import '../utils/image_compression.dart';

/// خدمة البلاطات الفضائية مع الضغط
/// Satellite Tile Service with Compression
///
/// يوفر جلب ومعالجة وضغط بلاطات الخرائط الفضائية
/// Provides fetching, processing, and compression of satellite map tiles
///
/// Features:
/// - جلب وضغط البلاطات - Fetch and compress tiles
/// - تحميل مسبق للمناطق - Prefetch tiles for areas
/// - إدارة ذكية للكاش - Smart cache management
/// - دعم مستويات التكبير المتعددة - Multiple zoom levels support
class TileService {
  final Dio _dio;
  final String _baseUrl;
  final ImageFormat _preferredFormat;

  /// إنشاء خدمة بلاطات جديدة
  /// Create new tile service
  ///
  /// [baseUrl] رابط خادم البلاطات - Tile server URL
  /// [dio] عميل HTTP (اختياري) - HTTP client (optional)
  /// [preferredFormat] الصيغة المفضلة للصور - Preferred image format
  TileService({
    required String baseUrl,
    Dio? dio,
    ImageFormat preferredFormat = ImageFormat.webp,
  })  : _baseUrl = baseUrl,
        _preferredFormat = preferredFormat,
        _dio = dio ?? Dio();

  /// جلب وضغط بلاطة واحدة
  /// Fetch and compress a single tile
  ///
  /// [url] رابط البلاطة - Tile URL
  /// [zoom] مستوى التكبير - Zoom level
  /// [x] إحداثي X - X coordinate
  /// [y] إحداثي Y - Y coordinate
  /// [quality] جودة الضغط - Compression quality
  Future<TileResult?> fetchAndCompressTile({
    required String url,
    required int zoom,
    required int x,
    required int y,
    double? quality,
  }) async {
    final tileKey = '$zoom/$x/$y';

    try {
      // تحقق من الكاش أولاً - Check cache first
      final cached = await ImageCompressionUtil.getCachedTile(tileKey);
      if (cached != null) {
        return TileResult(
          data: cached,
          zoom: zoom,
          x: x,
          y: y,
          fromCache: true,
          format: _preferredFormat,
        );
      }

      AppLogger.d('Fetching tile: $tileKey', tag: 'TILE_SERVICE');

      // جلب البلاطة من الخادم - Fetch tile from server
      final response = await _dio.get<List<int>>(
        url,
        options: Options(
          responseType: ResponseType.bytes,
          receiveTimeout: const Duration(seconds: 15),
          sendTimeout: const Duration(seconds: 10),
        ),
      );

      if (response.data == null || response.data!.isEmpty) {
        AppLogger.e('Empty tile response: $tileKey', tag: 'TILE_SERVICE');
        return null;
      }

      final originalData = Uint8List.fromList(response.data!);

      // تغيير الحجم إذا لزم الأمر - Resize if necessary
      final resized = await ImageCompressionUtil.resizeForMobile(
        imageData: originalData,
        maxWidth: ImageCompressionUtil.maxTileWidth,
        maxHeight: ImageCompressionUtil.maxTileHeight,
      );

      if (resized == null) {
        AppLogger.e('Failed to resize tile: $tileKey', tag: 'TILE_SERVICE');
        return null;
      }

      // ضغط البلاطة - Compress tile
      final compressed = await ImageCompressionUtil.compressToWebP(
        imageData: resized,
        quality: quality ?? ImageCompressionUtil.mobileQuality,
        format: _preferredFormat,
      );

      if (compressed == null) {
        AppLogger.e('Failed to compress tile: $tileKey', tag: 'TILE_SERVICE');
        return null;
      }

      // احفظ في الكاش - Save to cache
      await ImageCompressionUtil.setCachedTile(
        tileKey: tileKey,
        data: compressed,
        format: _preferredFormat,
      );

      return TileResult(
        data: compressed,
        zoom: zoom,
        x: x,
        y: y,
        fromCache: false,
        format: _preferredFormat,
      );
    } catch (e) {
      AppLogger.e(
        'Failed to fetch tile: $tileKey',
        tag: 'TILE_SERVICE',
        error: e,
      );
      return null;
    }
  }

  /// تحميل مسبق للبلاطات في منطقة محددة
  /// Prefetch tiles for a specific area
  ///
  /// [bounds] حدود المنطقة - Area bounds
  /// [zoomLevels] مستويات التكبير المطلوبة - Required zoom levels
  /// [quality] جودة الضغط - Compression quality
  /// [onProgress] دالة لمتابعة التقدم - Progress callback
  Future<PrefetchResult> prefetchTilesForArea({
    required LatLngBounds bounds,
    required List<int> zoomLevels,
    double? quality,
    Function(int completed, int total)? onProgress,
  }) async {
    final startTime = DateTime.now();
    int totalTiles = 0;
    int successfulTiles = 0;
    int cachedTiles = 0;
    int failedTiles = 0;

    try {
      AppLogger.i(
        'Starting prefetch for ${zoomLevels.length} zoom levels',
        tag: 'TILE_SERVICE',
      );

      // احسب العدد الكلي للبلاطات - Calculate total tiles
      for (final zoom in zoomLevels) {
        final tiles = _getTilesForBounds(bounds, zoom);
        totalTiles += tiles.length;
      }

      AppLogger.i('Total tiles to prefetch: $totalTiles', tag: 'TILE_SERVICE');

      int completed = 0;

      // جلب البلاطات لكل مستوى تكبير - Fetch tiles for each zoom level
      for (final zoom in zoomLevels) {
        final tiles = _getTilesForBounds(bounds, zoom);

        // معالجة البلاطات على دفعات لتجنب الضغط على الذاكرة
        // Process tiles in batches to avoid memory pressure
        const batchSize = 5;
        for (int i = 0; i < tiles.length; i += batchSize) {
          final batch = tiles.skip(i).take(batchSize).toList();

          await Future.wait(
            batch.map((tile) async {
              final url = _buildTileUrl(zoom, tile.x, tile.y);
              final result = await fetchAndCompressTile(
                url: url,
                zoom: zoom,
                x: tile.x,
                y: tile.y,
                quality: quality,
              );

              if (result != null) {
                successfulTiles++;
                if (result.fromCache) {
                  cachedTiles++;
                }
              } else {
                failedTiles++;
              }

              completed++;
              onProgress?.call(completed, totalTiles);
            }),
          );
        }
      }

      final duration = DateTime.now().difference(startTime);

      AppLogger.i(
        'Prefetch completed: $successfulTiles/$totalTiles tiles '
        '($cachedTiles from cache, $failedTiles failed) '
        'in ${duration.inSeconds}s',
        tag: 'TILE_SERVICE',
      );

      return PrefetchResult(
        totalTiles: totalTiles,
        successfulTiles: successfulTiles,
        cachedTiles: cachedTiles,
        failedTiles: failedTiles,
        duration: duration,
      );
    } catch (e) {
      AppLogger.e(
        'Prefetch failed',
        tag: 'TILE_SERVICE',
        error: e,
      );

      return PrefetchResult(
        totalTiles: totalTiles,
        successfulTiles: successfulTiles,
        cachedTiles: cachedTiles,
        failedTiles: failedTiles + (totalTiles - successfulTiles - failedTiles),
        duration: DateTime.now().difference(startTime),
      );
    }
  }

  /// تحميل مسبق للبلاطات حول موقع محدد
  /// Prefetch tiles around a specific location
  ///
  /// [center] الموقع المركزي - Center location
  /// [radiusKm] نصف القطر بالكيلومتر - Radius in kilometers
  /// [zoomLevels] مستويات التكبير - Zoom levels
  /// [quality] جودة الضغط - Compression quality
  /// [onProgress] دالة لمتابعة التقدم - Progress callback
  Future<PrefetchResult> prefetchTilesAroundLocation({
    required LatLng center,
    required double radiusKm,
    required List<int> zoomLevels,
    double? quality,
    Function(int completed, int total)? onProgress,
  }) async {
    // احسب حدود المنطقة من نصف القطر - Calculate bounds from radius
    final bounds = _boundsFromRadius(center, radiusKm);

    return prefetchTilesForArea(
      bounds: bounds,
      zoomLevels: zoomLevels,
      quality: quality,
      onProgress: onProgress,
    );
  }

  /// بناء رابط البلاطة
  /// Build tile URL
  String _buildTileUrl(int zoom, int x, int y) {
    return _baseUrl
        .replaceAll('{z}', zoom.toString())
        .replaceAll('{x}', x.toString())
        .replaceAll('{y}', y.toString());
  }

  /// الحصول على البلاطات في حدود معينة
  /// Get tiles within bounds
  List<TileCoord> _getTilesForBounds(LatLngBounds bounds, int zoom) {
    final tiles = <TileCoord>[];

    // تحويل الإحداثيات الجغرافية إلى إحداثيات البلاطات
    // Convert geographic coordinates to tile coordinates
    final nwTile = _latLngToTile(bounds.northWest, zoom);
    final seTile = _latLngToTile(bounds.southEast, zoom);

    // جمع جميع البلاطات في المنطقة - Collect all tiles in area
    for (int x = nwTile.x; x <= seTile.x; x++) {
      for (int y = nwTile.y; y <= seTile.y; y++) {
        tiles.add(TileCoord(x: x, y: y));
      }
    }

    return tiles;
  }

  /// تحويل إحداثيات جغرافية إلى إحداثيات بلاطة
  /// Convert geographic coordinates to tile coordinates
  TileCoord _latLngToTile(LatLng latLng, int zoom) {
    final scale = 1 << zoom; // 2^zoom
    final worldCoords = _latLngToWorldCoords(latLng);

    return TileCoord(
      x: (worldCoords.x * scale).floor(),
      y: (worldCoords.y * scale).floor(),
    );
  }

  /// تحويل إحداثيات جغرافية إلى إحداثيات عالمية (0-1)
  /// Convert geographic coordinates to world coordinates (0-1)
  _WorldCoord _latLngToWorldCoords(LatLng latLng) {
    const pi = 3.14159265359;
    final lat = latLng.latitude * pi / 180;
    final lng = latLng.longitude;

    final x = (lng + 180) / 360;
    final y = (1 - log(tan(lat) + 1 / cos(lat)) / pi) / 2;

    return _WorldCoord(x: x, y: y);
  }

  /// حساب حدود من موقع ونصف قطر
  /// Calculate bounds from location and radius
  LatLngBounds _boundsFromRadius(LatLng center, double radiusKm) {
    // تقريب بسيط: 1 درجة ≈ 111 كم
    // Simple approximation: 1 degree ≈ 111 km
    final degreeOffset = radiusKm / 111.0;

    return LatLngBounds(
      LatLng(center.latitude - degreeOffset, center.longitude - degreeOffset),
      LatLng(center.latitude + degreeOffset, center.longitude + degreeOffset),
    );
  }

  /// مسح كاش البلاطات
  /// Clear tile cache
  Future<void> clearCache() async {
    await ImageCompressionUtil.clearCache();
  }

  /// الحصول على معلومات الكاش
  /// Get cache information
  Future<CacheSizeInfo> getCacheInfo() async {
    return await ImageCompressionUtil.getCacheSize();
  }
}

/// نتيجة جلب البلاطة
/// Tile fetch result
class TileResult {
  final Uint8List data;
  final int zoom;
  final int x;
  final int y;
  final bool fromCache;
  final ImageFormat format;

  TileResult({
    required this.data,
    required this.zoom,
    required this.x,
    required this.y,
    required this.fromCache,
    required this.format,
  });

  String get tileKey => '$zoom/$x/$y';

  int get sizeBytes => data.length;
  double get sizeKB => sizeBytes / 1024;
  double get sizeMB => sizeBytes / (1024 * 1024);

  @override
  String toString() =>
      'TileResult($tileKey, ${sizeKB.toStringAsFixed(1)} KB, '
      'cached: $fromCache, format: ${format.name})';
}

/// نتيجة التحميل المسبق
/// Prefetch result
class PrefetchResult {
  final int totalTiles;
  final int successfulTiles;
  final int cachedTiles;
  final int failedTiles;
  final Duration duration;

  PrefetchResult({
    required this.totalTiles,
    required this.successfulTiles,
    required this.cachedTiles,
    required this.failedTiles,
    required this.duration,
  });

  double get successRate =>
      totalTiles > 0 ? (successfulTiles / totalTiles) * 100 : 0;

  double get cacheHitRate =>
      successfulTiles > 0 ? (cachedTiles / successfulTiles) * 100 : 0;

  @override
  String toString() =>
      'PrefetchResult($successfulTiles/$totalTiles tiles, '
      '${successRate.toStringAsFixed(1)}% success, '
      '${cacheHitRate.toStringAsFixed(1)}% cached, '
      '${duration.inSeconds}s)';
}

/// إحداثيات البلاطة
/// Tile coordinates
class TileCoord {
  final int x;
  final int y;

  TileCoord({required this.x, required this.y});

  @override
  String toString() => 'TileCoord($x, $y)';

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is TileCoord && other.x == x && other.y == y;
  }

  @override
  int get hashCode => Object.hash(x, y);
}

/// إحداثيات عالمية (داخلية)
/// World coordinates (internal)
class _WorldCoord {
  final double x;
  final double y;

  _WorldCoord({required this.x, required this.y});
}

/// مثال على الاستخدام - Usage Example
///
/// ```dart
/// // إنشاء خدمة البلاطات - Create tile service
/// final tileService = TileService(
///   baseUrl: 'https://tiles.example.com/{z}/{x}/{y}.png',
/// );
///
/// // جلب بلاطة واحدة - Fetch single tile
/// final tile = await tileService.fetchAndCompressTile(
///   url: 'https://tiles.example.com/10/512/384.png',
///   zoom: 10,
///   x: 512,
///   y: 384,
///   quality: ImageCompressionUtil.mobileQuality,
/// );
///
/// // تحميل مسبق لمنطقة - Prefetch area
/// final bounds = LatLngBounds(
///   LatLng(15.0, 44.0),  // جنوب غرب - Southwest
///   LatLng(16.0, 45.0),  // شمال شرق - Northeast
/// );
///
/// final result = await tileService.prefetchTilesForArea(
///   bounds: bounds,
///   zoomLevels: [10, 11, 12],
///   onProgress: (completed, total) {
///     print('Progress: $completed/$total');
///   },
/// );
///
/// print('Downloaded: ${result.successfulTiles} tiles');
/// print('From cache: ${result.cachedTiles} tiles');
/// ```
