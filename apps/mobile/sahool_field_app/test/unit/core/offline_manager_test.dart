import 'dart:async';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/offline/offline_data_manager.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('OfflineDataManager', () {
    late OfflineDataManager offlineManager;

    setUp(() async {
      // Mock the connectivity_plus method channel (checkConnectivity)
      const connectivityMethodChannel =
          MethodChannel('dev.fluttercommunity.plus/connectivity');
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockMethodCallHandler(connectivityMethodChannel,
              (MethodCall methodCall) async {
        if (methodCall.method == 'check') {
          return ['none'];
        }
        return null;
      });

      // Mock the connectivity_plus event channel (onConnectivityChanged)
      const connectivityEventChannel =
          EventChannel('dev.fluttercommunity.plus/connectivity_status');
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockStreamHandler(
        connectivityEventChannel,
        MockStreamHandler.inline(
          onListen: (Object? arguments, MockStreamHandlerEventSink events) {
            // Don't send any events - simulates idle connectivity stream
          },
          onCancel: (Object? arguments) {},
        ),
      );

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
        final savedItem =
            await offlineManager.getLocalItem(entityId, entityType);
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
        final savedItem =
            await offlineManager.getLocalItem(entityId, entityType);
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
        final subscription =
            offlineManager.pendingChangesCount.listen(counts.add);

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
        // Arrange - switch connectivity to online so syncNow enters the sync path
        const connectivityMethodChannel =
            MethodChannel('dev.fluttercommunity.plus/connectivity');
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
            .setMockMethodCallHandler(connectivityMethodChannel,
                (MethodCall methodCall) async {
          if (methodCall.method == 'check') {
            return ['wifi'];
          }
          return null;
        });

        final statuses = <OfflineSyncStatus>[];
        final subscription = offlineManager.syncStatus.listen(statuses.add);

        // Act - syncNow will enter the syncing code path (online, no pending items)
        await offlineManager.syncNow();

        await Future.delayed(const Duration(milliseconds: 100));

        // Assert - should emit syncing then idle
        expect(statuses, isNotEmpty);

        // Cleanup
        await subscription.cancel();
      });

      test('should not sync if already syncing', () async {
        // Arrange - use a Completer to block the FIRST syncNow() at the
        // connectivity check. Then start a second syncNow() AFTER the
        // first one has set _isSyncing = true (i.e., after completing the
        // connectivity check but before the sync finishes).
        //
        // Flow:
        // 1. First syncNow() starts, blocks on checkConnectivity (completer)
        // 2. We complete the completer with ['wifi']
        // 3. First syncNow() continues: passes offline check, _isSyncing = true
        //    then enters for loop with pending items. Each updateItemStatus
        //    involves async await, yielding control.
        // 4. Second syncNow() starts, sees _isSyncing == true, returns early.

        // Save some pending items so the sync loop has work to do
        // (creating yield points within the sync)
        await offlineManager.saveLocally(
          id: 'task_sync_001',
          entityType: 'task',
          data: {'title': 'Sync Test 1'},
        );
        await offlineManager.saveLocally(
          id: 'task_sync_002',
          entityType: 'task',
          data: {'title': 'Sync Test 2'},
        );

        // Track connectivity check calls - saveLocally triggers _trySyncNow
        // which also calls checkConnectivity, so we need to account for that
        final syncCompleter = Completer<List<String>>();
        var directSyncCheckCount = 0;
        const connectivityMethodChannel =
            MethodChannel('dev.fluttercommunity.plus/connectivity');
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
            .setMockMethodCallHandler(connectivityMethodChannel,
                (MethodCall methodCall) async {
          if (methodCall.method == 'check') {
            directSyncCheckCount++;
            if (directSyncCheckCount == 1) {
              // First direct syncNow check: block until we release it
              return syncCompleter.future;
            }
            // All other calls return offline to prevent interference
            return ['none'];
          }
          return null;
        });

        directSyncCheckCount = 0;

        // Start first sync - blocks at checkConnectivity
        final firstSync = offlineManager.syncNow();
        await Future.value(null); // microtask yield

        // Complete connectivity check with online status
        syncCompleter.complete(['wifi']);

        // Yield at microtask level to let first sync advance past
        // the connectivity check and set _isSyncing = true.
        // Each await Future.value(null) yields one microtask.
        // We need enough yields for the continuation to proceed past:
        //   checkConnectivity -> offline check -> _isSyncing = true
        // but NOT so many that the entire sync completes.
        await Future.value(null);
        await Future.value(null);

        // Act - try second sync while first is in progress
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
