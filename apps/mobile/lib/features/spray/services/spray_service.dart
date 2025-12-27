/// Spray Advisor Service - خدمة مستشار الرش
/// يتواصل مع Spray Advisor API Service
library;

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/config/api_config.dart';
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

  const ApiResult._({this.data, this.error, this.errorAr, required this.isSuccess});

  factory ApiResult.success(T data) => ApiResult._(data: data, isSuccess: true);
  factory ApiResult.failure(String error, [String? errorAr]) =>
      ApiResult._(error: error, errorAr: errorAr, isSuccess: false);
}

/// Spray Advisor Service
class SprayService {
  final Dio _dio;

  // Note: Add spray service port to ApiConfig when backend is ready
  static const int sprayServicePort = 8098;

  SprayService({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: 'http://${_getHost()}:$sprayServicePort',
              connectTimeout: ApiConfig.connectTimeout,
              sendTimeout: ApiConfig.sendTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  static String _getHost() {
    // Use same logic as ApiConfig
    return ApiConfig.baseUrl.contains('10.0.2.2') ? '10.0.2.2' : 'localhost';
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Spray Recommendations
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب توصيات الرش لحقل
  Future<ApiResult<List<SprayRecommendation>>> getSprayRecommendations({
    String? fieldId,
    SprayType? sprayType,
    RecommendationStatus? status,
    DateTime? startDate,
    DateTime? endDate,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };
      if (fieldId != null) queryParams['field_id'] = fieldId;
      if (sprayType != null) queryParams['spray_type'] = sprayType.value;
      if (status != null) queryParams['status'] = status.value;
      if (startDate != null) queryParams['start_date'] = startDate.toIso8601String();
      if (endDate != null) queryParams['end_date'] = endDate.toIso8601String();

      final response = await _dio.get(
        '/v1/spray/recommendations',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final recommendations = (data['recommendations'] as List)
          .map((e) => SprayRecommendation.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(recommendations);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch spray recommendations',
        'فشل في جلب توصيات الرش',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب توصية محددة
  Future<ApiResult<SprayRecommendation>> getRecommendationById(String recommendationId) async {
    try {
      final response = await _dio.get('/v1/spray/recommendations/$recommendationId');
      return ApiResult.success(
        SprayRecommendation.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Recommendation not found', 'التوصية غير موجودة');
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
        return ApiResult.failure('Recommendation not found', 'التوصية غير موجودة');
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
  Future<ApiResult<List<SprayWindow>>> getOptimalSprayWindows({
    required String fieldId,
    int days = 7,
  }) async {
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

      return ApiResult.success(windows);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch spray windows',
        'فشل في جلب نوافذ الرش',
      );
    } catch (e) {
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
        return ApiResult.failure('Spray window not found', 'نافذة الرش غير موجودة');
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
  Future<ApiResult<WeatherCondition>> getCurrentWeather({
    required String fieldId,
  }) async {
    try {
      final response = await _dio.get(
        '/v1/spray/weather/current',
        queryParameters: {
          'field_id': fieldId,
        },
      );

      return ApiResult.success(
        WeatherCondition.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch current weather',
        'فشل في جلب الطقس الحالي',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Spray Products - منتجات الرش
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب منتجات الرش
  Future<ApiResult<List<SprayProduct>>> getSprayProducts({
    SprayType? sprayType,
    bool yemenProductsOnly = false,
    String? search,
    int limit = 100,
    int offset = 0,
  }) async {
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

      return ApiResult.success(products);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch spray products',
        'فشل في جلب منتجات الرش',
      );
    } catch (e) {
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
  Future<ApiResult<List<SprayApplicationLog>>> getSprayLogs({
    String? fieldId,
    SprayType? sprayType,
    DateTime? startDate,
    DateTime? endDate,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };
      if (fieldId != null) queryParams['field_id'] = fieldId;
      if (sprayType != null) queryParams['spray_type'] = sprayType.value;
      if (startDate != null) queryParams['start_date'] = startDate.toIso8601String();
      if (endDate != null) queryParams['end_date'] = endDate.toIso8601String();

      final response = await _dio.get(
        '/v1/spray/logs',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final logs = (data['logs'] as List)
          .map((e) => SprayApplicationLog.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(logs);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch spray logs',
        'فشل في جلب سجلات الرش',
      );
    } catch (e) {
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
