/// Database Initialization and Core Operations Tests
/// اختبارات تهيئة قاعدة البيانات والعمليات الاساسية
///
/// Tests for:
/// - Database initialization
/// - Schema creation
/// - Migration handling
/// - Transaction support
/// - Error handling
///
/// Uses in-memory database for testing
import 'package:drift/drift.dart' hide isNull, isNotNull;
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';

// Note: We create a test-specific in-memory database since the actual
// AppDatabase uses SQLCipher encryption which requires native libraries
part 'database_test.g.dart';

/// Test Tasks Table - mirrors production structure with all indexes
/// جدول المهام التجريبي - يعكس بنية الإنتاج مع جميع الفهارس
@TableIndex(name: 'test_tasks_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'test_tasks_field_idx', columns: {#fieldId})
@TableIndex(name: 'test_tasks_status_idx', columns: {#status})
@TableIndex(name: 'test_tasks_synced_idx', columns: {#synced})
@TableIndex(name: 'test_tasks_tenant_status_idx', columns: {#tenantId, #status})
@TableIndex(name: 'test_tasks_created_idx', columns: {#createdAt})
class TestTasks extends Table {
  TextColumn get id => text()();
  TextColumn get tenantId => text()();
  TextColumn get fieldId => text()();
  TextColumn get farmId => text().nullable()();
  TextColumn get title => text()();
  TextColumn get description => text().nullable()();
  TextColumn get status => text().withDefault(const Constant('open'))();
  TextColumn get priority => text().withDefault(const Constant('medium'))();
  DateTimeColumn get dueDate => dateTime().nullable()();
  TextColumn get assignedTo => text().nullable()();
  TextColumn get evidenceNotes => text().nullable()();
  TextColumn get evidencePhotos => text().nullable()(); // JSON array of file paths
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();

  @override
  Set<Column> get primaryKey => {id};
}

/// Test Outbox Table - for offline sync queue with ETag support
/// جدول صندوق الصادر التجريبي - لقائمة المزامنة غير المتصلة مع دعم ETag
@TableIndex(name: 'test_outbox_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'test_outbox_synced_idx', columns: {#isSynced})
@TableIndex(name: 'test_outbox_entity_idx', columns: {#entityType, #entityId})
@TableIndex(name: 'test_outbox_created_idx', columns: {#createdAt})
@TableIndex(name: 'test_outbox_tenant_synced_idx', columns: {#tenantId, #isSynced})
class TestOutbox extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get tenantId => text()();
  TextColumn get entityType => text()();
  TextColumn get entityId => text()();
  TextColumn get apiEndpoint => text()();
  TextColumn get method => text().withDefault(const Constant('POST'))();
  TextColumn get payload => text()();
  TextColumn get ifMatch => text().nullable()();
  IntColumn get retryCount => integer().withDefault(const Constant(0))();
  BoolColumn get isSynced => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

/// Test Fields Table with GIS support and all production indexes
/// جدول الحقول التجريبي مع دعم نظم المعلومات الجغرافية وجميع فهارس الإنتاج
@TableIndex(name: 'test_fields_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'test_fields_farm_idx', columns: {#farmId})
@TableIndex(name: 'test_fields_synced_idx', columns: {#synced})
@TableIndex(name: 'test_fields_deleted_idx', columns: {#isDeleted})
@TableIndex(name: 'test_fields_tenant_deleted_idx', columns: {#tenantId, #isDeleted})
@TableIndex(name: 'test_fields_updated_idx', columns: {#updatedAt})
@TableIndex(name: 'test_fields_remote_idx', columns: {#remoteId})
class TestFields extends Table {
  TextColumn get id => text()();
  TextColumn get remoteId => text().nullable()();
  TextColumn get tenantId => text()();
  TextColumn get farmId => text().nullable()();
  TextColumn get name => text().withLength(min: 1, max: 100)();
  TextColumn get cropType => text().nullable()();
  TextColumn get boundary => text()(); // GeoJSON stored as text
  TextColumn get centroid => text().nullable()();
  RealColumn get areaHectares => real()();
  TextColumn get status => text().nullable()();
  RealColumn get ndviCurrent => real().nullable()();
  DateTimeColumn get ndviUpdatedAt => dateTime().nullable()();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
  BoolColumn get isDeleted => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  TextColumn get etag => text().nullable()();
  DateTimeColumn get serverUpdatedAt => dateTime().nullable()();

  @override
  Set<Column> get primaryKey => {id};
}

/// Test SyncLogs Table with performance indexes
/// جدول سجلات المزامنة التجريبي مع فهارس الأداء
@TableIndex(name: 'test_sync_logs_status_idx', columns: {#status})
@TableIndex(name: 'test_sync_logs_timestamp_idx', columns: {#timestamp})
@TableIndex(name: 'test_sync_logs_type_status_idx', columns: {#type, #status})
class TestSyncLogs extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get type => text()();
  TextColumn get status => text()();
  TextColumn get message => text().nullable()();
  DateTimeColumn get timestamp => dateTime()();
}

/// Test SyncEvents Table - أحداث المزامنة والتعارضات
@TableIndex(name: 'test_sync_events_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'test_sync_events_read_idx', columns: {#isRead})
@TableIndex(name: 'test_sync_events_tenant_read_idx', columns: {#tenantId, #isRead})
@TableIndex(name: 'test_sync_events_created_idx', columns: {#createdAt})
class TestSyncEvents extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get tenantId => text()();
  TextColumn get type => text()();
  TextColumn get entityType => text().nullable()();
  TextColumn get entityId => text().nullable()();
  TextColumn get message => text()();
  BoolColumn get isRead => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

/// Test CachedUsers Table - mirrors production CachedUsers
/// جدول المستخدمين المخزنين مؤقتاً للاختبار
@TableIndex(name: 'test_cached_users_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'test_cached_users_email_idx', columns: {#email})
class TestCachedUsers extends Table {
  TextColumn get id => text()();
  TextColumn get email => text()();
  TextColumn get firstName => text().nullable()();
  TextColumn get lastName => text().nullable()();
  TextColumn get firstNameAr => text().nullable()();
  TextColumn get lastNameAr => text().nullable()();
  TextColumn get phone => text().nullable()();
  TextColumn get role => text().withDefault(const Constant('FARMER'))();
  TextColumn get status => text().withDefault(const Constant('ACTIVE'))();
  BoolColumn get emailVerified => boolean().withDefault(const Constant(false))();
  BoolColumn get phoneVerified => boolean().withDefault(const Constant(false))();
  TextColumn get tenantId => text().nullable()();
  TextColumn get avatarUrl => text().nullable()();
  IntColumn get failedLoginAttempts => integer().withDefault(const Constant(0))();
  DateTimeColumn get lockoutUntil => dateTime().nullable()();
  DateTimeColumn get lastLoginAt => dateTime().nullable()();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();

  @override
  Set<Column> get primaryKey => {id};
}

/// Test CachedUserProfiles Table - mirrors production CachedUserProfiles
/// جدول الملفات الشخصية المخزنة مؤقتاً للاختبار
class TestCachedUserProfiles extends Table {
  TextColumn get userId => text()();
  TextColumn get nationalId => text().nullable()();
  DateTimeColumn get dateOfBirth => dateTime().nullable()();
  TextColumn get address => text().nullable()();
  TextColumn get city => text().nullable()();
  TextColumn get region => text().nullable()();
  TextColumn get country => text().withDefault(const Constant('SA')).nullable()();
  DateTimeColumn get updatedAt => dateTime()();

  @override
  Set<Column> get primaryKey => {userId};
}

/// Test Database - In-memory version for unit testing
@DriftDatabase(tables: [
  TestTasks,
  TestOutbox,
  TestFields,
  TestSyncLogs,
  TestSyncEvents,
  TestCachedUsers,
  TestCachedUserProfiles,
])
class TestDatabase extends _$TestDatabase {
  TestDatabase() : super(_openInMemoryConnection());

  /// Constructor for custom executor (useful for testing migration)
  TestDatabase.withExecutor(super.e);

  @override
  int get schemaVersion => 6;

  @override
  MigrationStrategy get migration => MigrationStrategy(
        onCreate: (Migrator m) async {
          await m.createAll();
        },
        onUpgrade: (Migrator m, int from, int to) async {
          if (from < 2) {
            await m.deleteTable('test_fields');
            await m.createTable(testFields);
          }
          if (from < 3) {
            await m.addColumn(testFields, testFields.etag);
            await m.addColumn(testFields, testFields.serverUpdatedAt);
            await m.createTable(testSyncEvents);
          }
          if (from < 4) {
            await m.deleteTable('test_outbox');
            await m.createTable(testOutbox);
          }
          if (from < 6) {
            await m.createTable(testCachedUsers);
            await m.createTable(testCachedUserProfiles);
          }
        },
      );
}

/// Opens an in-memory database connection
LazyDatabase _openInMemoryConnection() {
  return LazyDatabase(() async {
    return NativeDatabase.memory();
  });
}

/// Creates a fresh in-memory test database
TestDatabase createTestDatabase() {
  return TestDatabase();
}

void main() {
  group('Database Initialization', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should initialize database successfully', () async {
      // Database should be accessible
      final result = await db.customSelect('SELECT 1 as value').getSingle();
      expect(result.read<int>('value'), equals(1));
    });

    test('should have correct schema version', () {
      expect(db.schemaVersion, equals(6));
    });

    test('should create all tables on initialization', () async {
      // Verify all tables exist
      final tables = await db.customSelect(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'",
      ).get();

      final tableNames = tables.map((r) => r.read<String>('name')).toSet();

      expect(tableNames, contains('test_tasks'));
      expect(tableNames, contains('test_outbox'));
      expect(tableNames, contains('test_fields'));
      expect(tableNames, contains('test_sync_logs'));
      expect(tableNames, contains('test_sync_events'));
      expect(tableNames, contains('test_cached_users'));
      expect(tableNames, contains('test_cached_user_profiles'));
    });

    test('should create indexes on initialization', () async {
      final indexes = await db.customSelect(
        "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'",
      ).get();

      final indexNames = indexes.map((r) => r.read<String>('name')).toSet();

      // Verify all TestTasks indexes
      expect(indexNames, contains('test_tasks_tenant_idx'));
      expect(indexNames, contains('test_tasks_field_idx'));
      expect(indexNames, contains('test_tasks_status_idx'));
      expect(indexNames, contains('test_tasks_synced_idx'));
      expect(indexNames, contains('test_tasks_tenant_status_idx'));
      expect(indexNames, contains('test_tasks_created_idx'));

      // Verify all TestOutbox indexes
      expect(indexNames, contains('test_outbox_tenant_idx'));
      expect(indexNames, contains('test_outbox_synced_idx'));
      expect(indexNames, contains('test_outbox_entity_idx'));
      expect(indexNames, contains('test_outbox_created_idx'));
      expect(indexNames, contains('test_outbox_tenant_synced_idx'));

      // Verify all TestFields indexes
      expect(indexNames, contains('test_fields_tenant_idx'));
      expect(indexNames, contains('test_fields_farm_idx'));
      expect(indexNames, contains('test_fields_synced_idx'));
      expect(indexNames, contains('test_fields_deleted_idx'));
      expect(indexNames, contains('test_fields_tenant_deleted_idx'));
      expect(indexNames, contains('test_fields_updated_idx'));
      expect(indexNames, contains('test_fields_remote_idx'));

      // Verify all TestSyncLogs indexes
      expect(indexNames, contains('test_sync_logs_status_idx'));
      expect(indexNames, contains('test_sync_logs_timestamp_idx'));
      expect(indexNames, contains('test_sync_logs_type_status_idx'));

      // Verify all TestSyncEvents indexes
      expect(indexNames, contains('test_sync_events_tenant_idx'));
      expect(indexNames, contains('test_sync_events_read_idx'));
      expect(indexNames, contains('test_sync_events_tenant_read_idx'));
      expect(indexNames, contains('test_sync_events_created_idx'));

      // Verify all TestCachedUsers indexes
      expect(indexNames, contains('test_cached_users_tenant_idx'));
      expect(indexNames, contains('test_cached_users_email_idx'));
    });

    test('should handle close and reopen', () async {
      // Insert some data
      await db.into(db.testTasks).insert(TestTasksCompanion.insert(
            id: 'task-1',
            tenantId: 'tenant-1',
            fieldId: 'field-1',
            title: 'Test Task',
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          ));

      // Close database
      await db.close();

      // Create new instance
      db = createTestDatabase();

      // Database should be accessible (fresh in-memory db)
      final result = await db.customSelect('SELECT 1 as value').getSingle();
      expect(result.read<int>('value'), equals(1));
    });
  });

  group('Transaction Support', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should commit transaction on success', () async {
      await db.transaction(() async {
        await db.into(db.testTasks).insert(TestTasksCompanion.insert(
              id: 'task-tx-1',
              tenantId: 'tenant-1',
              fieldId: 'field-1',
              title: 'Transaction Task',
              createdAt: DateTime.now(),
              updatedAt: DateTime.now(),
            ));
      });

      final tasks = await db.select(db.testTasks).get();
      expect(tasks.length, equals(1));
      expect(tasks.first.id, equals('task-tx-1'));
    });

    test('should rollback transaction on error', () async {
      try {
        await db.transaction(() async {
          await db.into(db.testTasks).insert(TestTasksCompanion.insert(
                id: 'task-tx-2',
                tenantId: 'tenant-1',
                fieldId: 'field-1',
                title: 'Will Rollback',
                createdAt: DateTime.now(),
                updatedAt: DateTime.now(),
              ));

          // Simulate an error
          throw Exception('Simulated error');
        });
      } catch (_) {
        // Expected error
      }

      // Task should not exist after rollback
      final tasks = await (db.select(db.testTasks)
            ..where((t) => t.id.equals('task-tx-2')))
          .get();
      expect(tasks, isEmpty);
    });

    test('should support nested transactions', () async {
      await db.transaction(() async {
        await db.into(db.testTasks).insert(TestTasksCompanion.insert(
              id: 'task-nested-1',
              tenantId: 'tenant-1',
              fieldId: 'field-1',
              title: 'Outer Transaction',
              createdAt: DateTime.now(),
              updatedAt: DateTime.now(),
            ));

        // Nested transaction (savepoint)
        await db.transaction(() async {
          await db.into(db.testTasks).insert(TestTasksCompanion.insert(
                id: 'task-nested-2',
                tenantId: 'tenant-1',
                fieldId: 'field-1',
                title: 'Inner Transaction',
                createdAt: DateTime.now(),
                updatedAt: DateTime.now(),
              ));
        });
      });

      final tasks = await db.select(db.testTasks).get();
      expect(tasks.length, equals(2));
    });
  });

  group('Batch Operations', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should insert multiple records in batch', () async {
      await db.batch((batch) {
        for (int i = 0; i < 100; i++) {
          batch.insert(
            db.testTasks,
            TestTasksCompanion.insert(
              id: 'batch-task-$i',
              tenantId: 'tenant-1',
              fieldId: 'field-1',
              title: 'Batch Task $i',
              createdAt: DateTime.now(),
              updatedAt: DateTime.now(),
            ),
          );
        }
      });

      final count = await db.testTasks.count().getSingle();
      expect(count, equals(100));
    });

    test('should handle batch insert with conflict resolution', () async {
      // Insert initial record
      await db.into(db.testTasks).insert(TestTasksCompanion.insert(
            id: 'conflict-task',
            tenantId: 'tenant-1',
            fieldId: 'field-1',
            title: 'Original Title',
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          ));

      // Batch insert with conflict update
      await db.batch((batch) {
        batch.insert(
          db.testTasks,
          TestTasksCompanion.insert(
            id: 'conflict-task',
            tenantId: 'tenant-1',
            fieldId: 'field-1',
            title: 'Updated Title',
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          ),
          onConflict: DoUpdate((old) => TestTasksCompanion(
                title: const Value('Updated Title'),
              )),
        );
      });

      final task = await (db.select(db.testTasks)
            ..where((t) => t.id.equals('conflict-task')))
          .getSingle();
      expect(task.title, equals('Updated Title'));
    });

    test('should roll back entire batch on error', () async {
      try {
        await db.batch((batch) {
          for (int i = 0; i < 10; i++) {
            batch.insert(
              db.testTasks,
              TestTasksCompanion.insert(
                id: 'rollback-task-$i',
                tenantId: 'tenant-1',
                fieldId: 'field-1',
                title: 'Will Rollback $i',
                createdAt: DateTime.now(),
                updatedAt: DateTime.now(),
              ),
            );
          }
          // This would fail due to constraint violation (same id)
          batch.insert(
            db.testTasks,
            TestTasksCompanion.insert(
              id: 'rollback-task-0', // Duplicate!
              tenantId: 'tenant-1',
              fieldId: 'field-1',
              title: 'Duplicate',
              createdAt: DateTime.now(),
              updatedAt: DateTime.now(),
            ),
          );
        });
      } catch (_) {
        // Expected
      }

      // All inserts should be rolled back
      final count = await db.testTasks.count().getSingle();
      expect(count, equals(0));
    });
  });

  group('Query Operations', () {
    late TestDatabase db;

    setUp(() async {
      db = createTestDatabase();

      // Insert test data
      await db.batch((batch) {
        for (int i = 1; i <= 20; i++) {
          batch.insert(
            db.testTasks,
            TestTasksCompanion.insert(
              id: 'query-task-$i',
              tenantId: i <= 10 ? 'tenant-1' : 'tenant-2',
              fieldId: 'field-${i % 3 + 1}',
              title: 'Task $i',
              status: Value(i % 4 == 0 ? 'done' : (i % 2 == 0 ? 'open' : 'in_progress')),
              priority: Value(i % 3 == 0 ? 'high' : (i % 2 == 0 ? 'medium' : 'low')),
              createdAt: DateTime.now().subtract(Duration(days: i)),
              updatedAt: DateTime.now(),
            ),
          );
        }
      });
    });

    tearDown(() async {
      await db.close();
    });

    test('should filter by tenant', () async {
      final tenant1Tasks = await (db.select(db.testTasks)
            ..where((t) => t.tenantId.equals('tenant-1')))
          .get();

      expect(tenant1Tasks.length, equals(10));
      expect(tenant1Tasks.every((t) => t.tenantId == 'tenant-1'), isTrue);
    });

    test('should filter by status', () async {
      final openTasks = await (db.select(db.testTasks)
            ..where((t) => t.status.equals('open')))
          .get();

      expect(openTasks.every((t) => t.status == 'open'), isTrue);
    });

    test('should filter by multiple conditions', () async {
      final highPriorityOpenTasks = await (db.select(db.testTasks)
            ..where((t) => t.tenantId.equals('tenant-1'))
            ..where((t) => t.status.equals('open'))
            ..where((t) => t.priority.equals('high')))
          .get();

      expect(
        highPriorityOpenTasks.every((t) =>
            t.tenantId == 'tenant-1' &&
            t.status == 'open' &&
            t.priority == 'high'),
        isTrue,
      );
    });

    test('should order by created date', () async {
      final orderedTasks = await (db.select(db.testTasks)
            ..orderBy([(t) => OrderingTerm.desc(t.createdAt)])
            ..limit(5))
          .get();

      for (int i = 0; i < orderedTasks.length - 1; i++) {
        expect(
          orderedTasks[i].createdAt.isAfter(orderedTasks[i + 1].createdAt) ||
              orderedTasks[i].createdAt.isAtSameMomentAs(orderedTasks[i + 1].createdAt),
          isTrue,
        );
      }
    });

    test('should limit and offset results', () async {
      final page1 = await (db.select(db.testTasks)
            ..orderBy([(t) => OrderingTerm.asc(t.id)])
            ..limit(5))
          .get();

      final page2 = await (db.select(db.testTasks)
            ..orderBy([(t) => OrderingTerm.asc(t.id)])
            ..limit(5, offset: 5))
          .get();

      expect(page1.length, equals(5));
      expect(page2.length, equals(5));
      expect(page1.map((t) => t.id).toSet().intersection(page2.map((t) => t.id).toSet()), isEmpty);
    });

    test('should count records with filter', () async {
      final count = await (db.testTasks.count(
        where: (t) => t.tenantId.equals('tenant-1'),
      )).getSingle();

      expect(count, equals(10));
    });

    test('should use IN clause for multiple values', () async {
      final result = await (db.select(db.testTasks)
            ..where((t) => t.status.isIn(['open', 'in_progress'])))
          .get();

      expect(result.every((t) => t.status == 'open' || t.status == 'in_progress'), isTrue);
    });
  });

  group('Watch Streams', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should emit initial value on watch', () async {
      await db.into(db.testTasks).insert(TestTasksCompanion.insert(
            id: 'watch-task-1',
            tenantId: 'tenant-1',
            fieldId: 'field-1',
            title: 'Initial Task',
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          ));

      final stream = db.select(db.testTasks).watch();
      final result = await stream.first;

      expect(result.length, equals(1));
      expect(result.first.title, equals('Initial Task'));
    });

    test('should emit on insert', () async {
      final stream = db.select(db.testTasks).watch();
      final results = <List<TestTask>>[];

      final subscription = stream.listen((data) {
        results.add(data);
      });

      // Wait for initial emission
      await Future<void>.delayed(const Duration(milliseconds: 50));

      // Insert new record
      await db.into(db.testTasks).insert(TestTasksCompanion.insert(
            id: 'stream-task',
            tenantId: 'tenant-1',
            fieldId: 'field-1',
            title: 'Streamed Task',
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          ));

      // Wait for stream update
      await Future<void>.delayed(const Duration(milliseconds: 50));

      await subscription.cancel();

      // Should have received at least 2 emissions (initial + after insert)
      expect(results.length, greaterThanOrEqualTo(2));
      expect(results.last.length, equals(1));
    });
  });

  group('Custom Statements', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should execute raw SQL select', () async {
      await db.into(db.testTasks).insert(TestTasksCompanion.insert(
            id: 'raw-task',
            tenantId: 'tenant-1',
            fieldId: 'field-1',
            title: 'Raw SQL Task',
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          ));

      final result = await db.customSelect(
        'SELECT COUNT(*) as count FROM test_tasks WHERE tenant_id = ?',
        variables: [Variable.withString('tenant-1')],
      ).getSingle();

      expect(result.read<int>('count'), equals(1));
    });

    test('should execute raw SQL update', () async {
      await db.into(db.testTasks).insert(TestTasksCompanion.insert(
            id: 'raw-update-task',
            tenantId: 'tenant-1',
            fieldId: 'field-1',
            title: 'Original',
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          ));

      await db.customStatement(
        'UPDATE test_tasks SET title = ? WHERE id = ?',
        ['Updated via raw SQL', 'raw-update-task'],
      );

      final task = await (db.select(db.testTasks)
            ..where((t) => t.id.equals('raw-update-task')))
          .getSingle();

      expect(task.title, equals('Updated via raw SQL'));
    });

    test('should execute PRAGMA commands', () async {
      // Check foreign keys setting
      final result = await db.customSelect('PRAGMA foreign_keys;').getSingle();
      // Note: foreign_keys may be 0 or 1 depending on database setup
      expect(result.data.containsKey('foreign_keys'), isTrue);
    });
  });

  group('Error Handling', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should throw on duplicate primary key', () async {
      await db.into(db.testTasks).insert(TestTasksCompanion.insert(
            id: 'dup-task',
            tenantId: 'tenant-1',
            fieldId: 'field-1',
            title: 'Original',
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          ));

      expect(
        () async => await db.into(db.testTasks).insert(TestTasksCompanion.insert(
              id: 'dup-task',
              tenantId: 'tenant-1',
              fieldId: 'field-1',
              title: 'Duplicate',
              createdAt: DateTime.now(),
              updatedAt: DateTime.now(),
            )),
        throwsA(isA<SqliteException>()),
      );
    });

    test('should throw on invalid SQL', () async {
      expect(
        () async => await db.customSelect('INVALID SQL QUERY').get(),
        throwsA(isA<SqliteException>()),
      );
    });

    test('should handle null values correctly', () async {
      await db.into(db.testTasks).insert(TestTasksCompanion.insert(
            id: 'nullable-task',
            tenantId: 'tenant-1',
            fieldId: 'field-1',
            title: 'Nullable Task',
            description: const Value(null),
            assignedTo: const Value(null),
            dueDate: const Value(null),
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          ));

      final task = await (db.select(db.testTasks)
            ..where((t) => t.id.equals('nullable-task')))
          .getSingle();

      expect(task.description, isNull);
      expect(task.assignedTo, isNull);
      expect(task.dueDate, isNull);
    });
  });

  group('Pending Tasks Query - getPendingTasks', () {
    late TestDatabase db;

    setUp(() async {
      db = createTestDatabase();
      final now = DateTime.now();

      // Insert tasks with various statuses
      await db.batch((batch) {
        batch.insert(db.testTasks, TestTasksCompanion.insert(
          id: 'pending-1', tenantId: 'tenant-1', fieldId: 'field-1',
          title: 'Open Task 1', status: const Value('open'),
          priority: const Value('high'),
          dueDate: Value(now.add(const Duration(days: 1))),
          createdAt: now, updatedAt: now,
        ));
        batch.insert(db.testTasks, TestTasksCompanion.insert(
          id: 'pending-2', tenantId: 'tenant-1', fieldId: 'field-1',
          title: 'In Progress Task', status: const Value('in_progress'),
          priority: const Value('medium'),
          dueDate: Value(now.add(const Duration(days: 3))),
          createdAt: now, updatedAt: now,
        ));
        batch.insert(db.testTasks, TestTasksCompanion.insert(
          id: 'pending-3', tenantId: 'tenant-1', fieldId: 'field-1',
          title: 'Done Task', status: const Value('done'),
          priority: const Value('low'),
          createdAt: now, updatedAt: now,
        ));
        batch.insert(db.testTasks, TestTasksCompanion.insert(
          id: 'pending-4', tenantId: 'tenant-1', fieldId: 'field-2',
          title: 'Cancelled Task', status: const Value('cancelled'),
          priority: const Value('medium'),
          createdAt: now, updatedAt: now,
        ));
        batch.insert(db.testTasks, TestTasksCompanion.insert(
          id: 'pending-5', tenantId: 'tenant-2', fieldId: 'field-3',
          title: 'Other Tenant Open', status: const Value('open'),
          priority: const Value('high'),
          createdAt: now, updatedAt: now,
        ));
        batch.insert(db.testTasks, TestTasksCompanion.insert(
          id: 'pending-6', tenantId: 'tenant-1', fieldId: 'field-1',
          title: 'Open Task 2', status: const Value('open'),
          priority: const Value('low'),
          dueDate: Value(now.add(const Duration(days: 5))),
          createdAt: now, updatedAt: now,
        ));
      });
    });

    tearDown(() async {
      await db.close();
    });

    test('should return only open and in_progress tasks for tenant', () async {
      final pendingTasks = await (db.select(db.testTasks)
            ..where((t) => t.tenantId.equals('tenant-1'))
            ..where((t) => t.status.isIn(['open', 'in_progress']))
            ..orderBy([
              (t) => OrderingTerm.asc(t.dueDate),
              (t) => OrderingTerm.desc(t.priority),
            ]))
          .get();

      expect(pendingTasks.length, equals(3));
      expect(
        pendingTasks.every((t) =>
            t.status == 'open' || t.status == 'in_progress'),
        isTrue,
      );
      expect(pendingTasks.every((t) => t.tenantId == 'tenant-1'), isTrue);
    });

    test('should not include done or cancelled tasks', () async {
      final pendingTasks = await (db.select(db.testTasks)
            ..where((t) => t.tenantId.equals('tenant-1'))
            ..where((t) => t.status.isIn(['open', 'in_progress'])))
          .get();

      final ids = pendingTasks.map((t) => t.id).toSet();
      expect(ids, isNot(contains('pending-3'))); // done
      expect(ids, isNot(contains('pending-4'))); // cancelled
    });

    test('should not include tasks from other tenants', () async {
      final pendingTasks = await (db.select(db.testTasks)
            ..where((t) => t.tenantId.equals('tenant-1'))
            ..where((t) => t.status.isIn(['open', 'in_progress'])))
          .get();

      expect(pendingTasks.every((t) => t.tenantId == 'tenant-1'), isTrue);
      expect(
        pendingTasks.map((t) => t.id).toSet(),
        isNot(contains('pending-5')),
      );
    });

    test('should order by due date ascending then priority descending', () async {
      final pendingTasks = await (db.select(db.testTasks)
            ..where((t) => t.tenantId.equals('tenant-1'))
            ..where((t) => t.status.isIn(['open', 'in_progress']))
            ..orderBy([
              (t) => OrderingTerm.asc(t.dueDate),
              (t) => OrderingTerm.desc(t.priority),
            ]))
          .get();

      expect(pendingTasks.length, equals(3));
      final withDueDates = pendingTasks.where((t) => t.dueDate != null).toList();
      for (int i = 0; i < withDueDates.length - 1; i++) {
        expect(
          withDueDates[i].dueDate!.isBefore(withDueDates[i + 1].dueDate!) ||
              withDueDates[i].dueDate!.isAtSameMomentAs(withDueDates[i + 1].dueDate!),
          isTrue,
        );
      }
    });

    test('should return empty list when no pending tasks exist', () async {
      final pendingTasks = await (db.select(db.testTasks)
            ..where((t) => t.tenantId.equals('tenant-nonexistent'))
            ..where((t) => t.status.isIn(['open', 'in_progress'])))
          .get();

      expect(pendingTasks, isEmpty);
    });
  });

  group('Mark Task Done - markTaskDone', () {
    late TestDatabase db;

    setUp(() async {
      db = createTestDatabase();
      final now = DateTime.now();

      await db.into(db.testTasks).insert(TestTasksCompanion.insert(
            id: 'mark-done-1',
            tenantId: 'tenant-1',
            fieldId: 'field-1',
            title: 'Task to Complete',
            status: const Value('open'),
            createdAt: now,
            updatedAt: now,
          ));

      await db.into(db.testTasks).insert(TestTasksCompanion.insert(
            id: 'mark-done-2',
            tenantId: 'tenant-1',
            fieldId: 'field-1',
            title: 'Task with Evidence',
            status: const Value('in_progress'),
            createdAt: now,
            updatedAt: now,
          ));
    });

    tearDown(() async {
      await db.close();
    });

    test('should mark task as done with status change', () async {
      await (db.update(db.testTasks)
            ..where((t) => t.id.equals('mark-done-1')))
          .write(TestTasksCompanion(
        status: const Value('done'),
        updatedAt: Value(DateTime.now()),
        synced: const Value(false),
      ));

      final task = await (db.select(db.testTasks)
            ..where((t) => t.id.equals('mark-done-1')))
          .getSingle();

      expect(task.status, equals('done'));
      expect(task.synced, isFalse);
    });

    test('should mark task done with evidence notes', () async {
      const notes = 'تم الانتهاء من رش المبيدات - Applied pesticide successfully';

      await (db.update(db.testTasks)
            ..where((t) => t.id.equals('mark-done-2')))
          .write(TestTasksCompanion(
        status: const Value('done'),
        evidenceNotes: const Value(notes),
        updatedAt: Value(DateTime.now()),
        synced: const Value(false),
      ));

      final task = await (db.select(db.testTasks)
            ..where((t) => t.id.equals('mark-done-2')))
          .getSingle();

      expect(task.status, equals('done'));
      expect(task.evidenceNotes, equals(notes));
      expect(task.synced, isFalse);
    });

    test('should mark task done with evidence photos as JSON array', () async {
      final photos = ['photo_001.jpg', 'photo_002.jpg', 'photo_003.jpg'];
      final photosJson = '["photo_001.jpg","photo_002.jpg","photo_003.jpg"]';

      await (db.update(db.testTasks)
            ..where((t) => t.id.equals('mark-done-1')))
          .write(TestTasksCompanion(
        status: const Value('done'),
        evidenceNotes: const Value('Field inspection complete'),
        evidencePhotos: Value(photosJson),
        updatedAt: Value(DateTime.now()),
        synced: const Value(false),
      ));

      final task = await (db.select(db.testTasks)
            ..where((t) => t.id.equals('mark-done-1')))
          .getSingle();

      expect(task.status, equals('done'));
      expect(task.evidenceNotes, equals('Field inspection complete'));
      expect(task.evidencePhotos, equals(photosJson));

      // Verify photos can be decoded from JSON
      final decoded = (task.evidencePhotos!.substring(1, task.evidencePhotos!.length - 1))
          .split(',')
          .map((s) => s.replaceAll('"', '').trim())
          .toList();
      expect(decoded.length, equals(3));
      expect(decoded.first, equals('photo_001.jpg'));
    });

    test('should mark task done with null evidence', () async {
      await (db.update(db.testTasks)
            ..where((t) => t.id.equals('mark-done-1')))
          .write(const TestTasksCompanion(
        status: Value('done'),
        evidenceNotes: Value(null),
        evidencePhotos: Value(null),
        synced: Value(false),
      ));

      final task = await (db.select(db.testTasks)
            ..where((t) => t.id.equals('mark-done-1')))
          .getSingle();

      expect(task.status, equals('done'));
      expect(task.evidenceNotes, isNull);
      expect(task.evidencePhotos, isNull);
    });

    test('should set synced to false when marking task done', () async {
      // First set as synced
      await (db.update(db.testTasks)
            ..where((t) => t.id.equals('mark-done-1')))
          .write(const TestTasksCompanion(synced: Value(true)));

      // Then mark as done (mirrors production markTaskDone)
      await (db.update(db.testTasks)
            ..where((t) => t.id.equals('mark-done-1')))
          .write(TestTasksCompanion(
        status: const Value('done'),
        updatedAt: Value(DateTime.now()),
        synced: const Value(false),
      ));

      final task = await (db.select(db.testTasks)
            ..where((t) => t.id.equals('mark-done-1')))
          .getSingle();

      expect(task.synced, isFalse);
    });
  });

  group('Performance', () {
    late TestDatabase db;

    setUp(() {
      db = createTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should handle large batch insert efficiently', () async {
      final stopwatch = Stopwatch()..start();

      await db.batch((batch) {
        for (int i = 0; i < 1000; i++) {
          batch.insert(
            db.testTasks,
            TestTasksCompanion.insert(
              id: 'perf-task-$i',
              tenantId: 'tenant-${i % 10}',
              fieldId: 'field-${i % 5}',
              title: 'Performance Task $i',
              createdAt: DateTime.now(),
              updatedAt: DateTime.now(),
            ),
          );
        }
      });

      stopwatch.stop();

      // Should complete within reasonable time (1 second for 1000 records)
      expect(stopwatch.elapsedMilliseconds, lessThan(1000));

      final count = await db.testTasks.count().getSingle();
      expect(count, equals(1000));
    });

    test('should use index for filtered queries', () async {
      // Insert test data
      await db.batch((batch) {
        for (int i = 0; i < 500; i++) {
          batch.insert(
            db.testTasks,
            TestTasksCompanion.insert(
              id: 'idx-task-$i',
              tenantId: 'tenant-${i % 5}',
              fieldId: 'field-1',
              title: 'Indexed Task $i',
              createdAt: DateTime.now(),
              updatedAt: DateTime.now(),
            ),
          );
        }
      });

      final stopwatch = Stopwatch()..start();

      // Query using indexed column
      final result = await (db.select(db.testTasks)
            ..where((t) => t.tenantId.equals('tenant-0')))
          .get();

      stopwatch.stop();

      // Should be fast due to index
      expect(stopwatch.elapsedMilliseconds, lessThan(100));
      expect(result.length, equals(100));
    });
  });
}
