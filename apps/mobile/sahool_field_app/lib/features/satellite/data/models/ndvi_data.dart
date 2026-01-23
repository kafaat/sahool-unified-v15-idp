/// NDVI Data Model - نموذج بيانات NDVI
/// Vegetation index data from satellite imagery
library;

import 'package:equatable/equatable.dart';

/// NDVI Data Point
/// نقطة بيانات NDVI
class NdviDataPoint extends Equatable {
  final DateTime date;
  final double value;
  final String source; // sentinel-2, landsat-8
  final double cloudCoverage;

  const NdviDataPoint({
    required this.date,
    required this.value,
    required this.source,
    this.cloudCoverage = 0.0,
  });

  factory NdviDataPoint.fromJson(Map<String, dynamic> json) {
    return NdviDataPoint(
      date: DateTime.parse(json['date'] ?? json['timestamp']),
      value: (json['value'] ?? json['ndvi'] ?? 0.0).toDouble(),
      source: json['source'] ?? 'sentinel-2',
      cloudCoverage: (json['cloud_coverage'] ?? json['cloudCoverage'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'date': date.toIso8601String(),
      'value': value,
      'source': source,
      'cloud_coverage': cloudCoverage,
    };
  }

  @override
  List<Object?> get props => [date, value, source, cloudCoverage];
}

/// NDVI Analysis Result
/// نتيجة تحليل NDVI
class NdviAnalysis extends Equatable {
  final String fieldId;
  final double currentNdvi;
  final double previousNdvi;
  final double changeRate; // percentage change
  final VegetationHealth health;
  final List<NdviDataPoint> timeSeries;
  final DateTime analyzedAt;
  final String? imageUrl; // colored NDVI map
  final Map<String, double>? indices; // NDVI, NDWI, EVI, NDRE

  const NdviAnalysis({
    required this.fieldId,
    required this.currentNdvi,
    required this.previousNdvi,
    required this.changeRate,
    required this.health,
    required this.timeSeries,
    required this.analyzedAt,
    this.imageUrl,
    this.indices,
  });

  factory NdviAnalysis.fromJson(Map<String, dynamic> json) {
    final timeSeriesData = json['time_series'] ?? json['timeSeries'] ?? [];
    final indicesData = json['indices'];

    return NdviAnalysis(
      fieldId: json['field_id'] ?? json['fieldId'] ?? '',
      currentNdvi: (json['current_ndvi'] ?? json['currentNdvi'] ?? 0.0).toDouble(),
      previousNdvi: (json['previous_ndvi'] ?? json['previousNdvi'] ?? 0.0).toDouble(),
      changeRate: (json['change_rate'] ?? json['changeRate'] ?? 0.0).toDouble(),
      health: VegetationHealth.fromString(
        json['health_status'] ?? json['healthStatus'] ?? 'unknown',
      ),
      timeSeries: (timeSeriesData as List)
          .map((item) => NdviDataPoint.fromJson(item as Map<String, dynamic>))
          .toList(),
      analyzedAt: DateTime.parse(
        json['analyzed_at'] ?? json['analyzedAt'] ?? DateTime.now().toIso8601String(),
      ),
      imageUrl: json['image_url'] ?? json['imageUrl'],
      indices: indicesData != null
          ? (indicesData as Map<String, dynamic>).map(
              (key, value) => MapEntry(key, (value as num).toDouble()),
            )
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'field_id': fieldId,
      'current_ndvi': currentNdvi,
      'previous_ndvi': previousNdvi,
      'change_rate': changeRate,
      'health_status': health.value,
      'time_series': timeSeries.map((point) => point.toJson()).toList(),
      'analyzed_at': analyzedAt.toIso8601String(),
      'image_url': imageUrl,
      'indices': indices,
    };
  }

  @override
  List<Object?> get props => [
        fieldId,
        currentNdvi,
        previousNdvi,
        changeRate,
        health,
        timeSeries,
        analyzedAt,
        imageUrl,
        indices,
      ];
}

/// Vegetation Health Status
/// حالة صحة النباتات
enum VegetationHealth {
  excellent('excellent', 'ممتاز', 0.8),
  good('good', 'جيد', 0.6),
  fair('fair', 'متوسط', 0.4),
  poor('poor', 'ضعيف', 0.2),
  critical('critical', 'حرج', 0.0),
  unknown('unknown', 'غير معروف', 0.0);

  final String value;
  final String arabicLabel;
  final double threshold;

  const VegetationHealth(this.value, this.arabicLabel, this.threshold);

  static VegetationHealth fromString(String value) {
    return VegetationHealth.values.firstWhere(
      (health) => health.value.toLowerCase() == value.toLowerCase(),
      orElse: () => VegetationHealth.unknown,
    );
  }

  static VegetationHealth fromNdvi(double ndvi) {
    if (ndvi >= 0.8) return VegetationHealth.excellent;
    if (ndvi >= 0.6) return VegetationHealth.good;
    if (ndvi >= 0.4) return VegetationHealth.fair;
    if (ndvi >= 0.2) return VegetationHealth.poor;
    return VegetationHealth.critical;
  }

  String getLabel(bool isArabic) => isArabic ? arabicLabel : value;
}

/// Vegetation Index
/// مؤشر نباتي
class VegetationIndex extends Equatable {
  final String name;
  final String nameAr;
  final String code; // NDVI, NDWI, EVI, NDRE
  final double value;
  final String unit;
  final String description;
  final String descriptionAr;

  const VegetationIndex({
    required this.name,
    required this.nameAr,
    required this.code,
    required this.value,
    this.unit = '',
    this.description = '',
    this.descriptionAr = '',
  });

  factory VegetationIndex.fromJson(Map<String, dynamic> json) {
    return VegetationIndex(
      name: json['name'] ?? '',
      nameAr: json['name_ar'] ?? json['nameAr'] ?? '',
      code: json['code'] ?? '',
      value: (json['value'] ?? 0.0).toDouble(),
      unit: json['unit'] ?? '',
      description: json['description'] ?? '',
      descriptionAr: json['description_ar'] ?? json['descriptionAr'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'name_ar': nameAr,
      'code': code,
      'value': value,
      'unit': unit,
      'description': description,
      'description_ar': descriptionAr,
    };
  }

  @override
  List<Object?> get props => [name, nameAr, code, value, unit, description, descriptionAr];
}
