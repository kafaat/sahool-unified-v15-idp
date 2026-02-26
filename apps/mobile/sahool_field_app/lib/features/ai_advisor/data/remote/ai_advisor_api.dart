import '../../../../core/api/kong_gateway_client.dart';

/// AI Advisor API - Multi-Agent Agricultural Intelligence
/// خدمة المستشار الذكي - الذكاء الاصطناعي المتعدد الوكلاء
///
/// Connected to copilot-api service (port 8088) via Kong gateway
/// Supports RAG search, multi-LLM chat, tool execution
class AiAdvisorApi {
  final KongGatewayClient _gateway;

  AiAdvisorApi({KongGatewayClient? gateway})
      : _gateway = gateway ?? kongGateway;

  /// Ask a general agricultural question via copilot chat
  /// طرح سؤال زراعي عام عبر المحادثة الذكية
  Future<AdvisorResponse> ask({
    required String question,
    String? fieldId,
    String language = 'ar',
    String? sessionId,
  }) async {
    final response = await _gateway.post<Map<String, dynamic>>(
      KongServices.copilot,
      '/chat',
      data: {
        'messages': [
          {'role': 'user', 'content': question}
        ],
        'context': {
          if (fieldId != null) 'field_id': fieldId,
          'language': language,
        },
        if (sessionId != null) 'session_id': sessionId,
      },
      fromJson: (data) => data as Map<String, dynamic>,
    );

    if (response.success && response.data != null) {
      return AdvisorResponse.fromJson(response.data!);
    }

    // Fallback to legacy advisor endpoint if copilot is unavailable
    final legacyResponse = await _gateway.post<Map<String, dynamic>>(
      KongServices.aiAdvisor,
      '/ask',
      data: {
        'query': question,
        'field_id': fieldId,
        'language': language,
      },
      fromJson: (data) => data as Map<String, dynamic>,
    );

    if (legacyResponse.success && legacyResponse.data != null) {
      return AdvisorResponse.fromJson(legacyResponse.data!);
    }

    throw const AiAdvisorException(
      code: 'API_ERROR',
      message: 'فشل في الاتصال بالمستشار الذكي',
    );
  }

  /// Search agricultural knowledge base via RAG
  /// البحث في قاعدة المعرفة الزراعية
  Future<List<RagSearchResult>> searchKnowledge({
    required String query,
    int topK = 5,
    String? category,
  }) async {
    final response = await _gateway.get<List<dynamic>>(
      KongServices.copilot,
      '/rag/search',
      queryParams: {
        'query': query,
        'k': topK,
        if (category != null) 'category': category,
      },
      fromJson: (data) => data as List<dynamic>,
    );

    if (response.success && response.data != null) {
      return response.data!
          .map((e) => RagSearchResult.fromJson(e as Map<String, dynamic>))
          .toList();
    }

    return [];
  }

  /// Get crop health diagnosis with image
  /// تشخيص صحة المحصول بالصورة
  Future<DiagnosisResponse> diagnose({
    required String imagePath,
    String? cropType,
    String? fieldId,
  }) async {
    final response = await _gateway.uploadFile<Map<String, dynamic>>(
      KongServices.pestDetection,
      '/detect',
      filePath: imagePath,
      fieldName: 'image',
      extraData: {
        if (cropType != null) 'crop_type': cropType,
        if (fieldId != null) 'field_id': fieldId,
      },
      fromJson: (data) => data as Map<String, dynamic>,
    );

    if (response.success && response.data != null) {
      return DiagnosisResponse.fromJson(response.data!);
    }

    throw const AiAdvisorException(
      code: 'DIAGNOSIS_ERROR',
      message: 'فشل في تحليل التشخيص',
    );
  }

  /// Get personalized recommendations for a field
  /// الحصول على توصيات مخصصة للحقل
  Future<RecommendationsResponse> getRecommendations({
    required String fieldId,
    String? focus, // irrigation, fertilization, pest_control
  }) async {
    // Use copilot tool execution for recommendations
    final response = await _gateway.post<Map<String, dynamic>>(
      KongServices.copilot,
      '/tools/run',
      data: {
        'tool': 'field.recommendations',
        'params': {
          'field_id': fieldId,
          if (focus != null) 'focus': focus,
        },
      },
      fromJson: (data) => data as Map<String, dynamic>,
    );

    if (response.success && response.data != null) {
      return RecommendationsResponse.fromJson(response.data!);
    }

    // Fallback to advisory service
    final fallback = await _gateway.get<Map<String, dynamic>>(
      KongServices.advisory,
      '/recommend',
      queryParams: {
        'field_id': fieldId,
        if (focus != null) 'focus': focus,
      },
      fromJson: (data) => data as Map<String, dynamic>,
    );

    if (fallback.success && fallback.data != null) {
      return RecommendationsResponse.fromJson(fallback.data!);
    }

    throw const AiAdvisorException(
      code: 'RECOMMENDATIONS_ERROR',
      message: 'فشل في تحليل التوصيات',
    );
  }

  /// Analyze a field comprehensively via copilot
  /// تحليل شامل للحقل
  Future<FieldAnalysisResponse> analyzeField({
    required String fieldId,
  }) async {
    final response = await _gateway.post<Map<String, dynamic>>(
      KongServices.copilot,
      '/tools/run',
      data: {
        'tool': 'field.analyze',
        'params': {'field_id': fieldId},
      },
      fromJson: (data) => data as Map<String, dynamic>,
    );

    if (response.success && response.data != null) {
      return FieldAnalysisResponse.fromJson(response.data!);
    }

    throw const AiAdvisorException(
      code: 'ANALYSIS_ERROR',
      message: 'فشل في تحليل الحقل',
    );
  }

  /// Get chat history
  /// الحصول على سجل المحادثة
  Future<List<ChatMessage>> getChatHistory({
    String? sessionId,
    int limit = 50,
  }) async {
    final response = await _gateway.get<List<dynamic>>(
      KongServices.copilot,
      '/chat/history',
      queryParams: {
        'limit': limit,
        if (sessionId != null) 'session_id': sessionId,
      },
      fromJson: (data) => data as List<dynamic>,
    );

    if (response.success && response.data != null) {
      return response.data!
          .map((e) => ChatMessage.fromJson(e as Map<String, dynamic>))
          .toList();
    }

    return [];
  }

  /// Get available copilot tools
  /// الحصول على الأدوات المتاحة
  Future<List<CopilotTool>> getAvailableTools() async {
    final response = await _gateway.get<List<dynamic>>(
      KongServices.copilot,
      '/tools/list',
      fromJson: (data) => data as List<dynamic>,
    );

    if (response.success && response.data != null) {
      return response.data!
          .map((e) => CopilotTool.fromJson(e as Map<String, dynamic>))
          .toList();
    }

    return [];
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Models - نماذج البيانات
// ═══════════════════════════════════════════════════════════════════════════

/// Advisor response model
class AdvisorResponse {
  final String answer;
  final String? answerAr;
  final double confidence;
  final List<String> sources;
  final Map<String, dynamic>? metadata;
  final String? sessionId;

  AdvisorResponse({
    required this.answer,
    this.answerAr,
    required this.confidence,
    required this.sources,
    this.metadata,
    this.sessionId,
  });

  factory AdvisorResponse.fromJson(Map<String, dynamic> json) {
    return AdvisorResponse(
      answer: json['answer'] ?? json['response'] ?? json['content'] ?? '',
      answerAr: json['answer_ar'],
      confidence: (json['confidence'] ?? 0.8).toDouble(),
      sources: (json['sources'] as List?)?.cast<String>() ?? [],
      metadata: json['metadata'],
      sessionId: json['session_id'],
    );
  }
}

/// RAG search result
class RagSearchResult {
  final String content;
  final double score;
  final String? source;
  final String? category;
  final Map<String, dynamic>? metadata;

  RagSearchResult({
    required this.content,
    required this.score,
    this.source,
    this.category,
    this.metadata,
  });

  factory RagSearchResult.fromJson(Map<String, dynamic> json) {
    return RagSearchResult(
      content: json['content'] ?? json['text'] ?? '',
      score: (json['score'] ?? json['similarity'] ?? 0.0).toDouble(),
      source: json['source'],
      category: json['category'],
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
    final recs =
        json['recommendations'] as List? ?? json['result'] as List? ?? [];
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
      dueDate:
          json['due_date'] != null ? DateTime.tryParse(json['due_date']) : null,
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
  final Map<String, dynamic>? metadata;

  ChatMessage({
    required this.id,
    required this.role,
    required this.content,
    required this.timestamp,
    this.metadata,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] ?? '',
      role: json['role'] ?? 'assistant',
      content: json['content'] ?? '',
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
      metadata: json['metadata'],
    );
  }
}

/// Copilot tool definition
class CopilotTool {
  final String name;
  final String description;
  final Map<String, dynamic>? parameters;

  CopilotTool({
    required this.name,
    required this.description,
    this.parameters,
  });

  factory CopilotTool.fromJson(Map<String, dynamic> json) {
    return CopilotTool(
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      parameters: json['parameters'],
    );
  }
}

/// AI Advisor Exception
class AiAdvisorException implements Exception {
  final String code;
  final String message;

  const AiAdvisorException({required this.code, required this.message});

  @override
  String toString() => 'AiAdvisorException($code): $message';
}
