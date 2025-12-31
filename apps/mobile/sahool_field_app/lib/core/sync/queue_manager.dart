import 'dart:async';
import '../storage/database.dart';
import 'sync_metrics_service.dart';

/// Queue Priority Levels
enum QueuePriority {
  /// Critical operations (e.g., delete, important updates)
  critical(0),

  /// High priority (e.g., task completion)
  high(1),

  /// Normal priority (e.g., field updates)
  normal(2),

  /// Low priority (e.g., analytics, metadata)
  low(3);

  const QueuePriority(this.value);
  final int value;
}

/// Queue Item Status
enum QueueItemStatus {
  pending,
  processing,
  completed,
  failed,
  conflict,
}

/// Queue Statistics
class QueueStats {
  final int totalPending;
  final int totalFailed;
  final int totalConflicts;
  final int processedToday;
  final DateTime? lastSyncTime;
  final DateTime? nextScheduledSync;

  const QueueStats({
    required this.totalPending,
    required this.totalFailed,
    required this.totalConflicts,
    required this.processedToday,
    this.lastSyncTime,
    this.nextScheduledSync,
  });

  bool get isEmpty => totalPending == 0;
  bool get hasFailures => totalFailed > 0;
  bool get hasConflicts => totalConflicts > 0;
  bool get needsAttention => hasFailures || hasConflicts;

  QueueStats copyWith({
    int? totalPending,
    int? totalFailed,
    int? totalConflicts,
    int? processedToday,
    DateTime? lastSyncTime,
    DateTime? nextScheduledSync,
  }) {
    return QueueStats(
      totalPending: totalPending ?? this.totalPending,
      totalFailed: totalFailed ?? this.totalFailed,
      totalConflicts: totalConflicts ?? this.totalConflicts,
      processedToday: processedToday ?? this.processedToday,
      lastSyncTime: lastSyncTime ?? this.lastSyncTime,
      nextScheduledSync: nextScheduledSync ?? this.nextScheduledSync,
    );
  }
}

/// Queue Manager - Manages offline sync queue with priorities
class QueueManager {
  final AppDatabase _database;
  final SyncMetricsService? _metricsService;
  final _statsController = StreamController<QueueStats>.broadcast();

  QueueStats _currentStats = const QueueStats(
    totalPending: 0,
    totalFailed: 0,
    totalConflicts: 0,
    processedToday: 0,
  );

  Timer? _queueMonitorTimer;

  QueueManager({
    required AppDatabase database,
    SyncMetricsService? metricsService,
  }) : _database = database,
       _metricsService = metricsService {
    _refreshStats();
    _startQueueMonitoring();
  }

  /// Stream of queue statistics
  Stream<QueueStats> get statsStream => _statsController.stream;

  /// Current queue statistics
  QueueStats get currentStats => _currentStats;

  /// Refresh queue statistics
  Future<void> _refreshStats() async {
    try {
      final pending = await _database.getPendingOutbox();
      final logs = await _database.getRecentSyncLogs(limit: 100);

      // Count conflicts from today
      final today = DateTime.now();
      final todayStart = DateTime(today.year, today.month, today.day);

      int conflictsToday = 0;
      int processedToday = 0;
      DateTime? lastSync;

      for (final log in logs) {
        if (log.timestamp.isAfter(todayStart)) {
          if (log.type == 'conflict') conflictsToday++;
          if (log.status == 'success') processedToday++;
        }
        if (lastSync == null && log.type.contains('sync') && log.status == 'success') {
          lastSync = log.timestamp;
        }
      }

      // Count failed items (retry count > 0)
      final failedCount = pending.where((p) => p.retryCount > 0).length;

      _currentStats = QueueStats(
        totalPending: pending.length,
        totalFailed: failedCount,
        totalConflicts: conflictsToday,
        processedToday: processedToday,
        lastSyncTime: lastSync,
      );

      _statsController.add(_currentStats);
    } catch (e) {
      // Log error but don't crash
      await _database.logSync(
        type: 'queue_manager',
        status: 'error',
        message: 'Failed to refresh stats: $e',
      );
    }
  }

  /// Get priority for entity type and operation
  static QueuePriority getPriorityForOperation(String entityType, String method) {
    // Delete operations are critical
    if (method.toUpperCase() == 'DELETE') {
      return QueuePriority.critical;
    }

    // Task completions are high priority
    if (entityType == 'task' && method.toUpperCase() == 'PUT') {
      return QueuePriority.high;
    }

    // Field updates are normal priority
    if (entityType == 'field') {
      return QueuePriority.normal;
    }

    // Everything else is low priority
    return QueuePriority.low;
  }

  /// Add item to queue with priority
  Future<void> enqueue({
    required String tenantId,
    required String entityType,
    required String entityId,
    required String apiEndpoint,
    required String method,
    required String payload,
    String? ifMatch,
    QueuePriority priority = QueuePriority.normal,
  }) async {
    await _database.queueOutboxItem(
      tenantId: tenantId,
      entityType: entityType,
      entityId: entityId,
      apiEndpoint: apiEndpoint,
      method: method,
      payload: payload,
      ifMatch: ifMatch,
    );

    await _refreshStats();
  }

  /// Get pending items sorted by priority
  Future<List<OutboxData>> getPendingItemsSorted({int limit = 50}) async {
    final items = await _database.getPendingOutbox(limit: limit);

    // Sort by priority (based on entity type and method)
    items.sort((a, b) {
      final priorityA = getPriorityForOperation(a.entityType, a.method);
      final priorityB = getPriorityForOperation(b.entityType, b.method);

      // First sort by priority
      final priorityCompare = priorityA.value.compareTo(priorityB.value);
      if (priorityCompare != 0) return priorityCompare;

      // Then by creation time (oldest first)
      return a.createdAt.compareTo(b.createdAt);
    });

    return items;
  }

  /// Get queue health indicator
  QueueHealthStatus getHealthStatus() {
    if (_currentStats.isEmpty) {
      return QueueHealthStatus.healthy;
    }

    if (_currentStats.totalFailed > 5) {
      return QueueHealthStatus.critical;
    }

    if (_currentStats.hasConflicts || _currentStats.hasFailures) {
      return QueueHealthStatus.warning;
    }

    if (_currentStats.totalPending > 20) {
      return QueueHealthStatus.busy;
    }

    return QueueHealthStatus.healthy;
  }

  /// Clear all completed items from queue
  Future<void> cleanup() async {
    await _database.cleanupOutbox();
    await _refreshStats();
  }

  /// Clear old synced items
  Future<void> cleanupOld({Duration olderThan = const Duration(days: 7)}) async {
    await _database.cleanupOldOutbox(olderThan: olderThan);
    await _refreshStats();
  }

  /// Retry failed items
  Future<int> retryFailed() async {
    final pending = await _database.getPendingOutbox();
    int retriedCount = 0;

    for (final item in pending) {
      if (item.retryCount > 0) {
        // Reset retry count to give it another chance
        await _database.customStatement(
          'UPDATE outbox SET retry_count = 0 WHERE id = ?',
          [item.id],
        );
        retriedCount++;
      }
    }

    await _refreshStats();
    return retriedCount;
  }

  /// Notify stats changed (call after sync operations)
  Future<void> notifyStatsChanged() async {
    await _refreshStats();
  }

  /// Start monitoring queue depth for metrics
  void _startQueueMonitoring() {
    _queueMonitorTimer?.cancel();
    _queueMonitorTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) async {
        final pending = await _database.getPendingOutbox();
        await _metricsService?.updateQueueDepth(pending.length);
      },
    );
  }

  void dispose() {
    _queueMonitorTimer?.cancel();
    _statsController.close();
  }
}

/// Queue Health Status
enum QueueHealthStatus {
  /// All synced, no pending items
  healthy,

  /// Some pending items but working normally
  busy,

  /// Has failures or conflicts that need attention
  warning,

  /// Many failures, needs immediate attention
  critical,
}

/// Extension to get Arabic status messages
extension QueueHealthStatusExtension on QueueHealthStatus {
  String get messageAr {
    switch (this) {
      case QueueHealthStatus.healthy:
        return 'متزامن بالكامل';
      case QueueHealthStatus.busy:
        return 'جاري المزامنة...';
      case QueueHealthStatus.warning:
        return 'يوجد تعارضات تحتاج مراجعة';
      case QueueHealthStatus.critical:
        return 'يوجد مشاكل في المزامنة';
    }
  }

  String get messageEn {
    switch (this) {
      case QueueHealthStatus.healthy:
        return 'Fully synced';
      case QueueHealthStatus.busy:
        return 'Syncing...';
      case QueueHealthStatus.warning:
        return 'Conflicts need review';
      case QueueHealthStatus.critical:
        return 'Sync issues detected';
    }
  }
}
