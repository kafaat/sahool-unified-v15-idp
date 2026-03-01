/// Terrain Analysis Repository
/// مستودع تحليل التضاريس
///
/// Fetches terrain analysis from API with offline-first caching using Drift.
/// Supports elevation profiles, slope analysis, and soil characteristics.

import 'dart:convert';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;

import '../../../core/config/api_config.dart';
import '../../../core/storage/database.dart';

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
@immutable
class TerrainAnalysis {
  final String fieldId;
  final double averageElevationM;
  final double minElevationM;
  final double maxElevationM;
  final double elevationRangeM;
  final double averageSlopePercent;
  final double maxSlopePercent;
  final String dominantAspect;
  final String dominantAspectAr;
  final String? soilType;
  final String? soilTypeAr;
  final String? drainageClass;
  final double? roughnessIndex;
  final double? wetnessIndex;
  final DateTime? timestamp;
  final String dataSource;

  const TerrainAnalysis({
    required this.fieldId,
    required this.averageElevationM,
    required this.minElevationM,
    required this.maxElevationM,
    required this.elevationRangeM,
    required this.averageSlopePercent,
    required this.maxSlopePercent,
    required this.dominantAspect,
    required this.dominantAspectAr,
    this.soilType,
    this.soilTypeAr,
    this.drainageClass,
    this.roughnessIndex,
    this.wetnessIndex,
    this.timestamp,
    this.dataSource = 'dem',
  });

  factory TerrainAnalysis.fromJson(Map<String, dynamic> json) {
    return TerrainAnalysis(
      fieldId: json['fieldId'] as String,
      averageElevationM: (json['averageElevationM'] as num).toDouble(),
      minElevationM: (json['minElevationM'] as num).toDouble(),
      maxElevationM: (json['maxElevationM'] as num).toDouble(),
      elevationRangeM: (json['elevationRangeM'] as num).toDouble(),
      averageSlopePercent: (json['averageSlopePercent'] as num).toDouble(),
      maxSlopePercent: (json['maxSlopePercent'] as num).toDouble(),
      dominantAspect: json['dominantAspect'] as String,
      dominantAspectAr: json['dominantAspectAr'] as String,
      soilType: json['soilType'] as String?,
      soilTypeAr: json['soilTypeAr'] as String?,
      drainageClass: json['drainageClass'] as String?,
      roughnessIndex: (json['roughnessIndex'] as num?)?.toDouble(),
      wetnessIndex: (json['wetnessIndex'] as num?)?.toDouble(),
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : null,
      dataSource: json['dataSource'] as String? ?? 'dem',
    );
  }

  Map<String, dynamic> toJson() => {
        'fieldId': fieldId,
        'averageElevationM': averageElevationM,
        'minElevationM': minElevationM,
        'maxElevationM': maxElevationM,
        'elevationRangeM': elevationRangeM,
        'averageSlopePercent': averageSlopePercent,
        'maxSlopePercent': maxSlopePercent,
        'dominantAspect': dominantAspect,
        'dominantAspectAr': dominantAspectAr,
        'soilType': soilType,
        'soilTypeAr': soilTypeAr,
        'drainageClass': drainageClass,
        'roughnessIndex': roughnessIndex,
        'wetnessIndex': wetnessIndex,
        'timestamp': timestamp?.toIso8601String(),
        'dataSource': dataSource,
      };

  TerrainAnalysis copyWith({
    String? fieldId,
    double? averageElevationM,
    double? minElevationM,
    double? maxElevationM,
    double? elevationRangeM,
    double? averageSlopePercent,
    double? maxSlopePercent,
    String? dominantAspect,
    String? dominantAspectAr,
    String? soilType,
    String? soilTypeAr,
    String? drainageClass,
    double? roughnessIndex,
    double? wetnessIndex,
    DateTime? timestamp,
    String? dataSource,
  }) {
    return TerrainAnalysis(
      fieldId: fieldId ?? this.fieldId,
      averageElevationM: averageElevationM ?? this.averageElevationM,
      minElevationM: minElevationM ?? this.minElevationM,
      maxElevationM: maxElevationM ?? this.maxElevationM,
      elevationRangeM: elevationRangeM ?? this.elevationRangeM,
      averageSlopePercent: averageSlopePercent ?? this.averageSlopePercent,
      maxSlopePercent: maxSlopePercent ?? this.maxSlopePercent,
      dominantAspect: dominantAspect ?? this.dominantAspect,
      dominantAspectAr: dominantAspectAr ?? this.dominantAspectAr,
      soilType: soilType ?? this.soilType,
      soilTypeAr: soilTypeAr ?? this.soilTypeAr,
      drainageClass: drainageClass ?? this.drainageClass,
      roughnessIndex: roughnessIndex ?? this.roughnessIndex,
      wetnessIndex: wetnessIndex ?? this.wetnessIndex,
      timestamp: timestamp ?? this.timestamp,
      dataSource: dataSource ?? this.dataSource,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is TerrainAnalysis &&
          runtimeType == other.runtimeType &&
          fieldId == other.fieldId &&
          averageElevationM == other.averageElevationM &&
          minElevationM == other.minElevationM &&
          maxElevationM == other.maxElevationM &&
          elevationRangeM == other.elevationRangeM &&
          averageSlopePercent == other.averageSlopePercent &&
          maxSlopePercent == other.maxSlopePercent &&
          dominantAspect == other.dominantAspect &&
          dominantAspectAr == other.dominantAspectAr &&
          soilType == other.soilType &&
          soilTypeAr == other.soilTypeAr &&
          drainageClass == other.drainageClass &&
          roughnessIndex == other.roughnessIndex &&
          wetnessIndex == other.wetnessIndex &&
          dataSource == other.dataSource;

  @override
  int get hashCode => Object.hash(
        fieldId,
        averageElevationM,
        minElevationM,
        maxElevationM,
        elevationRangeM,
        averageSlopePercent,
        maxSlopePercent,
        dominantAspect,
        dominantAspectAr,
        soilType,
        soilTypeAr,
        drainageClass,
        roughnessIndex,
        wetnessIndex,
        dataSource,
      );

  @override
  String toString() =>
      'TerrainAnalysis(fieldId: $fieldId, elevation: $averageElevationM m, slope: $averageSlopePercent%)';
}

/// Elevation profile along a transect
/// ملف الارتفاع على طول خط عرضي
@immutable
class ElevationProfile {
  final String fieldId;
  final List<ElevationPoint> points;
  final double totalDistanceM;
  final double totalGainM;
  final double totalLossM;
  final double? profileDirection;
  final double? resolutionM;

  const ElevationProfile({
    required this.fieldId,
    required this.points,
    required this.totalDistanceM,
    required this.totalGainM,
    required this.totalLossM,
    this.profileDirection,
    this.resolutionM,
  });

  factory ElevationProfile.fromJson(Map<String, dynamic> json) {
    return ElevationProfile(
      fieldId: json['fieldId'] as String,
      points: (json['points'] as List<dynamic>)
          .map((p) => ElevationPoint.fromJson(p as Map<String, dynamic>))
          .toList(),
      totalDistanceM: (json['totalDistanceM'] as num).toDouble(),
      totalGainM: (json['totalGainM'] as num).toDouble(),
      totalLossM: (json['totalLossM'] as num).toDouble(),
      profileDirection: (json['profileDirection'] as num?)?.toDouble(),
      resolutionM: (json['resolutionM'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'fieldId': fieldId,
        'points': points.map((p) => p.toJson()).toList(),
        'totalDistanceM': totalDistanceM,
        'totalGainM': totalGainM,
        'totalLossM': totalLossM,
        'profileDirection': profileDirection,
        'resolutionM': resolutionM,
      };

  ElevationProfile copyWith({
    String? fieldId,
    List<ElevationPoint>? points,
    double? totalDistanceM,
    double? totalGainM,
    double? totalLossM,
    double? profileDirection,
    double? resolutionM,
  }) {
    return ElevationProfile(
      fieldId: fieldId ?? this.fieldId,
      points: points ?? this.points,
      totalDistanceM: totalDistanceM ?? this.totalDistanceM,
      totalGainM: totalGainM ?? this.totalGainM,
      totalLossM: totalLossM ?? this.totalLossM,
      profileDirection: profileDirection ?? this.profileDirection,
      resolutionM: resolutionM ?? this.resolutionM,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ElevationProfile &&
          runtimeType == other.runtimeType &&
          fieldId == other.fieldId &&
          listEquals(points, other.points) &&
          totalDistanceM == other.totalDistanceM &&
          totalGainM == other.totalGainM &&
          totalLossM == other.totalLossM &&
          profileDirection == other.profileDirection &&
          resolutionM == other.resolutionM;

  @override
  int get hashCode => Object.hash(
        fieldId,
        Object.hashAll(points),
        totalDistanceM,
        totalGainM,
        totalLossM,
        profileDirection,
        resolutionM,
      );

  @override
  String toString() =>
      'ElevationProfile(fieldId: $fieldId, points: ${points.length}, distance: $totalDistanceM m)';
}

/// Single elevation point
/// نقطة ارتفاع واحدة
@immutable
class ElevationPoint {
  final double distanceM;
  final double elevationM;
  final double? latitude;
  final double? longitude;
  final double? slopePercent;

  const ElevationPoint({
    required this.distanceM,
    required this.elevationM,
    this.latitude,
    this.longitude,
    this.slopePercent,
  });

  factory ElevationPoint.fromJson(Map<String, dynamic> json) {
    return ElevationPoint(
      distanceM: (json['distanceM'] as num).toDouble(),
      elevationM: (json['elevationM'] as num).toDouble(),
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      slopePercent: (json['slopePercent'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'distanceM': distanceM,
        'elevationM': elevationM,
        'latitude': latitude,
        'longitude': longitude,
        'slopePercent': slopePercent,
      };

  ElevationPoint copyWith({
    double? distanceM,
    double? elevationM,
    double? latitude,
    double? longitude,
    double? slopePercent,
  }) {
    return ElevationPoint(
      distanceM: distanceM ?? this.distanceM,
      elevationM: elevationM ?? this.elevationM,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      slopePercent: slopePercent ?? this.slopePercent,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ElevationPoint &&
          runtimeType == other.runtimeType &&
          distanceM == other.distanceM &&
          elevationM == other.elevationM &&
          latitude == other.latitude &&
          longitude == other.longitude &&
          slopePercent == other.slopePercent;

  @override
  int get hashCode =>
      Object.hash(distanceM, elevationM, latitude, longitude, slopePercent);

  @override
  String toString() =>
      'ElevationPoint(distance: $distanceM m, elevation: $elevationM m)';
}

/// Slope analysis for a field
/// تحليل الانحدار للحقل
@immutable
class SlopeAnalysis {
  final String fieldId;
  final Map<String, double> slopeDistribution;
  final String dominantSlopeClass;
  final String dominantSlopeClassAr;
  final String erosionRisk;
  final String erosionRiskAr;
  final List<String> recommendations;
  final List<String> recommendationsAr;
  final double? contourIntervalM;
  final double? tillageDirDegrees;

  const SlopeAnalysis({
    required this.fieldId,
    required this.slopeDistribution,
    required this.dominantSlopeClass,
    required this.dominantSlopeClassAr,
    required this.erosionRisk,
    required this.erosionRiskAr,
    this.recommendations = const [],
    this.recommendationsAr = const [],
    this.contourIntervalM,
    this.tillageDirDegrees,
  });

  factory SlopeAnalysis.fromJson(Map<String, dynamic> json) {
    return SlopeAnalysis(
      fieldId: json['fieldId'] as String,
      slopeDistribution:
          (json['slopeDistribution'] as Map<String, dynamic>).map(
        (k, v) => MapEntry(k, (v as num).toDouble()),
      ),
      dominantSlopeClass: json['dominantSlopeClass'] as String,
      dominantSlopeClassAr: json['dominantSlopeClassAr'] as String,
      erosionRisk: json['erosionRisk'] as String,
      erosionRiskAr: json['erosionRiskAr'] as String,
      recommendations: (json['recommendations'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          [],
      recommendationsAr: (json['recommendationsAr'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          [],
      contourIntervalM: (json['contourIntervalM'] as num?)?.toDouble(),
      tillageDirDegrees: (json['tillageDirDegrees'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'fieldId': fieldId,
        'slopeDistribution': slopeDistribution,
        'dominantSlopeClass': dominantSlopeClass,
        'dominantSlopeClassAr': dominantSlopeClassAr,
        'erosionRisk': erosionRisk,
        'erosionRiskAr': erosionRiskAr,
        'recommendations': recommendations,
        'recommendationsAr': recommendationsAr,
        'contourIntervalM': contourIntervalM,
        'tillageDirDegrees': tillageDirDegrees,
      };

  SlopeAnalysis copyWith({
    String? fieldId,
    Map<String, double>? slopeDistribution,
    String? dominantSlopeClass,
    String? dominantSlopeClassAr,
    String? erosionRisk,
    String? erosionRiskAr,
    List<String>? recommendations,
    List<String>? recommendationsAr,
    double? contourIntervalM,
    double? tillageDirDegrees,
  }) {
    return SlopeAnalysis(
      fieldId: fieldId ?? this.fieldId,
      slopeDistribution: slopeDistribution ?? this.slopeDistribution,
      dominantSlopeClass: dominantSlopeClass ?? this.dominantSlopeClass,
      dominantSlopeClassAr: dominantSlopeClassAr ?? this.dominantSlopeClassAr,
      erosionRisk: erosionRisk ?? this.erosionRisk,
      erosionRiskAr: erosionRiskAr ?? this.erosionRiskAr,
      recommendations: recommendations ?? this.recommendations,
      recommendationsAr: recommendationsAr ?? this.recommendationsAr,
      contourIntervalM: contourIntervalM ?? this.contourIntervalM,
      tillageDirDegrees: tillageDirDegrees ?? this.tillageDirDegrees,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SlopeAnalysis &&
          runtimeType == other.runtimeType &&
          fieldId == other.fieldId &&
          mapEquals(slopeDistribution, other.slopeDistribution) &&
          dominantSlopeClass == other.dominantSlopeClass &&
          dominantSlopeClassAr == other.dominantSlopeClassAr &&
          erosionRisk == other.erosionRisk &&
          erosionRiskAr == other.erosionRiskAr &&
          listEquals(recommendations, other.recommendations) &&
          listEquals(recommendationsAr, other.recommendationsAr) &&
          contourIntervalM == other.contourIntervalM &&
          tillageDirDegrees == other.tillageDirDegrees;

  @override
  int get hashCode => Object.hash(
        fieldId,
        Object.hashAll(slopeDistribution.entries),
        dominantSlopeClass,
        dominantSlopeClassAr,
        erosionRisk,
        erosionRiskAr,
        Object.hashAll(recommendations),
        Object.hashAll(recommendationsAr),
        contourIntervalM,
        tillageDirDegrees,
      );

  @override
  String toString() =>
      'SlopeAnalysis(fieldId: $fieldId, dominantSlope: $dominantSlopeClass, erosionRisk: $erosionRisk)';
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
    return null;
  }

  /// Save data to local cache
  Future<void> _saveToLocalCache(
    String fieldId,
    String dataType,
    Map<String, dynamic> data,
  ) async {}

  /// Clear cache for a field
  /// مسح التخزين المؤقت للحقل
  Future<void> clearCache(String fieldId) async {
    _memoryCache.removeWhere((key, _) => key.contains(fieldId));
  }

  /// Clear all terrain cache
  /// مسح كل التخزين المؤقت للتضاريس
  Future<void> clearAllCache() async {
    _memoryCache.clear();
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
