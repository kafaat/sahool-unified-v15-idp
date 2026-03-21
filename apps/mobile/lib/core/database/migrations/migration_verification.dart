/// Migration Verification Utilities
/// ادوات التحقق من الترحيل
///
/// This module provides utilities for verifying database migrations:
/// - Schema verification
/// - Data integrity checks
/// - Index verification
/// - Foreign key validation
library;

import 'package:drift/drift.dart';

import '../schema_version.dart';
import '../../utils/app_logger.dart';

/// Database verification utilities
class MigrationVerifier {
  final GeneratedDatabase _db;

  MigrationVerifier(this._db);

  /// Run full verification suite
  Future<DatabaseVerificationReport> runFullVerification() async {
    AppLogger.i('Starting full database verification', tag: 'MigrationVerifier');

    final stopwatch = Stopwatch()..start();
    final issues = <VerificationIssue>[];

    // Verify schema version
    final schemaResult = await verifySchemaVersion();
    issues.addAll(schemaResult.issues);

    // Verify all expected tables exist
    final tablesResult = await verifyTables();
    issues.addAll(tablesResult.issues);

    // Verify indices
    final indicesResult = await verifyIndices();
    issues.addAll(indicesResult.issues);

    // Verify foreign keys
    final fkResult = await verifyForeignKeys();
    issues.addAll(fkResult.issues);

    // Verify data integrity
    final dataResult = await verifyDataIntegrity();
    issues.addAll(dataResult.issues);

    stopwatch.stop();

    final report = DatabaseVerificationReport(
      passed: issues.where((i) => i.severity == IssueSeverity.error).isEmpty,
      schemaVersion: await _getSchemaVersion(),
      verificationTime: stopwatch.elapsed,
      issues: issues,
    );

    if (report.passed) {
      AppLogger.i(
        'Database verification passed (${issues.length} warnings)',
        tag: 'MigrationVerifier',
      );
    } else {
      AppLogger.e(
        'Database verification failed with ${report.errorCount} errors',
        tag: 'MigrationVerifier',
      );
    }

    return report;
  }

  /// Verify schema version matches expected
  Future<VerificationResult> verifySchemaVersion() async {
    final issues = <VerificationIssue>[];

    try {
      final version = await _getSchemaVersion();

      if (version < minimumSupportedVersion) {
        issues.add(VerificationIssue(
          category: 'Schema',
          message: 'Schema version $version is below minimum supported ($minimumSupportedVersion)',
          severity: IssueSeverity.error,
        ));
      } else if (version > currentSchemaVersion) {
        issues.add(VerificationIssue(
          category: 'Schema',
          message: 'Schema version $version is newer than expected ($currentSchemaVersion)',
          severity: IssueSeverity.warning,
        ));
      }
    } catch (e) {
      issues.add(VerificationIssue(
        category: 'Schema',
        message: 'Failed to read schema version: $e',
        severity: IssueSeverity.error,
      ));
    }

    return VerificationResult(
      passed: issues.isEmpty,
      issues: issues,
    );
  }

  /// Verify all expected tables exist with correct structure
  Future<VerificationResult> verifyTables() async {
    final issues = <VerificationIssue>[];

    // Define expected tables and their required columns
    final expectedTables = {
      'tasks': ['id', 'tenant_id', 'field_id', 'title', 'status', 'created_at', 'updated_at', 'synced'],
      'outbox': ['id', 'tenant_id', 'entity_type', 'entity_id', 'api_endpoint', 'method', 'payload'],
      'fields': ['id', 'tenant_id', 'name', 'boundary', 'area_hectares', 'synced', 'created_at', 'updated_at'],
      'sync_logs': ['id', 'type', 'status', 'timestamp'],
      'sync_events': ['id', 'tenant_id', 'type', 'message', 'is_read', 'created_at'],
    };

    for (final entry in expectedTables.entries) {
      final tableName = entry.key;
      final requiredColumns = entry.value;

      // Check if table exists
      final tableExists = await _tableExists(tableName);
      if (!tableExists) {
        issues.add(VerificationIssue(
          category: 'Tables',
          message: 'Missing required table: $tableName',
          severity: IssueSeverity.error,
        ));
        continue;
      }

      // Check columns
      final columns = await _getTableColumns(tableName);
      for (final column in requiredColumns) {
        if (!columns.contains(column)) {
          issues.add(VerificationIssue(
            category: 'Tables',
            message: 'Table $tableName missing required column: $column',
            severity: IssueSeverity.error,
          ));
        }
      }
    }

    return VerificationResult(
      passed: issues.where((i) => i.severity == IssueSeverity.error).isEmpty,
      issues: issues,
    );
  }

  /// Verify indices exist
  Future<VerificationResult> verifyIndices() async {
    final issues = <VerificationIssue>[];

    // Get all indices
    final result = await _db.customSelect(
      "SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'",
    ).get();

    final indexNames = result.map((r) => r.read<String>('name')).toSet();

    // Define expected indices (critical ones)
    final expectedIndices = [
      'tasks_tenant_idx',
      'tasks_field_idx',
      'tasks_status_idx',
      'outbox_tenant_idx',
      'outbox_synced_idx',
      'fields_tenant_idx',
      'fields_synced_idx',
    ];

    for (final indexName in expectedIndices) {
      if (!indexNames.contains(indexName)) {
        issues.add(VerificationIssue(
          category: 'Indices',
          message: 'Missing expected index: $indexName',
          severity: IssueSeverity.warning,
        ));
      }
    }

    return VerificationResult(
      passed: true, // Missing indices are warnings, not errors
      issues: issues,
    );
  }

  /// Verify foreign key constraints
  Future<VerificationResult> verifyForeignKeys() async {
    final issues = <VerificationIssue>[];

    try {
      // Check for foreign key violations
      final violations = await _db.customSelect(
        'PRAGMA foreign_key_check',
      ).get();

      for (final row in violations) {
        issues.add(VerificationIssue(
          category: 'ForeignKeys',
          message: 'Foreign key violation in table ${row.read<String?>('table')}',
          severity: IssueSeverity.error,
          details: row.data,
        ));
      }
    } catch (e) {
      // Foreign key check might not be available
      AppLogger.w(
        'Could not check foreign keys: $e',
        tag: 'MigrationVerifier',
      );
    }

    return VerificationResult(
      passed: issues.isEmpty,
      issues: issues,
    );
  }

  /// Verify data integrity
  Future<VerificationResult> verifyDataIntegrity() async {
    final issues = <VerificationIssue>[];

    try {
      // Run SQLite integrity check
      final result = await _db.customSelect('PRAGMA integrity_check').get();

      for (final row in result) {
        final check = row.read<String?>('integrity_check');
        if (check != null && check != 'ok') {
          issues.add(VerificationIssue(
            category: 'DataIntegrity',
            message: 'Integrity check failed: $check',
            severity: IssueSeverity.error,
          ));
        }
      }
    } catch (e) {
      issues.add(VerificationIssue(
        category: 'DataIntegrity',
        message: 'Failed to run integrity check: $e',
        severity: IssueSeverity.warning,
      ));
    }

    // Check for orphaned data
    await _checkOrphanedOutboxItems(issues);

    return VerificationResult(
      passed: issues.where((i) => i.severity == IssueSeverity.error).isEmpty,
      issues: issues,
    );
  }

  /// Check for orphaned outbox items
  Future<void> _checkOrphanedOutboxItems(List<VerificationIssue> issues) async {
    try {
      // Check for outbox items referencing non-existent fields
      final orphaned = await _db.customSelect('''
        SELECT COUNT(*) as count FROM outbox o
        WHERE o.entity_type = 'field'
        AND NOT EXISTS (SELECT 1 FROM fields f WHERE f.id = o.entity_id)
        AND o.is_synced = 0
      ''').getSingle();

      final count = orphaned.read<int>('count');
      if (count > 0) {
        issues.add(VerificationIssue(
          category: 'DataIntegrity',
          message: 'Found $count orphaned outbox items referencing deleted fields',
          severity: IssueSeverity.warning,
        ));
      }
    } catch (e) {
      // Query might fail if tables don't exist yet
      AppLogger.d(
        'Could not check orphaned items: $e',
        tag: 'MigrationVerifier',
      );
    }
  }

  /// Get database statistics
  Future<DatabaseStats> getStats() async {
    final stats = DatabaseStats();

    // Get table counts
    final tables = ['tasks', 'outbox', 'fields', 'sync_logs', 'sync_events'];
    for (final table in tables) {
      try {
        final result = await _db.customSelect(
          'SELECT COUNT(*) as count FROM $table',
        ).getSingle();
        stats.tableCounts[table] = result.read<int>('count');
      } catch (e) {
        stats.tableCounts[table] = -1;
      }
    }

    // Get database file size (approximate via page count)
    try {
      final pageCount = await _db.customSelect('PRAGMA page_count').getSingle();
      final pageSize = await _db.customSelect('PRAGMA page_size').getSingle();
      stats.estimatedSizeBytes =
          pageCount.read<int>('page_count') * pageSize.read<int>('page_size');
    } catch (e) {
      AppLogger.w('Could not get database size: $e', tag: 'MigrationVerifier');
    }

    // Get schema version
    stats.schemaVersion = await _getSchemaVersion();

    return stats;
  }

  /// Get current schema version
  Future<int> _getSchemaVersion() async {
    final result = await _db.customSelect('PRAGMA user_version').getSingle();
    return result.read<int>('user_version');
  }

  /// Check if a table exists
  Future<bool> _tableExists(String tableName) async {
    final result = await _db.customSelect(
      "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
      variables: [Variable.withString(tableName)],
    ).get();
    return result.isNotEmpty;
  }

  /// Get column names for a table
  Future<List<String>> _getTableColumns(String tableName) async {
    final result = await _db.customSelect(
      'PRAGMA table_info($tableName)',
    ).get();
    return result.map((row) => row.read<String>('name')).toList();
  }
}

/// Result of a verification check
class VerificationResult {
  final bool passed;
  final List<VerificationIssue> issues;

  VerificationResult({
    required this.passed,
    required this.issues,
  });
}

/// A verification issue found during checks
class VerificationIssue {
  final String category;
  final String message;
  final IssueSeverity severity;
  final Map<String, dynamic>? details;

  VerificationIssue({
    required this.category,
    required this.message,
    required this.severity,
    this.details,
  });

  @override
  String toString() => '[$severity] $category: $message';
}

/// Severity levels for verification issues
enum IssueSeverity {
  info,
  warning,
  error;

  @override
  String toString() {
    switch (this) {
      case IssueSeverity.info:
        return 'INFO';
      case IssueSeverity.warning:
        return 'WARNING';
      case IssueSeverity.error:
        return 'ERROR';
    }
  }
}

/// Full database verification report
class DatabaseVerificationReport {
  final bool passed;
  final int schemaVersion;
  final Duration verificationTime;
  final List<VerificationIssue> issues;

  DatabaseVerificationReport({
    required this.passed,
    required this.schemaVersion,
    required this.verificationTime,
    required this.issues,
  });

  int get errorCount => issues.where((i) => i.severity == IssueSeverity.error).length;
  int get warningCount => issues.where((i) => i.severity == IssueSeverity.warning).length;
  int get infoCount => issues.where((i) => i.severity == IssueSeverity.info).length;

  List<VerificationIssue> get errors =>
      issues.where((i) => i.severity == IssueSeverity.error).toList();
  List<VerificationIssue> get warnings =>
      issues.where((i) => i.severity == IssueSeverity.warning).toList();

  @override
  String toString() {
    final status = passed ? 'PASSED' : 'FAILED';
    return 'DatabaseVerificationReport($status, v$schemaVersion, '
        'errors: $errorCount, warnings: $warningCount, '
        'time: ${verificationTime.inMilliseconds}ms)';
  }

  /// Generate a detailed report string
  String toDetailedReport() {
    final buffer = StringBuffer();
    buffer.writeln('═══════════════════════════════════════════════════════════');
    buffer.writeln('  DATABASE VERIFICATION REPORT');
    buffer.writeln('═══════════════════════════════════════════════════════════');
    buffer.writeln('  Status: ${passed ? "PASSED" : "FAILED"}');
    buffer.writeln('  Schema Version: $schemaVersion');
    buffer.writeln('  Verification Time: ${verificationTime.inMilliseconds}ms');
    buffer.writeln('  Errors: $errorCount | Warnings: $warningCount | Info: $infoCount');
    buffer.writeln('───────────────────────────────────────────────────────────');

    if (issues.isNotEmpty) {
      buffer.writeln('  ISSUES:');
      for (final issue in issues) {
        buffer.writeln('    [${issue.severity}] ${issue.category}: ${issue.message}');
      }
    } else {
      buffer.writeln('  No issues found.');
    }

    buffer.writeln('═══════════════════════════════════════════════════════════');
    return buffer.toString();
  }
}

/// Database statistics
class DatabaseStats {
  final Map<String, int> tableCounts = {};
  int estimatedSizeBytes = 0;
  int schemaVersion = 0;

  String get formattedSize {
    if (estimatedSizeBytes < 1024) return '$estimatedSizeBytes B';
    if (estimatedSizeBytes < 1024 * 1024) {
      return '${(estimatedSizeBytes / 1024).toStringAsFixed(1)} KB';
    }
    return '${(estimatedSizeBytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }

  int get totalRows => tableCounts.values.fold(0, (sum, count) => sum + (count > 0 ? count : 0));

  @override
  String toString() {
    return 'DatabaseStats(v$schemaVersion, size: $formattedSize, '
        'tables: $tableCounts, totalRows: $totalRows)';
  }
}
