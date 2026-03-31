/// Fertilizer Recommendation Models
/// نماذج توصيات التسميد
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'fertilizer_models.freezed.dart';
part 'fertilizer_models.g.dart';

/// Soil analysis data
/// بيانات تحليل التربة
@freezed
class SoilAnalysis with _$SoilAnalysis {
  const factory SoilAnalysis({
    required double ph,
    required double nitrogen, // mg/kg
    required double phosphorus, // mg/kg
    required double potassium, // mg/kg
    @Default(0) double organicMatter, // %
    @Default('') String soilType,
    @Default('') String soilTypeAr,
  }) = _SoilAnalysis;

  factory SoilAnalysis.fromJson(Map<String, dynamic> json) =>
      _$SoilAnalysisFromJson(json);
}

/// Fertilizer recommendation request
/// طلب توصية التسميد
@freezed
class FertilizerRequest with _$FertilizerRequest {
  const factory FertilizerRequest({
    required String cropType,
    required double fieldArea, // hectares
    required SoilAnalysis soilAnalysis,
    required String growthStage,
    @Default('') String governorate,
    @Default('') String irrigationType,
  }) = _FertilizerRequest;

  factory FertilizerRequest.fromJson(Map<String, dynamic> json) =>
      _$FertilizerRequestFromJson(json);
}

/// NPK Recommendation
/// توصية السماد NPK
@freezed
class NpkRecommendation with _$NpkRecommendation {
  const factory NpkRecommendation({
    required double nitrogenKg, // كجم/هكتار
    required double phosphorusKg,
    required double potassiumKg,
    required double totalKgPerHectare,
    required double totalKgForField,
    @Default('') String applicationMethod,
    @Default('') String applicationMethodAr,
    @Default('') String timing,
    @Default('') String timingAr,
  }) = _NpkRecommendation;

  factory NpkRecommendation.fromJson(Map<String, dynamic> json) =>
      _$NpkRecommendationFromJson(json);
}

/// Fertilizer product suggestion
/// اقتراح منتج السماد
@freezed
class FertilizerProduct with _$FertilizerProduct {
  const factory FertilizerProduct({
    required String productId,
    required String name,
    required String nameAr,
    required String npkRatio, // e.g., "15-15-15"
    required double quantityKg,
    @Default(0) double pricePerKg,
    @Default('') String applicationNotes,
    @Default('') String applicationNotesAr,
  }) = _FertilizerProduct;

  factory FertilizerProduct.fromJson(Map<String, dynamic> json) =>
      _$FertilizerProductFromJson(json);
}

/// Complete fertilizer recommendation
/// توصية التسميد الكاملة
@freezed
class FertilizerRecommendation with _$FertilizerRecommendation {
  const factory FertilizerRecommendation({
    required String recommendationId,
    required String fieldId,
    required String cropType,
    required String cropTypeAr,
    required NpkRecommendation npkRecommendation,
    required List<FertilizerProduct> suggestedProducts,
    required String soilHealthStatus,
    required String soilHealthStatusAr,
    @Default([]) List<String> deficiencies,
    @Default([]) List<String> deficienciesAr,
    @Default([]) List<String> warnings,
    @Default([]) List<String> warningsAr,
    required DateTime generatedAt,
    @Default('') String seasonalNote,
    @Default('') String seasonalNoteAr,
  }) = _FertilizerRecommendation;

  factory FertilizerRecommendation.fromJson(Map<String, dynamic> json) =>
      _$FertilizerRecommendationFromJson(json);
}

/// Deficiency symptom
/// أعراض النقص
@freezed
class DeficiencySymptom with _$DeficiencySymptom {
  const factory DeficiencySymptom({
    required String nutrient,
    required String nutrientAr,
    required String severity, // low, medium, high, critical
    required List<String> visualSymptoms,
    required List<String> visualSymptomsAr,
    required String recommendation,
    required String recommendationAr,
    @Default('') String imageUrl,
  }) = _DeficiencySymptom;

  factory DeficiencySymptom.fromJson(Map<String, dynamic> json) =>
      _$DeficiencySymptomFromJson(json);
}

/// Soil interpretation result
/// نتيجة تفسير التربة
@freezed
class SoilInterpretation with _$SoilInterpretation {
  const factory SoilInterpretation({
    required String overallHealth, // excellent, good, fair, poor
    required String overallHealthAr,
    required Map<String, String> nutrientLevels, // nutrient -> level
    required Map<String, String> nutrientLevelsAr,
    required List<String> recommendations,
    required List<String> recommendationsAr,
    required double fertilitySCore, // 0-100
  }) = _SoilInterpretation;

  factory SoilInterpretation.fromJson(Map<String, dynamic> json) =>
      _$SoilInterpretationFromJson(json);
}

/// Available crop types for fertilizer advisor
/// أنواع المحاصيل المتاحة لمستشار التسميد
@freezed
class CropTypeOption with _$CropTypeOption {
  const factory CropTypeOption({
    required String id,
    required String name,
    required String nameAr,
    required String category,
    required String categoryAr,
    @Default([]) List<String> growthStages,
    @Default([]) List<String> growthStagesAr,
  }) = _CropTypeOption;

  factory CropTypeOption.fromJson(Map<String, dynamic> json) =>
      _$CropTypeOptionFromJson(json);
}
