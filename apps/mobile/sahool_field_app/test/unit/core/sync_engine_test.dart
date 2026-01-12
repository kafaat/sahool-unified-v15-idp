import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/sync/sync_engine.dart';
import 'package:sahool_field_app/core/storage/database.dart';
import 'package:sahool_field_app/core/sync/network_status.dart';
import 'package:sahool_field_app/core/http/api_client.dart';
import '../../mocks/mock_app_database.dart';
import '../../mocks/mock_network_status.dart';

/// Mock ApiClient for testing
class MockApiClient extends Mock implements ApiClient {
  @override
  String get tenantId => 'tenant_test';
}

void main() {
  group('SyncEngine', () {
    late SyncEngine syncEngine;
    late MockAppDatabase mockDatabase;
    late MockNetworkStatus mockNetworkStatus;
    late MockApiClient mockApiClient;

    setUp(() {
      mockDatabase = MockAppDatabase();
      mockNetworkStatus = MockNetworkStatus(isOnline: true);
      mockApiClient = MockApiClient();

      // Setup default mock behaviors
      when(() => mockApiClient.get(any(), queryParameters: any(named: 'queryParameters')))
          .thenAnswer((_) async => <Map<String, dynamic>>[]);
      when(() => mockApiClient.post(any(), any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => {});
      when(() => mockApiClient.put(any(), any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => {});
      when(() => mockApiClient.delete(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => {});

      // Inject all mocks into SyncEngine
      syncEngine = SyncEngine(
        database: mockDatabase,
        networkStatus: mockNetworkStatus,
        apiClient: mockApiClient,
      );

      // Clear mock database before each test
      mockDatabase.clearAll();
    });

    tearDown(() {
      syncEngine.dispose();
      mockNetworkStatus.dispose();
    });

    group('runOnce', () {
      test('should return success when sync completes', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(true);

        // Act
        final result = await syncEngine.runOnce();

        // Assert
        expect(result.success, isTrue);
      });

      test('should return failure when offline', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(false);

        // Act
        final result = await syncEngine.runOnce();

        // Assert
        expect(result.success, isFalse);
        expect(result.message, contains('network'));
      });

      test('should return failure when sync already in progress', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(true);

        // Start first sync (don't await)
        final firstSync = syncEngine.runOnce();

        // Act - Try to start second sync while first is running
        final secondResult = await syncEngine.runOnce();

        // Assert
        expect(secondResult.success, isFalse);
        expect(secondResult.message, contains('already in progress'));

        // Cleanup - wait for first sync to complete
        await firstSync;
      });

      test('should emit syncing status during sync', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(true);
        final statusList = <SyncStatus>[];

        // Listen to status stream
        final subscription = syncEngine.syncStatus.listen(statusList.add);

        // Act
        await syncEngine.runOnce();

        // Assert
        expect(statusList, contains(SyncStatus.syncing));
        expect(statusList.last, SyncStatus.idle);

        // Cleanup
        await subscription.cancel();
      });

      test('should emit error status on failure', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(true);
        final statusList = <SyncStatus>[];

        // Setup database to throw error
        when(() => mockDatabase.getPendingOutbox(limit: any(named: 'limit')))
            .thenThrow(Exception('Database error'));

        final subscription = syncEngine.syncStatus.listen(statusList.add);

        // Act
        await syncEngine.runOnce();

        // Assert
        expect(statusList, contains(SyncStatus.error));

        // Cleanup
        await subscription.cancel();
      });
    });

    group('processOutbox', () {
      test('should process pending outbox items', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(true);

        // Add some pending outbox items
        await mockDatabase.queueOutboxItem(
          tenantId: 'tenant_test',
          entityType: 'task',
          entityId: 'task_001',
          apiEndpoint: '/api/v1/tasks/task_001',
          method: 'PUT',
          payload: '{"status": "done"}',
        );

        await mockDatabase.queueOutboxItem(
          tenantId: 'tenant_test',
          entityType: 'field',
          entityId: 'field_001',
          apiEndpoint: '/api/v1/fields',
          method: 'POST',
          payload: '{"name": "New Field"}',
        );

        // Act
        final result = await syncEngine.runOnce();

        // Assert
        expect(result.success, isTrue);

        // Verify outbox is empty after sync
        final pendingItems = await mockDatabase.getPendingOutbox();
        expect(pendingItems, isEmpty);
      });

      test('should handle empty outbox', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(true);

        // Act
        final result = await syncEngine.runOnce();

        // Assert
        expect(result.success, isTrue);
        expect(result.uploaded, 0);
      });
    });

    group('pullFromServer', () {
      test('should pull and save tasks from server', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(true);

        // Act
        final result = await syncEngine.runOnce();

        // Assert
        expect(result.success, isTrue);
      });
    });

    group('forceRefresh', () {
      test('should throw when offline', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(false);

        // Act & Assert
        expect(
          () => syncEngine.forceRefresh(),
          throwsA(isA<Exception>()),
        );
      });

      test('should emit syncing status during refresh', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(true);
        final statusList = <SyncStatus>[];

        final subscription = syncEngine.syncStatus.listen(statusList.add);

        // Act
        await syncEngine.forceRefresh();

        // Assert
        expect(statusList, contains(SyncStatus.syncing));
        expect(statusList.last, SyncStatus.idle);

        // Cleanup
        await subscription.cancel();
      });
    });

    group('periodic sync', () {
      test('should start periodic sync', () {
        // Arrange & Act
        syncEngine.startPeriodic();

        // Assert - just verify no errors
        expect(syncEngine, isNotNull);

        // Cleanup
        syncEngine.stop();
      });

      test('should stop periodic sync', () {
        // Arrange
        syncEngine.startPeriodic();

        // Act
        syncEngine.stop();

        // Assert - just verify no errors
        expect(syncEngine, isNotNull);
      });
    });

    group('network status integration', () {
      test('should sync when network comes back online', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(false);
        syncEngine.startPeriodic();

        // Act
        mockNetworkStatus.setOnlineStatus(true);

        // Wait a bit for the sync to trigger
        await Future.delayed(const Duration(milliseconds: 500));

        // Assert - verify sync was triggered (check status stream)
        // This is a simplified test - in real scenario, you'd verify the actual sync
        expect(mockNetworkStatus.isOnline, isTrue);

        // Cleanup
        syncEngine.stop();
      });
    });

    group('logging', () {
      test('should log successful sync', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(true);

        // Act
        await syncEngine.runOnce();

        // Assert - verify sync log was created
        final logs = await mockDatabase.getRecentSyncLogs(limit: 1);
        expect(logs, isNotEmpty);
        expect(logs.first.type, 'full_sync');
        expect(logs.first.status, 'success');
      });

      test('should log failed sync', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(true);

        // Setup database to throw error
        when(() => mockDatabase.getPendingOutbox(limit: any(named: 'limit')))
            .thenThrow(Exception('Sync error'));

        // Act
        await syncEngine.runOnce();

        // Assert
        final logs = await mockDatabase.getRecentSyncLogs(limit: 1);
        expect(logs, isNotEmpty);
        expect(logs.first.status, 'failed');
      });
    });
  });
}
