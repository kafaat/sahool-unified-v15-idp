/// Migration Tests for SAHOOL Mobile Database
/// اختبارات ترحيل قاعدة بيانات سهول
///
/// These tests verify the database migration system works correctly,
/// including schema upgrades, data preservation, and rollback support.
library;
import 'package:flutter_test/flutter_test.dart';

// Import the migration system
import 'package:sahool_field_app/core/database/schema_version.dart';
import 'package:sahool_field_app/core/database/migration_strategy.dart';
import 'package:sahool_field_app/core/database/migrations/migration_base.dart';
import 'package:sahool_field_app/core/database/migrations/migration_v5.dart';
import 'package:sahool_field_app/core/database/migrations/migration_verification.dart';

void main() {
  group('SchemaVersion', () {
    test('currentSchemaVersion should be 6', () {
      expect(currentSchemaVersion, equals(6));
    });

    test('minimumSupportedVersion should be 1', () {
      expect(minimumSupportedVersion, equals(1));
    });

    test('SchemaVersionRegistry should have all versions', () {
      expect(SchemaVersionRegistry.versions.length, equals(6));
      expect(SchemaVersionRegistry.versions.first.version, equals(1));
      expect(SchemaVersionRegistry.versions.last.version, equals(6));
    });

    test('SchemaVersionRegistry.current should return latest version', () {
      final current = SchemaVersionRegistry.current;
      expect(current.version, equals(6));
      expect(current.description, contains('CachedUsers'));
    });

    test('SchemaVersionRegistry.getVersion should return correct version', () {
      final v3 = SchemaVersionRegistry.getVersion(3);
      expect(v3, isNotNull);
      expect(v3!.version, equals(3));
      expect(v3.description, contains('ETag'));
    });

    test('SchemaVersionRegistry.getVersion should return null for invalid version', () {
      final invalid = SchemaVersionRegistry.getVersion(99);
      expect(invalid, isNull);
    });

    test('SchemaVersionRegistry.isSupported should check version bounds', () {
      expect(SchemaVersionRegistry.isSupported(0), isFalse);
      expect(SchemaVersionRegistry.isSupported(1), isTrue);
      expect(SchemaVersionRegistry.isSupported(6), isTrue);
      expect(SchemaVersionRegistry.isSupported(7), isFalse);
    });

    test('SchemaVersionRegistry.getVersionsBetween should return correct versions', () {
      final versions = SchemaVersionRegistry.getVersionsBetween(2, 5);
      expect(versions.length, equals(3));
      expect(versions.map((v) => v.version).toList(), equals([3, 4, 5]));
    });

    test('SchemaVersionRegistry.getMigrationPath should return correct path', () {
      final path = SchemaVersionRegistry.getMigrationPath(1, 5);
      expect(path, equals([2, 3, 4, 5]));
    });
  });

  group('MigrationResult', () {
    test('success factory should create successful result', () {
      final result = MigrationResult.success(
        targetVersion: 5,
        fromVersion: 4,
        duration: const Duration(milliseconds: 100),
        rowsAffected: 10,
      );

      expect(result.success, isTrue);
      expect(result.targetVersion, equals(5));
      expect(result.fromVersion, equals(4));
      expect(result.rowsAffected, equals(10));
      expect(result.error, isNull);
    });

    test('failure factory should create failed result', () {
      final result = MigrationResult.failure(
        targetVersion: 5,
        fromVersion: 4,
        duration: const Duration(milliseconds: 50),
        error: 'Test error',
      );

      expect(result.success, isFalse);
      expect(result.targetVersion, equals(5));
      expect(result.error, equals('Test error'));
    });

    test('toString should format correctly', () {
      final success = MigrationResult.success(
        targetVersion: 5,
        fromVersion: 4,
        duration: const Duration(milliseconds: 100),
      );
      expect(success.toString(), contains('success'));
      expect(success.toString(), contains('v4 -> v5'));

      final failure = MigrationResult.failure(
        targetVersion: 5,
        fromVersion: 4,
        duration: const Duration(milliseconds: 50),
        error: 'Test error',
      );
      expect(failure.toString(), contains('failed'));
      expect(failure.toString(), contains('Test error'));
    });
  });

  group('MigrationV5', () {
    late MigrationV5 migration;

    setUp(() {
      migration = MigrationV5();
    });

    test('should have correct version numbers', () {
      expect(migration.targetVersion, equals(5));
      expect(migration.fromVersion, equals(4));
    });

    test('should have descriptions', () {
      expect(migration.description, isNotEmpty);
      expect(migration.descriptionAr, isNotEmpty);
    });

    test('should support rollback', () {
      expect(migration.supportsRollback, isTrue);
    });

    test('should require backup', () {
      expect(migration.requiresBackup, isTrue);
    });

    test('should list affected tables', () {
      expect(migration.affectedTables, contains('migration_history'));
      expect(migration.affectedTables, contains('fields'));
      expect(migration.affectedTables, contains('outbox'));
    });

    test('should generate consistent checksum', () {
      final checksum1 = migration.checksum;
      final checksum2 = MigrationV5().checksum;
      expect(checksum1, equals(checksum2));
    });
  });

  group('MigrationVerificationResult', () {
    test('success factory should create passing result', () {
      final result = MigrationVerificationResult.success(
        version: 5,
        message: 'Verification passed',
        details: {'key': 'value'},
      );

      expect(result.passed, isTrue);
      expect(result.version, equals(5));
      expect(result.message, equals('Verification passed'));
      expect(result.details, isNotNull);
      expect(result.issues, isEmpty);
    });

    test('failure factory should create failing result', () {
      final result = MigrationVerificationResult.failure(
        version: 5,
        message: 'Verification failed',
        issues: ['Issue 1', 'Issue 2'],
      );

      expect(result.passed, isFalse);
      expect(result.version, equals(5));
      expect(result.issues.length, equals(2));
    });
  });

  group('MigrationStep', () {
    test('should track step progress', () {
      final step = MigrationStep(
        stepNumber: 1,
        description: 'Create table',
      );

      expect(step.completed, isFalse);
      expect(step.error, isNull);
      expect(step.duration, isNull);

      step.completed = true;
      step.duration = const Duration(milliseconds: 50);

      expect(step.completed, isTrue);
      expect(step.toString(), contains('DONE'));
    });

    test('should track step failure', () {
      final step = MigrationStep(
        stepNumber: 1,
        description: 'Create table',
      );

      step.error = 'Table already exists';

      expect(step.completed, isFalse);
      expect(step.toString(), contains('FAILED'));
    });
  });

  group('SyncPriority', () {
    test('should have correct priority levels', () {
      expect(SyncPriority.low, equals(0));
      expect(SyncPriority.normal, equals(10));
      expect(SyncPriority.high, equals(20));
      expect(SyncPriority.critical, equals(30));
    });

    test('forEntityType should return correct priorities', () {
      expect(SyncPriority.forEntityType('field'), equals(SyncPriority.high));
      expect(SyncPriority.forEntityType('task'), equals(SyncPriority.normal));
      expect(SyncPriority.forEntityType('unknown'), equals(SyncPriority.normal));
    });

    test('forMethod should return correct priorities', () {
      expect(SyncPriority.forMethod('DELETE'), equals(SyncPriority.critical));
      expect(SyncPriority.forMethod('POST'), equals(SyncPriority.high));
      expect(SyncPriority.forMethod('PUT'), equals(SyncPriority.normal));
      expect(SyncPriority.forMethod('GET'), equals(SyncPriority.low));
    });
  });

  group('VerificationIssue', () {
    test('should format correctly', () {
      final issue = VerificationIssue(
        category: 'Schema',
        message: 'Missing column',
        severity: IssueSeverity.error,
      );

      expect(issue.toString(), contains('[ERROR]'));
      expect(issue.toString(), contains('Schema'));
      expect(issue.toString(), contains('Missing column'));
    });
  });

  group('IssueSeverity', () {
    test('should have correct string representations', () {
      expect(IssueSeverity.info.toString(), equals('INFO'));
      expect(IssueSeverity.warning.toString(), equals('WARNING'));
      expect(IssueSeverity.error.toString(), equals('ERROR'));
    });
  });

  group('DatabaseStats', () {
    test('should format size correctly', () {
      final stats = DatabaseStats();

      stats.estimatedSizeBytes = 500;
      expect(stats.formattedSize, equals('500 B'));

      stats.estimatedSizeBytes = 2048;
      expect(stats.formattedSize, equals('2.0 KB'));

      stats.estimatedSizeBytes = 1024 * 1024 * 5;
      expect(stats.formattedSize, equals('5.0 MB'));
    });

    test('should calculate total rows', () {
      final stats = DatabaseStats();
      stats.tableCounts['tasks'] = 10;
      stats.tableCounts['fields'] = 5;
      stats.tableCounts['outbox'] = 3;

      expect(stats.totalRows, equals(18));
    });

    test('should handle negative counts in totalRows', () {
      final stats = DatabaseStats();
      stats.tableCounts['tasks'] = 10;
      stats.tableCounts['fields'] = -1; // Table doesn't exist

      expect(stats.totalRows, equals(10));
    });
  });

  group('DatabaseVerificationReport', () {
    test('should count issues by severity', () {
      final report = DatabaseVerificationReport(
        passed: false,
        schemaVersion: 6,
        verificationTime: const Duration(milliseconds: 100),
        issues: [
          VerificationIssue(
            category: 'Schema',
            message: 'Error 1',
            severity: IssueSeverity.error,
          ),
          VerificationIssue(
            category: 'Schema',
            message: 'Error 2',
            severity: IssueSeverity.error,
          ),
          VerificationIssue(
            category: 'Indices',
            message: 'Warning 1',
            severity: IssueSeverity.warning,
          ),
          VerificationIssue(
            category: 'Info',
            message: 'Info 1',
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

    test('toDetailedReport should generate formatted string', () {
      final report = DatabaseVerificationReport(
        passed: true,
        schemaVersion: 6,
        verificationTime: const Duration(milliseconds: 50),
        issues: [],
      );

      final detailed = report.toDetailedReport();
      expect(detailed, contains('PASSED'));
      expect(detailed, contains('Schema Version: 6'));
      expect(detailed, contains('No issues found'));
    });
  });

  group('BackupInfo', () {
    test('should format size correctly', () {
      final backup = BackupInfo(
        path: '/path/to/backup.db',
        createdAt: DateTime.now(),
        sizeBytes: 1024 * 500,
      );

      expect(backup.filename, equals('backup.db'));
      expect(backup.sizeFormatted, equals('500.0 KB'));
    });
  });

  group('MigrationException', () {
    test('should include version in toString', () {
      final exception = MigrationException(
        'Migration failed',
        5,
        issues: ['Issue 1', 'Issue 2'],
      );

      expect(exception.toString(), contains('v5'));
      expect(exception.toString(), contains('Migration failed'));
      expect(exception.issues.length, equals(2));
    });
  });

  group('SahoolMigrationStrategy', () {
    test('getMigration should return migration for valid version', () {
      final migration = SahoolMigrationStrategy.getMigration(5);
      expect(migration, isNotNull);
      expect(migration!.targetVersion, equals(5));
    });

    test('getMigration should return null for invalid version', () {
      final migration = SahoolMigrationStrategy.getMigration(99);
      expect(migration, isNull);
    });

    test('getMigrationsBetween should return correct migrations', () {
      final migrations = SahoolMigrationStrategy.getMigrationsBetween(4, 5);
      expect(migrations.length, equals(1));
      expect(migrations.first.targetVersion, equals(5));
    });

    test('getMigrationsBetween should return empty for no migrations', () {
      final migrations = SahoolMigrationStrategy.getMigrationsBetween(5, 5);
      expect(migrations, isEmpty);
    });
  });
}
