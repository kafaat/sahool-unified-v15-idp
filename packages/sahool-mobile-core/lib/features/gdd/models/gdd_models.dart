/// GDD Models - نماذج درجات النمو الحراري (Growing Degree Days)
/// مطابقة لـ FastAPI GDD Service
library;

import 'package:flutter/foundation.dart';

/// نوع المحصول (Yemen specific crops)
enum CropType {
  wheat('wheat', 'قمح', 'Wheat'),
  corn('corn', 'ذرة', 'Corn'),
  tomato('tomato', 'طماطم', 'Tomato'),
  coffee('coffee', 'بن', 'Coffee'),
  sorghum('sorghum', 'ذرة رفيعة', 'Sorghum'),
  potato('potato', 'بطاطس', 'Potato'),
  onion('onion', 'بصل', 'Onion'),
  cotton('cotton', 'قطن', 'Cotton'),
  sesame('sesame', 'سمسم', 'Sesame'),
  millet('millet', 'دخن', 'Millet');

  final String value;
  final String nameAr;
  final String nameEn;

  const CropType(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static CropType fromString(String value) {
    return CropType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => CropType.wheat,
    );
  }
}

/// طريقة حساب GDD
enum GDDCalculationMethod {
  average('average', 'متوسط', 'Average Method'),
  sine('sine', 'موجة جيبية', 'Sine Wave Method'),
  modifiedAverage('modified_average', 'متوسط معدل', 'Modified Average');

  final String value;
  final String nameAr;
  final String nameEn;

  const GDDCalculationMethod(this.value, this.nameAr, this.nameEn);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static GDDCalculationMethod fromString(String value) {
    return GDDCalculationMethod.values.firstWhere(
      (e) => e.value == value,
      orElse: () => GDDCalculationMethod.average,
    );
  }
}

/// مرحلة النمو
@immutable
class GrowthStage {
  final String stageId;
  final String stageName;
  final String? stageNameAr;
  final int stageNumber;
  final double gddRequired;
  final double gddStart;
  final double gddEnd;
  final String? description;
  final String? descriptionAr;
  final String? icon;
  final bool isCompleted;

  const GrowthStage({
    required this.stageId,
    required this.stageName,
    this.stageNameAr,
    required this.stageNumber,
    required this.gddRequired,
    required this.gddStart,
    required this.gddEnd,
    this.description,
    this.descriptionAr,
    this.icon,
    this.isCompleted = false,
  });

  String getName(String locale) {
    return locale == 'ar' && stageNameAr != null ? stageNameAr! : stageName;
  }

  String? getDescription(String locale) {
    return locale == 'ar' && descriptionAr != null ? descriptionAr : description;
  }

  factory GrowthStage.fromJson(Map<String, dynamic> json) {
    return GrowthStage(
      stageId: json['stage_id'] as String,
      stageName: json['stage_name'] as String,
      stageNameAr: json['stage_name_ar'] as String?,
      stageNumber: json['stage_number'] as int,
      gddRequired: (json['gdd_required'] as num).toDouble(),
      gddStart: (json['gdd_start'] as num).toDouble(),
      gddEnd: (json['gdd_end'] as num).toDouble(),
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      icon: json['icon'] as String?,
      isCompleted: json['is_completed'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
        'stage_id': stageId,
        'stage_name': stageName,
        'stage_name_ar': stageNameAr,
        'stage_number': stageNumber,
        'gdd_required': gddRequired,
        'gdd_start': gddStart,
        'gdd_end': gddEnd,
        'description': description,
        'description_ar': descriptionAr,
        'icon': icon,
        'is_completed': isCompleted,
      };

  GrowthStage copyWith({
    String? stageId,
    String? stageName,
    String? stageNameAr,
    int? stageNumber,
    double? gddRequired,
    double? gddStart,
    double? gddEnd,
    String? description,
    String? descriptionAr,
    String? icon,
    bool? isCompleted,
  }) {
    return GrowthStage(
      stageId: stageId ?? this.stageId,
      stageName: stageName ?? this.stageName,
      stageNameAr: stageNameAr ?? this.stageNameAr,
      stageNumber: stageNumber ?? this.stageNumber,
      gddRequired: gddRequired ?? this.gddRequired,
      gddStart: gddStart ?? this.gddStart,
      gddEnd: gddEnd ?? this.gddEnd,
      description: description ?? this.description,
      descriptionAr: descriptionAr ?? this.descriptionAr,
      icon: icon ?? this.icon,
      isCompleted: isCompleted ?? this.isCompleted,
    );
  }
}

/// متطلبات GDD للمحصول
@immutable
class CropGDDRequirements {
  final String cropType;
  final String cropName;
  final String? cropNameAr;
  final double baseTemperature;
  final double upperThreshold;
  final double totalGDDRequired;
  final List<GrowthStage> growthStages;
  final Map<String, dynamic>? metadata;

  const CropGDDRequirements({
    required this.cropType,
    required this.cropName,
    this.cropNameAr,
    required this.baseTemperature,
    required this.upperThreshold,
    required this.totalGDDRequired,
    required this.growthStages,
    this.metadata,
  });

  String getName(String locale) {
    return locale == 'ar' && cropNameAr != null ? cropNameAr! : cropName;
  }

  factory CropGDDRequirements.fromJson(Map<String, dynamic> json) {
    return CropGDDRequirements(
      cropType: json['crop_type'] as String,
      cropName: json['crop_name'] as String,
      cropNameAr: json['crop_name_ar'] as String?,
      baseTemperature: (json['base_temperature'] as num).toDouble(),
      upperThreshold: (json['upper_threshold'] as num).toDouble(),
      totalGDDRequired: (json['total_gdd_required'] as num).toDouble(),
      growthStages: (json['growth_stages'] as List)
          .map((e) => GrowthStage.fromJson(e as Map<String, dynamic>))
          .toList(),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'crop_type': cropType,
        'crop_name': cropName,
        'crop_name_ar': cropNameAr,
        'base_temperature': baseTemperature,
        'upper_threshold': upperThreshold,
        'total_gdd_required': totalGDDRequired,
        'growth_stages': growthStages.map((e) => e.toJson()).toList(),
        'metadata': metadata,
      };
}

/// سجل GDD يومي
@immutable
class GDDRecord {
  final String recordId;
  final String fieldId;
  final DateTime date;
  final double tMin;
  final double tMax;
  final double tAvg;
  final double gddValue;
  final double accumulatedGDD;
  final GDDCalculationMethod calculationMethod;
  final double baseTemperature;
  final double? upperThreshold;
  final String? source;
  final DateTime createdAt;

  const GDDRecord({
    required this.recordId,
    required this.fieldId,
    required this.date,
    required this.tMin,
    required this.tMax,
    required this.tAvg,
    required this.gddValue,
    required this.accumulatedGDD,
    required this.calculationMethod,
    required this.baseTemperature,
    this.upperThreshold,
    this.source,
    required this.createdAt,
  });

  factory GDDRecord.fromJson(Map<String, dynamic> json) {
    return GDDRecord(
      recordId: json['record_id'] as String,
      fieldId: json['field_id'] as String,
      date: DateTime.parse(json['date'] as String),
      tMin: (json['t_min'] as num).toDouble(),
      tMax: (json['t_max'] as num).toDouble(),
      tAvg: (json['t_avg'] as num).toDouble(),
      gddValue: (json['gdd_value'] as num).toDouble(),
      accumulatedGDD: (json['accumulated_gdd'] as num).toDouble(),
      calculationMethod: GDDCalculationMethod.fromString(
        json['calculation_method'] as String,
      ),
      baseTemperature: (json['base_temperature'] as num).toDouble(),
      upperThreshold: (json['upper_threshold'] as num?)?.toDouble(),
      source: json['source'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'record_id': recordId,
        'field_id': fieldId,
        'date': date.toIso8601String(),
        't_min': tMin,
        't_max': tMax,
        't_avg': tAvg,
        'gdd_value': gddValue,
        'accumulated_gdd': accumulatedGDD,
        'calculation_method': calculationMethod.value,
        'base_temperature': baseTemperature,
        'upper_threshold': upperThreshold,
        'source': source,
        'created_at': createdAt.toIso8601String(),
      };
}

/// تراكم GDD
@immutable
class GDDAccumulation {
  final String fieldId;
  final String? fieldName;
  final CropType? cropType;
  final DateTime startDate;
  final DateTime? endDate;
  final double totalGDD;
  final double baseTemperature;
  final double? upperThreshold;
  final GDDCalculationMethod calculationMethod;
  final int daysCount;
  final double averageGDDPerDay;
  final GrowthStage? currentStage;
  final GrowthStage? nextStage;
  final double? progressPercent;
  final int? daysToNextStage;
  final List<GDDRecord> recentRecords;
  final DateTime calculatedAt;

  const GDDAccumulation({
    required this.fieldId,
    this.fieldName,
    this.cropType,
    required this.startDate,
    this.endDate,
    required this.totalGDD,
    required this.baseTemperature,
    this.upperThreshold,
    required this.calculationMethod,
    required this.daysCount,
    required this.averageGDDPerDay,
    this.currentStage,
    this.nextStage,
    this.progressPercent,
    this.daysToNextStage,
    required this.recentRecords,
    required this.calculatedAt,
  });

  /// هل الحقل في مرحلة نمو نشطة؟
  bool get isActiveGrowth => currentStage != null;

  /// نسبة التقدم في المرحلة الحالية
  double? get currentStageProgress {
    if (currentStage == null) return null;
    final stageGDD = totalGDD - currentStage!.gddStart;
    final stageRange = currentStage!.gddEnd - currentStage!.gddStart;
    if (stageRange <= 0) return 0;
    return (stageGDD / stageRange).clamp(0.0, 1.0);
  }

  /// GDD المتبقي حتى المرحلة التالية
  double? get gddToNextStage {
    if (nextStage == null) return null;
    return (nextStage!.gddStart - totalGDD).clamp(0.0, double.infinity);
  }

  factory GDDAccumulation.fromJson(Map<String, dynamic> json) {
    return GDDAccumulation(
      fieldId: json['field_id'] as String,
      fieldName: json['field_name'] as String?,
      cropType: json['crop_type'] != null
          ? CropType.fromString(json['crop_type'] as String)
          : null,
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: json['end_date'] != null
          ? DateTime.parse(json['end_date'] as String)
          : null,
      totalGDD: (json['total_gdd'] as num).toDouble(),
      baseTemperature: (json['base_temperature'] as num).toDouble(),
      upperThreshold: (json['upper_threshold'] as num?)?.toDouble(),
      calculationMethod: GDDCalculationMethod.fromString(
        json['calculation_method'] as String,
      ),
      daysCount: json['days_count'] as int,
      averageGDDPerDay: (json['average_gdd_per_day'] as num).toDouble(),
      currentStage: json['current_stage'] != null
          ? GrowthStage.fromJson(json['current_stage'] as Map<String, dynamic>)
          : null,
      nextStage: json['next_stage'] != null
          ? GrowthStage.fromJson(json['next_stage'] as Map<String, dynamic>)
          : null,
      progressPercent: (json['progress_percent'] as num?)?.toDouble(),
      daysToNextStage: json['days_to_next_stage'] as int?,
      recentRecords: (json['recent_records'] as List?)
              ?.map((e) => GDDRecord.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      calculatedAt: DateTime.parse(json['calculated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'field_id': fieldId,
        'field_name': fieldName,
        'crop_type': cropType?.value,
        'start_date': startDate.toIso8601String(),
        'end_date': endDate?.toIso8601String(),
        'total_gdd': totalGDD,
        'base_temperature': baseTemperature,
        'upper_threshold': upperThreshold,
        'calculation_method': calculationMethod.value,
        'days_count': daysCount,
        'average_gdd_per_day': averageGDDPerDay,
        'current_stage': currentStage?.toJson(),
        'next_stage': nextStage?.toJson(),
        'progress_percent': progressPercent,
        'days_to_next_stage': daysToNextStage,
        'recent_records': recentRecords.map((e) => e.toJson()).toList(),
        'calculated_at': calculatedAt.toIso8601String(),
      };
}

/// توقعات GDD
@immutable
class GDDForecast {
  final String fieldId;
  final DateTime forecastDate;
  final double forecastGDD;
  final double cumulativeGDD;
  final double tMinForecast;
  final double tMaxForecast;
  final double confidence;
  final String? source;

  const GDDForecast({
    required this.fieldId,
    required this.forecastDate,
    required this.forecastGDD,
    required this.cumulativeGDD,
    required this.tMinForecast,
    required this.tMaxForecast,
    required this.confidence,
    this.source,
  });

  factory GDDForecast.fromJson(Map<String, dynamic> json) {
    return GDDForecast(
      fieldId: json['field_id'] as String,
      forecastDate: DateTime.parse(json['forecast_date'] as String),
      forecastGDD: (json['forecast_gdd'] as num).toDouble(),
      cumulativeGDD: (json['cumulative_gdd'] as num).toDouble(),
      tMinForecast: (json['t_min_forecast'] as num).toDouble(),
      tMaxForecast: (json['t_max_forecast'] as num).toDouble(),
      confidence: (json['confidence'] as num).toDouble(),
      source: json['source'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'field_id': fieldId,
        'forecast_date': forecastDate.toIso8601String(),
        'forecast_gdd': forecastGDD,
        'cumulative_gdd': cumulativeGDD,
        't_min_forecast': tMinForecast,
        't_max_forecast': tMaxForecast,
        'confidence': confidence,
        'source': source,
      };
}

/// إعدادات GDD للحقل
@immutable
class GDDSettings {
  final String fieldId;
  final CropType cropType;
  final double baseTemperature;
  final double upperThreshold;
  final GDDCalculationMethod calculationMethod;
  final DateTime plantingDate;
  final DateTime? harvestDate;
  final bool autoCalculate;
  final Map<String, dynamic>? metadata;

  const GDDSettings({
    required this.fieldId,
    required this.cropType,
    required this.baseTemperature,
    required this.upperThreshold,
    required this.calculationMethod,
    required this.plantingDate,
    this.harvestDate,
    this.autoCalculate = true,
    this.metadata,
  });

  factory GDDSettings.fromJson(Map<String, dynamic> json) {
    return GDDSettings(
      fieldId: json['field_id'] as String,
      cropType: CropType.fromString(json['crop_type'] as String),
      baseTemperature: (json['base_temperature'] as num).toDouble(),
      upperThreshold: (json['upper_threshold'] as num).toDouble(),
      calculationMethod: GDDCalculationMethod.fromString(
        json['calculation_method'] as String,
      ),
      plantingDate: DateTime.parse(json['planting_date'] as String),
      harvestDate: json['harvest_date'] != null
          ? DateTime.parse(json['harvest_date'] as String)
          : null,
      autoCalculate: json['auto_calculate'] as bool? ?? true,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'field_id': fieldId,
        'crop_type': cropType.value,
        'base_temperature': baseTemperature,
        'upper_threshold': upperThreshold,
        'calculation_method': calculationMethod.value,
        'planting_date': plantingDate.toIso8601String(),
        'harvest_date': harvestDate?.toIso8601String(),
        'auto_calculate': autoCalculate,
        'metadata': metadata,
      };

  GDDSettings copyWith({
    String? fieldId,
    CropType? cropType,
    double? baseTemperature,
    double? upperThreshold,
    GDDCalculationMethod? calculationMethod,
    DateTime? plantingDate,
    DateTime? harvestDate,
    bool? autoCalculate,
    Map<String, dynamic>? metadata,
  }) {
    return GDDSettings(
      fieldId: fieldId ?? this.fieldId,
      cropType: cropType ?? this.cropType,
      baseTemperature: baseTemperature ?? this.baseTemperature,
      upperThreshold: upperThreshold ?? this.upperThreshold,
      calculationMethod: calculationMethod ?? this.calculationMethod,
      plantingDate: plantingDate ?? this.plantingDate,
      harvestDate: harvestDate ?? this.harvestDate,
      autoCalculate: autoCalculate ?? this.autoCalculate,
      metadata: metadata ?? this.metadata,
    );
  }
}
