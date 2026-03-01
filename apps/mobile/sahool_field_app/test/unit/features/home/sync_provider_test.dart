import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/home/logic/sync_provider.dart';

void main() {
  // ═════════════════════════════════════════════════════════════════════════════
  // SyncStatus Enum Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('SyncStatus enum', () {
    test('has exactly 3 values', () {
      expect(SyncStatus.values.length, 3);
    });

    test('contains synced, syncing, offline', () {
      expect(SyncStatus.values, contains(SyncStatus.synced));
      expect(SyncStatus.values, contains(SyncStatus.syncing));
      expect(SyncStatus.values, contains(SyncStatus.offline));
    });

    test('synced has index 0', () {
      expect(SyncStatus.synced.index, 0);
    });

    test('syncing has index 1', () {
      expect(SyncStatus.syncing.index, 1);
    });

    test('offline has index 2', () {
      expect(SyncStatus.offline.index, 2);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // SyncStatusExtension Tests (Arabic Labels)
  // ═════════════════════════════════════════════════════════════════════════════

  group('SyncStatusExtension Arabic labels', () {
    test('synced label is Arabic for synced', () {
      expect(SyncStatus.synced.label, 'متزامن');
    });

    test('syncing label is Arabic for syncing', () {
      expect(SyncStatus.syncing.label, 'جاري المزامنة...');
    });

    test('offline label is Arabic for offline', () {
      expect(SyncStatus.offline.label, 'غير متصل');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // SyncStatusExtension Tests (English Labels)
  // ═════════════════════════════════════════════════════════════════════════════

  group('SyncStatusExtension English labels', () {
    test('synced labelEn is Synced', () {
      expect(SyncStatus.synced.labelEn, 'Synced');
    });

    test('syncing labelEn is Syncing...', () {
      expect(SyncStatus.syncing.labelEn, 'Syncing...');
    });

    test('offline labelEn is Offline', () {
      expect(SyncStatus.offline.labelEn, 'Offline');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // SyncStatus bilingual consistency tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('SyncStatus bilingual consistency', () {
    test('every status has both Arabic and English labels', () {
      for (final status in SyncStatus.values) {
        expect(status.label, isNotEmpty,
            reason: '${status.name} should have an Arabic label');
        expect(status.labelEn, isNotEmpty,
            reason: '${status.name} should have an English label');
      }
    });

    test('Arabic and English labels differ for all statuses', () {
      for (final status in SyncStatus.values) {
        expect(status.label, isNot(equals(status.labelEn)),
            reason:
                '${status.name} Arabic and English labels should be different');
      }
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // isOnlineProvider Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('isOnlineProvider', () {
    test('defaults to true (online)', () {
      // Arrange
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Act
      final isOnline = container.read(isOnlineProvider);

      // Assert
      expect(isOnline, isTrue);
    });

    test('can be toggled to offline', () {
      // Arrange
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Act
      container.read(isOnlineProvider.notifier).state = false;

      // Assert
      expect(container.read(isOnlineProvider), isFalse);
    });

    test('can be toggled back to online', () {
      // Arrange
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Act
      container.read(isOnlineProvider.notifier).state = false;
      container.read(isOnlineProvider.notifier).state = true;

      // Assert
      expect(container.read(isOnlineProvider), isTrue);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // SyncStatus state transitions
  // ═════════════════════════════════════════════════════════════════════════════

  group('SyncStatus state transitions (manual via StateProvider)', () {
    test('simulates synced -> syncing -> synced cycle', () {
      // Arrange: create a standalone StateProvider for testing the pattern
      final testSyncStatus = StateProvider<SyncStatus>(
        (ref) => SyncStatus.synced,
      );
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Act & Assert: initial state
      expect(container.read(testSyncStatus), SyncStatus.synced);

      // Transition to syncing
      container.read(testSyncStatus.notifier).state = SyncStatus.syncing;
      expect(container.read(testSyncStatus), SyncStatus.syncing);

      // Transition back to synced
      container.read(testSyncStatus.notifier).state = SyncStatus.synced;
      expect(container.read(testSyncStatus), SyncStatus.synced);
    });

    test('simulates synced -> offline -> syncing -> synced cycle', () {
      // Arrange
      final testSyncStatus = StateProvider<SyncStatus>(
        (ref) => SyncStatus.synced,
      );
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Assert initial state
      expect(container.read(testSyncStatus), SyncStatus.synced);

      // Go offline
      container.read(testSyncStatus.notifier).state = SyncStatus.offline;
      expect(container.read(testSyncStatus), SyncStatus.offline);

      // Start syncing (came back online)
      container.read(testSyncStatus.notifier).state = SyncStatus.syncing;
      expect(container.read(testSyncStatus), SyncStatus.syncing);

      // Finish syncing
      container.read(testSyncStatus.notifier).state = SyncStatus.synced;
      expect(container.read(testSyncStatus), SyncStatus.synced);
    });

    test('offline state has correct labels during offline scenario', () {
      final testSyncStatus = StateProvider<SyncStatus>(
        (ref) => SyncStatus.synced,
      );
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Go offline
      container.read(testSyncStatus.notifier).state = SyncStatus.offline;
      final offlineStatus = container.read(testSyncStatus);

      expect(offlineStatus.label, 'غير متصل');
      expect(offlineStatus.labelEn, 'Offline');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // Provider type validation
  // ═════════════════════════════════════════════════════════════════════════════

  group('Provider types', () {
    test('isOnlineProvider is a StateProvider<bool>', () {
      // Verify type at compile time and runtime
      expect(isOnlineProvider, isA<StateProvider<bool>>());
    });

    test('pendingOperationsProvider is a FutureProvider<int>', () {
      expect(pendingOperationsProvider, isA<FutureProvider<int>>());
    });

    test('syncStatusUiProvider is a StateProvider<SyncStatus>', () {
      expect(syncStatusUiProvider, isA<StateProvider<SyncStatus>>());
    });
  });
}
