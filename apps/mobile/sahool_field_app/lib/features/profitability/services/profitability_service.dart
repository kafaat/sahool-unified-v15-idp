/// Profitability Service - خدمة تحليل الربحية
/// يتواصل مع FastAPI Profitability Analysis Service
library;

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/config/api_config.dart';
import '../models/profitability_models.dart';

/// Profitability Service Provider
final profitabilityServiceProvider = Provider<ProfitabilityService>((ref) {
  return ProfitabilityService();
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

/// Profitability Service
class ProfitabilityService {
  final Dio _dio;

  ProfitabilityService({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: '${ApiConfig.effectiveBaseUrl}/profitability',
              connectTimeout: ApiConfig.connectTimeout,
              sendTimeout: ApiConfig.sendTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  // ─────────────────────────────────────────────────────────────────────────────
  // Profitability Analysis
  // ─────────────────────────────────────────────────────────────────────────────

  /// تحليل ربحية حقل محدد
  Future<ApiResult<CropProfitability>> analyzeProfitability({
    required String fieldId,
    required String season,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/analyze',
        data: {
          'field_id': fieldId,
          'season': season,
        },
      );

      return ApiResult.success(
        CropProfitability.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to analyze profitability',
        'فشل في تحليل الربحية',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// الحصول على تحليل ربحية محدد
  Future<ApiResult<CropProfitability>> getProfitabilityById(
    String profitabilityId,
  ) async {
    try {
      final response = await _dio.get('/v1/profitability/$profitabilityId');
      return ApiResult.success(
        CropProfitability.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Analysis not found', 'التحليل غير موجود');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch profitability',
        'فشل في جلب تحليل الربحية',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// الحصول على تحليلات الربحية لحقل
  Future<ApiResult<List<CropProfitability>>> getFieldProfitability({
    required String fieldId,
    String? season,
    DateTime? startDate,
    DateTime? endDate,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'field_id': fieldId,
        'limit': limit,
        'offset': offset,
      };
      if (season != null) queryParams['season'] = season;
      if (startDate != null) queryParams['start_date'] = startDate.toIso8601String();
      if (endDate != null) queryParams['end_date'] = endDate.toIso8601String();

      final response = await _dio.get(
        '/v1/profitability',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final profitability = (data['profitability'] as List)
          .map((e) => CropProfitability.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(profitability);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch profitability',
        'فشل في جلب تحليلات الربحية',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Season Summary
  // ─────────────────────────────────────────────────────────────────────────────

  /// الحصول على ملخص الموسم
  Future<ApiResult<SeasonSummary>> getSeasonSummary({
    required String farmId,
    required String season,
  }) async {
    try {
      final response = await _dio.get(
        '/v1/season-summary',
        queryParameters: {
          'farm_id': farmId,
          'season': season,
        },
      );

      return ApiResult.success(
        SeasonSummary.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch season summary',
        'فشل في جلب ملخص الموسم',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// الحصول على جميع ملخصات المواسم للمزرعة
  Future<ApiResult<List<SeasonSummary>>> getFarmSeasons({
    required String farmId,
    int limit = 10,
    int offset = 0,
  }) async {
    try {
      final response = await _dio.get(
        '/v1/farm-seasons',
        queryParameters: {
          'farm_id': farmId,
          'limit': limit,
          'offset': offset,
        },
      );

      final data = response.data as Map<String, dynamic>;
      final seasons = (data['seasons'] as List)
          .map((e) => SeasonSummary.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(seasons);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch farm seasons',
        'فشل في جلب مواسم المزرعة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Cost Breakdown
  // ─────────────────────────────────────────────────────────────────────────────

  /// الحصول على تفصيل التكاليف لحقل
  Future<ApiResult<Map<String, double>>> getCostBreakdown({
    required String fieldId,
    String? season,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'field_id': fieldId,
      };
      if (season != null) queryParams['season'] = season;

      final response = await _dio.get(
        '/v1/cost-breakdown',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final breakdown = Map<String, double>.from(data['breakdown'] as Map);

      return ApiResult.success(breakdown);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch cost breakdown',
        'فشل في جلب تفصيل التكاليف',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// إضافة تكلفة
  Future<ApiResult<CostCategory>> addCost({
    required String fieldId,
    required CostType type,
    required String name,
    String? nameAr,
    required double quantity,
    required double unitCost,
    required String unit,
    String? unitAr,
    String? description,
    String? descriptionAr,
    DateTime? date,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/costs',
        data: {
          'field_id': fieldId,
          'type': type.value,
          'name': name,
          'name_ar': nameAr,
          'quantity': quantity,
          'unit_cost': unitCost,
          'unit': unit,
          'unit_ar': unitAr,
          'description': description,
          'description_ar': descriptionAr,
          'date': date?.toIso8601String() ?? DateTime.now().toIso8601String(),
        },
      );

      return ApiResult.success(
        CostCategory.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to add cost',
        'فشل في إضافة التكلفة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تحديث تكلفة
  Future<ApiResult<CostCategory>> updateCost(
    String costId,
    Map<String, dynamic> updates,
  ) async {
    try {
      final response = await _dio.put(
        '/v1/costs/$costId',
        data: updates,
      );

      return ApiResult.success(
        CostCategory.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to update cost',
        'فشل في تحديث التكلفة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// حذف تكلفة
  Future<ApiResult<void>> deleteCost(String costId) async {
    try {
      await _dio.delete('/v1/costs/$costId');
      return ApiResult.success(null);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to delete cost',
        'فشل في حذف التكلفة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Revenue Management
  // ─────────────────────────────────────────────────────────────────────────────

  /// إضافة إيراد
  Future<ApiResult<Revenue>> addRevenue({
    required String fieldId,
    required RevenueType type,
    required String name,
    String? nameAr,
    required double quantity,
    required double unitPrice,
    required String unit,
    String? unitAr,
    String? description,
    String? descriptionAr,
    DateTime? date,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/revenues',
        data: {
          'field_id': fieldId,
          'type': type.value,
          'name': name,
          'name_ar': nameAr,
          'quantity': quantity,
          'unit_price': unitPrice,
          'unit': unit,
          'unit_ar': unitAr,
          'description': description,
          'description_ar': descriptionAr,
          'date': date?.toIso8601String() ?? DateTime.now().toIso8601String(),
        },
      );

      return ApiResult.success(
        Revenue.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to add revenue',
        'فشل في إضافة الإيراد',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تحديث إيراد
  Future<ApiResult<Revenue>> updateRevenue(
    String revenueId,
    Map<String, dynamic> updates,
  ) async {
    try {
      final response = await _dio.put(
        '/v1/revenues/$revenueId',
        data: updates,
      );

      return ApiResult.success(
        Revenue.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to update revenue',
        'فشل في تحديث الإيراد',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// حذف إيراد
  Future<ApiResult<void>> deleteRevenue(String revenueId) async {
    try {
      await _dio.delete('/v1/revenues/$revenueId');
      return ApiResult.success(null);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to delete revenue',
        'فشل في حذف الإيراد',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Break-Even Analysis
  // ─────────────────────────────────────────────────────────────────────────────

  /// حساب نقطة التعادل
  Future<ApiResult<BreakEvenAnalysis>> getBreakEvenPoint({
    required String fieldId,
    String? season,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'field_id': fieldId,
      };
      if (season != null) queryParams['season'] = season;

      final response = await _dio.get(
        '/v1/break-even',
        queryParameters: queryParams,
      );

      return ApiResult.success(
        BreakEvenAnalysis.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to calculate break-even point',
        'فشل في حساب نقطة التعادل',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Crop Comparison
  // ─────────────────────────────────────────────────────────────────────────────

  /// مقارنة المحاصيل
  Future<ApiResult<ProfitabilityComparison>> compareCrops({
    required List<String> cropIds,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/compare-crops',
        data: {
          'crop_ids': cropIds,
        },
      );

      return ApiResult.success(
        ProfitabilityComparison.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to compare crops',
        'فشل في مقارنة المحاصيل',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Historical Trends
  // ─────────────────────────────────────────────────────────────────────────────

  /// الحصول على الاتجاهات التاريخية
  Future<ApiResult<List<CropProfitability>>> getHistoricalTrend({
    required String fieldId,
    int years = 3,
  }) async {
    try {
      final response = await _dio.get(
        '/v1/historical-trend',
        queryParameters: {
          'field_id': fieldId,
          'years': years,
        },
      );

      final data = response.data as Map<String, dynamic>;
      final trend = (data['trend'] as List)
          .map((e) => CropProfitability.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(trend);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch historical trend',
        'فشل في جلب الاتجاهات التاريخية',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// الحصول على متوسطات تاريخية لمحصول
  Future<ApiResult<Map<String, dynamic>>> getCropHistoricalAverages({
    required String cropType,
    int years = 5,
  }) async {
    try {
      final response = await _dio.get(
        '/v1/crop-averages',
        queryParameters: {
          'crop_type': cropType,
          'years': years,
        },
      );

      return ApiResult.success(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch crop averages',
        'فشل في جلب متوسطات المحصول',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Export & Reports
  // ─────────────────────────────────────────────────────────────────────────────

  /// تصدير تقرير PDF
  Future<ApiResult<String>> exportPdfReport({
    required String profitabilityId,
    required String savePath,
  }) async {
    try {
      await _dio.download(
        '/v1/export/pdf/$profitabilityId',
        savePath,
      );

      return ApiResult.success(savePath);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to export PDF',
        'فشل في تصدير PDF',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تصدير تقرير Excel
  Future<ApiResult<String>> exportExcelReport({
    required String profitabilityId,
    required String savePath,
  }) async {
    try {
      await _dio.download(
        '/v1/export/excel/$profitabilityId',
        savePath,
      );

      return ApiResult.success(savePath);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to export Excel',
        'فشل في تصدير Excel',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }
}
