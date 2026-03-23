/// GDD Service - خدمة درجات النمو الحراري
/// يتواصل مع FastAPI GDD Service
library;

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/config/api_config.dart';
import '../models/gdd_models.dart';

/// GDD Service Provider
final gddServiceProvider = Provider<GDDService>((ref) {
  return GDDService();
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

/// GDD Service
class GDDService {
  final Dio _dio;

  GDDService({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              sendTimeout: ApiConfig.sendTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  // ═════════════════════════════════════════════════════════════════════════════
  // GDD Accumulation & Records
  // ═════════════════════════════════════════════════════════════════════════════

  /// جلب تراكم GDD للحقل
  Future<ApiResult<GDDAccumulation>> getGDDAccumulation(
    String fieldId, {
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String().split('T')[0];
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String().split('T')[0];
      }

      final response = await _dio.get(
        '/api/v1/gdd/fields/$fieldId/accumulation',
        queryParameters: queryParams,
      );

      return ApiResult.success(
        GDDAccumulation.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure(
          'Field not found or no GDD data',
          'الحقل غير موجود أو لا توجد بيانات GDD',
        );
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch GDD accumulation',
        'فشل في جلب تراكم GDD',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب سجلات GDD اليومية
  Future<ApiResult<List<GDDRecord>>> getGDDRecords(
    String fieldId, {
    DateTime? startDate,
    DateTime? endDate,
    int limit = 100,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
      };
      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String().split('T')[0];
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String().split('T')[0];
      }

      final response = await _dio.get(
        '/api/v1/gdd/fields/$fieldId/records',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final records = (data['records'] as List)
          .map((e) => GDDRecord.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(records);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch GDD records',
        'فشل في جلب سجلات GDD',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// حساب GDD يدوياً
  Future<ApiResult<GDDRecord>> calculateGDD(
    String fieldId, {
    required DateTime date,
    required double tMin,
    required double tMax,
    double? baseTemperature,
    double? upperThreshold,
    GDDCalculationMethod? method,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/gdd/fields/$fieldId/calculate',
        data: {
          'date': date.toIso8601String().split('T')[0],
          't_min': tMin,
          't_max': tMax,
          if (baseTemperature != null) 'base_temperature': baseTemperature,
          if (upperThreshold != null) 'upper_threshold': upperThreshold,
          if (method != null) 'calculation_method': method.value,
        },
      );

      return ApiResult.success(
        GDDRecord.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to calculate GDD',
        'فشل في حساب GDD',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // Growth Stages
  // ═════════════════════════════════════════════════════════════════════════════

  /// جلب المرحلة الحالية للنمو
  Future<ApiResult<GrowthStage>> getCurrentGrowthStage(String fieldId) async {
    try {
      final response = await _dio.get(
        '/api/v1/gdd/fields/$fieldId/current-stage',
      );

      return ApiResult.success(
        GrowthStage.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure(
          'No current growth stage found',
          'لا توجد مرحلة نمو حالية',
        );
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch current growth stage',
        'فشل في جلب مرحلة النمو الحالية',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب جميع مراحل النمو للمحصول
  Future<ApiResult<List<GrowthStage>>> getGrowthStages(
    String fieldId,
  ) async {
    try {
      final response = await _dio.get(
        '/api/v1/gdd/fields/$fieldId/stages',
      );

      final data = response.data as Map<String, dynamic>;
      final stages = (data['stages'] as List)
          .map((e) => GrowthStage.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(stages);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch growth stages',
        'فشل في جلب مراحل النمو',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // Crop Requirements
  // ═════════════════════════════════════════════════════════════════════════════

  /// جلب متطلبات GDD للمحصول
  Future<ApiResult<CropGDDRequirements>> getCropGDDRequirements(
    CropType cropType,
  ) async {
    try {
      final response = await _dio.get(
        '/api/v1/gdd/crops/${cropType.value}/requirements',
      );

      return ApiResult.success(
        CropGDDRequirements.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure(
          'Crop requirements not found',
          'متطلبات المحصول غير موجودة',
        );
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch crop requirements',
        'فشل في جلب متطلبات المحصول',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب قائمة المحاصيل المدعومة
  Future<ApiResult<List<CropGDDRequirements>>> getSupportedCrops() async {
    try {
      final response = await _dio.get('/api/v1/gdd/crops');

      final data = response.data as Map<String, dynamic>;
      final crops = (data['crops'] as List)
          .map((e) => CropGDDRequirements.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(crops);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch supported crops',
        'فشل في جلب المحاصيل المدعومة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // Forecast
  // ═════════════════════════════════════════════════════════════════════════════

  /// جلب توقعات GDD
  Future<ApiResult<List<GDDForecast>>> getGDDForecast(
    String fieldId, {
    int days = 7,
  }) async {
    try {
      final response = await _dio.get(
        '/api/v1/gdd/fields/$fieldId/forecast',
        queryParameters: {'days': days},
      );

      final data = response.data as Map<String, dynamic>;
      final forecasts = (data['forecasts'] as List)
          .map((e) => GDDForecast.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(forecasts);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch GDD forecast',
        'فشل في جلب توقعات GDD',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // Settings
  // ═════════════════════════════════════════════════════════════════════════════

  /// جلب إعدادات GDD للحقل
  Future<ApiResult<GDDSettings>> getGDDSettings(String fieldId) async {
    try {
      final response = await _dio.get(
        '/api/v1/gdd/fields/$fieldId/settings',
      );

      return ApiResult.success(
        GDDSettings.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure(
          'GDD settings not found',
          'إعدادات GDD غير موجودة',
        );
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch GDD settings',
        'فشل في جلب إعدادات GDD',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تحديث إعدادات GDD للحقل
  Future<ApiResult<GDDSettings>> updateGDDSettings(
    String fieldId,
    GDDSettings settings,
  ) async {
    try {
      final response = await _dio.put(
        '/api/v1/gdd/fields/$fieldId/settings',
        data: settings.toJson(),
      );

      return ApiResult.success(
        GDDSettings.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to update GDD settings',
        'فشل في تحديث إعدادات GDD',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// إنشاء إعدادات GDD للحقل
  Future<ApiResult<GDDSettings>> createGDDSettings(
    GDDSettings settings,
  ) async {
    try {
      final response = await _dio.post(
        '/api/v1/gdd/fields/${settings.fieldId}/settings',
        data: settings.toJson(),
      );

      return ApiResult.success(
        GDDSettings.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to create GDD settings',
        'فشل في إنشاء إعدادات GDD',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // Comparison & Analysis
  // ═════════════════════════════════════════════════════════════════════════════

  /// مقارنة GDD بين المواسم
  Future<ApiResult<Map<String, dynamic>>> compareSeasons(
    String fieldId, {
    required int currentYear,
    required int comparisonYear,
  }) async {
    try {
      final response = await _dio.get(
        '/api/v1/gdd/fields/$fieldId/compare',
        queryParameters: {
          'current_year': currentYear,
          'comparison_year': comparisonYear,
        },
      );

      return ApiResult.success(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to compare seasons',
        'فشل في مقارنة المواسم',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تحليل اتجاه GDD
  Future<ApiResult<Map<String, dynamic>>> getGDDTrend(
    String fieldId, {
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (startDate != null) {
        queryParams['start_date'] = startDate.toIso8601String().split('T')[0];
      }
      if (endDate != null) {
        queryParams['end_date'] = endDate.toIso8601String().split('T')[0];
      }

      final response = await _dio.get(
        '/api/v1/gdd/fields/$fieldId/trend',
        queryParameters: queryParams,
      );

      return ApiResult.success(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to get GDD trend',
        'فشل في جلب اتجاه GDD',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }
}
