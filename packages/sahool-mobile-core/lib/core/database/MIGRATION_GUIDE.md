# Database Migration Guide

## SAHOOL Mobile Database Migration System
## نظام ترحيل قاعدة بيانات سهول

This guide documents the database migration system for the SAHOOL mobile application.

---

## Overview

The migration system provides:
- **Sequential schema upgrades** - Migrations are applied in order
- **Pre-migration backups** - Automatic backup before migration
- **Verification** - Schema and data integrity verification
- **Rollback support** - Where SQLite limitations allow
- **Audit logging** - Complete migration history tracking
- **Encrypted database support** - Works with SQLCipher

---

## Current Schema Version

**Version 5** (as of January 2025)

### Version History

| Version | Description | Changes |
|---------|-------------|---------|
| v1 | Initial schema | Tasks, Outbox, Fields, SyncLogs tables |
| v2 | GIS support | Added boundary, centroid columns to Fields |
| v3 | ETag support | Added etag, server_updated_at, SyncEvents table |
| v4 | Unified Outbox | Restructured Outbox with entity targeting |
| v5 | Migration tracking | migration_history table, sync metadata |

---

## Creating a New Migration

### Step 1: Create Migration File

Create a new file in `lib/core/database/migrations/`:

```dart
// lib/core/database/migrations/migration_v6.dart

import 'package:drift/drift.dart';
import '../schema_version.dart';
import 'migration_base.dart';

class MigrationV6 extends Migration with MigrationHelpers {
  @override
  int get targetVersion => 6;

  @override
  String get description => 'Add feature X support';

  @override
  String get descriptionAr => 'اضافة دعم الميزة X';

  @override
  bool get supportsRollback => true; // Set to true if rollback is possible

  @override
  List<String> get affectedTables => ['table_name'];

  @override
  Future<void> upgrade(Migrator m, GeneratedDatabase db) async {
    // Add your migration logic here
    await executeStep('Add new column', () async {
      await addColumnIfNotExists(
        db,
        'table_name',
        'new_column TEXT',
        'new_column',
      );
    });
  }

  @override
  Future<void> rollback(Migrator m, GeneratedDatabase db) async {
    // Add rollback logic if supportsRollback is true
    log('Rolling back migration v6');
    // Note: SQLite cannot drop columns, may need table recreation
  }

  @override
  Future<MigrationVerificationResult> verify(GeneratedDatabase db) async {
    // Verify the migration was successful
    if (!await columnExists(db, 'table_name', 'new_column')) {
      return MigrationVerificationResult.failure(
        version: targetVersion,
        message: 'Column not created',
        issues: ['new_column missing from table_name'],
      );
    }
    return MigrationVerificationResult.success(
      version: targetVersion,
      message: 'Migration v6 verified',
    );
  }
}
```

### Step 2: Register Migration

Add the migration to `migration_strategy.dart`:

```dart
static final Map<int, Migration> _migrations = {
  5: MigrationV5(),
  6: MigrationV6(), // Add new migration
};
```

### Step 3: Update Schema Version

In `schema_version.dart`:

1. Update `currentSchemaVersion`:
```dart
const int currentSchemaVersion = 6; // Updated from 5
```

2. Add version to registry:
```dart
SchemaVersion(
  version: 6,
  description: 'Add feature X support',
  descriptionAr: 'اضافة دعم الميزة X',
  releaseDate: DateTime(2025, 7, 1),
),
```

### Step 4: Export Migration

Add to `migrations/migrations.dart`:
```dart
export 'migration_v6.dart';
```

---

## Migration Best Practices

### DO:

1. **Test migrations thoroughly**
   ```bash
   flutter test test/core/database/migration_test.dart
   ```

2. **Use helper methods**
   ```dart
   await addColumnIfNotExists(db, 'table', 'column TEXT', 'column');
   await createIndexIfNotExists(db, 'idx_name', 'table', ['column']);
   ```

3. **Implement verification**
   ```dart
   @override
   Future<MigrationVerificationResult> verify(GeneratedDatabase db) async {
     // Always verify critical changes
   }
   ```

4. **Log progress**
   ```dart
   await executeStep('Step description', () async {
     // Migration logic
   });
   ```

5. **Preserve data when possible**
   ```dart
   final backup = await backupTableData(db, 'table_name');
   // Make changes
   await restoreTableData(db, 'table_name', backup, columns);
   ```

### DON'T:

1. **Don't modify existing migration files** - Create new migrations instead

2. **Don't skip versions** - Migrations must be sequential

3. **Don't assume columns exist** - Always check first
   ```dart
   if (await columnExists(db, 'table', 'column')) { ... }
   ```

4. **Don't forget encrypted database** - Test with SQLCipher

---

## SQLite Limitations

Be aware of SQLite's limitations:

| Operation | Supported | Workaround |
|-----------|-----------|------------|
| Add column | Yes | Use ALTER TABLE |
| Drop column | No* | Recreate table |
| Rename column | No* | Recreate table |
| Change type | No | Recreate table |
| Add constraint | No | Recreate table |

*SQLite 3.35+ supports some of these, but mobile SQLite may be older

### Table Recreation Pattern

```dart
Future<void> recreateTableWithChanges(GeneratedDatabase db) async {
  // 1. Backup data
  final backup = await backupTableData(db, 'old_table');

  // 2. Drop old table
  await db.customStatement('DROP TABLE IF EXISTS old_table');

  // 3. Create new table with changes
  await db.customStatement('''
    CREATE TABLE old_table (
      id TEXT PRIMARY KEY,
      -- new schema
    )
  ''');

  // 4. Restore data
  await restoreTableData(db, 'old_table', backup, ['id', ...]);
}
```

---

## Testing Migrations

### Unit Tests

```dart
test('migration should add column', () async {
  final migration = MigrationV6();
  expect(migration.targetVersion, equals(6));
  expect(migration.supportsRollback, isTrue);
});
```

### Integration Tests

```dart
test('should migrate from v5 to v6', () async {
  // Create v5 database
  final db = createTestDatabaseAtVersion(5);

  // Run migration
  await db.runMigrations();

  // Verify
  final columns = await db.getColumns('table_name');
  expect(columns, contains('new_column'));
});
```

### Encrypted Database Tests

Test with SQLCipher:
```dart
test('migration works with encrypted database', () async {
  final db = createEncryptedTestDatabase();
  // ... test migration
});
```

---

## Troubleshooting

### Migration Failed

1. Check error message in logs
2. Review backup file (if created)
3. Verify pre-conditions met

### Verification Failed

```dart
// Get detailed verification report
final report = await db.verifyDatabase();
print(report.toDetailedReport());
```

### Rollback Needed

```dart
// Attempt rollback (if supported)
final result = await SahoolMigrationStrategy.attemptRollback(
  db,
  targetVersion,
  backupPath,
);

if (!result.success) {
  // Manual restore from backup required
  print('Restore from: ${result.backupPath}');
}
```

---

## API Reference

### MigrationVerifier

```dart
final verifier = MigrationVerifier(db);

// Full verification
final report = await verifier.runFullVerification();

// Individual checks
await verifier.verifySchemaVersion();
await verifier.verifyTables();
await verifier.verifyIndices();
await verifier.verifyDataIntegrity();

// Statistics
final stats = await verifier.getStats();
```

### MigrationHelpers Mixin

```dart
// Table existence
bool exists = await tableExists(db, 'table_name');

// Column existence
bool hasColumn = await columnExists(db, 'table', 'column');

// Index existence
bool hasIndex = await indexExists(db, 'index_name');

// Row count
int count = await getRowCount(db, 'table_name');

// Column list
List<String> columns = await getColumns(db, 'table_name');

// Safe column addition
await addColumnIfNotExists(db, 'table', 'col TEXT', 'col');

// Safe index creation
await createIndexIfNotExists(db, 'idx', 'table', ['col']);

// Data backup/restore
List<Map> data = await backupTableData(db, 'table');
int rows = await restoreTableData(db, 'table', data, columns);
```

---

## Migration History

Query migration history:

```dart
final history = await db.getMigrationHistory();
for (final record in history) {
  print('v${record['version']}: ${record['status']}');
}
```

---

## Emergency Procedures

### Database Corruption

1. Stop the app
2. Locate backup: `getApplicationDocumentsDirectory()/backups/`
3. Replace corrupted database with backup
4. Restart app

### Manual Recovery

```sql
-- Check integrity
PRAGMA integrity_check;

-- Export data before recreation
.mode csv
.output backup.csv
SELECT * FROM table_name;

-- Recreate corrupted tables
DROP TABLE IF EXISTS corrupted_table;
CREATE TABLE corrupted_table (...);

-- Import data
.import backup.csv corrupted_table
```

---

*Last updated: January 2025*
