/// Phenology Data Model - نموذج بيانات مراحل النمو
/// Crop growth stage tracking from satellite monitoring
library;

import 'package:equatable/equatable.dart';

/// Phenology Data
/// بيانات مراحل النمو
class PhenologyData extends Equatable {
  final String fieldId;
  final String cropType;
  final String cropTypeAr;
  final GrowthStage currentStage;
  final int daysInCurrentStage;
  final int? daysToNextStage;
  final int? daysToHarvest;
  final DateTime plantingDate;
  final DateTime? expectedHarvestDate;
  final List<GrowthStageInfo> stages;
  final List<String> currentTasks;
  final List<String> currentTasksAr;
  final double completionPercentage; // 0-100
  final DateTime analyzedAt;

  const PhenologyData({
    required this.fieldId,
    required this.cropType,
    required this.cropTypeAr,
    required this.currentStage,
    required this.daysInCurrentStage,
    this.daysToNextStage,
    this.daysToHarvest,
    required this.plantingDate,
    this.expectedHarvestDate,
    this.stages = const [],
    this.currentTasks = const [],
    this.currentTasksAr = const [],
    required this.completionPercentage,
    required this.analyzedAt,
  });

  factory PhenologyData.fromJson(Map<String, dynamic> json) {
    final stagesData = json['stages'] ?? [];
    final tasksData = json['current_tasks'] ?? json['currentTasks'] ?? [];
    final tasksArData = json['current_tasks_ar'] ?? json['currentTasksAr'] ?? [];

    return PhenologyData(
      fieldId: json['field_id'] ?? json['fieldId'] ?? '',
      cropType: json['crop_type'] ?? json['cropType'] ?? '',
      cropTypeAr: json['crop_type_ar'] ?? json['cropTypeAr'] ?? '',
      currentStage: GrowthStage.fromString(
        json['current_stage'] ?? json['currentStage'] ?? 'unknown',
      ),
      daysInCurrentStage: json['days_in_current_stage'] ?? json['daysInCurrentStage'] ?? 0,
      daysToNextStage: json['days_to_next_stage'] ?? json['daysToNextStage'],
      daysToHarvest: json['days_to_harvest'] ?? json['daysToHarvest'],
      plantingDate: DateTime.parse(
        json['planting_date'] ?? json['plantingDate'] ?? DateTime.now().toIso8601String(),
      ),
      expectedHarvestDate: json['expected_harvest_date'] != null
          ? DateTime.parse(json['expected_harvest_date'])
          : null,
      stages: (stagesData as List)
          .map((item) => GrowthStageInfo.fromJson(item as Map<String, dynamic>))
          .toList(),
      currentTasks: (tasksData as List).map((task) => task.toString()).toList(),
      currentTasksAr: (tasksArData as List).map((task) => task.toString()).toList(),
      completionPercentage: (json['completion_percentage'] ?? json['completionPercentage'] ?? 0.0)
          .toDouble(),
      analyzedAt: DateTime.parse(
        json['analyzed_at'] ?? json['analyzedAt'] ?? DateTime.now().toIso8601String(),
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'field_id': fieldId,
      'crop_type': cropType,
      'crop_type_ar': cropTypeAr,
      'current_stage': currentStage.value,
      'days_in_current_stage': daysInCurrentStage,
      'days_to_next_stage': daysToNextStage,
      'days_to_harvest': daysToHarvest,
      'planting_date': plantingDate.toIso8601String(),
      'expected_harvest_date': expectedHarvestDate?.toIso8601String(),
      'stages': stages.map((stage) => stage.toJson()).toList(),
      'current_tasks': currentTasks,
      'current_tasks_ar': currentTasksAr,
      'completion_percentage': completionPercentage,
      'analyzed_at': analyzedAt.toIso8601String(),
    };
  }

  @override
  List<Object?> get props => [
        fieldId,
        cropType,
        cropTypeAr,
        currentStage,
        daysInCurrentStage,
        daysToNextStage,
        daysToHarvest,
        plantingDate,
        expectedHarvestDate,
        stages,
        currentTasks,
        currentTasksAr,
        completionPercentage,
        analyzedAt,
      ];
}

/// Growth Stage
/// مرحلة النمو
enum GrowthStage {
  germination('germination', 'إنبات', '#8BC34A'),
  vegetative('vegetative', 'نمو خضري', '#4CAF50'),
  flowering('flowering', 'إزهار', '#FFC107'),
  fruitDevelopment('fruit_development', 'تطور الثمار', '#FF9800'),
  ripening('ripening', 'نضج', '#FF5722'),
  harvest('harvest', 'حصاد', '#795548'),
  unknown('unknown', 'غير معروف', '#9E9E9E');

  final String value;
  final String arabicLabel;
  final String colorHex;

  const GrowthStage(this.value, this.arabicLabel, this.colorHex);

  static GrowthStage fromString(String value) {
    return GrowthStage.values.firstWhere(
      (stage) => stage.value.toLowerCase() == value.toLowerCase(),
      orElse: () => GrowthStage.unknown,
    );
  }

  String getLabel(bool isArabic) => isArabic ? arabicLabel : value;
}

/// Growth Stage Info
/// معلومات مرحلة النمو
class GrowthStageInfo extends Equatable {
  final GrowthStage stage;
  final String name;
  final String nameAr;
  final int durationDays;
  final DateTime? startDate;
  final DateTime? endDate;
  final bool isCompleted;
  final bool isCurrent;
  final String description;
  final String descriptionAr;
  final List<String> tasks;
  final List<String> tasksAr;

  const GrowthStageInfo({
    required this.stage,
    required this.name,
    required this.nameAr,
    required this.durationDays,
    this.startDate,
    this.endDate,
    required this.isCompleted,
    required this.isCurrent,
    this.description = '',
    this.descriptionAr = '',
    this.tasks = const [],
    this.tasksAr = const [],
  });

  factory GrowthStageInfo.fromJson(Map<String, dynamic> json) {
    final tasksData = json['tasks'] ?? [];
    final tasksArData = json['tasks_ar'] ?? json['tasksAr'] ?? [];

    return GrowthStageInfo(
      stage: GrowthStage.fromString(json['stage'] ?? 'unknown'),
      name: json['name'] ?? '',
      nameAr: json['name_ar'] ?? json['nameAr'] ?? '',
      durationDays: json['duration_days'] ?? json['durationDays'] ?? 0,
      startDate: json['start_date'] != null ? DateTime.parse(json['start_date']) : null,
      endDate: json['end_date'] != null ? DateTime.parse(json['end_date']) : null,
      isCompleted: json['is_completed'] ?? json['isCompleted'] ?? false,
      isCurrent: json['is_current'] ?? json['isCurrent'] ?? false,
      description: json['description'] ?? '',
      descriptionAr: json['description_ar'] ?? json['descriptionAr'] ?? '',
      tasks: (tasksData as List).map((task) => task.toString()).toList(),
      tasksAr: (tasksArData as List).map((task) => task.toString()).toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'stage': stage.value,
      'name': name,
      'name_ar': nameAr,
      'duration_days': durationDays,
      'start_date': startDate?.toIso8601String(),
      'end_date': endDate?.toIso8601String(),
      'is_completed': isCompleted,
      'is_current': isCurrent,
      'description': description,
      'description_ar': descriptionAr,
      'tasks': tasks,
      'tasks_ar': tasksAr,
    };
  }

  @override
  List<Object?> get props => [
        stage,
        name,
        nameAr,
        durationDays,
        startDate,
        endDate,
        isCompleted,
        isCurrent,
        description,
        descriptionAr,
        tasks,
        tasksAr,
      ];
}
