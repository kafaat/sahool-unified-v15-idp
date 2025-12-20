import '../utils/app_logger.dart';

/// SAHOOL Sync Conflict Resolver
/// حل تعارضات المزامنة
///
/// Features:
/// - Multiple resolution strategies
/// - Field-level conflict detection
/// - Custom merge logic
/// - Audit trail

class SyncConflictResolver {
  /// اكتشاف التعارض
  bool detectConflict({
    required Map<String, dynamic> local,
    required Map<String, dynamic> server,
    required Map<String, dynamic> base,
  }) {
    // Get all keys that changed
    final localChanges = _getChangedFields(base, local);
    final serverChanges = _getChangedFields(base, server);

    // Check if same fields changed differently
    for (final field in localChanges) {
      if (serverChanges.contains(field)) {
        if (local[field] != server[field]) {
          AppLogger.d('Conflict detected in field: $field', tag: 'CONFLICT');
          return true;
        }
      }
    }

    return false;
  }

  /// الحصول على الحقول المتغيرة
  Set<String> _getChangedFields(
    Map<String, dynamic> base,
    Map<String, dynamic> current,
  ) {
    final changed = <String>{};

    for (final key in current.keys) {
      if (!base.containsKey(key) || base[key] != current[key]) {
        changed.add(key);
      }
    }

    // Check for deleted fields
    for (final key in base.keys) {
      if (!current.containsKey(key)) {
        changed.add(key);
      }
    }

    return changed;
  }

  /// حل التعارض
  Future<Map<String, dynamic>> resolve({
    required Map<String, dynamic> local,
    required Map<String, dynamic> server,
    required Map<String, dynamic> base,
    required ConflictStrategy strategy,
    ConflictResolver? customResolver,
  }) async {
    switch (strategy) {
      case ConflictStrategy.localWins:
        AppLogger.i('Conflict resolved: local wins', tag: 'CONFLICT');
        return local;

      case ConflictStrategy.serverWins:
        AppLogger.i('Conflict resolved: server wins', tag: 'CONFLICT');
        return server;

      case ConflictStrategy.lastWriteWins:
        return _resolveLastWriteWins(local, server);

      case ConflictStrategy.merge:
        return _resolveMerge(local, server, base);

      case ConflictStrategy.custom:
        if (customResolver != null) {
          return await customResolver(local, server, base);
        }
        // Fallback to server wins
        return server;
    }
  }

  /// حل بآخر كتابة
  Map<String, dynamic> _resolveLastWriteWins(
    Map<String, dynamic> local,
    Map<String, dynamic> server,
  ) {
    final localUpdatedAt = _getUpdatedAt(local);
    final serverUpdatedAt = _getUpdatedAt(server);

    if (localUpdatedAt != null && serverUpdatedAt != null) {
      if (localUpdatedAt.isAfter(serverUpdatedAt)) {
        AppLogger.i('Conflict resolved: local is newer', tag: 'CONFLICT');
        return local;
      } else {
        AppLogger.i('Conflict resolved: server is newer', tag: 'CONFLICT');
        return server;
      }
    }

    // Fallback to server
    return server;
  }

  /// الحصول على تاريخ التحديث
  DateTime? _getUpdatedAt(Map<String, dynamic> data) {
    final updatedAt = data['updatedAt'] ?? data['updated_at'];
    if (updatedAt is String) {
      return DateTime.tryParse(updatedAt);
    }
    if (updatedAt is DateTime) {
      return updatedAt;
    }
    return null;
  }

  /// حل بالدمج
  Map<String, dynamic> _resolveMerge(
    Map<String, dynamic> local,
    Map<String, dynamic> server,
    Map<String, dynamic> base,
  ) {
    final merged = Map<String, dynamic>.from(base);

    // Apply server changes first
    final serverChanges = _getChangedFields(base, server);
    for (final field in serverChanges) {
      if (server.containsKey(field)) {
        merged[field] = server[field];
      } else {
        merged.remove(field);
      }
    }

    // Apply local changes (overwrite if same field changed)
    final localChanges = _getChangedFields(base, local);
    for (final field in localChanges) {
      if (local.containsKey(field)) {
        merged[field] = local[field];
      } else {
        merged.remove(field);
      }
    }

    AppLogger.i('Conflict resolved: merged ${localChanges.length} local + ${serverChanges.length} server changes', tag: 'CONFLICT');
    return merged;
  }

  /// حل تعارضات القائمة
  List<T> resolveListConflict<T>({
    required List<T> local,
    required List<T> server,
    required String Function(T) getId,
    required T Function(T local, T server) mergeItem,
  }) {
    final result = <T>[];
    final serverMap = {for (final item in server) getId(item): item};
    final processedIds = <String>{};

    // Process local items
    for (final localItem in local) {
      final id = getId(localItem);
      processedIds.add(id);

      final serverItem = serverMap[id];
      if (serverItem != null) {
        // Both have this item - merge
        result.add(mergeItem(localItem, serverItem));
      } else {
        // Only in local - keep
        result.add(localItem);
      }
    }

    // Add server-only items
    for (final serverItem in server) {
      final id = getId(serverItem);
      if (!processedIds.contains(id)) {
        result.add(serverItem);
      }
    }

    return result;
  }
}

/// استراتيجيات حل التعارض
enum ConflictStrategy {
  /// البيانات المحلية تفوز
  localWins,

  /// بيانات الخادم تفوز
  serverWins,

  /// آخر كتابة تفوز (بناءً على timestamp)
  lastWriteWins,

  /// دمج التغييرات (field-level)
  merge,

  /// منطق مخصص
  custom,
}

/// نوع الـ Custom Resolver
typedef ConflictResolver = Future<Map<String, dynamic>> Function(
  Map<String, dynamic> local,
  Map<String, dynamic> server,
  Map<String, dynamic> base,
);

/// تفاصيل التعارض
class ConflictDetails {
  final String entityType;
  final String entityId;
  final Map<String, dynamic> local;
  final Map<String, dynamic> server;
  final Map<String, dynamic> base;
  final Set<String> conflictingFields;
  final DateTime detectedAt;

  const ConflictDetails({
    required this.entityType,
    required this.entityId,
    required this.local,
    required this.server,
    required this.base,
    required this.conflictingFields,
    required this.detectedAt,
  });
}

/// سجل حل التعارض
class ConflictResolution {
  final ConflictDetails conflict;
  final ConflictStrategy strategy;
  final Map<String, dynamic> resolvedData;
  final DateTime resolvedAt;
  final String? resolvedBy;

  const ConflictResolution({
    required this.conflict,
    required this.strategy,
    required this.resolvedData,
    required this.resolvedAt,
    this.resolvedBy,
  });
}
