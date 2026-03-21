/// SAHOOL Crash Reporting Configuration
/// تكوين تقارير الأعطال
///
/// Centralized configuration for crash reporting, Sentry integration,
/// and error filtering settings.
///
/// Usage:
/// ```dart
/// final config = CrashConfig.fromEnvironment();
/// await crashReporter.initialize(config);
/// ```
library;

import 'package:flutter/foundation.dart';
import '../config/env_config.dart';

/// Configuration for crash reporting behavior
/// تكوين سلوك تقارير الأعطال
class CrashConfig {
  /// Sentry DSN from environment
  final String sentryDsn;

  /// Environment name for Sentry (development, staging, production)
  final String environment;

  /// Application version
  final String appVersion;

  /// Build number
  final String buildNumber;

  /// Whether crash reporting is enabled
  final bool enabled;

  /// Sampling rate for errors (0.0 to 1.0)
  /// 1.0 = capture all errors, 0.5 = capture 50%
  final double sampleRate;

  /// Sampling rate for performance traces (0.0 to 1.0)
  final double tracesSampleRate;

  /// Maximum number of breadcrumbs to store
  final int maxBreadcrumbs;

  /// Whether to attach stack traces to all events
  final bool attachStacktrace;

  /// Whether to enable automatic session tracking
  final bool enableAutoSessionTracking;

  /// Session timeout in milliseconds
  final int sessionTimeout;

  /// Whether to report in debug mode
  final bool reportInDebug;

  /// List of error messages to ignore
  final List<String> ignoredErrors;

  /// List of sensitive field names to filter from reports
  final List<String> sensitiveFields;

  /// Maximum offline reports to store
  final int maxOfflineReports;

  /// Whether to enable offline crash storage
  final bool enableOfflineStorage;

  /// Release name format (e.g., "sahool-field@16.0.0+1")
  final String release;

  /// Distribution identifier
  final String? dist;

  const CrashConfig({
    required this.sentryDsn,
    required this.environment,
    required this.appVersion,
    required this.buildNumber,
    this.enabled = true,
    this.sampleRate = 1.0,
    this.tracesSampleRate = 0.2,
    this.maxBreadcrumbs = 100,
    this.attachStacktrace = true,
    this.enableAutoSessionTracking = true,
    this.sessionTimeout = 30000,
    this.reportInDebug = false,
    this.ignoredErrors = const [],
    this.sensitiveFields = const [],
    this.maxOfflineReports = 50,
    this.enableOfflineStorage = true,
    this.release = '',
    this.dist,
  });

  /// Create configuration from environment variables
  /// إنشاء التكوين من متغيرات البيئة
  factory CrashConfig.fromEnvironment() {
    final dsn = EnvConfig.sentryDsn;
    final environment = EnvConfig.sentryEnvironment;
    final appVersion = EnvConfig.appVersion;
    final buildNumber = EnvConfig.buildNumber;

    // Only enable if DSN is provided and crash reporting is enabled
    final enabled = dsn.isNotEmpty && EnvConfig.enableCrashReporting;

    return CrashConfig(
      sentryDsn: dsn,
      environment: environment,
      appVersion: appVersion,
      buildNumber: buildNumber,
      enabled: enabled,
      sampleRate: _getSampleRateForEnvironment(environment),
      tracesSampleRate: _getTracesSampleRateForEnvironment(environment),
      maxBreadcrumbs: 100,
      attachStacktrace: true,
      enableAutoSessionTracking: true,
      sessionTimeout: 30000,
      reportInDebug: false,
      ignoredErrors: _defaultIgnoredErrors,
      sensitiveFields: _defaultSensitiveFields,
      maxOfflineReports: 50,
      enableOfflineStorage: true,
      release: 'sahool-field@$appVersion+$buildNumber',
      dist: buildNumber,
    );
  }

  /// Create a test configuration (no actual reporting)
  /// إنشاء تكوين للاختبار
  factory CrashConfig.test() {
    return const CrashConfig(
      sentryDsn: '',
      environment: 'test',
      appVersion: '0.0.0',
      buildNumber: '0',
      enabled: false,
      reportInDebug: false,
      enableOfflineStorage: false,
    );
  }

  /// Create development configuration (console only)
  /// تكوين التطوير (وحدة التحكم فقط)
  factory CrashConfig.development() {
    return CrashConfig(
      sentryDsn: '',
      environment: 'development',
      appVersion: EnvConfig.appVersion,
      buildNumber: EnvConfig.buildNumber,
      enabled: true,
      reportInDebug: kDebugMode,
      sampleRate: 1.0,
      tracesSampleRate: 1.0,
      enableOfflineStorage: true,
    );
  }

  /// Get sample rate based on environment
  static double _getSampleRateForEnvironment(String environment) {
    switch (environment.toLowerCase()) {
      case 'production':
        return 1.0; // Capture all in production
      case 'staging':
        return 1.0; // Capture all in staging for testing
      case 'development':
        return 0.5; // Sample in development
      default:
        return 1.0;
    }
  }

  /// Get traces sample rate based on environment
  static double _getTracesSampleRateForEnvironment(String environment) {
    switch (environment.toLowerCase()) {
      case 'production':
        return 0.2; // 20% of traces in production
      case 'staging':
        return 0.5; // 50% in staging
      case 'development':
        return 1.0; // All traces in development
      default:
        return 0.2;
    }
  }

  /// Default errors to ignore
  static const List<String> _defaultIgnoredErrors = [
    // Network errors that are expected in offline-first app
    'SocketException',
    'HttpException',
    'TimeoutException',
    'HandshakeException',
    'ClientException',
    // User-initiated actions
    'CancelledException',
    'UserCancelledException',
    // Background task interruptions
    'BackgroundFetch cancelled',
    // Expected Flutter framework errors
    'Looking up a deactivated widget',
    'setState() called after dispose()',
    // Image loading failures (common in low connectivity)
    'NetworkImageLoadException',
    'Image codec error',
  ];

  /// Default sensitive fields to redact
  static const List<String> _defaultSensitiveFields = [
    'password',
    'pwd',
    'secret',
    'token',
    'auth',
    'authorization',
    'api_key',
    'apikey',
    'accessToken',
    'access_token',
    'refreshToken',
    'refresh_token',
    'privateKey',
    'private_key',
    'credit_card',
    'creditCard',
    'cvv',
    'ssn',
    'social_security',
    'national_id',
    'nationalId',
    'passport',
    'license',
    'phone',
    'email',
    'otp',
    'pin',
  ];

  /// Check if an error should be ignored
  bool shouldIgnoreError(dynamic error) {
    final errorString = error.toString().toLowerCase();

    for (final pattern in ignoredErrors) {
      if (errorString.contains(pattern.toLowerCase())) {
        return true;
      }
    }

    return false;
  }

  /// Check if Sentry is configured
  bool get hasSentryDsn => sentryDsn.isNotEmpty;

  /// Check if should report errors
  bool get shouldReport {
    if (!enabled) return false;
    if (kDebugMode && !reportInDebug) return false;
    return true;
  }

  /// Create a copy with modified fields
  CrashConfig copyWith({
    String? sentryDsn,
    String? environment,
    String? appVersion,
    String? buildNumber,
    bool? enabled,
    double? sampleRate,
    double? tracesSampleRate,
    int? maxBreadcrumbs,
    bool? attachStacktrace,
    bool? enableAutoSessionTracking,
    int? sessionTimeout,
    bool? reportInDebug,
    List<String>? ignoredErrors,
    List<String>? sensitiveFields,
    int? maxOfflineReports,
    bool? enableOfflineStorage,
    String? release,
    String? dist,
  }) {
    return CrashConfig(
      sentryDsn: sentryDsn ?? this.sentryDsn,
      environment: environment ?? this.environment,
      appVersion: appVersion ?? this.appVersion,
      buildNumber: buildNumber ?? this.buildNumber,
      enabled: enabled ?? this.enabled,
      sampleRate: sampleRate ?? this.sampleRate,
      tracesSampleRate: tracesSampleRate ?? this.tracesSampleRate,
      maxBreadcrumbs: maxBreadcrumbs ?? this.maxBreadcrumbs,
      attachStacktrace: attachStacktrace ?? this.attachStacktrace,
      enableAutoSessionTracking:
          enableAutoSessionTracking ?? this.enableAutoSessionTracking,
      sessionTimeout: sessionTimeout ?? this.sessionTimeout,
      reportInDebug: reportInDebug ?? this.reportInDebug,
      ignoredErrors: ignoredErrors ?? this.ignoredErrors,
      sensitiveFields: sensitiveFields ?? this.sensitiveFields,
      maxOfflineReports: maxOfflineReports ?? this.maxOfflineReports,
      enableOfflineStorage: enableOfflineStorage ?? this.enableOfflineStorage,
      release: release ?? this.release,
      dist: dist ?? this.dist,
    );
  }

  @override
  String toString() {
    return 'CrashConfig('
        'enabled: $enabled, '
        'environment: $environment, '
        'hasDsn: $hasSentryDsn, '
        'sampleRate: $sampleRate, '
        'maxBreadcrumbs: $maxBreadcrumbs'
        ')';
  }
}

/// Severity levels for crash reports
/// مستويات خطورة تقارير الأعطال
enum CrashSeverity {
  /// Debug information (not sent in production)
  debug,

  /// Informational event
  info,

  /// Warning event (potential issue)
  warning,

  /// Error event (non-fatal)
  error,

  /// Fatal error (app crash)
  fatal,
}

/// Extension to convert severity to Sentry level
extension CrashSeverityExtension on CrashSeverity {
  /// Get the string representation for Sentry
  String get sentryLevel {
    switch (this) {
      case CrashSeverity.debug:
        return 'debug';
      case CrashSeverity.info:
        return 'info';
      case CrashSeverity.warning:
        return 'warning';
      case CrashSeverity.error:
        return 'error';
      case CrashSeverity.fatal:
        return 'fatal';
    }
  }

  /// Check if this severity should be reported
  bool shouldReport(CrashConfig config) {
    if (!config.shouldReport) return false;

    // Debug level only reported in debug mode
    if (this == CrashSeverity.debug && !kDebugMode) return false;

    return true;
  }
}
