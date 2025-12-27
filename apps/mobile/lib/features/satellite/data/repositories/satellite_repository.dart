/// Satellite Repository - مستودع الأقمار الصناعية
/// Handles caching and data management for satellite features
library;

import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../remote/satellite_api.dart';
import '../models/ndvi_data.dart';
import '../models/field_health.dart';
import '../models/weather_data.dart';
import '../models/phenology_data.dart';

/// Satellite Repository
/// مستودع الأقمار الصناعية
class SatelliteRepository {
  final SatelliteApi _api;
  final SharedPreferences _prefs;

  // Cache duration: 24 hours for satellite data
  static const Duration _cacheDuration = Duration(hours: 24);

  SatelliteRepository({
    required SatelliteApi api,
    required SharedPreferences prefs,
  })  : _api = api,
        _prefs = prefs;

  // ═══════════════════════════════════════════════════════════════════════════
  // Field Health
  // صحة الحقل
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get field health with caching
  /// جلب صحة الحقل مع التخزين المؤقت
  Future<FieldHealth> getFieldHealth(String fieldId, {bool forceRefresh = false}) async {
    final cacheKey = 'field_health_$fieldId';

    // Check cache first
    if (!forceRefresh) {
      final cached = _getCachedData<FieldHealth>(
        cacheKey,
        (json) => FieldHealth.fromJson(json),
      );
      if (cached != null) return cached;
    }

    // Fetch from API
    try {
      final health = await _api.getFieldHealth(fieldId);
      _cacheData(cacheKey, health.toJson());
      return health;
    } catch (e) {
      // Return cached data if available on error
      final cached = _getCachedData<FieldHealth>(
        cacheKey,
        (json) => FieldHealth.fromJson(json),
        ignoreTtl: true,
      );
      if (cached != null) return cached;
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // NDVI Analysis
  // تحليل NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get NDVI analysis with caching
  /// جلب تحليل NDVI مع التخزين المؤقت
  Future<NdviAnalysis> getNdviAnalysis(String fieldId, {bool forceRefresh = false}) async {
    final cacheKey = 'ndvi_analysis_$fieldId';

    if (!forceRefresh) {
      final cached = _getCachedData<NdviAnalysis>(
        cacheKey,
        (json) => NdviAnalysis.fromJson(json),
      );
      if (cached != null) return cached;
    }

    try {
      final analysis = await _api.getNdviAnalysis(fieldId);
      _cacheData(cacheKey, analysis.toJson());
      return analysis;
    } catch (e) {
      final cached = _getCachedData<NdviAnalysis>(
        cacheKey,
        (json) => NdviAnalysis.fromJson(json),
        ignoreTtl: true,
      );
      if (cached != null) return cached;
      rethrow;
    }
  }

  /// Get NDVI time series
  /// جلب السلسلة الزمنية لـ NDVI
  Future<List<NdviDataPoint>> getNdviTimeSeries(
    String fieldId, {
    int days = 30,
    bool forceRefresh = false,
  }) async {
    final cacheKey = 'ndvi_timeseries_${fieldId}_$days';

    if (!forceRefresh) {
      final cached = _getCachedListData<NdviDataPoint>(
        cacheKey,
        (json) => NdviDataPoint.fromJson(json),
      );
      if (cached != null) return cached;
    }

    try {
      final timeSeries = await _api.getNdviTimeSeries(fieldId, days: days);
      _cacheListData(cacheKey, timeSeries.map((point) => point.toJson()).toList());
      return timeSeries;
    } catch (e) {
      final cached = _getCachedListData<NdviDataPoint>(
        cacheKey,
        (json) => NdviDataPoint.fromJson(json),
        ignoreTtl: true,
      );
      if (cached != null) return cached;
      rethrow;
    }
  }

  /// Get vegetation indices
  /// جلب المؤشرات النباتية
  Future<Map<String, double>> getVegetationIndices(
    String fieldId, {
    bool forceRefresh = false,
  }) async {
    final cacheKey = 'vegetation_indices_$fieldId';

    if (!forceRefresh) {
      final cachedJson = _prefs.getString(cacheKey);
      if (cachedJson != null) {
        final timestampKey = '${cacheKey}_timestamp';
        final timestamp = _prefs.getInt(timestampKey);
        if (timestamp != null) {
          final cacheTime = DateTime.fromMillisecondsSinceEpoch(timestamp);
          if (DateTime.now().difference(cacheTime) < _cacheDuration) {
            final data = jsonDecode(cachedJson) as Map<String, dynamic>;
            return data.map((key, value) => MapEntry(key, (value as num).toDouble()));
          }
        }
      }
    }

    try {
      final indices = await _api.getVegetationIndices(fieldId);
      await _prefs.setString(cacheKey, jsonEncode(indices));
      await _prefs.setInt('${cacheKey}_timestamp', DateTime.now().millisecondsSinceEpoch);
      return indices;
    } catch (e) {
      final cachedJson = _prefs.getString(cacheKey);
      if (cachedJson != null) {
        final data = jsonDecode(cachedJson) as Map<String, dynamic>;
        return data.map((key, value) => MapEntry(key, (value as num).toDouble()));
      }
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Weather
  // الطقس
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get weather forecast with caching (shorter cache duration for weather)
  /// جلب توقعات الطقس مع التخزين المؤقت
  Future<WeatherSummary> getWeatherForecast(String fieldId, {bool forceRefresh = false}) async {
    final cacheKey = 'weather_forecast_$fieldId';
    final weatherCacheDuration = const Duration(hours: 3); // Weather updates more frequently

    if (!forceRefresh) {
      final cached = _getCachedData<WeatherSummary>(
        cacheKey,
        (json) => WeatherSummary.fromJson(json),
        customDuration: weatherCacheDuration,
      );
      if (cached != null) return cached;
    }

    try {
      final weather = await _api.getWeatherForecast(fieldId);
      _cacheData(cacheKey, weather.toJson());
      return weather;
    } catch (e) {
      final cached = _getCachedData<WeatherSummary>(
        cacheKey,
        (json) => WeatherSummary.fromJson(json),
        ignoreTtl: true,
      );
      if (cached != null) return cached;
      rethrow;
    }
  }

  /// Get weather alerts
  /// جلب تنبيهات الطقس
  Future<List<WeatherAlertSummary>> getWeatherAlerts(
    String fieldId, {
    bool forceRefresh = false,
  }) async {
    final cacheKey = 'weather_alerts_$fieldId';

    if (!forceRefresh) {
      final cached = _getCachedListData<WeatherAlertSummary>(
        cacheKey,
        (json) => WeatherAlertSummary.fromJson(json),
        customDuration: const Duration(hours: 1),
      );
      if (cached != null) return cached;
    }

    try {
      final alerts = await _api.getWeatherAlerts(fieldId);
      _cacheListData(cacheKey, alerts.map((alert) => alert.toJson()).toList());
      return alerts;
    } catch (e) {
      final cached = _getCachedListData<WeatherAlertSummary>(
        cacheKey,
        (json) => WeatherAlertSummary.fromJson(json),
        ignoreTtl: true,
      );
      if (cached != null) return cached;
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Phenology
  // مراحل النمو
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get phenology data with caching
  /// جلب بيانات مراحل النمو مع التخزين المؤقت
  Future<PhenologyData> getPhenologyData(String fieldId, {bool forceRefresh = false}) async {
    final cacheKey = 'phenology_data_$fieldId';

    if (!forceRefresh) {
      final cached = _getCachedData<PhenologyData>(
        cacheKey,
        (json) => PhenologyData.fromJson(json),
      );
      if (cached != null) return cached;
    }

    try {
      final phenology = await _api.getPhenologyData(fieldId);
      _cacheData(cacheKey, phenology.toJson());
      return phenology;
    } catch (e) {
      final cached = _getCachedData<PhenologyData>(
        cacheKey,
        (json) => PhenologyData.fromJson(json),
        ignoreTtl: true,
      );
      if (cached != null) return cached;
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Dashboard
  // لوحة المعلومات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get complete dashboard data
  /// جلب بيانات لوحة المعلومات الكاملة
  Future<SatelliteDashboardData> getDashboardData(
    String fieldId, {
    bool forceRefresh = false,
  }) async {
    try {
      // Fetch all data in parallel
      final results = await Future.wait([
        getFieldHealth(fieldId, forceRefresh: forceRefresh),
        getNdviAnalysis(fieldId, forceRefresh: forceRefresh),
        getWeatherForecast(fieldId, forceRefresh: forceRefresh),
        getPhenologyData(fieldId, forceRefresh: forceRefresh),
      ]);

      return SatelliteDashboardData(
        fieldHealth: results[0] as FieldHealth,
        ndviAnalysis: results[1] as NdviAnalysis,
        weatherSummary: results[2] as WeatherSummary,
        phenologyData: results[3] as PhenologyData,
      );
    } catch (e) {
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Cache Helpers
  // مساعدات التخزين المؤقت
  // ═══════════════════════════════════════════════════════════════════════════

  T? _getCachedData<T>(
    String key,
    T Function(Map<String, dynamic>) fromJson, {
    bool ignoreTtl = false,
    Duration? customDuration,
  }) {
    final cachedJson = _prefs.getString(key);
    if (cachedJson == null) return null;

    if (!ignoreTtl) {
      final timestampKey = '${key}_timestamp';
      final timestamp = _prefs.getInt(timestampKey);
      if (timestamp != null) {
        final cacheTime = DateTime.fromMillisecondsSinceEpoch(timestamp);
        final duration = customDuration ?? _cacheDuration;
        if (DateTime.now().difference(cacheTime) >= duration) {
          return null;
        }
      }
    }

    try {
      final json = jsonDecode(cachedJson) as Map<String, dynamic>;
      return fromJson(json);
    } catch (e) {
      return null;
    }
  }

  List<T>? _getCachedListData<T>(
    String key,
    T Function(Map<String, dynamic>) fromJson, {
    bool ignoreTtl = false,
    Duration? customDuration,
  }) {
    final cachedJson = _prefs.getString(key);
    if (cachedJson == null) return null;

    if (!ignoreTtl) {
      final timestampKey = '${key}_timestamp';
      final timestamp = _prefs.getInt(timestampKey);
      if (timestamp != null) {
        final cacheTime = DateTime.fromMillisecondsSinceEpoch(timestamp);
        final duration = customDuration ?? _cacheDuration;
        if (DateTime.now().difference(cacheTime) >= duration) {
          return null;
        }
      }
    }

    try {
      final list = jsonDecode(cachedJson) as List<dynamic>;
      return list.map((item) => fromJson(item as Map<String, dynamic>)).toList();
    } catch (e) {
      return null;
    }
  }

  Future<void> _cacheData(String key, Map<String, dynamic> data) async {
    await _prefs.setString(key, jsonEncode(data));
    await _prefs.setInt('${key}_timestamp', DateTime.now().millisecondsSinceEpoch);
  }

  Future<void> _cacheListData(String key, List<Map<String, dynamic>> data) async {
    await _prefs.setString(key, jsonEncode(data));
    await _prefs.setInt('${key}_timestamp', DateTime.now().millisecondsSinceEpoch);
  }

  /// Clear all cached satellite data
  /// مسح جميع بيانات الأقمار الصناعية المخزنة مؤقتاً
  Future<void> clearCache() async {
    final keys = _prefs.getKeys();
    final satelliteKeys = keys.where((key) =>
        key.startsWith('field_health_') ||
        key.startsWith('ndvi_') ||
        key.startsWith('weather_') ||
        key.startsWith('phenology_') ||
        key.startsWith('vegetation_indices_'));

    for (final key in satelliteKeys) {
      await _prefs.remove(key);
      await _prefs.remove('${key}_timestamp');
    }
  }

  /// Clear cache for specific field
  /// مسح التخزين المؤقت لحقل محدد
  Future<void> clearFieldCache(String fieldId) async {
    final keys = [
      'field_health_$fieldId',
      'ndvi_analysis_$fieldId',
      'weather_forecast_$fieldId',
      'weather_alerts_$fieldId',
      'phenology_data_$fieldId',
      'vegetation_indices_$fieldId',
    ];

    for (final key in keys) {
      await _prefs.remove(key);
      await _prefs.remove('${key}_timestamp');
    }
  }
}
