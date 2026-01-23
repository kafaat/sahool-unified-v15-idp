import 'dart:convert';

/// SAHOOL Structured Log Models
/// نماذج السجلات المهيكلة لتطبيق سهول
///
/// Provides comprehensive data models for structured logging with:
/// - Log levels (debug, info, warning, error, fatal)
/// - Structured metadata (userId, fieldId, action, etc.)
/// - Arabic language support
/// - JSON serialization for offline storage and sync

/// Log severity levels
/// مستويات خطورة السجل
enum LogLevel {
  /// Debug logs - for development only
  /// سجلات التصحيح - للتطوير فقط
  debug(0, 'DEBUG', 'تصحيح'),

  /// Info logs - general information
  /// سجلات معلومات - معلومات عامة
  info(1, 'INFO', 'معلومات'),

  /// Warning logs - potential issues
  /// سجلات تحذير - مشاكل محتملة
  warning(2, 'WARNING', 'تحذير'),

  /// Error logs - errors that need attention
  /// سجلات خطأ - أخطاء تحتاج اهتمام
  error(3, 'ERROR', 'خطأ'),

  /// Fatal logs - critical errors
  /// سجلات فادحة - أخطاء حرجة
  fatal(4, 'FATAL', 'فادح');

  const LogLevel(this.value, this.name, this.nameAr);

  /// Numeric value for comparison
  final int value;

  /// English name
  @override
  final String name;

  /// Arabic name
  final String nameAr;

  /// Check if this level is at or above another level
  bool isAtLeast(LogLevel other) => value >= other.value;
}

/// Log category for grouping logs
/// فئة السجل للتجميع
enum LogCategory {
  /// Application lifecycle events
  app('APP', 'التطبيق'),

  /// User actions and interactions
  user('USER', 'المستخدم'),

  /// Field operations
  field('FIELD', 'الحقل'),

  /// Network/API operations
  network('NETWORK', 'الشبكة'),

  /// Sync operations
  sync('SYNC', 'المزامنة'),

  /// Authentication events
  auth('AUTH', 'المصادقة'),

  /// Navigation events
  navigation('NAV', 'التنقل'),

  /// Performance metrics
  performance('PERF', 'الأداء'),

  /// Database operations
  database('DB', 'قاعدة البيانات'),

  /// Notifications
  notification('NOTIF', 'الإشعارات'),

  /// Advisory/AI features
  advisory('ADVISORY', 'الاستشارات'),

  /// Generic/uncategorized
  general('GENERAL', 'عام');

  const LogCategory(this.code, this.nameAr);

  /// Short code for the category
  final String code;

  /// Arabic name
  final String nameAr;
}

/// Structured metadata for log entries
/// البيانات الوصفية المهيكلة لإدخالات السجل
class LogMetadata {
  /// User ID
  final String? userId;

  /// Field ID (for field-related operations)
  final String? fieldId;

  /// Tenant/Farm ID
  final String? tenantId;

  /// Session ID
  final String? sessionId;

  /// Action being performed
  final String? action;

  /// Arabic description of the action
  final String? actionAr;

  /// Screen/route name
  final String? screen;

  /// Request ID for API calls
  final String? requestId;

  /// Duration in milliseconds
  final int? durationMs;

  /// HTTP status code
  final int? statusCode;

  /// Custom additional data
  final Map<String, dynamic>? extra;

  const LogMetadata({
    this.userId,
    this.fieldId,
    this.tenantId,
    this.sessionId,
    this.action,
    this.actionAr,
    this.screen,
    this.requestId,
    this.durationMs,
    this.statusCode,
    this.extra,
  });

  /// Create an empty metadata instance
  factory LogMetadata.empty() => const LogMetadata();

  /// Copy with modifications
  LogMetadata copyWith({
    String? userId,
    String? fieldId,
    String? tenantId,
    String? sessionId,
    String? action,
    String? actionAr,
    String? screen,
    String? requestId,
    int? durationMs,
    int? statusCode,
    Map<String, dynamic>? extra,
  }) {
    return LogMetadata(
      userId: userId ?? this.userId,
      fieldId: fieldId ?? this.fieldId,
      tenantId: tenantId ?? this.tenantId,
      sessionId: sessionId ?? this.sessionId,
      action: action ?? this.action,
      actionAr: actionAr ?? this.actionAr,
      screen: screen ?? this.screen,
      requestId: requestId ?? this.requestId,
      durationMs: durationMs ?? this.durationMs,
      statusCode: statusCode ?? this.statusCode,
      extra: extra ?? this.extra,
    );
  }

  /// Convert to JSON map
  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{};
    if (userId != null) map['user_id'] = userId;
    if (fieldId != null) map['field_id'] = fieldId;
    if (tenantId != null) map['tenant_id'] = tenantId;
    if (sessionId != null) map['session_id'] = sessionId;
    if (action != null) map['action'] = action;
    if (actionAr != null) map['action_ar'] = actionAr;
    if (screen != null) map['screen'] = screen;
    if (requestId != null) map['request_id'] = requestId;
    if (durationMs != null) map['duration_ms'] = durationMs;
    if (statusCode != null) map['status_code'] = statusCode;
    if (extra != null && extra!.isNotEmpty) map['extra'] = extra;
    return map;
  }

  /// Create from JSON map
  factory LogMetadata.fromJson(Map<String, dynamic> json) {
    return LogMetadata(
      userId: json['user_id'] as String?,
      fieldId: json['field_id'] as String?,
      tenantId: json['tenant_id'] as String?,
      sessionId: json['session_id'] as String?,
      action: json['action'] as String?,
      actionAr: json['action_ar'] as String?,
      screen: json['screen'] as String?,
      requestId: json['request_id'] as String?,
      durationMs: json['duration_ms'] as int?,
      statusCode: json['status_code'] as int?,
      extra: json['extra'] as Map<String, dynamic>?,
    );
  }

  /// Check if metadata is empty
  bool get isEmpty =>
      userId == null &&
      fieldId == null &&
      tenantId == null &&
      sessionId == null &&
      action == null &&
      actionAr == null &&
      screen == null &&
      requestId == null &&
      durationMs == null &&
      statusCode == null &&
      (extra == null || extra!.isEmpty);

  @override
  String toString() => toJson().toString();
}

/// Structured log entry
/// إدخال سجل مهيكل
class StructuredLogEntry {
  /// Unique log ID
  final String id;

  /// Timestamp of the log
  final DateTime timestamp;

  /// Log level
  final LogLevel level;

  /// Log category
  final LogCategory category;

  /// Log message (English)
  final String message;

  /// Log message (Arabic) - optional
  final String? messageAr;

  /// Tag for filtering
  final String? tag;

  /// Error object if present
  final String? error;

  /// Stack trace if present
  final String? stackTrace;

  /// Structured metadata
  final LogMetadata metadata;

  /// App version
  final String? appVersion;

  /// Device info
  final String? deviceId;

  /// Platform (iOS, Android)
  final String? platform;

  /// Whether this log has been synced to server
  bool synced;

  StructuredLogEntry({
    required this.id,
    required this.timestamp,
    required this.level,
    required this.category,
    required this.message,
    this.messageAr,
    this.tag,
    this.error,
    this.stackTrace,
    LogMetadata? metadata,
    this.appVersion,
    this.deviceId,
    this.platform,
    this.synced = false,
  }) : metadata = metadata ?? LogMetadata.empty();

  /// Convert to JSON for storage/sync
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'timestamp': timestamp.toUtc().toIso8601String(),
      'level': level.name,
      'category': category.code,
      'message': message,
      if (messageAr != null) 'message_ar': messageAr,
      if (tag != null) 'tag': tag,
      if (error != null) 'error': error,
      if (stackTrace != null) 'stack_trace': stackTrace,
      if (!metadata.isEmpty) 'metadata': metadata.toJson(),
      if (appVersion != null) 'app_version': appVersion,
      if (deviceId != null) 'device_id': deviceId,
      if (platform != null) 'platform': platform,
      'synced': synced,
    };
  }

  /// Convert to JSON string
  String toJsonString() => jsonEncode(toJson());

  /// Create from JSON map
  factory StructuredLogEntry.fromJson(Map<String, dynamic> json) {
    return StructuredLogEntry(
      id: json['id'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      level: LogLevel.values.firstWhere(
        (l) => l.name == json['level'],
        orElse: () => LogLevel.info,
      ),
      category: LogCategory.values.firstWhere(
        (c) => c.code == json['category'],
        orElse: () => LogCategory.general,
      ),
      message: json['message'] as String,
      messageAr: json['message_ar'] as String?,
      tag: json['tag'] as String?,
      error: json['error'] as String?,
      stackTrace: json['stack_trace'] as String?,
      metadata: json['metadata'] != null
          ? LogMetadata.fromJson(json['metadata'] as Map<String, dynamic>)
          : null,
      appVersion: json['app_version'] as String?,
      deviceId: json['device_id'] as String?,
      platform: json['platform'] as String?,
      synced: json['synced'] as bool? ?? false,
    );
  }

  /// Create from JSON string
  factory StructuredLogEntry.fromJsonString(String jsonString) {
    return StructuredLogEntry.fromJson(
      jsonDecode(jsonString) as Map<String, dynamic>,
    );
  }

  /// Get formatted message with metadata
  String get formattedMessage {
    final buffer = StringBuffer();
    buffer.write('[${level.name}]');
    if (tag != null) buffer.write(' [$tag]');
    buffer.write(' $message');
    if (!metadata.isEmpty) {
      buffer.write(' | ${metadata.toJson()}');
    }
    if (error != null) {
      buffer.write(' | Error: $error');
    }
    return buffer.toString();
  }

  /// Get formatted message with Arabic
  String get formattedMessageAr {
    final buffer = StringBuffer();
    buffer.write('[${level.nameAr}]');
    if (tag != null) buffer.write(' [$tag]');
    buffer.write(' ${messageAr ?? message}');
    return buffer.toString();
  }

  /// Copy with modifications
  StructuredLogEntry copyWith({
    String? id,
    DateTime? timestamp,
    LogLevel? level,
    LogCategory? category,
    String? message,
    String? messageAr,
    String? tag,
    String? error,
    String? stackTrace,
    LogMetadata? metadata,
    String? appVersion,
    String? deviceId,
    String? platform,
    bool? synced,
  }) {
    return StructuredLogEntry(
      id: id ?? this.id,
      timestamp: timestamp ?? this.timestamp,
      level: level ?? this.level,
      category: category ?? this.category,
      message: message ?? this.message,
      messageAr: messageAr ?? this.messageAr,
      tag: tag ?? this.tag,
      error: error ?? this.error,
      stackTrace: stackTrace ?? this.stackTrace,
      metadata: metadata ?? this.metadata,
      appVersion: appVersion ?? this.appVersion,
      deviceId: deviceId ?? this.deviceId,
      platform: platform ?? this.platform,
      synced: synced ?? this.synced,
    );
  }

  @override
  String toString() => formattedMessage;
}

/// Log file info for rotation management
/// معلومات ملف السجل لإدارة التدوير
class LogFileInfo {
  /// File path
  final String path;

  /// File name
  final String name;

  /// File size in bytes
  final int sizeBytes;

  /// Creation timestamp
  final DateTime createdAt;

  /// Last modified timestamp
  final DateTime modifiedAt;

  /// Number of entries in the file
  final int entryCount;

  const LogFileInfo({
    required this.path,
    required this.name,
    required this.sizeBytes,
    required this.createdAt,
    required this.modifiedAt,
    required this.entryCount,
  });

  /// Size in MB
  double get sizeMB => sizeBytes / (1024 * 1024);

  /// Check if file exceeds max size (2MB default)
  bool exceedsMaxSize([int maxBytes = 2 * 1024 * 1024]) => sizeBytes >= maxBytes;

  Map<String, dynamic> toJson() => {
        'path': path,
        'name': name,
        'size_bytes': sizeBytes,
        'size_mb': sizeMB,
        'created_at': createdAt.toIso8601String(),
        'modified_at': modifiedAt.toIso8601String(),
        'entry_count': entryCount,
      };
}

/// Log sync status
/// حالة مزامنة السجل
class LogSyncStatus {
  /// Total logs pending sync
  final int pendingCount;

  /// Logs successfully synced
  final int syncedCount;

  /// Logs that failed to sync
  final int failedCount;

  /// Last sync timestamp
  final DateTime? lastSyncAt;

  /// Last sync error if any
  final String? lastError;

  /// Whether sync is in progress
  final bool isSyncing;

  const LogSyncStatus({
    this.pendingCount = 0,
    this.syncedCount = 0,
    this.failedCount = 0,
    this.lastSyncAt,
    this.lastError,
    this.isSyncing = false,
  });

  /// Check if there are pending logs
  bool get hasPending => pendingCount > 0;

  Map<String, dynamic> toJson() => {
        'pending_count': pendingCount,
        'synced_count': syncedCount,
        'failed_count': failedCount,
        'last_sync_at': lastSyncAt?.toIso8601String(),
        'last_error': lastError,
        'is_syncing': isSyncing,
      };

  LogSyncStatus copyWith({
    int? pendingCount,
    int? syncedCount,
    int? failedCount,
    DateTime? lastSyncAt,
    String? lastError,
    bool? isSyncing,
  }) {
    return LogSyncStatus(
      pendingCount: pendingCount ?? this.pendingCount,
      syncedCount: syncedCount ?? this.syncedCount,
      failedCount: failedCount ?? this.failedCount,
      lastSyncAt: lastSyncAt ?? this.lastSyncAt,
      lastError: lastError ?? this.lastError,
      isSyncing: isSyncing ?? this.isSyncing,
    );
  }
}

/// Configuration for the logger
/// إعدادات المسجل
class LoggerConfig {
  /// Minimum log level to capture
  final LogLevel minLevel;

  /// Whether to enable console output
  final bool enableConsole;

  /// Whether to enable file logging
  final bool enableFileLogging;

  /// Whether to enable automatic sync
  final bool enableAutoSync;

  /// Maximum file size in bytes (default 2MB)
  final int maxFileSizeBytes;

  /// Maximum number of log files to keep (default 5)
  final int maxFileCount;

  /// Batch size for syncing logs
  final int syncBatchSize;

  /// Sync interval in seconds
  final int syncIntervalSeconds;

  /// Whether to include stack traces for errors
  final bool includeStackTrace;

  /// Whether to enable PII filtering
  final bool enablePiiFiltering;

  /// Whether this is a debug build
  final bool isDebug;

  const LoggerConfig({
    this.minLevel = LogLevel.debug,
    this.enableConsole = true,
    this.enableFileLogging = true,
    this.enableAutoSync = true,
    this.maxFileSizeBytes = 2 * 1024 * 1024, // 2MB
    this.maxFileCount = 5,
    this.syncBatchSize = 100,
    this.syncIntervalSeconds = 300, // 5 minutes
    this.includeStackTrace = true,
    this.enablePiiFiltering = true,
    this.isDebug = false,
  });

  /// Production configuration
  factory LoggerConfig.production() => const LoggerConfig(
        minLevel: LogLevel.info,
        enableConsole: false,
        enableFileLogging: true,
        enableAutoSync: true,
        includeStackTrace: false,
        enablePiiFiltering: true,
        isDebug: false,
      );

  /// Development configuration
  factory LoggerConfig.development() => const LoggerConfig(
        minLevel: LogLevel.debug,
        enableConsole: true,
        enableFileLogging: true,
        enableAutoSync: false,
        includeStackTrace: true,
        enablePiiFiltering: false,
        isDebug: true,
      );

  LoggerConfig copyWith({
    LogLevel? minLevel,
    bool? enableConsole,
    bool? enableFileLogging,
    bool? enableAutoSync,
    int? maxFileSizeBytes,
    int? maxFileCount,
    int? syncBatchSize,
    int? syncIntervalSeconds,
    bool? includeStackTrace,
    bool? enablePiiFiltering,
    bool? isDebug,
  }) {
    return LoggerConfig(
      minLevel: minLevel ?? this.minLevel,
      enableConsole: enableConsole ?? this.enableConsole,
      enableFileLogging: enableFileLogging ?? this.enableFileLogging,
      enableAutoSync: enableAutoSync ?? this.enableAutoSync,
      maxFileSizeBytes: maxFileSizeBytes ?? this.maxFileSizeBytes,
      maxFileCount: maxFileCount ?? this.maxFileCount,
      syncBatchSize: syncBatchSize ?? this.syncBatchSize,
      syncIntervalSeconds: syncIntervalSeconds ?? this.syncIntervalSeconds,
      includeStackTrace: includeStackTrace ?? this.includeStackTrace,
      enablePiiFiltering: enablePiiFiltering ?? this.enablePiiFiltering,
      isDebug: isDebug ?? this.isDebug,
    );
  }
}
