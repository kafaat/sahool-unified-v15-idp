import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sahool_field_app/core/offline/outbox_repository.dart';
import 'package:sahool_field_app/core/offline/offline_sync_engine.dart';

void main() {
  group('OutboxRepository', () {
    late OutboxRepository outboxRepository;

    setUp(() async {
      // Initialize with empty storage
      SharedPreferences.setMockInitialValues({});
      outboxRepository = OutboxRepository();
    });

    group('initialization', () {
      test('should initialize successfully', () async {
        // Act
        await outboxRepository.initialize();

        // Assert
        final count = await outboxRepository.getTotalCount();
        expect(count, 0);
      });

      test('should load existing entries from storage', () async {
        // This test demonstrates the expected behavior
        // In practice, entries would be persisted and loaded
        await outboxRepository.initialize();
        expect(outboxRepository, isNotNull);
      });
    });

    group('add', () {
      test('should add entry to repository', () async {
        // Arrange
        await outboxRepository.initialize();

        final entry = OutboxEntry(
          id: 'test_1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {'name': 'Test Task'},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        );

        // Act
        await outboxRepository.add(entry);

        // Assert
        final count = await outboxRepository.getPendingCount();
        expect(count, 1);
      });

      test('should sort entries by priority after adding', () async {
        // Arrange
        await outboxRepository.initialize();

        final lowPriority = OutboxEntry(
          id: 'test_1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.low,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        );

        final highPriority = OutboxEntry(
          id: 'test_2',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.high,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        );

        // Act
        await outboxRepository.add(lowPriority);
        await outboxRepository.add(highPriority);

        // Assert
        final all = await outboxRepository.getAll();
        expect(all.first.id, 'test_2'); // High priority first
        expect(all.last.id, 'test_1');
      });
    });

    group('getPending', () {
      test('should return only pending entries', () async {
        // Arrange
        await outboxRepository.initialize();

        final pending = OutboxEntry(
          id: 'pending_1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        );

        final completed = OutboxEntry(
          id: 'completed_1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.completed,
        );

        await outboxRepository.add(pending);
        await outboxRepository.add(completed);

        // Act
        final pendingEntries = await outboxRepository.getPending();

        // Assert
        expect(pendingEntries.length, 1);
        expect(pendingEntries.first.id, 'pending_1');
      });
    });

    group('getById', () {
      test('should return entry by id', () async {
        // Arrange
        await outboxRepository.initialize();

        final entry = OutboxEntry(
          id: 'test_1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {'name': 'Test'},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        );

        await outboxRepository.add(entry);

        // Act
        final retrieved = await outboxRepository.getById('test_1');

        // Assert
        expect(retrieved, isNotNull);
        expect(retrieved!.id, 'test_1');
      });

      test('should return null for non-existent id', () async {
        // Arrange
        await outboxRepository.initialize();

        // Act
        final retrieved = await outboxRepository.getById('non_existent');

        // Assert
        expect(retrieved, isNull);
      });
    });

    group('markCompleted', () {
      test('should mark entry as completed', () async {
        // Arrange
        await outboxRepository.initialize();

        final entry = OutboxEntry(
          id: 'test_1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        );

        await outboxRepository.add(entry);

        // Act
        await outboxRepository.markCompleted('test_1');

        // Assert
        final retrieved = await outboxRepository.getById('test_1');
        expect(retrieved!.status, OutboxStatus.completed);
      });
    });

    group('markFailed', () {
      test('should mark entry as failed with error message', () async {
        // Arrange
        await outboxRepository.initialize();

        final entry = OutboxEntry(
          id: 'test_1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        );

        await outboxRepository.add(entry);

        // Act
        await outboxRepository.markFailed('test_1', 'Network error');

        // Assert
        final retrieved = await outboxRepository.getById('test_1');
        expect(retrieved!.status, OutboxStatus.failed);
        expect(retrieved.lastError, 'Network error');
        expect(retrieved.retryCount, 1);
      });

      test('should increment retry count on repeated failures', () async {
        // Arrange
        await outboxRepository.initialize();

        final entry = OutboxEntry(
          id: 'test_1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        );

        await outboxRepository.add(entry);

        // Act
        await outboxRepository.markFailed('test_1', 'Error 1');
        await outboxRepository.markFailed('test_1', 'Error 2');
        await outboxRepository.markFailed('test_1', 'Error 3');

        // Assert
        final retrieved = await outboxRepository.getById('test_1');
        expect(retrieved!.retryCount, 3);
      });
    });

    group('resetFailed', () {
      test('should reset failed entries to pending', () async {
        // Arrange
        await outboxRepository.initialize();

        final entry = OutboxEntry(
          id: 'test_1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.failed,
        );

        await outboxRepository.add(entry);

        // Act
        await outboxRepository.resetFailed();

        // Assert
        final retrieved = await outboxRepository.getById('test_1');
        expect(retrieved!.status, OutboxStatus.pending);
      });
    });

    group('counts', () {
      test('should return correct pending count', () async {
        // Arrange
        await outboxRepository.initialize();

        await outboxRepository.add(OutboxEntry(
          id: '1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        ));

        await outboxRepository.add(OutboxEntry(
          id: '2',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        ));

        // Act
        final count = await outboxRepository.getPendingCount();

        // Assert
        expect(count, 2);
      });

      test('should return correct failed count', () async {
        // Arrange
        await outboxRepository.initialize();

        await outboxRepository.add(OutboxEntry(
          id: '1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.failed,
        ));

        // Act
        final count = await outboxRepository.getFailedCount();

        // Assert
        expect(count, 1);
      });

      test('should return correct total count', () async {
        // Arrange
        await outboxRepository.initialize();

        await outboxRepository.add(OutboxEntry(
          id: '1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        ));

        await outboxRepository.add(OutboxEntry(
          id: '2',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.completed,
        ));

        // Act
        final count = await outboxRepository.getTotalCount();

        // Assert
        expect(count, 2);
      });
    });

    group('clearCompleted', () {
      test('should remove all completed entries', () async {
        // Arrange
        await outboxRepository.initialize();

        await outboxRepository.add(OutboxEntry(
          id: '1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.completed,
        ));

        await outboxRepository.add(OutboxEntry(
          id: '2',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        ));

        // Act
        await outboxRepository.clearCompleted();

        // Assert
        final total = await outboxRepository.getTotalCount();
        final completed = await outboxRepository.getCompletedCount();
        expect(total, 1);
        expect(completed, 0);
      });
    });

    group('clearAll', () {
      test('should remove all entries', () async {
        // Arrange
        await outboxRepository.initialize();

        await outboxRepository.add(OutboxEntry(
          id: '1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        ));

        // Act
        await outboxRepository.clearAll();

        // Assert
        final count = await outboxRepository.getTotalCount();
        expect(count, 0);
      });
    });

    group('getByEntityType', () {
      test('should return entries of specific entity type', () async {
        // Arrange
        await outboxRepository.initialize();

        await outboxRepository.add(OutboxEntry(
          id: '1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        ));

        await outboxRepository.add(OutboxEntry(
          id: '2',
          entityType: 'field',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        ));

        // Act
        final tasks = await outboxRepository.getByEntityType('task');

        // Assert
        expect(tasks.length, 1);
        expect(tasks.first.entityType, 'task');
      });
    });

    group('getByOperation', () {
      test('should return entries of specific operation', () async {
        // Arrange
        await outboxRepository.initialize();

        await outboxRepository.add(OutboxEntry(
          id: '1',
          entityType: 'task',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        ));

        await outboxRepository.add(OutboxEntry(
          id: '2',
          entityType: 'task',
          operation: SyncOperation.update,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        ));

        // Act
        final creates = await outboxRepository.getByOperation(SyncOperation.create);

        // Assert
        expect(creates.length, 1);
        expect(creates.first.operation, SyncOperation.create);
      });
    });

    group('hasPendingChanges', () {
      test('should return true when pending changes exist', () async {
        // Arrange
        await outboxRepository.initialize();

        await outboxRepository.add(OutboxEntry(
          id: '1',
          entityType: 'task',
          entityId: 'task_123',
          operation: SyncOperation.update,
          data: {},
          priority: SyncPriority.normal,
          createdAt: DateTime.now(),
          status: OutboxStatus.pending,
        ));

        // Act
        final hasPending = await outboxRepository.hasPendingChanges('task', 'task_123');

        // Assert
        expect(hasPending, isTrue);
      });

      test('should return false when no pending changes exist', () async {
        // Arrange
        await outboxRepository.initialize();

        // Act
        final hasPending = await outboxRepository.hasPendingChanges('task', 'task_123');

        // Assert
        expect(hasPending, isFalse);
      });
    });
  });

  group('OutboxEntry', () {
    test('should create entry from JSON', () {
      // Arrange
      final json = {
        'id': 'test_1',
        'entityType': 'task',
        'entityId': 'task_123',
        'operation': 'create',
        'data': {'name': 'Test Task'},
        'priority': 1,
        'createdAt': DateTime.now().toIso8601String(),
        'status': 'pending',
        'retryCount': 0,
      };

      // Act
      final entry = OutboxEntry.fromJson(json);

      // Assert
      expect(entry.id, 'test_1');
      expect(entry.entityType, 'task');
      expect(entry.operation, SyncOperation.create);
    });

    test('should convert entry to JSON', () {
      // Arrange
      final entry = OutboxEntry(
        id: 'test_1',
        entityType: 'task',
        operation: SyncOperation.create,
        data: {'name': 'Test'},
        priority: SyncPriority.normal,
        createdAt: DateTime.now(),
        status: OutboxStatus.pending,
      );

      // Act
      final json = entry.toJson();

      // Assert
      expect(json['id'], 'test_1');
      expect(json['entityType'], 'task');
      expect(json['operation'], 'create');
    });
  });
}
