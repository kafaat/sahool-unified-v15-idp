// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'fertilizer_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$SoilAnalysisImpl _$$SoilAnalysisImplFromJson(Map<String, dynamic> json) =>
    _$SoilAnalysisImpl(
      ph: (json['ph'] as num).toDouble(),
      nitrogen: (json['nitrogen'] as num).toDouble(),
      phosphorus: (json['phosphorus'] as num).toDouble(),
      potassium: (json['potassium'] as num).toDouble(),
      organicMatter: (json['organicMatter'] as num?)?.toDouble() ?? 0,
      soilType: json['soilType'] as String? ?? '',
      soilTypeAr: json['soilTypeAr'] as String? ?? '',
    );

Map<String, dynamic> _$$SoilAnalysisImplToJson(_$SoilAnalysisImpl instance) =>
    <String, dynamic>{
      'ph': instance.ph,
      'nitrogen': instance.nitrogen,
      'phosphorus': instance.phosphorus,
      'potassium': instance.potassium,
      'organicMatter': instance.organicMatter,
      'soilType': instance.soilType,
      'soilTypeAr': instance.soilTypeAr,
    };

_$FertilizerRequestImpl _$$FertilizerRequestImplFromJson(
        Map<String, dynamic> json) =>
    _$FertilizerRequestImpl(
      cropType: json['cropType'] as String,
      fieldArea: (json['fieldArea'] as num).toDouble(),
      soilAnalysis:
          SoilAnalysis.fromJson(json['soilAnalysis'] as Map<String, dynamic>),
      growthStage: json['growthStage'] as String,
      governorate: json['governorate'] as String? ?? '',
      irrigationType: json['irrigationType'] as String? ?? '',
    );

Map<String, dynamic> _$$FertilizerRequestImplToJson(
        _$FertilizerRequestImpl instance) =>
    <String, dynamic>{
      'cropType': instance.cropType,
      'fieldArea': instance.fieldArea,
      'soilAnalysis': instance.soilAnalysis,
      'growthStage': instance.growthStage,
      'governorate': instance.governorate,
      'irrigationType': instance.irrigationType,
    };

_$NpkRecommendationImpl _$$NpkRecommendationImplFromJson(
        Map<String, dynamic> json) =>
    _$NpkRecommendationImpl(
      nitrogenKg: (json['nitrogenKg'] as num).toDouble(),
      phosphorusKg: (json['phosphorusKg'] as num).toDouble(),
      potassiumKg: (json['potassiumKg'] as num).toDouble(),
      totalKgPerHectare: (json['totalKgPerHectare'] as num).toDouble(),
      totalKgForField: (json['totalKgForField'] as num).toDouble(),
      applicationMethod: json['applicationMethod'] as String? ?? '',
      applicationMethodAr: json['applicationMethodAr'] as String? ?? '',
      timing: json['timing'] as String? ?? '',
      timingAr: json['timingAr'] as String? ?? '',
    );

Map<String, dynamic> _$$NpkRecommendationImplToJson(
        _$NpkRecommendationImpl instance) =>
    <String, dynamic>{
      'nitrogenKg': instance.nitrogenKg,
      'phosphorusKg': instance.phosphorusKg,
      'potassiumKg': instance.potassiumKg,
      'totalKgPerHectare': instance.totalKgPerHectare,
      'totalKgForField': instance.totalKgForField,
      'applicationMethod': instance.applicationMethod,
      'applicationMethodAr': instance.applicationMethodAr,
      'timing': instance.timing,
      'timingAr': instance.timingAr,
    };

_$FertilizerProductImpl _$$FertilizerProductImplFromJson(
        Map<String, dynamic> json) =>
    _$FertilizerProductImpl(
      productId: json['productId'] as String,
      name: json['name'] as String,
      nameAr: json['nameAr'] as String,
      npkRatio: json['npkRatio'] as String,
      quantityKg: (json['quantityKg'] as num).toDouble(),
      pricePerKg: (json['pricePerKg'] as num?)?.toDouble() ?? 0,
      applicationNotes: json['applicationNotes'] as String? ?? '',
      applicationNotesAr: json['applicationNotesAr'] as String? ?? '',
    );

Map<String, dynamic> _$$FertilizerProductImplToJson(
        _$FertilizerProductImpl instance) =>
    <String, dynamic>{
      'productId': instance.productId,
      'name': instance.name,
      'nameAr': instance.nameAr,
      'npkRatio': instance.npkRatio,
      'quantityKg': instance.quantityKg,
      'pricePerKg': instance.pricePerKg,
      'applicationNotes': instance.applicationNotes,
      'applicationNotesAr': instance.applicationNotesAr,
    };

_$FertilizerRecommendationImpl _$$FertilizerRecommendationImplFromJson(
        Map<String, dynamic> json) =>
    _$FertilizerRecommendationImpl(
      recommendationId: json['recommendationId'] as String,
      fieldId: json['fieldId'] as String,
      cropType: json['cropType'] as String,
      cropTypeAr: json['cropTypeAr'] as String,
      npkRecommendation: NpkRecommendation.fromJson(
          json['npkRecommendation'] as Map<String, dynamic>),
      suggestedProducts: (json['suggestedProducts'] as List<dynamic>)
          .map((e) => FertilizerProduct.fromJson(e as Map<String, dynamic>))
          .toList(),
      soilHealthStatus: json['soilHealthStatus'] as String,
      soilHealthStatusAr: json['soilHealthStatusAr'] as String,
      deficiencies: (json['deficiencies'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      deficienciesAr: (json['deficienciesAr'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      warnings: (json['warnings'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      warningsAr: (json['warningsAr'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      generatedAt: DateTime.parse(json['generatedAt'] as String),
      seasonalNote: json['seasonalNote'] as String? ?? '',
      seasonalNoteAr: json['seasonalNoteAr'] as String? ?? '',
    );

Map<String, dynamic> _$$FertilizerRecommendationImplToJson(
        _$FertilizerRecommendationImpl instance) =>
    <String, dynamic>{
      'recommendationId': instance.recommendationId,
      'fieldId': instance.fieldId,
      'cropType': instance.cropType,
      'cropTypeAr': instance.cropTypeAr,
      'npkRecommendation': instance.npkRecommendation,
      'suggestedProducts': instance.suggestedProducts,
      'soilHealthStatus': instance.soilHealthStatus,
      'soilHealthStatusAr': instance.soilHealthStatusAr,
      'deficiencies': instance.deficiencies,
      'deficienciesAr': instance.deficienciesAr,
      'warnings': instance.warnings,
      'warningsAr': instance.warningsAr,
      'generatedAt': instance.generatedAt.toIso8601String(),
      'seasonalNote': instance.seasonalNote,
      'seasonalNoteAr': instance.seasonalNoteAr,
    };

_$DeficiencySymptomImpl _$$DeficiencySymptomImplFromJson(
        Map<String, dynamic> json) =>
    _$DeficiencySymptomImpl(
      nutrient: json['nutrient'] as String,
      nutrientAr: json['nutrientAr'] as String,
      severity: json['severity'] as String,
      visualSymptoms: (json['visualSymptoms'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      visualSymptomsAr: (json['visualSymptomsAr'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      recommendation: json['recommendation'] as String,
      recommendationAr: json['recommendationAr'] as String,
      imageUrl: json['imageUrl'] as String? ?? '',
    );

Map<String, dynamic> _$$DeficiencySymptomImplToJson(
        _$DeficiencySymptomImpl instance) =>
    <String, dynamic>{
      'nutrient': instance.nutrient,
      'nutrientAr': instance.nutrientAr,
      'severity': instance.severity,
      'visualSymptoms': instance.visualSymptoms,
      'visualSymptomsAr': instance.visualSymptomsAr,
      'recommendation': instance.recommendation,
      'recommendationAr': instance.recommendationAr,
      'imageUrl': instance.imageUrl,
    };

_$SoilInterpretationImpl _$$SoilInterpretationImplFromJson(
        Map<String, dynamic> json) =>
    _$SoilInterpretationImpl(
      overallHealth: json['overallHealth'] as String,
      overallHealthAr: json['overallHealthAr'] as String,
      nutrientLevels: Map<String, String>.from(json['nutrientLevels'] as Map),
      nutrientLevelsAr:
          Map<String, String>.from(json['nutrientLevelsAr'] as Map),
      recommendations: (json['recommendations'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      recommendationsAr: (json['recommendationsAr'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      fertilitySCore: (json['fertilitySCore'] as num).toDouble(),
    );

Map<String, dynamic> _$$SoilInterpretationImplToJson(
        _$SoilInterpretationImpl instance) =>
    <String, dynamic>{
      'overallHealth': instance.overallHealth,
      'overallHealthAr': instance.overallHealthAr,
      'nutrientLevels': instance.nutrientLevels,
      'nutrientLevelsAr': instance.nutrientLevelsAr,
      'recommendations': instance.recommendations,
      'recommendationsAr': instance.recommendationsAr,
      'fertilitySCore': instance.fertilitySCore,
    };

_$CropTypeOptionImpl _$$CropTypeOptionImplFromJson(Map<String, dynamic> json) =>
    _$CropTypeOptionImpl(
      id: json['id'] as String,
      name: json['name'] as String,
      nameAr: json['nameAr'] as String,
      category: json['category'] as String,
      categoryAr: json['categoryAr'] as String,
      growthStages: (json['growthStages'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      growthStagesAr: (json['growthStagesAr'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$CropTypeOptionImplToJson(
        _$CropTypeOptionImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'nameAr': instance.nameAr,
      'category': instance.category,
      'categoryAr': instance.categoryAr,
      'growthStages': instance.growthStages,
      'growthStagesAr': instance.growthStagesAr,
    };
