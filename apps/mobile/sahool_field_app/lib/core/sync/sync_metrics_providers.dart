import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'sync_metrics_service.dart';
import '../storage/database.dart';
import 'sync_engine.dart';
import 'queue_manager.dart';

// Import canonical providers from main.dart
import '../../main.dart' show databaseProvider, syncEngineProvider;

/// SharedPreferences provider - must be overridden in main.dart
/// This is the canonical definition for SharedPreferences
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError(
    'sharedPreferencesProvider must be overridden in main.dart with actual SharedPreferences instance',
  );
});

// Note: databaseProvider is imported from main.dart (canonical source)
// Note: syncEngineProvider is imported from main.dart (canonical source)

/// Provide SyncMetricsService instance
final syncMetricsServiceProvider = Provider<SyncMetricsService>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return SyncMetricsService(prefs);
});

/// Provide base QueueManager without metrics
/// This is the canonical queueManagerProvider definition
final queueManagerProvider = Provider<QueueManager>((ref) {
  final database = ref.watch(databaseProvider);
  return QueueManager(database: database);
});

/// Metrics-aware wrapper for SyncEngine that tracks sync operations
/// Uses composition pattern instead of constructor injection
/// Provides comprehensive tracking of uploads, downloads, conflicts, and retries
class MetricsAwareSyncEngine {
  final SyncEngine _engine;
  final SyncMetricsService _metrics;
  StreamSubscription<SyncStatus>? _statusSubscription;
  StreamSubscription<BackoffStatus>? _backoffSubscription;

  MetricsAwareSyncEngine(this._engine, this._metrics) {
    _initializeStatusTracking();
  }

  void _initializeStatusTracking() {
    // Track sync status changes for metrics
    _statusSubscription = _engine.syncStatus.listen((status) {
      if (status == SyncStatus.error) {
        // Update metrics when sync enters error state
        _metrics.updateQueueDepth(0); // Will be updated on next queue check
      }
    });

    // Track backoff status for retry metrics
    _backoffSubscription = _engine.backoffStatus.listen((status) {
      if (status.isBackoffActive) {
        // Track endpoints in backoff
        for (final endpoint in status.affectedEndpoints) {
          final retryCount = endpoint.retryCount;
          if (retryCount > 0) {
            _metrics.recordRetry(
              operationId: 'backoff_${endpoint.endpoint}',
              attemptNumber: retryCount,
              backoffDelay: endpoint.timeUntilRetry ?? Duration.zero,
            );
          }
        }
      }
    });
  }

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

  /// Run single sync cycle with comprehensive metrics tracking
  /// Tracks both upload (outbox processing) and download (server pull) operations
  Future<SyncResult> runOnce() async {
    // Track upload operation (processing local changes)
    final uploadOperationId = _metrics.startSyncOperation(
      type: SyncOperationType.upload,
      entityType: 'outbox',
    );

    try {
      final result = await _engine.runOnce();

      // Complete upload operation tracking
      await _metrics.completeSyncOperation(
        operationId: uploadOperationId,
        success: result.success,
        actualPayloadSize: result.uploaded * 1024, // Estimate 1KB per item
        errorMessage: result.success ? null : result.message,
      );

      // Track download operation if items were pulled
      if (result.downloaded > 0) {
        final downloadOperationId = _metrics.startSyncOperation(
          type: SyncOperationType.download,
          entityType: 'server',
        );
        await _metrics.completeSyncOperation(
          operationId: downloadOperationId,
          success: true,
          actualPayloadSize: result.downloaded * 1024,
        );
      }

      return result;
    } catch (e) {
      await _metrics.completeSyncOperation(
        operationId: uploadOperationId,
        success: false,
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  /// Track a conflict resolution
  Future<void> trackConflict({
    required String entityType,
    required String entityId,
    required ConflictResolution resolution,
  }) async {
    final operationId = _metrics.startSyncOperation(
      type: SyncOperationType.conflict,
      entityType: entityType,
    );
    await _metrics.completeSyncOperation(
      operationId: operationId,
      success: true,
      wasConflict: true,
      conflictResolution: resolution,
    );
  }

  /// Track a retry attempt
  Future<void> trackRetry({
    required String endpoint,
    required int attemptNumber,
    Duration backoffDelay = Duration.zero,
  }) async {
    await _metrics.recordRetry(
      operationId: 'retry_$endpoint',
      attemptNumber: attemptNumber,
      backoffDelay: backoffDelay,
    );
  }

  /// Get sync statistics including metrics
  SyncStatistics getStatistics() => _engine.getStatistics();

  /// Get current metrics snapshot
  SyncMetrics getCurrentMetrics() => _metrics.currentMetrics;

  /// Export metrics as JSON for debugging
  Map<String, dynamic> exportMetrics() => _metrics.exportMetrics();

  /// Sync status stream
  Stream<SyncStatus> get syncStatus => _engine.syncStatus;

  /// Backoff status stream
  Stream<BackoffStatus> get backoffStatus => _engine.backoffStatus;

  /// Dispose subscriptions
  void dispose() {
    _statusSubscription?.cancel();
    _backoffSubscription?.cancel();
  }
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
final metricsAwareQueueManagerProvider =
    Provider<MetricsAwareQueueManager>((ref) {
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
