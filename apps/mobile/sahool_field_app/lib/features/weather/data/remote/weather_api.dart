/// Weather API Client - Integrated with Weather Service (port 8092)
/// عميل API الطقس - متكامل مع خدمة الطقس
library;

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../../core/config/api_config.dart';
import '../../domain/entities/weather_entities.dart';

/// Weather API Client
/// عميل API الطقس
class WeatherApi {
  final http.Client _client;
  final String? _authToken;

  WeatherApi({
    http.Client? client,
    String? authToken,
  })  : _client = client ?? http.Client(),
        _authToken = authToken;

  Map<String, String> get _headers => {
        ...ApiConfig.defaultHeaders,
        if (_authToken != null) 'Authorization': 'Bearer $_authToken',
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Current Weather
  // الطقس الحالي
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get current weather for a location (governorate name)
  /// جلب الطقس الحالي لموقع (اسم المحافظة)
  Future<WeatherData> getCurrentWeather(String location) async {
    final response = await _client.get(
      Uri.parse(ApiConfig.weatherByLocation(location)),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return WeatherData.fromJson(json);
    } else {
      throw WeatherApiException(
        'فشل جلب بيانات الطقس الحالي',
        statusCode: response.statusCode,
      );
    }
  }

  /// Get current weather by coordinates
  /// جلب الطقس الحالي بالإحداثيات
  Future<WeatherData> getWeatherByCoordinates(double lat, double lon) async {
    final uri = Uri.parse(ApiConfig.weather).replace(
      queryParameters: {
        'lat': lat.toString(),
        'lon': lon.toString(),
      },
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return WeatherData.fromJson(json);
    } else {
      throw WeatherApiException(
        'فشل جلب بيانات الطقس',
        statusCode: response.statusCode,
      );
    }
  }

  /// Get weather for a field (uses field's location)
  /// جلب الطقس للحقل
  Future<WeatherData> getFieldWeather(String fieldId) async {
    // For field weather, we fetch by field's governorate or coordinates
    // This would typically lookup the field first, then get weather
    final uri = Uri.parse(ApiConfig.weather).replace(
      queryParameters: {'field_id': fieldId},
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return WeatherData.fromJson(json);
    } else {
      throw WeatherApiException(
        'فشل جلب بيانات الطقس للحقل',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Forecasts
  // التوقعات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get 7-day forecast for a location
  /// جلب توقعات 7 أيام لموقع
  Future<List<DailyForecast>> getForecast(String location, {int days = 7}) async {
    final uri = Uri.parse(ApiConfig.forecastByLocation(location)).replace(
      queryParameters: {'days': days.toString()},
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> forecasts = data['forecasts'] ?? data;
      return forecasts.map((d) => DailyForecast.fromJson(d)).toList();
    } else {
      throw WeatherApiException(
        'فشل جلب التوقعات',
        statusCode: response.statusCode,
      );
    }
  }

  /// Get hourly forecast (from daily forecast details)
  /// جلب التوقعات الساعية
  Future<List<HourlyForecast>> getHourlyForecast(
    String location, {
    int hours = 24,
  }) async {
    final uri = Uri.parse(ApiConfig.forecastByLocation(location)).replace(
      queryParameters: {
        'hourly': 'true',
        'hours': hours.toString(),
      },
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> hourly = data['hourly'] ?? [];
      return hourly.map((h) => HourlyForecast.fromJson(h)).toList();
    } else {
      throw WeatherApiException(
        'فشل جلب التوقعات الساعية',
        statusCode: response.statusCode,
      );
    }
  }

  /// Get daily forecast for a field
  /// جلب التوقعات اليومية للحقل
  Future<List<DailyForecast>> getDailyForecast(
    String fieldId, {
    int days = 7,
  }) async {
    // Use field's location for forecast
    final uri = Uri.parse(ApiConfig.forecast).replace(
      queryParameters: {
        'field_id': fieldId,
        'days': days.toString(),
      },
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> forecasts = data['forecasts'] ?? data;
      return forecasts.map((d) => DailyForecast.fromJson(d)).toList();
    } else {
      throw WeatherApiException(
        'فشل جلب التوقعات اليومية',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Alerts
  // التنبيهات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get weather alerts for a location
  /// جلب تنبيهات الطقس لموقع
  Future<List<WeatherAlert>> getAlerts(String location) async {
    final response = await _client.get(
      Uri.parse(ApiConfig.weatherAlertsByLocation(location)),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> alerts = data['alerts'] ?? data;
      return alerts.map((a) => WeatherAlert.fromJson(a)).toList();
    } else {
      throw WeatherApiException(
        'فشل جلب تنبيهات الطقس',
        statusCode: response.statusCode,
      );
    }
  }

  /// Get weather alerts for a field
  /// جلب تنبيهات الطقس للحقل
  Future<List<WeatherAlert>> getWeatherAlerts(String fieldId) async {
    final uri = Uri.parse(ApiConfig.weatherAlerts).replace(
      queryParameters: {'field_id': fieldId},
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> alerts = data['alerts'] ?? data;
      return alerts.map((a) => WeatherAlert.fromJson(a)).toList();
    } else {
      throw WeatherApiException(
        'فشل جلب تنبيهات الطقس',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Agricultural Impact
  // التأثيرات الزراعية
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get agricultural calendar for planning
  /// جلب التقويم الزراعي للتخطيط
  Future<List<AgriculturalImpact>> getAgriculturalCalendar({
    String? location,
    String? cropType,
  }) async {
    final queryParams = <String, String>{};
    if (location != null) queryParams['location'] = location;
    if (cropType != null) queryParams['crop'] = cropType;

    final uri = Uri.parse(ApiConfig.agriculturalCalendar).replace(
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> impacts = data['impacts'] ?? data;
      return impacts.map((i) => AgriculturalImpact.fromJson(i)).toList();
    } else {
      throw WeatherApiException(
        'فشل جلب التقويم الزراعي',
        statusCode: response.statusCode,
      );
    }
  }

  /// Get agricultural impacts for a field
  /// جلب التأثيرات الزراعية للحقل
  Future<List<AgriculturalImpact>> getAgriculturalImpacts(String fieldId) async {
    final uri = Uri.parse(ApiConfig.agriculturalCalendar).replace(
      queryParameters: {'field_id': fieldId},
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> impacts = data['impacts'] ?? data;
      return impacts.map((i) => AgriculturalImpact.fromJson(i)).toList();
    } else {
      throw WeatherApiException(
        'فشل جلب التأثيرات الزراعية',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Locations
  // المواقع
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get available Yemen locations (governorates)
  /// جلب المحافظات اليمنية المتاحة
  Future<List<WeatherLocation>> getAvailableLocations() async {
    final response = await _client.get(
      Uri.parse(ApiConfig.weatherLocations),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> locations = data['locations'] ?? data;
      return locations.map((l) => WeatherLocation.fromJson(l)).toList();
    } else {
      throw WeatherApiException(
        'فشل جلب المواقع',
        statusCode: response.statusCode,
      );
    }
  }

  void dispose() {
    _client.close();
  }
}

/// Weather location model
/// نموذج موقع الطقس
class WeatherLocation {
  final String id;
  final String name;
  final String nameAr;
  final double latitude;
  final double longitude;
  final String region; // highland, coastal, desert
  final String regionAr;

  WeatherLocation({
    required this.id,
    required this.name,
    required this.nameAr,
    required this.latitude,
    required this.longitude,
    required this.region,
    required this.regionAr,
  });

  factory WeatherLocation.fromJson(Map<String, dynamic> json) {
    return WeatherLocation(
      id: json['id'] ?? json['location_id'] ?? '',
      name: json['name'] ?? '',
      nameAr: json['name_ar'] ?? json['nameAr'] ?? '',
      latitude: (json['latitude'] ?? json['lat'] ?? 0).toDouble(),
      longitude: (json['longitude'] ?? json['lon'] ?? 0).toDouble(),
      region: json['region'] ?? '',
      regionAr: json['region_ar'] ?? json['regionAr'] ?? '',
    );
  }
}

/// Weather API Exception
/// استثناء API الطقس
class WeatherApiException implements Exception {
  final String message;
  final int? statusCode;

  WeatherApiException(this.message, {this.statusCode});

  @override
  String toString() => 'WeatherApiException: $message (code: $statusCode)';
}
