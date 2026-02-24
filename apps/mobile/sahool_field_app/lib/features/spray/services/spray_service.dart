/// Spray Advisor Service - خدمة مستشار الرش
/// يتواصل مع Spray Advisor API Service
/// Supports offline-first architecture with local caching
library;

import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../core/config/api_config.dart';
import '../../../core/config/env_config.dart';
import '../models/spray_models.dart';

/// Spray Service Provider
final sprayServiceProvider = Provider<SprayService>((ref) {
  return SprayService();
});

/// نتيجة API
class ApiResult<T> {
  final T? data;
  final String? error;
  final String? errorAr;
  final bool isSuccess;
  final bool isFromCache;

  const ApiResult._({
    this.data,
    this.error,
    this.errorAr,
    required this.isSuccess,
    this.isFromCache = false,
  });

  factory ApiResult.success(T data, {bool isFromCache = false}) =>
      ApiResult._(data: data, isSuccess: true, isFromCache: isFromCache);
  factory ApiResult.failure(String error, [String? errorAr]) =>
      ApiResult._(error: error, errorAr: errorAr, isSuccess: false);
}

/// Cache keys for offline support
class _CacheKeys {
  static String recommendations(String? fieldId) =>
      'spray_recommendations_${fieldId ?? 'all'}';
  static String products(String? type) => 'spray_products_${type ?? 'all'}';
  static String logs(String? fieldId) => 'spray_logs_${fieldId ?? 'all'}';
  static String currentWeather(String fieldId) => 'spray_weather_$fieldId';
  static String sprayWindows(String fieldId) => 'spray_windows_$fieldId';
}

/// Spray Advisor Service
class SprayService {
  final Dio _dio;
  SharedPreferences? _prefs;

  /// Cache expiry duration (1 hour for weather, 24 hours for products)
  static const Duration _weatherCacheExpiry = Duration(hours: 1);
  static const Duration _dataCacheExpiry = Duration(hours: 24);

  SprayService({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: EnvConfig.sprayUrl,
              connectTimeout: ApiConfig.connectTimeout,
              sendTimeout: ApiConfig.sendTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            )) {
    _initPrefs();
  }

  Future<void> _initPrefs() async {
    _prefs = await SharedPreferences.getInstance();
  }

  /// Save data to cache with timestamp
  Future<void> _saveToCache(String key, dynamic data) async {
    _prefs ??= await SharedPreferences.getInstance();
    final cacheData = {
      'timestamp': DateTime.now().toIso8601String(),
      'data': data,
    };
    await _prefs!.setString(key, jsonEncode(cacheData));
  }

  /// Get data from cache if not expired
  Future<dynamic> _getFromCache(String key, Duration expiry) async {
    _prefs ??= await SharedPreferences.getInstance();
    final cached = _prefs!.getString(key);
    if (cached == null) return null;

    try {
      final cacheData = jsonDecode(cached) as Map<String, dynamic>;
      final timestamp = DateTime.parse(cacheData['timestamp'] as String);
      if (DateTime.now().difference(timestamp) > expiry) {
        return null; // Cache expired
      }
      return cacheData['data'];
    } catch (_) {
      return null;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Spray Recommendations
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب توصيات الرش لحقل
  /// Supports offline-first: returns cached data if network fails
  Future<ApiResult<List<SprayRecommendation>>> getSprayRecommendations({
    String? fieldId,
    SprayType? sprayType,
    RecommendationStatus? status,
    DateTime? startDate,
    DateTime? endDate,
    int limit = 50,
    int offset = 0,
  }) async {
    final cacheKey = _CacheKeys.recommendations(fieldId);

    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };
      if (fieldId != null) queryParams['field_id'] = fieldId;
      if (sprayType != null) queryParams['spray_type'] = sprayType.value;
      if (status != null) queryParams['status'] = status.value;
      if (startDate != null)
        queryParams['start_date'] = startDate.toIso8601String();
      if (endDate != null) queryParams['end_date'] = endDate.toIso8601String();

      final response = await _dio.get(
        '/v1/spray/recommendations',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final recommendations = (data['recommendations'] as List)
          .map((e) => SprayRecommendation.fromJson(e as Map<String, dynamic>))
          .toList();

      // Cache the data for offline access
      await _saveToCache(cacheKey, data['recommendations']);

      return ApiResult.success(recommendations);
    } on DioException catch (e) {
      // Try to return cached data on network error
      final cached = await _getFromCache(cacheKey, _dataCacheExpiry);
      if (cached != null) {
        final recommendations = (cached as List)
            .map((e) => SprayRecommendation.fromJson(e as Map<String, dynamic>))
            .toList();
        return ApiResult.success(recommendations, isFromCache: true);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch spray recommendations',
        'فشل في جلب توصيات الرش',
      );
    } catch (e) {
      // Try cache on any error
      final cached = await _getFromCache(cacheKey, _dataCacheExpiry);
      if (cached != null) {
        final recommendations = (cached as List)
            .map((e) => SprayRecommendation.fromJson(e as Map<String, dynamic>))
            .toList();
        return ApiResult.success(recommendations, isFromCache: true);
      }
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب توصية محددة
  Future<ApiResult<SprayRecommendation>> getRecommendationById(
      String recommendationId) async {
    try {
      final response =
          await _dio.get('/v1/spray/recommendations/$recommendationId');
      return ApiResult.success(
        SprayRecommendation.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure(
            'Recommendation not found', 'التوصية غير موجودة');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch recommendation',
        'فشل في جلب التوصية',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// إنشاء توصية رش جديدة
  Future<ApiResult<SprayRecommendation>> createRecommendation({
    required String fieldId,
    required String title,
    String? titleAr,
    required String description,
    String? descriptionAr,
    required SprayType sprayType,
    String? productId,
    required double recommendedRate,
    required String unit,
    String? unitAr,
    DateTime? targetDate,
    int priority = 3,
    String? notes,
    String? notesAr,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/spray/recommendations',
        data: {
          'field_id': fieldId,
          'title': title,
          'title_ar': titleAr,
          'description': description,
          'description_ar': descriptionAr,
          'spray_type': sprayType.value,
          'product_id': productId,
          'recommended_rate': recommendedRate,
          'unit': unit,
          'unit_ar': unitAr,
          'target_date': targetDate?.toIso8601String(),
          'priority': priority,
          'notes': notes,
          'notes_ar': notesAr,
        },
      );

      return ApiResult.success(
        SprayRecommendation.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to create recommendation',
        'فشل في إنشاء التوصية',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تحديث حالة توصية
  Future<ApiResult<SprayRecommendation>> updateRecommendationStatus(
    String recommendationId,
    RecommendationStatus status, {
    String? notes,
    String? notesAr,
  }) async {
    try {
      final response = await _dio.put(
        '/v1/spray/recommendations/$recommendationId/status',
        data: {
          'status': status.value,
          'notes': notes,
          'notes_ar': notesAr,
        },
      );

      return ApiResult.success(
        SprayRecommendation.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to update recommendation status',
        'فشل في تحديث حالة التوصية',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// حذف توصية
  Future<ApiResult<void>> deleteRecommendation(String recommendationId) async {
    try {
      await _dio.delete('/v1/spray/recommendations/$recommendationId');
      return ApiResult.success(null);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure(
            'Recommendation not found', 'التوصية غير موجودة');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to delete recommendation',
        'فشل في حذف التوصية',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Spray Windows - نوافذ الرش
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب نوافذ الرش المثلى
  /// Supports offline-first: returns cached data if network fails
  Future<ApiResult<List<SprayWindow>>> getOptimalSprayWindows({
    required String fieldId,
    int days = 7,
  }) async {
    final cacheKey = _CacheKeys.sprayWindows(fieldId);

    try {
      final response = await _dio.get(
        '/v1/spray/windows',
        queryParameters: {
          'field_id': fieldId,
          'days': days,
        },
      );

      final data = response.data as Map<String, dynamic>;
      final windows = (data['windows'] as List)
          .map((e) => SprayWindow.fromJson(e as Map<String, dynamic>))
          .toList();

      // Cache for offline access (shorter expiry for time-sensitive data)
      await _saveToCache(cacheKey, data['windows']);

      return ApiResult.success(windows);
    } on DioException catch (e) {
      // Try cached data on network error
      final cached = await _getFromCache(cacheKey, _weatherCacheExpiry);
      if (cached != null) {
        final windows = (cached as List)
            .map((e) => SprayWindow.fromJson(e as Map<String, dynamic>))
            .toList();
        return ApiResult.success(windows, isFromCache: true);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch spray windows',
        'فشل في جلب نوافذ الرش',
      );
    } catch (e) {
      final cached = await _getFromCache(cacheKey, _weatherCacheExpiry);
      if (cached != null) {
        final windows = (cached as List)
            .map((e) => SprayWindow.fromJson(e as Map<String, dynamic>))
            .toList();
        return ApiResult.success(windows, isFromCache: true);
      }
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب نافذة رش محددة
  Future<ApiResult<SprayWindow>> getSprayWindowById(String windowId) async {
    try {
      final response = await _dio.get('/v1/spray/windows/$windowId');
      return ApiResult.success(
        SprayWindow.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure(
            'Spray window not found', 'نافذة الرش غير موجودة');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch spray window',
        'فشل في جلب نافذة الرش',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Weather Forecast - توقعات الطقس
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب توقعات الطقس للحقل
  Future<ApiResult<List<WeatherCondition>>> getWeatherForecast({
    required String fieldId,
    int days = 7,
  }) async {
    try {
      final response = await _dio.get(
        '/v1/spray/weather/forecast',
        queryParameters: {
          'field_id': fieldId,
          'days': days,
        },
      );

      final data = response.data as Map<String, dynamic>;
      final forecast = (data['forecast'] as List)
          .map((e) => WeatherCondition.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(forecast);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch weather forecast',
        'فشل في جلب توقعات الطقس',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب الطقس الحالي
  /// Supports offline-first: returns cached data if network fails
  Future<ApiResult<WeatherCondition>> getCurrentWeather({
    required String fieldId,
  }) async {
    final cacheKey = _CacheKeys.currentWeather(fieldId);

    try {
      final response = await _dio.get(
        '/v1/spray/weather/current',
        queryParameters: {
          'field_id': fieldId,
        },
      );

      // Cache for offline access
      await _saveToCache(cacheKey, response.data);

      return ApiResult.success(
        WeatherCondition.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      // Try cached weather on network error
      final cached = await _getFromCache(cacheKey, _weatherCacheExpiry);
      if (cached != null) {
        return ApiResult.success(
          WeatherCondition.fromJson(cached as Map<String, dynamic>),
          isFromCache: true,
        );
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch current weather',
        'فشل في جلب الطقس الحالي',
      );
    } catch (e) {
      final cached = await _getFromCache(cacheKey, _weatherCacheExpiry);
      if (cached != null) {
        return ApiResult.success(
          WeatherCondition.fromJson(cached as Map<String, dynamic>),
          isFromCache: true,
        );
      }
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Spray Products - منتجات الرش
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب منتجات الرش
  /// Supports offline-first: returns cached data if network fails
  Future<ApiResult<List<SprayProduct>>> getSprayProducts({
    SprayType? sprayType,
    bool yemenProductsOnly = false,
    String? search,
    int limit = 100,
    int offset = 0,
  }) async {
    final cacheKey = _CacheKeys.products(sprayType?.value);

    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };
      if (sprayType != null) queryParams['spray_type'] = sprayType.value;
      if (yemenProductsOnly) queryParams['yemen_products_only'] = true;
      if (search != null && search.isNotEmpty) queryParams['search'] = search;

      final response = await _dio.get(
        '/v1/spray/products',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final products = (data['products'] as List)
          .map((e) => SprayProduct.fromJson(e as Map<String, dynamic>))
          .toList();

      // Cache for offline access (products rarely change)
      await _saveToCache(cacheKey, data['products']);

      return ApiResult.success(products);
    } on DioException catch (e) {
      // Try cached products on network error
      final cached = await _getFromCache(cacheKey, _dataCacheExpiry);
      if (cached != null) {
        final products = (cached as List)
            .map((e) => SprayProduct.fromJson(e as Map<String, dynamic>))
            .toList();
        return ApiResult.success(products, isFromCache: true);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch spray products',
        'فشل في جلب منتجات الرش',
      );
    } catch (e) {
      final cached = await _getFromCache(cacheKey, _dataCacheExpiry);
      if (cached != null) {
        final products = (cached as List)
            .map((e) => SprayProduct.fromJson(e as Map<String, dynamic>))
            .toList();
        return ApiResult.success(products, isFromCache: true);
      }
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب منتج محدد
  Future<ApiResult<SprayProduct>> getProductById(String productId) async {
    try {
      final response = await _dio.get('/v1/spray/products/$productId');
      return ApiResult.success(
        SprayProduct.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Product not found', 'المنتج غير موجود');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch product',
        'فشل في جلب المنتج',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Spray Application Logs - سجلات تطبيق الرش
  // ─────────────────────────────────────────────────────────────────────────────

  /// تسجيل تطبيق رش
  Future<ApiResult<SprayApplicationLog>> logSprayApplication({
    required String fieldId,
    String? recommendationId,
    required SprayType sprayType,
    required String productId,
    required double appliedRate,
    required String unit,
    String? unitAr,
    required double area,
    required DateTime applicationDate,
    String? applicatorName,
    String? equipmentUsed,
    String? equipmentUsedAr,
    List<String> photoUrls = const [],
    String? notes,
    String? notesAr,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/spray/logs',
        data: {
          'field_id': fieldId,
          'recommendation_id': recommendationId,
          'spray_type': sprayType.value,
          'product_id': productId,
          'applied_rate': appliedRate,
          'unit': unit,
          'unit_ar': unitAr,
          'area': area,
          'application_date': applicationDate.toIso8601String(),
          'applicator_name': applicatorName,
          'equipment_used': equipmentUsed,
          'equipment_used_ar': equipmentUsedAr,
          'photo_urls': photoUrls,
          'notes': notes,
          'notes_ar': notesAr,
        },
      );

      return ApiResult.success(
        SprayApplicationLog.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to log spray application',
        'فشل في تسجيل تطبيق الرش',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب سجلات تطبيق الرش
  /// Supports offline-first: returns cached data if network fails
  Future<ApiResult<List<SprayApplicationLog>>> getSprayLogs({
    String? fieldId,
    SprayType? sprayType,
    DateTime? startDate,
    DateTime? endDate,
    int limit = 50,
    int offset = 0,
  }) async {
    final cacheKey = _CacheKeys.logs(fieldId);

    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };
      if (fieldId != null) queryParams['field_id'] = fieldId;
      if (sprayType != null) queryParams['spray_type'] = sprayType.value;
      if (startDate != null)
        queryParams['start_date'] = startDate.toIso8601String();
      if (endDate != null) queryParams['end_date'] = endDate.toIso8601String();

      final response = await _dio.get(
        '/v1/spray/logs',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final logs = (data['logs'] as List)
          .map((e) => SprayApplicationLog.fromJson(e as Map<String, dynamic>))
          .toList();

      // Cache for offline access
      await _saveToCache(cacheKey, data['logs']);

      return ApiResult.success(logs);
    } on DioException catch (e) {
      // Try cached logs on network error
      final cached = await _getFromCache(cacheKey, _dataCacheExpiry);
      if (cached != null) {
        final logs = (cached as List)
            .map((e) => SprayApplicationLog.fromJson(e as Map<String, dynamic>))
            .toList();
        return ApiResult.success(logs, isFromCache: true);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch spray logs',
        'فشل في جلب سجلات الرش',
      );
    } catch (e) {
      final cached = await _getFromCache(cacheKey, _dataCacheExpiry);
      if (cached != null) {
        final logs = (cached as List)
            .map((e) => SprayApplicationLog.fromJson(e as Map<String, dynamic>))
            .toList();
        return ApiResult.success(logs, isFromCache: true);
      }
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب سجل محدد
  Future<ApiResult<SprayApplicationLog>> getLogById(String logId) async {
    try {
      final response = await _dio.get('/v1/spray/logs/$logId');
      return ApiResult.success(
        SprayApplicationLog.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Log not found', 'السجل غير موجود');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch log',
        'فشل في جلب السجل',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// حذف سجل
  Future<ApiResult<void>> deleteLog(String logId) async {
    try {
      await _dio.delete('/v1/spray/logs/$logId');
      return ApiResult.success(null);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Log not found', 'السجل غير موجود');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to delete log',
        'فشل في حذف السجل',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Photo Upload - رفع الصور
  // ─────────────────────────────────────────────────────────────────────────────

  /// رفع صورة
  Future<ApiResult<String>> uploadPhoto(String filePath) async {
    try {
      final formData = FormData.fromMap({
        'photo': await MultipartFile.fromFile(filePath),
      });

      final response = await _dio.post(
        '/v1/spray/upload',
        data: formData,
      );

      final data = response.data as Map<String, dynamic>;
      return ApiResult.success(data['url'] as String);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to upload photo',
        'فشل في رفع الصورة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }
}
