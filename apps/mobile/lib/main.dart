import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'core/sync/sync_engine.dart';
import 'core/sync/background_sync_task.dart';
import 'core/storage/database.dart';
import 'core/config/env_config.dart';
import 'core/services/crash_reporting_service.dart';
import 'core/security/device_integrity_service.dart';
import 'core/security/device_security_screen.dart';
import 'core/security/security_config.dart';

void main() async {
  // Ensure Flutter bindings are initialized first
  WidgetsFlutterBinding.ensureInitialized();

  // Set up Flutter error handler before anything else
  FlutterError.onError = (FlutterErrorDetails details) {
    // Log to console in debug mode
    FlutterError.presentError(details);

    // Report to crash reporting service
    final crashReporting = CrashReportingService();
    crashReporting.reportError(
      details.exception,
      details.stack,
      severity: ErrorSeverity.error,
      reason: details.context?.toString(),
      customData: {
        'library': details.library ?? 'unknown',
        'silent': details.silent,
      },
      fatal: false,
    );
  };

  // Catch all async errors in the zone
  await runZonedGuarded(() async {
    // Load environment configuration first (non-critical)
    try {
      await EnvConfig.load();
    } catch (e) {
      debugPrint('⚠️ EnvConfig load failed: $e');
      // Continue anyway - defaults will be used
    }

    // Initialize crash reporting service early
    try {
      final crashReporting = CrashReportingService();
      await crashReporting.initialize(
        samplingRate: 1.0, // 100% in production, can be adjusted
        maxBreadcrumbs: 100,
      );

      // Record app start breadcrumb
      crashReporting.recordBreadcrumb(
        message: 'App started',
        category: 'lifecycle',
        level: BreadcrumbLevel.info,
      );

      debugPrint('✅ Crash reporting initialized');
    } catch (e) {
      debugPrint('⚠️ Crash reporting init failed (non-critical): $e');
    }

    // Device Integrity Check - Security Feature
    // فحص سلامة الجهاز - ميزة أمنية
    final securityConfig = SecurityConfig.fromBuildMode();
    debugPrint('🔒 Security config: $securityConfig');

    // Perform device integrity check if enabled
    if (securityConfig.deviceIntegrityPolicy != DeviceIntegrityPolicy.disabled) {
      try {
        crashReporting.recordBreadcrumb(
          message: 'Starting device integrity check',
          category: 'security',
          level: BreadcrumbLevel.info,
        );

        final deviceIntegrity = DeviceIntegrityService();
        final securityResult = await deviceIntegrity.checkDeviceIntegrity();

        crashReporting.recordBreadcrumb(
          message: 'Device integrity check completed',
          category: 'security',
          level: BreadcrumbLevel.info,
          data: {
            'compromised': securityResult.isCompromised,
            'threatLevel': securityResult.threatLevel.toString(),
            'threats': securityResult.detectedThreats.length,
          },
        );

        // Log security event
        if (securityConfig.logSecurityEvents) {
          deviceIntegrity.logSecurityEvent(securityResult);
        }

        // Check if app should be blocked
        final shouldBlock = deviceIntegrity.shouldBlockApp(securityResult, securityConfig);

        if (shouldBlock ||
            (securityConfig.deviceIntegrityPolicy == DeviceIntegrityPolicy.warn &&
             securityResult.hasSecurityIssues)) {

          debugPrint('🚨 Security check failed - showing security screen');
          crashReporting.recordBreadcrumb(
            message: 'Security check failed - blocking app',
            category: 'security',
            level: BreadcrumbLevel.warning,
          );

          // Show security screen
          runApp(
            MaterialApp(
              debugShowCheckedModeBanner: false,
              home: DeviceSecurityScreen(
                securityResult: securityResult,
                isBlocked: shouldBlock,
                onContinueAnyway: shouldBlock
                    ? null
                    : () {
                        // User chose to continue anyway
                        debugPrint('⚠️ User bypassed security warning');
                        crashReporting.recordBreadcrumb(
                          message: 'User bypassed security warning',
                          category: 'security',
                          level: BreadcrumbLevel.warning,
                        );
                        // Restart app initialization
                        main();
                      },
              ),
            ),
          );
          return; // Stop app initialization
        }

        debugPrint('✅ Device security check passed');
        crashReporting.recordBreadcrumb(
          message: 'Device security check passed',
          category: 'security',
          level: BreadcrumbLevel.info,
        );
      } catch (e, stackTrace) {
        debugPrint('⚠️ Device integrity check failed (non-critical): $e');
        // Continue anyway - don't block app if security check fails
        crashReporting.reportError(
          e,
          stackTrace,
          severity: ErrorSeverity.warning,
          reason: 'Device integrity check failed',
          fatal: false,
        );
      }
    } else {
      debugPrint('🔓 Device integrity checks disabled');
      crashReporting.recordBreadcrumb(
        message: 'Device integrity checks disabled',
        category: 'security',
        level: BreadcrumbLevel.info,
      );
    }

    // Initialize database
    late AppDatabase database;
    final crashReporting = CrashReportingService();
    try {
      crashReporting.recordBreadcrumb(
        message: 'Initializing database',
        category: 'lifecycle',
        level: BreadcrumbLevel.info,
      );
      database = AppDatabase();
      crashReporting.recordBreadcrumb(
        message: 'Database initialized successfully',
        category: 'lifecycle',
        level: BreadcrumbLevel.info,
      );
    } catch (e, stackTrace) {
      debugPrint('❌ Database initialization failed: $e');
      crashReporting.reportError(
        e,
        stackTrace,
        severity: ErrorSeverity.fatal,
        reason: 'Database initialization failed',
        fatal: true,
      );
      rethrow;
    }

    // Initialize sync engine
    late SyncEngine syncEngine;
    try {
      crashReporting.recordBreadcrumb(
        message: 'Initializing sync engine',
        category: 'lifecycle',
        level: BreadcrumbLevel.info,
      );
      syncEngine = SyncEngine(database: database);
      crashReporting.recordBreadcrumb(
        message: 'Sync engine initialized successfully',
        category: 'lifecycle',
        level: BreadcrumbLevel.info,
      );
    } catch (e, stackTrace) {
      debugPrint('❌ SyncEngine initialization failed: $e');
      crashReporting.reportError(
        e,
        stackTrace,
        severity: ErrorSeverity.fatal,
        reason: 'SyncEngine initialization failed',
        fatal: true,
      );
      rethrow;
    }

    // Initialize background sync with Workmanager (non-critical)
    try {
      crashReporting.recordBreadcrumb(
        message: 'Initializing background sync',
        category: 'lifecycle',
        level: BreadcrumbLevel.info,
      );
      await BackgroundSyncManager.initialize();
      await BackgroundSyncManager.registerPeriodicSync();
      debugPrint('✅ Background sync initialized');
      crashReporting.recordBreadcrumb(
        message: 'Background sync initialized successfully',
        category: 'lifecycle',
        level: BreadcrumbLevel.info,
      );
    } catch (e, stackTrace) {
      // Non-critical - app can work without background sync
      debugPrint('⚠️ Background sync init failed (non-critical): $e');
      crashReporting.reportError(
        e,
        stackTrace,
        severity: ErrorSeverity.warning,
        reason: 'Background sync initialization failed (non-critical)',
        fatal: false,
      );
    }

    // Run the app
    crashReporting.recordBreadcrumb(
      message: 'Starting Flutter app',
      category: 'lifecycle',
      level: BreadcrumbLevel.info,
    );

    runApp(
      ProviderScope(
        overrides: [
          databaseProvider.overrideWithValue(database),
          syncEngineProvider.overrideWithValue(syncEngine),
        ],
        child: const SahoolFieldApp(),
      ),
    );

    // Start foreground sync when app is active (non-blocking)
    try {
      crashReporting.recordBreadcrumb(
        message: 'Starting foreground sync',
        category: 'lifecycle',
        level: BreadcrumbLevel.info,
      );
      syncEngine.startPeriodic();
    } catch (e, stackTrace) {
      debugPrint('⚠️ Foreground sync start failed: $e');
      crashReporting.reportError(
        e,
        stackTrace,
        severity: ErrorSeverity.warning,
        reason: 'Foreground sync start failed (non-critical)',
        fatal: false,
      );
    }
  }, (error, stackTrace) {
    // Global zone error handler - catches all uncaught async errors
    debugPrint('❌ Uncaught error: $error');
    debugPrint('Stack trace: $stackTrace');

    // Report to crash reporting service
    final crashReporting = CrashReportingService();
    crashReporting.reportError(
      error,
      stackTrace,
      severity: ErrorSeverity.fatal,
      reason: 'Uncaught zone error',
      fatal: true,
    );

    // In release mode, the error has been reported
    // In debug mode, the error is logged and the app may continue or crash
  });
}

// Global providers
final databaseProvider = Provider<AppDatabase>((ref) {
  throw UnimplementedError('Database not initialized');
});

final syncEngineProvider = Provider<SyncEngine>((ref) {
  throw UnimplementedError('SyncEngine not initialized');
});

final crashReportingProvider = Provider<CrashReportingService>((ref) {
  return CrashReportingService();
});
