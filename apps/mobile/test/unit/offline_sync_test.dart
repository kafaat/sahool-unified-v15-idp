/// Offline Sync Unit Tests
/// اختبارات وحدة المزامنة دون اتصال
///
/// Tests the following offline-sync components:
/// - SyncPriority constants and ordering (migration_v5.dart)
/// - ExponentialBackoff policy (core/utils/retry_policy.dart)
/// - SyncConflictResolver strategies (core/offline/sync_conflict_resolver.dart)
/// - ETag-based optimistic locking (pure string logic)
/// - Sync queue item builder (pure logic)
/// - Sync statistics helpers (pure logic)
/// - Delta sync logic (pure logic)
/// - Offline operation queue ordering (pure logic)
///
/// Run with: flutter test test/unit/offline_sync_test.dart

import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/database/migrations/migration_v5.dart'
    show SyncPriority;
import 'package:sahool_field_app/core/utils/retry_policy.dart';
import 'package:sahool_field_app/core/offline/sync_conflict_resolver.dart';

void main() {
  // ============================================================
  // SyncPriority Tests
  // ============================================================
  group('SyncPriority - أولوية المزامنة', () {
    group('Priority Constants', () {
      test('low priority is 0', () {
        expect(SyncPriority.low, equals(0));
      });

      test('normal priority is 10', () {
        expect(SyncPriority.normal, equals(10));
      });

      test('high priority is 20', () {
        expect(SyncPriority.high, equals(20));
      });

      test('critical priority is 30', () {
        expect(SyncPriority.critical, equals(30));
      });

      test('priorities are correctly ordered', () {
        expect(SyncPriority.low, lessThan(SyncPriority.normal));
        expect(SyncPriority.normal, lessThan(SyncPriority.high));
        expect(SyncPriority.high, lessThan(SyncPriority.critical));
      });
    });

    group('forEntityType - Priority by Entity', () {
      test('field entity has HIGH priority', () {
        expect(SyncPriority.forEntityType('field'), equals(SyncPriority.high));
      });

      test('task entity has NORMAL priority', () {
        expect(SyncPriority.forEntityType('task'), equals(SyncPriority.normal));
      });

      test('sync_event entity has LOW priority', () {
        expect(
          SyncPriority.forEntityType('sync_event'),
          equals(SyncPriority.low),
        );
      });

      test('unknown entity types default to NORMAL priority', () {
        expect(SyncPriority.forEntityType('unknown'), equals(SyncPriority.normal));
        expect(SyncPriority.forEntityType(''), equals(SyncPriority.normal));
        expect(
          SyncPriority.forEntityType('some_custom_entity'),
          equals(SyncPriority.normal),
        );
        expect(
          SyncPriority.forEntityType('advisory'),
          equals(SyncPriority.normal),
        );
      });

      test('entity type matching is case insensitive', () {
        expect(SyncPriority.forEntityType('FIELD'), equals(SyncPriority.high));
        expect(SyncPriority.forEntityType('Field'), equals(SyncPriority.high));
        expect(SyncPriority.forEntityType('fIeLd'), equals(SyncPriority.high));
        expect(SyncPriority.forEntityType('TASK'), equals(SyncPriority.normal));
      });
    });

    group('forMethod - Priority by HTTP Method', () {
      test('DELETE operations have CRITICAL priority', () {
        expect(SyncPriority.forMethod('DELETE'), equals(SyncPriority.critical));
      });

      test('POST operations have HIGH priority', () {
        expect(SyncPriority.forMethod('POST'), equals(SyncPriority.high));
      });

      test('PUT operations have NORMAL priority', () {
        expect(SyncPriority.forMethod('PUT'), equals(SyncPriority.normal));
      });

      test('PATCH operations have NORMAL priority', () {
        expect(SyncPriority.forMethod('PATCH'), equals(SyncPriority.normal));
      });

      test('GET operations have LOW priority', () {
        expect(SyncPriority.forMethod('GET'), equals(SyncPriority.low));
      });

      test('method matching is case insensitive', () {
        expect(SyncPriority.forMethod('delete'), equals(SyncPriority.critical));
        expect(SyncPriority.forMethod('Delete'), equals(SyncPriority.critical));
        expect(SyncPriority.forMethod('post'), equals(SyncPriority.high));
        expect(SyncPriority.forMethod('put'), equals(SyncPriority.normal));
      });

      test('unknown methods default to NORMAL priority', () {
        expect(SyncPriority.forMethod('HEAD'), equals(SyncPriority.normal));
        expect(SyncPriority.forMethod('OPTIONS'), equals(SyncPriority.normal));
        expect(SyncPriority.forMethod('UNKNOWN'), equals(SyncPriority.normal));
      });
    });

    group('Priority Combination Logic', () {
      test('determines effective priority as max of entity and method priorities', () {
        // Field (high) + DELETE (critical) => critical
        final fieldDelete = [
          SyncPriority.forEntityType('field'),
          SyncPriority.forMethod('DELETE'),
        ].reduce((a, b) => a > b ? a : b);
        expect(fieldDelete, equals(SyncPriority.critical));

        // Task (normal) + POST (high) => high
        final taskPost = [
          SyncPriority.forEntityType('task'),
          SyncPriority.forMethod('POST'),
        ].reduce((a, b) => a > b ? a : b);
        expect(taskPost, equals(SyncPriority.high));

        // SyncEvent (low) + GET (low) => low
        final eventGet = [
          SyncPriority.forEntityType('sync_event'),
          SyncPriority.forMethod('GET'),
        ].reduce((a, b) => a > b ? a : b);
        expect(eventGet, equals(SyncPriority.low));
      });

      test('can be used to sort sync items correctly', () {
        final items = [
          {'priority': SyncPriority.forMethod('DELETE'), 'id': 'del1'},
          {'priority': SyncPriority.forEntityType('field'), 'id': 'field1'},
          {'priority': SyncPriority.forMethod('GET'), 'id': 'get1'},
          {'priority': SyncPriority.forMethod('POST'), 'id': 'post1'},
        ];

        // Sort descending by priority (highest first)
        items.sort((a, b) =>
            (b['priority'] as int).compareTo(a['priority'] as int));

        expect(items.first['id'], equals('del1')); // critical = 30
        expect(items.last['id'], equals('get1')); // low = 0
      });
    });
  });

  // ============================================================
  // Retry Logic Tests — uses production ExponentialBackoff
  // ============================================================
  group('Retry Logic - منطق إعادة المحاولة', () {
    late ExponentialBackoff backoff;

    setUp(() {
      // Disable jitter so delays are deterministic in tests
      backoff = ExponentialBackoff(
        initialDelayMs: 1000,
        multiplier: 2.0,
        maxDelayMs: 300000, // 300,000 ms = 5 minutes (production default)
        maxRetries: 5,
        enableJitter: false,
      );
    });

    test('calculateDelay returns initialDelayMs for retry 0', () {
      expect(backoff.calculateDelay(0), equals(1000));
    });

    test('calculateDelay doubles on each retry (exponential)', () {
      expect(backoff.calculateDelay(0), equals(1000)); // 1s
      expect(backoff.calculateDelay(1), equals(2000)); // 2s
      expect(backoff.calculateDelay(2), equals(4000)); // 4s
      expect(backoff.calculateDelay(3), equals(8000)); // 8s
      expect(backoff.calculateDelay(4), equals(16000)); // 16s
    });

    test('calculateDelay is capped at maxDelayMs (5 min default)', () {
      // At retry 9: 1000 * 2^9 = 512,000ms > 300,000ms → capped at 300,000ms
      expect(backoff.calculateDelay(9), equals(300000));
      expect(backoff.calculateDelay(20), equals(300000));
    });

    test('shouldRetry returns true while under maxRetries', () {
      expect(backoff.shouldRetry(0), isTrue);
      expect(backoff.shouldRetry(4), isTrue);
    });

    test('shouldRetry returns false at or above maxRetries', () {
      expect(backoff.shouldRetry(5), isFalse);
      expect(backoff.shouldRetry(10), isFalse);
    });

    test('calculateNextRetryTime is in the future', () {
      final before = DateTime.now();
      final nextRetry = backoff.calculateNextRetryTime(0);
      expect(nextRetry.isAfter(before), isTrue);
    });

    test('calculateNextRetryTime delay increases with retry count', () {
      final t0 = backoff.calculateNextRetryTime(0);
      final t1 = backoff.calculateNextRetryTime(1);
      final t2 = backoff.calculateNextRetryTime(2);
      expect(t1.isAfter(t0), isTrue);
      expect(t2.isAfter(t1), isTrue);
    });

    test('getDelayDescription returns human-readable string', () {
      final desc = backoff.getDelayDescription(0);
      expect(desc, isA<String>());
      expect(desc, isNotEmpty);
    });

    test('handles network timeout simulation', () {
      final errors = [
        'Connection timeout',
        'Network unreachable',
        'SSL handshake failed',
      ];

      for (final error in errors) {
        expect(
          () => throw Exception(error),
          throwsException,
          reason: 'Should throw for: $error',
        );
      }
    });
  });

  // ============================================================
  // ETag / Conflict Resolution Tests — uses SyncConflictResolver
  // ============================================================
  group('ETag Conflict Resolution - حل تعارضات ETag', () {
    late SyncConflictResolver resolver;

    setUp(() {
      resolver = SyncConflictResolver();
    });

    test('ETag comparison detects no conflict for same ETag', () {
      const localEtag = '"abc123"';
      const serverEtag = '"abc123"';
      expect(localEtag == serverEtag, isTrue);
    });

    test('ETag comparison detects conflict for different ETags', () {
      const localEtag = '"abc123"';
      const serverEtag = '"def456"';
      expect(localEtag == serverEtag, isFalse);
    });

    test('null ETag means no previous sync (safe to override)', () {
      const String? localEtag = null;
      final isFirstSync = localEtag == null;
      expect(isFirstSync, isTrue);
    });

    test('detectConflict returns false when the same field has the same value', () {
      final base = {'name': 'Field A', 'area': 5.0};
      final local = {'name': 'Field A updated', 'area': 5.0};
      final server = {'name': 'Field A updated', 'area': 5.0}; // identical change
      expect(
        resolver.detectConflict(local: local, server: server, base: base),
        isFalse,
      );
    });

    test('detectConflict returns true when both sides changed the same field differently', () {
      final base = {'name': 'Field A', 'area': 5.0};
      final local = {'name': 'Local Name', 'area': 5.0};
      final server = {'name': 'Server Name', 'area': 5.0};
      expect(
        resolver.detectConflict(local: local, server: server, base: base),
        isTrue,
      );
    });

    test('resolve with ConflictStrategy.localWins returns local data', () async {
      final base = {'name': 'Base', 'area': 5.0};
      final local = {'name': 'Local', 'area': 5.0};
      final server = {'name': 'Server', 'area': 6.0};

      final result = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.localWins,
      );

      expect(result, equals(local));
    });

    test('resolve with ConflictStrategy.serverWins returns server data', () async {
      final base = {'name': 'Base', 'area': 5.0};
      final local = {'name': 'Local', 'area': 5.0};
      final server = {'name': 'Server', 'area': 6.0};

      final result = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.serverWins,
      );

      expect(result, equals(server));
    });

    test('resolve with ConflictStrategy.lastWriteWins picks the newer record', () async {
      final base = {'name': 'Base', 'updatedAt': '2025-01-01T00:00:00Z'};
      final local = {'name': 'Local', 'updatedAt': '2025-01-15T10:00:00Z'};  // newer
      final server = {'name': 'Server', 'updatedAt': '2025-01-10T08:00:00Z'};

      final result = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.lastWriteWins,
      );

      expect(result, equals(local)); // local is more recent
    });

    test('generates If-Match header from ETag', () {
      const etag = '"abc123"';
      final headers = {'If-Match': etag};
      expect(headers['If-Match'], equals(etag));
    });

    test('weak ETags are different from strong ETags', () {
      const weakEtag = 'W/"abc123"';
      const strongEtag = '"abc123"';
      expect(weakEtag == strongEtag, isFalse);
      expect(weakEtag.startsWith('W/'), isTrue);
    });
  });

  // ============================================================
  // Sync Queue Item Builder (pure logic)
  // ============================================================
  group('Sync Queue Item Builder - بناء عناصر قائمة المزامنة', () {
    Map<String, dynamic> buildQueueItem({
      required String tenantId,
      required String entityType,
      required String entityId,
      required String apiEndpoint,
      String method = 'POST',
      required String payload,
      String? ifMatch,
      int retryCount = 0,
      int maxRetries = 5,
      int? priority,
    }) {
      return {
        'tenantId': tenantId,
        'entityType': entityType,
        'entityId': entityId,
        'apiEndpoint': apiEndpoint,
        'method': method,
        'payload': payload,
        'ifMatch': ifMatch,
        'retryCount': retryCount,
        'maxRetries': maxRetries,
        'priority': priority ??
            [
              SyncPriority.forEntityType(entityType),
              SyncPriority.forMethod(method),
            ].reduce((a, b) => a > b ? a : b),
        'isSynced': false,
        'createdAt': DateTime.now().toIso8601String(),
      };
    }

    test('builds field creation item with correct priority', () {
      final item = buildQueueItem(
        tenantId: 'tenant-1',
        entityType: 'field',
        entityId: 'field-123',
        apiEndpoint: '/api/v1/fields',
        method: 'POST',
        payload: '{"name": "Test Field", "area": 10.5}',
      );

      expect(item['tenantId'], equals('tenant-1'));
      expect(item['entityType'], equals('field'));
      expect(item['method'], equals('POST'));
      expect(item['isSynced'], isFalse);
      // field (high=20) + POST (high=20) => 20
      expect(item['priority'], equals(SyncPriority.high));
    });

    test('builds field deletion item with critical priority', () {
      final item = buildQueueItem(
        tenantId: 'tenant-1',
        entityType: 'field',
        entityId: 'field-123',
        apiEndpoint: '/api/v1/fields/field-123',
        method: 'DELETE',
        payload: '{}',
        ifMatch: '"abc123"',
      );

      // field (high=20) + DELETE (critical=30) => 30
      expect(item['priority'], equals(SyncPriority.critical));
      expect(item['ifMatch'], equals('"abc123"'));
    });

    test('builds item with default retry settings', () {
      final item = buildQueueItem(
        tenantId: 'tenant-1',
        entityType: 'task',
        entityId: 'task-1',
        apiEndpoint: '/api/v1/tasks',
        payload: '{"title": "Test"}',
      );

      expect(item['retryCount'], equals(0));
      expect(item['maxRetries'], equals(5));
    });

    test('builds JSON payload correctly', () {
      final payload = {
        'name': 'Test Field',
        'area': 10.5,
        'coordinates': [[44.0, 15.0], [44.1, 15.0]],
      };

      final item = buildQueueItem(
        tenantId: 'tenant-1',
        entityType: 'field',
        entityId: 'field-1',
        apiEndpoint: '/api/v1/fields',
        payload: jsonEncode(payload),
      );

      final decodedPayload =
          jsonDecode(item['payload'] as String) as Map<String, dynamic>;
      expect(decodedPayload['name'], equals('Test Field'));
      expect(decodedPayload['area'], equals(10.5));
    });
  });

  // ============================================================
  // Sync Statistics Tests (pure logic)
  // ============================================================
  group('Sync Statistics - إحصائيات المزامنة', () {
    test('calculates sync success rate', () {
      const total = 100;
      const failed = 15;
      const succeeded = total - failed;

      final successRate = succeeded / total;
      expect(successRate, equals(0.85));
    });

    test('calculates average sync duration', () {
      final durations = [100, 200, 150, 300, 250];
      final total = durations.fold(0, (sum, d) => sum + d);
      final avg = total / durations.length;
      expect(avg, equals(200.0));
    });

    test('identifies bottleneck entity types', () {
      final failuresByType = {
        'field': 5,
        'task': 10,
        'observation': 2,
        'irrigation': 8,
      };

      final sortedByFailures = failuresByType.entries.toList()
        ..sort((a, b) => b.value.compareTo(a.value));

      expect(sortedByFailures.first.key, equals('task'));
      expect(sortedByFailures.first.value, equals(10));
    });

    test('tracks pending items count correctly', () {
      final queue = <Map<String, dynamic>>[
        {'isSynced': false, 'entityType': 'field'},
        {'isSynced': true, 'entityType': 'field'},
        {'isSynced': false, 'entityType': 'task'},
        {'isSynced': false, 'entityType': 'task'},
        {'isSynced': true, 'entityType': 'observation'},
      ];

      final pending = queue.where((item) => item['isSynced'] == false).length;
      expect(pending, equals(3));

      final synced = queue.where((item) => item['isSynced'] == true).length;
      expect(synced, equals(2));
    });

    test('calculates items by entity type', () {
      final queue = <Map<String, dynamic>>[
        {'entityType': 'field'},
        {'entityType': 'field'},
        {'entityType': 'task'},
        {'entityType': 'field'},
        {'entityType': 'observation'},
      ];

      final byType = <String, int>{};
      for (final item in queue) {
        final type = item['entityType'] as String;
        byType[type] = (byType[type] ?? 0) + 1;
      }

      expect(byType['field'], equals(3));
      expect(byType['task'], equals(1));
      expect(byType['observation'], equals(1));
    });
  });

  // ============================================================
  // Delta Sync Logic Tests (pure logic)
  // ============================================================
  group('Delta Sync Logic - منطق المزامنة التدريجية', () {
    test('filters new items since last sync', () {
      final lastSyncTime = DateTime(2025, 1, 15, 10, 0, 0);
      final items = [
        {
          'id': '1',
          'updatedAt': DateTime(2025, 1, 14, 9, 0, 0).toIso8601String(),
        },
        {
          'id': '2',
          'updatedAt': DateTime(2025, 1, 15, 11, 0, 0).toIso8601String(),
        },
        {
          'id': '3',
          'updatedAt': DateTime(2025, 1, 16, 8, 0, 0).toIso8601String(),
        },
      ];

      final newItems = items.where((item) {
        final updatedAt = DateTime.parse(item['updatedAt']!);
        return updatedAt.isAfter(lastSyncTime);
      }).toList();

      expect(newItems.length, equals(2));
      expect(newItems.map((i) => i['id']).toList(), containsAll(['2', '3']));
    });

    test('identifies deleted items correctly', () {
      final localIds = {'field-1', 'field-2', 'field-3', 'field-4'};
      final serverIds = {'field-1', 'field-3'}; // field-2 and field-4 deleted

      final deletedIds = localIds.difference(serverIds);
      expect(deletedIds.length, equals(2));
      expect(deletedIds, contains('field-2'));
      expect(deletedIds, contains('field-4'));
    });

    test('identifies new server items to download', () {
      final localIds = {'field-1', 'field-2'};
      final serverIds = {'field-1', 'field-2', 'field-3', 'field-4'};

      final newServerIds = serverIds.difference(localIds);
      expect(newServerIds.length, equals(2));
      expect(newServerIds, contains('field-3'));
      expect(newServerIds, contains('field-4'));
    });

    test('identifies items to update (modified on server)', () {
      final localItems = [
        {'id': 'field-1', 'updatedAt': '2025-01-14T10:00:00Z'},
        {'id': 'field-2', 'updatedAt': '2025-01-15T10:00:00Z'},
      ];

      final serverItems = [
        {
          'id': 'field-1',
          'serverUpdatedAt': '2025-01-14T10:00:00Z',
        }, // Same - no update needed
        {
          'id': 'field-2',
          'serverUpdatedAt': '2025-01-16T10:00:00Z',
        }, // Newer - needs update
      ];

      final itemsToUpdate = serverItems.where((serverItem) {
        final local = localItems.firstWhere(
          (l) => l['id'] == serverItem['id'],
          orElse: () => {},
        );
        if (local.isEmpty) return true; // New item
        return serverItem['serverUpdatedAt']! != local['updatedAt']!;
      }).toList();

      expect(itemsToUpdate.length, equals(1));
      expect(itemsToUpdate.first['id'], equals('field-2'));
    });
  });

  // ============================================================
  // Offline Operation Queue Tests (pure logic)
  // ============================================================
  group('Offline Operation Queue - قائمة العمليات دون اتصال', () {
    test('orders operations by priority (highest first)', () {
      final operations = [
        {'id': '1', 'priority': SyncPriority.low},
        {'id': '2', 'priority': SyncPriority.critical},
        {'id': '3', 'priority': SyncPriority.normal},
        {'id': '4', 'priority': SyncPriority.high},
      ];

      operations
          .sort((a, b) => (b['priority'] as int).compareTo(a['priority'] as int));

      expect(operations[0]['id'], equals('2')); // critical = 30
      expect(operations[1]['id'], equals('4')); // high = 20
      expect(operations[2]['id'], equals('3')); // normal = 10
      expect(operations[3]['id'], equals('1')); // low = 0
    });

    test('limits queue size to max allowed', () {
      const maxQueueSize = 10;
      final queue = List.generate(
        15,
        (i) => {
          'id': 'op-$i',
          'priority': SyncPriority.normal,
        },
      );

      final limitedQueue =
          queue.take(maxQueueSize).toList();
      expect(limitedQueue.length, equals(maxQueueSize));
    });

    test('removes completed operations from queue', () {
      final queue = [
        {'id': '1', 'isSynced': true},
        {'id': '2', 'isSynced': false},
        {'id': '3', 'isSynced': true},
        {'id': '4', 'isSynced': false},
      ];

      final pending = queue.where((op) => op['isSynced'] == false).toList();
      expect(pending.length, equals(2));
      expect(pending.map((op) => op['id']).toList(), equals(['2', '4']));
    });

    test('handles empty queue gracefully', () {
      final queue = <Map<String, dynamic>>[];
      expect(queue.isEmpty, isTrue);
      expect(queue.where((op) => op['isSynced'] == false).isEmpty, isTrue);
    });

    test('calculates total payload size', () {
      final operations = [
        {'payload': jsonEncode({'name': 'Field 1', 'area': 5.0})},
        {'payload': jsonEncode({'name': 'Field 2', 'area': 8.5})},
        {'payload': jsonEncode({'title': 'Task 1', 'status': 'open'})},
      ];

      final totalSize = operations.fold(
          0,
          (sum, op) => sum + (op['payload'] as String).length);
      expect(totalSize, greaterThan(0));
    });
  });
}
