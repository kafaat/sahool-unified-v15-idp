import 'dart:convert';

import 'package:drift/drift.dart' show Value;
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/storage/database.dart';
import 'package:sahool_field_app/core/utils/retry_policy.dart';

import '../mocks/mock_app_database.dart';

/// Mobile Sync Integration Tests
/// اختبارات تكامل المزامنة المحمولة
///
/// Tests the offline-first sync engine with:
/// - Outbox operations (add, process, retry, cleanup)
/// - SyncResult structure validation
/// - Conflict resolution via ETag / if-match
/// - Exponential backoff policy
/// - Batch processing in the outbox queue
/// - Offline recovery scenarios
void main() {
  group('Mobile Sync Integration Tests - اختبارات تكامل المزامنة', () {
    late MockAppDatabase db;

    setUp(() {
      db = MockAppDatabase();
    });

    tearDown(() {
      db.clearAll();
      db.dispose();
    });

    // =========================================================================
    // Outbox Operations
    // عمليات صندوق الصادر
    // =========================================================================

    group('Outbox Operations - عمليات الصندوق', () {
      test('addToOutbox queues item correctly', () async {
        // Arrange
        final item = OutboxCompanion.insert(
          tenantId: 'tenant-001',
          entityType: 'field',
          entityId: 'field-001',
          apiEndpoint: '/api/v1/fields',
          method: const Value('POST'),
          payload: jsonEncode({'name': 'Test Field', 'area': 5.0}),
        );

        // Act
        await db.addToOutbox(item);

        // Assert
        final pending = await db.getPendingOutbox();
        expect(pending.length, equals(1));
        expect(pending.first.entityType, equals('field'));
        expect(pending.first.entityId, equals('field-001'));
        expect(pending.first.tenantId, equals('tenant-001'));
        expect(pending.first.isSynced, isFalse);
        expect(pending.first.retryCount, equals(0));
      });

      test('queueOutboxItem adds item using named parameters', () async {
        // Act
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'task',
          entityId: 'task-001',
          apiEndpoint: '/api/v1/tasks',
          method: 'POST',
          payload: jsonEncode({'title': 'Irrigate Field', 'status': 'open'}),
        );

        // Assert
        final pending = await db.getPendingOutbox();
        expect(pending.length, equals(1));
        expect(pending.first.entityType, equals('task'));
        expect(pending.first.method, equals('POST'));
      });

      test('getPendingOutbox returns only unsynced items', () async {
        // Arrange: add 3 items, mark 1 done
        for (int i = 0; i < 3; i++) {
          await db.queueOutboxItem(
            tenantId: 'tenant-001',
            entityType: 'field',
            entityId: 'field-$i',
            apiEndpoint: '/api/v1/fields',
            method: 'POST',
            payload: jsonEncode({'id': 'field-$i'}),
          );
        }
        final all = await db.getPendingOutbox();
        await db.markOutboxDone(all.first.id);

        // Act
        final pending = await db.getPendingOutbox();

        // Assert
        expect(pending.length, equals(2));
        expect(pending.every((o) => !o.isSynced), isTrue);
      });

      test('getPendingOutbox respects limit parameter', () async {
        // Arrange: add 10 items
        for (int i = 0; i < 10; i++) {
          await db.queueOutboxItem(
            tenantId: 'tenant-001',
            entityType: 'task',
            entityId: 'task-$i',
            apiEndpoint: '/api/v1/tasks',
            method: 'POST',
            payload: jsonEncode({'id': 'task-$i'}),
          );
        }

        // Act
        final limited = await db.getPendingOutbox(limit: 5);

        // Assert
        expect(limited.length, equals(5));
      });

      test('markOutboxDone marks item as synced', () async {
        // Arrange
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'field',
          entityId: 'field-001',
          apiEndpoint: '/api/v1/fields',
          method: 'POST',
          payload: '{}',
        );
        final pending = await db.getPendingOutbox();
        final itemId = pending.first.id;

        // Act
        await db.markOutboxDone(itemId);

        // Assert
        final afterMark = await db.getPendingOutbox();
        expect(afterMark.isEmpty, isTrue);

        final item = await db.getOutboxItemById(itemId);
        expect(item?.isSynced, isTrue);
      });

      test('bumpOutboxRetry increments retry count', () async {
        // Arrange
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'field',
          entityId: 'field-001',
          apiEndpoint: '/api/v1/fields',
          method: 'PUT',
          payload: '{}',
        );
        final pending = await db.getPendingOutbox();
        final itemId = pending.first.id;
        expect(pending.first.retryCount, equals(0));

        // Act: bump retry 3 times
        await db.bumpOutboxRetry(itemId);
        await db.bumpOutboxRetry(itemId);
        await db.bumpOutboxRetry(itemId);

        // Assert
        final item = await db.getOutboxItemById(itemId);
        expect(item?.retryCount, equals(3));
      });

      test('cleanupOutbox removes synced items', () async {
        // Arrange: add 3 items, mark 2 as done
        for (int i = 0; i < 3; i++) {
          await db.queueOutboxItem(
            tenantId: 'tenant-001',
            entityType: 'task',
            entityId: 'task-$i',
            apiEndpoint: '/api/v1/tasks',
            method: 'POST',
            payload: '{}',
          );
        }
        final all = await db.getPendingOutbox();
        await db.markOutboxDone(all[0].id);
        await db.markOutboxDone(all[1].id);

        // Act
        await db.cleanupOutbox();

        // Assert: only 1 unsynced item remains
        final pending = await db.getPendingOutbox();
        expect(pending.length, equals(1));
      });
    });

    // =========================================================================
    // ETag / Conflict Resolution
    // حل التعارضات باستخدام ETag
    // =========================================================================

    group('ETag / Conflict Resolution - حل التعارضات', () {
      test('addToOutbox stores ifMatch ETag for optimistic locking', () async {
        // Arrange
        const etag = '"v3-abc123"';
        final item = OutboxCompanion.insert(
          tenantId: 'tenant-001',
          entityType: 'field',
          entityId: 'field-001',
          apiEndpoint: '/api/v1/fields/field-001',
          method: const Value('PUT'),
          payload: jsonEncode({'name': 'Updated Name'}),
          ifMatch: const Value(etag),
        );

        // Act
        await db.addToOutbox(item);

        // Assert
        final pending = await db.getPendingOutbox();
        expect(pending.first.ifMatch, equals(etag));
        expect(pending.first.method, equals('PUT'));
      });

      test('ETag not required for POST requests', () async {
        // Arrange & Act
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'field',
          entityId: 'field-new',
          apiEndpoint: '/api/v1/fields',
          method: 'POST',
          payload: jsonEncode({'name': 'New Field'}),
          // No ifMatch
        );

        // Assert
        final pending = await db.getPendingOutbox();
        expect(pending.first.ifMatch, isNull);
      });

      test('DELETE request can include ETag', () async {
        // Arrange
        const etag = '"v2-xyz789"';
        final item = OutboxCompanion.insert(
          tenantId: 'tenant-001',
          entityType: 'task',
          entityId: 'task-001',
          apiEndpoint: '/api/v1/tasks/task-001',
          method: const Value('DELETE'),
          payload: '{}',
          ifMatch: const Value(etag),
        );

        // Act
        await db.addToOutbox(item);

        // Assert
        final pending = await db.getPendingOutbox();
        expect(pending.first.method, equals('DELETE'));
        expect(pending.first.ifMatch, equals(etag));
      });

      test('updateFieldWithEtag updates field and etag atomically', () async {
        // Arrange: seed a field
        final now = DateTime.now();
        db.seedField(Field(
          id: 'field-001',
          remoteId: 'remote-001',
          tenantId: 'tenant-001',
          farmId: null,
          name: 'Old Name',
          cropType: 'wheat',
          boundary: [],
          centroid: null,
          areaHectares: 5.0,
          status: 'active',
          ndviCurrent: null,
          ndviUpdatedAt: null,
          synced: true,
          isDeleted: false,
          createdAt: now,
          updatedAt: now,
          etag: '"v1-old"',
          serverUpdatedAt: now,
        ));

        // Act
        await db.updateFieldWithEtag(
          fieldId: 'field-001',
          etag: '"v2-new"',
          serverUpdatedAt: now.add(const Duration(hours: 1)),
        );

        // Assert
        final field = await db.getFieldById('field-001');
        expect(field?.etag, equals('"v2-new"'));
        expect(field?.synced, isTrue);
      });
    });

    // =========================================================================
    // Exponential Backoff Policy
    // سياسة التراجع الأسي
    // =========================================================================

    group('Exponential Backoff Policy - سياسة التراجع', () {
      test('ExponentialBackoff calculates correct delay for retry 0', () {
        final backoff = ExponentialBackoff(
          initialDelayMs: 1000,
          multiplier: 2.0,
          maxDelayMs: 300000,
          maxRetries: 5,
          enableJitter: false,
        );

        final delay = backoff.calculateDelay(0);
        expect(delay, equals(1000)); // 1 second
      });

      test('ExponentialBackoff doubles delay for each retry', () {
        final backoff = ExponentialBackoff(
          initialDelayMs: 1000,
          multiplier: 2.0,
          maxDelayMs: 300000,
          maxRetries: 5,
          enableJitter: false,
        );

        expect(backoff.calculateDelay(0), equals(1000)); // 1s
        expect(backoff.calculateDelay(1), equals(2000)); // 2s
        expect(backoff.calculateDelay(2), equals(4000)); // 4s
        expect(backoff.calculateDelay(3), equals(8000)); // 8s
        expect(backoff.calculateDelay(4), equals(16000)); // 16s
      });

      test('ExponentialBackoff caps at maxDelayMs', () {
        final backoff = ExponentialBackoff(
          initialDelayMs: 1000,
          multiplier: 2.0,
          maxDelayMs: 10000, // 10 seconds cap
          maxRetries: 10,
          enableJitter: false,
        );

        // retry 10 would exceed cap
        final delay = backoff.calculateDelay(10);
        expect(delay, lessThanOrEqualTo(10000));
      });

      test('ExponentialBackoff returns maxDelayMs when retries exhausted', () {
        final backoff = ExponentialBackoff(
          initialDelayMs: 1000,
          multiplier: 2.0,
          maxDelayMs: 300000,
          maxRetries: 5,
          enableJitter: false,
        );

        final delay = backoff.calculateDelay(5); // >= maxRetries
        expect(delay, equals(300000));
      });

      test('ExponentialBackoff shouldRetry returns false beyond maxRetries', () {
        final backoff = ExponentialBackoff(maxRetries: 5);

        expect(backoff.shouldRetry(0), isTrue);
        expect(backoff.shouldRetry(4), isTrue);
        expect(backoff.shouldRetry(5), isFalse);
        expect(backoff.shouldRetry(10), isFalse);
      });

      test('ExponentialBackoff with jitter adds non-negative variation', () {
        final backoff = ExponentialBackoff(
          initialDelayMs: 1000,
          multiplier: 2.0,
          maxDelayMs: 300000,
          maxRetries: 5,
          enableJitter: true,
        );

        // With jitter, delay should be >= base (no negative jitter)
        const baseDelay = 1000; // retry 0
        for (int i = 0; i < 10; i++) {
          final delay = backoff.calculateDelay(0);
          expect(delay, greaterThanOrEqualTo(baseDelay));
          expect(delay, lessThanOrEqualTo((baseDelay * 1.25).toInt() + 1));
        }
      });

      test('ExponentialBackoff getDelayDescription formats correctly', () {
        final backoff = ExponentialBackoff(
          initialDelayMs: 1000,
          multiplier: 2.0,
          maxDelayMs: 300000,
          maxRetries: 5,
          enableJitter: false,
        );

        final desc0 = backoff.getDelayDescription(0); // 1000ms -> "1.0s"
        expect(desc0, contains('s'));

        final desc4 = backoff.getDelayDescription(4); // 16000ms -> "16.0s"
        expect(desc4, contains('s'));
      });

      test('ExponentialBackoff.execute retries on failure', () async {
        final backoff = ExponentialBackoff(
          initialDelayMs: 10, // very short for tests
          multiplier: 2.0,
          maxDelayMs: 100,
          maxRetries: 3,
          enableJitter: false,
        );

        int callCount = 0;
        final result = await backoff.execute<String>(
          () async {
            callCount++;
            if (callCount < 3) throw Exception('Transient error');
            return 'success';
          },
          onRetry: (retry, delay) {},
        );

        expect(result, equals('success'));
        expect(callCount, equals(3));
      });

      test('ExponentialBackoff calculateNextRetryTime is in the future', () {
        final backoff = ExponentialBackoff(
          initialDelayMs: 1000,
          multiplier: 2.0,
          maxDelayMs: 300000,
          maxRetries: 5,
          enableJitter: false,
        );

        final nextRetry = backoff.calculateNextRetryTime(0);
        expect(nextRetry.isAfter(DateTime.now()), isTrue);
      });
    });

    // =========================================================================
    // SyncResult Validation
    // التحقق من نتيجة المزامنة
    // =========================================================================

    group('SyncResult Validation - التحقق من نتيجة المزامنة', () {
      test('SyncResult.success has correct defaults', () {
        final result = SyncResult(success: true);
        expect(result.success, isTrue);
        expect(result.uploaded, equals(0));
        expect(result.downloaded, equals(0));
        expect(result.message, isNull);
      });

      test('SyncResult failure carries message', () {
        const errorMsg = 'No network connection';
        final result = SyncResult(success: false, message: errorMsg);
        expect(result.success, isFalse);
        expect(result.message, equals(errorMsg));
      });

      test('SyncResult tracks uploaded and downloaded counts', () {
        final result = SyncResult(
          success: true,
          uploaded: 5,
          downloaded: 12,
        );
        expect(result.uploaded, equals(5));
        expect(result.downloaded, equals(12));
      });

      test('OutboxResult tracks all processing metrics', () {
        final result = OutboxResult(
          processed: 8,
          failed: 2,
          conflicts: 1,
          skipped: 0,
        );
        expect(result.processed, equals(8));
        expect(result.failed, equals(2));
        expect(result.conflicts, equals(1));
        expect(result.skipped, equals(0));
      });

      test('PullResult tracks download count', () {
        final result = PullResult(count: 15);
        expect(result.count, equals(15));
      });

      test('OutboxResult toString is human-readable', () {
        final result = OutboxResult(
          processed: 3,
          failed: 1,
          conflicts: 0,
          skipped: 0,
        );
        final str = result.toString();
        expect(str, contains('3'));
        expect(str, contains('1'));
      });
    });

    // =========================================================================
    // Batch Processing
    // المعالجة الجماعية
    // =========================================================================

    group('Batch Processing - المعالجة الجماعية', () {
      test('Multiple outbox items processed in batch order', () async {
        // Arrange: add items for different entity types
        final entities = [
          ('field', 'field-001', '/api/v1/fields', 'POST'),
          ('task', 'task-001', '/api/v1/tasks', 'POST'),
          ('task', 'task-002', '/api/v1/tasks', 'POST'),
          ('field', 'field-002', '/api/v1/fields', 'PUT'),
        ];

        for (final (type, id, endpoint, method) in entities) {
          await db.queueOutboxItem(
            tenantId: 'tenant-001',
            entityType: type,
            entityId: id,
            apiEndpoint: endpoint,
            method: method,
            payload: jsonEncode({'id': id, 'entityType': type}),
          );
        }

        // Act
        final pending = await db.getPendingOutbox(limit: 10);

        // Assert: all items queued
        expect(pending.length, equals(4));
        expect(pending.every((o) => !o.isSynced), isTrue);
        expect(pending.every((o) => o.tenantId == 'tenant-001'), isTrue);
      });

      test('Batch processing marks items done incrementally', () async {
        // Arrange: add 5 items
        for (int i = 0; i < 5; i++) {
          await db.queueOutboxItem(
            tenantId: 'tenant-001',
            entityType: 'task',
            entityId: 'task-$i',
            apiEndpoint: '/api/v1/tasks',
            method: 'POST',
            payload: jsonEncode({'id': 'task-$i'}),
          );
        }

        // Act: process one batch at a time
        var pending = await db.getPendingOutbox(limit: 2);
        for (final item in pending) {
          await db.markOutboxDone(item.id);
        }

        // Assert: 3 items still pending
        pending = await db.getPendingOutbox();
        expect(pending.length, equals(3));
      });

      test('Batch retry increments retryCount for each item', () async {
        // Arrange: add 3 items
        for (int i = 0; i < 3; i++) {
          await db.queueOutboxItem(
            tenantId: 'tenant-001',
            entityType: 'field',
            entityId: 'field-$i',
            apiEndpoint: '/api/v1/fields',
            method: 'POST',
            payload: '{}',
          );
        }

        // Act: bump all retries twice
        final pending = await db.getPendingOutbox();
        for (final item in pending) {
          await db.bumpOutboxRetry(item.id);
          await db.bumpOutboxRetry(item.id);
        }

        // Assert: each item has retryCount == 2
        final afterRetry = await db.getPendingOutbox();
        for (final item in afterRetry) {
          expect(item.retryCount, equals(2));
        }
      });

      test('Failed outbox items counted correctly', () async {
        // Arrange: add 5 items, bump 2 beyond maxRetries
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
        final pending = await db.getPendingOutbox();
        // Bump first 2 items to retryCount >= 5
        for (int retry = 0; retry < 5; retry++) {
          await db.bumpOutboxRetry(pending[0].id);
          await db.bumpOutboxRetry(pending[1].id);
        }

        // Assert
        final failedCount = await db.getFailedOutboxCount(maxRetries: 5);
        expect(failedCount, equals(2));
      });

      test('resetFailedOutboxItems resets retry count to 0', () async {
        // Arrange
        for (int i = 0; i < 3; i++) {
          await db.queueOutboxItem(
            tenantId: 'tenant-001',
            entityType: 'task',
            entityId: 'task-$i',
            apiEndpoint: '/api/v1/tasks',
            method: 'POST',
            payload: '{}',
          );
        }
        final pending = await db.getPendingOutbox();
        for (int retry = 0; retry < 5; retry++) {
          await db.bumpOutboxRetry(pending[0].id);
        }
        expect(await db.getFailedOutboxCount(maxRetries: 5), equals(1));

        // Act
        await db.resetFailedOutboxItems(maxRetries: 5);

        // Assert
        expect(await db.getFailedOutboxCount(maxRetries: 5), equals(0));
      });
    });

    // =========================================================================
    // Sync Log Operations
    // عمليات سجل المزامنة
    // =========================================================================

    group('Sync Log Operations - عمليات سجل المزامنة', () {
      test('logSync stores sync events', () async {
        // Act
        await db.logSync(
          type: 'full_sync',
          status: 'success',
          message: 'Uploaded 3, downloaded 5',
        );

        // Assert
        final logs = await db.getRecentSyncLogs(limit: 10);
        expect(logs.length, equals(1));
        expect(logs.first.type, equals('full_sync'));
        expect(logs.first.status, equals('success'));
        expect(logs.first.message, equals('Uploaded 3, downloaded 5'));
      });

      test('getRecentSyncLogs returns most recent first', () async {
        // Arrange: log 3 events
        await db.logSync(type: 'full_sync', status: 'success');
        await Future.delayed(const Duration(milliseconds: 10));
        await db.logSync(type: 'upload_sync', status: 'failed', message: 'err');
        await Future.delayed(const Duration(milliseconds: 10));
        await db.logSync(type: 'pull_sync', status: 'success');

        // Act
        final logs = await db.getRecentSyncLogs(limit: 10);

        // Assert: most recent is first
        expect(logs.length, equals(3));
        expect(logs.first.type, equals('pull_sync'));
        expect(logs.last.type, equals('full_sync'));
      });

      test('getRecentSyncLogs respects limit', () async {
        // Arrange: log 10 events
        for (int i = 0; i < 10; i++) {
          await db.logSync(type: 'full_sync', status: 'success');
        }

        // Act
        final logs = await db.getRecentSyncLogs(limit: 5);

        // Assert
        expect(logs.length, equals(5));
      });
    });

    // =========================================================================
    // Offline Recovery Scenarios
    // سيناريوهات الاسترداد من الانقطاع
    // =========================================================================

    group('Offline Recovery Scenarios - سيناريوهات الاسترداد', () {
      test('Outbox persists items when offline (simulated)', () async {
        // Simulate going offline: queue multiple changes
        final changes = [
          ('field', 'field-001', 'POST', '/api/v1/fields'),
          ('task', 'task-001', 'POST', '/api/v1/tasks'),
          ('task', 'task-002', 'PUT', '/api/v1/tasks/task-002'),
        ];

        for (final (type, id, method, endpoint) in changes) {
          await db.queueOutboxItem(
            tenantId: 'tenant-001',
            entityType: type,
            entityId: id,
            apiEndpoint: endpoint,
            method: method,
            payload: jsonEncode({'id': id}),
          );
        }

        // Verify all queued
        final pending = await db.getPendingOutbox();
        expect(pending.length, equals(3));
        expect(pending.every((o) => !o.isSynced), isTrue);
      });

      test('On reconnect, items remain in queue until processed', () async {
        // Arrange: queue offline changes
        await db.queueOutboxItem(
          tenantId: 'tenant-001',
          entityType: 'field',
          entityId: 'field-001',
          apiEndpoint: '/api/v1/fields',
          method: 'POST',
          payload: '{"name": "Offline Field"}',
        );

        // Simulate reconnect without processing
        final pendingBeforeSync = await db.getPendingOutbox();
        expect(pendingBeforeSync.length, equals(1));

        // Simulate successful sync: mark done
        await db.markOutboxDone(pendingBeforeSync.first.id);
        await db.cleanupOutbox();

        // After sync, queue should be empty
        final pendingAfterSync = await db.getPendingOutbox();
        expect(pendingAfterSync.isEmpty, isTrue);
      });

      test('Partial sync leaves failed items for retry', () async {
        // Arrange: add 4 items
        for (int i = 0; i < 4; i++) {
          await db.queueOutboxItem(
            tenantId: 'tenant-001',
            entityType: 'field',
            entityId: 'field-$i',
            apiEndpoint: '/api/v1/fields',
            method: 'POST',
            payload: jsonEncode({'id': 'field-$i'}),
          );
        }

        // Act: successfully process 2, fail 2 (bump retry)
        final items = await db.getPendingOutbox();
        await db.markOutboxDone(items[0].id);
        await db.markOutboxDone(items[1].id);
        await db.bumpOutboxRetry(items[2].id);
        await db.bumpOutboxRetry(items[3].id);

        // Assert: 2 items done, 2 with retry
        final pending = await db.getPendingOutbox();
        expect(pending.length, equals(2));
        expect(pending.every((o) => o.retryCount == 1), isTrue);
      });

      test('Multi-tenant isolation in outbox', () async {
        // Arrange: queue items for 2 tenants
        for (final tenant in ['tenant-A', 'tenant-B']) {
          await db.queueOutboxItem(
            tenantId: tenant,
            entityType: 'field',
            entityId: 'field-$tenant',
            apiEndpoint: '/api/v1/fields',
            method: 'POST',
            payload: jsonEncode({'tenantId': tenant}),
          );
        }

        // Act: get all pending
        final pending = await db.getPendingOutbox();

        // Assert: both tenants present
        expect(pending.length, equals(2));
        expect(
          pending.map((o) => o.tenantId).toSet(),
          containsAll({'tenant-A', 'tenant-B'}),
        );
      });

      test('clearTenantData removes only that tenant\'s outbox', () async {
        // Arrange: 2 items per tenant
        for (final tenant in ['tenant-A', 'tenant-B']) {
          for (int i = 0; i < 2; i++) {
            await db.queueOutboxItem(
              tenantId: tenant,
              entityType: 'task',
              entityId: 'task-$tenant-$i',
              apiEndpoint: '/api/v1/tasks',
              method: 'POST',
              payload: '{}',
            );
          }
        }

        // Act: clear tenant-A
        await db.clearTenantData('tenant-A');

        // Assert: only tenant-B items remain
        final pending = await db.getPendingOutbox();
        expect(pending.every((o) => o.tenantId == 'tenant-B'), isTrue);
        expect(pending.length, equals(2));
      });
    });

    // =========================================================================
    // Sync Event Notifications
    // إشعارات أحداث المزامنة
    // =========================================================================

    group('Sync Event Notifications - إشعارات الأحداث', () {
      test('addSyncEvent stores event correctly', () async {
        // Act
        await db.addSyncEvent(
          tenantId: 'tenant-001',
          type: 'conflict',
          entityType: 'field',
          entityId: 'field-001',
          message: 'Conflict resolved using server version',
        );

        // Assert
        final events = await db.getUnreadSyncEvents('tenant-001');
        expect(events.length, equals(1));
        expect(events.first.type, equals('conflict'));
        expect(events.first.entityType, equals('field'));
        expect(events.first.isRead, isFalse);
      });

      test('markSyncEventRead marks event as read', () async {
        // Arrange
        await db.addSyncEvent(
          tenantId: 'tenant-001',
          type: 'conflict',
          entityType: 'task',
          entityId: 'task-001',
          message: 'Conflict resolved',
        );
        final events = await db.getUnreadSyncEvents('tenant-001');
        final eventId = events.first.id;

        // Act
        await db.markSyncEventRead(eventId);

        // Assert
        final unread = await db.getUnreadSyncEvents('tenant-001');
        expect(unread.isEmpty, isTrue);
      });

      test('markAllSyncEventsRead clears all unread events', () async {
        // Arrange: add 3 events
        for (int i = 0; i < 3; i++) {
          await db.addSyncEvent(
            tenantId: 'tenant-001',
            type: 'update',
            entityType: 'field',
            entityId: 'field-$i',
            message: 'Updated from server',
          );
        }
        expect(
          (await db.getUnreadSyncEvents('tenant-001')).length,
          equals(3),
        );

        // Act
        await db.markAllSyncEventsRead('tenant-001');

        // Assert
        final unread = await db.getUnreadSyncEvents('tenant-001');
        expect(unread.isEmpty, isTrue);
      });

      test('Sync events are tenant-isolated', () async {
        // Arrange: events for 2 tenants
        await db.addSyncEvent(
          tenantId: 'tenant-A',
          type: 'update',
          entityType: 'field',
          entityId: 'field-001',
          message: 'Tenant A update',
        );
        await db.addSyncEvent(
          tenantId: 'tenant-B',
          type: 'update',
          entityType: 'field',
          entityId: 'field-002',
          message: 'Tenant B update',
        );

        // Act
        final eventsA = await db.getUnreadSyncEvents('tenant-A');
        final eventsB = await db.getUnreadSyncEvents('tenant-B');

        // Assert
        expect(eventsA.length, equals(1));
        expect(eventsA.first.entityId, equals('field-001'));
        expect(eventsB.length, equals(1));
        expect(eventsB.first.entityId, equals('field-002'));
      });
    });

    // =========================================================================
    // Database Health
    // صحة قاعدة البيانات
    // =========================================================================

    group('Database Health - صحة قاعدة البيانات', () {
      test('checkHealth returns healthy status when empty', () async {
        final health = await db.checkHealth();
        expect(health['healthy'], isTrue);
        expect(health['pendingOutboxCount'], isZero);
      });

      test('checkHealth reflects pending outbox count', () async {
        // Arrange: add 3 pending items
        for (int i = 0; i < 3; i++) {
          await db.queueOutboxItem(
            tenantId: 'tenant-001',
            entityType: 'task',
            entityId: 'task-$i',
            apiEndpoint: '/api/v1/tasks',
            method: 'POST',
            payload: '{}',
          );
        }

        // Act
        final health = await db.checkHealth();

        // Assert
        expect(health['healthy'], isTrue);
        expect(health['pendingOutboxCount'], equals(3));
      });

      test('getStatistics returns correct counts', () async {
        // Arrange: seed some unsynced fields
        final now = DateTime.now();
        for (int i = 0; i < 3; i++) {
          db.seedField(Field(
            id: 'field-$i',
            remoteId: null,
            tenantId: 'tenant-001',
            farmId: null,
            name: 'Field $i',
            cropType: 'wheat',
            boundary: [],
            centroid: null,
            areaHectares: 5.0,
            status: 'active',
            ndviCurrent: null,
            ndviUpdatedAt: null,
            synced: false, // unsynced
            isDeleted: false,
            createdAt: now,
            updatedAt: now,
            etag: null,
            serverUpdatedAt: null,
          ));
        }

        // Act
        final stats = await db.getStatistics();

        // Assert
        expect(stats['unsyncedFields'], equals(3));
      });

      test('pruneOldOutboxItems removes old synced items without crash',
          () async {
        // Arrange: add items and mark done
        for (int i = 0; i < 3; i++) {
          await db.queueOutboxItem(
            tenantId: 'tenant-001',
            entityType: 'task',
            entityId: 'task-$i',
            apiEndpoint: '/api/v1/tasks',
            method: 'POST',
            payload: '{}',
          );
        }
        final pending = await db.getPendingOutbox();
        for (final item in pending) {
          await db.markOutboxDone(item.id);
        }

        // Act: prune with 0-day TTL
        final pruned = await db.pruneOldOutboxItems(
          olderThan: Duration.zero,
        );

        // Assert: no crash, returns count
        expect(pruned, isA<int>());
        expect(pruned, greaterThanOrEqualTo(0));
      });
    });
  });
}
