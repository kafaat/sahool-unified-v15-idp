/// Equipment Local Database - قاعدة بيانات المعدات المحلية
/// Offline-first storage for equipment data
library;

import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'equipment_models.dart';

/// Keys for SharedPreferences storage
class _StorageKeys {
  static const String equipmentList = 'equipment_list';
  static const String equipmentStats = 'equipment_stats';
  static const String maintenanceAlerts = 'maintenance_alerts';
  static const String maintenanceRecords = 'equipment_maintenance_records_';
  static const String fuelLogs = 'equipment_fuel_logs_';
  static const String usageLogs = 'equipment_usage_logs_';
  static const String pendingOperations = 'equipment_pending_operations';
  static const String lastSyncTime = 'equipment_last_sync_time';
  static const String cacheTimestamp = 'equipment_cache_timestamp';
}

/// Pending Operation for offline sync
@immutable
class PendingOperation {
  final String id;
  final String entity;
  final String type; // 'create', 'update', 'delete'
  final Map<String, dynamic> data;
  final DateTime createdAt;
  final int retryCount;

  const PendingOperation({
    required this.id,
    required this.entity,
    required this.type,
    required this.data,
    required this.createdAt,
    this.retryCount = 0,
  });

  factory PendingOperation.fromJson(Map<String, dynamic> json) {
    return PendingOperation(
      id: json['id'] as String,
      entity: json['entity'] as String,
      type: json['type'] as String,
      data: json['data'] as Map<String, dynamic>,
      createdAt: DateTime.parse(json['created_at'] as String),
      retryCount: json['retry_count'] as int? ?? 0,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'entity': entity,
        'type': type,
        'data': data,
        'created_at': createdAt.toIso8601String(),
        'retry_count': retryCount,
      };

  PendingOperation copyWith({
    String? id,
    String? entity,
    String? type,
    Map<String, dynamic>? data,
    DateTime? createdAt,
    int? retryCount,
  }) {
    return PendingOperation(
      id: id ?? this.id,
      entity: entity ?? this.entity,
      type: type ?? this.type,
      data: data ?? this.data,
      createdAt: createdAt ?? this.createdAt,
      retryCount: retryCount ?? this.retryCount,
    );
  }
}

/// Equipment Local Database for offline-first support
class EquipmentLocalDb {
  SharedPreferences? _prefs;

  /// Get SharedPreferences instance
  Future<SharedPreferences> get _preferences async {
    _prefs ??= await SharedPreferences.getInstance();
    return _prefs!;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Equipment CRUD
  // ═══════════════════════════════════════════════════════════════════════════

  /// Save list of equipment to local storage
  Future<void> saveEquipmentList(List<Equipment> equipmentList) async {
    final prefs = await _preferences;
    final jsonList = equipmentList.map((e) => e.toJson()).toList();
    await prefs.setString(_StorageKeys.equipmentList, jsonEncode(jsonList));
    await prefs.setString(
      _StorageKeys.cacheTimestamp,
      DateTime.now().toIso8601String(),
    );
  }

  /// Get equipment list from local storage
  Future<List<Equipment>> getEquipmentList({
    EquipmentType? type,
    EquipmentStatus? status,
    String? fieldId,
    String? search,
  }) async {
    final prefs = await _preferences;
    final jsonString = prefs.getString(_StorageKeys.equipmentList);
    if (jsonString == null) return [];

    try {
      final jsonList = jsonDecode(jsonString) as List;
      var equipmentList = jsonList
          .map((e) => Equipment.fromJson(e as Map<String, dynamic>))
          .toList();

      // Apply filters
      if (type != null) {
        equipmentList =
            equipmentList.where((e) => e.equipmentType == type).toList();
      }
      if (status != null) {
        equipmentList = equipmentList.where((e) => e.status == status).toList();
      }
      if (fieldId != null) {
        equipmentList =
            equipmentList.where((e) => e.fieldId == fieldId).toList();
      }
      if (search != null && search.isNotEmpty) {
        final searchLower = search.toLowerCase();
        equipmentList = equipmentList
            .where((e) =>
                e.name.toLowerCase().contains(searchLower) ||
                (e.nameAr?.contains(search) ?? false) ||
                (e.brand?.toLowerCase().contains(searchLower) ?? false) ||
                (e.model?.toLowerCase().contains(searchLower) ?? false) ||
                (e.serialNumber?.toLowerCase().contains(searchLower) ?? false))
            .toList();
      }

      return equipmentList;
    } catch (e) {
      debugPrint('Error parsing equipment list: $e');
      return [];
    }
  }

  /// Save single equipment to local storage
  Future<void> saveEquipment(Equipment equipment) async {
    final equipmentList = await getEquipmentList();
    final index = equipmentList.indexWhere(
      (e) => e.equipmentId == equipment.equipmentId,
    );

    if (index >= 0) {
      equipmentList[index] = equipment;
    } else {
      equipmentList.add(equipment);
    }

    await saveEquipmentList(equipmentList);
  }

  /// Get equipment by ID from local storage
  Future<Equipment?> getEquipmentById(String equipmentId) async {
    final equipmentList = await getEquipmentList();
    try {
      return equipmentList.firstWhere(
        (e) => e.equipmentId == equipmentId,
      );
    } catch (_) {
      return null;
    }
  }

  /// Get equipment by QR code from local storage
  Future<Equipment?> getEquipmentByQrCode(String qrCode) async {
    final equipmentList = await getEquipmentList();
    try {
      return equipmentList.firstWhere(
        (e) => e.qrCode == qrCode,
      );
    } catch (_) {
      return null;
    }
  }

  /// Delete equipment from local storage
  Future<void> deleteEquipment(String equipmentId) async {
    final equipmentList = await getEquipmentList();
    equipmentList.removeWhere((e) => e.equipmentId == equipmentId);
    await saveEquipmentList(equipmentList);
  }

  /// Clear all cached data for an equipment
  Future<void> clearEquipmentCache(String equipmentId) async {
    final prefs = await _preferences;
    await prefs.remove('${_StorageKeys.maintenanceRecords}$equipmentId');
    await prefs.remove('${_StorageKeys.fuelLogs}$equipmentId');
    await prefs.remove('${_StorageKeys.usageLogs}$equipmentId');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Statistics & Alerts
  // ═══════════════════════════════════════════════════════════════════════════

  /// Save equipment stats
  Future<void> saveStats(EquipmentStats stats) async {
    final prefs = await _preferences;
    await prefs.setString(
        _StorageKeys.equipmentStats, jsonEncode(stats.toJson()));
  }

  /// Get equipment stats from local storage
  Future<EquipmentStats?> getStats() async {
    final prefs = await _preferences;
    final jsonString = prefs.getString(_StorageKeys.equipmentStats);
    if (jsonString == null) return null;

    try {
      return EquipmentStats.fromJson(
        jsonDecode(jsonString) as Map<String, dynamic>,
      );
    } catch (e) {
      debugPrint('Error parsing equipment stats: $e');
      return null;
    }
  }

  /// Calculate stats from local data
  Future<EquipmentStats> calculateLocalStats() async {
    final equipmentList = await getEquipmentList();

    final byType = <String, int>{};
    final byStatus = <String, int>{};
    var operational = 0;
    var maintenance = 0;
    var inactive = 0;
    var lowFuel = 0;
    var needsMaintenance = 0;
    var totalValue = 0.0;
    var totalHours = 0.0;

    for (final equipment in equipmentList) {
      // Count by type
      final typeKey = equipment.equipmentType.value;
      byType[typeKey] = (byType[typeKey] ?? 0) + 1;

      // Count by status
      final statusKey = equipment.status.value;
      byStatus[statusKey] = (byStatus[statusKey] ?? 0) + 1;

      // Count statuses
      switch (equipment.status) {
        case EquipmentStatus.operational:
        case EquipmentStatus.standby:
          operational++;
          break;
        case EquipmentStatus.maintenance:
          maintenance++;
          break;
        case EquipmentStatus.inactive:
        case EquipmentStatus.repair:
          inactive++;
          break;
        case EquipmentStatus.inUse:
          operational++;
          break;
      }

      // Count alerts
      if (equipment.isLowFuel) lowFuel++;
      if (equipment.needsMaintenanceSoon) needsMaintenance++;

      // Sum values
      if (equipment.currentValue != null) totalValue += equipment.currentValue!;
      if (equipment.currentHours != null) totalHours += equipment.currentHours!;
    }

    return EquipmentStats(
      total: equipmentList.length,
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
  // Maintenance Records
  // ═══════════════════════════════════════════════════════════════════════════

  /// Save maintenance records for equipment
  Future<void> saveMaintenanceRecords(
    String equipmentId,
    List<MaintenanceRecord> records,
  ) async {
    final prefs = await _preferences;
    final jsonList = records.map((r) => r.toJson()).toList();
    await prefs.setString(
      '${_StorageKeys.maintenanceRecords}$equipmentId',
      jsonEncode(jsonList),
    );
  }

  /// Get maintenance records from local storage
  Future<List<MaintenanceRecord>> getMaintenanceRecords(
      String equipmentId) async {
    final prefs = await _preferences;
    final jsonString = prefs.getString(
      '${_StorageKeys.maintenanceRecords}$equipmentId',
    );
    if (jsonString == null) return [];

    try {
      final jsonList = jsonDecode(jsonString) as List;
      return jsonList
          .map((r) => MaintenanceRecord.fromJson(r as Map<String, dynamic>))
          .toList();
    } catch (e) {
      debugPrint('Error parsing maintenance records: $e');
      return [];
    }
  }

  /// Add a maintenance record
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
    final jsonList = logs.map((l) => l.toJson()).toList();
    await prefs.setString(
      '${_StorageKeys.fuelLogs}$equipmentId',
      jsonEncode(jsonList),
    );
  }

  /// Get fuel logs from local storage
  Future<List<FuelLog>> getFuelLogs(
    String equipmentId, {
    DateTime? from,
    DateTime? to,
  }) async {
    final prefs = await _preferences;
    final jsonString = prefs.getString('${_StorageKeys.fuelLogs}$equipmentId');
    if (jsonString == null) return [];

    try {
      final jsonList = jsonDecode(jsonString) as List;
      var logs = jsonList
          .map((l) => FuelLog.fromJson(l as Map<String, dynamic>))
          .toList();

      // Apply date filters
      if (from != null) {
        logs = logs.where((l) => l.timestamp.isAfter(from)).toList();
      }
      if (to != null) {
        logs = logs.where((l) => l.timestamp.isBefore(to)).toList();
      }

      return logs;
    } catch (e) {
      debugPrint('Error parsing fuel logs: $e');
      return [];
    }
  }

  /// Add a fuel log
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
    final jsonList = logs.map((l) => l.toJson()).toList();
    await prefs.setString(
      '${_StorageKeys.usageLogs}$equipmentId',
      jsonEncode(jsonList),
    );
  }

  /// Get usage logs from local storage
  Future<List<UsageLog>> getUsageLogs(
    String equipmentId, {
    DateTime? from,
    DateTime? to,
    UsageType? usageType,
  }) async {
    final prefs = await _preferences;
    final jsonString = prefs.getString('${_StorageKeys.usageLogs}$equipmentId');
    if (jsonString == null) return [];

    try {
      final jsonList = jsonDecode(jsonString) as List;
      var logs = jsonList
          .map((l) => UsageLog.fromJson(l as Map<String, dynamic>))
          .toList();

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
      debugPrint('Error parsing usage logs: $e');
      return [];
    }
  }

  /// Save a usage log
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

  /// Get active usage session for equipment
  Future<UsageLog?> getActiveUsageSession(String equipmentId) async {
    final logs = await getUsageLogs(equipmentId);
    try {
      return logs.firstWhere((l) => l.isActive);
    } catch (_) {
      return null;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Pending Operations (Offline Sync)
  // ═══════════════════════════════════════════════════════════════════════════

  /// Add a pending operation
  Future<void> addPendingOperation(PendingOperation operation) async {
    final prefs = await _preferences;
    final operations = await getPendingOperations();
    operations.add(operation);
    final jsonList = operations.map((o) => o.toJson()).toList();
    await prefs.setString(_StorageKeys.pendingOperations, jsonEncode(jsonList));
  }

  /// Get all pending operations
  Future<List<PendingOperation>> getPendingOperations() async {
    final prefs = await _preferences;
    final jsonString = prefs.getString(_StorageKeys.pendingOperations);
    if (jsonString == null) return [];

    try {
      final jsonList = jsonDecode(jsonString) as List;
      return jsonList
          .map((o) => PendingOperation.fromJson(o as Map<String, dynamic>))
          .toList();
    } catch (e) {
      debugPrint('Error parsing pending operations: $e');
      return [];
    }
  }

  /// Update a pending operation
  Future<void> updatePendingOperation(PendingOperation operation) async {
    final prefs = await _preferences;
    final operations = await getPendingOperations();
    final index = operations.indexWhere((o) => o.id == operation.id);
    if (index >= 0) {
      operations[index] = operation;
      final jsonList = operations.map((o) => o.toJson()).toList();
      await prefs.setString(
          _StorageKeys.pendingOperations, jsonEncode(jsonList));
    }
  }

  /// Remove a pending operation
  Future<void> removePendingOperation(String operationId) async {
    final prefs = await _preferences;
    final operations = await getPendingOperations();
    operations.removeWhere((o) => o.id == operationId);
    final jsonList = operations.map((o) => o.toJson()).toList();
    await prefs.setString(_StorageKeys.pendingOperations, jsonEncode(jsonList));
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

  /// Set last sync time
  Future<void> setLastSyncTime(DateTime time) async {
    final prefs = await _preferences;
    await prefs.setString(_StorageKeys.lastSyncTime, time.toIso8601String());
  }

  /// Get last sync time
  Future<DateTime?> getLastSyncTime() async {
    final prefs = await _preferences;
    final timeString = prefs.getString(_StorageKeys.lastSyncTime);
    if (timeString == null) return null;
    return DateTime.tryParse(timeString);
  }

  /// Check if cache is stale (older than 1 hour)
  Future<bool> isCacheStale() async {
    final prefs = await _preferences;
    final timestampString = prefs.getString(_StorageKeys.cacheTimestamp);
    if (timestampString == null) return true;

    final timestamp = DateTime.tryParse(timestampString);
    if (timestamp == null) return true;

    return DateTime.now().difference(timestamp).inHours >= 1;
  }

  /// Clear all equipment data
  Future<void> clearAll() async {
    final prefs = await _preferences;
    final keys = prefs.getKeys().where((k) => k.startsWith('equipment_'));
    for (final key in keys) {
      await prefs.remove(key);
    }
  }
}
