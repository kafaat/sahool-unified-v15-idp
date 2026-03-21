/// AI Advisor Repository
/// مستودع المستشار الذكي
///
/// Manages data access for AI advisory features with offline support
library;

import 'dart:async';
import '../remote/ai_advisor_api.dart';
import '../cache/advisory_cache.dart';
import '../../domain/models/advisory.dart';
import '../../domain/models/advisory_request.dart';
import '../../domain/models/advisory_context.dart';
import '../../domain/models/advisory_feedback.dart';

/// AI Advisor Repository
class AiAdvisorRepository {
  final AiAdvisorApi _api;
  final AdvisoryCache _cache;

  /// Stream controller for real-time updates
  final _messageStreamController = StreamController<ChatMessage>.broadcast();

  /// Current context
  AdvisoryContext? _currentContext;

  AiAdvisorRepository({
    required AiAdvisorApi api,
    required AdvisoryCache cache,
  })  : _api = api,
        _cache = cache;

  /// Stream of incoming messages
  Stream<ChatMessage> get messageStream => _messageStreamController.stream;

  /// Current context
  AdvisoryContext? get currentContext => _currentContext;

  // ─────────────────────────────────────────────────────────────────────────────
  // Chat & Questions
  // ─────────────────────────────────────────────────────────────────────────────

  /// Send a message/question to the AI advisor
  /// إرسال رسالة/سؤال إلى المستشار الذكي
  Future<ChatMessage> sendMessage({
    required String content,
    String? fieldId,
    String? cropType,
    String language = 'ar',
  }) async {
    // Create user message
    final userMessage = ChatMessage(
      id: 'msg_${DateTime.now().millisecondsSinceEpoch}',
      role: 'user',
      content: content,
      timestamp: DateTime.now(),
      fieldId: fieldId,
    );

    // Cache user message
    await _cache.addMessage(userMessage);

    try {
      // Send to API
      final response = await _api.ask(
        question: content,
        fieldId: fieldId,
        cropType: cropType,
        language: language,
      );

      // Create assistant message
      final assistantMessage = ChatMessage(
        id: response.id.isNotEmpty ? response.id : 'msg_${DateTime.now().millisecondsSinceEpoch}_response',
        role: 'assistant',
        content: response.answer,
        contentAr: response.answerAr,
        timestamp: DateTime.now(),
        fieldId: fieldId,
        recommendations: response.recommendations,
        metadata: {
          'confidence': response.confidence,
          'sources': response.sources,
        },
      );

      // Cache assistant message
      await _cache.addMessage(assistantMessage);

      // Update context if provided
      if (response.context != null) {
        _currentContext = response.context;
        await _cache.saveContext(_currentContext!);
      }

      // Emit message
      _messageStreamController.add(assistantMessage);

      return assistantMessage;
    } catch (e) {
      // Try to get cached response for similar questions
      final cachedResponse = await _cache.findSimilarQuestion(content);
      if (cachedResponse != null) {
        return cachedResponse;
      }
      rethrow;
    }
  }

  /// Send advisory request
  /// إرسال طلب استشارة
  Future<AdvisoryResponse> sendRequest(AdvisoryRequest request) async {
    try {
      final response = await _api.sendRequest(request);

      // Cache advisories
      for (final advisory in response.advisories) {
        await _cache.saveAdvisory(advisory);
      }

      // Update context
      if (response.context != null) {
        _currentContext = response.context;
        await _cache.saveContext(_currentContext!);
      }

      return response;
    } catch (e) {
      // Return cached data if available
      final cachedAdvisories = await _cache.getAdvisories(
        fieldId: request.fieldId,
        type: request.focusArea,
      );

      if (cachedAdvisories.isNotEmpty) {
        return AdvisoryResponse(
          id: 'cached_${DateTime.now().millisecondsSinceEpoch}',
          response: 'استجابة محفوظة (غير متصل)',
          confidence: 0.7,
          advisories: cachedAdvisories,
        );
      }
      rethrow;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Diagnosis
  // ─────────────────────────────────────────────────────────────────────────────

  /// Diagnose crop disease from image
  /// تشخيص مرض المحصول من الصورة
  Future<DiagnosisResponse> diagnose({
    required String imagePath,
    String? cropType,
    String? fieldId,
    String? symptoms,
    String language = 'ar',
  }) async {
    final response = await _api.diagnose(
      imagePath: imagePath,
      cropType: cropType,
      fieldId: fieldId,
      symptoms: symptoms,
      language: language,
    );

    // Cache diagnosis advisory if provided
    if (response.advisory != null) {
      await _cache.saveAdvisory(response.advisory!);
    }

    return response;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Recommendations
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get recommendations for a field
  /// الحصول على توصيات للحقل
  Future<List<Advisory>> getRecommendations({
    required String fieldId,
    AdvisoryType? focus,
    bool forceRefresh = false,
    String language = 'ar',
  }) async {
    // Return cached if not forcing refresh
    if (!forceRefresh) {
      final cached = await _cache.getAdvisories(fieldId: fieldId, type: focus);
      if (cached.isNotEmpty) {
        return cached;
      }
    }

    try {
      final response = await _api.getRecommendations(
        fieldId: fieldId,
        focus: focus,
        language: language,
      );

      // Cache recommendations
      for (final advisory in response.recommendations) {
        await _cache.saveAdvisory(advisory);
      }

      // Update context
      if (response.context != null) {
        _currentContext = response.context;
        await _cache.saveContext(_currentContext!);
      }

      return response.recommendations;
    } catch (e) {
      // Return cached on error
      return _cache.getAdvisories(fieldId: fieldId, type: focus);
    }
  }

  /// Get irrigation recommendation
  /// الحصول على توصية الري
  Future<Advisory> getIrrigationRecommendation({
    required String fieldId,
    String language = 'ar',
  }) async {
    final advisory = await _api.getIrrigationRecommendation(
      fieldId: fieldId,
      language: language,
    );

    await _cache.saveAdvisory(advisory);
    return advisory;
  }

  /// Get fertilizer recommendation
  /// الحصول على توصية التسميد
  Future<Advisory> getFertilizerRecommendation({
    required String fieldId,
    String language = 'ar',
  }) async {
    final advisory = await _api.getFertilizerRecommendation(
      fieldId: fieldId,
      language: language,
    );

    await _cache.saveAdvisory(advisory);
    return advisory;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Field Analysis
  // ─────────────────────────────────────────────────────────────────────────────

  /// Analyze field comprehensively
  /// تحليل شامل للحقل
  Future<FieldAnalysisResponse> analyzeField({
    required String fieldId,
    String language = 'ar',
  }) async {
    final response = await _api.analyzeField(
      fieldId: fieldId,
      language: language,
    );

    // Cache recommendations
    for (final advisory in response.recommendations) {
      await _cache.saveAdvisory(advisory);
    }

    // Update context
    if (response.context != null) {
      _currentContext = response.context;
      await _cache.saveContext(_currentContext!);
    }

    return response;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Context
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get advisory context
  /// الحصول على سياق التوصية
  Future<AdvisoryContext> getContext({
    String? fieldId,
    bool forceRefresh = false,
  }) async {
    // Return cached context if available
    if (!forceRefresh && _currentContext != null) {
      return _currentContext!;
    }

    // Try to load from cache
    if (!forceRefresh) {
      final cachedContext = await _cache.getContext(fieldId);
      if (cachedContext != null) {
        _currentContext = cachedContext;
        return cachedContext;
      }
    }

    try {
      final context = await _api.getContext(fieldId: fieldId);
      _currentContext = context;
      await _cache.saveContext(context);
      return context;
    } catch (e) {
      // Return cached on error
      final cachedContext = await _cache.getContext(fieldId);
      if (cachedContext != null) {
        return cachedContext;
      }
      rethrow;
    }
  }

  /// Update current field context
  /// تحديث سياق الحقل الحالي
  Future<void> updateFieldContext(String fieldId) async {
    _currentContext = await getContext(fieldId: fieldId, forceRefresh: true);
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
    bool forceRefresh = false,
  }) async {
    // Return cached if not forcing refresh
    if (!forceRefresh) {
      final cached = await _cache.getMessages(limit: limit, offset: offset);
      if (cached.isNotEmpty) {
        return cached;
      }
    }

    try {
      final messages = await _api.getChatHistory(
        limit: limit,
        offset: offset,
        fieldId: fieldId,
      );

      // Cache messages
      for (final message in messages) {
        await _cache.addMessage(message);
      }

      return messages;
    } catch (e) {
      // Return cached on error
      return _cache.getMessages(limit: limit, offset: offset);
    }
  }

  /// Get advisory history
  /// الحصول على سجل التوصيات
  Future<List<Advisory>> getAdvisoryHistory({
    int limit = 20,
    int offset = 0,
    String? fieldId,
    AdvisoryType? type,
    AdvisoryStatus? status,
    bool forceRefresh = false,
  }) async {
    // Return cached if not forcing refresh
    if (!forceRefresh) {
      final cached = await _cache.getAdvisories(
        fieldId: fieldId,
        type: type,
        status: status,
        limit: limit,
      );
      if (cached.isNotEmpty) {
        return cached;
      }
    }

    try {
      final advisories = await _api.getAdvisoryHistory(
        limit: limit,
        offset: offset,
        fieldId: fieldId,
        type: type,
        status: status,
      );

      // Cache advisories
      for (final advisory in advisories) {
        await _cache.saveAdvisory(advisory);
      }

      return advisories;
    } catch (e) {
      // Return cached on error
      return _cache.getAdvisories(
        fieldId: fieldId,
        type: type,
        status: status,
        limit: limit,
      );
    }
  }

  /// Get single advisory by ID
  /// الحصول على توصية واحدة
  Future<Advisory> getAdvisory(String advisoryId) async {
    // Check cache first
    final cached = await _cache.getAdvisory(advisoryId);
    if (cached != null) {
      return cached;
    }

    final advisory = await _api.getAdvisory(advisoryId);
    await _cache.saveAdvisory(advisory);
    return advisory;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Feedback
  // ─────────────────────────────────────────────────────────────────────────────

  /// Submit feedback for an advisory
  /// إرسال ردود الفعل على التوصية
  Future<void> submitFeedback(AdvisoryFeedback feedback) async {
    // Save to cache immediately
    await _cache.saveFeedback(feedback);

    try {
      // Try to send to API
      await _api.submitFeedback(feedback);

      // Mark as synced
      await _cache.markFeedbackSynced(feedback.id);
    } catch (e) {
      // Queue for later sync if offline
      await _cache.queueFeedbackForSync(feedback);
    }
  }

  /// Update advisory status
  /// تحديث حالة التوصية
  Future<void> updateAdvisoryStatus({
    required String advisoryId,
    required AdvisoryStatus status,
  }) async {
    // Update in cache
    await _cache.updateAdvisoryStatus(advisoryId, status);

    try {
      // Try to sync with API
      await _api.updateAdvisoryStatus(
        advisoryId: advisoryId,
        status: status,
      );
    } catch (e) {
      // Queue for later sync if offline
      await _cache.queueStatusUpdateForSync(advisoryId, status);
    }
  }

  /// Mark advisory as applied
  /// تعيين التوصية كمطبقة
  Future<void> markAdvisoryApplied(String advisoryId) async {
    await updateAdvisoryStatus(
      advisoryId: advisoryId,
      status: AdvisoryStatus.applied,
    );
  }

  /// Dismiss advisory
  /// تجاهل التوصية
  Future<void> dismissAdvisory(String advisoryId) async {
    await updateAdvisoryStatus(
      advisoryId: advisoryId,
      status: AdvisoryStatus.dismissed,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Cache Management
  // ─────────────────────────────────────────────────────────────────────────────

  /// Clear chat history
  /// مسح سجل المحادثة
  Future<void> clearChatHistory() async {
    await _cache.clearMessages();

    try {
      await _api.clearChatHistory();
    } catch (e) {
      // Ignore API errors for clear
    }
  }

  /// Clear all cached data
  /// مسح جميع البيانات المحفوظة
  Future<void> clearAllCache() async {
    await _cache.clearAll();
    _currentContext = null;
  }

  /// Sync pending feedback
  /// مزامنة ردود الفعل المعلقة
  Future<void> syncPendingFeedback() async {
    final pending = await _cache.getPendingFeedback();

    for (final feedback in pending) {
      try {
        await _api.submitFeedback(feedback);
        await _cache.markFeedbackSynced(feedback.id);
      } catch (e) {
        // Keep in queue for next sync
      }
    }
  }

  /// Sync pending status updates
  /// مزامنة تحديثات الحالة المعلقة
  Future<void> syncPendingStatusUpdates() async {
    final pending = await _cache.getPendingStatusUpdates();

    for (final entry in pending.entries) {
      try {
        await _api.updateAdvisoryStatus(
          advisoryId: entry.key,
          status: entry.value,
        );
        await _cache.markStatusUpdateSynced(entry.key);
      } catch (e) {
        // Keep in queue for next sync
      }
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Cleanup
  // ─────────────────────────────────────────────────────────────────────────────

  /// Dispose resources
  void dispose() {
    _messageStreamController.close();
  }
}
