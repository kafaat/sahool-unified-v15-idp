/// Satellite API Client - عميل API الأقمار الصناعية
/// Integrated with Satellite Service (port 8090)
library;

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../../core/config/api_config.dart';
import '../models/ndvi_data.dart';
import '../models/field_health.dart';
import '../models/weather_data.dart';
import '../models/phenology_data.dart';

/// Satellite API Client
/// عميل API الأقمار الصناعية
class SatelliteApi {
  final http.Client _client;
  final String? _authToken;

  SatelliteApi({
    http.Client? client,
    String? authToken,
  })  : _client = client ?? http.Client(),
        _authToken = authToken;

  Map<String, String> get _headers => {
        ...ApiConfig.defaultHeaders,
        if (_authToken != null) 'Authorization': 'Bearer $_authToken',
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // NDVI Analysis
  // تحليل NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get NDVI analysis for a field
  /// جلب تحليل NDVI للحقل
  Future<NdviAnalysis> getNdviAnalysis(String fieldId) async {
    final uri = Uri.parse('${ApiConfig.satelliteServiceUrl}/v1/analyze/$fieldId');

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return NdviAnalysis.fromJson(json);
    } else {
      throw SatelliteApiException(
        'فشل جلب تحليل NDVI',
        statusCode: response.statusCode,
      );
    }
  }

  /// Get NDVI time series for a field
  /// جلب سلسلة NDVI الزمنية للحقل
  Future<List<NdviDataPoint>> getNdviTimeSeries(
    String fieldId, {
    int days = 30,
  }) async {
    final uri = Uri.parse('${ApiConfig.satelliteServiceUrl}/v1/timeseries/$fieldId').replace(
      queryParameters: {'days': days.toString()},
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> timeSeries = data['time_series'] ?? data['timeseries'] ?? data;
      return timeSeries.map((item) => NdviDataPoint.fromJson(item as Map<String, dynamic>)).toList();
    } else {
      throw SatelliteApiException(
        'فشل جلب السلسلة الزمنية لـ NDVI',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Vegetation Indices
  // المؤشرات النباتية
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get all vegetation indices for a field
  /// جلب جميع المؤشرات النباتية للحقل
  Future<Map<String, double>> getVegetationIndices(String fieldId) async {
    final uri = Uri.parse('${ApiConfig.satelliteServiceUrl}/v1/indices/$fieldId');

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final indicesData = data['indices'] ?? data;

      return (indicesData as Map<String, dynamic>).map(
        (key, value) => MapEntry(key, (value as num).toDouble()),
      );
    } else {
      throw SatelliteApiException(
        'فشل جلب المؤشرات النباتية',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Field Health
  // صحة الحقل
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get field health assessment
  /// جلب تقييم صحة الحقل
  Future<FieldHealth> getFieldHealth(String fieldId) async {
    final uri = Uri.parse('${ApiConfig.satelliteServiceUrl}/v1/health/$fieldId');

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return FieldHealth.fromJson(json);
    } else {
      throw SatelliteApiException(
        'فشل جلب تقييم صحة الحقل',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Weather Integration
  // تكامل الطقس
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get weather forecast for a field (integrated with weather service)
  /// جلب توقعات الطقس للحقل
  Future<WeatherSummary> getWeatherForecast(String fieldId) async {
    final uri = Uri.parse('${ApiConfig.weatherServiceUrl}/v1/forecast/field/$fieldId');

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return WeatherSummary.fromJson(json);
    } else {
      throw SatelliteApiException(
        'فشل جلب توقعات الطقس',
        statusCode: response.statusCode,
      );
    }
  }

  /// Get weather alerts for a field
  /// جلب تنبيهات الطقس للحقل
  Future<List<WeatherAlertSummary>> getWeatherAlerts(String fieldId) async {
    final uri = Uri.parse('${ApiConfig.weatherServiceUrl}/v1/alerts/field/$fieldId');

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> alerts = data['alerts'] ?? data;
      return alerts.map((item) => WeatherAlertSummary.fromJson(item as Map<String, dynamic>)).toList();
    } else {
      throw SatelliteApiException(
        'فشل جلب تنبيهات الطقس',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Phenology (Crop Growth Stages)
  // مراحل نمو المحصول
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get phenology data for a field
  /// جلب بيانات مراحل النمو للحقل
  Future<PhenologyData> getPhenologyData(String fieldId) async {
    final uri = Uri.parse('${ApiConfig.satelliteServiceUrl}/v1/phenology/$fieldId');

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return PhenologyData.fromJson(json);
    } else {
      throw SatelliteApiException(
        'فشل جلب بيانات مراحل النمو',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Satellite Imagery
  // صور الأقمار الصناعية
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get satellite imagery URL for a field
  /// جلب رابط صورة القمر الصناعي للحقل
  Future<String> getSatelliteImageUrl(
    String fieldId, {
    String type = 'ndvi', // ndvi, rgb, false-color
    DateTime? date,
  }) async {
    final queryParams = <String, String>{
      'type': type,
      if (date != null) 'date': date.toIso8601String(),
    };

    final uri = Uri.parse('${ApiConfig.satelliteServiceUrl}/v1/imagery/$fieldId').replace(
      queryParameters: queryParams,
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return json['image_url'] ?? json['imageUrl'] ?? '';
    } else {
      throw SatelliteApiException(
        'فشل جلب صورة القمر الصناعي',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Dashboard Summary
  // ملخص لوحة المعلومات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get complete satellite dashboard data for a field
  /// جلب بيانات لوحة الأقمار الصناعية الكاملة للحقل
  Future<SatelliteDashboardData> getDashboardData(String fieldId) async {
    // Fetch all data in parallel for better performance
    final results = await Future.wait([
      getFieldHealth(fieldId),
      getNdviAnalysis(fieldId),
      getWeatherForecast(fieldId),
      getPhenologyData(fieldId),
    ]);

    return SatelliteDashboardData(
      fieldHealth: results[0] as FieldHealth,
      ndviAnalysis: results[1] as NdviAnalysis,
      weatherSummary: results[2] as WeatherSummary,
      phenologyData: results[3] as PhenologyData,
    );
  }

  void dispose() {
    _client.close();
  }
}

/// Satellite Dashboard Data
/// بيانات لوحة الأقمار الصناعية
class SatelliteDashboardData {
  final FieldHealth fieldHealth;
  final NdviAnalysis ndviAnalysis;
  final WeatherSummary weatherSummary;
  final PhenologyData phenologyData;

  SatelliteDashboardData({
    required this.fieldHealth,
    required this.ndviAnalysis,
    required this.weatherSummary,
    required this.phenologyData,
  });
}

/// Satellite API Exception
/// استثناء API الأقمار الصناعية
class SatelliteApiException implements Exception {
  final String message;
  final int? statusCode;

  SatelliteApiException(this.message, {this.statusCode});

  @override
  String toString() => 'SatelliteApiException: $message (code: $statusCode)';
}
