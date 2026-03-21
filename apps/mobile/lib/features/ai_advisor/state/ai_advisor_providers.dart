/// AI Advisor State Management Providers
/// مزودات حالة المستشار الذكي
///
/// Riverpod providers for AI advisor feature state management
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/remote/ai_advisor_api.dart';
import '../data/repositories/ai_advisor_repository.dart';
import '../data/cache/advisory_cache.dart';
import '../domain/models/advisory.dart';
import '../domain/models/advisory_request.dart';
import '../domain/models/advisory_context.dart';
import '../domain/models/advisory_feedback.dart';
import '../../../core/http/api_client.dart';
import 'chat_controller.dart';

// ============================================================================
// Core Providers
// ============================================================================

/// API client provider
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

/// AI Advisor API provider
final aiAdvisorApiProvider = Provider<AiAdvisorApi>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return AiAdvisorApi(apiClient);
});

/// Advisory cache provider
final advisoryCacheProvider = Provider<AdvisoryCache>((ref) {
  return AdvisoryCache();
});

/// AI Advisor repository provider
final aiAdvisorRepositoryProvider = Provider<AiAdvisorRepository>((ref) {
  final api = ref.watch(aiAdvisorApiProvider);
  final cache = ref.watch(advisoryCacheProvider);
  return AiAdvisorRepository(api: api, cache: cache);
});

// ============================================================================
// Chat State Providers
// ============================================================================

/// Chat messages state
final chatMessagesProvider = StateNotifierProvider.autoDispose<ChatMessagesNotifier, AsyncValue<List<ChatMessage>>>((ref) {
  final repository = ref.watch(aiAdvisorRepositoryProvider);
  return ChatMessagesNotifier(repository);
});

/// Chat messages notifier
class ChatMessagesNotifier extends StateNotifier<AsyncValue<List<ChatMessage>>> {
  final AiAdvisorRepository _repository;

  ChatMessagesNotifier(this._repository) : super(const AsyncValue.data([]));

  /// Load chat history
  Future<void> loadHistory({String? fieldId}) async {
    state = const AsyncValue.loading();
    try {
      final messages = await _repository.getChatHistory(fieldId: fieldId);
      state = AsyncValue.data(messages);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  /// Send a message
  Future<void> sendMessage(AdvisoryRequest request) async {
    // Add user message to state
    final userMessage = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: request.query,
      contentAr: request.query,
      role: 'user',
      timestamp: DateTime.now(),
    );

    state.whenData((messages) {
      state = AsyncValue.data([...messages, userMessage]);
    });

    try {
      final response = await _repository.sendMessage(content: request.query, fieldId: request.fieldId, cropType: request.cropType, language: request.language);

      // Add AI response to state
      state.whenData((messages) {
        state = AsyncValue.data([...messages, response]);
      });
    } catch (e) {
      // Add error message
      final errorMessage = ChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        content: 'Sorry, there was an error processing your request.',
        contentAr: 'عذراً، حدث خطأ في معالجة طلبك.',
        role: 'assistant',
        timestamp: DateTime.now(),
        metadata: {'error': true},
      );

      state.whenData((messages) {
        state = AsyncValue.data([...messages, errorMessage]);
      });
    }
  }

  /// Diagnose with image
  Future<void> diagnoseImage(String imagePath, {String? fieldId, String? description}) async {
    // Add user message with image
    final userMessage = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: description ?? 'Please analyze this image',
      contentAr: description ?? 'الرجاء تحليل هذه الصورة',
      role: 'user',
      timestamp: DateTime.now(),
      metadata: {'image_path': imagePath},
    );

    state.whenData((messages) {
      state = AsyncValue.data([...messages, userMessage]);
    });

    try {
      final diagnosisResult = await _repository.diagnose(
        imagePath: imagePath,
        fieldId: fieldId,
        symptoms: description,
      );

      // Convert diagnosis to chat message
      final response = ChatMessage(
        id: diagnosisResult.id,
        role: 'assistant',
        content: diagnosisResult.disease,
        contentAr: diagnosisResult.diseaseAr,
        timestamp: DateTime.now(),
        fieldId: fieldId,
      );

      // Add AI response to state
      state.whenData((messages) {
        state = AsyncValue.data([...messages, response]);
      });
    } catch (e) {
      final errorMessage = ChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        content: 'Sorry, there was an error analyzing the image.',
        contentAr: 'عذراً، حدث خطأ في تحليل الصورة.',
        role: 'assistant',
        timestamp: DateTime.now(),
        metadata: {'error': true},
      );

      state.whenData((messages) {
        state = AsyncValue.data([...messages, errorMessage]);
      });
    }
  }

  /// Clear chat history
  void clearHistory() {
    state = const AsyncValue.data([]);
  }
}

// ============================================================================
// Advisory State Providers
// ============================================================================

/// All advisories state
final advisoriesProvider = StateNotifierProvider.autoDispose<AdvisoriesNotifier, AsyncValue<List<Advisory>>>((ref) {
  final repository = ref.watch(aiAdvisorRepositoryProvider);
  return AdvisoriesNotifier(repository);
});

/// Advisories notifier
class AdvisoriesNotifier extends StateNotifier<AsyncValue<List<Advisory>>> {
  final AiAdvisorRepository _repository;

  AdvisoriesNotifier(this._repository) : super(const AsyncValue.data([]));

  /// Load advisories
  Future<void> loadAdvisories({String? fieldId, AdvisoryType? type, AdvisoryStatus? status}) async {
    state = const AsyncValue.loading();
    try {
      final advisories = await _repository.getRecommendations(
        fieldId: fieldId ?? '',
        focus: type,
      );

      // Filter by status if provided
      final filtered = status != null
          ? advisories.where((a) => a.status == status).toList()
          : advisories;

      state = AsyncValue.data(filtered);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  /// Update advisory status
  void updateAdvisoryStatus(String advisoryId, AdvisoryStatus newStatus) {
    state.whenData((advisories) {
      final updated = advisories.map((a) {
        if (a.id == advisoryId) {
          return a.copyWith(status: newStatus);
        }
        return a;
      }).toList();
      state = AsyncValue.data(updated);
    });
  }

  /// Add advisory
  void addAdvisory(Advisory advisory) {
    state.whenData((advisories) {
      state = AsyncValue.data([advisory, ...advisories]);
    });
  }
}

/// Filtered advisories by type
final filteredAdvisoriesProvider = Provider.autoDispose.family<AsyncValue<List<Advisory>>, AdvisoryType?>((ref, type) {
  final advisories = ref.watch(advisoriesProvider);

  return advisories.whenData((list) {
    if (type == null) return list;
    return list.where((a) => a.type == type).toList();
  });
});

/// Pending advisories
final pendingAdvisoriesProvider = Provider.autoDispose<AsyncValue<List<Advisory>>>((ref) {
  final advisories = ref.watch(advisoriesProvider);

  return advisories.whenData((list) {
    return list.where((a) => a.status == AdvisoryStatus.pending).toList();
  });
});

/// Applied advisories
final appliedAdvisoriesProvider = Provider.autoDispose<AsyncValue<List<Advisory>>>((ref) {
  final advisories = ref.watch(advisoriesProvider);

  return advisories.whenData((list) {
    return list.where((a) => a.status == AdvisoryStatus.applied).toList();
  });
});

// ============================================================================
// Context State Providers
// ============================================================================

/// Advisory context state
final advisoryContextProvider = StateNotifierProvider.autoDispose<AdvisoryContextNotifier, AsyncValue<AdvisoryContext?>>((ref) {
  final repository = ref.watch(aiAdvisorRepositoryProvider);
  return AdvisoryContextNotifier(repository);
});

/// Advisory context notifier
class AdvisoryContextNotifier extends StateNotifier<AsyncValue<AdvisoryContext?>> {
  final AiAdvisorRepository _repository;

  AdvisoryContextNotifier(this._repository) : super(const AsyncValue.data(null));

  /// Load context for field
  Future<void> loadContext(String fieldId) async {
    state = const AsyncValue.loading();
    try {
      final context = await _repository.getContext(fieldId: fieldId);
      state = AsyncValue.data(context);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  /// Clear context
  void clearContext() {
    state = const AsyncValue.data(null);
  }
}

// ============================================================================
// Feedback State Providers
// ============================================================================

/// Feedback submission state
final feedbackSubmissionProvider = StateNotifierProvider.autoDispose<FeedbackSubmissionNotifier, AsyncValue<void>>((ref) {
  final repository = ref.watch(aiAdvisorRepositoryProvider);
  return FeedbackSubmissionNotifier(repository);
});

/// Feedback submission notifier
class FeedbackSubmissionNotifier extends StateNotifier<AsyncValue<void>> {
  final AiAdvisorRepository _repository;

  FeedbackSubmissionNotifier(this._repository) : super(const AsyncValue.data(null));

  /// Submit feedback
  Future<bool> submitFeedback(AdvisoryFeedback feedback) async {
    state = const AsyncValue.loading();
    try {
      await _repository.submitFeedback(feedback);
      state = const AsyncValue.data(null);
      return true;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return false;
    }
  }
}

// ============================================================================
// UI State Providers
// ============================================================================

/// Is typing state (for typing indicator)
final isTypingProvider = StateProvider.autoDispose<bool>((ref) => false);

/// Selected field ID for context
final selectedFieldIdProvider = StateProvider.autoDispose<String?>((ref) => null);

/// Selected advisory type filter
final selectedAdvisoryTypeProvider = StateProvider.autoDispose<AdvisoryType?>((ref) => null);

/// Selected advisory status filter
final selectedAdvisoryStatusProvider = StateProvider.autoDispose<AdvisoryStatus?>((ref) => null);

/// Chat input text
final chatInputProvider = StateProvider.autoDispose<String>((ref) => '');

/// Show context panel
final showContextPanelProvider = StateProvider.autoDispose<bool>((ref) => false);

// ============================================================================
// Computed Providers
// ============================================================================

/// Has pending advisories
final hasPendingAdvisoriesProvider = Provider.autoDispose<bool>((ref) {
  final pending = ref.watch(pendingAdvisoriesProvider);
  return pending.whenOrNull(data: (list) => list.isNotEmpty) ?? false;
});

/// Pending advisories count
final pendingAdvisoriesCountProvider = Provider.autoDispose<int>((ref) {
  final pending = ref.watch(pendingAdvisoriesProvider);
  return pending.whenOrNull(data: (list) => list.length) ?? 0;
});

/// Context completeness percentage
final contextCompletenessProvider = Provider.autoDispose<double>((ref) {
  final context = ref.watch(advisoryContextProvider);
  return context.whenOrNull(data: (ctx) => ctx?.completeness ?? 0.0) ?? 0.0;
});

/// Quick questions for selected field
final quickQuestionsProvider = Provider.autoDispose<List<QuickQuestion>>((ref) {
  final context = ref.watch(advisoryContextProvider);

  return context.whenOrNull(data: (ctx) {
    if (ctx == null) return QuickQuestion.predefined;

    // Filter quick questions based on available context
    final filtered = <QuickQuestion>[];

    if (ctx.hasFieldData) {
      filtered.addAll(QuickQuestion.predefined.where(
        (q) => q.focusArea == AdvisoryType.general ||
               q.focusArea == AdvisoryType.irrigation ||
               q.focusArea == AdvisoryType.harvest
      ));
    }

    if (ctx.hasCropData) {
      filtered.addAll(QuickQuestion.predefined.where(
        (q) => q.focusArea == AdvisoryType.fertilization ||
               q.focusArea == AdvisoryType.pestControl ||
               q.focusArea == AdvisoryType.diseaseControl
      ));
    }

    if (ctx.hasWeatherData) {
      filtered.addAll(QuickQuestion.predefined.where(
        (q) => q.focusArea == AdvisoryType.weather
      ));
    }

    // Remove duplicates
    final uniqueQuestions = <String, QuickQuestion>{};
    for (final q in filtered) {
      uniqueQuestions[q.id] = q;
    }

    return uniqueQuestions.values.toList();
  }) ?? QuickQuestion.predefined;
});

// ============================================================================
// Advisory Details Provider
// ============================================================================

/// Selected advisory for details view
final selectedAdvisoryProvider = StateProvider.autoDispose<Advisory?>((ref) => null);

/// Advisory details provider (loads full details)
final advisoryDetailsProvider = FutureProvider.autoDispose.family<Advisory?, String>((ref, advisoryId) async {
  final advisories = ref.watch(advisoriesProvider);

  return advisories.whenOrNull(
    data: (list) => list.firstWhere(
      (a) => a.id == advisoryId,
      orElse: () => throw Exception('Advisory not found'),
    ),
  );
});

// ============================================================================
// Compatibility Aliases
// ============================================================================

/// Type alias for AiAdvisorState (uses ChatSessionState)
typedef AiAdvisorState = ChatSessionState;

/// Alias for the main AI advisor provider (wraps chatControllerProvider)
final aiAdvisorProvider = chatControllerProvider;

/// Advisory history provider
final advisoryHistoryProvider = StateNotifierProvider.autoDispose<AdvisoryHistoryNotifier, AsyncValue<List<Advisory>>>((ref) {
  final repository = ref.watch(aiAdvisorRepositoryProvider);
  return AdvisoryHistoryNotifier(repository);
});

/// Advisory history notifier
class AdvisoryHistoryNotifier extends StateNotifier<AsyncValue<List<Advisory>>> {
  final AiAdvisorRepository _repository;

  AdvisoryHistoryNotifier(this._repository) : super(const AsyncValue.data([]));

  /// Load advisory history
  Future<void> loadHistory({String? fieldId, AdvisoryType? type, AdvisoryStatus? status}) async {
    state = const AsyncValue.loading();
    try {
      final advisories = await _repository.getAdvisoryHistory(
        fieldId: fieldId,
        type: type,
        status: status,
      );
      state = AsyncValue.data(advisories);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  /// Refresh advisory history
  Future<void> refresh({String? fieldId}) async {
    try {
      final advisories = await _repository.getAdvisoryHistory(
        fieldId: fieldId,
        forceRefresh: true,
      );
      state = AsyncValue.data(advisories);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  /// Filter by type
  void filterByType(AdvisoryType? type) {
    state.whenData((advisories) {
      if (type == null) return;
      final filtered = advisories.where((a) => a.type == type).toList();
      state = AsyncValue.data(filtered);
    });
  }

  /// Filter by status
  void filterByStatus(AdvisoryStatus? status) {
    state.whenData((advisories) {
      if (status == null) return;
      final filtered = advisories.where((a) => a.status == status).toList();
      state = AsyncValue.data(filtered);
    });
  }
}
