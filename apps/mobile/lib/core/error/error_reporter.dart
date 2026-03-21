/// SAHOOL Error Reporter - Centralized Error Reporting Service
/// خدمة تقارير الأخطاء المركزية
///
/// Provides unified error reporting to Sentry, analytics, and crash reporting services.
/// Integrates with the existing CrashReportingService for comprehensive error tracking.
library;

import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/crash_reporting_service.dart';
import '../utils/app_logger.dart';
import 'error_messages.dart';

/// Error severity levels for reporting
enum ReportSeverity {
  /// Debug level - only in development
  debug,

  /// Info level - non-critical information
  info,

  /// Warning level - potential issues
  warning,

  /// Error level - recoverable errors
  error,

  /// Fatal level - app crashes
  fatal,
}

/// Error context containing additional information about the error
class ErrorContext {
  /// Screen/route where the error occurred
  final String? screen;

  /// Widget that caused the error
  final String? widget;

  /// User action that triggered the error
  final String? action;

  /// Additional metadata
  final Map<String, dynamic>? metadata;

  /// Error type classification
  final ErrorType? errorType;

  /// Whether the error is recoverable
  final bool recoverable;

  /// Timestamp of the error
  final DateTime timestamp;

  const ErrorContext({
    this.screen,
    this.widget,
    this.action,
    this.metadata,
    this.errorType,
    this.recoverable = true,
  }) : timestamp = const _CurrentDateTime();

  /// Create from current context
  factory ErrorContext.current({
    String? screen,
    String? widget,
    String? action,
    Map<String, dynamic>? metadata,
    ErrorType? errorType,
    bool recoverable = true,
  }) {
    return ErrorContext(
      screen: screen,
      widget: widget,
      action: action,
      metadata: metadata,
      errorType: errorType,
      recoverable: recoverable,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      if (screen != null) 'screen': screen,
      if (widget != null) 'widget': widget,
      if (action != null) 'action': action,
      if (metadata != null) ...metadata!,
      if (errorType != null) 'errorType': errorType!.name,
      'recoverable': recoverable,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}

/// Workaround class for const DateTime
class _CurrentDateTime implements DateTime {
  const _CurrentDateTime();

  DateTime get _now => DateTime.now();

  @override
  bool get isUtc => _now.isUtc;
  @override
  int get year => _now.year;
  @override
  int get month => _now.month;
  @override
  int get day => _now.day;
  @override
  int get hour => _now.hour;
  @override
  int get minute => _now.minute;
  @override
  int get second => _now.second;
  @override
  int get millisecond => _now.millisecond;
  @override
  int get microsecond => _now.microsecond;
  @override
  int get weekday => _now.weekday;
  @override
  int get millisecondsSinceEpoch => _now.millisecondsSinceEpoch;
  @override
  int get microsecondsSinceEpoch => _now.microsecondsSinceEpoch;
  @override
  String get timeZoneName => _now.timeZoneName;
  @override
  Duration get timeZoneOffset => _now.timeZoneOffset;

  @override
  DateTime add(Duration duration) => _now.add(duration);
  @override
  DateTime subtract(Duration duration) => _now.subtract(duration);
  @override
  Duration difference(DateTime other) => _now.difference(other);
  @override
  bool isBefore(DateTime other) => _now.isBefore(other);
  @override
  bool isAfter(DateTime other) => _now.isAfter(other);
  @override
  bool isAtSameMomentAs(DateTime other) => _now.isAtSameMomentAs(other);
  @override
  int compareTo(DateTime other) => _now.compareTo(other);
  @override
  DateTime toLocal() => _now.toLocal();
  @override
  DateTime toUtc() => _now.toUtc();
  @override
  String toIso8601String() => _now.toIso8601String();

  @override
  String toString() => _now.toString();
}

/// Error report containing all error information
class ErrorReport {
  final Object error;
  final StackTrace? stackTrace;
  final ReportSeverity severity;
  final ErrorContext? context;
  final DateTime timestamp;

  ErrorReport({
    required this.error,
    this.stackTrace,
    this.severity = ReportSeverity.error,
    this.context,
  }) : timestamp = DateTime.now();

  Map<String, dynamic> toMap() {
    return {
      'error': error.toString(),
      'errorType': error.runtimeType.toString(),
      'severity': severity.name,
      'timestamp': timestamp.toIso8601String(),
      if (stackTrace != null) 'stackTrace': stackTrace.toString(),
      if (context != null) 'context': context!.toMap(),
    };
  }
}

/// Centralized error reporting service
class ErrorReporter {
  static final ErrorReporter _instance = ErrorReporter._internal();
  factory ErrorReporter() => _instance;
  ErrorReporter._internal();

  /// Crash reporting service instance
  final CrashReportingService _crashReporting = CrashReportingService();

  /// Error callback listeners
  final List<void Function(ErrorReport)> _listeners = [];

  /// Recent errors for debugging (limited to last 50)
  final List<ErrorReport> _recentErrors = [];
  static const int _maxRecentErrors = 50;

  /// Whether reporting is enabled
  bool _enabled = true;

  /// Initialize the error reporter
  Future<void> initialize() async {
    // Crash reporting is initialized in main.dart
    AppLogger.i('ErrorReporter initialized', tag: 'ErrorReporter');
  }

  /// Report an error with optional context
  Future<void> reportError(
    Object error, {
    StackTrace? stackTrace,
    ReportSeverity severity = ReportSeverity.error,
    ErrorContext? context,
    bool silent = false,
  }) async {
    if (!_enabled) return;

    final report = ErrorReport(
      error: error,
      stackTrace: stackTrace,
      severity: severity,
      context: context,
    );

    // Store in recent errors
    _addToRecentErrors(report);

    // Log the error
    if (!silent) {
      _logError(report);
    }

    // Report to crash reporting service
    await _reportToCrashService(report);

    // Notify listeners
    _notifyListeners(report);
  }

  /// Report a Flutter error from FlutterError.onError
  Future<void> reportFlutterError(
    FlutterErrorDetails details, {
    ErrorContext? context,
  }) async {
    final errorContext = context ??
        ErrorContext.current(
          widget: details.context?.toString(),
          metadata: {
            'library': details.library ?? 'unknown',
            'silent': details.silent,
          },
        );

    await reportError(
      details.exception,
      stackTrace: details.stack,
      severity: ReportSeverity.error,
      context: errorContext,
      silent: details.silent,
    );
  }

  /// Report a platform error from PlatformDispatcher.instance.onError
  Future<void> reportPlatformError(
    Object error,
    StackTrace stackTrace, {
    ErrorContext? context,
  }) async {
    await reportError(
      error,
      stackTrace: stackTrace,
      severity: ReportSeverity.fatal,
      context: context ?? ErrorContext.current(recoverable: false),
    );
  }

  /// Report a warning (non-critical issue)
  Future<void> reportWarning(
    String message, {
    Map<String, dynamic>? metadata,
    ErrorContext? context,
  }) async {
    final errorContext = context ??
        ErrorContext.current(
          metadata: metadata,
          recoverable: true,
        );

    await reportError(
      Exception(message),
      severity: ReportSeverity.warning,
      context: errorContext,
      silent: true,
    );
  }

  /// Report an info message (for tracking purposes)
  void reportInfo(
    String message, {
    Map<String, dynamic>? metadata,
  }) {
    _crashReporting.recordBreadcrumb(
      message: message,
      category: 'info',
      data: metadata,
      level: BreadcrumbLevel.info,
    );
  }

  /// Record a breadcrumb for context
  void recordBreadcrumb({
    required String message,
    String? category,
    Map<String, dynamic>? data,
    BreadcrumbLevel level = BreadcrumbLevel.info,
  }) {
    _crashReporting.recordBreadcrumb(
      message: message,
      category: category,
      data: data,
      level: level,
    );
  }

  /// Set user context for error reports
  Future<void> setUserContext({
    required String userId,
    String? tenantId,
    String? role,
    Map<String, dynamic>? metadata,
  }) async {
    await _crashReporting.setUserContext(
      anonymousId: userId,
      tenantId: tenantId,
      role: role,
      metadata: metadata,
    );
  }

  /// Clear user context (e.g., on logout)
  Future<void> clearUserContext() async {
    await _crashReporting.clearUserContext();
  }

  /// Set a custom key-value pair for error reports
  Future<void> setCustomKey(String key, dynamic value) async {
    await _crashReporting.setCustomKey(key, value);
  }

  /// Add a listener for error reports
  void addListener(void Function(ErrorReport) listener) {
    _listeners.add(listener);
  }

  /// Remove a listener
  void removeListener(void Function(ErrorReport) listener) {
    _listeners.remove(listener);
  }

  /// Get recent errors for debugging
  List<ErrorReport> get recentErrors => List.unmodifiable(_recentErrors);

  /// Enable or disable error reporting
  set enabled(bool value) {
    _enabled = value;
    _crashReporting.setEnabled(value);
  }

  /// Check if error reporting is enabled
  bool get enabled => _enabled;

  /// Clear recent errors
  void clearRecentErrors() {
    _recentErrors.clear();
  }

  // Private methods

  void _addToRecentErrors(ErrorReport report) {
    _recentErrors.add(report);
    if (_recentErrors.length > _maxRecentErrors) {
      _recentErrors.removeAt(0);
    }
  }

  void _logError(ErrorReport report) {
    final severity = report.severity;
    final error = report.error;
    final stackTrace = report.stackTrace;

    switch (severity) {
      case ReportSeverity.debug:
        AppLogger.d('$error', tag: 'ErrorReporter');
        break;
      case ReportSeverity.info:
        AppLogger.i('$error', tag: 'ErrorReporter');
        break;
      case ReportSeverity.warning:
        AppLogger.w('$error', tag: 'ErrorReporter');
        break;
      case ReportSeverity.error:
        AppLogger.e('$error',
            tag: 'ErrorReporter', error: error, stackTrace: stackTrace);
        break;
      case ReportSeverity.fatal:
        AppLogger.critical('$error',
            tag: 'ErrorReporter', error: error, stackTrace: stackTrace);
        break;
    }
  }

  Future<void> _reportToCrashService(ErrorReport report) async {
    final crashSeverity = _mapSeverity(report.severity);

    await _crashReporting.reportError(
      report.error,
      report.stackTrace,
      severity: crashSeverity,
      reason: report.context?.action,
      customData: report.context?.toMap(),
      fatal: report.severity == ReportSeverity.fatal,
    );
  }

  ErrorSeverity _mapSeverity(ReportSeverity severity) {
    switch (severity) {
      case ReportSeverity.debug:
        return ErrorSeverity.debug;
      case ReportSeverity.info:
        return ErrorSeverity.info;
      case ReportSeverity.warning:
        return ErrorSeverity.warning;
      case ReportSeverity.error:
        return ErrorSeverity.error;
      case ReportSeverity.fatal:
        return ErrorSeverity.fatal;
    }
  }

  void _notifyListeners(ErrorReport report) {
    for (final listener in _listeners) {
      try {
        listener(report);
      } catch (e) {
        // Ignore listener errors
        debugPrint('Error in error listener: $e');
      }
    }
  }
}

/// Riverpod provider for ErrorReporter
final errorReporterProvider = Provider<ErrorReporter>((ref) {
  return ErrorReporter();
});

/// Extension for easy error reporting from WidgetRef
extension ErrorReporterExtension on WidgetRef {
  /// Report an error using the ErrorReporter
  Future<void> reportError(
    Object error, {
    StackTrace? stackTrace,
    ReportSeverity severity = ReportSeverity.error,
    ErrorContext? context,
  }) async {
    await read(errorReporterProvider).reportError(
      error,
      stackTrace: stackTrace,
      severity: severity,
      context: context,
    );
  }

  /// Record a breadcrumb
  void recordBreadcrumb({
    required String message,
    String? category,
    Map<String, dynamic>? data,
  }) {
    read(errorReporterProvider).recordBreadcrumb(
      message: message,
      category: category,
      data: data,
    );
  }
}

/// Global error reporter instance for easy access
final errorReporter = ErrorReporter();
