/// Migration v7 -> v8: Add ndvi_cache table
/// الترحيل من الاصدار 7 الى 8: إضافة جدول كاش مؤشرات NDVI
///
/// Creates a persistent cache table for spectral-index values with TTL support.
/// The DAO ([NdviCacheDao]) uses raw SQL, so no code-generation step is needed.
library;

import 'package:drift/drift.dart';

import 'migration_base.dart';

/// Migration from schema version 7 to 8.
///
/// Changes:
/// 1. Creates `ndvi_cache` table with TTL columns.
/// 2. Creates a unique index on `(field_id, index_code, date_key)`.
class MigrationV8 extends Migration with MigrationHelpers {
  @override
  int get targetVersion => 8;

  @override
  String get description => 'Add ndvi_cache table for persistent spectral-index cache';

  @override
  String get descriptionAr =>
      'إضافة جدول ndvi_cache للكاش المستمر لقيم المؤشرات الطيفية';

  @override
  bool get supportsRollback => true;

  @override
  bool get requiresBackup => false;

  @override
  int get estimatedDurationMs => 300;

  @override
  List<String> get affectedTables => ['ndvi_cache'];

  @override
  Future<void> upgrade(Migrator m, GeneratedDatabase db) async {
    await db.customStatement('''
      CREATE TABLE IF NOT EXISTS ndvi_cache (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        field_id   TEXT    NOT NULL,
        index_code TEXT    NOT NULL,
        date_key   TEXT    NOT NULL,
        value      REAL    NOT NULL,
        fetched_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL
      )
    ''');
    await db.customStatement('''
      CREATE UNIQUE INDEX IF NOT EXISTS ndvi_cache_key_idx
        ON ndvi_cache (field_id, index_code, date_key)
    ''');
  }

  @override
  Future<void> rollback(Migrator m, GeneratedDatabase db) async {
    await db.customStatement('DROP TABLE IF EXISTS ndvi_cache');
  }

  @override
  Future<bool> preCheck(Migrator m, GeneratedDatabase db) async {
    return true; // Pure table creation — always safe.
  }

  @override
  Future<bool> postCheck(Migrator m, GeneratedDatabase db) async {
    return await tableExists(db, 'ndvi_cache');
  }
}
