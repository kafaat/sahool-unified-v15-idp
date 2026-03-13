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
}
