/// SyncPriority Enum & OutboxEntry Serialization Tests
/// اختبارات enum أولوية المزامنة و تسلسل عناصر صندوق الصادر
///
/// These tests verify:
/// - All SyncPriority enum values exist and are correctly ordered
/// - OutboxEntry JSON serialization/deserialization with all priority levels
/// - Priority index stability for persistent storage compatibility
/// - Edge cases for enum access patterns used in repository files
///
/// Run with: flutter test test/unit/core/sync_priority_enum_test.dart
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/offline/offline_sync_engine.dart';

void main() {
  // ============================================================
  // SyncPriority Enum Values
  // ============================================================
  group('SyncPriority Enum - قيم أولوية المزامنة', () {
    test('has all 5 priority levels', () {
      expect(SyncPriority.values.length, equals(5));
    });

    test('low value exists', () {
      expect(SyncPriority.low, isNotNull);
      expect(SyncPriority.low.name, equals('low'));
    });

    test('normal value exists', () {
      expect(SyncPriority.normal, isNotNull);
      expect(SyncPriority.normal.name, equals('normal'));
    });

    test('medium value exists', () {
      expect(SyncPriority.medium, isNotNull);
      expect(SyncPriority.medium.name, equals('medium'));
    });

    test('high value exists', () {
      expect(SyncPriority.high, isNotNull);
      expect(SyncPriority.high.name, equals('high'));
    });

    test('critical value exists', () {
      expect(SyncPriority.critical, isNotNull);
      expect(SyncPriority.critical.name, equals('critical'));
    });

    test('enum values are in correct ascending order', () {
      expect(SyncPriority.low.index, lessThan(SyncPriority.normal.index));
      expect(SyncPriority.normal.index, lessThan(SyncPriority.medium.index));
      expect(SyncPriority.medium.index, lessThan(SyncPriority.high.index));
      expect(SyncPriority.high.index, lessThan(SyncPriority.critical.index));
    });

    test('enum indices are stable for serialization', () {
      // These indices are used in OutboxEntry.toJson()/fromJson()
      // Changing them would break persisted outbox data
      expect(SyncPriority.low.index, equals(0));
      expect(SyncPriority.normal.index, equals(1));
      expect(SyncPriority.medium.index, equals(2));
      expect(SyncPriority.high.index, equals(3));
      expect(SyncPriority.critical.index, equals(4));
    });

    test('values list contains all members in order', () {
      expect(SyncPriority.values, [
        SyncPriority.low,
        SyncPriority.normal,
        SyncPriority.medium,
        SyncPriority.high,
        SyncPriority.critical,
      ]);
    });

    test('can be looked up by index (used in OutboxEntry.fromJson)', () {
      expect(SyncPriority.values[0], equals(SyncPriority.low));
      expect(SyncPriority.values[1], equals(SyncPriority.normal));
      expect(SyncPriority.values[2], equals(SyncPriority.medium));
      expect(SyncPriority.values[3], equals(SyncPriority.high));
      expect(SyncPriority.values[4], equals(SyncPriority.critical));
    });

    test('can be looked up by name', () {
      expect(SyncPriority.values.byName('low'), equals(SyncPriority.low));
      expect(SyncPriority.values.byName('normal'), equals(SyncPriority.normal));
      expect(SyncPriority.values.byName('medium'), equals(SyncPriority.medium));
      expect(SyncPriority.values.byName('high'), equals(SyncPriority.high));
      expect(SyncPriority.values.byName('critical'), equals(SyncPriority.critical));
    });
  });

  // ============================================================
  // OutboxEntry Serialization
  // ============================================================
  group('OutboxEntry Serialization - تسلسل عناصر صندوق الصادر', () {
    OutboxEntry _createEntry({
      required SyncPriority priority,
      String entityType = 'test_entity',
      String? entityId = 'entity-1',
      SyncOperation operation = SyncOperation.create,
    }) {
      return OutboxEntry(
        id: 'test-id-123',
        entityType: entityType,
        entityId: entityId,
        operation: operation,
        data: {'key': 'value', 'count': 42},
        priority: priority,
        createdAt: DateTime.utc(2026, 3, 30, 12, 0, 0),
        status: OutboxStatus.pending,
      );
    }

    test('serializes low priority correctly', () {
      final entry = _createEntry(priority: SyncPriority.low);
      final json = entry.toJson();
      expect(json['priority'], equals(0));

      final restored = OutboxEntry.fromJson(json);
      expect(restored.priority, equals(SyncPriority.low));
    });

    test('serializes normal priority correctly', () {
      final entry = _createEntry(priority: SyncPriority.normal);
      final json = entry.toJson();
      expect(json['priority'], equals(1));

      final restored = OutboxEntry.fromJson(json);
      expect(restored.priority, equals(SyncPriority.normal));
    });

    test('serializes medium priority correctly', () {
      final entry = _createEntry(priority: SyncPriority.medium);
      final json = entry.toJson();
      expect(json['priority'], equals(2));

      final restored = OutboxEntry.fromJson(json);
      expect(restored.priority, equals(SyncPriority.medium));
    });

    test('serializes high priority correctly', () {
      final entry = _createEntry(priority: SyncPriority.high);
      final json = entry.toJson();
      expect(json['priority'], equals(3));

      final restored = OutboxEntry.fromJson(json);
      expect(restored.priority, equals(SyncPriority.high));
    });

    test('serializes critical priority correctly', () {
      final entry = _createEntry(priority: SyncPriority.critical);
      final json = entry.toJson();
      expect(json['priority'], equals(4));

      final restored = OutboxEntry.fromJson(json);
      expect(restored.priority, equals(SyncPriority.critical));
    });

    test('full roundtrip preserves all fields', () {
      final entry = OutboxEntry(
        id: 'roundtrip-id',
        entityType: 'equipment',
        entityId: 'eq-42',
        operation: SyncOperation.update,
        data: {'name': 'Tractor', 'status': 'active'},
        previousData: {'name': 'Old Tractor'},
        priority: SyncPriority.medium,
        createdAt: DateTime.utc(2026, 3, 30, 14, 30, 0),
        status: OutboxStatus.pending,
        retryCount: 2,
        lastError: 'Timeout',
      );

      final json = entry.toJson();
      final restored = OutboxEntry.fromJson(json);

      expect(restored.id, equals(entry.id));
      expect(restored.entityType, equals(entry.entityType));
      expect(restored.entityId, equals(entry.entityId));
      expect(restored.operation, equals(entry.operation));
      expect(restored.data, equals(entry.data));
      expect(restored.previousData, equals(entry.previousData));
      expect(restored.priority, equals(SyncPriority.medium));
      expect(restored.status, equals(entry.status));
      expect(restored.retryCount, equals(entry.retryCount));
      expect(restored.lastError, equals(entry.lastError));
    });
  });

  // ============================================================
  // OutboxEntry.copyWith
  // ============================================================
  group('OutboxEntry.copyWith - نسخ مع تعديل', () {
    test('can change priority to medium', () {
      final entry = OutboxEntry(
        id: 'copy-test',
        entityType: 'crm',
        operation: SyncOperation.create,
        data: {'type': 'farmer'},
        priority: SyncPriority.normal,
        createdAt: DateTime.now(),
        status: OutboxStatus.pending,
      );

      final updated = entry.copyWith(priority: SyncPriority.medium);
      expect(updated.priority, equals(SyncPriority.medium));
      expect(updated.id, equals(entry.id)); // other fields preserved
    });
  });

  // ============================================================
  // Priority Sorting (as used in OutboxRepository)
  // ============================================================
  group('Priority Sorting - ترتيب حسب الأولوية', () {
    test('sorts entries by priority descending (critical first)', () {
      final now = DateTime.now();
      final entries = [
        OutboxEntry(
          id: 'low',
          entityType: 'test',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.low,
          createdAt: now,
          status: OutboxStatus.pending,
        ),
        OutboxEntry(
          id: 'critical',
          entityType: 'test',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.critical,
          createdAt: now,
          status: OutboxStatus.pending,
        ),
        OutboxEntry(
          id: 'medium',
          entityType: 'test',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.medium,
          createdAt: now,
          status: OutboxStatus.pending,
        ),
        OutboxEntry(
          id: 'high',
          entityType: 'test',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.high,
          createdAt: now,
          status: OutboxStatus.pending,
        ),
        OutboxEntry(
          id: 'normal',
          entityType: 'test',
          operation: SyncOperation.create,
          data: {},
          priority: SyncPriority.normal,
          createdAt: now,
          status: OutboxStatus.pending,
        ),
      ];

      // Sort by priority descending (matches OutboxRepository._sortByPriority)
      entries.sort((a, b) => b.priority.index.compareTo(a.priority.index));

      expect(entries[0].id, equals('critical'));
      expect(entries[1].id, equals('high'));
      expect(entries[2].id, equals('medium'));
      expect(entries[3].id, equals('normal'));
      expect(entries[4].id, equals('low'));
    });
  });

  // ============================================================
  // SyncOperation & OutboxStatus Enums (completeness)
  // ============================================================
  group('SyncOperation Enum - عمليات المزامنة', () {
    test('has create, update, delete values', () {
      expect(SyncOperation.values.length, equals(3));
      expect(SyncOperation.create, isNotNull);
      expect(SyncOperation.update, isNotNull);
      expect(SyncOperation.delete, isNotNull);
    });
  });

  group('OutboxStatus Enum - حالات صندوق الصادر', () {
    test('has pending, processing, completed, failed values', () {
      expect(OutboxStatus.values.length, equals(4));
      expect(OutboxStatus.pending, isNotNull);
      expect(OutboxStatus.processing, isNotNull);
      expect(OutboxStatus.completed, isNotNull);
      expect(OutboxStatus.failed, isNotNull);
    });
  });

  group('SyncStatus Enum - حالات المزامنة', () {
    test('has all status values', () {
      expect(SyncStatus.values.length, equals(6));
      expect(SyncStatus.idle, isNotNull);
      expect(SyncStatus.syncing, isNotNull);
      expect(SyncStatus.success, isNotNull);
      expect(SyncStatus.partialSuccess, isNotNull);
      expect(SyncStatus.error, isNotNull);
      expect(SyncStatus.offline, isNotNull);
    });
  });
}
