library;

/// Weather Repository - Offline-First Weather Data Access
/// مستودع الطقس - وصول البيانات مع دعم العمل بدون اتصال
///
/// Implements offline-first caching for weather data with:
/// - In-memory cache for fast access
/// - Local storage for offline support
/// - Provider fallback for reliable data fetching
/// - Automatic cache expiration

import 'dart:async';
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../../domain/entities/weather_entities.dart';
import '../remote/weather_api.dart';
import '../../../../core/services/weather_provider_service.dart'
    hide WeatherData;
import '../../../../core/config/providers_config.dart';
import '../../../../core/utils/app_logger.dart';

/// Cache entry with expiration tracking
class _CacheEntry<T> {
  final T data;
  final DateTime cachedAt;
  final Duration ttl;

  _CacheEntry({
    required this.data,
    required this.cachedAt,
    required this.ttl,
  });

  bool get isExpired => DateTime.now().difference(cachedAt) > ttl;

  Map<String, dynamic> toJson(Map<String, dynamic> Function(T) encoder) => {
        'data': encoder(data),
        'cachedAt': cachedAt.toIso8601String(),
        'ttlMinutes': ttl.inMinutes,
      };

  static _CacheEntry<T>? fromJson<T>(
    Map<String, dynamic>? json,
    T Function(Map<String, dynamic>) decoder,
  ) {
    if (json == null) return null;
    try {
      return _CacheEntry<T>(
        data: decoder(json['data'] as Map<String, dynamic>),
        cachedAt: DateTime.parse(json['cachedAt'] as String),
        ttl: Duration(minutes: json['ttlMinutes'] as int? ?? 10),
      );
    } catch (e) {
      return null;
    }
  }
}

/// Weather Repository with offline-first caching
/// مستودع الطقس مع دعم التخزين المؤقت والعمل بدون اتصال
class WeatherRepository {
  final WeatherApi _api;
  final WeatherProviderService _providerService;
  final SharedPreferences? _prefs;

  static const _tag = 'WeatherRepo';

  // Cache durations
  static const _currentWeatherTtl = Duration(minutes: 10);
  static const _forecastTtl = Duration(minutes: 30);
  static const _alertsTtl = Duration(minutes: 15);
  static const _impactsTtl = Duration(minutes: 30);

  // In-memory cache
  final Map<String, _CacheEntry<WeatherData>> _weatherCache = {};
  final Map<String, _CacheEntry<List<DailyForecast>>> _forecastCache = {};
  final Map<String, _CacheEntry<List<HourlyForecast>>> _hourlyCache = {};
  final Map<String, _CacheEntry<List<WeatherAlert>>> _alertsCache = {};
  final Map<String, _CacheEntry<List<AgriculturalImpact>>> _impactsCache = {};

  // Storage keys
  static const _weatherStorageKey = 'weather_cache';
  static const _forecastStorageKey = 'forecast_cache';
  static const _alertsStorageKey = 'alerts_cache';
  static const _impactsStorageKey = 'impacts_cache';

  WeatherRepository({
    WeatherApi? api,
    WeatherProviderService? providerService,
    SharedPreferences? prefs,
    String? authToken,
  })  : _api = api ?? WeatherApi(authToken: authToken),
        _providerService = providerService ??
            WeatherProviderService(config: const ProvidersConfig()),
        _prefs = prefs {
    _loadFromStorage();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Current Weather - الطقس الحالي
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get current weather for a field
  /// جلب الطقس الحالي للحقل
  Future<WeatherData> getWeatherForField(String fieldId) async {
    final cacheKey = 'field_$fieldId';

    // Check in-memory cache
    final cached = _weatherCache[cacheKey];
    if (cached != null && !cached.isExpired) {
      AppLogger.d('Weather cache hit', tag: _tag, data: {'fieldId': fieldId});
      return cached.data;
    }

    try {
      // Try API first
      final data = await _api.getFieldWeather(fieldId);
      _cacheWeather(cacheKey, data);
      return data;
    } catch (e) {
      AppLogger.w('API failed, trying cache',
          tag: _tag, data: {'error': e.toString()});

      // Return stale cache if available
      if (cached != null) {
        AppLogger.i('Returning stale cache', tag: _tag);
        return cached.data;
      }

      rethrow;
    }
  }

  /// Get weather by coordinates using multi-provider fallback
  /// جلب الطقس بالإحداثيات مع دعم مزودين متعددين
  Future<WeatherData> getWeatherByCoordinates(double lat, double lon) async {
    final cacheKey =
        'coord_${lat.toStringAsFixed(2)}_${lon.toStringAsFixed(2)}';

    // Check in-memory cache
    final cached = _weatherCache[cacheKey];
    if (cached != null && !cached.isExpired) {
      AppLogger.d('Weather cache hit (coords)', tag: _tag);
      return cached.data;
    }

    try {
      // Try primary API
      final data = await _api.getWeatherByCoordinates(lat, lon);
      _cacheWeather(cacheKey, data);
      return data;
    } catch (e) {
      AppLogger.w('Primary API failed, trying provider service', tag: _tag);

      // Fallback to multi-provider service
      try {
        final result = await _providerService.getCurrentWeather(lat, lon);
        if (result.success && result.data != null) {
          // Convert provider data to domain entity
          final providerData = result.data!;
          final weatherData = WeatherData(
            current: CurrentWeather(
              temperature: providerData.temperature,
              feelsLike: providerData.temperature - 2, // Estimate
              humidity: providerData.humidity.toInt(),
              windSpeed: providerData.windSpeed,
              windDirection: providerData.windDirection,
              condition: providerData.condition,
              conditionAr: providerData.conditionAr,
              icon: providerData.icon,
              precipitation: providerData.precipitation,
              uvIndex: providerData.uvIndex,
              timestamp: providerData.timestamp,
            ),
            hourly: [],
            daily: [],
            alerts: [],
            impacts: [],
          );
          _cacheWeather(cacheKey, weatherData);
          return weatherData;
        }
      } catch (providerError) {
        AppLogger.w('Provider service also failed', tag: _tag);
      }

      // Return stale cache if available
      if (cached != null) {
        AppLogger.i('Returning stale cache', tag: _tag);
        return cached.data;
      }

      rethrow;
    }
  }

  /// Get weather by location name
  /// جلب الطقس باسم الموقع
  Future<WeatherData> getWeatherByLocation(String location) async {
    final cacheKey = 'location_$location';

    // Check in-memory cache
    final cached = _weatherCache[cacheKey];
    if (cached != null && !cached.isExpired) {
      return cached.data;
    }

    try {
      final data = await _api.getCurrentWeather(location);
      _cacheWeather(cacheKey, data);
      return data;
    } catch (e) {
      // Return stale cache if available
      if (cached != null) {
        return cached.data;
      }
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Forecasts - التوقعات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get daily forecast for a location
  /// جلب التوقعات اليومية للموقع
  Future<List<DailyForecast>> getDailyForecast(
    String location, {
    int days = 7,
  }) async {
    final cacheKey = 'daily_${location}_$days';

    // Check in-memory cache
    final cached = _forecastCache[cacheKey];
    if (cached != null && !cached.isExpired) {
      return cached.data;
    }

    try {
      final data = await _api.getForecast(location, days: days);
      _cacheForecast(cacheKey, data);
      return data;
    } catch (e) {
      // Return stale cache if available
      if (cached != null) {
        return cached.data;
      }
      rethrow;
    }
  }

  /// Get daily forecast for a field
  /// جلب التوقعات اليومية للحقل
  Future<List<DailyForecast>> getDailyForecastForField(
    String fieldId, {
    int days = 7,
  }) async {
    final cacheKey = 'daily_field_${fieldId}_$days';

    // Check in-memory cache
    final cached = _forecastCache[cacheKey];
    if (cached != null && !cached.isExpired) {
      return cached.data;
    }

    try {
      final data = await _api.getDailyForecast(fieldId, days: days);
      _cacheForecast(cacheKey, data);
      return data;
    } catch (e) {
      // Return stale cache if available
      if (cached != null) {
        return cached.data;
      }
      rethrow;
    }
  }

  /// Get hourly forecast
  /// جلب التوقعات الساعية
  Future<List<HourlyForecast>> getHourlyForecast(
    String location, {
    int hours = 24,
  }) async {
    final cacheKey = 'hourly_${location}_$hours';

    // Check in-memory cache
    final cached = _hourlyCache[cacheKey];
    if (cached != null && !cached.isExpired) {
      return cached.data;
    }

    try {
      final data = await _api.getHourlyForecast(location, hours: hours);
      _cacheHourly(cacheKey, data);
      return data;
    } catch (e) {
      // Return stale cache if available
      if (cached != null) {
        return cached.data;
      }
      rethrow;
    }
  }

  /// Get forecast by coordinates using provider fallback
  /// جلب التوقعات بالإحداثيات مع دعم مزودين متعددين
  Future<List<DailyForecast>> getForecastByCoordinates(
    double lat,
    double lon, {
    int days = 7,
  }) async {
    final cacheKey =
        'daily_coord_${lat.toStringAsFixed(2)}_${lon.toStringAsFixed(2)}_$days';

    // Check in-memory cache
    final cached = _forecastCache[cacheKey];
    if (cached != null && !cached.isExpired) {
      return cached.data;
    }

    try {
      // Try provider service for coordinates
      final result = await _providerService.getForecast(lat, lon, days: days);
      if (result.success && result.data != null) {
        final forecasts = result.data!
            .map((f) => DailyForecast(
                  date: f.date,
                  tempMin: f.tempMin,
                  tempMax: f.tempMax,
                  condition: f.condition,
                  conditionAr: f.conditionAr,
                  icon: f.icon,
                  precipitationChance: f.precipitationProbability,
                  precipitationAmount: f.precipitation,
                  humidity: 50, // Default estimate
                  windSpeed: f.windSpeed,
                ))
            .toList();
        _cacheForecast(cacheKey, forecasts);
        return forecasts;
      }
      throw Exception(result.error ?? 'Failed to fetch forecast');
    } catch (e) {
      // Return stale cache if available
      if (cached != null) {
        return cached.data;
      }
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Alerts - التنبيهات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get weather alerts for a location
  /// جلب تنبيهات الطقس للموقع
  Future<List<WeatherAlert>> getAlerts(String location) async {
    final cacheKey = 'alerts_$location';

    // Check in-memory cache
    final cached = _alertsCache[cacheKey];
    if (cached != null && !cached.isExpired) {
      return cached.data;
    }

    try {
      final data = await _api.getAlerts(location);
      _cacheAlerts(cacheKey, data);
      return data;
    } catch (e) {
      // Return stale cache or empty list
      if (cached != null) {
        return cached.data;
      }
      return [];
    }
  }

  /// Get weather alerts for a field
  /// جلب تنبيهات الطقس للحقل
  Future<List<WeatherAlert>> getAlertsForField(String fieldId) async {
    final cacheKey = 'alerts_field_$fieldId';

    // Check in-memory cache
    final cached = _alertsCache[cacheKey];
    if (cached != null && !cached.isExpired) {
      return cached.data;
    }

    try {
      final data = await _api.getWeatherAlerts(fieldId);
      _cacheAlerts(cacheKey, data);
      return data;
    } catch (e) {
      // Return stale cache or empty list
      if (cached != null) {
        return cached.data;
      }
      return [];
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Agricultural Impacts - التأثيرات الزراعية
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get agricultural impacts for a location
  /// جلب التأثيرات الزراعية للموقع
  Future<List<AgriculturalImpact>> getAgriculturalImpacts({
    String? location,
    String? cropType,
  }) async {
    final cacheKey = 'impacts_${location ?? 'all'}_${cropType ?? 'all'}';

    // Check in-memory cache
    final cached = _impactsCache[cacheKey];
    if (cached != null && !cached.isExpired) {
      return cached.data;
    }

    try {
      final data = await _api.getAgriculturalCalendar(
        location: location,
        cropType: cropType,
      );
      _cacheImpacts(cacheKey, data);
      return data;
    } catch (e) {
      // Return stale cache or empty list
      if (cached != null) {
        return cached.data;
      }
      return [];
    }
  }

  /// Get agricultural impacts for a field
  /// جلب التأثيرات الزراعية للحقل
  Future<List<AgriculturalImpact>> getImpactsForField(String fieldId) async {
    final cacheKey = 'impacts_field_$fieldId';

    // Check in-memory cache
    final cached = _impactsCache[cacheKey];
    if (cached != null && !cached.isExpired) {
      return cached.data;
    }

    try {
      final data = await _api.getAgriculturalImpacts(fieldId);
      _cacheImpacts(cacheKey, data);
      return data;
    } catch (e) {
      // Return stale cache or empty list
      if (cached != null) {
        return cached.data;
      }
      return [];
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Locations - المواقع
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get available weather locations
  /// جلب المواقع المتاحة
  Future<List<WeatherLocation>> getAvailableLocations() async {
    return _api.getAvailableLocations();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Cache Management - إدارة التخزين المؤقت
  // ═══════════════════════════════════════════════════════════════════════════

  void _cacheWeather(String key, WeatherData data) {
    _weatherCache[key] = _CacheEntry(
      data: data,
      cachedAt: DateTime.now(),
      ttl: _currentWeatherTtl,
    );
    _saveToStorage();
  }

  void _cacheForecast(String key, List<DailyForecast> data) {
    _forecastCache[key] = _CacheEntry(
      data: data,
      cachedAt: DateTime.now(),
      ttl: _forecastTtl,
    );
    _saveToStorage();
  }

  void _cacheHourly(String key, List<HourlyForecast> data) {
    _hourlyCache[key] = _CacheEntry(
      data: data,
      cachedAt: DateTime.now(),
      ttl: _forecastTtl,
    );
    _saveToStorage();
  }

  void _cacheAlerts(String key, List<WeatherAlert> data) {
    _alertsCache[key] = _CacheEntry(
      data: data,
      cachedAt: DateTime.now(),
      ttl: _alertsTtl,
    );
    _saveToStorage();
  }

  void _cacheImpacts(String key, List<AgriculturalImpact> data) {
    _impactsCache[key] = _CacheEntry(
      data: data,
      cachedAt: DateTime.now(),
      ttl: _impactsTtl,
    );
    _saveToStorage();
  }

  /// Clear all caches
  /// مسح جميع البيانات المؤقتة
  void clearCache() {
    _weatherCache.clear();
    _forecastCache.clear();
    _hourlyCache.clear();
    _alertsCache.clear();
    _impactsCache.clear();
    _clearStorage();
    AppLogger.i('Weather cache cleared', tag: _tag);
  }

  /// Clear expired cache entries
  /// مسح البيانات المنتهية الصلاحية
  void clearExpired() {
    _weatherCache.removeWhere((_, entry) => entry.isExpired);
    _forecastCache.removeWhere((_, entry) => entry.isExpired);
    _hourlyCache.removeWhere((_, entry) => entry.isExpired);
    _alertsCache.removeWhere((_, entry) => entry.isExpired);
    _impactsCache.removeWhere((_, entry) => entry.isExpired);
    _saveToStorage();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Persistent Storage - التخزين الدائم
  // ═══════════════════════════════════════════════════════════════════════════

  Future<void> _saveToStorage() async {
    final prefs = _prefs;
    if (prefs == null) return;

    try {
      // Save weather cache
      final weatherJson = <String, dynamic>{};
      for (final entry in _weatherCache.entries) {
        weatherJson[entry.key] = entry.value.toJson(
          (data) => data.toJson(),
        );
      }
      await prefs.setString(_weatherStorageKey, jsonEncode(weatherJson));

      // Save forecast cache
      final forecastJson = <String, dynamic>{};
      for (final entry in _forecastCache.entries) {
        forecastJson[entry.key] = {
          'data': entry.value.data.map((f) => f.toJson()).toList(),
          'cachedAt': entry.value.cachedAt.toIso8601String(),
          'ttlMinutes': entry.value.ttl.inMinutes,
        };
      }
      await prefs.setString(_forecastStorageKey, jsonEncode(forecastJson));
    } catch (e) {
      AppLogger.w('Failed to save to storage',
          tag: _tag, data: {'error': e.toString()});
    }
  }

  Future<void> _loadFromStorage() async {
    final prefs = _prefs;
    if (prefs == null) return;

    try {
      // Load weather cache
      final weatherStr = prefs.getString(_weatherStorageKey);
      if (weatherStr != null) {
        final weatherJson = jsonDecode(weatherStr) as Map<String, dynamic>;
        for (final entry in weatherJson.entries) {
          final cached = _CacheEntry.fromJson<WeatherData>(
            entry.value as Map<String, dynamic>?,
            (json) => WeatherData.fromJson(json),
          );
          if (cached != null && !cached.isExpired) {
            _weatherCache[entry.key] = cached;
          }
        }
      }

      // Load forecast cache
      final forecastStr = prefs.getString(_forecastStorageKey);
      if (forecastStr != null) {
        final forecastJson = jsonDecode(forecastStr) as Map<String, dynamic>;
        for (final entry in forecastJson.entries) {
          final json = entry.value as Map<String, dynamic>;
          final dataList = json['data'] as List?;
          if (dataList != null) {
            final data = dataList
                .map((d) => DailyForecast.fromJson(d as Map<String, dynamic>))
                .toList();
            final cached = _CacheEntry<List<DailyForecast>>(
              data: data,
              cachedAt: DateTime.parse(json['cachedAt'] as String),
              ttl: Duration(minutes: json['ttlMinutes'] as int? ?? 30),
            );
            if (!cached.isExpired) {
              _forecastCache[entry.key] = cached;
            }
          }
        }
      }

      AppLogger.d('Weather cache loaded from storage', tag: _tag, data: {
        'weatherEntries': _weatherCache.length,
        'forecastEntries': _forecastCache.length,
      });
    } catch (e) {
      AppLogger.w('Failed to load from storage',
          tag: _tag, data: {'error': e.toString()});
    }
  }

  void _clearStorage() {
    final prefs = _prefs;
    if (prefs == null) return;

    prefs.remove(_weatherStorageKey);
    prefs.remove(_forecastStorageKey);
    prefs.remove(_alertsStorageKey);
    prefs.remove(_impactsStorageKey);
  }

  void dispose() {
    _api.dispose();
    _providerService.clearCache();
  }
}
