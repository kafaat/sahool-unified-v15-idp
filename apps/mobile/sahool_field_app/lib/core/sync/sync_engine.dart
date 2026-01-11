import 'dart:async';
import 'dart:convert';
import 'package:drift/drift.dart';
import 'package:flutter/foundation.dart';
import '../storage/database.dart';
import '../http/api_client.dart';
import '../config/config.dart';
import 'network_status.dart';
import 'sync_metrics_service.dart';

/// Sync Engine - Handles offline-first synchronization with ETag support
class SyncEngine {
  final AppDatabase database;
  final SyncMetricsService? metricsService;
  final NetworkStatus _networkStatus = NetworkStatus();
  late final ApiClient _apiClient;

  Timer? _syncTimer;
  bool _isSyncing = false;

  final _syncStatusController = StreamController<SyncStatus>.broadcast();
  Stream<SyncStatus> get syncStatus => _syncStatusController.stream;

  SyncEngine({
    required this.database,
    this.metricsService,
  }) {
    _apiClient = ApiClient();
  }

  /// Get current tenant ID from API client
  String get _tenantId => _apiClient.tenantId;

  /// Start periodic sync
  void startPeriodic() {
    _syncTimer?.cancel();
    _syncTimer = Timer.periodic(
      AppConfig.syncInterval,
      (_) => runOnce(),
    );

    // Also sync when network comes back online
    _networkStatus.onlineStream.listen((online) {
      if (online) {
        debugPrint('📶 Network restored - triggering sync');
        runOnce();
      }
    });

    // Initial sync
    runOnce();
  }

  /// Stop periodic sync
  void stop() {
    _syncTimer?.cancel();
    _syncTimer = null;
  }

  /// Run single sync cycle
  Future<SyncResult> runOnce() async {
    if (_isSyncing) {
      return SyncResult(success: false, message: 'Sync already in progress');
    }

    if (!await _networkStatus.checkOnline()) {
      return SyncResult(success: false, message: 'No network connection');
    }

    _isSyncing = true;
    _syncStatusController.add(SyncStatus.syncing);

    final syncStartTime = DateTime.now();

    try {
      // 1. Process outbox (upload local changes)
      final uploadResult = await _processOutbox();

      // 2. Pull latest data from server
      final pullResult = await _pullFromServer();

      // 3. Cleanup completed outbox items
      await database.cleanupOutbox();

      // Log success
      await database.logSync(
        type: 'full_sync',
        status: 'success',
        message: 'Uploaded: ${uploadResult.processed}, Pulled: ${pullResult.count}',
      );

      _syncStatusController.add(SyncStatus.idle);
      _isSyncing = false;

      return SyncResult(
        success: true,
        uploaded: uploadResult.processed,
        downloaded: pullResult.count,
      );
    } catch (e) {
      await database.logSync(
        type: 'full_sync',
        status: 'failed',
        message: e.toString(),
      );

      _syncStatusController.add(SyncStatus.error);
      _isSyncing = false;

      return SyncResult(success: false, message: e.toString());
    }
  }

  /// Process outbox - upload local changes with ETag support
  Future<OutboxResult> _processOutbox() async {
    final items = await database.getPendingOutbox(
      limit: AppConfig.outboxBatchSize,
    );

    int processed = 0;
    int failed = 0;
    int conflicts = 0;

    for (final item in items) {
      try {
        final result = await _processOutboxItem(item);
        if (result == _ItemResult.conflict) {
          conflicts++;
        }
        await database.markOutboxDone(item.id);
        processed++;
      } catch (e) {
        debugPrint('❌ Outbox item failed: ${item.id} - $e');
        await database.bumpOutboxRetry(item.id);
        failed++;

        // Skip items with too many retries
        if (item.retryCount >= AppConfig.maxRetryCount) {
          await database.markOutboxDone(item.id);
          await database.logSync(
            type: 'outbox_max_retry',
            status: 'failed',
            message: 'Item ${item.id} exceeded max retries',
          );
        }
      }
    }

    return OutboxResult(processed: processed, failed: failed, conflicts: conflicts);
  }

  /// Process single outbox item with ETag support
  Future<_ItemResult> _processOutboxItem(OutboxData item) async {
    final payload = jsonDecode(item.payload) as Map<String, dynamic>;
    final payloadSize = item.payload.length;

    // Start metrics tracking
    final operationId = metricsService?.startSyncOperation(
      type: SyncOperationType.upload,
      entityType: item.entityType,
      estimatedPayloadSize: payloadSize,
    );

    // Build headers with If-Match for optimistic locking
    Map<String, String>? headers;
    if (item.ifMatch != null && item.ifMatch!.isNotEmpty) {
      headers = {'If-Match': item.ifMatch!};
    }

    try {
      // Use method and endpoint from outbox item
      switch (item.method.toUpperCase()) {
        case 'POST':
          await _apiClient.post(item.apiEndpoint, payload, headers: headers);
          break;
        case 'PUT':
          await _apiClient.put(item.apiEndpoint, payload, headers: headers);
          break;
        case 'DELETE':
          await _apiClient.delete(item.apiEndpoint, headers: headers);
          break;
        default:
          await _apiClient.post(item.apiEndpoint, payload, headers: headers);
      }

      // Record success
      if (operationId != null) {
        await metricsService?.completeSyncOperation(
          operationId: operationId,
          success: true,
          actualPayloadSize: payloadSize,
        );
      }

      return _ItemResult.success;
    } catch (e) {
      // Check for 409 Conflict
      if (e.toString().contains('409') || e.toString().contains('Conflict')) {
        await _handleConflict(item);

        // Record conflict
        if (operationId != null) {
          await metricsService?.completeSyncOperation(
            operationId: operationId,
            success: true,
            actualPayloadSize: payloadSize,
            wasConflict: true,
            conflictResolution: ConflictResolution.serverWins,
          );
        }

        return _ItemResult.conflict;
      }

      // Record failure
      if (operationId != null) {
        await metricsService?.completeSyncOperation(
          operationId: operationId,
          success: false,
          errorMessage: e.toString(),
        );
      }

      rethrow;
    }
  }

  /// Handle 409 Conflict - apply server version
  Future<void> _handleConflict(OutboxData item) async {
    // Add sync event for UI notification
    await database.addSyncEvent(
      tenantId: _tenantId,
      type: 'CONFLICT',
      message: 'تم تطبيق نسخة السيرفر بسبب تعارض في ${_getEntityTypeAr(item.entityType)}',
      entityType: item.entityType,
      entityId: item.entityId,
    );

    await database.logSync(
      type: 'conflict',
      status: 'resolved',
      message: 'Conflict resolved by applying server version for: ${item.entityType}/${item.entityId}',
    );
  }

  /// Get Arabic entity type name
  String _getEntityTypeAr(String type) {
    switch (type) {
      case 'field':
        return 'الحقل';
      case 'task':
        return 'المهمة';
      default:
        return 'البيانات';
    }
  }

  /// Pull latest data from server
  Future<PullResult> _pullFromServer() async {
    int count = 0;

    // Start metrics tracking
    final operationId = metricsService?.startSyncOperation(
      type: SyncOperationType.download,
      entityType: 'tasks',
    );

    try {
      // Pull tasks
      final tasksResponse = await _apiClient.get(
        '/tasks',
        queryParameters: {'tenant_id': _apiClient.tenantId},
      );

      if (tasksResponse is List) {
        await database.upsertTasksFromServer(
          tasksResponse.cast<Map<String, dynamic>>(),
        );
        count += tasksResponse.length;

        // Estimate payload size
        final payloadSize = jsonEncode(tasksResponse).length;

        // Record success
        if (operationId != null) {
          await metricsService?.completeSyncOperation(
            operationId: operationId,
            success: true,
            actualPayloadSize: payloadSize,
          );
        }
      }
    } catch (e) {
      debugPrint('⚠️ Failed to pull tasks: $e');

      // Record failure
      if (operationId != null) {
        await metricsService?.completeSyncOperation(
          operationId: operationId,
          success: false,
          errorMessage: e.toString(),
        );
      }
    }

    return PullResult(count: count);
  }

  /// Force refresh from server
  Future<void> forceRefresh() async {
    if (!await _networkStatus.checkOnline()) {
      throw Exception('لا يوجد اتصال بالإنترنت');
    }

    _syncStatusController.add(SyncStatus.syncing);

    try {
      await _pullFromServer();
      _syncStatusController.add(SyncStatus.idle);
    } catch (e) {
      _syncStatusController.add(SyncStatus.error);
      rethrow;
    }
  }

  void dispose() {
    stop();
    _networkStatus.dispose();
    _syncStatusController.close();
  }
}

/// Sync status enum
enum SyncStatus { idle, syncing, error }

/// Sync result
class SyncResult {
  final bool success;
  final String? message;
  final int uploaded;
  final int downloaded;

  SyncResult({
    required this.success,
    this.message,
    this.uploaded = 0,
    this.downloaded = 0,
  });
}

/// Outbox processing result
class OutboxResult {
  final int processed;
  final int failed;
  final int conflicts;

  OutboxResult({
    required this.processed,
    required this.failed,
    this.conflicts = 0,
  });
}

/// Pull result
class PullResult {
  final int count;

  PullResult({required this.count});
}

/// Internal item processing result
enum _ItemResult { success, conflict, failed }
