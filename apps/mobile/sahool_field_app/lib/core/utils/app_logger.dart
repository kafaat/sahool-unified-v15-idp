import 'dart:developer' as developer;
import 'package:flutter/foundation.dart';

/// SAHOOL App Logger - Structured Logging System
/// نظام تسجيل مهيكل للتطبيق
///
/// Usage:
/// ```dart
/// AppLogger.d('Debug message');
/// AppLogger.i('Info message');
/// AppLogger.w('Warning message');
/// AppLogger.e('Error message', error: exception, stackTrace: stack);
/// ```

enum LogLevel { debug, info, warning, error, critical }

class AppLogger {
  static bool _enabled = true;
  static LogLevel _minLevel = kDebugMode ? LogLevel.debug : LogLevel.info;
  static final List<LogEntry> _logBuffer = [];
  static const int _maxBufferSize = 1000;

  /// Configure logger settings
  static void configure({
    bool? enabled,
    LogLevel? minLevel,
  }) {
    if (enabled != null) _enabled = enabled;
    if (minLevel != null) _minLevel = minLevel;
  }

  /// Debug log - للتطوير فقط
  static void d(String message, {String? tag, Map<String, dynamic>? data}) {
    _log(LogLevel.debug, message, tag: tag, data: data);
  }

  /// Info log - معلومات عامة
  static void i(String message, {String? tag, Map<String, dynamic>? data}) {
    _log(LogLevel.info, message, tag: tag, data: data);
  }

  /// Warning log - تحذيرات
  static void w(String message, {String? tag, Map<String, dynamic>? data}) {
    _log(LogLevel.warning, message, tag: tag, data: data);
  }

  /// Error log - أخطاء
  static void e(
    String message, {
    String? tag,
    Object? error,
    StackTrace? stackTrace,
    Map<String, dynamic>? data,
  }) {
    _log(
      LogLevel.error,
      message,
      tag: tag,
      error: error,
      stackTrace: stackTrace,
      data: data,
    );
  }

  /// Critical log - أخطاء حرجة
  static void critical(
    String message, {
    String? tag,
    Object? error,
    StackTrace? stackTrace,
    Map<String, dynamic>? data,
  }) {
    _log(
      LogLevel.critical,
      message,
      tag: tag,
      error: error,
      stackTrace: stackTrace,
      data: data,
    );
  }

  /// Network request log
  static void network(
    String method,
    String url, {
    int? statusCode,
    Duration? duration,
    Map<String, dynamic>? data,
  }) {
    final emoji = _getNetworkEmoji(statusCode);
    final durationStr = duration != null ? ' (${duration.inMilliseconds}ms)' : '';

    _log(
      statusCode != null && statusCode >= 400 ? LogLevel.error : LogLevel.info,
      '$emoji $method $url ${statusCode ?? ""}$durationStr',
      tag: 'NETWORK',
      data: data,
    );
  }

  /// Sync operation log
  static void sync(String operation, {bool success = true, String? details}) {
    final emoji = success ? '🔄' : '❌';
    _log(
      success ? LogLevel.info : LogLevel.error,
      '$emoji Sync: $operation${details != null ? " - $details" : ""}',
      tag: 'SYNC',
    );
  }

  /// User action log
  static void userAction(String action, {Map<String, dynamic>? params}) {
    _log(
      LogLevel.info,
      '👆 User: $action',
      tag: 'USER',
      data: params,
    );
  }

  /// Performance log
  static void performance(String operation, Duration duration) {
    final emoji = duration.inMilliseconds > 1000 ? '🐢' : '⚡';
    _log(
      duration.inMilliseconds > 2000 ? LogLevel.warning : LogLevel.debug,
      '$emoji $operation took ${duration.inMilliseconds}ms',
      tag: 'PERF',
    );
  }

  /// Get recent logs (for debugging/crash reports)
  static List<LogEntry> getRecentLogs({int count = 50}) {
    final start = _logBuffer.length > count ? _logBuffer.length - count : 0;
    return _logBuffer.sublist(start);
  }

  /// Clear log buffer
  static void clearBuffer() {
    _logBuffer.clear();
  }

  /// Export logs as string (for crash reports)
  static String exportLogs() {
    return _logBuffer.map((e) => e.toString()).join('\n');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Private Methods
  // ═══════════════════════════════════════════════════════════════════════════

  static void _log(
    LogLevel level,
    String message, {
    String? tag,
    Object? error,
    StackTrace? stackTrace,
    Map<String, dynamic>? data,
  }) {
    if (!_enabled) return;
    if (level.index < _minLevel.index) return;

    final entry = LogEntry(
      level: level,
      message: message,
      tag: tag,
      error: error,
      stackTrace: stackTrace,
      data: data,
      timestamp: DateTime.now(),
    );

    // Add to buffer
    _logBuffer.add(entry);
    if (_logBuffer.length > _maxBufferSize) {
      _logBuffer.removeAt(0);
    }

    // Print to console in debug mode
    if (kDebugMode) {
      _printToConsole(entry);
    }

    // Log to developer tools
    developer.log(
      entry.formattedMessage,
      name: entry.tag ?? 'SAHOOL',
      level: _getLevelValue(level),
      error: error,
      stackTrace: stackTrace,
    );
  }

  static void _printToConsole(LogEntry entry) {
    final buffer = StringBuffer();

    // Timestamp
    buffer.write(_formatTime(entry.timestamp));
    buffer.write(' ');

    // Level emoji
    buffer.write(_getLevelEmoji(entry.level));
    buffer.write(' ');

    // Tag
    if (entry.tag != null) {
      buffer.write('[${entry.tag}] ');
    }

    // Message
    buffer.write(entry.message);

    // Data
    if (entry.data != null && entry.data!.isNotEmpty) {
      buffer.write(' | ${entry.data}');
    }

    // Error
    if (entry.error != null) {
      buffer.write('\n   Error: ${entry.error}');
    }

    // Stack trace (first 5 lines)
    if (entry.stackTrace != null) {
      final lines = entry.stackTrace.toString().split('\n').take(5);
      buffer.write('\n   ${lines.join('\n   ')}');
    }

    // Use appropriate print based on level
    switch (entry.level) {
      case LogLevel.error:
      case LogLevel.critical:
        debugPrint('\x1B[31m${buffer.toString()}\x1B[0m'); // Red
        break;
      case LogLevel.warning:
        debugPrint('\x1B[33m${buffer.toString()}\x1B[0m'); // Yellow
        break;
      case LogLevel.info:
        debugPrint('\x1B[32m${buffer.toString()}\x1B[0m'); // Green
        break;
      default:
        debugPrint('\x1B[37m${buffer.toString()}\x1B[0m'); // White
    }
  }

  static String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:'
        '${time.minute.toString().padLeft(2, '0')}:'
        '${time.second.toString().padLeft(2, '0')}.'
        '${time.millisecond.toString().padLeft(3, '0')}';
  }

  static String _getLevelEmoji(LogLevel level) {
    switch (level) {
      case LogLevel.debug:
        return '🔍';
      case LogLevel.info:
        return 'ℹ️';
      case LogLevel.warning:
        return '⚠️';
      case LogLevel.error:
        return '❌';
      case LogLevel.critical:
        return '🔥';
    }
  }

  static String _getNetworkEmoji(int? statusCode) {
    if (statusCode == null) return '📤';
    if (statusCode >= 200 && statusCode < 300) return '📥';
    if (statusCode >= 400 && statusCode < 500) return '⚠️';
    if (statusCode >= 500) return '❌';
    return '📡';
  }

  static int _getLevelValue(LogLevel level) {
    switch (level) {
      case LogLevel.debug:
        return 500;
      case LogLevel.info:
        return 800;
      case LogLevel.warning:
        return 900;
      case LogLevel.error:
        return 1000;
      case LogLevel.critical:
        return 1200;
    }
  }
}

/// Log entry model
class LogEntry {
  final LogLevel level;
  final String message;
  final String? tag;
  final Object? error;
  final StackTrace? stackTrace;
  final Map<String, dynamic>? data;
  final DateTime timestamp;

  LogEntry({
    required this.level,
    required this.message,
    this.tag,
    this.error,
    this.stackTrace,
    this.data,
    required this.timestamp,
  });

  String get formattedMessage {
    final buffer = StringBuffer(message);
    if (data != null) buffer.write(' | $data');
    if (error != null) buffer.write(' | Error: $error');
    return buffer.toString();
  }

  Map<String, dynamic> toJson() => {
        'level': level.name,
        'message': message,
        'tag': tag,
        'error': error?.toString(),
        'data': data,
        'timestamp': timestamp.toIso8601String(),
      };

  @override
  String toString() {
    return '${timestamp.toIso8601String()} [${level.name.toUpperCase()}] '
        '${tag != null ? "[$tag] " : ""}'
        '$message'
        '${error != null ? " | Error: $error" : ""}';
  }
}

/// Mixin for classes that need logging
mixin LoggerMixin {
  String get logTag => runtimeType.toString();

  void logDebug(String message, {Map<String, dynamic>? data}) {
    AppLogger.d(message, tag: logTag, data: data);
  }

  void logInfo(String message, {Map<String, dynamic>? data}) {
    AppLogger.i(message, tag: logTag, data: data);
  }

  void logWarning(String message, {Map<String, dynamic>? data}) {
    AppLogger.w(message, tag: logTag, data: data);
  }

  void logError(String message, {Object? error, StackTrace? stackTrace}) {
    AppLogger.e(message, tag: logTag, error: error, stackTrace: stackTrace);
  }
}
