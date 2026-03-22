/// Weather-Irrigation Integration Service
/// خدمة تكامل الطقس والري
///
/// Provides integration between weather data and irrigation planning:
/// - ET0 calculation from weather data
/// - Rain-adjusted irrigation scheduling
/// - Weather alerts for irrigation
/// - Optimal irrigation timing recommendations
library;

import 'dart:math' as math;

import '../../../weather/domain/entities/weather_entities.dart'
    as weather_entities;
import 'irrigation_scheduler.dart';

/// Weather-Irrigation Integration Service
/// خدمة تكامل الطقس والري
class WeatherIrrigationIntegration {
  const WeatherIrrigationIntegration();

  // ═══════════════════════════════════════════════════════════════════════════
  // ET0 Calculations - حسابات البخر-نتح المرجعي
  // ═══════════════════════════════════════════════════════════════════════════

  /// Calculate reference evapotranspiration (ET0) using Penman-Monteith equation
  /// حساب البخر-نتح المرجعي باستخدام معادلة بنمان-مونتيث
  ///
  /// Simplified FAO-56 Penman-Monteith method
  ///
  /// [temperatureMax] - Maximum temperature (C)
  /// [temperatureMin] - Minimum temperature (C)
  /// [humidity] - Relative humidity (%)
  /// [windSpeed] - Wind speed at 2m (m/s)
  /// [solarRadiation] - Solar radiation (MJ/m2/day) - estimated if null
  /// [latitude] - Latitude for radiation estimation
  /// [dayOfYear] - Day of year (1-365)
  ///
  /// Returns ET0 in mm/day
  double calculateET0({
    required double temperatureMax,
    required double temperatureMin,
    required double humidity,
    required double windSpeed,
    double? solarRadiation,
    double latitude = 15.0, // Default for Yemen
    int? dayOfYear,
  }) {
    // Mean temperature
    final tMean = (temperatureMax + temperatureMin) / 2;

    // Psychrometric constant (kPa/C) for sea level
    const gamma = 0.066;

    // Slope of saturation vapor pressure curve
    final delta = 4098 *
        (0.6108 * math.exp(17.27 * tMean / (tMean + 237.3))) /
        math.pow(tMean + 237.3, 2);

    // Saturation vapor pressure
    final esTmax =
        0.6108 * math.exp(17.27 * temperatureMax / (temperatureMax + 237.3));
    final esTmin =
        0.6108 * math.exp(17.27 * temperatureMin / (temperatureMin + 237.3));
    final es = (esTmax + esTmin) / 2;

    // Actual vapor pressure
    final ea = es * humidity / 100;

    // Net radiation (estimated if not provided)
    double rn;
    if (solarRadiation != null) {
      rn = _calculateNetRadiation(
          solarRadiation, temperatureMax, temperatureMin, ea);
    } else {
      rn = _estimateNetRadiation(
        latitude: latitude,
        dayOfYear: dayOfYear ??
            DateTime.now()
                    .difference(DateTime(DateTime.now().year, 1, 1))
                    .inDays +
                1,
        temperatureMax: temperatureMax,
        temperatureMin: temperatureMin,
        ea: ea,
      );
    }

    // Soil heat flux (assumed 0 for daily calculations)
    const g = 0.0;

    // ET0 calculation (FAO-56 equation)
    final et0 = (0.408 * delta * (rn - g) +
            gamma * 900 / (tMean + 273) * windSpeed * (es - ea)) /
        (delta + gamma * (1 + 0.34 * windSpeed));

    return et0.clamp(0.0, 15.0); // Reasonable bounds
  }

  /// Calculate net radiation from solar radiation
  double _calculateNetRadiation(
    double solarRadiation,
    double tMax,
    double tMin,
    double ea,
  ) {
    // Net shortwave radiation (assuming albedo of 0.23 for grass)
    final rns = (1 - 0.23) * solarRadiation;

    // Net longwave radiation (Stefan-Boltzmann)
    const sigma = 4.903e-9; // Stefan-Boltzmann constant
    final tMaxK = tMax + 273.16;
    final tMinK = tMin + 273.16;

    final rnl = sigma *
        ((math.pow(tMaxK, 4) + math.pow(tMinK, 4)) / 2) *
        (0.34 - 0.14 * math.sqrt(ea)) *
        (1.35 * solarRadiation / (0.75 * 25) - 0.35); // Simplified Rs/Rso ratio

    return rns - rnl;
  }

  /// Estimate net radiation from location and date
  double _estimateNetRadiation({
    required double latitude,
    required int dayOfYear,
    required double temperatureMax,
    required double temperatureMin,
    required double ea,
  }) {
    // Solar declination
    final dr = 1 + 0.033 * math.cos(2 * math.pi / 365 * dayOfYear);
    final delta = 0.409 * math.sin(2 * math.pi / 365 * dayOfYear - 1.39);

    // Latitude in radians
    final phi = latitude * math.pi / 180;

    // Sunset hour angle
    final ws = math.acos(-math.tan(phi) * math.tan(delta));

    // Extraterrestrial radiation
    final ra = (24 * 60 / math.pi) *
        0.0820 *
        dr *
        (ws * math.sin(phi) * math.sin(delta) +
            math.cos(phi) * math.cos(delta) * math.sin(ws));

    // Clear-sky radiation
    final rso = (0.75 + 2e-5 * 0) * ra; // 0 elevation

    // Estimated actual radiation (assuming average cloudiness)
    final rs = 0.65 * rso;

    return _calculateNetRadiation(rs, temperatureMax, temperatureMin, ea);
  }

  /// Calculate ET0 from weather entity
  /// حساب البخر-نتح المرجعي من كيان الطقس
  double calculateET0FromWeather(
    IrrigationWeatherData weather, {
    double latitude = 15.0,
  }) {
    // Convert wind from km/h to m/s if needed
    final windMs = weather.windSpeed / 3.6;

    return calculateET0(
      temperatureMax: weather.temperatureMax,
      temperatureMin: weather.temperatureMin,
      humidity: weather.humidity,
      windSpeed: windMs,
      latitude: latitude,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Weather-Based Adjustments - التعديلات المبنية على الطقس
  // ═══════════════════════════════════════════════════════════════════════════

  /// Adjust irrigation amount based on weather conditions
  /// تعديل كمية الري بناءً على أحوال الطقس
  IrrigationAdjustment calculateAdjustment({
    required double baseWaterNeedMm,
    required IrrigationWeatherData currentWeather,
    List<IrrigationWeatherData>? forecast,
  }) {
    double adjustment = 1.0;
    final reasons = <String>[];
    final reasonsAr = <String>[];

    // Temperature adjustment
    if (currentWeather.temperature > 40) {
      adjustment *= 1.15;
      reasons.add('High temperature (+15%)');
      reasonsAr.add('درجة حرارة عالية (+15%)');
    } else if (currentWeather.temperature > 35) {
      adjustment *= 1.10;
      reasons.add('Warm temperature (+10%)');
      reasonsAr.add('درجة حرارة دافئة (+10%)');
    } else if (currentWeather.temperature < 15) {
      adjustment *= 0.90;
      reasons.add('Cool temperature (-10%)');
      reasonsAr.add('درجة حرارة باردة (-10%)');
    }

    // Humidity adjustment
    if (currentWeather.humidity < 30) {
      adjustment *= 1.10;
      reasons.add('Low humidity (+10%)');
      reasonsAr.add('رطوبة منخفضة (+10%)');
    } else if (currentWeather.humidity > 80) {
      adjustment *= 0.95;
      reasons.add('High humidity (-5%)');
      reasonsAr.add('رطوبة عالية (-5%)');
    }

    // Wind adjustment
    final windMs = currentWeather.windSpeed / 3.6;
    if (windMs > 5) {
      adjustment *= 1.10;
      reasons.add('Windy conditions (+10%)');
      reasonsAr.add('ظروف رياح (+10%)');
    } else if (windMs > 3) {
      adjustment *= 1.05;
      reasons.add('Light wind (+5%)');
      reasonsAr.add('رياح خفيفة (+5%)');
    }

    // Rain adjustment from forecast
    double expectedRain = 0;
    if (forecast != null) {
      for (final day in forecast.take(3)) {
        expectedRain += day.precipitation;
      }
    }

    if (expectedRain > 20) {
      adjustment *= 0.50;
      reasons.add('Heavy rain expected (-50%)');
      reasonsAr.add('أمطار غزيرة متوقعة (-50%)');
    } else if (expectedRain > 10) {
      adjustment *= 0.70;
      reasons.add('Rain expected (-30%)');
      reasonsAr.add('أمطار متوقعة (-30%)');
    } else if (expectedRain > 5) {
      adjustment *= 0.85;
      reasons.add('Light rain expected (-15%)');
      reasonsAr.add('أمطار خفيفة متوقعة (-15%)');
    }

    // Recent rain adjustment
    if (currentWeather.precipitation > 5) {
      adjustment *= 0.80;
      reasons.add('Recent rain (-20%)');
      reasonsAr.add('أمطار حديثة (-20%)');
    }

    final adjustedAmount = baseWaterNeedMm * adjustment;

    return IrrigationAdjustment(
      originalAmount: baseWaterNeedMm,
      adjustedAmount: adjustedAmount,
      adjustmentFactor: adjustment,
      reasons: reasons,
      reasonsAr: reasonsAr,
      expectedRainMm: expectedRain,
    );
  }

  /// Determine if irrigation should be skipped
  /// تحديد ما إذا كان يجب تخطي الري
  SkipDecision shouldSkipIrrigation({
    required IrrigationWeatherData currentWeather,
    required List<IrrigationWeatherData> forecast,
  }) {
    // Calculate expected rain in next 48 hours
    double rain48h = 0;
    for (final day in forecast.take(2)) {
      rain48h += day.precipitation;
    }

    // Check for rain conditions
    if (rain48h > 15) {
      return SkipDecision(
        shouldSkip: true,
        reason:
            'Significant rain expected (${rain48h.toStringAsFixed(0)}mm in 48h)',
        reasonAr:
            'أمطار كبيرة متوقعة (${rain48h.toStringAsFixed(0)}ملم في 48 ساعة)',
        postponeDays: 2,
      );
    }

    // Check current rain
    if (currentWeather.precipitation > 10) {
      return const SkipDecision(
        shouldSkip: true,
        reason: 'Current rain event',
        reasonAr: 'هطول أمطار حالي',
        postponeDays: 1,
      );
    }

    // Check for extreme cold
    if (currentWeather.temperatureMin < 2) {
      return const SkipDecision(
        shouldSkip: true,
        reason: 'Frost risk - delay irrigation',
        reasonAr: 'خطر الصقيع - تأخير الري',
        postponeDays: 1,
      );
    }

    // Check for extreme wind
    if (currentWeather.windSpeed > 40) {
      return const SkipDecision(
        shouldSkip: true,
        reason: 'High wind - poor irrigation efficiency',
        reasonAr: 'رياح قوية - كفاءة ري ضعيفة',
        postponeDays: 1,
      );
    }

    return const SkipDecision(
      shouldSkip: false,
      reason: 'Weather conditions suitable for irrigation',
      reasonAr: 'الطقس مناسب للري',
      postponeDays: 0,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Optimal Timing - التوقيت الأمثل
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get optimal irrigation window for the day
  /// الحصول على نافذة الري المثلى لليوم
  IrrigationWindow getOptimalIrrigationWindow(IrrigationWeatherData weather) {
    // Best times are early morning or evening
    // Avoid midday due to high evaporation

    DateTime optimalStart;
    DateTime optimalEnd;
    String reason;
    String reasonAr;

    if (weather.temperature > 35) {
      // Hot day - prefer early morning
      optimalStart =
          DateTime(weather.date.year, weather.date.month, weather.date.day, 5);
      optimalEnd =
          DateTime(weather.date.year, weather.date.month, weather.date.day, 8);
      reason = 'Early morning to avoid heat and evaporation';
      reasonAr = 'الصباح الباكر لتجنب الحرارة والتبخر';
    } else if (weather.windSpeed > 25) {
      // Windy - prefer calm periods (usually early morning/evening)
      optimalStart =
          DateTime(weather.date.year, weather.date.month, weather.date.day, 5);
      optimalEnd =
          DateTime(weather.date.year, weather.date.month, weather.date.day, 7);
      reason = 'Early morning when wind is typically calmer';
      reasonAr = 'الصباح الباكر عندما تكون الرياح أهدأ';
    } else if (weather.humidity > 80) {
      // High humidity - midday acceptable
      optimalStart =
          DateTime(weather.date.year, weather.date.month, weather.date.day, 6);
      optimalEnd =
          DateTime(weather.date.year, weather.date.month, weather.date.day, 18);
      reason = 'Flexible timing due to low evaporation risk';
      reasonAr = 'توقيت مرن بسبب انخفاض خطر التبخر';
    } else {
      // Normal conditions - morning or evening
      optimalStart =
          DateTime(weather.date.year, weather.date.month, weather.date.day, 5);
      optimalEnd =
          DateTime(weather.date.year, weather.date.month, weather.date.day, 9);
      reason = 'Morning hours for best efficiency';
      reasonAr = 'ساعات الصباح للحصول على أفضل كفاءة';
    }

    // Calculate efficiency factor for this window
    double efficiencyFactor = 1.0;
    if (weather.temperature > 30 && optimalStart.hour > 10) {
      efficiencyFactor = 0.85;
    }

    return IrrigationWindow(
      optimalStart: optimalStart,
      optimalEnd: optimalEnd,
      reason: reason,
      reasonAr: reasonAr,
      efficiencyFactor: efficiencyFactor,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Weather Alerts for Irrigation - تنبيهات الطقس للري
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get irrigation-relevant weather alerts
  /// الحصول على تنبيهات الطقس المتعلقة بالري
  List<IrrigationWeatherAlert> getIrrigationAlerts(
    IrrigationWeatherData weather,
    List<IrrigationWeatherData> forecast,
  ) {
    final alerts = <IrrigationWeatherAlert>[];

    // Heat wave alert
    if (weather.temperatureMax > 42 ||
        (forecast.isNotEmpty &&
            forecast.take(3).every((w) => w.temperatureMax > 40))) {
      alerts.add(const IrrigationWeatherAlert(
        type: IrrigationAlertType.heatWave,
        severity: AlertSeverity.high,
        message: 'Heat wave conditions - increase irrigation frequency',
        messageAr: 'ظروف موجة حر - زيادة تكرار الري',
        action: 'Increase irrigation by 15-20% and water during cooler hours',
        actionAr: 'زيادة الري بنسبة 15-20% والري خلال الساعات الباردة',
      ));
    }

    // Frost alert
    if (weather.temperatureMin < 3 ||
        forecast.any((w) => w.temperatureMin < 3)) {
      alerts.add(const IrrigationWeatherAlert(
        type: IrrigationAlertType.frost,
        severity: AlertSeverity.critical,
        message: 'Frost risk - protect crops and avoid irrigation',
        messageAr: 'خطر الصقيع - حماية المحاصيل وتجنب الري',
        action: 'Delay irrigation until temperatures rise above 5C',
        actionAr: 'تأخير الري حتى ترتفع درجات الحرارة فوق 5°م',
      ));
    }

    // Heavy rain alert
    final totalRain =
        forecast.take(3).fold<double>(0, (sum, w) => sum + w.precipitation);
    if (totalRain > 30) {
      alerts.add(IrrigationWeatherAlert(
        type: IrrigationAlertType.heavyRain,
        severity: AlertSeverity.medium,
        message:
            'Heavy rain expected (${totalRain.toStringAsFixed(0)}mm) - skip irrigation',
        messageAr:
            'أمطار غزيرة متوقعة (${totalRain.toStringAsFixed(0)}ملم) - تخطي الري',
        action: 'Cancel scheduled irrigation for next 2-3 days',
        actionAr: 'إلغاء الري المجدول لمدة 2-3 أيام',
      ));
    }

    // High wind alert
    if (weather.windSpeed > 30) {
      alerts.add(const IrrigationWeatherAlert(
        type: IrrigationAlertType.highWind,
        severity: AlertSeverity.medium,
        message: 'High wind reduces irrigation efficiency',
        messageAr: 'الرياح العالية تقلل من كفاءة الري',
        action: 'Use drip irrigation or wait for calmer conditions',
        actionAr: 'استخدم الري بالتنقيط أو انتظر هدوء الرياح',
      ));
    }

    // Drought conditions
    if (forecast.length >= 7 &&
        forecast.every((w) => w.precipitation < 1) &&
        weather.humidity < 30) {
      alerts.add(const IrrigationWeatherAlert(
        type: IrrigationAlertType.drought,
        severity: AlertSeverity.high,
        message: 'Drought conditions - monitor soil moisture closely',
        messageAr: 'ظروف جفاف - مراقبة رطوبة التربة عن كثب',
        action: 'Increase irrigation frequency and use mulch to conserve water',
        actionAr: 'زيادة تكرار الري واستخدام الغطاء للحفاظ على المياه',
      ));
    }

    return alerts;
  }

  /// Convert weather forecast to irrigation scheduler format
  /// تحويل توقعات الطقس إلى تنسيق مجدول الري
  WeatherForecast toSchedulerForecast(List<IrrigationWeatherData> weatherData) {
    return WeatherForecast(
      days: weatherData
          .map((w) => DayForecast(
                date: w.date,
                temperatureMax: w.temperatureMax,
                temperatureMin: w.temperatureMin,
                humidity: w.humidity,
                rainMm: w.precipitation,
                windSpeedKmh: w.windSpeed,
                condition: w.condition,
              ))
          .toList(),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Supporting Models - نماذج مساعدة
// ═══════════════════════════════════════════════════════════════════════════

/// Irrigation adjustment result
/// نتيجة تعديل الري
class IrrigationAdjustment {
  final double originalAmount;
  final double adjustedAmount;
  final double adjustmentFactor;
  final List<String> reasons;
  final List<String> reasonsAr;
  final double expectedRainMm;

  const IrrigationAdjustment({
    required this.originalAmount,
    required this.adjustedAmount,
    required this.adjustmentFactor,
    required this.reasons,
    required this.reasonsAr,
    required this.expectedRainMm,
  });

  double get savingsPercent => (1 - adjustmentFactor) * 100;
}

/// Skip irrigation decision
/// قرار تخطي الري
class SkipDecision {
  final bool shouldSkip;
  final String reason;
  final String reasonAr;
  final int postponeDays;

  const SkipDecision({
    required this.shouldSkip,
    required this.reason,
    required this.reasonAr,
    required this.postponeDays,
  });
}

/// Optimal irrigation window
/// نافذة الري المثلى
class IrrigationWindow {
  final DateTime optimalStart;
  final DateTime optimalEnd;
  final String reason;
  final String reasonAr;
  final double efficiencyFactor;

  const IrrigationWindow({
    required this.optimalStart,
    required this.optimalEnd,
    required this.reason,
    required this.reasonAr,
    required this.efficiencyFactor,
  });

  Duration get duration => optimalEnd.difference(optimalStart);
}

/// Irrigation weather alert
/// تنبيه طقس الري
class IrrigationWeatherAlert {
  final IrrigationAlertType type;
  final AlertSeverity severity;
  final String message;
  final String messageAr;
  final String action;
  final String actionAr;

  const IrrigationWeatherAlert({
    required this.type,
    required this.severity,
    required this.message,
    required this.messageAr,
    required this.action,
    required this.actionAr,
  });
}

/// Alert types for irrigation
enum IrrigationAlertType {
  heatWave,
  frost,
  heavyRain,
  highWind,
  drought,
  waterRestriction,
}

/// Alert severity levels
enum AlertSeverity {
  low,
  medium,
  high,
  critical,
}

extension AlertSeverityX on AlertSeverity {
  String get displayName {
    switch (this) {
      case AlertSeverity.low:
        return 'Low';
      case AlertSeverity.medium:
        return 'Medium';
      case AlertSeverity.high:
        return 'High';
      case AlertSeverity.critical:
        return 'Critical';
    }
  }

  String get displayNameAr {
    switch (this) {
      case AlertSeverity.low:
        return 'منخفض';
      case AlertSeverity.medium:
        return 'متوسط';
      case AlertSeverity.high:
        return 'عالي';
      case AlertSeverity.critical:
        return 'حرج';
    }
  }
}

/// Simplified weather data for internal irrigation calculations
/// بيانات طقس مبسطة لحسابات الري الداخلية
class IrrigationWeatherData {
  final DateTime date;
  final double temperature;
  final double temperatureMax;
  final double temperatureMin;
  final double humidity;
  final double windSpeed;
  final double precipitation;
  final String condition;

  const IrrigationWeatherData({
    required this.date,
    required this.temperature,
    required this.temperatureMax,
    required this.temperatureMin,
    required this.humidity,
    required this.windSpeed,
    required this.precipitation,
    required this.condition,
  });

  /// Create from weather entities DailyForecast
  factory IrrigationWeatherData.fromDailyForecast(
    weather_entities.DailyForecast forecast,
  ) {
    return IrrigationWeatherData(
      date: forecast.date,
      temperature: (forecast.tempMax + forecast.tempMin) / 2,
      temperatureMax: forecast.tempMax,
      temperatureMin: forecast.tempMin,
      humidity: forecast.humidity.toDouble(),
      windSpeed: forecast.windSpeed,
      precipitation: forecast.precipitationAmount ?? 0,
      condition: forecast.condition,
    );
  }

  /// Create from weather entities CurrentWeather
  factory IrrigationWeatherData.fromCurrentWeather(
    weather_entities.CurrentWeather current,
    DateTime date,
  ) {
    return IrrigationWeatherData(
      date: date,
      temperature: current.temperature,
      temperatureMax: current.temperature + 3, // Estimate
      temperatureMin: current.temperature - 5, // Estimate
      humidity: current.humidity.toDouble(),
      windSpeed: current.windSpeed,
      precipitation: current.precipitation ?? 0,
      condition: current.condition,
    );
  }
}
