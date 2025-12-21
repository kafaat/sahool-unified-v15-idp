import 'package:dio/dio.dart';
import '../../../core/http/api_client.dart';
import '../../../core/config/api_config.dart';

/// NDVI/Satellite Service API Integration
/// تكامل خدمة صور الأقمار الصناعية ومؤشر NDVI
///
/// Port: 8090
/// Features: Field imagery, NDVI analysis, time-series data
class SatelliteApi {
  final Dio _dio;
  final String _baseUrl;

  SatelliteApi({Dio? dio, String? baseUrl})
      : _dio = dio ?? Dio(),
        _baseUrl = baseUrl ?? '${ApiConfig.baseUrl}:8090';

  // ─────────────────────────────────────────────────────────────────────────
  // Field Imagery - صور الحقول
  // ─────────────────────────────────────────────────────────────────────────

  /// Get latest satellite image for field
  /// جلب أحدث صورة قمر صناعي للحقل
  Future<ApiResult<FieldImagery>> getLatestImagery(String fieldId) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/fields/$fieldId/imagery/latest',
      );
      return ApiResult.success(FieldImagery.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Get imagery history for field
  /// جلب سجل الصور للحقل
  Future<ApiResult<List<FieldImagery>>> getImageryHistory({
    required String fieldId,
    DateTime? startDate,
    DateTime? endDate,
    int? limit,
  }) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/fields/$fieldId/imagery',
        queryParameters: {
          if (startDate != null) 'start_date': startDate.toIso8601String(),
          if (endDate != null) 'end_date': endDate.toIso8601String(),
          if (limit != null) 'limit': limit,
        },
      );
      final List<dynamic> data = response.data['data'] ?? response.data;
      return ApiResult.success(
        data.map((e) => FieldImagery.fromJson(e)).toList(),
      );
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Get satellite image tiles URL
  /// جلب رابط بلاطات الصور
  String getTileUrl({
    required String fieldId,
    required String imageType, // 'rgb', 'ndvi', 'false_color'
    required String date,
  }) {
    return '$_baseUrl/tiles/$fieldId/{z}/{x}/{y}.png?type=$imageType&date=$date';
  }

  // ─────────────────────────────────────────────────────────────────────────
  // NDVI Analysis - تحليل NDVI
  // ─────────────────────────────────────────────────────────────────────────

  /// Get current NDVI value for field
  /// جلب قيمة NDVI الحالية للحقل
  Future<ApiResult<NdviData>> getCurrentNdvi(String fieldId) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/fields/$fieldId/ndvi/current',
      );
      return ApiResult.success(NdviData.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Get NDVI time series
  /// جلب سلسلة NDVI الزمنية
  Future<ApiResult<List<NdviData>>> getNdviTimeSeries({
    required String fieldId,
    DateTime? startDate,
    DateTime? endDate,
    String interval = 'daily', // daily, weekly, monthly
  }) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/fields/$fieldId/ndvi/timeseries',
        queryParameters: {
          if (startDate != null) 'start_date': startDate.toIso8601String(),
          if (endDate != null) 'end_date': endDate.toIso8601String(),
          'interval': interval,
        },
      );
      final List<dynamic> data = response.data['data'] ?? response.data;
      return ApiResult.success(
        data.map((e) => NdviData.fromJson(e)).toList(),
      );
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Get NDVI statistics for field
  /// جلب إحصائيات NDVI للحقل
  Future<ApiResult<NdviStatistics>> getNdviStatistics({
    required String fieldId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/fields/$fieldId/ndvi/statistics',
        queryParameters: {
          if (startDate != null) 'start_date': startDate.toIso8601String(),
          if (endDate != null) 'end_date': endDate.toIso8601String(),
        },
      );
      return ApiResult.success(NdviStatistics.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Get NDVI zones (anomaly detection)
  /// جلب مناطق NDVI (اكتشاف الشذوذ)
  Future<ApiResult<List<NdviZone>>> getNdviZones(String fieldId) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/fields/$fieldId/ndvi/zones',
      );
      final List<dynamic> data = response.data['zones'] ?? response.data;
      return ApiResult.success(
        data.map((e) => NdviZone.fromJson(e)).toList(),
      );
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Comparison & Analysis - المقارنة والتحليل
  // ─────────────────────────────────────────────────────────────────────────

  /// Compare NDVI between two dates
  /// مقارنة NDVI بين تاريخين
  Future<ApiResult<NdviComparison>> compareNdvi({
    required String fieldId,
    required DateTime date1,
    required DateTime date2,
  }) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/fields/$fieldId/ndvi/compare',
        queryParameters: {
          'date1': date1.toIso8601String(),
          'date2': date2.toIso8601String(),
        },
      );
      return ApiResult.success(NdviComparison.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Get crop health analysis from satellite
  /// جلب تحليل صحة المحصول من الأقمار الصناعية
  Future<ApiResult<CropHealthAnalysis>> getCropHealthAnalysis(
    String fieldId,
  ) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/fields/$fieldId/analysis/health',
      );
      return ApiResult.success(CropHealthAnalysis.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Request new satellite acquisition
  /// طلب التقاط صورة جديدة
  Future<ApiResult<AcquisitionRequest>> requestAcquisition({
    required String fieldId,
    String? priority, // 'normal', 'high', 'urgent'
    String? imageType,
  }) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/fields/$fieldId/acquisition/request',
        data: {
          if (priority != null) 'priority': priority,
          if (imageType != null) 'image_type': imageType,
        },
      );
      return ApiResult.success(AcquisitionRequest.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Error Handling
  // ─────────────────────────────────────────────────────────────────────────

  String _handleError(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.receiveTimeout:
        return 'انتهت مهلة الاتصال بخدمة الأقمار الصناعية';
      case DioExceptionType.connectionError:
        return 'لا يمكن الاتصال بخدمة الأقمار الصناعية';
      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode ?? 0;
        if (statusCode == 404) {
          return 'لم يتم العثور على بيانات للحقل المطلوب';
        } else if (statusCode == 503) {
          return 'خدمة الأقمار الصناعية غير متاحة حالياً';
        }
        return 'خطأ في الخادم: $statusCode';
      default:
        return 'حدث خطأ غير متوقع';
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Data Models - نماذج البيانات
// ─────────────────────────────────────────────────────────────────────────────

/// API Result wrapper
class ApiResult<T> {
  final T? data;
  final String? error;
  final bool isSuccess;

  ApiResult._({this.data, this.error, required this.isSuccess});

  factory ApiResult.success(T data) =>
      ApiResult._(data: data, isSuccess: true);

  factory ApiResult.failure(String error) =>
      ApiResult._(error: error, isSuccess: false);
}

/// Field satellite imagery
class FieldImagery {
  final String id;
  final String fieldId;
  final String imageType; // rgb, ndvi, false_color
  final String tileUrl;
  final String? thumbnailUrl;
  final DateTime acquisitionDate;
  final double cloudCover;
  final String satellite; // sentinel-2, landsat-8, planet
  final double resolution; // meters per pixel

  FieldImagery({
    required this.id,
    required this.fieldId,
    required this.imageType,
    required this.tileUrl,
    this.thumbnailUrl,
    required this.acquisitionDate,
    required this.cloudCover,
    required this.satellite,
    required this.resolution,
  });

  factory FieldImagery.fromJson(Map<String, dynamic> json) {
    return FieldImagery(
      id: json['id'] ?? '',
      fieldId: json['field_id'] ?? '',
      imageType: json['image_type'] ?? 'rgb',
      tileUrl: json['tile_url'] ?? '',
      thumbnailUrl: json['thumbnail_url'],
      acquisitionDate: DateTime.parse(
        json['acquisition_date'] ?? DateTime.now().toIso8601String(),
      ),
      cloudCover: (json['cloud_cover'] ?? 0).toDouble(),
      satellite: json['satellite'] ?? 'sentinel-2',
      resolution: (json['resolution'] ?? 10).toDouble(),
    );
  }
}

/// NDVI data point
class NdviData {
  final String fieldId;
  final DateTime date;
  final double value; // -1 to 1
  final double min;
  final double max;
  final double mean;
  final double stdDev;
  final String healthStatus; // excellent, good, moderate, poor, critical

  NdviData({
    required this.fieldId,
    required this.date,
    required this.value,
    required this.min,
    required this.max,
    required this.mean,
    required this.stdDev,
    required this.healthStatus,
  });

  factory NdviData.fromJson(Map<String, dynamic> json) {
    return NdviData(
      fieldId: json['field_id'] ?? '',
      date: DateTime.parse(json['date'] ?? DateTime.now().toIso8601String()),
      value: (json['value'] ?? 0).toDouble(),
      min: (json['min'] ?? 0).toDouble(),
      max: (json['max'] ?? 0).toDouble(),
      mean: (json['mean'] ?? json['value'] ?? 0).toDouble(),
      stdDev: (json['std_dev'] ?? 0).toDouble(),
      healthStatus: json['health_status'] ?? 'unknown',
    );
  }

  /// Get health status in Arabic
  String get healthStatusAr {
    switch (healthStatus) {
      case 'excellent':
        return 'ممتاز';
      case 'good':
        return 'جيد';
      case 'moderate':
        return 'متوسط';
      case 'poor':
        return 'ضعيف';
      case 'critical':
        return 'حرج';
      default:
        return 'غير معروف';
    }
  }
}

/// NDVI statistics
class NdviStatistics {
  final String fieldId;
  final DateTime startDate;
  final DateTime endDate;
  final double average;
  final double min;
  final double max;
  final double trend; // positive = improving, negative = declining
  final String trendDirection;
  final int dataPoints;

  NdviStatistics({
    required this.fieldId,
    required this.startDate,
    required this.endDate,
    required this.average,
    required this.min,
    required this.max,
    required this.trend,
    required this.trendDirection,
    required this.dataPoints,
  });

  factory NdviStatistics.fromJson(Map<String, dynamic> json) {
    return NdviStatistics(
      fieldId: json['field_id'] ?? '',
      startDate: DateTime.parse(json['start_date'] ?? DateTime.now().toIso8601String()),
      endDate: DateTime.parse(json['end_date'] ?? DateTime.now().toIso8601String()),
      average: (json['average'] ?? 0).toDouble(),
      min: (json['min'] ?? 0).toDouble(),
      max: (json['max'] ?? 0).toDouble(),
      trend: (json['trend'] ?? 0).toDouble(),
      trendDirection: json['trend_direction'] ?? 'stable',
      dataPoints: json['data_points'] ?? 0,
    );
  }
}

/// NDVI zone (for anomaly detection)
class NdviZone {
  final String id;
  final String type; // low, normal, high
  final double ndviValue;
  final double areaHectares;
  final double percentOfField;
  final List<List<double>> coordinates; // GeoJSON coordinates
  final String recommendation;

  NdviZone({
    required this.id,
    required this.type,
    required this.ndviValue,
    required this.areaHectares,
    required this.percentOfField,
    required this.coordinates,
    required this.recommendation,
  });

  factory NdviZone.fromJson(Map<String, dynamic> json) {
    return NdviZone(
      id: json['id'] ?? '',
      type: json['type'] ?? 'normal',
      ndviValue: (json['ndvi_value'] ?? 0).toDouble(),
      areaHectares: (json['area_hectares'] ?? 0).toDouble(),
      percentOfField: (json['percent_of_field'] ?? 0).toDouble(),
      coordinates: (json['coordinates'] as List<dynamic>?)
              ?.map((e) => (e as List<dynamic>).map((c) => (c as num).toDouble()).toList())
              .toList() ??
          [],
      recommendation: json['recommendation'] ?? '',
    );
  }
}

/// NDVI comparison result
class NdviComparison {
  final DateTime date1;
  final DateTime date2;
  final double ndvi1;
  final double ndvi2;
  final double change;
  final double changePercent;
  final String trend;
  final String analysis;

  NdviComparison({
    required this.date1,
    required this.date2,
    required this.ndvi1,
    required this.ndvi2,
    required this.change,
    required this.changePercent,
    required this.trend,
    required this.analysis,
  });

  factory NdviComparison.fromJson(Map<String, dynamic> json) {
    return NdviComparison(
      date1: DateTime.parse(json['date1'] ?? DateTime.now().toIso8601String()),
      date2: DateTime.parse(json['date2'] ?? DateTime.now().toIso8601String()),
      ndvi1: (json['ndvi1'] ?? 0).toDouble(),
      ndvi2: (json['ndvi2'] ?? 0).toDouble(),
      change: (json['change'] ?? 0).toDouble(),
      changePercent: (json['change_percent'] ?? 0).toDouble(),
      trend: json['trend'] ?? 'stable',
      analysis: json['analysis'] ?? '',
    );
  }
}

/// Crop health analysis from satellite
class CropHealthAnalysis {
  final String fieldId;
  final DateTime analysisDate;
  final double overallHealth; // 0-100
  final String healthGrade; // A, B, C, D, F
  final List<String> issues;
  final List<String> recommendations;
  final Map<String, double> zoneHealth;

  CropHealthAnalysis({
    required this.fieldId,
    required this.analysisDate,
    required this.overallHealth,
    required this.healthGrade,
    required this.issues,
    required this.recommendations,
    required this.zoneHealth,
  });

  factory CropHealthAnalysis.fromJson(Map<String, dynamic> json) {
    return CropHealthAnalysis(
      fieldId: json['field_id'] ?? '',
      analysisDate: DateTime.parse(json['analysis_date'] ?? DateTime.now().toIso8601String()),
      overallHealth: (json['overall_health'] ?? 0).toDouble(),
      healthGrade: json['health_grade'] ?? 'C',
      issues: List<String>.from(json['issues'] ?? []),
      recommendations: List<String>.from(json['recommendations'] ?? []),
      zoneHealth: Map<String, double>.from(
        (json['zone_health'] ?? {}).map(
          (k, v) => MapEntry(k.toString(), (v as num).toDouble()),
        ),
      ),
    );
  }
}

/// Satellite acquisition request
class AcquisitionRequest {
  final String id;
  final String fieldId;
  final String status; // pending, scheduled, completed, failed
  final DateTime requestedAt;
  final DateTime? scheduledFor;
  final String priority;

  AcquisitionRequest({
    required this.id,
    required this.fieldId,
    required this.status,
    required this.requestedAt,
    this.scheduledFor,
    required this.priority,
  });

  factory AcquisitionRequest.fromJson(Map<String, dynamic> json) {
    return AcquisitionRequest(
      id: json['id'] ?? '',
      fieldId: json['field_id'] ?? '',
      status: json['status'] ?? 'pending',
      requestedAt: DateTime.parse(json['requested_at'] ?? DateTime.now().toIso8601String()),
      scheduledFor: json['scheduled_for'] != null
          ? DateTime.parse(json['scheduled_for'])
          : null,
      priority: json['priority'] ?? 'normal',
    );
  }
}
