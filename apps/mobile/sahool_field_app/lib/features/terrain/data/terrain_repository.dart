/// Terrain Analysis Repository
/// مستودع تحليل التضاريس
///
/// Fetches terrain analysis from API with offline-first caching using Drift.
/// Supports elevation profiles, slope analysis, and soil characteristics.
library;

import 'dart:convert';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:http/http.dart' as http;

import '../../../core/config/api_config.dart';
import '../../../core/storage/database.dart';

part 'terrain_repository.freezed.dart';
part 'terrain_repository.g.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Providers - الموفرون
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for TerrainRepository instance
/// موفر لنسخة مستودع التضاريس
final terrainRepositoryProvider = Provider<TerrainRepository>((ref) {
  final repository = TerrainRepository();
  ref.onDispose(() => repository.dispose());
  return repository;
});

/// Provider for terrain analysis by field ID
/// موفر لتحليل التضاريس حسب معرف الحقل
final terrainAnalysisProvider =
    FutureProvider.family<TerrainAnalysis?, String>((ref, fieldId) async {
  final repository = ref.watch(terrainRepositoryProvider);
  return repository.getTerrainAnalysis(fieldId);
});

/// Provider for elevation profile by field ID
/// موفر لملف الارتفاع حسب معرف الحقل
final elevationProfileProvider =
    FutureProvider.family<ElevationProfile?, String>((ref, fieldId) async {
  final repository = ref.watch(terrainRepositoryProvider);
  return repository.getElevationProfile(fieldId);
});

/// Provider for slope analysis by field ID
/// موفر لتحليل الانحدار حسب معرف الحقل
final slopeAnalysisProvider =
    FutureProvider.family<SlopeAnalysis?, String>((ref, fieldId) async {
  final repository = ref.watch(terrainRepositoryProvider);
  return repository.getSlopeAnalysis(fieldId);
});

// ═══════════════════════════════════════════════════════════════════════════════
// Models - النماذج
// ═══════════════════════════════════════════════════════════════════════════════

/// Terrain analysis result
/// نتيجة تحليل التضاريس
@freezed
class TerrainAnalysis with _$TerrainAnalysis {
  const factory TerrainAnalysis({
    /// Field ID
    /// معرف الحقل
    required String fieldId,

    /// Average elevation in meters
    /// متوسط الارتفاع بالمتر
    required double averageElevationM,

    /// Minimum elevation
    /// الحد الأدنى للارتفاع
    required double minElevationM,

    /// Maximum elevation
    /// الحد الأقصى للارتفاع
    required double maxElevationM,

    /// Elevation range (max - min)
    /// نطاق الارتفاع
    required double elevationRangeM,

    /// Average slope percentage
    /// متوسط الانحدار بالنسبة المئوية
    required double averageSlopePercent,

    /// Maximum slope percentage
    /// الحد الأقصى للانحدار
    required double maxSlopePercent,

    /// Dominant aspect (N, NE, E, SE, S, SW, W, NW)
    /// الاتجاه السائد
    required String dominantAspect,

    /// Arabic aspect name
    /// اسم الاتجاه بالعربية
    required String dominantAspectAr,

    /// Soil type if available
    /// نوع التربة إن توفر
    String? soilType,

    /// Arabic soil type
    /// نوع التربة بالعربية
    String? soilTypeAr,

    /// Drainage class
    /// فئة الصرف
    String? drainageClass,

    /// Terrain roughness index (0-1)
    /// مؤشر خشونة التضاريس
    double? roughnessIndex,

    /// Topographic wetness index
    /// مؤشر الرطوبة الطبوغرافية
    double? wetnessIndex,

    /// Timestamp of analysis
    /// وقت التحليل
    DateTime? timestamp,

    /// Data source
    /// مصدر البيانات
    @Default('dem') String dataSource,
  }) = _TerrainAnalysis;

  factory TerrainAnalysis.fromJson(Map<String, dynamic> json) =>
      _$TerrainAnalysisFromJson(json);
}

/// Elevation profile along a transect
/// ملف الارتفاع على طول خط عرضي
@freezed
class ElevationProfile with _$ElevationProfile {
  const factory ElevationProfile({
    /// Field ID
    /// معرف الحقل
    required String fieldId,

    /// List of elevation points
    /// قائمة نقاط الارتفاع
    required List<ElevationPoint> points,

    /// Total distance in meters
    /// المسافة الإجمالية بالمتر
    required double totalDistanceM,

    /// Total elevation gain
    /// إجمالي الارتفاع المكتسب
    required double totalGainM,

    /// Total elevation loss
    /// إجمالي الارتفاع المفقود
    required double totalLossM,

    /// Profile direction (degrees from north)
    /// اتجاه الملف (درجات من الشمال)
    double? profileDirection,

    /// Resolution in meters
    /// الدقة بالمتر
    double? resolutionM,
  }) = _ElevationProfile;

  factory ElevationProfile.fromJson(Map<String, dynamic> json) =>
      _$ElevationProfileFromJson(json);
}

/// Single elevation point
/// نقطة ارتفاع واحدة
@freezed
class ElevationPoint with _$ElevationPoint {
  const factory ElevationPoint({
    /// Distance from start (meters)
    /// المسافة من البداية (متر)
    required double distanceM,

    /// Elevation (meters)
    /// الارتفاع (متر)
    required double elevationM,

    /// Latitude
    /// خط العرض
    double? latitude,

    /// Longitude
    /// خط الطول
    double? longitude,

    /// Slope at this point (percent)
    /// الانحدار عند هذه النقطة (نسبة مئوية)
    double? slopePercent,
  }) = _ElevationPoint;

  factory ElevationPoint.fromJson(Map<String, dynamic> json) =>
      _$ElevationPointFromJson(json);
}

/// Slope analysis for a field
/// تحليل الانحدار للحقل
@freezed
class SlopeAnalysis with _$SlopeAnalysis {
  const factory SlopeAnalysis({
    /// Field ID
    /// معرف الحقل
    required String fieldId,

    /// Slope distribution by class
    /// توزيع الانحدار حسب الفئة
    required Map<String, double> slopeDistribution,

    /// Dominant slope class
    /// فئة الانحدار السائدة
    required String dominantSlopeClass,

    /// Arabic dominant slope class
    /// فئة الانحدار السائدة بالعربية
    required String dominantSlopeClassAr,

    /// Erosion risk level
    /// مستوى خطر التعرية
    required String erosionRisk,

    /// Arabic erosion risk
    /// خطر التعرية بالعربية
    required String erosionRiskAr,

    /// Recommended practices
    /// الممارسات الموصى بها
    @Default([]) List<String> recommendations,

    /// Arabic recommendations
    /// التوصيات بالعربية
    @Default([]) List<String> recommendationsAr,

    /// Contour interval recommendation (meters)
    /// توصية فترة الخطوط الكنتورية (متر)
    double? contourIntervalM,

    /// Tillage direction recommendation (degrees)
    /// توصية اتجاه الحراثة (درجات)
    double? tillageDirDegrees,
  }) = _SlopeAnalysis;

  factory SlopeAnalysis.fromJson(Map<String, dynamic> json) =>
      _$SlopeAnalysisFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Terrain Repository - مستودع التضاريس
// ═══════════════════════════════════════════════════════════════════════════════

/// Repository for terrain analysis with offline caching
/// مستودع تحليل التضاريس مع التخزين المؤقت دون اتصال
class TerrainRepository {
  final http.Client _httpClient;
  final AppDatabase? _database;

  // Cache TTL (7 days for terrain data)
  static const Duration cacheTtl = Duration(days: 7);

  // In-memory cache
  final Map<String, _CachedTerrain> _memoryCache = {};

  TerrainRepository({
    http.Client? httpClient,
    AppDatabase? database,
  })  : _httpClient = httpClient ?? http.Client(),
        _database = database;

  /// Base URL for terrain service
  static String get _baseUrl => '${ApiConfig.effectiveBaseUrl}/api/v1/terrain';

  Map<String, String> get _headers => ApiConfig.defaultHeaders;

  // ═══════════════════════════════════════════════════════════════════════════
  // Terrain Analysis - تحليل التضاريس
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get terrain analysis for a field
  /// الحصول على تحليل التضاريس للحقل
  Future<TerrainAnalysis?> getTerrainAnalysis(
    String fieldId, {
    bool forceRefresh = false,
  }) async {
    // Check memory cache first
    if (!forceRefresh && _memoryCache.containsKey('terrain_$fieldId')) {
      final cached = _memoryCache['terrain_$fieldId']!;
      if (!cached.isExpired) {
        return cached.data as TerrainAnalysis?;
      }
    }

    // Check local database cache
    if (!forceRefresh) {
      final localData = await _getFromLocalCache(fieldId, 'terrain');
      if (localData != null) {
        final analysis = TerrainAnalysis.fromJson(localData);
        _memoryCache['terrain_$fieldId'] = _CachedTerrain(
          data: analysis,
          timestamp: DateTime.now(),
        );
        return analysis;
      }
    }

    // Fetch from API
    final connectivity = await Connectivity().checkConnectivity();
    if (connectivity.contains(ConnectivityResult.none)) {
      // Offline - return cached data even if expired
      final localData = await _getFromLocalCache(fieldId, 'terrain');
      if (localData != null) {
        return TerrainAnalysis.fromJson(localData);
      }
      return null;
    }

    try {
      final response = await _httpClient
          .get(
            Uri.parse('$_baseUrl/analysis/$fieldId'),
            headers: _headers,
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final analysis = TerrainAnalysis.fromJson(data);

        // Cache locally
        await _saveToLocalCache(fieldId, 'terrain', data);

        // Update memory cache
        _memoryCache['terrain_$fieldId'] = _CachedTerrain(
          data: analysis,
          timestamp: DateTime.now(),
        );

        return analysis;
      }

      if (response.statusCode == 404) {
        return null;
      }

      throw TerrainException(
        'Failed to fetch terrain analysis: ${response.statusCode}',
        'فشل في جلب تحليل التضاريس',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is TerrainException) rethrow;

      // Return cached data on network error
      final localData = await _getFromLocalCache(fieldId, 'terrain');
      if (localData != null) {
        return TerrainAnalysis.fromJson(localData);
      }

      throw TerrainException(
        'Network error: $e',
        'خطأ في الشبكة',
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Elevation Profile - ملف الارتفاع
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get elevation profile for a field
  /// الحصول على ملف الارتفاع للحقل
  Future<ElevationProfile?> getElevationProfile(
    String fieldId, {
    double? direction,
    int? numPoints,
    bool forceRefresh = false,
  }) async {
    final cacheKey = 'elevation_$fieldId';

    // Check memory cache
    if (!forceRefresh && _memoryCache.containsKey(cacheKey)) {
      final cached = _memoryCache[cacheKey]!;
      if (!cached.isExpired) {
        return cached.data as ElevationProfile?;
      }
    }

    // Check local cache
    if (!forceRefresh) {
      final localData = await _getFromLocalCache(fieldId, 'elevation');
      if (localData != null) {
        final profile = ElevationProfile.fromJson(localData);
        _memoryCache[cacheKey] = _CachedTerrain(
          data: profile,
          timestamp: DateTime.now(),
        );
        return profile;
      }
    }

    // Fetch from API
    final connectivity = await Connectivity().checkConnectivity();
    if (connectivity.contains(ConnectivityResult.none)) {
      final localData = await _getFromLocalCache(fieldId, 'elevation');
      if (localData != null) {
        return ElevationProfile.fromJson(localData);
      }
      return null;
    }

    try {
      final queryParams = <String, String>{};
      if (direction != null) queryParams['direction'] = direction.toString();
      if (numPoints != null) queryParams['num_points'] = numPoints.toString();

      final uri = Uri.parse('$_baseUrl/elevation/$fieldId').replace(
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      );

      final response = await _httpClient.get(uri, headers: _headers).timeout(
            const Duration(seconds: 30),
          );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final profile = ElevationProfile.fromJson(data);

        await _saveToLocalCache(fieldId, 'elevation', data);
        _memoryCache[cacheKey] = _CachedTerrain(
          data: profile,
          timestamp: DateTime.now(),
        );

        return profile;
      }

      if (response.statusCode == 404) return null;

      throw TerrainException(
        'Failed to fetch elevation profile',
        'فشل في جلب ملف الارتفاع',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is TerrainException) rethrow;

      final localData = await _getFromLocalCache(fieldId, 'elevation');
      if (localData != null) {
        return ElevationProfile.fromJson(localData);
      }

      throw TerrainException(
        'Network error: $e',
        'خطأ في الشبكة',
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Slope Analysis - تحليل الانحدار
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get slope analysis for a field
  /// الحصول على تحليل الانحدار للحقل
  Future<SlopeAnalysis?> getSlopeAnalysis(
    String fieldId, {
    bool forceRefresh = false,
  }) async {
    final cacheKey = 'slope_$fieldId';

    // Check memory cache
    if (!forceRefresh && _memoryCache.containsKey(cacheKey)) {
      final cached = _memoryCache[cacheKey]!;
      if (!cached.isExpired) {
        return cached.data as SlopeAnalysis?;
      }
    }

    // Check local cache
    if (!forceRefresh) {
      final localData = await _getFromLocalCache(fieldId, 'slope');
      if (localData != null) {
        final slope = SlopeAnalysis.fromJson(localData);
        _memoryCache[cacheKey] = _CachedTerrain(
          data: slope,
          timestamp: DateTime.now(),
        );
        return slope;
      }
    }

    // Fetch from API
    final connectivity = await Connectivity().checkConnectivity();
    if (connectivity.contains(ConnectivityResult.none)) {
      final localData = await _getFromLocalCache(fieldId, 'slope');
      if (localData != null) {
        return SlopeAnalysis.fromJson(localData);
      }
      return null;
    }

    try {
      final response = await _httpClient
          .get(
            Uri.parse('$_baseUrl/slope/$fieldId'),
            headers: _headers,
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final slope = SlopeAnalysis.fromJson(data);

        await _saveToLocalCache(fieldId, 'slope', data);
        _memoryCache[cacheKey] = _CachedTerrain(
          data: slope,
          timestamp: DateTime.now(),
        );

        return slope;
      }

      if (response.statusCode == 404) return null;

      throw TerrainException(
        'Failed to fetch slope analysis',
        'فشل في جلب تحليل الانحدار',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is TerrainException) rethrow;

      final localData = await _getFromLocalCache(fieldId, 'slope');
      if (localData != null) {
        return SlopeAnalysis.fromJson(localData);
      }

      throw TerrainException(
        'Network error: $e',
        'خطأ في الشبكة',
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Cache Management - إدارة التخزين المؤقت
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get cached data from local storage
  Future<Map<String, dynamic>?> _getFromLocalCache(
    String fieldId,
    String dataType,
  ) async {
    // In a full implementation, this would use a dedicated Drift table
    // For now, using shared preferences or a cache table

    // Placeholder - in real implementation:
    // final cached = await _database?.getCachedTerrainData(fieldId, dataType);
    // if (cached != null && !_isCacheExpired(cached.timestamp)) {
    //   return json.decode(cached.data);
    // }

    return null;
  }

  /// Save data to local cache
  Future<void> _saveToLocalCache(
    String fieldId,
    String dataType,
    Map<String, dynamic> data,
  ) async {
    // In a full implementation, this would save to a Drift table
    // For now, placeholder

    // await _database?.upsertTerrainCache(
    //   fieldId: fieldId,
    //   dataType: dataType,
    //   data: json.encode(data),
    //   timestamp: DateTime.now(),
    // );
  }

  /// Clear cache for a field
  /// مسح التخزين المؤقت للحقل
  Future<void> clearCache(String fieldId) async {
    _memoryCache.removeWhere((key, _) => key.contains(fieldId));
    // await _database?.deleteTerrainCache(fieldId);
  }

  /// Clear all terrain cache
  /// مسح كل التخزين المؤقت للتضاريس
  Future<void> clearAllCache() async {
    _memoryCache.clear();
    // await _database?.deleteAllTerrainCache();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Health Check - فحص الصحة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if terrain service is available
  /// التحقق من توفر خدمة التضاريس
  Future<bool> isServiceAvailable() async {
    try {
      final response = await _httpClient
          .get(
            Uri.parse('$_baseUrl/healthz'),
            headers: _headers,
          )
          .timeout(const Duration(seconds: 5));

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  /// Dispose resources
  void dispose() {
    _httpClient.close();
    _memoryCache.clear();
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Cache Entry - إدخال التخزين المؤقت
// ═══════════════════════════════════════════════════════════════════════════════

/// Internal cache entry
class _CachedTerrain {
  final Object? data;
  final DateTime timestamp;

  _CachedTerrain({required this.data, required this.timestamp});

  bool get isExpired =>
      DateTime.now().difference(timestamp) > TerrainRepository.cacheTtl;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Exception - الاستثناء
// ═══════════════════════════════════════════════════════════════════════════════

/// Exception for terrain API errors
/// استثناء أخطاء واجهة التضاريس
class TerrainException implements Exception {
  final String message;
  final String messageAr;
  final int? statusCode;

  TerrainException(this.message, this.messageAr, {this.statusCode});

  @override
  String toString() => 'TerrainException: $message';
}
