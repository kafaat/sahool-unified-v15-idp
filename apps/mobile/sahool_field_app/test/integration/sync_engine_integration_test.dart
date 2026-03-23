/// SAHOOL Field App - Sync Engine Integration Tests
/// اختبارات تكامل محرك المزامنة
///
/// Tests the database-level integration for sync operations including:
/// - Field database CRUD operations
/// - Task CRUD operations
/// - Sync event workflows end-to-end
/// - Watch streams emit correct values
/// - Database health monitoring
library;
import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:sahool_field_app/core/storage/database.dart';

import '../mocks/mock_app_database.dart';

void main() {
  group(
      'Sync Engine Database Integration Tests - اختبارات تكامل قاعدة البيانات',
      () {
    late MockAppDatabase db;

    setUp(() {
      db = MockAppDatabase();
    });

    tearDown(() {
      db.clearAll();
      db.dispose();
    });

    // =========================================================================
    // Field CRUD Integration
    // تكامل عمليات الحقول
    // =========================================================================

    group('Field CRUD Integration - تكامل عمليات الحقول', () {
      Field makeField({
        required String id,
        String tenantId = 'tenant-001',
        String name = 'Test Field',
        String? cropType = 'wheat',
        double areaHectares = 5.0,
        bool synced = false,
        String? etag,
      }) {
        final now = DateTime.now();
        return Field(
          id: id,
          remoteId: null,
          tenantId: tenantId,
          farmId: null,
          name: name,
          cropType: cropType,
          boundary: const [
            LatLng(15.3694, 44.1910),
            LatLng(15.3704, 44.1920),
            LatLng(15.3704, 44.1900),
          ],
          centroid: null,
          areaHectares: areaHectares,
          status: 'active',
          ndviCurrent: null,
          ndviUpdatedAt: null,
          synced: synced,
          isDeleted: false,
          createdAt: now,
          updatedAt: now,
          etag: etag,
          serverUpdatedAt: null,
        );
      }

      test('seedField + getAllFields returns the field', () async {
        db.seedField(makeField(id: 'f001', name: 'حقل القمح'));

        final fields = await db.getAllFields('tenant-001');
        expect(fields.length, equals(1));
        expect(fields.first.name, equals('حقل القمح'));
        expect(fields.first.id, equals('f001'));
      });

      test('getAllFields returns only non-deleted fields', () async {
        db.seedField(makeField(id: 'f001', name: 'Field Active'));
        db.seedField(Field(
          id: 'f002',
          remoteId: null,
          tenantId: 'tenant-001',
          farmId: null,
          name: 'Field Deleted',
          cropType: 'corn',
          boundary: [],
          centroid: null,
          areaHectares: 3.0,
          status: 'active',
          ndviCurrent: null,
          ndviUpdatedAt: null,
          synced: false,
          isDeleted: true, // soft-deleted
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
          etag: null,
          serverUpdatedAt: null,
        ));

        final fields = await db.getAllFields('tenant-001');
        expect(fields.length, equals(1));
        expect(fields.first.name, equals('Field Active'));
      });

      test('getFieldById returns correct field', () async {
        db.seedField(makeField(id: 'f001', name: 'حقل الذرة'));
        db.seedField(makeField(id: 'f002', name: 'حقل القمح'));

        final field = await db.getFieldById('f001');
        expect(field, isNotNull);
        expect(field!.name, equals('حقل الذرة'));
      });

      test('getFieldById returns null for missing field', () async {
        final field = await db.getFieldById('non-existent');
        expect(field, isNull);
      });

      test('softDeleteField marks field as deleted', () async {
        db.seedField(makeField(id: 'f001'));

        await db.softDeleteField('f001');

        final fields = await db.getAllFields('tenant-001');
        expect(fields.isEmpty, isTrue);

        // But field exists in the mock with isDeleted=true
        // (getAllFields filters deleted)
      });

      test('markFieldSynced updates synced flag and remoteId', () async {
        db.seedField(makeField(id: 'f001', synced: false));

        await db.markFieldSynced('f001', 'remote-001');

        final field = await db.getFieldById('f001');
        expect(field?.synced, isTrue);
        expect(field?.remoteId, equals('remote-001'));
      });

      test('getUnsyncedFields returns only unsynced fields', () async {
        db.seedField(makeField(id: 'f001', synced: false));
        db.seedField(makeField(id: 'f002', synced: true));
        db.seedField(makeField(id: 'f003', synced: false));

        final unsynced = await db.getUnsyncedFields();
        expect(unsynced.length, equals(2));
        expect(unsynced.every((f) => !f.synced), isTrue);
      });

      test('Tenant isolation in getAllFields', () async {
        db.seedField(makeField(id: 'f001', tenantId: 'tenant-A'));
        db.seedField(makeField(id: 'f002', tenantId: 'tenant-B'));
        db.seedField(makeField(id: 'f003', tenantId: 'tenant-A'));

        final fieldsA = await db.getAllFields('tenant-A');
        final fieldsB = await db.getAllFields('tenant-B');

        expect(fieldsA.length, equals(2));
        expect(fieldsB.length, equals(1));
        expect(fieldsA.every((f) => f.tenantId == 'tenant-A'), isTrue);
      });
    });

    // =========================================================================
    // Task CRUD Integration
    // تكامل عمليات المهام
    // =========================================================================

    group('Task CRUD Integration - تكامل عمليات المهام', () {
      Task makeTask({
        required String id,
        String tenantId = 'tenant-001',
        String fieldId = 'field-001',
        String title = 'Test Task',
        String status = 'open',
        bool synced = false,
      }) {
        final now = DateTime.now();
        return Task(
          id: id,
          tenantId: tenantId,
          fieldId: fieldId,
          farmId: null,
          title: title,
          description: null,
          status: status,
          priority: 'medium',
          dueDate: null,
          assignedTo: null,
          evidenceNotes: null,
          evidencePhotos: null,
          createdAt: now,
          updatedAt: now,
          synced: synced,
        );
      }

      test('seedTask + getAllTasks returns the task', () async {
        db.seedTask(makeTask(id: 't001', title: 'إضافة سماد'));

        final tasks = await db.getAllTasks('tenant-001');
        expect(tasks.length, equals(1));
        expect(tasks.first.title, equals('إضافة سماد'));
      });

      test('getTasksForField returns only tasks for that field', () async {
        db.seedTask(makeTask(id: 't001', fieldId: 'field-001'));
        db.seedTask(makeTask(id: 't002', fieldId: 'field-002'));
        db.seedTask(makeTask(id: 't003', fieldId: 'field-001'));

        final tasks = await db.getTasksForField('field-001');
        expect(tasks.length, equals(2));
        expect(tasks.every((t) => t.fieldId == 'field-001'), isTrue);
      });

      test('getPendingTasks returns open and in_progress tasks', () async {
        db.seedTask(makeTask(id: 't001', status: 'open'));
        db.seedTask(makeTask(id: 't002', status: 'in_progress'));
        db.seedTask(makeTask(id: 't003', status: 'done'));

        final pending = await db.getPendingTasks('tenant-001');
        expect(pending.length, equals(2));
        expect(pending.every((t) => t.status != 'done'), isTrue);
      });

      test('getTaskById returns correct task', () async {
        db.seedTask(makeTask(id: 't001', title: 'مهمة الري'));

        final task = await db.getTaskById('t001');
        expect(task, isNotNull);
        expect(task!.title, equals('مهمة الري'));
      });

      test('getTaskById returns null for missing task', () async {
        final task = await db.getTaskById('no-such-task');
        expect(task, isNull);
      });

      test('Task tenant isolation in getAllTasks', () async {
        db.seedTask(makeTask(id: 't001', tenantId: 'tenant-A'));
        db.seedTask(makeTask(id: 't002', tenantId: 'tenant-B'));

        final tasksA = await db.getAllTasks('tenant-A');
        final tasksB = await db.getAllTasks('tenant-B');

        expect(tasksA.length, equals(1));
        expect(tasksB.length, equals(1));
      });
    });

    // =========================================================================
    // Full Sync Workflow Integration
    // تكامل سير عمل المزامنة الكاملة
    // =========================================================================

    group('Full Sync Workflow - سير عمل المزامنة الكاملة', () {
      test('Create field → queue → process → cleanup workflow', () async {
        // 1. Queue field creation in outbox
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'field',
          entityId: 'field-new-001',
          apiEndpoint: '/api/v1/fields',
          method: 'POST',
          payload: '{"name": "حقل القمح الجديد", "area": 5.5}',
        );

        // 2. Verify it's pending
        var pending = await db.getPendingOutbox();
        expect(pending.length, equals(1));
        expect(pending.first.entityId, equals('field-new-001'));

        // 3. Simulate successful upload: mark done
        await db.markOutboxDone(pending.first.id);

        // 4. Log success
        await db.logSync(
          type: 'upload_sync',
          status: 'success',
          message: 'Uploaded field creation',
        );

        // 5. Cleanup
        await db.cleanupOutbox();

        // 6. Verify state
        pending = await db.getPendingOutbox();
        expect(pending.isEmpty, isTrue);

        final logs = await db.getRecentSyncLogs();
        expect(logs.length, equals(1));
        expect(logs.first.status, equals('success'));
      });

      test('Offline edit → retry → success workflow', () async {
        // 1. Queue edit while offline
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'task',
          entityId: 'task-001',
          apiEndpoint: '/api/v1/tasks/task-001',
          method: 'PUT',
          payload: '{"status": "done"}',
          ifMatch: '"v1-old-etag"',
        );

        // 2. Try once, fail → bump retry
        var pending = await db.getPendingOutbox();
        await db.bumpOutboxRetry(pending.first.id);
        await db.logSync(
            type: 'upload_sync', status: 'failed', message: 'Network error');

        // 3. Verify retry count
        pending = await db.getPendingOutbox();
        expect(pending.first.retryCount, equals(1));

        // 4. Retry and succeed
        await db.markOutboxDone(pending.first.id);
        await db.logSync(
            type: 'upload_sync', status: 'success', message: 'Task updated');
        await db.cleanupOutbox();

        // 5. Final state
        expect((await db.getPendingOutbox()).isEmpty, isTrue);

        final logs = await db.getRecentSyncLogs();
        expect(logs.first.status, equals('success'));
      });

      test('Conflict detected → emit sync event → user reads event', () async {
        // 1. Simulate conflict during sync
        await db.addSyncEvent(
          tenantId: 'tenant-001',
          type: 'conflict',
          entityType: 'field',
          entityId: 'field-001',
          message:
              'تعارض: تم استخدام نسخة الخادم (الأحدث)',
        );

        // 2. Verify event is unread
        final events = await db.getUnreadSyncEvents('tenant-001');
        expect(events.length, equals(1));
        expect(events.first.type, equals('conflict'));
        expect(events.first.isRead, isFalse);

        // 3. User reads it
        await db.markSyncEventRead(events.first.id);

        // 4. Verify cleared
        final unread = await db.getUnreadSyncEvents('tenant-001');
        expect(unread.isEmpty, isTrue);
      });

      test(
          'Multiple entity types sync in single batch without cross-contamination',
          () async {
        // Arrange: queue fields, tasks, and an update
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'field',
          entityId: 'field-001',
          apiEndpoint: '/api/v1/fields',
          method: 'POST',
          payload: '{"name": "New Field"}',
        );
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'task',
          entityId: 'task-001',
          apiEndpoint: '/api/v1/tasks',
          method: 'POST',
          payload: '{"title": "New Task"}',
        );
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'field',
          entityId: 'field-002',
          apiEndpoint: '/api/v1/fields/field-002',
          method: 'PUT',
          payload: '{"name": "Updated Field"}',
          ifMatch: '"v1"',
        );

        // Process batch
        final pending = await db.getPendingOutbox();
        expect(pending.length, equals(3));

        // Mark all done
        for (final item in pending) {
          await db.markOutboxDone(item.id);
        }
        await db.cleanupOutbox();

        // Verify
        expect((await db.getPendingOutbox()).isEmpty, isTrue);
      });

      test('Database health stays consistent after sync operations', () async {
        // Add items
        for (int i = 0; i < 5; i++) {
          await db.queueOutboxItem(
            tenantId: 'tenant-001',
            entityType: 'task',
            entityId: 'task-$i',
            apiEndpoint: '/api/v1/tasks',
            method: 'POST',
            payload: '{}',
          );
        }

        var health = await db.checkHealth();
        expect(health['healthy'], isTrue);
        expect(health['pendingOutboxCount'], equals(5));

        // Process all
        final items = await db.getPendingOutbox();
        for (final item in items) {
          await db.markOutboxDone(item.id);
        }
        await db.cleanupOutbox();

        health = await db.checkHealth();
        expect(health['pendingOutboxCount'], equals(0));
      });
    });

    // =========================================================================
    // Stream Watcher Tests
    // اختبارات مراقبة البث
    // =========================================================================

    group('Stream Watcher Tests - اختبارات المراقبة', () {
      test('watchPendingOutboxCount emits updates', () async {
        final counts = <int>[];
        final sub = db.watchPendingOutboxCount().listen(counts.add);

        // Add an item
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'field',
          entityId: 'f001',
          apiEndpoint: '/api/v1/fields',
          method: 'POST',
          payload: '{}',
        );

        await Future.delayed(const Duration(milliseconds: 50));

        expect(counts.isNotEmpty, isTrue);
        expect(counts.last, greaterThan(0));

        await sub.cancel();
      });

      test('watchPendingOutboxCount decreases when item marked done', () async {
        final counts = <int>[];
        final sub = db.watchPendingOutboxCount().listen(counts.add);

        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'task',
          entityId: 't001',
          apiEndpoint: '/api/v1/tasks',
          method: 'POST',
          payload: '{}',
        );
        await Future.delayed(const Duration(milliseconds: 30));

        final pending = await db.getPendingOutbox();
        await db.markOutboxDone(pending.first.id);
        await Future.delayed(const Duration(milliseconds: 30));

        // Last count should be 0 (done item no longer pending)
        expect(counts.last, equals(0));

        await sub.cancel();
      });

      test('watchPendingTasks emits task updates', () async {
        final taskLists = <List<Task>>[];
        final sub = db
            .watchPendingTasks('tenant-001')
            .listen(taskLists.add);

        final now = DateTime.now();
        db.seedTask(Task(
          id: 't001',
          tenantId: 'tenant-001',
          fieldId: 'f001',
          farmId: null,
          title: 'Pending Task',
          description: null,
          status: 'open',
          priority: 'high',
          dueDate: null,
          assignedTo: null,
          evidenceNotes: null,
          evidencePhotos: null,
          createdAt: now,
          updatedAt: now,
          synced: false,
        ));

        await Future.delayed(const Duration(milliseconds: 50));

        expect(taskLists.isNotEmpty, isTrue);
        final lastList = taskLists.last;
        expect(lastList.any((t) => t.id == 't001'), isTrue);

        await sub.cancel();
      });

      test('watchUnreadEventsCount emits updates on new event', () async {
        final counts = <int>[];
        final sub =
            db.watchUnreadEventsCount('tenant-001').listen(counts.add);

        await db.addSyncEvent(
          tenantId: 'tenant-001',
          type: 'update',
          entityType: 'field',
          entityId: 'f001',
          message: 'Field updated from server',
        );

        await Future.delayed(const Duration(milliseconds: 50));

        expect(counts.isNotEmpty, isTrue);
        expect(counts.last, greaterThan(0));

        await sub.cancel();
      });
    });
  });
}
