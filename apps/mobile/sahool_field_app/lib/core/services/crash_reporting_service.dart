/// SAHOOL Crash Reporting Service
/// خدمة تتبع الأعطال والأخطاء
///
/// Handles error reporting, crash tracking, and debugging support
/// Sanitizes PII, tracks breadcrumbs, and supports multiple providers

import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';
import '../config/env_config.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Enums & Data Models
// ═══════════════════════════════════════════════════════════════════════════

/// Error severity levels
enum ErrorSeverity {
  debug,
  info,
  warning,
  error,
  fatal,
}

/// Breadcrumb for tracking user actions leading to errors
class Breadcrumb {
  final String message;
  final DateTime timestamp;
  final String? category;
  final Map<String, dynamic>? data;
  final BreadcrumbLevel level;

  Breadcrumb({
    required this.message,
    DateTime? timestamp,
    this.category,
    this.data,
    this.level = BreadcrumbLevel.info,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toJson() {
    return {
      'message': message,
      'timestamp': timestamp.toIso8601String(),
      if (category != null) 'category': category,
      if (data != null) 'data': data,
      'level': level.name,
    };
  }
}

enum BreadcrumbLevel {
  debug,
  info,
  warning,
  error,
}

/// User context for crash reporting (anonymized)
class UserContext {
  final String anonymousId;
  final String? tenantId;
  final String? role;
  final Map<String, dynamic>? metadata;

  const UserContext({
    required this.anonymousId,
    this.tenantId,
    this.role,
    this.metadata,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': anonymousId,
      if (tenantId != null) 'tenantId': tenantId,
      if (role != null) 'role': role,
      if (metadata != null) ...metadata!,
    };
  }
}

/// Device and app context
class AppContext {
  final String appVersion;
  final String buildNumber;
  final String environment;
  final String platform;
  final String? osVersion;
  final String? deviceModel;
  final String? locale;

  const AppContext({
    required this.appVersion,
    required this.buildNumber,
    required this.environment,
    required this.platform,
    this.osVersion,
    this.deviceModel,
    this.locale,
  });

  Map<String, dynamic> toJson() {
    return {
      'version': appVersion,
      'build': buildNumber,
      'environment': environment,
      'platform': platform,
      if (osVersion != null) 'osVersion': osVersion,
      if (deviceModel != null) 'deviceModel': deviceModel,
      if (locale != null) 'locale': locale,
    };
  }
}

/// Error report data structure
class ErrorReport {
  final dynamic error;
  final StackTrace? stackTrace;
  final ErrorSeverity severity;
  final String? reason;
  final Map<String, dynamic>? customData;
  final DateTime timestamp;
  final bool fatal;

  ErrorReport({
    required this.error,
    this.stackTrace,
    this.severity = ErrorSeverity.error,
    this.reason,
    this.customData,
    DateTime? timestamp,
    this.fatal = false,
  }) : timestamp = timestamp ?? DateTime.now();
}

// ═══════════════════════════════════════════════════════════════════════════
// Abstract Interface
// ═══════════════════════════════════════════════════════════════════════════

/// Abstract crash reporting provider interface
/// Allows multiple implementations (Firebase Crashlytics, Sentry, etc.)
abstract class CrashReportingProvider {
  /// Initialize the crash reporting provider
  Future<void> initialize();

  /// Report an error
  Future<void> reportError(ErrorReport report);

  /// Record a breadcrumb
  Future<void> recordBreadcrumb(Breadcrumb breadcrumb);

  /// Set user context
  Future<void> setUserContext(UserContext? user);

  /// Set app context
  Future<void> setAppContext(AppContext context);

  /// Set custom key-value pairs
  Future<void> setCustomKey(String key, dynamic value);

  /// Enable/disable crash reporting
  Future<void> setEnabled(bool enabled);

  /// Check if provider is enabled
  bool get isEnabled;

  /// Provider name for debugging
  String get name;
}

// ═══════════════════════════════════════════════════════════════════════════
// Console Provider (Default/Fallback)
// ═══════════════════════════════════════════════════════════════════════════

/// Console-based crash reporting (for development/fallback)
class ConsoleCrashReportingProvider implements CrashReportingProvider {
  bool _enabled = true;

  @override
  String get name => 'Console';

  @override
  bool get isEnabled => _enabled;

  @override
  Future<void> initialize() async {
    debugPrint('✅ Console crash reporting initialized');
  }

  @override
  Future<void> reportError(ErrorReport report) async {
    if (!_enabled) return;

    final severity = report.severity.name.toUpperCase();
    final timestamp = report.timestamp.toIso8601String();

    debugPrint('');
    debugPrint('╔════════════════════════════════════════════════════════════╗');
    debugPrint('║  CRASH REPORT [$severity]${' ' * (44 - severity.length)}║');
    debugPrint('╠════════════════════════════════════════════════════════════╣');
    debugPrint('║ Time: ${timestamp.padRight(51)}║');
    if (report.reason != null) {
      debugPrint('║ Reason: ${report.reason!.padRight(49)}║');
    }
    debugPrint('╠════════════════════════════════════════════════════════════╣');
    debugPrint('║ Error: ${report.error.toString().substring(0, report.error.toString().length > 50 ? 50 : report.error.toString().length).padRight(50)}║');
    if (report.stackTrace != null) {
      debugPrint('╠════════════════════════════════════════════════════════════╣');
      debugPrint('║ Stack Trace:                                               ║');
      final stackLines = report.stackTrace.toString().split('\n');
      for (var i = 0; i < (stackLines.length < 10 ? stackLines.length : 10); i++) {
        final line = stackLines[i].substring(0, stackLines[i].length > 56 ? 56 : stackLines[i].length);
        debugPrint('║ $line${' ' * (58 - line.length)}║');
      }
    }
    debugPrint('╚════════════════════════════════════════════════════════════╝');
    debugPrint('');
  }

  @override
  Future<void> recordBreadcrumb(Breadcrumb breadcrumb) async {
    if (!_enabled) return;
    debugPrint('🍞 Breadcrumb: [${breadcrumb.category ?? 'general'}] ${breadcrumb.message}');
  }

  @override
  Future<void> setUserContext(UserContext? user) async {
    if (!_enabled) return;
    if (user != null) {
      debugPrint('👤 User context set: ${user.anonymousId}');
    } else {
      debugPrint('👤 User context cleared');
    }
  }

  @override
  Future<void> setAppContext(AppContext context) async {
    if (!_enabled) return;
    debugPrint('📱 App context: ${context.appVersion} (${context.environment})');
  }

  @override
  Future<void> setCustomKey(String key, dynamic value) async {
    if (!_enabled) return;
    debugPrint('🔧 Custom key: $key = $value');
  }

  @override
  Future<void> setEnabled(bool enabled) async {
    _enabled = enabled;
    debugPrint('Console crash reporting ${enabled ? 'enabled' : 'disabled'}');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// PII Sanitization
// ═══════════════════════════════════════════════════════════════════════════

class PIISanitizer {
  // Patterns for PII detection
  static final _emailPattern = RegExp(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
  );
  static final _phonePattern = RegExp(
    r'\b(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b',
  );
  static final _creditCardPattern = RegExp(
    r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
  );
  static final _ssnPattern = RegExp(
    r'\b\d{3}-\d{2}-\d{4}\b',
  );
  static final _ipPattern = RegExp(
    r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
  );

  /// Sanitize string by removing PII
  static String sanitizeString(String input) {
    String sanitized = input;

    // Remove email addresses
    sanitized = sanitized.replaceAll(_emailPattern, '[EMAIL_REDACTED]');

    // Remove phone numbers
    sanitized = sanitized.replaceAll(_phonePattern, '[PHONE_REDACTED]');

    // Remove credit card numbers
    sanitized = sanitized.replaceAll(_creditCardPattern, '[CARD_REDACTED]');

    // Remove SSN
    sanitized = sanitized.replaceAll(_ssnPattern, '[SSN_REDACTED]');

    // Keep IP addresses but mask last octet (for debugging purposes)
    sanitized = sanitized.replaceAllMapped(
      _ipPattern,
      (match) => '${match.group(0)!.substring(0, match.group(0)!.lastIndexOf('.'))}.XXX',
    );

    return sanitized;
  }

  /// Sanitize map by removing PII from values
  static Map<String, dynamic> sanitizeMap(Map<String, dynamic> input) {
    final sanitized = <String, dynamic>{};

    for (final entry in input.entries) {
      final key = entry.key.toLowerCase();

      // Remove sensitive keys entirely
      if (_isSensitiveKey(key)) {
        sanitized[entry.key] = '[REDACTED]';
        continue;
      }

      // Sanitize values
      final value = entry.value;
      if (value is String) {
        sanitized[entry.key] = sanitizeString(value);
      } else if (value is Map<String, dynamic>) {
        sanitized[entry.key] = sanitizeMap(value);
      } else if (value is List) {
        sanitized[entry.key] = value.map((item) {
          if (item is String) return sanitizeString(item);
          if (item is Map<String, dynamic>) return sanitizeMap(item);
          return item;
        }).toList();
      } else {
        sanitized[entry.key] = value;
      }
    }

    return sanitized;
  }

  /// Check if key is sensitive
  static bool _isSensitiveKey(String key) {
    const sensitiveKeys = [
      'password',
      'pwd',
      'secret',
      'token',
      'auth',
      'authorization',
      'api_key',
      'apikey',
      'access_token',
      'refresh_token',
      'private_key',
      'credit_card',
      'ssn',
      'social_security',
      'passport',
      'license',
    ];

    return sensitiveKeys.any((sensitive) => key.contains(sensitive));
  }

  /// Sanitize stack trace
  static String sanitizeStackTrace(String stackTrace) {
    return sanitizeString(stackTrace);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Main Crash Reporting Service
// ═══════════════════════════════════════════════════════════════════════════

/// Main crash reporting service with multiple provider support
class CrashReportingService {
  static final CrashReportingService _instance = CrashReportingService._internal();
  factory CrashReportingService() => _instance;
  CrashReportingService._internal();

  final List<CrashReportingProvider> _providers = [];
  final List<Breadcrumb> _breadcrumbs = [];

  bool _initialized = false;
  bool _enabled = false;
  double _samplingRate = 1.0;
  int _maxBreadcrumbs = 100;

  UserContext? _userContext;
  AppContext? _appContext;
  final Map<String, dynamic> _customKeys = {};

  /// Initialize crash reporting with providers
  Future<void> initialize({
    List<CrashReportingProvider>? providers,
    double samplingRate = 1.0,
    int maxBreadcrumbs = 100,
  }) async {
    if (_initialized) {
      debugPrint('⚠️ Crash reporting already initialized');
      return;
    }

    // Check if crash reporting is enabled in config
    _enabled = EnvConfig.enableCrashReporting;
    _samplingRate = samplingRate;
    _maxBreadcrumbs = maxBreadcrumbs;

    if (!_enabled) {
      debugPrint('ℹ️ Crash reporting disabled by configuration');
      _initialized = true;
      return;
    }

    // Add provided providers or use console provider as default
    if (providers != null && providers.isNotEmpty) {
      _providers.addAll(providers);
    } else {
      _providers.add(ConsoleCrashReportingProvider());
    }

    // Initialize all providers
    for (final provider in _providers) {
      try {
        await provider.initialize();
        debugPrint('✅ Crash reporting provider initialized: ${provider.name}');
      } catch (e) {
        debugPrint('❌ Failed to initialize provider ${provider.name}: $e');
      }
    }

    // Set up app context
    await _setupAppContext();

    _initialized = true;
    debugPrint('✅ Crash reporting service initialized (${_providers.length} providers)');
  }

  /// Set up app context with device and package info
  Future<void> _setupAppContext() async {
    try {
      final packageInfo = await PackageInfo.fromPlatform();
      final deviceInfo = DeviceInfoPlugin();

      String? osVersion;
      String? deviceModel;

      if (Platform.isAndroid) {
        final androidInfo = await deviceInfo.androidInfo;
        osVersion = 'Android ${androidInfo.version.release}';
        deviceModel = '${androidInfo.manufacturer} ${androidInfo.model}';
      } else if (Platform.isIOS) {
        final iosInfo = await deviceInfo.iosInfo;
        osVersion = 'iOS ${iosInfo.systemVersion}';
        deviceModel = iosInfo.model;
      }

      _appContext = AppContext(
        appVersion: packageInfo.version,
        buildNumber: packageInfo.buildNumber,
        environment: EnvConfig.environment.name,
        platform: Platform.operatingSystem,
        osVersion: osVersion,
        deviceModel: deviceModel,
        locale: Platform.localeName,
      );

      for (final provider in _providers) {
        await provider.setAppContext(_appContext!);
      }
    } catch (e) {
      debugPrint('⚠️ Failed to setup app context: $e');
    }
  }

  /// Report an error to all providers
  Future<void> reportError(
    dynamic error,
    StackTrace? stackTrace, {
    ErrorSeverity severity = ErrorSeverity.error,
    String? reason,
    Map<String, dynamic>? customData,
    bool fatal = false,
  }) async {
    if (!_initialized || !_enabled) return;

    // Apply sampling rate
    if (_samplingRate < 1.0 && _samplingRate < (DateTime.now().millisecondsSinceEpoch % 100) / 100) {
      return;
    }

    // Filter out certain errors if needed
    if (_shouldFilterError(error)) {
      return;
    }

    // Sanitize error data
    final sanitizedError = _sanitizeError(error);
    final sanitizedStackTrace = stackTrace != null
        ? StackTrace.fromString(PIISanitizer.sanitizeStackTrace(stackTrace.toString()))
        : null;
    final sanitizedCustomData = customData != null
        ? PIISanitizer.sanitizeMap(customData)
        : null;

    final report = ErrorReport(
      error: sanitizedError,
      stackTrace: sanitizedStackTrace,
      severity: severity,
      reason: reason != null ? PIISanitizer.sanitizeString(reason) : null,
      customData: sanitizedCustomData,
      fatal: fatal,
    );

    // Add breadcrumb for this error
    recordBreadcrumb(
      message: 'Error: ${sanitizedError.toString().substring(0, sanitizedError.toString().length > 50 ? 50 : sanitizedError.toString().length)}',
      category: 'error',
      level: BreadcrumbLevel.error,
    );

    // Report to all providers
    for (final provider in _providers) {
      try {
        await provider.reportError(report);
      } catch (e) {
        debugPrint('❌ Failed to report error to ${provider.name}: $e');
      }
    }
  }

  /// Record a breadcrumb
  void recordBreadcrumb({
    required String message,
    String? category,
    Map<String, dynamic>? data,
    BreadcrumbLevel level = BreadcrumbLevel.info,
  }) {
    if (!_initialized || !_enabled) return;

    final sanitizedMessage = PIISanitizer.sanitizeString(message);
    final sanitizedData = data != null ? PIISanitizer.sanitizeMap(data) : null;

    final breadcrumb = Breadcrumb(
      message: sanitizedMessage,
      category: category,
      data: sanitizedData,
      level: level,
    );

    _breadcrumbs.add(breadcrumb);

    // Limit breadcrumbs to max size
    if (_breadcrumbs.length > _maxBreadcrumbs) {
      _breadcrumbs.removeAt(0);
    }

    // Send to providers
    for (final provider in _providers) {
      try {
        provider.recordBreadcrumb(breadcrumb);
      } catch (e) {
        // Silently fail breadcrumb recording
      }
    }
  }

  /// Set user context (anonymized)
  Future<void> setUserContext({
    required String anonymousId,
    String? tenantId,
    String? role,
    Map<String, dynamic>? metadata,
  }) async {
    if (!_initialized || !_enabled) return;

    // Sanitize metadata
    final sanitizedMetadata = metadata != null
        ? PIISanitizer.sanitizeMap(metadata)
        : null;

    _userContext = UserContext(
      anonymousId: anonymousId,
      tenantId: tenantId,
      role: role,
      metadata: sanitizedMetadata,
    );

    for (final provider in _providers) {
      try {
        await provider.setUserContext(_userContext);
      } catch (e) {
        debugPrint('❌ Failed to set user context for ${provider.name}: $e');
      }
    }
  }

  /// Clear user context (e.g., on logout)
  Future<void> clearUserContext() async {
    if (!_initialized || !_enabled) return;

    _userContext = null;

    for (final provider in _providers) {
      try {
        await provider.setUserContext(null);
      } catch (e) {
        debugPrint('❌ Failed to clear user context for ${provider.name}: $e');
      }
    }
  }

  /// Set custom key-value pair
  Future<void> setCustomKey(String key, dynamic value) async {
    if (!_initialized || !_enabled) return;

    // Sanitize value
    dynamic sanitizedValue = value;
    if (value is String) {
      sanitizedValue = PIISanitizer.sanitizeString(value);
    } else if (value is Map<String, dynamic>) {
      sanitizedValue = PIISanitizer.sanitizeMap(value);
    }

    _customKeys[key] = sanitizedValue;

    for (final provider in _providers) {
      try {
        await provider.setCustomKey(key, sanitizedValue);
      } catch (e) {
        debugPrint('❌ Failed to set custom key for ${provider.name}: $e');
      }
    }
  }

  /// Sanitize error object
  dynamic _sanitizeError(dynamic error) {
    if (error is String) {
      return PIISanitizer.sanitizeString(error);
    } else if (error is Exception) {
      return PIISanitizer.sanitizeString(error.toString());
    } else if (error is Error) {
      return PIISanitizer.sanitizeString(error.toString());
    }
    return error;
  }

  /// Filter certain errors that shouldn't be reported
  bool _shouldFilterError(dynamic error) {
    final errorString = error.toString().toLowerCase();

    // Filter out common non-critical errors
    const ignoredPatterns = [
      'socket',
      'network',
      'http',
      'connection refused',
      'connection timeout',
      // Add more patterns as needed
    ];

    // Only filter these in non-fatal cases
    return ignoredPatterns.any((pattern) => errorString.contains(pattern));
  }

  /// Get current breadcrumbs (for debugging)
  List<Breadcrumb> get breadcrumbs => List.unmodifiable(_breadcrumbs);

  /// Get current user context
  UserContext? get userContext => _userContext;

  /// Get app context
  AppContext? get appContext => _appContext;

  /// Check if service is initialized
  bool get isInitialized => _initialized;

  /// Check if service is enabled
  bool get isEnabled => _enabled;

  /// Enable/disable crash reporting
  Future<void> setEnabled(bool enabled) async {
    _enabled = enabled;

    for (final provider in _providers) {
      try {
        await provider.setEnabled(enabled);
      } catch (e) {
        debugPrint('❌ Failed to set enabled state for ${provider.name}: $e');
      }
    }
  }
}
