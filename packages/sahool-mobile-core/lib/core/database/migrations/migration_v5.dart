/// Migration v4 -> v5: Migration Tracking and Metadata
/// الترحيل من الاصدار 4 الى 5: تتبع الترحيل والبيانات الوصفية
///
/// This migration adds:
/// - migration_history table for tracking all migrations
/// - last_sync_at column to Fields table
/// - sync_priority column to Outbox table
/// - Data validation improvements
library;

import 'package:drift/drift.dart';

import 'migration_base.dart';

/// Migration from schema version 4 to 5
///
/// Changes:
/// 1. Creates migration_history table for audit trail
/// 2. Adds last_sync_at column to Fields for better sync tracking
/// 3. Adds sync_priority to Outbox for prioritized sync
/// 4. Creates indices for performance optimization
class MigrationV5 extends Migration with MigrationHelpers {
  @override
  int get targetVersion => 5;

  @override
  String get description => 'Add migration tracking and sync metadata';

  @override
  String get descriptionAr => 'اضافة تتبع الترحيل وبيانات المزامنة';

  @override
  bool get supportsRollback => true;

  @override
  bool get requiresBackup => true;

  @override
  int get estimatedDurationMs => 2000;

  @override
  List<String> get affectedTables => [
        'migration_history',
        'fields',
        'outbox',
      ];

  @override
  Future<bool> preCheck(Migrator m, GeneratedDatabase db) async {
    // Verify we're coming from version 4
    final result = await db.customSelect('PRAGMA user_version').getSingle();
    final currentVersion = result.read<int>('user_version');

    if (currentVersion != 4) {
      log('Pre-check: Expected version 4, got $currentVersion');
      // Allow migration anyway if version is less than 5
      return currentVersion < 5;
    }

    // Verify required tables exist
    final requiredTables = ['fields', 'outbox', 'tasks', 'sync_logs', 'sync_events'];
    for (final table in requiredTables) {
      if (!await tableExists(db, table)) {
        log('Pre-check: Missing required table: $table');
        return false;
      }
    }

    log('Pre-check passed');
    return true;
  }

  @override
  Future<void> upgrade(Migrator m, GeneratedDatabase db) async {
    // Step 1: Create migration_history table
    await executeStep(
      'Create migration_history table',
      () => _createMigrationHistoryTable(db),
    );

    // Step 2: Add last_sync_at column to Fields
    await executeStep(
      'Add last_sync_at to Fields',
      () => _addFieldsSyncMetadata(db),
    );

    // Step 3: Add sync_priority to Outbox
    await executeStep(
      'Add sync_priority to Outbox',
      () => _addOutboxPriority(db),
    );

    // Step 4: Create performance indices
    await executeStep(
      'Create performance indices',
      () => _createIndices(db),
    );

    // Step 5: Initialize migration history with existing data
    await executeStep(
      'Initialize migration history',
      () => _initializeMigrationHistory(db),
    );

    log('Migration v5 completed successfully');
  }

  @override
  Future<void> rollback(Migrator m, GeneratedDatabase db) async {
    log('Rolling back migration v5');

    // Step 1: Drop migration_history table
    await executeStep(
      'Drop migration_history table',
      () async {
        await db.customStatement('DROP TABLE IF EXISTS migration_history');
      },
    );

    // Step 2: Drop added indices
    await executeStep(
      'Drop performance indices',
      () async {
        await db.customStatement('DROP INDEX IF EXISTS fields_last_sync_idx');
        await db.customStatement('DROP INDEX IF EXISTS outbox_priority_idx');
      },
    );

    // Note: We cannot remove columns in SQLite without recreating the table
    // The added columns (last_sync_at, sync_priority) will remain but unused
    log('Rollback note: Added columns remain in tables (SQLite limitation)');

    log('Migration v5 rollback completed');
  }

  @override
  Future<MigrationVerificationResult> verify(GeneratedDatabase db) async {
    final issues = <String>[];
    final details = <String, dynamic>{};

    // Verify migration_history table exists
    if (!await tableExists(db, 'migration_history')) {
      issues.add('migration_history table does not exist');
    } else {
      details['migration_history_exists'] = true;
    }

    // Verify last_sync_at column exists in Fields
    if (!await columnExists(db, 'fields', 'last_sync_at')) {
      issues.add('last_sync_at column missing from fields table');
    } else {
      details['fields_last_sync_at'] = true;
    }

    // Verify sync_priority column exists in Outbox
    if (!await columnExists(db, 'outbox', 'sync_priority')) {
      issues.add('sync_priority column missing from outbox table');
    } else {
      details['outbox_sync_priority'] = true;
    }

    // Verify indices exist
    if (!await indexExists(db, 'fields_last_sync_idx')) {
      issues.add('fields_last_sync_idx index does not exist');
    }

    if (!await indexExists(db, 'outbox_priority_idx')) {
      issues.add('outbox_priority_idx index does not exist');
    }

    if (issues.isEmpty) {
      return MigrationVerificationResult.success(
        version: targetVersion,
        message: 'All v5 migration changes verified',
        details: details,
      );
    } else {
      return MigrationVerificationResult.failure(
        version: targetVersion,
        message: 'Migration verification failed',
        issues: issues,
        details: details,
      );
    }
  }

  /// Create the migration_history table
  Future<void> _createMigrationHistoryTable(GeneratedDatabase db) async {
    // Check if table already exists
    if (await tableExists(db, 'migration_history')) {
      log('migration_history table already exists, skipping creation');
      return;
    }

    await db.customStatement('''
      CREATE TABLE migration_history (
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

    await db.customStatement('''
      CREATE INDEX migration_history_version_idx
      ON migration_history (version)
    ''');

    await db.customStatement('''
      CREATE INDEX migration_history_status_idx
      ON migration_history (status)
    ''');

    log('Created migration_history table with indices');
  }

  /// Add sync metadata columns to Fields table
  Future<void> _addFieldsSyncMetadata(GeneratedDatabase db) async {
    // Add last_sync_at column for tracking when field was last synced
    await addColumnIfNotExists(
      db,
      'fields',
      'last_sync_at TEXT',
      'last_sync_at',
    );

    // Add sync_error column for tracking sync errors
    await addColumnIfNotExists(
      db,
      'fields',
      'sync_error TEXT',
      'sync_error',
    );

    // Add sync_attempts column for tracking retry count
    await addColumnIfNotExists(
      db,
      'fields',
      'sync_attempts INTEGER DEFAULT 0',
      'sync_attempts',
    );
  }

  /// Add priority column to Outbox for prioritized sync
  Future<void> _addOutboxPriority(GeneratedDatabase db) async {
    // Add sync_priority column (higher number = higher priority)
    await addColumnIfNotExists(
      db,
      'outbox',
      'sync_priority INTEGER DEFAULT 0',
      'sync_priority',
    );

    // Add scheduled_at column for delayed sync support
    await addColumnIfNotExists(
      db,
      'outbox',
      'scheduled_at TEXT',
      'scheduled_at',
    );

    // Add last_error column for error tracking
    await addColumnIfNotExists(
      db,
      'outbox',
      'last_error TEXT',
      'last_error',
    );
  }

  /// Create performance indices
  Future<void> _createIndices(GeneratedDatabase db) async {
    // Index for fields sync status
    await createIndexIfNotExists(
      db,
      'fields_last_sync_idx',
      'fields',
      ['last_sync_at'],
    );

    // Index for outbox priority ordering
    await createIndexIfNotExists(
      db,
      'outbox_priority_idx',
      'outbox',
      ['sync_priority', 'created_at'],
    );

    // Index for outbox scheduled sync
    await createIndexIfNotExists(
      db,
      'outbox_scheduled_idx',
      'outbox',
      ['scheduled_at'],
    );
  }

  /// Initialize migration history with record of previous versions
  Future<void> _initializeMigrationHistory(GeneratedDatabase db) async {
    // Check if any records exist
    final existing = await db.customSelect(
      'SELECT COUNT(*) as count FROM migration_history',
    ).getSingle();

    if (existing.read<int>('count') > 0) {
      log('Migration history already initialized, skipping');
      return;
    }

    // Add historical migration records
    final now = DateTime.now().toIso8601String();
    final historicalVersions = [
      {'from': 0, 'to': 1, 'desc': 'Initial schema'},
      {'from': 1, 'to': 2, 'desc': 'GIS columns'},
      {'from': 2, 'to': 3, 'desc': 'ETag support'},
      {'from': 3, 'to': 4, 'desc': 'Unified Outbox'},
    ];

    for (final migration in historicalVersions) {
      await db.customStatement(
        '''
        INSERT INTO migration_history (
          version, from_version, started_at, completed_at, status, metadata
        ) VALUES (?, ?, ?, ?, 'completed', ?)
        ''',
        [
          Variable.withInt(migration['to'] as int),
          Variable.withInt(migration['from'] as int),
          Variable.withString(now),
          Variable.withString(now),
          Variable.withString('{"retroactive": true, "description": "${migration['desc']}"}'),
        ],
      );
    }

    log('Initialized migration history with ${historicalVersions.length} historical records');
  }
}

/// Sync priority levels for Outbox items
///
/// Higher numbers indicate higher priority
class SyncPriority {
  static const int low = 0;
  static const int normal = 10;
  static const int high = 20;
  static const int critical = 30;

  /// Get priority for an entity type
  static int forEntityType(String entityType) {
    switch (entityType.toLowerCase()) {
      case 'field':
        return high;
      case 'task':
        return normal;
      case 'sync_event':
        return low;
      default:
        return normal;
    }
  }

  /// Get priority for an HTTP method
  static int forMethod(String method) {
    switch (method.toUpperCase()) {
      case 'DELETE':
        return critical;
      case 'POST':
        return high;
      case 'PUT':
      case 'PATCH':
        return normal;
      case 'GET':
        return low;
      default:
        return normal;
    }
  }
}
