import 'dart:async';
import 'dart:developer' as developer;
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';

import '../utils/pii_filter.dart';
import 'log_models.dart';
import 'file_logger.dart';
import 'log_sync_service.dart';

/// SAHOOL Structured Logger
/// نظام التسجيل المهيكل لتطبيق سهول
///
/// Comprehensive logging system with:
/// - Log levels: debug, info, warning, error, fatal
/// - Structured metadata support (userId, fieldId, action, etc.)
/// - File-based logging for offline mode
/// - Log rotation (max 5 files, 2MB each)
/// - Automatic sync when online
/// - Arabic language support
/// - PII filtering
/// - JSON structured logs
///
/// Usage:
/// ```dart
/// // Initialize
/// await Logger.initialize();
///
/// // Basic logging
/// Logger.debug('Debug message');
/// Logger.info('User logged in', metadata: LogMetadata(userId: 'user123'));
/// Logger.warning('Low storage', messageAr: 'مساحة التخزين منخفضة');
/// Logger.error('API failed', error: exception, stackTrace: stack);
/// Logger.fatal('Critical failure');
///
/// // Category-based logging
/// Logger.field('Field created', fieldId: 'field_001', action: 'create');
/// Logger.network('GET', '/api/fields', statusCode: 200, durationMs: 150);
/// Logger.sync('Sync completed', success: true);
/// Logger.user('Tap', screen: 'home', action: 'refresh_button');
/// ```
class Logger {
  /// Singleton instance
  static Logger? _instance;

  /// Configuration
  LoggerConfig _config;

  /// File logger
  FileLogger? _fileLogger;

  /// Sync service
  LogSyncService? _syncService;

  /// In-memory log buffer for crash reports
  final List<StructuredLogEntry> _logBuffer = [];

  /// Max buffer size
  static const int _maxBufferSize = 500;

  /// UUID generator
  final Uuid _uuid = const Uuid();

  /// App version
  String? _appVersion;

  /// Device ID
  String? _deviceId;

  /// Platform name
  String? _platform;

  /// Global context (user, tenant, session)
  LogMetadata _globalContext = LogMetadata.empty();

  /// PII filtering enabled
  bool _piiFilteringEnabled = true;

  /// PII filtered count
  int _piiFilteredCount = 0;

  Logger._internal({LoggerConfig? config})
      : _config = config ?? const LoggerConfig();

  /// Get the logger instance
  static Logger get instance {
    _instance ??= Logger._internal();
    return _instance!;
  }

  /// Initialize the logger
  /// تهيئة المسجل
  static Future<void> initialize({
    LoggerConfig? config,
    Future<bool> Function(List<Map<String, dynamic>>)? syncCallback,
  }) async {
    final logger = instance;
    logger._config = config ??
        (kDebugMode
            ? LoggerConfig.development()
            : LoggerConfig.production());

    // Get device info
    await logger._initializeDeviceInfo();

    // Initialize file logger
    if (logger._config.enableFileLogging) {
      logger._fileLogger = FileLogger(config: logger._config);
      await logger._fileLogger!.initialize();
    }

    // Initialize sync service
    if (logger._config.enableAutoSync && logger._fileLogger != null) {
      logger._syncService = LogSyncService(
        fileLogger: logger._fileLogger!,
        config: logger._config,
        syncCallback: syncCallback,
      );
      await logger._syncService!.start();
    }

    logger._piiFilteringEnabled = logger._config.enablePiiFiltering;

    Logger.info(
      'Logger initialized',
      messageAr: 'تم تهيئة المسجل',
      category: LogCategory.app,
      tag: 'LOGGER',
    );
  }

  /// Configure the logger
  /// ضبط إعدادات المسجل
  static void configure({
    LogLevel? minLevel,
    bool? enableConsole,
    bool? enableFileLogging,
    bool? enableAutoSync,
    bool? enablePiiFiltering,
  }) {
    final logger = instance;
    logger._config = logger._config.copyWith(
      minLevel: minLevel,
      enableConsole: enableConsole,
      enableFileLogging: enableFileLogging,
      enableAutoSync: enableAutoSync,
      enablePiiFiltering: enablePiiFiltering,
    );
    logger._piiFilteringEnabled = logger._config.enablePiiFiltering;
  }

  /// Set global context (user info, tenant, etc.)
  /// تعيين السياق العام (معلومات المستخدم، المستأجر، إلخ)
  static void setGlobalContext({
    String? userId,
    String? tenantId,
    String? sessionId,
  }) {
    final logger = instance;
    logger._globalContext = logger._globalContext.copyWith(
      userId: userId,
      tenantId: tenantId,
      sessionId: sessionId,
    );
  }

  /// Clear global context
  /// مسح السياق العام
  static void clearGlobalContext() {
    instance._globalContext = LogMetadata.empty();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Log Level Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Debug log - for development only
  /// سجل تصحيح - للتطوير فقط
  static void debug(
    String message, {
    String? messageAr,
    String? tag,
    LogCategory category = LogCategory.general,
    LogMetadata? metadata,
    Map<String, dynamic>? extra,
  }) {
    instance._log(
      LogLevel.debug,
      message,
      messageAr: messageAr,
      tag: tag,
      category: category,
      metadata: metadata,
      extra: extra,
    );
  }

  /// Shorthand for debug
  static void d(String message, {String? tag, Map<String, dynamic>? data}) {
    debug(message, tag: tag, extra: data);
  }

  /// Info log - general information
  /// سجل معلومات - معلومات عامة
  static void info(
    String message, {
    String? messageAr,
    String? tag,
    LogCategory category = LogCategory.general,
    LogMetadata? metadata,
    Map<String, dynamic>? extra,
  }) {
    instance._log(
      LogLevel.info,
      message,
      messageAr: messageAr,
      tag: tag,
      category: category,
      metadata: metadata,
      extra: extra,
    );
  }

  /// Shorthand for info
  static void i(String message, {String? tag, Map<String, dynamic>? data}) {
    info(message, tag: tag, extra: data);
  }

  /// Warning log - potential issues
  /// سجل تحذير - مشاكل محتملة
  static void warning(
    String message, {
    String? messageAr,
    String? tag,
    LogCategory category = LogCategory.general,
    LogMetadata? metadata,
    Map<String, dynamic>? extra,
  }) {
    instance._log(
      LogLevel.warning,
      message,
      messageAr: messageAr,
      tag: tag,
      category: category,
      metadata: metadata,
      extra: extra,
    );
  }

  /// Shorthand for warning
  static void w(String message, {String? tag, Map<String, dynamic>? data}) {
    warning(message, tag: tag, extra: data);
  }

  /// Error log - errors requiring attention
  /// سجل خطأ - أخطاء تحتاج اهتمام
  static void error(
    String message, {
    String? messageAr,
    String? tag,
    LogCategory category = LogCategory.general,
    Object? error,
    StackTrace? stackTrace,
    LogMetadata? metadata,
    Map<String, dynamic>? extra,
  }) {
    instance._log(
      LogLevel.error,
      message,
      messageAr: messageAr,
      tag: tag,
      category: category,
      error: error,
      stackTrace: stackTrace,
      metadata: metadata,
      extra: extra,
    );
  }

  /// Shorthand for error
  static void e(
    String message, {
    String? tag,
    Object? error,
    StackTrace? stackTrace,
    Map<String, dynamic>? data,
  }) {
    Logger.error(message, tag: tag, error: error, stackTrace: stackTrace, extra: data);
  }

  /// Fatal log - critical errors
  /// سجل فادح - أخطاء حرجة
  static void fatal(
    String message, {
    String? messageAr,
    String? tag,
    LogCategory category = LogCategory.general,
    Object? error,
    StackTrace? stackTrace,
    LogMetadata? metadata,
    Map<String, dynamic>? extra,
  }) {
    instance._log(
      LogLevel.fatal,
      message,
      messageAr: messageAr,
      tag: tag,
      category: category,
      error: error,
      stackTrace: stackTrace,
      metadata: metadata,
      extra: extra,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Category-Based Logging Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Field operation log
  /// سجل عمليات الحقل
  static void field(
    String message, {
    String? messageAr,
    required String fieldId,
    String? action,
    String? actionAr,
    LogLevel level = LogLevel.info,
    Map<String, dynamic>? extra,
  }) {
    instance._log(
      level,
      message,
      messageAr: messageAr,
      tag: 'FIELD',
      category: LogCategory.field,
      metadata: LogMetadata(
        fieldId: fieldId,
        action: action,
        actionAr: actionAr,
      ),
      extra: extra,
    );
  }

  /// Network/API log
  /// سجل الشبكة/API
  static void network(
    String method,
    String url, {
    int? statusCode,
    int? durationMs,
    String? requestId,
    Object? error,
    Map<String, dynamic>? extra,
  }) {
    final level = statusCode != null && statusCode >= 400
        ? LogLevel.error
        : LogLevel.info;

    final statusEmoji = _getNetworkEmoji(statusCode);
    final message = '$statusEmoji $method $url ${statusCode ?? ""}';

    instance._log(
      level,
      message,
      tag: 'HTTP',
      category: LogCategory.network,
      error: error,
      metadata: LogMetadata(
        statusCode: statusCode,
        durationMs: durationMs,
        requestId: requestId,
      ),
      extra: extra,
    );
  }

  /// Sync operation log
  /// سجل عمليات المزامنة
  static void sync(
    String operation, {
    bool success = true,
    String? details,
    String? detailsAr,
    int? recordCount,
    int? durationMs,
  }) {
    final emoji = success ? '🔄' : '❌';
    final level = success ? LogLevel.info : LogLevel.error;

    instance._log(
      level,
      '$emoji Sync: $operation${details != null ? " - $details" : ""}',
      messageAr: detailsAr != null ? '$emoji مزامنة: $detailsAr' : null,
      tag: 'SYNC',
      category: LogCategory.sync,
      metadata: LogMetadata(durationMs: durationMs),
      extra: recordCount != null ? {'record_count': recordCount} : null,
    );
  }

  /// User action log
  /// سجل إجراءات المستخدم
  static void user(
    String action, {
    String? actionAr,
    String? screen,
    String? targetId,
    Map<String, dynamic>? params,
  }) {
    instance._log(
      LogLevel.info,
      '👆 User: $action',
      messageAr: actionAr != null ? '👆 المستخدم: $actionAr' : null,
      tag: 'USER',
      category: LogCategory.user,
      metadata: LogMetadata(
        action: action,
        actionAr: actionAr,
        screen: screen,
      ),
      extra: {
        if (targetId != null) 'target_id': targetId,
        if (params != null) ...params,
      },
    );
  }

  /// Authentication log
  /// سجل المصادقة
  static void auth(
    String event, {
    String? eventAr,
    String? userId,
    bool success = true,
    String? reason,
  }) {
    final emoji = success ? '🔐' : '🚫';
    final level = success ? LogLevel.info : LogLevel.warning;

    instance._log(
      level,
      '$emoji Auth: $event',
      messageAr: eventAr != null ? '$emoji المصادقة: $eventAr' : null,
      tag: 'AUTH',
      category: LogCategory.auth,
      metadata: LogMetadata(userId: userId),
      extra: reason != null ? {'reason': reason} : null,
    );
  }

  /// Navigation log
  /// سجل التنقل
  static void navigation(
    String routeName, {
    String? routeNameAr,
    String? fromRoute,
    Map<String, dynamic>? params,
  }) {
    instance._log(
      LogLevel.debug,
      '📱 Navigate: $routeName',
      messageAr: routeNameAr != null ? '📱 تنقل: $routeNameAr' : null,
      tag: 'NAV',
      category: LogCategory.navigation,
      metadata: LogMetadata(screen: routeName),
      extra: {
        if (fromRoute != null) 'from': fromRoute,
        if (params != null) 'params': params,
      },
    );
  }

  /// Performance log
  /// سجل الأداء
  static void performance(
    String operation, {
    required int durationMs,
    String? operationAr,
    Map<String, dynamic>? metrics,
  }) {
    final emoji = durationMs > 1000 ? '🐢' : '⚡';
    final level = durationMs > 2000 ? LogLevel.warning : LogLevel.debug;

    instance._log(
      level,
      '$emoji $operation took ${durationMs}ms',
      messageAr: operationAr != null
          ? '$emoji $operationAr استغرق ${durationMs}ms'
          : null,
      tag: 'PERF',
      category: LogCategory.performance,
      metadata: LogMetadata(durationMs: durationMs),
      extra: metrics,
    );
  }

  /// Advisory/AI log
  /// سجل الاستشارات/الذكاء الاصطناعي
  static void advisory(
    String message, {
    String? messageAr,
    String? fieldId,
    String? advisoryType,
    double? confidence,
    Map<String, dynamic>? extra,
  }) {
    instance._log(
      LogLevel.info,
      '🤖 Advisory: $message',
      messageAr: messageAr != null ? '🤖 استشارة: $messageAr' : null,
      tag: 'AI',
      category: LogCategory.advisory,
      metadata: LogMetadata(fieldId: fieldId),
      extra: {
        if (advisoryType != null) 'advisory_type': advisoryType,
        if (confidence != null) 'confidence': confidence,
        if (extra != null) ...extra,
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Log Management Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get recent logs from memory buffer
  /// الحصول على السجلات الحديثة من المخزن المؤقت
  static List<StructuredLogEntry> getRecentLogs({int count = 50}) {
    final buffer = instance._logBuffer;
    final start = buffer.length > count ? buffer.length - count : 0;
    return buffer.sublist(start);
  }

  /// Export logs as JSON string
  /// تصدير السجلات كنص JSON
  static Future<String> exportLogs({
    DateTime? start,
    DateTime? end,
    LogLevel? minLevel,
  }) async {
    if (instance._fileLogger != null) {
      return instance._fileLogger!.exportLogsAsJson(
        start: start,
        end: end,
        minLevel: minLevel,
      );
    }
    return '[]';
  }

  /// Sync logs now
  /// مزامنة السجلات الآن
  static Future<LogSyncStatus?> syncNow() async {
    return instance._syncService?.syncNow();
  }

  /// Get sync status
  /// الحصول على حالة المزامنة
  static LogSyncStatus? getSyncStatus() {
    return instance._syncService?.status;
  }

  /// Get sync status stream
  /// الحصول على تدفق حالة المزامنة
  static Stream<LogSyncStatus>? getSyncStatusStream() {
    return instance._syncService?.statusStream;
  }

  /// Get log files info
  /// الحصول على معلومات ملفات السجل
  static Future<List<LogFileInfo>> getLogFilesInfo() async {
    final fileLogger = instance._fileLogger;
    if (fileLogger == null) return [];
    return fileLogger.getLogFilesInfo();
  }

  /// Get total storage size
  /// الحصول على إجمالي حجم التخزين
  static Future<int> getTotalStorageSize() async {
    final fileLogger = instance._fileLogger;
    if (fileLogger == null) return 0;
    return fileLogger.getTotalStorageSize();
  }

  /// Clear synced logs
  /// مسح السجلات المتزامنة
  static Future<int> clearSyncedLogs({int keepDays = 7}) async {
    final fileLogger = instance._fileLogger;
    if (fileLogger == null) return 0;
    return fileLogger.clearSyncedLogs(keepDays: keepDays);
  }

  /// Clear all logs
  /// مسح جميع السجلات
  static Future<void> clearAllLogs() async {
    instance._logBuffer.clear();
    await instance._fileLogger?.clearAllLogs();
  }

  /// Flush pending logs to file
  /// تفريغ السجلات المعلقة إلى الملف
  static Future<void> flush() async {
    await instance._fileLogger?.flush();
  }

  /// Get PII filtering stats
  /// الحصول على إحصائيات تصفية البيانات الشخصية
  static Map<String, dynamic> getPiiStats() {
    return {
      'enabled': instance._piiFilteringEnabled,
      'filtered_count': instance._piiFilteredCount,
    };
  }

  /// Dispose logger
  /// التخلص من المسجل
  static Future<void> dispose() async {
    await instance._fileLogger?.dispose();
    await instance._syncService?.dispose();
    instance._logBuffer.clear();
    _instance = null;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Private Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Internal log method
  void _log(
    LogLevel level,
    String message, {
    String? messageAr,
    String? tag,
    LogCategory category = LogCategory.general,
    Object? error,
    StackTrace? stackTrace,
    LogMetadata? metadata,
    Map<String, dynamic>? extra,
  }) {
    // Check minimum level
    if (!level.isAtLeast(_config.minLevel)) return;

    // Apply PII filtering
    String sanitizedMessage = message;
    String? sanitizedMessageAr = messageAr;
    String? sanitizedError;
    Map<String, dynamic>? sanitizedExtra = extra;

    if (_piiFilteringEnabled) {
      if (PiiFilter.containsPii(message)) {
        sanitizedMessage = PiiFilter.sanitize(message) as String;
        _piiFilteredCount++;
      }
      if (messageAr != null && PiiFilter.containsPii(messageAr)) {
        sanitizedMessageAr = PiiFilter.sanitize(messageAr) as String?;
        _piiFilteredCount++;
      }
      if (error != null) {
        final errorStr = error.toString();
        if (PiiFilter.containsPii(errorStr)) {
          sanitizedError = PiiFilter.sanitize(errorStr) as String?;
          _piiFilteredCount++;
        } else {
          sanitizedError = errorStr;
        }
      }
      if (extra != null) {
        sanitizedExtra = PiiFilter.sanitize(extra) as Map<String, dynamic>?;
      }
    } else {
      sanitizedError = error?.toString();
    }

    // Merge metadata with global context
    final mergedMetadata = LogMetadata(
      userId: metadata?.userId ?? _globalContext.userId,
      fieldId: metadata?.fieldId ?? _globalContext.fieldId,
      tenantId: metadata?.tenantId ?? _globalContext.tenantId,
      sessionId: metadata?.sessionId ?? _globalContext.sessionId,
      action: metadata?.action,
      actionAr: metadata?.actionAr,
      screen: metadata?.screen,
      requestId: metadata?.requestId,
      durationMs: metadata?.durationMs,
      statusCode: metadata?.statusCode,
      extra: sanitizedExtra,
    );

    // Create log entry
    final entry = StructuredLogEntry(
      id: _uuid.v4(),
      timestamp: DateTime.now(),
      level: level,
      category: category,
      message: sanitizedMessage,
      messageAr: sanitizedMessageAr,
      tag: tag,
      error: sanitizedError,
      stackTrace: _config.includeStackTrace && stackTrace != null
          ? stackTrace.toString()
          : null,
      metadata: mergedMetadata,
      appVersion: _appVersion,
      deviceId: _deviceId,
      platform: _platform,
    );

    // Add to buffer
    _logBuffer.add(entry);
    if (_logBuffer.length > _maxBufferSize) {
      _logBuffer.removeAt(0);
    }

    // Write to file
    _fileLogger?.writeLog(entry);

    // Print to console
    if (_config.enableConsole) {
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

  /// Initialize device info
  Future<void> _initializeDeviceInfo() async {
    try {
      final packageInfo = await PackageInfo.fromPlatform();
      _appVersion = '${packageInfo.version}+${packageInfo.buildNumber}';

      final deviceInfo = DeviceInfoPlugin();
      if (Platform.isAndroid) {
        final androidInfo = await deviceInfo.androidInfo;
        _deviceId = androidInfo.id;
        _platform = 'Android ${androidInfo.version.release}';
      } else if (Platform.isIOS) {
        final iosInfo = await deviceInfo.iosInfo;
        _deviceId = iosInfo.identifierForVendor;
        _platform = 'iOS ${iosInfo.systemVersion}';
      }
    } catch (e) {
      debugPrint('Logger: Failed to get device info: $e');
    }
  }

  /// Print log entry to console with colors
  void _printToConsole(StructuredLogEntry entry) {
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

    // Metadata
    if (!entry.metadata.isEmpty) {
      buffer.write(' | ${entry.metadata.toJson()}');
    }

    // Error
    if (entry.error != null) {
      buffer.write('\n   Error: ${entry.error}');
    }

    // Stack trace (first 5 lines)
    if (entry.stackTrace != null) {
      final lines = entry.stackTrace!.split('\n').take(5);
      buffer.write('\n   ${lines.join('\n   ')}');
    }

    // Color output based on level
    switch (entry.level) {
      case LogLevel.error:
      case LogLevel.fatal:
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

  /// Format timestamp
  static String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:'
        '${time.minute.toString().padLeft(2, '0')}:'
        '${time.second.toString().padLeft(2, '0')}.'
        '${time.millisecond.toString().padLeft(3, '0')}';
  }

  /// Get emoji for log level
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
      case LogLevel.fatal:
        return '🔥';
    }
  }

  /// Get emoji for network status
  static String _getNetworkEmoji(int? statusCode) {
    if (statusCode == null) return '📤';
    if (statusCode >= 200 && statusCode < 300) return '📥';
    if (statusCode >= 400 && statusCode < 500) return '⚠️';
    if (statusCode >= 500) return '❌';
    return '📡';
  }

  /// Get numeric value for log level
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
      case LogLevel.fatal:
        return 1200;
    }
  }
}

/// Mixin for classes that need logging
/// خليط للفئات التي تحتاج التسجيل
mixin LoggerMixin {
  /// Get log tag (class name by default)
  String get logTag => runtimeType.toString();

  /// Log debug message
  void logDebug(String message, {Map<String, dynamic>? data}) {
    Logger.debug(message, tag: logTag, extra: data);
  }

  /// Log info message
  void logInfo(String message, {Map<String, dynamic>? data}) {
    Logger.info(message, tag: logTag, extra: data);
  }

  /// Log warning message
  void logWarning(String message, {Map<String, dynamic>? data}) {
    Logger.warning(message, tag: logTag, extra: data);
  }

  /// Log error message
  void logError(String message, {Object? error, StackTrace? stackTrace}) {
    Logger.error(message, tag: logTag, error: error, stackTrace: stackTrace);
  }

  /// Log fatal message
  void logFatal(String message, {Object? error, StackTrace? stackTrace}) {
    Logger.fatal(message, tag: logTag, error: error, stackTrace: stackTrace);
  }
}

/// Extension for timing operations
/// امتداد لقياس وقت العمليات
extension LoggerTiming on Logger {
  /// Time an async operation and log the result
  static Future<T> timeAsync<T>(
    String operation,
    Future<T> Function() action, {
    String? operationAr,
  }) async {
    final stopwatch = Stopwatch()..start();
    try {
      final result = await action();
      stopwatch.stop();
      Logger.performance(
        operation,
        durationMs: stopwatch.elapsedMilliseconds,
        operationAr: operationAr,
      );
      return result;
    } catch (e, stack) {
      stopwatch.stop();
      Logger.error(
        '$operation failed after ${stopwatch.elapsedMilliseconds}ms',
        error: e,
        stackTrace: stack,
      );
      rethrow;
    }
  }

  /// Time a sync operation and log the result
  static T timeSync<T>(
    String operation,
    T Function() action, {
    String? operationAr,
  }) {
    final stopwatch = Stopwatch()..start();
    try {
      final result = action();
      stopwatch.stop();
      Logger.performance(
        operation,
        durationMs: stopwatch.elapsedMilliseconds,
        operationAr: operationAr,
      );
      return result;
    } catch (e, stack) {
      stopwatch.stop();
      Logger.error(
        '$operation failed after ${stopwatch.elapsedMilliseconds}ms',
        error: e,
        stackTrace: stack,
      );
      rethrow;
    }
  }
}
