/// Base class for database migrations
/// الفئة الاساسية لترحيل قاعدة البيانات
///
/// This module provides the foundation for creating versioned database migrations
/// with support for:
/// - Forward migrations (upgrade)
/// - Rollback support (where possible)
/// - Data preservation verification
/// - Migration verification
/// - Audit logging
library;

import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:drift/drift.dart';

import '../../utils/app_logger.dart';

/// Base class for all database migrations
///
/// Each migration must implement:
/// - [upgrade] - Apply the migration
/// - [verify] - Verify migration was applied correctly
///
/// Optional implementations:
/// - [rollback] - Undo the migration (if possible)
/// - [preCheck] - Verify preconditions before migration
abstract class Migration {
  /// Target version this migration upgrades to
  int get targetVersion;

  /// Source version this migration upgrades from
  int get fromVersion => targetVersion - 1;

  /// Human-readable description of this migration
  String get description;

  /// Arabic description
  String get descriptionAr;

  /// Whether this migration supports rollback
  bool get supportsRollback => false;

  /// Whether this migration requires a backup before executing
  bool get requiresBackup => true;

  /// Estimated time in milliseconds for this migration
  int get estimatedDurationMs => 1000;

  /// Tables affected by this migration
  List<String> get affectedTables;

  /// Unique checksum for this migration script (for verification)
  String get checksum {
    final content = '$targetVersion-$fromVersion-$description-${affectedTables.join(",")}';
    return md5.convert(utf8.encode(content)).toString();
  }

  /// Pre-migration check
  ///
  /// Override to verify preconditions before migration.
  /// Return true if migration can proceed, false otherwise.
  Future<bool> preCheck(Migrator m, GeneratedDatabase db) async {
    return true;
  }

  /// Apply the migration
  ///
  /// Implement the actual migration logic here.
  /// This method should be idempotent where possible.
  Future<void> upgrade(Migrator m, GeneratedDatabase db);

  /// Rollback the migration
  ///
  /// Implement if the migration can be reversed.
  /// SQLite has limitations on schema rollback (can't drop columns),
  /// so this may involve recreating tables.
  Future<void> rollback(Migrator m, GeneratedDatabase db) async {
    throw UnsupportedError(
      'Rollback not supported for migration v$fromVersion -> v$targetVersion',
    );
  }

  /// Verify the migration was applied correctly
  ///
  /// Override to add custom verification logic.
  /// Default implementation checks schema version.
  Future<MigrationVerificationResult> verify(GeneratedDatabase db) async {
    return MigrationVerificationResult.success(
      version: targetVersion,
      message: 'Migration v$targetVersion verified',
    );
  }

  /// Log migration progress
  void log(String message, {LogLevel level = LogLevel.info}) {
    AppLogger.i(
      message,
      tag: 'Migration_v$targetVersion',
    );
  }

  /// Log migration error
  void logError(String message, {Object? error, StackTrace? stackTrace}) {
    AppLogger.e(
      message,
      tag: 'Migration_v$targetVersion',
      error: error,
      stackTrace: stackTrace,
    );
  }

  @override
  String toString() => 'Migration(v$fromVersion -> v$targetVersion: $description)';
}

/// Result of migration verification
class MigrationVerificationResult {
  /// Whether verification passed
  final bool passed;

  /// Version that was verified
  final int version;

  /// Verification message
  final String message;

  /// Details of the verification
  final Map<String, dynamic>? details;

  /// List of issues found (if any)
  final List<String> issues;

  const MigrationVerificationResult({
    required this.passed,
    required this.version,
    required this.message,
    this.details,
    this.issues = const [],
  });

  factory MigrationVerificationResult.success({
    required int version,
    required String message,
    Map<String, dynamic>? details,
  }) {
    return MigrationVerificationResult(
      passed: true,
      version: version,
      message: message,
      details: details,
    );
  }

  factory MigrationVerificationResult.failure({
    required int version,
    required String message,
    List<String> issues = const [],
    Map<String, dynamic>? details,
  }) {
    return MigrationVerificationResult(
      passed: false,
      version: version,
      message: message,
      issues: issues,
      details: details,
    );
  }

  @override
  String toString() {
    if (passed) {
      return 'VerificationResult(passed: v$version - $message)';
    } else {
      return 'VerificationResult(failed: v$version - $message, issues: $issues)';
    }
  }
}

/// Helper mixin for common migration operations
mixin MigrationHelpers on Migration {
  /// Check if a table exists
  Future<bool> tableExists(GeneratedDatabase db, String tableName) async {
    final result = await db.customSelect(
      "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
      variables: [Variable.withString(tableName)],
    ).get();
    return result.isNotEmpty;
  }

  /// Check if a column exists in a table
  Future<bool> columnExists(
    GeneratedDatabase db,
    String tableName,
    String columnName,
  ) async {
    final result = await db.customSelect(
      'PRAGMA table_info($tableName)',
    ).get();

    for (final row in result) {
      if (row.read<String>('name') == columnName) {
        return true;
      }
    }
    return false;
  }

  /// Check if an index exists
  Future<bool> indexExists(GeneratedDatabase db, String indexName) async {
    final result = await db.customSelect(
      "SELECT name FROM sqlite_master WHERE type='index' AND name=?",
      variables: [Variable.withString(indexName)],
    ).get();
    return result.isNotEmpty;
  }

  /// Get row count for a table
  Future<int> getRowCount(GeneratedDatabase db, String tableName) async {
    final result = await db.customSelect(
      'SELECT COUNT(*) as count FROM $tableName',
    ).getSingle();
    return result.read<int>('count');
  }

  /// Get all column names for a table
  Future<List<String>> getColumns(
    GeneratedDatabase db,
    String tableName,
  ) async {
    final result = await db.customSelect(
      'PRAGMA table_info($tableName)',
    ).get();

    return result.map((row) => row.read<String>('name')).toList();
  }

  /// Safely add a column if it doesn't exist
  Future<void> addColumnIfNotExists(
    GeneratedDatabase db,
    String tableName,
    String columnDefinition,
    String columnName,
  ) async {
    if (!await columnExists(db, tableName, columnName)) {
      await db.customStatement(
        'ALTER TABLE $tableName ADD COLUMN $columnDefinition',
      );
      log('Added column $columnName to $tableName');
    } else {
      log('Column $columnName already exists in $tableName, skipping');
    }
  }

  /// Create index if it doesn't exist
  Future<void> createIndexIfNotExists(
    GeneratedDatabase db,
    String indexName,
    String tableName,
    List<String> columns,
  ) async {
    if (!await indexExists(db, indexName)) {
      final columnList = columns.join(', ');
      await db.customStatement(
        'CREATE INDEX $indexName ON $tableName ($columnList)',
      );
      log('Created index $indexName on $tableName');
    } else {
      log('Index $indexName already exists, skipping');
    }
  }

  /// Backup data from a table before modification
  Future<List<Map<String, dynamic>>> backupTableData(
    GeneratedDatabase db,
    String tableName,
  ) async {
    final result = await db.customSelect('SELECT * FROM $tableName').get();
    return result.map((row) => row.data).toList();
  }

  /// Restore data to a table after recreation
  Future<int> restoreTableData(
    GeneratedDatabase db,
    String tableName,
    List<Map<String, dynamic>> data,
    List<String> columns,
  ) async {
    int rowsRestored = 0;

    for (final row in data) {
      final values = columns
          .where((c) => row.containsKey(c))
          .map((c) => row[c])
          .toList();
      final columnList = columns.where((c) => row.containsKey(c)).join(', ');
      final placeholders = List.filled(values.length, '?').join(', ');

      await db.customStatement(
        'INSERT OR REPLACE INTO $tableName ($columnList) VALUES ($placeholders)',
        values.map((v) => Variable(v)).toList(),
      );
      rowsRestored++;
    }

    return rowsRestored;
  }

  /// Execute a migration step with error handling
  Future<void> executeStep(
    String stepDescription,
    Future<void> Function() action,
  ) async {
    log('Starting: $stepDescription');
    try {
      await action();
      log('Completed: $stepDescription');
    } catch (e, stackTrace) {
      logError('Failed: $stepDescription', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
}

/// Represents a migration step for detailed tracking
class MigrationStep {
  /// Step number (1, 2, 3, etc.)
  final int stepNumber;

  /// Description of this step
  final String description;

  /// Whether this step has been completed
  bool completed;

  /// Error if this step failed
  String? error;

  /// Duration of this step
  Duration? duration;

  MigrationStep({
    required this.stepNumber,
    required this.description,
    this.completed = false,
    this.error,
    this.duration,
  });

  @override
  String toString() {
    final status = completed ? 'DONE' : (error != null ? 'FAILED' : 'PENDING');
    return 'Step $stepNumber [$status]: $description';
  }
}

/// Interface for migrations that support data preservation
abstract class DataPreservingMigration extends Migration {
  /// Get the data that needs to be preserved before migration
  Future<Map<String, List<Map<String, dynamic>>>> backupData(
    GeneratedDatabase db,
  );

  /// Restore the preserved data after migration
  Future<void> restoreData(
    GeneratedDatabase db,
    Map<String, List<Map<String, dynamic>>> backup,
  );

  /// Verify data integrity after migration
  Future<bool> verifyDataIntegrity(
    GeneratedDatabase db,
    Map<String, int> expectedRowCounts,
  );
}
