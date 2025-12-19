/// Sahool Diagnosis Model
/// نموذج نتيجة تشخيص أمراض النبات

import 'package:freezed_annotation/freezed_annotation.dart';

part 'diagnosis_model.freezed.dart';
part 'diagnosis_model.g.dart';

/// شدة الإصابة
enum DiseaseSeverity {
  @JsonValue('healthy')
  healthy,
  @JsonValue('low')
  low,
  @JsonValue('medium')
  medium,
  @JsonValue('high')
  high,
  @JsonValue('critical')
  critical;

  String get arabicName => switch (this) {
    healthy => 'سليم',
    low => 'منخفض',
    medium => 'متوسط',
    high => 'مرتفع',
    critical => 'حرج',
  };

  String get color => switch (this) {
    healthy => '#22C55E',  // green
    low => '#84CC16',      // lime
    medium => '#EAB308',   // yellow
    high => '#F97316',     // orange
    critical => '#EF4444', // red
  };
}

/// نموذج العلاج المقترح
@freezed
class TreatmentModel with _$TreatmentModel {
  const factory TreatmentModel({
    @JsonKey(name: 'treatment_type') required String treatmentType,
    @JsonKey(name: 'product_name') required String productName,
    @JsonKey(name: 'product_name_ar') required String productNameAr,
    required String dosage,
    @JsonKey(name: 'dosage_ar') required String dosageAr,
    @JsonKey(name: 'application_method') required String applicationMethod,
    @JsonKey(name: 'application_method_ar') required String applicationMethodAr,
    required String frequency,
    @JsonKey(name: 'frequency_ar') required String frequencyAr,
    @Default([]) List<String> precautions,
    @JsonKey(name: 'precautions_ar') @Default([]) List<String> precautionsAr,
  }) = _TreatmentModel;

  factory TreatmentModel.fromJson(Map<String, dynamic> json) =>
      _$TreatmentModelFromJson(json);
}

/// نموذج نتيجة التشخيص الكامل
@freezed
class DiagnosisModel with _$DiagnosisModel {
  const factory DiagnosisModel({
    @JsonKey(name: 'diagnosis_id') required String diagnosisId,
    required DateTime timestamp,

    // معلومات المرض
    @JsonKey(name: 'disease_name') required String diseaseName,
    @JsonKey(name: 'disease_name_ar') required String diseaseNameAr,
    @JsonKey(name: 'disease_description') String? diseaseDescription,
    @JsonKey(name: 'disease_description_ar') String? diseaseDescriptionAr,

    // الثقة والشدة
    required double confidence,
    required DiseaseSeverity severity,
    @JsonKey(name: 'affected_area_percent') @Default(0) double affectedAreaPercent,

    // المحصول
    @JsonKey(name: 'detected_crop') String? detectedCrop,
    @JsonKey(name: 'growth_stage') String? growthStage,

    // العلاج
    @Default([]) List<TreatmentModel> treatments,
    @JsonKey(name: 'urgent_action_required') @Default(false) bool urgentActionRequired,

    // مراجعة الخبير
    @JsonKey(name: 'needs_expert_review') @Default(false) bool needsExpertReview,
    @JsonKey(name: 'expert_review_reason') String? expertReviewReason,

    // نصائح إضافية
    @JsonKey(name: 'weather_consideration') String? weatherConsideration,
    @JsonKey(name: 'prevention_tips') @Default([]) List<String> preventionTips,
    @JsonKey(name: 'prevention_tips_ar') @Default([]) List<String> preventionTipsAr,

    // الصورة المحفوظة
    @JsonKey(name: 'image_url') String? imageUrl,
  }) = _DiagnosisModel;

  factory DiagnosisModel.fromJson(Map<String, dynamic> json) =>
      _$DiagnosisModelFromJson(json);
}

/// نموذج مبسط للعرض السريع
@freezed
class DiagnosisSummary with _$DiagnosisSummary {
  const factory DiagnosisSummary({
    required String id,
    required String diseaseNameAr,
    required double confidence,
    required DiseaseSeverity severity,
    required DateTime timestamp,
    String? imageUrl,
  }) = _DiagnosisSummary;

  factory DiagnosisSummary.fromDiagnosis(DiagnosisModel diagnosis) {
    return DiagnosisSummary(
      id: diagnosis.diagnosisId,
      diseaseNameAr: diagnosis.diseaseNameAr,
      confidence: diagnosis.confidence,
      severity: diagnosis.severity,
      timestamp: diagnosis.timestamp,
      imageUrl: diagnosis.imageUrl,
    );
  }
}
