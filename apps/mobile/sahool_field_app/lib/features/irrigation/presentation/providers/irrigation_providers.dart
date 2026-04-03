library;

/// Irrigation Providers - State Management
/// مزودو الري - إدارة الحالة
///
/// Riverpod providers for irrigation feature state management including:
/// - Smart irrigation calculation providers
/// - Schedule management providers
/// - Weather integration providers
/// - Sensor data providers

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/remote/irrigation_api.dart';
import '../../data/repositories/irrigation_repository.dart';
import '../../domain/services/water_calculator.dart';
import '../../domain/services/irrigation_scheduler.dart';
import '../../domain/services/weather_irrigation_integration.dart';
import '../../../advisor/data/models/irrigation_models.dart'
    hide IrrigationCalculation, IrrigationSchedule, IrrigationEvent;

// ═══════════════════════════════════════════════════════════════════════════
// Core Providers - المزودون الأساسيون
// ═══════════════════════════════════════════════════════════════════════════

/// Weather-Irrigation Integration Provider
final weatherIrrigationProvider = Provider<WeatherIrrigationIntegration>((ref) {
  return const WeatherIrrigationIntegration();
});

// ═══════════════════════════════════════════════════════════════════════════
// Calculation Providers - مزودو الحسابات
// ═══════════════════════════════════════════════════════════════════════════

/// Smart Irrigation Calculation Provider
final smartIrrigationCalculationProvider =
    FutureProvider.family<SmartIrrigationResult, SmartIrrigationParams>(
        (ref, params) async {
  final repo = ref.watch(irrigationRepositoryProvider);
  final weatherIntegration = ref.watch(weatherIrrigationProvider);
  final calculator = repo.calculator;

  // Get crop and method data
  final crop = await repo.getCropById(params.cropId);
  final method = await repo.getMethodById(params.methodId);

  if (crop == null || method == null) {
    throw Exception('Invalid crop or method ID');
  }

  // Calculate ET0 from weather if available
  double et0 = params.et0;
  if (params.weatherData != null) {
    et0 = weatherIntegration.calculateET0FromWeather(
      params.weatherData!,
      latitude: params.latitude ?? 15.0,
    );
  }

  // Calculate irrigation requirement
  final requirement = calculator.calculateIrrigationRequirement(
    et0: et0,
    crop: crop,
    method: method,
    areaHectares: params.areaHectares,
    growthStage: params.growthStage,
    soilMoistureCurrent: params.soilMoistureCurrent,
    soilMoistureFieldCapacity: params.soilMoistureFieldCapacity,
  );

  // Get weather adjustment if forecast available
  IrrigationAdjustment? adjustment;
  if (params.weatherData != null && params.weatherForecast != null) {
    adjustment = weatherIntegration.calculateAdjustment(
      baseWaterNeedMm: requirement.waterNeedMm,
      currentWeather: params.weatherData!,
      forecast: params.weatherForecast,
    );
  }

  // Get water balance
  final waterBalance = calculator.calculateWaterBalance(
    soilMoisture: params.soilMoistureCurrent ?? 35.0,
    fieldCapacity: params.soilMoistureFieldCapacity ?? 45.0,
    wiltingPoint: 15.0,
    madFraction: crop.madFraction,
    rootDepthMm: crop.rootDepthMm.toDouble(),
  );

  // Generate recommendations
  final recommendations = _generateRecommendations(
    requirement: requirement,
    waterBalance: waterBalance,
    adjustment: adjustment,
    crop: crop,
    method: method,
  );

  return SmartIrrigationResult(
    requirement: requirement,
    adjustment: adjustment,
    waterBalance: waterBalance,
    et0: et0,
    crop: crop,
    method: method,
    recommendations: recommendations,
  );
});

/// Generate smart recommendations
List<IrrigationRecommendation> _generateRecommendations({
  required IrrigationRequirement requirement,
  required WaterBalance waterBalance,
  IrrigationAdjustment? adjustment,
  required IrrigationCrop crop,
  required IrrigationMethod method,
}) {
  final recommendations = <IrrigationRecommendation>[];

  // Urgency-based recommendation
  if (waterBalance.status == 'critical') {
    recommendations.add(const IrrigationRecommendation(
      type: RecommendationType.urgency,
      priority: Priority.high,
      title: 'Urgent Irrigation Needed',
      titleAr: 'الري العاجل مطلوب',
      description: 'Soil moisture is critically low. Irrigate immediately.',
      descriptionAr: 'رطوبة التربة منخفضة جدًا. الري فورًا.',
    ));
  } else if (waterBalance.status == 'low') {
    recommendations.add(const IrrigationRecommendation(
      type: RecommendationType.urgency,
      priority: Priority.medium,
      title: 'Irrigation Recommended',
      titleAr: 'الري موصى به',
      description:
          'Soil moisture is below optimal. Schedule irrigation within 24 hours.',
      descriptionAr: 'رطوبة التربة أقل من المثلى. جدول الري خلال 24 ساعة.',
    ));
  }

  // Weather-adjusted recommendation
  if (adjustment != null && adjustment.adjustmentFactor < 0.9) {
    recommendations.add(IrrigationRecommendation(
      type: RecommendationType.weatherAdjustment,
      priority: Priority.medium,
      title: 'Weather-Based Adjustment',
      titleAr: 'تعديل مبني على الطقس',
      description:
          'Reduce irrigation by ${adjustment.savingsPercent.toStringAsFixed(0)}% due to: ${adjustment.reasons.join(", ")}',
      descriptionAr:
          'تقليل الري بنسبة ${adjustment.savingsPercent.toStringAsFixed(0)}% بسبب: ${adjustment.reasonsAr.join("، ")}',
    ));
  }

  // Timing recommendation
  if (requirement.etc > 5) {
    recommendations.add(const IrrigationRecommendation(
      type: RecommendationType.timing,
      priority: Priority.low,
      title: 'Optimal Irrigation Time',
      titleAr: 'الوقت الأمثل للري',
      description:
          'Schedule irrigation in early morning (5-8 AM) to minimize evaporation losses.',
      descriptionAr:
          'جدول الري في الصباح الباكر (5-8 صباحًا) لتقليل خسائر التبخر.',
    ));
  }

  // Efficiency recommendation
  if (method.efficiency < 0.8) {
    recommendations.add(IrrigationRecommendation(
      type: RecommendationType.efficiency,
      priority: Priority.low,
      title: 'Consider Upgrading Irrigation Method',
      titleAr: 'فكر في ترقية طريقة الري',
      description:
          'Current method has ${(method.efficiency * 100).toStringAsFixed(0)}% efficiency. Drip irrigation can save up to 30% water.',
      descriptionAr:
          'الطريقة الحالية كفاءتها ${(method.efficiency * 100).toStringAsFixed(0)}%. الري بالتنقيط يمكن أن يوفر حتى 30% من المياه.',
    ));
  }

  return recommendations;
}

// ═══════════════════════════════════════════════════════════════════════════
// Schedule Providers - مزودو الجداول
// ═══════════════════════════════════════════════════════════════════════════

/// Smart Schedule Generation Provider
final smartScheduleProvider =
    FutureProvider.family<SmartScheduleResult, SmartScheduleParams>(
        (ref, params) async {
  final repo = ref.watch(irrigationRepositoryProvider);
  final weatherIntegration = ref.watch(weatherIrrigationProvider);
  final scheduler = repo.scheduler;

  // Get crop and method data
  final crop = await repo.getCropById(params.cropId);
  final method = await repo.getMethodById(params.methodId);

  if (crop == null || method == null) {
    throw Exception('Invalid crop or method ID');
  }

  // Convert weather forecast to scheduler format
  WeatherForecast? forecast;
  if (params.weatherForecast != null && params.weatherForecast!.isNotEmpty) {
    forecast = weatherIntegration.toSchedulerForecast(params.weatherForecast!);
  }

  // Generate smart schedule
  return scheduler.createSmartSchedule(
    fieldId: params.fieldId,
    crop: crop,
    method: method,
    areaHectares: params.areaHectares,
    days: params.days,
    et0: params.et0,
    growthStage: params.growthStage,
    soilMoistureCurrent: params.soilMoistureCurrent,
    soilMoistureFieldCapacity: params.soilMoistureFieldCapacity,
    weatherForecast: forecast,
  );
});

/// Upcoming Events Provider
final upcomingIrrigationEventsProvider =
    FutureProvider.family<List<IrrigationEvent>, String>((ref, fieldId) async {
  final repo = ref.watch(irrigationRepositoryProvider);
  return repo.scheduler.getUpcomingEvents(fieldId, days: 14);
});

/// Next Irrigation Event Provider
final nextIrrigationEventProvider =
    FutureProvider.family<IrrigationEvent?, String>((ref, fieldId) async {
  final repo = ref.watch(irrigationRepositoryProvider);
  return repo.scheduler.getNextEvent(fieldId);
});

// ═══════════════════════════════════════════════════════════════════════════
// Weather Alert Providers - مزودو تنبيهات الطقس
// ═══════════════════════════════════════════════════════════════════════════

/// Irrigation Weather Alerts Provider
final irrigationWeatherAlertsProvider =
    FutureProvider.family<List<IrrigationWeatherAlert>, WeatherAlertParams>(
        (ref, params) async {
  final weatherIntegration = ref.watch(weatherIrrigationProvider);

  return weatherIntegration.getIrrigationAlerts(
    params.currentWeather,
    params.forecast,
  );
});

/// Should Skip Irrigation Provider
final shouldSkipIrrigationProvider =
    Provider.family<SkipDecision, WeatherAlertParams>((ref, params) {
  final weatherIntegration = ref.watch(weatherIrrigationProvider);

  return weatherIntegration.shouldSkipIrrigation(
    currentWeather: params.currentWeather,
    forecast: params.forecast,
  );
});

/// Optimal Irrigation Window Provider
final optimalIrrigationWindowProvider =
    Provider.family<IrrigationWindow, IrrigationWeatherData>((ref, weather) {
  final weatherIntegration = ref.watch(weatherIrrigationProvider);
  return weatherIntegration.getOptimalIrrigationWindow(weather);
});

// ═══════════════════════════════════════════════════════════════════════════
// Sensor Trigger Providers - مزودو محفز المستشعر
// ═══════════════════════════════════════════════════════════════════════════

/// Soil Moisture Trigger Check Provider
final soilMoistureTriggerProvider =
    Provider.family<SensorTriggerResult, SoilMoistureParams>((ref, params) {
  final repo = ref.watch(irrigationRepositoryProvider);
  final scheduler = repo.scheduler;

  return scheduler.checkSoilMoistureTrigger(
    currentMoisture: params.currentMoisture,
    fieldCapacity: params.fieldCapacity,
    wiltingPoint: params.wiltingPoint,
    madFraction: params.madFraction,
    triggerBuffer: params.triggerBuffer,
  );
});

// ═══════════════════════════════════════════════════════════════════════════
// Sync Providers - مزودو المزامنة
// ═══════════════════════════════════════════════════════════════════════════

/// Last Sync Time Provider
final lastIrrigationSyncProvider = FutureProvider<DateTime?>((ref) async {
  final repo = ref.watch(irrigationRepositoryProvider);
  return repo.getLastSyncTime();
});

/// Sync Pending Changes Provider
final syncIrrigationChangesProvider = FutureProvider<SyncResult>((ref) async {
  final repo = ref.watch(irrigationRepositoryProvider);
  return repo.syncPendingChanges();
});

// ═══════════════════════════════════════════════════════════════════════════
// Parameter Classes - فئات المعلمات
// ═══════════════════════════════════════════════════════════════════════════

/// Parameters for smart irrigation calculation
class SmartIrrigationParams {
  final String cropId;
  final String methodId;
  final double areaHectares;
  final double et0;
  final String? growthStage;
  final double? soilMoistureCurrent;
  final double? soilMoistureFieldCapacity;
  final double? latitude;
  final IrrigationWeatherData? weatherData;
  final List<IrrigationWeatherData>? weatherForecast;

  const SmartIrrigationParams({
    required this.cropId,
    required this.methodId,
    required this.areaHectares,
    required this.et0,
    this.growthStage,
    this.soilMoistureCurrent,
    this.soilMoistureFieldCapacity,
    this.latitude,
    this.weatherData,
    this.weatherForecast,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SmartIrrigationParams &&
          runtimeType == other.runtimeType &&
          cropId == other.cropId &&
          methodId == other.methodId &&
          areaHectares == other.areaHectares &&
          et0 == other.et0 &&
          growthStage == other.growthStage;

  @override
  int get hashCode =>
      cropId.hashCode ^
      methodId.hashCode ^
      areaHectares.hashCode ^
      et0.hashCode ^
      growthStage.hashCode;
}

/// Parameters for smart schedule generation
class SmartScheduleParams {
  final String fieldId;
  final String cropId;
  final String methodId;
  final double areaHectares;
  final int days;
  final double et0;
  final String? growthStage;
  final double? soilMoistureCurrent;
  final double? soilMoistureFieldCapacity;
  final List<IrrigationWeatherData>? weatherForecast;

  const SmartScheduleParams({
    required this.fieldId,
    required this.cropId,
    required this.methodId,
    required this.areaHectares,
    required this.days,
    required this.et0,
    this.growthStage,
    this.soilMoistureCurrent,
    this.soilMoistureFieldCapacity,
    this.weatherForecast,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SmartScheduleParams &&
          runtimeType == other.runtimeType &&
          fieldId == other.fieldId &&
          cropId == other.cropId &&
          methodId == other.methodId;

  @override
  int get hashCode => fieldId.hashCode ^ cropId.hashCode ^ methodId.hashCode;
}

/// Parameters for weather alerts
class WeatherAlertParams {
  final IrrigationWeatherData currentWeather;
  final List<IrrigationWeatherData> forecast;

  const WeatherAlertParams({
    required this.currentWeather,
    required this.forecast,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is WeatherAlertParams &&
          runtimeType == other.runtimeType &&
          currentWeather.date == other.currentWeather.date;

  @override
  int get hashCode => currentWeather.date.hashCode;
}

/// Parameters for soil moisture trigger
class SoilMoistureParams {
  final double currentMoisture;
  final double fieldCapacity;
  final double wiltingPoint;
  final double madFraction;
  final double triggerBuffer;

  const SoilMoistureParams({
    required this.currentMoisture,
    required this.fieldCapacity,
    this.wiltingPoint = 15.0,
    this.madFraction = 0.55,
    this.triggerBuffer = 5.0,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SoilMoistureParams &&
          runtimeType == other.runtimeType &&
          currentMoisture == other.currentMoisture &&
          fieldCapacity == other.fieldCapacity;

  @override
  int get hashCode => currentMoisture.hashCode ^ fieldCapacity.hashCode;
}

// ═══════════════════════════════════════════════════════════════════════════
// Result Classes - فئات النتائج
// ═══════════════════════════════════════════════════════════════════════════

/// Smart irrigation calculation result
class SmartIrrigationResult {
  final IrrigationRequirement requirement;
  final IrrigationAdjustment? adjustment;
  final WaterBalance waterBalance;
  final double et0;
  final IrrigationCrop crop;
  final IrrigationMethod method;
  final List<IrrigationRecommendation> recommendations;

  const SmartIrrigationResult({
    required this.requirement,
    this.adjustment,
    required this.waterBalance,
    required this.et0,
    required this.crop,
    required this.method,
    required this.recommendations,
  });

  /// Get final water need (adjusted if available)
  double get finalWaterNeedMm =>
      adjustment?.adjustedAmount ?? requirement.waterNeedMm;

  /// Get final water need in liters
  double get finalWaterNeedLiters => adjustment != null
      ? (adjustment!.adjustedAmount / requirement.waterNeedMm) *
          requirement.waterNeedLiters
      : requirement.waterNeedLiters;
}

/// Irrigation recommendation
class IrrigationRecommendation {
  final RecommendationType type;
  final Priority priority;
  final String title;
  final String titleAr;
  final String description;
  final String descriptionAr;

  const IrrigationRecommendation({
    required this.type,
    required this.priority,
    required this.title,
    required this.titleAr,
    required this.description,
    required this.descriptionAr,
  });
}

/// Recommendation types
enum RecommendationType {
  urgency,
  weatherAdjustment,
  timing,
  efficiency,
  waterSaving,
}

/// Priority levels
enum Priority {
  low,
  medium,
  high,
}
