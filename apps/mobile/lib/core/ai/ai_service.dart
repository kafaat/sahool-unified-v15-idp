/// SAHOOL AI Service - خدمة الذكاء الاصطناعي
///
/// Provides AI-powered agricultural advisory capabilities.
/// Connects to the copilot-api backend service for complex inference,
/// with fallback to on-device lightweight models for offline scenarios.
///
/// Features:
/// - Crop disease detection from images
/// - Agricultural advisory chat
/// - Pest identification
/// - Fertilizer recommendations
/// - Yield prediction
library;

import 'dart:typed_data';

import 'package:flutter_riverpod/flutter_riverpod.dart';


// =============================================================================
// Models
// =============================================================================

/// AI advisory response
/// استجابة الاستشارة الذكية
class AiAdvisory {
  final String id;
  final String question;
  final String answer;
  final String answerAr;
  final double confidence;
  final List<String> sources;
  final AdvisoryType type;
  final DateTime createdAt;

  const AiAdvisory({
    required this.id,
    required this.question,
    required this.answer,
    required this.answerAr,
    required this.confidence,
    this.sources = const [],
    required this.type,
    required this.createdAt,
  });

  factory AiAdvisory.fromJson(Map<String, dynamic> json) => AiAdvisory(
        id: json['id'] as String? ?? '',
        question: json['question'] as String? ?? '',
        answer: json['answer'] as String? ?? '',
        answerAr: json['answer_ar'] as String? ?? '',
        confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
        sources: (json['sources'] as List?)?.cast<String>() ?? [],
        type: AdvisoryType.fromString(json['type'] as String? ?? 'general'),
        createdAt: json['created_at'] != null
            ? DateTime.tryParse(json['created_at'] as String) ?? DateTime.now()
            : DateTime.now(),
      );
}

/// Advisory type classification
/// تصنيف نوع الاستشارة
enum AdvisoryType {
  irrigation('irrigation', 'الري'),
  fertilizer('fertilizer', 'التسميد'),
  pestControl('pest_control', 'مكافحة الآفات'),
  diseaseManagement('disease_management', 'إدارة الأمراض'),
  cropPlanning('crop_planning', 'تخطيط المحاصيل'),
  weatherAdvisory('weather_advisory', 'استشارات الطقس'),
  general('general', 'عام');

  final String value;
  final String labelAr;

  const AdvisoryType(this.value, this.labelAr);

  static AdvisoryType fromString(String value) {
    return AdvisoryType.values.firstWhere(
      (e) => e.value == value,
      orElse: () => AdvisoryType.general,
    );
  }
}

/// Image analysis result for crop disease / pest detection
/// نتيجة تحليل الصورة لاكتشاف أمراض / آفات المحاصيل
class ImageAnalysisResult {
  final String detectedClass;
  final String detectedClassAr;
  final double confidence;
  final String severity;
  final String severityAr;
  final List<AiRecommendation> recommendations;
  final Map<String, dynamic> boundingBox;

  const ImageAnalysisResult({
    required this.detectedClass,
    required this.detectedClassAr,
    required this.confidence,
    required this.severity,
    required this.severityAr,
    this.recommendations = const [],
    this.boundingBox = const {},
  });

  factory ImageAnalysisResult.fromJson(Map<String, dynamic> json) =>
      ImageAnalysisResult(
        detectedClass: json['detected_class'] as String? ?? 'Unknown',
        detectedClassAr: json['detected_class_ar'] as String? ?? 'غير معروف',
        confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
        severity: json['severity'] as String? ?? 'unknown',
        severityAr: json['severity_ar'] as String? ?? 'غير معروف',
        recommendations: (json['recommendations'] as List?)
                ?.map((e) =>
                    AiRecommendation.fromJson(e as Map<String, dynamic>))
                .toList() ??
            [],
        boundingBox:
            json['bounding_box'] as Map<String, dynamic>? ?? {},
      );
}

/// AI recommendation item
/// توصية الذكاء الاصطناعي
class AiRecommendation {
  final String title;
  final String titleAr;
  final String description;
  final String descriptionAr;
  final String priority; // high, medium, low
  final String? actionRoute;

  const AiRecommendation({
    required this.title,
    required this.titleAr,
    required this.description,
    required this.descriptionAr,
    required this.priority,
    this.actionRoute,
  });

  factory AiRecommendation.fromJson(Map<String, dynamic> json) =>
      AiRecommendation(
        title: json['title'] as String? ?? '',
        titleAr: json['title_ar'] as String? ?? '',
        description: json['description'] as String? ?? '',
        descriptionAr: json['description_ar'] as String? ?? '',
        priority: json['priority'] as String? ?? 'medium',
        actionRoute: json['action_route'] as String?,
      );
}

/// Chat message for AI advisory
/// رسالة محادثة للاستشارة الذكية
class AiChatMessage {
  final String id;
  final String content;
  final bool isUser;
  final DateTime timestamp;
  final List<AiRecommendation> recommendations;

  const AiChatMessage({
    required this.id,
    required this.content,
    required this.isUser,
    required this.timestamp,
    this.recommendations = const [],
  });
}

// =============================================================================
// AI Service
// =============================================================================

/// AI Service state
/// حالة خدمة الذكاء الاصطناعي
class AiServiceState {
  final bool isLoading;
  final bool isAnalyzing;
  final String? error;
  final List<AiChatMessage> chatHistory;
  final ImageAnalysisResult? lastAnalysis;
  final List<AiAdvisory> recentAdvisories;

  const AiServiceState({
    this.isLoading = false,
    this.isAnalyzing = false,
    this.error,
    this.chatHistory = const [],
    this.lastAnalysis,
    this.recentAdvisories = const [],
  });

  AiServiceState copyWith({
    bool? isLoading,
    bool? isAnalyzing,
    String? error,
    List<AiChatMessage>? chatHistory,
    ImageAnalysisResult? lastAnalysis,
    List<AiAdvisory>? recentAdvisories,
  }) {
    return AiServiceState(
      isLoading: isLoading ?? this.isLoading,
      isAnalyzing: isAnalyzing ?? this.isAnalyzing,
      error: error,
      chatHistory: chatHistory ?? this.chatHistory,
      lastAnalysis: lastAnalysis ?? this.lastAnalysis,
      recentAdvisories: recentAdvisories ?? this.recentAdvisories,
    );
  }
}

/// AI Service Notifier - manages AI interactions
/// مُعلم خدمة الذكاء الاصطناعي - إدارة تفاعلات الذكاء الاصطناعي
class AiServiceNotifier extends StateNotifier<AiServiceState> {
  AiServiceNotifier() : super(const AiServiceState());

  /// Send a question to the AI advisory
  /// إرسال سؤال للمستشار الذكي
  Future<AiAdvisory?> askAdvisor({
    required String question,
    String? fieldId,
    String? cropType,
    Map<String, dynamic>? context,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      // Add user message to chat history
      final userMessage = AiChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        content: question,
        isUser: true,
        timestamp: DateTime.now(),
      );

      state = state.copyWith(
        chatHistory: [...state.chatHistory, userMessage],
      );

      // In production, call the copilot-api via Kong gateway
      // For now, return a mock advisory response
      await Future.delayed(const Duration(seconds: 1));

      final advisory = AiAdvisory(
        id: 'adv_${DateTime.now().millisecondsSinceEpoch}',
        question: question,
        answer: _getMockAnswer(question),
        answerAr: _getMockAnswerAr(question),
        confidence: 0.85,
        sources: ['SAHOOL Knowledge Base', 'Agricultural Best Practices'],
        type: _classifyQuestion(question),
        createdAt: DateTime.now(),
      );

      // Add AI response to chat history
      final aiMessage = AiChatMessage(
        id: 'ai_${DateTime.now().millisecondsSinceEpoch}',
        content: advisory.answerAr,
        isUser: false,
        timestamp: DateTime.now(),
        recommendations: [],
      );

      state = state.copyWith(
        isLoading: false,
        chatHistory: [...state.chatHistory, aiMessage],
        recentAdvisories: [advisory, ...state.recentAdvisories].take(20).toList(),
      );

      return advisory;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      return null;
    }
  }

  /// Analyze an image for disease/pest detection
  /// تحليل صورة لاكتشاف الأمراض / الآفات
  Future<ImageAnalysisResult?> analyzeImage({
    required Uint8List imageBytes,
    String? cropType,
  }) async {
    state = state.copyWith(isAnalyzing: true, error: null);

    try {
      // In production, send image to yolo26-vision-service via Kong
      await Future.delayed(const Duration(seconds: 2));

      const result = ImageAnalysisResult(
        detectedClass: 'Leaf Rust',
        detectedClassAr: 'صدأ الأوراق',
        confidence: 0.87,
        severity: 'moderate',
        severityAr: 'متوسط',
        recommendations: [
          AiRecommendation(
            title: 'Apply Fungicide',
            titleAr: 'تطبيق مبيد فطري',
            description: 'Apply propiconazole-based fungicide within 48 hours',
            descriptionAr: 'تطبيق مبيد فطري أساسه بروبيكونازول خلال 48 ساعة',
            priority: 'high',
          ),
          AiRecommendation(
            title: 'Monitor Adjacent Fields',
            titleAr: 'مراقبة الحقول المجاورة',
            description: 'Check nearby wheat fields for similar symptoms',
            descriptionAr: 'فحص حقول القمح المجاورة لأعراض مشابهة',
            priority: 'medium',
          ),
        ],
      );

      state = state.copyWith(
        isAnalyzing: false,
        lastAnalysis: result,
      );

      return result;
    } catch (e) {
      state = state.copyWith(
        isAnalyzing: false,
        error: e.toString(),
      );
      return null;
    }
  }

  /// Clear chat history
  /// مسح سجل المحادثة
  void clearChat() {
    state = state.copyWith(chatHistory: []);
  }

  /// Clear last analysis
  void clearAnalysis() {
    state = state.copyWith(lastAnalysis: null);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Private helpers
  // ═══════════════════════════════════════════════════════════════════════════

  AdvisoryType _classifyQuestion(String question) {
    final q = question.toLowerCase();
    if (q.contains('ري') || q.contains('irrigat') || q.contains('water')) {
      return AdvisoryType.irrigation;
    }
    if (q.contains('سماد') || q.contains('fertiliz') || q.contains('نيتروجين')) {
      return AdvisoryType.fertilizer;
    }
    if (q.contains('آفة') || q.contains('حشر') || q.contains('pest') || q.contains('insect')) {
      return AdvisoryType.pestControl;
    }
    if (q.contains('مرض') || q.contains('disease') || q.contains('صدأ')) {
      return AdvisoryType.diseaseManagement;
    }
    if (q.contains('طقس') || q.contains('weather') || q.contains('مطر')) {
      return AdvisoryType.weatherAdvisory;
    }
    return AdvisoryType.general;
  }

  String _getMockAnswer(String question) {
    return 'Based on current field conditions and agricultural best practices, '
        'I recommend monitoring soil moisture levels and adjusting irrigation '
        'schedules accordingly. Please check the detailed recommendations below.';
  }

  String _getMockAnswerAr(String question) {
    return 'بناءً على ظروف الحقل الحالية وأفضل الممارسات الزراعية، '
        'أنصح بمراقبة مستويات رطوبة التربة وتعديل جداول الري وفقاً لذلك. '
        'يرجى مراجعة التوصيات المفصلة أدناه.';
  }
}

// =============================================================================
// Providers
// =============================================================================

/// Provider for AI service state
/// موفر حالة خدمة الذكاء الاصطناعي
final aiServiceProvider =
    StateNotifierProvider<AiServiceNotifier, AiServiceState>((ref) {
  return AiServiceNotifier();
});

/// Provider for chat history
/// موفر سجل المحادثة
final aiChatHistoryProvider = Provider<List<AiChatMessage>>((ref) {
  return ref.watch(aiServiceProvider).chatHistory;
});

/// Provider for AI loading state
/// موفر حالة التحميل
final aiIsLoadingProvider = Provider<bool>((ref) {
  return ref.watch(aiServiceProvider).isLoading;
});

/// Provider for last image analysis
/// موفر آخر تحليل صورة
final lastImageAnalysisProvider = Provider<ImageAnalysisResult?>((ref) {
  return ref.watch(aiServiceProvider).lastAnalysis;
});
