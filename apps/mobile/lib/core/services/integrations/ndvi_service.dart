/// SAHOOL NDVI Service Integration
/// تكامل خدمة مؤشر الغطاء النباتي
///
/// Handles vegetation analysis operations:
/// - NDVI analysis
/// - Vegetation indices
/// - Satellite imagery
/// - Field health monitoring
/// - Phenology tracking
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../network/api_result.dart';
import '../service_connector.dart';

/// NDVI analysis result model
class NdviAnalysis {
  final String fieldId;
  final double ndviValue;
  final double? ndviMin;
  final double? ndviMax;
  final double? ndviMean;
  final double? ndviStd;
  final String? healthStatus;
  final String? healthStatusAr;
  final String? recommendation;
  final String? recommendationAr;
  final DateTime analysisDate;
  final String? satelliteSource;
  final int? cloudCoverage;
  final Map<String, dynamic>? zoneAnalysis;
  final Map<String, dynamic>? metadata;

  const NdviAnalysis({
    required this.fieldId,
    required this.ndviValue,
    this.ndviMin,
    this.ndviMax,
    this.ndviMean,
    this.ndviStd,
    this.healthStatus,
    this.healthStatusAr,
    this.recommendation,
    this.recommendationAr,
    required this.analysisDate,
    this.satelliteSource,
    this.cloudCoverage,
    this.zoneAnalysis,
    this.metadata,
  });

  factory NdviAnalysis.fromJson(Map<String, dynamic> json) {
    return NdviAnalysis(
      fieldId: json['field_id'] as String? ?? '',
      ndviValue: (json['ndvi_value'] as num?)?.toDouble() ?? 0.0,
      ndviMin: (json['ndvi_min'] as num?)?.toDouble(),
      ndviMax: (json['ndvi_max'] as num?)?.toDouble(),
      ndviMean: (json['ndvi_mean'] as num?)?.toDouble(),
      ndviStd: (json['ndvi_std'] as num?)?.toDouble(),
      healthStatus: json['health_status'] as String?,
      healthStatusAr: json['health_status_ar'] as String?,
      recommendation: json['recommendation'] as String?,
      recommendationAr: json['recommendation_ar'] as String?,
      analysisDate: json['analysis_date'] != null
          ? DateTime.tryParse(json['analysis_date'] as String) ?? DateTime.now()
          : DateTime.now(),
      satelliteSource: json['satellite_source'] as String?,
      cloudCoverage: (json['cloud_coverage'] as num?)?.toInt(),
      zoneAnalysis: json['zone_analysis'] as Map<String, dynamic>?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  /// Get health status color
  String get healthColor {
    switch (healthStatus?.toLowerCase()) {
      case 'excellent':
        return '#2E7D32';
      case 'good':
        return '#689F38';
      case 'moderate':
        return '#FBC02D';
      case 'poor':
        return '#F57C00';
      case 'critical':
        return '#D32F2F';
      default:
        return '#9E9E9E';
    }
  }
}

/// NDVI timeseries data point
class NdviTimeseriesPoint {
  final DateTime date;
  final double value;
  final String? source;
  final int? cloudCoverage;

  const NdviTimeseriesPoint({
    required this.date,
    required this.value,
    this.source,
    this.cloudCoverage,
  });

  factory NdviTimeseriesPoint.fromJson(Map<String, dynamic> json) {
    return NdviTimeseriesPoint(
      date: DateTime.tryParse(json['date'] as String) ?? DateTime.now(),
      value: (json['value'] as num?)?.toDouble() ?? 0.0,
      source: json['source'] as String?,
      cloudCoverage: (json['cloud_coverage'] as num?)?.toInt(),
    );
  }
}

/// Vegetation index model
class VegetationIndex {
  final String name;
  final String? nameAr;
  final double value;
  final String? description;
  final String? descriptionAr;
  final String? interpretation;
  final String? interpretationAr;
  final double? minValue;
  final double? maxValue;

  const VegetationIndex({
    required this.name,
    this.nameAr,
    required this.value,
    this.description,
    this.descriptionAr,
    this.interpretation,
    this.interpretationAr,
    this.minValue,
    this.maxValue,
  });

  factory VegetationIndex.fromJson(Map<String, dynamic> json) {
    return VegetationIndex(
      name: json['name'] as String? ?? '',
      nameAr: json['name_ar'] as String?,
      value: (json['value'] as num?)?.toDouble() ?? 0.0,
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      interpretation: json['interpretation'] as String?,
      interpretationAr: json['interpretation_ar'] as String?,
      minValue: (json['min_value'] as num?)?.toDouble(),
      maxValue: (json['max_value'] as num?)?.toDouble(),
    );
  }
}

/// Satellite imagery model
class SatelliteImagery {
  final String id;
  final String fieldId;
  final String imageUrl;
  final String? thumbnailUrl;
  final DateTime captureDate;
  final String? satelliteSource;
  final int? cloudCoverage;
  final String? imageType;
  final Map<String, dynamic>? bounds;
  final Map<String, dynamic>? metadata;

  const SatelliteImagery({
    required this.id,
    required this.fieldId,
    required this.imageUrl,
    this.thumbnailUrl,
    required this.captureDate,
    this.satelliteSource,
    this.cloudCoverage,
    this.imageType,
    this.bounds,
    this.metadata,
  });

  factory SatelliteImagery.fromJson(Map<String, dynamic> json) {
    return SatelliteImagery(
      id: json['id'] as String? ?? '',
      fieldId: json['field_id'] as String? ?? '',
      imageUrl: json['image_url'] as String? ?? '',
      thumbnailUrl: json['thumbnail_url'] as String?,
      captureDate: json['capture_date'] != null
          ? DateTime.tryParse(json['capture_date'] as String) ?? DateTime.now()
          : DateTime.now(),
      satelliteSource: json['satellite_source'] as String?,
      cloudCoverage: (json['cloud_coverage'] as num?)?.toInt(),
      imageType: json['image_type'] as String?,
      bounds: json['bounds'] as Map<String, dynamic>?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }
}

/// Field health assessment model
class FieldHealth {
  final String fieldId;
  final String overallStatus;
  final String? overallStatusAr;
  final double healthScore;
  final Map<String, dynamic>? issues;
  final List<String>? recommendations;
  final List<String>? recommendationsAr;
  final DateTime assessmentDate;
  final Map<String, dynamic>? zoneHealth;

  const FieldHealth({
    required this.fieldId,
    required this.overallStatus,
    this.overallStatusAr,
    required this.healthScore,
    this.issues,
    this.recommendations,
    this.recommendationsAr,
    required this.assessmentDate,
    this.zoneHealth,
  });

  factory FieldHealth.fromJson(Map<String, dynamic> json) {
    return FieldHealth(
      fieldId: json['field_id'] as String? ?? '',
      overallStatus: json['overall_status'] as String? ?? 'unknown',
      overallStatusAr: json['overall_status_ar'] as String?,
      healthScore: (json['health_score'] as num?)?.toDouble() ?? 0.0,
      issues: json['issues'] as Map<String, dynamic>?,
      recommendations: (json['recommendations'] as List?)?.cast<String>(),
      recommendationsAr: (json['recommendations_ar'] as List?)?.cast<String>(),
      assessmentDate: json['assessment_date'] != null
          ? DateTime.tryParse(json['assessment_date'] as String) ?? DateTime.now()
          : DateTime.now(),
      zoneHealth: json['zone_health'] as Map<String, dynamic>?,
    );
  }
}

/// Phenology stage model
class PhenologyStage {
  final String stage;
  final String? stageAr;
  final DateTime? startDate;
  final DateTime? endDate;
  final int? daysInStage;
  final double? progress;
  final String? description;
  final String? descriptionAr;
  final List<String>? recommendations;
  final List<String>? recommendationsAr;

  const PhenologyStage({
    required this.stage,
    this.stageAr,
    this.startDate,
    this.endDate,
    this.daysInStage,
    this.progress,
    this.description,
    this.descriptionAr,
    this.recommendations,
    this.recommendationsAr,
  });

  factory PhenologyStage.fromJson(Map<String, dynamic> json) {
    return PhenologyStage(
      stage: json['stage'] as String? ?? '',
      stageAr: json['stage_ar'] as String?,
      startDate:
          json['start_date'] != null ? DateTime.tryParse(json['start_date'] as String) : null,
      endDate: json['end_date'] != null ? DateTime.tryParse(json['end_date'] as String) : null,
      daysInStage: (json['days_in_stage'] as num?)?.toInt(),
      progress: (json['progress'] as num?)?.toDouble(),
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      recommendations: (json['recommendations'] as List?)?.cast<String>(),
      recommendationsAr: (json['recommendations_ar'] as List?)?.cast<String>(),
    );
  }
}

/// NDVI Service Connector
/// موصل خدمة مؤشر الغطاء النباتي
class NdviServiceConnector extends ServiceConnector {
  NdviServiceConnector({required super.ref}) : super(serviceId: 'vegetation-analysis');

  /// Analyze field NDVI
  /// تحليل مؤشر الغطاء النباتي للحقل
  Future<ApiResult<NdviAnalysis>> analyzeField(String fieldId) async {
    return get(
      '${getEndpoint('analyze') ?? '/api/v1/satellite/analyze'}/$fieldId',
      parser: (data) => NdviAnalysis.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Get NDVI timeseries for field
  /// الحصول على السلسلة الزمنية لمؤشر الغطاء النباتي
  Future<ApiResult<List<NdviTimeseriesPoint>>> getTimeseries(
    String fieldId, {
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final queryParams = <String, dynamic>{
      if (startDate != null) 'start_date': startDate.toIso8601String(),
      if (endDate != null) 'end_date': endDate.toIso8601String(),
    };

    return get(
      '${getEndpoint('timeseries') ?? '/api/v1/satellite/timeseries'}/$fieldId',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
      parser: (data) {
        if (data is List) {
          return data.map((e) => NdviTimeseriesPoint.fromJson(e as Map<String, dynamic>)).toList();
        }
        if (data is Map && data['timeseries'] != null) {
          return (data['timeseries'] as List)
              .map((e) => NdviTimeseriesPoint.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <NdviTimeseriesPoint>[];
      },
    );
  }

  /// Get vegetation indices for field
  /// الحصول على مؤشرات الغطاء النباتي للحقل
  Future<ApiResult<List<VegetationIndex>>> getIndices(String fieldId) async {
    return get(
      '${getEndpoint('indices') ?? '/api/v1/satellite/indices'}/$fieldId',
      parser: (data) {
        if (data is List) {
          return data.map((e) => VegetationIndex.fromJson(e as Map<String, dynamic>)).toList();
        }
        if (data is Map && data['indices'] != null) {
          return (data['indices'] as List)
              .map((e) => VegetationIndex.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <VegetationIndex>[];
      },
    );
  }

  /// Get satellite imagery for field
  /// الحصول على صور الأقمار الصناعية للحقل
  Future<ApiResult<List<SatelliteImagery>>> getImagery(
    String fieldId, {
    DateTime? startDate,
    DateTime? endDate,
    String? imageType,
    int? maxCloudCoverage,
  }) async {
    final queryParams = <String, dynamic>{
      if (startDate != null) 'start_date': startDate.toIso8601String(),
      if (endDate != null) 'end_date': endDate.toIso8601String(),
      if (imageType != null) 'image_type': imageType,
      if (maxCloudCoverage != null) 'max_cloud_coverage': maxCloudCoverage,
    };

    return get(
      '${getEndpoint('imagery') ?? '/api/v1/satellite/imagery'}/$fieldId',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
      parser: (data) {
        if (data is List) {
          return data.map((e) => SatelliteImagery.fromJson(e as Map<String, dynamic>)).toList();
        }
        if (data is Map && data['imagery'] != null) {
          return (data['imagery'] as List)
              .map((e) => SatelliteImagery.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <SatelliteImagery>[];
      },
    );
  }

  /// Get field health assessment
  /// الحصول على تقييم صحة الحقل
  Future<ApiResult<FieldHealth>> getFieldHealth(String fieldId) async {
    return get(
      '${getEndpoint('health') ?? '/api/v1/satellite/health'}/$fieldId',
      parser: (data) => FieldHealth.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Get phenology information for field
  /// الحصول على معلومات الفينولوجيا للحقل
  Future<ApiResult<PhenologyStage>> getPhenology(String fieldId) async {
    return get(
      '${getEndpoint('phenology') ?? '/api/v1/satellite/phenology'}/$fieldId',
      parser: (data) => PhenologyStage.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Get available satellites
  /// الحصول على الأقمار الصناعية المتاحة
  Future<ApiResult<List<String>>> getAvailableSatellites() async {
    return get(
      '/api/v1/satellite/satellites',
      parser: (data) {
        if (data is List) {
          return data.cast<String>();
        }
        if (data is Map && data['satellites'] != null) {
          return (data['satellites'] as List).cast<String>();
        }
        return <String>[];
      },
    );
  }

  /// Compare NDVI between two dates
  /// مقارنة مؤشر الغطاء النباتي بين تاريخين
  Future<ApiResult<Map<String, dynamic>>> compareNdvi(
    String fieldId, {
    required DateTime date1,
    required DateTime date2,
  }) async {
    return get(
      '/api/v1/ndvi/comparison',
      queryParameters: {
        'field_id': fieldId,
        'date1': date1.toIso8601String(),
        'date2': date2.toIso8601String(),
      },
      parser: (data) => data as Map<String, dynamic>,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// NDVI Service Provider
final ndviServiceProvider = Provider<NdviServiceConnector>((ref) {
  return NdviServiceConnector(ref: ref);
});

/// NDVI Analysis Provider
final ndviAnalysisProvider = FutureProvider.family<NdviAnalysis?, String>((ref, fieldId) async {
  final service = ref.watch(ndviServiceProvider);
  final result = await service.analyzeField(fieldId);
  return result.dataOrNull;
});

/// NDVI Timeseries Provider
final ndviTimeseriesProvider =
    FutureProvider.family<List<NdviTimeseriesPoint>, String>((ref, fieldId) async {
  final service = ref.watch(ndviServiceProvider);
  final result = await service.getTimeseries(fieldId);
  return result.dataOrNull ?? [];
});

/// Vegetation Indices Provider
final vegetationIndicesProvider =
    FutureProvider.family<List<VegetationIndex>, String>((ref, fieldId) async {
  final service = ref.watch(ndviServiceProvider);
  final result = await service.getIndices(fieldId);
  return result.dataOrNull ?? [];
});

/// Satellite Imagery Provider
final satelliteImageryProvider =
    FutureProvider.family<List<SatelliteImagery>, String>((ref, fieldId) async {
  final service = ref.watch(ndviServiceProvider);
  final result = await service.getImagery(fieldId);
  return result.dataOrNull ?? [];
});

/// Field Health Provider
final fieldHealthProvider = FutureProvider.family<FieldHealth?, String>((ref, fieldId) async {
  final service = ref.watch(ndviServiceProvider);
  final result = await service.getFieldHealth(fieldId);
  return result.dataOrNull;
});

/// Phenology Provider
final phenologyProvider = FutureProvider.family<PhenologyStage?, String>((ref, fieldId) async {
  final service = ref.watch(ndviServiceProvider);
  final result = await service.getPhenology(fieldId);
  return result.dataOrNull;
});
