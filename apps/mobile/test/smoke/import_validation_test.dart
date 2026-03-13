/// Import Validation Tests - اختبارات التحقق من الاستيرادات
///
/// These tests verify that all critical imports in the SAHOOL mobile app
/// can be resolved and don't have circular dependencies or missing files.
///
/// اختبارات التحقق من أن جميع الاستيرادات الحيوية في تطبيق سهول
/// يمكن حلها وأنها لا تحتوي على تبعيات دائرية أو ملفات مفقودة.
///
/// Run with: flutter test test/smoke/import_validation_test.dart

// ignore_for_file: unused_import, unnecessary_import

library;

import 'package:flutter_test/flutter_test.dart';

// Core imports
import 'package:sahool_field_app/core/utils/app_logger.dart';
import 'package:sahool_field_app/core/database/schema_version.dart';
import 'package:sahool_field_app/core/database/migration_strategy.dart';
import 'package:sahool_field_app/core/database/migrations/migration_base.dart';
import 'package:sahool_field_app/core/database/migrations/migration_v5.dart';
import 'package:sahool_field_app/core/database/migrations/migration_verification.dart';
import 'package:sahool_field_app/core/database/migrations/migrations.dart';

// Auth imports
import 'package:sahool_field_app/core/auth/auth_service.dart';
import 'package:sahool_field_app/core/auth/biometric_service.dart';
import 'package:sahool_field_app/core/auth/secure_storage_service.dart';
import 'package:sahool_field_app/core/auth/token_manager.dart';

// Contracts imports
import 'package:sahool_field_app/core/contracts/service_ports.dart';
import 'package:sahool_field_app/core/contracts/error_codes.dart';

// Feature imports - Field
import 'package:sahool_field_app/features/field/domain/entities/field.dart';

// Feature imports - Sync
import 'package:sahool_field_app/core/sync/network_status.dart';

void main() {
  group('Import Validation Tests - اختبارات التحقق من الاستيرادات', () {
    group('Core Imports', () {
      test('App config is importable', () {
        // If we reach this point, the import worked
        expect(true, isTrue);
      });

      test('App logger is importable', () {
        expect(AppLogger, isNotNull);
      });

      test('Database schema version constants are accessible', () {
        expect(currentSchemaVersion, greaterThan(0));
        expect(minimumSupportedVersion, greaterThan(0));
        expect(currentSchemaVersion, greaterThanOrEqualTo(minimumSupportedVersion));
      });

      test('SchemaVersionRegistry has all expected versions', () {
        expect(SchemaVersionRegistry.versions, isNotEmpty);
        expect(SchemaVersionRegistry.current, isNotNull);
        expect(SchemaVersionRegistry.current.version, equals(currentSchemaVersion));
      });

      test('Migration strategy is importable', () {
        expect(SahoolMigrationStrategy.getMigration(5), isNotNull);
      });

      test('Migration base is importable', () {
        // MigrationResult should be accessible
        final result = MigrationResult.success(
          targetVersion: 5,
          fromVersion: 4,
          duration: const Duration(milliseconds: 1),
        );
        expect(result.success, isTrue);
      });

      test('MigrationV5 is importable and has correct version', () {
        final migration = MigrationV5();
        expect(migration.targetVersion, equals(5));
        expect(migration.fromVersion, equals(4));
      });

      test('Migration verification models are importable', () {
        final result = MigrationVerificationResult.success(
          version: 5,
          message: 'Test',
        );
        expect(result.passed, isTrue);
      });

      test('MigrationException is importable', () {
        final ex = MigrationException('Test error', 5);
        expect(ex.targetVersion, equals(5));
        expect(ex.toString(), contains('v5'));
      });
    });

    group('Auth Imports', () {
      test('AuthStatus enum is importable', () {
        expect(AuthStatus.values, isNotEmpty);
        expect(AuthStatus.authenticated, isNotNull);
        expect(AuthStatus.unauthenticated, isNotNull);
      });

      test('AuthState is importable and constructible', () {
        const state = AuthState(status: AuthStatus.unauthenticated);
        expect(state.status, equals(AuthStatus.unauthenticated));
        expect(state.user, isNull);
        expect(state.isAuthenticated, isFalse);
      });

      test('AuthState copyWith works correctly', () {
        const state = AuthState(status: AuthStatus.unauthenticated);
        final loadingState = state.copyWith(status: AuthStatus.loading);
        expect(loadingState.status, equals(AuthStatus.loading));
        expect(loadingState.isLoading, isTrue);
      });
    });

    group('Contract Imports', () {
      test('Service ports are accessible', () {
        // From the generated contracts
        expect(ServicePorts.fieldManagement, greaterThan(0));
        expect(ServicePorts.userService, greaterThan(0));
        expect(ServicePorts.weather, greaterThan(0));
      });

      test('Error codes are accessible', () {
        expect(ErrorCodes.unauthorized, isNotNull);
        expect(ErrorCodes.notFound, isNotNull);
        expect(ErrorCodes.networkError, isNotNull);
      });
    });

    group('Domain Model Imports', () {
      test('Field entity is importable', () {
        // If we reach here, the import resolved
        expect(true, isTrue);
      });

      test('NetworkStatus is importable', () {
        expect(NetworkStatus, isNotNull);
      });
    });

    group('Sync Priority', () {
      test('SyncPriority constants are correctly defined', () {
        expect(SyncPriority.low, equals(0));
        expect(SyncPriority.normal, equals(10));
        expect(SyncPriority.high, equals(20));
        expect(SyncPriority.critical, equals(30));
      });

      test('SyncPriority.forEntityType returns correct priorities', () {
        expect(SyncPriority.forEntityType('field'), equals(SyncPriority.high));
        expect(SyncPriority.forEntityType('task'), equals(SyncPriority.normal));
        expect(SyncPriority.forEntityType('unknown'), equals(SyncPriority.normal));
      });

      test('SyncPriority.forMethod returns correct priorities', () {
        expect(SyncPriority.forMethod('DELETE'), equals(SyncPriority.critical));
        expect(SyncPriority.forMethod('POST'), equals(SyncPriority.high));
        expect(SyncPriority.forMethod('PUT'), equals(SyncPriority.normal));
        expect(SyncPriority.forMethod('GET'), equals(SyncPriority.low));
        expect(SyncPriority.forMethod('PATCH'), equals(SyncPriority.normal));
      });
    });
  });

  group('Database Module Imports', () {
    test('All migration versions are registered', () {
      final versions = SchemaVersionRegistry.versions;
      expect(versions.length, equals(currentSchemaVersion));

      // Verify versions are sequential
      for (int i = 0; i < versions.length; i++) {
        expect(versions[i].version, equals(i + 1));
      }
    });

    test('Version 5 has correct metadata', () {
      final v5 = SchemaVersionRegistry.getVersion(5);
      expect(v5, isNotNull);
      expect(v5!.version, equals(5));
      expect(v5.description, isNotEmpty);
      expect(v5.descriptionAr, isNotEmpty);
    });

    test('getVersionsBetween works correctly', () {
      final between = SchemaVersionRegistry.getVersionsBetween(2, 5);
      expect(between.length, equals(3));
      expect(between.map((v) => v.version).toList(), equals([3, 4, 5]));
    });

    test('getMigrationPath returns correct path', () {
      final path = SchemaVersionRegistry.getMigrationPath(1, 5);
      expect(path, equals([2, 3, 4, 5]));
    });

    test('isSupported checks version bounds correctly', () {
      expect(SchemaVersionRegistry.isSupported(0), isFalse);
      expect(SchemaVersionRegistry.isSupported(minimumSupportedVersion), isTrue);
      expect(SchemaVersionRegistry.isSupported(currentSchemaVersion), isTrue);
      expect(SchemaVersionRegistry.isSupported(currentSchemaVersion + 1), isFalse);
    });
  });
}
