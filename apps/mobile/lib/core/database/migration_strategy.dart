/// Migration Strategy for SAHOOL Mobile Database
/// استراتيجية ترحيل قاعدة بيانات سهول
///
/// This module orchestrates database migrations, providing:
/// - Sequential migration execution
/// - Pre-migration backup
/// - Migration verification
/// - Rollback support (where possible)
/// - Audit logging
/// - Encrypted database support
library;

import 'dart:io';

import 'package:drift/drift.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;

import 'schema_version.dart';
import 'migrations/migration_base.dart';
import 'migrations/migration_v5.dart';
import 'migrations/migration_v6.dart';
import 'migrations/migration_v7.dart';
import '../utils/app_logger.dart';

/// Migration strategy coordinator
///
/// Manages the execution of all database migrations in sequence,
/// with support for backup, verification, and rollback.
class SahoolMigrationStrategy {
  /// Registry of all available migrations
  static final Map<int, Migration> _migrations = {
    5: MigrationV5(),
    6: MigrationV6(),
    7: MigrationV7(),
  };

  /// Get migration for a specific target version
  static Migration? getMigration(int targetVersion) {
    return _migrations[targetVersion];
  }

  /// Get all migrations between two versions
  static List<Migration> getMigrationsBetween(int from, int to) {
    final migrations = <Migration>[];
    for (int version = from + 1; version <= to; version++) {
      final migration = _migrations[version];
      if (migration != null) {
        migrations.add(migration);
      }
    }
    return migrations;
  }

  /// Create the migration strategy for Drift
  ///
  /// This is the main entry point for database migration.
  /// It handles:
  /// - Fresh database creation
  /// - Sequential upgrades from any version
  /// - Migration verification
  /// - Audit logging
  static MigrationStrategy create({
    required GeneratedDatabase database,
    bool createBackup = true,
    bool verifyMigrations = true,
    void Function(MigrationResult)? onMigrationComplete,
  }) {
    return MigrationStrategy(
      onCreate: (Migrator m) async {
        AppLogger.i(
          'Creating new database with schema v$currentSchemaVersion',
          tag: 'Migration',
        );
        await m.createAll();

        // Log initial creation
        await _logMigrationHistory(
          database,
          fromVersion: 0,
          toVersion: currentSchemaVersion,
          status: MigrationStatus.completed,
          durationMs: 0,
        );
      },
      onUpgrade: (Migrator m, int from, int to) async {
        AppLogger.i(
          'Upgrading database from v$from to v$to',
          tag: 'Migration',
        );

        final stopwatch = Stopwatch()..start();
        String? backupPath;

        try {
          // Create backup if enabled
          if (createBackup) {
            backupPath = await _createBackup(database);
            AppLogger.i(
              'Backup created at: $backupPath',
              tag: 'Migration',
            );
          }

          // Execute legacy migrations (v1-v4)
          await _executeLegacyMigrations(m, database, from, to);

          // Execute new modular migrations (v5+)
          await _executeModularMigrations(
            m,
            database,
            from,
            to,
            verifyMigrations: verifyMigrations,
          );

          stopwatch.stop();

          // Log successful migration
          await _logMigrationHistory(
            database,
            fromVersion: from,
            toVersion: to,
            status: MigrationStatus.completed,
            durationMs: stopwatch.elapsedMilliseconds,
            backupPath: backupPath,
          );

          final result = MigrationResult.success(
            targetVersion: to,
            fromVersion: from,
            duration: stopwatch.elapsed,
            backupPath: backupPath,
          );

          AppLogger.i(
            'Migration completed: $result',
            tag: 'Migration',
          );

          onMigrationComplete?.call(result);
        } catch (e, stackTrace) {
          stopwatch.stop();

          // Log failed migration
          await _logMigrationHistory(
            database,
            fromVersion: from,
            toVersion: to,
            status: MigrationStatus.failed,
            durationMs: stopwatch.elapsedMilliseconds,
            errorMessage: e.toString(),
            backupPath: backupPath,
          );

          final result = MigrationResult.failure(
            targetVersion: to,
            fromVersion: from,
            duration: stopwatch.elapsed,
            error: e.toString(),
            stackTrace: stackTrace,
            backupPath: backupPath,
          );

          AppLogger.e(
            'Migration failed: $result',
            tag: 'Migration',
            error: e,
            stackTrace: stackTrace,
          );

          onMigrationComplete?.call(result);
          rethrow;
        }
      },
      beforeOpen: (details) async {
        // Enable foreign keys
        await database.customStatement('PRAGMA foreign_keys = ON');

        AppLogger.d(
          'Database opened: v${details.versionNow}, '
          'wasCreated: ${details.wasCreated}, '
          'hadUpgrade: ${details.hadUpgrade}',
          tag: 'Migration',
        );
      },
    );
  }

  /// Execute legacy migrations (v1-v4)
  ///
  /// These are the original inline migrations from the database.dart file.
  /// They are preserved for backward compatibility.
  static Future<void> _executeLegacyMigrations(
    Migrator m,
    GeneratedDatabase db,
    int from,
    int to,
  ) async {
    // Only execute if migrating from versions < 5
    if (from >= 4) return;

    if (from < 2 && to >= 2) {
      AppLogger.i('Executing legacy migration v1 -> v2', tag: 'Migration');
      // Migration from v1 to v2: recreate fields table with GIS columns
      // Note: This deletes existing fields data
      await _safeDeleteTable(m, db, 'fields');
    }

    if (from < 3 && to >= 3) {
      AppLogger.i('Executing legacy migration v2 -> v3', tag: 'Migration');
      // Migration to v3: Add ETag support + SyncEvents
      await _safeAddColumn(db, 'fields', 'etag', 'TEXT');
      await _safeAddColumn(db, 'fields', 'server_updated_at', 'TEXT');
    }

    if (from < 4 && to >= 4) {
      AppLogger.i('Executing legacy migration v3 -> v4', tag: 'Migration');
      // Migration to v4: Unified Outbox schema
      // Note: This deletes existing outbox data
      await _safeDeleteTable(m, db, 'outbox');
    }
  }

  /// Execute modular migrations (v5+)
  static Future<void> _executeModularMigrations(
    Migrator m,
    GeneratedDatabase db,
    int from,
    int to, {
    bool verifyMigrations = true,
  }) async {
    final migrations = getMigrationsBetween(from, to);

    for (final migration in migrations) {
      AppLogger.i(
        'Executing migration: ${migration.description}',
        tag: 'Migration',
      );

      // Pre-check
      final canProceed = await migration.preCheck(m, db);
      if (!canProceed) {
        throw MigrationException(
          'Pre-check failed for migration v${migration.targetVersion}',
          migration.targetVersion,
        );
      }

      // Execute migration
      await migration.upgrade(m, db);

      // Verify migration
      if (verifyMigrations) {
        final verificationResult = await migration.verify(db);
        if (!verificationResult.passed) {
          throw MigrationException(
            'Verification failed: ${verificationResult.message}',
            migration.targetVersion,
            issues: verificationResult.issues,
          );
        }
        AppLogger.i(
          'Migration v${migration.targetVersion} verified: ${verificationResult.message}',
          tag: 'Migration',
        );
      }
    }
  }

  /// Create a backup of the database
  static Future<String> _createBackup(GeneratedDatabase db) async {
    final appDir = await getApplicationDocumentsDirectory();
    final timestamp = DateTime.now().toIso8601String().replaceAll(':', '-');
    final backupName = 'sahool_backup_$timestamp.db';
    final backupPath = p.join(appDir.path, 'backups', backupName);

    // Ensure backup directory exists
    final backupDir = Directory(p.join(appDir.path, 'backups'));
    if (!await backupDir.exists()) {
      await backupDir.create(recursive: true);
    }

    // Create backup using SQLite backup API
    await db.customStatement('VACUUM INTO ?', [backupPath]);

    return backupPath;
  }

  /// Regex for valid SQL identifiers (alphanumeric and underscores only).
  /// Prevents SQL injection through table or column names.
  static final _validIdentifier = RegExp(r'^[a-zA-Z_][a-zA-Z0-9_]*$');

  /// Validate that a SQL identifier (table/column name) is safe to use
  /// in string-interpolated SQL statements.
  static void _validateIdentifier(String name, String kind) {
    if (!_validIdentifier.hasMatch(name)) {
      throw MigrationException(
        'Invalid $kind name "$name": must contain only alphanumeric '
        'characters and underscores, and must start with a letter or underscore.',
        -1,
      );
    }
  }

  /// Safely delete a table if it exists
  static Future<void> _safeDeleteTable(
    Migrator m,
    GeneratedDatabase db,
    String tableName,
  ) async {
    _validateIdentifier(tableName, 'table');
    try {
      final exists = await db.customSelect(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        variables: [Variable.withString(tableName)],
      ).get();

      if (exists.isNotEmpty) {
        await db.customStatement('DROP TABLE IF EXISTS $tableName');
        AppLogger.d('Dropped table: $tableName', tag: 'Migration');
      }
    } catch (e) {
      AppLogger.w(
        'Could not drop table $tableName: $e',
        tag: 'Migration',
      );
    }
  }

  /// Safely add a column if it doesn't exist
  static Future<void> _safeAddColumn(
    GeneratedDatabase db,
    String tableName,
    String columnName,
    String columnType,
  ) async {
    _validateIdentifier(tableName, 'table');
    _validateIdentifier(columnName, 'column');
    _validateIdentifier(columnType, 'column type');
    try {
      // Check if column exists
      final columns = await db.customSelect(
        'PRAGMA table_info($tableName)',
      ).get();

      final columnExists = columns.any(
        (row) => row.read<String>('name') == columnName,
      );

      if (!columnExists) {
        await db.customStatement(
          'ALTER TABLE $tableName ADD COLUMN $columnName $columnType',
        );
        AppLogger.d(
          'Added column $columnName to $tableName',
          tag: 'Migration',
        );
      }
    } catch (e) {
      AppLogger.w(
        'Could not add column $columnName to $tableName: $e',
        tag: 'Migration',
      );
    }
  }

  /// Log migration to history table
  static Future<void> _logMigrationHistory(
    GeneratedDatabase db,
    {
    required int fromVersion,
    required int toVersion,
    required MigrationStatus status,
    required int durationMs,
    String? errorMessage,
    String? backupPath,
  }) async {
    try {
      // Check if migration_history table exists
      final tableExists = await db.customSelect(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='migration_history'",
      ).get();

      if (tableExists.isEmpty) {
        // Create migration_history table if it doesn't exist
        await db.customStatement('''
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

        await db.customStatement('''
          CREATE INDEX IF NOT EXISTS migration_history_version_idx
          ON migration_history (version)
        ''');
      }

      // Insert migration record
      await db.customStatement(
        '''
        INSERT INTO migration_history (
          version, from_version, started_at, completed_at, status,
          error_message, duration_ms, backup_created, backup_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        [
          Variable.withInt(toVersion),
          Variable.withInt(fromVersion),
          Variable.withString(DateTime.now().toIso8601String()),
          status == MigrationStatus.completed
              ? Variable.withString(DateTime.now().toIso8601String())
              : const CustomExpression<String>('NULL'),
          Variable.withString(status.value),
          errorMessage != null ? Variable.withString(errorMessage) : const CustomExpression<String>('NULL'),
          Variable.withInt(durationMs),
          Variable.withBool(backupPath != null),
          backupPath != null ? Variable.withString(backupPath) : const CustomExpression<String>('NULL'),
        ],
      );
    } catch (e) {
      // Don't fail the migration if logging fails
      AppLogger.w(
        'Could not log migration history: $e',
        tag: 'Migration',
      );
    }
  }

  /// Attempt to rollback to a previous version
  ///
  /// Note: SQLite has limitations on schema changes, so rollback
  /// may require restoring from backup.
  static Future<MigrationResult> attemptRollback(
    GeneratedDatabase db,
    int targetVersion,
    String? backupPath,
  ) async {
    final stopwatch = Stopwatch()..start();

    try {
      // Get current version
      final currentVersion = await _getCurrentVersion(db);

      if (targetVersion >= currentVersion) {
        throw MigrationException(
          'Cannot rollback to v$targetVersion from v$currentVersion',
          targetVersion,
        );
      }

      // Try to use migration rollback
      for (int v = currentVersion; v > targetVersion; v--) {
        final migration = _migrations[v];
        if (migration != null && migration.supportsRollback) {
          AppLogger.i(
            'Rolling back migration v$v',
            tag: 'Migration',
          );
          await migration.rollback(
            Migrator(db),
            db,
          );
        } else if (backupPath != null) {
          // Migration doesn't support rollback, restore from backup
          AppLogger.i(
            'Migration v$v does not support rollback, restoring from backup',
            tag: 'Migration',
          );
          // Note: Actual backup restore would need to close and replace the database file
          throw MigrationException(
            'Rollback requires database restore from backup: $backupPath',
            targetVersion,
          );
        } else {
          throw MigrationException(
            'Cannot rollback migration v$v (no rollback support and no backup)',
            targetVersion,
          );
        }
      }

      stopwatch.stop();
      return MigrationResult.success(
        targetVersion: targetVersion,
        fromVersion: currentVersion,
        duration: stopwatch.elapsed,
      );
    } catch (e, stackTrace) {
      stopwatch.stop();
      return MigrationResult.failure(
        targetVersion: targetVersion,
        fromVersion: currentSchemaVersion,
        duration: stopwatch.elapsed,
        error: e.toString(),
        stackTrace: stackTrace,
        backupPath: backupPath,
      );
    }
  }

  /// Get current database version
  static Future<int> _getCurrentVersion(GeneratedDatabase db) async {
    final result = await db.customSelect('PRAGMA user_version').getSingle();
    return result.read<int>('user_version');
  }

  /// List available backups
  static Future<List<BackupInfo>> listBackups() async {
    final appDir = await getApplicationDocumentsDirectory();
    final backupDir = Directory(p.join(appDir.path, 'backups'));

    if (!await backupDir.exists()) {
      return [];
    }

    final backups = <BackupInfo>[];
    await for (final entity in backupDir.list()) {
      if (entity is File && entity.path.endsWith('.db')) {
        final stat = await entity.stat();
        backups.add(BackupInfo(
          path: entity.path,
          createdAt: stat.modified,
          sizeBytes: stat.size,
        ));
      }
    }

    backups.sort((a, b) => b.createdAt.compareTo(a.createdAt));
    return backups;
  }

  /// Delete old backups, keeping only the most recent [keepCount]
  static Future<int> cleanupOldBackups({int keepCount = 5}) async {
    final backups = await listBackups();

    if (backups.length <= keepCount) {
      return 0;
    }

    int deleted = 0;
    for (int i = keepCount; i < backups.length; i++) {
      try {
        await File(backups[i].path).delete();
        deleted++;
        AppLogger.d(
          'Deleted old backup: ${backups[i].path}',
          tag: 'Migration',
        );
      } catch (e) {
        AppLogger.w(
          'Could not delete backup ${backups[i].path}: $e',
          tag: 'Migration',
        );
      }
    }

    return deleted;
  }
}

/// Exception thrown during migration
class MigrationException implements Exception {
  final String message;
  final int targetVersion;
  final List<String> issues;

  MigrationException(this.message, this.targetVersion, {this.issues = const []});

  @override
  String toString() => 'MigrationException(v$targetVersion): $message';
}

/// Information about a database backup
class BackupInfo {
  final String path;
  final DateTime createdAt;
  final int sizeBytes;

  BackupInfo({
    required this.path,
    required this.createdAt,
    required this.sizeBytes,
  });

  String get filename => p.basename(path);

  String get sizeFormatted {
    if (sizeBytes < 1024) return '$sizeBytes B';
    if (sizeBytes < 1024 * 1024) return '${(sizeBytes / 1024).toStringAsFixed(1)} KB';
    return '${(sizeBytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }

  @override
  String toString() => 'BackupInfo($filename, $sizeFormatted, $createdAt)';
}
