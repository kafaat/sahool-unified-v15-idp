import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/offline/sync_conflict_resolver.dart';

void main() {
  group('SyncConflictResolver', () {
    late SyncConflictResolver resolver;

    setUp(() {
      resolver = SyncConflictResolver();
    });

    group('detectConflict', () {
      test('should detect conflict when same field changed differently', () {
        // Arrange
        final base = {'name': 'Task 1', 'status': 'pending'};
        final local = {'name': 'Task 1 Updated', 'status': 'pending'};
        final server = {'name': 'Task 1 Modified', 'status': 'pending'};

        // Act
        final hasConflict = resolver.detectConflict(
          local: local,
          server: server,
          base: base,
        );

        // Assert
        expect(hasConflict, isTrue);
      });

      test('should not detect conflict when same field changed to same value', () {
        // Arrange
        final base = {'name': 'Task 1', 'status': 'pending'};
        final local = {'name': 'Task 1 Updated', 'status': 'pending'};
        final server = {'name': 'Task 1 Updated', 'status': 'pending'};

        // Act
        final hasConflict = resolver.detectConflict(
          local: local,
          server: server,
          base: base,
        );

        // Assert
        expect(hasConflict, isFalse);
      });

      test('should not detect conflict when different fields changed', () {
        // Arrange
        final base = {'name': 'Task 1', 'status': 'pending', 'priority': 'low'};
        final local = {'name': 'Task 1 Updated', 'status': 'pending', 'priority': 'low'};
        final server = {'name': 'Task 1', 'status': 'completed', 'priority': 'low'};

        // Act
        final hasConflict = resolver.detectConflict(
          local: local,
          server: server,
          base: base,
        );

        // Assert
        expect(hasConflict, isFalse);
      });

      test('should not detect conflict when no changes made', () {
        // Arrange
        final base = {'name': 'Task 1', 'status': 'pending'};
        final local = {'name': 'Task 1', 'status': 'pending'};
        final server = {'name': 'Task 1', 'status': 'pending'};

        // Act
        final hasConflict = resolver.detectConflict(
          local: local,
          server: server,
          base: base,
        );

        // Assert
        expect(hasConflict, isFalse);
      });
    });

    group('resolve - localWins', () {
      test('should return local data when strategy is localWins', () async {
        // Arrange
        final base = {'name': 'Task 1', 'status': 'pending'};
        final local = {'name': 'Task 1 Local', 'status': 'in_progress'};
        final server = {'name': 'Task 1 Server', 'status': 'completed'};

        // Act
        final resolved = await resolver.resolve(
          local: local,
          server: server,
          base: base,
          strategy: ConflictStrategy.localWins,
        );

        // Assert
        expect(resolved, equals(local));
        expect(resolved['name'], 'Task 1 Local');
        expect(resolved['status'], 'in_progress');
      });
    });

    group('resolve - serverWins', () {
      test('should return server data when strategy is serverWins', () async {
        // Arrange
        final base = {'name': 'Task 1', 'status': 'pending'};
        final local = {'name': 'Task 1 Local', 'status': 'in_progress'};
        final server = {'name': 'Task 1 Server', 'status': 'completed'};

        // Act
        final resolved = await resolver.resolve(
          local: local,
          server: server,
          base: base,
          strategy: ConflictStrategy.serverWins,
        );

        // Assert
        expect(resolved, equals(server));
        expect(resolved['name'], 'Task 1 Server');
        expect(resolved['status'], 'completed');
      });
    });

    group('resolve - lastWriteWins', () {
      test('should return local data when local is newer', () async {
        // Arrange
        final now = DateTime.now();
        final base = {'name': 'Task 1', 'updatedAt': now.subtract(const Duration(hours: 2)).toIso8601String()};
        final local = {'name': 'Task 1 Local', 'updatedAt': now.toIso8601String()};
        final server = {'name': 'Task 1 Server', 'updatedAt': now.subtract(const Duration(hours: 1)).toIso8601String()};

        // Act
        final resolved = await resolver.resolve(
          local: local,
          server: server,
          base: base,
          strategy: ConflictStrategy.lastWriteWins,
        );

        // Assert
        expect(resolved, equals(local));
        expect(resolved['name'], 'Task 1 Local');
      });

      test('should return server data when server is newer', () async {
        // Arrange
        final now = DateTime.now();
        final base = {'name': 'Task 1', 'updatedAt': now.subtract(const Duration(hours: 2)).toIso8601String()};
        final local = {'name': 'Task 1 Local', 'updatedAt': now.subtract(const Duration(hours: 1)).toIso8601String()};
        final server = {'name': 'Task 1 Server', 'updatedAt': now.toIso8601String()};

        // Act
        final resolved = await resolver.resolve(
          local: local,
          server: server,
          base: base,
          strategy: ConflictStrategy.lastWriteWins,
        );

        // Assert
        expect(resolved, equals(server));
        expect(resolved['name'], 'Task 1 Server');
      });

      test('should fallback to server when timestamps are missing', () async {
        // Arrange
        final base = {'name': 'Task 1'};
        final local = {'name': 'Task 1 Local'};
        final server = {'name': 'Task 1 Server'};

        // Act
        final resolved = await resolver.resolve(
          local: local,
          server: server,
          base: base,
          strategy: ConflictStrategy.lastWriteWins,
        );

        // Assert
        expect(resolved, equals(server));
      });
    });

    group('resolve - merge', () {
      test('should merge local and server changes', () async {
        // Arrange
        final base = {'name': 'Task 1', 'status': 'pending', 'priority': 'low'};
        final local = {'name': 'Task 1 Updated', 'status': 'pending', 'priority': 'low'};
        final server = {'name': 'Task 1', 'status': 'in_progress', 'priority': 'low'};

        // Act
        final resolved = await resolver.resolve(
          local: local,
          server: server,
          base: base,
          strategy: ConflictStrategy.merge,
        );

        // Assert
        expect(resolved['name'], 'Task 1 Updated'); // Local change
        expect(resolved['status'], 'in_progress'); // Server change overwritten by local
        expect(resolved['priority'], 'low'); // Unchanged
      });

      test('should handle field deletions in merge', () async {
        // Arrange
        final base = {'name': 'Task 1', 'status': 'pending', 'description': 'Old description'};
        final local = {'name': 'Task 1', 'status': 'pending'}; // description deleted
        final server = {'name': 'Task 1', 'status': 'completed', 'description': 'Old description'};

        // Act
        final resolved = await resolver.resolve(
          local: local,
          server: server,
          base: base,
          strategy: ConflictStrategy.merge,
        );

        // Assert
        expect(resolved.containsKey('description'), isFalse);
      });

      test('should handle new field additions in merge', () async {
        // Arrange
        final base = {'name': 'Task 1'};
        final local = {'name': 'Task 1', 'priority': 'high'};
        final server = {'name': 'Task 1', 'status': 'completed'};

        // Act
        final resolved = await resolver.resolve(
          local: local,
          server: server,
          base: base,
          strategy: ConflictStrategy.merge,
        );

        // Assert
        expect(resolved['priority'], 'high'); // Local addition
        expect(resolved['status'], 'completed'); // Server addition
      });
    });

    group('resolve - custom', () {
      test('should use custom resolver when provided', () async {
        // Arrange
        final base = {'name': 'Task 1'};
        final local = {'name': 'Task 1 Local'};
        final server = {'name': 'Task 1 Server'};

        Future<Map<String, dynamic>> customResolver(
          Map<String, dynamic> local,
          Map<String, dynamic> server,
          Map<String, dynamic> base,
        ) async {
          return {'name': 'Custom Resolution'};
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
        expect(resolved['name'], 'Custom Resolution');
      });

      test('should fallback to server when custom resolver is null', () async {
        // Arrange
        final base = {'name': 'Task 1'};
        final local = {'name': 'Task 1 Local'};
        final server = {'name': 'Task 1 Server'};

        // Act
        final resolved = await resolver.resolve(
          local: local,
          server: server,
          base: base,
          strategy: ConflictStrategy.custom,
        );

        // Assert
        expect(resolved, equals(server));
      });
    });

    group('resolveListConflict', () {
      test('should merge items from both lists', () {
        // Arrange
        final local = [
          {'id': '1', 'name': 'Item 1 Local'},
          {'id': '2', 'name': 'Item 2'},
          {'id': '3', 'name': 'Item 3 Local'},
        ];

        final server = [
          {'id': '1', 'name': 'Item 1 Server'},
          {'id': '2', 'name': 'Item 2'},
          {'id': '4', 'name': 'Item 4 Server'},
        ];

        // Act
        final resolved = resolver.resolveListConflict<Map<String, dynamic>>(
          local: local,
          server: server,
          getId: (item) => item['id'] as String,
          mergeItem: (local, server) => local, // Local wins
        );

        // Assert
        expect(resolved.length, 4); // 4 unique items
        expect(resolved.where((i) => i['id'] == '1').first['name'], 'Item 1 Local');
        expect(resolved.where((i) => i['id'] == '3').first['name'], 'Item 3 Local');
        expect(resolved.where((i) => i['id'] == '4').first['name'], 'Item 4 Server');
      });

      test('should keep server-only items', () {
        // Arrange
        final local = [
          {'id': '1', 'name': 'Item 1'},
        ];

        final server = [
          {'id': '1', 'name': 'Item 1'},
          {'id': '2', 'name': 'Item 2 Server'},
          {'id': '3', 'name': 'Item 3 Server'},
        ];

        // Act
        final resolved = resolver.resolveListConflict<Map<String, dynamic>>(
          local: local,
          server: server,
          getId: (item) => item['id'] as String,
          mergeItem: (local, server) => server,
        );

        // Assert
        expect(resolved.length, 3);
        expect(resolved.any((i) => i['id'] == '2'), isTrue);
        expect(resolved.any((i) => i['id'] == '3'), isTrue);
      });

      test('should keep local-only items', () {
        // Arrange
        final local = [
          {'id': '1', 'name': 'Item 1'},
          {'id': '2', 'name': 'Item 2 Local'},
          {'id': '3', 'name': 'Item 3 Local'},
        ];

        final server = [
          {'id': '1', 'name': 'Item 1'},
        ];

        // Act
        final resolved = resolver.resolveListConflict<Map<String, dynamic>>(
          local: local,
          server: server,
          getId: (item) => item['id'] as String,
          mergeItem: (local, server) => local,
        );

        // Assert
        expect(resolved.length, 3);
        expect(resolved.any((i) => i['id'] == '2'), isTrue);
        expect(resolved.any((i) => i['id'] == '3'), isTrue);
      });
    });
  });

  group('ConflictDetails', () {
    test('should create conflict details with all fields', () {
      // Act
      final details = ConflictDetails(
        entityType: 'task',
        entityId: 'task_123',
        local: {'name': 'Local'},
        server: {'name': 'Server'},
        base: {'name': 'Base'},
        conflictingFields: {'name'},
        detectedAt: DateTime.now(),
      );

      // Assert
      expect(details.entityType, 'task');
      expect(details.entityId, 'task_123');
      expect(details.conflictingFields, contains('name'));
    });
  });

  group('ConflictResolution', () {
    test('should create conflict resolution with all fields', () {
      // Arrange
      final conflict = ConflictDetails(
        entityType: 'task',
        entityId: 'task_123',
        local: {'name': 'Local'},
        server: {'name': 'Server'},
        base: {'name': 'Base'},
        conflictingFields: {'name'},
        detectedAt: DateTime.now(),
      );

      // Act
      final resolution = ConflictResolution(
        conflict: conflict,
        strategy: ConflictStrategy.serverWins,
        resolvedData: {'name': 'Server'},
        resolvedAt: DateTime.now(),
        resolvedBy: 'system',
      );

      // Assert
      expect(resolution.strategy, ConflictStrategy.serverWins);
      expect(resolution.resolvedBy, 'system');
      expect(resolution.resolvedData['name'], 'Server');
    });
  });
}
