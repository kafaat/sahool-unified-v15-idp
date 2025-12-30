/// Unit Tests - Sync Conflict Resolver
/// اختبارات وحدة - حل تعارضات المزامنة

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/offline/sync_conflict_resolver.dart';

void main() {
  late SyncConflictResolver resolver;

  setUp(() {
    resolver = SyncConflictResolver();
  });

  group('Conflict Detection', () {
    test('should detect no conflict when data is identical', () {
      // Arrange
      final base = {'id': '1', 'name': 'Field A', 'area': 100.0};
      final local = {'id': '1', 'name': 'Field A', 'area': 100.0};
      final server = {'id': '1', 'name': 'Field A', 'area': 100.0};

      // Act
      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      // Assert
      expect(hasConflict, isFalse);
    });

    test('should detect no conflict when only local changed', () {
      // Arrange
      final base = {'id': '1', 'name': 'Field A', 'area': 100.0};
      final local = {'id': '1', 'name': 'Field A Updated', 'area': 100.0};
      final server = {'id': '1', 'name': 'Field A', 'area': 100.0};

      // Act
      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      // Assert
      expect(hasConflict, isFalse);
    });

    test('should detect no conflict when only server changed', () {
      // Arrange
      final base = {'id': '1', 'name': 'Field A', 'area': 100.0};
      final local = {'id': '1', 'name': 'Field A', 'area': 100.0};
      final server = {'id': '1', 'name': 'Field A', 'area': 150.0};

      // Act
      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      // Assert
      expect(hasConflict, isFalse);
    });

    test('should detect conflict when same field changed differently', () {
      // Arrange
      final base = {'id': '1', 'name': 'Field A', 'area': 100.0};
      final local = {'id': '1', 'name': 'Field A Local', 'area': 100.0};
      final server = {'id': '1', 'name': 'Field A Server', 'area': 100.0};

      // Act
      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      // Assert
      expect(hasConflict, isTrue);
    });

    test('should detect conflict when same field has different values', () {
      // Arrange
      final base = {'id': '1', 'area': 100.0, 'crop': 'wheat'};
      final local = {'id': '1', 'area': 150.0, 'crop': 'wheat'};
      final server = {'id': '1', 'area': 200.0, 'crop': 'wheat'};

      // Act
      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      // Assert
      expect(hasConflict, isTrue);
    });

    test('should not detect conflict when different fields changed', () {
      // Arrange
      final base = {'id': '1', 'name': 'Field', 'area': 100.0, 'crop': 'wheat'};
      final local = {'id': '1', 'name': 'Field Updated', 'area': 100.0, 'crop': 'wheat'};
      final server = {'id': '1', 'name': 'Field', 'area': 150.0, 'crop': 'wheat'};

      // Act
      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      // Assert
      expect(hasConflict, isFalse);
    });

    test('should detect conflict with field deletion', () {
      // Arrange
      final base = {'id': '1', 'name': 'Field', 'description': 'Test'};
      final local = {'id': '1', 'name': 'Field', 'description': 'Updated locally'};
      final server = {'id': '1', 'name': 'Field'}; // description removed

      // Act
      final hasConflict = resolver.detectConflict(
        local: local,
        server: server,
        base: base,
      );

      // Assert
      expect(hasConflict, isTrue);
    });
  });

  group('Local Wins Strategy', () {
    test('should return local data when strategy is localWins', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Base'};
      final local = {'id': '1', 'name': 'Local Version'};
      final server = {'id': '1', 'name': 'Server Version'};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.localWins,
      );

      // Assert
      expect(resolved['name'], equals('Local Version'));
    });

    test('should preserve all local fields with localWins', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Base', 'area': 100.0};
      final local = {'id': '1', 'name': 'Local', 'area': 150.0, 'crop': 'wheat'};
      final server = {'id': '1', 'name': 'Server', 'area': 200.0};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.localWins,
      );

      // Assert
      expect(resolved['name'], equals('Local'));
      expect(resolved['area'], equals(150.0));
      expect(resolved['crop'], equals('wheat'));
    });
  });

  group('Server Wins Strategy', () {
    test('should return server data when strategy is serverWins', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Base'};
      final local = {'id': '1', 'name': 'Local Version'};
      final server = {'id': '1', 'name': 'Server Version'};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.serverWins,
      );

      // Assert
      expect(resolved['name'], equals('Server Version'));
    });

    test('should preserve all server fields with serverWins', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Base'};
      final local = {'id': '1', 'name': 'Local', 'extra': 'data'};
      final server = {'id': '1', 'name': 'Server', 'area': 200.0};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.serverWins,
      );

      // Assert
      expect(resolved['name'], equals('Server'));
      expect(resolved['area'], equals(200.0));
      expect(resolved.containsKey('extra'), isFalse);
    });
  });

  group('Last Write Wins Strategy', () {
    test('should use local when local is newer', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Base'};
      final local = {
        'id': '1',
        'name': 'Local',
        'updatedAt': DateTime.now().toIso8601String(),
      };
      final server = {
        'id': '1',
        'name': 'Server',
        'updatedAt': DateTime.now().subtract(const Duration(hours: 1)).toIso8601String(),
      };

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.lastWriteWins,
      );

      // Assert
      expect(resolved['name'], equals('Local'));
    });

    test('should use server when server is newer', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Base'};
      final local = {
        'id': '1',
        'name': 'Local',
        'updatedAt': DateTime.now().subtract(const Duration(hours: 1)).toIso8601String(),
      };
      final server = {
        'id': '1',
        'name': 'Server',
        'updatedAt': DateTime.now().toIso8601String(),
      };

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.lastWriteWins,
      );

      // Assert
      expect(resolved['name'], equals('Server'));
    });

    test('should handle updated_at field (snake_case)', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Base'};
      final local = {
        'id': '1',
        'name': 'Local',
        'updated_at': DateTime.now().toIso8601String(),
      };
      final server = {
        'id': '1',
        'name': 'Server',
        'updated_at': DateTime.now().subtract(const Duration(hours: 1)).toIso8601String(),
      };

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.lastWriteWins,
      );

      // Assert
      expect(resolved['name'], equals('Local'));
    });

    test('should fallback to server when timestamps missing', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Base'};
      final local = {'id': '1', 'name': 'Local'};
      final server = {'id': '1', 'name': 'Server'};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.lastWriteWins,
      );

      // Assert
      expect(resolved['name'], equals('Server'));
    });

    test('should handle DateTime objects directly', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Base'};
      final local = {
        'id': '1',
        'name': 'Local',
        'updatedAt': DateTime.now(),
      };
      final server = {
        'id': '1',
        'name': 'Server',
        'updatedAt': DateTime.now().subtract(const Duration(hours: 1)),
      };

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.lastWriteWins,
      );

      // Assert
      expect(resolved['name'], equals('Local'));
    });
  });

  group('Merge Strategy', () {
    test('should merge non-conflicting changes', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Field', 'area': 100.0, 'crop': 'wheat'};
      final local = {'id': '1', 'name': 'Field Updated', 'area': 100.0, 'crop': 'wheat'};
      final server = {'id': '1', 'name': 'Field', 'area': 150.0, 'crop': 'wheat'};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.merge,
      );

      // Assert
      expect(resolved['name'], equals('Field Updated')); // Local change
      expect(resolved['area'], equals(150.0)); // Server change
    });

    test('should prefer local on conflicting fields', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Base Name'};
      final local = {'id': '1', 'name': 'Local Name'};
      final server = {'id': '1', 'name': 'Server Name'};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.merge,
      );

      // Assert - Local should win in merge strategy
      expect(resolved['name'], equals('Local Name'));
    });

    test('should add server-only fields', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Field'};
      final local = {'id': '1', 'name': 'Field'};
      final server = {'id': '1', 'name': 'Field', 'new_field': 'server value'};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.merge,
      );

      // Assert
      expect(resolved['new_field'], equals('server value'));
    });

    test('should add local-only fields', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Field'};
      final local = {'id': '1', 'name': 'Field', 'local_field': 'local value'};
      final server = {'id': '1', 'name': 'Field'};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.merge,
      );

      // Assert
      expect(resolved['local_field'], equals('local value'));
    });

    test('should handle field deletions in merge', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Field', 'temp': 'value'};
      final local = {'id': '1', 'name': 'Field'}; // temp removed locally
      final server = {'id': '1', 'name': 'Field', 'temp': 'value'};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.merge,
      );

      // Assert - Local deletion should be preserved
      expect(resolved.containsKey('temp'), isFalse);
    });

    test('should merge complex nested changes', () async {
      // Arrange
      final base = {
        'id': '1',
        'name': 'Field',
        'metadata': {'created': '2024-01-01'},
      };

      final local = {
        'id': '1',
        'name': 'Field Updated',
        'metadata': {'created': '2024-01-01'},
      };

      final server = {
        'id': '1',
        'name': 'Field',
        'metadata': {'created': '2024-01-01', 'verified': true},
      };

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.merge,
      );

      // Assert
      expect(resolved['name'], equals('Field Updated'));
      // Note: Nested merge would need deeper implementation
    });
  });

  group('Custom Strategy', () {
    test('should use custom resolver when provided', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Base'};
      final local = {'id': '1', 'name': 'Local'};
      final server = {'id': '1', 'name': 'Server'};

      // Custom resolver that always returns a specific value
      Future<Map<String, dynamic>> customResolver(
        Map<String, dynamic> local,
        Map<String, dynamic> server,
        Map<String, dynamic> base,
      ) async {
        return {'id': '1', 'name': 'Custom Resolution'};
      }

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.custom,
        customResolver: customResolver,
      );

      // Assert
      expect(resolved['name'], equals('Custom Resolution'));
    });

    test('should fallback to serverWins when no custom resolver', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Base'};
      final local = {'id': '1', 'name': 'Local'};
      final server = {'id': '1', 'name': 'Server'};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.custom,
        // No custom resolver provided
      );

      // Assert
      expect(resolved['name'], equals('Server'));
    });

    test('should handle async custom resolver', () async {
      // Arrange
      final base = {'id': '1', 'value': 10};
      final local = {'id': '1', 'value': 20};
      final server = {'id': '1', 'value': 30};

      // Custom resolver with async operation
      Future<Map<String, dynamic>> asyncResolver(
        Map<String, dynamic> local,
        Map<String, dynamic> server,
        Map<String, dynamic> base,
      ) async {
        await Future.delayed(const Duration(milliseconds: 10));
        // Take average
        final avg = ((local['value'] as int) + (server['value'] as int)) ~/ 2;
        return {'id': '1', 'value': avg};
      }

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.custom,
        customResolver: asyncResolver,
      );

      // Assert
      expect(resolved['value'], equals(25));
    });
  });

  group('List Conflict Resolution', () {
    test('should merge lists with no conflicts', () {
      // Arrange
      final local = [
        {'id': '1', 'name': 'Item 1'},
        {'id': '2', 'name': 'Item 2 Local'},
      ];

      final server = [
        {'id': '1', 'name': 'Item 1'},
        {'id': '3', 'name': 'Item 3'},
      ];

      // Act
      final resolved = resolver.resolveListConflict<Map<String, dynamic>>(
        local: local,
        server: server,
        getId: (item) => item['id'] as String,
        mergeItem: (local, server) => local, // Simple merge
      );

      // Assert
      expect(resolved.length, equals(3));
      expect(resolved.any((item) => item['id'] == '1'), isTrue);
      expect(resolved.any((item) => item['id'] == '2'), isTrue);
      expect(resolved.any((item) => item['id'] == '3'), isTrue);
    });

    test('should merge conflicting items in list', () {
      // Arrange
      final local = [
        {'id': '1', 'name': 'Local Name', 'value': 100},
      ];

      final server = [
        {'id': '1', 'name': 'Server Name', 'value': 200},
      ];

      // Act
      final resolved = resolver.resolveListConflict<Map<String, dynamic>>(
        local: local,
        server: server,
        getId: (item) => item['id'] as String,
        mergeItem: (local, server) {
          return {
            'id': local['id'],
            'name': local['name'], // Prefer local name
            'value': server['value'], // Prefer server value
          };
        },
      );

      // Assert
      expect(resolved.length, equals(1));
      expect(resolved[0]['name'], equals('Local Name'));
      expect(resolved[0]['value'], equals(200));
    });

    test('should preserve local-only items', () {
      // Arrange
      final local = [
        {'id': '1', 'name': 'Item 1'},
        {'id': '2', 'name': 'Local Only'},
      ];

      final server = [
        {'id': '1', 'name': 'Item 1'},
      ];

      // Act
      final resolved = resolver.resolveListConflict<Map<String, dynamic>>(
        local: local,
        server: server,
        getId: (item) => item['id'] as String,
        mergeItem: (local, server) => server,
      );

      // Assert
      expect(resolved.length, equals(2));
      expect(resolved.any((item) => item['id'] == '2'), isTrue);
    });

    test('should add server-only items', () {
      // Arrange
      final local = [
        {'id': '1', 'name': 'Item 1'},
      ];

      final server = [
        {'id': '1', 'name': 'Item 1'},
        {'id': '2', 'name': 'Server Only'},
      ];

      // Act
      final resolved = resolver.resolveListConflict<Map<String, dynamic>>(
        local: local,
        server: server,
        getId: (item) => item['id'] as String,
        mergeItem: (local, server) => server,
      );

      // Assert
      expect(resolved.length, equals(2));
      expect(resolved.any((item) => item['id'] == '2'), isTrue);
      expect(
        resolved.firstWhere((item) => item['id'] == '2')['name'],
        equals('Server Only'),
      );
    });

    test('should handle empty lists', () {
      // Arrange
      final local = <Map<String, dynamic>>[];
      final server = [
        {'id': '1', 'name': 'Item 1'},
      ];

      // Act
      final resolved = resolver.resolveListConflict<Map<String, dynamic>>(
        local: local,
        server: server,
        getId: (item) => item['id'] as String,
        mergeItem: (local, server) => server,
      );

      // Assert
      expect(resolved.length, equals(1));
    });

    test('should handle large lists efficiently', () {
      // Arrange
      final local = List.generate(
        100,
        (i) => {'id': 'item_$i', 'name': 'Local $i'},
      );

      final server = List.generate(
        100,
        (i) => {'id': 'item_${i + 50}', 'name': 'Server ${i + 50}'},
      );

      // Act
      final stopwatch = Stopwatch()..start();
      final resolved = resolver.resolveListConflict<Map<String, dynamic>>(
        local: local,
        server: server,
        getId: (item) => item['id'] as String,
        mergeItem: (local, server) => local,
      );
      stopwatch.stop();

      // Assert
      expect(resolved.length, equals(150));
      expect(stopwatch.elapsedMilliseconds, lessThan(100)); // Should be fast
    });
  });

  group('Edge Cases', () {
    test('should handle null values in fields', () async {
      // Arrange
      final base = {'id': '1', 'name': 'Field', 'description': 'Test'};
      final local = {'id': '1', 'name': 'Field', 'description': null};
      final server = {'id': '1', 'name': 'Field', 'description': 'Updated'};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.merge,
      );

      // Assert - Local null should be preserved
      expect(resolved['description'], isNull);
    });

    test('should handle empty maps', () async {
      // Arrange
      final base = <String, dynamic>{};
      final local = <String, dynamic>{};
      final server = <String, dynamic>{};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.merge,
      );

      // Assert
      expect(resolved, isEmpty);
    });

    test('should handle maps with only id field', () async {
      // Arrange
      final base = {'id': '1'};
      final local = {'id': '1'};
      final server = {'id': '1'};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.serverWins,
      );

      // Assert
      expect(resolved['id'], equals('1'));
    });

    test('should handle very long string values', () async {
      // Arrange
      final longString = 'x' * 10000;
      final base = {'id': '1', 'data': 'short'};
      final local = {'id': '1', 'data': longString};
      final server = {'id': '1', 'data': 'short'};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.localWins,
      );

      // Assert
      expect(resolved['data'], equals(longString));
    });

    test('should handle numeric types correctly', () async {
      // Arrange
      final base = {'id': '1', 'intValue': 10, 'doubleValue': 10.0};
      final local = {'id': '1', 'intValue': 20, 'doubleValue': 20.5};
      final server = {'id': '1', 'intValue': 30, 'doubleValue': 30.0};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.localWins,
      );

      // Assert
      expect(resolved['intValue'], equals(20));
      expect(resolved['doubleValue'], equals(20.5));
    });

    test('should handle boolean values', () async {
      // Arrange
      final base = {'id': '1', 'active': false};
      final local = {'id': '1', 'active': true};
      final server = {'id': '1', 'active': false};

      // Act
      final resolved = await resolver.resolve(
        local: local,
        server: server,
        base: base,
        strategy: ConflictStrategy.localWins,
      );

      // Assert
      expect(resolved['active'], isTrue);
    });
  });
}
