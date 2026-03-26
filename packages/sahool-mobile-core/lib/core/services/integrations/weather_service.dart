/// SAHOOL Weather Service Integration
/// تكامل خدمة الطقس
///
/// Handles weather-related operations:
/// - Current weather conditions
/// - Weather forecasts
/// - Weather alerts
/// - Agricultural calendar
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../network/api_result.dart';
import '../service_connector.dart';

/// Current weather data model
class CurrentWeather {
  final double temperature;
  final double? feelsLike;
  final int humidity;
  final double? windSpeed;
  final String? windDirection;
  final double? precipitation;
  final int? cloudCover;
  final double? uvIndex;
  final String? condition;
  final String? conditionAr;
  final String? icon;
  final DateTime timestamp;
  final String? location;

  const CurrentWeather({
    required this.temperature,
    this.feelsLike,
    required this.humidity,
    this.windSpeed,
    this.windDirection,
    this.precipitation,
    this.cloudCover,
    this.uvIndex,
    this.condition,
    this.conditionAr,
    this.icon,
    required this.timestamp,
    this.location,
  });

  factory CurrentWeather.fromJson(Map<String, dynamic> json) {
    return CurrentWeather(
      temperature: (json['temperature'] as num?)?.toDouble() ?? 0.0,
      feelsLike: (json['feels_like'] as num?)?.toDouble(),
      humidity: (json['humidity'] as num?)?.toInt() ?? 0,
      windSpeed: (json['wind_speed'] as num?)?.toDouble(),
      windDirection: json['wind_direction'] as String?,
      precipitation: (json['precipitation'] as num?)?.toDouble(),
      cloudCover: (json['cloud_cover'] as num?)?.toInt(),
      uvIndex: (json['uv_index'] as num?)?.toDouble(),
      condition: json['condition'] as String?,
      conditionAr: json['condition_ar'] as String?,
      icon: json['icon'] as String?,
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : DateTime.now(),
      location: json['location'] as String?,
    );
  }
}

/// Weather forecast day model
class ForecastDay {
  final DateTime date;
  final double tempMax;
  final double tempMin;
  final double? avgTemp;
  final int? avgHumidity;
  final double? totalPrecipitation;
  final double? precipitationProbability;
  final double? maxWindSpeed;
  final String? condition;
  final String? conditionAr;
  final String? icon;
  final DateTime? sunrise;
  final DateTime? sunset;

  const ForecastDay({
    required this.date,
    required this.tempMax,
    required this.tempMin,
    this.avgTemp,
    this.avgHumidity,
    this.totalPrecipitation,
    this.precipitationProbability,
    this.maxWindSpeed,
    this.condition,
    this.conditionAr,
    this.icon,
    this.sunrise,
    this.sunset,
  });

  factory ForecastDay.fromJson(Map<String, dynamic> json) {
    return ForecastDay(
      date: DateTime.parse(json['date'] as String),
      tempMax: (json['temp_max'] as num?)?.toDouble() ?? 0.0,
      tempMin: (json['temp_min'] as num?)?.toDouble() ?? 0.0,
      avgTemp: (json['avg_temp'] as num?)?.toDouble(),
      avgHumidity: (json['avg_humidity'] as num?)?.toInt(),
      totalPrecipitation: (json['total_precipitation'] as num?)?.toDouble(),
      precipitationProbability: (json['precipitation_probability'] as num?)?.toDouble(),
      maxWindSpeed: (json['max_wind_speed'] as num?)?.toDouble(),
      condition: json['condition'] as String?,
      conditionAr: json['condition_ar'] as String?,
      icon: json['icon'] as String?,
      sunrise: json['sunrise'] != null ? DateTime.tryParse(json['sunrise'] as String) : null,
      sunset: json['sunset'] != null ? DateTime.tryParse(json['sunset'] as String) : null,
    );
  }
}

/// Weather alert model
class WeatherAlert {
  final String id;
  final String type;
  final String severity;
  final String headline;
  final String? headlineAr;
  final String? description;
  final String? descriptionAr;
  final DateTime startTime;
  final DateTime endTime;
  final String? source;
  final List<String>? affectedAreas;

  const WeatherAlert({
    required this.id,
    required this.type,
    required this.severity,
    required this.headline,
    this.headlineAr,
    this.description,
    this.descriptionAr,
    required this.startTime,
    required this.endTime,
    this.source,
    this.affectedAreas,
  });

  factory WeatherAlert.fromJson(Map<String, dynamic> json) {
    return WeatherAlert(
      id: json['id'] as String? ?? '',
      type: json['type'] as String? ?? 'unknown',
      severity: json['severity'] as String? ?? 'moderate',
      headline: json['headline'] as String? ?? '',
      headlineAr: json['headline_ar'] as String?,
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      startTime: DateTime.parse(json['start_time'] as String),
      endTime: DateTime.parse(json['end_time'] as String),
      source: json['source'] as String?,
      affectedAreas: (json['affected_areas'] as List?)?.cast<String>(),
    );
  }

  bool get isActive {
    final now = DateTime.now();
    return now.isAfter(startTime) && now.isBefore(endTime);
  }
}

/// Agricultural calendar event
class AgriculturalEvent {
  final String id;
  final String title;
  final String? titleAr;
  final String type;
  final String? description;
  final String? descriptionAr;
  final DateTime date;
  final String? cropType;
  final String? recommendation;
  final String? recommendationAr;

  const AgriculturalEvent({
    required this.id,
    required this.title,
    this.titleAr,
    required this.type,
    this.description,
    this.descriptionAr,
    required this.date,
    this.cropType,
    this.recommendation,
    this.recommendationAr,
  });

  factory AgriculturalEvent.fromJson(Map<String, dynamic> json) {
    return AgriculturalEvent(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      titleAr: json['title_ar'] as String?,
      type: json['type'] as String? ?? 'general',
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      date: DateTime.parse(json['date'] as String),
      cropType: json['crop_type'] as String?,
      recommendation: json['recommendation'] as String?,
      recommendationAr: json['recommendation_ar'] as String?,
    );
  }
}

/// Weather Service Connector
/// موصل خدمة الطقس
class WeatherServiceConnector extends ServiceConnector {
  WeatherServiceConnector({required super.ref}) : super(serviceId: 'weather');

  /// Get current weather
  /// الحصول على الطقس الحالي
  Future<ApiResult<CurrentWeather>> getCurrentWeather({
    double? latitude,
    double? longitude,
    String? location,
  }) async {
    final queryParams = <String, dynamic>{
      if (latitude != null) 'lat': latitude,
      if (longitude != null) 'lng': longitude,
      if (location != null) 'location': location,
    };

    return get(
      getEndpoint('current') ?? '/api/v1/weather/current',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
      parser: (data) => CurrentWeather.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Get weather by location name
  /// الحصول على الطقس حسب اسم الموقع
  Future<ApiResult<CurrentWeather>> getWeatherByLocation(String location) async {
    return get(
      '${getEndpoint('current') ?? '/api/v1/weather/current'}/$location',
      parser: (data) => CurrentWeather.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Get weather forecast
  /// الحصول على توقعات الطقس
  Future<ApiResult<List<ForecastDay>>> getForecast({
    double? latitude,
    double? longitude,
    String? location,
    int days = 7,
  }) async {
    final queryParams = <String, dynamic>{
      if (latitude != null) 'lat': latitude,
      if (longitude != null) 'lng': longitude,
      if (location != null) 'location': location,
      'days': days,
    };

    return get(
      getEndpoint('forecast') ?? '/api/v1/weather/forecast',
      queryParameters: queryParams,
      parser: (data) {
        if (data is List) {
          return data.map((e) => ForecastDay.fromJson(e as Map<String, dynamic>)).toList();
        }
        if (data is Map && data['forecast'] != null) {
          return (data['forecast'] as List)
              .map((e) => ForecastDay.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <ForecastDay>[];
      },
    );
  }

  /// Get weather forecast for field
  /// الحصول على توقعات الطقس للحقل
  Future<ApiResult<List<ForecastDay>>> getForecastByField(String fieldId, {int days = 7}) async {
    return get(
      '${getEndpoint('forecast') ?? '/api/v1/weather/forecast'}/field/$fieldId',
      queryParameters: {'days': days},
      parser: (data) {
        if (data is List) {
          return data.map((e) => ForecastDay.fromJson(e as Map<String, dynamic>)).toList();
        }
        if (data is Map && data['forecast'] != null) {
          return (data['forecast'] as List)
              .map((e) => ForecastDay.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <ForecastDay>[];
      },
    );
  }

  /// Get weather alerts
  /// الحصول على تنبيهات الطقس
  Future<ApiResult<List<WeatherAlert>>> getAlerts({
    double? latitude,
    double? longitude,
    String? location,
  }) async {
    final queryParams = <String, dynamic>{
      if (latitude != null) 'lat': latitude,
      if (longitude != null) 'lng': longitude,
      if (location != null) 'location': location,
    };

    return get(
      getEndpoint('alerts') ?? '/api/v1/weather/alerts',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
      parser: (data) {
        if (data is List) {
          return data.map((e) => WeatherAlert.fromJson(e as Map<String, dynamic>)).toList();
        }
        if (data is Map && data['alerts'] != null) {
          return (data['alerts'] as List)
              .map((e) => WeatherAlert.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <WeatherAlert>[];
      },
    );
  }

  /// Get weather alerts for field
  /// الحصول على تنبيهات الطقس للحقل
  Future<ApiResult<List<WeatherAlert>>> getAlertsByField(String fieldId) async {
    return get(
      '${getEndpoint('alerts') ?? '/api/v1/weather/alerts'}/field/$fieldId',
      parser: (data) {
        if (data is List) {
          return data.map((e) => WeatherAlert.fromJson(e as Map<String, dynamic>)).toList();
        }
        return <WeatherAlert>[];
      },
    );
  }

  /// Get agricultural calendar
  /// الحصول على التقويم الزراعي
  Future<ApiResult<List<AgriculturalEvent>>> getAgriculturalCalendar({
    String? cropType,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final queryParams = <String, dynamic>{
      if (cropType != null) 'crop_type': cropType,
      if (startDate != null) 'start_date': startDate.toIso8601String(),
      if (endDate != null) 'end_date': endDate.toIso8601String(),
    };

    return get(
      getEndpoint('agricultural-calendar') ?? '/api/v1/weather/agricultural-calendar',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
      parser: (data) {
        if (data is List) {
          return data.map((e) => AgriculturalEvent.fromJson(e as Map<String, dynamic>)).toList();
        }
        if (data is Map && data['events'] != null) {
          return (data['events'] as List)
              .map((e) => AgriculturalEvent.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <AgriculturalEvent>[];
      },
    );
  }

  /// Get available locations
  /// الحصول على المواقع المتاحة
  Future<ApiResult<List<String>>> getLocations() async {
    return get(
      getEndpoint('locations') ?? '/api/v1/weather/locations',
      parser: (data) {
        if (data is List) {
          return data.cast<String>();
        }
        if (data is Map && data['locations'] != null) {
          return (data['locations'] as List).cast<String>();
        }
        return <String>[];
      },
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Weather Service Provider
final weatherServiceProvider = Provider<WeatherServiceConnector>((ref) {
  return WeatherServiceConnector(ref: ref);
});

/// Current Weather Provider (by coordinates)
final currentWeatherProvider = FutureProvider.family<CurrentWeather?, ({double lat, double lng})>(
  (ref, coords) async {
    final service = ref.watch(weatherServiceProvider);
    final result = await service.getCurrentWeather(
      latitude: coords.lat,
      longitude: coords.lng,
    );
    return result.dataOrNull;
  },
);

/// Weather Forecast Provider
final weatherForecastProvider = FutureProvider.family<List<ForecastDay>, String?>(
  (ref, fieldId) async {
    final service = ref.watch(weatherServiceProvider);
    if (fieldId != null) {
      final result = await service.getForecastByField(fieldId);
      return result.dataOrNull ?? [];
    }
    final result = await service.getForecast();
    return result.dataOrNull ?? [];
  },
);

/// Weather Alerts Provider
final weatherAlertsProvider = FutureProvider.family<List<WeatherAlert>, String?>(
  (ref, fieldId) async {
    final service = ref.watch(weatherServiceProvider);
    if (fieldId != null) {
      final result = await service.getAlertsByField(fieldId);
      return result.dataOrNull ?? [];
    }
    final result = await service.getAlerts();
    return result.dataOrNull ?? [];
  },
);

/// Active Weather Alerts Provider
final activeWeatherAlertsProvider = FutureProvider<List<WeatherAlert>>((ref) async {
  final service = ref.watch(weatherServiceProvider);
  final result = await service.getAlerts();
  return (result.dataOrNull ?? []).where((a) => a.isActive).toList();
});

/// Agricultural Calendar Provider
final agriculturalCalendarProvider = FutureProvider.family<List<AgriculturalEvent>, String?>(
  (ref, cropType) async {
    final service = ref.watch(weatherServiceProvider);
    final result = await service.getAgriculturalCalendar(cropType: cropType);
    return result.dataOrNull ?? [];
  },
);
