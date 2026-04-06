/// Migration v6 -> v7: Add irrigationType, plantingDate, notes to Fields
/// الترحيل من الاصدار 6 الى 7: اضافة نوع الري وتاريخ الزراعة والملاحظات
///
/// This migration adds nullable columns to the fields table so
/// form data captured in field_form_screen.dart is persisted.
library;

import 'package:drift/drift.dart';

import 'migration_base.dart';

/// Migration from schema version 6 to 7
///
/// Changes:
/// 1. Adds irrigation_type (TEXT nullable) to fields
/// 2. Adds planting_date (INTEGER/DateTime nullable) to fields
/// 3. Adds notes (TEXT nullable) to fields
class MigrationV7 extends Migration with MigrationHelpers {
  @override
  int get targetVersion => 7;

  @override
  String get description =>
      'Add irrigationType, plantingDate, notes to Fields table';

  @override
  String get descriptionAr =>
      'اضافة نوع الري وتاريخ الزراعة والملاحظات لجدول الحقول';

  @override
  bool get supportsRollback => true;

  @override
  bool get requiresBackup => false;

  @override
  int get estimatedDurationMs => 500;

  @override
  List<String> get affectedTables => ['fields'];

  @override
  Future<void> up(Migrator m, GeneratedDatabase db) async {
    // All columns are nullable — safe additive migration
    await db.customStatement(
      'ALTER TABLE fields ADD COLUMN irrigation_type TEXT',
    );
    await db.customStatement(
      'ALTER TABLE fields ADD COLUMN planting_date INTEGER',
    );
    await db.customStatement(
      'ALTER TABLE fields ADD COLUMN notes TEXT',
    );
  }

  @override
  Future<void> rollback(Migrator m, GeneratedDatabase db) async {
    // SQLite doesn't support DROP COLUMN before 3.35.0
    // For older versions, this is a no-op (columns are nullable, harmless)
    try {
      await db.customStatement(
        'ALTER TABLE fields DROP COLUMN irrigation_type',
      );
      await db.customStatement(
        'ALTER TABLE fields DROP COLUMN planting_date',
      );
      await db.customStatement(
        'ALTER TABLE fields DROP COLUMN notes',
      );
    } catch (_) {
      // SQLite < 3.35.0 doesn't support DROP COLUMN — safe to ignore
    }
  }

  @override
  Future<bool> preCheck(Migrator m, GeneratedDatabase db) async {
    return true; // Simple additive columns, always safe
  }

  @override
  Future<bool> postCheck(Migrator m, GeneratedDatabase db) async {
    return await columnExists(db, 'fields', 'irrigation_type');
  }
}
