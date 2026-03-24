/// SAHOOL Unified App - Entry Point
/// نقطة دخول تطبيق سهول الموحد
///
/// Thin wrapper that initializes the app using sahool_mobile_core.
/// غلاف رقيق يقوم بتهيئة التطبيق باستخدام الحزمة الأساسية.
import 'dart:async';
import 'dart:ui';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Core package imports - استيراد الحزمة الأساسية
import 'package:sahool_mobile_core/core/config/env_config.dart';
import 'package:sahool_mobile_core/core/crash/crash_reporter.dart';
import 'package:sahool_mobile_core/core/error/error.dart';
import 'package:sahool_mobile_core/core/persistence/app_state_manager.dart';
import 'package:sahool_mobile_core/core/persistence/preferences_manager.dart';
import 'package:sahool_mobile_core/core/persistence/draft_manager.dart';
import 'package:sahool_mobile_core/core/security/device_integrity_service.dart';
import 'package:sahool_mobile_core/core/security/device_security_screen.dart';
import 'package:sahool_mobile_core/core/security/security_config.dart';
import 'package:sahool_mobile_core/core/services/crash_reporting_service.dart'
    as legacy_crash;
import 'package:sahool_mobile_core/core/storage/database.dart';
import 'package:sahool_mobile_core/core/sync/sync_engine.dart';
import 'package:sahool_mobile_core/core/sync/background_sync_task.dart';
import 'package:sahool_mobile_core/core/utils/app_logger.dart';

import 'app.dart';

// Global crash reporting instance (legacy - kept for compatibility)
// مثيل تقارير الأعطال العالمي (قديم - محفوظ للتوافقية)
final crashReporting = legacy_crash.CrashReportingService();

/// Guard against infinite recursion when user bypasses security warning.
bool _securityBypassRestart = false;

void main() async {
  // Ensure Flutter bindings are initialized first
  // تأكد من تهيئة ارتباطات Flutter أولاً
  WidgetsFlutterBinding.ensureInitialized();

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
  // التقاط جميع الأخطاء غير المتزامنة في المنطقة
  await runZonedGuarded(() async {
    // Load environment configuration first (non-critical)
    try {
      await EnvConfig.load();
    } catch (e) {
      AppLogger.w('EnvConfig load failed: $e', tag: 'Main');
      // Continue anyway - defaults will be used
    }

    // Initialize new CrashReporter with Sentry integration
    // تهيئة مُبلّغ الأعطال الجديد مع تكامل Sentry
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
    // تهيئة مُبلّغ الأخطاء (طبقة معالجة الأخطاء الموحدة)
    try {
      await errorReporter.initialize();
      AppLogger.i('ErrorReporter initialized', tag: 'Main');
    } catch (e) {
      AppLogger.w('ErrorReporter init failed (non-critical): $e', tag: 'Main');
    }

    // Initialize legacy crash reporting (delegates to primary CrashReporter)
    // تهيئة تقارير الأعطال القديمة (تفوض للمُبلّغ الأساسي)
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
    // Skip if restarting after user bypassed security warning
    final securityConfig = SecurityConfig.fromBuildMode();
    AppLogger.d('Security config: $securityConfig', tag: 'Security');

    // Perform device integrity check if enabled (skip on security bypass restart)
    if (!_securityBypassRestart &&
        securityConfig.deviceIntegrityPolicy !=
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
                        // Continue app initialization safely (skip security re-check).
                        // Wrapped in runZonedGuarded to maintain error handling.
                        _securityBypassRestart = true;
                        runZonedGuarded(() async {
                          await _initializeAndRunApp();
                        }, (error, stackTrace) {
                          AppLogger.critical('Uncaught error after security bypass: $error',
                              tag: 'Main', error: error, stackTrace: stackTrace);
                          crashReporter.reportError(
                            error,
                            stackTrace,
                            severity: CrashSeverity.fatal,
                            reason: 'Uncaught zone error (security bypass)',
                            fatal: true,
                          );
                        });
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

/// Initialize database, sync, persistence and run the app.
/// Extracted to avoid duplicating initialization when user bypasses security.
/// تهيئة قاعدة البيانات والمزامنة وتشغيل التطبيق.
Future<void> _initializeAndRunApp() async {
    // Initialize database
    // تهيئة قاعدة البيانات
    late AppDatabase database;
    try {
      crashReporting.recordBreadcrumb(
        message: 'Initializing database',
        category: 'lifecycle',
        level: legacy_crash.BreadcrumbLevel.info,
      );
      database = AppDatabase();
      crashReporting.recordBreadcrumb(
        message: 'Database initialized successfully',
        category: 'lifecycle',
        level: legacy_crash.BreadcrumbLevel.info,
      );
    } catch (e, stackTrace) {
      AppLogger.critical('Database initialization failed: $e',
          tag: 'Main', error: e, stackTrace: stackTrace);
      crashReporting.reportError(
        e,
        stackTrace,
        severity: legacy_crash.ErrorSeverity.fatal,
        reason: 'Database initialization failed',
        fatal: true,
      );
      rethrow;
    }

    // Initialize sync engine
    // تهيئة محرك المزامنة
    late SyncEngine syncEngine;
    try {
      crashReporting.recordBreadcrumb(
        message: 'Initializing sync engine',
        category: 'lifecycle',
        level: legacy_crash.BreadcrumbLevel.info,
      );
      syncEngine = SyncEngine(database: database);
      crashReporting.recordBreadcrumb(
        message: 'Sync engine initialized successfully',
        category: 'lifecycle',
        level: legacy_crash.BreadcrumbLevel.info,
      );
    } catch (e, stackTrace) {
      AppLogger.critical('SyncEngine initialization failed: $e',
          tag: 'Main', error: e, stackTrace: stackTrace);
      crashReporting.reportError(
        e,
        stackTrace,
        severity: legacy_crash.ErrorSeverity.fatal,
        reason: 'SyncEngine initialization failed',
        fatal: true,
      );
      rethrow;
    }

    // Initialize background sync with Workmanager (non-critical)
    // تهيئة المزامنة الخلفية مع Workmanager (غير حرج)
    try {
      crashReporting.recordBreadcrumb(
        message: 'Initializing background sync',
        category: 'lifecycle',
        level: legacy_crash.BreadcrumbLevel.info,
      );
      await BackgroundSyncManager.initialize();
      await BackgroundSyncManager.registerPeriodicSync();
      AppLogger.i('Background sync initialized', tag: 'Main');
      crashReporting.recordBreadcrumb(
        message: 'Background sync initialized successfully',
        category: 'lifecycle',
        level: legacy_crash.BreadcrumbLevel.info,
      );
    } catch (e, stackTrace) {
      // Non-critical - app can work without background sync
      AppLogger.w('Background sync init failed (non-critical): $e',
          tag: 'Main');
      crashReporting.reportError(
        e,
        stackTrace,
        severity: legacy_crash.ErrorSeverity.warning,
        reason: 'Background sync initialization failed (non-critical)',
        fatal: false,
      );
    }

    // Initialize persistence managers (non-critical)
    // تهيئة مديري الحفظ (غير حرج)
    final appStateManager = AppStateManager();
    final preferencesManager = PreferencesManager();
    final draftManager = DraftManager();

    try {
      crashReporting.recordBreadcrumb(
        message: 'Initializing persistence managers',
        category: 'lifecycle',
        level: legacy_crash.BreadcrumbLevel.info,
      );

      await Future.wait([
        appStateManager.initialize(),
        preferencesManager.initialize(),
        draftManager.initialize(),
      ]);

      AppLogger.i('Persistence managers initialized', tag: 'Main');
      crashReporting.recordBreadcrumb(
        message: 'Persistence managers initialized successfully',
        category: 'lifecycle',
        level: legacy_crash.BreadcrumbLevel.info,
      );
    } catch (e, stackTrace) {
      // Non-critical - app can work without persistence
      AppLogger.w('Persistence managers init failed (non-critical): $e',
          tag: 'Main');
      crashReporting.reportError(
        e,
        stackTrace,
        severity: legacy_crash.ErrorSeverity.warning,
        reason: 'Persistence managers initialization failed (non-critical)',
        fatal: false,
      );
    }

    // Run the app
    // تشغيل التطبيق
    crashReporting.recordBreadcrumb(
      message: 'Starting Flutter app',
      category: 'lifecycle',
      level: legacy_crash.BreadcrumbLevel.info,
    );

    runApp(
      ProviderScope(
        overrides: [
          databaseProvider.overrideWithValue(database),
          syncEngineProvider.overrideWithValue(syncEngine),
          appStateManagerProvider.overrideWithValue(appStateManager),
          preferencesManagerProvider.overrideWithValue(preferencesManager),
          draftManagerProvider.overrideWithValue(draftManager),
        ],
        child: SahoolAppWithLifecycle(
          appStateManager: appStateManager,
          draftManager: draftManager,
          child: const SahoolApp(),
        ),
      ),
    );

    // Start foreground sync when app is active (non-blocking)
    // بدء المزامنة الأمامية عندما يكون التطبيق نشطاً (غير معطل)
    try {
      breadcrumbService.recordSync('foreground', success: true);
      crashReporting.recordBreadcrumb(
        message: 'Starting foreground sync',
        category: 'lifecycle',
        level: legacy_crash.BreadcrumbLevel.info,
      );
      syncEngine.startPeriodic();
    } catch (e, stackTrace) {
      AppLogger.w('Foreground sync start failed: $e', tag: 'Main');
      breadcrumbService.recordSync('foreground', success: false);
      crashReporter.reportError(
        e,
        stackTrace,
        severity: CrashSeverity.warning,
        reason: 'Foreground sync start failed (non-critical)',
        fatal: false,
      );
      crashReporting.reportError(
        e,
        stackTrace,
        severity: legacy_crash.ErrorSeverity.warning,
        reason: 'Foreground sync start failed (non-critical)',
        fatal: false,
      );
    }
}

// ============================================================
// Global Providers - المزودون العالميون
// ============================================================

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
// مزود مُبلّغ الأعطال الجديد (مع تكامل Sentry)
final newCrashReporterProvider = Provider<CrashReporter>((ref) {
  return CrashReporter.instance;
});

// Breadcrumb service provider
// مزود خدمة فتات الخبز
final breadcrumbServiceProvider = Provider<BreadcrumbService>((ref) {
  return breadcrumbService;
});

// ============================================================
// App Lifecycle Widget - ويدجت دورة حياة التطبيق
// ============================================================

/// Widget that wraps the app with lifecycle observation
/// ويدجت يغلف التطبيق بمراقبة دورة الحياة
class SahoolAppWithLifecycle extends StatefulWidget {
  final AppStateManager appStateManager;
  final DraftManager draftManager;
  final Widget child;

  const SahoolAppWithLifecycle({
    super.key,
    required this.appStateManager,
    required this.draftManager,
    required this.child,
  });

  @override
  State<SahoolAppWithLifecycle> createState() =>
      _SahoolAppWithLifecycleState();
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
