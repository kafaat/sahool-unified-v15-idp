/// Field Health Model - نموذج صحة الحقل
/// Complete field health assessment from satellite data
library;

import 'package:equatable/equatable.dart';
import 'ndvi_data.dart';

/// Field Health Score
/// درجة صحة الحقل
class FieldHealth extends Equatable {
  final String fieldId;
  final double healthScore; // 0-100
  final HealthStatus status;
  final double ndvi;
  final double ndwi; // water stress
  final double evi; // enhanced vegetation index
  final double? soilMoisture;
  final List<HealthAlert> alerts;
  final List<Recommendation> recommendations;
  final DateTime assessedAt;
  final Map<String, double>? zoneScores; // scores by field zone

  const FieldHealth({
    required this.fieldId,
    required this.healthScore,
    required this.status,
    required this.ndvi,
    required this.ndwi,
    required this.evi,
    this.soilMoisture,
    this.alerts = const [],
    this.recommendations = const [],
    required this.assessedAt,
    this.zoneScores,
  });

  factory FieldHealth.fromJson(Map<String, dynamic> json) {
    final alertsData = json['alerts'] ?? [];
    final recommendationsData = json['recommendations'] ?? [];
    final zoneScoresData = json['zone_scores'] ?? json['zoneScores'];

    return FieldHealth(
      fieldId: json['field_id'] ?? json['fieldId'] ?? '',
      healthScore: (json['health_score'] ?? json['healthScore'] ?? 0.0).toDouble(),
      status: HealthStatus.fromString(
        json['status'] ?? json['health_status'] ?? 'unknown',
      ),
      ndvi: (json['ndvi'] ?? 0.0).toDouble(),
      ndwi: (json['ndwi'] ?? 0.0).toDouble(),
      evi: (json['evi'] ?? 0.0).toDouble(),
      soilMoisture: json['soil_moisture'] != null
          ? (json['soil_moisture'] as num).toDouble()
          : null,
      alerts: (alertsData as List)
          .map((item) => HealthAlert.fromJson(item as Map<String, dynamic>))
          .toList(),
      recommendations: (recommendationsData as List)
          .map((item) => Recommendation.fromJson(item as Map<String, dynamic>))
          .toList(),
      assessedAt: DateTime.parse(
        json['assessed_at'] ?? json['assessedAt'] ?? DateTime.now().toIso8601String(),
      ),
      zoneScores: zoneScoresData != null
          ? (zoneScoresData as Map<String, dynamic>).map(
              (key, value) => MapEntry(key, (value as num).toDouble()),
            )
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'field_id': fieldId,
      'health_score': healthScore,
      'status': status.value,
      'ndvi': ndvi,
      'ndwi': ndwi,
      'evi': evi,
      'soil_moisture': soilMoisture,
      'alerts': alerts.map((alert) => alert.toJson()).toList(),
      'recommendations': recommendations.map((rec) => rec.toJson()).toList(),
      'assessed_at': assessedAt.toIso8601String(),
      'zone_scores': zoneScores,
    };
  }

  @override
  List<Object?> get props => [
        fieldId,
        healthScore,
        status,
        ndvi,
        ndwi,
        evi,
        soilMoisture,
        alerts,
        recommendations,
        assessedAt,
        zoneScores,
      ];
}

/// Health Status
/// حالة الصحة
enum HealthStatus {
  excellent('excellent', 'ممتاز', '#4CAF50'),
  good('good', 'جيد', '#8BC34A'),
  warning('warning', 'تحذير', '#FFC107'),
  critical('critical', 'حرج', '#F44336'),
  unknown('unknown', 'غير معروف', '#9E9E9E');

  final String value;
  final String arabicLabel;
  final String colorHex;

  const HealthStatus(this.value, this.arabicLabel, this.colorHex);

  static HealthStatus fromString(String value) {
    return HealthStatus.values.firstWhere(
      (status) => status.value.toLowerCase() == value.toLowerCase(),
      orElse: () => HealthStatus.unknown,
    );
  }

  static HealthStatus fromScore(double score) {
    if (score >= 80) return HealthStatus.excellent;
    if (score >= 60) return HealthStatus.good;
    if (score >= 40) return HealthStatus.warning;
    return HealthStatus.critical;
  }

  String getLabel(bool isArabic) => isArabic ? arabicLabel : value;
}

/// Health Alert
/// تنبيه صحي
class HealthAlert extends Equatable {
  final String id;
  final AlertType type;
  final AlertSeverity severity;
  final String message;
  final String messageAr;
  final DateTime detectedAt;
  final String? affectedZone;

  const HealthAlert({
    required this.id,
    required this.type,
    required this.severity,
    required this.message,
    required this.messageAr,
    required this.detectedAt,
    this.affectedZone,
  });

  factory HealthAlert.fromJson(Map<String, dynamic> json) {
    return HealthAlert(
      id: json['id'] ?? '',
      type: AlertType.fromString(json['type'] ?? 'other'),
      severity: AlertSeverity.fromString(json['severity'] ?? 'info'),
      message: json['message'] ?? '',
      messageAr: json['message_ar'] ?? json['messageAr'] ?? '',
      detectedAt: DateTime.parse(
        json['detected_at'] ?? json['detectedAt'] ?? DateTime.now().toIso8601String(),
      ),
      affectedZone: json['affected_zone'] ?? json['affectedZone'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type.value,
      'severity': severity.value,
      'message': message,
      'message_ar': messageAr,
      'detected_at': detectedAt.toIso8601String(),
      'affected_zone': affectedZone,
    };
  }

  @override
  List<Object?> get props => [id, type, severity, message, messageAr, detectedAt, affectedZone];
}

/// Alert Type
/// نوع التنبيه
enum AlertType {
  waterStress('water_stress', 'إجهاد مائي'),
  nutrientDeficiency('nutrient_deficiency', 'نقص المغذيات'),
  diseaseRisk('disease_risk', 'خطر مرضي'),
  pestRisk('pest_risk', 'خطر آفات'),
  growthAnomaly('growth_anomaly', 'خلل في النمو'),
  other('other', 'آخر');

  final String value;
  final String arabicLabel;

  const AlertType(this.value, this.arabicLabel);

  static AlertType fromString(String value) {
    return AlertType.values.firstWhere(
      (type) => type.value.toLowerCase() == value.toLowerCase(),
      orElse: () => AlertType.other,
    );
  }

  String getLabel(bool isArabic) => isArabic ? arabicLabel : value;
}

/// Alert Severity
/// شدة التنبيه
enum AlertSeverity {
  info('info', 'معلومات', '#2196F3'),
  warning('warning', 'تحذير', '#FFC107'),
  critical('critical', 'حرج', '#F44336');

  final String value;
  final String arabicLabel;
  final String colorHex;

  const AlertSeverity(this.value, this.arabicLabel, this.colorHex);

  static AlertSeverity fromString(String value) {
    return AlertSeverity.values.firstWhere(
      (severity) => severity.value.toLowerCase() == value.toLowerCase(),
      orElse: () => AlertSeverity.info,
    );
  }

  String getLabel(bool isArabic) => isArabic ? arabicLabel : value;
}

/// Recommendation
/// توصية
class Recommendation extends Equatable {
  final String id;
  final RecommendationType type;
  final String title;
  final String titleAr;
  final String description;
  final String descriptionAr;
  final RecommendationPriority priority;
  final DateTime? dueDate;

  const Recommendation({
    required this.id,
    required this.type,
    required this.title,
    required this.titleAr,
    required this.description,
    required this.descriptionAr,
    required this.priority,
    this.dueDate,
  });

  factory Recommendation.fromJson(Map<String, dynamic> json) {
    return Recommendation(
      id: json['id'] ?? '',
      type: RecommendationType.fromString(json['type'] ?? 'general'),
      title: json['title'] ?? '',
      titleAr: json['title_ar'] ?? json['titleAr'] ?? '',
      description: json['description'] ?? '',
      descriptionAr: json['description_ar'] ?? json['descriptionAr'] ?? '',
      priority: RecommendationPriority.fromString(json['priority'] ?? 'medium'),
      dueDate: json['due_date'] != null ? DateTime.parse(json['due_date']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type.value,
      'title': title,
      'title_ar': titleAr,
      'description': description,
      'description_ar': descriptionAr,
      'priority': priority.value,
      'due_date': dueDate?.toIso8601String(),
    };
  }

  @override
  List<Object?> get props =>
      [id, type, title, titleAr, description, descriptionAr, priority, dueDate];
}

/// Recommendation Type
/// نوع التوصية
enum RecommendationType {
  irrigation('irrigation', 'ري'),
  fertilization('fertilization', 'تسميد'),
  pestControl('pest_control', 'مكافحة آفات'),
  diseaseControl('disease_control', 'مكافحة أمراض'),
  monitoring('monitoring', 'مراقبة'),
  general('general', 'عام');

  final String value;
  final String arabicLabel;

  const RecommendationType(this.value, this.arabicLabel);

  static RecommendationType fromString(String value) {
    return RecommendationType.values.firstWhere(
      (type) => type.value.toLowerCase() == value.toLowerCase(),
      orElse: () => RecommendationType.general,
    );
  }

  String getLabel(bool isArabic) => isArabic ? arabicLabel : value;
}

/// Recommendation Priority
/// أولوية التوصية
enum RecommendationPriority {
  high('high', 'عالية'),
  medium('medium', 'متوسطة'),
  low('low', 'منخفضة');

  final String value;
  final String arabicLabel;

  const RecommendationPriority(this.value, this.arabicLabel);

  static RecommendationPriority fromString(String value) {
    return RecommendationPriority.values.firstWhere(
      (priority) => priority.value.toLowerCase() == value.toLowerCase(),
      orElse: () => RecommendationPriority.medium,
    );
  }

  String getLabel(bool isArabic) => isArabic ? arabicLabel : value;
}
