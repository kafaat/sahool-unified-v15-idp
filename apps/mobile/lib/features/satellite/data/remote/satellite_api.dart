/// Satellite API Client - عميل API الأقمار الصناعية
/// Integrated with Satellite Service (port 8090)
library;

import 'dart:convert';
import 'dart:developer' as developer;
import 'package:http/http.dart' as http;
import '../../../../core/config/api_config.dart';
import '../models/ndvi_data.dart';
import '../models/field_health.dart';
import '../models/weather_data.dart';
import '../models/phenology_data.dart';
import '../models/index_filmstrip.dart';

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
      try {
        final json = jsonDecode(response.body) as Map<String, dynamic>;
        return NdviAnalysis.fromJson(json);
      } catch (e) {
        throw SatelliteApiException(
          'فشل تحليل استجابة NDVI: $e',
          statusCode: response.statusCode,
        );
      }
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
      final decoded = jsonDecode(response.body);
      final List<dynamic> timeSeries;
      if (decoded is List) {
        timeSeries = decoded;
      } else if (decoded is Map<String, dynamic>) {
        timeSeries = (decoded['time_series'] ?? decoded['timeseries'] ?? []) as List<dynamic>;
      } else {
        timeSeries = [];
      }
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
      final decoded = jsonDecode(response.body);
      final Map<String, dynamic> indicesData;
      if (decoded is Map<String, dynamic>) {
        indicesData = (decoded['indices'] as Map<String, dynamic>?) ?? decoded;
      } else {
        indicesData = {};
      }
      return indicesData.map(
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
      final json = jsonDecode(response.body) as Map<String, dynamic>;
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
      final json = jsonDecode(response.body) as Map<String, dynamic>;
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
      final decoded = jsonDecode(response.body);
      final List<dynamic> alerts;
      if (decoded is List) {
        alerts = decoded;
      } else if (decoded is Map<String, dynamic>) {
        alerts = (decoded['alerts'] ?? []) as List<dynamic>;
      } else {
        alerts = [];
      }
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
      final json = jsonDecode(response.body) as Map<String, dynamic>;
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
      final json = jsonDecode(response.body) as Map<String, dynamic>;
      return (json['image_url'] ?? json['imageUrl'] ?? '') as String;
    } else {
      throw SatelliteApiException(
        'فشل جلب صورة القمر الصناعي',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Phase-1 / Phase-2 map + pixel endpoints
  // نقاط نهاية الخريطة وفحص البكسل
  // ═══════════════════════════════════════════════════════════════════════════

  /// Safely compose a satellite-service URL from un-trusted path
  /// segments. Encodes each segment with [Uri.encodeComponent] so that
  /// characters like `/`, `%`, or `?` in a fieldId / indexName can't
  /// break out of the path and change which endpoint is hit
  /// (Copilot review #1704, feedback round 2).
  Uri _buildIndicesUri(List<String> segments, {Map<String, String>? query}) {
    final base = Uri.parse(ApiConfig.satelliteServiceUrl);
    return base.replace(
      pathSegments: [
        ...base.pathSegments.where((s) => s.isNotEmpty),
        'v1',
        'indices',
        ...segments,
      ],
      queryParameters: query,
    );
  }

  /// Get raster-tile metadata for a mappable vegetation index.
  /// جلب بيانات الطبقة النقطية لمؤشر قابل للعرض
  ///
  /// `indexName` must be one of: ndvi | ndre | ndwi | evi | savi | lai.
  /// Backend rejects anything else with 400.
  Future<IndexMapData> getIndexMap(
    String fieldId, {
    required String indexName,
    DateTime? date,
  }) async {
    final uri = _buildIndicesUri(
      [fieldId, indexName, 'map'],
      query: {
        if (date != null) 'date': date.toIso8601String().substring(0, 10),
      },
    );
    final response = await _client.get(uri, headers: _headers);
    if (response.statusCode != 200) {
      throw SatelliteApiException(
        'فشل جلب الطبقة النقطية | Failed to load index map',
        statusCode: response.statusCode,
      );
    }
    return IndexMapData.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  /// Click-to-inspect: every computed index at (lat, lon) for the field.
  /// فحص البكسل: جميع المؤشرات عند نقطة
  ///
  /// Defaults to all 44 indices; pass [indices] to trim the server
  /// payload to a subset.
  Future<PixelInspection> getPixelInspection(
    String fieldId, {
    required double lat,
    required double lon,
    DateTime? date,
    List<String>? indices,
  }) async {
    final uri = _buildIndicesUri(
      [fieldId, 'pixel'],
      query: {
        'lat': lat.toString(),
        'lon': lon.toString(),
        if (date != null) 'date': date.toIso8601String().substring(0, 10),
        if (indices != null && indices.isNotEmpty) 'indices': indices.join(','),
      },
    );
    final response = await _client.get(uri, headers: _headers);
    if (response.statusCode != 200) {
      throw SatelliteApiException(
        'فشل فحص البكسل | Pixel inspection failed',
        statusCode: response.statusCode,
      );
    }
    return PixelInspection.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Phase-3 multi-date endpoints
  // نقاط نهاية متعددة التواريخ (المرحلة ٣)
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get filmstrip (per-date thumbnail metadata) for a mappable index.
  /// جلب شريط الصور لمؤشر قابل للعرض على الخريطة
  ///
  /// Supports the 6 mappable indices: ndvi | ndre | ndwi | evi | savi | lai.
  /// The backend caps [stepDays] at 90 and total frames at 20.
  Future<IndexFilmstrip> getIndexFilmstrip(
    String fieldId, {
    required String indexName,
    int stepDays = 7,
    DateTime? start,
    DateTime? end,
  }) async {
    final uri = _buildIndicesUri(
      [fieldId, indexName, 'filmstrip'],
      query: {
        'step_days': stepDays.toString(),
        if (start != null) 'start': start.toIso8601String().substring(0, 10),
        if (end != null) 'end': end.toIso8601String().substring(0, 10),
      },
    );
    final response = await _client.get(uri, headers: _headers);
    if (response.statusCode != 200) {
      throw SatelliteApiException(
        'فشل جلب شريط الصور | Failed to load filmstrip',
        statusCode: response.statusCode,
      );
    }
    return IndexFilmstrip.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  /// Get N-day composite summary (median/mean per window) for a mappable index.
  /// جلب التركيب الزمني لكل N يوم
  Future<IndexComposite> getIndexComposite(
    String fieldId, {
    required String indexName,
    int stepDays = 7,
    DateTime? start,
    DateTime? end,
    String stat = 'median',
  }) async {
    final uri = _buildIndicesUri(
      [fieldId, indexName, 'composite'],
      query: {
        'step_days': stepDays.toString(),
        'stat': stat,
        if (start != null) 'start': start.toIso8601String().substring(0, 10),
        if (end != null) 'end': end.toIso8601String().substring(0, 10),
      },
    );
    final response = await _client.get(uri, headers: _headers);
    if (response.statusCode != 200) {
      throw SatelliteApiException(
        'فشل جلب التركيب الزمني | Failed to load composite',
        statusCode: response.statusCode,
      );
    }
    return IndexComposite.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  /// Compare a mappable index across up to 12 dates.
  /// مقارنة المؤشر عبر حتى ١٢ تاريخاً
  ///
  /// Pass either [dates] (explicit list, 2-12 entries) OR the triple
  /// [start] + [end] + [stepDays]. When both are provided, [dates] wins —
  /// same precedence as the backend validator.
  Future<MultiDateCompare> multiDateCompare(
    String fieldId, {
    required String indexName,
    List<DateTime>? dates,
    DateTime? start,
    DateTime? end,
    int? stepDays,
  }) async {
    final uri = _buildIndicesUri([fieldId, indexName, 'multi-date-compare']);
    final body = <String, dynamic>{};
    if (dates != null && dates.isNotEmpty) {
      body['dates'] = dates.map((d) => d.toIso8601String().substring(0, 10)).toList();
    } else if (start != null && end != null && stepDays != null) {
      body['start'] = start.toIso8601String().substring(0, 10);
      body['end'] = end.toIso8601String().substring(0, 10);
      body['step_days'] = stepDays;
    } else {
      throw ArgumentError(
        'Provide either `dates` or all of `start`, `end`, `stepDays`',
      );
    }
    final response = await _client.post(uri, headers: _headers, body: jsonEncode(body));
    if (response.statusCode != 200) {
      throw SatelliteApiException(
        'فشل المقارنة متعددة التواريخ | Multi-date compare failed',
        statusCode: response.statusCode,
      );
    }
    return MultiDateCompare.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Dashboard Summary
  // ملخص لوحة المعلومات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get complete satellite dashboard data for a field
  /// جلب بيانات لوحة الأقمار الصناعية الكاملة للحقل
  Future<SatelliteDashboardData> getDashboardData(String fieldId) async {
    // Fetch all data in parallel - handle partial failures gracefully
    final results = await Future.wait<dynamic>([
      getFieldHealth(fieldId).catchError((e) {
        developer.log('getFieldHealth failed: $e', name: 'SatelliteApi');
        return null;
      }),
      getNdviAnalysis(fieldId).catchError((e) {
        developer.log('getNdviAnalysis failed: $e', name: 'SatelliteApi');
        return null;
      }),
      getWeatherForecast(fieldId).catchError((e) {
        developer.log('getWeatherForecast failed: $e', name: 'SatelliteApi');
        return null;
      }),
      getPhenologyData(fieldId).catchError((e) {
        developer.log('getPhenologyData failed: $e', name: 'SatelliteApi');
        return null;
      }),
    ]);

    // Require at least field health or NDVI data
    if (results[0] == null && results[1] == null) {
      throw SatelliteApiException(
        'فشل جلب بيانات الحقل الأساسية',
        statusCode: 0,
      );
    }

    return SatelliteDashboardData(
      fieldHealth: results[0] as FieldHealth?,
      ndviAnalysis: results[1] as NdviAnalysis?,
      weatherSummary: results[2] as WeatherSummary?,
      phenologyData: results[3] as PhenologyData?,
    );
  }

  void dispose() {
    _client.close();
  }
}

/// Satellite Dashboard Data
/// بيانات لوحة الأقمار الصناعية
class SatelliteDashboardData {
  final FieldHealth? fieldHealth;
  final NdviAnalysis? ndviAnalysis;
  final WeatherSummary? weatherSummary;
  final PhenologyData? phenologyData;

  SatelliteDashboardData({
    this.fieldHealth,
    this.ndviAnalysis,
    this.weatherSummary,
    this.phenologyData,
  });

  /// Whether essential data is available
  bool get hasEssentialData => fieldHealth != null || ndviAnalysis != null;
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
