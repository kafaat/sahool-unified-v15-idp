import 'dart:async';
import 'dart:ui' as ui;

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';

import 'tile_storage.dart';

/// Offline Tile Provider - مزود البلاطات مع دعم العمل بدون اتصال
///
/// Features:
/// - Serve tiles from local storage - تقديم البلاطات من التخزين المحلي
/// - Fallback to network when available - الرجوع للشبكة عند توفرها
/// - Tile request prioritization - ترتيب أولويات طلبات البلاطات
/// - Automatic caching - التخزين المؤقت التلقائي
/// - LRU cache for memory efficiency - كاش LRU لكفاءة الذاكرة
class OfflineTileProvider extends TileProvider {
  final TileStorage _storage;
  final Dio _dio;
  final String urlTemplate;
  final bool cacheNetworkTiles;
  final TilePriority priorityMode;

  // LRU memory cache for frequently accessed tiles
  final _memoryCache = <String, Uint8List>{};
  static const int _maxMemoryCacheSize = 100;

  // Statistics tracking
  int _cacheHits = 0;
  int _cacheMisses = 0;
  int _networkLoads = 0;
  int _failedLoads = 0;

  OfflineTileProvider({
    TileStorage? storage,
    Dio? dio,
    this.urlTemplate = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    this.cacheNetworkTiles = true,
    this.priorityMode = TilePriority.offlineFirst,
  })  : _storage = storage ?? TileStorage(),
        _dio = dio ??
            Dio(BaseOptions(
              connectTimeout: const Duration(seconds: 10),
              receiveTimeout: const Duration(seconds: 15),
              headers: {'User-Agent': 'SAHOOL-App/16.0.0'},
            ));

  @override
  ImageProvider getImage(TileCoordinates coordinates, TileLayer options) {
    final url = getTileUrl(coordinates, options);

    return OfflineCachedTileImage(
      url: url,
      x: coordinates.x,
      y: coordinates.y,
      z: coordinates.z,
      storage: _storage,
      dio: _dio,
      cacheNetworkTiles: cacheNetworkTiles,
      priorityMode: priorityMode,
      memoryCache: _memoryCache,
      onCacheHit: () => _cacheHits++,
      onCacheMiss: () => _cacheMisses++,
      onNetworkLoad: () => _networkLoads++,
      onLoadFailed: () => _failedLoads++,
    );
  }

  /// Get provider statistics - إحصائيات المزود
  TileProviderStats get stats => TileProviderStats(
        cacheHits: _cacheHits,
        cacheMisses: _cacheMisses,
        networkLoads: _networkLoads,
        failedLoads: _failedLoads,
        memoryCacheSize: _memoryCache.length,
      );

  /// Reset statistics - إعادة تعيين الإحصائيات
  void resetStats() {
    _cacheHits = 0;
    _cacheMisses = 0;
    _networkLoads = 0;
    _failedLoads = 0;
  }

  /// Clear memory cache - مسح كاش الذاكرة
  void clearMemoryCache() {
    _memoryCache.clear();
  }

  /// Dispose resources - تحرير الموارد
  @override
  void dispose() {
    _memoryCache.clear();
    super.dispose();
  }
}

/// Cached tile image provider - مزود صور البلاطات المخزنة
class OfflineCachedTileImage extends ImageProvider<OfflineCachedTileImage> {
  final String url;
  final int x, y, z;
  final TileStorage storage;
  final Dio dio;
  final bool cacheNetworkTiles;
  final TilePriority priorityMode;
  final Map<String, Uint8List> memoryCache;
  final VoidCallback? onCacheHit;
  final VoidCallback? onCacheMiss;
  final VoidCallback? onNetworkLoad;
  final VoidCallback? onLoadFailed;

  OfflineCachedTileImage({
    required this.url,
    required this.x,
    required this.y,
    required this.z,
    required this.storage,
    required this.dio,
    required this.cacheNetworkTiles,
    required this.priorityMode,
    required this.memoryCache,
    this.onCacheHit,
    this.onCacheMiss,
    this.onNetworkLoad,
    this.onLoadFailed,
  });

  String get _cacheKey => '$z/$x/$y';

  @override
  Future<OfflineCachedTileImage> obtainKey(ImageConfiguration configuration) {
    return SynchronousFuture<OfflineCachedTileImage>(this);
  }

  @override
  ImageStreamCompleter loadImage(
    OfflineCachedTileImage key,
    ImageDecoderCallback decode,
  ) {
    return MultiFrameImageStreamCompleter(
      codec: _loadAsync(key, decode),
      scale: 1.0,
      debugLabel: 'OfflineTile($z/$x/$y)',
      informationCollector: () => <DiagnosticsNode>[
        DiagnosticsProperty<String>('URL', url),
        DiagnosticsProperty<String>('Tile', '$z/$x/$y'),
        DiagnosticsProperty<TilePriority>('Priority', priorityMode),
      ],
    );
  }

  Future<ui.Codec> _loadAsync(
    OfflineCachedTileImage key,
    ImageDecoderCallback decode,
  ) async {
    try {
      // 1. Check memory cache first (fastest)
      if (memoryCache.containsKey(_cacheKey)) {
        onCacheHit?.call();
        final bytes = memoryCache[_cacheKey]!;
        final buffer = await ui.ImmutableBuffer.fromUint8List(bytes);
        return await decode(buffer);
      }

      // 2. Load based on priority mode
      Uint8List? bytes;

      switch (priorityMode) {
        case TilePriority.offlineFirst:
          bytes = await _loadOfflineFirst();
          break;
        case TilePriority.onlineFirst:
          bytes = await _loadOnlineFirst();
          break;
        case TilePriority.offlineOnly:
          bytes = await _loadOfflineOnly();
          break;
        case TilePriority.onlineOnly:
          bytes = await _loadOnlineOnly();
          break;
      }

      if (bytes != null && bytes.isNotEmpty) {
        // Add to memory cache with LRU eviction
        _addToMemoryCache(bytes);

        final buffer = await ui.ImmutableBuffer.fromUint8List(bytes);
        return await decode(buffer);
      }

      // 3. Return transparent tile if nothing found
      onLoadFailed?.call();
      return _transparentTile(decode);
    } catch (e) {
      debugPrint('Tile load failed ($z/$x/$y): $e');
      onLoadFailed?.call();
      return _transparentTile(decode);
    }
  }

  /// Load offline first, fallback to network - التحميل من المحلي أولاً
  Future<Uint8List?> _loadOfflineFirst() async {
    // Try local storage first
    final localBytes = await storage.getTileFromAnyRegion(z: z, x: x, y: y);
    if (localBytes != null) {
      onCacheHit?.call();
      return localBytes;
    }

    // Fallback to network
    onCacheMiss?.call();
    return _loadFromNetwork();
  }

  /// Load online first, fallback to local - التحميل من الشبكة أولاً
  Future<Uint8List?> _loadOnlineFirst() async {
    // Try network first
    final networkBytes = await _loadFromNetwork();
    if (networkBytes != null) {
      return networkBytes;
    }

    // Fallback to local storage
    onCacheMiss?.call();
    return storage.getTileFromAnyRegion(z: z, x: x, y: y);
  }

  /// Load offline only - التحميل من المحلي فقط
  Future<Uint8List?> _loadOfflineOnly() async {
    final bytes = await storage.getTileFromAnyRegion(z: z, x: x, y: y);
    if (bytes != null) {
      onCacheHit?.call();
    } else {
      onCacheMiss?.call();
    }
    return bytes;
  }

  /// Load online only - التحميل من الشبكة فقط
  Future<Uint8List?> _loadOnlineOnly() async {
    return _loadFromNetwork();
  }

  /// Load tile from network - تحميل البلاطة من الشبكة
  Future<Uint8List?> _loadFromNetwork() async {
    try {
      final response = await dio.get<List<int>>(
        url,
        options: Options(responseType: ResponseType.bytes),
      );

      if (response.data == null || response.data!.isEmpty) {
        return null;
      }

      final bytes = Uint8List.fromList(response.data!);
      onNetworkLoad?.call();

      // Cache the tile if enabled
      if (cacheNetworkTiles) {
        _cacheToStorage(bytes);
      }

      return bytes;
    } catch (e) {
      debugPrint('Network load failed ($z/$x/$y): $e');
      return null;
    }
  }

  /// Cache tile to storage - تخزين البلاطة
  void _cacheToStorage(Uint8List bytes) {
    storage.storeTile(
      regionId: '_network_cache',
      z: z,
      x: x,
      y: y,
      data: bytes,
    ).catchError((e) {
      debugPrint('Failed to cache tile: $e');
    });
  }

  /// Add to memory cache with LRU eviction - إضافة للكاش مع إخلاء LRU
  void _addToMemoryCache(Uint8List bytes) {
    // Remove oldest entries if cache is full
    while (memoryCache.length >= _maxMemoryCacheSize) {
      memoryCache.remove(memoryCache.keys.first);
    }
    memoryCache[_cacheKey] = bytes;
  }

  /// Create a transparent 1x1 pixel tile - إنشاء بلاطة شفافة
  Future<ui.Codec> _transparentTile(ImageDecoderCallback decode) async {
    // PNG transparent 1x1 pixel
    final Uint8List transparent = Uint8List.fromList([
      0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, // PNG signature
      0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52, // IHDR chunk
      0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
      0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
      0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41, // IDAT chunk
      0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
      0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
      0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, // IEND chunk
      0x42, 0x60, 0x82,
    ]);
    final buffer = await ui.ImmutableBuffer.fromUint8List(transparent);
    return decode(buffer);
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is OfflineCachedTileImage &&
        other.url == url &&
        other.z == z &&
        other.x == x &&
        other.y == y;
  }

  @override
  int get hashCode => Object.hash(url, z, x, y);

  @override
  String toString() => 'OfflineCachedTileImage($z/$x/$y)';
}

/// Tile loading priority mode - وضع أولوية تحميل البلاطات
enum TilePriority {
  /// Try offline storage first, then network - المحلي أولاً ثم الشبكة
  offlineFirst,

  /// Try network first, then offline storage - الشبكة أولاً ثم المحلي
  onlineFirst,

  /// Only use offline storage - المحلي فقط
  offlineOnly,

  /// Only use network - الشبكة فقط
  onlineOnly,
}

/// Tile provider statistics - إحصائيات مزود البلاطات
class TileProviderStats {
  final int cacheHits;
  final int cacheMisses;
  final int networkLoads;
  final int failedLoads;
  final int memoryCacheSize;

  const TileProviderStats({
    required this.cacheHits,
    required this.cacheMisses,
    required this.networkLoads,
    required this.failedLoads,
    required this.memoryCacheSize,
  });

  /// Total requests - إجمالي الطلبات
  int get totalRequests => cacheHits + cacheMisses;

  /// Cache hit rate - نسبة إصابة الكاش
  double get cacheHitRate =>
      totalRequests > 0 ? cacheHits / totalRequests : 0.0;

  /// Cache hit rate percentage - نسبة إصابة الكاش المئوية
  int get cacheHitRatePercent => (cacheHitRate * 100).round();

  /// Success rate - نسبة النجاح
  double get successRate {
    final successful = cacheHits + networkLoads;
    final total = successful + failedLoads;
    return total > 0 ? successful / total : 0.0;
  }

  @override
  String toString() =>
      'TileProviderStats(hits: $cacheHits, misses: $cacheMisses, '
      'network: $networkLoads, failed: $failedLoads, '
      'hitRate: $cacheHitRatePercent%)';
}

/// Offline-aware TileLayer configuration helper
/// مساعد تكوين طبقة البلاطات مع دعم العمل بدون اتصال
class OfflineTileLayerOptions {
  /// Create a TileLayer configured for offline-first usage
  /// إنشاء طبقة بلاطات مُكونة للعمل بدون اتصال أولاً
  static TileLayer create({
    TileStorage? storage,
    String urlTemplate = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    TilePriority priorityMode = TilePriority.offlineFirst,
    bool cacheNetworkTiles = true,
    int minZoom = 1,
    int maxZoom = 18,
    int tileSize = 256,
    int keepBuffer = 2,
  }) {
    return TileLayer(
      urlTemplate: urlTemplate,
      tileProvider: OfflineTileProvider(
        storage: storage,
        urlTemplate: urlTemplate,
        priorityMode: priorityMode,
        cacheNetworkTiles: cacheNetworkTiles,
      ),
      minZoom: minZoom.toDouble(),
      maxZoom: maxZoom.toDouble(),
      tileDimension: tileSize,
      keepBuffer: keepBuffer,
    );
  }
}
