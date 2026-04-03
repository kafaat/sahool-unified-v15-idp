library;

/// Equipment Repository - مستودع بيانات المعدات
/// يتواصل مع FastAPI Equipment Service
/// Enhanced with offline-first support

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/config/api_config.dart';
import 'equipment_models.dart';
import 'equipment_local_db.dart';

/// Equipment Repository Provider
final equipmentRepositoryProvider = Provider<EquipmentRepository>((ref) {
  return EquipmentRepository();
});

/// Equipment Local Database Provider
final equipmentLocalDbProvider = Provider<EquipmentLocalDb>((ref) {
  return EquipmentLocalDb();
});

/// نتيجة API
class ApiResult<T> {
  final T? data;
  final String? error;
  final String? errorAr;
  final bool isSuccess;
  final int? statusCode;

  const ApiResult._({
    this.data,
    this.error,
    this.errorAr,
    required this.isSuccess,
    this.statusCode,
  });

  factory ApiResult.success(T data, {int? statusCode}) => ApiResult._(
        data: data,
        isSuccess: true,
        statusCode: statusCode,
      );

  factory ApiResult.failure(String error, [String? errorAr, int? statusCode]) =>
      ApiResult._(
        error: error,
        errorAr: errorAr,
        isSuccess: false,
        statusCode: statusCode,
      );

  /// Get localized error message
  String getError(String locale) {
    return locale == 'ar' && errorAr != null
        ? errorAr!
        : (error ?? 'Unknown error');
  }
}

/// Equipment Repository
class EquipmentRepository {
  final Dio _dio;
  final EquipmentLocalDb _localDb;

  EquipmentRepository({Dio? dio, EquipmentLocalDb? localDb})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              sendTimeout: ApiConfig.sendTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            )),
        _localDb = localDb ?? EquipmentLocalDb();

  // ─────────────────────────────────────────────────────────────────────────────
  // Equipment CRUD
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب جميع المعدات with offline fallback
  Future<ApiResult<List<Equipment>>> getEquipment({
    EquipmentType? type,
    EquipmentStatus? status,
    String? fieldId,
    String? search,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };
      if (type != null) queryParams['equipment_type'] = type.value;
      if (status != null) queryParams['status'] = status.value;
      if (fieldId != null) queryParams['field_id'] = fieldId;
      if (search != null && search.isNotEmpty) queryParams['search'] = search;

      final response = await _dio.get(
        '/api/v1/equipment',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final equipmentList = (data['equipment'] as List)
          .map((e) => Equipment.fromJson(e as Map<String, dynamic>))
          .toList();

      // Cache to local DB
      await _localDb.saveEquipmentList(equipmentList);

      return ApiResult.success(equipmentList, statusCode: response.statusCode);
    } on DioException catch (e) {
      // Fallback to local cache
      final cached = await _localDb.getEquipmentList(
        type: type,
        status: status,
        fieldId: fieldId,
        search: search,
      );
      if (cached.isNotEmpty) {
        return ApiResult.success(cached);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch equipment',
        'فشل في جلب المعدات',
        e.response?.statusCode,
      );
    } catch (e) {
      // Fallback to local cache
      final cached = await _localDb.getEquipmentList(
        type: type,
        status: status,
        fieldId: fieldId,
        search: search,
      );
      if (cached.isNotEmpty) {
        return ApiResult.success(cached);
      }
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب معدة محددة with offline fallback
  Future<ApiResult<Equipment>> getEquipmentById(String equipmentId) async {
    try {
      final response = await _dio.get('/api/v1/equipment/$equipmentId');
      final equipment =
          Equipment.fromJson(response.data as Map<String, dynamic>);

      // Cache to local DB
      await _localDb.saveEquipment(equipment);

      return ApiResult.success(equipment, statusCode: response.statusCode);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure(
            'Equipment not found', 'المعدة غير موجودة', 404);
      }
      // Fallback to local cache
      final cached = await _localDb.getEquipmentById(equipmentId);
      if (cached != null) {
        return ApiResult.success(cached);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch equipment',
        'فشل في جلب المعدة',
        e.response?.statusCode,
      );
    } catch (e) {
      // Fallback to local cache
      final cached = await _localDb.getEquipmentById(equipmentId);
      if (cached != null) {
        return ApiResult.success(cached);
      }
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب معدة عبر QR Code with offline fallback
  Future<ApiResult<Equipment>> getEquipmentByQrCode(String qrCode) async {
    try {
      final response = await _dio.get('/api/v1/equipment/qr/$qrCode');
      final equipment =
          Equipment.fromJson(response.data as Map<String, dynamic>);

      // Cache to local DB
      await _localDb.saveEquipment(equipment);

      return ApiResult.success(equipment, statusCode: response.statusCode);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure(
            'Equipment not found', 'المعدة غير موجودة', 404);
      }
      // Fallback to local cache
      final cached = await _localDb.getEquipmentByQrCode(qrCode);
      if (cached != null) {
        return ApiResult.success(cached);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch equipment',
        'فشل في جلب المعدة',
        e.response?.statusCode,
      );
    } catch (e) {
      // Fallback to local cache
      final cached = await _localDb.getEquipmentByQrCode(qrCode);
      if (cached != null) {
        return ApiResult.success(cached);
      }
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// إنشاء معدة جديدة
  Future<ApiResult<Equipment>> createEquipment({
    required String name,
    String? nameAr,
    required EquipmentType type,
    String? brand,
    String? model,
    String? serialNumber,
    int? year,
    DateTime? purchaseDate,
    double? purchasePrice,
    String? fieldId,
    String? locationName,
    int? horsepower,
    FuelType? fuelType,
    double? fuelCapacityLiters,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/equipment',
        data: {
          'name': name,
          'name_ar': nameAr,
          'equipment_type': type.value,
          'brand': brand,
          'model': model,
          'serial_number': serialNumber,
          'year': year,
          'purchase_date': purchaseDate?.toIso8601String(),
          'purchase_price': purchasePrice,
          'field_id': fieldId,
          'location_name': locationName,
          'horsepower': horsepower,
          'fuel_type': fuelType?.value,
          'fuel_capacity_liters': fuelCapacityLiters,
          'metadata': metadata,
        },
      );

      final equipment =
          Equipment.fromJson(response.data as Map<String, dynamic>);

      // Cache to local DB
      await _localDb.saveEquipment(equipment);

      return ApiResult.success(equipment, statusCode: response.statusCode);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to create equipment',
        'فشل في إنشاء المعدة',
        e.response?.statusCode,
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تحديث معدة
  Future<ApiResult<Equipment>> updateEquipment(
    String equipmentId,
    Map<String, dynamic> updates,
  ) async {
    try {
      final response = await _dio.put(
        '/api/v1/equipment/$equipmentId',
        data: updates,
      );

      final equipment =
          Equipment.fromJson(response.data as Map<String, dynamic>);

      // Cache to local DB
      await _localDb.saveEquipment(equipment);

      return ApiResult.success(equipment, statusCode: response.statusCode);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure(
            'Equipment not found', 'المعدة غير موجودة', 404);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to update equipment',
        'فشل في تحديث المعدة',
        e.response?.statusCode,
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تحديث حالة المعدة
  Future<ApiResult<Equipment>> updateEquipmentStatus(
    String equipmentId,
    EquipmentStatus status,
  ) async {
    try {
      final response = await _dio.post(
        '/api/v1/equipment/$equipmentId/status',
        queryParameters: {'status': status.value},
      );

      final equipment =
          Equipment.fromJson(response.data as Map<String, dynamic>);

      // Cache to local DB
      await _localDb.saveEquipment(equipment);

      return ApiResult.success(equipment, statusCode: response.statusCode);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to update status',
        'فشل في تحديث الحالة',
        e.response?.statusCode,
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تحديث موقع المعدة (GPS)
  Future<ApiResult<Equipment>> updateEquipmentLocation(
    String equipmentId, {
    required double lat,
    required double lon,
    String? locationName,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/equipment/$equipmentId/location',
        queryParameters: {
          'lat': lat,
          'lon': lon,
          if (locationName != null) 'location_name': locationName,
        },
      );

      final equipment =
          Equipment.fromJson(response.data as Map<String, dynamic>);

      // Cache to local DB
      await _localDb.saveEquipment(equipment);

      return ApiResult.success(equipment, statusCode: response.statusCode);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to update location',
        'فشل في تحديث الموقع',
        e.response?.statusCode,
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تحديث بيانات القياس (Telemetry)
  Future<ApiResult<Equipment>> updateTelemetry(
    String equipmentId, {
    double? fuelPercent,
    double? hours,
    double? lat,
    double? lon,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/equipment/$equipmentId/telemetry',
        queryParameters: {
          if (fuelPercent != null) 'fuel_percent': fuelPercent,
          if (hours != null) 'hours': hours,
          if (lat != null) 'lat': lat,
          if (lon != null) 'lon': lon,
        },
      );

      final equipment =
          Equipment.fromJson(response.data as Map<String, dynamic>);

      // Cache to local DB
      await _localDb.saveEquipment(equipment);

      return ApiResult.success(equipment, statusCode: response.statusCode);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to update telemetry',
        'فشل في تحديث القياسات',
        e.response?.statusCode,
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// حذف معدة
  Future<ApiResult<void>> deleteEquipment(String equipmentId) async {
    try {
      await _dio.delete('/api/v1/equipment/$equipmentId');

      // Remove from local cache
      await _localDb.deleteEquipment(equipmentId);
      await _localDb.clearEquipmentCache(equipmentId);

      return ApiResult.success(null);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure(
            'Equipment not found', 'المعدة غير موجودة', 404);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to delete equipment',
        'فشل في حذف المعدة',
        e.response?.statusCode,
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Statistics & Alerts
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب إحصائيات المعدات with offline fallback
  Future<ApiResult<EquipmentStats>> getStats() async {
    try {
      final response = await _dio.get('/api/v1/equipment/stats');
      final stats =
          EquipmentStats.fromJson(response.data as Map<String, dynamic>);

      // Cache to local DB
      await _localDb.saveStats(stats);

      return ApiResult.success(stats, statusCode: response.statusCode);
    } on DioException {
      // Fallback to local stats
      final cached = await _localDb.getStats();
      if (cached != null) {
        return ApiResult.success(cached);
      }
      // Calculate from local data
      final calculated = await _localDb.calculateLocalStats();
      return ApiResult.success(calculated);
    } catch (e) {
      // Fallback to local stats
      final cached = await _localDb.getStats();
      if (cached != null) {
        return ApiResult.success(cached);
      }
      final calculated = await _localDb.calculateLocalStats();
      return ApiResult.success(calculated);
    }
  }

  /// جلب تنبيهات الصيانة
  Future<ApiResult<List<MaintenanceAlert>>> getMaintenanceAlerts({
    MaintenancePriority? priority,
    bool overdueOnly = false,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'overdue_only': overdueOnly,
      };
      if (priority != null) queryParams['priority'] = priority.value;

      final response = await _dio.get(
        '/api/v1/equipment/alerts',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final alerts = (data['alerts'] as List)
          .map((e) => MaintenanceAlert.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(alerts, statusCode: response.statusCode);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch alerts',
        'فشل في جلب التنبيهات',
        e.response?.statusCode,
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Maintenance Records
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب سجل الصيانة لمعدة with offline fallback
  Future<ApiResult<List<MaintenanceRecord>>> getMaintenanceHistory(
    String equipmentId, {
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final response = await _dio.get(
        '/api/v1/equipment/$equipmentId/maintenance',
        queryParameters: {'limit': limit, 'offset': offset},
      );

      final data = response.data as Map<String, dynamic>;
      final records = (data['records'] as List)
          .map((r) => MaintenanceRecord.fromJson(r as Map<String, dynamic>))
          .toList();

      // Cache to local DB
      await _localDb.saveMaintenanceRecords(equipmentId, records);

      return ApiResult.success(records, statusCode: response.statusCode);
    } on DioException catch (e) {
      // Fallback to local cache
      final cached = await _localDb.getMaintenanceRecords(equipmentId);
      if (cached.isNotEmpty) {
        return ApiResult.success(cached);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch maintenance history',
        'فشل في جلب سجل الصيانة',
        e.response?.statusCode,
      );
    } catch (e) {
      // Fallback to local cache
      final cached = await _localDb.getMaintenanceRecords(equipmentId);
      if (cached.isNotEmpty) {
        return ApiResult.success(cached);
      }
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// إضافة سجل صيانة
  Future<ApiResult<MaintenanceRecord>> addMaintenanceRecord(
    String equipmentId, {
    required MaintenanceType maintenanceType,
    required String description,
    String? descriptionAr,
    String? performedBy,
    double? cost,
    String? notes,
    List<String>? partsReplaced,
    double? hoursAtMaintenance,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/equipment/$equipmentId/maintenance',
        data: {
          'maintenance_type': maintenanceType.value,
          'description': description,
          'description_ar': descriptionAr,
          'performed_by': performedBy,
          'cost': cost,
          'notes': notes,
          'parts_replaced': partsReplaced,
          'hours_at_maintenance': hoursAtMaintenance,
        },
      );

      final record =
          MaintenanceRecord.fromJson(response.data as Map<String, dynamic>);

      // Cache to local DB
      await _localDb.addMaintenanceRecord(record);

      return ApiResult.success(record, statusCode: response.statusCode);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to add maintenance record',
        'فشل في إضافة سجل الصيانة',
        e.response?.statusCode,
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جدولة صيانة
  Future<ApiResult<ScheduledMaintenance>> scheduleMaintenance(
    String equipmentId, {
    required MaintenanceType maintenanceType,
    required MaintenancePriority priority,
    required String description,
    String? descriptionAr,
    required DateTime scheduledDate,
    double? scheduledAtHours,
    bool isRecurring = false,
    int? recurringIntervalDays,
    int? recurringIntervalHours,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/equipment/$equipmentId/maintenance/schedule',
        data: {
          'maintenance_type': maintenanceType.value,
          'priority': priority.value,
          'description': description,
          'description_ar': descriptionAr,
          'scheduled_date': scheduledDate.toIso8601String(),
          'scheduled_at_hours': scheduledAtHours,
          'is_recurring': isRecurring,
          'recurring_interval_days': recurringIntervalDays,
          'recurring_interval_hours': recurringIntervalHours,
        },
      );

      return ApiResult.success(
        ScheduledMaintenance.fromJson(response.data as Map<String, dynamic>),
        statusCode: response.statusCode,
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to schedule maintenance',
        'فشل في جدولة الصيانة',
        e.response?.statusCode,
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Fuel Logs
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get fuel logs for equipment with offline fallback
  Future<ApiResult<List<FuelLog>>> getFuelLogs(
    String equipmentId, {
    DateTime? from,
    DateTime? to,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };
      if (from != null) queryParams['from'] = from.toIso8601String();
      if (to != null) queryParams['to'] = to.toIso8601String();

      final response = await _dio.get(
        '/api/v1/equipment/$equipmentId/fuel',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final logs = (data['logs'] as List)
          .map((l) => FuelLog.fromJson(l as Map<String, dynamic>))
          .toList();

      // Cache to local DB
      await _localDb.saveFuelLogs(equipmentId, logs);

      return ApiResult.success(logs, statusCode: response.statusCode);
    } on DioException catch (e) {
      // Fallback to local cache
      final cached =
          await _localDb.getFuelLogs(equipmentId, from: from, to: to);
      if (cached.isNotEmpty) {
        return ApiResult.success(cached);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch fuel logs',
        'فشل في جلب سجل الوقود',
        e.response?.statusCode,
      );
    } catch (e) {
      final cached =
          await _localDb.getFuelLogs(equipmentId, from: from, to: to);
      if (cached.isNotEmpty) {
        return ApiResult.success(cached);
      }
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Add fuel log entry
  Future<ApiResult<FuelLog>> addFuelLog(
    String equipmentId, {
    required FuelOperationType operationType,
    FuelType? fuelType,
    required double quantity,
    double? pricePerLiter,
    double? totalCost,
    double? odometerReading,
    String? odometerUnit,
    double? fuelLevelBefore,
    double? fuelLevelAfter,
    String? stationName,
    String? receiptNumber,
    String? notes,
    String? notesAr,
    double? lat,
    double? lon,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/equipment/$equipmentId/fuel',
        data: {
          'operation_type': operationType.value,
          'fuel_type': fuelType?.value,
          'quantity': quantity,
          'price_per_liter': pricePerLiter,
          'total_cost': totalCost,
          'odometer_reading': odometerReading,
          'odometer_unit': odometerUnit,
          'fuel_level_before': fuelLevelBefore,
          'fuel_level_after': fuelLevelAfter,
          'station_name': stationName,
          'receipt_number': receiptNumber,
          'notes': notes,
          'notes_ar': notesAr,
          'lat': lat,
          'lon': lon,
        },
      );

      final log = FuelLog.fromJson(response.data as Map<String, dynamic>);

      // Cache to local DB
      await _localDb.addFuelLog(log);

      return ApiResult.success(log, statusCode: response.statusCode);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to add fuel log',
        'فشل في إضافة سجل الوقود',
        e.response?.statusCode,
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Get fuel consumption summary
  Future<ApiResult<FuelConsumptionSummary>> getFuelConsumptionSummary(
    String equipmentId, {
    DateTime? from,
    DateTime? to,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (from != null) queryParams['from'] = from.toIso8601String();
      if (to != null) queryParams['to'] = to.toIso8601String();

      final response = await _dio.get(
        '/api/v1/equipment/$equipmentId/fuel/summary',
        queryParameters: queryParams,
      );

      return ApiResult.success(
        FuelConsumptionSummary.fromJson(response.data as Map<String, dynamic>),
        statusCode: response.statusCode,
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch fuel summary',
        'فشل في جلب ملخص الوقود',
        e.response?.statusCode,
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Usage Logs
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get usage logs for equipment with offline fallback
  Future<ApiResult<List<UsageLog>>> getUsageLogs(
    String equipmentId, {
    DateTime? from,
    DateTime? to,
    UsageType? usageType,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };
      if (from != null) queryParams['from'] = from.toIso8601String();
      if (to != null) queryParams['to'] = to.toIso8601String();
      if (usageType != null) queryParams['usage_type'] = usageType.value;

      final response = await _dio.get(
        '/api/v1/equipment/$equipmentId/usage',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final logs = (data['logs'] as List)
          .map((l) => UsageLog.fromJson(l as Map<String, dynamic>))
          .toList();

      // Cache to local DB
      await _localDb.saveUsageLogs(equipmentId, logs);

      return ApiResult.success(logs, statusCode: response.statusCode);
    } on DioException catch (e) {
      // Fallback to local cache
      final cached = await _localDb.getUsageLogs(
        equipmentId,
        from: from,
        to: to,
        usageType: usageType,
      );
      if (cached.isNotEmpty) {
        return ApiResult.success(cached);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch usage logs',
        'فشل في جلب سجل الاستخدام',
        e.response?.statusCode,
      );
    } catch (e) {
      final cached = await _localDb.getUsageLogs(
        equipmentId,
        from: from,
        to: to,
        usageType: usageType,
      );
      if (cached.isNotEmpty) {
        return ApiResult.success(cached);
      }
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Start usage session
  Future<ApiResult<UsageLog>> startUsageSession(
    String equipmentId, {
    required UsageType usageType,
    FieldActivityType? activityType,
    String? fieldId,
    String? operatorId,
    String? operatorName,
    double? startHourReading,
    String? notes,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/equipment/$equipmentId/usage/start',
        data: {
          'usage_type': usageType.value,
          'activity_type': activityType?.value,
          'field_id': fieldId,
          'operator_id': operatorId,
          'operator_name': operatorName,
          'start_hour_reading': startHourReading,
          'notes': notes,
        },
      );

      final log = UsageLog.fromJson(response.data as Map<String, dynamic>);

      // Cache to local DB
      await _localDb.saveUsageLog(log);

      return ApiResult.success(log, statusCode: response.statusCode);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to start usage session',
        'فشل في بدء جلسة الاستخدام',
        e.response?.statusCode,
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// End usage session
  Future<ApiResult<UsageLog>> endUsageSession(
    String equipmentId,
    String logId, {
    double? endHourReading,
    double? fuelUsed,
    double? areaWorked,
    double? distanceTraveled,
    String? notes,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/equipment/$equipmentId/usage/$logId/end',
        data: {
          'end_hour_reading': endHourReading,
          'fuel_used': fuelUsed,
          'area_worked': areaWorked,
          'distance_traveled': distanceTraveled,
          'notes': notes,
        },
      );

      final log = UsageLog.fromJson(response.data as Map<String, dynamic>);

      // Cache to local DB
      await _localDb.saveUsageLog(log);

      return ApiResult.success(log, statusCode: response.statusCode);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to end usage session',
        'فشل في إنهاء جلسة الاستخدام',
        e.response?.statusCode,
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Get usage summary
  Future<ApiResult<UsageSummary>> getUsageSummary(
    String equipmentId, {
    DateTime? from,
    DateTime? to,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (from != null) queryParams['from'] = from.toIso8601String();
      if (to != null) queryParams['to'] = to.toIso8601String();

      final response = await _dio.get(
        '/api/v1/equipment/$equipmentId/usage/summary',
        queryParameters: queryParams,
      );

      return ApiResult.success(
        UsageSummary.fromJson(response.data as Map<String, dynamic>),
        statusCode: response.statusCode,
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch usage summary',
        'فشل في جلب ملخص الاستخدام',
        e.response?.statusCode,
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Get active usage session for equipment
  Future<ApiResult<UsageLog?>> getActiveUsageSession(String equipmentId) async {
    final cached = await _localDb.getActiveUsageSession(equipmentId);
    return ApiResult.success(cached);
  }
}
