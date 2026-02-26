/// Analytics Provider - Dashboard Data Provider
/// موفر التحليلات - موفر بيانات لوحة القيادة
import 'package:flutter_riverpod/flutter_riverpod.dart';

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
final analyticsDashboardProvider =
    FutureProvider.autoDispose<AnalyticsDashboardData>((ref) async {
  // In production, fetch from API
  await Future.delayed(const Duration(milliseconds: 500));

  return AnalyticsDashboardData(
    totalAreaHectares: 450,
    avgNdvi: 0.72,
    totalYield: 2450,
    totalWaterUsage: 18500,
    fieldPerformances: [
      const FieldPerformance(
        fieldId: 'f001', fieldName: 'North Wheat', fieldNameAr: 'القمح الشمالي',
        cropType: 'wheat', areaHectares: 45, ndviScore: 0.85,
        yieldTonsPerHa: 4.2, waterUsageM3: 3500,
        healthStatus: 'Healthy', healthStatusAr: 'صحي',
      ),
      const FieldPerformance(
        fieldId: 'f002', fieldName: 'West Corn', fieldNameAr: 'الذرة الغربي',
        cropType: 'corn', areaHectares: 60, ndviScore: 0.72,
        yieldTonsPerHa: 8.5, waterUsageM3: 5200,
        healthStatus: 'Moderate', healthStatusAr: 'معتدل',
      ),
      const FieldPerformance(
        fieldId: 'f003', fieldName: 'Barley South', fieldNameAr: 'الشعير الجنوبي',
        cropType: 'barley', areaHectares: 35, ndviScore: 0.45,
        yieldTonsPerHa: 3.1, waterUsageM3: 2100,
        healthStatus: 'Stressed', healthStatusAr: 'مجهد',
      ),
      const FieldPerformance(
        fieldId: 'f004', fieldName: 'Alfalfa Field', fieldNameAr: 'حقل البرسيم',
        cropType: 'alfalfa', areaHectares: 50, ndviScore: 0.90,
        yieldTonsPerHa: 12.0, waterUsageM3: 4800,
        healthStatus: 'Healthy', healthStatusAr: 'صحي',
      ),
    ],
    ndviTrends: List.generate(12, (i) => NdviTrendPoint(
      date: DateTime(2026, 1, 1).add(Duration(days: i * 14)),
      value: 0.55 + (i * 0.03) + (i % 3 == 0 ? -0.02 : 0.01),
      fieldId: 'f001',
    )),
    seasonSummaries: const [
      SeasonSummary(
        season: 'Winter 2025', seasonAr: 'شتاء 2025',
        totalYield: 2200, totalWaterUsage: 16000, avgNdvi: 0.68,
        fieldsCount: 10, revenue: 4070000,
      ),
      SeasonSummary(
        season: 'Summer 2025', seasonAr: 'صيف 2025',
        totalYield: 1800, totalWaterUsage: 22000, avgNdvi: 0.62,
        fieldsCount: 8, revenue: 3330000,
      ),
      SeasonSummary(
        season: 'Winter 2026', seasonAr: 'شتاء 2026',
        totalYield: 2450, totalWaterUsage: 18500, avgNdvi: 0.72,
        fieldsCount: 12, revenue: 4532500,
      ),
    ],
  );
});
