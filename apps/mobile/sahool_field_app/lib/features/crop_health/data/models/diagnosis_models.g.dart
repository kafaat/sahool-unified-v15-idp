// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'diagnosis_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$TreatmentImpl _$$TreatmentImplFromJson(Map<String, dynamic> json) =>
    _$TreatmentImpl(
      treatmentType: json['treatmentType'] as String,
      productName: json['productName'] as String,
      productNameAr: json['productNameAr'] as String,
      dosage: json['dosage'] as String,
      dosageAr: json['dosageAr'] as String,
      applicationMethod: json['applicationMethod'] as String,
      applicationMethodAr: json['applicationMethodAr'] as String,
      frequency: json['frequency'] as String,
      frequencyAr: json['frequencyAr'] as String,
      precautions: (json['precautions'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      precautionsAr: (json['precautionsAr'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$TreatmentImplToJson(_$TreatmentImpl instance) =>
    <String, dynamic>{
      'treatmentType': instance.treatmentType,
      'productName': instance.productName,
      'productNameAr': instance.productNameAr,
      'dosage': instance.dosage,
      'dosageAr': instance.dosageAr,
      'applicationMethod': instance.applicationMethod,
      'applicationMethodAr': instance.applicationMethodAr,
      'frequency': instance.frequency,
      'frequencyAr': instance.frequencyAr,
      'precautions': instance.precautions,
      'precautionsAr': instance.precautionsAr,
    };

_$DiagnosisResultImpl _$$DiagnosisResultImplFromJson(
        Map<String, dynamic> json) =>
    _$DiagnosisResultImpl(
      diagnosisId: json['diagnosisId'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      diseaseName: json['diseaseName'] as String,
      diseaseNameAr: json['diseaseNameAr'] as String,
      diseaseDescription: json['diseaseDescription'] as String,
      diseaseDescriptionAr: json['diseaseDescriptionAr'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      severity: json['severity'] as String,
      affectedAreaPercent: (json['affectedAreaPercent'] as num).toDouble(),
      detectedCrop: json['detectedCrop'] as String,
      growthStage: json['growthStage'] as String?,
      treatments: (json['treatments'] as List<dynamic>)
          .map((e) => Treatment.fromJson(e as Map<String, dynamic>))
          .toList(),
      urgentActionRequired: json['urgentActionRequired'] as bool,
      needsExpertReview: json['needsExpertReview'] as bool,
      expertReviewReason: json['expertReviewReason'] as String?,
      weatherConsideration: json['weatherConsideration'] as String?,
      preventionTips: (json['preventionTips'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      preventionTipsAr: (json['preventionTipsAr'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$DiagnosisResultImplToJson(
        _$DiagnosisResultImpl instance) =>
    <String, dynamic>{
      'diagnosisId': instance.diagnosisId,
      'timestamp': instance.timestamp.toIso8601String(),
      'diseaseName': instance.diseaseName,
      'diseaseNameAr': instance.diseaseNameAr,
      'diseaseDescription': instance.diseaseDescription,
      'diseaseDescriptionAr': instance.diseaseDescriptionAr,
      'confidence': instance.confidence,
      'severity': instance.severity,
      'affectedAreaPercent': instance.affectedAreaPercent,
      'detectedCrop': instance.detectedCrop,
      'growthStage': instance.growthStage,
      'treatments': instance.treatments,
      'urgentActionRequired': instance.urgentActionRequired,
      'needsExpertReview': instance.needsExpertReview,
      'expertReviewReason': instance.expertReviewReason,
      'weatherConsideration': instance.weatherConsideration,
      'preventionTips': instance.preventionTips,
      'preventionTipsAr': instance.preventionTipsAr,
    };

_$CropOptionImpl _$$CropOptionImplFromJson(Map<String, dynamic> json) =>
    _$CropOptionImpl(
      cropId: json['cropId'] as String,
      name: json['name'] as String,
      nameAr: json['nameAr'] as String,
      icon: json['icon'] as String,
      diseasesCount: (json['diseasesCount'] as num?)?.toInt() ?? 0,
    );

Map<String, dynamic> _$$CropOptionImplToJson(_$CropOptionImpl instance) =>
    <String, dynamic>{
      'cropId': instance.cropId,
      'name': instance.name,
      'nameAr': instance.nameAr,
      'icon': instance.icon,
      'diseasesCount': instance.diseasesCount,
    };

_$DiseaseInfoImpl _$$DiseaseInfoImplFromJson(Map<String, dynamic> json) =>
    _$DiseaseInfoImpl(
      diseaseId: json['diseaseId'] as String,
      name: json['name'] as String,
      nameAr: json['nameAr'] as String,
      crop: json['crop'] as String,
      severity: json['severity'] as String,
    );

Map<String, dynamic> _$$DiseaseInfoImplToJson(_$DiseaseInfoImpl instance) =>
    <String, dynamic>{
      'diseaseId': instance.diseaseId,
      'name': instance.name,
      'nameAr': instance.nameAr,
      'crop': instance.crop,
      'severity': instance.severity,
    };

_$ExpertReviewRequestImpl _$$ExpertReviewRequestImplFromJson(
        Map<String, dynamic> json) =>
    _$ExpertReviewRequestImpl(
      diagnosisId: json['diagnosisId'] as String,
      farmerNotes: json['farmerNotes'] as String?,
      urgency: json['urgency'] as String? ?? 'normal',
    );

Map<String, dynamic> _$$ExpertReviewRequestImplToJson(
        _$ExpertReviewRequestImpl instance) =>
    <String, dynamic>{
      'diagnosisId': instance.diagnosisId,
      'farmerNotes': instance.farmerNotes,
      'urgency': instance.urgency,
    };

_$ExpertReviewResponseImpl _$$ExpertReviewResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$ExpertReviewResponseImpl(
      reviewId: json['reviewId'] as String,
      diagnosisId: json['diagnosisId'] as String,
      status: json['status'] as String,
      estimatedResponseTime: json['estimatedResponseTime'] as String,
      message: json['message'] as String,
      messageEn: json['messageEn'] as String,
    );

Map<String, dynamic> _$$ExpertReviewResponseImplToJson(
        _$ExpertReviewResponseImpl instance) =>
    <String, dynamic>{
      'reviewId': instance.reviewId,
      'diagnosisId': instance.diagnosisId,
      'status': instance.status,
      'estimatedResponseTime': instance.estimatedResponseTime,
      'message': instance.message,
      'messageEn': instance.messageEn,
    };

_$BatchDiagnosisResultImpl _$$BatchDiagnosisResultImplFromJson(
        Map<String, dynamic> json) =>
    _$BatchDiagnosisResultImpl(
      batchId: json['batchId'] as String,
      fieldId: json['fieldId'] as String?,
      totalImages: (json['totalImages'] as num).toInt(),
      processed: (json['processed'] as num).toInt(),
      results: (json['results'] as List<dynamic>)
          .map((e) => BatchImageResult.fromJson(e as Map<String, dynamic>))
          .toList(),
      summary: BatchSummary.fromJson(json['summary'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$$BatchDiagnosisResultImplToJson(
        _$BatchDiagnosisResultImpl instance) =>
    <String, dynamic>{
      'batchId': instance.batchId,
      'fieldId': instance.fieldId,
      'totalImages': instance.totalImages,
      'processed': instance.processed,
      'results': instance.results,
      'summary': instance.summary,
    };

_$BatchImageResultImpl _$$BatchImageResultImplFromJson(
        Map<String, dynamic> json) =>
    _$BatchImageResultImpl(
      filename: json['filename'] as String,
      disease: json['disease'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      diseaseNameAr: json['diseaseNameAr'] as String,
    );

Map<String, dynamic> _$$BatchImageResultImplToJson(
        _$BatchImageResultImpl instance) =>
    <String, dynamic>{
      'filename': instance.filename,
      'disease': instance.disease,
      'confidence': instance.confidence,
      'diseaseNameAr': instance.diseaseNameAr,
    };

_$BatchSummaryImpl _$$BatchSummaryImplFromJson(Map<String, dynamic> json) =>
    _$BatchSummaryImpl(
      healthyCount: (json['healthyCount'] as num).toInt(),
      infectedCount: (json['infectedCount'] as num).toInt(),
      averageConfidence: (json['averageConfidence'] as num).toDouble(),
    );

Map<String, dynamic> _$$BatchSummaryImplToJson(_$BatchSummaryImpl instance) =>
    <String, dynamic>{
      'healthyCount': instance.healthyCount,
      'infectedCount': instance.infectedCount,
      'averageConfidence': instance.averageConfidence,
    };

_$DiagnosisHistoryItemImpl _$$DiagnosisHistoryItemImplFromJson(
        Map<String, dynamic> json) =>
    _$DiagnosisHistoryItemImpl(
      diagnosisId: json['diagnosisId'] as String,
      diseaseName: json['diseaseName'] as String,
      diseaseNameAr: json['diseaseNameAr'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      severity: json['severity'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      fieldId: json['fieldId'] as String?,
      imagePath: json['imagePath'] as String?,
      isResolved: json['isResolved'] as bool? ?? false,
    );

Map<String, dynamic> _$$DiagnosisHistoryItemImplToJson(
        _$DiagnosisHistoryItemImpl instance) =>
    <String, dynamic>{
      'diagnosisId': instance.diagnosisId,
      'diseaseName': instance.diseaseName,
      'diseaseNameAr': instance.diseaseNameAr,
      'confidence': instance.confidence,
      'severity': instance.severity,
      'timestamp': instance.timestamp.toIso8601String(),
      'fieldId': instance.fieldId,
      'imagePath': instance.imagePath,
      'isResolved': instance.isResolved,
    };
