// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'diagnosis_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$TreatmentModelImpl _$$TreatmentModelImplFromJson(Map<String, dynamic> json) =>
    _$TreatmentModelImpl(
      treatmentType: json['treatment_type'] as String,
      productName: json['product_name'] as String,
      productNameAr: json['product_name_ar'] as String,
      dosage: json['dosage'] as String,
      dosageAr: json['dosage_ar'] as String,
      applicationMethod: json['application_method'] as String,
      applicationMethodAr: json['application_method_ar'] as String,
      frequency: json['frequency'] as String,
      frequencyAr: json['frequency_ar'] as String,
      precautions: (json['precautions'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      precautionsAr: (json['precautions_ar'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$TreatmentModelImplToJson(
        _$TreatmentModelImpl instance) =>
    <String, dynamic>{
      'treatment_type': instance.treatmentType,
      'product_name': instance.productName,
      'product_name_ar': instance.productNameAr,
      'dosage': instance.dosage,
      'dosage_ar': instance.dosageAr,
      'application_method': instance.applicationMethod,
      'application_method_ar': instance.applicationMethodAr,
      'frequency': instance.frequency,
      'frequency_ar': instance.frequencyAr,
      'precautions': instance.precautions,
      'precautions_ar': instance.precautionsAr,
    };

_$DiagnosisModelImpl _$$DiagnosisModelImplFromJson(Map<String, dynamic> json) =>
    _$DiagnosisModelImpl(
      diagnosisId: json['diagnosis_id'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      diseaseName: json['disease_name'] as String,
      diseaseNameAr: json['disease_name_ar'] as String,
      diseaseDescription: json['disease_description'] as String?,
      diseaseDescriptionAr: json['disease_description_ar'] as String?,
      confidence: (json['confidence'] as num).toDouble(),
      severity: $enumDecode(_$DiseaseSeverityEnumMap, json['severity']),
      affectedAreaPercent:
          (json['affected_area_percent'] as num?)?.toDouble() ?? 0,
      detectedCrop: json['detected_crop'] as String?,
      growthStage: json['growth_stage'] as String?,
      treatments: (json['treatments'] as List<dynamic>?)
              ?.map((e) => TreatmentModel.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      urgentActionRequired: json['urgent_action_required'] as bool? ?? false,
      needsExpertReview: json['needs_expert_review'] as bool? ?? false,
      expertReviewReason: json['expert_review_reason'] as String?,
      weatherConsideration: json['weather_consideration'] as String?,
      preventionTips: (json['prevention_tips'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      preventionTipsAr: (json['prevention_tips_ar'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      imageUrl: json['image_url'] as String?,
    );

Map<String, dynamic> _$$DiagnosisModelImplToJson(
        _$DiagnosisModelImpl instance) =>
    <String, dynamic>{
      'diagnosis_id': instance.diagnosisId,
      'timestamp': instance.timestamp.toIso8601String(),
      'disease_name': instance.diseaseName,
      'disease_name_ar': instance.diseaseNameAr,
      'disease_description': instance.diseaseDescription,
      'disease_description_ar': instance.diseaseDescriptionAr,
      'confidence': instance.confidence,
      'severity': _$DiseaseSeverityEnumMap[instance.severity]!,
      'affected_area_percent': instance.affectedAreaPercent,
      'detected_crop': instance.detectedCrop,
      'growth_stage': instance.growthStage,
      'treatments': instance.treatments,
      'urgent_action_required': instance.urgentActionRequired,
      'needs_expert_review': instance.needsExpertReview,
      'expert_review_reason': instance.expertReviewReason,
      'weather_consideration': instance.weatherConsideration,
      'prevention_tips': instance.preventionTips,
      'prevention_tips_ar': instance.preventionTipsAr,
      'image_url': instance.imageUrl,
    };

const _$DiseaseSeverityEnumMap = {
  DiseaseSeverity.healthy: 'healthy',
  DiseaseSeverity.low: 'low',
  DiseaseSeverity.medium: 'medium',
  DiseaseSeverity.high: 'high',
  DiseaseSeverity.critical: 'critical',
};
