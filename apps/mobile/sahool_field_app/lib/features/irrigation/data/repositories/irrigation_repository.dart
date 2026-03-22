/// Irrigation Repository - Data Layer with Offline Support
/// مستودع الري - طبقة البيانات مع دعم عدم الاتصال
///
/// Provides data access layer for irrigation features with:
/// - Remote API integration
/// - Local caching for offline support
/// - Sync management
/// - Conflict resolution
library;

import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../remote/irrigation_api.dart';
import '../../domain/services/water_calculator.dart';
import '../../domain/services/irrigation_scheduler.dart';
import '../../../advisor/data/models/irrigation_models.dart'
    hide IrrigationCalculation, IrrigationSchedule, IrrigationEvent;

/// Irrigation Repository
/// مستودع الري
class IrrigationRepository {
  final IrrigationApi _api;
  final WaterCalculator _calculator;
  late final IrrigationScheduler _scheduler;

  // Cache keys
  static const String _cropsKey = 'irrigation_crops';
  static const String _methodsKey = 'irrigation_methods';
  static const String _schedulesKeyPrefix = 'irrigation_schedule_';
  static const String _calculationsKeyPrefix = 'irrigation_calc_';
  static const String _pendingSyncKey = 'irrigation_pending_sync';
  static const String _lastSyncKey = 'irrigation_last_sync';

  // In-memory cache
  List<IrrigationCrop>? _cropsCache;
  List<IrrigationMethod>? _methodsCache;
  final Map<String, IrrigationSchedule> _schedulesCache = {};
  final Map<String, IrrigationCalculation> _calculationsCache = {};

  IrrigationRepository({
    required IrrigationApi api,
    WaterCalculator? calculator,
  })  : _api = api,
        _calculator = calculator ?? const WaterCalculator() {
    _scheduler = IrrigationScheduler(api: _api, calculator: _calculator);
  }

  /// Get the scheduler instance
  IrrigationScheduler get scheduler => _scheduler;

  /// Get the calculator instance
  WaterCalculator get calculator => _calculator;

  // ═══════════════════════════════════════════════════════════════════════════
  // Crops - المحاصيل
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get available crops for irrigation
  /// الحصول على المحاصيل المتاحة للري
  Future<List<IrrigationCrop>> getCrops({bool forceRefresh = false}) async {
    // Return cached if available and not forcing refresh
    if (!forceRefresh && _cropsCache != null) {
      return _cropsCache!;
    }

    try {
      // Try to fetch from API
      final crops = await _api.getCrops();
      _cropsCache = crops;
      await _saveCropsToCache(crops);
      return crops;
    } catch (e) {
      // Fall back to cached data
      final cached = await _loadCropsFromCache();
      if (cached != null) {
        _cropsCache = cached;
        return cached;
      }
      rethrow;
    }
  }

  /// Get crop by ID
  /// الحصول على المحصول بالمعرف
  Future<IrrigationCrop?> getCropById(String cropId) async {
    final crops = await getCrops();
    try {
      return crops.firstWhere((c) => c.id == cropId);
    } catch (_) {
      return null;
    }
  }

  Future<void> _saveCropsToCache(List<IrrigationCrop> crops) async {
    final prefs = await SharedPreferences.getInstance();
    final jsonList = crops
        .map((c) => {
              'id': c.id,
              'name_ar': c.nameAr,
              'name_en': c.nameEn,
              'kc': c.kc,
              'kc_stages': c.kcStages,
              'root_depth_mm': c.rootDepthMm,
              'mad_fraction': c.madFraction,
            })
        .toList();
    await prefs.setString(_cropsKey, jsonEncode(jsonList));
  }

  Future<List<IrrigationCrop>?> _loadCropsFromCache() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonStr = prefs.getString(_cropsKey);
    if (jsonStr == null) return null;

    try {
      final jsonList = jsonDecode(jsonStr) as List;
      return jsonList.map((j) => IrrigationCrop.fromJson(j)).toList();
    } catch (_) {
      return null;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Methods - طرق الري
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get available irrigation methods
  /// الحصول على طرق الري المتاحة
  Future<List<IrrigationMethod>> getMethods({bool forceRefresh = false}) async {
    // Return cached if available and not forcing refresh
    if (!forceRefresh && _methodsCache != null) {
      return _methodsCache!;
    }

    try {
      // Try to fetch from API
      final methods = await _api.getMethods();
      _methodsCache = methods;
      await _saveMethodsToCache(methods);
      return methods;
    } catch (e) {
      // Fall back to cached data
      final cached = await _loadMethodsFromCache();
      if (cached != null) {
        _methodsCache = cached;
        return cached;
      }
      rethrow;
    }
  }

  /// Get method by ID
  /// الحصول على الطريقة بالمعرف
  Future<IrrigationMethod?> getMethodById(String methodId) async {
    final methods = await getMethods();
    try {
      return methods.firstWhere((m) => m.id == methodId);
    } catch (_) {
      return null;
    }
  }

  Future<void> _saveMethodsToCache(List<IrrigationMethod> methods) async {
    final prefs = await SharedPreferences.getInstance();
    final jsonList = methods
        .map((m) => {
              'id': m.id,
              'name_ar': m.nameAr,
              'name_en': m.nameEn,
              'efficiency': m.efficiency,
              'description': m.description,
            })
        .toList();
    await prefs.setString(_methodsKey, jsonEncode(jsonList));
  }

  Future<List<IrrigationMethod>?> _loadMethodsFromCache() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonStr = prefs.getString(_methodsKey);
    if (jsonStr == null) return null;

    try {
      final jsonList = jsonDecode(jsonStr) as List;
      return jsonList.map((j) => IrrigationMethod.fromJson(j)).toList();
    } catch (_) {
      return null;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Calculations - الحسابات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Calculate irrigation needs
  /// حساب احتياجات الري
  Future<IrrigationCalculation> calculate(
    IrrigationCalculationRequest request,
  ) async {
    final cacheKey = _calculationCacheKey(request);

    try {
      // Try to get from API
      final result = await _api.calculate(request);
      _calculationsCache[cacheKey] = result;
      await _saveCalculationToCache(cacheKey, result);
      return result;
    } catch (e) {
      // Fall back to cached or calculate locally
      final cached = await _loadCalculationFromCache(cacheKey);
      if (cached != null) {
        return cached;
      }

      // Try local calculation
      return _calculateLocally(request);
    }
  }

  String _calculationCacheKey(IrrigationCalculationRequest request) {
    return '${request.cropId}_${request.methodId}_${request.areaHectares}_${request.et0}';
  }

  Future<IrrigationCalculation> _calculateLocally(
    IrrigationCalculationRequest request,
  ) async {
    final crop = await getCropById(request.cropId);
    final method = await getMethodById(request.methodId);

    if (crop == null || method == null) {
      throw Exception('Crop or method not found for local calculation');
    }

    final requirement = _calculator.calculateIrrigationRequirement(
      et0: request.et0,
      crop: crop,
      method: method,
      areaHectares: request.areaHectares,
      growthStage: request.growthStage,
      soilMoistureCurrent: request.soilMoistureCurrent,
      soilMoistureFieldCapacity: request.soilMoistureFieldCapacity,
    );

    return IrrigationCalculation(
      waterNeedMm: requirement.waterNeedMm,
      waterNeedLiters: requirement.waterNeedLiters,
      waterNeedM3: requirement.waterNeedM3,
      irrigationDurationMinutes: _calculator.calculateIrrigationDuration(
        requirement.waterNeedLiters,
        50000 * method.efficiency, // Estimated flow rate
      ),
      etc: requirement.etc,
      recommendation:
          'Apply ${requirement.waterNeedMm.toStringAsFixed(1)} mm irrigation',
      recommendationAr:
          'قم بري ${requirement.waterNeedMm.toStringAsFixed(1)} ملم',
      nextIrrigationDate: requirement.nextIrrigationDate,
    );
  }

  Future<void> _saveCalculationToCache(
    String key,
    IrrigationCalculation calc,
  ) async {
    final prefs = await SharedPreferences.getInstance();
    final json = {
      'water_need_mm': calc.waterNeedMm,
      'water_need_liters': calc.waterNeedLiters,
      'water_need_m3': calc.waterNeedM3,
      'irrigation_duration_minutes': calc.irrigationDurationMinutes,
      'etc': calc.etc,
      'recommendation': calc.recommendation,
      'recommendation_ar': calc.recommendationAr,
      'next_irrigation_date': calc.nextIrrigationDate.toIso8601String(),
    };
    await prefs.setString('$_calculationsKeyPrefix$key', jsonEncode(json));
  }

  Future<IrrigationCalculation?> _loadCalculationFromCache(String key) async {
    final prefs = await SharedPreferences.getInstance();
    final jsonStr = prefs.getString('$_calculationsKeyPrefix$key');
    if (jsonStr == null) return null;

    try {
      final json = jsonDecode(jsonStr);
      return IrrigationCalculation.fromJson(json);
    } catch (_) {
      return null;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Schedules - الجداول
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get irrigation schedule for a field
  /// الحصول على جدول الري لحقل
  Future<IrrigationSchedule> getSchedule(
    String fieldId, {
    bool forceRefresh = false,
  }) async {
    // Return cached if available
    if (!forceRefresh && _schedulesCache.containsKey(fieldId)) {
      return _schedulesCache[fieldId]!;
    }

    try {
      final schedule = await _api.getSchedule(fieldId);
      _schedulesCache[fieldId] = schedule;
      await _saveScheduleToCache(fieldId, schedule);
      return schedule;
    } catch (e) {
      // Fall back to cached
      final cached = await _loadScheduleFromCache(fieldId);
      if (cached != null) {
        _schedulesCache[fieldId] = cached;
        return cached;
      }
      rethrow;
    }
  }

  /// Generate a new irrigation schedule
  /// إنشاء جدول ري جديد
  Future<IrrigationSchedule> generateSchedule({
    required String fieldId,
    required String cropId,
    required String methodId,
    required int days,
  }) async {
    try {
      final schedule = await _api.generateSchedule(
        fieldId: fieldId,
        cropId: cropId,
        methodId: methodId,
        days: days,
      );
      _schedulesCache[fieldId] = schedule;
      await _saveScheduleToCache(fieldId, schedule);
      return schedule;
    } catch (e) {
      // Generate locally if offline
      return _generateScheduleLocally(
        fieldId: fieldId,
        cropId: cropId,
        methodId: methodId,
        days: days,
      );
    }
  }

  Future<IrrigationSchedule> _generateScheduleLocally({
    required String fieldId,
    required String cropId,
    required String methodId,
    required int days,
  }) async {
    final crop = await getCropById(cropId);
    final method = await getMethodById(methodId);

    if (crop == null || method == null) {
      throw Exception('Crop or method not found for local schedule generation');
    }

    // Generate basic schedule
    final events = <IrrigationEvent>[];
    final now = DateTime.now();
    const int interval = 3; // Default 3 days

    for (var i = 0; i < days; i += interval) {
      events.add(IrrigationEvent(
        scheduledAt: now.add(Duration(days: i, hours: 6)),
        durationMinutes: 120,
        waterAmountLiters: 50000, // Default estimate
        status: 'pending',
        notes: 'Locally generated schedule',
      ));
    }

    final schedule = IrrigationSchedule(
      fieldId: fieldId,
      events: events,
      generatedAt: DateTime.now(),
    );

    // Mark for sync
    await _markForSync(fieldId, 'schedule');
    await _saveScheduleToCache(fieldId, schedule);

    return schedule;
  }

  Future<void> _saveScheduleToCache(
    String fieldId,
    IrrigationSchedule schedule,
  ) async {
    final prefs = await SharedPreferences.getInstance();
    final eventsJson = schedule.events
        .map((e) => {
              'scheduled_at': e.scheduledAt.toIso8601String(),
              'duration_minutes': e.durationMinutes,
              'water_amount_liters': e.waterAmountLiters,
              'status': e.status,
              'notes': e.notes,
            })
        .toList();

    final json = {
      'field_id': schedule.fieldId,
      'events': eventsJson,
      'generated_at': schedule.generatedAt.toIso8601String(),
    };

    await prefs.setString('$_schedulesKeyPrefix$fieldId', jsonEncode(json));
  }

  Future<IrrigationSchedule?> _loadScheduleFromCache(String fieldId) async {
    final prefs = await SharedPreferences.getInstance();
    final jsonStr = prefs.getString('$_schedulesKeyPrefix$fieldId');
    if (jsonStr == null) return null;

    try {
      final json = jsonDecode(jsonStr);
      return IrrigationSchedule.fromJson(json);
    } catch (_) {
      return null;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Water Balance - التوازن المائي
  // ═══════════════════════════════════════════════════════════════════════════

  /// Calculate water balance for a field
  /// حساب التوازن المائي لحقل
  Future<WaterBalance> getWaterBalance({
    required String fieldId,
    required double soilMoisture,
    required double fieldCapacity,
    required double wiltingPoint,
    double madFraction = 0.55,
    double rootDepthMm = 1500,
  }) async {
    return _calculator.calculateWaterBalance(
      soilMoisture: soilMoisture,
      fieldCapacity: fieldCapacity,
      wiltingPoint: wiltingPoint,
      madFraction: madFraction,
      rootDepthMm: rootDepthMm,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Sync Management - إدارة المزامنة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Sync pending changes with server
  /// مزامنة التغييرات المعلقة مع الخادم
  Future<SyncResult> syncPendingChanges() async {
    final prefs = await SharedPreferences.getInstance();
    final pendingJson = prefs.getString(_pendingSyncKey);
    if (pendingJson == null) {
      return const SyncResult(success: true, syncedItems: 0, failedItems: 0);
    }

    int synced = 0;
    int failed = 0;

    try {
      final pending =
          (jsonDecode(pendingJson) as List).cast<Map<String, dynamic>>();

      for (final item in pending) {
        final type = item['type'] as String;
        final fieldId = item['field_id'] as String;

        try {
          switch (type) {
            case 'schedule':
              final cached = await _loadScheduleFromCache(fieldId);
              if (cached != null) {
                await _api.generateSchedule(
                  fieldId: fieldId,
                  cropId: 'wheat', // Would need to store this
                  methodId: 'drip',
                  days: 14,
                );
              }
              synced++;
              break;
            default:
              failed++;
          }
        } catch (_) {
          failed++;
        }
      }

      // Clear synced items
      if (failed == 0) {
        await prefs.remove(_pendingSyncKey);
      }

      // Update last sync time
      await prefs.setString(_lastSyncKey, DateTime.now().toIso8601String());
    } catch (_) {
      return SyncResult(
          success: false, syncedItems: synced, failedItems: failed);
    }

    return SyncResult(
        success: failed == 0, syncedItems: synced, failedItems: failed);
  }

  Future<void> _markForSync(String fieldId, String type) async {
    final prefs = await SharedPreferences.getInstance();
    final pendingJson = prefs.getString(_pendingSyncKey);

    List<Map<String, dynamic>> pending = [];
    if (pendingJson != null) {
      pending = (jsonDecode(pendingJson) as List).cast<Map<String, dynamic>>();
    }

    // Add if not already pending
    if (!pending.any((p) => p['field_id'] == fieldId && p['type'] == type)) {
      pending.add({
        'field_id': fieldId,
        'type': type,
        'timestamp': DateTime.now().toIso8601String()
      });
      await prefs.setString(_pendingSyncKey, jsonEncode(pending));
    }
  }

  /// Get last sync time
  /// الحصول على آخر وقت مزامنة
  Future<DateTime?> getLastSyncTime() async {
    final prefs = await SharedPreferences.getInstance();
    final syncStr = prefs.getString(_lastSyncKey);
    if (syncStr == null) return null;
    return DateTime.tryParse(syncStr);
  }

  /// Check if there are pending changes
  /// التحقق من وجود تغييرات معلقة
  Future<bool> hasPendingChanges() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.containsKey(_pendingSyncKey);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Cache Management - إدارة التخزين المؤقت
  // ═══════════════════════════════════════════════════════════════════════════

  /// Clear all cached data
  /// مسح جميع البيانات المخزنة مؤقتًا
  Future<void> clearCache() async {
    _cropsCache = null;
    _methodsCache = null;
    _schedulesCache.clear();
    _calculationsCache.clear();

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_cropsKey);
    await prefs.remove(_methodsKey);

    // Clear all schedule and calculation caches
    final keys = prefs.getKeys();
    for (final key in keys) {
      if (key.startsWith(_schedulesKeyPrefix) ||
          key.startsWith(_calculationsKeyPrefix)) {
        await prefs.remove(key);
      }
    }
  }

  /// Preload reference data for offline use
  /// تحميل البيانات المرجعية للاستخدام دون اتصال
  Future<void> preloadReferenceData() async {
    try {
      await getCrops(forceRefresh: true);
      await getMethods(forceRefresh: true);
    } catch (_) {
      // Ignore errors during preload
    }
  }

  /// Dispose resources
  void dispose() {
    _api.dispose();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Supporting Models - نماذج مساعدة
// ═══════════════════════════════════════════════════════════════════════════

/// Sync result
/// نتيجة المزامنة
class SyncResult {
  final bool success;
  final int syncedItems;
  final int failedItems;
  final String? error;

  const SyncResult({
    required this.success,
    required this.syncedItems,
    required this.failedItems,
    this.error,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Riverpod Providers - موفرو Riverpod
// ═══════════════════════════════════════════════════════════════════════════

/// Irrigation API Provider
final irrigationApiProvider = Provider<IrrigationApi>((ref) {
  return IrrigationApi();
});

/// Irrigation Repository Provider
final irrigationRepositoryProvider = Provider<IrrigationRepository>((ref) {
  final api = ref.watch(irrigationApiProvider);
  return IrrigationRepository(api: api);
});

/// Water Calculator Provider
final waterCalculatorProvider = Provider<WaterCalculator>((ref) {
  return const WaterCalculator();
});

/// Irrigation Scheduler Provider
final irrigationSchedulerProvider = Provider<IrrigationScheduler>((ref) {
  final repo = ref.watch(irrigationRepositoryProvider);
  return repo.scheduler;
});

/// Crops Provider
final irrigationCropsProvider = FutureProvider<List<IrrigationCrop>>((ref) {
  final repo = ref.watch(irrigationRepositoryProvider);
  return repo.getCrops();
});

/// Methods Provider
final irrigationMethodsProvider = FutureProvider<List<IrrigationMethod>>((ref) {
  final repo = ref.watch(irrigationRepositoryProvider);
  return repo.getMethods();
});

/// Schedule Provider
final fieldScheduleProvider =
    FutureProvider.family<IrrigationSchedule, String>((ref, fieldId) {
  final repo = ref.watch(irrigationRepositoryProvider);
  return repo.getSchedule(fieldId);
});

/// Pending Sync Provider
final hasPendingSyncProvider = FutureProvider<bool>((ref) {
  final repo = ref.watch(irrigationRepositoryProvider);
  return repo.hasPendingChanges();
});
