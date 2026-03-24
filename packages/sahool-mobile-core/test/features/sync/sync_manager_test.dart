
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_mobile_core/core/offline/offline_sync_engine.dart';
import 'package:sahool_mobile_core/core/utils/retry_policy.dart';

import 'sync_mocks.dart';

/// Sync Manager Tests
/// اختبارات مدير المزامنة
///
/// Tests for:
/// - Sync engine operations
/// - Background sync
/// - Retry logic with exponential backoff
/// - Circuit breaker pattern
/// - Partial sync failures
/// - Backoff status tracking

void main() {
  setUpAll(() {
    registerSyncFallbackValues();
  });

  group('SyncStatus', () {
    test('should have all expected status values', () {
      expect(SyncStatus.values, contains(SyncStatus.idle));
      expect(SyncStatus.values, contains(SyncStatus.syncing));
      expect(SyncStatus.values, contains(SyncStatus.success));
      expect(SyncStatus.values, contains(SyncStatus.partialSuccess));
      expect(SyncStatus.values, contains(SyncStatus.error));
      expect(SyncStatus.values, contains(SyncStatus.offline));
    });
  });

  group('SyncOperation', () {
    test('should have all expected operations', () {
      expect(SyncOperation.values, contains(SyncOperation.create));
      expect(SyncOperation.values, contains(SyncOperation.update));
      expect(SyncOperation.values, contains(SyncOperation.delete));
    });
  });

  group('SyncPriority', () {
    test('should have all expected priorities', () {
      expect(SyncPriority.values, contains(SyncPriority.low));
      expect(SyncPriority.values, contains(SyncPriority.normal));
      expect(SyncPriority.values, contains(SyncPriority.high));
      expect(SyncPriority.values, contains(SyncPriority.critical));
    });

    test('priorities should be in correct order', () {
      expect(SyncPriority.low.index, lessThan(SyncPriority.normal.index));
      expect(SyncPriority.normal.index, lessThan(SyncPriority.high.index));
      expect(SyncPriority.high.index, lessThan(SyncPriority.critical.index));
    });
  });

  group('OutboxStatus', () {
    test('should have all expected statuses', () {
      expect(OutboxStatus.values, contains(OutboxStatus.pending));
      expect(OutboxStatus.values, contains(OutboxStatus.processing));
      expect(OutboxStatus.values, contains(OutboxStatus.completed));
      expect(OutboxStatus.values, contains(OutboxStatus.failed));
    });
  });

  group('OutboxEntry', () {
    test('should create valid entry', () {
      final entry = OutboxEntry(
        id: 'entry_001',
        entityType: 'field',
        entityId: 'field_001',
        operation: SyncOperation.update,
        data: {'name': 'Test'},
        priority: SyncPriority.normal,
        createdAt: DateTime.now(),
        status: OutboxStatus.pending,
      );

      expect(entry.id, equals('entry_001'));
      expect(entry.entityType, equals('field'));
      expect(entry.operation, equals(SyncOperation.update));
      expect(entry.status, equals(OutboxStatus.pending));
      expect(entry.retryCount, equals(0));
    });

    test('copyWith should create new instance with updated values', () {
      final original = OutboxEntry(
        id: 'entry_001',
        entityType: 'field',
        entityId: 'field_001',
        operation: SyncOperation.update,
        data: {'name': 'Test'},
        priority: SyncPriority.normal,
        createdAt: DateTime.now(),
        status: OutboxStatus.pending,
      );

      final updated = original.copyWith(
        status: OutboxStatus.processing,
        retryCount: 1,
      );

      expect(updated.id, equals(original.id));
      expect(updated.status, equals(OutboxStatus.processing));
      expect(updated.retryCount, equals(1));
      expect(original.status, equals(OutboxStatus.pending)); // Original unchanged
    });

    test('toJson and fromJson should be symmetric', () {
      final original = OutboxEntry(
        id: 'entry_001',
        entityType: 'field',
        entityId: 'field_001',
        operation: SyncOperation.update,
        data: {'name': 'Test', 'area': 100.0},
        previousData: {'name': 'Old', 'area': 50.0},
        priority: SyncPriority.high,
        createdAt: DateTime.parse('2024-01-15T10:30:00Z'),
        status: OutboxStatus.pending,
        retryCount: 2,
        lastError: 'Network error',
      );

      final json = original.toJson();
      final restored = OutboxEntry.fromJson(json);

      expect(restored.id, equals(original.id));
      expect(restored.entityType, equals(original.entityType));
      expect(restored.operation, equals(original.operation));
      expect(restored.priority, equals(original.priority));
      expect(restored.status, equals(original.status));
      expect(restored.retryCount, equals(original.retryCount));
      expect(restored.lastError, equals(original.lastError));
    });
  });

  group('SyncResult', () {
    test('should create success result', () {
      const result = SyncResult(
        success: true,
        syncedCount: 5,
        message: 'Synced 5 items',
      );

      expect(result.success, isTrue);
      expect(result.syncedCount, equals(5));
      expect(result.failedCount, equals(0));
    });

    test('should create failure result', () {
      const result = SyncResult(
        success: false,
        syncedCount: 2,
        failedCount: 3,
        errors: ['Error 1', 'Error 2', 'Error 3'],
        message: 'Partial failure',
      );

      expect(result.success, isFalse);
      expect(result.syncedCount, equals(2));
      expect(result.failedCount, equals(3));
      expect(result.errors.length, equals(3));
    });
  });

  group('OutboxStats', () {
    test('should calculate totalCount correctly', () {
      const stats = OutboxStats(
        pendingCount: 5,
        failedCount: 2,
        completedCount: 10,
        isSyncing: false,
        lastSyncStatus: SyncStatus.idle,
      );

      expect(stats.totalCount, equals(17)); // 5 + 2 + 10
    });

    test('hasPending should return correct value', () {
      const statsWithPending = OutboxStats(
        pendingCount: 5,
        failedCount: 0,
        completedCount: 0,
        isSyncing: false,
        lastSyncStatus: SyncStatus.idle,
      );
      expect(statsWithPending.hasPending, isTrue);

      const statsNoPending = OutboxStats(
        pendingCount: 0,
        failedCount: 0,
        completedCount: 5,
        isSyncing: false,
        lastSyncStatus: SyncStatus.idle,
      );
      expect(statsNoPending.hasPending, isFalse);
    });

    test('hasFailed should return correct value', () {
      const statsWithFailed = OutboxStats(
        pendingCount: 0,
        failedCount: 3,
        completedCount: 0,
        isSyncing: false,
        lastSyncStatus: SyncStatus.error,
      );
      expect(statsWithFailed.hasFailed, isTrue);
    });
  });

  group('ExponentialBackoff', () {
    test('should calculate correct delays', () {
      final backoff = ExponentialBackoff(
        initialDelayMs: 1000,
        multiplier: 2.0,
        maxDelayMs: 300000,
        maxRetries: 5,
        enableJitter: false,
      );

      expect(backoff.calculateDelay(0), equals(1000)); // 1s
      expect(backoff.calculateDelay(1), equals(2000)); // 2s
      expect(backoff.calculateDelay(2), equals(4000)); // 4s
      expect(backoff.calculateDelay(3), equals(8000)); // 8s
      expect(backoff.calculateDelay(4), equals(16000)); // 16s
    });

    test('should cap at max delay', () {
      final backoff = ExponentialBackoff(
        initialDelayMs: 1000,
        multiplier: 2.0,
        maxDelayMs: 5000,
        maxRetries: 10,
        enableJitter: false,
      );

      expect(backoff.calculateDelay(5), equals(5000)); // Capped at 5s
      expect(backoff.calculateDelay(10), equals(5000)); // Still capped
    });

    test('should add jitter when enabled', () {
      final backoff = ExponentialBackoff(
        initialDelayMs: 1000,
        multiplier: 2.0,
        maxDelayMs: 300000,
        maxRetries: 5,
        enableJitter: true,
      );

      final delays = List.generate(10, (_) => backoff.calculateDelay(2));

      // With jitter, delays should vary (base is 4000ms, jitter adds 0-25%)
      // Highly likely to have some variation (not guaranteed but probable)
      // At minimum, all should be >= base delay
      for (final delay in delays) {
        expect(delay, greaterThanOrEqualTo(4000));
        expect(delay, lessThanOrEqualTo(5000)); // 4000 * 1.25
      }
    });

    test('shouldRetry returns correct values', () {
      final backoff = ExponentialBackoff(maxRetries: 5);

      expect(backoff.shouldRetry(0), isTrue);
      expect(backoff.shouldRetry(4), isTrue);
      expect(backoff.shouldRetry(5), isFalse);
      expect(backoff.shouldRetry(10), isFalse);
    });

    test('getDelayDescription formats correctly', () {
      final backoff = ExponentialBackoff(
        initialDelayMs: 1000,
        multiplier: 2.0,
        maxDelayMs: 300000,
        enableJitter: false,
      );

      // Milliseconds
      expect(backoff.getDelayDescription(0), contains('1'));

      // Seconds
      final desc1 = backoff.getDelayDescription(1);
      expect(desc1.contains('2') || desc1.contains('s'), isTrue);

      // Minutes (for large delays)
      final backoffLong = ExponentialBackoff(
        initialDelayMs: 60000,
        multiplier: 2.0,
        enableJitter: false,
      );
      expect(backoffLong.getDelayDescription(1), contains('m'));
    });

    test('calculateNextRetryTime returns future time', () {
      final backoff = ExponentialBackoff(
        initialDelayMs: 1000,
        enableJitter: false,
      );

      final now = DateTime.now();
      final nextRetry = backoff.calculateNextRetryTime(0);

      expect(nextRetry.isAfter(now), isTrue);
      expect(
        nextRetry.difference(now).inMilliseconds,
        closeTo(1000, 100),
      );
    });
  });

  group('CircuitBreaker', () {
    late CircuitBreaker circuitBreaker;
    late DateTime fakeNow;

    setUp(() {
      fakeNow = DateTime(2026, 1, 1);
      circuitBreaker = CircuitBreaker(
        name: 'test-endpoint',
        failureThreshold: 3,
        openTimeout: const Duration(seconds: 30),
        halfOpenMaxAttempts: 2,
        clock: () => fakeNow,
      );
    });

    test('should start in closed state', () {
      expect(circuitBreaker.state, equals(CircuitState.closed));
      expect(circuitBreaker.canAttempt(), isTrue);
    });

    test('should remain closed below failure threshold', () {
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();

      expect(circuitBreaker.state, equals(CircuitState.closed));
      expect(circuitBreaker.failureCount, equals(2));
    });

    test('should open after reaching failure threshold', () {
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();

      expect(circuitBreaker.state, equals(CircuitState.open));
      expect(circuitBreaker.canAttempt(), isFalse);
    });

    test('should reset failure count on success', () {
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();
      circuitBreaker.recordSuccess();

      expect(circuitBreaker.failureCount, equals(0));
      expect(circuitBreaker.state, equals(CircuitState.closed));
    });

    test('should transition to half-open after timeout', () {
      // Open the circuit
      for (int i = 0; i < 3; i++) {
        circuitBreaker.recordFailure();
      }
      expect(circuitBreaker.state, equals(CircuitState.open));
      expect(circuitBreaker.canAttempt(), isFalse);

      // Advance fake clock past timeout
      fakeNow = fakeNow.add(const Duration(seconds: 31));

      // Should now allow attempts (half-open)
      expect(circuitBreaker.canAttempt(), isTrue);
      expect(circuitBreaker.state, equals(CircuitState.halfOpen));
    });

    test('should close on success in half-open state', () {
      // Open the circuit
      for (int i = 0; i < 3; i++) {
        circuitBreaker.recordFailure();
      }

      // Advance fake clock past timeout
      fakeNow = fakeNow.add(const Duration(seconds: 31));

      // Trigger half-open check
      circuitBreaker.canAttempt();

      // Success in half-open should close
      circuitBreaker.recordSuccess();

      expect(circuitBreaker.state, equals(CircuitState.closed));
    });

    test('should re-open on failures in half-open state', () {
      // Open the circuit
      for (int i = 0; i < 3; i++) {
        circuitBreaker.recordFailure();
      }

      // Advance fake clock past timeout
      fakeNow = fakeNow.add(const Duration(seconds: 31));

      // Trigger half-open
      circuitBreaker.canAttempt();

      // Fail in half-open
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();

      expect(circuitBreaker.state, equals(CircuitState.open));
    });

    test('reset should restore initial state', () {
      // Add some failures
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();
      circuitBreaker.recordFailure();

      expect(circuitBreaker.state, equals(CircuitState.open));

      // Reset
      circuitBreaker.reset();

      expect(circuitBreaker.state, equals(CircuitState.closed));
      expect(circuitBreaker.failureCount, equals(0));
      expect(circuitBreaker.canAttempt(), isTrue);
    });

    test('getStateDescription returns human-readable description', () {
      expect(circuitBreaker.getStateDescription(), equals('Normal'));

      for (int i = 0; i < 3; i++) {
        circuitBreaker.recordFailure();
      }
      expect(circuitBreaker.getStateDescription(), contains('Failed'));
    });
  });

  group('EndpointRetryTracker', () {
    late EndpointRetryTracker tracker;

    setUp(() {
      tracker = EndpointRetryTracker(
        backoffPolicy: ExponentialBackoff(
          initialDelayMs: 1000,
          multiplier: 2.0,
          maxDelayMs: 60000,
          maxRetries: 5,
          enableJitter: false,
        ),
      );
    });

    test('should allow retry for new endpoint', () {
      expect(tracker.canRetryNow('/api/v1/fields'), isTrue);
    });

    test('should track retry count per endpoint', () {
      tracker.recordFailure('/api/v1/fields', 1);

      expect(tracker.getRetryCount('/api/v1/fields'), equals(1));
      expect(tracker.getRetryCount('/api/v1/tasks'), equals(0));
    });

    test('should track different endpoints independently', () {
      tracker.recordFailure('/api/v1/fields', 1);
      tracker.recordFailure('/api/v1/fields', 2);
      tracker.recordFailure('/api/v1/tasks', 1);

      expect(tracker.getRetryCount('/api/v1/fields'), equals(2));
      expect(tracker.getRetryCount('/api/v1/tasks'), equals(1));
    });

    test('should reset counters on success', () {
      tracker.recordFailure('/api/v1/fields', 1);
      tracker.recordFailure('/api/v1/fields', 2);

      tracker.recordSuccess('/api/v1/fields');

      expect(tracker.getRetryCount('/api/v1/fields'), equals(0));
      expect(tracker.canRetryNow('/api/v1/fields'), isTrue);
    });

    test('should calculate next retry time', () {
      tracker.recordFailure('/api/v1/fields', 1);

      final nextRetry = tracker.getNextRetryTime('/api/v1/fields');

      expect(nextRetry, isNotNull);
      expect(nextRetry!.isAfter(DateTime.now()), isTrue);
    });

    test('should block retry during backoff period', () {
      tracker.recordFailure('/api/v1/fields', 1);

      // Immediately after failure, should not allow retry
      expect(tracker.canRetryNow('/api/v1/fields'), isFalse);
    });

    test('getTimeUntilRetry returns correct duration', () {
      tracker.recordFailure('/api/v1/fields', 0);

      final timeUntil = tracker.getTimeUntilRetry('/api/v1/fields');

      expect(timeUntil, isNotNull);
      expect(timeUntil!.inMilliseconds, greaterThan(0));
    });

    test('getAllEndpointStatuses returns all tracked endpoints', () {
      tracker.recordFailure('/api/v1/fields', 1);
      tracker.recordFailure('/api/v1/tasks', 1);

      final statuses = tracker.getAllEndpointStatuses();

      expect(statuses.containsKey('/api/v1/fields'), isTrue);
      expect(statuses.containsKey('/api/v1/tasks'), isTrue);
    });

    test('getEndpointStatus returns correct status', () {
      tracker.recordFailure('/api/v1/fields', 2);

      final status = tracker.getEndpointStatus('/api/v1/fields');

      expect(status.endpoint, equals('/api/v1/fields'));
      expect(status.retryCount, equals(2));
      expect(status.canRetry, isFalse); // In backoff
    });

    test('resetAll should clear all tracking data', () {
      tracker.recordFailure('/api/v1/fields', 1);
      tracker.recordFailure('/api/v1/tasks', 1);

      tracker.resetAll();

      expect(tracker.canRetryNow('/api/v1/fields'), isTrue);
      expect(tracker.canRetryNow('/api/v1/tasks'), isTrue);
      expect(tracker.getRetryCount('/api/v1/fields'), equals(0));
    });

    test('resetEndpoint should clear specific endpoint', () {
      tracker.recordFailure('/api/v1/fields', 1);
      tracker.recordFailure('/api/v1/tasks', 1);

      tracker.resetEndpoint('/api/v1/fields');

      expect(tracker.canRetryNow('/api/v1/fields'), isTrue);
      expect(tracker.canRetryNow('/api/v1/tasks'), isFalse); // Still in backoff
    });
  });

  group('EndpointStatus', () {
    test('isHealthy returns true for healthy endpoint', () {
      final status = EndpointStatus(
        endpoint: '/api/v1/fields',
        circuitState: CircuitState.closed,
        retryCount: 0,
        failureCount: 0,
        canRetry: true,
      );

      expect(status.isHealthy, isTrue);
    });

    test('isHealthy returns false when circuit is open', () {
      final status = EndpointStatus(
        endpoint: '/api/v1/fields',
        circuitState: CircuitState.open,
        retryCount: 3,
        failureCount: 5,
        canRetry: false,
      );

      expect(status.isHealthy, isFalse);
    });

    test('statusDescription returns correct description', () {
      // Healthy
      var status = EndpointStatus(
        endpoint: '/api/v1/fields',
        circuitState: CircuitState.closed,
        retryCount: 0,
        failureCount: 0,
        canRetry: true,
      );
      expect(status.statusDescription, equals('Healthy'));

      // Circuit Open
      status = EndpointStatus(
        endpoint: '/api/v1/fields',
        circuitState: CircuitState.open,
        retryCount: 3,
        failureCount: 5,
        canRetry: false,
      );
      expect(status.statusDescription, equals('Circuit Open'));

      // Testing
      status = EndpointStatus(
        endpoint: '/api/v1/fields',
        circuitState: CircuitState.halfOpen,
        retryCount: 1,
        failureCount: 3,
        canRetry: true,
      );
      expect(status.statusDescription, equals('Testing'));
    });
  });

  group('Partial Sync Failures', () {
    late MockSyncDatabase mockDb;

    setUp(() {
      mockDb = MockSyncDatabase();
    });

    tearDown(() {
      mockDb.reset();
    });

    test('should handle mixed success and failure', () async {
      // Queue 5 items
      final ids = <int>[];
      for (int i = 0; i < 5; i++) {
        final id = await mockDb.queueOutboxItem(
          tenantId: 'tenant_1',
          entityType: 'field',
          entityId: 'field_00$i',
          apiEndpoint: '/api/v1/fields/field_00$i',
          method: 'PUT',
          payload: '{}',
        );
        ids.add(id);
      }

      // Process: 3 succeed, 2 fail
      int successCount = 0;
      int failCount = 0;

      for (int i = 0; i < ids.length; i++) {
        if (i < 3) {
          await mockDb.markOutboxDone(ids[i]);
          successCount++;
        } else {
          await mockDb.bumpOutboxRetry(ids[i]);
          failCount++;
        }
      }

      final pending = await mockDb.getPendingOutbox();

      expect(successCount, equals(3));
      expect(failCount, equals(2));
      expect(pending.length, equals(2));
    });

    test('should track items exceeding max retries', () async {
      final id = await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{}',
      );

      // Simulate max retries (5)
      for (int i = 0; i < 5; i++) {
        await mockDb.bumpOutboxRetry(id);
      }

      final pending = await mockDb.getPendingOutbox();
      expect(pending.first.retryCount, equals(5));

      // Log that max retries exceeded
      await mockDb.logSync(
        type: 'outbox_max_retry',
        status: 'failed',
        message: 'Item $id exceeded max retries',
      );

      final logs = await mockDb.getRecentSyncLogs();
      expect(
        logs.any((log) => log['type'] == 'outbox_max_retry'),
        isTrue,
      );
    });

    test('should stop processing batch on too many failures', () async {
      // Queue 10 items
      final ids = <int>[];
      for (int i = 0; i < 10; i++) {
        final id = await mockDb.queueOutboxItem(
          tenantId: 'tenant_1',
          entityType: 'field',
          entityId: 'field_0$i',
          apiEndpoint: '/api/v1/fields/field_0$i',
          method: 'PUT',
          payload: '{}',
        );
        ids.add(id);
      }

      // Process with failure threshold of 3
      int successCount = 0;
      int failCount = 0;
      const failureThreshold = 3;

      for (final id in ids) {
        // Simulate 50% failure rate
        if (id % 2 == 0) {
          await mockDb.markOutboxDone(id);
          successCount++;
        } else {
          await mockDb.bumpOutboxRetry(id);
          failCount++;

          if (failCount >= failureThreshold) {
            break; // Stop processing batch
          }
        }
      }

      expect(failCount, equals(failureThreshold));
      expect(successCount, lessThan(ids.length - failureThreshold));
    });
  });

  group('Background Sync Simulation', () {
    late MockSyncDatabase mockDb;
    late MockNetworkStatus networkStatus;

    setUp(() {
      mockDb = MockSyncDatabase();
      networkStatus = MockNetworkStatus();
    });

    tearDown(() {
      mockDb.reset();
      networkStatus.dispose();
    });

    test('should not sync when offline', () async {
      networkStatus.setOnline(false);

      // Queue item
      await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{}',
      );

      // Simulate sync check
      if (networkStatus.isOnline) {
        // Would process here
        fail('Should not reach here when offline');
      }

      final pending = await mockDb.getPendingOutbox();
      expect(pending.length, equals(1));
    });

    test('should sync immediately when online', () async {
      networkStatus.setOnline(true);

      final id = await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{}',
      );

      // Simulate sync when online
      if (networkStatus.isOnline) {
        await mockDb.markOutboxDone(id);
      }

      final pending = await mockDb.getPendingOutbox();
      expect(pending.length, equals(0));
    });

    test('should log sync operations', () async {
      await mockDb.logSync(
        type: 'full_sync',
        status: 'started',
        message: 'Starting sync with 5 pending items',
      );

      await mockDb.logSync(
        type: 'full_sync',
        status: 'success',
        message: 'Uploaded: 5, Pulled: 10',
      );

      final logs = await mockDb.getRecentSyncLogs();
      expect(logs.length, equals(2));
      expect(logs.first['status'], equals('started'));
      expect(logs.last['status'], equals('success'));
    });
  });

  group('Retry Logic Integration', () {
    test('should implement proper exponential backoff sequence', () {
      final backoff = ExponentialBackoff(
        initialDelayMs: 1000,
        multiplier: 2.0,
        maxDelayMs: 300000,
        maxRetries: 5,
        enableJitter: false,
      );

      // Verify exponential sequence
      final expectedDelays = [1000, 2000, 4000, 8000, 16000];

      for (int i = 0; i < expectedDelays.length; i++) {
        expect(backoff.calculateDelay(i), equals(expectedDelays[i]));
      }
    });

    test('should combine backoff with circuit breaker', () {
      final tracker = EndpointRetryTracker(
        backoffPolicy: ExponentialBackoff(
          initialDelayMs: 1000,
          multiplier: 2.0,
          maxDelayMs: 60000,
          enableJitter: false,
        ),
      );

      const endpoint = '/api/v1/fields';

      // Record failures until circuit opens
      for (int i = 0; i < 5; i++) {
        tracker.recordFailure(endpoint, i);
      }

      final status = tracker.getEndpointStatus(endpoint);

      // Circuit should be open
      expect(status.circuitState, equals(CircuitState.open));
      expect(status.canRetry, isFalse);
    });
  });

  group('SyncResult from OfflineSyncEngine', () {
    test('should create valid SyncResult with all fields', () {
      const result = SyncResult(
        success: true,
        syncedCount: 5,
        failedCount: 1,
        errors: ['Error syncing field_006'],
        message: 'Synced 5 items, 1 failed',
      );

      expect(result.success, isTrue);
      expect(result.syncedCount, equals(5));
      expect(result.failedCount, equals(1));
      expect(result.errors.length, equals(1));
      expect(result.message, contains('5'));
    });
  });
}
