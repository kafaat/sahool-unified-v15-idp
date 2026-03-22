/// Sync Queue DAO Tests - Outbox and Sync Operations
/// اختبارات قائمة المزامنة - صندوق الصادر وعمليات المزامنة
///
/// Tests for:
/// - Outbox queue management for offline-first sync
/// - Sync log tracking
/// - Sync events and conflict notifications
/// - ETag-based conflict resolution
/// - Queue priority and ordering
/// - Cleanup operations
library;
import 'dart:convert';

import 'package:drift/drift.dart' hide isNull, isNotNull;
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';

part 'sync_queue_dao_test.g.dart';

/// Outbox Table - offline sync queue with ETag support
@TableIndex(name: 'sync_outbox_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'sync_outbox_synced_idx', columns: {#isSynced})
@TableIndex(name: 'sync_outbox_entity_idx', columns: {#entityType, #entityId})
@TableIndex(name: 'sync_outbox_created_idx', columns: {#createdAt})
@TableIndex(name: 'sync_outbox_priority_idx', columns: {#priority})
class SyncOutbox extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get tenantId => text()();
  TextColumn get entityType => text()(); // 'field', 'task', 'observation', etc.
  TextColumn get entityId => text()();
  TextColumn get apiEndpoint => text()();
  TextColumn get method => text().withDefault(const Constant('POST'))(); // POST/PUT/PATCH/DELETE
  TextColumn get payload => text()(); // JSON payload
  TextColumn get ifMatch => text().nullable()(); // ETag for optimistic locking
  IntColumn get retryCount => integer().withDefault(const Constant(0))();
  IntColumn get maxRetries => integer().withDefault(const Constant(5))();
  IntColumn get priority => integer().withDefault(const Constant(0))(); // Higher = more urgent
  BoolColumn get isSynced => boolean().withDefault(const Constant(false))();
  TextColumn get errorMessage => text().nullable()();
  DateTimeColumn get lastAttempt => dateTime().nullable()();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

/// Sync Logs Table - history of sync operations
@TableIndex(name: 'sync_logs_type_idx', columns: {#type})
@TableIndex(name: 'sync_logs_status_idx', columns: {#status})
@TableIndex(name: 'sync_logs_timestamp_idx', columns: {#timestamp})
class SyncLogs extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get type => text()(); // 'full_sync', 'delta_sync', 'push', 'pull'
  TextColumn get status => text()(); // 'started', 'success', 'failed', 'partial'
  TextColumn get message => text().nullable()();
  IntColumn get itemsSynced => integer().nullable()();
  IntColumn get itemsFailed => integer().nullable()();
  IntColumn get durationMs => integer().nullable()();
  TextColumn get details => text().nullable()(); // JSON for extra details
  DateTimeColumn get timestamp => dateTime()();
}

/// Sync Events Table - conflict notifications and sync events
@TableIndex(name: 'sync_events_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'sync_events_read_idx', columns: {#isRead})
@TableIndex(name: 'sync_events_type_idx', columns: {#type})
@TableIndex(name: 'sync_events_created_idx', columns: {#createdAt})
class SyncEvents extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get tenantId => text()();
  TextColumn get type => text()(); // 'CONFLICT', 'INFO', 'ERROR', 'WARNING'
  TextColumn get entityType => text().nullable()();
  TextColumn get entityId => text().nullable()();
  TextColumn get message => text()();
  TextColumn get messageAr => text().nullable()();
  TextColumn get details => text().nullable()(); // JSON for conflict details
  TextColumn get resolution => text().nullable()(); // 'local_wins', 'server_wins', 'merged', 'manual'
  BoolColumn get isRead => boolean().withDefault(const Constant(false))();
  BoolColumn get isResolved => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

/// Sync DAO Test Database
@DriftDatabase(tables: [SyncOutbox, SyncLogs, SyncEvents])
class SyncDaoTestDatabase extends _$SyncDaoTestDatabase {
  SyncDaoTestDatabase() : super(NativeDatabase.memory());

  @override
  int get schemaVersion => 1;

  // ============================================================
  // Outbox Operations
  // ============================================================

  /// Add item to outbox queue
  Future<int> addToOutbox(SyncOutboxCompanion item) {
    return into(syncOutbox).insert(item);
  }

  /// Queue entity operation with ETag support
  Future<int> queueOperation({
    required String tenantId,
    required String entityType,
    required String entityId,
    required String apiEndpoint,
    required String method,
    required String payload,
    String? ifMatch,
    int priority = 0,
  }) {
    return into(syncOutbox).insert(SyncOutboxCompanion.insert(
      tenantId: tenantId,
      entityType: entityType,
      entityId: entityId,
      apiEndpoint: apiEndpoint,
      method: Value(method),
      payload: payload,
      ifMatch: Value(ifMatch),
      priority: Value(priority),
    ));
  }

  /// Get pending outbox items (not synced, under max retries)
  Future<List<SyncOutboxData>> getPendingItems({
    String? tenantId,
    int limit = 50,
  }) {
    final query = select(syncOutbox)
      ..where((o) => o.isSynced.equals(false))
      ..where((o) => o.retryCount.isSmallerThanValue(5))
      ..orderBy([
        (o) => OrderingTerm.desc(o.priority),
        (o) => OrderingTerm.asc(o.createdAt),
      ])
      ..limit(limit);

    if (tenantId != null) {
      query.where((o) => o.tenantId.equals(tenantId));
    }

    return query.get();
  }

  /// Get outbox item by ID
  Future<SyncOutboxData?> getOutboxItemById(int id) {
    return (select(syncOutbox)..where((o) => o.id.equals(id))).getSingleOrNull();
  }

  /// Get outbox items for entity
  Future<List<SyncOutboxData>> getOutboxItemsForEntity(
    String entityType,
    String entityId,
  ) {
    return (select(syncOutbox)
          ..where((o) => o.entityType.equals(entityType))
          ..where((o) => o.entityId.equals(entityId))
          ..orderBy([(o) => OrderingTerm.desc(o.createdAt)]))
        .get();
  }

  /// Mark outbox item as synced
  Future<void> markSynced(int id) async {
    await (update(syncOutbox)..where((o) => o.id.equals(id))).write(
      const SyncOutboxCompanion(isSynced: Value(true)),
    );
  }

  /// Increment retry count and record error
  Future<void> recordRetryFailure(int id, String? errorMessage) async {
    await customStatement(
      'UPDATE sync_outbox SET retry_count = retry_count + 1, error_message = ?, last_attempt = ? WHERE id = ?',
      [errorMessage, DateTime.now().toIso8601String(), id],
    );
  }

  /// Delete synced items (cleanup)
  Future<int> cleanupSynced() async {
    return (delete(syncOutbox)..where((o) => o.isSynced.equals(true))).go();
  }

  /// Delete old synced items
  Future<int> cleanupOldSynced({Duration olderThan = const Duration(days: 7)}) async {
    final cutoff = DateTime.now().subtract(olderThan);
    return (delete(syncOutbox)
          ..where((o) => o.isSynced.equals(true))
          ..where((o) => o.createdAt.isSmallerThanValue(cutoff)))
        .go();
  }

  /// Delete failed items exceeding max retries
  Future<int> cleanupFailed() async {
    return (delete(syncOutbox)
          ..where((o) => o.retryCount.isBiggerOrEqualValue(5))
          ..where((o) => o.isSynced.equals(false)))
        .go();
  }

  /// Get outbox count by status
  Future<Map<String, int>> getOutboxStats() async {
    final pending = await (syncOutbox.count(
      where: (o) => o.isSynced.equals(false) & o.retryCount.isSmallerThanValue(5),
    )).getSingle();

    final synced = await (syncOutbox.count(
      where: (o) => o.isSynced.equals(true),
    )).getSingle();

    final failed = await (syncOutbox.count(
      where: (o) => o.isSynced.equals(false) & o.retryCount.isBiggerOrEqualValue(5),
    )).getSingle();

    return {
      'pending': pending,
      'synced': synced,
      'failed': failed,
    };
  }

  /// Watch pending outbox count
  Stream<int> watchPendingCount(String tenantId) {
    final query = selectOnly(syncOutbox)
      ..where(syncOutbox.tenantId.equals(tenantId))
      ..where(syncOutbox.isSynced.equals(false))
      ..where(syncOutbox.retryCount.isSmallerThanValue(5))
      ..addColumns([syncOutbox.id.count()]);
    return query.map((row) => row.read(syncOutbox.id.count()) ?? 0).watchSingle();
  }

  // ============================================================
  // Sync Log Operations
  // ============================================================

  /// Log sync operation
  Future<int> logSync({
    required String type,
    required String status,
    String? message,
    int? itemsSynced,
    int? itemsFailed,
    int? durationMs,
    Map<String, dynamic>? details,
  }) {
    return into(syncLogs).insert(SyncLogsCompanion.insert(
      type: type,
      status: status,
      message: Value(message),
      itemsSynced: Value(itemsSynced),
      itemsFailed: Value(itemsFailed),
      durationMs: Value(durationMs),
      details: Value(details != null ? jsonEncode(details) : null),
      timestamp: DateTime.now(),
    ));
  }

  /// Get recent sync logs
  Future<List<SyncLog>> getRecentLogs({int limit = 20}) {
    return (select(syncLogs)
          ..orderBy([(l) => OrderingTerm.desc(l.timestamp)])
          ..limit(limit))
        .get();
  }

  /// Get sync logs by type
  Future<List<SyncLog>> getLogsByType(String type, {int limit = 10}) {
    return (select(syncLogs)
          ..where((l) => l.type.equals(type))
          ..orderBy([(l) => OrderingTerm.desc(l.timestamp)])
          ..limit(limit))
        .get();
  }

  /// Get last successful sync
  Future<SyncLog?> getLastSuccessfulSync(String type) {
    return (select(syncLogs)
          ..where((l) => l.type.equals(type))
          ..where((l) => l.status.equals('success'))
          ..orderBy([(l) => OrderingTerm.desc(l.timestamp)])
          ..limit(1))
        .getSingleOrNull();
  }

  /// Delete old sync logs
  Future<int> cleanupOldLogs({Duration olderThan = const Duration(days: 30)}) async {
    final cutoff = DateTime.now().subtract(olderThan);
    return (delete(syncLogs)..where((l) => l.timestamp.isSmallerThanValue(cutoff))).go();
  }

  // ============================================================
  // Sync Events Operations
  // ============================================================

  /// Add sync event
  Future<int> addSyncEvent({
    required String tenantId,
    required String type,
    required String message,
    String? messageAr,
    String? entityType,
    String? entityId,
    Map<String, dynamic>? details,
  }) {
    return into(syncEvents).insert(SyncEventsCompanion.insert(
      tenantId: tenantId,
      type: type,
      message: message,
      messageAr: Value(messageAr),
      entityType: Value(entityType),
      entityId: Value(entityId),
      details: Value(details != null ? jsonEncode(details) : null),
    ));
  }

  /// Get unread sync events
  Future<List<SyncEvent>> getUnreadEvents(String tenantId) {
    return (select(syncEvents)
          ..where((e) => e.tenantId.equals(tenantId))
          ..where((e) => e.isRead.equals(false))
          ..orderBy([(e) => OrderingTerm.desc(e.createdAt)]))
        .get();
  }

  /// Get unresolved conflicts
  Future<List<SyncEvent>> getUnresolvedConflicts(String tenantId) {
    return (select(syncEvents)
          ..where((e) => e.tenantId.equals(tenantId))
          ..where((e) => e.type.equals('CONFLICT'))
          ..where((e) => e.isResolved.equals(false))
          ..orderBy([(e) => OrderingTerm.desc(e.createdAt)]))
        .get();
  }

  /// Watch unread events count
  Stream<int> watchUnreadEventsCount(String tenantId) {
    final query = selectOnly(syncEvents)
      ..where(syncEvents.tenantId.equals(tenantId))
      ..where(syncEvents.isRead.equals(false))
      ..addColumns([syncEvents.id.count()]);
    return query.map((row) => row.read(syncEvents.id.count()) ?? 0).watchSingle();
  }

  /// Mark event as read
  Future<void> markEventRead(int eventId) async {
    await (update(syncEvents)..where((e) => e.id.equals(eventId))).write(
      const SyncEventsCompanion(isRead: Value(true)),
    );
  }

  /// Mark all events as read
  Future<void> markAllEventsRead(String tenantId) async {
    await (update(syncEvents)
          ..where((e) => e.tenantId.equals(tenantId))
          ..where((e) => e.isRead.equals(false)))
        .write(const SyncEventsCompanion(isRead: Value(true)));
  }

  /// Resolve conflict
  Future<void> resolveConflict(int eventId, String resolution) async {
    await (update(syncEvents)..where((e) => e.id.equals(eventId))).write(
      SyncEventsCompanion(
        isResolved: const Value(true),
        resolution: Value(resolution),
      ),
    );
  }
}

/// Test fixtures for Sync DAO
class SyncDaoFixtures {
  static SyncOutboxCompanion createOutboxItem({
    String tenantId = 'tenant-1',
    String entityType = 'field',
    String entityId = 'field-001',
    String apiEndpoint = '/api/v1/fields',
    String method = 'POST',
    Map<String, dynamic>? payload,
    String? ifMatch,
    int priority = 0,
  }) {
    return SyncOutboxCompanion.insert(
      tenantId: tenantId,
      entityType: entityType,
      entityId: entityId,
      apiEndpoint: apiEndpoint,
      method: Value(method),
      payload: jsonEncode(payload ?? {'name': 'Test Field', 'area': 10.0}),
      ifMatch: Value(ifMatch),
      priority: Value(priority),
    );
  }

  static SyncLogsCompanion createSyncLog({
    String type = 'full_sync',
    String status = 'success',
    String? message,
    int? itemsSynced,
    int? itemsFailed,
    int? durationMs,
  }) {
    return SyncLogsCompanion.insert(
      type: type,
      status: status,
      message: Value(message),
      itemsSynced: Value(itemsSynced),
      itemsFailed: Value(itemsFailed),
      durationMs: Value(durationMs),
      timestamp: DateTime.now(),
    );
  }

  static SyncEventsCompanion createSyncEvent({
    String tenantId = 'tenant-1',
    String type = 'INFO',
    String message = 'Sync completed',
    String? messageAr,
    String? entityType,
    String? entityId,
    Map<String, dynamic>? details,
  }) {
    return SyncEventsCompanion.insert(
      tenantId: tenantId,
      type: type,
      message: message,
      messageAr: Value(messageAr),
      entityType: Value(entityType),
      entityId: Value(entityId),
      details: Value(details != null ? jsonEncode(details) : null),
    );
  }
}

void main() {
  group('Outbox - Insert Operations', () {
    late SyncDaoTestDatabase db;

    setUp(() {
      db = SyncDaoTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should add item to outbox', () async {
      final item = SyncDaoFixtures.createOutboxItem();
      final id = await db.addToOutbox(item);

      expect(id, greaterThan(0));

      final retrieved = await db.getOutboxItemById(id);
      expect(retrieved, isNotNull);
      expect(retrieved!.entityType, equals('field'));
    });

    test('should queue operation with ETag', () async {
      final id = await db.queueOperation(
        tenantId: 'tenant-1',
        entityType: 'field',
        entityId: 'field-001',
        apiEndpoint: '/api/v1/fields/field-001',
        method: 'PUT',
        payload: jsonEncode({'name': 'Updated Field'}),
        ifMatch: '"etag-abc123"',
      );

      final item = await db.getOutboxItemById(id);
      expect(item!.ifMatch, equals('"etag-abc123"'));
      expect(item.method, equals('PUT'));
    });

    test('should set priority correctly', () async {
      await db.queueOperation(
        tenantId: 'tenant-1',
        entityType: 'task',
        entityId: 'task-001',
        apiEndpoint: '/api/v1/tasks',
        method: 'POST',
        payload: '{}',
        priority: 10, // High priority
      );

      await db.queueOperation(
        tenantId: 'tenant-1',
        entityType: 'field',
        entityId: 'field-001',
        apiEndpoint: '/api/v1/fields',
        method: 'POST',
        payload: '{}',
        priority: 0, // Normal priority
      );

      final pending = await db.getPendingItems();
      expect(pending.first.entityType, equals('task')); // High priority first
    });
  });

  group('Outbox - Read Operations', () {
    late SyncDaoTestDatabase db;

    setUp(() async {
      db = SyncDaoTestDatabase();

      // Insert test data
      for (int i = 0; i < 10; i++) {
        await db.addToOutbox(SyncDaoFixtures.createOutboxItem(
          tenantId: i < 5 ? 'tenant-1' : 'tenant-2',
          entityId: 'field-$i',
          priority: i % 3,
        ));
      }

      // Add a synced item
      final syncedItem = SyncDaoFixtures.createOutboxItem(entityId: 'synced-1');
      final syncedId = await db.addToOutbox(syncedItem);
      await db.markSynced(syncedId);
    });

    tearDown(() async {
      await db.close();
    });

    test('should get pending items', () async {
      final pending = await db.getPendingItems();

      expect(pending.length, equals(10));
      expect(pending.every((p) => !p.isSynced), isTrue);
    });

    test('should filter pending items by tenant', () async {
      final pending = await db.getPendingItems(tenantId: 'tenant-1');

      expect(pending.length, equals(5));
      expect(pending.every((p) => p.tenantId == 'tenant-1'), isTrue);
    });

    test('should limit pending items', () async {
      final pending = await db.getPendingItems(limit: 3);

      expect(pending.length, equals(3));
    });

    test('should order by priority and creation date', () async {
      final pending = await db.getPendingItems();

      // Higher priority items should come first
      for (int i = 0; i < pending.length - 1; i++) {
        final current = pending[i];
        final next = pending[i + 1];
        expect(
          current.priority >= next.priority ||
              (current.priority == next.priority &&
                  (current.createdAt.isBefore(next.createdAt) ||
                      current.createdAt.isAtSameMomentAs(next.createdAt))),
          isTrue,
        );
      }
    });

    test('should get items for specific entity', () async {
      final items = await db.getOutboxItemsForEntity('field', 'field-0');

      expect(items.length, equals(1));
      expect(items.first.entityId, equals('field-0'));
    });

    test('should get outbox stats', () async {
      final stats = await db.getOutboxStats();

      expect(stats['pending'], equals(10));
      expect(stats['synced'], equals(1));
      expect(stats['failed'], equals(0));
    });
  });

  group('Outbox - Update Operations', () {
    late SyncDaoTestDatabase db;
    late int testItemId;

    setUp(() async {
      db = SyncDaoTestDatabase();

      testItemId = await db.addToOutbox(SyncDaoFixtures.createOutboxItem());
    });

    tearDown(() async {
      await db.close();
    });

    test('should mark item as synced', () async {
      await db.markSynced(testItemId);

      final item = await db.getOutboxItemById(testItemId);
      expect(item!.isSynced, isTrue);
    });

    test('should record retry failure', () async {
      await db.recordRetryFailure(testItemId, 'Network error');

      final item = await db.getOutboxItemById(testItemId);
      expect(item!.retryCount, equals(1));
      expect(item.errorMessage, equals('Network error'));
      expect(item.lastAttempt, isNotNull);
    });

    test('should increment retry count on multiple failures', () async {
      await db.recordRetryFailure(testItemId, 'Error 1');
      await db.recordRetryFailure(testItemId, 'Error 2');
      await db.recordRetryFailure(testItemId, 'Error 3');

      final item = await db.getOutboxItemById(testItemId);
      expect(item!.retryCount, equals(3));
      expect(item.errorMessage, equals('Error 3'));
    });

    test('should exclude items exceeding max retries from pending', () async {
      // Fail item 5 times
      for (int i = 0; i < 5; i++) {
        await db.recordRetryFailure(testItemId, 'Error $i');
      }

      final pending = await db.getPendingItems();
      expect(pending.any((p) => p.id == testItemId), isFalse);
    });
  });

  group('Outbox - Cleanup Operations', () {
    late SyncDaoTestDatabase db;

    setUp(() async {
      db = SyncDaoTestDatabase();

      // Add pending items
      for (int i = 0; i < 5; i++) {
        await db.addToOutbox(SyncDaoFixtures.createOutboxItem(entityId: 'pending-$i'));
      }

      // Add synced items
      for (int i = 0; i < 3; i++) {
        final id = await db.addToOutbox(SyncDaoFixtures.createOutboxItem(entityId: 'synced-$i'));
        await db.markSynced(id);
      }

      // Add failed items (exceed max retries)
      for (int i = 0; i < 2; i++) {
        final id = await db.addToOutbox(SyncDaoFixtures.createOutboxItem(entityId: 'failed-$i'));
        for (int j = 0; j < 5; j++) {
          await db.recordRetryFailure(id, 'Error');
        }
      }
    });

    tearDown(() async {
      await db.close();
    });

    test('should cleanup synced items', () async {
      final deleted = await db.cleanupSynced();
      expect(deleted, equals(3));

      final stats = await db.getOutboxStats();
      expect(stats['synced'], equals(0));
    });

    test('should cleanup failed items', () async {
      final deleted = await db.cleanupFailed();
      expect(deleted, equals(2));

      final stats = await db.getOutboxStats();
      expect(stats['failed'], equals(0));
    });

    test('should only cleanup old synced items', () async {
      // All items are new, so cleanup with 7 day threshold should delete none
      final deleted = await db.cleanupOldSynced(olderThan: const Duration(days: 7));
      // Since items were just created, none should be deleted
      expect(deleted, equals(0));
    });
  });

  group('Outbox - Watch Streams', () {
    late SyncDaoTestDatabase db;

    setUp(() {
      db = SyncDaoTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should watch pending count', () async {
      final stream = db.watchPendingCount('tenant-1');

      // Initial count
      expect(await stream.first, equals(0));

      // Add items
      await db.addToOutbox(SyncDaoFixtures.createOutboxItem());
      await Future<void>.delayed(const Duration(milliseconds: 50));

      expect(await stream.first, equals(1));
    });
  });

  group('Sync Logs - Insert Operations', () {
    late SyncDaoTestDatabase db;

    setUp(() {
      db = SyncDaoTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should log sync operation', () async {
      final id = await db.logSync(
        type: 'full_sync',
        status: 'success',
        message: 'Full sync completed',
        itemsSynced: 25,
        itemsFailed: 2,
        durationMs: 1500,
      );

      expect(id, greaterThan(0));
    });

    test('should log sync with details', () async {
      await db.logSync(
        type: 'delta_sync',
        status: 'partial',
        details: {
          'synced_entities': ['field-1', 'field-2'],
          'failed_entities': ['task-1'],
          'errors': [{'entity': 'task-1', 'error': 'Conflict'}],
        },
      );

      final logs = await db.getRecentLogs(limit: 1);
      expect(logs.first.details, isNotNull);

      final details = jsonDecode(logs.first.details!);
      expect(details['synced_entities'], hasLength(2));
    });
  });

  group('Sync Logs - Read Operations', () {
    late SyncDaoTestDatabase db;

    setUp(() async {
      db = SyncDaoTestDatabase();

      // Insert various logs
      await db.logSync(type: 'full_sync', status: 'success', itemsSynced: 100);
      await db.logSync(type: 'full_sync', status: 'failed', message: 'Network error');
      await db.logSync(type: 'delta_sync', status: 'success', itemsSynced: 5);
      await db.logSync(type: 'push', status: 'success', itemsSynced: 3);
      await db.logSync(type: 'pull', status: 'success', itemsSynced: 10);
    });

    tearDown(() async {
      await db.close();
    });

    test('should get recent logs', () async {
      final logs = await db.getRecentLogs();

      expect(logs.length, equals(5));
      // Should be ordered by timestamp desc
      for (int i = 0; i < logs.length - 1; i++) {
        expect(
          logs[i].timestamp.isAfter(logs[i + 1].timestamp) ||
              logs[i].timestamp.isAtSameMomentAs(logs[i + 1].timestamp),
          isTrue,
        );
      }
    });

    test('should get logs by type', () async {
      final fullSyncLogs = await db.getLogsByType('full_sync');

      expect(fullSyncLogs.length, equals(2));
      expect(fullSyncLogs.every((l) => l.type == 'full_sync'), isTrue);
    });

    test('should get last successful sync', () async {
      final lastSuccess = await db.getLastSuccessfulSync('full_sync');

      expect(lastSuccess, isNotNull);
      expect(lastSuccess!.status, equals('success'));
      expect(lastSuccess.itemsSynced, equals(100));
    });

    test('should return null if no successful sync', () async {
      final lastSuccess = await db.getLastSuccessfulSync('non_existent_type');
      expect(lastSuccess, isNull);
    });
  });

  group('Sync Events - Insert Operations', () {
    late SyncDaoTestDatabase db;

    setUp(() {
      db = SyncDaoTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should add sync event', () async {
      final id = await db.addSyncEvent(
        tenantId: 'tenant-1',
        type: 'INFO',
        message: 'Sync completed successfully',
        messageAr: 'اكتملت المزامنة بنجاح',
      );

      expect(id, greaterThan(0));
    });

    test('should add conflict event', () async {
      await db.addSyncEvent(
        tenantId: 'tenant-1',
        type: 'CONFLICT',
        message: 'Conflict detected on field-001',
        messageAr: 'تم اكتشاف تعارض في الحقل-001',
        entityType: 'field',
        entityId: 'field-001',
        details: {
          'local_version': {'name': 'Local Name', 'updated_at': '2025-01-15T10:00:00Z'},
          'server_version': {'name': 'Server Name', 'updated_at': '2025-01-15T11:00:00Z'},
        },
      );

      final conflicts = await db.getUnresolvedConflicts('tenant-1');
      expect(conflicts.length, equals(1));
      expect(conflicts.first.entityType, equals('field'));
    });
  });

  group('Sync Events - Read Operations', () {
    late SyncDaoTestDatabase db;

    setUp(() async {
      db = SyncDaoTestDatabase();

      // Insert various events
      await db.addSyncEvent(
        tenantId: 'tenant-1',
        type: 'INFO',
        message: 'Sync started',
      );
      await db.addSyncEvent(
        tenantId: 'tenant-1',
        type: 'CONFLICT',
        message: 'Conflict on field-1',
        entityType: 'field',
        entityId: 'field-1',
      );
      await db.addSyncEvent(
        tenantId: 'tenant-1',
        type: 'ERROR',
        message: 'Network error',
      );
      await db.addSyncEvent(
        tenantId: 'tenant-2',
        type: 'INFO',
        message: 'Other tenant event',
      );
    });

    tearDown(() async {
      await db.close();
    });

    test('should get unread events for tenant', () async {
      final unread = await db.getUnreadEvents('tenant-1');

      expect(unread.length, equals(3));
      expect(unread.every((e) => e.tenantId == 'tenant-1'), isTrue);
    });

    test('should get unresolved conflicts', () async {
      final conflicts = await db.getUnresolvedConflicts('tenant-1');

      expect(conflicts.length, equals(1));
      expect(conflicts.first.type, equals('CONFLICT'));
      expect(conflicts.first.entityId, equals('field-1'));
    });

    test('should isolate events by tenant', () async {
      final tenant1Events = await db.getUnreadEvents('tenant-1');
      final tenant2Events = await db.getUnreadEvents('tenant-2');

      expect(tenant1Events.length, equals(3));
      expect(tenant2Events.length, equals(1));
    });
  });

  group('Sync Events - Update Operations', () {
    late SyncDaoTestDatabase db;
    late int conflictEventId;

    setUp(() async {
      db = SyncDaoTestDatabase();

      await db.addSyncEvent(
        tenantId: 'tenant-1',
        type: 'INFO',
        message: 'Info event',
      );

      conflictEventId = await db.addSyncEvent(
        tenantId: 'tenant-1',
        type: 'CONFLICT',
        message: 'Conflict event',
        entityType: 'field',
        entityId: 'field-1',
      );
    });

    tearDown(() async {
      await db.close();
    });

    test('should mark event as read', () async {
      final unreadBefore = await db.getUnreadEvents('tenant-1');
      expect(unreadBefore.length, equals(2));

      await db.markEventRead(conflictEventId);

      final unreadAfter = await db.getUnreadEvents('tenant-1');
      expect(unreadAfter.length, equals(1));
    });

    test('should mark all events as read', () async {
      await db.markAllEventsRead('tenant-1');

      final unread = await db.getUnreadEvents('tenant-1');
      expect(unread, isEmpty);
    });

    test('should resolve conflict', () async {
      await db.resolveConflict(conflictEventId, 'server_wins');

      final conflicts = await db.getUnresolvedConflicts('tenant-1');
      expect(conflicts, isEmpty);
    });
  });

  group('Sync Events - Watch Streams', () {
    late SyncDaoTestDatabase db;

    setUp(() {
      db = SyncDaoTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should watch unread events count', () async {
      final stream = db.watchUnreadEventsCount('tenant-1');

      expect(await stream.first, equals(0));

      await db.addSyncEvent(
        tenantId: 'tenant-1',
        type: 'INFO',
        message: 'New event',
      );

      await Future<void>.delayed(const Duration(milliseconds: 50));
      expect(await stream.first, equals(1));
    });
  });

  group('ETag Conflict Resolution', () {
    late SyncDaoTestDatabase db;

    setUp(() {
      db = SyncDaoTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should store ETag for PUT operations', () async {
      final id = await db.queueOperation(
        tenantId: 'tenant-1',
        entityType: 'field',
        entityId: 'field-001',
        apiEndpoint: '/api/v1/fields/field-001',
        method: 'PUT',
        payload: jsonEncode({'name': 'Updated'}),
        ifMatch: '"etag-v1"',
      );

      final item = await db.getOutboxItemById(id);
      expect(item!.ifMatch, equals('"etag-v1"'));
    });

    test('should handle 412 Precondition Failed scenario', () async {
      // Queue initial update
      final id = await db.queueOperation(
        tenantId: 'tenant-1',
        entityType: 'field',
        entityId: 'field-001',
        apiEndpoint: '/api/v1/fields/field-001',
        method: 'PUT',
        payload: jsonEncode({'name': 'Local Update'}),
        ifMatch: '"etag-v1"',
      );

      // Simulate 412 Precondition Failed (ETag mismatch)
      await db.recordRetryFailure(id, '412 Precondition Failed: ETag mismatch');

      // Log conflict event
      await db.addSyncEvent(
        tenantId: 'tenant-1',
        type: 'CONFLICT',
        message: 'Update conflict on field-001: Server has newer version',
        messageAr: 'تعارض في التحديث: الخادم يحتوي على نسخة أحدث',
        entityType: 'field',
        entityId: 'field-001',
        details: {
          'local_etag': '"etag-v1"',
          'conflict_type': 'etag_mismatch',
        },
      );

      final conflicts = await db.getUnresolvedConflicts('tenant-1');
      expect(conflicts.length, equals(1));
      expect(conflicts.first.details, contains('etag_mismatch'));
    });
  });

  group('Multi-Entity Sync Queue', () {
    late SyncDaoTestDatabase db;

    setUp(() async {
      db = SyncDaoTestDatabase();

      // Queue operations for multiple entity types
      await db.queueOperation(
        tenantId: 'tenant-1',
        entityType: 'field',
        entityId: 'field-001',
        apiEndpoint: '/api/v1/fields',
        method: 'POST',
        payload: jsonEncode({'name': 'New Field'}),
        priority: 5,
      );

      await db.queueOperation(
        tenantId: 'tenant-1',
        entityType: 'task',
        entityId: 'task-001',
        apiEndpoint: '/api/v1/tasks',
        method: 'POST',
        payload: jsonEncode({'title': 'New Task'}),
        priority: 10, // Higher priority
      );

      await db.queueOperation(
        tenantId: 'tenant-1',
        entityType: 'observation',
        entityId: 'obs-001',
        apiEndpoint: '/api/v1/observations',
        method: 'POST',
        payload: jsonEncode({'notes': 'Field observation'}),
        priority: 0,
      );
    });

    tearDown(() async {
      await db.close();
    });

    test('should process entities by priority', () async {
      final pending = await db.getPendingItems();

      expect(pending[0].entityType, equals('task')); // priority 10
      expect(pending[1].entityType, equals('field')); // priority 5
      expect(pending[2].entityType, equals('observation')); // priority 0
    });

    test('should track items for specific entity', () async {
      // Add more operations for same field
      await db.queueOperation(
        tenantId: 'tenant-1',
        entityType: 'field',
        entityId: 'field-001',
        apiEndpoint: '/api/v1/fields/field-001',
        method: 'PUT',
        payload: jsonEncode({'name': 'Updated Name'}),
      );

      final fieldOps = await db.getOutboxItemsForEntity('field', 'field-001');
      expect(fieldOps.length, equals(2));
    });
  });
}
