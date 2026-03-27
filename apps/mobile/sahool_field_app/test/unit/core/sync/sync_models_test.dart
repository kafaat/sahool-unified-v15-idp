import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/sync/sync_engine.dart';
import 'package:sahool_field_app/core/utils/retry_policy.dart';

/// Sync Models Unit Tests
/// اختبارات وحدات نماذج المزامنة
///
/// Tests for SyncResult, OutboxResult, PullResult, SyncStatistics,
/// BackoffStatus, and SyncStatus data models.
void main() {
  // ===========================================================================
  // SyncStatus enum
  // ===========================================================================
  group('SyncStatus', () {
    test('has all expected values', () {
      expect(SyncStatus.values, hasLength(3));
      expect(
        SyncStatus.values,
        containsAll([
          SyncStatus.idle,
          SyncStatus.syncing,
          SyncStatus.error,
        ]),
      );
    });
  });

  // ===========================================================================
  // SyncResult
  // ===========================================================================
  group('SyncResult', () {
    test('should create successful result with defaults', () {
      final result = SyncResult(success: true);

      expect(result.success, isTrue);
      expect(result.message, isNull);
      expect(result.uploaded, 0);
      expect(result.downloaded, 0);
    });

    test('should create successful result with counts', () {
      final result = SyncResult(
        success: true,
        uploaded: 5,
        downloaded: 10,
      );

      expect(result.success, isTrue);
      expect(result.uploaded, 5);
      expect(result.downloaded, 10);
    });

    test('should create failure result with message', () {
      final result = SyncResult(
        success: false,
        message: 'No network connection',
      );

      expect(result.success, isFalse);
      expect(result.message, 'No network connection');
      expect(result.uploaded, 0);
      expect(result.downloaded, 0);
    });

    test('should create failure result with Arabic message', () {
      final result = SyncResult(
        success: false,
        message: 'لا يوجد اتصال بالشبكة',
      );

      expect(result.success, isFalse);
      expect(result.message, 'لا يوجد اتصال بالشبكة');
    });

    test('should create result with all fields populated', () {
      final result = SyncResult(
        success: true,
        message: 'Sync completed',
        uploaded: 3,
        downloaded: 7,
      );

      expect(result.success, isTrue);
      expect(result.message, 'Sync completed');
      expect(result.uploaded, 3);
      expect(result.downloaded, 7);
    });
  });

  // ===========================================================================
  // OutboxResult
  // ===========================================================================
  group('OutboxResult', () {
    test('should create with required fields', () {
      final result = OutboxResult(
        processed: 5,
        failed: 1,
      );

      expect(result.processed, 5);
      expect(result.failed, 1);
      expect(result.conflicts, 0);
      expect(result.skipped, 0);
    });

    test('should create with all fields', () {
      final result = OutboxResult(
        processed: 10,
        failed: 2,
        conflicts: 1,
        skipped: 3,
      );

      expect(result.processed, 10);
      expect(result.failed, 2);
      expect(result.conflicts, 1);
      expect(result.skipped, 3);
    });

    test('toString should include all fields', () {
      final result = OutboxResult(
        processed: 10,
        failed: 2,
        conflicts: 1,
        skipped: 3,
      );

      final str = result.toString();

      expect(str, contains('processed: 10'));
      expect(str, contains('failed: 2'));
      expect(str, contains('conflicts: 1'));
      expect(str, contains('skipped: 3'));
      expect(str, startsWith('OutboxResult('));
    });

    test('toString should work with zero values', () {
      final result = OutboxResult(
        processed: 0,
        failed: 0,
        conflicts: 0,
        skipped: 0,
      );

      final str = result.toString();

      expect(str, contains('processed: 0'));
      expect(str, contains('failed: 0'));
    });
  });

  // ===========================================================================
  // PullResult
  // ===========================================================================
  group('PullResult', () {
    test('should create with count only', () {
      final result = PullResult(count: 15);

      expect(result.count, 15);
      expect(result.fieldsCount, 0);
      expect(result.tasksCount, 0);
    });

    test('should create with breakdown', () {
      final result = PullResult(
        count: 20,
        fieldsCount: 12,
        tasksCount: 8,
      );

      expect(result.count, 20);
      expect(result.fieldsCount, 12);
      expect(result.tasksCount, 8);
    });

    test('toString should include all counts', () {
      final result = PullResult(
        count: 20,
        fieldsCount: 12,
        tasksCount: 8,
      );

      final str = result.toString();

      expect(str, contains('total: 20'));
      expect(str, contains('fields: 12'));
      expect(str, contains('tasks: 8'));
    });
  });

  // ===========================================================================
  // SyncStatistics
  // ===========================================================================
  group('SyncStatistics', () {
    test('isHealthy should return true when fresh (no failures, no unhealthy endpoints)', () {
      final stats = SyncStatistics(
        consecutiveFailures: 0,
        lastSuccessfulSync: DateTime.now(),
        isSyncing: false,
        unhealthyEndpoints: 0,
      );

      expect(stats.isHealthy, isTrue);
    });

    test('isHealthy should return true with 1-2 consecutive failures', () {
      final stats = SyncStatistics(
        consecutiveFailures: 2,
        lastSuccessfulSync: DateTime.now(),
        isSyncing: false,
        unhealthyEndpoints: 0,
      );

      expect(stats.isHealthy, isTrue);
    });

    test('isHealthy should return false when consecutiveFailures >= 3', () {
      final stats = SyncStatistics(
        consecutiveFailures: 3,
        lastSuccessfulSync: DateTime.now(),
        isSyncing: false,
        unhealthyEndpoints: 0,
      );

      expect(stats.isHealthy, isFalse);
    });

    test('isHealthy should return false when unhealthyEndpoints > 0', () {
      final stats = SyncStatistics(
        consecutiveFailures: 0,
        lastSuccessfulSync: DateTime.now(),
        isSyncing: false,
        unhealthyEndpoints: 1,
      );

      expect(stats.isHealthy, isFalse);
    });

    test('isHealthy should return false when both failures and unhealthy endpoints', () {
      final stats = SyncStatistics(
        consecutiveFailures: 5,
        lastSuccessfulSync: null,
        isSyncing: false,
        unhealthyEndpoints: 2,
      );

      expect(stats.isHealthy, isFalse);
    });

    test('timeSinceLastSync should return null when never synced', () {
      final stats = SyncStatistics(
        consecutiveFailures: 0,
        lastSuccessfulSync: null,
        isSyncing: false,
      );

      expect(stats.timeSinceLastSync, isNull);
    });

    test('timeSinceLastSync should return a positive duration when synced before', () {
      final stats = SyncStatistics(
        consecutiveFailures: 0,
        lastSuccessfulSync: DateTime.now().subtract(const Duration(minutes: 5)),
        isSyncing: false,
      );

      expect(stats.timeSinceLastSync, isNotNull);
      // Should be approximately 5 minutes (with small tolerance)
      expect(stats.timeSinceLastSync!.inMinutes, greaterThanOrEqualTo(4));
      expect(stats.timeSinceLastSync!.inMinutes, lessThanOrEqualTo(6));
    });

    test('isSyncing should reflect current sync state', () {
      final syncing = SyncStatistics(
        consecutiveFailures: 0,
        lastSuccessfulSync: null,
        isSyncing: true,
      );

      final idle = SyncStatistics(
        consecutiveFailures: 0,
        lastSuccessfulSync: null,
        isSyncing: false,
      );

      expect(syncing.isSyncing, isTrue);
      expect(idle.isSyncing, isFalse);
    });

    test('toString should include all fields', () {
      final stats = SyncStatistics(
        consecutiveFailures: 2,
        lastSuccessfulSync: null,
        isSyncing: true,
        unhealthyEndpoints: 1,
      );

      final str = stats.toString();

      expect(str, contains('failures: 2'));
      expect(str, contains('syncing: true'));
      expect(str, contains('unhealthyEndpoints: 1'));
      expect(str, contains('healthy: false'));
    });

    test('toString should show "never" when lastSync is null', () {
      final stats = SyncStatistics(
        consecutiveFailures: 0,
        lastSuccessfulSync: null,
        isSyncing: false,
      );

      final str = stats.toString();
      expect(str, contains('never'));
    });

    test('unhealthyEndpoints defaults to 0', () {
      final stats = SyncStatistics(
        consecutiveFailures: 0,
        lastSuccessfulSync: null,
        isSyncing: false,
      );

      expect(stats.unhealthyEndpoints, 0);
    });
  });

  // ===========================================================================
  // BackoffStatus
  // ===========================================================================
  group('BackoffStatus', () {
    test('idle factory should create inactive status', () {
      final status = BackoffStatus.idle();

      expect(status.isBackoffActive, isFalse);
      expect(status.affectedEndpoints, isEmpty);
      expect(status.totalEndpointsInBackoff, 0);
    });

    test('should create active backoff status', () {
      final status = BackoffStatus(
        isBackoffActive: true,
        affectedEndpoints: [
          EndpointStatus(
            endpoint: '/api/v1/fields',
            circuitState: CircuitState.open,
            retryCount: 3,
            failureCount: 5,
            canRetry: false,
          ),
        ],
        totalEndpointsInBackoff: 1,
      );

      expect(status.isBackoffActive, isTrue);
      expect(status.affectedEndpoints, hasLength(1));
      expect(status.totalEndpointsInBackoff, 1);
    });

    test('statusMessage should return "All endpoints healthy" when idle', () {
      final status = BackoffStatus.idle();
      expect(status.statusMessage, 'All endpoints healthy');
    });

    test('statusMessage should indicate open circuits when backoff active', () {
      final status = BackoffStatus(
        isBackoffActive: true,
        affectedEndpoints: [
          EndpointStatus(
            endpoint: '/api/v1/fields',
            circuitState: CircuitState.open,
            retryCount: 3,
            failureCount: 5,
            canRetry: false,
          ),
        ],
        totalEndpointsInBackoff: 1,
      );

      expect(status.statusMessage, contains('circuit(s) open'));
    });

    test('statusMessage should indicate half-open circuits testing recovery', () {
      final status = BackoffStatus(
        isBackoffActive: true,
        affectedEndpoints: [
          EndpointStatus(
            endpoint: '/api/v1/tasks',
            circuitState: CircuitState.halfOpen,
            retryCount: 2,
            failureCount: 3,
            canRetry: true,
          ),
        ],
        totalEndpointsInBackoff: 1,
      );

      expect(status.statusMessage, contains('testing recovery'));
    });

    test('statusMessage should return "Backoff active" when backoff active but no special state', () {
      // When all affected endpoints are in closed state (which means the
      // circuitStateCounts for open and halfOpen are both 0) and no nextRetryIn,
      // the message list is empty, so fallback is 'Backoff active'.
      final status = BackoffStatus(
        isBackoffActive: true,
        affectedEndpoints: [
          EndpointStatus(
            endpoint: '/api/v1/data',
            circuitState: CircuitState.closed,
            retryCount: 1,
            failureCount: 1,
            canRetry: false,
          ),
        ],
        totalEndpointsInBackoff: 1,
      );

      expect(status.statusMessage, 'Backoff active');
    });

    test('nextRetryIn should return null when no affected endpoints', () {
      final status = BackoffStatus.idle();
      expect(status.nextRetryIn, isNull);
    });

    test('nextRetryIn should return shortest duration across endpoints', () {
      final status = BackoffStatus(
        isBackoffActive: true,
        affectedEndpoints: [
          EndpointStatus(
            endpoint: '/api/v1/fields',
            circuitState: CircuitState.open,
            retryCount: 3,
            failureCount: 5,
            timeUntilRetry: const Duration(seconds: 30),
            canRetry: false,
          ),
          EndpointStatus(
            endpoint: '/api/v1/tasks',
            circuitState: CircuitState.open,
            retryCount: 2,
            failureCount: 3,
            timeUntilRetry: const Duration(seconds: 10),
            canRetry: false,
          ),
        ],
        totalEndpointsInBackoff: 2,
      );

      expect(status.nextRetryIn, const Duration(seconds: 10));
    });

    test('nextRetryIn should return null when all endpoints have null timeUntilRetry', () {
      final status = BackoffStatus(
        isBackoffActive: true,
        affectedEndpoints: [
          EndpointStatus(
            endpoint: '/api/v1/fields',
            circuitState: CircuitState.open,
            retryCount: 3,
            failureCount: 5,
            canRetry: false,
          ),
        ],
        totalEndpointsInBackoff: 1,
      );

      expect(status.nextRetryIn, isNull);
    });

    test('circuitStateCounts should count endpoints per circuit state', () {
      final status = BackoffStatus(
        isBackoffActive: true,
        affectedEndpoints: [
          EndpointStatus(
            endpoint: '/api/v1/fields',
            circuitState: CircuitState.open,
            retryCount: 3,
            failureCount: 5,
            canRetry: false,
          ),
          EndpointStatus(
            endpoint: '/api/v1/tasks',
            circuitState: CircuitState.open,
            retryCount: 2,
            failureCount: 3,
            canRetry: false,
          ),
          EndpointStatus(
            endpoint: '/api/v1/data',
            circuitState: CircuitState.halfOpen,
            retryCount: 1,
            failureCount: 2,
            canRetry: true,
          ),
        ],
        totalEndpointsInBackoff: 3,
      );

      final counts = status.circuitStateCounts;
      expect(counts[CircuitState.open], 2);
      expect(counts[CircuitState.halfOpen], 1);
      expect(counts[CircuitState.closed], 0);
    });

    test('toString should include key fields', () {
      final status = BackoffStatus(
        isBackoffActive: true,
        totalEndpointsInBackoff: 2,
        affectedEndpoints: [
          EndpointStatus(
            endpoint: '/api/v1/fields',
            circuitState: CircuitState.open,
            retryCount: 3,
            failureCount: 5,
            canRetry: false,
          ),
          EndpointStatus(
            endpoint: '/api/v1/tasks',
            circuitState: CircuitState.open,
            retryCount: 2,
            failureCount: 3,
            canRetry: false,
          ),
        ],
      );

      final str = status.toString();
      expect(str, contains('active: true'));
      expect(str, contains('endpoints: 2'));
    });

    test('affectedEndpoints defaults to empty list', () {
      final status = BackoffStatus(isBackoffActive: false);
      expect(status.affectedEndpoints, isEmpty);
    });
  });
}
