/// Virtual Sensors Models - Smart Irrigation
/// نماذج المستشعرات الافتراضية - الري الذكي
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'virtual_sensor_models.freezed.dart';
part 'virtual_sensor_models.g.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Enums
// ═══════════════════════════════════════════════════════════════════════════════

/// Growth stages for crops
/// مراحل نمو المحاصيل
enum GrowthStage {
  @JsonValue('initial')
  initial,
  @JsonValue('development')
  development,
  @JsonValue('mid_season')
  midSeason,
  @JsonValue('late_season')
  lateSeason,
}

/// Soil types
/// أنواع التربة
enum SoilType {
  @JsonValue('sandy')
  sandy,
  @JsonValue('sandy_loam')
  sandyLoam,
  @JsonValue('loam')
  loam,
  @JsonValue('clay_loam')
  clayLoam,
  @JsonValue('clay')
  clay,
  @JsonValue('silty_clay')
  siltyClay,
}

/// Irrigation methods
/// طرق الري
enum IrrigationMethod {
  @JsonValue('drip')
  drip,
  @JsonValue('sprinkler')
  sprinkler,
  @JsonValue('surface')
  surface,
  @JsonValue('flood')
  flood,
  @JsonValue('furrow')
  furrow,
}

/// Urgency levels
/// مستويات الاستعجال
enum UrgencyLevel {
  @JsonValue('none')
  none,
  @JsonValue('low')
  low,
  @JsonValue('medium')
  medium,
  @JsonValue('high')
  high,
  @JsonValue('critical')
  critical,
}

// ═══════════════════════════════════════════════════════════════════════════════
// Weather Input Model
// نموذج بيانات الطقس
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class WeatherInput with _$WeatherInput {
  const factory WeatherInput({
    required double temperatureMax,
    required double temperatureMin,
    required double humidity,
    required double windSpeed,
    double? solarRadiation,
    double? sunshineHours,
    required double latitude,
    @Default(0) double altitude,
    DateTime? date,
  }) = _WeatherInput;

  factory WeatherInput.fromJson(Map<String, dynamic> json) =>
      _$WeatherInputFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// ET0 Response
// استجابة التبخر-نتح المرجعي
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class ET0Response with _$ET0Response {
  const factory ET0Response({
    required double et0,
    required String et0Ar,
    required String method,
    required Map<String, dynamic> weatherSummary,
    required DateTime calculationDate,
  }) = _ET0Response;

  factory ET0Response.fromJson(Map<String, dynamic> json) =>
      _$ET0ResponseFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Crop ETc Response
// استجابة التبخر-نتح للمحصول
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class CropETcResponse with _$CropETcResponse {
  const factory CropETcResponse({
    required String cropType,
    required String cropNameAr,
    required String growthStage,
    required double kc,
    required double et0,
    required double etc,
    required double dailyWaterNeedLiters,
    required double dailyWaterNeedM3,
    required double weeklyWaterNeedM3,
    required bool criticalPeriod,
    required String notes,
    required String notesAr,
  }) = _CropETcResponse;

  factory CropETcResponse.fromJson(Map<String, dynamic> json) =>
      _$CropETcResponseFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Crop Option (for dropdown)
// خيارات المحاصيل
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class CropKcOption with _$CropKcOption {
  const factory CropKcOption({
    required String cropId,
    required String name,
    required String nameAr,
    required double kcInitial,
    required double kcMid,
    required double kcEnd,
    required double rootDepthMax,
    @Default([]) List<String> criticalPeriods,
  }) = _CropKcOption;

  factory CropKcOption.fromJson(Map<String, dynamic> json) =>
      _$CropKcOptionFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Soil Moisture Response
// استجابة رطوبة التربة
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class VirtualSoilMoistureResponse with _$VirtualSoilMoistureResponse {
  const factory VirtualSoilMoistureResponse({
    required String calculationId,
    required double estimatedMoisture,
    required double moisturePercentage,
    required int daysSinceIrrigation,
    required double totalEtLoss,
    required double availableWater,
    required double totalAvailableWater,
    required String status,
    required String statusAr,
    required UrgencyLevel urgency,
  }) = _VirtualSoilMoistureResponse;

  factory VirtualSoilMoistureResponse.fromJson(Map<String, dynamic> json) =>
      _$VirtualSoilMoistureResponseFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Irrigation Recommendation
// توصية الري
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class IrrigationRecommendation with _$IrrigationRecommendation {
  const factory IrrigationRecommendation({
    required String recommendationId,
    required DateTime timestamp,

    // Field info
    required String cropType,
    required String cropNameAr,
    required String growthStage,
    required double fieldAreaHectares,

    // Calculations
    required double et0,
    required double kc,
    required double etc,

    // Soil status
    required String soilType,
    required String soilTypeAr,
    required double estimatedMoisture,
    required double moistureDepletionPercent,

    // Recommendation
    required bool irrigationNeeded,
    required UrgencyLevel urgency,
    required String urgencyAr,
    required double recommendedAmountMm,
    required double recommendedAmountLiters,
    required double recommendedAmountM3,
    required double grossIrrigationMm,

    // Timing
    required String optimalTime,
    required String optimalTimeAr,
    required int nextIrrigationDays,

    // Advice
    required String advice,
    required String adviceAr,
    @Default([]) List<String> warnings,
    @Default([]) List<String> warningsAr,
  }) = _IrrigationRecommendation;

  factory IrrigationRecommendation.fromJson(Map<String, dynamic> json) =>
      _$IrrigationRecommendationFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Quick Check Response
// استجابة الفحص السريع
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class QuickIrrigationCheck with _$QuickIrrigationCheck {
  const factory QuickIrrigationCheck({
    required String cropType,
    required String cropNameAr,
    required String growthStage,
    required int daysSinceIrrigation,
    required double estimatedEt0,
    required double kc,
    required double estimatedEtc,
    required double estimatedWaterLossMm,
    required double estimatedDepletionPercent,
    required String status,
    required String statusAr,
    required bool needsIrrigation,
    required String recommendation,
    required String recommendationAr,
  }) = _QuickIrrigationCheck;

  factory QuickIrrigationCheck.fromJson(Map<String, dynamic> json) =>
      _$QuickIrrigationCheckFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Soil Type Info
// معلومات نوع التربة
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class SoilTypeInfo with _$SoilTypeInfo {
  const factory SoilTypeInfo({
    required String soilType,
    required String nameAr,
    required double fieldCapacity,
    required double wiltingPoint,
    required double availableWaterCapacity,
    required double infiltrationRateMmHr,
  }) = _SoilTypeInfo;

  factory SoilTypeInfo.fromJson(Map<String, dynamic> json) =>
      _$SoilTypeInfoFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Irrigation Method Info
// معلومات طريقة الري
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class IrrigationMethodInfo with _$IrrigationMethodInfo {
  const factory IrrigationMethodInfo({
    required String method,
    required double efficiency,
    required String efficiencyPercent,
  }) = _IrrigationMethodInfo;

  factory IrrigationMethodInfo.fromJson(Map<String, dynamic> json) =>
      _$IrrigationMethodInfoFromJson(json);
}
