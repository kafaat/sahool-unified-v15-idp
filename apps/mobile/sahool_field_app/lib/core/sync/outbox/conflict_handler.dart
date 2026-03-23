import 'dart:convert';

import '../../storage/database.dart';
import '../../utils/app_logger.dart';

/// SAHOOL Conflict Handler
/// معالج التعارضات
///
/// Handles conflict detection and resolution for the outbox pattern.
/// Supports multiple resolution strategies and provides audit trail.
///
/// Features:
/// - Field-level conflict detection
/// - Multiple resolution strategies
/// - Three-way merge support
/// - Audit logging
/// - User notification

class ConflictHandler {
  final AppDatabase _db;
  final ConflictStrategy defaultStrategy;

  ConflictHandler({
    required AppDatabase database,
    this.defaultStrategy = ConflictStrategy.serverWins,
  }) : _db = database;

  // ═══════════════════════════════════════════════════════════════════════════
  // Conflict Detection - اكتشاف التعارضات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Detect if there's a conflict between local and server data
  ConflictDetectionResult detectConflict({
    required Map<String, dynamic> local,
    required Map<String, dynamic> server,
    required Map<String, dynamic> base,
    Set<String>? ignoredFields,
  }) {
    final effectiveIgnored = ignoredFields ?? _defaultIgnoredFields;

    // Get changed fields
    final localChanges = _getChangedFields(base, local, effectiveIgnored);
    final serverChanges = _getChangedFields(base, server, effectiveIgnored);

    // Find conflicting fields (changed in both with different values)
    final conflictingFields = <String>{};
    for (final field in localChanges) {
      if (serverChanges.contains(field)) {
        if (!_valuesEqual(local[field], server[field])) {
          conflictingFields.add(field);
        }
      }
    }

    return ConflictDetectionResult(
      hasConflict: conflictingFields.isNotEmpty,
      localChanges: localChanges,
      serverChanges: serverChanges,
      conflictingFields: conflictingFields,
    );
  }

  /// Default fields to ignore in conflict detection
  static const _defaultIgnoredFields = <String>{
    'id',
    'created_at',
    'createdAt',
    'updated_at',
    'updatedAt',
    'synced',
    'is_synced',
    'isSynced',
    'etag',
    'version',
    'remote_id',
    'remoteId',
  };

  /// Get fields that changed between base and current
  Set<String> _getChangedFields(
    Map<String, dynamic> base,
    Map<String, dynamic> current,
    Set<String> ignoredFields,
  ) {
    final changed = <String>{};

    for (final key in current.keys) {
      if (ignoredFields.contains(key)) continue;
      if (!base.containsKey(key) || !_valuesEqual(base[key], current[key])) {
        changed.add(key);
      }
    }

    // Check for deleted fields
    for (final key in base.keys) {
      if (ignoredFields.contains(key)) continue;
      if (!current.containsKey(key)) {
        changed.add(key);
      }
    }

    return changed;
  }

  /// Compare values for equality
  bool _valuesEqual(dynamic a, dynamic b) {
    if (a == null && b == null) return true;
    if (a == null || b == null) return false;

    // Handle lists
    if (a is List && b is List) {
      if (a.length != b.length) return false;
      for (int i = 0; i < a.length; i++) {
        if (!_valuesEqual(a[i], b[i])) return false;
      }
      return true;
    }

    // Handle maps
    if (a is Map && b is Map) {
      if (a.length != b.length) return false;
      for (final key in a.keys) {
        if (!b.containsKey(key)) return false;
        if (!_valuesEqual(a[key], b[key])) return false;
      }
      return true;
    }

    return a == b;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Conflict Resolution - حل التعارضات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Resolve conflict using specified strategy
  Future<ConflictResolutionResult> resolve({
    required String entityType,
    required String entityId,
    required String tenantId,
    required Map<String, dynamic> local,
    required Map<String, dynamic> server,
    required Map<String, dynamic> base,
    ConflictStrategy? strategy,
    CustomConflictResolver? customResolver,
  }) async {
    final effectiveStrategy = strategy ?? defaultStrategy;

    // Detect the conflict
    final detection = detectConflict(local: local, server: server, base: base);

    Map<String, dynamic> resolved;
    String resolutionMethod;

    switch (effectiveStrategy) {
      case ConflictStrategy.localWins:
        resolved = Map.from(local);
        resolutionMethod = 'local_wins';
        break;

      case ConflictStrategy.serverWins:
        resolved = Map.from(server);
        resolutionMethod = 'server_wins';
        break;

      case ConflictStrategy.lastWriteWins:
        resolved = _resolveLastWriteWins(local, server);
        resolutionMethod = 'last_write_wins';
        break;

      case ConflictStrategy.merge:
        resolved = _resolveMerge(local, server, base, detection);
        resolutionMethod = 'merge';
        break;

      case ConflictStrategy.fieldLevel:
        resolved = _resolveFieldLevel(local, server, base, detection);
        resolutionMethod = 'field_level';
        break;

      case ConflictStrategy.custom:
        if (customResolver != null) {
          resolved = await customResolver(local, server, base, detection);
          resolutionMethod = 'custom';
        } else {
          resolved = Map.from(server);
          resolutionMethod = 'server_wins_fallback';
        }
        break;
    }

    // Log the resolution
    await _logResolution(
      entityType: entityType,
      entityId: entityId,
      tenantId: tenantId,
      strategy: effectiveStrategy,
      detection: detection,
      resolved: resolved,
    );

    return ConflictResolutionResult(
      resolved: resolved,
      strategy: effectiveStrategy,
      method: resolutionMethod,
      detection: detection,
    );
  }

  /// Resolve using last write wins (based on updated_at)
  Map<String, dynamic> _resolveLastWriteWins(
    Map<String, dynamic> local,
    Map<String, dynamic> server,
  ) {
    final localUpdatedAt =
        _parseDateTime(local['updated_at'] ?? local['updatedAt']);
    final serverUpdatedAt =
        _parseDateTime(server['updated_at'] ?? server['updatedAt']);

    if (localUpdatedAt != null && serverUpdatedAt != null) {
      return localUpdatedAt.isAfter(serverUpdatedAt)
          ? Map.from(local)
          : Map.from(server);
    }

    // Fallback to server if timestamps unavailable
    return Map.from(server);
  }

  /// Parse datetime from various formats
  DateTime? _parseDateTime(dynamic value) {
    if (value == null) return null;
    if (value is DateTime) return value;
    if (value is String) return DateTime.tryParse(value);
    return null;
  }

  /// Resolve using three-way merge
  Map<String, dynamic> _resolveMerge(
    Map<String, dynamic> local,
    Map<String, dynamic> server,
    Map<String, dynamic> base,
    ConflictDetectionResult detection,
  ) {
    final merged = Map<String, dynamic>.from(base);

    // Apply non-conflicting server changes
    for (final field in detection.serverChanges) {
      if (!detection.conflictingFields.contains(field)) {
        if (server.containsKey(field)) {
          merged[field] = server[field];
        } else {
          merged.remove(field);
        }
      }
    }

    // Apply non-conflicting local changes (overwrite server)
    for (final field in detection.localChanges) {
      if (!detection.conflictingFields.contains(field)) {
        if (local.containsKey(field)) {
          merged[field] = local[field];
        } else {
          merged.remove(field);
        }
      }
    }

    // For conflicting fields, use server value (server wins for conflicts)
    for (final field in detection.conflictingFields) {
      if (server.containsKey(field)) {
        merged[field] = server[field];
      } else {
        merged.remove(field);
      }
    }

    return merged;
  }

  /// Resolve at field level using per-field rules
  Map<String, dynamic> _resolveFieldLevel(
    Map<String, dynamic> local,
    Map<String, dynamic> server,
    Map<String, dynamic> base,
    ConflictDetectionResult detection,
  ) {
    final merged = Map<String, dynamic>.from(base);

    // Apply all non-conflicting changes
    for (final field in detection.serverChanges) {
      if (!detection.conflictingFields.contains(field)) {
        if (server.containsKey(field)) {
          merged[field] = server[field];
        }
      }
    }

    for (final field in detection.localChanges) {
      if (!detection.conflictingFields.contains(field)) {
        if (local.containsKey(field)) {
          merged[field] = local[field];
        }
      }
    }

    // For conflicting fields, apply field-specific rules
    for (final field in detection.conflictingFields) {
      merged[field] = _resolveFieldConflict(
        field,
        local[field],
        server[field],
        base[field],
      );
    }

    return merged;
  }

  /// Resolve conflict for a specific field based on field type
  dynamic _resolveFieldConflict(
    String fieldName,
    dynamic local,
    dynamic server,
    dynamic base,
  ) {
    // Numeric fields: keep larger value (additive changes)
    if (fieldName.contains('count') ||
        fieldName.contains('quantity') ||
        fieldName.contains('amount')) {
      if (local is num && server is num) {
        return local > server ? local : server;
      }
    }

    // Status fields: use predefined precedence
    if (fieldName == 'status') {
      return _resolveStatusConflict(local, server);
    }

    // Array fields: union
    if (local is List && server is List) {
      return _mergeArrays(local, server);
    }

    // Default: server wins
    return server;
  }

  /// Resolve status field conflict using precedence
  dynamic _resolveStatusConflict(dynamic local, dynamic server) {
    // Status precedence (higher = more important)
    const statusPrecedence = {
      'deleted': 100,
      'done': 90,
      'completed': 90,
      'cancelled': 80,
      'in_progress': 70,
      'active': 60,
      'pending': 50,
      'open': 40,
      'draft': 30,
    };

    final localPrecedence = statusPrecedence[local?.toString()] ?? 0;
    final serverPrecedence = statusPrecedence[server?.toString()] ?? 0;

    return localPrecedence > serverPrecedence ? local : server;
  }

  /// Merge arrays (union with deduplication)
  List _mergeArrays(List local, List server) {
    final result = <dynamic>[];
    final seen = <dynamic>{};

    for (final item in server) {
      if (!seen.contains(item)) {
        result.add(item);
        seen.add(item);
      }
    }

    for (final item in local) {
      if (!seen.contains(item)) {
        result.add(item);
        seen.add(item);
      }
    }

    return result;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Logging & Notifications - التسجيل والإشعارات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Log conflict resolution
  Future<void> _logResolution({
    required String entityType,
    required String entityId,
    required String tenantId,
    required ConflictStrategy strategy,
    required ConflictDetectionResult detection,
    required Map<String, dynamic> resolved,
  }) async {
    await _db.logSync(
      type: 'conflict_resolution',
      status: 'resolved',
      message: jsonEncode({
        'entity_type': entityType,
        'entity_id': entityId,
        'strategy': strategy.name,
        'conflicting_fields': detection.conflictingFields.toList(),
        'local_changes': detection.localChanges.toList(),
        'server_changes': detection.serverChanges.toList(),
      }),
    );

    AppLogger.i(
      'Conflict resolved: $entityType/$entityId using ${strategy.name}',
      tag: 'CONFLICT',
      data: {'fields': detection.conflictingFields.toList()},
    );
  }

  /// Notify user about conflict
  Future<void> notifyUser({
    required String tenantId,
    required String entityType,
    required String entityId,
    required ConflictDetectionResult detection,
    required ConflictStrategy strategy,
  }) async {
    final messageAr = _getConflictMessageAr(entityType, strategy);
    final messageEn = _getConflictMessageEn(entityType, strategy);

    await _db.addSyncEvent(
      tenantId: tenantId,
      type: 'CONFLICT',
      message: messageAr,
      entityType: entityType,
      entityId: entityId,
    );

    AppLogger.i('User notified of conflict: $entityType/$entityId',
        tag: 'CONFLICT');
  }

  String _getConflictMessageAr(String entityType, ConflictStrategy strategy) {
    final entityAr = _getEntityTypeAr(entityType);
    final strategyAr = _getStrategyAr(strategy);
    return 'تم اكتشاف تعارض في $entityAr. $strategyAr';
  }

  String _getConflictMessageEn(String entityType, ConflictStrategy strategy) {
    final strategyEn = _getStrategyEn(strategy);
    return 'Conflict detected in $entityType. $strategyEn';
  }

  String _getEntityTypeAr(String type) {
    switch (type) {
      case 'field':
        return 'الحقل';
      case 'task':
        return 'المهمة';
      default:
        return 'البيانات';
    }
  }

  String _getStrategyAr(ConflictStrategy strategy) {
    switch (strategy) {
      case ConflictStrategy.localWins:
        return 'تم الاحتفاظ بالتغييرات المحلية.';
      case ConflictStrategy.serverWins:
        return 'تم تطبيق نسخة السيرفر.';
      case ConflictStrategy.lastWriteWins:
        return 'تم تطبيق آخر تحديث.';
      case ConflictStrategy.merge:
        return 'تم دمج التغييرات.';
      case ConflictStrategy.fieldLevel:
        return 'تم دمج التغييرات على مستوى الحقل.';
      case ConflictStrategy.custom:
        return 'تم تطبيق قاعدة مخصصة.';
    }
  }

  String _getStrategyEn(ConflictStrategy strategy) {
    switch (strategy) {
      case ConflictStrategy.localWins:
        return 'Local changes kept.';
      case ConflictStrategy.serverWins:
        return 'Server version applied.';
      case ConflictStrategy.lastWriteWins:
        return 'Latest update applied.';
      case ConflictStrategy.merge:
        return 'Changes merged.';
      case ConflictStrategy.fieldLevel:
        return 'Field-level merge applied.';
      case ConflictStrategy.custom:
        return 'Custom rule applied.';
    }
  }
}

/// Conflict detection result
class ConflictDetectionResult {
  final bool hasConflict;
  final Set<String> localChanges;
  final Set<String> serverChanges;
  final Set<String> conflictingFields;

  const ConflictDetectionResult({
    required this.hasConflict,
    required this.localChanges,
    required this.serverChanges,
    required this.conflictingFields,
  });

  /// Number of fields that changed only locally
  int get localOnlyCount => localChanges.difference(serverChanges).length;

  /// Number of fields that changed only on server
  int get serverOnlyCount => serverChanges.difference(localChanges).length;

  /// Number of conflicting fields
  int get conflictCount => conflictingFields.length;
}

/// Conflict resolution result
class ConflictResolutionResult {
  final Map<String, dynamic> resolved;
  final ConflictStrategy strategy;
  final String method;
  final ConflictDetectionResult detection;

  const ConflictResolutionResult({
    required this.resolved,
    required this.strategy,
    required this.method,
    required this.detection,
  });
}

/// Conflict resolution strategies
enum ConflictStrategy {
  /// Local changes always win
  localWins,

  /// Server changes always win
  serverWins,

  /// Most recent update wins (based on timestamp)
  lastWriteWins,

  /// Three-way merge (server wins for conflicts)
  merge,

  /// Field-level merge with type-specific rules
  fieldLevel,

  /// Custom resolver function
  custom,
}

/// Extension for strategy labels
extension ConflictStrategyExtension on ConflictStrategy {
  String get labelAr {
    switch (this) {
      case ConflictStrategy.localWins:
        return 'الأولوية للمحلي';
      case ConflictStrategy.serverWins:
        return 'الأولوية للسيرفر';
      case ConflictStrategy.lastWriteWins:
        return 'آخر كتابة تفوز';
      case ConflictStrategy.merge:
        return 'دمج';
      case ConflictStrategy.fieldLevel:
        return 'دمج على مستوى الحقل';
      case ConflictStrategy.custom:
        return 'مخصص';
    }
  }

  String get labelEn {
    switch (this) {
      case ConflictStrategy.localWins:
        return 'Local wins';
      case ConflictStrategy.serverWins:
        return 'Server wins';
      case ConflictStrategy.lastWriteWins:
        return 'Last write wins';
      case ConflictStrategy.merge:
        return 'Merge';
      case ConflictStrategy.fieldLevel:
        return 'Field-level merge';
      case ConflictStrategy.custom:
        return 'Custom';
    }
  }
}

/// Custom conflict resolver function type
typedef CustomConflictResolver = Future<Map<String, dynamic>> Function(
  Map<String, dynamic> local,
  Map<String, dynamic> server,
  Map<String, dynamic> base,
  ConflictDetectionResult detection,
);
