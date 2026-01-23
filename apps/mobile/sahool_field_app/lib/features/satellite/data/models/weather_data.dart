/// Weather Data Model for Satellite Feature - نموذج بيانات الطقس
/// Simplified weather data for satellite monitoring integration
library;

import 'package:equatable/equatable.dart';

/// Weather Summary for Field
/// ملخص الطقس للحقل
class WeatherSummary extends Equatable {
  final String fieldId;
  final double temperature; // °C
  final double minTemp;
  final double maxTemp;
  final double precipitation; // mm
  final double humidity; // %
  final double et0; // mm/day - reference evapotranspiration
  final String condition; // sunny, cloudy, rainy
  final String conditionAr;
  final DateTime updatedAt;
  final List<DailyForecastSummary> forecast; // 7 days

  const WeatherSummary({
    required this.fieldId,
    required this.temperature,
    required this.minTemp,
    required this.maxTemp,
    required this.precipitation,
    required this.humidity,
    required this.et0,
    required this.condition,
    required this.conditionAr,
    required this.updatedAt,
    this.forecast = const [],
  });

  factory WeatherSummary.fromJson(Map<String, dynamic> json) {
    final forecastData = json['forecast'] ?? [];

    return WeatherSummary(
      fieldId: json['field_id'] ?? json['fieldId'] ?? '',
      temperature: (json['temperature'] ?? json['temp'] ?? 0.0).toDouble(),
      minTemp: (json['min_temp'] ?? json['minTemp'] ?? 0.0).toDouble(),
      maxTemp: (json['max_temp'] ?? json['maxTemp'] ?? 0.0).toDouble(),
      precipitation: (json['precipitation'] ?? json['rain'] ?? 0.0).toDouble(),
      humidity: (json['humidity'] ?? 0.0).toDouble(),
      et0: (json['et0'] ?? json['evapotranspiration'] ?? 0.0).toDouble(),
      condition: json['condition'] ?? json['weather'] ?? 'clear',
      conditionAr: json['condition_ar'] ?? json['conditionAr'] ?? 'صافي',
      updatedAt: DateTime.parse(
        json['updated_at'] ?? json['updatedAt'] ?? DateTime.now().toIso8601String(),
      ),
      forecast: (forecastData as List)
          .map((item) => DailyForecastSummary.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'field_id': fieldId,
      'temperature': temperature,
      'min_temp': minTemp,
      'max_temp': maxTemp,
      'precipitation': precipitation,
      'humidity': humidity,
      'et0': et0,
      'condition': condition,
      'condition_ar': conditionAr,
      'updated_at': updatedAt.toIso8601String(),
      'forecast': forecast.map((f) => f.toJson()).toList(),
    };
  }

  /// Get irrigation need based on ET0
  /// حساب احتياج الري بناءً على ET0
  double getIrrigationNeed() {
    // Simple calculation: ET0 - recent rain
    return (et0 - (precipitation / 7)).clamp(0.0, et0);
  }

  @override
  List<Object?> get props => [
        fieldId,
        temperature,
        minTemp,
        maxTemp,
        precipitation,
        humidity,
        et0,
        condition,
        conditionAr,
        updatedAt,
        forecast,
      ];
}

/// Daily Forecast Summary
/// ملخص التوقعات اليومية
class DailyForecastSummary extends Equatable {
  final DateTime date;
  final double tempMin;
  final double tempMax;
  final double precipitation; // mm
  final String condition;
  final String conditionAr;
  final String? icon;

  const DailyForecastSummary({
    required this.date,
    required this.tempMin,
    required this.tempMax,
    required this.precipitation,
    required this.condition,
    required this.conditionAr,
    this.icon,
  });

  factory DailyForecastSummary.fromJson(Map<String, dynamic> json) {
    return DailyForecastSummary(
      date: DateTime.parse(json['date'] ?? DateTime.now().toIso8601String()),
      tempMin: (json['temp_min'] ?? json['tempMin'] ?? 0.0).toDouble(),
      tempMax: (json['temp_max'] ?? json['tempMax'] ?? 0.0).toDouble(),
      precipitation: (json['precipitation'] ?? json['rain'] ?? 0.0).toDouble(),
      condition: json['condition'] ?? json['weather'] ?? 'clear',
      conditionAr: json['condition_ar'] ?? json['conditionAr'] ?? 'صافي',
      icon: json['icon'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'date': date.toIso8601String(),
      'temp_min': tempMin,
      'temp_max': tempMax,
      'precipitation': precipitation,
      'condition': condition,
      'condition_ar': conditionAr,
      'icon': icon,
    };
  }

  @override
  List<Object?> get props => [date, tempMin, tempMax, precipitation, condition, conditionAr, icon];
}

/// Weather Alert for Satellite Feature
/// تنبيه طقس لميزة الأقمار
class WeatherAlertSummary extends Equatable {
  final String id;
  final WeatherAlertType type;
  final String severity; // info, warning, critical
  final String message;
  final String messageAr;
  final DateTime startsAt;
  final DateTime? endsAt;

  const WeatherAlertSummary({
    required this.id,
    required this.type,
    required this.severity,
    required this.message,
    required this.messageAr,
    required this.startsAt,
    this.endsAt,
  });

  factory WeatherAlertSummary.fromJson(Map<String, dynamic> json) {
    return WeatherAlertSummary(
      id: json['id'] ?? '',
      type: WeatherAlertType.fromString(json['type'] ?? 'general'),
      severity: json['severity'] ?? 'info',
      message: json['message'] ?? '',
      messageAr: json['message_ar'] ?? json['messageAr'] ?? '',
      startsAt: DateTime.parse(
        json['starts_at'] ?? json['startsAt'] ?? DateTime.now().toIso8601String(),
      ),
      endsAt: json['ends_at'] != null ? DateTime.parse(json['ends_at']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type.value,
      'severity': severity,
      'message': message,
      'message_ar': messageAr,
      'starts_at': startsAt.toIso8601String(),
      'ends_at': endsAt?.toIso8601String(),
    };
  }

  @override
  List<Object?> get props => [id, type, severity, message, messageAr, startsAt, endsAt];
}

/// Weather Alert Type
/// نوع تنبيه الطقس
enum WeatherAlertType {
  frost('frost', 'صقيع'),
  heat('heat', 'حرارة عالية'),
  drought('drought', 'جفاف'),
  heavyRain('heavy_rain', 'أمطار غزيرة'),
  wind('wind', 'رياح قوية'),
  general('general', 'عام');

  final String value;
  final String arabicLabel;

  const WeatherAlertType(this.value, this.arabicLabel);

  static WeatherAlertType fromString(String value) {
    return WeatherAlertType.values.firstWhere(
      (type) => type.value.toLowerCase() == value.toLowerCase(),
      orElse: () => WeatherAlertType.general,
    );
  }

  String getLabel(bool isArabic) => isArabic ? arabicLabel : value;
}
