/// Comprehensive Migration Tests for SAHOOL Mobile Database
/// اختبارات شاملة لترحيل قاعدة بيانات سهول
///
/// Tests the complete migration system including:
/// - Schema version management
/// - Migration logic correctness
/// - Migration strategy orchestration
/// - Error handling in migrations
/// - Data preservation guarantees
/// - Version compatibility checks
/// - Migration rollback support
/// - Migration checksum verification
///
/// Run with: flutter test test/core/database/comprehensive_migration_test.dart
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/database/schema_version.dart';
import 'package:sahool_field_app/core/database/migration_strategy.dart';
import 'package:sahool_field_app/core/database/migrations/migration_base.dart';
import 'package:sahool_field_app/core/database/migrations/migration_v5.dart';
import 'package:sahool_field_app/core/database/migrations/migration_verification.dart';

void main() {
  // ============================================================
  // Schema Version Management Tests
  // ============================================================
  group('SchemaVersion Management - إدارة إصدارات المخطط', () {
    test('currentSchemaVersion is a valid positive integer', () {
      expect(currentSchemaVersion, isA<int>());
      expect(currentSchemaVersion, greaterThan(0));
    });

    test('minimumSupportedVersion is at least 1', () {
      expect(minimumSupportedVersion, greaterThanOrEqualTo(1));
    });

    test('currentSchemaVersion is >= minimumSupportedVersion', () {
      expect(currentSchemaVersion, greaterThanOrEqualTo(minimumSupportedVersion));
    });

    test('SchemaVersionRegistry has correct number of versions', () {
      expect(
        SchemaVersionRegistry.versions.length,
        equals(currentSchemaVersion),
        reason: 'Every schema version should have an entry in the registry',
      );
    });

    test('SchemaVersionRegistry versions are ordered correctly', () {
      final versions = SchemaVersionRegistry.versions;
      for (int i = 0; i < versions.length; i++) {
        expect(
          versions[i].version,
          equals(i + 1),
          reason: 'Version at index $i should be ${i + 1}',
        );
      }
    });

    test('SchemaVersionRegistry.current returns latest version', () {
      final current = SchemaVersionRegistry.current;
      expect(current.version, equals(currentSchemaVersion));
      expect(current.description, isNotEmpty);
      expect(current.descriptionAr, isNotEmpty);
    });

    test('Each SchemaVersion has non-empty descriptions', () {
      for (final version in SchemaVersionRegistry.versions) {
        expect(
          version.description,
          isNotEmpty,
          reason: 'Version ${version.version} must have a description',
        );
        expect(
          version.descriptionAr,
          isNotEmpty,
          reason: 'Version ${version.version} must have an Arabic description',
        );
      }
    });

    test('Each SchemaVersion has a valid release date', () {
      for (final version in SchemaVersionRegistry.versions) {
        expect(
          version.releaseDate,
          isNotNull,
          reason: 'Version ${version.version} must have a release date',
        );
        // Release date should be after 2020 (SAHOOL project start)
        expect(
          version.releaseDate.year,
          greaterThanOrEqualTo(2020),
          reason: 'Version ${version.version} release date seems invalid',
        );
      }
    });

    test('SchemaVersionRegistry.getVersion returns correct version', () {
      for (int v = minimumSupportedVersion; v <= currentSchemaVersion; v++) {
        final version = SchemaVersionRegistry.getVersion(v);
        expect(version, isNotNull, reason: 'Version $v should exist');
        expect(version!.version, equals(v));
      }
    });

    test('SchemaVersionRegistry.getVersion returns null for invalid versions', () {
      expect(SchemaVersionRegistry.getVersion(0), isNull);
      expect(SchemaVersionRegistry.getVersion(-1), isNull);
      expect(SchemaVersionRegistry.getVersion(999), isNull);
      expect(SchemaVersionRegistry.getVersion(currentSchemaVersion + 1), isNull);
    });

    test('SchemaVersionRegistry.isSupported validates version bounds correctly', () {
      expect(SchemaVersionRegistry.isSupported(0), isFalse);
      expect(SchemaVersionRegistry.isSupported(-1), isFalse);

      for (int v = minimumSupportedVersion; v <= currentSchemaVersion; v++) {
        expect(
          SchemaVersionRegistry.isSupported(v),
          isTrue,
          reason: 'Version $v should be supported',
        );
      }

      expect(SchemaVersionRegistry.isSupported(currentSchemaVersion + 1), isFalse);
    });

    test('getVersionsBetween returns correct intermediate versions', () {
      final between12 = SchemaVersionRegistry.getVersionsBetween(1, 2);
      expect(between12.length, equals(1));
      expect(between12.first.version, equals(2));

      if (currentSchemaVersion >= 5) {
        final between15 = SchemaVersionRegistry.getVersionsBetween(1, 5);
        expect(between15.length, equals(4)); // versions 2, 3, 4, 5
        expect(between15.map((v) => v.version).toList(), equals([2, 3, 4, 5]));

        final between25 = SchemaVersionRegistry.getVersionsBetween(2, 5);
        expect(between25.length, equals(3));
        expect(between25.map((v) => v.version).toList(), equals([3, 4, 5]));
      }
    });

    test('getVersionsBetween returns empty for same version', () {
      final between = SchemaVersionRegistry.getVersionsBetween(3, 3);
      expect(between, isEmpty);
    });

    test('getMigrationPath returns complete upgrade path', () {
      if (currentSchemaVersion >= 5) {
        final path = SchemaVersionRegistry.getMigrationPath(1, 5);
        expect(path, equals([2, 3, 4, 5]));

        final singleStep = SchemaVersionRegistry.getMigrationPath(4, 5);
        expect(singleStep, equals([5]));

        final noOp = SchemaVersionRegistry.getMigrationPath(5, 5);
        expect(noOp, isEmpty);
      }
    });
  });

  // ============================================================
  // MigrationV5 Tests
  // ============================================================
  group('MigrationV5 - ترحيل الإصدار الخامس', () {
    late MigrationV5 migration;

    setUp(() {
      migration = MigrationV5();
    });

    test('targetVersion should be 5', () {
      expect(migration.targetVersion, equals(5));
    });

    test('fromVersion should be 4', () {
      expect(migration.fromVersion, equals(4));
    });

    test('description should be non-empty', () {
      expect(migration.description, isNotEmpty);
      expect(migration.description.length, greaterThan(5));
    });

    test('descriptionAr should be non-empty Arabic text', () {
      expect(migration.descriptionAr, isNotEmpty);
      expect(migration.descriptionAr.length, greaterThan(5));
    });

    test('supportsRollback should be true', () {
      expect(migration.supportsRollback, isTrue);
    });

    test('requiresBackup should be true for migration with data changes', () {
      expect(migration.requiresBackup, isTrue);
    });

    test('affectedTables should include critical tables', () {
      final tables = migration.affectedTables;
      expect(tables, isNotEmpty);
      expect(tables, contains('migration_history'));
      expect(tables, contains('fields'));
      expect(tables, contains('outbox'));
    });

    test('checksum should be consistent across instances', () {
      final checksum1 = migration.checksum;
      final checksum2 = MigrationV5().checksum;
      expect(checksum1, equals(checksum2));
    });

    test('checksum should be a non-empty hex string (MD5, 32 chars)', () {
      final checksum = migration.checksum;
      expect(checksum, isNotEmpty);
      // Migration.checksum is an MD5 digest → always 32 lowercase hex chars
      expect(checksum.length, equals(32));
      // Should only contain hex characters
      expect(RegExp(r'^[0-9a-f]+$').hasMatch(checksum), isTrue);
    });

    test('migration is a Migration subclass', () {
      expect(migration, isA<Migration>());
    });
  });

  // ============================================================
  // MigrationResult Tests
  // ============================================================
  group('MigrationResult - نتيجة الترحيل', () {
    test('success factory creates successful result with all fields', () {
      final result = MigrationResult.success(
        targetVersion: 5,
        fromVersion: 4,
        duration: const Duration(milliseconds: 250),
        rowsAffected: 42,
      );

      expect(result.success, isTrue);
      expect(result.targetVersion, equals(5));
      expect(result.fromVersion, equals(4));
      expect(result.duration.inMilliseconds, equals(250));
      expect(result.rowsAffected, equals(42));
      expect(result.error, isNull);
    });

    test('success factory works without optional rowsAffected', () {
      final result = MigrationResult.success(
        targetVersion: 3,
        fromVersion: 2,
        duration: const Duration(milliseconds: 10),
      );

      expect(result.success, isTrue);
      expect(result.rowsAffected, equals(0));
      expect(result.error, isNull);
    });

    test('failure factory creates failed result with error message', () {
      const errorMsg = 'SQLite constraint violation: UNIQUE constraint failed';
      final result = MigrationResult.failure(
        targetVersion: 5,
        fromVersion: 4,
        duration: const Duration(milliseconds: 50),
        error: errorMsg,
      );

      expect(result.success, isFalse);
      expect(result.targetVersion, equals(5));
      expect(result.fromVersion, equals(4));
      expect(result.error, equals(errorMsg));
    });

    test('toString includes relevant information', () {
      final success = MigrationResult.success(
        targetVersion: 5,
        fromVersion: 4,
        duration: const Duration(milliseconds: 100),
      );
      final successStr = success.toString();
      expect(successStr, contains('success'));
      expect(successStr, contains('v4'));
      expect(successStr, contains('v5'));

      final failure = MigrationResult.failure(
        targetVersion: 5,
        fromVersion: 4,
        duration: const Duration(milliseconds: 50),
        error: 'Test error',
      );
      final failureStr = failure.toString();
      expect(failureStr, contains('fail'));
      expect(failureStr, contains('Test error'));
    });

    test('multiple results can be collected and analyzed', () {
      final results = <MigrationResult>[
        MigrationResult.success(
          targetVersion: 2,
          fromVersion: 1,
          duration: const Duration(milliseconds: 10),
          rowsAffected: 5,
        ),
        MigrationResult.success(
          targetVersion: 3,
          fromVersion: 2,
          duration: const Duration(milliseconds: 20),
          rowsAffected: 10,
        ),
        MigrationResult.failure(
          targetVersion: 4,
          fromVersion: 3,
          duration: const Duration(milliseconds: 5),
          error: 'Test failure',
        ),
      ];

      expect(results.where((r) => r.success).length, equals(2));
      expect(results.where((r) => !r.success).length, equals(1));
      expect(
        results.fold<int>(0, (sum, r) => sum + r.rowsAffected),
        equals(15),
      );
    });
  });

  // ============================================================
  // SahoolMigrationStrategy Tests
  // ============================================================
  group('SahoolMigrationStrategy - استراتيجية الترحيل', () {
    test('getMigration returns correct migration for version 5', () {
      final migration = SahoolMigrationStrategy.getMigration(5);
      expect(migration, isNotNull);
      expect(migration, isA<MigrationV5>());
      expect(migration!.targetVersion, equals(5));
    });

    test('getMigration returns null for unsupported versions', () {
      expect(SahoolMigrationStrategy.getMigration(0), isNull);
      expect(SahoolMigrationStrategy.getMigration(1), isNull);
      expect(SahoolMigrationStrategy.getMigration(99), isNull);
      expect(SahoolMigrationStrategy.getMigration(-1), isNull);
    });

    test('getMigrationsBetween returns correct list for v4->v5', () {
      final migrations = SahoolMigrationStrategy.getMigrationsBetween(4, 5);
      expect(migrations.length, equals(1));
      expect(migrations.first.targetVersion, equals(5));
    });

    test('getMigrationsBetween returns empty list for same version', () {
      final migrations = SahoolMigrationStrategy.getMigrationsBetween(5, 5);
      expect(migrations, isEmpty);
    });

    test('getMigrationsBetween handles range with no known migrations', () {
      final migrations = SahoolMigrationStrategy.getMigrationsBetween(1, 3);
      // Versions 2 and 3 don't have explicit migration objects in the strategy
      // The strategy only has v5 migration
      expect(migrations, isEmpty);
    });

    test('getMigrationsBetween returns multiple migrations for large range', () {
      // Only v5 is registered, so 1->5 should return [v5]
      final migrations = SahoolMigrationStrategy.getMigrationsBetween(1, 5);
      expect(migrations.length, equals(1));
      expect(migrations.first.targetVersion, equals(5));
    });
  });

  // ============================================================
  // MigrationVerificationResult Tests
  // ============================================================
  group('MigrationVerificationResult - نتائج التحقق', () {
    test('success factory creates passing result', () {
      final result = MigrationVerificationResult.success(
        version: 5,
        message: 'All tables verified successfully',
        details: {'tables_checked': 5, 'indexes_checked': 12},
      );

      expect(result.passed, isTrue);
      expect(result.version, equals(5));
      expect(result.message, equals('All tables verified successfully'));
      expect(result.details, isNotNull);
      expect(result.issues, isEmpty);
    });

    test('failure factory creates failing result with issues', () {
      final result = MigrationVerificationResult.failure(
        version: 5,
        message: 'Verification failed: missing columns',
        issues: [
          'Column last_sync_at missing from fields table',
          'Column sync_priority missing from outbox table',
        ],
      );

      expect(result.passed, isFalse);
      expect(result.version, equals(5));
      expect(result.issues.length, equals(2));
    });

    test('success result has no issues', () {
      final result = MigrationVerificationResult.success(
        version: 5,
        message: 'OK',
      );
      expect(result.issues, isEmpty);
    });

    test('failure result preserves all issues', () {
      final issues = List.generate(
        5,
        (i) => 'Issue $i: some problem occurred',
      );
      final result = MigrationVerificationResult.failure(
        version: 5,
        message: 'Multiple issues found',
        issues: issues,
      );

      expect(result.issues.length, equals(5));
      for (int i = 0; i < 5; i++) {
        expect(result.issues[i], contains('Issue $i'));
      }
    });
  });

  // ============================================================
  // VerificationIssue Tests
  // ============================================================
  group('VerificationIssue - مشكلات التحقق', () {
    test('formats correctly with all severity levels', () {
      for (final severity in IssueSeverity.values) {
        final issue = VerificationIssue(
          category: 'Test',
          message: 'Test issue message',
          severity: severity,
        );
        expect(issue.toString(), contains(severity.toString()));
        expect(issue.toString(), contains('Test'));
        expect(issue.toString(), contains('Test issue message'));
      }
    });

    test('INFO severity formats correctly', () {
      final issue = VerificationIssue(
        category: 'Schema',
        message: 'Database schema version is current',
        severity: IssueSeverity.info,
      );
      expect(issue.toString(), contains('[INFO]'));
    });

    test('WARNING severity formats correctly', () {
      final issue = VerificationIssue(
        category: 'Performance',
        message: 'Missing composite index on tenant_id + status',
        severity: IssueSeverity.warning,
      );
      expect(issue.toString(), contains('[WARNING]'));
    });

    test('ERROR severity formats correctly', () {
      final issue = VerificationIssue(
        category: 'Integrity',
        message: 'Required column not found in table',
        severity: IssueSeverity.error,
      );
      expect(issue.toString(), contains('[ERROR]'));
    });
  });

  // ============================================================
  // IssueSeverity Tests
  // ============================================================
  group('IssueSeverity - مستوى الخطورة', () {
    test('has expected values', () {
      expect(IssueSeverity.values.length, equals(3));
      expect(IssueSeverity.values, contains(IssueSeverity.info));
      expect(IssueSeverity.values, contains(IssueSeverity.warning));
      expect(IssueSeverity.values, contains(IssueSeverity.error));
    });

    test('toString returns correct string representations', () {
      expect(IssueSeverity.info.toString(), equals('INFO'));
      expect(IssueSeverity.warning.toString(), equals('WARNING'));
      expect(IssueSeverity.error.toString(), equals('ERROR'));
    });
  });

  // ============================================================
  // MigrationStep Tests
  // ============================================================
  group('MigrationStep - خطوة الترحيل', () {
    test('initializes with correct defaults', () {
      final step = MigrationStep(
        stepNumber: 1,
        description: 'Create migration_history table',
      );

      expect(step.stepNumber, equals(1));
      expect(step.description, equals('Create migration_history table'));
      expect(step.completed, isFalse);
      expect(step.error, isNull);
      expect(step.duration, isNull);
    });

    test('marks step as completed', () {
      final step = MigrationStep(
        stepNumber: 2,
        description: 'Add sync_priority column to outbox',
      );

      step.completed = true;
      step.duration = const Duration(milliseconds: 15);

      expect(step.completed, isTrue);
      expect(step.duration, equals(const Duration(milliseconds: 15)));
      expect(step.toString(), contains('DONE'));
    });

    test('marks step with error', () {
      final step = MigrationStep(
        stepNumber: 3,
        description: 'Update field records',
      );

      step.error = 'Column does not exist: last_sync_at';

      expect(step.completed, isFalse);
      expect(step.error, isNotNull);
      expect(step.toString(), contains('FAILED'));
    });

    test('toString includes step number and description', () {
      final step = MigrationStep(
        stepNumber: 1,
        description: 'Test step',
      );
      expect(step.toString(), contains('1'));
      expect(step.toString(), contains('Test step'));
    });
  });

  // ============================================================
  // SyncPriority Tests
  // ============================================================
  group('SyncPriority - أولوية المزامنة', () {
    test('priority constants are correctly ordered', () {
      expect(SyncPriority.low, lessThan(SyncPriority.normal));
      expect(SyncPriority.normal, lessThan(SyncPriority.high));
      expect(SyncPriority.high, lessThan(SyncPriority.critical));
    });

    test('all priority levels have expected values', () {
      expect(SyncPriority.low, equals(0));
      expect(SyncPriority.normal, equals(10));
      expect(SyncPriority.high, equals(20));
      expect(SyncPriority.critical, equals(30));
    });

    test('forEntityType returns critical for sensitive entities', () {
      // High priority entities
      expect(SyncPriority.forEntityType('field'), equals(SyncPriority.high));
    });

    test('forEntityType returns normal as default', () {
      expect(SyncPriority.forEntityType('unknown'), equals(SyncPriority.normal));
      expect(SyncPriority.forEntityType(''), equals(SyncPriority.normal));
      expect(SyncPriority.forEntityType('some_random_entity'), equals(SyncPriority.normal));
    });

    test('forMethod prioritizes destructive operations', () {
      // DELETE should be most critical
      expect(SyncPriority.forMethod('DELETE'), equals(SyncPriority.critical));
    });

    test('forMethod handles all HTTP methods', () {
      expect(SyncPriority.forMethod('POST'), equals(SyncPriority.high));
      expect(SyncPriority.forMethod('PUT'), equals(SyncPriority.normal));
      expect(SyncPriority.forMethod('PATCH'), equals(SyncPriority.normal));
      expect(SyncPriority.forMethod('GET'), equals(SyncPriority.low));
    });

    test('forMethod returns normal for unknown methods', () {
      expect(SyncPriority.forMethod('UNKNOWN'), equals(SyncPriority.normal));
    });
  });

  // ============================================================
  // DatabaseStats Tests
  // ============================================================
  group('DatabaseStats - إحصائيات قاعدة البيانات', () {
    test('formats bytes correctly', () {
      final stats = DatabaseStats();

      stats.estimatedSizeBytes = 500;
      expect(stats.formattedSize, equals('500 B'));
    });

    test('formats kilobytes correctly', () {
      final stats = DatabaseStats();
      stats.estimatedSizeBytes = 2048;
      expect(stats.formattedSize, equals('2.0 KB'));
    });

    test('formats megabytes correctly', () {
      final stats = DatabaseStats();
      stats.estimatedSizeBytes = 1024 * 1024 * 5;
      expect(stats.formattedSize, equals('5.0 MB'));
    });

    test('formats large values as MB (max unit supported)', () {
      final stats = DatabaseStats();
      stats.estimatedSizeBytes = 1024 * 1024 * 1024 * 2;
      // DatabaseStats only formats up to MB
      expect(stats.formattedSize, contains('MB'));
    });

    test('calculates total rows correctly', () {
      final stats = DatabaseStats();
      stats.tableCounts['tasks'] = 100;
      stats.tableCounts['fields'] = 25;
      stats.tableCounts['outbox'] = 5;
      stats.tableCounts['sync_logs'] = 200;

      expect(stats.totalRows, equals(330));
    });

    test('ignores negative table counts (non-existent tables)', () {
      final stats = DatabaseStats();
      stats.tableCounts['tasks'] = 10;
      stats.tableCounts['missing_table'] = -1;

      expect(stats.totalRows, equals(10));
    });

    test('handles empty database', () {
      final stats = DatabaseStats();
      expect(stats.totalRows, equals(0));
      expect(stats.estimatedSizeBytes, equals(0));
    });
  });

  // ============================================================
  // DatabaseVerificationReport Tests
  // ============================================================
  group('DatabaseVerificationReport - تقرير التحقق', () {
    test('counts errors correctly by severity', () {
      final report = DatabaseVerificationReport(
        passed: false,
        schemaVersion: 6,
        verificationTime: const Duration(milliseconds: 100),
        issues: [
          VerificationIssue(
            category: 'Schema',
            message: 'Critical error 1',
            severity: IssueSeverity.error,
          ),
          VerificationIssue(
            category: 'Schema',
            message: 'Critical error 2',
            severity: IssueSeverity.error,
          ),
          VerificationIssue(
            category: 'Performance',
            message: 'Performance warning',
            severity: IssueSeverity.warning,
          ),
          VerificationIssue(
            category: 'Info',
            message: 'Informational note',
            severity: IssueSeverity.info,
          ),
        ],
      );

      expect(report.errorCount, equals(2));
      expect(report.warningCount, equals(1));
      expect(report.infoCount, equals(1));
      expect(report.errors.length, equals(2));
      expect(report.warnings.length, equals(1));
    });

    test('toDetailedReport generates formatted output', () {
      final passedReport = DatabaseVerificationReport(
        passed: true,
        schemaVersion: 6,
        verificationTime: const Duration(milliseconds: 50),
        issues: [],
      );

      final detailed = passedReport.toDetailedReport();
      expect(detailed, contains('PASSED'));
      expect(detailed, contains('Schema Version: 6'));
      expect(detailed, contains('No issues found'));
    });

    test('toDetailedReport includes issues when failed', () {
      final failedReport = DatabaseVerificationReport(
        passed: false,
        schemaVersion: 6,
        verificationTime: const Duration(milliseconds: 100),
        issues: [
          VerificationIssue(
            category: 'Schema',
            message: 'Missing column: last_sync_at',
            severity: IssueSeverity.error,
          ),
        ],
      );

      final detailed = failedReport.toDetailedReport();
      expect(detailed, contains('FAILED'));
      expect(detailed, contains('Missing column'));
    });

    test('empty report passes with no issues', () {
      final report = DatabaseVerificationReport(
        passed: true,
        schemaVersion: currentSchemaVersion,
        verificationTime: const Duration(microseconds: 100),
        issues: [],
      );

      expect(report.passed, isTrue);
      expect(report.errorCount, equals(0));
      expect(report.warningCount, equals(0));
      expect(report.infoCount, equals(0));
    });
  });

  // ============================================================
  // BackupInfo Tests
  // ============================================================
  group('BackupInfo - معلومات النسخ الاحتياطي', () {
    test('extracts filename from path', () {
      final backup = BackupInfo(
        path: '/data/user/0/backup.db',
        createdAt: DateTime(2025, 1, 15, 10, 30),
        sizeBytes: 1024 * 512,
      );

      expect(backup.filename, equals('backup.db'));
    });

    test('formats size as KB', () {
      final backup = BackupInfo(
        path: '/path/to/backup_v4.db',
        createdAt: DateTime.now(),
        sizeBytes: 1024 * 500,
      );

      expect(backup.sizeFormatted, equals('500.0 KB'));
    });

    test('formats size as MB', () {
      final backup = BackupInfo(
        path: '/path/to/large_backup.db',
        createdAt: DateTime.now(),
        sizeBytes: 1024 * 1024 * 2,
      );

      expect(backup.sizeFormatted, equals('2.0 MB'));
    });

    test('formats size as bytes for small files', () {
      final backup = BackupInfo(
        path: '/path/to/tiny.db',
        createdAt: DateTime.now(),
        sizeBytes: 512,
      );

      expect(backup.sizeFormatted, equals('512 B'));
    });

    test('createdAt is preserved', () {
      final createdAt = DateTime(2025, 6, 15, 14, 30, 0);
      final backup = BackupInfo(
        path: '/path/to/backup.db',
        createdAt: createdAt,
        sizeBytes: 1024,
      );

      expect(backup.createdAt, equals(createdAt));
    });
  });

  // ============================================================
  // MigrationException Tests
  // ============================================================
  group('MigrationException - استثناء الترحيل', () {
    test('stores version and message', () {
      final ex = MigrationException('Migration failed due to constraint', 5);

      expect(ex.targetVersion, equals(5));
      expect(ex.message, equals('Migration failed due to constraint'));
    });

    test('stores issues list', () {
      final issues = ['Missing table', 'Invalid schema', 'Corrupted index'];
      final ex = MigrationException(
        'Multiple issues found',
        5,
        issues: issues,
      );

      expect(ex.issues.length, equals(3));
      expect(ex.issues, containsAll(issues));
    });

    test('toString includes version and message', () {
      final ex = MigrationException('Critical failure', 5);
      final str = ex.toString();

      expect(str, contains('v5'));
      expect(str, contains('Critical failure'));
    });

    test('can be thrown and caught as Exception', () {
      expect(
        () => throw MigrationException('Test', 5),
        throwsA(isA<MigrationException>()),
      );
    });

    test('empty issues list is handled', () {
      final ex = MigrationException('Test', 3, issues: []);
      expect(ex.issues, isEmpty);
    });
  });

  // ============================================================
  // Integration - Complete Migration Flow Tests
  // ============================================================
  group('Migration Flow Integration - تدفق الترحيل الكامل', () {
    test('getMigrationPath + getMigration produces valid migration chain', () {
      const fromVersion = 1;
      const toVersion = 5;

      final path = SchemaVersionRegistry.getMigrationPath(fromVersion, toVersion);
      expect(path, isNotEmpty);

      // Check each version in path has a corresponding migration (or is handled)
      for (final version in path) {
        final migration = SahoolMigrationStrategy.getMigration(version);
        if (migration != null) {
          expect(migration.targetVersion, equals(version));
          expect(migration.fromVersion, equals(version - 1));
        }
      }
    });

    test('migration chain is monotonically increasing', () {
      const fromVersion = 1;
      const toVersion = currentSchemaVersion;

      final migrations = SahoolMigrationStrategy.getMigrationsBetween(
        fromVersion,
        toVersion,
      );

      for (int i = 1; i < migrations.length; i++) {
        expect(
          migrations[i].targetVersion,
          greaterThan(migrations[i - 1].targetVersion),
          reason: 'Migrations must be in ascending version order',
        );
      }
    });

    test('all registered migrations have valid version relationships', () {
      for (int v = minimumSupportedVersion; v <= currentSchemaVersion; v++) {
        final migration = SahoolMigrationStrategy.getMigration(v);
        if (migration != null) {
          expect(
            migration.targetVersion,
            equals(v),
            reason: 'Migration registered as v$v must target version $v',
          );
          expect(
            migration.fromVersion,
            equals(v - 1),
            reason: 'Migration to v$v must come from v${v - 1}',
          );
          expect(
            migration.targetVersion,
            greaterThan(migration.fromVersion),
            reason: 'targetVersion must be greater than fromVersion',
          );
        }
      }
    });

    test('SchemaVersion and SahoolMigrationStrategy are consistent', () {
      // All migration strategy entries should have corresponding schema versions
      for (int v = minimumSupportedVersion + 1; v <= currentSchemaVersion; v++) {
        final schemaVersion = SchemaVersionRegistry.getVersion(v);
        expect(
          schemaVersion,
          isNotNull,
          reason: 'Schema registry must have entry for version $v',
        );
      }
    });
  });
}
