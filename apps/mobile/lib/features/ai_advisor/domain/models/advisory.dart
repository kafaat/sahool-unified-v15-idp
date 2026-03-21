/// AI Advisory Domain Model
/// نموذج التوصية من المستشار الذكي
///
/// Represents an AI-generated agricultural advisory/recommendation

import 'package:flutter/foundation.dart';

/// Advisory type enum
/// نوع التوصية
enum AdvisoryType {
  irrigation,      // ري
  fertilization,   // تسميد
  pestControl,     // مكافحة الآفات
  diseaseControl,  // مكافحة الأمراض
  harvest,         // حصاد
  planting,        // زراعة
  weather,         // طقس
  general,         // عام
}

/// Advisory priority enum
/// أولوية التوصية
enum AdvisoryPriority {
  critical,  // حرج - خلال 6 ساعات
  high,      // عالي - خلال 24 ساعة
  medium,    // متوسط - خلال أسبوع
  low,       // منخفض - للعلم
}

/// Advisory status enum
/// حالة التوصية
enum AdvisoryStatus {
  pending,    // قيد الانتظار
  applied,    // تم التطبيق
  dismissed,  // تم التجاهل
  expired,    // منتهية الصلاحية
}

/// AI Advisory Model
/// نموذج التوصية الذكية
@immutable
class Advisory {
  /// Unique identifier
  final String id;

  /// Advisory type
  final AdvisoryType type;

  /// Priority level
  final AdvisoryPriority priority;

  /// Current status
  final AdvisoryStatus status;

  /// Title in English
  final String title;

  /// Title in Arabic
  final String titleAr;

  /// Detailed description in English
  final String description;

  /// Detailed description in Arabic
  final String descriptionAr;

  /// Summary/short description
  final String? summary;

  /// Summary in Arabic
  final String? summaryAr;

  /// Recommended actions (list of steps)
  final List<String> actions;

  /// Recommended actions in Arabic
  final List<String> actionsAr;

  /// Confidence score (0.0 to 1.0)
  final double confidence;

  /// Data sources used for the recommendation
  final List<String> sources;

  /// Field ID if specific to a field
  final String? fieldId;

  /// Field name
  final String? fieldName;

  /// Crop type
  final String? cropType;

  /// Crop type in Arabic
  final String? cropTypeAr;

  /// Economic impact estimate (cost/benefit)
  final EconomicImpact? economicImpact;

  /// Weather conditions considered
  final Map<String, dynamic>? weatherContext;

  /// Soil conditions considered
  final Map<String, dynamic>? soilContext;

  /// Timing recommendation
  final AdvisoryTiming? timing;

  /// Created timestamp
  final DateTime createdAt;

  /// Expiry timestamp
  final DateTime? expiresAt;

  /// Applied timestamp
  final DateTime? appliedAt;

  /// User feedback
  final AdvisoryFeedbackSummary? feedback;

  /// Additional metadata
  final Map<String, dynamic>? metadata;

  const Advisory({
    required this.id,
    required this.type,
    required this.priority,
    required this.status,
    required this.title,
    required this.titleAr,
    required this.description,
    required this.descriptionAr,
    this.summary,
    this.summaryAr,
    required this.actions,
    required this.actionsAr,
    required this.confidence,
    required this.sources,
    this.fieldId,
    this.fieldName,
    this.cropType,
    this.cropTypeAr,
    this.economicImpact,
    this.weatherContext,
    this.soilContext,
    this.timing,
    required this.createdAt,
    this.expiresAt,
    this.appliedAt,
    this.feedback,
    this.metadata,
  });

  /// Create from JSON
  factory Advisory.fromJson(Map<String, dynamic> json) {
    return Advisory(
      id: json['id'] as String? ?? json['_id'] as String? ?? '',
      type: _parseAdvisoryType(json['type'] as String?),
      priority: _parseAdvisoryPriority(json['priority'] as String?),
      status: _parseAdvisoryStatus(json['status'] as String?),
      title: json['title'] as String? ?? '',
      titleAr: json['title_ar'] as String? ?? json['title'] as String? ?? '',
      description: json['description'] as String? ?? '',
      descriptionAr: json['description_ar'] as String? ?? json['description'] as String? ?? '',
      summary: json['summary'] as String?,
      summaryAr: json['summary_ar'] as String?,
      actions: (json['actions'] as List?)?.cast<String>() ?? [],
      actionsAr: (json['actions_ar'] as List?)?.cast<String>() ??
                 (json['actions'] as List?)?.cast<String>() ?? [],
      confidence: ((json['confidence'] ?? 0.8) as num).toDouble(),
      sources: (json['sources'] as List?)?.cast<String>() ?? [],
      fieldId: json['field_id'] as String?,
      fieldName: json['field_name'] as String?,
      cropType: json['crop_type'] as String?,
      cropTypeAr: json['crop_type_ar'] as String?,
      economicImpact: json['economic_impact'] != null
          ? EconomicImpact.fromJson(json['economic_impact'] as Map<String, dynamic>)
          : null,
      weatherContext: json['weather_context'] as Map<String, dynamic>?,
      soilContext: json['soil_context'] as Map<String, dynamic>?,
      timing: json['timing'] != null
          ? AdvisoryTiming.fromJson(json['timing'] as Map<String, dynamic>)
          : null,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
      expiresAt: json['expires_at'] != null
          ? DateTime.parse(json['expires_at'] as String)
          : null,
      appliedAt: json['applied_at'] != null
          ? DateTime.parse(json['applied_at'] as String)
          : null,
      feedback: json['feedback'] != null
          ? AdvisoryFeedbackSummary.fromJson(json['feedback'] as Map<String, dynamic>)
          : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() => {
    'id': id,
    'type': type.name,
    'priority': priority.name,
    'status': status.name,
    'title': title,
    'title_ar': titleAr,
    'description': description,
    'description_ar': descriptionAr,
    'summary': summary,
    'summary_ar': summaryAr,
    'actions': actions,
    'actions_ar': actionsAr,
    'confidence': confidence,
    'sources': sources,
    'field_id': fieldId,
    'field_name': fieldName,
    'crop_type': cropType,
    'crop_type_ar': cropTypeAr,
    'economic_impact': economicImpact?.toJson(),
    'weather_context': weatherContext,
    'soil_context': soilContext,
    'timing': timing?.toJson(),
    'created_at': createdAt.toIso8601String(),
    'expires_at': expiresAt?.toIso8601String(),
    'applied_at': appliedAt?.toIso8601String(),
    'feedback': feedback?.toJson(),
    'metadata': metadata,
  };

  /// Copy with
  Advisory copyWith({
    String? id,
    AdvisoryType? type,
    AdvisoryPriority? priority,
    AdvisoryStatus? status,
    String? title,
    String? titleAr,
    String? description,
    String? descriptionAr,
    String? summary,
    String? summaryAr,
    List<String>? actions,
    List<String>? actionsAr,
    double? confidence,
    List<String>? sources,
    String? fieldId,
    String? fieldName,
    String? cropType,
    String? cropTypeAr,
    EconomicImpact? economicImpact,
    Map<String, dynamic>? weatherContext,
    Map<String, dynamic>? soilContext,
    AdvisoryTiming? timing,
    DateTime? createdAt,
    DateTime? expiresAt,
    DateTime? appliedAt,
    AdvisoryFeedbackSummary? feedback,
    Map<String, dynamic>? metadata,
  }) {
    return Advisory(
      id: id ?? this.id,
      type: type ?? this.type,
      priority: priority ?? this.priority,
      status: status ?? this.status,
      title: title ?? this.title,
      titleAr: titleAr ?? this.titleAr,
      description: description ?? this.description,
      descriptionAr: descriptionAr ?? this.descriptionAr,
      summary: summary ?? this.summary,
      summaryAr: summaryAr ?? this.summaryAr,
      actions: actions ?? this.actions,
      actionsAr: actionsAr ?? this.actionsAr,
      confidence: confidence ?? this.confidence,
      sources: sources ?? this.sources,
      fieldId: fieldId ?? this.fieldId,
      fieldName: fieldName ?? this.fieldName,
      cropType: cropType ?? this.cropType,
      cropTypeAr: cropTypeAr ?? this.cropTypeAr,
      economicImpact: economicImpact ?? this.economicImpact,
      weatherContext: weatherContext ?? this.weatherContext,
      soilContext: soilContext ?? this.soilContext,
      timing: timing ?? this.timing,
      createdAt: createdAt ?? this.createdAt,
      expiresAt: expiresAt ?? this.expiresAt,
      appliedAt: appliedAt ?? this.appliedAt,
      feedback: feedback ?? this.feedback,
      metadata: metadata ?? this.metadata,
    );
  }

  /// Get localized title
  String getLocalizedTitle(String locale) {
    return locale == 'ar' ? titleAr : title;
  }

  /// Get localized description
  String getLocalizedDescription(String locale) {
    return locale == 'ar' ? descriptionAr : description;
  }

  /// Get localized actions
  List<String> getLocalizedActions(String locale) {
    return locale == 'ar' ? actionsAr : actions;
  }

  /// Check if advisory is expired
  bool get isExpired {
    if (expiresAt == null) return false;
    return DateTime.now().isAfter(expiresAt!);
  }

  /// Check if advisory requires urgent action
  bool get isUrgent {
    return priority == AdvisoryPriority.critical || priority == AdvisoryPriority.high;
  }

  /// Get priority color (hex color string)
  String get priorityColorHex {
    switch (priority) {
      case AdvisoryPriority.critical:
        return '#DC2626'; // Red
      case AdvisoryPriority.high:
        return '#F59E0B'; // Orange
      case AdvisoryPriority.medium:
        return '#3B82F6'; // Blue
      case AdvisoryPriority.low:
        return '#10B981'; // Green
    }
  }

  /// Get type icon name
  String get typeIconName {
    switch (type) {
      case AdvisoryType.irrigation:
        return 'water_drop';
      case AdvisoryType.fertilization:
        return 'compost';
      case AdvisoryType.pestControl:
        return 'pest_control';
      case AdvisoryType.diseaseControl:
        return 'healing';
      case AdvisoryType.harvest:
        return 'agriculture';
      case AdvisoryType.planting:
        return 'eco';
      case AdvisoryType.weather:
        return 'cloud';
      case AdvisoryType.general:
        return 'lightbulb';
    }
  }

  /// Get type label in Arabic
  String get typeAr {
    switch (type) {
      case AdvisoryType.irrigation:
        return 'ري';
      case AdvisoryType.fertilization:
        return 'تسميد';
      case AdvisoryType.pestControl:
        return 'مكافحة الآفات';
      case AdvisoryType.diseaseControl:
        return 'مكافحة الأمراض';
      case AdvisoryType.harvest:
        return 'حصاد';
      case AdvisoryType.planting:
        return 'زراعة';
      case AdvisoryType.weather:
        return 'طقس';
      case AdvisoryType.general:
        return 'عام';
    }
  }

  /// Get priority label in Arabic
  String get priorityAr {
    switch (priority) {
      case AdvisoryPriority.critical:
        return 'حرج';
      case AdvisoryPriority.high:
        return 'عالي';
      case AdvisoryPriority.medium:
        return 'متوسط';
      case AdvisoryPriority.low:
        return 'منخفض';
    }
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Advisory && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() => 'Advisory($id: $title)';
}

/// Economic Impact Model
/// نموذج التأثير الاقتصادي
@immutable
class EconomicImpact {
  /// Estimated cost of implementing the recommendation
  final double? cost;

  /// Currency
  final String currency;

  /// Expected benefit/savings
  final double? expectedBenefit;

  /// Return on investment percentage
  final double? roi;

  /// Cost description
  final String? costDescription;

  /// Cost description in Arabic
  final String? costDescriptionAr;

  /// Benefit description
  final String? benefitDescription;

  /// Benefit description in Arabic
  final String? benefitDescriptionAr;

  const EconomicImpact({
    this.cost,
    this.currency = 'SAR',
    this.expectedBenefit,
    this.roi,
    this.costDescription,
    this.costDescriptionAr,
    this.benefitDescription,
    this.benefitDescriptionAr,
  });

  factory EconomicImpact.fromJson(Map<String, dynamic> json) {
    return EconomicImpact(
      cost: (json['cost'] as num?)?.toDouble(),
      currency: json['currency'] as String? ?? 'SAR',
      expectedBenefit: (json['expected_benefit'] as num?)?.toDouble(),
      roi: (json['roi'] as num?)?.toDouble(),
      costDescription: json['cost_description'] as String?,
      costDescriptionAr: json['cost_description_ar'] as String?,
      benefitDescription: json['benefit_description'] as String?,
      benefitDescriptionAr: json['benefit_description_ar'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'cost': cost,
    'currency': currency,
    'expected_benefit': expectedBenefit,
    'roi': roi,
    'cost_description': costDescription,
    'cost_description_ar': costDescriptionAr,
    'benefit_description': benefitDescription,
    'benefit_description_ar': benefitDescriptionAr,
  };
}

/// Advisory Timing Model
/// نموذج توقيت التوصية
@immutable
class AdvisoryTiming {
  /// Recommended start time
  final DateTime? startTime;

  /// Recommended end time (deadline)
  final DateTime? endTime;

  /// Best time of day
  final String? bestTimeOfDay;

  /// Best time of day in Arabic
  final String? bestTimeOfDayAr;

  /// Duration estimate
  final Duration? estimatedDuration;

  /// Weather window description
  final String? weatherWindow;

  /// Weather window in Arabic
  final String? weatherWindowAr;

  const AdvisoryTiming({
    this.startTime,
    this.endTime,
    this.bestTimeOfDay,
    this.bestTimeOfDayAr,
    this.estimatedDuration,
    this.weatherWindow,
    this.weatherWindowAr,
  });

  factory AdvisoryTiming.fromJson(Map<String, dynamic> json) {
    return AdvisoryTiming(
      startTime: json['start_time'] != null
          ? DateTime.parse(json['start_time'] as String)
          : null,
      endTime: json['end_time'] != null
          ? DateTime.parse(json['end_time'] as String)
          : null,
      bestTimeOfDay: json['best_time_of_day'] as String?,
      bestTimeOfDayAr: json['best_time_of_day_ar'] as String?,
      estimatedDuration: json['estimated_duration_minutes'] != null
          ? Duration(minutes: json['estimated_duration_minutes'] as int)
          : null,
      weatherWindow: json['weather_window'] as String?,
      weatherWindowAr: json['weather_window_ar'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'start_time': startTime?.toIso8601String(),
    'end_time': endTime?.toIso8601String(),
    'best_time_of_day': bestTimeOfDay,
    'best_time_of_day_ar': bestTimeOfDayAr,
    'estimated_duration_minutes': estimatedDuration?.inMinutes,
    'weather_window': weatherWindow,
    'weather_window_ar': weatherWindowAr,
  };
}

/// Advisory Feedback Summary
/// ملخص ردود الفعل على التوصية
@immutable
class AdvisoryFeedbackSummary {
  /// User rating (1-5)
  final int? rating;

  /// Thumbs up/down
  final bool? thumbsUp;

  /// Outcome status
  final String? outcome;

  /// Comment
  final String? comment;

  const AdvisoryFeedbackSummary({
    this.rating,
    this.thumbsUp,
    this.outcome,
    this.comment,
  });

  factory AdvisoryFeedbackSummary.fromJson(Map<String, dynamic> json) {
    return AdvisoryFeedbackSummary(
      rating: json['rating'] as int?,
      thumbsUp: json['thumbs_up'] as bool?,
      outcome: json['outcome'] as String?,
      comment: json['comment'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'rating': rating,
    'thumbs_up': thumbsUp,
    'outcome': outcome,
    'comment': comment,
  };
}

// Helper functions

AdvisoryType _parseAdvisoryType(String? type) {
  switch (type?.toLowerCase()) {
    case 'irrigation':
      return AdvisoryType.irrigation;
    case 'fertilization':
    case 'fertilizer':
      return AdvisoryType.fertilization;
    case 'pest_control':
    case 'pestcontrol':
      return AdvisoryType.pestControl;
    case 'disease_control':
    case 'diseasecontrol':
      return AdvisoryType.diseaseControl;
    case 'harvest':
      return AdvisoryType.harvest;
    case 'planting':
      return AdvisoryType.planting;
    case 'weather':
      return AdvisoryType.weather;
    case 'general':
    default:
      return AdvisoryType.general;
  }
}

AdvisoryPriority _parseAdvisoryPriority(String? priority) {
  switch (priority?.toLowerCase()) {
    case 'critical':
      return AdvisoryPriority.critical;
    case 'high':
      return AdvisoryPriority.high;
    case 'medium':
      return AdvisoryPriority.medium;
    case 'low':
    default:
      return AdvisoryPriority.low;
  }
}

AdvisoryStatus _parseAdvisoryStatus(String? status) {
  switch (status?.toLowerCase()) {
    case 'applied':
      return AdvisoryStatus.applied;
    case 'dismissed':
      return AdvisoryStatus.dismissed;
    case 'expired':
      return AdvisoryStatus.expired;
    case 'pending':
    default:
      return AdvisoryStatus.pending;
  }
}
