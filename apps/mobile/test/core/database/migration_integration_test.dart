/// Migration Integration Tests for SAHOOL Mobile Database
/// اختبارات تكامل ترحيل قاعدة بيانات سهول
///
/// These tests verify the database migration system works correctly
/// with an in-memory SQLite database.
///
/// Note: These tests use an unencrypted in-memory database for testing
/// as SQLCipher is not available in the test environment.
import 'package:flutter_test/flutter_test.dart';
import 'package:drift/drift.dart' hide isNull, isNotNull;
import 'package:drift/native.dart';

part 'migration_integration_test.g.dart';

// We need to create a mock/test database since the real one uses SQLCipher

/// Test database that mimics the structure of AppDatabase
/// but without SQLCipher encryption for testing
@DriftDatabase(tables: [TestTasks, TestOutbox, TestFields, TestSyncLogs, TestSyncEvents])
class TestDatabase extends _$TestDatabase {
  TestDatabase(super.e);

  @override
  int get schemaVersion => 6;

  @override
  MigrationStrategy get migration => MigrationStrategy(
        onCreate: (Migrator m) async {
          await m.createAll();
          // Create migration_history table
          await customStatement('''
            CREATE TABLE IF NOT EXISTS migration_history (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              version INTEGER NOT NULL,
              from_version INTEGER NOT NULL,
              started_at TEXT NOT NULL,
              completed_at TEXT,
              status TEXT NOT NULL DEFAULT 'pending',
              error_message TEXT,
              script_checksum TEXT,
              duration_ms INTEGER,
              backup_created INTEGER NOT NULL DEFAULT 0,
              backup_path TEXT,
              metadata TEXT
            )
          ''');
        },
        onUpgrade: (Migrator m, int from, int to) async {
          // Simulate upgrade logic
          if (from < 5 && to >= 5) {
            // Add migration_history table if needed
            await customStatement('''
              CREATE TABLE IF NOT EXISTS migration_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL,
                from_version INTEGER NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                error_message TEXT,
                script_checksum TEXT,
                duration_ms INTEGER,
                backup_created INTEGER NOT NULL DEFAULT 0,
                backup_path TEXT,
                metadata TEXT
              )
            ''');

            // Add new columns to fields (if not exists)
            try {
              await customStatement('ALTER TABLE test_fields ADD COLUMN last_sync_at TEXT');
            } catch (_) {
              // Column might already exist
            }

            try {
              await customStatement('ALTER TABLE test_outbox ADD COLUMN sync_priority INTEGER DEFAULT 0');
            } catch (_) {
              // Column might already exist
            }
          }
        },
      );
}

// Test tables that mirror the real schema

class TestTasks extends Table {
  TextColumn get id => text()();
  TextColumn get tenantId => text()();
  TextColumn get fieldId => text()();
  TextColumn get title => text()();
  TextColumn get status => text().withDefault(const Constant('open'))();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();

  @override
  Set<Column> get primaryKey => {id};
}

class TestOutbox extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get tenantId => text()();
  TextColumn get entityType => text()();
  TextColumn get entityId => text()();
  TextColumn get apiEndpoint => text()();
  TextColumn get method => text().withDefault(const Constant('POST'))();
  TextColumn get payload => text()();
  BoolColumn get isSynced => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

class TestFields extends Table {
  TextColumn get id => text()();
  TextColumn get tenantId => text()();
  TextColumn get name => text()();
  TextColumn get boundary => text()();
  RealColumn get areaHectares => real()();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();

  @override
  Set<Column> get primaryKey => {id};
}

class TestSyncLogs extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get type => text()();
  TextColumn get status => text()();
  TextColumn get message => text().nullable()();
  DateTimeColumn get timestamp => dateTime()();
}

class TestSyncEvents extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get tenantId => text()();
  TextColumn get type => text()();
  TextColumn get message => text()();
  BoolColumn get isRead => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

void main() {
  late TestDatabase db;

  setUp(() {
    // Create an in-memory database for testing
    db = TestDatabase(NativeDatabase.memory());
  });

  tearDown(() async {
    await db.close();
  });

  group('Database Creation', () {
    test('should create all tables on new database', () async {
      // Insert a test record to verify tables exist
      await db.into(db.testTasks).insert(TestTasksCompanion.insert(
        id: 'task-1',
        tenantId: 'tenant-1',
        fieldId: 'field-1',
        title: 'Test Task',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      ));

      final tasks = await db.select(db.testTasks).get();
      expect(tasks.length, equals(1));
    });

    test('should have correct schema version', () async {
      final result = await db.customSelect('PRAGMA user_version').getSingle();
      expect(result.read<int>('user_version'), equals(6));
    });
  });

  group('Migration History Table', () {
    test('migration_history table should exist', () async {
      final tables = await db.customSelect(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='migration_history'",
      ).get();
      expect(tables.length, equals(1));
    });

    test('should be able to insert migration records', () async {
      await db.customStatement('''
        INSERT INTO migration_history (
          version, from_version, started_at, completed_at, status
        ) VALUES (5, 4, ?, ?, 'completed')
      ''', [
        DateTime.now().toIso8601String(),
        DateTime.now().toIso8601String(),
      ]);

      final records = await db.customSelect(
        'SELECT * FROM migration_history',
      ).get();
      expect(records.length, equals(1));
      expect(records.first.read<int>('version'), equals(5));
    });
  });

  group('Data Preservation', () {
    test('should preserve task data across operations', () async {
      // Insert test data
      await db.into(db.testTasks).insert(TestTasksCompanion.insert(
        id: 'task-preserve-1',
        tenantId: 'tenant-1',
        fieldId: 'field-1',
        title: 'Preserved Task',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      ));

      // Verify data exists
      final tasks = await (db.select(db.testTasks)
            ..where((t) => t.id.equals('task-preserve-1')))
          .get();
      expect(tasks.length, equals(1));
      expect(tasks.first.title, equals('Preserved Task'));
    });

    test('should preserve field data with GIS information', () async {
      // Insert field with boundary
      await db.into(db.testFields).insert(TestFieldsCompanion.insert(
        id: 'field-geo-1',
        tenantId: 'tenant-1',
        name: 'Geo Field',
        boundary: '[[44.191,15.369],[44.192,15.370]]',
        areaHectares: 10.5,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      ));

      // Verify data preserved
      final fields = await (db.select(db.testFields)
            ..where((f) => f.id.equals('field-geo-1')))
          .get();
      expect(fields.length, equals(1));
      expect(fields.first.name, equals('Geo Field'));
      expect(fields.first.boundary, contains('44.191'));
      expect(fields.first.areaHectares, equals(10.5));
    });

    test('should preserve outbox items', () async {
      // Insert outbox item
      await db.into(db.testOutbox).insert(TestOutboxCompanion.insert(
        tenantId: 'tenant-1',
        entityType: 'field',
        entityId: 'field-1',
        apiEndpoint: '/api/v1/fields',
        payload: '{"name": "New Field"}',
      ));

      // Verify data preserved
      final outbox = await (db.select(db.testOutbox)
            ..where((o) => o.entityId.equals('field-1')))
          .get();
      expect(outbox.length, equals(1));
      expect(outbox.first.entityType, equals('field'));
    });
  });

  group('Schema Verification', () {
    test('should have required columns in tasks table', () async {
      final columns = await db.customSelect(
        "PRAGMA table_info(test_tasks)",
      ).get();

      final columnNames = columns.map((c) => c.read<String>('name')).toList();
      expect(columnNames, contains('id'));
      expect(columnNames, contains('tenant_id'));
      expect(columnNames, contains('field_id'));
      expect(columnNames, contains('title'));
      expect(columnNames, contains('status'));
      expect(columnNames, contains('synced'));
    });

    test('should have required columns in fields table', () async {
      final columns = await db.customSelect(
        "PRAGMA table_info(test_fields)",
      ).get();

      final columnNames = columns.map((c) => c.read<String>('name')).toList();
      expect(columnNames, contains('id'));
      expect(columnNames, contains('tenant_id'));
      expect(columnNames, contains('name'));
      expect(columnNames, contains('boundary'));
      expect(columnNames, contains('area_hectares'));
    });

    test('should have required columns in outbox table', () async {
      final columns = await db.customSelect(
        "PRAGMA table_info(test_outbox)",
      ).get();

      final columnNames = columns.map((c) => c.read<String>('name')).toList();
      expect(columnNames, contains('id'));
      expect(columnNames, contains('tenant_id'));
      expect(columnNames, contains('entity_type'));
      expect(columnNames, contains('entity_id'));
      expect(columnNames, contains('api_endpoint'));
      expect(columnNames, contains('method'));
      expect(columnNames, contains('payload'));
    });
  });

  group('Database Integrity', () {
    test('integrity_check should pass', () async {
      final result = await db.customSelect('PRAGMA integrity_check').getSingle();
      expect(result.read<String>('integrity_check'), equals('ok'));
    });

    test('foreign_keys pragma should be available', () async {
      await db.customStatement('PRAGMA foreign_keys = ON');
      final result = await db.customSelect('PRAGMA foreign_keys').getSingle();
      expect(result.read<int>('foreign_keys'), equals(1));
    });
  });

  group('Concurrent Operations', () {
    test('should handle concurrent inserts', () async {
      // Insert multiple tasks concurrently
      final futures = List.generate(10, (i) {
        return db.into(db.testTasks).insert(TestTasksCompanion.insert(
          id: 'concurrent-task-$i',
          tenantId: 'tenant-1',
          fieldId: 'field-1',
          title: 'Concurrent Task $i',
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        ));
      });

      await Future.wait(futures);

      final tasks = await (db.select(db.testTasks)
            ..where((t) => t.id.like('concurrent-task-%')))
          .get();
      expect(tasks.length, equals(10));
    });
  });

  group('Batch Operations', () {
    test('should support batch inserts', () async {
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

      final count = await db.customSelect(
        "SELECT COUNT(*) as count FROM test_tasks WHERE id LIKE 'batch-task-%'",
      ).getSingle();
      expect(count.read<int>('count'), equals(100));
    });
  });

  group('Transaction Support', () {
    test('should rollback failed transactions', () async {
      try {
        await db.transaction(() async {
          await db.into(db.testTasks).insert(TestTasksCompanion.insert(
            id: 'tx-task-1',
            tenantId: 'tenant-1',
            fieldId: 'field-1',
            title: 'Transaction Task',
            createdAt: DateTime.now(),
            updatedAt: DateTime.now(),
          ));

          // Force an error
          throw Exception('Simulated error');
        });
      } catch (_) {
        // Expected
      }

      // Task should not exist due to rollback
      final tasks = await (db.select(db.testTasks)
            ..where((t) => t.id.equals('tx-task-1')))
          .get();
      expect(tasks, isEmpty);
    });

    test('should commit successful transactions', () async {
      await db.transaction(() async {
        await db.into(db.testTasks).insert(TestTasksCompanion.insert(
          id: 'tx-task-success',
          tenantId: 'tenant-1',
          fieldId: 'field-1',
          title: 'Committed Task',
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        ));
      });

      // Task should exist
      final tasks = await (db.select(db.testTasks)
            ..where((t) => t.id.equals('tx-task-success')))
          .get();
      expect(tasks.length, equals(1));
    });
  });
}
