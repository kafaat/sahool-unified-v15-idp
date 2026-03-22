import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/storage/database.dart';

import '../../../integration_test/helpers/mock_server.dart';
import '../mocks/mock_app_database.dart';

/// Integration Tests - Offline Sync
/// اختبارات تكامل المزامنة بدون اتصال
///
/// Tests offline-first sync patterns using MockAppDatabase and MockServer:
/// - Data caching in local database
/// - Outbox queuing while offline
/// - Sync processing when back online
/// - Conflict detection and resolution
/// - Network status transitions
/// - Delta sync and partial sync
/// - Data persistence across sessions

void main() {
  // ===========================================================================
  // Offline Data Caching
  // تخزين البيانات بدون اتصال
  // ===========================================================================

  group('Offline Data Caching - تخزين البيانات', () {
    late MockAppDatabase db;

    setUp(() {
      db = MockAppDatabase();
    });

    tearDown(() {
      db.clearAll();
      db.dispose();
    });

    test('fields are cached locally for offline access', () async {
      final now = DateTime.now();
      // Simulate: server returned fields, cache them locally
      for (int i = 0; i < 3; i++) {
        db.seedField(Field(
          id: 'field-$i',
          remoteId: 'remote-field-$i',
          tenantId: 'tenant-001',
          farmId: null,
          name: 'حقل $i',
          cropType: 'wheat',
          boundary: [],
          centroid: null,
          areaHectares: 5.0 + i,
          status: 'active',
          ndviCurrent: 0.65 + (i * 0.05),
          ndviUpdatedAt: now,
          synced: true,
          isDeleted: false,
          createdAt: now,
          updatedAt: now,
          etag: '"v1-field-$i"',
          serverUpdatedAt: now,
        ));
      }

      // Verify local cache
      final fields = await db.getFieldsForTenant('tenant-001');
      expect(fields.length, equals(3));
      expect(fields.every((f) => f.synced), isTrue);
      expect(fields.every((f) => f.tenantId == 'tenant-001'), isTrue);
    });

    test('locally created field is marked as unsynced', () async {
      final now = DateTime.now();
      db.seedField(Field(
        id: 'field-local-001',
        remoteId: null, // No remote ID yet
        tenantId: 'tenant-001',
        farmId: null,
        name: 'حقل محلي جديد',
        cropType: 'barley',
        boundary: [],
        centroid: null,
        areaHectares: 3.0,
        status: 'active',
        ndviCurrent: null,
        ndviUpdatedAt: null,
        synced: false, // Not synced
        isDeleted: false,
        createdAt: now,
        updatedAt: now,
        etag: null,
        serverUpdatedAt: null,
      ));

      final stats = await db.getStatistics();
      expect(stats['unsyncedFields'], equals(1));
    });

    test('tasks cached for offline field work', () async {
      final now = DateTime.now();
      // Seed tasks for a field
      for (int i = 0; i < 5; i++) {
        db.seedTask(Task(
          id: 'task-$i',
          tenantId: 'tenant-001',
          fieldId: 'field-001',
          farmId: null,
          title: 'مهمة $i',
          description: 'وصف المهمة $i',
          status: i < 3 ? 'open' : 'done',
          priority: i == 0 ? 'high' : 'medium',
          dueDate: now.add(Duration(days: i)),
          assignedTo: 'user-001',
          createdAt: now,
          updatedAt: now,
          synced: true,
        ));
      }

      final allTasks = await db.getAllTasks('tenant-001');
      expect(allTasks.length, equals(5));

      final pendingTasks = await db.getPendingTasks('tenant-001');
      expect(pendingTasks.length, equals(3));

      final fieldTasks = await db.getTasksForField('field-001');
      expect(fieldTasks.length, equals(5));
    });
  });

  // ===========================================================================
  // Outbox Queuing While Offline
  // صف العمليات أثناء الانقطاع
  // ===========================================================================

  group('Outbox Queuing While Offline - صف العمليات', () {
    late MockAppDatabase db;

    setUp(() {
      db = MockAppDatabase();
    });

    tearDown(() {
      db.clearAll();
      db.dispose();
    });

    test('field creation queued while offline', () async {
      await db.queueOutboxItem(
        tenantId: 'tenant-001',
        entityType: 'field',
        entityId: 'field-offline-001',
        apiEndpoint: '/api/v1/fields',
        method: 'POST',
        payload: jsonEncode({
          'name': 'حقل أنشئ بدون اتصال',
          'area': 7.5,
          'cropType': 'wheat',
          'irrigationType': 'drip',
        }),
      );

      final pending = await db.getPendingOutbox();
      expect(pending.length, equals(1));
      expect(pending.first.entityType, equals('field'));
      expect(pending.first.method, equals('POST'));
      expect(pending.first.isSynced, isFalse);
    });

    test('task update queued with ETag', () async {
      await db.queueOutboxItem(
        tenantId: 'tenant-001',
        entityType: 'task',
        entityId: 'task-001',
        apiEndpoint: '/api/v1/tasks/task-001',
        method: 'PUT',
        payload: jsonEncode({
          'status': 'completed',
          'completedAt': DateTime.now().toIso8601String(),
        }),
        ifMatch: '"v3-task-001"',
      );

      final pending = await db.getPendingOutbox();
      expect(pending.first.ifMatch, equals('"v3-task-001"'));
    });

    test('multiple offline changes maintain order', () async {
      final operations = [
        ('field', 'field-001', 'POST', '/api/v1/fields'),
        ('task', 'task-001', 'POST', '/api/v1/tasks'),
        ('field', 'field-001', 'PUT', '/api/v1/fields/field-001'),
        ('task', 'task-001', 'PUT', '/api/v1/tasks/task-001'),
        ('observation', 'obs-001', 'POST', '/api/v1/crop-health/observations'),
      ];

      for (final (type, id, method, endpoint) in operations) {
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: type,
          entityId: id,
          apiEndpoint: endpoint,
          method: method,
          payload: jsonEncode({'id': id, 'type': type}),
        );
      }

      final pending = await db.getPendingOutbox();
      expect(pending.length, equals(5));
      // First item should be the first queued
      expect(pending.first.entityType, equals('field'));
      expect(pending.first.method, equals('POST'));
    });
  });

  // ===========================================================================
  // Sync Processing When Online
  // معالجة المزامنة عند الاتصال
  // ===========================================================================

  group('Sync Processing When Online - معالجة المزامنة', () {
    late MockAppDatabase db;
    late MockHttpClient client;

    setUp(() {
      db = MockAppDatabase();
      setupMockServer();
      client = MockHttpClient();
    });

    tearDown(() {
      db.clearAll();
      db.dispose();
      resetMockServer();
    });

    test('outbox items synced in batch when online', () async {
      // Queue 3 offline changes
      for (int i = 0; i < 3; i++) {
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'field',
          entityId: 'field-$i',
          apiEndpoint: '/api/v1/fields',
          method: 'POST',
          payload: jsonEncode({
            'name': 'Offline Field $i',
            'area': 5.0 + i,
          }),
        );
      }

      // Simulate sync: process each outbox item via API
      final pending = await db.getPendingOutbox();
      expect(pending.length, equals(3));

      int synced = 0;
      for (final item in pending) {
        final payload = jsonDecode(item.payload) as Map<String, dynamic>;
        final response = await client.post(
          item.apiEndpoint,
          body: payload,
        );

        if (response.statusCode == 200 || response.statusCode == 201) {
          await db.markOutboxDone(item.id);
          synced++;
        } else {
          await db.bumpOutboxRetry(item.id);
        }
      }

      expect(synced, equals(3));

      // All processed
      final remaining = await db.getPendingOutbox();
      expect(remaining.isEmpty, isTrue);

      // Log sync result
      await db.logSync(
        type: 'outbox_sync',
        status: 'success',
        message: 'Synced $synced items',
      );

      final logs = await db.getRecentSyncLogs(limit: 1);
      expect(logs.first.status, equals('success'));
    });

    test('failed sync increments retry count', () async {
      await db.queueOutboxItem(
        tenantId: 'tenant-001',
        entityType: 'field',
        entityId: 'field-fail',
        apiEndpoint: '/api/v1/nonexistent',
        method: 'POST',
        payload: '{}',
      );

      final pending = await db.getPendingOutbox();
      final item = pending.first;

      // Simulate failed API call
      final response = await client.post(item.apiEndpoint);
      expect(response.statusCode, equals(404));

      // Bump retry
      await db.bumpOutboxRetry(item.id);

      final retried = await db.getOutboxItemById(item.id);
      expect(retried?.retryCount, equals(1));
    });

    test('server error triggers retry with backoff tracking', () async {
      // Stub server error
      stubResponse('/api/v1/fields', MockResponse.serverError);

      await db.queueOutboxItem(
        tenantId: 'tenant-001',
        entityType: 'field',
        entityId: 'field-retry',
        apiEndpoint: '/api/v1/fields',
        method: 'POST',
        payload: jsonEncode({'name': 'Retry Field'}),
      );

      final pending = await db.getPendingOutbox();

      // Try 3 times
      for (int attempt = 0; attempt < 3; attempt++) {
        final response = await client.post(
          pending.first.apiEndpoint,
          body: jsonDecode(pending.first.payload),
        );
        if (response.statusCode >= 500) {
          await db.bumpOutboxRetry(pending.first.id);
        }
      }

      final item = await db.getOutboxItemById(pending.first.id);
      expect(item?.retryCount, equals(3));
      expect(item?.isSynced, isFalse);
    });
  });

  // ===========================================================================
  // Conflict Detection & Resolution
  // كشف التعارضات وحلها
  // ===========================================================================

  group('Conflict Detection & Resolution - كشف التعارضات', () {
    late MockAppDatabase db;

    setUp(() {
      db = MockAppDatabase();
    });

    tearDown(() {
      db.clearAll();
      db.dispose();
    });

    test('ETag mismatch generates conflict sync event', () async {
      // Simulate: local update has old ETag, server has newer
      final now = DateTime.now();
      db.seedField(Field(
        id: 'field-001',
        remoteId: 'remote-001',
        tenantId: 'tenant-001',
        farmId: null,
        name: 'Local Version',
        cropType: 'wheat',
        boundary: [],
        centroid: null,
        areaHectares: 5.0,
        status: 'active',
        ndviCurrent: null,
        ndviUpdatedAt: null,
        synced: false,
        isDeleted: false,
        createdAt: now,
        updatedAt: now,
        etag: '"v1-old"',
        serverUpdatedAt: now.subtract(const Duration(hours: 1)),
      ));

      // Simulate conflict detected during sync
      await db.addSyncEvent(
        tenantId: 'tenant-001',
        type: 'conflict',
        entityType: 'field',
        entityId: 'field-001',
        message: 'تعارض: ETag المحلي v1-old لا يطابق الخادم v3-new',
      );

      // Resolve: accept server version
      await db.updateFieldWithEtag(
        fieldId: 'field-001',
        etag: '"v3-new"',
        serverUpdatedAt: now,
      );

      // Mark conflict as read
      final events = await db.getUnreadSyncEvents('tenant-001');
      expect(events.length, equals(1));
      expect(events.first.type, equals('conflict'));

      await db.markSyncEventRead(events.first.id);
      final unread = await db.getUnreadSyncEvents('tenant-001');
      expect(unread.isEmpty, isTrue);

      // Field should now be synced with new ETag
      final field = await db.getFieldById('field-001');
      expect(field?.etag, equals('"v3-new"'));
      expect(field?.synced, isTrue);
    });

    test('server-wins resolution updates local data', () async {
      final now = DateTime.now();
      db.seedField(Field(
        id: 'field-conflict',
        remoteId: 'remote-conflict',
        tenantId: 'tenant-001',
        farmId: null,
        name: 'اسم محلي',
        cropType: 'wheat',
        boundary: [],
        centroid: null,
        areaHectares: 5.0,
        status: 'active',
        ndviCurrent: null,
        ndviUpdatedAt: null,
        synced: false,
        isDeleted: false,
        createdAt: now,
        updatedAt: now.subtract(const Duration(minutes: 30)),
        etag: '"v2"',
        serverUpdatedAt: now.subtract(const Duration(hours: 1)),
      ));

      // Server version is newer
      final serverUpdatedAt = now;
      await db.updateFieldWithEtag(
        fieldId: 'field-conflict',
        etag: '"v4-server"',
        serverUpdatedAt: serverUpdatedAt,
      );

      final resolved = await db.getFieldById('field-conflict');
      expect(resolved?.etag, equals('"v4-server"'));
      expect(resolved?.synced, isTrue);
    });
  });

  // ===========================================================================
  // Network Transition Scenarios
  // سيناريوهات انتقال الشبكة
  // ===========================================================================

  group('Network Transition Scenarios - انتقال الشبكة', () {
    late MockAppDatabase db;
    late MockHttpClient client;

    setUp(() {
      db = MockAppDatabase();
      setupMockServer();
      client = MockHttpClient();
    });

    tearDown(() {
      db.clearAll();
      db.dispose();
      resetMockServer();
    });

    test('offline → online: queued changes sync successfully', () async {
      // Phase 1: Offline - queue changes
      await db.queueOutboxItem(
        tenantId: 'tenant-001',
        entityType: 'field',
        entityId: 'field-offline',
        apiEndpoint: '/api/v1/fields',
        method: 'POST',
        payload: jsonEncode({'name': 'Offline Created'}),
      );
      await db.queueOutboxItem(
        tenantId: 'tenant-001',
        entityType: 'task',
        entityId: 'task-offline',
        apiEndpoint: '/api/v1/tasks',
        method: 'POST',
        payload: jsonEncode({'title': 'Offline Task'}),
      );

      final beforeSync = await db.getPendingOutbox();
      expect(beforeSync.length, equals(2));

      // Phase 2: Online - process queue
      // Stub task endpoint
      MockServer.instance.stub('/api/v1/tasks', (request) {
        return MockResponse.created({'data': {'id': 'task-new', ...?request.body}});
      });

      for (final item in beforeSync) {
        final resp = await client.post(
          item.apiEndpoint,
          body: jsonDecode(item.payload),
        );
        if (resp.statusCode == 200 || resp.statusCode == 201) {
          await db.markOutboxDone(item.id);
        }
      }

      // Phase 3: Verify sync complete
      final afterSync = await db.getPendingOutbox();
      expect(afterSync.isEmpty, isTrue);

      await db.logSync(
        type: 'full_sync',
        status: 'success',
        message: 'Synced 2 items after reconnection',
      );

      final logs = await db.getRecentSyncLogs(limit: 1);
      expect(logs.first.message, contains('2 items'));
    });

    test('intermittent connectivity: partial sync with retry', () async {
      // Queue 4 items
      for (int i = 0; i < 4; i++) {
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'field',
          entityId: 'field-$i',
          apiEndpoint: '/api/v1/fields',
          method: 'POST',
          payload: jsonEncode({'name': 'Field $i'}),
        );
      }

      final items = await db.getPendingOutbox();

      // First 2 succeed, last 2 fail (connection drops)
      await db.markOutboxDone(items[0].id);
      await db.markOutboxDone(items[1].id);
      await db.bumpOutboxRetry(items[2].id);
      await db.bumpOutboxRetry(items[3].id);

      final remaining = await db.getPendingOutbox();
      expect(remaining.length, equals(2));
      expect(remaining.every((o) => o.retryCount == 1), isTrue);

      // Second attempt: all succeed
      for (final item in remaining) {
        await db.markOutboxDone(item.id);
      }

      final afterRetry = await db.getPendingOutbox();
      expect(afterRetry.isEmpty, isTrue);
    });
  });

  // ===========================================================================
  // Data Persistence
  // استمرار البيانات
  // ===========================================================================

  group('Data Persistence - استمرار البيانات', () {
    test('database health tracks pending items', () async {
      final db = MockAppDatabase();

      // Empty database is healthy
      var health = await db.checkHealth();
      expect(health['healthy'], isTrue);
      expect(health['pendingOutboxCount'], equals(0));

      // Queue items
      for (int i = 0; i < 5; i++) {
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'field',
          entityId: 'field-$i',
          apiEndpoint: '/api/v1/fields',
          method: 'POST',
          payload: '{}',
        );
      }

      health = await db.checkHealth();
      expect(health['pendingOutboxCount'], equals(5));

      db.clearAll();
      db.dispose();
    });

    test('sync logs persist across operations', () async {
      final db = MockAppDatabase();

      // Log multiple sync events
      await db.logSync(
        type: 'full_sync',
        status: 'success',
        message: 'First sync: 10 items',
      );
      await Future.delayed(const Duration(milliseconds: 5));
      await db.logSync(
        type: 'delta_sync',
        status: 'success',
        message: 'Delta: 2 items',
      );
      await Future.delayed(const Duration(milliseconds: 5));
      await db.logSync(
        type: 'outbox_sync',
        status: 'failed',
        message: 'Network timeout',
      );

      final logs = await db.getRecentSyncLogs(limit: 10);
      expect(logs.length, equals(3));
      // Most recent first
      expect(logs.first.type, equals('outbox_sync'));
      expect(logs.first.status, equals('failed'));
      expect(logs.last.type, equals('full_sync'));

      db.clearAll();
      db.dispose();
    });
  });
}
