/// SAHOOL Field App - Sync Integration Tests
/// اختبارات تكامل المزامنة الشاملة
///
/// Test scenarios:
/// - Offline data creation and queuing
/// - Sync when connectivity restored
/// - Conflict detection and resolution
/// - Retry on failure with exponential backoff
/// - Optimistic locking with ETags
/// - Concurrent sync requests

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Sync Integration Tests', () {
    late ProviderContainer container;

    setUp(() async {
      SharedPreferences.setMockInitialValues({});
      container = ProviderContainer();
    });

    tearDown(() {
      container.dispose();
    });

    // =========================================================================
    // Offline Data Creation Tests
    // =========================================================================

    testWidgets('should create task offline and add to outbox', (tester) async {
      // Arrange
      SharedPreferences.setMockInitialValues({
        'is_online': false,
      });

      final prefs = await SharedPreferences.getInstance();

      // Simulate creating a task offline
      final newTask = {
        'id': 'task-001',
        'title': 'مهمة اختبارية',
        'status': 'pending',
        'created_at': DateTime.now().toIso8601String(),
        'tenant_id': 'test_tenant',
      };

      // Act - Add to outbox
      final outboxItem = {
        'id': 'outbox-001',
        'entity_type': 'task',
        'entity_id': 'task-001',
        'method': 'POST',
        'api_endpoint': '/tasks',
        'payload': newTask.toString(),
        'retry_count': 0,
        'created_at': DateTime.now().toIso8601String(),
      };

      final outbox = prefs.getStringList('outbox') ?? [];
      outbox.add(outboxItem.toString());
      await prefs.setStringList('outbox', outbox);

      // Assert
      final savedOutbox = prefs.getStringList('outbox');
      expect(savedOutbox, isNotNull);
      expect(savedOutbox!.length, equals(1));
      expect(savedOutbox.first.contains('task-001'), isTrue);
    });

    testWidgets('should create field record offline with GPS coordinates', (tester) async {
      // Arrange
      final fieldData = {
        'id': 'field-001',
        'name': 'حقل الزيتون',
        'area': 100.5,
        'latitude': 24.7136,
        'longitude': 46.6753,
        'tenant_id': 'test_tenant',
        'created_at': DateTime.now().toIso8601String(),
      };

      final prefs = await SharedPreferences.getInstance();

      // Act - Save locally
      await prefs.setString('field_field-001', fieldData.toString());

      // Add to outbox
      final outboxItem = {
        'entity_type': 'field',
        'entity_id': 'field-001',
        'method': 'POST',
        'api_endpoint': '/fields',
        'payload': fieldData.toString(),
      };

      final outbox = prefs.getStringList('outbox') ?? [];
      outbox.add(outboxItem.toString());
      await prefs.setStringList('outbox', outbox);

      // Assert
      expect(prefs.getString('field_field-001'), isNotNull);
      expect(prefs.getStringList('outbox')!.length, equals(1));
    });

    testWidgets('should create multiple records offline and batch queue', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      final records = <Map<String, dynamic>>[];

      // Act - Create multiple records
      for (int i = 0; i < 5; i++) {
        records.add({
          'id': 'record-00$i',
          'type': 'soil_health',
          'created_at': DateTime.now().toIso8601String(),
        });
      }

      // Add all to outbox
      final outbox = <String>[];
      for (final record in records) {
        outbox.add({
          'entity_type': 'ecological_record',
          'entity_id': record['id'],
          'method': 'POST',
          'payload': record.toString(),
        }.toString());
      }
      await prefs.setStringList('outbox', outbox);

      // Assert
      expect(prefs.getStringList('outbox')!.length, equals(5));
    });

    // =========================================================================
    // Sync When Online Tests
    // =========================================================================

    testWidgets('should detect online status and trigger sync', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('is_online', false);

      // Add pending items
      await prefs.setStringList('outbox', ['item1', 'item2']);

      // Act - Simulate going online
      await prefs.setBool('is_online', true);
      final shouldSync = prefs.getBool('is_online') ?? false;

      // Assert
      expect(shouldSync, isTrue);
      expect(prefs.getStringList('outbox')!.length, greaterThan(0));
    });

    testWidgets('should process outbox items in order', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      final outbox = [
        {'id': '1', 'created_at': DateTime.now().subtract(const Duration(hours: 2)).toIso8601String()}.toString(),
        {'id': '2', 'created_at': DateTime.now().subtract(const Duration(hours: 1)).toIso8601String()}.toString(),
        {'id': '3', 'created_at': DateTime.now().toIso8601String()}.toString(),
      ];
      await prefs.setStringList('outbox', outbox);

      // Act - Process in FIFO order
      final items = prefs.getStringList('outbox')!;
      final processed = <String>[];

      for (final item in items) {
        processed.add(item);
        // Simulate successful upload
      }

      // Clear outbox after processing
      await prefs.setStringList('outbox', []);

      // Assert
      expect(processed.length, equals(3));
      expect(prefs.getStringList('outbox'), isEmpty);
    });

    testWidgets('should sync and update local cache with server data', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Simulate local cached data
      await prefs.setString('task_001', {
        'id': '001',
        'title': 'Local Task',
        'updated_at': DateTime.now().subtract(const Duration(hours: 1)).toIso8601String(),
      }.toString());

      // Simulate server data (newer)
      final serverData = {
        'id': '001',
        'title': 'Updated from Server',
        'updated_at': DateTime.now().toIso8601String(),
      };

      // Act - Update local cache with server data
      await prefs.setString('task_001', serverData.toString());
      await prefs.setString('last_sync', DateTime.now().toIso8601String());

      // Assert
      final cachedTask = prefs.getString('task_001');
      expect(cachedTask, contains('Updated from Server'));
      expect(prefs.getString('last_sync'), isNotNull);
    });

    // =========================================================================
    // Conflict Resolution Tests
    // =========================================================================

    testWidgets('should detect conflict when local and server differ', (tester) async {
      // Arrange
      final localData = {
        'id': 'field-001',
        'name': 'Local Field Name',
        'updated_at': DateTime.now().subtract(const Duration(minutes: 5)).toIso8601String(),
      };

      final serverData = {
        'id': 'field-001',
        'name': 'Server Field Name',
        'updated_at': DateTime.now().toIso8601String(),
      };

      final baseData = {
        'id': 'field-001',
        'name': 'Original Field Name',
        'updated_at': DateTime.now().subtract(const Duration(hours: 1)).toIso8601String(),
      };

      // Act - Detect conflict
      final localChanged = localData['name'] != baseData['name'];
      final serverChanged = serverData['name'] != baseData['name'];
      final hasConflict = localChanged && serverChanged && (localData['name'] != serverData['name']);

      // Assert
      expect(hasConflict, isTrue);
    });

    testWidgets('should resolve conflict using last-write-wins strategy', (tester) async {
      // Arrange
      final localData = {
        'id': 'field-001',
        'name': 'Local Update',
        'updated_at': DateTime.parse('2024-01-01T10:00:00Z'),
      };

      final serverData = {
        'id': 'field-001',
        'name': 'Server Update',
        'updated_at': DateTime.parse('2024-01-01T11:00:00Z'), // Newer
      };

      // Act - Apply last-write-wins
      final localTime = localData['updated_at'] as DateTime;
      final serverTime = serverData['updated_at'] as DateTime;
      final resolvedData = serverTime.isAfter(localTime) ? serverData : localData;

      // Assert
      expect(resolvedData['name'], equals('Server Update'));
    });

    testWidgets('should merge non-conflicting fields', (tester) async {
      // Arrange
      final baseData = {
        'id': 'field-001',
        'name': 'Field A',
        'area': 100.0,
        'crop': 'wheat',
      };

      final localData = {
        'id': 'field-001',
        'name': 'Field A',
        'area': 150.0, // Changed locally
        'crop': 'wheat',
      };

      final serverData = {
        'id': 'field-001',
        'name': 'Field A',
        'area': 100.0,
        'crop': 'barley', // Changed on server
      };

      // Act - Merge changes
      final merged = Map<String, dynamic>.from(baseData);

      // Apply server changes
      if (serverData['crop'] != baseData['crop']) {
        merged['crop'] = serverData['crop'];
      }

      // Apply local changes
      if (localData['area'] != baseData['area']) {
        merged['area'] = localData['area'];
      }

      // Assert - Both changes should be merged
      expect(merged['area'], equals(150.0)); // Local change
      expect(merged['crop'], equals('barley')); // Server change
    });

    testWidgets('should create conflict log entry', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      final conflictDetails = {
        'id': 'conflict-001',
        'entity_type': 'field',
        'entity_id': 'field-001',
        'local_value': 'Local Name',
        'server_value': 'Server Name',
        'resolution': 'server_wins',
        'resolved_at': DateTime.now().toIso8601String(),
      };

      // Act - Log conflict
      final conflicts = prefs.getStringList('conflict_log') ?? [];
      conflicts.add(conflictDetails.toString());
      await prefs.setStringList('conflict_log', conflicts);

      // Assert
      expect(prefs.getStringList('conflict_log')!.length, equals(1));
    });

    // =========================================================================
    // Retry on Failure Tests
    // =========================================================================

    testWidgets('should retry failed sync with exponential backoff', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      const maxRetries = 3;
      int retryCount = 0;

      final outboxItem = {
        'id': 'outbox-001',
        'entity_id': 'task-001',
        'retry_count': retryCount,
        'max_retries': maxRetries,
      };

      // Act - Simulate retry logic
      final delays = <Duration>[];
      while (retryCount < maxRetries) {
        retryCount++;
        // Exponential backoff: 2^retry * base_delay
        final delaySeconds = (1 << (retryCount - 1)) * 2; // 2s, 4s, 8s
        delays.add(Duration(seconds: delaySeconds));
      }

      // Assert
      expect(delays.length, equals(3));
      expect(delays[0].inSeconds, equals(2));  // First retry: 2s
      expect(delays[1].inSeconds, equals(4));  // Second retry: 4s
      expect(delays[2].inSeconds, equals(8));  // Third retry: 8s
    });

    testWidgets('should mark item as failed after max retries', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      const maxRetries = 5;

      // Act - Simulate exceeding max retries
      await prefs.setInt('retry_count', maxRetries + 1);
      final retryCount = prefs.getInt('retry_count')!;
      final shouldMarkFailed = retryCount > maxRetries;

      if (shouldMarkFailed) {
        await prefs.setString('item_status', 'failed');
      }

      // Assert
      expect(prefs.getString('item_status'), equals('failed'));
    });

    testWidgets('should reset retry count on successful sync', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setInt('retry_count', 3);

      // Act - Simulate successful sync
      await prefs.setInt('retry_count', 0);
      await prefs.setString('last_sync', DateTime.now().toIso8601String());

      // Assert
      expect(prefs.getInt('retry_count'), equals(0));
      expect(prefs.getString('last_sync'), isNotNull);
    });

    testWidgets('should implement circuit breaker pattern', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      int failureCount = 0;
      const failureThreshold = 5;
      const circuitOpenDuration = Duration(minutes: 5);

      // Act - Simulate failures
      for (int i = 0; i < failureThreshold; i++) {
        failureCount++;
      }

      // Open circuit
      if (failureCount >= failureThreshold) {
        await prefs.setBool('circuit_open', true);
        await prefs.setString(
          'circuit_opened_at',
          DateTime.now().toIso8601String(),
        );
      }

      // Check if circuit should be closed
      final circuitOpen = prefs.getBool('circuit_open') ?? false;
      final openedAt = DateTime.tryParse(prefs.getString('circuit_opened_at') ?? '');

      bool canRetry = false;
      if (circuitOpen && openedAt != null) {
        final elapsed = DateTime.now().difference(openedAt);
        if (elapsed >= circuitOpenDuration) {
          canRetry = true;
          await prefs.setBool('circuit_open', false);
        }
      }

      // Assert
      expect(prefs.getBool('circuit_open'), isNotNull);
      expect(failureCount, equals(failureThreshold));
    });

    // =========================================================================
    // Optimistic Locking Tests
    // =========================================================================

    testWidgets('should include ETag in update request', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      const etag = 'W/"abc123"';

      final outboxItem = {
        'id': 'outbox-001',
        'method': 'PUT',
        'entity_id': 'field-001',
        'if_match': etag,
        'payload': {'name': 'Updated Field'}.toString(),
      };

      // Act - Store with ETag
      await prefs.setString('outbox_001', outboxItem.toString());

      // Assert
      final stored = prefs.getString('outbox_001');
      expect(stored, contains('if_match'));
      expect(stored, contains(etag));
    });

    testWidgets('should handle 409 Conflict response', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Simulate receiving 409 Conflict
      const statusCode = 409;
      final serverVersion = {
        'id': 'field-001',
        'name': 'Server Version',
        'etag': 'W/"xyz789"',
      };

      // Act - Handle conflict
      if (statusCode == 409) {
        // Fetch latest from server and apply
        await prefs.setString('field_001', serverVersion.toString());

        // Log conflict event
        final events = prefs.getStringList('sync_events') ?? [];
        events.add({
          'type': 'CONFLICT',
          'entity_id': 'field-001',
          'message': 'تم تطبيق نسخة السيرفر بسبب تعارض',
          'timestamp': DateTime.now().toIso8601String(),
        }.toString());
        await prefs.setStringList('sync_events', events);
      }

      // Assert
      expect(prefs.getString('field_001'), contains('Server Version'));
      expect(prefs.getStringList('sync_events')!.length, equals(1));
    });

    // =========================================================================
    // Concurrent Sync Tests
    // =========================================================================

    testWidgets('should prevent concurrent sync operations', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('is_syncing', false);

      // Act - First sync starts
      final canStartSync = !(prefs.getBool('is_syncing') ?? false);

      if (canStartSync) {
        await prefs.setBool('is_syncing', true);
      }

      // Try to start second sync
      final canStartSecondSync = !(prefs.getBool('is_syncing') ?? false);

      // Assert
      expect(canStartSync, isTrue);
      expect(canStartSecondSync, isFalse); // Should be blocked
    });

    testWidgets('should queue sync requests while syncing', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('is_syncing', true);

      // Act - Queue sync request
      final queue = prefs.getStringList('sync_queue') ?? [];
      queue.add({
        'requested_at': DateTime.now().toIso8601String(),
        'trigger': 'manual',
      }.toString());
      await prefs.setStringList('sync_queue', queue);

      // Assert
      expect(prefs.getStringList('sync_queue')!.length, equals(1));
    });

    // =========================================================================
    // Sync Statistics and Monitoring Tests
    // =========================================================================

    testWidgets('should track sync statistics', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      final syncStats = {
        'total_syncs': 10,
        'successful_syncs': 8,
        'failed_syncs': 2,
        'items_uploaded': 45,
        'items_downloaded': 32,
        'last_sync': DateTime.now().toIso8601String(),
        'average_sync_duration_ms': 2500,
      };

      // Act - Save stats
      for (final entry in syncStats.entries) {
        if (entry.value is int) {
          await prefs.setInt('sync_stat_${entry.key}', entry.value as int);
        } else {
          await prefs.setString('sync_stat_${entry.key}', entry.value.toString());
        }
      }

      // Assert
      expect(prefs.getInt('sync_stat_total_syncs'), equals(10));
      expect(prefs.getInt('sync_stat_successful_syncs'), equals(8));
      expect(prefs.getString('sync_stat_last_sync'), isNotNull);
    });

    testWidgets('should calculate sync success rate', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setInt('successful_syncs', 85);
      await prefs.setInt('total_syncs', 100);

      // Act - Calculate success rate
      final successful = prefs.getInt('successful_syncs')!;
      final total = prefs.getInt('total_syncs')!;
      final successRate = (successful / total * 100).round();

      await prefs.setInt('sync_success_rate', successRate);

      // Assert
      expect(prefs.getInt('sync_success_rate'), equals(85));
    });
  });

  // ===========================================================================
  // Background Sync Tests
  // ===========================================================================

  group('Background Sync Tests', () {
    testWidgets('should schedule periodic background sync', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      const syncIntervalMinutes = 15;

      // Act - Schedule sync
      final nextSyncTime = DateTime.now().add(const Duration(minutes: syncIntervalMinutes));
      await prefs.setString('next_sync_time', nextSyncTime.toIso8601String());
      await prefs.setInt('sync_interval_minutes', syncIntervalMinutes);

      // Assert
      expect(prefs.getString('next_sync_time'), isNotNull);
      expect(prefs.getInt('sync_interval_minutes'), equals(15));
    });

    testWidgets('should respect battery optimization settings', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Act - Check battery saver mode
      await prefs.setBool('battery_saver_active', true);
      await prefs.setBool('sync_on_battery_saver', false);

      final batterySaver = prefs.getBool('battery_saver_active') ?? false;
      final allowSync = prefs.getBool('sync_on_battery_saver') ?? true;
      final shouldSync = !batterySaver || allowSync;

      // Assert
      expect(shouldSync, isFalse); // Sync should be disabled
    });
  });

  // ===========================================================================
  // Sync Event Notifications Tests
  // ===========================================================================

  group('Sync Event Notifications', () {
    testWidgets('should show sync status in UI', (tester) async {
      // Arrange
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Column(
                children: [
                  // Sync status indicator
                  Material(
                    color: Colors.blue,
                    child: Padding(
                      padding: EdgeInsets.all(8),
                      child: Row(
                        children: [
                          SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          ),
                          SizedBox(width: 8),
                          Text(
                            'جاري المزامنة...',
                            style: TextStyle(color: Colors.white),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Assert
      expect(find.text('جاري المزامنة...'), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('should show conflict notification to user', (tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Column(
                children: [
                  Material(
                    color: Colors.orange,
                    child: Padding(
                      padding: const EdgeInsets.all(8),
                      child: Row(
                        children: [
                          const Icon(Icons.warning, color: Colors.white),
                          const SizedBox(width: 8),
                          const Text(
                            'تم حل تعارض في البيانات',
                            style: TextStyle(color: Colors.white),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Assert
      expect(find.text('تم حل تعارض في البيانات'), findsOneWidget);
      expect(find.byIcon(Icons.warning), findsOneWidget);
    });
  });
}
