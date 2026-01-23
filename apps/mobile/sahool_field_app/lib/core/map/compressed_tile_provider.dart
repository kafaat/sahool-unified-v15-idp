import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import '../services/tile_service.dart';
import '../utils/image_compression.dart';
import '../utils/app_logger.dart';

/// مزود بلاطات الخريطة مع ضغط WebP
/// Map Tile Provider with WebP Compression
///
/// نسخة محسّنة من SahoolTileProvider مع دعم ضغط WebP
/// Enhanced version of SahoolTileProvider with WebP compression support
///
/// Features:
/// - ضغط تلقائي للبلاطات بصيغة WebP - Automatic WebP compression
/// - تخزين محلي ذكي - Smart local caching
/// - تراجع إلى JPEG - JPEG fallback
/// - تحسين الأداء - Performance optimization
class CompressedTileProvider extends TileProvider {
  final TileService _tileService;
  final double quality;
  final bool enableResize;

  /// إنشاء مزود بلاطات مضغوط
  /// Create compressed tile provider
  ///
  /// [baseUrl] رابط خادم البلاطات - Tile server URL
  /// [quality] جودة الضغط (0.0 - 1.0) - Compression quality
  /// [enableResize] تفعيل تصغير الحجم - Enable resizing
  CompressedTileProvider({
    required String baseUrl,
    this.quality = ImageCompressionUtil.mobileQuality,
    this.enableResize = true,
  }) : _tileService = TileService(baseUrl: baseUrl);

  @override
  ImageProvider getImage(TileCoordinates coordinates, TileLayer options) {
    return CompressedTileImage(
      tileService: _tileService,
      coordinates: coordinates,
      options: options,
      quality: quality,
      enableResize: enableResize,
    );
  }

  /// مسح الكاش - Clear cache
  Future<void> clearCache() => _tileService.clearCache();

  /// معلومات الكاش - Cache info
  Future<CacheSizeInfo> getCacheInfo() => _tileService.getCacheInfo();
}

/// ImageProvider مخصص للبلاطات المضغوطة
/// Custom ImageProvider for compressed tiles
class CompressedTileImage extends ImageProvider<CompressedTileImage> {
  final TileService tileService;
  final TileCoordinates coordinates;
  final TileLayer options;
  final double quality;
  final bool enableResize;

  CompressedTileImage({
    required this.tileService,
    required this.coordinates,
    required this.options,
    required this.quality,
    required this.enableResize,
  });

  @override
  Future<CompressedTileImage> obtainKey(ImageConfiguration configuration) {
    return SynchronousFuture<CompressedTileImage>(this);
  }

  @override
  ImageStreamCompleter loadImage(
    CompressedTileImage key,
    ImageDecoderCallback decode,
  ) {
    return MultiFrameImageStreamCompleter(
      codec: _loadAsync(key, decode),
      scale: 1.0,
      debugLabel: 'CompressedTile(${coordinates.z}/${coordinates.x}/${coordinates.y})',
      informationCollector: () => <DiagnosticsNode>[
        DiagnosticsProperty<TileCoordinates>('Coordinates', coordinates),
        DiagnosticsProperty<double>('Quality', quality),
      ],
    );
  }

  Future<ui.Codec> _loadAsync(
    CompressedTileImage key,
    ImageDecoderCallback decode,
  ) async {
    try {
      // بناء رابط البلاطة - Build tile URL
      final url = getTileUrl(coordinates, options);

      // جلب البلاطة مع الضغط - Fetch tile with compression
      final tile = await tileService.fetchAndCompressTile(
        url: url,
        zoom: coordinates.z,
        x: coordinates.x,
        y: coordinates.y,
        quality: quality,
      );

      if (tile != null) {
        final buffer = await ui.ImmutableBuffer.fromUint8List(tile.data);
        return await decode(buffer);
      }

      // فشل التحميل - Load failed
      AppLogger.e(
        'Failed to load compressed tile: ${coordinates.z}/${coordinates.x}/${coordinates.y}',
        tag: 'COMPRESSED_TILE',
      );

      return _transparentTile(decode);
    } catch (e) {
      AppLogger.e(
        'Error loading compressed tile',
        tag: 'COMPRESSED_TILE',
        error: e,
      );
      return _transparentTile(decode);
    }
  }

  /// صورة شفافة احتياطية - Fallback transparent image
  Future<ui.Codec> _transparentTile(ImageDecoderCallback decode) async {
    final Uint8List transparent = Uint8List.fromList([
      0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
      0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
      0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
      0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
      0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,
      0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
      0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
      0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,
      0x42, 0x60, 0x82,
    ]);
    final buffer = await ui.ImmutableBuffer.fromUint8List(transparent);
    return await decode(buffer);
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is CompressedTileImage &&
        other.coordinates == coordinates &&
        other.quality == quality;
  }

  @override
  int get hashCode => Object.hash(coordinates, quality);

  @override
  String toString() =>
      'CompressedTileImage(${coordinates.z}/${coordinates.x}/${coordinates.y}, q=$quality)';
}

/// مثال على الاستخدام في Widget - Usage Example in Widget
///
/// ```dart
/// class SatelliteMapWidget extends StatefulWidget {
///   @override
///   _SatelliteMapWidgetState createState() => _SatelliteMapWidgetState();
/// }
///
/// class _SatelliteMapWidgetState extends State<SatelliteMapWidget> {
///   late CompressedTileProvider _tileProvider;
///
///   @override
///   void initState() {
///     super.initState();
///     _tileProvider = CompressedTileProvider(
///       baseUrl: 'https://tiles.example.com/{z}/{x}/{y}.png',
///       quality: ImageCompressionUtil.mobileQuality,
///       enableResize: true,
///     );
///   }
///
///   @override
///   Widget build(BuildContext context) {
///     return FlutterMap(
///       options: MapOptions(
///         initialCenter: LatLng(15.3694, 44.1910), // صنعاء
///         initialZoom: 12.0,
///       ),
///       children: [
///         TileLayer(
///           urlTemplate: 'https://tiles.example.com/{z}/{x}/{y}.png',
///           tileProvider: _tileProvider,
///           userAgentPackageName: 'com.sahool.field_app',
///         ),
///       ],
///     );
///   }
///
///   @override
///   void dispose() {
///     // تنظيف الموارد
///     super.dispose();
///   }
/// }
/// ```

/// مساعد لإدارة البلاطات المضغوطة
/// Helper for managing compressed tiles
class CompressedTileManager {
  final CompressedTileProvider _provider;

  CompressedTileManager(this._provider);

  /// تحميل مسبق لمنطقة - Prefetch area
  Future<PrefetchResult> prefetchArea({
    required LatLngBounds bounds,
    required List<int> zoomLevels,
    Function(int completed, int total)? onProgress,
  }) async {
    return await _provider._tileService.prefetchTilesForArea(
      bounds: bounds,
      zoomLevels: zoomLevels,
      quality: _provider.quality,
      onProgress: onProgress,
    );
  }

  /// تحميل مسبق حول موقع - Prefetch around location
  Future<PrefetchResult> prefetchAroundLocation({
    required LatLng center,
    required double radiusKm,
    required List<int> zoomLevels,
    Function(int completed, int total)? onProgress,
  }) async {
    return await _provider._tileService.prefetchTilesAroundLocation(
      center: center,
      radiusKm: radiusKm,
      zoomLevels: zoomLevels,
      quality: _provider.quality,
      onProgress: onProgress,
    );
  }

  /// معلومات الكاش - Cache info
  Future<CacheSizeInfo> getCacheInfo() => _provider.getCacheInfo();

  /// مسح الكاش - Clear cache
  Future<void> clearCache() => _provider.clearCache();
}

/// Widget لعرض معلومات الكاش
/// Widget to display cache information
class TileCacheInfoWidget extends StatefulWidget {
  final CompressedTileProvider tileProvider;

  const TileCacheInfoWidget({
    super.key,
    required this.tileProvider,
  });

  @override
  State<TileCacheInfoWidget> createState() => _TileCacheInfoWidgetState();
}

class _TileCacheInfoWidgetState extends State<TileCacheInfoWidget> {
  CacheSizeInfo? _cacheInfo;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _loadCacheInfo();
  }

  Future<void> _loadCacheInfo() async {
    setState(() => _loading = true);
    try {
      final info = await widget.tileProvider.getCacheInfo();
      setState(() => _cacheInfo = info);
    } catch (e) {
      AppLogger.e('Failed to load cache info', tag: 'CACHE_INFO', error: e);
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _clearCache() async {
    setState(() => _loading = true);
    try {
      await widget.tileProvider.clearCache();
      await _loadCacheInfo();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تم مسح الكاش بنجاح - Cache cleared')),
        );
      }
    } catch (e) {
      AppLogger.e('Failed to clear cache', tag: 'CACHE_INFO', error: e);
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_cacheInfo == null) {
      return const Center(child: Text('لا توجد معلومات'));
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'كاش البلاطات - Tile Cache',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            _InfoRow(
              label: 'الحجم - Size',
              value: _cacheInfo!.sizeFormatted,
            ),
            _InfoRow(
              label: 'عدد الملفات - Files',
              value: _cacheInfo!.fileCount.toString(),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                ElevatedButton.icon(
                  onPressed: _loadCacheInfo,
                  icon: const Icon(Icons.refresh),
                  label: const Text('تحديث - Refresh'),
                ),
                const SizedBox(width: 8),
                ElevatedButton.icon(
                  onPressed: _clearCache,
                  icon: const Icon(Icons.delete),
                  label: const Text('مسح - Clear'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
          Text(value),
        ],
      ),
    );
  }
}
