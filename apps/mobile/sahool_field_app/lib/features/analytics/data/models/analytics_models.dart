/// Analytics Models - Predictive Analytics Data Models
/// نماذج التحليلات - نماذج بيانات التحليلات التنبؤية
library;

import 'package:flutter/foundation.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Field Health Score
// درجة صحة الحقل
// ═══════════════════════════════════════════════════════════════════════════════

/// Overall health score for a field
/// درجة الصحة الإجمالية للحقل
@immutable
class FieldHealthScore {
  final String fieldId;
  final String fieldName;
  final double overallScore; // 0-100
  final double ndviScore;
  final double soilHealthScore;
  final double waterStressScore;
  final double pestRiskScore;
  final double nutrientScore;
  final HealthTrend trend;
  final DateTime calculatedAt;
  final List<HealthRecommendation> recommendations;

  const FieldHealthScore({
    required this.fieldId,
    required this.fieldName,
    required this.overallScore,
    required this.ndviScore,
    required this.soilHealthScore,
    required this.waterStressScore,
    required this.pestRiskScore,
    required this.nutrientScore,
    required this.trend,
    required this.calculatedAt,
    this.recommendations = const [],
  });

  /// Get health status based on score
  /// الحصول على حالة الصحة بناءً على الدرجة
  HealthStatus get status {
    if (overallScore >= 80) return HealthStatus.excellent;
    if (overallScore >= 60) return HealthStatus.good;
    if (overallScore >= 40) return HealthStatus.moderate;
    if (overallScore >= 20) return HealthStatus.poor;
    return HealthStatus.critical;
  }

  /// Get Arabic status name
  /// الحصول على اسم الحالة بالعربية
  String get statusNameAr {
    switch (status) {
      case HealthStatus.excellent:
        return 'ممتاز';
      case HealthStatus.good:
        return 'جيد';
      case HealthStatus.moderate:
        return 'متوسط';
      case HealthStatus.poor:
        return 'ضعيف';
      case HealthStatus.critical:
        return 'حرج';
    }
  }

  factory FieldHealthScore.fromJson(Map<String, dynamic> json) {
    return FieldHealthScore(
      fieldId: json['field_id'] as String,
      fieldName: json['field_name'] as String? ?? '',
      overallScore: (json['overall_score'] as num).toDouble(),
      ndviScore: (json['ndvi_score'] as num?)?.toDouble() ?? 0,
      soilHealthScore: (json['soil_health_score'] as num?)?.toDouble() ?? 0,
      waterStressScore: (json['water_stress_score'] as num?)?.toDouble() ?? 0,
      pestRiskScore: (json['pest_risk_score'] as num?)?.toDouble() ?? 0,
      nutrientScore: (json['nutrient_score'] as num?)?.toDouble() ?? 0,
      trend: HealthTrend.values.firstWhere(
        (t) => t.name == json['trend'],
        orElse: () => HealthTrend.stable,
      ),
      calculatedAt: DateTime.parse(json['calculated_at'] as String),
      recommendations: (json['recommendations'] as List<dynamic>?)
              ?.map((r) => HealthRecommendation.fromJson(r as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() => {
        'field_id': fieldId,
        'field_name': fieldName,
        'overall_score': overallScore,
        'ndvi_score': ndviScore,
        'soil_health_score': soilHealthScore,
        'water_stress_score': waterStressScore,
        'pest_risk_score': pestRiskScore,
        'nutrient_score': nutrientScore,
        'trend': trend.name,
        'calculated_at': calculatedAt.toIso8601String(),
        'recommendations': recommendations.map((r) => r.toJson()).toList(),
      };
}

enum HealthStatus { excellent, good, moderate, poor, critical }

enum HealthTrend { improving, stable, declining }

// ═══════════════════════════════════════════════════════════════════════════════
// Health Recommendation
// توصية صحية
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class HealthRecommendation {
  final String id;
  final String title;
  final String titleAr;
  final String description;
  final String descriptionAr;
  final RecommendationPriority priority;
  final RecommendationType type;
  final String? actionUrl;

  const HealthRecommendation({
    required this.id,
    required this.title,
    required this.titleAr,
    required this.description,
    required this.descriptionAr,
    required this.priority,
    required this.type,
    this.actionUrl,
  });

  factory HealthRecommendation.fromJson(Map<String, dynamic> json) {
    return HealthRecommendation(
      id: json['id'] as String,
      title: json['title'] as String,
      titleAr: json['title_ar'] as String? ?? json['title'] as String,
      description: json['description'] as String,
      descriptionAr: json['description_ar'] as String? ?? json['description'] as String,
      priority: RecommendationPriority.values.firstWhere(
        (p) => p.name == json['priority'],
        orElse: () => RecommendationPriority.medium,
      ),
      type: RecommendationType.values.firstWhere(
        (t) => t.name == json['type'],
        orElse: () => RecommendationType.general,
      ),
      actionUrl: json['action_url'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'title': title,
        'title_ar': titleAr,
        'description': description,
        'description_ar': descriptionAr,
        'priority': priority.name,
        'type': type.name,
        'action_url': actionUrl,
      };
}

enum RecommendationPriority { critical, high, medium, low }

enum RecommendationType {
  irrigation,
  fertilizer,
  pestControl,
  harvest,
  planting,
  general,
}

// ═══════════════════════════════════════════════════════════════════════════════
// Yield Prediction
// توقع الإنتاجية
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class YieldPrediction {
  final String fieldId;
  final String cropType;
  final String cropTypeAr;
  final double predictedYield; // kg/hectare
  final double minYield;
  final double maxYield;
  final double confidence; // 0-1
  final DateTime harvestDate;
  final double revenueEstimate; // YER
  final List<YieldFactor> factors;
  final DateTime calculatedAt;

  const YieldPrediction({
    required this.fieldId,
    required this.cropType,
    required this.cropTypeAr,
    required this.predictedYield,
    required this.minYield,
    required this.maxYield,
    required this.confidence,
    required this.harvestDate,
    required this.revenueEstimate,
    this.factors = const [],
    required this.calculatedAt,
  });

  /// Get yield quality assessment
  /// تقييم جودة الإنتاجية
  YieldQuality get quality {
    // Based on typical Yemen crop yields
    if (predictedYield >= 4000) return YieldQuality.excellent;
    if (predictedYield >= 3000) return YieldQuality.good;
    if (predictedYield >= 2000) return YieldQuality.average;
    if (predictedYield >= 1000) return YieldQuality.belowAverage;
    return YieldQuality.poor;
  }

  factory YieldPrediction.fromJson(Map<String, dynamic> json) {
    return YieldPrediction(
      fieldId: json['field_id'] as String,
      cropType: json['crop_type'] as String,
      cropTypeAr: json['crop_type_ar'] as String? ?? json['crop_type'] as String,
      predictedYield: (json['predicted_yield'] as num).toDouble(),
      minYield: (json['min_yield'] as num).toDouble(),
      maxYield: (json['max_yield'] as num).toDouble(),
      confidence: (json['confidence'] as num).toDouble(),
      harvestDate: DateTime.parse(json['harvest_date'] as String),
      revenueEstimate: (json['revenue_estimate'] as num).toDouble(),
      factors: (json['factors'] as List<dynamic>?)
              ?.map((f) => YieldFactor.fromJson(f as Map<String, dynamic>))
              .toList() ??
          [],
      calculatedAt: DateTime.parse(json['calculated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'field_id': fieldId,
        'crop_type': cropType,
        'crop_type_ar': cropTypeAr,
        'predicted_yield': predictedYield,
        'min_yield': minYield,
        'max_yield': maxYield,
        'confidence': confidence,
        'harvest_date': harvestDate.toIso8601String(),
        'revenue_estimate': revenueEstimate,
        'factors': factors.map((f) => f.toJson()).toList(),
        'calculated_at': calculatedAt.toIso8601String(),
      };
}

enum YieldQuality { excellent, good, average, belowAverage, poor }

@immutable
class YieldFactor {
  final String name;
  final String nameAr;
  final double impact; // -1 to 1 (negative = reducing yield)
  final String description;
  final String descriptionAr;

  const YieldFactor({
    required this.name,
    required this.nameAr,
    required this.impact,
    required this.description,
    required this.descriptionAr,
  });

  factory YieldFactor.fromJson(Map<String, dynamic> json) {
    return YieldFactor(
      name: json['name'] as String,
      nameAr: json['name_ar'] as String? ?? json['name'] as String,
      impact: (json['impact'] as num).toDouble(),
      description: json['description'] as String,
      descriptionAr: json['description_ar'] as String? ?? json['description'] as String,
    );
  }

  Map<String, dynamic> toJson() => {
        'name': name,
        'name_ar': nameAr,
        'impact': impact,
        'description': description,
        'description_ar': descriptionAr,
      };
}

// ═══════════════════════════════════════════════════════════════════════════════
// Risk Assessment
// تقييم المخاطر
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class RiskAssessment {
  final String fieldId;
  final List<Risk> risks;
  final double overallRiskScore; // 0-100
  final DateTime assessedAt;

  const RiskAssessment({
    required this.fieldId,
    required this.risks,
    required this.overallRiskScore,
    required this.assessedAt,
  });

  RiskLevel get overallRiskLevel {
    if (overallRiskScore >= 80) return RiskLevel.critical;
    if (overallRiskScore >= 60) return RiskLevel.high;
    if (overallRiskScore >= 40) return RiskLevel.moderate;
    if (overallRiskScore >= 20) return RiskLevel.low;
    return RiskLevel.minimal;
  }

  factory RiskAssessment.fromJson(Map<String, dynamic> json) {
    return RiskAssessment(
      fieldId: json['field_id'] as String,
      risks: (json['risks'] as List<dynamic>)
          .map((r) => Risk.fromJson(r as Map<String, dynamic>))
          .toList(),
      overallRiskScore: (json['overall_risk_score'] as num).toDouble(),
      assessedAt: DateTime.parse(json['assessed_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'field_id': fieldId,
        'risks': risks.map((r) => r.toJson()).toList(),
        'overall_risk_score': overallRiskScore,
        'assessed_at': assessedAt.toIso8601String(),
      };
}

@immutable
class Risk {
  final String id;
  final RiskType type;
  final String name;
  final String nameAr;
  final String description;
  final String descriptionAr;
  final RiskLevel level;
  final double probability; // 0-1
  final double potentialImpact; // 0-100
  final List<String> mitigationSteps;
  final List<String> mitigationStepsAr;

  const Risk({
    required this.id,
    required this.type,
    required this.name,
    required this.nameAr,
    required this.description,
    required this.descriptionAr,
    required this.level,
    required this.probability,
    required this.potentialImpact,
    this.mitigationSteps = const [],
    this.mitigationStepsAr = const [],
  });

  factory Risk.fromJson(Map<String, dynamic> json) {
    return Risk(
      id: json['id'] as String,
      type: RiskType.values.firstWhere(
        (t) => t.name == json['type'],
        orElse: () => RiskType.other,
      ),
      name: json['name'] as String,
      nameAr: json['name_ar'] as String? ?? json['name'] as String,
      description: json['description'] as String,
      descriptionAr: json['description_ar'] as String? ?? json['description'] as String,
      level: RiskLevel.values.firstWhere(
        (l) => l.name == json['level'],
        orElse: () => RiskLevel.moderate,
      ),
      probability: (json['probability'] as num).toDouble(),
      potentialImpact: (json['potential_impact'] as num).toDouble(),
      mitigationSteps: (json['mitigation_steps'] as List<dynamic>?)
              ?.map((s) => s as String)
              .toList() ??
          [],
      mitigationStepsAr: (json['mitigation_steps_ar'] as List<dynamic>?)
              ?.map((s) => s as String)
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'type': type.name,
        'name': name,
        'name_ar': nameAr,
        'description': description,
        'description_ar': descriptionAr,
        'level': level.name,
        'probability': probability,
        'potential_impact': potentialImpact,
        'mitigation_steps': mitigationSteps,
        'mitigation_steps_ar': mitigationStepsAr,
      };
}

enum RiskType {
  disease,
  pest,
  drought,
  flood,
  frost,
  heatWave,
  nutrientDeficiency,
  marketPrice,
  other,
}

enum RiskLevel { minimal, low, moderate, high, critical }

// ═══════════════════════════════════════════════════════════════════════════════
// Analytics Summary
// ملخص التحليلات
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class AnalyticsSummary {
  final int totalFields;
  final double averageHealthScore;
  final double totalPredictedYield;
  final double totalRevenueEstimate;
  final int highRiskFields;
  final int fieldsNeedingAttention;
  final List<FieldHealthScore> topPerformingFields;
  final List<FieldHealthScore> fieldsAtRisk;
  final DateTime generatedAt;

  const AnalyticsSummary({
    required this.totalFields,
    required this.averageHealthScore,
    required this.totalPredictedYield,
    required this.totalRevenueEstimate,
    required this.highRiskFields,
    required this.fieldsNeedingAttention,
    this.topPerformingFields = const [],
    this.fieldsAtRisk = const [],
    required this.generatedAt,
  });

  factory AnalyticsSummary.fromJson(Map<String, dynamic> json) {
    return AnalyticsSummary(
      totalFields: json['total_fields'] as int,
      averageHealthScore: (json['average_health_score'] as num).toDouble(),
      totalPredictedYield: (json['total_predicted_yield'] as num).toDouble(),
      totalRevenueEstimate: (json['total_revenue_estimate'] as num).toDouble(),
      highRiskFields: json['high_risk_fields'] as int,
      fieldsNeedingAttention: json['fields_needing_attention'] as int,
      topPerformingFields: (json['top_performing_fields'] as List<dynamic>?)
              ?.map((f) => FieldHealthScore.fromJson(f as Map<String, dynamic>))
              .toList() ??
          [],
      fieldsAtRisk: (json['fields_at_risk'] as List<dynamic>?)
              ?.map((f) => FieldHealthScore.fromJson(f as Map<String, dynamic>))
              .toList() ??
          [],
      generatedAt: DateTime.parse(json['generated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'total_fields': totalFields,
        'average_health_score': averageHealthScore,
        'total_predicted_yield': totalPredictedYield,
        'total_revenue_estimate': totalRevenueEstimate,
        'high_risk_fields': highRiskFields,
        'fields_needing_attention': fieldsNeedingAttention,
        'top_performing_fields': topPerformingFields.map((f) => f.toJson()).toList(),
        'fields_at_risk': fieldsAtRisk.map((f) => f.toJson()).toList(),
        'generated_at': generatedAt.toIso8601String(),
      };
}

// ═══════════════════════════════════════════════════════════════════════════════
// Historical Data Point
// نقطة بيانات تاريخية
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class HistoricalDataPoint {
  final DateTime date;
  final double value;
  final String? label;

  const HistoricalDataPoint({
    required this.date,
    required this.value,
    this.label,
  });

  factory HistoricalDataPoint.fromJson(Map<String, dynamic> json) {
    return HistoricalDataPoint(
      date: DateTime.parse(json['date'] as String),
      value: (json['value'] as num).toDouble(),
      label: json['label'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'date': date.toIso8601String(),
        'value': value,
        'label': label,
      };
}

@immutable
class HistoricalTrend {
  final String metricName;
  final String metricNameAr;
  final List<HistoricalDataPoint> dataPoints;
  final double changePercent;
  final HealthTrend trend;

  const HistoricalTrend({
    required this.metricName,
    required this.metricNameAr,
    required this.dataPoints,
    required this.changePercent,
    required this.trend,
  });

  factory HistoricalTrend.fromJson(Map<String, dynamic> json) {
    return HistoricalTrend(
      metricName: json['metric_name'] as String,
      metricNameAr: json['metric_name_ar'] as String? ?? json['metric_name'] as String,
      dataPoints: (json['data_points'] as List<dynamic>)
          .map((d) => HistoricalDataPoint.fromJson(d as Map<String, dynamic>))
          .toList(),
      changePercent: (json['change_percent'] as num).toDouble(),
      trend: HealthTrend.values.firstWhere(
        (t) => t.name == json['trend'],
        orElse: () => HealthTrend.stable,
      ),
    );
  }

  Map<String, dynamic> toJson() => {
        'metric_name': metricName,
        'metric_name_ar': metricNameAr,
        'data_points': dataPoints.map((d) => d.toJson()).toList(),
        'change_percent': changePercent,
        'trend': trend.name,
      };
}
