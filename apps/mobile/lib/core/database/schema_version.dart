/// Schema Version Management for SAHOOL Mobile Database
/// ادارة اصدارات قاعدة البيانات لتطبيق سهول
///
/// This module tracks database schema versions and provides utilities
/// for version comparison and compatibility checking.
///
/// Version History:
/// - v1: Initial schema (Tasks, Outbox, Fields, SyncLogs)
/// - v2: Added GIS columns to Fields table
/// - v3: Added ETag support + SyncEvents table
/// - v4: Unified Outbox schema with ETag support
/// - v5: Added migration tracking + metadata columns
/// - v6: Added CachedUsers and CachedUserProfiles tables
library;

import 'package:drift/drift.dart';

/// Current schema version of the database
const int currentSchemaVersion = 6;

/// Minimum supported schema version for migration
const int minimumSupportedVersion = 1;

/// Schema version metadata for tracking migration history
class SchemaVersion {
  /// Version number (1, 2, 3, etc.)
  final int version;

  /// Description of this version
  final String description;

  /// Description in Arabic
  final String descriptionAr;

  /// Date when this version was released
  final DateTime releaseDate;

  /// Whether this version requires data migration (not just schema)
  final bool requiresDataMigration;

  /// Breaking changes introduced in this version
  final List<String> breakingChanges;

  SchemaVersion({
    required this.version,
    required this.description,
    required this.descriptionAr,
    required this.releaseDate,
    this.requiresDataMigration = false,
    this.breakingChanges = const [],
  });

  /// Check if migration from [fromVersion] is supported
  bool canMigrateFrom(int fromVersion) {
    return fromVersion >= minimumSupportedVersion && fromVersion < version;
  }

  @override
  String toString() => 'SchemaVersion(v$version: $description)';
}

// Release date constants (cannot be const, so defined as final)
final DateTime _v1ReleaseDate = DateTime(2024, 1, 1);
final DateTime _v2ReleaseDate = DateTime(2024, 6, 1);
final DateTime _v3ReleaseDate = DateTime(2024, 9, 1);
final DateTime _v4ReleaseDate = DateTime(2025, 1, 1);
final DateTime _v5ReleaseDate = DateTime(2025, 6, 1);
final DateTime _v6ReleaseDate = DateTime(2026, 3, 1);

/// Registry of all schema versions
class SchemaVersionRegistry {
  static final List<SchemaVersion> versions = [
    SchemaVersion(
      version: 1,
      description: 'Initial schema with Tasks, Outbox, Fields, SyncLogs',
      descriptionAr:
          'المخطط الاولي مع المهام والصندوق الصادر والحقول وسجلات المزامنة',
      releaseDate: _v1ReleaseDate,
    ),
    SchemaVersion(
      version: 2,
      description: 'Added GIS columns (boundary, centroid) to Fields table',
      descriptionAr: 'اضافة اعمدة نظام المعلومات الجغرافية للحقول',
      releaseDate: _v2ReleaseDate,
      requiresDataMigration: true,
      breakingChanges: ['Fields table recreated with new GIS columns'],
    ),
    SchemaVersion(
      version: 3,
      description: 'Added ETag support and SyncEvents table',
      descriptionAr: 'اضافة دعم ETag وجدول احداث المزامنة',
      releaseDate: _v3ReleaseDate,
    ),
    SchemaVersion(
      version: 4,
      description: 'Unified Outbox schema with ETag support',
      descriptionAr: 'توحيد مخطط صندوق الصادر مع دعم ETag',
      releaseDate: _v4ReleaseDate,
      requiresDataMigration: true,
      breakingChanges: ['Outbox table recreated with new schema'],
    ),
    SchemaVersion(
      version: 5,
      description: 'Added migration tracking and metadata columns',
      descriptionAr: 'اضافة تتبع الترحيل واعمدة البيانات الوصفية',
      releaseDate: _v5ReleaseDate,
    ),
    SchemaVersion(
      version: 6,
      description: 'Added CachedUsers and CachedUserProfiles tables',
      descriptionAr: 'اضافة جداول المستخدمين والملفات الشخصية المخزنة مؤقتاً',
      releaseDate: _v6ReleaseDate,
    ),
  ];

  /// Get schema version info by version number
  static SchemaVersion? getVersion(int version) {
    try {
      return versions.firstWhere((v) => v.version == version);
    } catch (e) {
      return null;
    }
  }

  /// Get current schema version info
  static SchemaVersion get current => versions.last;

  /// Check if version is supported
  static bool isSupported(int version) {
    return version >= minimumSupportedVersion &&
        version <= currentSchemaVersion;
  }

  /// Get all versions between [from] and [to] (exclusive of from, inclusive of to)
  static List<SchemaVersion> getVersionsBetween(int from, int to) {
    return versions.where((v) => v.version > from && v.version <= to).toList()
      ..sort((a, b) => a.version.compareTo(b.version));
  }

  /// Get migration path from [from] to [to]
  static List<int> getMigrationPath(int from, int to) {
    final List<int> path = [];
    for (int v = from + 1; v <= to; v++) {
      path.add(v);
    }
    return path;
  }
}

/// Migration tracking table for audit purposes
/// جدول تتبع الترحيل لاغراض التدقيق
@TableIndex(name: 'migration_history_version_idx', columns: {#version})
class MigrationHistory extends Table {
  /// Auto-incrementing primary key
  IntColumn get id => integer().autoIncrement()();

  /// Schema version this migration upgraded to
  IntColumn get version => integer()();

  /// Schema version this migration upgraded from
  IntColumn get fromVersion => integer()();

  /// When the migration started
  DateTimeColumn get startedAt => dateTime()();

  /// When the migration completed (null if failed)
  DateTimeColumn get completedAt => dateTime().nullable()();

  /// Migration status: pending, running, completed, failed, rolled_back
  TextColumn get status => text().withDefault(const Constant('pending'))();

  /// Error message if migration failed
  TextColumn get errorMessage => text().nullable()();

  /// Checksum of the migration script (for verification)
  TextColumn get scriptChecksum => text().nullable()();

  /// Duration in milliseconds
  IntColumn get durationMs => integer().nullable()();

  /// Whether a backup was created before migration
  BoolColumn get backupCreated =>
      boolean().withDefault(const Constant(false))();

  /// Path to backup file (if created)
  TextColumn get backupPath => text().nullable()();

  /// Additional metadata as JSON
  TextColumn get metadata => text().nullable()();
}

/// Enum for migration status
enum MigrationStatus {
  pending('pending'),
  running('running'),
  completed('completed'),
  failed('failed'),
  rolledBack('rolled_back');

  final String value;
  const MigrationStatus(this.value);

  static MigrationStatus fromString(String value) {
    return MigrationStatus.values.firstWhere(
      (e) => e.value == value,
      orElse: () => MigrationStatus.pending,
    );
  }
}

/// Result of a migration operation
class MigrationResult {
  /// Whether the migration succeeded
  final bool success;

  /// Target version after migration
  final int targetVersion;

  /// Starting version before migration
  final int fromVersion;

  /// Duration of the migration
  final Duration duration;

  /// Error message if failed
  final String? error;

  /// Stack trace if failed
  final StackTrace? stackTrace;

  /// Path to backup file if created
  final String? backupPath;

  /// Whether data was preserved
  final bool dataPreserved;

  /// Number of rows affected
  final int rowsAffected;

  /// Warnings generated during migration
  final List<String> warnings;

  const MigrationResult({
    required this.success,
    required this.targetVersion,
    required this.fromVersion,
    required this.duration,
    this.error,
    this.stackTrace,
    this.backupPath,
    this.dataPreserved = true,
    this.rowsAffected = 0,
    this.warnings = const [],
  });

  factory MigrationResult.success({
    required int targetVersion,
    required int fromVersion,
    required Duration duration,
    String? backupPath,
    int rowsAffected = 0,
    List<String> warnings = const [],
  }) {
    return MigrationResult(
      success: true,
      targetVersion: targetVersion,
      fromVersion: fromVersion,
      duration: duration,
      backupPath: backupPath,
      dataPreserved: true,
      rowsAffected: rowsAffected,
      warnings: warnings,
    );
  }

  factory MigrationResult.failure({
    required int targetVersion,
    required int fromVersion,
    required Duration duration,
    required String error,
    StackTrace? stackTrace,
    String? backupPath,
    bool dataPreserved = true,
  }) {
    return MigrationResult(
      success: false,
      targetVersion: targetVersion,
      fromVersion: fromVersion,
      duration: duration,
      error: error,
      stackTrace: stackTrace,
      backupPath: backupPath,
      dataPreserved: dataPreserved,
    );
  }

  @override
  String toString() {
    if (success) {
      return 'MigrationResult(success: v$fromVersion -> v$targetVersion in ${duration.inMilliseconds}ms)';
    } else {
      return 'MigrationResult(failed: v$fromVersion -> v$targetVersion, error: $error)';
    }
  }
}
