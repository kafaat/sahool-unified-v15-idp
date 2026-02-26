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

  Map<String, dynamic> toJson() => {
        'temperature': temperature,
        'feels_like': feelsLike,
        'humidity': humidity,
        'wind_speed': windSpeed,
        'wind_direction': windDirection,
        'condition': condition,
        'condition_ar': conditionAr,
        'icon': icon,
        'precipitation': precipitation,
        'uv_index': uvIndex,
        'timestamp': timestamp.toIso8601String(),
      };

  CurrentWeather copyWith({
    double? temperature,
    double? feelsLike,
    int? humidity,
    double? windSpeed,
    String? windDirection,
    String? condition,
    String? conditionAr,
    String? icon,
    double? precipitation,
    double? uvIndex,
    DateTime? timestamp,
  }) {
    return CurrentWeather(
      temperature: temperature ?? this.temperature,
      feelsLike: feelsLike ?? this.feelsLike,
      humidity: humidity ?? this.humidity,
      windSpeed: windSpeed ?? this.windSpeed,
      windDirection: windDirection ?? this.windDirection,
      condition: condition ?? this.condition,
      conditionAr: conditionAr ?? this.conditionAr,
      icon: icon ?? this.icon,
      precipitation: precipitation ?? this.precipitation,
      uvIndex: uvIndex ?? this.uvIndex,
      timestamp: timestamp ?? this.timestamp,
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

  Map<String, dynamic> toJson() => {
        'date': date.toIso8601String(),
        'temp_min': tempMin,
        'temp_max': tempMax,
        'condition': condition,
        'condition_ar': conditionAr,
        'icon': icon,
        'precipitation_chance': precipitationChance,
        'precipitation_amount': precipitationAmount,
        'humidity': humidity,
        'wind_speed': windSpeed,
      };

  DailyForecast copyWith({
    DateTime? date,
    double? tempMin,
    double? tempMax,
    String? condition,
    String? conditionAr,
    String? icon,
    int? precipitationChance,
    double? precipitationAmount,
    int? humidity,
    double? windSpeed,
  }) {
    return DailyForecast(
      date: date ?? this.date,
      tempMin: tempMin ?? this.tempMin,
      tempMax: tempMax ?? this.tempMax,
      condition: condition ?? this.condition,
      conditionAr: conditionAr ?? this.conditionAr,
      icon: icon ?? this.icon,
      precipitationChance: precipitationChance ?? this.precipitationChance,
      precipitationAmount: precipitationAmount ?? this.precipitationAmount,
      humidity: humidity ?? this.humidity,
      windSpeed: windSpeed ?? this.windSpeed,
    );
  }

  String get dayName {
    final days = [
      'الأحد',
      'الإثنين',
      'الثلاثاء',
      'الأربعاء',
      'الخميس',
      'الجمعة',
      'السبت'
    ];
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

  Map<String, dynamic> toJson() => {
        'time': time.toIso8601String(),
        'temperature': temperature,
        'condition': condition,
        'icon': icon,
        'precipitation_chance': precipitationChance,
        'humidity': humidity,
      };

  HourlyForecast copyWith({
    DateTime? time,
    double? temperature,
    String? condition,
    String? icon,
    int? precipitationChance,
    int? humidity,
  }) {
    return HourlyForecast(
      time: time ?? this.time,
      temperature: temperature ?? this.temperature,
      condition: condition ?? this.condition,
      icon: icon ?? this.icon,
      precipitationChance: precipitationChance ?? this.precipitationChance,
      humidity: humidity ?? this.humidity,
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

  Map<String, dynamic> toJson() => {
        'id': id,
        'type': type,
        'severity': severity,
        'title': title,
        'title_ar': titleAr,
        'description': description,
        'start_time': startTime.toIso8601String(),
        'end_time': endTime.toIso8601String(),
      };

  WeatherAlert copyWith({
    String? id,
    String? type,
    String? severity,
    String? title,
    String? titleAr,
    String? description,
    DateTime? startTime,
    DateTime? endTime,
  }) {
    return WeatherAlert(
      id: id ?? this.id,
      type: type ?? this.type,
      severity: severity ?? this.severity,
      title: title ?? this.title,
      titleAr: titleAr ?? this.titleAr,
      description: description ?? this.description,
      startTime: startTime ?? this.startTime,
      endTime: endTime ?? this.endTime,
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
      recommendationAr:
          json['recommendation_ar'] as String? ?? json['recommendation'],
      status: json['status'] as String,
      reasons: List<String>.from(json['reasons'] ?? []),
    );
  }

  Map<String, dynamic> toJson() => {
        'category': category,
        'recommendation': recommendation,
        'recommendation_ar': recommendationAr,
        'status': status,
        'reasons': reasons,
      };

  AgriculturalImpact copyWith({
    String? category,
    String? recommendation,
    String? recommendationAr,
    String? status,
    List<String>? reasons,
  }) {
    return AgriculturalImpact(
      category: category ?? this.category,
      recommendation: recommendation ?? this.recommendation,
      recommendationAr: recommendationAr ?? this.recommendationAr,
      status: status ?? this.status,
      reasons: reasons ?? this.reasons,
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

  Map<String, dynamic> toJson() => {
        'current': current.toJson(),
        'hourly': hourly.map((h) => h.toJson()).toList(),
        'daily': daily.map((d) => d.toJson()).toList(),
        'alerts': alerts.map((a) => a.toJson()).toList(),
        'impacts': impacts.map((i) => i.toJson()).toList(),
      };

  WeatherData copyWith({
    CurrentWeather? current,
    List<HourlyForecast>? hourly,
    List<DailyForecast>? daily,
    List<WeatherAlert>? alerts,
    List<AgriculturalImpact>? impacts,
  }) {
    return WeatherData(
      current: current ?? this.current,
      hourly: hourly ?? this.hourly,
      daily: daily ?? this.daily,
      alerts: alerts ?? this.alerts,
      impacts: impacts ?? this.impacts,
    );
  }
}
