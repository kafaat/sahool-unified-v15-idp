/// Crop Health Diagnosis Models
/// نماذج تشخيص صحة المحاصيل
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'diagnosis_models.freezed.dart';
part 'diagnosis_models.g.dart';

/// Disease severity levels
/// مستويات خطورة المرض
enum DiseaseSeverity {
  healthy,
  low,
  medium,
  high,
  critical,
}

/// Treatment type
/// نوع العلاج
enum TreatmentType {
  fungicide,
  insecticide,
  herbicide,
  fertilizer,
  irrigation,
  pruning,
  none,
}

/// Treatment information
/// معلومات العلاج
@freezed
class Treatment with _$Treatment {
  const factory Treatment({
    required String treatmentType,
    required String productName,
    required String productNameAr,
    required String dosage,
    required String dosageAr,
    required String applicationMethod,
    required String applicationMethodAr,
    required String frequency,
    required String frequencyAr,
    @Default([]) List<String> precautions,
    @Default([]) List<String> precautionsAr,
  }) = _Treatment;

  factory Treatment.fromJson(Map<String, dynamic> json) =>
      _$TreatmentFromJson(json);
}

/// Diagnosis result from AI
/// نتيجة التشخيص من الذكاء الاصطناعي
@freezed
class DiagnosisResult with _$DiagnosisResult {
  const factory DiagnosisResult({
    required String diagnosisId,
    required DateTime timestamp,

    // Disease information
    required String diseaseName,
    required String diseaseNameAr,
    required String diseaseDescription,
    required String diseaseDescriptionAr,

    // Confidence and severity
    required double confidence,
    required String severity,
    required double affectedAreaPercent,

    // Crop information
    required String detectedCrop,
    String? growthStage,

    // Treatment recommendations
    required List<Treatment> treatments,
    required bool urgentActionRequired,

    // Expert review
    required bool needsExpertReview,
    String? expertReviewReason,

    // Additional info
    String? weatherConsideration,
    @Default([]) List<String> preventionTips,
    @Default([]) List<String> preventionTipsAr,
  }) = _DiagnosisResult;

  factory DiagnosisResult.fromJson(Map<String, dynamic> json) =>
      _$DiagnosisResultFromJson(json);
}

/// Crop type option
/// خيار نوع المحصول
@freezed
class CropOption with _$CropOption {
  const factory CropOption({
    required String cropId,
    required String name,
    required String nameAr,
    required String icon,
    @Default(0) int diseasesCount,
  }) = _CropOption;

  factory CropOption.fromJson(Map<String, dynamic> json) =>
      _$CropOptionFromJson(json);
}

/// Disease info
/// معلومات المرض
@freezed
class DiseaseInfo with _$DiseaseInfo {
  const factory DiseaseInfo({
    required String diseaseId,
    required String name,
    required String nameAr,
    required String crop,
    required String severity,
  }) = _DiseaseInfo;

  factory DiseaseInfo.fromJson(Map<String, dynamic> json) =>
      _$DiseaseInfoFromJson(json);
}

/// Expert review request
/// طلب مراجعة خبير
@freezed
class ExpertReviewRequest with _$ExpertReviewRequest {
  const factory ExpertReviewRequest({
    required String diagnosisId,
    String? farmerNotes,
    @Default('normal') String urgency,
  }) = _ExpertReviewRequest;

  factory ExpertReviewRequest.fromJson(Map<String, dynamic> json) =>
      _$ExpertReviewRequestFromJson(json);
}

/// Expert review response
/// استجابة طلب المراجعة
@freezed
class ExpertReviewResponse with _$ExpertReviewResponse {
  const factory ExpertReviewResponse({
    required String reviewId,
    required String diagnosisId,
    required String status,
    required String estimatedResponseTime,
    required String message,
    required String messageEn,
  }) = _ExpertReviewResponse;

  factory ExpertReviewResponse.fromJson(Map<String, dynamic> json) =>
      _$ExpertReviewResponseFromJson(json);
}

/// Batch diagnosis result
/// نتيجة تشخيص الدفعة
@freezed
class BatchDiagnosisResult with _$BatchDiagnosisResult {
  const factory BatchDiagnosisResult({
    required String batchId,
    String? fieldId,
    required int totalImages,
    required int processed,
    required List<BatchImageResult> results,
    required BatchSummary summary,
  }) = _BatchDiagnosisResult;

  factory BatchDiagnosisResult.fromJson(Map<String, dynamic> json) =>
      _$BatchDiagnosisResultFromJson(json);
}

/// Single image result in batch
/// نتيجة صورة واحدة في الدفعة
@freezed
class BatchImageResult with _$BatchImageResult {
  const factory BatchImageResult({
    required String filename,
    required String disease,
    required double confidence,
    required String diseaseNameAr,
  }) = _BatchImageResult;

  factory BatchImageResult.fromJson(Map<String, dynamic> json) =>
      _$BatchImageResultFromJson(json);
}

/// Batch summary
/// ملخص الدفعة
@freezed
class BatchSummary with _$BatchSummary {
  const factory BatchSummary({
    required int healthyCount,
    required int infectedCount,
    required double averageConfidence,
  }) = _BatchSummary;

  factory BatchSummary.fromJson(Map<String, dynamic> json) =>
      _$BatchSummaryFromJson(json);
}

/// Diagnosis history item
/// عنصر سجل التشخيص
@freezed
class DiagnosisHistoryItem with _$DiagnosisHistoryItem {
  const factory DiagnosisHistoryItem({
    required String diagnosisId,
    required String diseaseName,
    required String diseaseNameAr,
    required double confidence,
    required String severity,
    required DateTime timestamp,
    String? fieldId,
    String? imagePath,
    @Default(false) bool isResolved,
  }) = _DiagnosisHistoryItem;

  factory DiagnosisHistoryItem.fromJson(Map<String, dynamic> json) =>
      _$DiagnosisHistoryItemFromJson(json);
}
