import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/offline/offline_sync_engine.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // SyncStatus Enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('SyncStatus', () {
    test('should have exactly 6 values', () {
      expect(SyncStatus.values.length, 6);
    });

    test('should contain all expected values', () {
      expect(SyncStatus.values, containsAll([
        SyncStatus.idle,
        SyncStatus.syncing,
        SyncStatus.success,
        SyncStatus.partialSuccess,
        SyncStatus.error,
        SyncStatus.offline,
      ]));
    });

    test('should resolve from name string', () {
      expect(SyncStatus.values.byName('idle'), SyncStatus.idle);
      expect(SyncStatus.values.byName('syncing'), SyncStatus.syncing);
      expect(SyncStatus.values.byName('success'), SyncStatus.success);
      expect(SyncStatus.values.byName('partialSuccess'), SyncStatus.partialSuccess);
      expect(SyncStatus.values.byName('error'), SyncStatus.error);
      expect(SyncStatus.values.byName('offline'), SyncStatus.offline);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SyncOperation Enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('SyncOperation', () {
    test('should have exactly 3 values', () {
      expect(SyncOperation.values.length, 3);
    });

    test('should contain create, update, delete', () {
      expect(SyncOperation.values, containsAll([
        SyncOperation.create,
        SyncOperation.update,
        SyncOperation.delete,
      ]));
    });

    test('should resolve from name string', () {
      expect(SyncOperation.values.byName('create'), SyncOperation.create);
      expect(SyncOperation.values.byName('update'), SyncOperation.update);
      expect(SyncOperation.values.byName('delete'), SyncOperation.delete);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SyncPriority Enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('SyncPriority', () {
    test('should have exactly 4 values', () {
      expect(SyncPriority.values.length, 4);
    });

    test('should contain low, normal, high, critical', () {
      expect(SyncPriority.values, containsAll([
        SyncPriority.low,
        SyncPriority.normal,
        SyncPriority.high,
        SyncPriority.critical,
      ]));
    });

    test('should have correct index order', () {
      expect(SyncPriority.low.index, 0);
      expect(SyncPriority.normal.index, 1);
      expect(SyncPriority.high.index, 2);
      expect(SyncPriority.critical.index, 3);
    });

    test('should resolve by index', () {
      expect(SyncPriority.values[0], SyncPriority.low);
      expect(SyncPriority.values[1], SyncPriority.normal);
      expect(SyncPriority.values[2], SyncPriority.high);
      expect(SyncPriority.values[3], SyncPriority.critical);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // OutboxStatus Enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('OutboxStatus', () {
    test('should have exactly 4 values', () {
      expect(OutboxStatus.values.length, 4);
    });

    test('should contain pending, processing, completed, failed', () {
      expect(OutboxStatus.values, containsAll([
        OutboxStatus.pending,
        OutboxStatus.processing,
        OutboxStatus.completed,
        OutboxStatus.failed,
      ]));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // OutboxEntry
  // ═══════════════════════════════════════════════════════════════════════════

  group('OutboxEntry', () {
    late DateTime testTime;
    late OutboxEntry entry;

    setUp(() {
      testTime = DateTime(2025, 6, 15, 10, 30);
      entry = OutboxEntry(
        id: 'entry-001',
        entityType: 'field',
        entityId: 'field-123',
        operation: SyncOperation.update,
        data: {'name': 'Updated Field', 'area': 5.0},
        previousData: {'name': 'Old Field', 'area': 4.5},
        priority: SyncPriority.high,
        createdAt: testTime,
        status: OutboxStatus.pending,
        retryCount: 2,
        lastError: 'Connection timeout',
      );
    });

    test('should construct with all fields', () {
      expect(entry.id, 'entry-001');
      expect(entry.entityType, 'field');
      expect(entry.entityId, 'field-123');
      expect(entry.operation, SyncOperation.update);
      expect(entry.data, {'name': 'Updated Field', 'area': 5.0});
      expect(entry.previousData, {'name': 'Old Field', 'area': 4.5});
      expect(entry.priority, SyncPriority.high);
      expect(entry.createdAt, testTime);
      expect(entry.status, OutboxStatus.pending);
      expect(entry.retryCount, 2);
      expect(entry.lastError, 'Connection timeout');
    });

    test('should default retryCount to 0', () {
      final newEntry = OutboxEntry(
        id: 'e1',
        entityType: 'task',
        operation: SyncOperation.create,
        data: {'title': 'Test'},
        priority: SyncPriority.normal,
        createdAt: testTime,
        status: OutboxStatus.pending,
      );
      expect(newEntry.retryCount, 0);
    });

    test('should default entityId to null', () {
      final newEntry = OutboxEntry(
        id: 'e1',
        entityType: 'task',
        operation: SyncOperation.create,
        data: {'title': 'Test'},
        priority: SyncPriority.normal,
        createdAt: testTime,
        status: OutboxStatus.pending,
      );
      expect(newEntry.entityId, isNull);
    });

    test('should default previousData to null', () {
      final newEntry = OutboxEntry(
        id: 'e1',
        entityType: 'task',
        operation: SyncOperation.create,
        data: {},
        priority: SyncPriority.normal,
        createdAt: testTime,
        status: OutboxStatus.pending,
      );
      expect(newEntry.previousData, isNull);
    });

    test('should default lastError to null', () {
      final newEntry = OutboxEntry(
        id: 'e1',
        entityType: 'task',
        operation: SyncOperation.create,
        data: {},
        priority: SyncPriority.normal,
        createdAt: testTime,
        status: OutboxStatus.pending,
      );
      expect(newEntry.lastError, isNull);
    });

    // ─────────────────────────────────────────────────────────────────────
    // copyWith
    // ─────────────────────────────────────────────────────────────────────

    group('copyWith', () {
      test('should return new instance with updated fields', () {
        final updated = entry.copyWith(
          status: OutboxStatus.processing,
          retryCount: 3,
          lastError: 'New error',
        );
        expect(updated.id, entry.id);
        expect(updated.entityType, entry.entityType);
        expect(updated.status, OutboxStatus.processing);
        expect(updated.retryCount, 3);
        expect(updated.lastError, 'New error');
      });

      test('should preserve original fields when not specified', () {
        final copy = entry.copyWith();
        expect(copy.id, entry.id);
        expect(copy.entityType, entry.entityType);
        expect(copy.entityId, entry.entityId);
        expect(copy.operation, entry.operation);
        expect(copy.data, entry.data);
        expect(copy.previousData, entry.previousData);
        expect(copy.priority, entry.priority);
        expect(copy.createdAt, entry.createdAt);
        expect(copy.status, entry.status);
        expect(copy.retryCount, entry.retryCount);
        expect(copy.lastError, entry.lastError);
      });

      test('should allow updating data map', () {
        final updated = entry.copyWith(data: {'name': 'New Name'});
        expect(updated.data, {'name': 'New Name'});
        expect(entry.data, {'name': 'Updated Field', 'area': 5.0});
      });

      test('should allow changing operation', () {
        final updated = entry.copyWith(operation: SyncOperation.delete);
        expect(updated.operation, SyncOperation.delete);
      });

      test('should allow changing priority', () {
        final updated = entry.copyWith(priority: SyncPriority.critical);
        expect(updated.priority, SyncPriority.critical);
      });
    });

    // ─────────────────────────────────────────────────────────────────────
    // toJson / fromJson
    // ─────────────────────────────────────────────────────────────────────

    group('toJson', () {
      test('should serialize all fields correctly', () {
        final json = entry.toJson();
        expect(json['id'], 'entry-001');
        expect(json['entityType'], 'field');
        expect(json['entityId'], 'field-123');
        expect(json['operation'], 'update');
        expect(json['data'], {'name': 'Updated Field', 'area': 5.0});
        expect(json['previousData'], {'name': 'Old Field', 'area': 4.5});
        expect(json['priority'], SyncPriority.high.index);
        expect(json['createdAt'], testTime.toIso8601String());
        expect(json['status'], 'pending');
        expect(json['retryCount'], 2);
        expect(json['lastError'], 'Connection timeout');
      });

      test('should serialize null optional fields as null', () {
        final minimalEntry = OutboxEntry(
          id: 'e1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {'title': 'Test'},
          priority: SyncPriority.normal,
          createdAt: testTime,
          status: OutboxStatus.pending,
        );
        final json = minimalEntry.toJson();
        expect(json['entityId'], isNull);
        expect(json['previousData'], isNull);
        expect(json['lastError'], isNull);
        expect(json['retryCount'], 0);
      });

      test('priority should serialize as integer index', () {
        for (final priority in SyncPriority.values) {
          final e = entry.copyWith(priority: priority);
          expect(e.toJson()['priority'], priority.index);
        }
      });
    });

    group('fromJson', () {
      test('should deserialize all fields correctly', () {
        final json = entry.toJson();
        final restored = OutboxEntry.fromJson(json);
        expect(restored.id, entry.id);
        expect(restored.entityType, entry.entityType);
        expect(restored.entityId, entry.entityId);
        expect(restored.operation, entry.operation);
        expect(restored.data, entry.data);
        expect(restored.previousData, entry.previousData);
        expect(restored.priority, entry.priority);
        expect(restored.createdAt, entry.createdAt);
        expect(restored.status, entry.status);
        expect(restored.retryCount, entry.retryCount);
        expect(restored.lastError, entry.lastError);
      });

      test('roundtrip should preserve all data', () {
        final restored = OutboxEntry.fromJson(entry.toJson());
        final reRestored = OutboxEntry.fromJson(restored.toJson());
        expect(reRestored.id, entry.id);
        expect(reRestored.entityType, entry.entityType);
        expect(reRestored.operation, entry.operation);
        expect(reRestored.priority, entry.priority);
      });

      test('should handle null entityId', () {
        final json = <String, dynamic>{
          'id': 'e1',
          'entityType': 'task',
          'entityId': null,
          'operation': 'create',
          'data': {'title': 'Test'},
          'previousData': null,
          'priority': 1,
          'createdAt': testTime.toIso8601String(),
          'status': 'pending',
          'retryCount': 0,
          'lastError': null,
        };
        final restored = OutboxEntry.fromJson(json);
        expect(restored.entityId, isNull);
        expect(restored.previousData, isNull);
        expect(restored.lastError, isNull);
      });

      test('should default retryCount to 0 when missing', () {
        final json = <String, dynamic>{
          'id': 'e1',
          'entityType': 'task',
          'operation': 'create',
          'data': {'title': 'Test'},
          'priority': 1,
          'createdAt': testTime.toIso8601String(),
          'status': 'pending',
          // retryCount intentionally missing
        };
        final restored = OutboxEntry.fromJson(json);
        expect(restored.retryCount, 0);
      });

      test('should deserialize each SyncOperation correctly', () {
        for (final op in SyncOperation.values) {
          final json = <String, dynamic>{
            'id': 'e1',
            'entityType': 'task',
            'operation': op.name,
            'data': {},
            'priority': 0,
            'createdAt': testTime.toIso8601String(),
            'status': 'pending',
          };
          final restored = OutboxEntry.fromJson(json);
          expect(restored.operation, op);
        }
      });

      test('should deserialize each OutboxStatus correctly', () {
        for (final status in OutboxStatus.values) {
          final json = <String, dynamic>{
            'id': 'e1',
            'entityType': 'task',
            'operation': 'create',
            'data': {},
            'priority': 0,
            'createdAt': testTime.toIso8601String(),
            'status': status.name,
          };
          final restored = OutboxEntry.fromJson(json);
          expect(restored.status, status);
        }
      });

      test('should deserialize each SyncPriority by index', () {
        for (final priority in SyncPriority.values) {
          final json = <String, dynamic>{
            'id': 'e1',
            'entityType': 'task',
            'operation': 'create',
            'data': {},
            'priority': priority.index,
            'createdAt': testTime.toIso8601String(),
            'status': 'pending',
          };
          final restored = OutboxEntry.fromJson(json);
          expect(restored.priority, priority);
        }
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SyncResult
  // ═══════════════════════════════════════════════════════════════════════════

  group('SyncResult', () {
    test('should construct with required fields and defaults', () {
      const result = SyncResult(
        success: true,
        message: 'All synced',
      );
      expect(result.success, true);
      expect(result.message, 'All synced');
      expect(result.syncedCount, 0);
      expect(result.failedCount, 0);
      expect(result.errors, isEmpty);
    });

    test('should construct with all fields', () {
      const result = SyncResult(
        success: false,
        syncedCount: 5,
        failedCount: 2,
        errors: ['Error 1', 'Error 2'],
        message: 'Partial sync',
      );
      expect(result.success, false);
      expect(result.syncedCount, 5);
      expect(result.failedCount, 2);
      expect(result.errors.length, 2);
      expect(result.message, 'Partial sync');
    });

    test('successful result should have success=true', () {
      const result = SyncResult(
        success: true,
        syncedCount: 10,
        failedCount: 0,
        message: 'Synced 10 items',
      );
      expect(result.success, true);
      expect(result.failedCount, 0);
    });

    test('failed result should have success=false', () {
      const result = SyncResult(
        success: false,
        syncedCount: 0,
        failedCount: 3,
        errors: ['timeout', 'conflict', 'auth'],
        message: 'Sync failed',
      );
      expect(result.success, false);
      expect(result.failedCount, 3);
      expect(result.errors, hasLength(3));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // OutboxStats
  // ═══════════════════════════════════════════════════════════════════════════

  group('OutboxStats', () {
    test('should construct with all required fields', () {
      const stats = OutboxStats(
        pendingCount: 5,
        failedCount: 2,
        completedCount: 10,
        isSyncing: false,
        lastSyncStatus: SyncStatus.success,
      );
      expect(stats.pendingCount, 5);
      expect(stats.failedCount, 2);
      expect(stats.completedCount, 10);
      expect(stats.isSyncing, false);
      expect(stats.lastSyncStatus, SyncStatus.success);
    });

    test('totalCount should sum pending + failed + completed', () {
      const stats = OutboxStats(
        pendingCount: 5,
        failedCount: 2,
        completedCount: 10,
        isSyncing: false,
        lastSyncStatus: SyncStatus.idle,
      );
      expect(stats.totalCount, 17);
    });

    test('totalCount should be 0 when all counts are 0', () {
      const stats = OutboxStats(
        pendingCount: 0,
        failedCount: 0,
        completedCount: 0,
        isSyncing: false,
        lastSyncStatus: SyncStatus.idle,
      );
      expect(stats.totalCount, 0);
    });

    test('hasPending should be true when pendingCount > 0', () {
      const stats = OutboxStats(
        pendingCount: 1,
        failedCount: 0,
        completedCount: 0,
        isSyncing: false,
        lastSyncStatus: SyncStatus.idle,
      );
      expect(stats.hasPending, true);
    });

    test('hasPending should be false when pendingCount is 0', () {
      const stats = OutboxStats(
        pendingCount: 0,
        failedCount: 0,
        completedCount: 0,
        isSyncing: false,
        lastSyncStatus: SyncStatus.idle,
      );
      expect(stats.hasPending, false);
    });

    test('hasFailed should be true when failedCount > 0', () {
      const stats = OutboxStats(
        pendingCount: 0,
        failedCount: 3,
        completedCount: 0,
        isSyncing: false,
        lastSyncStatus: SyncStatus.error,
      );
      expect(stats.hasFailed, true);
    });

    test('hasFailed should be false when failedCount is 0', () {
      const stats = OutboxStats(
        pendingCount: 0,
        failedCount: 0,
        completedCount: 5,
        isSyncing: false,
        lastSyncStatus: SyncStatus.success,
      );
      expect(stats.hasFailed, false);
    });

    test('isSyncing should reflect active sync state', () {
      const syncing = OutboxStats(
        pendingCount: 3,
        failedCount: 0,
        completedCount: 0,
        isSyncing: true,
        lastSyncStatus: SyncStatus.syncing,
      );
      expect(syncing.isSyncing, true);
    });

    test('should work with all SyncStatus values', () {
      for (final status in SyncStatus.values) {
        final stats = OutboxStats(
          pendingCount: 0,
          failedCount: 0,
          completedCount: 0,
          isSyncing: false,
          lastSyncStatus: status,
        );
        expect(stats.lastSyncStatus, status);
      }
    });

    test('large counts should be handled correctly', () {
      const stats = OutboxStats(
        pendingCount: 10000,
        failedCount: 500,
        completedCount: 50000,
        isSyncing: true,
        lastSyncStatus: SyncStatus.syncing,
      );
      expect(stats.totalCount, 60500);
      expect(stats.hasPending, true);
      expect(stats.hasFailed, true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // OutboxEntry edge cases and patterns
  // ═══════════════════════════════════════════════════════════════════════════

  group('OutboxEntry - typical usage patterns', () {
    test('create operation pattern should have no entityId', () {
      final entry = OutboxEntry(
        id: 'create-001',
        entityType: 'field',
        operation: SyncOperation.create,
        data: {'name': 'New Field', 'area': 10.0},
        priority: SyncPriority.normal,
        createdAt: DateTime.now(),
        status: OutboxStatus.pending,
      );
      expect(entry.entityId, isNull);
      expect(entry.previousData, isNull);
      expect(entry.operation, SyncOperation.create);
    });

    test('update operation pattern should have entityId and previousData', () {
      final entry = OutboxEntry(
        id: 'update-001',
        entityType: 'field',
        entityId: 'field-456',
        operation: SyncOperation.update,
        data: {'name': 'Renamed Field'},
        previousData: {'name': 'Original Field'},
        priority: SyncPriority.normal,
        createdAt: DateTime.now(),
        status: OutboxStatus.pending,
      );
      expect(entry.entityId, 'field-456');
      expect(entry.previousData, isNotNull);
      expect(entry.operation, SyncOperation.update);
    });

    test('delete operation pattern should have entityId and empty data', () {
      final entry = OutboxEntry(
        id: 'delete-001',
        entityType: 'field',
        entityId: 'field-789',
        operation: SyncOperation.delete,
        data: {},
        priority: SyncPriority.high,
        createdAt: DateTime.now(),
        status: OutboxStatus.pending,
      );
      expect(entry.entityId, 'field-789');
      expect(entry.data, isEmpty);
      expect(entry.operation, SyncOperation.delete);
      expect(entry.priority, SyncPriority.high);
    });

    test('failed entry should track error and retry count', () {
      final entry = OutboxEntry(
        id: 'fail-001',
        entityType: 'task',
        entityId: 'task-123',
        operation: SyncOperation.update,
        data: {'status': 'done'},
        priority: SyncPriority.normal,
        createdAt: DateTime.now(),
        status: OutboxStatus.failed,
        retryCount: 3,
        lastError: 'Server returned 500',
      );
      expect(entry.status, OutboxStatus.failed);
      expect(entry.retryCount, 3);
      expect(entry.lastError, 'Server returned 500');
    });

    test('transition from pending to processing via copyWith', () {
      final pending = OutboxEntry(
        id: 'e1',
        entityType: 'field',
        operation: SyncOperation.create,
        data: {'name': 'Test'},
        priority: SyncPriority.normal,
        createdAt: DateTime.now(),
        status: OutboxStatus.pending,
      );

      final processing = pending.copyWith(status: OutboxStatus.processing);
      expect(processing.status, OutboxStatus.processing);
      expect(processing.id, pending.id);

      final completed = processing.copyWith(status: OutboxStatus.completed);
      expect(completed.status, OutboxStatus.completed);
    });

    test('transition from pending to failed via copyWith', () {
      final pending = OutboxEntry(
        id: 'e1',
        entityType: 'field',
        operation: SyncOperation.create,
        data: {},
        priority: SyncPriority.normal,
        createdAt: DateTime.now(),
        status: OutboxStatus.pending,
      );

      final failed = pending.copyWith(
        status: OutboxStatus.failed,
        retryCount: 1,
        lastError: 'timeout',
      );
      expect(failed.status, OutboxStatus.failed);
      expect(failed.retryCount, 1);
      expect(failed.lastError, 'timeout');
    });
  });
}
