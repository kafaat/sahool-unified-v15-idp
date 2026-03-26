import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'tile_downloader.dart';

/// Tile Storage - تخزين بلاطات الخريطة
///
/// Features:
/// - Store tiles in local filesystem - تخزين البلاطات محلياً
/// - Cache management - إدارة الكاش
/// - Expiration handling - معالجة انتهاء الصلاحية
/// - Storage size tracking - تتبع حجم التخزين
/// - Region-based storage organization - تنظيم حسب المناطق
class TileStorage {
  final String storeName;
  late String _basePath;
  bool _initialized = false;

  // Cache metadata keys
  static const String _keyStorageSize = 'tile_storage_size';
  static const String _keyTileCount = 'tile_storage_count';
  static const String _keyLastCleanup = 'tile_storage_last_cleanup';
  static const String _keyRegions = 'tile_storage_regions';

  // Default expiration: 30 days
  static const int defaultExpirationDays = 30;

  TileStorage({this.storeName = 'sahool_offline_maps'});

  /// Initialize storage - تهيئة التخزين
  Future<void> initialize() async {
    if (_initialized) return;

    final dir = await getApplicationDocumentsDirectory();
    _basePath = '${dir.path}/$storeName';

    final storeDir = Directory(_basePath);
    if (!await storeDir.exists()) {
      await storeDir.create(recursive: true);
    }

    _initialized = true;
    debugPrint('TileStorage initialized at: $_basePath');
  }

  /// Get base storage path - الحصول على مسار التخزين الأساسي
  Future<String> getBasePath() async {
    await initialize();
    return _basePath;
  }

  /// Get path for a specific region - مسار منطقة محددة
  Future<String> getRegionPath(String regionId) async {
    await initialize();
    return '$_basePath/regions/$regionId';
  }

  /// Store a tile - تخزين بلاطة
  Future<bool> storeTile({
    required String regionId,
    required int z,
    required int x,
    required int y,
    required Uint8List data,
  }) async {
    try {
      await initialize();

      final regionPath = '$_basePath/regions/$regionId/$z';
      final dir = Directory(regionPath);

      if (!await dir.exists()) {
        await dir.create(recursive: true);
      }

      final file = File('$regionPath/${x}_$y.png');
      await file.writeAsBytes(data);

      return true;
    } catch (e) {
      debugPrint('Failed to store tile: $e');
      return false;
    }
  }

  /// Get a tile - الحصول على بلاطة
  Future<Uint8List?> getTile({
    required String regionId,
    required int z,
    required int x,
    required int y,
  }) async {
    try {
      await initialize();

      final file = File('$_basePath/regions/$regionId/$z/${x}_$y.png');

      if (await file.exists()) {
        return await file.readAsBytes();
      }
      return null;
    } catch (e) {
      debugPrint('Failed to get tile: $e');
      return null;
    }
  }

  /// Get tile from any region (searches all) - البحث في كل المناطق
  Future<Uint8List?> getTileFromAnyRegion({
    required int z,
    required int x,
    required int y,
  }) async {
    try {
      await initialize();

      final regionsDir = Directory('$_basePath/regions');
      if (!await regionsDir.exists()) return null;

      await for (final region in regionsDir.list()) {
        if (region is Directory) {
          final file = File('${region.path}/$z/${x}_$y.png');
          if (await file.exists()) {
            return await file.readAsBytes();
          }
        }
      }
      return null;
    } catch (e) {
      debugPrint('Failed to get tile from any region: $e');
      return null;
    }
  }

  /// Check if tile exists - التحقق من وجود بلاطة
  Future<bool> tileExists({
    required String regionId,
    required int z,
    required int x,
    required int y,
  }) async {
    await initialize();
    final file = File('$_basePath/regions/$regionId/$z/${x}_$y.png');
    return file.exists();
  }

  /// Check if tile exists in any region - التحقق من وجود بلاطة في أي منطقة
  Future<bool> tileExistsInAnyRegion({
    required int z,
    required int x,
    required int y,
  }) async {
    return await getTileFromAnyRegion(z: z, x: x, y: y) != null;
  }

  /// Get storage statistics - إحصائيات التخزين
  Future<StorageStats> getStorageStats() async {
    await initialize();

    int totalSize = 0;
    int tileCount = 0;
    final zoomLevels = <int>{};
    final regions = <String, RegionStats>{};

    final regionsDir = Directory('$_basePath/regions');
    if (!await regionsDir.exists()) {
      return const StorageStats(
        totalSizeBytes: 0,
        totalTileCount: 0,
        zoomLevels: [],
        regions: {},
      );
    }

    await for (final regionDir in regionsDir.list()) {
      if (regionDir is Directory) {
        final regionId = regionDir.path.split('/').last;
        int regionSize = 0;
        int regionTileCount = 0;
        final regionZooms = <int>{};

        await for (final zoomDir in regionDir.list()) {
          if (zoomDir is Directory) {
            final zoom = int.tryParse(zoomDir.path.split('/').last);
            if (zoom != null) {
              zoomLevels.add(zoom);
              regionZooms.add(zoom);

              await for (final file in zoomDir.list()) {
                if (file is File && file.path.endsWith('.png')) {
                  final stat = await file.stat();
                  totalSize += stat.size;
                  regionSize += stat.size;
                  tileCount++;
                  regionTileCount++;
                }
              }
            }
          }
        }

        regions[regionId] = RegionStats(
          regionId: regionId,
          sizeBytes: regionSize,
          tileCount: regionTileCount,
          zoomLevels: regionZooms.toList()..sort(),
        );
      }
    }

    return StorageStats(
      totalSizeBytes: totalSize,
      totalTileCount: tileCount,
      zoomLevels: zoomLevels.toList()..sort(),
      regions: regions,
    );
  }

  /// Get storage size for a region - حجم تخزين منطقة
  Future<int> getRegionSize(String regionId) async {
    await initialize();

    int size = 0;
    final regionDir = Directory('$_basePath/regions/$regionId');

    if (!await regionDir.exists()) return 0;

    await for (final entity in regionDir.list(recursive: true)) {
      if (entity is File) {
        final stat = await entity.stat();
        size += stat.size;
      }
    }

    return size;
  }

  /// Get tile count for a region - عدد البلاطات في منطقة
  Future<int> getRegionTileCount(String regionId) async {
    await initialize();

    int count = 0;
    final regionDir = Directory('$_basePath/regions/$regionId');

    if (!await regionDir.exists()) return 0;

    await for (final entity in regionDir.list(recursive: true)) {
      if (entity is File && entity.path.endsWith('.png')) {
        count++;
      }
    }

    return count;
  }

  /// Delete a region - حذف منطقة
  Future<bool> deleteRegion(String regionId) async {
    try {
      await initialize();

      final regionDir = Directory('$_basePath/regions/$regionId');
      if (await regionDir.exists()) {
        await regionDir.delete(recursive: true);
        debugPrint('Deleted region: $regionId');
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('Failed to delete region: $e');
      return false;
    }
  }

  /// Clear all storage - مسح كل التخزين
  Future<void> clearAll() async {
    try {
      await initialize();

      final storeDir = Directory(_basePath);
      if (await storeDir.exists()) {
        await storeDir.delete(recursive: true);
        await storeDir.create(recursive: true);
        debugPrint('Cleared all tile storage');
      }
    } catch (e) {
      debugPrint('Failed to clear storage: $e');
    }
  }

  /// Delete tiles older than specified days - حذف البلاطات القديمة
  Future<CleanupResult> cleanupExpiredTiles({
    int expirationDays = defaultExpirationDays,
  }) async {
    await initialize();

    int deletedCount = 0;
    int deletedSize = 0;
    final cutoffDate = DateTime.now().subtract(Duration(days: expirationDays));

    final regionsDir = Directory('$_basePath/regions');
    if (!await regionsDir.exists()) {
      return const CleanupResult(deletedCount: 0, freedBytes: 0);
    }

    await for (final regionDir in regionsDir.list()) {
      if (regionDir is Directory) {
        await for (final zoomDir in regionDir.list()) {
          if (zoomDir is Directory) {
            await for (final file in zoomDir.list()) {
              if (file is File && file.path.endsWith('.png')) {
                final stat = await file.stat();
                if (stat.modified.isBefore(cutoffDate)) {
                  deletedSize += stat.size;
                  await file.delete();
                  deletedCount++;
                }
              }
            }
          }
        }
      }
    }

    // Save cleanup timestamp
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_keyLastCleanup, DateTime.now().millisecondsSinceEpoch);

    debugPrint('Cleanup: deleted $deletedCount tiles, freed ${_formatBytes(deletedSize)}');

    return CleanupResult(
      deletedCount: deletedCount,
      freedBytes: deletedSize,
    );
  }

  /// Check if cleanup is needed - التحقق من الحاجة للتنظيف
  Future<bool> needsCleanup({int cleanupIntervalDays = 7}) async {
    final prefs = await SharedPreferences.getInstance();
    final lastCleanup = prefs.getInt(_keyLastCleanup);

    if (lastCleanup == null) return true;

    final lastCleanupDate = DateTime.fromMillisecondsSinceEpoch(lastCleanup);
    final threshold = DateTime.now().subtract(Duration(days: cleanupIntervalDays));

    return lastCleanupDate.isBefore(threshold);
  }

  /// Get list of downloaded region IDs - قائمة المناطق المحملة
  Future<List<String>> getDownloadedRegionIds() async {
    await initialize();

    final regions = <String>[];
    final regionsDir = Directory('$_basePath/regions');

    if (!await regionsDir.exists()) return regions;

    await for (final regionDir in regionsDir.list()) {
      if (regionDir is Directory) {
        final regionId = regionDir.path.split('/').last;
        regions.add(regionId);
      }
    }

    return regions;
  }

  /// Save region metadata - حفظ بيانات المنطقة
  Future<void> saveRegionMetadata(DownloadedRegion region) async {
    final prefs = await SharedPreferences.getInstance();
    final regionsJson = prefs.getStringList(_keyRegions) ?? [];

    // Remove existing entry for this region
    regionsJson.removeWhere((json) => json.contains('"id":"${region.id}"'));

    // Add updated entry
    regionsJson.add(region.toJsonString());

    await prefs.setStringList(_keyRegions, regionsJson);
  }

  /// Get region metadata - الحصول على بيانات المنطقة
  Future<DownloadedRegion?> getRegionMetadata(String regionId) async {
    final prefs = await SharedPreferences.getInstance();
    final regionsJson = prefs.getStringList(_keyRegions) ?? [];

    for (final json in regionsJson) {
      if (json.contains('"id":"$regionId"')) {
        return DownloadedRegion.fromJsonString(json);
      }
    }
    return null;
  }

  /// Get all regions metadata - الحصول على بيانات كل المناطق
  Future<List<DownloadedRegion>> getAllRegionsMetadata() async {
    final prefs = await SharedPreferences.getInstance();
    final regionsJson = prefs.getStringList(_keyRegions) ?? [];

    return regionsJson
        .map((json) => DownloadedRegion.fromJsonString(json))
        .whereType<DownloadedRegion>()
        .toList();
  }

  /// Delete region metadata - حذف بيانات المنطقة
  Future<void> deleteRegionMetadata(String regionId) async {
    final prefs = await SharedPreferences.getInstance();
    final regionsJson = prefs.getStringList(_keyRegions) ?? [];

    regionsJson.removeWhere((json) => json.contains('"id":"$regionId"'));

    await prefs.setStringList(_keyRegions, regionsJson);
  }

  /// Format bytes to human readable - تنسيق البايتات
  String _formatBytes(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    if (bytes < 1024 * 1024 * 1024) {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    }
    return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(2)} GB';
  }
}

/// Storage statistics - إحصائيات التخزين
class StorageStats {
  final int totalSizeBytes;
  final int totalTileCount;
  final List<int> zoomLevels;
  final Map<String, RegionStats> regions;

  const StorageStats({
    required this.totalSizeBytes,
    required this.totalTileCount,
    required this.zoomLevels,
    required this.regions,
  });

  /// Size in MB - الحجم بالميجابايت
  double get sizeMb => totalSizeBytes / (1024 * 1024);

  /// Size in GB - الحجم بالجيجابايت
  double get sizeGb => totalSizeBytes / (1024 * 1024 * 1024);

  /// Formatted size string - الحجم المنسق
  String get formattedSize {
    if (totalSizeBytes < 1024) return '$totalSizeBytes B';
    if (totalSizeBytes < 1024 * 1024) {
      return '${(totalSizeBytes / 1024).toStringAsFixed(1)} KB';
    }
    if (totalSizeBytes < 1024 * 1024 * 1024) {
      return '${sizeMb.toStringAsFixed(1)} MB';
    }
    return '${sizeGb.toStringAsFixed(2)} GB';
  }

  /// Zoom range string - نطاق التكبير
  String get zoomRange {
    if (zoomLevels.isEmpty) return 'N/A';
    if (zoomLevels.length == 1) return '${zoomLevels.first}';
    return '${zoomLevels.first}-${zoomLevels.last}';
  }

  @override
  String toString() =>
      'StorageStats(size: $formattedSize, tiles: $totalTileCount, '
      'zooms: $zoomRange, regions: ${regions.length})';
}

/// Region statistics - إحصائيات المنطقة
class RegionStats {
  final String regionId;
  final int sizeBytes;
  final int tileCount;
  final List<int> zoomLevels;

  const RegionStats({
    required this.regionId,
    required this.sizeBytes,
    required this.tileCount,
    required this.zoomLevels,
  });

  /// Size in MB - الحجم بالميجابايت
  double get sizeMb => sizeBytes / (1024 * 1024);

  /// Formatted size string - الحجم المنسق
  String get formattedSize {
    if (sizeBytes < 1024) return '$sizeBytes B';
    if (sizeBytes < 1024 * 1024) {
      return '${(sizeBytes / 1024).toStringAsFixed(1)} KB';
    }
    return '${sizeMb.toStringAsFixed(1)} MB';
  }

  @override
  String toString() =>
      'RegionStats($regionId: $formattedSize, $tileCount tiles)';
}

/// Cleanup result - نتيجة التنظيف
class CleanupResult {
  final int deletedCount;
  final int freedBytes;

  const CleanupResult({
    required this.deletedCount,
    required this.freedBytes,
  });

  /// Freed space in MB - المساحة المحررة بالميجابايت
  double get freedMb => freedBytes / (1024 * 1024);

  /// Formatted freed space - المساحة المحررة المنسقة
  String get formattedFreed {
    if (freedBytes < 1024) return '$freedBytes B';
    if (freedBytes < 1024 * 1024) {
      return '${(freedBytes / 1024).toStringAsFixed(1)} KB';
    }
    return '${freedMb.toStringAsFixed(1)} MB';
  }

  @override
  String toString() =>
      'CleanupResult(deleted: $deletedCount, freed: $formattedFreed)';
}

/// Downloaded region metadata - بيانات المنطقة المحملة
class DownloadedRegion {
  final String id;
  final String nameAr;
  final String nameEn;
  final RegionBounds bounds;
  final int minZoom;
  final int maxZoom;
  final DateTime downloadedAt;
  final int tileCount;
  final int sizeBytes;
  final DownloadStatus status;

  const DownloadedRegion({
    required this.id,
    required this.nameAr,
    required this.nameEn,
    required this.bounds,
    required this.minZoom,
    required this.maxZoom,
    required this.downloadedAt,
    required this.tileCount,
    required this.sizeBytes,
    required this.status,
  });

  /// Create a copy with updated values
  DownloadedRegion copyWith({
    String? id,
    String? nameAr,
    String? nameEn,
    RegionBounds? bounds,
    int? minZoom,
    int? maxZoom,
    DateTime? downloadedAt,
    int? tileCount,
    int? sizeBytes,
    DownloadStatus? status,
  }) {
    return DownloadedRegion(
      id: id ?? this.id,
      nameAr: nameAr ?? this.nameAr,
      nameEn: nameEn ?? this.nameEn,
      bounds: bounds ?? this.bounds,
      minZoom: minZoom ?? this.minZoom,
      maxZoom: maxZoom ?? this.maxZoom,
      downloadedAt: downloadedAt ?? this.downloadedAt,
      tileCount: tileCount ?? this.tileCount,
      sizeBytes: sizeBytes ?? this.sizeBytes,
      status: status ?? this.status,
    );
  }

  /// Formatted size - الحجم المنسق
  String get formattedSize {
    if (sizeBytes < 1024) return '$sizeBytes B';
    if (sizeBytes < 1024 * 1024) {
      return '${(sizeBytes / 1024).toStringAsFixed(1)} KB';
    }
    return '${(sizeBytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }

  /// Get name based on locale - الاسم حسب اللغة
  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  /// Convert to JSON string
  String toJsonString() {
    return '{"id":"$id","nameAr":"$nameAr","nameEn":"$nameEn",'
        '"bounds":${_boundsToJson(bounds)},'
        '"minZoom":$minZoom,"maxZoom":$maxZoom,'
        '"downloadedAt":${downloadedAt.millisecondsSinceEpoch},'
        '"tileCount":$tileCount,"sizeBytes":$sizeBytes,'
        '"status":"${status.name}"}';
  }

  String _boundsToJson(RegionBounds b) {
    return '{"south":${b.south},"west":${b.west},'
        '"north":${b.north},"east":${b.east}}';
  }

  /// Create from JSON string
  static DownloadedRegion? fromJsonString(String json) {
    try {
      // Simple JSON parsing without external dependency
      final id = _extractString(json, 'id');
      final nameAr = _extractString(json, 'nameAr');
      final nameEn = _extractString(json, 'nameEn');
      final minZoom = _extractInt(json, 'minZoom');
      final maxZoom = _extractInt(json, 'maxZoom');
      final downloadedAt = _extractInt(json, 'downloadedAt');
      final tileCount = _extractInt(json, 'tileCount');
      final sizeBytes = _extractInt(json, 'sizeBytes');
      final status = _extractString(json, 'status');

      // Extract bounds
      final boundsMatch = RegExp(r'"bounds":\{([^}]+)\}').firstMatch(json);
      if (boundsMatch == null) return null;
      final boundsJson = boundsMatch.group(1)!;
      final south = _extractDouble(boundsJson, 'south');
      final west = _extractDouble(boundsJson, 'west');
      final north = _extractDouble(boundsJson, 'north');
      final east = _extractDouble(boundsJson, 'east');

      return DownloadedRegion(
        id: id,
        nameAr: nameAr,
        nameEn: nameEn,
        bounds: RegionBounds(
          south: south,
          west: west,
          north: north,
          east: east,
        ),
        minZoom: minZoom,
        maxZoom: maxZoom,
        downloadedAt: DateTime.fromMillisecondsSinceEpoch(downloadedAt),
        tileCount: tileCount,
        sizeBytes: sizeBytes,
        status: DownloadStatus.values.firstWhere(
          (s) => s.name == status,
          orElse: () => DownloadStatus.completed,
        ),
      );
    } catch (e) {
      debugPrint('Failed to parse DownloadedRegion: $e');
      return null;
    }
  }

  static String _extractString(String json, String key) {
    final match = RegExp('"$key":"([^"]*)"').firstMatch(json);
    return match?.group(1) ?? '';
  }

  static int _extractInt(String json, String key) {
    final match = RegExp('"$key":([0-9]+)').firstMatch(json);
    return int.tryParse(match?.group(1) ?? '0') ?? 0;
  }

  static double _extractDouble(String json, String key) {
    final match = RegExp('"$key":([0-9.\\-]+)').firstMatch(json);
    return double.tryParse(match?.group(1) ?? '0') ?? 0.0;
  }
}

/// Download status - حالة التحميل
enum DownloadStatus {
  pending, // Pending download - في انتظار التحميل
  downloading, // Currently downloading - جارٍ التحميل
  paused, // Download paused - تحميل متوقف
  completed, // Download completed - اكتمل التحميل
  failed, // Download failed - فشل التحميل
}
