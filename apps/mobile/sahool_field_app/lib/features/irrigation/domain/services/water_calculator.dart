/// Water Calculator Service - Smart Irrigation Calculations
/// خدمة حاسبة المياه - حسابات الري الذكي
///
/// Provides comprehensive water requirement calculations including:
/// - ETc (Crop Evapotranspiration) calculations
/// - Water need conversions (mm, liters, m3)
/// - Irrigation duration calculations
/// - Pivot water volume calculations
/// - Sector area calculations
/// - Efficiency calculations
/// - Water balance calculations
library;

import 'dart:math' as math;

import '../../data/remote/irrigation_api.dart';
import '../../../advisor/data/models/irrigation_models.dart';

/// Water Calculator Service
/// خدمة حاسبة المياه
class WaterCalculator {
  const WaterCalculator();

  // ═══════════════════════════════════════════════════════════════════════════
  // ETc Calculations - حسابات البخر-نتح
  // ═══════════════════════════════════════════════════════════════════════════

  /// Calculate crop evapotranspiration (ETc) from reference ET (ET0) and crop coefficient (Kc)
  /// حساب البخر-نتح للمحصول من البخر-نتح المرجعي ومعامل المحصول
  ///
  /// Formula: ETc = ET0 * Kc
  ///
  /// [et0] - Reference evapotranspiration in mm/day
  /// [kc] - Crop coefficient (varies by crop and growth stage)
  ///
  /// Returns ETc in mm/day
  double calculateETc(double et0, double kc) {
    if (et0 < 0) return 0;
    if (kc < 0) return 0;
    return et0 * kc;
  }

  /// Get Kc value for a specific growth stage from crop data
  /// الحصول على قيمة Kc لمرحلة نمو محددة من بيانات المحصول
  double getKcForStage(IrrigationCrop crop, String? growthStage) {
    if (growthStage == null || crop.kcStages == null) {
      return crop.kc;
    }
    return crop.kcStages![growthStage] ?? crop.kc;
  }

  /// Calculate ETc with growth stage adjustment
  /// حساب البخر-نتح مع تعديل مرحلة النمو
  double calculateETcWithStage(
    double et0,
    IrrigationCrop crop,
    String? growthStage,
  ) {
    final kc = getKcForStage(crop, growthStage);
    return calculateETc(et0, kc);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Water Need Calculations - حسابات احتياجات المياه
  // ═══════════════════════════════════════════════════════════════════════════

  /// Calculate gross water need considering irrigation efficiency
  /// حساب احتياجات المياه الإجمالية مع مراعاة كفاءة الري
  ///
  /// Formula: Gross Water Need = ETc / Efficiency
  ///
  /// [etc] - Crop evapotranspiration in mm/day
  /// [efficiency] - Irrigation efficiency (0.0 - 1.0)
  /// [soilMoistureDeficit] - Optional soil moisture deficit to replenish (mm)
  ///
  /// Returns gross water need in mm
  double calculateWaterNeedMm(
    double etc,
    double efficiency, {
    double? soilMoistureDeficit,
  }) {
    if (etc < 0) return 0;
    if (efficiency <= 0 || efficiency > 1.0) efficiency = 0.85;

    double waterNeed = etc / efficiency;

    // Add soil moisture deficit if provided
    if (soilMoistureDeficit != null && soilMoistureDeficit > 0) {
      waterNeed += soilMoistureDeficit / efficiency;
    }

    return waterNeed;
  }

  /// Calculate complete irrigation requirement
  /// حساب متطلبات الري الكاملة
  IrrigationRequirement calculateIrrigationRequirement({
    required double et0,
    required IrrigationCrop crop,
    required IrrigationMethod method,
    required double areaHectares,
    String? growthStage,
    double? soilMoistureCurrent,
    double? soilMoistureFieldCapacity,
  }) {
    final kc = getKcForStage(crop, growthStage);
    final etc = calculateETc(et0, kc);

    // Calculate soil moisture deficit if data available
    double? soilMoistureDeficit;
    if (soilMoistureCurrent != null && soilMoistureFieldCapacity != null) {
      soilMoistureDeficit = soilMoistureFieldCapacity - soilMoistureCurrent;
      if (soilMoistureDeficit < 0) soilMoistureDeficit = 0;
    }

    final waterNeedMm = calculateWaterNeedMm(
      etc,
      method.efficiency,
      soilMoistureDeficit: soilMoistureDeficit,
    );

    final waterNeedLiters = convertMmToLiters(waterNeedMm, areaHectares);
    final waterNeedM3 = convertLitersToM3(waterNeedLiters);

    // Calculate next irrigation date based on MAD (Management Allowable Depletion)
    DateTime nextIrrigationDate = DateTime.now();
    if (soilMoistureCurrent != null && soilMoistureFieldCapacity != null) {
      final daysUntil = calculateDaysUntilIrrigation(
        soilMoistureCurrent: soilMoistureCurrent,
        fieldCapacity: soilMoistureFieldCapacity,
        wiltingPoint: 15.0, // Default wilting point
        dailyETc: etc,
        madFraction: crop.madFraction,
      );
      nextIrrigationDate =
          DateTime.now().add(Duration(days: daysUntil.toInt()));
    }

    return IrrigationRequirement(
      etc: etc,
      kc: kc,
      waterNeedMm: waterNeedMm,
      waterNeedLiters: waterNeedLiters,
      waterNeedM3: waterNeedM3,
      efficiency: method.efficiency,
      nextIrrigationDate: nextIrrigationDate,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Unit Conversions - تحويل الوحدات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Convert water depth (mm) to volume (liters) for a given area
  /// تحويل عمق المياه (ملم) إلى حجم (لتر) لمساحة معينة
  ///
  /// Formula: 1 mm on 1 hectare = 10,000 liters
  ///
  /// [depthMm] - Water depth in millimeters
  /// [areaHectares] - Field area in hectares
  ///
  /// Returns water volume in liters
  double convertMmToLiters(double depthMm, double areaHectares) {
    if (depthMm < 0 || areaHectares < 0) return 0;
    return depthMm * areaHectares * 10000;
  }

  /// Convert liters to cubic meters
  /// تحويل اللترات إلى متر مكعب
  double convertLitersToM3(double liters) {
    if (liters < 0) return 0;
    return liters / 1000;
  }

  /// Convert cubic meters to liters
  /// تحويل المتر المكعب إلى لترات
  double convertM3ToLiters(double m3) {
    if (m3 < 0) return 0;
    return m3 * 1000;
  }

  /// Convert liters to mm for a given area
  /// تحويل اللترات إلى ملم لمساحة معينة
  double convertLitersToMm(double liters, double areaHectares) {
    if (liters < 0 || areaHectares <= 0) return 0;
    return liters / (areaHectares * 10000);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Irrigation Duration - مدة الري
  // ═══════════════════════════════════════════════════════════════════════════

  /// Calculate irrigation duration from volume and flow rate
  /// حساب مدة الري من الحجم ومعدل التدفق
  ///
  /// [waterLiters] - Volume of water to apply in liters
  /// [flowRateLph] - Flow rate in liters per hour
  ///
  /// Returns duration in minutes
  double calculateIrrigationDuration(double waterLiters, double flowRateLph) {
    if (waterLiters <= 0 || flowRateLph <= 0) return 0;
    final hours = waterLiters / flowRateLph;
    return hours * 60; // Convert to minutes
  }

  /// Calculate flow rate needed for a specific duration
  /// حساب معدل التدفق المطلوب لمدة محددة
  double calculateRequiredFlowRate(double waterLiters, double durationMinutes) {
    if (waterLiters <= 0 || durationMinutes <= 0) return 0;
    final hours = durationMinutes / 60;
    return waterLiters / hours;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Pivot Water Volume - حجم مياه المحوري
  // ═══════════════════════════════════════════════════════════════════════════

  /// Calculate water volume for pivot irrigation
  /// حساب حجم المياه للري المحوري
  ///
  /// [radiusMeters] - Pivot radius in meters
  /// [depthMm] - Irrigation depth in millimeters
  /// [startAngle] - Start angle in degrees (default 0)
  /// [endAngle] - End angle in degrees (default 360 for full circle)
  ///
  /// Returns water volume in liters
  double calculatePivotWaterVolume({
    required double radiusMeters,
    required double depthMm,
    double startAngle = 0,
    double endAngle = 360,
  }) {
    if (radiusMeters <= 0 || depthMm <= 0) return 0;

    // Calculate angle fraction
    final angleFraction = ((endAngle - startAngle).abs() % 360) / 360;
    final effectiveFraction = angleFraction == 0 ? 1.0 : angleFraction;

    // Calculate area in square meters
    final areaM2 = math.pi * radiusMeters * radiusMeters * effectiveFraction;

    // Convert depth to meters and calculate volume
    final depthM = depthMm / 1000;
    final volumeM3 = areaM2 * depthM;

    // Convert to liters
    return volumeM3 * 1000;
  }

  /// Calculate pivot area in hectares
  /// حساب مساحة المحوري بالهكتار
  double calculatePivotArea({
    required double radiusMeters,
    double startAngle = 0,
    double endAngle = 360,
  }) {
    if (radiusMeters <= 0) return 0;

    final angleFraction = ((endAngle - startAngle).abs() % 360) / 360;
    final effectiveFraction = angleFraction == 0 ? 1.0 : angleFraction;

    final areaM2 = math.pi * radiusMeters * radiusMeters * effectiveFraction;
    return areaM2 / 10000; // Convert to hectares
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Sector Area Calculations - حسابات مساحة القطاع
  // ═══════════════════════════════════════════════════════════════════════════

  /// Calculate sector area
  /// حساب مساحة القطاع
  ///
  /// [radiusMeters] - Pivot radius in meters
  /// [startAngle] - Sector start angle in degrees
  /// [endAngle] - Sector end angle in degrees
  ///
  /// Returns area in hectares
  double calculateSectorArea(
    double radiusMeters,
    double startAngle,
    double endAngle,
  ) {
    if (radiusMeters <= 0) return 0;

    final angleFraction = (endAngle - startAngle).abs() / 360;
    final areaM2 = math.pi * radiusMeters * radiusMeters * angleFraction;
    return areaM2 / 10000; // Convert to hectares
  }

  /// Calculate annular sector area (ring sector)
  /// حساب مساحة القطاع الحلقي
  double calculateAnnularSectorArea(
    double innerRadius,
    double outerRadius,
    double startAngle,
    double endAngle,
  ) {
    if (outerRadius <= innerRadius || innerRadius < 0) return 0;

    final angleFraction = (endAngle - startAngle).abs() / 360;
    final outerArea = math.pi * outerRadius * outerRadius * angleFraction;
    final innerArea = math.pi * innerRadius * innerRadius * angleFraction;
    return (outerArea - innerArea) / 10000; // Convert to hectares
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Efficiency Calculations - حسابات الكفاءة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Calculate irrigation efficiency
  /// حساب كفاءة الري
  ///
  /// [appliedMm] - Water applied in mm
  /// [consumedMm] - Water actually consumed by crop in mm
  ///
  /// Returns efficiency as percentage (0-100)
  double calculateEfficiency(double appliedMm, double consumedMm) {
    if (appliedMm <= 0) return 0;
    if (consumedMm < 0) return 0;
    if (consumedMm > appliedMm) return 100;
    return (consumedMm / appliedMm) * 100;
  }

  /// Get efficiency rating from percentage
  /// الحصول على تصنيف الكفاءة من النسبة المئوية
  EfficiencyRating getEfficiencyRating(double efficiencyPercent) {
    if (efficiencyPercent >= 85) return EfficiencyRating.excellent;
    if (efficiencyPercent >= 70) return EfficiencyRating.good;
    if (efficiencyPercent >= 55) return EfficiencyRating.fair;
    return EfficiencyRating.poor;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Water Balance Calculations - حسابات التوازن المائي
  // ═══════════════════════════════════════════════════════════════════════════

  /// Calculate water balance status
  /// حساب حالة التوازن المائي
  WaterBalance calculateWaterBalance({
    required double soilMoisture,
    required double fieldCapacity,
    required double wiltingPoint,
    required double madFraction,
    required double rootDepthMm,
  }) {
    // Calculate available water
    final availableWater = soilMoisture - wiltingPoint;
    final totalAvailable = fieldCapacity - wiltingPoint;

    // Calculate depletion percentage
    final depletionPercent = totalAvailable > 0
        ? ((totalAvailable - availableWater) / totalAvailable) * 100
        : 0.0;

    // Determine status
    String status;
    String statusAr;
    bool irrigationNeeded;
    double recommendedWaterMm = 0;

    final madThreshold = totalAvailable * madFraction;
    final deficit = totalAvailable - availableWater;

    if (deficit > madThreshold) {
      // Beyond MAD - irrigation urgently needed
      status = 'critical';
      statusAr = 'حرج';
      irrigationNeeded = true;
      recommendedWaterMm = deficit;
    } else if (deficit > madThreshold * 0.7) {
      // Approaching MAD - irrigation recommended
      status = 'low';
      statusAr = 'منخفض';
      irrigationNeeded = true;
      recommendedWaterMm = deficit;
    } else if (soilMoisture > fieldCapacity) {
      // Excess water
      status = 'excess';
      statusAr = 'فائض';
      irrigationNeeded = false;
    } else {
      // Optimal
      status = 'optimal';
      statusAr = 'مثالي';
      irrigationNeeded = false;
    }

    return WaterBalance(
      soilMoisturePercent: soilMoisture,
      fieldCapacity: fieldCapacity,
      wiltingPoint: wiltingPoint,
      availableWater: availableWater > 0 ? availableWater : 0,
      depletionPercent: depletionPercent.clamp(0, 100),
      status: status,
      statusAr: statusAr,
      irrigationNeeded: irrigationNeeded,
      recommendedWaterMm: recommendedWaterMm > 0 ? recommendedWaterMm : 0,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Irrigation Date Calculations - حسابات تاريخ الري
  // ═══════════════════════════════════════════════════════════════════════════

  /// Calculate days until irrigation is needed
  /// حساب الأيام حتى يتطلب الري
  double calculateDaysUntilIrrigation({
    required double soilMoistureCurrent,
    required double fieldCapacity,
    required double wiltingPoint,
    required double dailyETc,
    required double madFraction,
  }) {
    if (dailyETc <= 0) return 30; // Default to 30 days if no ET data

    final totalAvailable = fieldCapacity - wiltingPoint;
    final currentAvailable = soilMoistureCurrent - wiltingPoint;
    final madThreshold = totalAvailable * (1 - madFraction);

    final waterAboveThreshold = currentAvailable - madThreshold;
    if (waterAboveThreshold <= 0) return 0; // Irrigation needed now

    return waterAboveThreshold / dailyETc;
  }

  /// Calculate next irrigation date
  /// حساب تاريخ الري التالي
  DateTime calculateNextIrrigationDate({
    required double currentSoilMoisture,
    required double fieldCapacity,
    required double dailyETc,
    required double madFraction,
    double wiltingPoint = 15.0,
  }) {
    final days = calculateDaysUntilIrrigation(
      soilMoistureCurrent: currentSoilMoisture,
      fieldCapacity: fieldCapacity,
      wiltingPoint: wiltingPoint,
      dailyETc: dailyETc,
      madFraction: madFraction,
    );

    return DateTime.now().add(Duration(days: days.ceil()));
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Weather-Based Adjustments - التعديلات المبنية على الطقس
  // ═══════════════════════════════════════════════════════════════════════════

  /// Adjust irrigation based on weather forecast
  /// تعديل الري بناءً على توقعات الطقس
  double adjustForWeather({
    required double baseWaterNeedMm,
    double? rainForecastMm,
    double? temperatureC,
    double? windSpeedKmh,
    double? humidityPercent,
  }) {
    double adjusted = baseWaterNeedMm;

    // Reduce for expected rain
    if (rainForecastMm != null && rainForecastMm > 0) {
      adjusted -= rainForecastMm * 0.8; // Assume 80% effective rainfall
    }

    // Increase for high temperature
    if (temperatureC != null && temperatureC > 35) {
      adjusted *= 1.1; // 10% increase for hot conditions
    }

    // Increase for wind
    if (windSpeedKmh != null && windSpeedKmh > 15) {
      adjusted *= 1.05; // 5% increase for windy conditions
    }

    // Decrease for high humidity
    if (humidityPercent != null && humidityPercent > 80) {
      adjusted *= 0.95; // 5% decrease for humid conditions
    }

    return adjusted > 0 ? adjusted : 0;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Supporting Models - نماذج مساعدة
// ═══════════════════════════════════════════════════════════════════════════

/// Irrigation requirement calculation result
/// نتيجة حساب متطلبات الري
class IrrigationRequirement {
  final double etc;
  final double kc;
  final double waterNeedMm;
  final double waterNeedLiters;
  final double waterNeedM3;
  final double efficiency;
  final DateTime nextIrrigationDate;

  const IrrigationRequirement({
    required this.etc,
    required this.kc,
    required this.waterNeedMm,
    required this.waterNeedLiters,
    required this.waterNeedM3,
    required this.efficiency,
    required this.nextIrrigationDate,
  });
}

/// Efficiency rating levels
/// مستويات تصنيف الكفاءة
enum EfficiencyRating {
  excellent, // > 85%
  good, // 70-85%
  fair, // 55-70%
  poor, // < 55%
}

extension EfficiencyRatingX on EfficiencyRating {
  String get displayName {
    switch (this) {
      case EfficiencyRating.excellent:
        return 'Excellent';
      case EfficiencyRating.good:
        return 'Good';
      case EfficiencyRating.fair:
        return 'Fair';
      case EfficiencyRating.poor:
        return 'Poor';
    }
  }

  String get displayNameAr {
    switch (this) {
      case EfficiencyRating.excellent:
        return 'ممتاز';
      case EfficiencyRating.good:
        return 'جيد';
      case EfficiencyRating.fair:
        return 'مقبول';
      case EfficiencyRating.poor:
        return 'ضعيف';
    }
  }
}
