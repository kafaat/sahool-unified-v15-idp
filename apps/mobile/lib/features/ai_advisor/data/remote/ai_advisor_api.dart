import '../../../../core/http/api_client.dart';

/// AI Advisor API - Multi-Agent Agricultural Intelligence
/// خدمة المستشار الذكي - الذكاء الاصطناعي المتعدد الوكلاء
class AiAdvisorApi {
  final ApiClient _client;

  AiAdvisorApi(this._client);

  /// Ask a general agricultural question
  /// طرح سؤال زراعي عام
  Future<AdvisorResponse> ask({
    required String question,
    String? fieldId,
    String language = 'ar',
  }) async {
    final response = await _client.post(
      '/api/v1/advisor/ask',
      {
        'query': question,
        'field_id': fieldId,
        'language': language,
        'tenant_id': _client.tenantId,
      },
    );

    if (response is Map<String, dynamic>) {
      return AdvisorResponse.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تحليل الاستجابة',
    );
  }

  /// Get crop health diagnosis with image
  /// تشخيص صحة المحصول بالصورة
  Future<DiagnosisResponse> diagnose({
    required String imagePath,
    String? cropType,
    String? fieldId,
  }) async {
    final response = await _client.uploadFile(
      '/api/v1/advisor/diagnose',
      imagePath,
      fieldName: 'image',
      extraData: {
        'crop_type': cropType,
        'field_id': fieldId,
        'tenant_id': _client.tenantId,
      },
    );

    if (response is Map<String, dynamic>) {
      return DiagnosisResponse.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تحليل التشخيص',
    );
  }

  /// Get personalized recommendations for a field
  /// الحصول على توصيات مخصصة للحقل
  Future<RecommendationsResponse> getRecommendations({
    required String fieldId,
    String? focus, // irrigation, fertilization, pest_control
  }) async {
    final queryParams = <String, dynamic>{
      'field_id': fieldId,
      'tenant_id': _client.tenantId,
    };

    if (focus != null) {
      queryParams['focus'] = focus;
    }

    final response = await _client.get(
      '/api/v1/advisor/recommend',
      queryParameters: queryParams,
    );

    if (response is Map<String, dynamic>) {
      return RecommendationsResponse.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تحليل التوصيات',
    );
  }

  /// Analyze a field comprehensively
  /// تحليل شامل للحقل
  Future<FieldAnalysisResponse> analyzeField({
    required String fieldId,
  }) async {
    final response = await _client.post(
      '/api/v1/advisor/analyze-field',
      {
        'field_id': fieldId,
        'tenant_id': _client.tenantId,
      },
    );

    if (response is Map<String, dynamic>) {
      return FieldAnalysisResponse.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تحليل الحقل',
    );
  }

  /// Get chat history
  /// الحصول على سجل المحادثة
  Future<List<ChatMessage>> getChatHistory({int limit = 50}) async {
    final response = await _client.get(
      '/api/v1/advisor/history',
      queryParameters: {
        'tenant_id': _client.tenantId,
        'limit': limit,
      },
    );

    if (response is List) {
      return response
          .cast<Map<String, dynamic>>()
          .map((json) => ChatMessage.fromJson(json))
          .toList();
    }

    return [];
  }
}

/// Advisor response model
class AdvisorResponse {
  final String answer;
  final String? answerAr;
  final double confidence;
  final List<String> sources;
  final Map<String, dynamic>? metadata;

  AdvisorResponse({
    required this.answer,
    this.answerAr,
    required this.confidence,
    required this.sources,
    this.metadata,
  });

  factory AdvisorResponse.fromJson(Map<String, dynamic> json) {
    return AdvisorResponse(
      answer: json['answer'] ?? json['response'] ?? '',
      answerAr: json['answer_ar'],
      confidence: (json['confidence'] ?? 0.8).toDouble(),
      sources: (json['sources'] as List?)?.cast<String>() ?? [],
      metadata: json['metadata'],
    );
  }
}

/// Diagnosis response model
class DiagnosisResponse {
  final String disease;
  final String diseaseAr;
  final double confidence;
  final String severity;
  final List<String> symptoms;
  final List<String> treatments;
  final List<String> preventionMeasures;

  DiagnosisResponse({
    required this.disease,
    required this.diseaseAr,
    required this.confidence,
    required this.severity,
    required this.symptoms,
    required this.treatments,
    required this.preventionMeasures,
  });

  factory DiagnosisResponse.fromJson(Map<String, dynamic> json) {
    return DiagnosisResponse(
      disease: json['disease'] ?? json['diagnosis'] ?? 'Unknown',
      diseaseAr: json['disease_ar'] ?? json['diagnosis_ar'] ?? 'غير معروف',
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      severity: json['severity'] ?? 'moderate',
      symptoms: (json['symptoms'] as List?)?.cast<String>() ?? [],
      treatments: (json['treatments'] as List?)?.cast<String>() ?? [],
      preventionMeasures: (json['prevention'] as List?)?.cast<String>() ?? [],
    );
  }
}

/// Recommendations response model
class RecommendationsResponse {
  final List<Recommendation> recommendations;
  final Map<String, dynamic>? fieldStatus;

  RecommendationsResponse({
    required this.recommendations,
    this.fieldStatus,
  });

  factory RecommendationsResponse.fromJson(Map<String, dynamic> json) {
    final recs = json['recommendations'] as List? ?? [];
    return RecommendationsResponse(
      recommendations: recs
          .cast<Map<String, dynamic>>()
          .map((r) => Recommendation.fromJson(r))
          .toList(),
      fieldStatus: json['field_status'],
    );
  }
}

/// Single recommendation
class Recommendation {
  final String type;
  final String title;
  final String titleAr;
  final String description;
  final String descriptionAr;
  final String priority;
  final DateTime? dueDate;

  Recommendation({
    required this.type,
    required this.title,
    required this.titleAr,
    required this.description,
    required this.descriptionAr,
    required this.priority,
    this.dueDate,
  });

  factory Recommendation.fromJson(Map<String, dynamic> json) {
    return Recommendation(
      type: json['type'] ?? 'general',
      title: json['title'] ?? '',
      titleAr: json['title_ar'] ?? json['title'] ?? '',
      description: json['description'] ?? '',
      descriptionAr: json['description_ar'] ?? json['description'] ?? '',
      priority: json['priority'] ?? 'medium',
      dueDate: json['due_date'] != null
          ? DateTime.tryParse(json['due_date'])
          : null,
    );
  }
}

/// Field analysis response
class FieldAnalysisResponse {
  final double healthScore;
  final String healthStatus;
  final Map<String, dynamic> ndviAnalysis;
  final Map<String, dynamic> weatherImpact;
  final List<String> alerts;
  final List<Recommendation> recommendations;

  FieldAnalysisResponse({
    required this.healthScore,
    required this.healthStatus,
    required this.ndviAnalysis,
    required this.weatherImpact,
    required this.alerts,
    required this.recommendations,
  });

  factory FieldAnalysisResponse.fromJson(Map<String, dynamic> json) {
    final recs = json['recommendations'] as List? ?? [];
    return FieldAnalysisResponse(
      healthScore: (json['health_score'] ?? 0.0).toDouble(),
      healthStatus: json['health_status'] ?? 'unknown',
      ndviAnalysis: json['ndvi_analysis'] ?? {},
      weatherImpact: json['weather_impact'] ?? {},
      alerts: (json['alerts'] as List?)?.cast<String>() ?? [],
      recommendations: recs
          .cast<Map<String, dynamic>>()
          .map((r) => Recommendation.fromJson(r))
          .toList(),
    );
  }
}

/// Chat message model
class ChatMessage {
  final String id;
  final String role; // user, assistant
  final String content;
  final DateTime timestamp;

  ChatMessage({
    required this.id,
    required this.role,
    required this.content,
    required this.timestamp,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] ?? '',
      role: json['role'] ?? 'assistant',
      content: json['content'] ?? '',
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
    );
  }
}

/// Exception class (imported from api_client but defined here for completeness)
class ApiException implements Exception {
  final String code;
  final String message;

  ApiException({required this.code, required this.message});
}
