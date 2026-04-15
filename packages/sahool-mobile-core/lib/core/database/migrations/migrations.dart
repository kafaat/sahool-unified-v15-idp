/// Database Migrations Library
/// مكتبة ترحيل قاعدة البيانات
///
/// This library exports all migration-related classes and utilities.
///
/// Usage:
/// ```dart
/// import 'package:sahool_mobile_core/core/database/migrations/migrations.dart';
///
/// // Use the migration strategy
/// final strategy = SahoolMigrationStrategy.create(database: db);
///
/// // Verify migrations
/// final verifier = MigrationVerifier(db);
/// final report = await verifier.runFullVerification();
/// ```
library;

// Schema version management
export '../schema_version.dart';

// Migration base classes
export 'migration_base.dart';

// Migration strategy coordinator
export '../migration_strategy.dart';

// Verification utilities
export 'migration_verification.dart';

// Individual migrations
export 'migration_v5.dart';
export 'migration_v6.dart';
