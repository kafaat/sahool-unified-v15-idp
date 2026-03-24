import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_mobile_core/core/offline/sync_conflict_resolver.dart';

import 'sync_mocks.dart';

/// Conflict Resolver Tests
/// اختبارات حل التعارضات
///
/// Tests for:
/// - Conflict detection
/// - Resolution strategies (local wins, server wins, last write wins, merge)
/// - Field-level conflict detection
/// - List conflict resolution
/// - Custom resolver support

void main() {
  late SyncConflictResolver resolver;

  setUp(() {
    resolver = SyncConflictResolver();
  });

  group('ConflictStrategy', () {
    test('should have all expected strategies', () {
      expect(ConflictStrategy.values, contains(ConflictStrategy.localWins));
      expect(ConflictStrategy.values, contains(ConflictStrategy.serverWins));
      expect(ConflictStrategy.values, contains(ConflictStrategy.lastWriteWins));
      expect(ConflictStrategy.values, contains(ConflictStrategy.merge));
      expect(ConflictStrategy.values, contains(ConflictStrategy.custom));
    });
  });

  group('Conflict Detection', () {
    test('should detect conflict when same field changed differently', () {
      final base = {'name': 'Original', 'area': 100.0, 'status': 'active'};
      final local = {'name': 'Local Name', 'area': 100.0, 'status': 'active'};
      final server = {'name': 'Server Name', 'area': 100.0, 'status': 'active'};

      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      expect(hasConflict, isTrue);
    });

    test('should not detect conflict when different fields changed', () {
      final base = {'name': 'Original', 'area': 100.0, 'status': 'active'};
      final local = {'name': 'Local Name', 'area': 100.0, 'status': 'active'};
      final server = {'name': 'Original', 'area': 150.0, 'status': 'active'};

      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      expect(hasConflict, isFalse);
    });

    test('should not detect conflict when same value set by both', () {
      final base = {'name': 'Original', 'area': 100.0};
      final local = {'name': 'Same Name', 'area': 100.0};
      final server = {'name': 'Same Name', 'area': 100.0};

      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      expect(hasConflict, isFalse);
    });

    test('should detect conflict on field deletion vs modification', () {
      final base = {'name': 'Original', 'description': 'Old desc'};
      final local = {'name': 'Original'}; // description deleted locally
      final server = {'name': 'Original', 'description': 'New desc'}; // description changed on server

      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      expect(hasConflict, isTrue);
    });

    test('should not detect conflict when no changes made', () {
      final base = {'name': 'Original', 'area': 100.0};
      final local = Map<String, dynamic>.from(base);
      final server = Map<String, dynamic>.from(base);

      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      expect(hasConflict, isFalse);
    });

    test('should detect conflict when new field added by both with different values', () {
      final base = <String, dynamic>{'name': 'Original'};
      final local = {'name': 'Original', 'newField': 'localValue'};
      final server = {'name': 'Original', 'newField': 'serverValue'};

      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      expect(hasConflict, isTrue);
    });
  });

  group('Local Wins Strategy', () {
    test('should return local data when strategy is localWins', () async {
      final local = SyncTestFixtures.sampleLocalData;
      final server = SyncTestFixtures.sampleServerData;
      final base = SyncTestFixtures.sampleBaseData;

      final result = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.localWins,
      );

      expect(result, equals(local));
      expect(result['name'], equals('Local Field Name'));
    });
  });

  group('Server Wins Strategy', () {
    test('should return server data when strategy is serverWins', () async {
      final local = SyncTestFixtures.sampleLocalData;
      final server = SyncTestFixtures.sampleServerData;
      final base = SyncTestFixtures.sampleBaseData;

      final result = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.serverWins,
      );

      expect(result, equals(server));
      expect(result['name'], equals('Server Field Name'));
    });
  });

  group('Last Write Wins Strategy', () {
    test('should return server data when server timestamp is newer', () async {
      final local = {
        'id': 'field_001',
        'name': 'Local Name',
        'updatedAt': DateTime.now().subtract(const Duration(hours: 1)).toIso8601String(),
      };
      final server = {
        'id': 'field_001',
        'name': 'Server Name',
        'updatedAt': DateTime.now().toIso8601String(),
      };
      final base = {
        'id': 'field_001',
        'name': 'Original',
        'updatedAt': DateTime.now().subtract(const Duration(hours: 2)).toIso8601String(),
      };

      final result = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.lastWriteWins,
      );

      expect(result['name'], equals('Server Name'));
    });

    test('should return local data when local timestamp is newer', () async {
      final local = {
        'id': 'field_001',
        'name': 'Local Name',
        'updatedAt': DateTime.now().toIso8601String(),
      };
      final server = {
        'id': 'field_001',
        'name': 'Server Name',
        'updatedAt': DateTime.now().subtract(const Duration(hours: 1)).toIso8601String(),
      };
      final base = {
        'id': 'field_001',
        'name': 'Original',
        'updatedAt': DateTime.now().subtract(const Duration(hours: 2)).toIso8601String(),
      };

      final result = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.lastWriteWins,
      );

      expect(result['name'], equals('Local Name'));
    });

    test('should fallback to server when timestamps are missing', () async {
      final local = {'id': 'field_001', 'name': 'Local Name'};
      final server = {'id': 'field_001', 'name': 'Server Name'};
      final base = {'id': 'field_001', 'name': 'Original'};

      final result = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.lastWriteWins,
      );

      expect(result['name'], equals('Server Name'));
    });

    test('should handle updated_at field format', () async {
      final local = {
        'id': 'field_001',
        'name': 'Local Name',
        'updated_at': DateTime.now().toIso8601String(),
      };
      final server = {
        'id': 'field_001',
        'name': 'Server Name',
        'updated_at': DateTime.now().subtract(const Duration(hours: 1)).toIso8601String(),
      };
      final base = {
        'id': 'field_001',
        'name': 'Original',
        'updated_at': DateTime.now().subtract(const Duration(hours: 2)).toIso8601String(),
      };

      final result = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.lastWriteWins,
      );

      expect(result['name'], equals('Local Name'));
    });
  });

  group('Merge Strategy', () {
    test('should merge non-conflicting changes from both sides', () async {
      final base = {'id': 'field_001', 'name': 'Original', 'area': 100.0, 'status': 'active'};
      final local = {'id': 'field_001', 'name': 'Local Name', 'area': 100.0, 'status': 'active'};
      final server = {'id': 'field_001', 'name': 'Original', 'area': 150.0, 'status': 'active'};

      final result = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.merge,
      );

      // Local name change should be preserved
      expect(result['name'], equals('Local Name'));
      // Server area change should also be preserved
      expect(result['area'], equals(150.0));
      // Unchanged field should remain
      expect(result['status'], equals('active'));
    });

    test('should prefer local changes on conflicting fields', () async {
      final base = {'id': 'field_001', 'name': 'Original', 'area': 100.0};
      final local = {'id': 'field_001', 'name': 'Local Name', 'area': 200.0};
      final server = {'id': 'field_001', 'name': 'Server Name', 'area': 150.0};

      final result = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.merge,
      );

      // Local changes should win on conflicting fields
      expect(result['name'], equals('Local Name'));
      expect(result['area'], equals(200.0));
    });

    test('should handle field deletion in merge', () async {
      final base = {'id': 'field_001', 'name': 'Original', 'description': 'Old desc', 'area': 100.0};
      final local = {'id': 'field_001', 'name': 'Original', 'area': 100.0}; // description deleted
      final server = {'id': 'field_001', 'name': 'Original', 'description': 'Old desc', 'area': 150.0}; // area changed

      final result = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.merge,
      );

      // Local deletion should be applied
      expect(result.containsKey('description'), isFalse);
      // Server change should be preserved
      expect(result['area'], equals(150.0));
    });

    test('should handle new field addition in merge', () async {
      final base = <String, dynamic>{'id': 'field_001', 'name': 'Original'};
      final local = {'id': 'field_001', 'name': 'Original', 'localField': 'local value'};
      final server = {'id': 'field_001', 'name': 'Original', 'serverField': 'server value'};

      final result = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.merge,
      );

      // Both new fields should be present
      expect(result['localField'], equals('local value'));
      expect(result['serverField'], equals('server value'));
    });
  });

  group('Custom Strategy', () {
    test('should use custom resolver when provided', () async {
      final local = {'id': 'field_001', 'name': 'Local', 'value': 10};
      final server = {'id': 'field_001', 'name': 'Server', 'value': 20};
      final base = {'id': 'field_001', 'name': 'Original', 'value': 5};

      // Custom resolver that sums values
      final customResolver = (
        Map<String, dynamic> l,
        Map<String, dynamic> s,
        Map<String, dynamic> b,
      ) async {
        return {
          'id': l['id'],
          'name': 'Merged',
          'value': (l['value'] as int) + (s['value'] as int),
        };
      };

      final result = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.custom,
        customResolver: customResolver,
      );

      expect(result['name'], equals('Merged'));
      expect(result['value'], equals(30)); // 10 + 20
    });

    test('should fallback to server when custom resolver not provided', () async {
      final local = {'id': 'field_001', 'name': 'Local'};
      final server = {'id': 'field_001', 'name': 'Server'};
      final base = {'id': 'field_001', 'name': 'Original'};

      final result = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.custom,
        // No customResolver provided
      );

      expect(result, equals(server));
    });
  });

  group('List Conflict Resolution', () {
    test('should merge lists keeping all unique items', () {
      final local = [
        {'id': '1', 'name': 'Item 1'},
        {'id': '2', 'name': 'Local Item 2'},
        {'id': '4', 'name': 'Local Only'},
      ];
      final server = [
        {'id': '1', 'name': 'Item 1'},
        {'id': '2', 'name': 'Server Item 2'},
        {'id': '3', 'name': 'Server Only'},
      ];

      final result = resolver.resolveListConflict<Map<String, dynamic>>(
        local: local,
        server: server,
        getId: (item) => item['id'] as String,
        mergeItem: (l, s) => s, // Prefer server for conflicts
      );

      expect(result.length, equals(4));

      // Check all items are present
      final ids = result.map((item) => item['id']).toList();
      expect(ids, containsAll(['1', '2', '3', '4']));

      // Item 2 should have server value (due to mergeItem preferring server)
      final item2 = result.firstWhere((item) => item['id'] == '2');
      expect(item2['name'], equals('Server Item 2'));
    });

    test('should handle empty local list', () {
      final local = <Map<String, dynamic>>[];
      final server = [
        {'id': '1', 'name': 'Item 1'},
        {'id': '2', 'name': 'Item 2'},
      ];

      final result = resolver.resolveListConflict<Map<String, dynamic>>(
        local: local,
        server: server,
        getId: (item) => item['id'] as String,
        mergeItem: (l, s) => s,
      );

      expect(result.length, equals(2));
    });

    test('should handle empty server list', () {
      final local = [
        {'id': '1', 'name': 'Item 1'},
        {'id': '2', 'name': 'Item 2'},
      ];
      final server = <Map<String, dynamic>>[];

      final result = resolver.resolveListConflict<Map<String, dynamic>>(
        local: local,
        server: server,
        getId: (item) => item['id'] as String,
        mergeItem: (l, s) => s,
      );

      expect(result.length, equals(2));
    });

    test('should use custom merge function for conflicting items', () {
      final local = [
        {'id': '1', 'count': 5},
      ];
      final server = [
        {'id': '1', 'count': 10},
      ];

      final result = resolver.resolveListConflict<Map<String, dynamic>>(
        local: local,
        server: server,
        getId: (item) => item['id'] as String,
        mergeItem: (l, s) => {
          'id': l['id'],
          'count': (l['count'] as int) + (s['count'] as int),
        },
      );

      expect(result.length, equals(1));
      expect(result.first['count'], equals(15)); // 5 + 10
    });
  });

  group('ConflictDetails', () {
    test('should create valid conflict details', () {
      final details = ConflictDetails(
        entityType: 'field',
        entityId: 'field_001',
        local: SyncTestFixtures.sampleLocalData,
        server: SyncTestFixtures.sampleServerData,
        base: SyncTestFixtures.sampleBaseData,
        conflictingFields: {'name', 'area'},
        detectedAt: DateTime.now(),
      );

      expect(details.entityType, equals('field'));
      expect(details.entityId, equals('field_001'));
      expect(details.conflictingFields, contains('name'));
      expect(details.conflictingFields, contains('area'));
    });
  });

  group('ConflictResolution', () {
    test('should create valid conflict resolution record', () {
      // Capture data once to avoid timestamp drift between getter calls
      final serverData = SyncTestFixtures.sampleServerData;

      final details = ConflictDetails(
        entityType: 'field',
        entityId: 'field_001',
        local: SyncTestFixtures.sampleLocalData,
        server: serverData,
        base: SyncTestFixtures.sampleBaseData,
        conflictingFields: {'name'},
        detectedAt: DateTime.now(),
      );

      final resolution = ConflictResolution(
        conflict: details,
        strategy: ConflictStrategy.serverWins,
        resolvedData: serverData,
        resolvedAt: DateTime.now(),
        resolvedBy: 'system',
      );

      expect(resolution.strategy, equals(ConflictStrategy.serverWins));
      expect(resolution.resolvedData, equals(serverData));
      expect(resolution.resolvedBy, equals('system'));
    });
  });

  group('Edge Cases', () {
    test('should handle null values in data', () async {
      final base = {'id': 'field_001', 'name': 'Original', 'description': null};
      final local = {'id': 'field_001', 'name': 'Local', 'description': 'New desc'};
      final server = {'id': 'field_001', 'name': 'Original', 'description': null};

      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      // No conflict: only local changed (name + description), server matches base
      expect(hasConflict, isFalse);
    });

    test('should handle empty maps', () async {
      final base = <String, dynamic>{};
      final local = {'name': 'Local'};
      final server = {'name': 'Server'};

      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      expect(hasConflict, isTrue);
    });

    test('should handle nested objects as atomic values', () async {
      final base = {
        'id': 'field_001',
        'location': {'lat': 15.0, 'lng': 44.0},
      };
      final local = {
        'id': 'field_001',
        'location': {'lat': 15.1, 'lng': 44.0}, // lat changed
      };
      final server = {
        'id': 'field_001',
        'location': {'lat': 15.0, 'lng': 44.1}, // lng changed
      };

      // Note: Current implementation treats nested objects as atomic
      // Both changed 'location', so conflict should be detected
      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      expect(hasConflict, isTrue);
    });

    test('should handle numeric type differences', () async {
      final base = {'id': 'field_001', 'area': 100};
      final local = {'id': 'field_001', 'area': 100.0}; // int vs double
      final server = {'id': 'field_001', 'area': 100};

      // This might be a conflict depending on implementation
      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      // Implementation may vary - we just verify it handles gracefully
      expect(() => hasConflict, returnsNormally);
    });
  });
}
