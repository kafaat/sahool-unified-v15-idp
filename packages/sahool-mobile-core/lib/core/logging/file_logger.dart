import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;

import 'log_models.dart';

/// SAHOOL File Logger with Log Rotation
/// نظام تسجيل الملفات مع تدوير السجلات
///
/// Features:
/// - File-based logging for offline mode
/// - Log rotation (configurable max files and size)
/// - Automatic cleanup of old logs
/// - Thread-safe file operations
/// - JSON-formatted logs for easy parsing
/// - Efficient batch writing
class FileLogger {
  /// Log directory name
  static const String _logDirName = 'sahool_logs';

  /// Log file prefix
  static const String _logFilePrefix = 'sahool_log_';

  /// Log file extension
  static const String _logFileExtension = '.jsonl';

  /// Configuration
  final LoggerConfig config;

  /// Write lock for thread safety
  final _writeLock = Lock();

  /// Current log file
  File? _currentFile;

  /// Current file size
  int _currentFileSize = 0;

  /// Whether initialized
  bool _initialized = false;

  /// Log directory
  Directory? _logDirectory;

  /// Write buffer for batching
  final List<String> _writeBuffer = [];

  /// Buffer flush timer
  Timer? _flushTimer;

  /// Buffer flush interval
  static const Duration _flushInterval = Duration(seconds: 2);

  /// Maximum buffer size before forced flush
  static const int _maxBufferSize = 50;

  FileLogger({LoggerConfig? config})
      : config = config ?? const LoggerConfig();

  /// Initialize the file logger
  /// تهيئة مسجل الملفات
  Future<void> initialize() async {
    if (_initialized) return;

    try {
      // Get application documents directory
      final appDir = await getApplicationDocumentsDirectory();
      _logDirectory = Directory(path.join(appDir.path, _logDirName));

      // Create log directory if it doesn't exist
      if (!await _logDirectory!.exists()) {
        await _logDirectory!.create(recursive: true);
      }

      // Initialize or get current log file
      await _initializeCurrentFile();

      // Start flush timer
      _startFlushTimer();

      _initialized = true;
      debugPrint('FileLogger initialized: ${_logDirectory!.path}');
    } catch (e) {
      debugPrint('FileLogger initialization failed: $e');
    }
  }

  /// Write a log entry to file
  /// كتابة إدخال سجل إلى الملف
  Future<void> writeLog(StructuredLogEntry entry) async {
    if (!_initialized || !config.enableFileLogging) return;

    final jsonLine = '${entry.toJsonString()}\n';
    _writeBuffer.add(jsonLine);

    // Force flush if buffer is full
    if (_writeBuffer.length >= _maxBufferSize) {
      await flush();
    }
  }

  /// Write multiple log entries at once
  /// كتابة عدة إدخالات سجل دفعة واحدة
  Future<void> writeLogs(List<StructuredLogEntry> entries) async {
    if (!_initialized || !config.enableFileLogging) return;

    for (final entry in entries) {
      final jsonLine = '${entry.toJsonString()}\n';
      _writeBuffer.add(jsonLine);
    }

    // Force flush if buffer is full
    if (_writeBuffer.length >= _maxBufferSize) {
      await flush();
    }
  }

  /// Flush write buffer to file
  /// تفريغ المخزن المؤقت للكتابة إلى الملف
  Future<void> flush() async {
    if (_writeBuffer.isEmpty || !_initialized) return;

    await _writeLock.synchronized(() async {
      if (_writeBuffer.isEmpty) return;

      try {
        // Check if rotation is needed
        final totalSize = _writeBuffer.fold<int>(
          0,
          (sum, line) => sum + line.length,
        );

        if (_currentFileSize + totalSize >= config.maxFileSizeBytes) {
          await _rotateLogFile();
        }

        // Write buffer to file
        final content = _writeBuffer.join();
        await _currentFile!.writeAsString(
          content,
          mode: FileMode.append,
          flush: true,
        );

        _currentFileSize += totalSize;
        _writeBuffer.clear();
      } catch (e) {
        debugPrint('FileLogger flush failed: $e');
      }
    });
  }

  /// Get all unsynced log entries
  /// الحصول على جميع إدخالات السجل غير المتزامنة
  Future<List<StructuredLogEntry>> getUnsyncedLogs({int limit = 100}) async {
    if (!_initialized) return [];

    final entries = <StructuredLogEntry>[];

    try {
      final files = await _getLogFiles();

      for (final file in files) {
        if (entries.length >= limit) break;

        final lines = await file.readAsLines();
        for (final line in lines) {
          if (entries.length >= limit) break;
          if (line.trim().isEmpty) continue;

          try {
            final entry = StructuredLogEntry.fromJsonString(line);
            if (!entry.synced) {
              entries.add(entry);
            }
          } catch (e) {
            // Skip malformed entries
            continue;
          }
        }
      }
    } catch (e) {
      debugPrint('FileLogger getUnsyncedLogs failed: $e');
    }

    return entries;
  }

  /// Mark logs as synced
  /// وضع علامة على السجلات كمتزامنة
  Future<void> markAsSynced(List<String> logIds) async {
    if (!_initialized || logIds.isEmpty) return;

    await _writeLock.synchronized(() async {
      try {
        final files = await _getLogFiles();

        for (final file in files) {
          final lines = await file.readAsLines();
          final updatedLines = <String>[];
          bool modified = false;

          for (final line in lines) {
            if (line.trim().isEmpty) continue;

            try {
              final entry = StructuredLogEntry.fromJsonString(line);
              if (logIds.contains(entry.id) && !entry.synced) {
                entry.synced = true;
                updatedLines.add(entry.toJsonString());
                modified = true;
              } else {
                updatedLines.add(line);
              }
            } catch (e) {
              updatedLines.add(line);
            }
          }

          if (modified) {
            await file.writeAsString('${updatedLines.join('\n')}\n');
          }
        }
      } catch (e) {
        debugPrint('FileLogger markAsSynced failed: $e');
      }
    });
  }

  /// Get log files info
  /// الحصول على معلومات ملفات السجل
  Future<List<LogFileInfo>> getLogFilesInfo() async {
    if (!_initialized) return [];

    final infos = <LogFileInfo>[];

    try {
      final files = await _getLogFiles();

      for (final file in files) {
        final stat = await file.stat();
        final lines = await file.readAsLines();

        infos.add(LogFileInfo(
          path: file.path,
          name: path.basename(file.path),
          sizeBytes: stat.size,
          createdAt: stat.changed,
          modifiedAt: stat.modified,
          entryCount: lines.where((l) => l.trim().isNotEmpty).length,
        ));
      }
    } catch (e) {
      debugPrint('FileLogger getLogFilesInfo failed: $e');
    }

    return infos;
  }

  /// Read all logs from a specific file
  /// قراءة جميع السجلات من ملف محدد
  Future<List<StructuredLogEntry>> readLogsFromFile(String filePath) async {
    final entries = <StructuredLogEntry>[];

    try {
      final file = File(filePath);
      if (!await file.exists()) return entries;

      final lines = await file.readAsLines();
      for (final line in lines) {
        if (line.trim().isEmpty) continue;
        try {
          entries.add(StructuredLogEntry.fromJsonString(line));
        } catch (e) {
          // Skip malformed entries
          continue;
        }
      }
    } catch (e) {
      debugPrint('FileLogger readLogsFromFile failed: $e');
    }

    return entries;
  }

  /// Get all logs within a date range
  /// الحصول على جميع السجلات ضمن نطاق تاريخي
  Future<List<StructuredLogEntry>> getLogsByDateRange(
    DateTime start,
    DateTime end, {
    LogLevel? minLevel,
    LogCategory? category,
    int limit = 1000,
  }) async {
    if (!_initialized) return [];

    final entries = <StructuredLogEntry>[];

    try {
      final files = await _getLogFiles();

      for (final file in files) {
        if (entries.length >= limit) break;

        final lines = await file.readAsLines();
        for (final line in lines) {
          if (entries.length >= limit) break;
          if (line.trim().isEmpty) continue;

          try {
            final entry = StructuredLogEntry.fromJsonString(line);

            // Apply filters
            if (entry.timestamp.isBefore(start) ||
                entry.timestamp.isAfter(end)) {
              continue;
            }
            if (minLevel != null && !entry.level.isAtLeast(minLevel)) {
              continue;
            }
            if (category != null && entry.category != category) {
              continue;
            }

            entries.add(entry);
          } catch (e) {
            continue;
          }
        }
      }
    } catch (e) {
      debugPrint('FileLogger getLogsByDateRange failed: $e');
    }

    // Sort by timestamp descending
    entries.sort((a, b) => b.timestamp.compareTo(a.timestamp));

    return entries;
  }

  /// Export logs as JSON string
  /// تصدير السجلات كنص JSON
  Future<String> exportLogsAsJson({
    DateTime? start,
    DateTime? end,
    LogLevel? minLevel,
  }) async {
    final logs = await getLogsByDateRange(
      start ?? DateTime.now().subtract(const Duration(days: 7)),
      end ?? DateTime.now(),
      minLevel: minLevel,
    );

    return jsonEncode(logs.map((e) => e.toJson()).toList());
  }

  /// Clear old synced logs
  /// مسح السجلات القديمة المتزامنة
  Future<int> clearSyncedLogs({int keepDays = 7}) async {
    if (!_initialized) return 0;

    int cleared = 0;
    final cutoff = DateTime.now().subtract(Duration(days: keepDays));

    await _writeLock.synchronized(() async {
      try {
        final files = await _getLogFiles();

        for (final file in files) {
          // Skip current file
          if (file.path == _currentFile?.path) continue;

          final lines = await file.readAsLines();
          final remainingLines = <String>[];

          for (final line in lines) {
            if (line.trim().isEmpty) continue;

            try {
              final entry = StructuredLogEntry.fromJsonString(line);

              // Keep if not synced or within keep period
              if (!entry.synced || entry.timestamp.isAfter(cutoff)) {
                remainingLines.add(line);
              } else {
                cleared++;
              }
            } catch (e) {
              // Keep malformed entries
              remainingLines.add(line);
            }
          }

          // Delete file if empty, otherwise update
          if (remainingLines.isEmpty) {
            await file.delete();
          } else {
            await file.writeAsString('${remainingLines.join('\n')}\n');
          }
        }
      } catch (e) {
        debugPrint('FileLogger clearSyncedLogs failed: $e');
      }
    });

    return cleared;
  }

  /// Clear all logs
  /// مسح جميع السجلات
  Future<void> clearAllLogs() async {
    if (!_initialized) return;

    await _writeLock.synchronized(() async {
      try {
        final files = await _getLogFiles();
        for (final file in files) {
          await file.delete();
        }
        _currentFile = null;
        _currentFileSize = 0;
        await _initializeCurrentFile();
      } catch (e) {
        debugPrint('FileLogger clearAllLogs failed: $e');
      }
    });
  }

  /// Get total log storage size in bytes
  /// الحصول على إجمالي حجم تخزين السجلات بالبايت
  Future<int> getTotalStorageSize() async {
    if (!_initialized) return 0;

    int totalSize = 0;

    try {
      final files = await _getLogFiles();
      for (final file in files) {
        final stat = await file.stat();
        totalSize += stat.size;
      }
    } catch (e) {
      debugPrint('FileLogger getTotalStorageSize failed: $e');
    }

    return totalSize;
  }

  /// Dispose resources
  /// التخلص من الموارد
  Future<void> dispose() async {
    _flushTimer?.cancel();
    await flush();
    _initialized = false;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Private Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Initialize or get current log file
  Future<void> _initializeCurrentFile() async {
    final files = await _getLogFiles();

    if (files.isEmpty) {
      _currentFile = await _createNewLogFile();
      _currentFileSize = 0;
    } else {
      // Use the most recent file if it's not full
      final mostRecent = files.last;
      final stat = await mostRecent.stat();

      if (stat.size < config.maxFileSizeBytes) {
        _currentFile = mostRecent;
        _currentFileSize = stat.size;
      } else {
        _currentFile = await _createNewLogFile();
        _currentFileSize = 0;
      }
    }
  }

  /// Create a new log file
  Future<File> _createNewLogFile() async {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final fileName = '$_logFilePrefix$timestamp$_logFileExtension';
    final file = File(path.join(_logDirectory!.path, fileName));
    await file.create();

    // Clean up old files if needed
    await _cleanupOldFiles();

    return file;
  }

  /// Rotate log file
  Future<void> _rotateLogFile() async {
    _currentFile = await _createNewLogFile();
    _currentFileSize = 0;
  }

  /// Get all log files sorted by name (timestamp)
  Future<List<File>> _getLogFiles() async {
    if (_logDirectory == null) return [];

    final entities = await _logDirectory!.list().toList();
    final files = entities
        .whereType<File>()
        .where((f) =>
            path.basename(f.path).startsWith(_logFilePrefix) &&
            f.path.endsWith(_logFileExtension))
        .toList();

    // Sort by filename (which includes timestamp)
    files.sort((a, b) => path.basename(a.path).compareTo(path.basename(b.path)));

    return files;
  }

  /// Clean up old log files beyond max count
  Future<void> _cleanupOldFiles() async {
    final files = await _getLogFiles();

    if (files.length > config.maxFileCount) {
      // Delete oldest files
      final toDelete = files.length - config.maxFileCount;
      for (int i = 0; i < toDelete; i++) {
        try {
          await files[i].delete();
          debugPrint('FileLogger: Deleted old log file: ${files[i].path}');
        } catch (e) {
          debugPrint('FileLogger: Failed to delete file: $e');
        }
      }
    }
  }

  /// Start the buffer flush timer
  void _startFlushTimer() {
    _flushTimer = Timer.periodic(_flushInterval, (_) {
      flush();
    });
  }
}

/// Simple lock for synchronization
/// قفل بسيط للتزامن
class Lock {
  Completer<void>? _completer;

  Future<T> synchronized<T>(Future<T> Function() action) async {
    while (_completer != null) {
      await _completer!.future;
    }

    _completer = Completer<void>();
    try {
      return await action();
    } finally {
      _completer!.complete();
      _completer = null;
    }
  }
}
