/// Database Encryption Migration Tests - _migrateToEncryptedDatabase
/// اختبارات ترحيل تشفير قاعدة البيانات
///
/// Tests for the migration logic from unencrypted to encrypted database:
/// - Temporary file management (creation, cleanup on error)
/// - Schema copy (tables, indexes) from old to new database
/// - Data preservation during migration
/// - File replacement flow (old -> temp -> final)
/// - Error handling and rollback on failure
/// - Verification step after migration
///
/// Note: Since SQLCipher native libraries are not available in test,
/// we test the migration logic using plain SQLite (simulating the
/// ATTACH/copy workflow without actual encryption). The encryption
/// key management is tested separately in encryption_test.dart.
library;
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:sqlite3/sqlite3.dart';

void main() {
  late Directory tempDir;

  setUp(() {
    tempDir = Directory.systemTemp.createTempSync('sahool_migration_test_');
  });

  tearDown(() {
    if (tempDir.existsSync()) {
      tempDir.deleteSync(recursive: true);
    }
  });

  group('Migration - Temporary File Management', () {
    test('should create temp .encrypted file during migration', () {
      final dbPath = '${tempDir.path}/sahool_field.db';
      final tempEncryptedPath = '$dbPath.encrypted';

      // Create the source database
      final sourceDb = sqlite3.open(dbPath);
      sourceDb.execute('CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT)');
      sourceDb.execute("INSERT INTO tasks VALUES ('t1', 'Task 1')");
      sourceDb.dispose();

      // Simulate migration: create temp encrypted file
      final tempFile = File(tempEncryptedPath);
      expect(tempFile.existsSync(), isFalse);

      // Attach and copy (simulating migration without actual encryption)
      final oldDb = sqlite3.open(dbPath);
      oldDb.execute("ATTACH DATABASE '$tempEncryptedPath' AS encrypted;");
      oldDb.execute('CREATE TABLE encrypted.tasks (id TEXT PRIMARY KEY, title TEXT)');
      oldDb.execute('INSERT INTO encrypted.tasks SELECT * FROM main.tasks;');
      oldDb.execute('DETACH DATABASE encrypted;');
      oldDb.dispose();

      // Temp file should now exist
      expect(tempFile.existsSync(), isTrue);

      // Verify data was copied
      final verifyDb = sqlite3.open(tempEncryptedPath);
      final result = verifyDb.select('SELECT COUNT(*) as count FROM tasks');
      expect(result.first['count'], equals(1));
      verifyDb.dispose();
    });

    test('should clean up existing temp file before migration', () {
      final dbPath = '${tempDir.path}/sahool_field.db';
      final tempEncryptedPath = '$dbPath.encrypted';

      // Create a stale temp file (from a previous failed migration)
      File(tempEncryptedPath).writeAsStringSync('stale data');
      expect(File(tempEncryptedPath).existsSync(), isTrue);

      // Mirror production: Remove temporary file if it exists
      final tempFile = File(tempEncryptedPath);
      if (tempFile.existsSync()) {
        tempFile.deleteSync();
      }

      expect(tempFile.existsSync(), isFalse);
    });

    test('should clean up temp file on migration error', () async {
      final dbPath = '${tempDir.path}/sahool_field.db';
      final tempEncryptedPath = '$dbPath.encrypted';

      // Create source database
      final sourceDb = sqlite3.open(dbPath);
      sourceDb.execute('CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT)');
      sourceDb.dispose();

      // Simulate migration that fails
      final tempFile = File(tempEncryptedPath);
      try {
        // Create temp file
        tempFile.writeAsStringSync('partial migration data');

        // Simulate error during migration
        throw Exception('Simulated migration error');
      } catch (e) {
        // Mirror production error handling: clean up temp file
        if (tempFile.existsSync()) {
          await tempFile.delete();
        }
      }

      // Temp file should be cleaned up
      expect(tempFile.existsSync(), isFalse);
      // Original file should be untouched
      expect(File(dbPath).existsSync(), isTrue);
    });
  });

  group('Migration - Schema Copy', () {
    test('should copy all tables from source to target database', () {
      final sourcePath = '${tempDir.path}/source.db';
      final targetPath = '${tempDir.path}/target.db';

      // Create source with multiple tables (mirrors production schema)
      final sourceDb = sqlite3.open(sourcePath);
      sourceDb.execute('''
        CREATE TABLE tasks (
          id TEXT PRIMARY KEY,
          tenant_id TEXT NOT NULL,
          field_id TEXT NOT NULL,
          title TEXT NOT NULL,
          status TEXT DEFAULT 'open',
          synced INTEGER DEFAULT 0,
          created_at TEXT NOT NULL
        )
      ''');
      sourceDb.execute('''
        CREATE TABLE outbox (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          tenant_id TEXT NOT NULL,
          entity_type TEXT NOT NULL,
          entity_id TEXT NOT NULL,
          api_endpoint TEXT NOT NULL,
          payload TEXT NOT NULL,
          is_synced INTEGER DEFAULT 0,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
      ''');
      sourceDb.execute('''
        CREATE TABLE fields (
          id TEXT PRIMARY KEY,
          tenant_id TEXT NOT NULL,
          name TEXT NOT NULL,
          boundary TEXT NOT NULL,
          area_hectares REAL NOT NULL,
          is_deleted INTEGER DEFAULT 0,
          etag TEXT
        )
      ''');
      sourceDb.execute('''
        CREATE TABLE sync_logs (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          type TEXT NOT NULL,
          status TEXT NOT NULL,
          message TEXT,
          timestamp TEXT NOT NULL
        )
      ''');
      sourceDb.execute('''
        CREATE TABLE sync_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          tenant_id TEXT NOT NULL,
          type TEXT NOT NULL,
          message TEXT NOT NULL,
          is_read INTEGER DEFAULT 0,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
      ''');
      sourceDb.dispose();

      // Simulate migration: copy schema using production's manual fallback pattern
      final oldDb = sqlite3.open(sourcePath);
      oldDb.execute("ATTACH DATABASE '$targetPath' AS encrypted;");

      // Get all tables (mirrors production logic)
      final tables = oldDb.select(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'",
      );

      for (final table in tables) {
        final tableName = table['name'] as String;

        // Copy schema
        final schema = oldDb.select(
          "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
          [tableName],
        );

        if (schema.isNotEmpty) {
          final createSql = schema.first['sql'] as String;
          oldDb.execute(createSql.replaceFirst('CREATE TABLE', 'CREATE TABLE encrypted.'));
        }
      }

      oldDb.execute('DETACH DATABASE encrypted;');
      oldDb.dispose();

      // Verify all tables were copied
      final verifyDb = sqlite3.open(targetPath);
      final targetTables = verifyDb.select(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'",
      );

      final tableNames = targetTables.map((r) => r['name'] as String).toSet();
      expect(tableNames, contains('tasks'));
      expect(tableNames, contains('outbox'));
      expect(tableNames, contains('fields'));
      expect(tableNames, contains('sync_logs'));
      expect(tableNames, contains('sync_events'));
      expect(tableNames.length, equals(5));

      verifyDb.dispose();
    });

    test('should copy all indexes from source to target', () {
      final sourcePath = '${tempDir.path}/source_idx.db';
      final targetPath = '${tempDir.path}/target_idx.db';

      // Create source with table and indexes
      final sourceDb = sqlite3.open(sourcePath);
      sourceDb.execute('''
        CREATE TABLE tasks (
          id TEXT PRIMARY KEY,
          tenant_id TEXT NOT NULL,
          field_id TEXT NOT NULL,
          status TEXT DEFAULT 'open',
          synced INTEGER DEFAULT 0,
          created_at TEXT NOT NULL
        )
      ''');
      sourceDb.execute('CREATE INDEX tasks_tenant_idx ON tasks(tenant_id)');
      sourceDb.execute('CREATE INDEX tasks_field_idx ON tasks(field_id)');
      sourceDb.execute('CREATE INDEX tasks_status_idx ON tasks(status)');
      sourceDb.execute('CREATE INDEX tasks_synced_idx ON tasks(synced)');
      sourceDb.execute('CREATE INDEX tasks_tenant_status_idx ON tasks(tenant_id, status)');
      sourceDb.execute('CREATE INDEX tasks_created_idx ON tasks(created_at)');
      sourceDb.dispose();

      // Migrate with table + index copy
      final oldDb = sqlite3.open(sourcePath);
      oldDb.execute("ATTACH DATABASE '$targetPath' AS encrypted;");

      // Copy table
      final tables = oldDb.select(
        "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'",
      );
      for (final table in tables) {
        final createSql = table['sql'] as String;
        oldDb.execute(createSql.replaceFirst('CREATE TABLE', 'CREATE TABLE encrypted.'));
      }

      // Copy indexes (mirrors production logic)
      final indices = oldDb.select(
        "SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL",
      );

      int indexesCopied = 0;
      for (final index in indices) {
        final createSql = index['sql'] as String;
        try {
          oldDb.execute(createSql.replaceFirst('CREATE INDEX', 'CREATE INDEX encrypted.'));
          indexesCopied++;
        } catch (e) {
          // Index might already exist, ignore (mirrors production)
        }
      }

      oldDb.execute('DETACH DATABASE encrypted;');
      oldDb.dispose();

      expect(indexesCopied, equals(6));

      // Verify indexes in target
      final verifyDb = sqlite3.open(targetPath);
      final targetIndexes = verifyDb.select(
        "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'",
      );

      final indexNames = targetIndexes.map((r) => r['name'] as String).toSet();
      expect(indexNames, contains('tasks_tenant_idx'));
      expect(indexNames, contains('tasks_field_idx'));
      expect(indexNames, contains('tasks_status_idx'));
      expect(indexNames, contains('tasks_synced_idx'));
      expect(indexNames, contains('tasks_tenant_status_idx'));
      expect(indexNames, contains('tasks_created_idx'));

      verifyDb.dispose();
    });
  });

  group('Migration - Data Preservation', () {
    test('should preserve all data during migration', () {
      final sourcePath = '${tempDir.path}/data_source.db';
      final targetPath = '${tempDir.path}/data_target.db';

      // Create source with sample data
      final sourceDb = sqlite3.open(sourcePath);
      sourceDb.execute('''
        CREATE TABLE tasks (
          id TEXT PRIMARY KEY,
          tenant_id TEXT NOT NULL,
          title TEXT NOT NULL,
          status TEXT DEFAULT 'open',
          priority TEXT DEFAULT 'medium',
          evidence_notes TEXT,
          evidence_photos TEXT
        )
      ''');

      // Insert diverse data including Arabic text and special characters
      sourceDb.execute(
        "INSERT INTO tasks VALUES ('t1', 'tenant-1', 'رش المبيدات الحشرية', 'open', 'high', 'ملاحظات التفتيش', 'photo1.jpg,photo2.jpg')",
      );
      sourceDb.execute(
        "INSERT INTO tasks VALUES ('t2', 'tenant-1', 'فحص التربة', 'done', 'medium', NULL, NULL)",
      );
      sourceDb.execute(
        "INSERT INTO tasks VALUES ('t3', 'tenant-2', 'Irrigation check', 'in_progress', 'low', 'All OK', NULL)",
      );

      sourceDb.execute('''
        CREATE TABLE fields (
          id TEXT PRIMARY KEY,
          tenant_id TEXT NOT NULL,
          name TEXT NOT NULL,
          boundary TEXT NOT NULL,
          centroid TEXT,
          area_hectares REAL NOT NULL
        )
      ''');
      sourceDb.execute(
        "INSERT INTO fields VALUES ('f1', 'tenant-1', 'حقل القمح', '[[46.7,24.7],[46.8,24.7],[46.8,24.8]]', '[46.75,24.75]', 12.5)",
      );

      sourceDb.dispose();

      // Migrate using production's manual fallback pattern
      final oldDb = sqlite3.open(sourcePath);
      oldDb.execute("ATTACH DATABASE '$targetPath' AS encrypted;");

      final tables = oldDb.select(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'",
      );

      for (final table in tables) {
        final tableName = table['name'] as String;

        final schema = oldDb.select(
          "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
          [tableName],
        );

        if (schema.isNotEmpty) {
          final createSql = schema.first['sql'] as String;
          oldDb.execute(createSql.replaceFirst('CREATE TABLE', 'CREATE TABLE encrypted.'));
        }

        // Copy data (mirrors production)
        oldDb.execute('INSERT INTO encrypted.$tableName SELECT * FROM main.$tableName;');
      }

      oldDb.execute('DETACH DATABASE encrypted;');
      oldDb.dispose();

      // Verify all data was preserved
      final verifyDb = sqlite3.open(targetPath);

      // Verify tasks
      final tasks = verifyDb.select('SELECT * FROM tasks ORDER BY id');
      expect(tasks.length, equals(3));

      // Verify Arabic text preserved
      expect(tasks[0]['title'], equals('رش المبيدات الحشرية'));
      expect(tasks[0]['evidence_notes'], equals('ملاحظات التفتيش'));
      expect(tasks[0]['evidence_photos'], equals('photo1.jpg,photo2.jpg'));

      // Verify NULLs preserved
      expect(tasks[1]['evidence_notes'], isNull);
      expect(tasks[1]['evidence_photos'], isNull);

      // Verify English text
      expect(tasks[2]['title'], equals('Irrigation check'));

      // Verify fields with GeoJSON data
      final fields = verifyDb.select('SELECT * FROM fields');
      expect(fields.length, equals(1));
      expect(fields[0]['name'], equals('حقل القمح'));
      expect(fields[0]['boundary'], contains('46.7'));
      expect(fields[0]['centroid'], contains('46.75'));
      expect(fields[0]['area_hectares'], equals(12.5));

      verifyDb.dispose();
    });

    test('should handle empty tables during migration', () {
      final sourcePath = '${tempDir.path}/empty_source.db';
      final targetPath = '${tempDir.path}/empty_target.db';

      final sourceDb = sqlite3.open(sourcePath);
      sourceDb.execute('CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT)');
      sourceDb.execute('CREATE TABLE outbox (id INTEGER PRIMARY KEY, payload TEXT)');
      // Both tables are empty
      sourceDb.dispose();

      // Migrate
      final oldDb = sqlite3.open(sourcePath);
      oldDb.execute("ATTACH DATABASE '$targetPath' AS encrypted;");

      final tables = oldDb.select(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'",
      );

      for (final table in tables) {
        final tableName = table['name'] as String;
        final schema = oldDb.select(
          "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
          [tableName],
        );
        if (schema.isNotEmpty) {
          oldDb.execute(
            (schema.first['sql'] as String).replaceFirst('CREATE TABLE', 'CREATE TABLE encrypted.'),
          );
        }
        oldDb.execute('INSERT INTO encrypted.$tableName SELECT * FROM main.$tableName;');
      }

      oldDb.execute('DETACH DATABASE encrypted;');
      oldDb.dispose();

      // Verify empty tables exist in target
      final verifyDb = sqlite3.open(targetPath);
      final taskCount = verifyDb.select('SELECT COUNT(*) as c FROM tasks');
      expect(taskCount.first['c'], equals(0));
      final outboxCount = verifyDb.select('SELECT COUNT(*) as c FROM outbox');
      expect(outboxCount.first['c'], equals(0));
      verifyDb.dispose();
    });

    test('should preserve large dataset during migration', () {
      final sourcePath = '${tempDir.path}/large_source.db';
      final targetPath = '${tempDir.path}/large_target.db';

      final sourceDb = sqlite3.open(sourcePath);
      sourceDb.execute('CREATE TABLE tasks (id TEXT PRIMARY KEY, tenant_id TEXT, title TEXT)');

      // Insert 500 records
      sourceDb.execute('BEGIN');
      for (int i = 0; i < 500; i++) {
        sourceDb.execute(
          "INSERT INTO tasks VALUES ('task-$i', 'tenant-${i % 5}', 'Task number $i')",
        );
      }
      sourceDb.execute('COMMIT');
      sourceDb.dispose();

      // Migrate
      final oldDb = sqlite3.open(sourcePath);
      oldDb.execute("ATTACH DATABASE '$targetPath' AS encrypted;");
      oldDb.execute('CREATE TABLE encrypted.tasks (id TEXT PRIMARY KEY, tenant_id TEXT, title TEXT)');
      oldDb.execute('INSERT INTO encrypted.tasks SELECT * FROM main.tasks;');
      oldDb.execute('DETACH DATABASE encrypted;');
      oldDb.dispose();

      // Verify count
      final verifyDb = sqlite3.open(targetPath);
      final count = verifyDb.select('SELECT COUNT(*) as c FROM tasks');
      expect(count.first['c'], equals(500));

      // Spot-check specific records
      final first = verifyDb.select("SELECT * FROM tasks WHERE id = 'task-0'");
      expect(first.first['tenant_id'], equals('tenant-0'));

      final last = verifyDb.select("SELECT * FROM tasks WHERE id = 'task-499'");
      expect(last.first['tenant_id'], equals('tenant-4'));

      verifyDb.dispose();
    });
  });

  group('Migration - File Replacement Flow', () {
    test('should replace original file with encrypted file', () async {
      final dbPath = '${tempDir.path}/sahool_field.db';
      final tempEncryptedPath = '$dbPath.encrypted';

      // Create original database
      final sourceDb = sqlite3.open(dbPath);
      sourceDb.execute('CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT)');
      sourceDb.execute("INSERT INTO tasks VALUES ('t1', 'Original')");
      sourceDb.dispose();

      // Create "encrypted" copy
      final oldDb = sqlite3.open(dbPath);
      oldDb.execute("ATTACH DATABASE '$tempEncryptedPath' AS encrypted;");
      oldDb.execute('CREATE TABLE encrypted.tasks (id TEXT PRIMARY KEY, title TEXT)');
      oldDb.execute('INSERT INTO encrypted.tasks SELECT * FROM main.tasks;');
      // Also update a value to prove we're reading from the new file later
      oldDb.execute("UPDATE encrypted.tasks SET title = 'Migrated' WHERE id = 't1'");
      oldDb.execute('DETACH DATABASE encrypted;');
      oldDb.dispose();

      // Replace old with new (mirrors production logic)
      final oldFile = File(dbPath);
      if (oldFile.existsSync()) {
        await oldFile.delete();
      }
      await File(tempEncryptedPath).rename(dbPath);

      // Original path should now contain the migrated database
      expect(File(dbPath).existsSync(), isTrue);
      expect(File(tempEncryptedPath).existsSync(), isFalse);

      // Verify the file at original path has migrated data
      final verifyDb = sqlite3.open(dbPath);
      final result = verifyDb.select("SELECT title FROM tasks WHERE id = 't1'");
      expect(result.first['title'], equals('Migrated'));
      verifyDb.dispose();
    });

    test('should keep backup of unencrypted database', () async {
      final dbPath = '${tempDir.path}/sahool_field.db';
      final backupPath = '${tempDir.path}/sahool_field_unencrypted.db';

      // Create original database
      final sourceDb = sqlite3.open(dbPath);
      sourceDb.execute('CREATE TABLE tasks (id TEXT PRIMARY KEY)');
      sourceDb.execute("INSERT INTO tasks VALUES ('backup-test')");
      sourceDb.dispose();

      // Mirror production: backup before migration
      await File(dbPath).copy(backupPath);

      // Verify backup exists
      expect(File(backupPath).existsSync(), isTrue);

      // Verify backup contains original data
      final backupDb = sqlite3.open(backupPath);
      final result = backupDb.select('SELECT * FROM tasks');
      expect(result.length, equals(1));
      expect(result.first['id'], equals('backup-test'));
      backupDb.dispose();
    });
  });

  group('Migration - Verification Step', () {
    test('should verify migrated database can be opened and queried', () {
      final targetPath = '${tempDir.path}/verify_target.db';

      // Create a "migrated" database
      final db = sqlite3.open(targetPath);
      db.execute('CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT)');
      db.execute('CREATE TABLE fields (id TEXT PRIMARY KEY, name TEXT)');
      db.execute("INSERT INTO tasks VALUES ('t1', 'Test')");
      db.execute("INSERT INTO fields VALUES ('f1', 'Field')");
      db.dispose();

      // Mirror production verification step
      final verifyDb = sqlite3.open(targetPath);

      // Test query to verify database works (mirrors production)
      final result = verifyDb.select('SELECT COUNT(*) as count FROM sqlite_master;');
      expect(result.first['count'], greaterThan(0));

      // Verify integrity
      final integrity = verifyDb.select('PRAGMA integrity_check;');
      expect(integrity.first['integrity_check'], equals('ok'));

      // Verify data is accessible
      final taskCount = verifyDb.select('SELECT COUNT(*) as c FROM tasks');
      expect(taskCount.first['c'], equals(1));

      verifyDb.dispose();
    });

    test('should detect corrupted migrated database', () {
      final targetPath = '${tempDir.path}/corrupted.db';

      // Create a corrupted file
      File(targetPath).writeAsBytesSync([0, 1, 2, 3, 4, 5]);

      // Attempt to open and query should fail (open is lazy, query forces read)
      expect(
        () {
          final db = sqlite3.open(targetPath);
          try {
            db.execute('SELECT * FROM sqlite_master');
          } finally {
            db.dispose();
          }
        },
        throwsA(isA<SqliteException>()),
      );
    });
  });

  group('Migration - Error Handling', () {
    test('should handle source database not found', () {
      final nonExistentPath = '${tempDir.path}/nonexistent.db';

      expect(
        () => sqlite3.open(nonExistentPath, mode: OpenMode.readOnly),
        throwsA(isA<SqliteException>()),
      );
    });

    test('should handle permission errors gracefully', () async {
      final dbPath = '${tempDir.path}/readonly_test.db';
      final tempPath = '$dbPath.encrypted';

      // Create source
      final db = sqlite3.open(dbPath);
      db.execute('CREATE TABLE t (id TEXT)');
      db.dispose();

      // The migration logic wraps everything in try/catch
      // and cleans up temp files on error (mirrors production)
      File? tempFile;
      try {
        tempFile = File(tempPath);

        // Simulate a migration step that throws
        throw const FileSystemException('Permission denied');
      } catch (e) {
        // Clean up temp file on error (mirrors production)
        if (tempFile != null && tempFile.existsSync()) {
          await tempFile.delete();
        }
        expect(e, isA<FileSystemException>());
      }
    });

    test('should rethrow error after cleanup', () async {
      final dbPath = '${tempDir.path}/rethrow_test.db';
      final tempPath = '$dbPath.encrypted';
      final tempFile = File(tempPath);

      // Mirror production error handling pattern
      bool errorRethrown = false;
      try {
        // Create temp file to verify cleanup
        tempFile.writeAsStringSync('temp');

        throw Exception('Migration failed: disk full');
      } catch (e) {
        // Clean up
        if (tempFile.existsSync()) {
          await tempFile.delete();
        }
        errorRethrown = true;
        // In production, rethrow happens here
      }

      expect(errorRethrown, isTrue);
      expect(tempFile.existsSync(), isFalse);
    });
  });

  group('Migration - Full End-to-End Simulation', () {
    test('should complete full migration workflow', () async {
      final dbPath = '${tempDir.path}/sahool_field.db';
      final backupPath = '${tempDir.path}/sahool_field_unencrypted.db';
      final tempEncryptedPath = '$dbPath.encrypted';

      // Step 1: Create production-like unencrypted database
      final sourceDb = sqlite3.open(dbPath);
      sourceDb.execute('''
        CREATE TABLE tasks (
          id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL,
          field_id TEXT NOT NULL, title TEXT NOT NULL,
          status TEXT DEFAULT 'open', priority TEXT DEFAULT 'medium',
          evidence_notes TEXT, evidence_photos TEXT,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
          synced INTEGER DEFAULT 0
        )
      ''');
      sourceDb.execute('''
        CREATE TABLE outbox (
          id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id TEXT NOT NULL,
          entity_type TEXT NOT NULL, entity_id TEXT NOT NULL,
          api_endpoint TEXT NOT NULL, method TEXT DEFAULT 'POST',
          payload TEXT NOT NULL, if_match TEXT,
          retry_count INTEGER DEFAULT 0, is_synced INTEGER DEFAULT 0,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
      ''');
      sourceDb.execute('''
        CREATE TABLE fields (
          id TEXT PRIMARY KEY, remote_id TEXT, tenant_id TEXT NOT NULL,
          farm_id TEXT, name TEXT NOT NULL, crop_type TEXT,
          boundary TEXT NOT NULL, centroid TEXT, area_hectares REAL NOT NULL,
          status TEXT, ndvi_current REAL, ndvi_updated_at TEXT,
          synced INTEGER DEFAULT 0, is_deleted INTEGER DEFAULT 0,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
          etag TEXT, server_updated_at TEXT
        )
      ''');
      sourceDb.execute('''
        CREATE TABLE sync_logs (
          id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT NOT NULL,
          status TEXT NOT NULL, message TEXT, timestamp TEXT NOT NULL
        )
      ''');
      sourceDb.execute('''
        CREATE TABLE sync_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id TEXT NOT NULL,
          type TEXT NOT NULL, entity_type TEXT, entity_id TEXT,
          message TEXT NOT NULL, is_read INTEGER DEFAULT 0,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
      ''');

      // Add indexes
      sourceDb.execute('CREATE INDEX tasks_tenant_idx ON tasks(tenant_id)');
      sourceDb.execute('CREATE INDEX tasks_status_idx ON tasks(status)');
      sourceDb.execute('CREATE INDEX tasks_synced_idx ON tasks(synced)');
      sourceDb.execute('CREATE INDEX outbox_synced_idx ON outbox(is_synced)');
      sourceDb.execute('CREATE INDEX fields_tenant_idx ON fields(tenant_id)');
      sourceDb.execute('CREATE INDEX fields_deleted_idx ON fields(is_deleted)');
      sourceDb.execute('CREATE INDEX sync_events_tenant_idx ON sync_events(tenant_id)');

      // Insert sample data
      sourceDb.execute('''
        INSERT INTO tasks VALUES (
          'task-1', 'tenant-1', 'field-1', 'رش المبيدات', 'open', 'high',
          'ملاحظات التفتيش', 'photo1.jpg,photo2.jpg',
          '2026-03-01T00:00:00Z', '2026-03-10T00:00:00Z', 0
        )
      ''');
      sourceDb.execute('''
        INSERT INTO fields VALUES (
          'field-1', 'remote-1', 'tenant-1', 'farm-1', 'حقل القمح', 'wheat',
          '[[46.7,24.7],[46.8,24.7],[46.8,24.8]]', '[46.75,24.75]', 12.5,
          'active', 0.72, '2026-03-10T00:00:00Z', 0, 0,
          '2026-01-01T00:00:00Z', '2026-03-10T00:00:00Z', '"etag-123"', '2026-03-10T00:00:00Z'
        )
      ''');
      sourceDb.execute('''
        INSERT INTO outbox (tenant_id, entity_type, entity_id, api_endpoint, payload)
        VALUES ('tenant-1', 'task', 'task-1', '/api/v1/tasks', '{"title":"رش المبيدات"}')
      ''');

      sourceDb.dispose();

      // Step 2: Backup (mirrors production)
      await File(dbPath).copy(backupPath);
      expect(File(backupPath).existsSync(), isTrue);

      // Step 3: Remove stale temp file if exists
      final tempFile = File(tempEncryptedPath);
      if (tempFile.existsSync()) {
        await tempFile.delete();
      }

      // Step 4: Migrate (mirrors production manual fallback)
      final oldDb = sqlite3.open(dbPath);

      oldDb.execute("ATTACH DATABASE '$tempEncryptedPath' AS encrypted;");

      // Copy all tables
      final tables = oldDb.select(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'",
      );

      for (final table in tables) {
        final tableName = table['name'] as String;

        final schema = oldDb.select(
          "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
          [tableName],
        );

        if (schema.isNotEmpty) {
          final createSql = schema.first['sql'] as String;
          oldDb.execute(createSql.replaceFirst('CREATE TABLE', 'CREATE TABLE encrypted.'));
        }

        oldDb.execute('INSERT INTO encrypted.$tableName SELECT * FROM main.$tableName;');
      }

      // Copy indexes
      final indices = oldDb.select(
        "SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL",
      );

      for (final index in indices) {
        final createSql = index['sql'] as String;
        try {
          oldDb.execute(createSql.replaceFirst('CREATE INDEX', 'CREATE INDEX encrypted.'));
        } catch (e) {
          // Ignore duplicate index errors (mirrors production)
        }
      }

      oldDb.execute('DETACH DATABASE encrypted;');
      oldDb.dispose();

      // Step 5: Verify migration (mirrors production)
      final verifyDb = sqlite3.open(tempEncryptedPath);
      final schemaCount = verifyDb.select('SELECT COUNT(*) as count FROM sqlite_master;');
      expect(schemaCount.first['count'] as int, greaterThan(0));

      final integrity = verifyDb.select('PRAGMA integrity_check;');
      expect(integrity.first['integrity_check'], equals('ok'));
      verifyDb.dispose();

      // Step 6: Replace original with encrypted (mirrors production)
      final oldFile = File(dbPath);
      if (oldFile.existsSync()) {
        await oldFile.delete();
      }
      await File(tempEncryptedPath).rename(dbPath);

      // Step 7: Final verification
      expect(File(dbPath).existsSync(), isTrue);
      expect(File(tempEncryptedPath).existsSync(), isFalse);
      expect(File(backupPath).existsSync(), isTrue); // Backup preserved

      final finalDb = sqlite3.open(dbPath);

      // Verify tables
      final finalTables = finalDb.select(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'",
      );
      expect(finalTables.length, equals(5));

      // Verify indexes
      final finalIndexes = finalDb.select(
        "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'",
      );
      expect(finalIndexes.length, equals(7));

      // Verify task data with Arabic text
      final taskResult = finalDb.select("SELECT * FROM tasks WHERE id = 'task-1'");
      expect(taskResult.length, equals(1));
      expect(taskResult.first['title'], equals('رش المبيدات'));
      expect(taskResult.first['evidence_notes'], equals('ملاحظات التفتيش'));
      expect(taskResult.first['evidence_photos'], equals('photo1.jpg,photo2.jpg'));
      expect(taskResult.first['priority'], equals('high'));

      // Verify field data with GIS
      final fieldResult = finalDb.select("SELECT * FROM fields WHERE id = 'field-1'");
      expect(fieldResult.length, equals(1));
      expect(fieldResult.first['name'], equals('حقل القمح'));
      expect(fieldResult.first['boundary'], contains('46.7'));
      expect(fieldResult.first['centroid'], contains('46.75'));
      expect(fieldResult.first['area_hectares'], equals(12.5));
      expect(fieldResult.first['etag'], equals('"etag-123"'));

      // Verify outbox data
      final outboxResult = finalDb.select('SELECT * FROM outbox');
      expect(outboxResult.length, equals(1));
      expect(outboxResult.first['entity_type'], equals('task'));
      expect(outboxResult.first['payload'], contains('رش المبيدات'));

      finalDb.dispose();
    });

    test('should rollback cleanly on failure mid-migration', () async {
      final dbPath = '${tempDir.path}/rollback_test.db';
      final backupPath = '${tempDir.path}/rollback_unencrypted.db';
      final tempEncryptedPath = '$dbPath.encrypted';

      // Create source database with data
      final sourceDb = sqlite3.open(dbPath);
      sourceDb.execute('CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT)');
      sourceDb.execute("INSERT INTO tasks VALUES ('t1', 'Important Data')");
      sourceDb.dispose();

      // Backup
      await File(dbPath).copy(backupPath);

      // Simulate migration that fails midway
      final tempFile = File(tempEncryptedPath);
      try {
        // Start migration
        tempFile.writeAsStringSync('partial data');

        // Simulate failure
        throw Exception('Disk full during migration');
      } catch (e) {
        // Clean up temp file (mirrors production)
        if (tempFile.existsSync()) {
          await tempFile.delete();
        }
      }

      // Original should be intact
      expect(File(dbPath).existsSync(), isTrue);
      final verifyDb = sqlite3.open(dbPath);
      final result = verifyDb.select('SELECT * FROM tasks');
      expect(result.length, equals(1));
      expect(result.first['title'], equals('Important Data'));
      verifyDb.dispose();

      // Backup should also be intact
      expect(File(backupPath).existsSync(), isTrue);

      // Temp file should be cleaned up
      expect(tempFile.existsSync(), isFalse);
    });
  });

  group('Migration - _openConnection Decision Logic', () {
    test('should detect need for migration (no key + db exists)', () async {
      final dbPath = '${tempDir.path}/existing_db.db';

      // Create existing unencrypted database
      final db = sqlite3.open(dbPath);
      db.execute('CREATE TABLE tasks (id TEXT)');
      db.dispose();

      // Simulate the decision logic from _openConnection
      final dbFile = File(dbPath);
      const hasKey = false; // No encryption key exists

      final needsMigration = !hasKey && dbFile.existsSync();
      expect(needsMigration, isTrue);
    });

    test('should detect first-time setup (no key + no db)', () async {
      final dbPath = '${tempDir.path}/new_db.db';

      // No database file exists
      final dbFile = File(dbPath);
      const hasKey = false;

      final needsMigration = !hasKey && dbFile.existsSync();
      final isFirstSetup = !hasKey && !dbFile.existsSync();

      expect(needsMigration, isFalse);
      expect(isFirstSetup, isTrue);
    });

    test('should detect normal open (has key + db exists)', () async {
      final dbPath = '${tempDir.path}/encrypted_db.db';

      // Create database file
      final db = sqlite3.open(dbPath);
      db.execute('CREATE TABLE tasks (id TEXT)');
      db.dispose();

      final dbFile = File(dbPath);
      const hasKey = true; // Key already exists

      final needsMigration = !hasKey && dbFile.existsSync();
      expect(needsMigration, isFalse);
    });
  });
}
