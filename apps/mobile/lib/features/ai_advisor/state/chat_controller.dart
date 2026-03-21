/// AI Chat Controller
/// متحكم محادثة المستشار الذكي
///
/// Manages chat session state and business logic for AI advisor

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/remote/ai_advisor_api.dart';
import '../data/repositories/ai_advisor_repository.dart';
import '../domain/models/advisory.dart';
import '../domain/models/advisory_request.dart';
import '../domain/models/advisory_context.dart';
import '../domain/models/advisory_feedback.dart';
import 'ai_advisor_providers.dart';

/// Chat session state
class ChatSessionState {
  final String? fieldId;
  final String? fieldName;
  final AdvisoryContext? context;
  final List<ChatMessage> messages;
  final bool isLoading;
  final bool isTyping;
  final String? error;
  final String inputText;
  final String? pendingImagePath;

  const ChatSessionState({
    this.fieldId,
    this.fieldName,
    this.context,
    this.messages = const [],
    this.isLoading = false,
    this.isTyping = false,
    this.error,
    this.inputText = '',
    this.pendingImagePath,
  });

  ChatSessionState copyWith({
    String? fieldId,
    String? fieldName,
    AdvisoryContext? context,
    List<ChatMessage>? messages,
    bool? isLoading,
    bool? isTyping,
    String? error,
    String? inputText,
    String? pendingImagePath,
  }) {
    return ChatSessionState(
      fieldId: fieldId ?? this.fieldId,
      fieldName: fieldName ?? this.fieldName,
      context: context ?? this.context,
      messages: messages ?? this.messages,
      isLoading: isLoading ?? this.isLoading,
      isTyping: isTyping ?? this.isTyping,
      error: error,
      inputText: inputText ?? this.inputText,
      pendingImagePath: pendingImagePath,
    );
  }

  /// Check if can send message
  bool get canSendMessage =>
      inputText.trim().isNotEmpty && !isLoading && !isTyping;

  /// Check if can send image
  bool get canSendImage =>
      pendingImagePath != null && !isLoading && !isTyping;

  /// Get last user message
  ChatMessage? get lastUserMessage {
    for (int i = messages.length - 1; i >= 0; i--) {
      if (messages[i].isUser) return messages[i];
    }
    return null;
  }

  /// Get last assistant message
  ChatMessage? get lastAssistantMessage {
    for (int i = messages.length - 1; i >= 0; i--) {
      if (!messages[i].isUser) return messages[i];
    }
    return null;
  }

  /// Get message count
  int get messageCount => messages.length;

  /// Check if session is empty
  bool get isEmpty => messages.isEmpty;

  /// Check if session has context
  bool get hasContext => context != null && context!.availableContextTypes.isNotEmpty;
}

/// Chat controller provider
final chatControllerProvider = StateNotifierProvider<ChatController, ChatSessionState>((ref) {
  final repository = ref.watch(aiAdvisorRepositoryProvider);
  return ChatController(repository, ref);
});

/// Chat Controller - manages chat session state and actions
class ChatController extends StateNotifier<ChatSessionState> {
  final AiAdvisorRepository _repository;
  final Ref _ref;

  /// Maximum number of messages to keep in memory to prevent unbounded growth.
  static const int _maxMessages = 500;

  ChatController(this._repository, this._ref) : super(const ChatSessionState());

  /// Trim messages list if it exceeds [_maxMessages], keeping the most recent.
  List<ChatMessage> _trimMessages(List<ChatMessage> messages) {
    if (messages.length > _maxMessages) {
      return messages.sublist(messages.length - _maxMessages);
    }
    return messages;
  }

  // ============================================================================
  // Session Management
  // ============================================================================

  /// Initialize chat session
  Future<void> initSession({String? fieldId, String? fieldName}) async {
    state = state.copyWith(
      fieldId: fieldId,
      fieldName: fieldName,
      isLoading: true,
      error: null,
    );

    try {
      // Load chat history
      final messages = await _repository.getChatHistory(fieldId: fieldId);

      // Load context if field selected
      AdvisoryContext? context;
      if (fieldId != null) {
        context = await _repository.getContext(fieldId: fieldId);
      }

      state = state.copyWith(
        messages: messages,
        context: context,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Change field context
  Future<void> changeField(String? fieldId, String? fieldName) async {
    state = state.copyWith(
      fieldId: fieldId,
      fieldName: fieldName,
      isLoading: true,
    );

    try {
      AdvisoryContext? context;
      if (fieldId != null) {
        context = await _repository.getContext(fieldId: fieldId);
      }

      state = state.copyWith(
        context: context,
        isLoading: false,
      );

      // Add system message about context change
      if (fieldName != null) {
        _addSystemMessage('تم تحديد الحقل: $fieldName');
      } else {
        _addSystemMessage('تم إلغاء تحديد الحقل');
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Clear session
  void clearSession() {
    state = const ChatSessionState();
  }

  // ============================================================================
  // Message Handling
  // ============================================================================

  /// Update input text
  void updateInputText(String text) {
    state = state.copyWith(inputText: text);
  }

  /// Send text message
  Future<void> sendMessage() async {
    final text = state.inputText.trim();
    if (text.isEmpty || state.isTyping) return;

    // Create request
    final request = AdvisoryRequest.question(
      query: text,
      fieldId: state.fieldId,
    );

    await _sendRequest(request, text);
  }

  /// Send quick question
  Future<void> sendQuickQuestion(QuickQuestion question) async {
    final locale = WidgetsBinding.instance.platformDispatcher.locale.languageCode;

    final request = AdvisoryRequest(
      query: question.getText(locale),
      type: question.type,
      focusArea: question.focusArea,
      fieldId: state.fieldId,
    );

    await _sendRequest(request, question.getText(locale));
  }

  /// Send image for diagnosis
  Future<void> sendDiagnosisImage(String imagePath, {String? description}) async {
    if (state.isTyping) return;

    // Add user message with image
    final userMessage = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: description ?? 'Please analyze this image for crop health',
      contentAr: description ?? 'الرجاء تحليل هذه الصورة لصحة المحصول',
      role: 'user',
      timestamp: DateTime.now(),
      metadata: {'image_path': imagePath},
    );

    state = state.copyWith(
      messages: _trimMessages([...state.messages, userMessage]),
      inputText: '',
      pendingImagePath: null,
      isTyping: true,
    );

    try {
      final diagnosisResult = await _repository.diagnose(
        imagePath: imagePath,
        fieldId: state.fieldId,
        symptoms: description,
      );

      final response = ChatMessage(
        id: diagnosisResult.id,
        role: 'assistant',
        content: diagnosisResult.disease,
        contentAr: diagnosisResult.diseaseAr,
        timestamp: DateTime.now(),
        fieldId: state.fieldId,
      );

      state = state.copyWith(
        messages: _trimMessages([...state.messages, response]),
        isTyping: false,
      );
    } catch (e) {
      _addErrorMessage('عذراً، حدث خطأ في تحليل الصورة: ${e.toString()}');
      state = state.copyWith(isTyping: false);
    }
  }

  /// Set pending image for diagnosis
  void setPendingImage(String? imagePath) {
    state = state.copyWith(pendingImagePath: imagePath);
  }

  /// Internal method to send request
  Future<void> _sendRequest(AdvisoryRequest request, String displayText) async {
    // Add user message
    final userMessage = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: displayText,
      contentAr: displayText,
      role: 'user',
      timestamp: DateTime.now(),
    );

    state = state.copyWith(
      messages: _trimMessages([...state.messages, userMessage]),
      inputText: '',
      isTyping: true,
    );

    try {
      final response = await _repository.sendMessage(content: request.query, fieldId: request.fieldId, cropType: request.cropType, language: request.language);

      state = state.copyWith(
        messages: _trimMessages([...state.messages, response]),
        isTyping: false,
      );

      // If response contains advisories, notify advisories provider
      if (response.recommendations != null && response.recommendations!.isNotEmpty) {
        for (final advisory in response.recommendations!) {
          _ref.read(advisoriesProvider.notifier).addAdvisory(advisory);
        }
      }
    } catch (e) {
      _addErrorMessage('عذراً، حدث خطأ في معالجة طلبك: ${e.toString()}');
      state = state.copyWith(isTyping: false);
    }
  }

  /// Add system message
  void _addSystemMessage(String message) {
    final systemMessage = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: message,
      contentAr: message,
      role: 'system',
      timestamp: DateTime.now(),
    );

    state = state.copyWith(
      messages: _trimMessages([...state.messages, systemMessage]),
    );
  }

  /// Add error message
  void _addErrorMessage(String message) {
    final errorMessage = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: message,
      contentAr: message,
      role: 'assistant',
      timestamp: DateTime.now(),
      metadata: {'error': true},
    );

    state = state.copyWith(
      messages: _trimMessages([...state.messages, errorMessage]),
    );
  }

  // ============================================================================
  // Feedback Handling
  // ============================================================================

  /// Submit message feedback
  Future<void> submitMessageFeedback(String messageId, bool isPositive) async {
    try {
      final feedback = AdvisoryFeedback.thumbs(
        advisoryId: messageId,
        userId: '', // Will be filled by repository
        thumbsUp: isPositive,
      );

      await _repository.submitFeedback(feedback);

      // Update message metadata to show feedback submitted
      final updatedMessages = state.messages.map((msg) {
        if (msg.id == messageId) {
          return ChatMessage(
            id: msg.id,
            content: msg.content,
            contentAr: msg.contentAr,
            role: msg.role,
            timestamp: msg.timestamp,
            recommendations: msg.recommendations,
            metadata: {
              ...?msg.metadata,
              'feedback_submitted': true,
              'feedback_positive': isPositive,
            },
          );
        }
        return msg;
      }).toList();

      state = state.copyWith(messages: updatedMessages);
    } catch (e) {
      debugPrint('Error submitting feedback: $e');
    }
  }

  /// Submit advisory feedback
  Future<void> submitAdvisoryFeedback(AdvisoryFeedback feedback) async {
    try {
      await _repository.submitFeedback(feedback);
    } catch (e) {
      debugPrint('Error submitting advisory feedback: $e');
    }
  }

  // ============================================================================
  // Advisory Actions
  // ============================================================================

  /// Mark advisory as applied
  void markAdvisoryApplied(String advisoryId) {
    _ref.read(advisoriesProvider.notifier).updateAdvisoryStatus(
      advisoryId,
      AdvisoryStatus.applied,
    );
  }

  /// Mark advisory as dismissed
  void markAdvisoryDismissed(String advisoryId) {
    _ref.read(advisoriesProvider.notifier).updateAdvisoryStatus(
      advisoryId,
      AdvisoryStatus.dismissed,
    );
  }

  /// Mark advisory as deferred
  void markAdvisoryDeferred(String advisoryId) {
    _ref.read(advisoriesProvider.notifier).updateAdvisoryStatus(
      advisoryId,
      AdvisoryStatus.pending,
    );
  }

  // ============================================================================
  // Context Actions
  // ============================================================================

  /// Refresh context
  Future<void> refreshContext() async {
    if (state.fieldId == null) return;

    state = state.copyWith(isLoading: true);

    try {
      final context = await _repository.getContext(fieldId: state.fieldId!);
      state = state.copyWith(
        context: context,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Get context summary for display
  String getContextSummary(String locale) {
    if (state.context == null) {
      return locale == 'ar'
          ? 'لا يوجد سياق محدد'
          : 'No context selected';
    }

    final types = state.context!.availableContextTypes;
    if (types.isEmpty) {
      return locale == 'ar'
          ? 'لا توجد بيانات متاحة'
          : 'No data available';
    }

    final typeNames = types.map((t) {
      switch (t) {
        case ContextType.field:
          return locale == 'ar' ? 'الحقل' : 'Field';
        case ContextType.weather:
          return locale == 'ar' ? 'الطقس' : 'Weather';
        case ContextType.crop:
          return locale == 'ar' ? 'المحصول' : 'Crop';
        case ContextType.soil:
          return locale == 'ar' ? 'التربة' : 'Soil';
        case ContextType.history:
          return locale == 'ar' ? 'السجل' : 'History';
      }
    }).join('، ');

    return typeNames;
  }
}

// ============================================================================
// Helper Providers
// ============================================================================

/// Chat session initialized provider
final chatSessionInitializedProvider = Provider<bool>((ref) {
  final state = ref.watch(chatControllerProvider);
  return !state.isLoading && state.error == null;
});

/// Chat session has messages provider
final chatHasMessagesProvider = Provider<bool>((ref) {
  final state = ref.watch(chatControllerProvider);
  return state.messages.isNotEmpty;
});

/// Chat is typing provider (derived from controller)
final chatIsTypingProvider = Provider<bool>((ref) {
  final state = ref.watch(chatControllerProvider);
  return state.isTyping;
});

/// Current chat context provider
final currentChatContextProvider = Provider<AdvisoryContext?>((ref) {
  final state = ref.watch(chatControllerProvider);
  return state.context;
});

/// Chat error provider
final chatErrorProvider = Provider<String?>((ref) {
  final state = ref.watch(chatControllerProvider);
  return state.error;
});

/// Chat can send provider
final chatCanSendProvider = Provider<bool>((ref) {
  final state = ref.watch(chatControllerProvider);
  return state.canSendMessage;
});

// ============================================================================
// Analysis Request Helpers
// ============================================================================

/// Request types for specialized analysis
enum AnalysisType {
  fieldHealth,
  irrigationPlan,
  fertilizerPlan,
  pestAssessment,
  yieldForecast,
  weatherImpact,
}

extension AnalysisTypeExtension on AnalysisType {
  String get titleEn {
    switch (this) {
      case AnalysisType.fieldHealth:
        return 'Field Health Analysis';
      case AnalysisType.irrigationPlan:
        return 'Irrigation Planning';
      case AnalysisType.fertilizerPlan:
        return 'Fertilizer Planning';
      case AnalysisType.pestAssessment:
        return 'Pest Assessment';
      case AnalysisType.yieldForecast:
        return 'Yield Forecast';
      case AnalysisType.weatherImpact:
        return 'Weather Impact Analysis';
    }
  }

  String get titleAr {
    switch (this) {
      case AnalysisType.fieldHealth:
        return 'تحليل صحة الحقل';
      case AnalysisType.irrigationPlan:
        return 'تخطيط الري';
      case AnalysisType.fertilizerPlan:
        return 'تخطيط التسميد';
      case AnalysisType.pestAssessment:
        return 'تقييم الآفات';
      case AnalysisType.yieldForecast:
        return 'توقع المحصول';
      case AnalysisType.weatherImpact:
        return 'تحليل تأثير الطقس';
    }
  }

  AdvisoryType get focusArea {
    switch (this) {
      case AnalysisType.fieldHealth:
        return AdvisoryType.general;
      case AnalysisType.irrigationPlan:
        return AdvisoryType.irrigation;
      case AnalysisType.fertilizerPlan:
        return AdvisoryType.fertilization;
      case AnalysisType.pestAssessment:
        return AdvisoryType.pestControl;
      case AnalysisType.yieldForecast:
        return AdvisoryType.harvest;
      case AnalysisType.weatherImpact:
        return AdvisoryType.weather;
    }
  }
}
