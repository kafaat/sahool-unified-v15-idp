/// Equipment Repository - مستودع بيانات المعدات
/// يتواصل مع FastAPI Equipment Service
library;

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/config/api_config.dart';
import '../../../core/offline/offline_sync_engine.dart';
import '../../../core/utils/app_logger.dart';
import 'equipment_models.dart';

/// Equipment Repository Provider
final equipmentRepositoryProvider = Provider<EquipmentRepository>((ref) {
  return EquipmentRepository();
});

/// نتيجة API
class ApiResult<T> {
  final T? data;
  final String? error;
  final String? errorAr;
  final bool isSuccess;

  const ApiResult._({this.data, this.error, this.errorAr, required this.isSuccess});

  factory ApiResult.success(T data) => ApiResult._(data: data, isSuccess: true);
  factory ApiResult.failure(String error, [String? errorAr]) =>
      ApiResult._(error: error, errorAr: errorAr, isSuccess: false);
}

/// Equipment Repository
class EquipmentRepository {
  final Dio _dio;

  EquipmentRepository({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              sendTimeout: ApiConfig.sendTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  // ─────────────────────────────────────────────────────────────────────────────
  // Equipment CRUD
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب جميع المعدات
  Future<ApiResult<List<Equipment>>> getEquipment({
    EquipmentType? type,
    EquipmentStatus? status,
    String? fieldId,
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

      final response = await _dio.get(
        '/api/v1/equipment',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final equipmentList = (data['equipment'] as List)
          .map((e) => Equipment.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(equipmentList);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch equipment',
        'فشل في جلب المعدات',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب معدة محددة
  Future<ApiResult<Equipment>> getEquipmentById(String equipmentId) async {
    try {
      final response = await _dio.get('/api/v1/equipment/$equipmentId');
      return ApiResult.success(
        Equipment.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Equipment not found', 'المعدة غير موجودة');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch equipment',
        'فشل في جلب المعدة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب معدة عبر QR Code
  Future<ApiResult<Equipment>> getEquipmentByQrCode(String qrCode) async {
    try {
      final response = await _dio.get('/api/v1/equipment/qr/$qrCode');
      return ApiResult.success(
        Equipment.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Equipment not found', 'المعدة غير موجودة');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch equipment',
        'فشل في جلب المعدة',
      );
    } catch (e) {
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
    double? fuelCapacityLiters,
    Map<String, dynamic>? metadata,
  }) async {
    final equipmentData = {
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
      'fuel_capacity_liters': fuelCapacityLiters,
      'metadata': metadata,
      'created_at': DateTime.now().toIso8601String(),
    };

    try {
      final response = await _dio.post(
        '/api/v1/equipment',
        data: equipmentData,
      );

      final equipment = Equipment.fromJson(response.data as Map<String, dynamic>);

      AppLogger.i('Equipment created via API', tag: 'EquipmentRepo', data: {'name': name});

      return ApiResult.success(equipment);
    } on DioException catch (e) {
      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueCreate(
          entityType: 'equipment',
          data: equipmentData,
          priority: SyncPriority.medium,
        );

        AppLogger.w('Equipment creation queued for offline sync (API unavailable)', tag: 'EquipmentRepo');
        return ApiResult.failure(
          'Saved offline - will sync when connected',
          'تم الحفظ محلياً - ستتم المزامنة عند الاتصال',
        );
      }

      return ApiResult.failure(
        e.message ?? 'Failed to create equipment',
        'فشل في إنشاء المعدة',
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

      final equipment = Equipment.fromJson(response.data as Map<String, dynamic>);

      AppLogger.i('Equipment updated via API', tag: 'EquipmentRepo', data: {'equipmentId': equipmentId});

      return ApiResult.success(equipment);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Equipment not found', 'المعدة غير موجودة');
      }

      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueUpdate(
          entityType: 'equipment',
          entityId: equipmentId,
          data: updates,
          priority: SyncPriority.medium,
        );

        AppLogger.w('Equipment update queued for offline sync (API unavailable)', tag: 'EquipmentRepo');
      }

      return ApiResult.failure(
        e.message ?? 'Failed to update equipment',
        'فشل في تحديث المعدة',
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

      final equipment = Equipment.fromJson(response.data as Map<String, dynamic>);

      AppLogger.i('Equipment status updated via API', tag: 'EquipmentRepo', data: {'equipmentId': equipmentId, 'status': status.value});

      return ApiResult.success(equipment);
    } on DioException catch (e) {
      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueUpdate(
          entityType: 'equipment',
          entityId: equipmentId,
          data: {'status': status.value},
          priority: SyncPriority.medium,
        );

        AppLogger.w('Equipment status update queued for offline sync (API unavailable)', tag: 'EquipmentRepo');
      }

      return ApiResult.failure(
        e.message ?? 'Failed to update status',
        'فشل في تحديث الحالة',
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

      return ApiResult.success(
        Equipment.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to update location',
        'فشل في تحديث الموقع',
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

      return ApiResult.success(
        Equipment.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to update telemetry',
        'فشل في تحديث القياسات',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// حذف معدة
  Future<ApiResult<void>> deleteEquipment(String equipmentId) async {
    try {
      await _dio.delete('/api/v1/equipment/$equipmentId');

      AppLogger.i('Equipment deleted via API', tag: 'EquipmentRepo', data: {'equipmentId': equipmentId});

      return ApiResult.success(null);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Equipment not found', 'المعدة غير موجودة');
      }

      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueDelete(
          entityType: 'equipment',
          entityId: equipmentId,
          priority: SyncPriority.medium,
        );

        AppLogger.w('Equipment deletion queued for offline sync (API unavailable)', tag: 'EquipmentRepo');
      }

      return ApiResult.failure(
        e.message ?? 'Failed to delete equipment',
        'فشل في حذف المعدة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Statistics & Alerts
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب إحصائيات المعدات
  Future<ApiResult<EquipmentStats>> getStats() async {
    try {
      final response = await _dio.get('/api/v1/equipment/stats');
      return ApiResult.success(
        EquipmentStats.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch stats',
        'فشل في جلب الإحصائيات',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
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

      return ApiResult.success(alerts);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch alerts',
        'فشل في جلب التنبيهات',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Maintenance Records
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب سجل الصيانة لمعدة
  Future<ApiResult<List<Map<String, dynamic>>>> getMaintenanceHistory(
    String equipmentId, {
    int limit = 20,
  }) async {
    try {
      final response = await _dio.get(
        '/api/v1/equipment/$equipmentId/maintenance',
        queryParameters: {'limit': limit},
      );

      final data = response.data as Map<String, dynamic>;
      final records = (data['records'] as List).cast<Map<String, dynamic>>();

      return ApiResult.success(records);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch maintenance history',
        'فشل في جلب سجل الصيانة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// إضافة سجل صيانة
  Future<ApiResult<Map<String, dynamic>>> addMaintenanceRecord(
    String equipmentId, {
    required MaintenanceType maintenanceType,
    required String description,
    String? descriptionAr,
    String? performedBy,
    double? cost,
    String? notes,
    List<String>? partsReplaced,
  }) async {
    final maintenanceData = {
      'equipment_id': equipmentId,
      'maintenance_type': maintenanceType.value,
      'description': description,
      'description_ar': descriptionAr,
      'performed_by': performedBy,
      'cost': cost,
      'notes': notes,
      'parts_replaced': partsReplaced,
      'created_at': DateTime.now().toIso8601String(),
    };

    try {
      final response = await _dio.post(
        '/api/v1/equipment/$equipmentId/maintenance',
        queryParameters: {
          'maintenance_type': maintenanceType.value,
          'description': description,
          if (descriptionAr != null) 'description_ar': descriptionAr,
          if (performedBy != null) 'performed_by': performedBy,
          if (cost != null) 'cost': cost,
          if (notes != null) 'notes': notes,
          if (partsReplaced != null) 'parts_replaced': partsReplaced,
        },
      );

      AppLogger.i('Maintenance record added via API', tag: 'EquipmentRepo', data: {'equipmentId': equipmentId});

      return ApiResult.success(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueCreate(
          entityType: 'equipment',
          data: {'type': 'maintenance_record', ...maintenanceData},
          priority: SyncPriority.medium,
        );

        AppLogger.w('Maintenance record queued for offline sync (API unavailable)', tag: 'EquipmentRepo');
      }

      return ApiResult.failure(
        e.message ?? 'Failed to add maintenance record',
        'فشل في إضافة سجل الصيانة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }
}
