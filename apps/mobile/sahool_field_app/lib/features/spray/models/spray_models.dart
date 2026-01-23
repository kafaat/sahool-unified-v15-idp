/// Spray Advisor Models - نماذج مستشار الرش
/// Spray timing and recommendations - توقيت الرش والتوصيات
library;

import 'package:flutter/foundation.dart';

// ═════════════════════════════════════════════════════════════════════════════
// Enums
// ═════════════════════════════════════════════════════════════════════════════

/// نوع الرش
enum SprayType {
  herbicide('herbicide', 'مبيد أعشاب', 'Herbicide'),
  fungicide('fungicide', 'مبيد فطري', 'Fungicide'),
  insecticide('insecticide', 'مبيد حشري', 'Insecticide'),
  foliar('foliar', 'سماد ورقي', 'Foliar Fertilizer');

  final String value;
  final String nameAr;
  final String nameEn;

  const SprayType(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static SprayType fromString(String value) {
    return SprayType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => SprayType.herbicide,
    );
  }
}

/// حالة نافذة الرش
enum SprayWindowStatus {
  optimal('optimal', 'مثالي', 'Optimal'),
  caution('caution', 'حذر', 'Caution'),
  avoid('avoid', 'تجنب', 'Avoid');

  final String value;
  final String nameAr;
  final String nameEn;

  const SprayWindowStatus(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static SprayWindowStatus fromString(String value) {
    return SprayWindowStatus.values.firstWhere(
      (e) => e.value == value,
      orElse: () => SprayWindowStatus.caution,
    );
  }
}

/// حالة التوصية
enum RecommendationStatus {
  active('active', 'نشط', 'Active'),
  completed('completed', 'مكتمل', 'Completed'),
  expired('expired', 'منتهي', 'Expired'),
  cancelled('cancelled', 'ملغي', 'Cancelled');

  final String value;
  final String nameAr;
  final String nameEn;

  const RecommendationStatus(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static RecommendationStatus fromString(String value) {
    return RecommendationStatus.values.firstWhere(
      (e) => e.value == value,
      orElse: () => RecommendationStatus.active,
    );
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// Models
// ═════════════════════════════════════════════════════════════════════════════

/// نموذج الظروف الجوية
@immutable
class WeatherCondition {
  final String conditionId;
  final DateTime timestamp;
  final double temperature; // درجة الحرارة (°C)
  final double humidity; // الرطوبة (%)
  final double windSpeed; // سرعة الرياح (km/h)
  final String windDirection; // اتجاه الرياح
  final String? windDirectionAr;
  final double rainProbability; // احتمالية المطر (%)
  final double? rainfall; // كمية الأمطار (mm)
  final double? pressure; // الضغط الجوي (hPa)
  final String condition; // الحالة الجوية (clear, cloudy, etc.)
  final String? conditionAr;
  final Map<String, dynamic>? metadata;

  const WeatherCondition({
    required this.conditionId,
    required this.timestamp,
    required this.temperature,
    required this.humidity,
    required this.windSpeed,
    required this.windDirection,
    this.windDirectionAr,
    required this.rainProbability,
    this.rainfall,
    this.pressure,
    required this.condition,
    this.conditionAr,
    this.metadata,
  });

  /// Get wind direction based on locale
  String getWindDirection(String locale) {
    return locale == 'ar' && windDirectionAr != null ? windDirectionAr! : windDirection;
  }

  /// Get condition based on locale
  String getCondition(String locale) {
    return locale == 'ar' && conditionAr != null ? conditionAr! : condition;
  }

  /// هل الظروف مناسبة للرش؟
  bool get isSuitableForSpraying {
    // الظروف المثالية:
    // - درجة الحرارة: 15-25°C
    // - الرطوبة: 50-70%
    // - سرعة الرياح: < 15 km/h
    // - احتمالية المطر: < 20%
    return temperature >= 15 &&
        temperature <= 25 &&
        humidity >= 50 &&
        humidity <= 70 &&
        windSpeed < 15 &&
        rainProbability < 20;
  }

  /// مؤشر ملاءمة الرش (0-100)
  int get spraySuitabilityScore {
    int score = 100;

    // درجة الحرارة
    if (temperature < 10 || temperature > 30) {
      score -= 40;
    } else if (temperature < 15 || temperature > 25) {
      score -= 20;
    }

    // الرطوبة
    if (humidity < 40 || humidity > 80) {
      score -= 30;
    } else if (humidity < 50 || humidity > 70) {
      score -= 15;
    }

    // سرعة الرياح
    if (windSpeed > 20) {
      score -= 40;
    } else if (windSpeed > 15) {
      score -= 20;
    }

    // احتمالية المطر
    if (rainProbability > 40) {
      score -= 30;
    } else if (rainProbability > 20) {
      score -= 15;
    }

    return score.clamp(0, 100);
  }

  factory WeatherCondition.fromJson(Map<String, dynamic> json) {
    return WeatherCondition(
      conditionId: json['condition_id'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      temperature: (json['temperature'] as num).toDouble(),
      humidity: (json['humidity'] as num).toDouble(),
      windSpeed: (json['wind_speed'] as num).toDouble(),
      windDirection: json['wind_direction'] as String,
      windDirectionAr: json['wind_direction_ar'] as String?,
      rainProbability: (json['rain_probability'] as num).toDouble(),
      rainfall: (json['rainfall'] as num?)?.toDouble(),
      pressure: (json['pressure'] as num?)?.toDouble(),
      condition: json['condition'] as String,
      conditionAr: json['condition_ar'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'condition_id': conditionId,
        'timestamp': timestamp.toIso8601String(),
        'temperature': temperature,
        'humidity': humidity,
        'wind_speed': windSpeed,
        'wind_direction': windDirection,
        'wind_direction_ar': windDirectionAr,
        'rain_probability': rainProbability,
        'rainfall': rainfall,
        'pressure': pressure,
        'condition': condition,
        'condition_ar': conditionAr,
        'metadata': metadata,
      };
}

/// نموذج منتج الرش
@immutable
class SprayProduct {
  final String productId;
  final String name;
  final String? nameAr;
  final SprayType type;
  final String manufacturer;
  final String? manufacturerAr;
  final String activeIngredient;
  final String? activeIngredientAr;
  final double concentration; // التركيز (%)
  final String unit; // وحدة القياس (L/ha, kg/ha, ml/L)
  final String? unitAr;
  final double recommendedRate; // المعدل الموصى به
  final double minRate; // الحد الأدنى
  final double maxRate; // الحد الأقصى
  final int? phi; // Pre-Harvest Interval (days) - فترة ما قبل الحصاد
  final int? rei; // Re-Entry Interval (hours) - فترة إعادة الدخول
  final String? targetPest; // الآفة المستهدفة
  final String? targetPestAr;
  final String? targetDisease; // المرض المستهدف
  final String? targetDiseaseAr;
  final String? notes;
  final String? notesAr;
  final bool isYemenProduct; // هل هو منتج يمني؟
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;
  final DateTime updatedAt;

  const SprayProduct({
    required this.productId,
    required this.name,
    this.nameAr,
    required this.type,
    required this.manufacturer,
    this.manufacturerAr,
    required this.activeIngredient,
    this.activeIngredientAr,
    required this.concentration,
    required this.unit,
    this.unitAr,
    required this.recommendedRate,
    required this.minRate,
    required this.maxRate,
    this.phi,
    this.rei,
    this.targetPest,
    this.targetPestAr,
    this.targetDisease,
    this.targetDiseaseAr,
    this.notes,
    this.notesAr,
    this.isYemenProduct = false,
    this.metadata,
    required this.createdAt,
    required this.updatedAt,
  });

  /// Get product name based on locale
  String getDisplayName(String locale) {
    return locale == 'ar' && nameAr != null ? nameAr! : name;
  }

  /// Get manufacturer based on locale
  String getManufacturer(String locale) {
    return locale == 'ar' && manufacturerAr != null ? manufacturerAr! : manufacturer;
  }

  /// Get active ingredient based on locale
  String getActiveIngredient(String locale) {
    return locale == 'ar' && activeIngredientAr != null ? activeIngredientAr! : activeIngredient;
  }

  /// Get unit based on locale
  String getUnit(String locale) {
    return locale == 'ar' && unitAr != null ? unitAr! : unit;
  }

  /// Get target pest/disease based on locale
  String? getTarget(String locale) {
    if (type == SprayType.insecticide || type == SprayType.herbicide) {
      return locale == 'ar' && targetPestAr != null ? targetPestAr : targetPest;
    } else {
      return locale == 'ar' && targetDiseaseAr != null ? targetDiseaseAr : targetDisease;
    }
  }

  /// Get notes based on locale
  String? getNotes(String locale) {
    return locale == 'ar' && notesAr != null ? notesAr : notes;
  }

  factory SprayProduct.fromJson(Map<String, dynamic> json) {
    return SprayProduct(
      productId: json['product_id'] as String,
      name: json['name'] as String,
      nameAr: json['name_ar'] as String?,
      type: SprayType.fromString(json['type'] as String),
      manufacturer: json['manufacturer'] as String,
      manufacturerAr: json['manufacturer_ar'] as String?,
      activeIngredient: json['active_ingredient'] as String,
      activeIngredientAr: json['active_ingredient_ar'] as String?,
      concentration: (json['concentration'] as num).toDouble(),
      unit: json['unit'] as String,
      unitAr: json['unit_ar'] as String?,
      recommendedRate: (json['recommended_rate'] as num).toDouble(),
      minRate: (json['min_rate'] as num).toDouble(),
      maxRate: (json['max_rate'] as num).toDouble(),
      phi: json['phi'] as int?,
      rei: json['rei'] as int?,
      targetPest: json['target_pest'] as String?,
      targetPestAr: json['target_pest_ar'] as String?,
      targetDisease: json['target_disease'] as String?,
      targetDiseaseAr: json['target_disease_ar'] as String?,
      notes: json['notes'] as String?,
      notesAr: json['notes_ar'] as String?,
      isYemenProduct: json['is_yemen_product'] as bool? ?? false,
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'product_id': productId,
        'name': name,
        'name_ar': nameAr,
        'type': type.value,
        'manufacturer': manufacturer,
        'manufacturer_ar': manufacturerAr,
        'active_ingredient': activeIngredient,
        'active_ingredient_ar': activeIngredientAr,
        'concentration': concentration,
        'unit': unit,
        'unit_ar': unitAr,
        'recommended_rate': recommendedRate,
        'min_rate': minRate,
        'max_rate': maxRate,
        'phi': phi,
        'rei': rei,
        'target_pest': targetPest,
        'target_pest_ar': targetPestAr,
        'target_disease': targetDisease,
        'target_disease_ar': targetDiseaseAr,
        'notes': notes,
        'notes_ar': notesAr,
        'is_yemen_product': isYemenProduct,
        'metadata': metadata,
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
      };
}

/// نموذج نافذة الرش المثلى
@immutable
class SprayWindow {
  final String windowId;
  final DateTime startTime;
  final DateTime endTime;
  final SprayWindowStatus status;
  final WeatherCondition weatherCondition;
  final int confidenceScore; // درجة الثقة (0-100)
  final String? reason; // سبب التصنيف
  final String? reasonAr;
  final List<String> warnings; // تحذيرات
  final List<String> warningsAr;
  final Map<String, dynamic>? metadata;

  const SprayWindow({
    required this.windowId,
    required this.startTime,
    required this.endTime,
    required this.status,
    required this.weatherCondition,
    required this.confidenceScore,
    this.reason,
    this.reasonAr,
    this.warnings = const [],
    this.warningsAr = const [],
    this.metadata,
  });

  /// Get reason based on locale
  String? getReason(String locale) {
    return locale == 'ar' && reasonAr != null ? reasonAr : reason;
  }

  /// Get warnings based on locale
  List<String> getWarnings(String locale) {
    return locale == 'ar' && warningsAr.isNotEmpty ? warningsAr : warnings;
  }

  /// مدة النافذة بالساعات
  int get durationHours {
    return endTime.difference(startTime).inHours;
  }

  /// هل النافذة حالية؟
  bool get isActive {
    final now = DateTime.now();
    return now.isAfter(startTime) && now.isBefore(endTime);
  }

  /// هل النافذة في المستقبل؟
  bool get isFuture {
    return DateTime.now().isBefore(startTime);
  }

  /// هل النافذة منتهية؟
  bool get isExpired {
    return DateTime.now().isAfter(endTime);
  }

  factory SprayWindow.fromJson(Map<String, dynamic> json) {
    return SprayWindow(
      windowId: json['window_id'] as String,
      startTime: DateTime.parse(json['start_time'] as String),
      endTime: DateTime.parse(json['end_time'] as String),
      status: SprayWindowStatus.fromString(json['status'] as String),
      weatherCondition: WeatherCondition.fromJson(json['weather_condition'] as Map<String, dynamic>),
      confidenceScore: json['confidence_score'] as int,
      reason: json['reason'] as String?,
      reasonAr: json['reason_ar'] as String?,
      warnings: (json['warnings'] as List?)?.map((e) => e as String).toList() ?? [],
      warningsAr: (json['warnings_ar'] as List?)?.map((e) => e as String).toList() ?? [],
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'window_id': windowId,
        'start_time': startTime.toIso8601String(),
        'end_time': endTime.toIso8601String(),
        'status': status.value,
        'weather_condition': weatherCondition.toJson(),
        'confidence_score': confidenceScore,
        'reason': reason,
        'reason_ar': reasonAr,
        'warnings': warnings,
        'warnings_ar': warningsAr,
        'metadata': metadata,
      };
}

/// نموذج توصية الرش
@immutable
class SprayRecommendation {
  final String recommendationId;
  final String tenantId;
  final String fieldId;
  final String fieldName;
  final String? fieldNameAr;
  final String title;
  final String? titleAr;
  final String description;
  final String? descriptionAr;
  final SprayType sprayType;
  final RecommendationStatus status;
  final SprayProduct? recommendedProduct;
  final List<SprayProduct> alternativeProducts;
  final double recommendedRate; // معدل الرش الموصى به
  final String unit;
  final String? unitAr;
  final double? estimatedArea; // المساحة المقدرة (ha)
  final double? totalQuantity; // الكمية الإجمالية
  final double? estimatedCost; // التكلفة المقدرة
  final List<SprayWindow> optimalWindows; // نوافذ الرش المثلى
  final DateTime? targetDate; // التاريخ المستهدف
  final DateTime? completedDate; // تاريخ الإكمال
  final String? createdBy;
  final String? createdByName;
  final int priority; // الأولوية (1-5)
  final String? notes;
  final String? notesAr;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;
  final DateTime updatedAt;

  const SprayRecommendation({
    required this.recommendationId,
    required this.tenantId,
    required this.fieldId,
    required this.fieldName,
    this.fieldNameAr,
    required this.title,
    this.titleAr,
    required this.description,
    this.descriptionAr,
    required this.sprayType,
    required this.status,
    this.recommendedProduct,
    this.alternativeProducts = const [],
    required this.recommendedRate,
    required this.unit,
    this.unitAr,
    this.estimatedArea,
    this.totalQuantity,
    this.estimatedCost,
    this.optimalWindows = const [],
    this.targetDate,
    this.completedDate,
    this.createdBy,
    this.createdByName,
    this.priority = 3,
    this.notes,
    this.notesAr,
    this.metadata,
    required this.createdAt,
    required this.updatedAt,
  });

  /// Get title based on locale
  String getTitle(String locale) {
    return locale == 'ar' && titleAr != null ? titleAr! : title;
  }

  /// Get description based on locale
  String getDescription(String locale) {
    return locale == 'ar' && descriptionAr != null ? descriptionAr! : description;
  }

  /// Get field name based on locale
  String getFieldName(String locale) {
    return locale == 'ar' && fieldNameAr != null ? fieldNameAr! : fieldName;
  }

  /// Get unit based on locale
  String getUnit(String locale) {
    return locale == 'ar' && unitAr != null ? unitAr! : unit;
  }

  /// Get notes based on locale
  String? getNotes(String locale) {
    return locale == 'ar' && notesAr != null ? notesAr : notes;
  }

  /// Get next optimal spray window
  SprayWindow? get nextOptimalWindow {
    final now = DateTime.now();
    try {
      return optimalWindows.firstWhere(
        (w) => w.endTime.isAfter(now) && w.status == SprayWindowStatus.optimal,
      );
    } catch (_) {
      return null;
    }
  }

  /// هل التوصية نشطة؟
  bool get isActive => status == RecommendationStatus.active;

  /// هل التوصية مكتملة؟
  bool get isCompleted => status == RecommendationStatus.completed;

  /// هل التوصية منتهية؟
  bool get isExpired => status == RecommendationStatus.expired;

  /// الأيام المتبقية حتى التاريخ المستهدف
  int? get daysUntilTarget {
    if (targetDate == null) return null;
    return targetDate!.difference(DateTime.now()).inDays;
  }

  factory SprayRecommendation.fromJson(Map<String, dynamic> json) {
    return SprayRecommendation(
      recommendationId: json['recommendation_id'] as String,
      tenantId: json['tenant_id'] as String,
      fieldId: json['field_id'] as String,
      fieldName: json['field_name'] as String,
      fieldNameAr: json['field_name_ar'] as String?,
      title: json['title'] as String,
      titleAr: json['title_ar'] as String?,
      description: json['description'] as String,
      descriptionAr: json['description_ar'] as String?,
      sprayType: SprayType.fromString(json['spray_type'] as String),
      status: RecommendationStatus.fromString(json['status'] as String),
      recommendedProduct: json['recommended_product'] != null
          ? SprayProduct.fromJson(json['recommended_product'] as Map<String, dynamic>)
          : null,
      alternativeProducts: (json['alternative_products'] as List?)
              ?.map((e) => SprayProduct.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      recommendedRate: (json['recommended_rate'] as num).toDouble(),
      unit: json['unit'] as String,
      unitAr: json['unit_ar'] as String?,
      estimatedArea: (json['estimated_area'] as num?)?.toDouble(),
      totalQuantity: (json['total_quantity'] as num?)?.toDouble(),
      estimatedCost: (json['estimated_cost'] as num?)?.toDouble(),
      optimalWindows: (json['optimal_windows'] as List?)
              ?.map((e) => SprayWindow.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      targetDate: json['target_date'] != null ? DateTime.parse(json['target_date'] as String) : null,
      completedDate:
          json['completed_date'] != null ? DateTime.parse(json['completed_date'] as String) : null,
      createdBy: json['created_by'] as String?,
      createdByName: json['created_by_name'] as String?,
      priority: json['priority'] as int? ?? 3,
      notes: json['notes'] as String?,
      notesAr: json['notes_ar'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'recommendation_id': recommendationId,
        'tenant_id': tenantId,
        'field_id': fieldId,
        'field_name': fieldName,
        'field_name_ar': fieldNameAr,
        'title': title,
        'title_ar': titleAr,
        'description': description,
        'description_ar': descriptionAr,
        'spray_type': sprayType.value,
        'status': status.value,
        'recommended_product': recommendedProduct?.toJson(),
        'alternative_products': alternativeProducts.map((e) => e.toJson()).toList(),
        'recommended_rate': recommendedRate,
        'unit': unit,
        'unit_ar': unitAr,
        'estimated_area': estimatedArea,
        'total_quantity': totalQuantity,
        'estimated_cost': estimatedCost,
        'optimal_windows': optimalWindows.map((e) => e.toJson()).toList(),
        'target_date': targetDate?.toIso8601String(),
        'completed_date': completedDate?.toIso8601String(),
        'created_by': createdBy,
        'created_by_name': createdByName,
        'priority': priority,
        'notes': notes,
        'notes_ar': notesAr,
        'metadata': metadata,
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
      };

  SprayRecommendation copyWith({
    String? recommendationId,
    String? tenantId,
    String? fieldId,
    String? fieldName,
    String? fieldNameAr,
    String? title,
    String? titleAr,
    String? description,
    String? descriptionAr,
    SprayType? sprayType,
    RecommendationStatus? status,
    SprayProduct? recommendedProduct,
    List<SprayProduct>? alternativeProducts,
    double? recommendedRate,
    String? unit,
    String? unitAr,
    double? estimatedArea,
    double? totalQuantity,
    double? estimatedCost,
    List<SprayWindow>? optimalWindows,
    DateTime? targetDate,
    DateTime? completedDate,
    String? createdBy,
    String? createdByName,
    int? priority,
    String? notes,
    String? notesAr,
    Map<String, dynamic>? metadata,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return SprayRecommendation(
      recommendationId: recommendationId ?? this.recommendationId,
      tenantId: tenantId ?? this.tenantId,
      fieldId: fieldId ?? this.fieldId,
      fieldName: fieldName ?? this.fieldName,
      fieldNameAr: fieldNameAr ?? this.fieldNameAr,
      title: title ?? this.title,
      titleAr: titleAr ?? this.titleAr,
      description: description ?? this.description,
      descriptionAr: descriptionAr ?? this.descriptionAr,
      sprayType: sprayType ?? this.sprayType,
      status: status ?? this.status,
      recommendedProduct: recommendedProduct ?? this.recommendedProduct,
      alternativeProducts: alternativeProducts ?? this.alternativeProducts,
      recommendedRate: recommendedRate ?? this.recommendedRate,
      unit: unit ?? this.unit,
      unitAr: unitAr ?? this.unitAr,
      estimatedArea: estimatedArea ?? this.estimatedArea,
      totalQuantity: totalQuantity ?? this.totalQuantity,
      estimatedCost: estimatedCost ?? this.estimatedCost,
      optimalWindows: optimalWindows ?? this.optimalWindows,
      targetDate: targetDate ?? this.targetDate,
      completedDate: completedDate ?? this.completedDate,
      createdBy: createdBy ?? this.createdBy,
      createdByName: createdByName ?? this.createdByName,
      priority: priority ?? this.priority,
      notes: notes ?? this.notes,
      notesAr: notesAr ?? this.notesAr,
      metadata: metadata ?? this.metadata,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

/// نموذج سجل تطبيق الرش
@immutable
class SprayApplicationLog {
  final String logId;
  final String tenantId;
  final String fieldId;
  final String fieldName;
  final String? fieldNameAr;
  final String? recommendationId;
  final SprayType sprayType;
  final SprayProduct product;
  final double appliedRate; // المعدل المطبق
  final String unit;
  final String? unitAr;
  final double area; // المساحة المطبقة (ha)
  final double totalQuantity; // الكمية الإجمالية
  final DateTime applicationDate; // تاريخ التطبيق
  final WeatherCondition weatherCondition; // الظروف الجوية وقت التطبيق
  final String? applicatorName; // اسم المطبق
  final String? equipmentUsed; // المعدة المستخدمة
  final String? equipmentUsedAr;
  final List<String> photoUrls; // صور التطبيق
  final String? notes;
  final String? notesAr;
  final String createdBy;
  final String? createdByName;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;
  final DateTime updatedAt;

  const SprayApplicationLog({
    required this.logId,
    required this.tenantId,
    required this.fieldId,
    required this.fieldName,
    this.fieldNameAr,
    this.recommendationId,
    required this.sprayType,
    required this.product,
    required this.appliedRate,
    required this.unit,
    this.unitAr,
    required this.area,
    required this.totalQuantity,
    required this.applicationDate,
    required this.weatherCondition,
    this.applicatorName,
    this.equipmentUsed,
    this.equipmentUsedAr,
    this.photoUrls = const [],
    this.notes,
    this.notesAr,
    required this.createdBy,
    this.createdByName,
    this.metadata,
    required this.createdAt,
    required this.updatedAt,
  });

  /// Get field name based on locale
  String getFieldName(String locale) {
    return locale == 'ar' && fieldNameAr != null ? fieldNameAr! : fieldName;
  }

  /// Get unit based on locale
  String getUnit(String locale) {
    return locale == 'ar' && unitAr != null ? unitAr! : unit;
  }

  /// Get equipment based on locale
  String? getEquipment(String locale) {
    return locale == 'ar' && equipmentUsedAr != null ? equipmentUsedAr : equipmentUsed;
  }

  /// Get notes based on locale
  String? getNotes(String locale) {
    return locale == 'ar' && notesAr != null ? notesAr : notes;
  }

  factory SprayApplicationLog.fromJson(Map<String, dynamic> json) {
    return SprayApplicationLog(
      logId: json['log_id'] as String,
      tenantId: json['tenant_id'] as String,
      fieldId: json['field_id'] as String,
      fieldName: json['field_name'] as String,
      fieldNameAr: json['field_name_ar'] as String?,
      recommendationId: json['recommendation_id'] as String?,
      sprayType: SprayType.fromString(json['spray_type'] as String),
      product: SprayProduct.fromJson(json['product'] as Map<String, dynamic>),
      appliedRate: (json['applied_rate'] as num).toDouble(),
      unit: json['unit'] as String,
      unitAr: json['unit_ar'] as String?,
      area: (json['area'] as num).toDouble(),
      totalQuantity: (json['total_quantity'] as num).toDouble(),
      applicationDate: DateTime.parse(json['application_date'] as String),
      weatherCondition: WeatherCondition.fromJson(json['weather_condition'] as Map<String, dynamic>),
      applicatorName: json['applicator_name'] as String?,
      equipmentUsed: json['equipment_used'] as String?,
      equipmentUsedAr: json['equipment_used_ar'] as String?,
      photoUrls: (json['photo_urls'] as List?)?.map((e) => e as String).toList() ?? [],
      notes: json['notes'] as String?,
      notesAr: json['notes_ar'] as String?,
      createdBy: json['created_by'] as String,
      createdByName: json['created_by_name'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'log_id': logId,
        'tenant_id': tenantId,
        'field_id': fieldId,
        'field_name': fieldName,
        'field_name_ar': fieldNameAr,
        'recommendation_id': recommendationId,
        'spray_type': sprayType.value,
        'product': product.toJson(),
        'applied_rate': appliedRate,
        'unit': unit,
        'unit_ar': unitAr,
        'area': area,
        'total_quantity': totalQuantity,
        'application_date': applicationDate.toIso8601String(),
        'weather_condition': weatherCondition.toJson(),
        'applicator_name': applicatorName,
        'equipment_used': equipmentUsed,
        'equipment_used_ar': equipmentUsedAr,
        'photo_urls': photoUrls,
        'notes': notes,
        'notes_ar': notesAr,
        'created_by': createdBy,
        'created_by_name': createdByName,
        'metadata': metadata,
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
      };
}
