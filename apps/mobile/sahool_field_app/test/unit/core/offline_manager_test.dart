import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/offline/offline_data_manager.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  group('OfflineDataManager', () {
    late OfflineDataManager offlineManager;

    setUp(() async {
      // Initialize shared preferences with empty data
      SharedPreferences.setMockInitialValues({});

      offlineManager = OfflineDataManager();
      await offlineManager.initialize();
    });

    tearDown(() {
      offlineManager.dispose();
    });

    group('saveLocally', () {
      test('should save data locally', () async {
        // Arrange
        const entityId = 'task_001';
        const entityType = 'task';
        final data = {'title': 'Test Task', 'status': 'pending'};

        // Act
        await offlineManager.saveLocally(
          id: entityId,
          entityType: entityType,
          data: data,
        );

        // Assert
        final savedItem = await offlineManager.getLocalItem(entityId, entityType);
        expect(savedItem, isNotNull);
        expect(savedItem!.id, entityId);
        expect(savedItem.entityType, entityType);
        expect(savedItem.data, data);
        expect(savedItem.status, LocalDataStatus.pendingSync);
      });

      test('should update existing item', () async {
        // Arrange
        const entityId = 'task_001';
        const entityType = 'task';
        final data1 = {'title': 'Task 1', 'status': 'pending'};
        final data2 = {'title': 'Updated Task', 'status': 'done'};

        // Act
        await offlineManager.saveLocally(
          id: entityId,
          entityType: entityType,
          data: data1,
        );

        await offlineManager.saveLocally(
          id: entityId,
          entityType: entityType,
          data: data2,
        );

        // Assert
        final savedItem = await offlineManager.getLocalItem(entityId, entityType);
        expect(savedItem!.data['title'], 'Updated Task');
        expect(savedItem.data['status'], 'done');
      });
    });

    group('getLocalItem', () {
      test('should return null for non-existent item', () async {
        // Act
        final item = await offlineManager.getLocalItem('nonexistent', 'task');

        // Assert
        expect(item, isNull);
      });

      test('should return saved item', () async {
        // Arrange
        const entityId = 'field_001';
        const entityType = 'field';
        final data = {'name': 'Test Field', 'area': 100.0};

        await offlineManager.saveLocally(
          id: entityId,
          entityType: entityType,
          data: data,
        );

        // Act
        final item = await offlineManager.getLocalItem(entityId, entityType);

        // Assert
        expect(item, isNotNull);
        expect(item!.id, entityId);
        expect(item.data['name'], 'Test Field');
      });
    });

    group('getPendingItems', () {
      test('should return only pending items', () async {
        // Arrange
        await offlineManager.saveLocally(
          id: 'task_001',
          entityType: 'task',
          data: {'title': 'Task 1'},
        );

        await offlineManager.saveLocally(
          id: 'task_002',
          entityType: 'task',
          data: {'title': 'Task 2'},
        );

        // Mark one as synced
        await offlineManager.updateItemStatus(
          'task_001',
          'task',
          LocalDataStatus.synced,
        );

        // Act
        final pendingItems = await offlineManager.getPendingItems();

        // Assert
        expect(pendingItems.length, 1);
        expect(pendingItems.first.id, 'task_002');
      });

      test('should return empty list when no pending items', () async {
        // Act
        final pendingItems = await offlineManager.getPendingItems();

        // Assert
        expect(pendingItems, isEmpty);
      });
    });

    group('getPendingCount', () {
      test('should return correct count', () async {
        // Arrange
        await offlineManager.saveLocally(
          id: 'task_001',
          entityType: 'task',
          data: {'title': 'Task 1'},
        );

        await offlineManager.saveLocally(
          id: 'task_002',
          entityType: 'task',
          data: {'title': 'Task 2'},
        );

        await offlineManager.saveLocally(
          id: 'field_001',
          entityType: 'field',
          data: {'name': 'Field 1'},
        );

        // Act
        final count = await offlineManager.getPendingCount();

        // Assert
        expect(count, 3);
      });

      test('should emit pending count updates', () async {
        // Arrange
        final counts = <int>[];
        final subscription = offlineManager.pendingChangesCount.listen(counts.add);

        // Act
        await offlineManager.saveLocally(
          id: 'task_001',
          entityType: 'task',
          data: {'title': 'Task 1'},
        );

        await Future.delayed(const Duration(milliseconds: 100));

        await offlineManager.saveLocally(
          id: 'task_002',
          entityType: 'task',
          data: {'title': 'Task 2'},
        );

        await Future.delayed(const Duration(milliseconds: 100));

        // Assert
        expect(counts, isNotEmpty);
        expect(counts.last, 2);

        // Cleanup
        await subscription.cancel();
      });
    });

    group('deleteLocalItem', () {
      test('should delete item', () async {
        // Arrange
        const entityId = 'task_001';
        const entityType = 'task';

        await offlineManager.saveLocally(
          id: entityId,
          entityType: entityType,
          data: {'title': 'Task to delete'},
        );

        // Act
        await offlineManager.deleteLocalItem(entityId, entityType);

        // Assert
        final item = await offlineManager.getLocalItem(entityId, entityType);
        expect(item, isNull);
      });

      test('should update pending count after delete', () async {
        // Arrange
        await offlineManager.saveLocally(
          id: 'task_001',
          entityType: 'task',
          data: {'title': 'Task 1'},
        );

        await offlineManager.saveLocally(
          id: 'task_002',
          entityType: 'task',
          data: {'title': 'Task 2'},
        );

        // Act
        await offlineManager.deleteLocalItem('task_001', 'task');

        // Assert
        final count = await offlineManager.getPendingCount();
        expect(count, 1);
      });
    });

    group('updateItemStatus', () {
      test('should update status to synced', () async {
        // Arrange
        const entityId = 'task_001';
        const entityType = 'task';

        await offlineManager.saveLocally(
          id: entityId,
          entityType: entityType,
          data: {'title': 'Task'},
        );

        // Act
        await offlineManager.updateItemStatus(
          entityId,
          entityType,
          LocalDataStatus.synced,
        );

        // Assert
        final item = await offlineManager.getLocalItem(entityId, entityType);
        expect(item!.status, LocalDataStatus.synced);
        expect(item.syncedAt, isNotNull);
      });

      test('should update status to error with message', () async {
        // Arrange
        const entityId = 'task_001';
        const entityType = 'task';
        const errorMessage = 'Sync failed';

        await offlineManager.saveLocally(
          id: entityId,
          entityType: entityType,
          data: {'title': 'Task'},
        );

        // Act
        await offlineManager.updateItemStatus(
          entityId,
          entityType,
          LocalDataStatus.error,
          errorMessage: errorMessage,
        );

        // Assert
        final item = await offlineManager.getLocalItem(entityId, entityType);
        expect(item!.status, LocalDataStatus.error);
        expect(item.errorMessage, errorMessage);
      });
    });

    group('syncNow', () {
      test('should return failure when offline', () async {
        // Act
        final result = await offlineManager.syncNow();

        // Assert
        expect(result.success, isFalse);
        expect(result.message, contains('اتصال'));
      });

      test('should emit syncing status', () async {
        // Arrange
        final statuses = <OfflineSyncStatus>[];
        final subscription = offlineManager.syncStatus.listen(statuses.add);

        // This will fail due to no network, but should still emit status
        await offlineManager.syncNow();

        await Future.delayed(const Duration(milliseconds: 100));

        // Assert
        expect(statuses, isNotEmpty);

        // Cleanup
        await subscription.cancel();
      });

      test('should not sync if already syncing', () async {
        // Arrange - start first sync (won't complete due to no network)
        final firstSync = offlineManager.syncNow();

        // Act - try second sync
        final secondResult = await offlineManager.syncNow();

        // Assert
        expect(secondResult.success, isFalse);
        expect(secondResult.message, contains('جارية'));

        // Cleanup
        await firstSync;
      });
    });

    group('LocalDataItem', () {
      test('should serialize to and from JSON', () {
        // Arrange
        final item = LocalDataItem(
          id: 'test_001',
          entityType: 'task',
          data: {'title': 'Test', 'status': 'done'},
          status: LocalDataStatus.pendingSync,
          modifiedAt: DateTime.now(),
          retryCount: 0,
        );

        // Act
        final json = item.toJson();
        final restored = LocalDataItem.fromJson(json);

        // Assert
        expect(restored.id, item.id);
        expect(restored.entityType, item.entityType);
        expect(restored.data, item.data);
        expect(restored.status, item.status);
        expect(restored.retryCount, item.retryCount);
      });

      test('should copyWith correctly', () {
        // Arrange
        final item = LocalDataItem(
          id: 'test_001',
          entityType: 'task',
          data: {'title': 'Test'},
          status: LocalDataStatus.pendingSync,
          modifiedAt: DateTime.now(),
        );

        // Act
        final updated = item.copyWith(
          status: LocalDataStatus.synced,
          syncedAt: DateTime.now(),
        );

        // Assert
        expect(updated.id, item.id);
        expect(updated.status, LocalDataStatus.synced);
        expect(updated.syncedAt, isNotNull);
      });
    });
  });
}
