import 'dart:async';
import 'dart:convert';
import 'package:drift/drift.dart';
import '../storage/database.dart';
import '../http/api_client.dart';
import '../config/config.dart';
import 'network_status.dart';

/// Sync Engine - Handles offline-first synchronization
class SyncEngine {
  final AppDatabase database;
  final NetworkStatus _networkStatus = NetworkStatus();
  late final ApiClient _apiClient;

  Timer? _syncTimer;
  bool _isSyncing = false;

  final _syncStatusController = StreamController<SyncStatus>.broadcast();
  Stream<SyncStatus> get syncStatus => _syncStatusController.stream;

  SyncEngine({required this.database}) {
    _apiClient = ApiClient();
  }

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
        print('📶 Network restored - triggering sync');
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

  /// Process outbox - upload local changes
  Future<OutboxResult> _processOutbox() async {
    final items = await database.getPendingOutbox(
      limit: AppConfig.outboxBatchSize,
    );

    int processed = 0;
    int failed = 0;

    for (final item in items) {
      try {
        await _processOutboxItem(item);
        await database.markOutboxDone(item.id);
        processed++;
      } catch (e) {
        print('❌ Outbox item failed: ${item.id} - $e');
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

    return OutboxResult(processed: processed, failed: failed);
  }

  /// Process single outbox item
  Future<void> _processOutboxItem(OutboxData item) async {
    final payload = jsonDecode(item.payloadJson) as Map<String, dynamic>;

    switch (item.type) {
      case 'task_complete':
        await _apiClient.post(
          '/tasks/${payload['task_id']}/complete',
          {
            'tenant_id': payload['tenant_id'],
            'evidence_notes': payload['evidence_notes'],
            'evidence_photos': payload['evidence_photos'],
          },
        );
        break;

      case 'task_update':
        await _apiClient.put(
          '/tasks/${payload['task_id']}',
          payload,
        );
        break;

      default:
        print('⚠️ Unknown outbox type: ${item.type}');
    }
  }

  /// Pull latest data from server
  Future<PullResult> _pullFromServer() async {
    int count = 0;

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
      }
    } catch (e) {
      print('⚠️ Failed to pull tasks: $e');
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

  OutboxResult({required this.processed, required this.failed});
}

/// Pull result
class PullResult {
  final int count;

  PullResult({required this.count});
}
