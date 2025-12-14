/// SAHOOL Weather Domain Entities
/// نماذج بيانات الطقس
///
/// Domain Layer - لا يعتمد على Flutter
/// يستخدم WeatherColor بدلاً من dart:ui Color

import '../value_objects/weather_color.dart';
import '../value_objects/alert_severity.dart';
import '../value_objects/weather_severity.dart';

/// حالة الطقس الحالية
class CurrentWeather {
  final double temperature;
  final double feelsLike;
  final int humidity;
  final double windSpeed;
  final String windDirection;
  final String condition;
  final String conditionAr;
  final String icon;
  final double? precipitation;
  final double? uvIndex;
  final DateTime timestamp;

  const CurrentWeather({
    required this.temperature,
    required this.feelsLike,
    required this.humidity,
    required this.windSpeed,
    required this.windDirection,
    required this.condition,
    required this.conditionAr,
    required this.icon,
    this.precipitation,
    this.uvIndex,
    required this.timestamp,
  });

  factory CurrentWeather.fromJson(Map<String, dynamic> json) {
    return CurrentWeather(
      temperature: (json['temperature'] as num).toDouble(),
      feelsLike: (json['feels_like'] as num).toDouble(),
      humidity: json['humidity'] as int,
      windSpeed: (json['wind_speed'] as num).toDouble(),
      windDirection: json['wind_direction'] as String,
      condition: json['condition'] as String,
      conditionAr: json['condition_ar'] as String? ?? json['condition'],
      icon: json['icon'] as String? ?? '☀️',
      precipitation: (json['precipitation'] as num?)?.toDouble(),
      uvIndex: (json['uv_index'] as num?)?.toDouble(),
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }

  String get temperatureDisplay => '${temperature.round()}°';
}

/// توقعات يوم واحد
class DailyForecast {
  final DateTime date;
  final double tempMin;
  final double tempMax;
  final String condition;
  final String conditionAr;
  final String icon;
  final int precipitationChance;
  final double? precipitationAmount;
  final int humidity;
  final double windSpeed;

  const DailyForecast({
    required this.date,
    required this.tempMin,
    required this.tempMax,
    required this.condition,
    required this.conditionAr,
    required this.icon,
    required this.precipitationChance,
    this.precipitationAmount,
    required this.humidity,
    required this.windSpeed,
  });

  factory DailyForecast.fromJson(Map<String, dynamic> json) {
    return DailyForecast(
      date: DateTime.parse(json['date'] as String),
      tempMin: (json['temp_min'] as num).toDouble(),
      tempMax: (json['temp_max'] as num).toDouble(),
      condition: json['condition'] as String,
      conditionAr: json['condition_ar'] as String? ?? json['condition'],
      icon: json['icon'] as String? ?? '☀️',
      precipitationChance: json['precipitation_chance'] as int? ?? 0,
      precipitationAmount: (json['precipitation_amount'] as num?)?.toDouble(),
      humidity: json['humidity'] as int? ?? 0,
      windSpeed: (json['wind_speed'] as num?)?.toDouble() ?? 0,
    );
  }

  String get dayName {
    final days = ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'];
    return days[date.weekday % 7];
  }
}

/// توقعات ساعية
class HourlyForecast {
  final DateTime time;
  final double temperature;
  final String condition;
  final String icon;
  final int precipitationChance;
  final int humidity;

  const HourlyForecast({
    required this.time,
    required this.temperature,
    required this.condition,
    required this.icon,
    required this.precipitationChance,
    required this.humidity,
  });

  factory HourlyForecast.fromJson(Map<String, dynamic> json) {
    return HourlyForecast(
      time: DateTime.parse(json['time'] as String),
      temperature: (json['temperature'] as num).toDouble(),
      condition: json['condition'] as String,
      icon: json['icon'] as String? ?? '☀️',
      precipitationChance: json['precipitation_chance'] as int? ?? 0,
      humidity: json['humidity'] as int? ?? 0,
    );
  }

  String get hourDisplay => '${time.hour}:00';
}

/// تنبيه طقس
class WeatherAlert {
  final String id;
  final String type;
  final String severity; // warning, watch, advisory
  final String title;
  final String titleAr;
  final String description;
  final DateTime startTime;
  final DateTime endTime;

  const WeatherAlert({
    required this.id,
    required this.type,
    required this.severity,
    required this.title,
    required this.titleAr,
    required this.description,
    required this.startTime,
    required this.endTime,
  });

  factory WeatherAlert.fromJson(Map<String, dynamic> json) {
    return WeatherAlert(
      id: json['id'] as String,
      type: json['type'] as String,
      severity: json['severity'] as String,
      title: json['title'] as String,
      titleAr: json['title_ar'] as String? ?? json['title'],
      description: json['description'] as String,
      startTime: DateTime.parse(json['start_time'] as String),
      endTime: DateTime.parse(json['end_time'] as String),
    );
  }

  /// الحصول على AlertSeverity enum
  AlertSeverity get alertSeverity => AlertSeverityColor.fromString(severity);

  /// الحصول على لون الشدة (Domain Color)
  WeatherColor get severityColor => alertSeverity.color;
}

/// تأثير الطقس على الزراعة
class AgriculturalImpact {
  final String category; // irrigation, spraying, harvesting, planting
  final String recommendation;
  final String recommendationAr;
  final String status; // favorable, caution, unfavorable
  final List<String> reasons;

  const AgriculturalImpact({
    required this.category,
    required this.recommendation,
    required this.recommendationAr,
    required this.status,
    required this.reasons,
  });

  factory AgriculturalImpact.fromJson(Map<String, dynamic> json) {
    return AgriculturalImpact(
      category: json['category'] as String,
      recommendation: json['recommendation'] as String,
      recommendationAr: json['recommendation_ar'] as String? ?? json['recommendation'],
      status: json['status'] as String,
      reasons: List<String>.from(json['reasons'] ?? []),
    );
  }

  /// الحصول على WeatherSeverity enum
  WeatherSeverity get weatherSeverity {
    switch (status.toLowerCase()) {
      case 'favorable':
        return WeatherSeverity.favorable;
      case 'caution':
        return WeatherSeverity.caution;
      case 'unfavorable':
        return WeatherSeverity.unfavorable;
      default:
        return WeatherSeverity.caution;
    }
  }

  /// الحصول على لون الحالة (Domain Color)
  WeatherColor get statusColor => weatherSeverity.color;

  String get categoryIcon {
    switch (category) {
      case 'irrigation':
        return '💧';
      case 'spraying':
        return '🌿';
      case 'harvesting':
        return '🌾';
      case 'planting':
        return '🌱';
      default:
        return '🌡️';
    }
  }

  String get categoryAr {
    switch (category) {
      case 'irrigation':
        return 'الري';
      case 'spraying':
        return 'الرش';
      case 'harvesting':
        return 'الحصاد';
      case 'planting':
        return 'الزراعة';
      default:
        return category;
    }
  }
}

/// بيانات الطقس الكاملة
class WeatherData {
  final CurrentWeather current;
  final List<HourlyForecast> hourly;
  final List<DailyForecast> daily;
  final List<WeatherAlert> alerts;
  final List<AgriculturalImpact> impacts;

  const WeatherData({
    required this.current,
    required this.hourly,
    required this.daily,
    required this.alerts,
    required this.impacts,
  });

  factory WeatherData.fromJson(Map<String, dynamic> json) {
    return WeatherData(
      current: CurrentWeather.fromJson(json['current']),
      hourly: (json['hourly'] as List?)
              ?.map((h) => HourlyForecast.fromJson(h))
              .toList() ??
          [],
      daily: (json['daily'] as List?)
              ?.map((d) => DailyForecast.fromJson(d))
              .toList() ??
          [],
      alerts: (json['alerts'] as List?)
              ?.map((a) => WeatherAlert.fromJson(a))
              .toList() ??
          [],
      impacts: (json['impacts'] as List?)
              ?.map((i) => AgriculturalImpact.fromJson(i))
              .toList() ??
          [],
    );
  }
}
