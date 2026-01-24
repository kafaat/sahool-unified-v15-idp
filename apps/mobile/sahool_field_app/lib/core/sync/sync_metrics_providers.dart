import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'sync_metrics_service.dart';
import '../storage/database.dart';
import 'sync_engine.dart';
import 'queue_manager.dart';

/// Initialize SharedPreferences for metrics service
/// Must be overridden in main.dart with actual SharedPreferences instance
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError(
    'sharedPreferencesProvider must be overridden in main.dart with actual SharedPreferences instance',
  );
});

/// Database provider (must be overridden in app)
final databaseProvider = Provider<AppDatabase>((ref) {
  throw UnimplementedError(
    'databaseProvider must be overridden in main.dart with actual AppDatabase instance',
  );
});

/// Provide SyncMetricsService instance
final syncMetricsServiceProvider = Provider<SyncMetricsService>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return SyncMetricsService(prefs);
});

/// Provide base SyncEngine without metrics
final syncEngineProvider = Provider<SyncEngine>((ref) {
  final database = ref.watch(databaseProvider);
  return SyncEngine(database: database);
});

/// Provide base QueueManager without metrics
final queueManagerProvider = Provider<QueueManager>((ref) {
  final database = ref.watch(databaseProvider);
  return QueueManager(database: database);
});

/// Metrics-aware wrapper for SyncEngine that tracks sync operations
/// Uses composition pattern instead of constructor injection
class MetricsAwareSyncEngine {
  final SyncEngine _engine;
  final SyncMetricsService _metrics;

  MetricsAwareSyncEngine(this._engine, this._metrics);

  /// Get the underlying sync engine
  SyncEngine get engine => _engine;

  /// Get the metrics service
  SyncMetricsService get metrics => _metrics;

  /// Start periodic sync with metrics tracking
  void startPeriodic() {
    _engine.startPeriodic();
  }

  /// Stop periodic sync
  void stop() {
    _engine.stop();
  }

  /// Run single sync cycle with metrics tracking
  Future<SyncResult> runOnce() async {
    // Start tracking the operation (upload since we're pushing local changes first)
    final operationId = _metrics.startSyncOperation(
      type: SyncOperationType.upload,
      entityType: 'all',
    );

    try {
      final result = await _engine.runOnce();

      // Complete the operation tracking
      await _metrics.completeSyncOperation(
        operationId: operationId,
        success: result.success,
        // Estimate payload size from number of items
        actualPayloadSize: (result.uploaded + result.downloaded) * 1024,
        errorMessage: result.success ? null : result.message,
      );

      return result;
    } catch (e) {
      await _metrics.completeSyncOperation(
        operationId: operationId,
        success: false,
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// Sync status stream
  Stream<SyncStatus> get syncStatus => _engine.syncStatus;

  /// Backoff status stream
  Stream<BackoffStatus> get backoffStatus => _engine.backoffStatus;
}

/// Provide MetricsAwareSyncEngine with composition pattern
final metricsAwareSyncEngineProvider = Provider<MetricsAwareSyncEngine>((ref) {
  final engine = ref.watch(syncEngineProvider);
  final metrics = ref.watch(syncMetricsServiceProvider);
  return MetricsAwareSyncEngine(engine, metrics);
});

/// Metrics-aware wrapper for QueueManager
class MetricsAwareQueueManager {
  final QueueManager _manager;
  final SyncMetricsService _metrics;

  MetricsAwareQueueManager(this._manager, this._metrics);

  /// Get the underlying queue manager
  QueueManager get manager => _manager;

  /// Get the metrics service
  SyncMetricsService get metrics => _metrics;

  /// Current queue statistics
  QueueStats get currentStats => _manager.currentStats;

  /// Stream of queue statistics
  Stream<QueueStats> get statsStream => _manager.statsStream;

  /// Add item to queue with metrics tracking
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
    // Track queue depth before adding
    await _metrics.updateQueueDepth(_manager.currentStats.totalPending + 1);

    await _manager.enqueue(
      tenantId: tenantId,
      entityType: entityType,
      entityId: entityId,
      apiEndpoint: apiEndpoint,
      method: method,
      payload: payload,
      ifMatch: ifMatch,
      priority: priority,
    );
  }

  /// Get pending items sorted by priority
  Future<List<OutboxData>> getPendingItemsSorted({int limit = 50}) async {
    return await _manager.getPendingItemsSorted(limit: limit);
  }

  /// Cleanup completed items
  Future<void> cleanup() async {
    await _manager.cleanup();
    await _metrics.updateQueueDepth(_manager.currentStats.totalPending);
  }

  /// Get queue health status
  QueueHealthStatus getHealthStatus() => _manager.getHealthStatus();
}

/// Provide MetricsAwareQueueManager with composition pattern
final metricsAwareQueueManagerProvider = Provider<MetricsAwareQueueManager>((ref) {
  final manager = ref.watch(queueManagerProvider);
  final metrics = ref.watch(syncMetricsServiceProvider);
  return MetricsAwareQueueManager(manager, metrics);
});

/// Stream provider for sync status
final syncStatusStreamProvider = StreamProvider<SyncStatus>((ref) {
  final engine = ref.watch(syncEngineProvider);
  return engine.syncStatus;
});

/// Stream provider for queue stats
final queueStatsStreamProvider = StreamProvider<QueueStats>((ref) {
  final manager = ref.watch(queueManagerProvider);
  return manager.statsStream;
});

/// Provider for current sync metrics
final syncMetricsProvider = Provider<SyncMetrics>((ref) {
  final service = ref.watch(syncMetricsServiceProvider);
  return service.currentMetrics;
});

/// Stream provider for real-time metrics updates
final syncMetricsStreamProvider = StreamProvider<SyncMetrics>((ref) {
  final service = ref.watch(syncMetricsServiceProvider);
  return service.metricsStream;
});

/// Legacy alias for backwards compatibility
@Deprecated('Use syncMetricsServiceProvider instead')
final syncMetricsServiceProviderImpl = syncMetricsServiceProvider;

/// Legacy alias for backwards compatibility
@Deprecated('Use metricsAwareSyncEngineProvider instead')
final syncEngineWithMetricsProvider = metricsAwareSyncEngineProvider;

/// Legacy alias for backwards compatibility
@Deprecated('Use metricsAwareQueueManagerProvider instead')
final queueManagerWithMetricsProvider = metricsAwareQueueManagerProvider;
