/// SAHOOL Crash Reporting Module
/// وحدة تقارير الأعطال
///
/// Comprehensive crash reporting with Sentry integration,
/// offline storage, breadcrumb tracking, and PII filtering.
///
/// Features:
/// - Sentry SDK integration (when SENTRY_DSN is configured)
/// - Flutter error capture
/// - Dart async error capture
/// - Native crash capture
/// - Navigation breadcrumbs
/// - User action breadcrumbs
/// - Sensitive data filtering (no passwords, tokens, PII)
/// - Offline crash report storage
/// - Custom tags (app version, device type)
/// - User context (anonymized)
///
/// Usage:
/// ```dart
/// import 'package:sahool_field_app/core/crash/crash.dart';
///
/// // Initialize in main.dart
/// await crashReporter.initialize(CrashConfig.fromEnvironment());
///
/// // Report errors manually
/// crashReporter.reportError(error, stackTrace);
///
/// // Add breadcrumbs
/// crashReporter.addBreadcrumb('User tapped button');
/// breadcrumbService.recordNavigation('/home', '/fields');
///
/// // Set user context
/// crashReporter.setUserContext(userId: 'user123');
/// ```
///
/// Configuration (via environment variables):
/// - SENTRY_DSN: Sentry project DSN
/// - SENTRY_ENVIRONMENT: Environment name (development, staging, production)
/// - ENABLE_CRASH_REPORTING: Enable/disable crash reporting (default: true in production)
///
/// The module automatically:
/// - Captures Flutter framework errors
/// - Captures Dart async errors
/// - Filters sensitive data (passwords, tokens, emails, phone numbers)
/// - Stores crash reports offline when network is unavailable
/// - Sends pending reports when network is restored
/// - Tracks breadcrumbs for debugging

library;

// Configuration
export 'crash_config.dart'
    show
        CrashConfig,
        CrashSeverity,
        CrashSeverityExtension;

// Breadcrumb service
export 'breadcrumb_service.dart'
    show
        Breadcrumb,
        BreadcrumbCategory,
        BreadcrumbLevel,
        BreadcrumbService,
        breadcrumbService,
        NavigationBreadcrumbExtension,
        FieldBreadcrumbExtension;

// Main crash reporter
export 'crash_reporter.dart'
    show
        CrashReporter,
        CrashUserContext,
        CrashDeviceContext,
        OfflineCrashReport,
        crashReporter;
