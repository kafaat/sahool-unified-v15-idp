import 'dart:io';
import 'dart:math' as math;
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';

/// Map Downloader - تحميل مناطق الخريطة للعمل Offline
///
/// يستخدم لتحميل منطقة محددة من الخريطة مسبقاً
/// قبل الذهاب للحقل (مثل Google Maps Offline)
class MapDownloader {
  final Dio _dio;
  final String storeName;
  final String urlTemplate;

  bool _isCancelled = false;

  MapDownloader({
    this.storeName = 'sahool_map_cache',
    this.urlTemplate = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    Dio? dio,
  }) : _dio = dio ?? Dio();

  /// إلغاء التحميل الجاري
  void cancel() {
    _isCancelled = true;
  }

  /// تحميل منطقة محددة بالإحداثيات
  ///
  /// [bounds] حدود المنطقة (minLat, minLng, maxLat, maxLng)
  /// [minZoom] أقل مستوى تكبير (افتراضي: 10)
  /// [maxZoom] أعلى مستوى تكبير (افتراضي: 16)
  /// [onProgress] دالة التقدم (تستقبل نسبة من 0.0 إلى 1.0)
  /// [onTileDownloaded] دالة تُستدعى عند تحميل كل بلاطة
  Future<DownloadResult> downloadRegion({
    required LatLngBounds bounds,
    int minZoom = 10,
    int maxZoom = 16,
    Function(double progress)? onProgress,
    Function(int downloaded, int total)? onTileDownloaded,
  }) async {
    _isCancelled = false;

    final dir = await getApplicationDocumentsDirectory();
    final cachePath = '${dir.path}/$storeName';

    // حساب كل البلاطات المطلوبة
    final List<TileCoord> tiles = [];
    for (int z = minZoom; z <= maxZoom; z++) {
      final tilesAtZoom = _getTilesInBounds(bounds, z);
      tiles.addAll(tilesAtZoom);
    }

    final totalTiles = tiles.length;
    int downloaded = 0;
    int failed = 0;
    int skipped = 0;

    debugPrint('Starting download of $totalTiles tiles...');

    for (final tile in tiles) {
      if (_isCancelled) {
        return DownloadResult(
          totalTiles: totalTiles,
          downloaded: downloaded,
          failed: failed,
          skipped: skipped,
          cancelled: true,
        );
      }

      try {
        final result = await _downloadTile(tile, cachePath);
        if (result == TileDownloadStatus.downloaded) {
          downloaded++;
        } else if (result == TileDownloadStatus.exists) {
          skipped++;
        } else {
          failed++;
        }
      } catch (e) {
        failed++;
        debugPrint('Failed to download tile ${tile.z}/${tile.x}/${tile.y}: $e');
      }

      final progress = (downloaded + skipped + failed) / totalTiles;
      onProgress?.call(progress);
      onTileDownloaded?.call(downloaded + skipped, totalTiles);
    }

    return DownloadResult(
      totalTiles: totalTiles,
      downloaded: downloaded,
      failed: failed,
      skipped: skipped,
      cancelled: false,
    );
  }

  /// تحميل بلاطة واحدة
  Future<TileDownloadStatus> _downloadTile(TileCoord tile, String cachePath) async {
    final zoomDir = Directory('$cachePath/${tile.z}');
    if (!await zoomDir.exists()) {
      await zoomDir.create(recursive: true);
    }

    final file = File('${zoomDir.path}/${tile.x}_${tile.y}.png');

    // تخطي إذا كانت موجودة بالفعل
    if (await file.exists()) {
      return TileDownloadStatus.exists;
    }

    // تحميل البلاطة
    final url = urlTemplate
        .replaceAll('{z}', '${tile.z}')
        .replaceAll('{x}', '${tile.x}')
        .replaceAll('{y}', '${tile.y}');

    final response = await _dio.get<List<int>>(
      url,
      options: Options(
        responseType: ResponseType.bytes,
        receiveTimeout: const Duration(seconds: 15),
        sendTimeout: const Duration(seconds: 5),
        headers: {
          'User-Agent': 'SAHOOL-App/15.3.0',
        },
      ),
    );

    if (response.data == null || response.data!.isEmpty) {
      return TileDownloadStatus.failed;
    }

    await file.writeAsBytes(response.data!);
    return TileDownloadStatus.downloaded;
  }

  /// حساب البلاطات في منطقة معينة لمستوى تكبير محدد
  List<TileCoord> _getTilesInBounds(LatLngBounds bounds, int zoom) {
    final minTile = _latLngToTile(bounds.south, bounds.west, zoom);
    final maxTile = _latLngToTile(bounds.north, bounds.east, zoom);

    final tiles = <TileCoord>[];

    final minX = math.min(minTile.x, maxTile.x);
    final maxX = math.max(minTile.x, maxTile.x);
    final minY = math.min(minTile.y, maxTile.y);
    final maxY = math.max(minTile.y, maxTile.y);

    for (int x = minX; x <= maxX; x++) {
      for (int y = minY; y <= maxY; y++) {
        tiles.add(TileCoord(x: x, y: y, z: zoom));
      }
    }

    return tiles;
  }

  /// تحويل إحداثيات LatLng إلى إحداثيات البلاطة
  TileCoord _latLngToTile(double lat, double lng, int zoom) {
    final n = math.pow(2, zoom).toInt();
    final x = ((lng + 180) / 360 * n).floor();
    final latRad = lat * math.pi / 180;
    final y = ((1 - math.log(math.tan(latRad) + 1 / math.cos(latRad)) / math.pi) / 2 * n).floor();

    return TileCoord(
      x: x.clamp(0, n - 1),
      y: y.clamp(0, n - 1),
      z: zoom,
    );
  }

  /// حساب عدد البلاطات في منطقة (للتقدير قبل التحميل)
  int estimateTileCount({
    required LatLngBounds bounds,
    int minZoom = 10,
    int maxZoom = 16,
  }) {
    int count = 0;
    for (int z = minZoom; z <= maxZoom; z++) {
      count += _getTilesInBounds(bounds, z).length;
    }
    return count;
  }

  /// حساب الحجم التقديري (بالميجابايت)
  double estimateSize({
    required LatLngBounds bounds,
    int minZoom = 10,
    int maxZoom = 16,
    double avgTileSizeKb = 15, // متوسط حجم البلاطة
  }) {
    final count = estimateTileCount(bounds: bounds, minZoom: minZoom, maxZoom: maxZoom);
    return (count * avgTileSizeKb) / 1024; // تحويل إلى MB
  }
}

/// إحداثيات بلاطة
class TileCoord {
  final int x;
  final int y;
  final int z;

  const TileCoord({required this.x, required this.y, required this.z});

  @override
  String toString() => 'TileCoord($z/$x/$y)';
}

/// حدود منطقة جغرافية
class LatLngBounds {
  final double south;
  final double west;
  final double north;
  final double east;

  const LatLngBounds({
    required this.south,
    required this.west,
    required this.north,
    required this.east,
  });

  /// منطقة صنعاء للتجربة
  static const sanaa = LatLngBounds(
    south: 15.30,
    west: 44.15,
    north: 15.45,
    east: 44.25,
  );

  /// منطقة ذمار للتجربة
  static const dhamar = LatLngBounds(
    south: 14.50,
    west: 44.35,
    north: 14.60,
    east: 44.45,
  );

  @override
  String toString() => 'LatLngBounds(S:$south, W:$west, N:$north, E:$east)';
}

/// نتيجة التحميل
class DownloadResult {
  final int totalTiles;
  final int downloaded;
  final int failed;
  final int skipped;
  final bool cancelled;

  const DownloadResult({
    required this.totalTiles,
    required this.downloaded,
    required this.failed,
    required this.skipped,
    required this.cancelled,
  });

  int get successful => downloaded + skipped;
  double get successRate => totalTiles > 0 ? successful / totalTiles : 0;

  @override
  String toString() =>
      'DownloadResult(total: $totalTiles, downloaded: $downloaded, skipped: $skipped, failed: $failed, cancelled: $cancelled)';
}

/// حالة تحميل البلاطة
enum TileDownloadStatus {
  downloaded,
  exists,
  failed,
}
