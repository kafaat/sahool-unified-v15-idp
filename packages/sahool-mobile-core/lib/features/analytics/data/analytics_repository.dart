/// SAHOOL Analytics Repository
/// مستودع التحليلات - يتصل بـ indicators-service (port 8091)
///
/// يوفر بيانات لوحة التحليلات مع مؤشرات الحقول والاتجاهات الموسمية
library;

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/config/api_config.dart';
import '../../../core/network/api_result.dart';
import '../presentation/providers/analytics_provider.dart';

// =============================================================================
// Providers
// =============================================================================

/// مزود مستودع التحليلات
final analyticsRepoProvider = Provider<AnalyticsRepository>((ref) {
  return AnalyticsRepository();
});

// =============================================================================
// Repository
// =============================================================================

/// مستودع بيانات التحليلات
/// Analytics data repository connecting to indicators-service (port 8091)
class AnalyticsRepository {
  final Dio _dio;

  AnalyticsRepository({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  /// جلب بيانات لوحة التحليلات من indicators-service
  /// Endpoint: GET /api/v1/indicators/dashboard
  Future<ApiResult<AnalyticsDashboardData>> getDashboard() async {
    try {
      final response = await _dio.get('/api/v1/indicators/dashboard');

      final data = response.data is Map<String, dynamic>
          ? response.data as Map<String, dynamic>
          : <String, dynamic>{};

      return Success(_parseDashboard(data));
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل تحميل بيانات التحليلات'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// تحليل بيانات لوحة القيادة القادمة من الخادم
  AnalyticsDashboardData _parseDashboard(Map<String, dynamic> data) {
    // Parse field performances
    final rawFields =
        data['fieldPerformances'] as List? ??
        data['fields'] as List? ??
        [];
    final fieldPerformances = rawFields
        .map((e) => _parseFieldPerformance(e as Map<String, dynamic>))
        .toList();

    // Parse NDVI trends
    final rawTrends =
        data['ndviTrends'] as List? ??
        data['trends'] as List? ??
        [];
    final ndviTrends = rawTrends
        .map((e) => _parseNdviTrend(e as Map<String, dynamic>))
        .toList();

    // Parse season summaries
    final rawSeasons =
        data['seasonSummaries'] as List? ??
        data['seasons'] as List? ??
        [];
    final seasonSummaries = rawSeasons
        .map((e) => _parseSeasonSummary(e as Map<String, dynamic>))
        .toList();

    return AnalyticsDashboardData(
      totalAreaHectares:
          (data['totalAreaHectares'] ?? data['totalArea'] ?? 0).toDouble(),
      avgNdvi: (data['avgNdvi'] ?? data['averageNdvi'] ?? 0).toDouble(),
      totalYield:
          (data['totalYield'] ?? data['yieldTotal'] ?? 0).toDouble(),
      totalWaterUsage:
          (data['totalWaterUsage'] ?? data['waterUsage'] ?? 0).toDouble(),
      fieldPerformances: fieldPerformances,
      ndviTrends: ndviTrends,
      seasonSummaries: seasonSummaries,
    );
  }

  FieldPerformance _parseFieldPerformance(Map<String, dynamic> e) {
    return FieldPerformance(
      fieldId: (e['fieldId'] ?? e['id'] ?? '').toString(),
      fieldName: (e['fieldName'] ?? e['name'] ?? '').toString(),
      fieldNameAr: (e['fieldNameAr'] ?? e['nameAr'] ?? e['fieldName'] ?? '').toString(),
      cropType: (e['cropType'] ?? e['crop'] ?? '').toString(),
      areaHectares: (e['areaHectares'] ?? e['area'] ?? 0).toDouble(),
      ndviScore: (e['ndviScore'] ?? e['ndvi'] ?? 0).toDouble(),
      yieldTonsPerHa:
          (e['yieldTonsPerHa'] ?? e['yield'] ?? 0).toDouble(),
      waterUsageM3:
          (e['waterUsageM3'] ?? e['waterUsage'] ?? 0).toDouble(),
      healthStatus:
          (e['healthStatus'] ?? e['health'] ?? 'unknown').toString(),
      healthStatusAr:
          (e['healthStatusAr'] ?? e['healthAr'] ?? e['healthStatus'] ?? '').toString(),
    );
  }

  NdviTrendPoint _parseNdviTrend(Map<String, dynamic> e) {
    return NdviTrendPoint(
      date: e['date'] != null
          ? DateTime.tryParse(e['date'].toString()) ?? DateTime.now()
          : DateTime.now(),
      value: (e['value'] ?? e['ndvi'] ?? 0).toDouble(),
      fieldId: (e['fieldId'] ?? e['field_id'] ?? '').toString(),
    );
  }

  SeasonSummary _parseSeasonSummary(Map<String, dynamic> e) {
    return SeasonSummary(
      season: (e['season'] ?? e['name'] ?? '').toString(),
      seasonAr: (e['seasonAr'] ?? e['nameAr'] ?? e['season'] ?? '').toString(),
      totalYield: (e['totalYield'] ?? e['yield'] ?? 0).toDouble(),
      totalWaterUsage:
          (e['totalWaterUsage'] ?? e['waterUsage'] ?? 0).toDouble(),
      avgNdvi: (e['avgNdvi'] ?? e['ndvi'] ?? 0).toDouble(),
      fieldsCount: (e['fieldsCount'] ?? e['fields'] ?? 0) as int,
      revenue: (e['revenue'] ?? 0).toDouble(),
    );
  }

  String _getErrorMessage(DioException e, String defaultMessage) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return 'انتهت مهلة الاتصال. تحقق من اتصالك بالإنترنت.';
    }
    if (e.type == DioExceptionType.connectionError) {
      return 'لا يمكن الاتصال بالخادم. تأكد من اتصالك بالإنترنت.';
    }
    if (e.response?.data != null && e.response?.data is Map) {
      final data = e.response?.data as Map;
      return (data['message'] ?? data['detail'] ?? defaultMessage).toString();
    }
    return defaultMessage;
  }
}
