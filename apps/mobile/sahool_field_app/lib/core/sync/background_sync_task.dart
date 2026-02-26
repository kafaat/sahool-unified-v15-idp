import 'dart:convert';
import 'package:workmanager/workmanager.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../storage/database.dart';
import '../http/api_client.dart';
import '../config/env_config.dart';

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
    final tenantId = prefs.getString('tenant_id') ?? EnvConfig.defaultTenantId;

    // Check if we have pending items
    final pendingItems = await database.getPendingOutbox(
      limit: BackgroundSyncConfig.maxBatchSize,
    );

    if (pendingItems.isEmpty) {
      await _logBackgroundInfo('No pending items to sync');
      return true;
    }

    await _logBackgroundInfo(
        'Starting background sync: ${pendingItems.length} items');

    int synced = 0;
    int failed = 0;
    int conflicts = 0;

    for (final item in pendingItems) {
      try {
        final result =
            await _processSyncItem(item, apiClient, database, tenantId);

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
        if (item.retryCount >= EnvConfig.maxRetryCount) {
          await database.markOutboxDone(item.id);
        }
      }
    }

    await database.logSync(
      type: 'background_sync',
      status: failed == 0 ? 'success' : 'partial',
      message:
          'Background: synced=$synced, conflicts=$conflicts, failed=$failed',
    );

    // Update last sync timestamp
    await prefs.setInt(
        'last_background_sync', DateTime.now().millisecondsSinceEpoch);

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
      await _handleConflict(item, database, apiClient, tenantId);
      await database.markOutboxDone(item.id);
      return _SyncItemResult.conflict;
    }
    rethrow;
  }
}

/// Handle 409 Conflict - fetch and apply server version
Future<void> _handleConflict(
  OutboxData item,
  AppDatabase database,
  ApiClient apiClient,
  String tenantId,
) async {
  try {
    // Fetch the latest server version and apply it
    await _fetchAndApplyServerVersion(item, database, apiClient, tenantId);
  } catch (e) {
    await _logBackgroundError(
      'Failed to fetch server version for conflict: ${item.entityType}/${item.entityId}: $e',
    );
  }

  await database.addSyncEvent(
    tenantId: tenantId,
    type: 'CONFLICT',
    message:
        'Server version applied due to conflict in ${_getEntityTypeAr(item.entityType)}',
    entityType: item.entityType,
    entityId: item.entityId,
  );

  await database.logSync(
    type: 'conflict',
    status: 'resolved',
    message:
        'Conflict resolved by applying server version for: ${item.entityType}/${item.entityId}',
  );
}

/// Fetch and apply the server version of an entity
Future<void> _fetchAndApplyServerVersion(
  OutboxData item,
  AppDatabase database,
  ApiClient apiClient,
  String tenantId,
) async {
  switch (item.entityType) {
    case 'field':
      await _fetchAndApplyFieldFromServer(
          item.entityId, database, apiClient, tenantId);
      break;
    case 'task':
      await _fetchAndApplyTaskFromServer(
          item.entityId, database, apiClient, tenantId);
      break;
    default:
      await _logBackgroundInfo(
        'Unknown entity type for conflict resolution: ${item.entityType}',
      );
  }
}

/// Fetch and apply field data from server
Future<void> _fetchAndApplyFieldFromServer(
  String fieldId,
  AppDatabase database,
  ApiClient apiClient,
  String tenantId,
) async {
  final response = await apiClient.get(
    '/api/v1/fields/$fieldId',
    queryParameters: {'tenant_id': tenantId},
  );

  if (response is Map<String, dynamic>) {
    // Handle GeoJSON feature response
    final Map<String, dynamic> fieldData;
    if (response.containsKey('properties')) {
      // GeoJSON Feature format
      final props = response['properties'] as Map<String, dynamic>;
      fieldData = {
        'id': fieldId,
        'remote_id': response['id'] ?? fieldId,
        'tenant_id': props['tenant_id'] ?? tenantId,
        'farm_id': props['farm_id'],
        'name': props['name'],
        'crop_type': props['crop_type'],
        'geometry': response['geometry'],
        'area_hectares': props['area_hectares'],
        'status': props['status'],
        'ndvi_current': props['ndvi_current'],
        'ndvi_updated_at': props['ndvi_updated_at'],
        'etag': props['etag'],
        'created_at': props['created_at'] ?? DateTime.now().toIso8601String(),
        'updated_at': props['updated_at'] ?? DateTime.now().toIso8601String(),
      };
    } else {
      fieldData = response;
    }

    await database.upsertFieldsFromServer([fieldData]);
    await _logBackgroundInfo('Server field version applied: $fieldId');
  }
}

/// Fetch and apply task data from server
Future<void> _fetchAndApplyTaskFromServer(
  String taskId,
  AppDatabase database,
  ApiClient apiClient,
  String tenantId,
) async {
  final response = await apiClient.get(
    '/api/v1/tasks/$taskId',
    queryParameters: {'tenant_id': tenantId},
  );

  if (response is Map<String, dynamic>) {
    await database.upsertTasksFromServer([response]);
    await _logBackgroundInfo('Server task version applied: $taskId');
  }
}

String _getEntityTypeAr(String type) {
  switch (type) {
    case 'field':
      return 'field';
    case 'task':
      return 'task';
    default:
      return 'data';
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
      isInDebugMode: EnvConfig.isDebugMode,
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
