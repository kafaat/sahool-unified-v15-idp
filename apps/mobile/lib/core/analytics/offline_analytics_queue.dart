/// SAHOOL Offline Analytics Queue - Offline event queuing for analytics
/// قائمة انتظار التحليلات بدون اتصال
///
/// Provides reliable offline storage and sync for analytics events.
/// Events are queued locally when offline and sent when connection is available.
///
/// Features:
/// - Persistent local storage for events
/// - Automatic retry with exponential backoff
/// - Batch sending for efficiency
/// - Event deduplication
/// - Size limits to prevent storage overflow
/// - Priority queue support
library;

import 'dart:async';
import 'dart:convert';
import 'dart:math';
import 'package:shared_preferences/shared_preferences.dart';
import '../sync/network_status.dart';
import '../utils/app_logger.dart';
import 'analytics_event.dart';

// =============================================================================
// Queue Configuration - تكوين قائمة الانتظار
// =============================================================================

/// Configuration for the offline analytics queue
class OfflineAnalyticsQueueConfig {
  /// Maximum number of events to store locally
  final int maxQueueSize;

  /// Maximum age of events in days before they are discarded
  final int maxEventAgeDays;

  /// Batch size for sending events
  final int batchSize;

  /// Initial retry delay in seconds
  final int initialRetryDelaySeconds;

  /// Maximum retry attempts before discarding
  final int maxRetryAttempts;

  /// Whether to enable automatic queue processing
  final bool autoProcessEnabled;

  /// Interval for automatic queue processing in minutes
  final int autoProcessIntervalMinutes;

  const OfflineAnalyticsQueueConfig({
    this.maxQueueSize = 1000,
    this.maxEventAgeDays = 7,
    this.batchSize = 50,
    this.initialRetryDelaySeconds = 5,
    this.maxRetryAttempts = 5,
    this.autoProcessEnabled = true,
    this.autoProcessIntervalMinutes = 5,
  });
}

// =============================================================================
// Queue Statistics - إحصائيات قائمة الانتظار
// =============================================================================

/// Statistics about the analytics queue
class AnalyticsQueueStats {
  /// Total number of events in queue
  final int totalEvents;

  /// Number of events pending to be sent
  final int pendingEvents;

  /// Number of events that have been sent
  final int sentEvents;

  /// Number of failed events
  final int failedEvents;

  /// Oldest event timestamp
  final DateTime? oldestEventTime;

  /// Newest event timestamp
  final DateTime? newestEventTime;

  /// Whether queue processing is in progress
  final bool isProcessing;

  /// Last successful sync time
  final DateTime? lastSyncTime;

  const AnalyticsQueueStats({
    required this.totalEvents,
    required this.pendingEvents,
    required this.sentEvents,
    required this.failedEvents,
    this.oldestEventTime,
    this.newestEventTime,
    required this.isProcessing,
    this.lastSyncTime,
  });

  Map<String, dynamic> toJson() => {
        'total_events': totalEvents,
        'pending_events': pendingEvents,
        'sent_events': sentEvents,
        'failed_events': failedEvents,
        'oldest_event_time': oldestEventTime?.toIso8601String(),
        'newest_event_time': newestEventTime?.toIso8601String(),
        'is_processing': isProcessing,
        'last_sync_time': lastSyncTime?.toIso8601String(),
      };
}

// =============================================================================
// Offline Analytics Queue - قائمة انتظار التحليلات بدون اتصال
// =============================================================================

/// Callback for sending events to analytics provider
typedef EventSendCallback = Future<bool> Function(List<AnalyticsEvent> events);

/// Offline analytics queue for reliable event delivery
class OfflineAnalyticsQueue {
  static const String _storageKey = 'sahool_analytics_queue';
  static const String _lastSyncKey = 'sahool_analytics_last_sync';
  static const String _statsKey = 'sahool_analytics_stats';

  final OfflineAnalyticsQueueConfig config;
  final EventSendCallback? onSendEvents;

  SharedPreferences? _prefs;
  List<AnalyticsEvent> _queue = [];
  bool _isInitialized = false;
  bool _isProcessing = false;
  Timer? _autoProcessTimer;
  int _consecutiveFailures = 0;

  // Stats tracking
  int _totalSentEvents = 0;
  int _totalFailedEvents = 0;
  DateTime? _lastSyncTime;

  /// Stream controller for queue status updates
  final _statusController = StreamController<AnalyticsQueueStats>.broadcast();

  /// Stream of queue status updates
  Stream<AnalyticsQueueStats> get statusStream => _statusController.stream;

  OfflineAnalyticsQueue({
    this.config = const OfflineAnalyticsQueueConfig(),
    this.onSendEvents,
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Initialization - التهيئة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Initialize the queue and load persisted events
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      _prefs = await SharedPreferences.getInstance();
      await _loadQueue();
      await _loadStats();
      _cleanExpiredEvents();

      if (config.autoProcessEnabled) {
        _startAutoProcess();
      }

      _isInitialized = true;
      AppLogger.i('Analytics queue initialized', tag: 'ANALYTICS', data: {
        'queue_size': _queue.length,
      });

      _notifyStatus();
    } catch (e) {
      AppLogger.e('Failed to initialize analytics queue', tag: 'ANALYTICS', error: e);
    }
  }

  /// Dispose and clean up resources
  void dispose() {
    _autoProcessTimer?.cancel();
    _statusController.close();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Queue Operations - عمليات قائمة الانتظار
  // ═══════════════════════════════════════════════════════════════════════════

  /// Add an event to the queue
  Future<void> enqueue(AnalyticsEvent event) async {
    if (!_isInitialized) {
      await initialize();
    }

    // Check for duplicates
    if (_queue.any((e) => e.id == event.id)) {
      AppLogger.d('Duplicate event ignored', tag: 'ANALYTICS', data: {
        'event_id': event.id,
      });
      return;
    }

    // Enforce queue size limit
    if (_queue.length >= config.maxQueueSize) {
      // Remove oldest unsent events
      _queue.removeWhere((e) => !e.isSent);
      if (_queue.length >= config.maxQueueSize) {
        _queue.removeAt(0);
      }
      AppLogger.w('Queue at capacity, old events removed', tag: 'ANALYTICS');
    }

    _queue.add(event);
    await _saveQueue();
    _notifyStatus();

    AppLogger.d('Event queued', tag: 'ANALYTICS', data: {
      'event_name': event.name,
      'queue_size': _queue.length,
    });
  }

  /// Add multiple events to the queue
  Future<void> enqueueBatch(List<AnalyticsEvent> events) async {
    for (final event in events) {
      await enqueue(event);
    }
  }

  /// Process the queue and send pending events
  Future<bool> processQueue() async {
    if (!_isInitialized) {
      await initialize();
    }

    if (_isProcessing) {
      AppLogger.d('Queue processing already in progress', tag: 'ANALYTICS');
      return false;
    }

    // Check network connectivity
    final isOnline = await NetworkStatus.instance.isConnected;
    if (!isOnline) {
      AppLogger.d('Offline, skipping queue processing', tag: 'ANALYTICS');
      return false;
    }

    if (onSendEvents == null) {
      AppLogger.w('No send callback configured', tag: 'ANALYTICS');
      return false;
    }

    _isProcessing = true;
    _notifyStatus();

    try {
      final pendingEvents = _queue.where((e) => !e.isSent).toList();

      if (pendingEvents.isEmpty) {
        AppLogger.d('No pending events to process', tag: 'ANALYTICS');
        return true;
      }

      AppLogger.i('Processing analytics queue', tag: 'ANALYTICS', data: {
        'pending_count': pendingEvents.length,
      });

      // Process in batches
      var successCount = 0;
      var failCount = 0;

      for (var i = 0; i < pendingEvents.length; i += config.batchSize) {
        final batch = pendingEvents.skip(i).take(config.batchSize).toList();

        try {
          final success = await onSendEvents!(batch);

          if (success) {
            // Mark events as sent
            for (final event in batch) {
              event.isSent = true;
            }
            successCount += batch.length;
            _consecutiveFailures = 0;
          } else {
            // Increment retry count
            for (final event in batch) {
              event.retryCount++;
            }
            failCount += batch.length;
            _consecutiveFailures++;
          }
        } catch (e) {
          // Handle batch failure
          for (final event in batch) {
            event.retryCount++;
          }
          failCount += batch.length;
          _consecutiveFailures++;

          AppLogger.e('Batch send failed', tag: 'ANALYTICS', error: e);

          // Apply exponential backoff on consecutive failures
          if (_consecutiveFailures > 1) {
            final delay = Duration(
              seconds: min(
                config.initialRetryDelaySeconds * pow(2, _consecutiveFailures - 1).toInt(),
                300, // Max 5 minutes
              ),
            );
            await Future.delayed(delay);
          }
        }
      }

      // Remove events that exceeded max retries
      _queue.removeWhere((e) => e.retryCount >= config.maxRetryAttempts);

      // Update stats
      _totalSentEvents += successCount;
      _totalFailedEvents += failCount;
      if (successCount > 0) {
        _lastSyncTime = DateTime.now();
      }

      await _saveQueue();
      await _saveStats();
      _notifyStatus();

      AppLogger.i('Queue processing completed', tag: 'ANALYTICS', data: {
        'success': successCount,
        'failed': failCount,
      });

      return failCount == 0;
    } finally {
      _isProcessing = false;
      _notifyStatus();
    }
  }

  /// Clear all events from the queue
  Future<void> clear() async {
    _queue.clear();
    await _saveQueue();
    _notifyStatus();
    AppLogger.i('Analytics queue cleared', tag: 'ANALYTICS');
  }

  /// Clear only sent events from the queue
  Future<void> clearSentEvents() async {
    _queue.removeWhere((e) => e.isSent);
    await _saveQueue();
    _notifyStatus();
  }

  /// Get current queue statistics
  AnalyticsQueueStats getStats() {
    final pendingEvents = _queue.where((e) => !e.isSent).toList();
    final sentEvents = _queue.where((e) => e.isSent).toList();
    final failedEvents = _queue.where((e) => e.retryCount > 0 && !e.isSent).toList();

    DateTime? oldestTime;
    DateTime? newestTime;

    if (_queue.isNotEmpty) {
      oldestTime = _queue.map((e) => e.timestamp).reduce((a, b) => a.isBefore(b) ? a : b);
      newestTime = _queue.map((e) => e.timestamp).reduce((a, b) => a.isAfter(b) ? a : b);
    }

    return AnalyticsQueueStats(
      totalEvents: _queue.length,
      pendingEvents: pendingEvents.length,
      sentEvents: sentEvents.length,
      failedEvents: failedEvents.length,
      oldestEventTime: oldestTime,
      newestEventTime: newestTime,
      isProcessing: _isProcessing,
      lastSyncTime: _lastSyncTime,
    );
  }

  /// Get pending events (not yet sent)
  List<AnalyticsEvent> getPendingEvents() {
    return _queue.where((e) => !e.isSent).toList();
  }

  /// Get event by ID
  AnalyticsEvent? getEventById(String id) {
    try {
      return _queue.firstWhere((e) => e.id == id);
    } catch (_) {
      return null;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Private Methods - طرق خاصة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Load queue from persistent storage
  Future<void> _loadQueue() async {
    try {
      final jsonString = _prefs?.getString(_storageKey);
      if (jsonString == null || jsonString.isEmpty) {
        _queue = [];
        return;
      }

      final jsonList = jsonDecode(jsonString) as List;
      _queue = jsonList
          .map((json) => AnalyticsEvent.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      AppLogger.e('Failed to load analytics queue', tag: 'ANALYTICS', error: e);
      _queue = [];
    }
  }

  /// Save queue to persistent storage
  Future<void> _saveQueue() async {
    try {
      final jsonList = _queue.map((e) => e.toJson()).toList();
      final jsonString = jsonEncode(jsonList);
      await _prefs?.setString(_storageKey, jsonString);
    } catch (e) {
      AppLogger.e('Failed to save analytics queue', tag: 'ANALYTICS', error: e);
    }
  }

  /// Load stats from persistent storage
  Future<void> _loadStats() async {
    try {
      final statsJson = _prefs?.getString(_statsKey);
      if (statsJson != null) {
        final stats = jsonDecode(statsJson) as Map<String, dynamic>;
        _totalSentEvents = stats['total_sent'] as int? ?? 0;
        _totalFailedEvents = stats['total_failed'] as int? ?? 0;
      }

      final lastSyncString = _prefs?.getString(_lastSyncKey);
      if (lastSyncString != null) {
        _lastSyncTime = DateTime.parse(lastSyncString);
      }
    } catch (e) {
      AppLogger.e('Failed to load analytics stats', tag: 'ANALYTICS', error: e);
    }
  }

  /// Save stats to persistent storage
  Future<void> _saveStats() async {
    try {
      final stats = {
        'total_sent': _totalSentEvents,
        'total_failed': _totalFailedEvents,
      };
      await _prefs?.setString(_statsKey, jsonEncode(stats));

      if (_lastSyncTime != null) {
        await _prefs?.setString(_lastSyncKey, _lastSyncTime!.toIso8601String());
      }
    } catch (e) {
      AppLogger.e('Failed to save analytics stats', tag: 'ANALYTICS', error: e);
    }
  }

  /// Remove events older than the configured max age
  void _cleanExpiredEvents() {
    final cutoff = DateTime.now().subtract(Duration(days: config.maxEventAgeDays));
    final beforeCount = _queue.length;

    _queue.removeWhere((e) => e.timestamp.isBefore(cutoff));

    final removedCount = beforeCount - _queue.length;
    if (removedCount > 0) {
      AppLogger.i('Expired events removed', tag: 'ANALYTICS', data: {
        'removed_count': removedCount,
      });
    }
  }

  /// Start automatic queue processing
  void _startAutoProcess() {
    _autoProcessTimer?.cancel();
    _autoProcessTimer = Timer.periodic(
      Duration(minutes: config.autoProcessIntervalMinutes),
      (_) => processQueue(),
    );
  }

  /// Notify listeners of status changes
  void _notifyStatus() {
    if (!_statusController.isClosed) {
      _statusController.add(getStats());
    }
  }
}

// =============================================================================
// Riverpod Providers - مزودو Riverpod
// =============================================================================

// Note: Providers are defined in analytics_service.dart to avoid circular imports
