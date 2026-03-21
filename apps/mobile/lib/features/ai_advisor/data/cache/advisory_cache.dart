/// Advisory Cache
/// ذاكرة التخزين المؤقت للتوصيات
///
/// Provides offline-first caching for AI advisory data
library;

import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../../domain/models/advisory.dart';
import '../../domain/models/advisory_context.dart';
import '../../domain/models/advisory_feedback.dart';
import '../remote/ai_advisor_api.dart';

/// Advisory Cache Manager
class AdvisoryCache {
  static const String _messagesKey = 'ai_advisor_messages';
  static const String _advisoriesKey = 'ai_advisor_advisories';
  static const String _contextKey = 'ai_advisor_context';
  static const String _feedbackKey = 'ai_advisor_feedback';
  static const String _pendingFeedbackKey = 'ai_advisor_pending_feedback';
  static const String _pendingStatusKey = 'ai_advisor_pending_status';
  static const String _questionCacheKey = 'ai_advisor_question_cache';

  /// Maximum cached messages
  static const int _maxMessages = 100;

  /// Maximum cached advisories
  static const int _maxAdvisories = 50;

  /// Cache expiry duration
  static const Duration _cacheExpiry = Duration(days: 7);

  SharedPreferences? _prefs;

  /// Initialize cache
  Future<void> initialize() async {
    _prefs ??= await SharedPreferences.getInstance();
  }

  /// Ensure preferences are initialized
  Future<SharedPreferences> _getPrefs() async {
    _prefs ??= await SharedPreferences.getInstance();
    return _prefs!;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Messages
  // ─────────────────────────────────────────────────────────────────────────────

  /// Add a message to cache
  Future<void> addMessage(ChatMessage message) async {
    final prefs = await _getPrefs();
    final messages = await getMessages();

    // Add new message at the beginning
    messages.insert(0, message);

    // Limit cache size
    if (messages.length > _maxMessages) {
      messages.removeRange(_maxMessages, messages.length);
    }

    // Save to cache
    final jsonList = messages.map((m) => m.toJson()).toList();
    await prefs.setString(_messagesKey, jsonEncode(jsonList));
  }

  /// Get cached messages
  Future<List<ChatMessage>> getMessages({
    int limit = 50,
    int offset = 0,
  }) async {
    final prefs = await _getPrefs();
    final jsonString = prefs.getString(_messagesKey);

    if (jsonString == null) return [];

    try {
      final jsonList = jsonDecode(jsonString) as List;
      final allMessages = jsonList
          .cast<Map<String, dynamic>>()
          .map((json) => ChatMessage.fromJson(json))
          .toList();

      // Apply pagination
      final end = offset + limit;
      if (offset >= allMessages.length) return [];

      return allMessages.sublist(
        offset,
        end > allMessages.length ? allMessages.length : end,
      );
    } catch (e) {
      return [];
    }
  }

  /// Clear all messages
  Future<void> clearMessages() async {
    final prefs = await _getPrefs();
    await prefs.remove(_messagesKey);
  }

  /// Find similar question in cache
  Future<ChatMessage?> findSimilarQuestion(String query) async {
    final prefs = await _getPrefs();
    final jsonString = prefs.getString(_questionCacheKey);

    if (jsonString == null) return null;

    try {
      final cache = jsonDecode(jsonString) as Map<String, dynamic>;
      final normalizedQuery = _normalizeQuery(query);

      // Check for exact or similar match
      for (final entry in cache.entries) {
        if (_isSimilarQuery(entry.key, normalizedQuery)) {
          return ChatMessage.fromJson(entry.value as Map<String, dynamic>);
        }
      }
    } catch (e) {
      // Cache corrupted
    }

    return null;
  }

  /// Cache a question-answer pair
  Future<void> cacheQuestionAnswer(String query, ChatMessage response) async {
    final prefs = await _getPrefs();
    final jsonString = prefs.getString(_questionCacheKey);

    Map<String, dynamic> cache;
    try {
      cache = jsonString != null
          ? jsonDecode(jsonString) as Map<String, dynamic>
          : {};
    } catch (e) {
      cache = {};
    }

    final normalizedQuery = _normalizeQuery(query);
    cache[normalizedQuery] = response.toJson();

    // Limit cache size
    if (cache.length > 100) {
      final keys = cache.keys.toList();
      for (int i = 0; i < 20; i++) {
        cache.remove(keys[i]);
      }
    }

    await prefs.setString(_questionCacheKey, jsonEncode(cache));
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Advisories
  // ─────────────────────────────────────────────────────────────────────────────

  /// Save advisory to cache
  Future<void> saveAdvisory(Advisory advisory) async {
    final prefs = await _getPrefs();
    final advisories = await _getAllAdvisoriesRaw();

    // Update or add advisory
    advisories[advisory.id] = _CachedAdvisory(
      advisory: advisory,
      cachedAt: DateTime.now(),
    );

    // Limit cache size
    if (advisories.length > _maxAdvisories) {
      _pruneOldAdvisories(advisories);
    }

    await _saveAdvisoriesRaw(prefs, advisories);
  }

  /// Get advisory by ID
  Future<Advisory?> getAdvisory(String advisoryId) async {
    final advisories = await _getAllAdvisoriesRaw();
    final cached = advisories[advisoryId];

    if (cached == null) return null;

    // Check expiry
    if (DateTime.now().difference(cached.cachedAt) > _cacheExpiry) {
      return null;
    }

    return cached.advisory;
  }

  /// Get advisories with filters
  Future<List<Advisory>> getAdvisories({
    String? fieldId,
    AdvisoryType? type,
    AdvisoryStatus? status,
    int limit = 20,
  }) async {
    final advisories = await _getAllAdvisoriesRaw();

    var filtered = advisories.values
        .where((cached) {
          // Check expiry
          if (DateTime.now().difference(cached.cachedAt) > _cacheExpiry) {
            return false;
          }

          final advisory = cached.advisory;

          if (fieldId != null && advisory.fieldId != fieldId) return false;
          if (type != null && advisory.type != type) return false;
          if (status != null && advisory.status != status) return false;

          return true;
        })
        .map((cached) => cached.advisory)
        .toList();

    // Sort by creation date (newest first)
    filtered.sort((a, b) => b.createdAt.compareTo(a.createdAt));

    // Apply limit
    if (filtered.length > limit) {
      filtered = filtered.sublist(0, limit);
    }

    return filtered;
  }

  /// Update advisory status in cache
  Future<void> updateAdvisoryStatus(String advisoryId, AdvisoryStatus status) async {
    final prefs = await _getPrefs();
    final advisories = await _getAllAdvisoriesRaw();

    final cached = advisories[advisoryId];
    if (cached != null) {
      advisories[advisoryId] = _CachedAdvisory(
        advisory: cached.advisory.copyWith(
          status: status,
          appliedAt: status == AdvisoryStatus.applied ? DateTime.now() : null,
        ),
        cachedAt: DateTime.now(),
      );
      await _saveAdvisoriesRaw(prefs, advisories);
    }
  }

  /// Clear all advisories
  Future<void> clearAdvisories() async {
    final prefs = await _getPrefs();
    await prefs.remove(_advisoriesKey);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Context
  // ─────────────────────────────────────────────────────────────────────────────

  /// Save context to cache
  Future<void> saveContext(AdvisoryContext context) async {
    final prefs = await _getPrefs();
    final jsonString = jsonEncode({
      'context': context.toJson(),
      'cachedAt': DateTime.now().toIso8601String(),
    });
    await prefs.setString(_contextKey, jsonString);
  }

  /// Get cached context
  Future<AdvisoryContext?> getContext(String? fieldId) async {
    final prefs = await _getPrefs();
    final jsonString = prefs.getString(_contextKey);

    if (jsonString == null) return null;

    try {
      final data = jsonDecode(jsonString) as Map<String, dynamic>;
      final cachedAt = DateTime.parse(data['cachedAt'] as String);

      // Check expiry (context expires faster)
      if (DateTime.now().difference(cachedAt) > const Duration(hours: 6)) {
        return null;
      }

      return AdvisoryContext.fromJson(data['context'] as Map<String, dynamic>);
    } catch (e) {
      return null;
    }
  }

  /// Clear context
  Future<void> clearContext() async {
    final prefs = await _getPrefs();
    await prefs.remove(_contextKey);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Feedback
  // ─────────────────────────────────────────────────────────────────────────────

  /// Save feedback to cache
  Future<void> saveFeedback(AdvisoryFeedback feedback) async {
    final prefs = await _getPrefs();
    final feedbackList = await _getAllFeedbackRaw();

    feedbackList[feedback.id] = _CachedFeedback(
      feedback: feedback,
      cachedAt: DateTime.now(),
      synced: false,
    );

    await _saveFeedbackRaw(prefs, feedbackList);
  }

  /// Mark feedback as synced
  Future<void> markFeedbackSynced(String feedbackId) async {
    final prefs = await _getPrefs();
    final feedbackList = await _getAllFeedbackRaw();

    final cached = feedbackList[feedbackId];
    if (cached != null) {
      feedbackList[feedbackId] = _CachedFeedback(
        feedback: cached.feedback,
        cachedAt: cached.cachedAt,
        synced: true,
      );
      await _saveFeedbackRaw(prefs, feedbackList);
    }
  }

  /// Queue feedback for sync
  Future<void> queueFeedbackForSync(AdvisoryFeedback feedback) async {
    final prefs = await _getPrefs();
    final jsonString = prefs.getString(_pendingFeedbackKey);

    List<Map<String, dynamic>> pending;
    try {
      pending = jsonString != null
          ? (jsonDecode(jsonString) as List).cast<Map<String, dynamic>>()
          : [];
    } catch (e) {
      pending = [];
    }

    pending.add(feedback.toJson());
    await prefs.setString(_pendingFeedbackKey, jsonEncode(pending));
  }

  /// Get pending feedback for sync
  Future<List<AdvisoryFeedback>> getPendingFeedback() async {
    final prefs = await _getPrefs();
    final jsonString = prefs.getString(_pendingFeedbackKey);

    if (jsonString == null) return [];

    try {
      final pending = (jsonDecode(jsonString) as List).cast<Map<String, dynamic>>();
      return pending.map((json) => AdvisoryFeedback.fromJson(json)).toList();
    } catch (e) {
      return [];
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Status Updates
  // ─────────────────────────────────────────────────────────────────────────────

  /// Queue status update for sync
  Future<void> queueStatusUpdateForSync(String advisoryId, AdvisoryStatus status) async {
    final prefs = await _getPrefs();
    final jsonString = prefs.getString(_pendingStatusKey);

    Map<String, String> pending;
    try {
      pending = jsonString != null
          ? (jsonDecode(jsonString) as Map<String, dynamic>).cast<String, String>()
          : {};
    } catch (e) {
      pending = {};
    }

    pending[advisoryId] = status.name;
    await prefs.setString(_pendingStatusKey, jsonEncode(pending));
  }

  /// Get pending status updates
  Future<Map<String, AdvisoryStatus>> getPendingStatusUpdates() async {
    final prefs = await _getPrefs();
    final jsonString = prefs.getString(_pendingStatusKey);

    if (jsonString == null) return {};

    try {
      final pending = (jsonDecode(jsonString) as Map<String, dynamic>).cast<String, String>();
      return pending.map((key, value) => MapEntry(key, _parseStatus(value)));
    } catch (e) {
      return {};
    }
  }

  /// Mark status update as synced
  Future<void> markStatusUpdateSynced(String advisoryId) async {
    final prefs = await _getPrefs();
    final jsonString = prefs.getString(_pendingStatusKey);

    if (jsonString == null) return;

    try {
      final pending = (jsonDecode(jsonString) as Map<String, dynamic>).cast<String, String>();
      pending.remove(advisoryId);
      await prefs.setString(_pendingStatusKey, jsonEncode(pending));
    } catch (e) {
      // Ignore
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Cache Management
  // ─────────────────────────────────────────────────────────────────────────────

  /// Clear all cached data
  Future<void> clearAll() async {
    final prefs = await _getPrefs();
    await prefs.remove(_messagesKey);
    await prefs.remove(_advisoriesKey);
    await prefs.remove(_contextKey);
    await prefs.remove(_feedbackKey);
    await prefs.remove(_questionCacheKey);
  }

  /// Get cache statistics
  Future<CacheStats> getStats() async {
    final prefs = await _getPrefs();

    final messages = await getMessages();
    final advisories = await _getAllAdvisoriesRaw();
    final feedback = await _getAllFeedbackRaw();
    final pendingFeedback = await getPendingFeedback();
    final pendingStatus = await getPendingStatusUpdates();

    return CacheStats(
      messageCount: messages.length,
      advisoryCount: advisories.length,
      feedbackCount: feedback.length,
      pendingFeedbackCount: pendingFeedback.length,
      pendingStatusCount: pendingStatus.length,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Private Helpers
  // ─────────────────────────────────────────────────────────────────────────────

  Future<Map<String, _CachedAdvisory>> _getAllAdvisoriesRaw() async {
    final prefs = await _getPrefs();
    final jsonString = prefs.getString(_advisoriesKey);

    if (jsonString == null) return {};

    try {
      final data = jsonDecode(jsonString) as Map<String, dynamic>;
      return data.map((key, value) => MapEntry(
        key,
        _CachedAdvisory.fromJson(value as Map<String, dynamic>),
      ));
    } catch (e) {
      return {};
    }
  }

  Future<void> _saveAdvisoriesRaw(
    SharedPreferences prefs,
    Map<String, _CachedAdvisory> advisories,
  ) async {
    final data = advisories.map((key, value) => MapEntry(key, value.toJson()));
    await prefs.setString(_advisoriesKey, jsonEncode(data));
  }

  Future<Map<String, _CachedFeedback>> _getAllFeedbackRaw() async {
    final prefs = await _getPrefs();
    final jsonString = prefs.getString(_feedbackKey);

    if (jsonString == null) return {};

    try {
      final data = jsonDecode(jsonString) as Map<String, dynamic>;
      return data.map((key, value) => MapEntry(
        key,
        _CachedFeedback.fromJson(value as Map<String, dynamic>),
      ));
    } catch (e) {
      return {};
    }
  }

  Future<void> _saveFeedbackRaw(
    SharedPreferences prefs,
    Map<String, _CachedFeedback> feedback,
  ) async {
    final data = feedback.map((key, value) => MapEntry(key, value.toJson()));
    await prefs.setString(_feedbackKey, jsonEncode(data));
  }

  void _pruneOldAdvisories(Map<String, _CachedAdvisory> advisories) {
    final entries = advisories.entries.toList()
      ..sort((a, b) => a.value.cachedAt.compareTo(b.value.cachedAt));

    // Remove oldest 20%
    final toRemove = (advisories.length * 0.2).ceil();
    for (int i = 0; i < toRemove; i++) {
      advisories.remove(entries[i].key);
    }
  }

  String _normalizeQuery(String query) {
    return query
        .toLowerCase()
        .trim()
        .replaceAll(RegExp(r'\s+'), ' ')
        .replaceAll(RegExp(r'[^\w\s\u0600-\u06FF]'), '');
  }

  bool _isSimilarQuery(String cached, String query) {
    // Simple similarity check
    if (cached == query) return true;

    // Check if one contains the other
    if (cached.contains(query) || query.contains(cached)) {
      return true;
    }

    // Calculate word overlap
    final cachedWords = cached.split(' ').toSet();
    final queryWords = query.split(' ').toSet();
    final overlap = cachedWords.intersection(queryWords).length;
    final total = cachedWords.union(queryWords).length;

    return total > 0 && (overlap / total) > 0.7;
  }

  AdvisoryStatus _parseStatus(String status) {
    switch (status.toLowerCase()) {
      case 'applied':
        return AdvisoryStatus.applied;
      case 'dismissed':
        return AdvisoryStatus.dismissed;
      case 'expired':
        return AdvisoryStatus.expired;
      default:
        return AdvisoryStatus.pending;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Helper Classes
// ═══════════════════════════════════════════════════════════════════════════════

/// Cached advisory with metadata
class _CachedAdvisory {
  final Advisory advisory;
  final DateTime cachedAt;

  _CachedAdvisory({
    required this.advisory,
    required this.cachedAt,
  });

  factory _CachedAdvisory.fromJson(Map<String, dynamic> json) {
    return _CachedAdvisory(
      advisory: Advisory.fromJson(json['advisory'] as Map<String, dynamic>),
      cachedAt: DateTime.parse(json['cachedAt'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
    'advisory': advisory.toJson(),
    'cachedAt': cachedAt.toIso8601String(),
  };
}

/// Cached feedback with metadata
class _CachedFeedback {
  final AdvisoryFeedback feedback;
  final DateTime cachedAt;
  final bool synced;

  _CachedFeedback({
    required this.feedback,
    required this.cachedAt,
    required this.synced,
  });

  factory _CachedFeedback.fromJson(Map<String, dynamic> json) {
    return _CachedFeedback(
      feedback: AdvisoryFeedback.fromJson(json['feedback'] as Map<String, dynamic>),
      cachedAt: DateTime.parse(json['cachedAt'] as String),
      synced: json['synced'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
    'feedback': feedback.toJson(),
    'cachedAt': cachedAt.toIso8601String(),
    'synced': synced,
  };
}

/// Cache statistics
class CacheStats {
  final int messageCount;
  final int advisoryCount;
  final int feedbackCount;
  final int pendingFeedbackCount;
  final int pendingStatusCount;

  CacheStats({
    required this.messageCount,
    required this.advisoryCount,
    required this.feedbackCount,
    required this.pendingFeedbackCount,
    required this.pendingStatusCount,
  });

  int get totalItems => messageCount + advisoryCount + feedbackCount;
  int get pendingCount => pendingFeedbackCount + pendingStatusCount;
  bool get hasPendingItems => pendingCount > 0;
}
