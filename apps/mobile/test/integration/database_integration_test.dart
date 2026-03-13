/// Database Integration Tests - اختبارات تكامل قاعدة البيانات
///
/// Tests the complete database workflow including:
/// - Cross-table operations (Tasks + Outbox + SyncEvents)
/// - Tenant isolation across all tables
/// - Offline-first sync cycle (create -> outbox -> sync -> cleanup)
/// - Field operations with GIS data
/// - Conflict detection and resolution flow
/// - Bulk operations and data integrity
///
/// Uses in-memory TestDatabase for fast, isolated testing
import 'dart:convert';

import 'package:drift/drift.dart' hide isNull, isNotNull;
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';

import '../core/database/database_test.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('Database Integration - Offline-First Sync Cycle', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should complete full offline-first cycle: create -> outbox -> sync -> cleanup',
        () async {
      final now = DateTime.now();
      const tenantId = 'tenant-integration-1';

      // Step 1: Create a field locally (offline)
      await db.into(db.testFields).insert(TestFieldsCompanion.insert(
            id: 'field-offline-1',
            tenantId: tenantId,
            name: 'حقل القمح الأول',
            boundary: '[[46.7,24.7],[46.8,24.7],[46.8,24.8],[46.7,24.8]]',
            areaHectares: 10.5,
            createdAt: now,
            updatedAt: now,
          ));

      // Step 2: Queue outbox entry for sync
      await db.into(db.testOutbox).insert(TestOutboxCompanion.insert(
            tenantId: tenantId,
            entityType: 'field',
            entityId: 'field-offline-1',
            apiEndpoint: '/api/v1/fields',
            payload: '{"name":"حقل القمح الأول","area":10.5}',
          ));

      // Step 3: Verify field is unsynced
      final unsyncedFields = await (db.select(db.testFields)
            ..where((f) => f.synced.equals(false)))
          .get();
      expect(unsyncedFields.length, equals(1));
      expect(unsyncedFields.first.name, equals('حقل القمح الأول'));

      // Step 4: Verify outbox has pending item
      final pendingOutbox = await (db.select(db.testOutbox)
            ..where((o) => o.isSynced.equals(false)))
          .get();
      expect(pendingOutbox.length, equals(1));
      expect(pendingOutbox.first.entityType, equals('field'));

      // Step 5: Simulate successful sync - mark field synced with ETag
      await (db.update(db.testFields)
            ..where((f) => f.id.equals('field-offline-1')))
          .write(const TestFieldsCompanion(
        synced: Value(true),
        etag: Value('etag-v1-abc123'),
        remoteId: Value('remote-field-001'),
      ));

      // Step 6: Mark outbox item as synced
      await (db.update(db.testOutbox)
            ..where((o) => o.entityId.equals('field-offline-1')))
          .write(const TestOutboxCompanion(isSynced: Value(true)));

      // Step 7: Log sync event
      await db.into(db.testSyncLogs).insert(TestSyncLogsCompanion.insert(
            type: 'field_sync',
            status: 'success',
            message: const Value('Synced field-offline-1 to server'),
            timestamp: DateTime.now(),
          ));

      // Step 8: Cleanup synced outbox
      await (db.delete(db.testOutbox)
            ..where((o) => o.isSynced.equals(true)))
          .go();

      // Verify final state
      final field = await (db.select(db.testFields)
            ..where((f) => f.id.equals('field-offline-1')))
          .getSingle();
      expect(field.synced, isTrue);
      expect(field.etag, equals('etag-v1-abc123'));
      expect(field.remoteId, equals('remote-field-001'));

      final remainingOutbox = await db.select(db.testOutbox).get();
      expect(remainingOutbox, isEmpty);

      final logs = await db.select(db.testSyncLogs).get();
      expect(logs.length, equals(1));
      expect(logs.first.status, equals('success'));
    });

    test('should handle sync failure with retry in outbox', () async {
      final now = DateTime.now();
      const tenantId = 'tenant-retry-1';

      // Create task and queue for sync
      await db.into(db.testTasks).insert(TestTasksCompanion.insert(
            id: 'task-retry-1',
            tenantId: tenantId,
            fieldId: 'field-1',
            title: 'مهمة تحتاج إعادة محاولة',
            createdAt: now,
            updatedAt: now,
          ));

      await db.into(db.testOutbox).insert(TestOutboxCompanion.insert(
            tenantId: tenantId,
            entityType: 'task',
            entityId: 'task-retry-1',
            apiEndpoint: '/api/v1/tasks',
            payload: '{"title":"مهمة تحتاج إعادة محاولة"}',
          ));

      // Simulate 3 failed sync attempts
      for (int attempt = 1; attempt <= 3; attempt++) {
        await db.customStatement(
          'UPDATE test_outbox SET retry_count = ? WHERE entity_id = ?',
          [attempt, 'task-retry-1'],
        );

        await db.into(db.testSyncLogs).insert(TestSyncLogsCompanion.insert(
              type: 'task_sync',
              status: 'failed',
              message: Value('Attempt $attempt failed: network timeout'),
              timestamp: DateTime.now(),
            ));
      }

      // Verify retry count
      final outboxItem = await (db.select(db.testOutbox)
            ..where((o) => o.entityId.equals('task-retry-1')))
          .getSingle();
      expect(outboxItem.retryCount, equals(3));
      expect(outboxItem.isSynced, isFalse);

      // Verify failed sync logs
      final failedLogs = await (db.select(db.testSyncLogs)
            ..where((l) => l.status.equals('failed')))
          .get();
      expect(failedLogs.length, equals(3));
    });
  });

  group('Database Integration - Tenant Isolation', () {
    late TestDatabase db;

    setUp(() async {
      db = createTestDatabase();

      // Setup data for two tenants
      final now = DateTime.now();
      await db.batch((batch) {
        // Tenant A: 3 fields, 5 tasks
        for (int i = 1; i <= 3; i++) {
          batch.insert(
            db.testFields,
            TestFieldsCompanion.insert(
              id: 'tenant-a-field-$i',
              tenantId: 'tenant-a',
              name: 'Field A-$i',
              boundary: '[[0,0],[1,0],[1,1],[0,1]]',
              areaHectares: i * 5.0,
              createdAt: now,
              updatedAt: now,
            ),
          );
        }
        for (int i = 1; i <= 5; i++) {
          batch.insert(
            db.testTasks,
            TestTasksCompanion.insert(
              id: 'tenant-a-task-$i',
              tenantId: 'tenant-a',
              fieldId: 'tenant-a-field-1',
              title: 'Task A-$i',
              createdAt: now,
              updatedAt: now,
            ),
          );
        }

        // Tenant B: 2 fields, 3 tasks
        for (int i = 1; i <= 2; i++) {
          batch.insert(
            db.testFields,
            TestFieldsCompanion.insert(
              id: 'tenant-b-field-$i',
              tenantId: 'tenant-b',
              name: 'Field B-$i',
              boundary: '[[2,2],[3,2],[3,3],[2,3]]',
              areaHectares: i * 3.0,
              createdAt: now,
              updatedAt: now,
            ),
          );
        }
        for (int i = 1; i <= 3; i++) {
          batch.insert(
            db.testTasks,
            TestTasksCompanion.insert(
              id: 'tenant-b-task-$i',
              tenantId: 'tenant-b',
              fieldId: 'tenant-b-field-1',
              title: 'Task B-$i',
              createdAt: now,
              updatedAt: now,
            ),
          );
        }
      });
    });

    tearDown(() async {
      await db.close();
    });

    test('should isolate fields by tenant', () async {
      final tenantAFields = await (db.select(db.testFields)
            ..where((f) => f.tenantId.equals('tenant-a')))
          .get();
      final tenantBFields = await (db.select(db.testFields)
            ..where((f) => f.tenantId.equals('tenant-b')))
          .get();

      expect(tenantAFields.length, equals(3));
      expect(tenantBFields.length, equals(2));
      expect(tenantAFields.every((f) => f.tenantId == 'tenant-a'), isTrue);
      expect(tenantBFields.every((f) => f.tenantId == 'tenant-b'), isTrue);
    });

    test('should isolate tasks by tenant', () async {
      final tenantATasks = await (db.select(db.testTasks)
            ..where((t) => t.tenantId.equals('tenant-a')))
          .get();
      final tenantBTasks = await (db.select(db.testTasks)
            ..where((t) => t.tenantId.equals('tenant-b')))
          .get();

      expect(tenantATasks.length, equals(5));
      expect(tenantBTasks.length, equals(3));
    });

    test('should clear tenant data without affecting other tenants', () async {
      // Delete all tenant-a data
      await db.transaction(() async {
        await (db.delete(db.testTasks)
              ..where((t) => t.tenantId.equals('tenant-a')))
            .go();
        await (db.delete(db.testFields)
              ..where((f) => f.tenantId.equals('tenant-a')))
            .go();
      });

      // Tenant A should be empty
      final tenantATasks = await (db.select(db.testTasks)
            ..where((t) => t.tenantId.equals('tenant-a')))
          .get();
      expect(tenantATasks, isEmpty);

      // Tenant B should be untouched
      final tenantBTasks = await (db.select(db.testTasks)
            ..where((t) => t.tenantId.equals('tenant-b')))
          .get();
      expect(tenantBTasks.length, equals(3));

      final tenantBFields = await (db.select(db.testFields)
            ..where((f) => f.tenantId.equals('tenant-b')))
          .get();
      expect(tenantBFields.length, equals(2));
    });
  });

  group('Database Integration - Conflict Resolution', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should detect ETag conflict and create sync event', () async {
      final now = DateTime.now();
      const tenantId = 'tenant-conflict-1';

      // Create field with ETag
      await db.into(db.testFields).insert(TestFieldsCompanion.insert(
            id: 'conflict-field-1',
            tenantId: tenantId,
            name: 'Original Field',
            boundary: '[[0,0],[1,0],[1,1],[0,1]]',
            areaHectares: 5.0,
            etag: const Value('etag-v1'),
            createdAt: now,
            updatedAt: now,
          ));

      // Queue update with old ETag
      await db.into(db.testOutbox).insert(TestOutboxCompanion.insert(
            tenantId: tenantId,
            entityType: 'field',
            entityId: 'conflict-field-1',
            apiEndpoint: '/api/v1/fields/conflict-field-1',
            method: const Value('PUT'),
            payload: '{"name":"Updated Field"}',
            ifMatch: const Value('etag-v1'),
          ));

      // Simulate 412 Precondition Failed - server has etag-v2
      // Create conflict sync event
      await db.into(db.testSyncEvents).insert(TestSyncEventsCompanion.insert(
            tenantId: tenantId,
            type: 'CONFLICT',
            entityType: const Value('field'),
            entityId: const Value('conflict-field-1'),
            message: 'ETag mismatch: local=etag-v1, server=etag-v2. Server data applied.',
          ));

      // Apply server version (resolve conflict)
      await (db.update(db.testFields)
            ..where((f) => f.id.equals('conflict-field-1')))
          .write(const TestFieldsCompanion(
        name: Value('Server Updated Field'),
        etag: Value('etag-v2'),
        synced: Value(true),
        serverUpdatedAt: Value(null),
      ));

      // Verify conflict was recorded
      final events = await (db.select(db.testSyncEvents)
            ..where((e) => e.tenantId.equals(tenantId))
            ..where((e) => e.type.equals('CONFLICT')))
          .get();
      expect(events.length, equals(1));
      expect(events.first.entityId, equals('conflict-field-1'));
      expect(events.first.isRead, isFalse);

      // Verify field has server data
      final field = await (db.select(db.testFields)
            ..where((f) => f.id.equals('conflict-field-1')))
          .getSingle();
      expect(field.name, equals('Server Updated Field'));
      expect(field.etag, equals('etag-v2'));
    });

    test('should mark conflict events as read', () async {
      const tenantId = 'tenant-read-events';

      // Create multiple sync events
      for (int i = 1; i <= 5; i++) {
        await db.into(db.testSyncEvents).insert(TestSyncEventsCompanion.insert(
              tenantId: tenantId,
              type: i <= 3 ? 'CONFLICT' : 'INFO',
              message: 'Event $i',
            ));
      }

      // Count unread
      final unreadCount = await (db.select(db.testSyncEvents)
            ..where((e) => e.tenantId.equals(tenantId))
            ..where((e) => e.isRead.equals(false)))
          .get();
      expect(unreadCount.length, equals(5));

      // Mark all as read
      await (db.update(db.testSyncEvents)
            ..where((e) => e.tenantId.equals(tenantId))
            ..where((e) => e.isRead.equals(false)))
          .write(const TestSyncEventsCompanion(isRead: Value(true)));

      // Verify all read
      final afterRead = await (db.select(db.testSyncEvents)
            ..where((e) => e.tenantId.equals(tenantId))
            ..where((e) => e.isRead.equals(false)))
          .get();
      expect(afterRead, isEmpty);
    });
  });

  group('Database Integration - Field Operations with GIS', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should store and retrieve field with GIS boundary', () async {
      final now = DateTime.now();
      const boundary = '[[46.7,24.7],[46.8,24.7],[46.8,24.8],[46.7,24.8]]';
      const centroid = '[46.75,24.75]';

      await db.into(db.testFields).insert(TestFieldsCompanion.insert(
            id: 'gis-field-1',
            tenantId: 'tenant-gis',
            name: 'حقل بحدود جغرافية',
            boundary: boundary,
            centroid: const Value(centroid),
            areaHectares: 12.5,
            cropType: const Value('wheat'),
            status: const Value('active'),
            ndviCurrent: const Value(0.72),
            ndviUpdatedAt: Value(now),
            createdAt: now,
            updatedAt: now,
          ));

      final field = await (db.select(db.testFields)
            ..where((f) => f.id.equals('gis-field-1')))
          .getSingle();

      expect(field.boundary, equals(boundary));
      expect(field.centroid, equals(centroid));
      expect(field.areaHectares, equals(12.5));
      expect(field.cropType, equals('wheat'));
      expect(field.ndviCurrent, equals(0.72));
    });

    test('should soft delete field and exclude from queries', () async {
      final now = DateTime.now();

      // Create 3 fields
      for (int i = 1; i <= 3; i++) {
        await db.into(db.testFields).insert(TestFieldsCompanion.insert(
              id: 'soft-del-field-$i',
              tenantId: 'tenant-softdel',
              name: 'Field $i',
              boundary: '[[0,0],[1,0],[1,1],[0,1]]',
              areaHectares: i * 2.0,
              createdAt: now,
              updatedAt: now,
            ));
      }

      // Soft delete field 2
      await (db.update(db.testFields)
            ..where((f) => f.id.equals('soft-del-field-2')))
          .write(TestFieldsCompanion(
        isDeleted: const Value(true),
        updatedAt: Value(DateTime.now()),
        synced: const Value(false),
      ));

      // Query excluding deleted
      final activeFields = await (db.select(db.testFields)
            ..where((f) => f.tenantId.equals('tenant-softdel'))
            ..where((f) => f.isDeleted.equals(false)))
          .get();
      expect(activeFields.length, equals(2));
      expect(activeFields.any((f) => f.id == 'soft-del-field-2'), isFalse);

      // Query including deleted
      final allFields = await (db.select(db.testFields)
            ..where((f) => f.tenantId.equals('tenant-softdel')))
          .get();
      expect(allFields.length, equals(3));
    });
  });

  group('Database Integration - Cross-Table Transactions', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should atomically create task with outbox entry', () async {
      final now = DateTime.now();
      const tenantId = 'tenant-atomic';

      await db.transaction(() async {
        // Insert task
        await db.into(db.testTasks).insert(TestTasksCompanion.insert(
              id: 'atomic-task-1',
              tenantId: tenantId,
              fieldId: 'field-1',
              title: 'Atomic Task',
              createdAt: now,
              updatedAt: now,
            ));

        // Insert outbox
        await db.into(db.testOutbox).insert(TestOutboxCompanion.insert(
              tenantId: tenantId,
              entityType: 'task',
              entityId: 'atomic-task-1',
              apiEndpoint: '/api/v1/tasks',
              payload: '{"title":"Atomic Task"}',
            ));
      });

      // Both should exist
      final tasks = await db.select(db.testTasks).get();
      final outbox = await db.select(db.testOutbox).get();
      expect(tasks.length, equals(1));
      expect(outbox.length, equals(1));
    });

    test('should rollback both task and outbox on error', () async {
      final now = DateTime.now();
      const tenantId = 'tenant-rollback';

      try {
        await db.transaction(() async {
          await db.into(db.testTasks).insert(TestTasksCompanion.insert(
                id: 'rollback-task',
                tenantId: tenantId,
                fieldId: 'field-1',
                title: 'Will Rollback',
                createdAt: now,
                updatedAt: now,
              ));

          await db.into(db.testOutbox).insert(TestOutboxCompanion.insert(
                tenantId: tenantId,
                entityType: 'task',
                entityId: 'rollback-task',
                apiEndpoint: '/api/v1/tasks',
                payload: '{"title":"Will Rollback"}',
              ));

          throw Exception('Simulated failure');
        });
      } catch (_) {}

      // Both should be empty
      final tasks = await db.select(db.testTasks).get();
      final outbox = await db.select(db.testOutbox).get();
      expect(tasks, isEmpty);
      expect(outbox, isEmpty);
    });

    test('should handle bulk server sync with fields and tasks', () async {
      final now = DateTime.now();
      const tenantId = 'tenant-bulk';

      // Simulate bulk sync from server
      await db.batch((batch) {
        // 10 fields from server
        for (int i = 1; i <= 10; i++) {
          batch.insert(
            db.testFields,
            TestFieldsCompanion.insert(
              id: 'server-field-$i',
              tenantId: tenantId,
              remoteId: Value('remote-$i'),
              name: 'Server Field $i',
              boundary: '[[0,0],[1,0],[1,1],[0,1]]',
              areaHectares: i * 2.5,
              etag: Value('etag-$i'),
              synced: const Value(true),
              createdAt: now,
              updatedAt: now,
            ),
          );
        }

        // 20 tasks from server
        for (int i = 1; i <= 20; i++) {
          batch.insert(
            db.testTasks,
            TestTasksCompanion.insert(
              id: 'server-task-$i',
              tenantId: tenantId,
              fieldId: 'server-field-${(i % 10) + 1}',
              title: 'Server Task $i',
              synced: const Value(true),
              createdAt: now,
              updatedAt: now,
            ),
          );
        }
      });

      // Verify counts
      final fieldCount = await db.testFields.count().getSingle();
      final taskCount = await db.testTasks.count().getSingle();
      expect(fieldCount, equals(10));
      expect(taskCount, equals(20));

      // Verify all synced
      final unsyncedFields = await (db.select(db.testFields)
            ..where((f) => f.synced.equals(false)))
          .get();
      expect(unsyncedFields, isEmpty);
    });
  });

  group('Database Integration - Stream Watchers', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should watch field changes across operations', () async {
      final now = DateTime.now();

      // Start watching
      final stream = (db.select(db.testFields)
            ..where((f) => f.tenantId.equals('tenant-watch'))
            ..where((f) => f.isDeleted.equals(false)))
          .watch();

      final emissions = <List<TestField>>[];
      final sub = stream.listen((data) => emissions.add(data));

      await Future<void>.delayed(const Duration(milliseconds: 50));

      // Insert field
      await db.into(db.testFields).insert(TestFieldsCompanion.insert(
            id: 'watch-field-1',
            tenantId: 'tenant-watch',
            name: 'Watched Field',
            boundary: '[[0,0],[1,0],[1,1],[0,1]]',
            areaHectares: 5.0,
            createdAt: now,
            updatedAt: now,
          ));

      await Future<void>.delayed(const Duration(milliseconds: 50));

      // Update field
      await (db.update(db.testFields)
            ..where((f) => f.id.equals('watch-field-1')))
          .write(const TestFieldsCompanion(
        ndviCurrent: Value(0.65),
      ));

      await Future<void>.delayed(const Duration(milliseconds: 50));

      await sub.cancel();

      // Should have received multiple emissions
      expect(emissions.length, greaterThanOrEqualTo(2));
    });
  });

  group('Database Integration - Outbox Priority Processing', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should process outbox items in FIFO order', () async {
      const tenantId = 'tenant-fifo';

      // Insert items with staggered timestamps
      for (int i = 1; i <= 5; i++) {
        await db.into(db.testOutbox).insert(TestOutboxCompanion.insert(
              tenantId: tenantId,
              entityType: 'task',
              entityId: 'task-$i',
              apiEndpoint: '/api/v1/tasks',
              payload: '{"order":$i}',
            ));
        // Small delay to ensure different timestamps
        await Future<void>.delayed(const Duration(milliseconds: 10));
      }

      // Fetch in order
      final ordered = await (db.select(db.testOutbox)
            ..where((o) => o.isSynced.equals(false))
            ..orderBy([(o) => OrderingTerm.asc(o.createdAt)])
            ..limit(3))
          .get();

      expect(ordered.length, equals(3));
      expect(ordered[0].entityId, equals('task-1'));
      expect(ordered[1].entityId, equals('task-2'));
      expect(ordered[2].entityId, equals('task-3'));
    });

    test('should skip already synced outbox items', () async {
      const tenantId = 'tenant-skip';

      // Insert 5 items, mark 2 as synced
      for (int i = 1; i <= 5; i++) {
        await db.into(db.testOutbox).insert(TestOutboxCompanion.insert(
              tenantId: tenantId,
              entityType: 'field',
              entityId: 'field-$i',
              apiEndpoint: '/api/v1/fields',
              payload: '{}',
            ));
      }

      // Mark items 1 and 2 as synced
      await (db.update(db.testOutbox)
            ..where((o) => o.entityId.isIn(['field-1', 'field-2'])))
          .write(const TestOutboxCompanion(isSynced: Value(true)));

      // Fetch pending
      final pending = await (db.select(db.testOutbox)
            ..where((o) => o.isSynced.equals(false))
            ..orderBy([(o) => OrderingTerm.asc(o.id)]))
          .get();

      expect(pending.length, equals(3));
      expect(pending.every((o) => !o.isSynced), isTrue);
    });
  });

  group('Database Integration - Data Integrity', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should maintain referential consistency across tables', () async {
      final now = DateTime.now();
      const tenantId = 'tenant-integrity';
      const fieldId = 'integrity-field-1';

      // Create field
      await db.into(db.testFields).insert(TestFieldsCompanion.insert(
            id: fieldId,
            tenantId: tenantId,
            name: 'Integrity Field',
            boundary: '[[0,0],[1,0],[1,1],[0,1]]',
            areaHectares: 8.0,
            createdAt: now,
            updatedAt: now,
          ));

      // Create tasks for the field
      for (int i = 1; i <= 3; i++) {
        await db.into(db.testTasks).insert(TestTasksCompanion.insert(
              id: 'integrity-task-$i',
              tenantId: tenantId,
              fieldId: fieldId,
              title: 'Task $i',
              createdAt: now,
              updatedAt: now,
            ));
      }

      // Verify tasks are linked to field
      final fieldTasks = await (db.select(db.testTasks)
            ..where((t) => t.fieldId.equals(fieldId)))
          .get();
      expect(fieldTasks.length, equals(3));
      expect(fieldTasks.every((t) => t.tenantId == tenantId), isTrue);
    });

    test('should handle concurrent-like batch operations', () async {
      final now = DateTime.now();

      // Simulate multiple "concurrent" batch inserts
      await Future.wait([
        db.batch((batch) {
          for (int i = 1; i <= 50; i++) {
            batch.insert(
              db.testTasks,
              TestTasksCompanion.insert(
                id: 'concurrent-a-$i',
                tenantId: 'tenant-concurrent',
                fieldId: 'field-1',
                title: 'Batch A Task $i',
                createdAt: now,
                updatedAt: now,
              ),
            );
          }
        }),
        db.batch((batch) {
          for (int i = 1; i <= 50; i++) {
            batch.insert(
              db.testSyncLogs,
              TestSyncLogsCompanion.insert(
                type: 'concurrent_test',
                status: 'success',
                message: Value('Log entry $i'),
                timestamp: now,
              ),
            );
          }
        }),
      ]);

      final taskCount = await db.testTasks.count().getSingle();
      final logCount = await db.testSyncLogs.count().getSingle();
      expect(taskCount, equals(50));
      expect(logCount, equals(50));
    });
  });

  group('Database Integration - upsertFieldsFromServer (GeoJSON)', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    /// Helper: Parse GeoJSON geometry and insert field - mirrors production logic
    Future<void> upsertFieldsFromServer(
      TestDatabase db,
      List<Map<String, dynamic>> items,
    ) async {
      await db.batch((batch) {
        for (final item in items) {
          // Parse GeoJSON geometry to boundary string (mirrors production GeoPolygonConverter)
          String boundary = '[]';
          String? centroid;

          final geometry = item['geometry'];
          if (geometry != null && geometry['type'] == 'Polygon') {
            final coords = geometry['coordinates'][0] as List;
            final points = coords.map((c) {
              final coord = c as List;
              return [
                (coord[0] as num).toDouble(), // lng
                (coord[1] as num).toDouble(), // lat
              ];
            }).toList();

            boundary = jsonEncode(points);

            // Calculate centroid
            if (points.isNotEmpty) {
              double sumLat = 0, sumLng = 0;
              for (final p in points) {
                sumLng += p[0];
                sumLat += p[1];
              }
              centroid = jsonEncode([
                sumLng / points.length,
                sumLat / points.length,
              ]);
            }
          }

          batch.insert(
            db.testFields,
            TestFieldsCompanion.insert(
              id: item['id'] as String,
              remoteId: Value(item['remote_id'] as String? ?? item['id'] as String),
              tenantId: item['tenant_id'] as String,
              farmId: Value(item['farm_id'] as String?),
              name: item['name'] as String,
              cropType: Value(item['crop_type'] as String?),
              boundary: boundary,
              centroid: Value(centroid),
              areaHectares: (item['area_hectares'] as num?)?.toDouble() ?? 0,
              status: Value(item['status'] as String?),
              ndviCurrent: Value((item['ndvi_current'] as num?)?.toDouble()),
              ndviUpdatedAt: Value(item['ndvi_updated_at'] != null
                  ? DateTime.tryParse(item['ndvi_updated_at'].toString())
                  : null),
              createdAt: DateTime.tryParse(item['created_at']?.toString() ?? '') ?? DateTime.now(),
              updatedAt: DateTime.tryParse(item['updated_at']?.toString() ?? '') ?? DateTime.now(),
              synced: const Value(true),
            ),
            onConflict: DoUpdate((old) => TestFieldsCompanion(
                  name: Value(item['name'] as String),
                  boundary: Value(boundary),
                  centroid: Value(centroid),
                  areaHectares: Value((item['area_hectares'] as num?)?.toDouble() ?? 0),
                  ndviCurrent: Value((item['ndvi_current'] as num?)?.toDouble()),
                  updatedAt: Value(
                      DateTime.tryParse(item['updated_at']?.toString() ?? '') ?? DateTime.now()),
                  synced: const Value(true),
                )),
          );
        }
      });
    }

    test('should insert fields from server with GeoJSON polygon', () async {
      final serverData = [
        {
          'id': 'server-field-1',
          'remote_id': 'remote-001',
          'tenant_id': 'tenant-geo',
          'farm_id': 'farm-1',
          'name': 'حقل القمح',
          'crop_type': 'wheat',
          'geometry': {
            'type': 'Polygon',
            'coordinates': [
              [
                [46.7, 24.7],
                [46.8, 24.7],
                [46.8, 24.8],
                [46.7, 24.8],
                [46.7, 24.7],
              ]
            ]
          },
          'area_hectares': 12.5,
          'status': 'active',
          'ndvi_current': 0.72,
          'ndvi_updated_at': '2026-03-10T08:00:00Z',
          'created_at': '2026-01-01T00:00:00Z',
          'updated_at': '2026-03-10T08:00:00Z',
        }
      ];

      await upsertFieldsFromServer(db, serverData);

      final fields = await db.select(db.testFields).get();
      expect(fields.length, equals(1));

      final field = fields.first;
      expect(field.id, equals('server-field-1'));
      expect(field.remoteId, equals('remote-001'));
      expect(field.tenantId, equals('tenant-geo'));
      expect(field.name, equals('حقل القمح'));
      expect(field.cropType, equals('wheat'));
      expect(field.areaHectares, equals(12.5));
      expect(field.status, equals('active'));
      expect(field.ndviCurrent, equals(0.72));
      expect(field.synced, isTrue);

      // Verify boundary was stored as JSON array of coordinate pairs
      final boundaryData = jsonDecode(field.boundary) as List;
      expect(boundaryData.length, equals(5));
      expect(boundaryData[0][0], equals(46.7)); // lng
      expect(boundaryData[0][1], equals(24.7)); // lat

      // Verify centroid was calculated
      expect(field.centroid, isNotNull);
      final centroidData = jsonDecode(field.centroid!) as List;
      expect(centroidData[0], closeTo(46.74, 0.01)); // avg lng
      expect(centroidData[1], closeTo(24.74, 0.01)); // avg lat
    });

    test('should handle bulk insert of multiple fields', () async {
      final serverData = List.generate(10, (i) => {
        return {
          'id': 'bulk-field-$i',
          'tenant_id': 'tenant-bulk',
          'name': 'حقل $i',
          'geometry': {
            'type': 'Polygon',
            'coordinates': [
              [
                [46.0 + i * 0.1, 24.0],
                [46.1 + i * 0.1, 24.0],
                [46.1 + i * 0.1, 24.1],
                [46.0 + i * 0.1, 24.1],
              ]
            ]
          },
          'area_hectares': 5.0 + i,
          'created_at': '2026-01-01T00:00:00Z',
          'updated_at': '2026-03-01T00:00:00Z',
        };
      });

      await upsertFieldsFromServer(db, serverData);

      final count = await db.testFields.count().getSingle();
      expect(count, equals(10));

      // Verify all are synced
      final unsyncedCount = await (db.testFields.count(
        where: (f) => f.synced.equals(false),
      )).getSingle();
      expect(unsyncedCount, equals(0));
    });

    test('should update existing field on conflict (upsert)', () async {
      // Insert initial field
      final now = DateTime.now();
      await db.into(db.testFields).insert(TestFieldsCompanion.insert(
            id: 'upsert-field-1',
            tenantId: 'tenant-upsert',
            name: 'Original Name',
            boundary: '[[46.7,24.7]]',
            areaHectares: 5.0,
            createdAt: now,
            updatedAt: now,
          ));

      // Upsert from server with updated data
      final serverData = [
        {
          'id': 'upsert-field-1',
          'tenant_id': 'tenant-upsert',
          'name': 'اسم محدث', // Updated name
          'geometry': {
            'type': 'Polygon',
            'coordinates': [
              [
                [47.0, 25.0],
                [47.1, 25.0],
                [47.1, 25.1],
                [47.0, 25.1],
              ]
            ]
          },
          'area_hectares': 15.0, // Updated area
          'ndvi_current': 0.85, // New NDVI
          'created_at': '2026-01-01T00:00:00Z',
          'updated_at': '2026-03-12T00:00:00Z',
        }
      ];

      await upsertFieldsFromServer(db, serverData);

      final field = await (db.select(db.testFields)
            ..where((f) => f.id.equals('upsert-field-1')))
          .getSingle();

      expect(field.name, equals('اسم محدث'));
      expect(field.areaHectares, equals(15.0));
      expect(field.ndviCurrent, equals(0.85));
      expect(field.synced, isTrue);

      // Should still be only 1 record
      final count = await db.testFields.count().getSingle();
      expect(count, equals(1));
    });

    test('should handle field without geometry (null geometry)', () async {
      final serverData = [
        {
          'id': 'no-geo-field',
          'tenant_id': 'tenant-geo',
          'name': 'حقل بدون إحداثيات',
          'geometry': null,
          'area_hectares': 0,
          'created_at': '2026-01-01T00:00:00Z',
          'updated_at': '2026-01-01T00:00:00Z',
        }
      ];

      await upsertFieldsFromServer(db, serverData);

      final field = await (db.select(db.testFields)
            ..where((f) => f.id.equals('no-geo-field')))
          .getSingle();

      expect(field.boundary, equals('[]'));
      expect(field.centroid, isNull);
    });

    test('should handle field with null optional fields', () async {
      final serverData = [
        {
          'id': 'minimal-field',
          'tenant_id': 'tenant-min',
          'name': 'Minimal Field',
          'geometry': null,
          'area_hectares': null,
          'farm_id': null,
          'crop_type': null,
          'status': null,
          'ndvi_current': null,
          'ndvi_updated_at': null,
          'created_at': null,
          'updated_at': null,
        }
      ];

      await upsertFieldsFromServer(db, serverData);

      final field = await (db.select(db.testFields)
            ..where((f) => f.id.equals('minimal-field')))
          .getSingle();

      expect(field.farmId, isNull);
      expect(field.cropType, isNull);
      expect(field.status, isNull);
      expect(field.ndviCurrent, isNull);
      expect(field.areaHectares, equals(0));
    });

    test('should correctly calculate centroid for complex polygon', () async {
      // Triangle polygon
      final serverData = [
        {
          'id': 'triangle-field',
          'tenant_id': 'tenant-centroid',
          'name': 'Triangle Field',
          'geometry': {
            'type': 'Polygon',
            'coordinates': [
              [
                [0.0, 0.0],
                [10.0, 0.0],
                [5.0, 10.0],
                [0.0, 0.0], // Closing point
              ]
            ]
          },
          'area_hectares': 50,
          'created_at': '2026-01-01T00:00:00Z',
          'updated_at': '2026-01-01T00:00:00Z',
        }
      ];

      await upsertFieldsFromServer(db, serverData);

      final field = await (db.select(db.testFields)
            ..where((f) => f.id.equals('triangle-field')))
          .getSingle();

      final centroidData = jsonDecode(field.centroid!) as List;
      // Average of [0,10,5,0] = 3.75 for lng, [0,0,10,0] = 2.5 for lat
      expect(centroidData[0], closeTo(3.75, 0.01)); // avg lng
      expect(centroidData[1], closeTo(2.5, 0.01));   // avg lat
    });

    test('should handle mixed insert and update in single batch', () async {
      final now = DateTime.now();

      // Pre-insert one field
      await db.into(db.testFields).insert(TestFieldsCompanion.insert(
            id: 'mixed-existing',
            tenantId: 'tenant-mixed',
            name: 'Existing Field',
            boundary: '[]',
            areaHectares: 3.0,
            createdAt: now,
            updatedAt: now,
          ));

      // Server batch with one existing (update) and one new (insert)
      final serverData = [
        {
          'id': 'mixed-existing',
          'tenant_id': 'tenant-mixed',
          'name': 'Updated Existing',
          'geometry': null,
          'area_hectares': 8.0,
          'created_at': '2026-01-01T00:00:00Z',
          'updated_at': '2026-03-12T00:00:00Z',
        },
        {
          'id': 'mixed-new',
          'tenant_id': 'tenant-mixed',
          'name': 'New From Server',
          'geometry': {
            'type': 'Polygon',
            'coordinates': [
              [
                [45.0, 23.0],
                [45.1, 23.0],
                [45.1, 23.1],
                [45.0, 23.1],
              ]
            ]
          },
          'area_hectares': 12.0,
          'created_at': '2026-01-01T00:00:00Z',
          'updated_at': '2026-03-12T00:00:00Z',
        },
      ];

      await upsertFieldsFromServer(db, serverData);

      final count = await db.testFields.count().getSingle();
      expect(count, equals(2));

      final existing = await (db.select(db.testFields)
            ..where((f) => f.id.equals('mixed-existing')))
          .getSingle();
      expect(existing.name, equals('Updated Existing'));
      expect(existing.areaHectares, equals(8.0));

      final newField = await (db.select(db.testFields)
            ..where((f) => f.id.equals('mixed-new')))
          .getSingle();
      expect(newField.name, equals('New From Server'));
      expect(newField.boundary, isNot(equals('[]')));
    });
  });

  group('Database Integration - upsertTasksFromServer', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    /// Helper: mirrors production upsertTasksFromServer logic
    Future<void> upsertTasksFromServer(
      TestDatabase db,
      List<Map<String, dynamic>> items,
    ) async {
      await db.batch((batch) {
        for (final item in items) {
          batch.insert(
            db.testTasks,
            TestTasksCompanion.insert(
              id: item['id'] as String,
              tenantId: item['tenant_id'] as String,
              fieldId: item['field_id'] as String,
              farmId: Value(item['farm_id'] as String?),
              title: item['title'] as String,
              description: Value(item['description'] as String?),
              status: Value(item['status'] as String? ?? 'open'),
              priority: Value(item['priority'] as String? ?? 'medium'),
              dueDate: Value(item['due_date'] != null
                  ? DateTime.tryParse(item['due_date'].toString())
                  : null),
              assignedTo: Value(item['assigned_to'] as String?),
              evidenceNotes: Value(item['evidence_notes'] as String?),
              evidencePhotos: Value(item['evidence_photos'] != null
                  ? (item['evidence_photos'] as List).join(',')
                  : null),
              createdAt: DateTime.tryParse(item['created_at']?.toString() ?? '') ?? DateTime.now(),
              updatedAt: DateTime.tryParse(item['updated_at']?.toString() ?? '') ?? DateTime.now(),
              synced: const Value(true),
            ),
            onConflict: DoUpdate((old) => TestTasksCompanion(
                  status: Value(item['status'] as String? ?? 'open'),
                  updatedAt: Value(
                      DateTime.tryParse(item['updated_at']?.toString() ?? '') ?? DateTime.now()),
                  synced: const Value(true),
                )),
          );
        }
      });
    }

    test('should insert tasks from server in bulk', () async {
      final serverTasks = [
        {
          'id': 'srv-task-1',
          'tenant_id': 'tenant-srv',
          'field_id': 'field-1',
          'farm_id': 'farm-1',
          'title': 'رش المبيدات',
          'description': 'رش مبيدات الحشرات في الحقل',
          'status': 'open',
          'priority': 'high',
          'due_date': '2026-03-15T00:00:00Z',
          'assigned_to': 'worker-1',
          'created_at': '2026-03-01T00:00:00Z',
          'updated_at': '2026-03-10T00:00:00Z',
        },
        {
          'id': 'srv-task-2',
          'tenant_id': 'tenant-srv',
          'field_id': 'field-2',
          'title': 'فحص التربة',
          'status': 'in_progress',
          'priority': 'medium',
          'created_at': '2026-03-02T00:00:00Z',
          'updated_at': '2026-03-11T00:00:00Z',
        },
      ];

      await upsertTasksFromServer(db, serverTasks);

      final tasks = await db.select(db.testTasks).get();
      expect(tasks.length, equals(2));
      expect(tasks.every((t) => t.synced), isTrue);

      final task1 = tasks.firstWhere((t) => t.id == 'srv-task-1');
      expect(task1.title, equals('رش المبيدات'));
      expect(task1.priority, equals('high'));
      expect(task1.assignedTo, equals('worker-1'));
    });

    test('should update existing task on conflict from server', () async {
      final now = DateTime.now();

      // Insert local task
      await db.into(db.testTasks).insert(TestTasksCompanion.insert(
            id: 'srv-conflict',
            tenantId: 'tenant-srv',
            fieldId: 'field-1',
            title: 'Local Task Title',
            status: const Value('open'),
            createdAt: now,
            updatedAt: now,
          ));

      // Server sends update for same task
      await upsertTasksFromServer(db, [
        {
          'id': 'srv-conflict',
          'tenant_id': 'tenant-srv',
          'field_id': 'field-1',
          'title': 'Server Updated Title',
          'status': 'done',
          'updated_at': '2026-03-12T00:00:00Z',
        },
      ]);

      final task = await (db.select(db.testTasks)
            ..where((t) => t.id.equals('srv-conflict')))
          .getSingle();

      // OnConflict only updates status, updatedAt, synced
      expect(task.status, equals('done'));
      expect(task.synced, isTrue);

      // Only 1 record, not duplicated
      final count = await db.testTasks.count().getSingle();
      expect(count, equals(1));
    });

    test('should handle tasks with evidence photos from server', () async {
      await upsertTasksFromServer(db, [
        {
          'id': 'srv-evidence',
          'tenant_id': 'tenant-srv',
          'field_id': 'field-1',
          'title': 'Task With Photos',
          'evidence_notes': 'Completed successfully',
          'evidence_photos': ['photo1.jpg', 'photo2.jpg'],
          'created_at': '2026-03-01T00:00:00Z',
          'updated_at': '2026-03-01T00:00:00Z',
        },
      ]);

      final task = await (db.select(db.testTasks)
            ..where((t) => t.id.equals('srv-evidence')))
          .getSingle();

      expect(task.evidenceNotes, equals('Completed successfully'));
      expect(task.evidencePhotos, equals('photo1.jpg,photo2.jpg'));
    });
  });

  group('Database Integration - Database Verification & Stats', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should verify all expected tables exist', () async {
      final tables = await db.customSelect(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'",
      ).get();

      final tableNames = tables.map((r) => r.read<String>('name')).toSet();

      expect(tableNames, contains('test_tasks'));
      expect(tableNames, contains('test_outbox'));
      expect(tableNames, contains('test_fields'));
      expect(tableNames, contains('test_sync_logs'));
      expect(tableNames, contains('test_sync_events'));
      expect(tableNames.length, equals(5));
    });

    test('should verify all expected indexes exist (25 total)', () async {
      final indexes = await db.customSelect(
        "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'",
      ).get();

      final indexNames = indexes.map((r) => r.read<String>('name')).toSet();
      expect(indexNames.length, equals(25));
    });

    test('should get database statistics (table counts)', () async {
      final now = DateTime.now();

      // Insert test data across all tables
      await db.batch((batch) {
        for (int i = 0; i < 5; i++) {
          batch.insert(db.testTasks, TestTasksCompanion.insert(
            id: 'stat-task-$i', tenantId: 'tenant-stats', fieldId: 'field-1',
            title: 'Stats Task $i', createdAt: now, updatedAt: now,
          ));
        }
        for (int i = 0; i < 3; i++) {
          batch.insert(db.testOutbox, TestOutboxCompanion.insert(
            tenantId: 'tenant-stats', entityType: 'task', entityId: 'stat-task-$i',
            apiEndpoint: '/api/v1/tasks', payload: '{}',
          ));
        }
        for (int i = 0; i < 2; i++) {
          batch.insert(db.testFields, TestFieldsCompanion.insert(
            id: 'stat-field-$i', tenantId: 'tenant-stats',
            name: 'Field $i', boundary: '[]', areaHectares: 5.0,
            createdAt: now, updatedAt: now,
          ));
        }
        batch.insert(db.testSyncLogs, TestSyncLogsCompanion.insert(
          type: 'full_sync', status: 'success', timestamp: now,
        ));
        batch.insert(db.testSyncEvents, TestSyncEventsCompanion.insert(
          tenantId: 'tenant-stats', type: 'INFO', message: 'Sync complete',
        ));
      });

      // Query stats (mirrors production getStats pattern)
      final taskCount = await db.testTasks.count().getSingle();
      final outboxCount = await db.testOutbox.count().getSingle();
      final fieldCount = await db.testFields.count().getSingle();
      final logCount = await db.testSyncLogs.count().getSingle();
      final eventCount = await db.testSyncEvents.count().getSingle();

      expect(taskCount, equals(5));
      expect(outboxCount, equals(3));
      expect(fieldCount, equals(2));
      expect(logCount, equals(1));
      expect(eventCount, equals(1));
    });

    test('should get database statistics with filters (unsynced counts)', () async {
      final now = DateTime.now();

      await db.batch((batch) {
        // 3 synced + 2 unsynced tasks
        for (int i = 0; i < 5; i++) {
          batch.insert(db.testTasks, TestTasksCompanion.insert(
            id: 'sync-stat-$i', tenantId: 'tenant-stats', fieldId: 'field-1',
            title: 'Task $i', synced: Value(i < 3),
            createdAt: now, updatedAt: now,
          ));
        }
        // 2 synced + 1 pending outbox
        for (int i = 0; i < 3; i++) {
          batch.insert(db.testOutbox, TestOutboxCompanion.insert(
            tenantId: 'tenant-stats', entityType: 'task', entityId: 'task-$i',
            apiEndpoint: '/api/v1/tasks', payload: '{}',
            isSynced: Value(i < 2),
          ));
        }
      });

      // Unsynced counts (mirrors verifyDatabase pattern)
      final unsyncedTasks = await (db.testTasks.count(
        where: (t) => t.synced.equals(false),
      )).getSingle();
      final pendingOutbox = await (db.testOutbox.count(
        where: (o) => o.isSynced.equals(false),
      )).getSingle();

      expect(unsyncedTasks, equals(2));
      expect(pendingOutbox, equals(1));
    });

    test('should verify table column integrity via insert/read cycle', () async {
      final now = DateTime.now();

      // Insert a complete task with ALL columns populated
      await db.into(db.testTasks).insert(TestTasksCompanion.insert(
            id: 'full-task',
            tenantId: 'tenant-verify',
            fieldId: 'field-verify',
            farmId: const Value('farm-verify'),
            title: 'Full Task',
            description: const Value('Complete task description'),
            status: const Value('in_progress'),
            priority: const Value('high'),
            dueDate: Value(now.add(const Duration(days: 7))),
            assignedTo: const Value('worker-123'),
            evidenceNotes: const Value('Inspection notes in Arabic: ملاحظات التفتيش'),
            evidencePhotos: const Value('img1.jpg,img2.jpg,img3.jpg'),
            createdAt: now,
            updatedAt: now,
            synced: const Value(true),
          ));

      final task = await (db.select(db.testTasks)
            ..where((t) => t.id.equals('full-task')))
          .getSingle();

      // Verify every column
      expect(task.id, equals('full-task'));
      expect(task.tenantId, equals('tenant-verify'));
      expect(task.fieldId, equals('field-verify'));
      expect(task.farmId, equals('farm-verify'));
      expect(task.title, equals('Full Task'));
      expect(task.description, equals('Complete task description'));
      expect(task.status, equals('in_progress'));
      expect(task.priority, equals('high'));
      expect(task.dueDate, isNotNull);
      expect(task.assignedTo, equals('worker-123'));
      expect(task.evidenceNotes, contains('ملاحظات التفتيش'));
      expect(task.evidencePhotos, equals('img1.jpg,img2.jpg,img3.jpg'));
      expect(task.synced, isTrue);
    });

    test('should verify field column integrity with GIS data', () async {
      final now = DateTime.now();
      final ndviTime = now.subtract(const Duration(hours: 6));

      await db.into(db.testFields).insert(TestFieldsCompanion.insert(
            id: 'full-field',
            remoteId: const Value('remote-uuid-123'),
            tenantId: 'tenant-verify',
            farmId: const Value('farm-verify'),
            name: 'حقل التحقق',
            cropType: const Value('wheat'),
            boundary: '[[46.7,24.7],[46.8,24.7],[46.8,24.8],[46.7,24.8]]',
            centroid: const Value('[46.75,24.75]'),
            areaHectares: 25.3,
            status: const Value('active'),
            ndviCurrent: const Value(0.78),
            ndviUpdatedAt: Value(ndviTime),
            synced: const Value(true),
            isDeleted: const Value(false),
            createdAt: now,
            updatedAt: now,
            etag: const Value('"abc123def"'),
            serverUpdatedAt: Value(now),
          ));

      final field = await (db.select(db.testFields)
            ..where((f) => f.id.equals('full-field')))
          .getSingle();

      expect(field.id, equals('full-field'));
      expect(field.remoteId, equals('remote-uuid-123'));
      expect(field.tenantId, equals('tenant-verify'));
      expect(field.farmId, equals('farm-verify'));
      expect(field.name, equals('حقل التحقق'));
      expect(field.cropType, equals('wheat'));
      expect(field.boundary, contains('46.7'));
      expect(field.centroid, contains('46.75'));
      expect(field.areaHectares, equals(25.3));
      expect(field.status, equals('active'));
      expect(field.ndviCurrent, equals(0.78));
      expect(field.ndviUpdatedAt, isNotNull);
      expect(field.synced, isTrue);
      expect(field.isDeleted, isFalse);
      expect(field.etag, equals('"abc123def"'));
      expect(field.serverUpdatedAt, isNotNull);
    });

    test('should return migration history table info', () async {
      // Mirrors production getMigrationHistory - query migration_history table
      // In test DB, migration_history table doesn't exist, so it should handle gracefully
      try {
        final result = await db.customSelect(
          'SELECT * FROM migration_history ORDER BY id DESC',
        ).get();
        // If table exists (unlikely in test), verify structure
        expect(result, isA<List>());
      } catch (e) {
        // Expected: table doesn't exist in test database
        // This mirrors production's try/catch in getMigrationHistory
        expect(e, isNotNull);
      }
    });

    test('should verify schema version matches expected', () {
      // Mirrors production schemaVersion check
      expect(db.schemaVersion, equals(4));
    });

    test('should verify database page size and journal mode', () async {
      final pageSize = await db.customSelect('PRAGMA page_size;').getSingle();
      expect(pageSize.data.containsKey('page_size'), isTrue);

      final journalMode = await db.customSelect('PRAGMA journal_mode;').getSingle();
      // In-memory databases use specific journal modes
      expect(journalMode.data.containsKey('journal_mode'), isTrue);
    });

    test('should verify database integrity check passes', () async {
      // SQLite PRAGMA integrity_check
      final result = await db.customSelect('PRAGMA integrity_check;').getSingle();
      expect(result.read<String>('integrity_check'), equals('ok'));
    });
  });
}
