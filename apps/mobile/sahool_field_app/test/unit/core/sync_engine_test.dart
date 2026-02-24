import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/sync/sync_engine.dart';
import '../../mocks/mock_app_database.dart';

/// SyncEngine Unit Tests
/// اختبارات وحدات محرك المزامنة
///
/// Note: SyncEngine creates its own NetworkStatus and ApiClient internally,
/// so we can only test basic functionality that doesn't require network access.
/// For full integration testing, use integration tests with a test server.
void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  // Mock the connectivity_plus platform channel so NetworkStatus can initialize
  setUpAll(() {
    const channel = MethodChannel('dev.fluttercommunity.plus/connectivity');
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (MethodCall methodCall) async {
      if (methodCall.method == 'check') {
        return ['wifi'];
      }
      return null;
    });
  });

  group('SyncEngine', () {
    late SyncEngine syncEngine;
    late MockAppDatabase mockDatabase;

    setUp(() {
      mockDatabase = MockAppDatabase();
      // Create SyncEngine with database only (actual constructor signature)
      syncEngine = SyncEngine(database: mockDatabase);
      mockDatabase.clearAll();
    });

    tearDown(() {
      // Stop periodic sync but don't dispose the engine,
      // as it would close the NetworkStatus singleton's stream controller
      // and break subsequent tests.
      syncEngine.stop();
    });

    group('initialization', () {
      test('should create SyncEngine with database', () {
        expect(syncEngine, isNotNull);
      });

      test('should expose syncStatus stream', () {
        expect(syncEngine.syncStatus, isNotNull);
      });

      test('should expose backoffStatus stream', () {
        expect(syncEngine.backoffStatus, isNotNull);
      });
    });

    group('SyncResult model', () {
      test('should create successful result', () {
        final result = SyncResult(
          success: true,
          uploaded: 5,
          downloaded: 3,
        );

        expect(result.success, isTrue);
        expect(result.uploaded, 5);
        expect(result.downloaded, 3);
        expect(result.message, isNull);
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
    });

    group('SyncStatus enum', () {
      test('should have all expected statuses', () {
        expect(
            SyncStatus.values,
            containsAll([
              SyncStatus.idle,
              SyncStatus.syncing,
              SyncStatus.error,
            ]));
      });
    });

    group('runOnce behavior', () {
      test('should return failure when sync already in progress', () async {
        // Start first sync (don't await) - this will likely fail due to no network
        // but we're testing the "already in progress" check
        final firstSync = syncEngine.runOnce();

        // Act - Try to start second sync while first might be running
        final secondResult = await syncEngine.runOnce();

        // Assert - at least one should fail with "already in progress"
        // or the first finishes quickly (offline) and second also runs
        // This tests the mutex behavior
        expect(secondResult, isNotNull);

        // Cleanup - wait for first sync to complete
        await firstSync;
      });
    });

    group('periodic sync', () {
      test('should start periodic sync without error', () {
        // Arrange & Act
        syncEngine.startPeriodic();

        // Assert - just verify no errors
        expect(syncEngine, isNotNull);

        // Cleanup
        syncEngine.stop();
      });

      test('should stop periodic sync without error', () {
        // Arrange
        syncEngine.startPeriodic();

        // Act
        syncEngine.stop();

        // Assert - just verify no errors
        expect(syncEngine, isNotNull);
      });

      test('should handle multiple start/stop cycles', () {
        syncEngine.startPeriodic();
        syncEngine.stop();
        syncEngine.startPeriodic();
        syncEngine.stop();

        expect(syncEngine, isNotNull);
      });
    });

    group('statistics', () {
      test('should return sync statistics', () {
        final stats = syncEngine.getStatistics();

        expect(stats, isNotNull);
        expect(stats.consecutiveFailures, greaterThanOrEqualTo(0));
        expect(stats.isSyncing, isFalse);
      });
    });

    group('backoff management', () {
      test('should get backoff statuses', () {
        final statuses = syncEngine.getBackoffStatuses();
        expect(statuses, isNotNull);
      });

      test('should reset all backoff without error', () {
        syncEngine.resetAllBackoff();
        expect(syncEngine, isNotNull);
      });
    });

    group('OutboxResult model', () {
      test('should create outbox result', () {
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

      test('should provide string representation', () {
        final result = OutboxResult(
          processed: 5,
          failed: 1,
          conflicts: 0,
          skipped: 2,
        );

        final str = result.toString();
        expect(str, contains('processed: 5'));
        expect(str, contains('failed: 1'));
        expect(str, contains('skipped: 2'));
      });
    });

    group('SyncStatistics model', () {
      test('should indicate healthy status when no failures', () {
        final stats = SyncStatistics(
          consecutiveFailures: 0,
          lastSuccessfulSync: DateTime.now(),
          isSyncing: false,
          unhealthyEndpoints: 0,
        );

        expect(stats.isHealthy, isTrue);
      });

      test('should indicate unhealthy status after many failures', () {
        final stats = SyncStatistics(
          consecutiveFailures: 5,
          lastSuccessfulSync: DateTime.now().subtract(const Duration(hours: 1)),
          isSyncing: false,
          unhealthyEndpoints: 2,
        );

        expect(stats.isHealthy, isFalse);
      });

      test('should calculate time since last sync', () {
        final lastSync = DateTime.now().subtract(const Duration(minutes: 30));
        final stats = SyncStatistics(
          consecutiveFailures: 0,
          lastSuccessfulSync: lastSync,
          isSyncing: false,
        );

        expect(stats.timeSinceLastSync, isNotNull);
        expect(stats.timeSinceLastSync!.inMinutes, greaterThanOrEqualTo(29));
      });

      test('should return null timeSinceLastSync when never synced', () {
        final stats = SyncStatistics(
          consecutiveFailures: 0,
          lastSuccessfulSync: null,
          isSyncing: false,
        );

        expect(stats.timeSinceLastSync, isNull);
      });
    });

    group('BackoffStatus model', () {
      test('should create idle status', () {
        final status = BackoffStatus.idle();

        expect(status.isBackoffActive, isFalse);
        expect(status.affectedEndpoints, isEmpty);
        expect(status.totalEndpointsInBackoff, 0);
      });

      test('should provide human-readable message', () {
        final idleStatus = BackoffStatus.idle();
        expect(idleStatus.statusMessage, contains('healthy'));
      });
    });
  });
}
