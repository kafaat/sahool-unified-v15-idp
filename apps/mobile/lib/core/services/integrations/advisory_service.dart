/// SAHOOL Advisory Service Integration
/// تكامل خدمة الاستشارات الزراعية
///
/// Handles advisory-related operations:
/// - Fertilizer recommendations
/// - Crop health diagnosis
/// - Soil interpretation
/// - Deficiency symptoms
/// - AI-powered advice
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../network/api_result.dart';
import '../service_connector.dart';

/// Fertilizer recommendation model
class FertilizerRecommendation {
  final String id;
  final String? fieldId;
  final String cropType;
  final String? cropStage;
  final String fertilizerType;
  final String? fertilizerTypeAr;
  final double applicationRate;
  final String unit;
  final String? method;
  final String? methodAr;
  final String? timing;
  final String? timingAr;
  final String? reason;
  final String? reasonAr;
  final double? confidence;
  final Map<String, dynamic>? nutrients;
  final DateTime recommendationDate;

  const FertilizerRecommendation({
    required this.id,
    this.fieldId,
    required this.cropType,
    this.cropStage,
    required this.fertilizerType,
    this.fertilizerTypeAr,
    required this.applicationRate,
    required this.unit,
    this.method,
    this.methodAr,
    this.timing,
    this.timingAr,
    this.reason,
    this.reasonAr,
    this.confidence,
    this.nutrients,
    required this.recommendationDate,
  });

  factory FertilizerRecommendation.fromJson(Map<String, dynamic> json) {
    return FertilizerRecommendation(
      id: json['id'] as String? ?? '',
      fieldId: json['field_id'] as String?,
      cropType: json['crop_type'] as String? ?? '',
      cropStage: json['crop_stage'] as String?,
      fertilizerType: json['fertilizer_type'] as String? ?? '',
      fertilizerTypeAr: json['fertilizer_type_ar'] as String?,
      applicationRate: (json['application_rate'] as num?)?.toDouble() ?? 0.0,
      unit: json['unit'] as String? ?? 'kg/ha',
      method: json['method'] as String?,
      methodAr: json['method_ar'] as String?,
      timing: json['timing'] as String?,
      timingAr: json['timing_ar'] as String?,
      reason: json['reason'] as String?,
      reasonAr: json['reason_ar'] as String?,
      confidence: (json['confidence'] as num?)?.toDouble(),
      nutrients: json['nutrients'] as Map<String, dynamic>?,
      recommendationDate: json['recommendation_date'] != null
          ? DateTime.tryParse(json['recommendation_date'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }
}

/// Soil interpretation model
class SoilInterpretation {
  final String? fieldId;
  final double? ph;
  final String? phInterpretation;
  final String? phInterpretationAr;
  final double? organicMatter;
  final String? omInterpretation;
  final String? omInterpretationAr;
  final Map<String, dynamic>? nutrients;
  final Map<String, dynamic>? nutrientInterpretations;
  final String? overallAssessment;
  final String? overallAssessmentAr;
  final List<String>? recommendations;
  final List<String>? recommendationsAr;

  const SoilInterpretation({
    this.fieldId,
    this.ph,
    this.phInterpretation,
    this.phInterpretationAr,
    this.organicMatter,
    this.omInterpretation,
    this.omInterpretationAr,
    this.nutrients,
    this.nutrientInterpretations,
    this.overallAssessment,
    this.overallAssessmentAr,
    this.recommendations,
    this.recommendationsAr,
  });

  factory SoilInterpretation.fromJson(Map<String, dynamic> json) {
    return SoilInterpretation(
      fieldId: json['field_id'] as String?,
      ph: (json['ph'] as num?)?.toDouble(),
      phInterpretation: json['ph_interpretation'] as String?,
      phInterpretationAr: json['ph_interpretation_ar'] as String?,
      organicMatter: (json['organic_matter'] as num?)?.toDouble(),
      omInterpretation: json['om_interpretation'] as String?,
      omInterpretationAr: json['om_interpretation_ar'] as String?,
      nutrients: json['nutrients'] as Map<String, dynamic>?,
      nutrientInterpretations: json['nutrient_interpretations'] as Map<String, dynamic>?,
      overallAssessment: json['overall_assessment'] as String?,
      overallAssessmentAr: json['overall_assessment_ar'] as String?,
      recommendations: (json['recommendations'] as List?)?.cast<String>(),
      recommendationsAr: (json['recommendations_ar'] as List?)?.cast<String>(),
    );
  }
}

/// Deficiency symptom model
class DeficiencySymptom {
  final String nutrient;
  final String? nutrientAr;
  final String? symptomDescription;
  final String? symptomDescriptionAr;
  final List<String>? visualSigns;
  final List<String>? visualSignsAr;
  final String? affectedPlantParts;
  final String? affectedPlantPartsAr;
  final String? remedy;
  final String? remedyAr;
  final List<String>? recommendedFertilizers;
  final String? severity;

  const DeficiencySymptom({
    required this.nutrient,
    this.nutrientAr,
    this.symptomDescription,
    this.symptomDescriptionAr,
    this.visualSigns,
    this.visualSignsAr,
    this.affectedPlantParts,
    this.affectedPlantPartsAr,
    this.remedy,
    this.remedyAr,
    this.recommendedFertilizers,
    this.severity,
  });

  factory DeficiencySymptom.fromJson(Map<String, dynamic> json) {
    return DeficiencySymptom(
      nutrient: json['nutrient'] as String? ?? '',
      nutrientAr: json['nutrient_ar'] as String?,
      symptomDescription: json['symptom_description'] as String?,
      symptomDescriptionAr: json['symptom_description_ar'] as String?,
      visualSigns: (json['visual_signs'] as List?)?.cast<String>(),
      visualSignsAr: (json['visual_signs_ar'] as List?)?.cast<String>(),
      affectedPlantParts: json['affected_plant_parts'] as String?,
      affectedPlantPartsAr: json['affected_plant_parts_ar'] as String?,
      remedy: json['remedy'] as String?,
      remedyAr: json['remedy_ar'] as String?,
      recommendedFertilizers: (json['recommended_fertilizers'] as List?)?.cast<String>(),
      severity: json['severity'] as String?,
    );
  }
}

/// Application schedule model
class ApplicationSchedule {
  final String id;
  final String? fieldId;
  final String cropType;
  final String? cropStage;
  final List<ApplicationEvent> events;
  final DateTime generatedAt;

  const ApplicationSchedule({
    required this.id,
    this.fieldId,
    required this.cropType,
    this.cropStage,
    required this.events,
    required this.generatedAt,
  });

  factory ApplicationSchedule.fromJson(Map<String, dynamic> json) {
    return ApplicationSchedule(
      id: json['id'] as String? ?? '',
      fieldId: json['field_id'] as String?,
      cropType: json['crop_type'] as String? ?? '',
      cropStage: json['crop_stage'] as String?,
      events: ((json['events'] as List?) ?? [])
          .map((e) => ApplicationEvent.fromJson(e as Map<String, dynamic>))
          .toList(),
      generatedAt: json['generated_at'] != null
          ? DateTime.tryParse(json['generated_at'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }
}

/// Application event model
class ApplicationEvent {
  final String type;
  final String? typeAr;
  final String product;
  final String? productAr;
  final double rate;
  final String unit;
  final DateTime scheduledDate;
  final String? method;
  final String? methodAr;
  final String? notes;
  final String? notesAr;
  final String? status;

  const ApplicationEvent({
    required this.type,
    this.typeAr,
    required this.product,
    this.productAr,
    required this.rate,
    required this.unit,
    required this.scheduledDate,
    this.method,
    this.methodAr,
    this.notes,
    this.notesAr,
    this.status,
  });

  factory ApplicationEvent.fromJson(Map<String, dynamic> json) {
    return ApplicationEvent(
      type: json['type'] as String? ?? '',
      typeAr: json['type_ar'] as String?,
      product: json['product'] as String? ?? '',
      productAr: json['product_ar'] as String?,
      rate: (json['rate'] as num?)?.toDouble() ?? 0.0,
      unit: json['unit'] as String? ?? '',
      scheduledDate: DateTime.tryParse(json['scheduled_date'] as String) ?? DateTime.now(),
      method: json['method'] as String?,
      methodAr: json['method_ar'] as String?,
      notes: json['notes'] as String?,
      notesAr: json['notes_ar'] as String?,
      status: json['status'] as String?,
    );
  }
}

/// Crop health diagnosis result
class CropHealthDiagnosis {
  final String id;
  final String? fieldId;
  final String? cropType;
  final String? imageUrl;
  final String diagnosis;
  final String? diagnosisAr;
  final double confidence;
  final String? severity;
  final String? severityAr;
  final String? description;
  final String? descriptionAr;
  final List<String>? treatments;
  final List<String>? treatmentsAr;
  final List<String>? preventions;
  final List<String>? preventionsAr;
  final DateTime diagnosedAt;

  const CropHealthDiagnosis({
    required this.id,
    this.fieldId,
    this.cropType,
    this.imageUrl,
    required this.diagnosis,
    this.diagnosisAr,
    required this.confidence,
    this.severity,
    this.severityAr,
    this.description,
    this.descriptionAr,
    this.treatments,
    this.treatmentsAr,
    this.preventions,
    this.preventionsAr,
    required this.diagnosedAt,
  });

  factory CropHealthDiagnosis.fromJson(Map<String, dynamic> json) {
    return CropHealthDiagnosis(
      id: json['id'] as String? ?? '',
      fieldId: json['field_id'] as String?,
      cropType: json['crop_type'] as String?,
      imageUrl: json['image_url'] as String?,
      diagnosis: json['diagnosis'] as String? ?? '',
      diagnosisAr: json['diagnosis_ar'] as String?,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      severity: json['severity'] as String?,
      severityAr: json['severity_ar'] as String?,
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      treatments: (json['treatments'] as List?)?.cast<String>(),
      treatmentsAr: (json['treatments_ar'] as List?)?.cast<String>(),
      preventions: (json['preventions'] as List?)?.cast<String>(),
      preventionsAr: (json['preventions_ar'] as List?)?.cast<String>(),
      diagnosedAt: json['diagnosed_at'] != null
          ? DateTime.tryParse(json['diagnosed_at'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }
}

/// AI Advisory response
class AiAdvisoryResponse {
  final String id;
  final String query;
  final String response;
  final String? responseAr;
  final double? confidence;
  final List<String>? sources;
  final Map<String, dynamic>? context;
  final DateTime timestamp;

  const AiAdvisoryResponse({
    required this.id,
    required this.query,
    required this.response,
    this.responseAr,
    this.confidence,
    this.sources,
    this.context,
    required this.timestamp,
  });

  factory AiAdvisoryResponse.fromJson(Map<String, dynamic> json) {
    return AiAdvisoryResponse(
      id: json['id'] as String? ?? '',
      query: json['query'] as String? ?? '',
      response: json['response'] as String? ?? '',
      responseAr: json['response_ar'] as String?,
      confidence: (json['confidence'] as num?)?.toDouble(),
      sources: (json['sources'] as List?)?.cast<String>(),
      context: json['context'] as Map<String, dynamic>?,
      timestamp: json['timestamp'] != null
          ? DateTime.tryParse(json['timestamp'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }
}

/// Advisory Service Connector
/// موصل خدمة الاستشارات
class AdvisoryServiceConnector extends ServiceConnector {
  AdvisoryServiceConnector({required super.ref}) : super(serviceId: 'advisory');

  /// Get fertilizer recommendation
  /// الحصول على توصية التسميد
  Future<ApiResult<FertilizerRecommendation>> getRecommendation({
    required String cropType,
    String? cropStage,
    String? fieldId,
    Map<String, dynamic>? soilData,
    double? targetYield,
  }) async {
    return post(
      getEndpoint('recommend') ?? '/api/v1/fertilizer/recommend',
      data: {
        'crop_type': cropType,
        if (cropStage != null) 'crop_stage': cropStage,
        if (fieldId != null) 'field_id': fieldId,
        if (soilData != null) 'soil_data': soilData,
        if (targetYield != null) 'target_yield': targetYield,
      },
      parser: (data) => FertilizerRecommendation.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Get soil interpretation
  /// الحصول على تفسير التربة
  Future<ApiResult<SoilInterpretation>> interpretSoil({
    double? ph,
    double? organicMatter,
    double? nitrogen,
    double? phosphorus,
    double? potassium,
    String? fieldId,
    Map<String, dynamic>? additionalNutrients,
  }) async {
    return post(
      getEndpoint('soil-interpret') ?? '/api/v1/fertilizer/soil/interpret',
      data: {
        if (ph != null) 'ph': ph,
        if (organicMatter != null) 'organic_matter': organicMatter,
        if (nitrogen != null) 'nitrogen': nitrogen,
        if (phosphorus != null) 'phosphorus': phosphorus,
        if (potassium != null) 'potassium': potassium,
        if (fieldId != null) 'field_id': fieldId,
        if (additionalNutrients != null) ...additionalNutrients,
      },
      parser: (data) => SoilInterpretation.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Get deficiency symptoms
  /// الحصول على أعراض النقص
  Future<ApiResult<List<DeficiencySymptom>>> getDeficiencySymptoms({
    String? nutrient,
    String? cropType,
  }) async {
    final queryParams = <String, dynamic>{
      if (nutrient != null) 'nutrient': nutrient,
      if (cropType != null) 'crop_type': cropType,
    };

    return get(
      getEndpoint('deficiency-symptoms') ?? '/api/v1/fertilizer/deficiency/symptoms',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
      parser: (data) {
        if (data is List) {
          return data.map((e) => DeficiencySymptom.fromJson(e as Map<String, dynamic>)).toList();
        }
        if (data is Map && data['symptoms'] != null) {
          return (data['symptoms'] as List? ?? [])
              .map((e) => DeficiencySymptom.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <DeficiencySymptom>[];
      },
    );
  }

  /// Get application schedule
  /// الحصول على جدول التطبيق
  Future<ApiResult<ApplicationSchedule>> getSchedule({
    required String cropType,
    String? cropStage,
    String? fieldId,
    DateTime? startDate,
  }) async {
    return post(
      getEndpoint('schedule') ?? '/api/v1/fertilizer/schedule',
      data: {
        'crop_type': cropType,
        if (cropStage != null) 'crop_stage': cropStage,
        if (fieldId != null) 'field_id': fieldId,
        if (startDate != null) 'start_date': startDate.toIso8601String(),
      },
      parser: (data) => ApplicationSchedule.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Get supported crops
  /// الحصول على المحاصيل المدعومة
  Future<ApiResult<List<Map<String, dynamic>>>> getCrops() async {
    return get(
      getEndpoint('crops') ?? '/api/v1/fertilizer/crops',
      parser: (data) {
        if (data is List) {
          return data.cast<Map<String, dynamic>>();
        }
        if (data is Map && data['crops'] != null) {
          return (data['crops'] as List? ?? []).cast<Map<String, dynamic>>();
        }
        return <Map<String, dynamic>>[];
      },
    );
  }

  /// Get fertilizer types
  /// الحصول على أنواع الأسمدة
  Future<ApiResult<List<Map<String, dynamic>>>> getFertilizerTypes() async {
    return get(
      getEndpoint('fertilizers') ?? '/api/v1/fertilizer/fertilizers',
      parser: (data) {
        if (data is List) {
          return data.cast<Map<String, dynamic>>();
        }
        if (data is Map && data['fertilizers'] != null) {
          return (data['fertilizers'] as List? ?? []).cast<Map<String, dynamic>>();
        }
        return <Map<String, dynamic>>[];
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Crop Health AI Methods
  // ═══════════════════════════════════════════════════════════════════════════════

  /// Diagnose crop health from image
  /// تشخيص صحة المحصول من الصورة
  Future<ApiResult<CropHealthDiagnosis>> diagnose({
    required String imagePath,
    String? cropType,
    String? fieldId,
  }) async {
    return uploadFile(
      '/api/v1/diagnose',
      filePath: imagePath,
      fieldName: 'image',
      additionalData: {
        if (cropType != null) 'crop_type': cropType,
        if (fieldId != null) 'field_id': fieldId,
      },
      parser: (data) => CropHealthDiagnosis.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Get AI advisory response
  /// الحصول على استجابة المستشار الذكي
  Future<ApiResult<AiAdvisoryResponse>> askAiAdvisor({
    required String query,
    String? fieldId,
    String? cropType,
    Map<String, dynamic>? context,
  }) async {
    return post(
      '/api/v1/ai-advisor/query',
      data: {
        'query': query,
        if (fieldId != null) 'field_id': fieldId,
        if (cropType != null) 'crop_type': cropType,
        if (context != null) 'context': context,
      },
      parser: (data) => AiAdvisoryResponse.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Get field recommendations
  /// الحصول على توصيات الحقل
  Future<ApiResult<List<FertilizerRecommendation>>> getFieldRecommendations(
    String fieldId,
  ) async {
    return get(
      '/api/v1/ai-advisor/recommendations/$fieldId',
      parser: (data) {
        if (data is List) {
          return data
              .map((e) => FertilizerRecommendation.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        if (data is Map && data['recommendations'] != null) {
          return (data['recommendations'] as List? ?? [])
              .map((e) => FertilizerRecommendation.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <FertilizerRecommendation>[];
      },
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Advisory Service Provider
final advisoryServiceProvider = Provider<AdvisoryServiceConnector>((ref) {
  return AdvisoryServiceConnector(ref: ref);
});

/// Deficiency Symptoms Provider
final deficiencySymptomsProvider =
    FutureProvider.family<List<DeficiencySymptom>, String?>((ref, cropType) async {
  final service = ref.watch(advisoryServiceProvider);
  final result = await service.getDeficiencySymptoms(cropType: cropType);
  return result.dataOrNull ?? [];
});

/// Supported Crops Provider
final supportedCropsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final service = ref.watch(advisoryServiceProvider);
  final result = await service.getCrops();
  return result.dataOrNull ?? [];
});

/// Fertilizer Types Provider
final fertilizerTypesProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final service = ref.watch(advisoryServiceProvider);
  final result = await service.getFertilizerTypes();
  return result.dataOrNull ?? [];
});

/// Field Recommendations Provider
final fieldRecommendationsProvider =
    FutureProvider.family<List<FertilizerRecommendation>, String>((ref, fieldId) async {
  final service = ref.watch(advisoryServiceProvider);
  final result = await service.getFieldRecommendations(fieldId);
  return result.dataOrNull ?? [];
});
