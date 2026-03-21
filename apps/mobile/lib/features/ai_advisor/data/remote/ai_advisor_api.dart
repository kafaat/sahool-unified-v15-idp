/// AI Advisor API - Multi-Agent Agricultural Intelligence
/// خدمة المستشار الذكي - الذكاء الاصطناعي المتعدد الوكلاء
///
/// Provides communication with the AI advisory backend services

import '../../../../core/http/api_client.dart';
import '../../domain/models/advisory.dart';
import '../../domain/models/advisory_request.dart';
import '../../domain/models/advisory_context.dart';
import '../../domain/models/advisory_feedback.dart';

/// AI Advisor API Service
class AiAdvisorApi {
  final ApiClient _client;

  AiAdvisorApi(this._client);

  // ─────────────────────────────────────────────────────────────────────────────
  // Chat & Questions
  // ─────────────────────────────────────────────────────────────────────────────

  /// Ask a general agricultural question
  /// طرح سؤال زراعي عام
  Future<ChatResponse> ask({
    required String question,
    String? fieldId,
    String? cropType,
    String language = 'ar',
    bool includeContext = true,
  }) async {
    final response = await _client.post(
      '/api/v1/advisor/ask',
      {
        'query': question,
        'field_id': fieldId,
        'crop_type': cropType,
        'language': language,
        'include_context': includeContext,
        'tenant_id': _client.tenantId,
      },
    );

    if (response is Map<String, dynamic>) {
      return ChatResponse.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تحليل الاستجابة',
    );
  }

  /// Send advisory request (question, diagnosis, recommendation, analysis)
  /// إرسال طلب استشارة
  Future<AdvisoryResponse> sendRequest(AdvisoryRequest request) async {
    final endpoint = _getEndpointForRequestType(request.type);

    final response = await _client.post(
      endpoint,
      {
        ...request.toJson(),
        'tenant_id': _client.tenantId,
      },
    );

    if (response is Map<String, dynamic>) {
      return AdvisoryResponse.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تحليل الاستجابة',
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Diagnosis
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get crop health diagnosis with image
  /// تشخيص صحة المحصول بالصورة
  Future<DiagnosisResponse> diagnose({
    required String imagePath,
    String? cropType,
    String? fieldId,
    String? symptoms,
    String language = 'ar',
  }) async {
    final response = await _client.uploadFile(
      '/api/v1/advisor/diagnose',
      imagePath,
      fieldName: 'image',
      extraData: {
        'crop_type': cropType,
        'field_id': fieldId,
        'symptoms': symptoms,
        'language': language,
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

  // ─────────────────────────────────────────────────────────────────────────────
  // Recommendations
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get personalized recommendations for a field
  /// الحصول على توصيات مخصصة للحقل
  Future<RecommendationsResponse> getRecommendations({
    required String fieldId,
    AdvisoryType? focus,
    String language = 'ar',
  }) async {
    final queryParams = <String, dynamic>{
      'field_id': fieldId,
      'language': language,
      'tenant_id': _client.tenantId,
    };

    if (focus != null) {
      queryParams['focus'] = focus.name;
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

  /// Get irrigation recommendation
  /// الحصول على توصية الري
  Future<Advisory> getIrrigationRecommendation({
    required String fieldId,
    String language = 'ar',
  }) async {
    final response = await _client.post(
      '/api/v1/advisor/irrigation',
      {
        'field_id': fieldId,
        'language': language,
        'tenant_id': _client.tenantId,
      },
    );

    if (response is Map<String, dynamic>) {
      return Advisory.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تحليل توصية الري',
    );
  }

  /// Get fertilizer recommendation
  /// الحصول على توصية التسميد
  Future<Advisory> getFertilizerRecommendation({
    required String fieldId,
    String language = 'ar',
  }) async {
    final response = await _client.post(
      '/api/v1/advisor/fertilizer',
      {
        'field_id': fieldId,
        'language': language,
        'tenant_id': _client.tenantId,
      },
    );

    if (response is Map<String, dynamic>) {
      return Advisory.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تحليل توصية التسميد',
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Field Analysis
  // ─────────────────────────────────────────────────────────────────────────────

  /// Analyze a field comprehensively
  /// تحليل شامل للحقل
  Future<FieldAnalysisResponse> analyzeField({
    required String fieldId,
    String language = 'ar',
  }) async {
    final response = await _client.post(
      '/api/v1/advisor/analyze-field',
      {
        'field_id': fieldId,
        'language': language,
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

  // ─────────────────────────────────────────────────────────────────────────────
  // Context
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get advisory context for a field
  /// الحصول على سياق التوصية للحقل
  Future<AdvisoryContext> getContext({
    String? fieldId,
    bool includeWeather = true,
    bool includeSoil = true,
    bool includeCrop = true,
    bool includeHistory = false,
  }) async {
    final queryParams = <String, dynamic>{
      'tenant_id': _client.tenantId,
      'include_weather': includeWeather,
      'include_soil': includeSoil,
      'include_crop': includeCrop,
      'include_history': includeHistory,
    };

    if (fieldId != null) {
      queryParams['field_id'] = fieldId;
    }

    final response = await _client.get(
      '/api/v1/advisor/context',
      queryParameters: queryParams,
    );

    if (response is Map<String, dynamic>) {
      return AdvisoryContext.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تحليل السياق',
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // History
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get chat history
  /// الحصول على سجل المحادثة
  Future<List<ChatMessage>> getChatHistory({
    int limit = 50,
    int offset = 0,
    String? fieldId,
  }) async {
    final queryParams = <String, dynamic>{
      'tenant_id': _client.tenantId,
      'limit': limit,
      'offset': offset,
    };

    if (fieldId != null) {
      queryParams['field_id'] = fieldId;
    }

    final response = await _client.get(
      '/api/v1/advisor/history',
      queryParameters: queryParams,
    );

    if (response is List) {
      return response
          .cast<Map<String, dynamic>>()
          .map((json) => ChatMessage.fromJson(json))
          .toList();
    }

    return [];
  }

  /// Get advisory history
  /// الحصول على سجل التوصيات
  Future<List<Advisory>> getAdvisoryHistory({
    int limit = 20,
    int offset = 0,
    String? fieldId,
    AdvisoryType? type,
    AdvisoryStatus? status,
  }) async {
    final queryParams = <String, dynamic>{
      'tenant_id': _client.tenantId,
      'limit': limit,
      'offset': offset,
    };

    if (fieldId != null) queryParams['field_id'] = fieldId;
    if (type != null) queryParams['type'] = type.name;
    if (status != null) queryParams['status'] = status.name;

    final response = await _client.get(
      '/api/v1/advisor/advisories',
      queryParameters: queryParams,
    );

    if (response is List) {
      return response
          .cast<Map<String, dynamic>>()
          .map((json) => Advisory.fromJson(json))
          .toList();
    }

    if (response is Map && response['data'] is List) {
      return (response['data'] as List)
          .cast<Map<String, dynamic>>()
          .map((json) => Advisory.fromJson(json))
          .toList();
    }

    return [];
  }

  /// Get single advisory by ID
  /// الحصول على توصية واحدة
  Future<Advisory> getAdvisory(String advisoryId) async {
    final response = await _client.get(
      '/api/v1/advisor/advisories/$advisoryId',
      queryParameters: {'tenant_id': _client.tenantId},
    );

    if (response is Map<String, dynamic>) {
      return Advisory.fromJson(response);
    }

    throw ApiException(
      code: 'PARSE_ERROR',
      message: 'فشل في تحليل التوصية',
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Feedback
  // ─────────────────────────────────────────────────────────────────────────────

  /// Submit feedback for an advisory
  /// إرسال ردود الفعل على التوصية
  Future<void> submitFeedback(AdvisoryFeedback feedback) async {
    await _client.post(
      '/api/v1/advisor/feedback',
      {
        ...feedback.toJson(),
        'tenant_id': _client.tenantId,
      },
    );
  }

  /// Update advisory status (applied/dismissed)
  /// تحديث حالة التوصية
  Future<void> updateAdvisoryStatus({
    required String advisoryId,
    required AdvisoryStatus status,
  }) async {
    await _client.put(
      '/api/v1/advisor/advisories/$advisoryId/status',
      {
        'status': status.name,
        'tenant_id': _client.tenantId,
      },
    );
  }

  /// Clear chat history
  /// مسح سجل المحادثة
  Future<void> clearChatHistory() async {
    await _client.delete(
      '/api/v1/advisor/history',
      queryParameters: {'tenant_id': _client.tenantId},
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Helpers
  // ─────────────────────────────────────────────────────────────────────────────

  String _getEndpointForRequestType(AdvisoryRequestType type) {
    switch (type) {
      case AdvisoryRequestType.question:
        return '/api/v1/advisor/ask';
      case AdvisoryRequestType.diagnosis:
        return '/api/v1/advisor/diagnose';
      case AdvisoryRequestType.recommendation:
        return '/api/v1/advisor/recommend';
      case AdvisoryRequestType.analysis:
        return '/api/v1/advisor/analyze';
    }
  }
}

// =============================================================================
// Response Models
// =============================================================================

/// Chat response model
/// نموذج استجابة المحادثة
class ChatResponse {
  final String id;
  final String answer;
  final String? answerAr;
  final double confidence;
  final List<String> sources;
  final AdvisoryContext? context;
  final List<Advisory>? recommendations;
  final Map<String, dynamic>? metadata;

  ChatResponse({
    required this.id,
    required this.answer,
    this.answerAr,
    required this.confidence,
    required this.sources,
    this.context,
    this.recommendations,
    this.metadata,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      id: json['id'] as String? ?? '',
      answer: (json['answer'] ?? json['response'] ?? '') as String,
      answerAr: json['answer_ar'] as String?,
      confidence: ((json['confidence'] ?? 0.8) as num).toDouble(),
      sources: (json['sources'] as List?)?.cast<String>() ?? [],
      context: json['context'] != null
          ? AdvisoryContext.fromJson(json['context'] as Map<String, dynamic>)
          : null,
      recommendations: (json['recommendations'] as List?)
          ?.cast<Map<String, dynamic>>()
          .map((r) => Advisory.fromJson(r))
          .toList(),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }
}

/// Advisory response model (wrapper for request responses)
/// نموذج استجابة التوصية
class AdvisoryResponse {
  final String id;
  final String response;
  final String? responseAr;
  final double confidence;
  final List<Advisory> advisories;
  final AdvisoryContext? context;
  final Map<String, dynamic>? metadata;

  AdvisoryResponse({
    required this.id,
    required this.response,
    this.responseAr,
    required this.confidence,
    required this.advisories,
    this.context,
    this.metadata,
  });

  factory AdvisoryResponse.fromJson(Map<String, dynamic> json) {
    return AdvisoryResponse(
      id: json['id'] as String? ?? '',
      response: (json['response'] ?? json['answer'] ?? '') as String,
      responseAr: (json['response_ar'] ?? json['answer_ar']) as String?,
      confidence: ((json['confidence'] ?? 0.8) as num).toDouble(),
      advisories: (json['advisories'] as List?)
              ?.cast<Map<String, dynamic>>()
              .map((r) => Advisory.fromJson(r))
              .toList() ??
          [],
      context: json['context'] != null
          ? AdvisoryContext.fromJson(json['context'] as Map<String, dynamic>)
          : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }
}

/// Diagnosis response model
/// نموذج استجابة التشخيص
class DiagnosisResponse {
  final String id;
  final String disease;
  final String diseaseAr;
  final double confidence;
  final String severity;
  final String severityAr;
  final List<String> symptoms;
  final List<String> symptomsAr;
  final List<String> treatments;
  final List<String> treatmentsAr;
  final List<String> preventionMeasures;
  final List<String> preventionMeasuresAr;
  final Advisory? advisory;
  final Map<String, dynamic>? metadata;

  DiagnosisResponse({
    required this.id,
    required this.disease,
    required this.diseaseAr,
    required this.confidence,
    required this.severity,
    required this.severityAr,
    required this.symptoms,
    required this.symptomsAr,
    required this.treatments,
    required this.treatmentsAr,
    required this.preventionMeasures,
    required this.preventionMeasuresAr,
    this.advisory,
    this.metadata,
  });

  factory DiagnosisResponse.fromJson(Map<String, dynamic> json) {
    return DiagnosisResponse(
      id: json['id'] as String? ?? '',
      disease: (json['disease'] ?? json['diagnosis'] ?? 'Unknown') as String,
      diseaseAr: (json['disease_ar'] ?? json['diagnosis_ar'] ?? 'غير معروف') as String,
      confidence: ((json['confidence'] ?? 0.0) as num).toDouble(),
      severity: (json['severity'] ?? 'moderate') as String,
      severityAr: (json['severity_ar'] ?? 'متوسط') as String,
      symptoms: (json['symptoms'] as List?)?.cast<String>() ?? [],
      symptomsAr: (json['symptoms_ar'] as List?)?.cast<String>() ??
                  (json['symptoms'] as List?)?.cast<String>() ?? [],
      treatments: (json['treatments'] as List?)?.cast<String>() ?? [],
      treatmentsAr: (json['treatments_ar'] as List?)?.cast<String>() ??
                    (json['treatments'] as List?)?.cast<String>() ?? [],
      preventionMeasures: (json['prevention'] as List?)?.cast<String>() ?? [],
      preventionMeasuresAr: (json['prevention_ar'] as List?)?.cast<String>() ??
                           (json['prevention'] as List?)?.cast<String>() ?? [],
      advisory: json['advisory'] != null
          ? Advisory.fromJson(json['advisory'] as Map<String, dynamic>)
          : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  /// Get severity color (hex)
  String get severityColorHex {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'severe':
        return '#DC2626';
      case 'high':
        return '#F59E0B';
      case 'moderate':
      case 'medium':
        return '#3B82F6';
      case 'low':
      case 'mild':
        return '#10B981';
      default:
        return '#6B7280';
    }
  }
}

/// Recommendations response model
/// نموذج استجابة التوصيات
class RecommendationsResponse {
  final List<Advisory> recommendations;
  final AdvisoryContext? context;
  final Map<String, dynamic>? fieldStatus;

  RecommendationsResponse({
    required this.recommendations,
    this.context,
    this.fieldStatus,
  });

  factory RecommendationsResponse.fromJson(Map<String, dynamic> json) {
    final recs = json['recommendations'] as List? ?? [];
    return RecommendationsResponse(
      recommendations: recs
          .cast<Map<String, dynamic>>()
          .map((r) => Advisory.fromJson(r))
          .toList(),
      context: json['context'] != null
          ? AdvisoryContext.fromJson(json['context'] as Map<String, dynamic>)
          : null,
      fieldStatus: json['field_status'] as Map<String, dynamic>?,
    );
  }
}

/// Field analysis response
/// نموذج استجابة تحليل الحقل
class FieldAnalysisResponse {
  final String fieldId;
  final double healthScore;
  final String healthStatus;
  final String healthStatusAr;
  final Map<String, dynamic> ndviAnalysis;
  final Map<String, dynamic> weatherImpact;
  final List<String> alerts;
  final List<String> alertsAr;
  final List<Advisory> recommendations;
  final AdvisoryContext? context;

  FieldAnalysisResponse({
    required this.fieldId,
    required this.healthScore,
    required this.healthStatus,
    required this.healthStatusAr,
    required this.ndviAnalysis,
    required this.weatherImpact,
    required this.alerts,
    required this.alertsAr,
    required this.recommendations,
    this.context,
  });

  factory FieldAnalysisResponse.fromJson(Map<String, dynamic> json) {
    final recs = json['recommendations'] as List? ?? [];
    return FieldAnalysisResponse(
      fieldId: json['field_id'] as String? ?? '',
      healthScore: ((json['health_score'] ?? 0.0) as num).toDouble(),
      healthStatus: (json['health_status'] ?? 'unknown') as String,
      healthStatusAr: (json['health_status_ar'] ?? 'غير معروف') as String,
      ndviAnalysis: json['ndvi_analysis'] as Map<String, dynamic>? ?? {},
      weatherImpact: json['weather_impact'] as Map<String, dynamic>? ?? {},
      alerts: (json['alerts'] as List?)?.cast<String>() ?? [],
      alertsAr: (json['alerts_ar'] as List?)?.cast<String>() ??
                (json['alerts'] as List?)?.cast<String>() ?? [],
      recommendations: recs
          .cast<Map<String, dynamic>>()
          .map((r) => Advisory.fromJson(r))
          .toList(),
      context: json['context'] != null
          ? AdvisoryContext.fromJson(json['context'] as Map<String, dynamic>)
          : null,
    );
  }
}

/// Chat message model
/// نموذج رسالة المحادثة
class ChatMessage {
  final String id;
  final String role; // user, assistant, system
  final String content;
  final String? contentAr;
  final DateTime timestamp;
  final String? fieldId;
  final Map<String, dynamic>? metadata;
  final List<Advisory>? recommendations;

  ChatMessage({
    required this.id,
    required this.role,
    required this.content,
    this.contentAr,
    required this.timestamp,
    this.fieldId,
    this.metadata,
    this.recommendations,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] as String? ?? '',
      role: json['role'] as String? ?? 'assistant',
      content: json['content'] as String? ?? '',
      contentAr: json['content_ar'] as String?,
      timestamp: DateTime.tryParse((json['timestamp'] ?? '') as String) ?? DateTime.now(),
      fieldId: json['field_id'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      recommendations: (json['recommendations'] as List?)
          ?.cast<Map<String, dynamic>>()
          .map((r) => Advisory.fromJson(r))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'role': role,
    'content': content,
    'content_ar': contentAr,
    'timestamp': timestamp.toIso8601String(),
    'field_id': fieldId,
    'metadata': metadata,
    'recommendations': recommendations?.map((r) => r.toJson()).toList(),
  };

  bool get isUser => role == 'user';
  bool get isAssistant => role == 'assistant';
  bool get isSystem => role == 'system';
}

/// API Exception class
class ApiException implements Exception {
  final String code;
  final String message;
  final int? statusCode;
  final bool isNetworkError;
  final bool isSecurityError;

  ApiException({
    required this.code,
    required this.message,
    this.statusCode,
    this.isNetworkError = false,
    this.isSecurityError = false,
  });

  @override
  String toString() => 'ApiException($code): $message';
}
