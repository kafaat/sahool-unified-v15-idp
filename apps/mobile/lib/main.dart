import 'dart:async';
import 'dart:ui';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'core/sync/sync_engine.dart';
import 'core/sync/background_sync_task.dart';
import 'core/storage/database.dart';
import 'core/config/env_config.dart';
// Legacy crash service kept for backward compatibility but delegates to CrashReporter
import 'core/services/crash_reporting_service.dart' as legacy_crash;
import 'core/security/device_integrity_service.dart';
import 'core/security/device_security_screen.dart';
import 'core/security/security_config.dart';
import 'core/utils/app_logger.dart';
import 'core/error/error.dart';
import 'core/crash/crash_reporter.dart';
import 'core/persistence/app_state_manager.dart';
import 'core/persistence/preferences_manager.dart';
import 'core/persistence/draft_manager.dart';

// Global crash reporting instance (legacy - kept for compatibility)
final crashReporting = legacy_crash.CrashReportingService();

/// Whether Flutter bindings have already been initialized.
/// Used to prevent redundant re-initialization on security bypass.
bool _bindingsInitialized = false;

/// Continue app initialization after user bypasses security warning.
/// This avoids calling main() recursively, which would cause infinite
/// recursion of WidgetsFlutterBinding.ensureInitialized(), error handlers,
/// and zone setup.
void _continueAppInitialization() {
  // Re-enter the initialization flow from the database setup step onward,
  // bypassing the security check. We call the inner initialization function
  // inside a new zone to maintain error handling.
  runZonedGuarded(() async {
    await _initializeAndRunApp(skipSecurityCheck: true);
  }, (error, stackTrace) {
    AppLogger.critical('Uncaught error: $error',
        tag: 'Main', error: error, stackTrace: stackTrace);
    crashReporter.reportError(
      error,
      stackTrace,
      severity: CrashSeverity.fatal,
      reason: 'Uncaught zone error',
      fatal: true,
    );
  });
}

void main() async {
  // Ensure Flutter bindings are initialized first
  WidgetsFlutterBinding.ensureInitialized();

  // Track whether bindings have already been initialized to avoid
  // redundant re-initialization when the user bypasses a security warning.
  _bindingsInitialized = true;

  // Set up Flutter error handler - single unified crash reporter
  // إعداد معالج أخطاء Flutter - نظام تقارير أعطال موحد
  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.presentError(details);

    // Single unified crash reporter (Sentry-backed)
    crashReporter.reportError(
      details.exception,
      details.stack,
      severity: CrashSeverity.error,
      reason: details.context?.toString(),
      context: {
        'library': details.library ?? 'unknown',
        'silent': details.silent,
      },
      fatal: false,
    );
  };

  // Platform Dispatcher error handler for async errors outside Flutter framework
  // مُعالج أخطاء منصة التشغيل للأخطاء غير المتزامنة
  PlatformDispatcher.instance.onError = (error, stack) {
    AppLogger.critical('Platform Dispatcher Error: $error',
        tag: 'Main', error: error, stackTrace: stack);

    crashReporter.reportError(
      error,
      stack,
      severity: CrashSeverity.fatal,
      reason: 'Platform Dispatcher Error',
      fatal: true,
    );

    return true;
  };

  // Catch all async errors in the zone
  await runZonedGuarded(() async {
    // Load environment configuration first (non-critical)
    try {
      await EnvConfig.load();
    } catch (e) {
      AppLogger.w('EnvConfig load failed: $e', tag: 'Main');
      // Continue anyway - defaults will be used
    }

    // Initialize new CrashReporter with Sentry integration
    try {
      final crashConfig = CrashConfig.fromEnvironment();
      await crashReporter.initialize(crashConfig);

      // Record app start breadcrumb
      breadcrumbService.recordLifecycle('app_started');
      breadcrumbService.recordSystem('environment', data: {
        'env': EnvConfig.environment.name,
        'version': EnvConfig.fullVersion,
        'platform': defaultTargetPlatform.name,
      });

      AppLogger.i(
          'New CrashReporter initialized (Sentry: ${crashConfig.hasSentryDsn})',
          tag: 'Main');
    } catch (e) {
      AppLogger.w('CrashReporter init failed (non-critical): $e', tag: 'Main');
    }

    // Initialize ErrorReporter (unified error handling layer)
    try {
      await errorReporter.initialize();
      AppLogger.i('ErrorReporter initialized', tag: 'Main');
    } catch (e) {
      AppLogger.w('ErrorReporter init failed (non-critical): $e', tag: 'Main');
    }

    // Initialize legacy crash reporting (delegates to primary CrashReporter)
    try {
      await crashReporting.initialize(
        samplingRate: 1.0,
        maxBreadcrumbs: 100,
      );
    } catch (e) {
      AppLogger.w('Legacy crash reporting init skipped: $e', tag: 'Main');
    }

    // Device Integrity Check - Security Feature
    // فحص سلامة الجهاز - ميزة أمنية
    final securityConfig = SecurityConfig.fromBuildMode();
    AppLogger.d('Security config: $securityConfig', tag: 'Security');

    // Perform device integrity check if enabled
    if (securityConfig.deviceIntegrityPolicy !=
        DeviceIntegrityPolicy.disabled) {
      try {
        // Record breadcrumbs in both systems
        breadcrumbService.recordSystem('device_integrity_check_starting');
        crashReporting.recordBreadcrumb(
          message: 'Starting device integrity check',
          category: 'security',
          level: legacy_crash.BreadcrumbLevel.info,
        );

        final deviceIntegrity = DeviceIntegrityService();
        final securityResult = await deviceIntegrity.checkDeviceIntegrity();

        crashReporting.recordBreadcrumb(
          message: 'Device integrity check completed',
          category: 'security',
          level: legacy_crash.BreadcrumbLevel.info,
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
        final shouldBlock =
            deviceIntegrity.shouldBlockApp(securityResult, securityConfig);

        if (shouldBlock ||
            (securityConfig.deviceIntegrityPolicy ==
                    DeviceIntegrityPolicy.warn &&
                securityResult.hasSecurityIssues)) {
          AppLogger.w('Security check failed - showing security screen',
              tag: 'Security');
          crashReporting.recordBreadcrumb(
            message: 'Security check failed - blocking app',
            category: 'security',
            level: legacy_crash.BreadcrumbLevel.warning,
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
                        AppLogger.w('User bypassed security warning',
                            tag: 'Security');
                        crashReporting.recordBreadcrumb(
                          message: 'User bypassed security warning',
                          category: 'security',
                          level: legacy_crash.BreadcrumbLevel.warning,
                        );
                        // Continue app initialization (skip security re-check)
                        _continueAppInitialization();
                      },
              ),
            ),
          );
          return; // Stop app initialization
        }

        AppLogger.i('Device security check passed', tag: 'Security');
        crashReporting.recordBreadcrumb(
          message: 'Device security check passed',
          category: 'security',
          level: legacy_crash.BreadcrumbLevel.info,
        );
      } catch (e, stackTrace) {
        AppLogger.w('Device integrity check failed (non-critical): $e',
            tag: 'Security');
        // Continue anyway - don't block app if security check fails
        crashReporting.reportError(
          e,
          stackTrace,
          severity: legacy_crash.ErrorSeverity.warning,
          reason: 'Device integrity check failed',
          fatal: false,
        );
      }
    } else {
      AppLogger.d('Device integrity checks disabled', tag: 'Security');
      crashReporting.recordBreadcrumb(
        message: 'Device integrity checks disabled',
        category: 'security',
        level: legacy_crash.BreadcrumbLevel.info,
      );
    }

    await _initializeAndRunApp();
  }, (error, stackTrace) {
    // Global zone error handler - catches all uncaught async errors
    // معالج أخطاء المنطقة العامة - يلتقط جميع الأخطاء غير المتزامنة
    AppLogger.critical('Uncaught error: $error',
        tag: 'Main', error: error, stackTrace: stackTrace);

    crashReporter.reportError(
      error,
      stackTrace,
      severity: CrashSeverity.fatal,
      reason: 'Uncaught zone error',
      fatal: true,
    );
  });
}

/// Initialize database, sync engine, and run the main app.
/// Extracted from main() so that [_continueAppInitialization] can call it
/// without re-running security checks or re-initializing bindings/zones,
/// which would cause infinite recursion.
Future<void> _initializeAndRunApp({bool skipSecurityCheck = false}) async {
  // Initialize database
  AppLogger.i('Initializing database...', tag: 'Main');
  final database = AppDatabase();

  // Initialize preferences manager
  final preferencesManager = PreferencesManager();
  await preferencesManager.initialize();

  // Initialize draft manager
  final draftManager = DraftManager();
  await draftManager.initialize();

  // Initialize app state manager
  final appStateManager = AppStateManager();
  await appStateManager.initialize();

  // Initialize sync engine
  final syncEngine = SyncEngine(database: database);

  // Register background sync task
  try {
    await BackgroundSyncManager.registerPeriodicSync();
    AppLogger.i('Background sync registered', tag: 'Main');
  } catch (e) {
    AppLogger.w('Background sync registration failed: $e', tag: 'Main');
  }

  AppLogger.i('App initialization complete', tag: 'Main');

  // Run the app with provider overrides
  runApp(
    ProviderScope(
      overrides: [
        databaseProvider.overrideWithValue(database),
        syncEngineProvider.overrideWithValue(syncEngine),
      ],
      child: SahoolAppWithLifecycle(
        appStateManager: appStateManager,
        draftManager: draftManager,
        syncEngine: syncEngine,
        child: const SahoolFieldApp(),
      ),
    ),
  );
}

// Global providers
final databaseProvider = Provider<AppDatabase>((ref) {
  throw UnimplementedError('Database not initialized');
});

final syncEngineProvider = Provider<SyncEngine>((ref) {
  throw UnimplementedError('SyncEngine not initialized');
});

final crashReportingProvider =
    Provider<legacy_crash.CrashReportingService>((ref) {
  return legacy_crash.CrashReportingService();
});

// New Crash Reporter provider (with Sentry integration)
final newCrashReporterProvider = Provider<CrashReporter>((ref) {
  return CrashReporter.instance;
});

// Breadcrumb service provider
final breadcrumbServiceProvider = Provider<BreadcrumbService>((ref) {
  return breadcrumbService;
});

// ============================================================
// App Lifecycle Widget
// ============================================================

/// Widget that wraps the app with lifecycle observation
/// ويدجت يغلف التطبيق بمراقبة دورة الحياة
class SahoolAppWithLifecycle extends StatefulWidget {
  final AppStateManager appStateManager;
  final DraftManager draftManager;
  final SyncEngine? syncEngine;
  final Widget child;

  const SahoolAppWithLifecycle({
    super.key,
    required this.appStateManager,
    required this.draftManager,
    this.syncEngine,
    required this.child,
  });

  @override
  State<SahoolAppWithLifecycle> createState() => _SahoolAppWithLifecycleState();
}

class _SahoolAppWithLifecycleState extends State<SahoolAppWithLifecycle>
    with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    AppLogger.d('App lifecycle observer registered', tag: 'Lifecycle');

    // Record app start
    breadcrumbService.recordLifecycle('app_lifecycle_observer_registered');
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    widget.draftManager.dispose();
    widget.syncEngine?.dispose();
    AppLogger.d('App lifecycle observer unregistered', tag: 'Lifecycle');
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    AppLogger.d('App lifecycle state changed: $state', tag: 'Lifecycle');

    switch (state) {
      case AppLifecycleState.paused:
        _handleAppPaused();
        break;
      case AppLifecycleState.inactive:
        _handleAppInactive();
        break;
      case AppLifecycleState.resumed:
        _handleAppResumed();
        break;
      case AppLifecycleState.detached:
        _handleAppDetached();
        break;
      case AppLifecycleState.hidden:
        _handleAppHidden();
        break;
    }
  }

  /// Handle app going to background (paused)
  /// معالجة انتقال التطبيق إلى الخلفية
  void _handleAppPaused() {
    AppLogger.i('App paused - saving state', tag: 'Lifecycle');
    breadcrumbService.recordLifecycle('app_paused');
    crashReporting.recordBreadcrumb(
      message: 'App paused',
      category: 'lifecycle',
      level: legacy_crash.BreadcrumbLevel.info,
    );

    // Save app state when going to background
    widget.appStateManager.onAppBackgrounded();
  }

  /// Handle app becoming inactive (e.g., phone call)
  /// معالجة عدم نشاط التطبيق
  void _handleAppInactive() {
    AppLogger.d('App inactive', tag: 'Lifecycle');
    breadcrumbService.recordLifecycle('app_inactive');
  }

  /// Handle app coming to foreground (resumed)
  /// معالجة عودة التطبيق إلى المقدمة
  void _handleAppResumed() {
    AppLogger.i('App resumed', tag: 'Lifecycle');
    breadcrumbService.recordLifecycle('app_resumed');
    crashReporting.recordBreadcrumb(
      message: 'App resumed',
      category: 'lifecycle',
      level: legacy_crash.BreadcrumbLevel.info,
    );

    // Restore app state when coming to foreground
    widget.appStateManager.onAppResumed();

    // Check if session expired (optional - for security)
    if (widget.appStateManager
        .isSessionExpired(timeout: const Duration(hours: 24))) {
      AppLogger.w('Session may be expired - consider re-authentication',
          tag: 'Lifecycle');
      breadcrumbService.recordSystem('session_expired_warning');
    }
  }

  /// Handle app being detached
  /// معالجة فصل التطبيق
  void _handleAppDetached() {
    AppLogger.d('App detached', tag: 'Lifecycle');
    breadcrumbService.recordLifecycle('app_detached');
  }

  /// Handle app being hidden (iOS only)
  /// معالجة إخفاء التطبيق
  void _handleAppHidden() {
    AppLogger.d('App hidden', tag: 'Lifecycle');
    breadcrumbService.recordLifecycle('app_hidden');
  }

  @override
  Widget build(BuildContext context) {
    return widget.child;
  }
}
