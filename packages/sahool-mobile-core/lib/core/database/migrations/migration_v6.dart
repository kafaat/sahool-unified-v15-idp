/// Migration v5 -> v6: CachedUsers and CachedUserProfiles Tables
/// الترحيل من الاصدار 5 الى 6: جداول المستخدمين والملفات الشخصية المخزنة
///
/// This migration adds:
/// - cached_users table for offline-first user data access
/// - cached_user_profiles table for extended user profile data
library;

import 'package:drift/drift.dart';

import 'migration_base.dart';

/// Migration from schema version 5 to 6
///
/// Changes:
/// 1. Creates cached_users table with indexes
/// 2. Creates cached_user_profiles table
class MigrationV6 extends Migration with MigrationHelpers {
  @override
  int get targetVersion => 6;

  @override
  String get description => 'Add CachedUsers and CachedUserProfiles tables';

  @override
  String get descriptionAr =>
      'اضافة جداول المستخدمين والملفات الشخصية المخزنة مؤقتاً';

  @override
  bool get supportsRollback => true;

  @override
  bool get requiresBackup => true;

  @override
  int get estimatedDurationMs => 1000;

  @override
  List<String> get affectedTables => [
        'cached_users',
        'cached_user_profiles',
      ];

  @override
  Future<bool> preCheck(Migrator m, GeneratedDatabase db) async {
    final result = await db.customSelect('PRAGMA user_version').getSingle();
    final currentVersion = result.read<int>('user_version');

    if (currentVersion != 5) {
      log('Pre-check: Expected version 5, got $currentVersion');
      return currentVersion < 6;
    }

    log('Pre-check passed');
    return true;
  }

  @override
  Future<void> upgrade(Migrator m, GeneratedDatabase db) async {
    // Step 1: Create cached_users table
    await executeStep(
      'Create cached_users table',
      () => _createCachedUsersTable(db),
    );

    // Step 2: Create cached_user_profiles table
    await executeStep(
      'Create cached_user_profiles table',
      () => _createCachedUserProfilesTable(db),
    );

    // Step 3: Create indexes
    await executeStep(
      'Create indexes for cached tables',
      () => _createIndexes(db),
    );

    log('Migration v6 completed successfully');
  }

  @override
  Future<void> rollback(Migrator m, GeneratedDatabase db) async {
    log('Rolling back migration v6');

    await executeStep(
      'Drop cached_user_profiles table',
      () async {
        await db.customStatement('DROP TABLE IF EXISTS cached_user_profiles');
      },
    );

    await executeStep(
      'Drop cached_users table',
      () async {
        await db.customStatement('DROP TABLE IF EXISTS cached_users');
      },
    );

    log('Migration v6 rollback completed');
  }

  @override
  Future<MigrationVerificationResult> verify(GeneratedDatabase db) async {
    final issues = <String>[];
    final details = <String, dynamic>{};

    if (!await tableExists(db, 'cached_users')) {
      issues.add('cached_users table does not exist');
    } else {
      details['cached_users_exists'] = true;
    }

    if (!await tableExists(db, 'cached_user_profiles')) {
      issues.add('cached_user_profiles table does not exist');
    } else {
      details['cached_user_profiles_exists'] = true;
    }

    if (!await indexExists(db, 'cached_users_tenant_idx')) {
      issues.add('cached_users_tenant_idx index does not exist');
    }

    if (!await indexExists(db, 'cached_users_email_idx')) {
      issues.add('cached_users_email_idx index does not exist');
    }

    if (issues.isEmpty) {
      log('Verification passed: All v6 migration changes verified');
      return MigrationVerificationResult.success(
        version: targetVersion,
        message: 'All v6 migration changes verified',
        details: details,
      );
    } else {
      for (final issue in issues) {
        log('WARNING: Verification issue - $issue');
      }
      log('Verification FAILED for v$targetVersion with ${issues.length} issue(s)');
      return MigrationVerificationResult.failure(
        version: targetVersion,
        message: 'Migration verification failed with ${issues.length} issue(s): ${issues.join(', ')}',
        issues: issues,
        details: details,
      );
    }
  }

  Future<void> _createCachedUsersTable(GeneratedDatabase db) async {
    if (await tableExists(db, 'cached_users')) {
      log('cached_users table already exists, skipping creation');
      return;
    }

    await db.customStatement('''
      CREATE TABLE cached_users (
        id TEXT NOT NULL PRIMARY KEY,
        email TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        first_name_ar TEXT,
        last_name_ar TEXT,
        phone TEXT,
        role TEXT NOT NULL DEFAULT 'FARMER',
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        email_verified INTEGER NOT NULL DEFAULT 0,
        phone_verified INTEGER NOT NULL DEFAULT 0,
        tenant_id TEXT,
        avatar_url TEXT,
        failed_login_attempts INTEGER NOT NULL DEFAULT 0,
        lockout_until INTEGER,
        last_login_at INTEGER,
        created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL,
        synced INTEGER NOT NULL DEFAULT 0
      )
    ''');

    log('Created cached_users table');
  }

  Future<void> _createCachedUserProfilesTable(GeneratedDatabase db) async {
    if (await tableExists(db, 'cached_user_profiles')) {
      log('cached_user_profiles table already exists, skipping creation');
      return;
    }

    await db.customStatement('''
      CREATE TABLE cached_user_profiles (
        user_id TEXT NOT NULL PRIMARY KEY,
        national_id TEXT,
        date_of_birth INTEGER,
        address TEXT,
        city TEXT,
        region TEXT,
        country TEXT DEFAULT 'SA',
        updated_at INTEGER NOT NULL
      )
    ''');

    log('Created cached_user_profiles table');
  }

  Future<void> _createIndexes(GeneratedDatabase db) async {
    await createIndexIfNotExists(
      db,
      'cached_users_tenant_idx',
      'cached_users',
      ['tenant_id'],
    );

    await createIndexIfNotExists(
      db,
      'cached_users_email_idx',
      'cached_users',
      ['email'],
    );
  }
}
