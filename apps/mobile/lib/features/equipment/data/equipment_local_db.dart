/// Equipment Local Database - قاعدة البيانات المحلية للمعدات
/// Offline-first storage using Drift with SQLCipher encryption
library;

import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../domain/models/equipment.dart';
import '../domain/models/equipment_status.dart';
import '../domain/models/maintenance_record.dart';
import '../domain/models/fuel_log.dart';
import '../domain/models/usage_log.dart';

/// Local DB Provider
final equipmentLocalDbProvider = Provider<EquipmentLocalDb>((ref) {
  return EquipmentLocalDb();
});

/// Pending operation for offline sync
class PendingOperation {
  final String id;
  final String type; // 'create', 'update', 'delete'
  final String entity; // 'equipment', 'maintenance', 'fuel', 'usage'
  final String entityId;
  final Map<String, dynamic> data;
  final DateTime createdAt;
  final int retryCount;

  PendingOperation({
    required this.id,
    required this.type,
    required this.entity,
    required this.entityId,
    required this.data,
    required this.createdAt,
    this.retryCount = 0,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'type': type,
        'entity': entity,
        'entity_id': entityId,
        'data': data,
        'created_at': createdAt.toIso8601String(),
        'retry_count': retryCount,
      };

  factory PendingOperation.fromJson(Map<String, dynamic> json) {
    return PendingOperation(
      id: json['id'] as String,
      type: json['type'] as String,
      entity: json['entity'] as String,
      entityId: json['entity_id'] as String,
      data: json['data'] as Map<String, dynamic>,
      createdAt: DateTime.tryParse(json['created_at'] as String) ?? DateTime.now(),
      retryCount: json['retry_count'] as int? ?? 0,
    );
  }

  PendingOperation copyWith({int? retryCount}) {
    return PendingOperation(
      id: id,
      type: type,
      entity: entity,
      entityId: entityId,
      data: data,
      createdAt: createdAt,
      retryCount: retryCount ?? this.retryCount,
    );
  }
}

/// Top-level function for compute() isolate - parses equipment JSON on background isolate
List<Equipment> _parseEquipmentList(String jsonStr) {
  final jsonList = jsonDecode(jsonStr) as List;
  return jsonList
      .map((e) => Equipment.fromJson(e as Map<String, dynamic>))
      .toList();
}

/// Top-level function for compute() isolate - parses maintenance records on background isolate
List<MaintenanceRecord> _parseMaintenanceRecords(String jsonStr) {
  final jsonList = jsonDecode(jsonStr) as List;
  return jsonList
      .map((e) => MaintenanceRecord.fromJson(e as Map<String, dynamic>))
      .toList();
}

/// Top-level function for compute() isolate - parses fuel logs on background isolate
List<FuelLog> _parseFuelLogs(String jsonStr) {
  final jsonList = jsonDecode(jsonStr) as List;
  return jsonList
      .map((e) => FuelLog.fromJson(e as Map<String, dynamic>))
      .toList();
}

/// Top-level function for compute() isolate - parses usage logs on background isolate
List<UsageLog> _parseUsageLogs(String jsonStr) {
  final jsonList = jsonDecode(jsonStr) as List;
  return jsonList
      .map((e) => UsageLog.fromJson(e as Map<String, dynamic>))
      .toList();
}

/// Top-level function for compute() isolate - parses pending operations on background isolate
List<PendingOperation> _parsePendingOperations(String jsonStr) {
  final jsonList = jsonDecode(jsonStr) as List;
  return jsonList
      .map((e) => PendingOperation.fromJson(e as Map<String, dynamic>))
      .toList();
}

/// Equipment Local Database
/// Uses SharedPreferences for simple offline storage
/// For production, should use Drift with SQLCipher
class EquipmentLocalDb {
  static const String _equipmentKey = 'equipment_cache';
  static const String _maintenanceKey = 'maintenance_cache';
  static const String _fuelLogsKey = 'fuel_logs_cache';
  static const String _usageLogsKey = 'usage_logs_cache';
  static const String _pendingOpsKey = 'equipment_pending_ops';
  static const String _lastSyncKey = 'equipment_last_sync';
  static const String _statsKey = 'equipment_stats_cache';

  SharedPreferences? _prefs;

  /// Initialize the database
  Future<void> initialize() async {
    _prefs ??= await SharedPreferences.getInstance();
  }

  Future<SharedPreferences> get _preferences async {
    _prefs ??= await SharedPreferences.getInstance();
    return _prefs!;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Equipment CRUD
  // ═══════════════════════════════════════════════════════════════════════════

  /// Save equipment list to local storage
  Future<void> saveEquipmentList(List<Equipment> equipment) async {
    final prefs = await _preferences;
    final jsonList = equipment.map((e) => e.toJson()).toList();
    await prefs.setString(_equipmentKey, jsonEncode(jsonList));
    await prefs.setString(_lastSyncKey, DateTime.now().toIso8601String());
  }

  /// Get cached equipment list
  Future<List<Equipment>> getEquipmentList({
    EquipmentType? type,
    EquipmentStatus? status,
    String? fieldId,
    String? search,
  }) async {
    final prefs = await _preferences;
    final jsonStr = prefs.getString(_equipmentKey);

    if (jsonStr == null) return [];

    try {
      // Parse on isolate to avoid blocking UI during app startup
      var equipment = await compute(_parseEquipmentList, jsonStr);

      // Apply filters
      if (type != null) {
        equipment = equipment.where((e) => e.equipmentType == type).toList();
      }
      if (status != null) {
        equipment = equipment.where((e) => e.status == status).toList();
      }
      if (fieldId != null) {
        equipment = equipment.where((e) => e.fieldId == fieldId).toList();
      }
      if (search != null && search.isNotEmpty) {
        final searchLower = search.toLowerCase();
        equipment = equipment.where((e) {
          return e.name.toLowerCase().contains(searchLower) ||
              (e.nameAr?.contains(search) ?? false) ||
              (e.serialNumber?.toLowerCase().contains(searchLower) ?? false) ||
              (e.brand?.toLowerCase().contains(searchLower) ?? false);
        }).toList();
      }

      return equipment;
    } catch (e) {
      return [];
    }
  }

  /// Get single equipment by ID
  Future<Equipment?> getEquipmentById(String equipmentId) async {
    final equipment = await getEquipmentList();
    try {
      return equipment.firstWhere((e) => e.equipmentId == equipmentId);
    } catch (e) {
      return null;
    }
  }

  /// Get equipment by QR code
  Future<Equipment?> getEquipmentByQrCode(String qrCode) async {
    final equipment = await getEquipmentList();
    try {
      return equipment.firstWhere((e) => e.qrCode == qrCode);
    } catch (e) {
      return null;
    }
  }

  /// Save single equipment
  Future<void> saveEquipment(Equipment equipment) async {
    final list = await getEquipmentList();
    final index = list.indexWhere((e) => e.equipmentId == equipment.equipmentId);

    if (index >= 0) {
      list[index] = equipment;
    } else {
      list.add(equipment);
    }

    await saveEquipmentList(list);
  }

  /// Delete equipment
  Future<void> deleteEquipment(String equipmentId) async {
    final list = await getEquipmentList();
    list.removeWhere((e) => e.equipmentId == equipmentId);
    await saveEquipmentList(list);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Maintenance Records
  // ═══════════════════════════════════════════════════════════════════════════

  /// Save maintenance records for equipment
  Future<void> saveMaintenanceRecords(
      String equipmentId, List<MaintenanceRecord> records) async {
    final prefs = await _preferences;
    final key = '${_maintenanceKey}_$equipmentId';
    final jsonList = records.map((e) => e.toJson()).toList();
    await prefs.setString(key, jsonEncode(jsonList));
  }

  /// Get maintenance records for equipment
  Future<List<MaintenanceRecord>> getMaintenanceRecords(
      String equipmentId) async {
    final prefs = await _preferences;
    final key = '${_maintenanceKey}_$equipmentId';
    final jsonStr = prefs.getString(key);

    if (jsonStr == null) return [];

    try {
      return await compute(_parseMaintenanceRecords, jsonStr);
    } catch (e) {
      return [];
    }
  }

  /// Add maintenance record
  Future<void> addMaintenanceRecord(MaintenanceRecord record) async {
    final records = await getMaintenanceRecords(record.equipmentId);
    records.insert(0, record);
    await saveMaintenanceRecords(record.equipmentId, records);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Fuel Logs
  // ═══════════════════════════════════════════════════════════════════════════

  /// Save fuel logs for equipment
  Future<void> saveFuelLogs(String equipmentId, List<FuelLog> logs) async {
    final prefs = await _preferences;
    final key = '${_fuelLogsKey}_$equipmentId';
    final jsonList = logs.map((e) => e.toJson()).toList();
    await prefs.setString(key, jsonEncode(jsonList));
  }

  /// Get fuel logs for equipment
  Future<List<FuelLog>> getFuelLogs(
    String equipmentId, {
    DateTime? from,
    DateTime? to,
  }) async {
    final prefs = await _preferences;
    final key = '${_fuelLogsKey}_$equipmentId';
    final jsonStr = prefs.getString(key);

    if (jsonStr == null) return [];

    try {
      var logs = await compute(_parseFuelLogs, jsonStr);

      // Apply date filters
      if (from != null) {
        logs = logs.where((l) => l.timestamp.isAfter(from)).toList();
      }
      if (to != null) {
        logs = logs.where((l) => l.timestamp.isBefore(to)).toList();
      }

      return logs;
    } catch (e) {
      return [];
    }
  }

  /// Add fuel log
  Future<void> addFuelLog(FuelLog log) async {
    final logs = await getFuelLogs(log.equipmentId);
    logs.insert(0, log);
    await saveFuelLogs(log.equipmentId, logs);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Usage Logs
  // ═══════════════════════════════════════════════════════════════════════════

  /// Save usage logs for equipment
  Future<void> saveUsageLogs(String equipmentId, List<UsageLog> logs) async {
    final prefs = await _preferences;
    final key = '${_usageLogsKey}_$equipmentId';
    final jsonList = logs.map((e) => e.toJson()).toList();
    await prefs.setString(key, jsonEncode(jsonList));
  }

  /// Get usage logs for equipment
  Future<List<UsageLog>> getUsageLogs(
    String equipmentId, {
    DateTime? from,
    DateTime? to,
    UsageType? usageType,
  }) async {
    final prefs = await _preferences;
    final key = '${_usageLogsKey}_$equipmentId';
    final jsonStr = prefs.getString(key);

    if (jsonStr == null) return [];

    try {
      var logs = await compute(_parseUsageLogs, jsonStr);

      // Apply filters
      if (from != null) {
        logs = logs.where((l) => l.startTime.isAfter(from)).toList();
      }
      if (to != null) {
        logs = logs.where((l) => l.startTime.isBefore(to)).toList();
      }
      if (usageType != null) {
        logs = logs.where((l) => l.usageType == usageType).toList();
      }

      return logs;
    } catch (e) {
      return [];
    }
  }

  /// Add or update usage log
  Future<void> saveUsageLog(UsageLog log) async {
    final logs = await getUsageLogs(log.equipmentId);
    final index = logs.indexWhere((l) => l.logId == log.logId);

    if (index >= 0) {
      logs[index] = log;
    } else {
      logs.insert(0, log);
    }

    await saveUsageLogs(log.equipmentId, logs);
  }

  /// Get active usage session
  Future<UsageLog?> getActiveUsageSession(String equipmentId) async {
    final logs = await getUsageLogs(equipmentId);
    try {
      return logs.firstWhere((l) => l.isActive);
    } catch (e) {
      return null;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Statistics
  // ═══════════════════════════════════════════════════════════════════════════

  /// Save equipment stats
  Future<void> saveStats(EquipmentStats stats) async {
    final prefs = await _preferences;
    await prefs.setString(_statsKey, jsonEncode(stats.toJson()));
  }

  /// Get cached equipment stats
  Future<EquipmentStats?> getStats() async {
    final prefs = await _preferences;
    final jsonStr = prefs.getString(_statsKey);

    if (jsonStr == null) return null;

    try {
      return EquipmentStats.fromJson(
          jsonDecode(jsonStr) as Map<String, dynamic>);
    } catch (e) {
      return null;
    }
  }

  /// Calculate stats from local data
  Future<EquipmentStats> calculateLocalStats() async {
    final equipment = await getEquipmentList();

    final byType = <String, int>{};
    final byStatus = <String, int>{};
    int operational = 0;
    int maintenance = 0;
    int inactive = 0;
    int lowFuel = 0;
    int needsMaintenance = 0;
    double totalValue = 0;
    double totalHours = 0;

    for (final e in equipment) {
      // By type
      byType[e.equipmentType.value] = (byType[e.equipmentType.value] ?? 0) + 1;

      // By status
      byStatus[e.status.value] = (byStatus[e.status.value] ?? 0) + 1;

      // Status counts
      switch (e.status) {
        case EquipmentStatus.operational:
        case EquipmentStatus.standby:
        case EquipmentStatus.inUse:
          operational++;
          break;
        case EquipmentStatus.maintenance:
          maintenance++;
          break;
        case EquipmentStatus.inactive:
        case EquipmentStatus.repair:
          inactive++;
          break;
      }

      // Fuel alerts
      if (e.isLowFuel) lowFuel++;

      // Maintenance alerts
      if (e.needsMaintenanceSoon || e.isMaintenanceOverdue) needsMaintenance++;

      // Value
      if (e.purchasePrice != null) totalValue += e.purchasePrice!;

      // Hours
      if (e.currentHours != null) totalHours += e.currentHours!;
    }

    return EquipmentStats(
      total: equipment.length,
      byType: byType,
      byStatus: byStatus,
      operational: operational,
      maintenance: maintenance,
      inactive: inactive,
      lowFuel: lowFuel,
      needsMaintenance: needsMaintenance,
      totalValue: totalValue,
      totalHours: totalHours,
      lastUpdated: DateTime.now(),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Pending Operations (Offline Sync)
  // ═══════════════════════════════════════════════════════════════════════════

  /// Add pending operation for sync
  Future<void> addPendingOperation(PendingOperation operation) async {
    final prefs = await _preferences;
    final operations = await getPendingOperations();
    operations.add(operation);
    final jsonList = operations.map((e) => e.toJson()).toList();
    await prefs.setString(_pendingOpsKey, jsonEncode(jsonList));
  }

  /// Get all pending operations
  Future<List<PendingOperation>> getPendingOperations() async {
    final prefs = await _preferences;
    final jsonStr = prefs.getString(_pendingOpsKey);

    if (jsonStr == null) return [];

    try {
      return await compute(_parsePendingOperations, jsonStr);
    } catch (e) {
      return [];
    }
  }

  /// Remove pending operation after successful sync
  Future<void> removePendingOperation(String operationId) async {
    final prefs = await _preferences;
    final operations = await getPendingOperations();
    operations.removeWhere((e) => e.id == operationId);
    final jsonList = operations.map((e) => e.toJson()).toList();
    await prefs.setString(_pendingOpsKey, jsonEncode(jsonList));
  }

  /// Update pending operation (e.g., increment retry count)
  Future<void> updatePendingOperation(PendingOperation operation) async {
    final prefs = await _preferences;
    final operations = await getPendingOperations();
    final index = operations.indexWhere((e) => e.id == operation.id);

    if (index >= 0) {
      operations[index] = operation;
      final jsonList = operations.map((e) => e.toJson()).toList();
      await prefs.setString(_pendingOpsKey, jsonEncode(jsonList));
    }
  }

  /// Check if there are pending operations
  Future<bool> hasPendingOperations() async {
    final operations = await getPendingOperations();
    return operations.isNotEmpty;
  }

  /// Get count of pending operations
  Future<int> getPendingOperationsCount() async {
    final operations = await getPendingOperations();
    return operations.length;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Sync Status
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get last sync timestamp
  Future<DateTime?> getLastSyncTime() async {
    final prefs = await _preferences;
    final timeStr = prefs.getString(_lastSyncKey);
    if (timeStr == null) return null;
    return DateTime.tryParse(timeStr); // null if invalid → forces re-sync
  }

  /// Update last sync timestamp
  Future<void> updateLastSyncTime() async {
    final prefs = await _preferences;
    await prefs.setString(_lastSyncKey, DateTime.now().toIso8601String());
  }

  /// Check if cache is stale (older than specified duration)
  Future<bool> isCacheStale({Duration maxAge = const Duration(hours: 1)}) async {
    final lastSync = await getLastSyncTime();
    if (lastSync == null) return true;
    return DateTime.now().difference(lastSync) > maxAge;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Clear Data
  // ═══════════════════════════════════════════════════════════════════════════

  /// Clear all equipment cache
  Future<void> clearCache() async {
    final prefs = await _preferences;
    final keys = prefs.getKeys();

    for (final key in keys) {
      if (key.startsWith('equipment') ||
          key.startsWith(_maintenanceKey) ||
          key.startsWith(_fuelLogsKey) ||
          key.startsWith(_usageLogsKey)) {
        await prefs.remove(key);
      }
    }
  }

  /// Clear cache for specific equipment
  Future<void> clearEquipmentCache(String equipmentId) async {
    final prefs = await _preferences;
    await prefs.remove('${_maintenanceKey}_$equipmentId');
    await prefs.remove('${_fuelLogsKey}_$equipmentId');
    await prefs.remove('${_usageLogsKey}_$equipmentId');
  }
}
