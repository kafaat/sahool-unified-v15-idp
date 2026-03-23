/// Analytics Provider - Dashboard Data Provider
/// موفر التحليلات - موفر بيانات لوحة القيادة
library;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/analytics_repository.dart';

/// Field performance data
/// بيانات أداء الحقل
class FieldPerformance {
  final String fieldId;
  final String fieldName;
  final String fieldNameAr;
  final String cropType;
  final double areaHectares;
  final double ndviScore;
  final double yieldTonsPerHa;
  final double waterUsageM3;
  final String healthStatus;
  final String healthStatusAr;

  const FieldPerformance({
    required this.fieldId,
    required this.fieldName,
    required this.fieldNameAr,
    required this.cropType,
    required this.areaHectares,
    required this.ndviScore,
    required this.yieldTonsPerHa,
    required this.waterUsageM3,
    required this.healthStatus,
    required this.healthStatusAr,
  });
}

/// NDVI trend data point
/// نقطة بيانات اتجاه NDVI
class NdviTrendPoint {
  final DateTime date;
  final double value;
  final String fieldId;

  const NdviTrendPoint({
    required this.date,
    required this.value,
    required this.fieldId,
  });
}

/// Season summary data
/// ملخص الموسم
class SeasonSummary {
  final String season;
  final String seasonAr;
  final double totalYield;
  final double totalWaterUsage;
  final double avgNdvi;
  final int fieldsCount;
  final double revenue;

  const SeasonSummary({
    required this.season,
    required this.seasonAr,
    required this.totalYield,
    required this.totalWaterUsage,
    required this.avgNdvi,
    required this.fieldsCount,
    required this.revenue,
  });
}

/// Analytics dashboard data
/// بيانات لوحة التحليلات
class AnalyticsDashboardData {
  final List<FieldPerformance> fieldPerformances;
  final List<NdviTrendPoint> ndviTrends;
  final List<SeasonSummary> seasonSummaries;
  final double totalAreaHectares;
  final double avgNdvi;
  final double totalYield;
  final double totalWaterUsage;

  const AnalyticsDashboardData({
    required this.fieldPerformances,
    required this.ndviTrends,
    required this.seasonSummaries,
    required this.totalAreaHectares,
    required this.avgNdvi,
    required this.totalYield,
    required this.totalWaterUsage,
  });
}

/// Provider for analytics dashboard data
/// موفر بيانات لوحة التحليلات
/// Fetches from indicators-service (port 8091) at /api/v1/indicators/dashboard
final analyticsDashboardProvider =
    FutureProvider.autoDispose<AnalyticsDashboardData>((ref) async {
  final repo = ref.read(analyticsRepoProvider);
  final result = await repo.getDashboard();
  return result.when(
    success: (data) => data,
    failure: (message, statusCode) => throw Exception(message),
  );
});
