/// Equipment Status Models - نماذج حالة المعدة
/// Status tracking and alert models
library;

import 'package:flutter/foundation.dart';

/// أولوية الصيانة - Maintenance Priority
enum MaintenancePriority {
  low('low', 'منخفضة', 'Low'),
  medium('medium', 'متوسطة', 'Medium'),
  high('high', 'عالية', 'High'),
  critical('critical', 'حرجة', 'Critical');

  final String value;
  final String nameAr;
  final String nameEn;

  const MaintenancePriority(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static MaintenancePriority fromString(String value) {
    return MaintenancePriority.values.firstWhere(
      (e) => e.value == value,
      orElse: () => MaintenancePriority.low,
    );
  }

  /// Get priority level (1-4)
  int get level {
    switch (this) {
      case MaintenancePriority.low:
        return 1;
      case MaintenancePriority.medium:
        return 2;
      case MaintenancePriority.high:
        return 3;
      case MaintenancePriority.critical:
        return 4;
    }
  }
}

/// نوع التنبيه - Alert Type
enum AlertType {
  maintenance('maintenance', 'صيانة', 'Maintenance'),
  fuel('fuel', 'وقود', 'Fuel'),
  location('location', 'موقع', 'Location'),
  usage('usage', 'استخدام', 'Usage'),
  error('error', 'خطأ', 'Error'),
  general('general', 'عام', 'General');

  final String value;
  final String nameAr;
  final String nameEn;

  const AlertType(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static AlertType fromString(String value) {
    return AlertType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => AlertType.general,
    );
  }
}

/// تنبيه المعدة - Equipment Alert
@immutable
class EquipmentAlert {
  final String alertId;
  final String equipmentId;
  final String equipmentName;
  final AlertType alertType;
  final MaintenancePriority priority;
  final String title;
  final String? titleAr;
  final String message;
  final String? messageAr;
  final bool isRead;
  final bool isDismissed;
  final DateTime createdAt;
  final DateTime? acknowledgedAt;
  final Map<String, dynamic>? metadata;

  const EquipmentAlert({
    required this.alertId,
    required this.equipmentId,
    required this.equipmentName,
    required this.alertType,
    required this.priority,
    required this.title,
    this.titleAr,
    required this.message,
    this.messageAr,
    this.isRead = false,
    this.isDismissed = false,
    required this.createdAt,
    this.acknowledgedAt,
    this.metadata,
  });

  String getTitle(String locale) {
    return locale == 'ar' && titleAr != null ? titleAr! : title;
  }

  String getMessage(String locale) {
    return locale == 'ar' && messageAr != null ? messageAr! : message;
  }

  factory EquipmentAlert.fromJson(Map<String, dynamic> json) {
    return EquipmentAlert(
      alertId: json['alert_id'] as String,
      equipmentId: json['equipment_id'] as String,
      equipmentName: json['equipment_name'] as String,
      alertType: AlertType.fromString(json['alert_type'] as String),
      priority: MaintenancePriority.fromString(json['priority'] as String),
      title: json['title'] as String,
      titleAr: json['title_ar'] as String?,
      message: json['message'] as String,
      messageAr: json['message_ar'] as String?,
      isRead: json['is_read'] as bool? ?? false,
      isDismissed: json['is_dismissed'] as bool? ?? false,
      createdAt: DateTime.tryParse(json['created_at'] as String) ?? DateTime.now(),
      acknowledgedAt: json['acknowledged_at'] != null
          ? DateTime.tryParse(json['acknowledged_at'] as String) ?? DateTime.now()
          : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'alert_id': alertId,
        'equipment_id': equipmentId,
        'equipment_name': equipmentName,
        'alert_type': alertType.value,
        'priority': priority.value,
        'title': title,
        'title_ar': titleAr,
        'message': message,
        'message_ar': messageAr,
        'is_read': isRead,
        'is_dismissed': isDismissed,
        'created_at': createdAt.toIso8601String(),
        'acknowledged_at': acknowledgedAt?.toIso8601String(),
        'metadata': metadata,
      };

  EquipmentAlert copyWith({
    bool? isRead,
    bool? isDismissed,
    DateTime? acknowledgedAt,
  }) {
    return EquipmentAlert(
      alertId: alertId,
      equipmentId: equipmentId,
      equipmentName: equipmentName,
      alertType: alertType,
      priority: priority,
      title: title,
      titleAr: titleAr,
      message: message,
      messageAr: messageAr,
      isRead: isRead ?? this.isRead,
      isDismissed: isDismissed ?? this.isDismissed,
      createdAt: createdAt,
      acknowledgedAt: acknowledgedAt ?? this.acknowledgedAt,
      metadata: metadata,
    );
  }
}

/// حالة صحة المعدة - Equipment Health Status
@immutable
class EquipmentHealthStatus {
  final String equipmentId;
  final int overallScore; // 0-100
  final int fuelScore;
  final int maintenanceScore;
  final int usageScore;
  final List<String> issues;
  final List<String> issuesAr;
  final List<String> recommendations;
  final List<String> recommendationsAr;
  final DateTime assessedAt;

  const EquipmentHealthStatus({
    required this.equipmentId,
    required this.overallScore,
    required this.fuelScore,
    required this.maintenanceScore,
    required this.usageScore,
    this.issues = const [],
    this.issuesAr = const [],
    this.recommendations = const [],
    this.recommendationsAr = const [],
    required this.assessedAt,
  });

  /// Get health grade
  String getGrade(String locale) {
    if (overallScore >= 90) return locale == 'ar' ? 'ممتاز' : 'Excellent';
    if (overallScore >= 75) return locale == 'ar' ? 'جيد' : 'Good';
    if (overallScore >= 50) return locale == 'ar' ? 'متوسط' : 'Fair';
    if (overallScore >= 25) return locale == 'ar' ? 'ضعيف' : 'Poor';
    return locale == 'ar' ? 'حرج' : 'Critical';
  }

  List<String> getIssues(String locale) {
    return locale == 'ar' && issuesAr.isNotEmpty ? issuesAr : issues;
  }

  List<String> getRecommendations(String locale) {
    return locale == 'ar' && recommendationsAr.isNotEmpty
        ? recommendationsAr
        : recommendations;
  }

  factory EquipmentHealthStatus.fromJson(Map<String, dynamic> json) {
    return EquipmentHealthStatus(
      equipmentId: json['equipment_id'] as String,
      overallScore: json['overall_score'] as int,
      fuelScore: json['fuel_score'] as int,
      maintenanceScore: json['maintenance_score'] as int,
      usageScore: json['usage_score'] as int,
      issues: json['issues'] != null
          ? List<String>.from(json['issues'] as List)
          : [],
      issuesAr: json['issues_ar'] != null
          ? List<String>.from(json['issues_ar'] as List)
          : [],
      recommendations: json['recommendations'] != null
          ? List<String>.from(json['recommendations'] as List)
          : [],
      recommendationsAr: json['recommendations_ar'] != null
          ? List<String>.from(json['recommendations_ar'] as List)
          : [],
      assessedAt: DateTime.tryParse(json['assessed_at'] as String) ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() => {
        'equipment_id': equipmentId,
        'overall_score': overallScore,
        'fuel_score': fuelScore,
        'maintenance_score': maintenanceScore,
        'usage_score': usageScore,
        'issues': issues,
        'issues_ar': issuesAr,
        'recommendations': recommendations,
        'recommendations_ar': recommendationsAr,
        'assessed_at': assessedAt.toIso8601String(),
      };
}

/// إحصائيات المعدات - Equipment Statistics
@immutable
class EquipmentStats {
  final int total;
  final Map<String, int> byType;
  final Map<String, int> byStatus;
  final int operational;
  final int maintenance;
  final int inactive;
  final int lowFuel;
  final int needsMaintenance;
  final double totalValue;
  final double totalHours;
  final DateTime? lastUpdated;

  const EquipmentStats({
    required this.total,
    required this.byType,
    required this.byStatus,
    required this.operational,
    required this.maintenance,
    required this.inactive,
    this.lowFuel = 0,
    this.needsMaintenance = 0,
    this.totalValue = 0.0,
    this.totalHours = 0.0,
    this.lastUpdated,
  });

  /// Calculate operational percentage
  double get operationalPercentage =>
      total > 0 ? (operational / total) * 100 : 0;

  factory EquipmentStats.fromJson(Map<String, dynamic> json) {
    return EquipmentStats(
      total: json['total'] as int,
      byType: Map<String, int>.from(json['by_type'] as Map),
      byStatus: Map<String, int>.from(json['by_status'] as Map),
      operational: json['operational'] as int,
      maintenance: json['maintenance'] as int,
      inactive: json['inactive'] as int,
      lowFuel: json['low_fuel'] as int? ?? 0,
      needsMaintenance: json['needs_maintenance'] as int? ?? 0,
      totalValue: (json['total_value'] as num?)?.toDouble() ?? 0.0,
      totalHours: (json['total_hours'] as num?)?.toDouble() ?? 0.0,
      lastUpdated: json['last_updated'] != null
          ? DateTime.tryParse(json['last_updated'] as String) ?? DateTime.now()
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'total': total,
        'by_type': byType,
        'by_status': byStatus,
        'operational': operational,
        'maintenance': maintenance,
        'inactive': inactive,
        'low_fuel': lowFuel,
        'needs_maintenance': needsMaintenance,
        'total_value': totalValue,
        'total_hours': totalHours,
        'last_updated': lastUpdated?.toIso8601String(),
      };

  factory EquipmentStats.empty() {
    return const EquipmentStats(
      total: 0,
      byType: {},
      byStatus: {},
      operational: 0,
      maintenance: 0,
      inactive: 0,
    );
  }
}
