
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/sync/queue_manager.dart';

import 'sync_mocks.dart';

/// Sync Queue Tests
/// اختبارات طابور المزامنة
///
/// Tests for:
/// - Queue prioritization
/// - Item status management
/// - Queue statistics
/// - Retry logic
/// - Cleanup operations

void main() {
  group('QueuePriority', () {
    test('should have correct priority values', () {
      expect(QueuePriority.critical.value, equals(0));
      expect(QueuePriority.high.value, equals(1));
      expect(QueuePriority.normal.value, equals(2));
      expect(QueuePriority.low.value, equals(3));
    });

    test('critical should be highest priority', () {
      expect(
        QueuePriority.critical.value < QueuePriority.high.value,
        isTrue,
      );
      expect(
        QueuePriority.high.value < QueuePriority.normal.value,
        isTrue,
      );
      expect(
        QueuePriority.normal.value < QueuePriority.low.value,
        isTrue,
      );
    });
  });

  group('QueueItemStatus', () {
    test('should have all expected statuses', () {
      expect(QueueItemStatus.values, contains(QueueItemStatus.pending));
      expect(QueueItemStatus.values, contains(QueueItemStatus.processing));
      expect(QueueItemStatus.values, contains(QueueItemStatus.completed));
      expect(QueueItemStatus.values, contains(QueueItemStatus.failed));
      expect(QueueItemStatus.values, contains(QueueItemStatus.conflict));
    });
  });

  group('QueueStats', () {
    test('isEmpty returns true when no pending items', () {
      const stats = QueueStats(
        totalPending: 0,
        totalFailed: 0,
        totalConflicts: 0,
        processedToday: 5,
      );

      expect(stats.isEmpty, isTrue);
    });

    test('isEmpty returns false when there are pending items', () {
      const stats = QueueStats(
        totalPending: 3,
        totalFailed: 0,
        totalConflicts: 0,
        processedToday: 5,
      );

      expect(stats.isEmpty, isFalse);
    });

    test('hasFailures returns true when there are failed items', () {
      const stats = QueueStats(
        totalPending: 0,
        totalFailed: 2,
        totalConflicts: 0,
        processedToday: 5,
      );

      expect(stats.hasFailures, isTrue);
    });

    test('hasConflicts returns true when there are conflicts', () {
      const stats = QueueStats(
        totalPending: 0,
        totalFailed: 0,
        totalConflicts: 1,
        processedToday: 5,
      );

      expect(stats.hasConflicts, isTrue);
    });

    test('needsAttention returns true when has failures or conflicts', () {
      const statsWithFailures = QueueStats(
        totalPending: 0,
        totalFailed: 1,
        totalConflicts: 0,
        processedToday: 5,
      );
      expect(statsWithFailures.needsAttention, isTrue);

      const statsWithConflicts = QueueStats(
        totalPending: 0,
        totalFailed: 0,
        totalConflicts: 1,
        processedToday: 5,
      );
      expect(statsWithConflicts.needsAttention, isTrue);

      const healthyStats = QueueStats(
        totalPending: 5,
        totalFailed: 0,
        totalConflicts: 0,
        processedToday: 10,
      );
      expect(healthyStats.needsAttention, isFalse);
    });

    test('copyWith creates a new instance with updated values', () {
      const original = QueueStats(
        totalPending: 5,
        totalFailed: 2,
        totalConflicts: 1,
        processedToday: 10,
      );

      final updated = original.copyWith(totalPending: 3);

      expect(updated.totalPending, equals(3));
      expect(updated.totalFailed, equals(2)); // unchanged
      expect(updated.totalConflicts, equals(1)); // unchanged
      expect(updated.processedToday, equals(10)); // unchanged
    });

    test('copyWith preserves original when no values provided', () {
      final now = DateTime.now();
      final stats = QueueStats(
        totalPending: 5,
        totalFailed: 2,
        totalConflicts: 1,
        processedToday: 10,
        lastSyncTime: now,
      );

      final copy = stats.copyWith();

      expect(copy.totalPending, equals(stats.totalPending));
      expect(copy.totalFailed, equals(stats.totalFailed));
      expect(copy.totalConflicts, equals(stats.totalConflicts));
      expect(copy.processedToday, equals(stats.processedToday));
      expect(copy.lastSyncTime, equals(stats.lastSyncTime));
    });
  });

  group('QueueHealthStatus', () {
    test('should have all expected statuses', () {
      expect(QueueHealthStatus.values, contains(QueueHealthStatus.healthy));
      expect(QueueHealthStatus.values, contains(QueueHealthStatus.busy));
      expect(QueueHealthStatus.values, contains(QueueHealthStatus.warning));
      expect(QueueHealthStatus.values, contains(QueueHealthStatus.critical));
    });

    test('messageAr returns correct Arabic messages', () {
      expect(QueueHealthStatus.healthy.messageAr, isNotEmpty);
      expect(QueueHealthStatus.busy.messageAr, isNotEmpty);
      expect(QueueHealthStatus.warning.messageAr, isNotEmpty);
      expect(QueueHealthStatus.critical.messageAr, isNotEmpty);
    });

    test('messageEn returns correct English messages', () {
      expect(QueueHealthStatus.healthy.messageEn, equals('Fully synced'));
      expect(QueueHealthStatus.busy.messageEn, equals('Syncing...'));
      expect(QueueHealthStatus.warning.messageEn, equals('Conflicts need review'));
      expect(QueueHealthStatus.critical.messageEn, equals('Sync issues detected'));
    });
  });

  group('Queue Priority Operations', () {
    test('DELETE operations should have critical priority', () {
      final priority = QueueManager.getPriorityForOperation('task', 'DELETE');
      expect(priority, equals(QueuePriority.critical));
    });

    test('task PUT operations should have high priority', () {
      final priority = QueueManager.getPriorityForOperation('task', 'PUT');
      expect(priority, equals(QueuePriority.high));
    });

    test('field updates should have normal priority', () {
      final priority = QueueManager.getPriorityForOperation('field', 'PUT');
      expect(priority, equals(QueuePriority.normal));

      final postPriority = QueueManager.getPriorityForOperation('field', 'POST');
      expect(postPriority, equals(QueuePriority.normal));
    });

    test('other operations should have low priority', () {
      final priority = QueueManager.getPriorityForOperation('metadata', 'PUT');
      expect(priority, equals(QueuePriority.low));

      final analyticsPriority = QueueManager.getPriorityForOperation('analytics', 'POST');
      expect(analyticsPriority, equals(QueuePriority.low));
    });

    test('method comparison should be case-insensitive', () {
      expect(
        QueueManager.getPriorityForOperation('task', 'delete'),
        equals(QueuePriority.critical),
      );
      expect(
        QueueManager.getPriorityForOperation('task', 'Delete'),
        equals(QueuePriority.critical),
      );
      expect(
        QueueManager.getPriorityForOperation('task', 'DELETE'),
        equals(QueuePriority.critical),
      );
    });
  });

  group('MockSyncDatabase Queue Operations', () {
    late MockSyncDatabase mockDb;

    setUp(() {
      mockDb = MockSyncDatabase();
    });

    tearDown(() {
      mockDb.reset();
    });

    test('should queue outbox items', () async {
      final id = await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{"name": "Test"}',
      );

      expect(id, equals(1));
      expect(mockDb.outbox.length, equals(1));
      expect(mockDb.outbox.first.entityType, equals('field'));
    });

    test('should get pending outbox items', () async {
      // Add multiple items
      await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{}',
      );
      await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'task',
        entityId: 'task_001',
        apiEndpoint: '/api/v1/tasks',
        method: 'POST',
        payload: '{}',
      );

      final pending = await mockDb.getPendingOutbox();
      expect(pending.length, equals(2));
    });

    test('should respect limit when getting pending items', () async {
      // Add 5 items
      for (int i = 0; i < 5; i++) {
        await mockDb.queueOutboxItem(
          tenantId: 'tenant_1',
          entityType: 'field',
          entityId: 'field_00$i',
          apiEndpoint: '/api/v1/fields/field_00$i',
          method: 'PUT',
          payload: '{}',
        );
      }

      final pending = await mockDb.getPendingOutbox(limit: 3);
      expect(pending.length, equals(3));
    });

    test('should mark outbox item as done', () async {
      final id = await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{}',
      );

      await mockDb.markOutboxDone(id);

      final pending = await mockDb.getPendingOutbox();
      expect(pending.length, equals(0));
      expect(mockDb.outbox.first.synced, isTrue);
    });

    test('should bump retry count on failure', () async {
      final id = await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{}',
      );

      expect(mockDb.outbox.first.retryCount, equals(0));

      await mockDb.bumpOutboxRetry(id);
      expect(mockDb.outbox.first.retryCount, equals(1));

      await mockDb.bumpOutboxRetry(id);
      expect(mockDb.outbox.first.retryCount, equals(2));
    });

    test('should cleanup completed outbox items', () async {
      // Add items
      final id1 = await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{}',
      );
      await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'task',
        entityId: 'task_001',
        apiEndpoint: '/api/v1/tasks',
        method: 'POST',
        payload: '{}',
      );

      // Mark first as done
      await mockDb.markOutboxDone(id1);

      // Cleanup
      await mockDb.cleanupOutbox();

      expect(mockDb.outbox.length, equals(1));
      expect(mockDb.outbox.first.entityType, equals('task'));
    });

    test('should log sync operations', () async {
      await mockDb.logSync(
        type: 'full_sync',
        status: 'success',
        message: 'Synced 5 items',
      );

      final logs = await mockDb.getRecentSyncLogs();
      expect(logs.length, equals(1));
      expect(logs.first['type'], equals('full_sync'));
      expect(logs.first['status'], equals('success'));
    });

    test('should add sync events', () async {
      await mockDb.addSyncEvent(
        tenantId: 'tenant_1',
        type: 'CONFLICT',
        message: 'Conflict detected',
        entityType: 'field',
        entityId: 'field_001',
      );

      expect(mockDb.syncEvents.length, equals(1));
      expect(mockDb.syncEvents.first['type'], equals('CONFLICT'));
    });

    test('should reset database state', () async {
      // Add some data
      await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{}',
      );
      await mockDb.logSync(type: 'test', status: 'ok', message: 'test');
      await mockDb.addSyncEvent(
        tenantId: 'tenant_1',
        type: 'TEST',
        message: 'test',
      );

      // Reset
      mockDb.reset();

      expect(mockDb.outbox.length, equals(0));
      expect(mockDb.syncLogs.length, equals(0));
      expect(mockDb.syncEvents.length, equals(0));
    });
  });

  group('Queue Sorting', () {
    test('items should be sorted by priority then by creation time', () {
      final items = SyncTestFixtures.createMixedPriorityOutboxItems();

      // Simulate sorting logic from QueueManager
      items.sort((a, b) {
        final priorityA = QueueManager.getPriorityForOperation(a.entityType, a.method);
        final priorityB = QueueManager.getPriorityForOperation(b.entityType, b.method);

        final priorityCompare = priorityA.value.compareTo(priorityB.value);
        if (priorityCompare != 0) return priorityCompare;

        return a.createdAt.compareTo(b.createdAt);
      });

      // Critical (DELETE) should be first
      expect(items[0].method, equals('DELETE'));
      // High priority (task PUT) should be second
      expect(items[1].entityType, equals('task'));
      expect(items[1].method, equals('PUT'));
      // Normal priority (field PUT) should be third
      expect(items[2].entityType, equals('field'));
      // Low priority (metadata) should be last
      expect(items[3].entityType, equals('metadata'));
    });

    test('same priority items should be sorted by creation time (oldest first)', () {
      final now = DateTime.now();
      final items = [
        MockOutboxData(
          id: 1,
          tenantId: 'tenant_1',
          entityType: 'field',
          entityId: 'field_002',
          apiEndpoint: '/api/v1/fields/field_002',
          method: 'PUT',
          payload: '{}',
          createdAt: now,
        ),
        MockOutboxData(
          id: 2,
          tenantId: 'tenant_1',
          entityType: 'field',
          entityId: 'field_001',
          apiEndpoint: '/api/v1/fields/field_001',
          method: 'PUT',
          payload: '{}',
          createdAt: now.subtract(const Duration(minutes: 5)),
        ),
        MockOutboxData(
          id: 3,
          tenantId: 'tenant_1',
          entityType: 'field',
          entityId: 'field_003',
          apiEndpoint: '/api/v1/fields/field_003',
          method: 'PUT',
          payload: '{}',
          createdAt: now.subtract(const Duration(minutes: 2)),
        ),
      ];

      items.sort((a, b) {
        final priorityA = QueueManager.getPriorityForOperation(a.entityType, a.method);
        final priorityB = QueueManager.getPriorityForOperation(b.entityType, b.method);

        final priorityCompare = priorityA.value.compareTo(priorityB.value);
        if (priorityCompare != 0) return priorityCompare;

        return a.createdAt.compareTo(b.createdAt);
      });

      // Oldest should be first (field_001, 5 minutes ago)
      expect(items[0].entityId, equals('field_001'));
      // Next oldest (field_003, 2 minutes ago)
      expect(items[1].entityId, equals('field_003'));
      // Most recent last (field_002, now)
      expect(items[2].entityId, equals('field_002'));
    });
  });

  group('Queue Edge Cases', () {
    late MockSyncDatabase mockDb;

    setUp(() {
      mockDb = MockSyncDatabase();
    });

    tearDown(() {
      mockDb.reset();
    });

    test('should handle empty queue gracefully', () async {
      final pending = await mockDb.getPendingOutbox();
      expect(pending, isEmpty);
    });

    test('should handle marking non-existent item as done', () async {
      // Should not throw
      await mockDb.markOutboxDone(999);
      expect(mockDb.outbox, isEmpty);
    });

    test('should handle bumping retry on non-existent item', () async {
      // Should not throw
      await mockDb.bumpOutboxRetry(999);
      expect(mockDb.outbox, isEmpty);
    });

    test('should handle cleanup on empty queue', () async {
      await mockDb.cleanupOutbox();
      expect(mockDb.outbox, isEmpty);
    });

    test('should track items exceeding max retry count', () async {
      final id = await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{}',
      );

      // Simulate 5 retries (max is typically 5)
      for (int i = 0; i < 5; i++) {
        await mockDb.bumpOutboxRetry(id);
      }

      final pending = await mockDb.getPendingOutbox();
      expect(pending.first.retryCount, equals(5));
      expect(pending.first.retryCount >= 5, isTrue);
    });

    test('should preserve ifMatch ETag when provided', () async {
      final etag = '"abc123"';
      await mockDb.queueOutboxItem(
        tenantId: 'tenant_1',
        entityType: 'field',
        entityId: 'field_001',
        apiEndpoint: '/api/v1/fields/field_001',
        method: 'PUT',
        payload: '{}',
        ifMatch: etag,
      );

      expect(mockDb.outbox.first.ifMatch, equals(etag));
    });
  });
}
