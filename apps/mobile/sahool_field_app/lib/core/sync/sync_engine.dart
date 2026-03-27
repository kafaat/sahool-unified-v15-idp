import 'dart:async';
import 'dart:convert';
import '../storage/database.dart';
import '../http/api_client.dart';
import '../http/rate_limiter.dart';
import '../config/env_config.dart';
import '../utils/app_logger.dart';
import '../utils/retry_policy.dart';
import 'network_status.dart';

/// Sync Engine - Handles offline-first synchronization with ETag support
/// Features exponential backoff and circuit breaker for resilient syncing
class SyncEngine {
  final AppDatabase database;
  final NetworkStatus _networkStatus = NetworkStatus();
  late final ApiClient _apiClient;

  Timer? _syncTimer;
  bool _isSyncing = false;
  int _consecutiveFailures = 0;
  DateTime? _lastSuccessfulSync;

  // Exponential backoff and circuit breaker for per-endpoint retry management
  final EndpointRetryTracker _retryTracker = EndpointRetryTracker(
    backoffPolicy: ExponentialBackoff(
      initialDelayMs: 1000, // 1 second
      multiplier: 2.0, // 2x per retry
      maxDelayMs: 300000, // 5 minutes
      maxRetries: 5,
      enableJitter: true,
    ),
  );

  final _syncStatusController = StreamController<SyncStatus>.broadcast();
  Stream<SyncStatus> get syncStatus => _syncStatusController.stream;

  // Backoff status stream for UI feedback
  final _backoffStatusController = StreamController<BackoffStatus>.broadcast();
  Stream<BackoffStatus> get backoffStatus => _backoffStatusController.stream;

  SyncEngine({required this.database}) {
    _apiClient = ApiClient();
  }

  /// Get current tenant ID from API client
  String get _tenantId => _apiClient.tenantId;

  /// Start periodic sync
  void startPeriodic() {
    _syncTimer?.cancel();
    _syncTimer = Timer.periodic(
      EnvConfig.syncInterval,
      (_) => runOnce(),
    );

    // Also sync when network comes back online
    _networkStatus.onlineStream.listen((online) {
      if (online) {
        AppLogger.i('Network restored - triggering sync', tag: 'SyncEngine');
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
        message:
            'Uploaded: ${uploadResult.processed}, Pulled: ${pullResult.count}, Skipped: ${uploadResult.skipped}',
      );

      // Reset failure counter and backoff on success
      _consecutiveFailures = 0;
      _lastSuccessfulSync = DateTime.now();

      // Emit idle backoff status
      _emitBackoffStatus();

      _syncStatusController.add(SyncStatus.idle);
      _isSyncing = false;

      return SyncResult(
        success: true,
        uploaded: uploadResult.processed,
        downloaded: pullResult.count,
      );
    } catch (e) {
      // Increment failure counter
      _consecutiveFailures++;

      await database.logSync(
        type: 'full_sync',
        status: 'failed',
        message: e.toString(),
      );

      _syncStatusController.add(SyncStatus.error);
      _isSyncing = false;

      // Apply exponential backoff if too many failures
      if (_consecutiveFailures >= 3) {
        final backoffDuration = _calculateBackoff(_consecutiveFailures);
        AppLogger.w('Too many sync failures, backing off',
            tag: 'SyncEngine',
            data: {'backoff_seconds': backoffDuration.inSeconds});

        // Reschedule next sync with backoff
        _syncTimer?.cancel();
        _syncTimer = Timer(backoffDuration, () {
          _syncTimer?.cancel();
          startPeriodic();
        });
      }

      return SyncResult(success: false, message: e.toString());
    }
  }

  /// Process outbox - upload local changes with ETag support
  /// Uses exponential backoff and circuit breaker per endpoint
  Future<OutboxResult> _processOutbox() async {
    final items = await database.getPendingOutbox(
      limit: EnvConfig.outboxBatchSize,
    );

    int processed = 0;
    int failed = 0;
    int conflicts = 0;
    int skipped = 0;

    for (final item in items) {
      final endpoint = item.apiEndpoint;

      // Validate endpoint before processing
      if (endpoint.isEmpty) {
        AppLogger.e('Skipping outbox item with empty endpoint',
            tag: 'SyncEngine',
            data: {'itemId': item.id, 'method': item.method});
        await database.markOutboxDone(item.id);
        await database.logSync(
          type: 'outbox_invalid_endpoint',
          status: 'failed',
          message: 'Item ${item.id} has empty endpoint',
        );
        failed++;
        continue;
      }

      // Check if endpoint can be retried based on backoff and circuit breaker
      if (!_retryTracker.canRetryNow(endpoint)) {
        final status = _retryTracker.getEndpointStatus(endpoint);
        skipped++;

        // Update backoff status for UI
        _emitBackoffStatus();

        AppLogger.d('Skipping outbox item',
            tag: 'SyncEngine',
            data: {'itemId': item.id, 'status': status.statusDescription});
        continue;
      }

      try {
        // Add small delay between items to respect rate limits
        if (processed > 0) {
          await Future<void>.delayed(const Duration(milliseconds: 100));
        }

        final result = await _processOutboxItem(item);

        if (result == _ItemResult.conflict) {
          conflicts++;
        }

        // Mark as done and record success in retry tracker
        await database.markOutboxDone(item.id);
        _retryTracker.recordSuccess(endpoint);
        processed++;

        // Emit updated backoff status
        _emitBackoffStatus();
      } catch (e) {
        AppLogger.e('Outbox item failed',
            tag: 'SyncEngine',
            data: {'itemId': item.id, 'error': e.toString()});

        // Check if it's a rate limit error
        final isRateLimitError = e.toString().contains('RateLimitException') ||
            e.toString().contains('429');

        if (isRateLimitError) {
          // For rate limit errors, add longer delay and retry later
          AppLogger.w('Rate limit hit, pausing outbox processing',
              tag: 'SyncEngine');
          await Future<void>.delayed(const Duration(seconds: 5));

          // Don't increment retry count for rate limit errors
          // They will be retried in the next sync cycle
          break; // Stop processing this batch
        } else {
          // Increment retry count in database
          await database.bumpOutboxRetry(item.id);
          failed++;

          // Record failure in retry tracker
          _retryTracker.recordFailure(endpoint, item.retryCount + 1);

          // Emit updated backoff status
          _emitBackoffStatus();

          // Skip items with too many retries
          if (item.retryCount >= EnvConfig.maxRetryCount) {
            await database.markOutboxDone(item.id);
            await database.logSync(
              type: 'outbox_max_retry',
              status: 'failed',
              message:
                  'Item ${item.id} exceeded max retries (endpoint: $endpoint)',
            );
          }
        }
      }
    }

    // Log summary if items were skipped
    if (skipped > 0) {
      AppLogger.d('Skipped items due to backoff/circuit breaker',
          tag: 'SyncEngine', data: {'skipped': skipped});
      await database.logSync(
        type: 'outbox_backoff',
        status: 'info',
        message: 'Skipped $skipped items due to exponential backoff',
      );
    }

    return OutboxResult(
      processed: processed,
      failed: failed,
      conflicts: conflicts,
      skipped: skipped,
    );
  }

  /// Process single outbox item with ETag support
  Future<_ItemResult> _processOutboxItem(OutboxData item) async {
    // Validate endpoint before making API call
    if (item.apiEndpoint.isEmpty) {
      AppLogger.e('Invalid outbox item: empty apiEndpoint',
          tag: 'SyncEngine', data: {'itemId': item.id, 'method': item.method});
      throw ArgumentError(
          'API endpoint cannot be empty for outbox item ${item.id}');
    }

    // Validate endpoint format
    if (!item.apiEndpoint.startsWith('/')) {
      AppLogger.w('Endpoint does not start with /, adding prefix',
          tag: 'SyncEngine', data: {'endpoint': item.apiEndpoint});
    }

    final payload = jsonDecode(item.payload) as Map<String, dynamic>;

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
      return _ItemResult.success;
    } catch (e) {
      // Check for 409 Conflict
      if (e.toString().contains('409') || e.toString().contains('Conflict')) {
        await _handleConflict(item);
        return _ItemResult.conflict;
      }
      rethrow;
    }
  }

  /// Handle 409 Conflict - fetch and apply server version
  /// Implements Last-Write-Wins (LWW) strategy with server preference
  Future<void> _handleConflict(OutboxData item) async {
    AppLogger.i('Handling conflict', tag: 'SyncEngine', data: {
      'entityType': item.entityType,
      'entityId': item.entityId,
    });

    try {
      // Fetch the latest server version and apply it
      await _fetchAndApplyServerVersion(item);
    } catch (e) {
      AppLogger.e('Failed to fetch server version for conflict resolution',
          tag: 'SyncEngine', data: {'error': e.toString()});
    }

    // Add sync event for UI notification
    await database.addSyncEvent(
      tenantId: _tenantId,
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
  Future<void> _fetchAndApplyServerVersion(OutboxData item) async {
    switch (item.entityType) {
      case 'field':
        await _fetchAndApplyFieldFromServer(item.entityId);
        break;
      case 'task':
        await _fetchAndApplyTaskFromServer(item.entityId);
        break;
      default:
        AppLogger.w('Unknown entity type for conflict resolution',
            tag: 'SyncEngine', data: {'entityType': item.entityType});
    }
  }

  /// Fetch and apply field data from server
  Future<void> _fetchAndApplyFieldFromServer(String fieldId) async {
    try {
      final response = await _apiClient.get(
        '/api/v1/fields/$fieldId',
        queryParameters: {'tenant_id': _tenantId},
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
            'tenant_id': props['tenant_id'] ?? _tenantId,
            'farm_id': props['farm_id'],
            'name': props['name'],
            'crop_type': props['crop_type'],
            'geometry': response['geometry'],
            'area_hectares': props['area_hectares'],
            'status': props['status'],
            'ndvi_current': props['ndvi_current'],
            'ndvi_updated_at': props['ndvi_updated_at'],
            'etag': props['etag'],
            'created_at':
                props['created_at'] ?? DateTime.now().toIso8601String(),
            'updated_at':
                props['updated_at'] ?? DateTime.now().toIso8601String(),
          };
        } else {
          fieldData = response;
        }

        await database.upsertFieldsFromServer([fieldData]);
        AppLogger.i('Server field version applied',
            tag: 'SyncEngine', data: {'fieldId': fieldId});
      }
    } catch (e) {
      AppLogger.e('Failed to fetch field from server',
          tag: 'SyncEngine', data: {'fieldId': fieldId, 'error': e.toString()});
      rethrow;
    }
  }

  /// Fetch and apply task data from server
  Future<void> _fetchAndApplyTaskFromServer(String taskId) async {
    try {
      final response = await _apiClient.get(
        '/api/v1/tasks/$taskId',
        queryParameters: {'tenant_id': _tenantId},
      );

      if (response is Map<String, dynamic>) {
        await database.upsertTasksFromServer([response]);
        AppLogger.i('Server task version applied',
            tag: 'SyncEngine', data: {'taskId': taskId});
      }
    } catch (e) {
      AppLogger.e('Failed to fetch task from server',
          tag: 'SyncEngine', data: {'taskId': taskId, 'error': e.toString()});
      rethrow;
    }
  }

  /// Get Arabic entity type name
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

  /// Pull latest data from server with circuit breaker
  /// Pulls both tasks and fields for comprehensive offline-first sync
  Future<PullResult> _pullFromServer() async {
    int count = 0;
    int fieldsCount = 0;
    int tasksCount = 0;

    // Pull fields
    fieldsCount = await _pullFields();
    count += fieldsCount;

    // Pull tasks
    tasksCount = await _pullTasks();
    count += tasksCount;

    AppLogger.d('Pull from server completed', tag: 'SyncEngine', data: {
      'fields': fieldsCount,
      'tasks': tasksCount,
      'total': count,
    });

    return PullResult(
        count: count, fieldsCount: fieldsCount, tasksCount: tasksCount);
  }

  /// Pull fields from server
  Future<int> _pullFields() async {
    const fieldsEndpoint = '/api/v1/fields';

    // Check if fields endpoint can be accessed
    if (!_retryTracker.canRetryNow(fieldsEndpoint)) {
      final status = _retryTracker.getEndpointStatus(fieldsEndpoint);
      AppLogger.d('Skipping fields pull - endpoint in backoff',
          tag: 'SyncEngine',
          data: {
            'endpoint': fieldsEndpoint,
            'status': status.statusDescription
          });
      return 0;
    }

    try {
      final fieldsResponse = await _apiClient.get(
        fieldsEndpoint,
        queryParameters: {'tenant_id': _tenantId},
      );

      if (fieldsResponse is Map && fieldsResponse['features'] is List) {
        // GeoJSON FeatureCollection response
        final features = fieldsResponse['features'] as List;
        final fieldMaps = features.map((feature) {
          final props = (feature as Map<String, dynamic>)['properties']
              as Map<String, dynamic>;
          return {
            'id': feature['id'] ?? props['local_id'],
            'remote_id': feature['id'],
            'tenant_id': props['tenant_id'] ?? _tenantId,
            'farm_id': props['farm_id'],
            'name': props['name'],
            'crop_type': props['crop_type'],
            'geometry': feature['geometry'],
            'area_hectares': props['area_hectares'],
            'status': props['status'],
            'ndvi_current': props['ndvi_current'],
            'ndvi_updated_at': props['ndvi_updated_at'],
            'etag': props['etag'],
            'created_at':
                props['created_at'] ?? DateTime.now().toIso8601String(),
            'updated_at':
                props['updated_at'] ?? DateTime.now().toIso8601String(),
          };
        }).toList();

        await database
            .upsertFieldsFromServer(fieldMaps.cast<Map<String, dynamic>>());
        _retryTracker.recordSuccess(fieldsEndpoint);
        return fieldMaps.length;
      } else if (fieldsResponse is List) {
        // Array response
        await database.upsertFieldsFromServer(
          fieldsResponse.cast<Map<String, dynamic>>(),
        );
        _retryTracker.recordSuccess(fieldsEndpoint);
        return fieldsResponse.length;
      }

      _retryTracker.recordSuccess(fieldsEndpoint);
      return 0;
    } catch (e) {
      AppLogger.w('Failed to pull fields',
          tag: 'SyncEngine', data: {'error': e.toString()});
      final currentRetry = _retryTracker.getRetryCount(fieldsEndpoint);
      _retryTracker.recordFailure(fieldsEndpoint, currentRetry + 1);

      if (e.toString().contains('RateLimitException') ||
          e.toString().contains('429')) {
        rethrow;
      }
      return 0;
    }
  }

  /// Pull tasks from server
  Future<int> _pullTasks() async {
    const tasksEndpoint = '/api/v1/tasks';

    // Check if tasks endpoint can be accessed
    if (!_retryTracker.canRetryNow(tasksEndpoint)) {
      final status = _retryTracker.getEndpointStatus(tasksEndpoint);
      AppLogger.d('Skipping tasks pull - endpoint in backoff',
          tag: 'SyncEngine',
          data: {
            'endpoint': tasksEndpoint,
            'status': status.statusDescription
          });
      return 0;
    }

    try {
      final tasksResponse = await _apiClient.get(
        tasksEndpoint,
        queryParameters: {'tenant_id': _tenantId},
      );

      if (tasksResponse is List) {
        await database.upsertTasksFromServer(
          tasksResponse.cast<Map<String, dynamic>>(),
        );
        _retryTracker.recordSuccess(tasksEndpoint);
        return tasksResponse.length;
      }

      _retryTracker.recordSuccess(tasksEndpoint);
      return 0;
    } catch (e) {
      AppLogger.w('Failed to pull tasks',
          tag: 'SyncEngine', data: {'error': e.toString()});
      final currentRetry = _retryTracker.getRetryCount(tasksEndpoint);
      _retryTracker.recordFailure(tasksEndpoint, currentRetry + 1);

      if (e.toString().contains('RateLimitException') ||
          e.toString().contains('429')) {
        rethrow;
      }
      return 0;
    }
  }

  /// Force refresh from server
  Future<void> forceRefresh() async {
    if (!await _networkStatus.checkOnline()) {
      throw Exception('No internet connection');
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

  /// Emit current backoff status for UI feedback
  void _emitBackoffStatus() {
    final endpointStatuses = _retryTracker.getAllEndpointStatuses();

    // Find endpoints with backoff active
    final backoffEndpoints = endpointStatuses.entries
        .where((e) =>
            !e.value.canRetry || e.value.circuitState != CircuitState.closed)
        .map((e) => e.value)
        .toList();

    if (backoffEndpoints.isEmpty) {
      _backoffStatusController.add(BackoffStatus.idle());
    } else {
      _backoffStatusController.add(BackoffStatus(
        isBackoffActive: true,
        affectedEndpoints: backoffEndpoints,
        totalEndpointsInBackoff: backoffEndpoints.length,
      ));
    }
  }

  /// Get current backoff status for all endpoints
  Map<String, EndpointStatus> getBackoffStatuses() {
    return _retryTracker.getAllEndpointStatuses();
  }

  /// Reset backoff for specific endpoint
  void resetEndpointBackoff(String endpoint) {
    _retryTracker.resetEndpoint(endpoint);
    _emitBackoffStatus();
  }

  /// Reset all backoff trackers
  void resetAllBackoff() {
    _retryTracker.resetAll();
    _consecutiveFailures = 0;
    _emitBackoffStatus();
  }

  /// Get sync statistics
  SyncStatistics getStatistics() {
    final backoffStatuses = _retryTracker.getAllEndpointStatuses();
    final unhealthyEndpoints =
        backoffStatuses.values.where((s) => !s.isHealthy).length;

    return SyncStatistics(
      consecutiveFailures: _consecutiveFailures,
      lastSuccessfulSync: _lastSuccessfulSync,
      isSyncing: _isSyncing,
      unhealthyEndpoints: unhealthyEndpoints,
    );
  }

  /// Get rate limit status for sync endpoints
  RateLimitStatus getSyncRateLimitStatus() {
    return _apiClient.getRateLimitStatus('sync');
  }

  /// Calculate exponential backoff duration after repeated sync failures.
  /// Starts after 3 failures, doubles each time, capped at 5 minutes.
  Duration _calculateBackoff(int failures) {
    final exponent = (failures - 3).clamp(0, 10);
    final seconds = (1 << exponent);
    final capped = seconds.clamp(1, 300);
    return Duration(seconds: capped);
  }

  void dispose() {
    stop();
    _networkStatus.dispose();
    _syncStatusController.close();
    _backoffStatusController.close();
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
  final int skipped;

  OutboxResult({
    required this.processed,
    required this.failed,
    this.conflicts = 0,
    this.skipped = 0,
  });

  @override
  String toString() {
    return 'OutboxResult(processed: $processed, failed: $failed, '
        'conflicts: $conflicts, skipped: $skipped)';
  }
}

/// Pull result with breakdown by entity type
class PullResult {
  final int count;
  final int fieldsCount;
  final int tasksCount;

  PullResult({
    required this.count,
    this.fieldsCount = 0,
    this.tasksCount = 0,
  });

  @override
  String toString() =>
      'PullResult(total: $count, fields: $fieldsCount, tasks: $tasksCount)';
}

/// Internal item processing result
enum _ItemResult { success, conflict }

/// Sync statistics with backoff information
class SyncStatistics {
  final int consecutiveFailures;
  final DateTime? lastSuccessfulSync;
  final bool isSyncing;
  final int unhealthyEndpoints;

  SyncStatistics({
    required this.consecutiveFailures,
    required this.lastSuccessfulSync,
    required this.isSyncing,
    this.unhealthyEndpoints = 0,
  });

  Duration? get timeSinceLastSync {
    if (lastSuccessfulSync == null) return null;
    return DateTime.now().difference(lastSuccessfulSync!);
  }

  bool get isHealthy => consecutiveFailures < 3 && unhealthyEndpoints == 0;

  @override
  String toString() {
    return 'SyncStatistics(failures: $consecutiveFailures, '
        'lastSync: ${timeSinceLastSync?.inMinutes ?? "never"} min ago, '
        'syncing: $isSyncing, unhealthyEndpoints: $unhealthyEndpoints, '
        'healthy: $isHealthy)';
  }
}

/// Backoff status for UI feedback
class BackoffStatus {
  final bool isBackoffActive;
  final List<EndpointStatus> affectedEndpoints;
  final int totalEndpointsInBackoff;

  BackoffStatus({
    required this.isBackoffActive,
    this.affectedEndpoints = const [],
    this.totalEndpointsInBackoff = 0,
  });

  factory BackoffStatus.idle() {
    return BackoffStatus(
      isBackoffActive: false,
      affectedEndpoints: [],
      totalEndpointsInBackoff: 0,
    );
  }

  /// Get shortest time until next retry across all endpoints
  Duration? get nextRetryIn {
    if (affectedEndpoints.isEmpty) return null;

    final durations = affectedEndpoints
        .map((e) => e.timeUntilRetry)
        .where((d) => d != null)
        .cast<Duration>()
        .toList();

    if (durations.isEmpty) return null;

    durations.sort((a, b) => a.inMilliseconds.compareTo(b.inMilliseconds));
    return durations.first;
  }

  /// Get number of endpoints in each circuit state
  Map<CircuitState, int> get circuitStateCounts {
    final counts = <CircuitState, int>{
      CircuitState.closed: 0,
      CircuitState.open: 0,
      CircuitState.halfOpen: 0,
    };

    for (final endpoint in affectedEndpoints) {
      counts[endpoint.circuitState] = (counts[endpoint.circuitState] ?? 0) + 1;
    }

    return counts;
  }

  /// Get human-readable status message
  String get statusMessage {
    if (!isBackoffActive) {
      return 'All endpoints healthy';
    }

    final counts = circuitStateCounts;
    final messages = <String>[];

    if (counts[CircuitState.open]! > 0) {
      messages.add('${counts[CircuitState.open]} circuit(s) open');
    }
    if (counts[CircuitState.halfOpen]! > 0) {
      messages.add('${counts[CircuitState.halfOpen]} testing recovery');
    }

    final nextRetry = nextRetryIn;
    if (nextRetry != null) {
      messages.add('next retry in ${nextRetry.inSeconds}s');
    }

    return messages.isEmpty ? 'Backoff active' : messages.join(', ');
  }

  @override
  String toString() {
    return 'BackoffStatus(active: $isBackoffActive, '
        'endpoints: $totalEndpointsInBackoff, '
        'message: $statusMessage)';
  }
}
