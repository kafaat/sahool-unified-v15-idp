/// Irrigation Planning Models
/// نماذج تخطيط الري
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'irrigation_models.freezed.dart';
part 'irrigation_models.g.dart';

/// Irrigation calculation request
/// طلب حساب الري
@freezed
class IrrigationRequest with _$IrrigationRequest {
  const factory IrrigationRequest({
    required String cropType,
    required String growthStage,
    required double fieldArea, // hectares
    required String soilType,
    required String irrigationMethod, // drip, sprinkler, flood, pivot
    @Default(0) double currentSoilMoisture, // %
    @Default(0) double temperature, // °C
    @Default(0) double humidity, // %
    @Default('') String governorate,
  }) = _IrrigationRequest;

  factory IrrigationRequest.fromJson(Map<String, dynamic> json) =>
      _$IrrigationRequestFromJson(json);
}

/// Irrigation calculation result
/// نتيجة حساب الري
@freezed
class IrrigationCalculation with _$IrrigationCalculation {
  const factory IrrigationCalculation({
    required double waterRequirementMm, // mm/day
    required double waterRequirementLiters, // liters/hectare/day
    required double totalWaterLiters, // total for field
    required double etCrop, // crop evapotranspiration
    required double irrigationEfficiency, // %
    required String recommendedFrequency,
    required String recommendedFrequencyAr,
    required int durationMinutes,
    @Default('') String notes,
    @Default('') String notesAr,
  }) = _IrrigationCalculation;

  factory IrrigationCalculation.fromJson(Map<String, dynamic> json) =>
      _$IrrigationCalculationFromJson(json);
}

/// Irrigation schedule
/// جدول الري
@freezed
class IrrigationSchedule with _$IrrigationSchedule {
  const factory IrrigationSchedule({
    required String scheduleId,
    required String fieldId,
    required List<IrrigationEvent> events,
    required DateTime startDate,
    required DateTime endDate,
    required double totalWaterPlanned, // liters
    @Default('') String notes,
    @Default('') String notesAr,
  }) = _IrrigationSchedule;

  factory IrrigationSchedule.fromJson(Map<String, dynamic> json) =>
      _$IrrigationScheduleFromJson(json);
}

/// Single irrigation event
/// حدث ري واحد
@freezed
class IrrigationEvent with _$IrrigationEvent {
  const factory IrrigationEvent({
    required String eventId,
    required DateTime scheduledTime,
    required int durationMinutes,
    required double waterLiters,
    required String status, // pending, in_progress, completed, skipped
    required String statusAr,
    @Default('') String notes,
  }) = _IrrigationEvent;

  factory IrrigationEvent.fromJson(Map<String, dynamic> json) =>
      _$IrrigationEventFromJson(json);
}

/// Water balance calculation
/// حساب التوازن المائي
@freezed
class WaterBalance with _$WaterBalance {
  const factory WaterBalance({
    required double soilMoisturePercent,
    required double fieldCapacity,
    required double wiltingPoint,
    required double availableWater,
    required double depletionPercent,
    required String status, // optimal, low, critical, excess
    required String statusAr,
    required bool irrigationNeeded,
    @Default(0) double recommendedWaterMm,
  }) = _WaterBalance;

  factory WaterBalance.fromJson(Map<String, dynamic> json) =>
      _$WaterBalanceFromJson(json);
}

/// Sensor reading from field
/// قراءة المستشعر من الحقل
@freezed
class SensorReading with _$SensorReading {
  const factory SensorReading({
    required String sensorId,
    required String sensorType, // soil_moisture, temperature, humidity
    required double value,
    required String unit,
    required DateTime timestamp,
    required String fieldId,
    @Default('') String location, // sensor location in field
  }) = _SensorReading;

  factory SensorReading.fromJson(Map<String, dynamic> json) =>
      _$SensorReadingFromJson(json);
}

/// Irrigation efficiency report
/// تقرير كفاءة الري
@freezed
class IrrigationEfficiencyReport with _$IrrigationEfficiencyReport {
  const factory IrrigationEfficiencyReport({
    required String reportId,
    required String fieldId,
    required String period, // weekly, monthly, seasonal
    required double waterUsedLiters,
    required double waterSavedLiters,
    required double efficiencyPercent,
    required double costSaved, // currency
    required Map<String, double> dailyUsage, // date -> liters
    required List<String> recommendations,
    required List<String> recommendationsAr,
    required DateTime generatedAt,
  }) = _IrrigationEfficiencyReport;

  factory IrrigationEfficiencyReport.fromJson(Map<String, dynamic> json) =>
      _$IrrigationEfficiencyReportFromJson(json);
}

/// Irrigation method option
/// خيار طريقة الري
@freezed
class IrrigationMethodOption with _$IrrigationMethodOption {
  const factory IrrigationMethodOption({
    required String id,
    required String name,
    required String nameAr,
    required double efficiency, // typical efficiency %
    required String description,
    required String descriptionAr,
    @Default([]) List<String> suitableCrops,
    @Default([]) List<String> suitableCropsAr,
  }) = _IrrigationMethodOption;

  factory IrrigationMethodOption.fromJson(Map<String, dynamic> json) =>
      _$IrrigationMethodOptionFromJson(json);
}

/// Crop water requirements
/// متطلبات المحصول المائية
@freezed
class CropWaterRequirement with _$CropWaterRequirement {
  const factory CropWaterRequirement({
    required String cropId,
    required String cropName,
    required String cropNameAr,
    required Map<String, double> stageRequirements, // growth_stage -> mm/day
    required double kcInitial,
    required double kcMid,
    required double kcEnd,
    required int rootDepthCm,
    required double criticalDepletionFraction,
  }) = _CropWaterRequirement;

  factory CropWaterRequirement.fromJson(Map<String, dynamic> json) =>
      _$CropWaterRequirementFromJson(json);
}
