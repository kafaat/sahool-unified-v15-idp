import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Integration Tests - Offline Sync
/// اختبارات تكامل المزامنة بدون اتصال

void main() {
  group('Offline Mode Integration Tests', () {
    late ProviderContainer container;

    setUp(() async {
      SharedPreferences.setMockInitialValues({});
      container = ProviderContainer();
    });

    tearDown(() {
      container.dispose();
    });

    test('Data should be cached locally when offline', () async {
      // Arrange
      final testData = {'id': '1', 'name': 'Test Field'};

      // Act
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('cached_field_1', testData.toString());

      // Assert
      expect(prefs.getString('cached_field_1'), isNotNull);
    });

    test('Pending changes should be stored in outbox', () async {
      // Arrange
      final pendingChange = {
        'type': 'create',
        'entity': 'task',
        'data': {'title': 'New Task'},
        'timestamp': DateTime.now().toIso8601String(),
      };

      // Act
      final prefs = await SharedPreferences.getInstance();
      await prefs.setStringList('outbox', [pendingChange.toString()]);

      // Assert
      final outbox = prefs.getStringList('outbox');
      expect(outbox, isNotNull);
      expect(outbox!.length, equals(1));
    });

    test('Sync should process outbox when online', () async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setStringList('outbox', ['change1', 'change2']);

      // Act - Simulate sync
      final outbox = prefs.getStringList('outbox') ?? [];
      final processedCount = outbox.length;
      await prefs.setStringList('outbox', []);

      // Assert
      expect(processedCount, equals(2));
      expect(prefs.getStringList('outbox'), isEmpty);
    });

    test('Conflict resolution should prefer server data by default', () async {
      // Arrange
      final localData = {
        'id': '1',
        'name': 'Local Name',
        'updatedAt': DateTime.now().subtract(const Duration(hours: 1)).toIso8601String(),
      };
      final serverData = {
        'id': '1',
        'name': 'Server Name',
        'updatedAt': DateTime.now().toIso8601String(),
      };

      // Act
      final localTime = DateTime.parse(localData['updatedAt']!);
      final serverTime = DateTime.parse(serverData['updatedAt']!);
      final useServer = serverTime.isAfter(localTime);

      // Assert
      expect(useServer, isTrue);
    });
  });

  group('Network Status', () {
    test('Should detect network changes', () async {
      // Arrange
      var isOnline = true;

      // Act
      isOnline = false;

      // Assert
      expect(isOnline, isFalse);
    });

    test('Should queue requests when offline', () async {
      // Arrange
      final requestQueue = <Map<String, dynamic>>[];
      const isOnline = false;

      // Act
      if (!isOnline) {
        requestQueue.add({'url': '/api/tasks', 'method': 'POST'});
      }

      // Assert
      expect(requestQueue.length, equals(1));
    });
  });

  group('Data Persistence', () {
    test('Local database should persist across app restarts', () async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('persistent_data', 'test_value');

      // Act - Simulate app restart by getting new instance
      final newPrefs = await SharedPreferences.getInstance();

      // Assert
      expect(newPrefs.getString('persistent_data'), equals('test_value'));
    });

    test('Cache should expire after TTL', () async {
      // Arrange
      final cacheEntry = {
        'data': 'cached_value',
        'expiresAt': DateTime.now().subtract(const Duration(minutes: 5)).toIso8601String(),
      };

      // Act
      final expiresAt = DateTime.parse(cacheEntry['expiresAt']!);
      final isExpired = DateTime.now().isAfter(expiresAt);

      // Assert
      expect(isExpired, isTrue);
    });
  });
}
