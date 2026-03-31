/// Irrigation Repository - مستودع بيانات الري
/// Wraps IrrigationApi with offline caching and error handling
/// يتواصل مع Irrigation Smart Service (port 8094)
library;

import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../../core/config/api_config.dart';
import '../../../../core/offline/offline_sync_engine.dart';
import '../../../../core/utils/app_logger.dart';
import '../remote/irrigation_api.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// API Result Wrapper
// ═══════════════════════════════════════════════════════════════════════════════

/// Generic API result with bilingual error support
/// نتيجة API مع دعم الأخطاء ثنائية اللغة
class ApiResult<T> {
  final T? data;
  final String? error;
  final String? errorAr;
  final bool isSuccess;
  final bool isFromCache;

  const ApiResult._({
    this.data,
    this.error,
    this.errorAr,
    required this.isSuccess,
    this.isFromCache = false,
  });

  factory ApiResult.success(T data, {bool fromCache = false}) =>
      ApiResult._(data: data, isSuccess: true, isFromCache: fromCache);

  factory ApiResult.failure(String error, [String? errorAr]) =>
      ApiResult._(error: error, errorAr: errorAr, isSuccess: false);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Cache Keys
// ═══════════════════════════════════════════════════════════════════════════════

class _CacheKeys {
  static const String crops = 'irrigation_crops';
  static const String methods = 'irrigation_methods';
  static String schedule(String fieldId) => 'irrigation_schedule_$fieldId';
  static String waterBalance(String fieldId) => 'irrigation_water_balance_$fieldId';
  static String calculation(String key) => 'irrigation_calc_$key';
  static String lastSync(String key) => 'irrigation_sync_$key';
}

// ═══════════════════════════════════════════════════════════════════════════════
// Irrigation Repository Provider
// ═══════════════════════════════════════════════════════════════════════════════

final irrigationRepositoryProvider = Provider<IrrigationRepository>((ref) {
  return IrrigationRepository();
});

// ═══════════════════════════════════════════════════════════════════════════════
// Irrigation Repository
// ═══════════════════════════════════════════════════════════════════════════════

/// Repository wrapping IrrigationApi with offline caching and error handling
/// مستودع يغلف API الري مع التخزين المؤقت ومعالجة الأخطاء
class IrrigationRepository {
  final Dio _dio;
  SharedPreferences? _prefs;

  /// Cache duration for reference data (crops, methods) - 24 hours
  static const Duration _refDataCacheDuration = Duration(hours: 24);

  /// Cache duration for dynamic data (schedules, calculations) - 1 hour
  static const Duration _dynamicCacheDuration = Duration(hours: 1);

  IrrigationRepository({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              sendTimeout: ApiConfig.sendTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  /// Initialize SharedPreferences for caching
  /// تهيئة التخزين المؤقت
  Future<SharedPreferences> _getPrefs() async {
    _prefs ??= await SharedPreferences.getInstance();
    return _prefs!;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Cache Helpers
  // مساعدات التخزين المؤقت
  // ─────────────────────────────────────────────────────────────────────────────

  /// Save data to local cache with timestamp
  Future<void> _cacheData(String key, dynamic data) async {
    try {
      final prefs = await _getPrefs();
      final encoded = jsonEncode(data);
      await prefs.setString(key, encoded);
      await prefs.setString(
        _CacheKeys.lastSync(key),
        DateTime.now().toIso8601String(),
      );
    } catch (e) {
      // ignore: empty_catches - Silently fail on cache errors - caching is best-effort
    }
  }

  /// Retrieve cached data if not expired
  Future<T?> _getCachedData<T>(
    String key,
    T Function(dynamic json) fromJson,
    Duration maxAge,
  ) async {
    try {
      final prefs = await _getPrefs();
      final cached = prefs.getString(key);
      final syncTime = prefs.getString(_CacheKeys.lastSync(key));

      if (cached == null || syncTime == null) return null;

      final lastSync = DateTime.tryParse(syncTime);
      if (lastSync == null) return null; // Treat invalid sync time as stale
      if (DateTime.now().difference(lastSync) > maxAge) return null;

      final decoded = jsonDecode(cached);
      return fromJson(decoded);
    } catch (e) {
      return null;
    }
  }

  /// Check if cache is stale
  Future<bool> isCacheStale(String key, Duration maxAge) async {
    final prefs = await _getPrefs();
    final syncTime = prefs.getString(_CacheKeys.lastSync(key));
    if (syncTime == null) return true;
    final lastSync = DateTime.tryParse(syncTime) ?? DateTime.now();
    return DateTime.now().difference(lastSync) > maxAge;
  }

  /// Clear all irrigation cache
  /// مسح جميع بيانات التخزين المؤقت للري
  Future<void> clearCache() async {
    final prefs = await _getPrefs();
    final keys = prefs.getKeys().where(
      (k) => k.startsWith('irrigation_'),
    );
    for (final key in keys) {
      await prefs.remove(key);
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Reference Data - البيانات المرجعية
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get available crops for irrigation (with offline cache)
  /// جلب المحاصيل المتاحة للري (مع تخزين مؤقت)
  Future<ApiResult<List<IrrigationCrop>>> getCrops() async {
    try {
      final response = await _dio.get('/api/v1/irrigation/crops');

      if (response.data == null || response.data is! Map<String, dynamic>) {
        return ApiResult.failure('Invalid response format', 'تنسيق الاستجابة غير صالح');
      }
      final data = response.data as Map<String, dynamic>;
      final rawList = data['data'];
      if (rawList == null || rawList is! List) {
        return ApiResult.failure('Missing data field', 'حقل البيانات مفقود');
      }
      final crops = rawList
          .whereType<Map<String, dynamic>>()
          .map((c) => IrrigationCrop.fromJson(c))
          .toList();

      // Cache the response
      await _cacheData(
        _CacheKeys.crops,
        (data['data'] as List? ?? []),
      );

      return ApiResult.success(crops);
    } on DioException catch (e) {
      // Try offline cache
      final cached = await _getCachedData<List<IrrigationCrop>>(
        _CacheKeys.crops,
        (json) => (json as List? ?? [])
            .map((c) => IrrigationCrop.fromJson(c as Map<String, dynamic>))
            .toList(),
        _refDataCacheDuration,
      );
      if (cached != null) {
        return ApiResult.success(cached, fromCache: true);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch crops',
        'فشل في جلب قائمة المحاصيل',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Get available irrigation methods (with offline cache)
  /// جلب طرق الري المتاحة (مع تخزين مؤقت)
  Future<ApiResult<List<IrrigationMethod>>> getMethods() async {
    try {
      final response = await _dio.get('/api/v1/irrigation/methods');

      if (response.data == null || response.data is! Map<String, dynamic>) {
        return ApiResult.failure('Invalid response format', 'تنسيق الاستجابة غير صالح');
      }
      final data = response.data as Map<String, dynamic>;
      final rawList = data['data'];
      if (rawList == null || rawList is! List) {
        return ApiResult.failure('Missing data field', 'حقل البيانات مفقود');
      }
      final methods = rawList
          .whereType<Map<String, dynamic>>()
          .map((m) => IrrigationMethod.fromJson(m))
          .toList();

      // Cache the response
      await _cacheData(_CacheKeys.methods, data['data']);

      return ApiResult.success(methods);
    } on DioException catch (e) {
      // Try offline cache
      final cached = await _getCachedData<List<IrrigationMethod>>(
        _CacheKeys.methods,
        (json) => (json as List? ?? [])
            .map((m) => IrrigationMethod.fromJson(m as Map<String, dynamic>))
            .toList(),
        _refDataCacheDuration,
      );
      if (cached != null) {
        return ApiResult.success(cached, fromCache: true);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch irrigation methods',
        'فشل في جلب طرق الري',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Calculations - الحسابات
  // ─────────────────────────────────────────────────────────────────────────────

  /// Calculate irrigation needs
  /// حساب احتياجات الري
  Future<ApiResult<IrrigationCalculation>> calculate(
    IrrigationCalculationRequest request,
  ) async {
    try {
      final response = await _dio.post(
        '/api/v1/irrigation/calculate',
        data: request.toJson(),
      );

      if (response.data == null || response.data is! Map<String, dynamic>) {
        return ApiResult.failure('Invalid response format', 'تنسيق الاستجابة غير صالح');
      }
      final data = response.data as Map<String, dynamic>;
      final rawData = data['data'];
      if (rawData == null || rawData is! Map<String, dynamic>) {
        return ApiResult.failure('Missing data field', 'حقل البيانات مفقود');
      }
      final calculation = IrrigationCalculation.fromJson(rawData);

      // Cache calculation with composite key
      final cacheKey =
          '${request.cropId}_${request.methodId}_${request.areaHectares}';
      await _cacheData(
        _CacheKeys.calculation(cacheKey),
        data['data'],
      );

      return ApiResult.success(calculation);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to calculate irrigation needs',
        'فشل في حساب احتياجات الري',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Calculate water balance for a field
  /// حساب توازن المياه لحقل
  Future<ApiResult<WaterBalanceData>> calculateWaterBalance({
    required String fieldId,
    required DateTime from,
    required DateTime to,
  }) async {
    try {
      final response = await _dio.get(
        '/api/v1/irrigation/water-balance',
        queryParameters: {
          'field_id': fieldId,
          'from': from.toIso8601String(),
          'to': to.toIso8601String(),
        },
      );

      if (response.data == null || response.data is! Map<String, dynamic>) {
        return ApiResult.failure('Invalid response format', 'تنسيق الاستجابة غير صالح');
      }
      final data = response.data as Map<String, dynamic>;
      final rawData = data['data'];
      if (rawData == null || rawData is! Map<String, dynamic>) {
        return ApiResult.failure('Missing data field', 'حقل البيانات مفقود');
      }
      final waterBalance = WaterBalanceData.fromJson(rawData);

      // Cache water balance
      await _cacheData(_CacheKeys.waterBalance(fieldId), rawData);

      return ApiResult.success(waterBalance);
    } on DioException catch (e) {
      // Try offline cache
      final cached = await _getCachedData<WaterBalanceData>(
        _CacheKeys.waterBalance(fieldId),
        (json) => WaterBalanceData.fromJson(json as Map<String, dynamic>),
        _dynamicCacheDuration,
      );
      if (cached != null) {
        return ApiResult.success(cached, fromCache: true);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to calculate water balance',
        'فشل في حساب توازن المياه',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Calculate irrigation efficiency
  /// حساب كفاءة الري
  Future<ApiResult<IrrigationEfficiencyData>> calculateEfficiency({
    required String methodId,
    required double appliedWaterMm,
    required double consumedWaterMm,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/irrigation/efficiency',
        data: {
          'method_id': methodId,
          'applied_water_mm': appliedWaterMm,
          'consumed_water_mm': consumedWaterMm,
        },
      );

      if (response.data == null || response.data is! Map<String, dynamic>) {
        return ApiResult.failure('Invalid response format', 'تنسيق الاستجابة غير صالح');
      }
      final data = response.data as Map<String, dynamic>;
      final rawData = data['data'];
      if (rawData == null || rawData is! Map<String, dynamic>) {
        return ApiResult.failure('Missing data field', 'حقل البيانات مفقود');
      }
      final efficiency = IrrigationEfficiencyData.fromJson(rawData);

      return ApiResult.success(efficiency);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to calculate efficiency',
        'فشل في حساب كفاءة الري',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Schedule - الجدولة
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get irrigation schedule for a field (with offline cache)
  /// جلب جدول الري لحقل (مع تخزين مؤقت)
  Future<ApiResult<IrrigationSchedule>> getSchedule(String fieldId) async {
    try {
      final response = await _dio.get(
        '/api/v1/irrigation/schedule',
        queryParameters: {'field_id': fieldId},
      );

      if (response.data == null || response.data is! Map<String, dynamic>) {
        return ApiResult.failure('Invalid response format', 'تنسيق الاستجابة غير صالح');
      }
      final data = response.data as Map<String, dynamic>;
      final rawData = data['data'];
      if (rawData == null || rawData is! Map<String, dynamic>) {
        return ApiResult.failure('Missing data field', 'حقل البيانات مفقود');
      }
      final schedule = IrrigationSchedule.fromJson(rawData);

      // Cache schedule
      await _cacheData(
        _CacheKeys.schedule(fieldId),
        rawData,
      );

      return ApiResult.success(schedule);
    } on DioException catch (e) {
      // Try offline cache
      final cached = await _getCachedData<IrrigationSchedule>(
        _CacheKeys.schedule(fieldId),
        (json) => IrrigationSchedule.fromJson(json as Map<String, dynamic>),
        _dynamicCacheDuration,
      );
      if (cached != null) {
        return ApiResult.success(cached, fromCache: true);
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch irrigation schedule',
        'فشل في جلب جدول الري',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// Generate irrigation schedule
  /// إنشاء جدول ري
  Future<ApiResult<IrrigationSchedule>> generateSchedule({
    required String fieldId,
    required String cropId,
    required String methodId,
    required int days,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/irrigation/schedule',
        data: {
          'field_id': fieldId,
          'crop_id': cropId,
          'method_id': methodId,
          'days': days,
        },
      );

      if (response.data == null || response.data is! Map<String, dynamic>) {
        return ApiResult.failure('Invalid response format', 'تنسيق الاستجابة غير صالح');
      }
      final data = response.data as Map<String, dynamic>;
      final rawData = data['data'];
      if (rawData == null || rawData is! Map<String, dynamic>) {
        return ApiResult.failure('Missing data field', 'حقل البيانات مفقود');
      }
      final schedule = IrrigationSchedule.fromJson(rawData);

      // Cache new schedule
      await _cacheData(_CacheKeys.schedule(fieldId), rawData);

      AppLogger.i('Irrigation schedule generated via API', tag: 'IrrigationRepo', data: {'fieldId': fieldId});

      return ApiResult.success(schedule);
    } on DioException catch (e) {
      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueCreate(
          entityType: 'irrigation',
          data: {
            'field_id': fieldId,
            'crop_id': cropId,
            'method_id': methodId,
            'days': days,
            'created_at': DateTime.now().toIso8601String(),
          },
          priority: SyncPriority.medium,
        );

        AppLogger.w('Irrigation schedule queued for offline sync (API unavailable)', tag: 'IrrigationRepo');
        return ApiResult.failure(
          'Saved offline - will sync when connected',
          'تم الحفظ محلياً - ستتم المزامنة عند الاتصال',
        );
      }

      return ApiResult.failure(
        e.message ?? 'Failed to generate irrigation schedule',
        'فشل في إنشاء جدول الري',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Sensor Integration - تكامل المستشعرات
  // ─────────────────────────────────────────────────────────────────────────────

  /// Record sensor reading (queues offline if no connection)
  /// تسجيل قراءة مستشعر (تخزين محلي إذا لم يكن هناك اتصال)
  Future<ApiResult<void>> recordSensorReading({
    required String fieldId,
    required String sensorType,
    required double value,
    required String unit,
  }) async {
    try {
      final timestamp = DateTime.now().toIso8601String();
      final sensorData = {
        'field_id': fieldId,
        'sensor_type': sensorType,
        'value': value,
        'unit': unit,
        'timestamp': timestamp,
      };

      await _dio.post(
        '/api/v1/irrigation/sensor-reading',
        data: sensorData,
      );

      AppLogger.i('Sensor reading recorded via API', tag: 'IrrigationRepo', data: {'fieldId': fieldId, 'sensorType': sensorType});

      return ApiResult.success(null);
    } on DioException catch (e) {
      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        final timestamp = DateTime.now().toIso8601String();
        final sensorData = {
          'type': 'sensor_reading',
          'field_id': fieldId,
          'sensor_type': sensorType,
          'value': value,
          'unit': unit,
          'timestamp': timestamp,
        };

        await OfflineSyncEngine.instance.enqueueCreate(
          entityType: 'irrigation',
          data: sensorData,
          priority: SyncPriority.medium,
        );

        AppLogger.w('Sensor reading queued for offline sync (API unavailable)', tag: 'IrrigationRepo');
        return ApiResult.failure(
          'Saved offline, will sync when connected',
          'تم الحفظ محلياً، سيتم المزامنة عند الاتصال',
        );
      }

      return ApiResult.failure(
        e.message ?? 'Failed to record sensor reading',
        'فشل في تسجيل قراءة المستشعر',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Offline Sync - المزامنة دون اتصال
  // ─────────────────────────────────────────────────────────────────────────────

  /// Sync all pending operations
  /// مزامنة جميع العمليات المعلقة
  Future<int> syncPendingOperations() async {
    final prefs = await _getPrefs();
    final pending = prefs.getStringList('irrigation_pending_ops') ?? [];
    if (pending.isEmpty) return 0;

    var synced = 0;
    final remaining = <String>[];

    for (final opJson in pending) {
      try {
        final op = jsonDecode(opJson) as Map<String, dynamic>;

        if (op['type'] == 'sensor_reading') {
          await _dio.post(
            '/api/v1/irrigation/sensor-reading',
            data: {
              'field_id': op['field_id'],
              'sensor_type': op['sensor_type'],
              'value': op['value'],
              'unit': op['unit'],
              'timestamp': op['timestamp'],
            },
          );
          synced++;
        }
      } catch (e) {
        remaining.add(opJson);
      }
    }

    await prefs.setStringList('irrigation_pending_ops', remaining);
    return synced;
  }

  /// Get pending operations count
  /// عدد العمليات المعلقة
  Future<int> getPendingOperationsCount() async {
    final prefs = await _getPrefs();
    final pending = prefs.getStringList('irrigation_pending_ops') ?? [];
    return pending.length;
  }

  /// Check if there are pending operations
  Future<bool> hasPendingOperations() async {
    return (await getPendingOperationsCount()) > 0;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Data Models - نماذج البيانات
// ═══════════════════════════════════════════════════════════════════════════════

/// Water balance data for a field
/// بيانات توازن المياه لحقل
class WaterBalanceData {
  final double et0;
  final double etc;
  final double rainfall;
  final double irrigationApplied;
  final double soilMoistureCurrent;
  final double soilMoistureFieldCapacity;
  final double soilMoistureWiltingPoint;
  final double deficit;
  final double surplus;
  final String status;
  final String statusAr;

  WaterBalanceData({
    required this.et0,
    required this.etc,
    required this.rainfall,
    required this.irrigationApplied,
    required this.soilMoistureCurrent,
    required this.soilMoistureFieldCapacity,
    required this.soilMoistureWiltingPoint,
    required this.deficit,
    required this.surplus,
    required this.status,
    required this.statusAr,
  });

  factory WaterBalanceData.fromJson(Map<String, dynamic> json) {
    return WaterBalanceData(
      et0: (json['et0'] as num?)?.toDouble() ?? 0,
      etc: (json['etc'] as num?)?.toDouble() ?? 0,
      rainfall: (json['rainfall'] as num?)?.toDouble() ?? 0,
      irrigationApplied: (json['irrigation_applied'] as num?)?.toDouble() ?? 0,
      soilMoistureCurrent:
          (json['soil_moisture_current'] as num?)?.toDouble() ?? 0,
      soilMoistureFieldCapacity:
          (json['soil_moisture_field_capacity'] as num?)?.toDouble() ?? 100,
      soilMoistureWiltingPoint:
          (json['soil_moisture_wilting_point'] as num?)?.toDouble() ?? 0,
      deficit: (json['deficit'] as num?)?.toDouble() ?? 0,
      surplus: (json['surplus'] as num?)?.toDouble() ?? 0,
      status: json['status'] as String? ?? 'unknown',
      statusAr: json['status_ar'] as String? ?? 'غير محدد',
    );
  }

  /// Soil moisture as percentage of field capacity
  double get soilMoisturePercent {
    if (soilMoistureFieldCapacity <= 0) return 0;
    return (soilMoistureCurrent / soilMoistureFieldCapacity * 100)
        .clamp(0, 100);
  }

  /// Whether the field needs irrigation
  bool get needsIrrigation => deficit > 0;
}

/// Irrigation efficiency data
/// بيانات كفاءة الري
class IrrigationEfficiencyData {
  final double efficiency;
  final double appliedWaterMm;
  final double consumedWaterMm;
  final double lostWaterMm;
  final String rating;
  final String ratingAr;
  final String recommendation;
  final String recommendationAr;

  IrrigationEfficiencyData({
    required this.efficiency,
    required this.appliedWaterMm,
    required this.consumedWaterMm,
    required this.lostWaterMm,
    required this.rating,
    required this.ratingAr,
    required this.recommendation,
    required this.recommendationAr,
  });

  factory IrrigationEfficiencyData.fromJson(Map<String, dynamic> json) {
    return IrrigationEfficiencyData(
      efficiency: (json['efficiency'] as num?)?.toDouble() ?? 0,
      appliedWaterMm: (json['applied_water_mm'] as num?)?.toDouble() ?? 0,
      consumedWaterMm: (json['consumed_water_mm'] as num?)?.toDouble() ?? 0,
      lostWaterMm: (json['lost_water_mm'] as num?)?.toDouble() ?? 0,
      rating: json['rating'] as String? ?? 'unknown',
      ratingAr: json['rating_ar'] as String? ?? 'غير محدد',
      recommendation: json['recommendation'] as String? ?? '',
      recommendationAr: json['recommendation_ar'] as String? ?? '',
    );
  }
}
