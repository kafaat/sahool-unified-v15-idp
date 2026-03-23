import 'dart:math' as math;
import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../domain/ndvi_colormap.dart';
import '../../../core/performance/image_cache_manager.dart';

/// NDVI Tile Layer Configuration
/// Supports COG (Cloud Optimized GeoTIFF) and standard XYZ tiles with offline caching
class NdviTileConfig {
  /// Tile URL template
  /// Use {z}, {x}, {y} for tile coordinates
  /// Use {field_id} for field-specific tiles
  final String urlTemplate;

  /// API key if required
  final String? apiKey;

  /// Additional headers
  final Map<String, String>? headers;

  /// Tile size (default 256)
  final int tileSize;

  /// Opacity (0.0 - 1.0)
  final double opacity;

  /// Min/Max zoom levels
  final int minZoom;
  final int maxZoom;

  const NdviTileConfig({
    required this.urlTemplate,
    this.apiKey,
    this.headers,
    this.tileSize = 256,
    this.opacity = 0.7,
    this.minZoom = 10,
    this.maxZoom = 18,
  });

  /// Default Sentinel Hub NDVI tiles
  static NdviTileConfig sentinelHub({required String apiKey}) {
    return NdviTileConfig(
      urlTemplate: 'https://services.sentinel-hub.com/ogc/wms/'
          '?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap'
          '&LAYERS=NDVI&FORMAT=image/png&TRANSPARENT=true'
          '&WIDTH=256&HEIGHT=256&CRS=EPSG:4326'
          '&BBOX={bbox}',
      apiKey: apiKey,
      headers: {
        'Authorization': 'Bearer $apiKey',
      },
    );
  }

  /// Local SAHOOL backend tiles
  static NdviTileConfig sahoolBackend({required String baseUrl}) {
    return NdviTileConfig(
      urlTemplate: '$baseUrl/api/v1/ndvi/tiles/{z}/{x}/{y}.png',
    );
  }
}

/// NDVI Tile Layer Widget for FlutterMap
/// Supports offline caching for agricultural field monitoring
class NdviTileLayerWidget extends StatelessWidget {
  final NdviTileConfig config;
  final bool visible;
  final bool enableOfflineCache;

  const NdviTileLayerWidget({
    super.key,
    required this.config,
    this.visible = true,
    this.enableOfflineCache = true,
  });

  @override
  Widget build(BuildContext context) {
    if (!visible) return const SizedBox.shrink();

    return Opacity(
      opacity: config.opacity,
      child: TileLayer(
        urlTemplate: config.urlTemplate,
        additionalOptions: {
          if (config.apiKey != null) 'apiKey': config.apiKey!,
        },
        tileDimension: config.tileSize,
        minZoom: config.minZoom.toDouble(),
        maxZoom: config.maxZoom.toDouble(),
        tileProvider: enableOfflineCache
            ? CachedNdviTileProvider(headers: config.headers)
            : null,
        errorTileCallback: (tile, error, stackTrace) {
          // Silent fail for missing tiles
        },
      ),
    );
  }
}

/// Cached NDVI Tile Provider for offline support
/// مزود البلاطات المخزنة مؤقتاً لدعم الوضع غير المتصل
class CachedNdviTileProvider extends TileProvider {
  @override
  final Map<String, String> headers;
  static const String _cacheKeyPrefix = 'ndvi_tile_';

  CachedNdviTileProvider({Map<String, String>? headers})
      : headers = headers ?? const {};

  @override
  ImageProvider getImage(TileCoordinates coordinates, TileLayer options) {
    final url = getTileUrl(coordinates, options);
    return CachedNdviTileImage(
      url: url,
      headers: headers,
      cacheKey:
          '$_cacheKeyPrefix${coordinates.z}_${coordinates.x}_${coordinates.y}',
    );
  }
}

/// Cached NDVI Tile Image Provider
/// مزود صورة بلاطة NDVI المخزنة مؤقتاً
class CachedNdviTileImage extends ImageProvider<CachedNdviTileImage> {
  final String url;
  final Map<String, String>? headers;
  final String cacheKey;

  const CachedNdviTileImage({
    required this.url,
    this.headers,
    required this.cacheKey,
  });

  @override
  ImageStreamCompleter loadImage(
      CachedNdviTileImage key, ImageDecoderCallback decode) {
    return MultiFrameImageStreamCompleter(
      codec: _loadAsync(key, decode),
      scale: 1.0,
    );
  }

  Future<ui.Codec> _loadAsync(
      CachedNdviTileImage key, ImageDecoderCallback decode) async {
    try {
      // Try to get from cache first
      final file = await SahoolImageCacheManager.instance.getSingleFile(
        key.url,
        key: key.cacheKey,
        headers: key.headers,
      );

      final bytes = await file.readAsBytes();
      final buffer = await ui.ImmutableBuffer.fromUint8List(bytes);
      return decode(buffer);
    } catch (e) {
      // Return transparent image on error
      final emptyBytes = _createTransparentPng();
      final buffer = await ui.ImmutableBuffer.fromUint8List(emptyBytes);
      return decode(buffer);
    }
  }

  /// Create a minimal transparent PNG for error fallback
  static Uint8List _createTransparentPng() {
    // 1x1 transparent PNG
    return Uint8List.fromList([
      0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, // PNG signature
      0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52, // IHDR length + type
      0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, // 1x1
      0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, // 8-bit RGBA
      0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41, // IDAT
      0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00, // compressed data
      0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00, // IEND
      0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,
      0x42, 0x60, 0x82,
    ]);
  }

  @override
  Future<CachedNdviTileImage> obtainKey(ImageConfiguration configuration) {
    return Future.value(this);
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is CachedNdviTileImage && other.url == url;
  }

  @override
  int get hashCode => url.hashCode;
}

/// NDVI Image Cache Manager for preloading tiles
/// مدير كاش صور NDVI للتحميل المسبق
class NdviImageCacheManager {
  static final NdviImageCacheManager instance = NdviImageCacheManager._();
  NdviImageCacheManager._();

  /// Preload NDVI tiles for a field's bounding box for offline use
  /// تحميل بلاطات NDVI مسبقاً لمنطقة الحقل
  Future<void> preloadFieldTiles({
    required String urlTemplate,
    required List<LatLng> boundary,
    required int minZoom,
    required int maxZoom,
    Map<String, String>? headers,
    void Function(int completed, int total)? onProgress,
  }) async {
    if (boundary.isEmpty) return;

    // Calculate bounds
    double minLat = boundary.first.latitude;
    double maxLat = boundary.first.latitude;
    double minLng = boundary.first.longitude;
    double maxLng = boundary.first.longitude;

    for (final point in boundary) {
      minLat = point.latitude < minLat ? point.latitude : minLat;
      maxLat = point.latitude > maxLat ? point.latitude : maxLat;
      minLng = point.longitude < minLng ? point.longitude : minLng;
      maxLng = point.longitude > maxLng ? point.longitude : maxLng;
    }

    // Generate tile URLs
    final urls = <String>[];
    for (int z = minZoom; z <= maxZoom; z++) {
      final tiles = _getTilesForBounds(minLat, minLng, maxLat, maxLng, z);
      for (final tile in tiles) {
        final url = urlTemplate
            .replaceAll('{z}', z.toString())
            .replaceAll('{x}', tile.x.toString())
            .replaceAll('{y}', tile.y.toString());
        urls.add(url);
      }
    }

    // Preload tiles
    await SahoolImageCacheManager.instance.preloadImages(
      urls,
      onProgress: onProgress,
    );
  }

  /// Calculate tile coordinates for a bounding box
  List<_TileCoords> _getTilesForBounds(
    double minLat,
    double minLng,
    double maxLat,
    double maxLng,
    int zoom,
  ) {
    final minTile = _latLngToTile(maxLat, minLng, zoom);
    final maxTile = _latLngToTile(minLat, maxLng, zoom);

    final tiles = <_TileCoords>[];
    for (int x = minTile.x; x <= maxTile.x; x++) {
      for (int y = minTile.y; y <= maxTile.y; y++) {
        tiles.add(_TileCoords(x, y, zoom));
      }
    }
    return tiles;
  }

  /// Convert lat/lng to tile coordinates
  _TileCoords _latLngToTile(double lat, double lng, int zoom) {
    final n = 1 << zoom;
    final x = ((lng + 180.0) / 360.0 * n).floor();
    final latRad = lat * 3.141592653589793 / 180.0;
    final y = ((1.0 -
                math.log(math.tan(latRad) + 1.0 / math.tan(latRad).abs()) /
                    3.141592653589793) /
            2.0 *
            n)
        .floor();
    return _TileCoords(x.clamp(0, n - 1), y.clamp(0, n - 1), zoom);
  }

  /// Clear cached NDVI tiles
  /// مسح البلاطات المخزنة مؤقتاً
  Future<void> clearCache() async {
    await SahoolImageCacheManager.instance.clearCache();
  }

  /// Get cache info
  /// الحصول على معلومات الكاش
  Future<CacheInfo> getCacheInfo() async {
    return SahoolImageCacheManager.instance.getCacheInfo();
  }
}

class _TileCoords {
  final int x;
  final int y;
  final int zoom;

  _TileCoords(this.x, this.y, this.zoom);
}

/// NDVI Polygon Overlay - Colors field polygons based on NDVI value
class NdviPolygonLayer extends StatelessWidget {
  final List<NdviFieldData> fields;
  final bool showLabels;
  final double borderWidth;
  final void Function(String fieldId)? onTap;

  const NdviPolygonLayer({
    super.key,
    required this.fields,
    this.showLabels = true,
    this.borderWidth = 2,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // Polygon layer
        PolygonLayer(
          polygons: fields.map((field) {
            final color = NdviColormap.getColor(
              field.ndviValue,
              stops: NdviColormap.yemenStops,
            );

            return Polygon(
              points: field.boundary,
              color: color.withOpacity(0.4),
              borderColor: color,
              borderStrokeWidth: borderWidth,
              label: showLabels ? field.name : null,
              labelStyle: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.bold,
                shadows: [
                  Shadow(
                    color: Colors.black54,
                    blurRadius: 4,
                  ),
                ],
              ),
            );
          }).toList(),
        ),

        // Tap detection layer (using markers at centroids)
        if (onTap != null)
          MarkerLayer(
            markers: fields.map((field) {
              final centroid = _calculateCentroid(field.boundary);
              return Marker(
                point: centroid,
                width: 1,
                height: 1,
                child: GestureDetector(
                  onTap: () => onTap!(field.id),
                  behavior: HitTestBehavior.translucent,
                  child: const SizedBox.expand(),
                ),
              );
            }).toList(),
          ),
      ],
    );
  }

  LatLng _calculateCentroid(List<LatLng> points) {
    if (points.isEmpty) return const LatLng(0, 0);
    double sumLat = 0, sumLng = 0;
    for (final p in points) {
      sumLat += p.latitude;
      sumLng += p.longitude;
    }
    return LatLng(sumLat / points.length, sumLng / points.length);
  }
}

/// Field data with NDVI value
class NdviFieldData {
  final String id;
  final String name;
  final List<LatLng> boundary;
  final double ndviValue;
  final DateTime? lastUpdated;

  const NdviFieldData({
    required this.id,
    required this.name,
    required this.boundary,
    required this.ndviValue,
    this.lastUpdated,
  });
}

/// NDVI Map Layer Control
class NdviLayerControl extends StatelessWidget {
  final bool isNdviVisible;
  final ValueChanged<bool> onVisibilityChanged;
  final double opacity;
  final ValueChanged<double>? onOpacityChanged;

  const NdviLayerControl({
    super.key,
    required this.isNdviVisible,
    required this.onVisibilityChanged,
    this.opacity = 0.7,
    this.onOpacityChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.grass,
                  color: isNdviVisible ? Colors.green : Colors.grey,
                  size: 20,
                ),
                const SizedBox(width: 8),
                const Text(
                  'طبقة NDVI',
                  style: TextStyle(fontWeight: FontWeight.w600),
                ),
                const Spacer(),
                Switch(
                  value: isNdviVisible,
                  onChanged: onVisibilityChanged,
                  activeColor: Colors.green,
                ),
              ],
            ),
            if (isNdviVisible && onOpacityChanged != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Text('الشفافية', style: TextStyle(fontSize: 12)),
                  Expanded(
                    child: Slider(
                      value: opacity,
                      onChanged: onOpacityChanged,
                      activeColor: Colors.green,
                      min: 0.1,
                      max: 1.0,
                    ),
                  ),
                  Text(
                    '${(opacity * 100).toInt()}%',
                    style: const TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}
