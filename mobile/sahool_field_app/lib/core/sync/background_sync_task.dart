import 'dart:convert';
import 'package:workmanager/workmanager.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../storage/database.dart';
import '../http/api_client.dart';
import '../config/config.dart';

/// Background Sync Task Names
const String backgroundSyncTask = 'sahool_background_sync';
const String periodicSyncTask = 'sahool_periodic_sync';

/// Background Sync Configuration
class BackgroundSyncConfig {
  static const Duration minInterval = Duration(minutes: 15);
  static const Duration maxRetryDelay = Duration(hours: 1);
  static const int maxBatchSize = 25;
}

/// Workmanager Callback Dispatcher
/// Must be a top-level function
@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    try {
      switch (task) {
        case backgroundSyncTask:
        case periodicSyncTask:
          return await _executeBackgroundSync();
        default:
          return Future.value(true);
      }
    } catch (e) {
      await _logBackgroundError('Background task failed: $e');
      return Future.value(false);
    }
  });
}

/// Execute background sync
Future<bool> _executeBackgroundSync() async {
  final database = AppDatabase();
  final apiClient = ApiClient();

  try {
    // Get tenant ID from shared preferences
    final prefs = await SharedPreferences.getInstance();
    final tenantId = prefs.getString('tenant_id') ?? AppConfig.defaultTenantId;

    // Check if we have pending items
    final pendingItems = await database.getPendingOutbox(
      limit: BackgroundSyncConfig.maxBatchSize,
    );

    if (pendingItems.isEmpty) {
      await _logBackgroundInfo('No pending items to sync');
      return true;
    }

    await _logBackgroundInfo('Starting background sync: ${pendingItems.length} items');

    int synced = 0;
    int failed = 0;
    int conflicts = 0;

    for (final item in pendingItems) {
      try {
        final result = await _processSyncItem(item, apiClient, database, tenantId);

        switch (result) {
          case _SyncItemResult.success:
            synced++;
            break;
          case _SyncItemResult.conflict:
            conflicts++;
            break;
          case _SyncItemResult.failed:
            failed++;
            break;
        }
      } catch (e) {
        failed++;
        await database.bumpOutboxRetry(item.id);

        // Mark as done if exceeded max retries
        if (item.retryCount >= AppConfig.maxRetryCount) {
          await database.markOutboxDone(item.id);
        }
      }
    }

    await database.logSync(
      type: 'background_sync',
      status: failed == 0 ? 'success' : 'partial',
      message: 'Background: synced=$synced, conflicts=$conflicts, failed=$failed',
    );

    // Update last sync timestamp
    await prefs.setInt('last_background_sync', DateTime.now().millisecondsSinceEpoch);

    return true;
  } catch (e) {
    await database.logSync(
      type: 'background_sync',
      status: 'failed',
      message: 'Background sync failed: $e',
    );
    return false;
  }
}

/// Process single sync item
Future<_SyncItemResult> _processSyncItem(
  OutboxData item,
  ApiClient apiClient,
  AppDatabase database,
  String tenantId,
) async {
  final payload = jsonDecode(item.payload) as Map<String, dynamic>;

  // Build headers with If-Match for optimistic locking
  Map<String, String>? headers;
  if (item.ifMatch != null && item.ifMatch!.isNotEmpty) {
    headers = {'If-Match': item.ifMatch!};
  }

  try {
    switch (item.method.toUpperCase()) {
      case 'POST':
        await apiClient.post(item.apiEndpoint, payload, headers: headers);
        break;
      case 'PUT':
        await apiClient.put(item.apiEndpoint, payload, headers: headers);
        break;
      case 'DELETE':
        await apiClient.delete(item.apiEndpoint, headers: headers);
        break;
      default:
        await apiClient.post(item.apiEndpoint, payload, headers: headers);
    }

    await database.markOutboxDone(item.id);
    return _SyncItemResult.success;
  } catch (e) {
    // Check for 409 Conflict
    if (e.toString().contains('409') || e.toString().contains('Conflict')) {
      await _handleConflict(item, database, tenantId);
      await database.markOutboxDone(item.id);
      return _SyncItemResult.conflict;
    }
    rethrow;
  }
}

/// Handle 409 Conflict
Future<void> _handleConflict(
  OutboxData item,
  AppDatabase database,
  String tenantId,
) async {
  await database.addSyncEvent(
    tenantId: tenantId,
    type: 'CONFLICT',
    message: 'تم تطبيق نسخة السيرفر بسبب تعارض في ${_getEntityTypeAr(item.entityType)}',
    entityType: item.entityType,
    entityId: item.entityId,
  );
}

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

Future<void> _logBackgroundInfo(String message) async {
  final database = AppDatabase();
  await database.logSync(
    type: 'background_task',
    status: 'info',
    message: message,
  );
}

Future<void> _logBackgroundError(String message) async {
  final database = AppDatabase();
  await database.logSync(
    type: 'background_task',
    status: 'error',
    message: message,
  );
}

enum _SyncItemResult { success, conflict, failed }

/// Background Sync Manager - Helper class for initialization
class BackgroundSyncManager {
  static bool _initialized = false;

  /// Initialize workmanager for background sync
  static Future<void> initialize() async {
    if (_initialized) return;

    await Workmanager().initialize(
      callbackDispatcher,
      isInDebugMode: AppConfig.isDebug,
    );

    _initialized = true;
  }

  /// Register periodic background sync task
  static Future<void> registerPeriodicSync() async {
    await initialize();

    await Workmanager().registerPeriodicTask(
      periodicSyncTask,
      periodicSyncTask,
      frequency: BackgroundSyncConfig.minInterval,
      constraints: Constraints(
        networkType: NetworkType.connected,
        requiresBatteryNotLow: true,
      ),
      existingWorkPolicy: ExistingWorkPolicy.keep,
      backoffPolicy: BackoffPolicy.exponential,
      backoffPolicyDelay: const Duration(minutes: 5),
    );
  }

  /// Register one-time background sync task
  static Future<void> registerOneTimeSync() async {
    await initialize();

    await Workmanager().registerOneOffTask(
      '${backgroundSyncTask}_${DateTime.now().millisecondsSinceEpoch}',
      backgroundSyncTask,
      constraints: Constraints(
        networkType: NetworkType.connected,
      ),
      backoffPolicy: BackoffPolicy.exponential,
      backoffPolicyDelay: const Duration(seconds: 30),
    );
  }

  /// Cancel all background sync tasks
  static Future<void> cancelAll() async {
    await Workmanager().cancelAll();
  }

  /// Cancel periodic sync only
  static Future<void> cancelPeriodicSync() async {
    await Workmanager().cancelByUniqueName(periodicSyncTask);
  }
}
