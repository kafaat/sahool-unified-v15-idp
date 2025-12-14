import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../domain/entities/weather_entities.dart';

/// Weather API Client
/// عميل API الطقس
class WeatherApi {
  final String baseUrl;
  final http.Client _client;

  WeatherApi({
    required this.baseUrl,
    http.Client? client,
  }) : _client = client ?? http.Client();

  /// جلب بيانات الطقس للحقل
  Future<WeatherData> getFieldWeather(String fieldId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/weather/field/$fieldId'),
      headers: {'Content-Type': 'application/json'},
    );

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

  /// جلب بيانات الطقس بالموقع
  Future<WeatherData> getWeatherByLocation(double lat, double lon) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/weather/location?lat=$lat&lon=$lon'),
      headers: {'Content-Type': 'application/json'},
    );

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

  /// جلب التوقعات الساعية
  Future<List<HourlyForecast>> getHourlyForecast(
    String fieldId, {
    int hours = 24,
  }) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/weather/field/$fieldId/hourly?hours=$hours'),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      final List<dynamic> json = jsonDecode(response.body);
      return json.map((h) => HourlyForecast.fromJson(h)).toList();
    } else {
      throw WeatherApiException(
        'فشل جلب التوقعات الساعية',
        statusCode: response.statusCode,
      );
    }
  }

  /// جلب التوقعات اليومية
  Future<List<DailyForecast>> getDailyForecast(
    String fieldId, {
    int days = 7,
  }) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/weather/field/$fieldId/daily?days=$days'),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      final List<dynamic> json = jsonDecode(response.body);
      return json.map((d) => DailyForecast.fromJson(d)).toList();
    } else {
      throw WeatherApiException(
        'فشل جلب التوقعات اليومية',
        statusCode: response.statusCode,
      );
    }
  }

  /// جلب تنبيهات الطقس
  Future<List<WeatherAlert>> getWeatherAlerts(String fieldId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/weather/field/$fieldId/alerts'),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      final List<dynamic> json = jsonDecode(response.body);
      return json.map((a) => WeatherAlert.fromJson(a)).toList();
    } else {
      throw WeatherApiException(
        'فشل جلب تنبيهات الطقس',
        statusCode: response.statusCode,
      );
    }
  }

  /// جلب التأثيرات الزراعية
  Future<List<AgriculturalImpact>> getAgriculturalImpacts(
    String fieldId,
  ) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/weather/field/$fieldId/impacts'),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      final List<dynamic> json = jsonDecode(response.body);
      return json.map((i) => AgriculturalImpact.fromJson(i)).toList();
    } else {
      throw WeatherApiException(
        'فشل جلب التأثيرات الزراعية',
        statusCode: response.statusCode,
      );
    }
  }

  void dispose() {
    _client.close();
  }
}

/// استثناء API الطقس
class WeatherApiException implements Exception {
  final String message;
  final int? statusCode;

  WeatherApiException(this.message, {this.statusCode});

  @override
  String toString() => 'WeatherApiException: $message (code: $statusCode)';
}
