/// Spray Advisor Providers - مزودات بيانات مستشار الرش
/// Riverpod providers للتواصل مع Spray Service
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/spray_models.dart';
import '../services/spray_service.dart';

// ═════════════════════════════════════════════════════════════════════════════
// Data Providers
// ═════════════════════════════════════════════════════════════════════════════

/// مزود قائمة توصيات الرش
final sprayRecommendationsProvider = FutureProvider.autoDispose
    .family<List<SprayRecommendation>, SprayRecommendationFilter?>((ref, filter) async {
  final service = ref.watch(sprayServiceProvider);
  final result = await service.getSprayRecommendations(
    fieldId: filter?.fieldId,
    sprayType: filter?.sprayType,
    status: filter?.status,
    startDate: filter?.startDate,
    endDate: filter?.endDate,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب توصيات الرش');
});

/// مزود تفاصيل توصية محددة
final recommendationDetailsProvider = FutureProvider.autoDispose
    .family<SprayRecommendation, String>((ref, recommendationId) async {
  final service = ref.watch(sprayServiceProvider);
  final result = await service.getRecommendationById(recommendationId);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'التوصية غير موجودة');
});

/// مزود نوافذ الرش المثلى
final sprayWindowsProvider =
    FutureProvider.autoDispose.family<List<SprayWindow>, SprayWindowParams>((ref, params) async {
  final service = ref.watch(sprayServiceProvider);
  final result = await service.getOptimalSprayWindows(
    fieldId: params.fieldId,
    days: params.days,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب نوافذ الرش');
});

/// مزود توقعات الطقس
final weatherForecastProvider = FutureProvider.autoDispose
    .family<List<WeatherCondition>, WeatherForecastParams>((ref, params) async {
  final service = ref.watch(sprayServiceProvider);
  final result = await service.getWeatherForecast(
    fieldId: params.fieldId,
    days: params.days,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب توقعات الطقس');
});

/// مزود الطقس الحالي
final currentWeatherProvider =
    FutureProvider.autoDispose.family<WeatherCondition, String>((ref, fieldId) async {
  final service = ref.watch(sprayServiceProvider);
  final result = await service.getCurrentWeather(fieldId: fieldId);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب الطقس الحالي');
});

/// مزود منتجات الرش
final sprayProductsProvider =
    FutureProvider.autoDispose.family<List<SprayProduct>, SprayProductFilter?>((ref, filter) async {
  final service = ref.watch(sprayServiceProvider);
  final result = await service.getSprayProducts(
    sprayType: filter?.sprayType,
    yemenProductsOnly: filter?.yemenProductsOnly ?? false,
    search: filter?.search,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب منتجات الرش');
});

/// مزود تفاصيل منتج محدد
final productDetailsProvider =
    FutureProvider.autoDispose.family<SprayProduct, String>((ref, productId) async {
  final service = ref.watch(sprayServiceProvider);
  final result = await service.getProductById(productId);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'المنتج غير موجود');
});

/// مزود سجلات تطبيق الرش
final sprayLogsProvider =
    FutureProvider.autoDispose.family<List<SprayApplicationLog>, SprayLogFilter?>((ref, filter) async {
  final service = ref.watch(sprayServiceProvider);
  final result = await service.getSprayLogs(
    fieldId: filter?.fieldId,
    sprayType: filter?.sprayType,
    startDate: filter?.startDate,
    endDate: filter?.endDate,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب سجلات الرش');
});

/// مزود تفاصيل سجل محدد
final logDetailsProvider =
    FutureProvider.autoDispose.family<SprayApplicationLog, String>((ref, logId) async {
  final service = ref.watch(sprayServiceProvider);
  final result = await service.getLogById(logId);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'السجل غير موجود');
});

// ═════════════════════════════════════════════════════════════════════════════
// State Providers
// ═════════════════════════════════════════════════════════════════════════════

/// فلتر التوصيات المحدد
final selectedRecommendationFilterProvider = StateProvider<SprayRecommendationFilter?>((ref) => null);

/// الحقل المحدد
final selectedFieldIdProvider = StateProvider<String?>((ref) => null);

/// التوصية الحالية (للتعديل)
final currentRecommendationProvider = StateProvider<SprayRecommendation?>((ref) => null);

/// المنتج المحدد
final selectedProductProvider = StateProvider<SprayProduct?>((ref) => null);

/// نوع الرش المحدد (للتصفية)
final selectedSprayTypeProvider = StateProvider<SprayType?>((ref) => null);

// ═════════════════════════════════════════════════════════════════════════════
// Filter Classes
// ═════════════════════════════════════════════════════════════════════════════

/// فلتر توصيات الرش
class SprayRecommendationFilter {
  final String? fieldId;
  final SprayType? sprayType;
  final RecommendationStatus? status;
  final DateTime? startDate;
  final DateTime? endDate;

  const SprayRecommendationFilter({
    this.fieldId,
    this.sprayType,
    this.status,
    this.startDate,
    this.endDate,
  });

  SprayRecommendationFilter copyWith({
    String? fieldId,
    SprayType? sprayType,
    RecommendationStatus? status,
    DateTime? startDate,
    DateTime? endDate,
    bool clearFieldId = false,
    bool clearSprayType = false,
    bool clearStatus = false,
    bool clearStartDate = false,
    bool clearEndDate = false,
  }) {
    return SprayRecommendationFilter(
      fieldId: clearFieldId ? null : (fieldId ?? this.fieldId),
      sprayType: clearSprayType ? null : (sprayType ?? this.sprayType),
      status: clearStatus ? null : (status ?? this.status),
      startDate: clearStartDate ? null : (startDate ?? this.startDate),
      endDate: clearEndDate ? null : (endDate ?? this.endDate),
    );
  }

  bool get hasFilters =>
      fieldId != null || sprayType != null || status != null || startDate != null || endDate != null;
}

/// معاملات نوافذ الرش
class SprayWindowParams {
  final String fieldId;
  final int days;

  const SprayWindowParams({
    required this.fieldId,
    this.days = 7,
  });

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is SprayWindowParams && other.fieldId == fieldId && other.days == days;
  }

  @override
  int get hashCode => Object.hash(fieldId, days);
}

/// معاملات توقعات الطقس
class WeatherForecastParams {
  final String fieldId;
  final int days;

  const WeatherForecastParams({
    required this.fieldId,
    this.days = 7,
  });

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is WeatherForecastParams && other.fieldId == fieldId && other.days == days;
  }

  @override
  int get hashCode => Object.hash(fieldId, days);
}

/// فلتر منتجات الرش
class SprayProductFilter {
  final SprayType? sprayType;
  final bool yemenProductsOnly;
  final String? search;

  const SprayProductFilter({
    this.sprayType,
    this.yemenProductsOnly = false,
    this.search,
  });

  SprayProductFilter copyWith({
    SprayType? sprayType,
    bool? yemenProductsOnly,
    String? search,
    bool clearSprayType = false,
    bool clearSearch = false,
  }) {
    return SprayProductFilter(
      sprayType: clearSprayType ? null : (sprayType ?? this.sprayType),
      yemenProductsOnly: yemenProductsOnly ?? this.yemenProductsOnly,
      search: clearSearch ? null : (search ?? this.search),
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is SprayProductFilter &&
        other.sprayType == sprayType &&
        other.yemenProductsOnly == yemenProductsOnly &&
        other.search == search;
  }

  @override
  int get hashCode => Object.hash(sprayType, yemenProductsOnly, search);
}

/// فلتر سجلات الرش
class SprayLogFilter {
  final String? fieldId;
  final SprayType? sprayType;
  final DateTime? startDate;
  final DateTime? endDate;

  const SprayLogFilter({
    this.fieldId,
    this.sprayType,
    this.startDate,
    this.endDate,
  });

  SprayLogFilter copyWith({
    String? fieldId,
    SprayType? sprayType,
    DateTime? startDate,
    DateTime? endDate,
    bool clearFieldId = false,
    bool clearSprayType = false,
    bool clearStartDate = false,
    bool clearEndDate = false,
  }) {
    return SprayLogFilter(
      fieldId: clearFieldId ? null : (fieldId ?? this.fieldId),
      sprayType: clearSprayType ? null : (sprayType ?? this.sprayType),
      startDate: clearStartDate ? null : (startDate ?? this.startDate),
      endDate: clearEndDate ? null : (endDate ?? this.endDate),
    );
  }

  bool get hasFilters => fieldId != null || sprayType != null || startDate != null || endDate != null;
}

// ═════════════════════════════════════════════════════════════════════════════
// Controller للعمليات (CRUD)
// ═════════════════════════════════════════════════════════════════════════════

class SprayController extends StateNotifier<AsyncValue<void>> {
  final SprayService _service;
  final Ref _ref;

  SprayController(this._service, this._ref) : super(const AsyncValue.data(null));

  /// إنشاء توصية رش جديدة
  Future<SprayRecommendation?> createRecommendation({
    required String fieldId,
    required String title,
    String? titleAr,
    required String description,
    String? descriptionAr,
    required SprayType sprayType,
    String? productId,
    required double recommendedRate,
    required String unit,
    String? unitAr,
    DateTime? targetDate,
    int priority = 3,
    String? notes,
    String? notesAr,
  }) async {
    state = const AsyncValue.loading();

    final result = await _service.createRecommendation(
      fieldId: fieldId,
      title: title,
      titleAr: titleAr,
      description: description,
      descriptionAr: descriptionAr,
      sprayType: sprayType,
      productId: productId,
      recommendedRate: recommendedRate,
      unit: unit,
      unitAr: unitAr,
      targetDate: targetDate,
      priority: priority,
      notes: notes,
      notesAr: notesAr,
    );

    if (result.isSuccess && result.data != null) {
      state = const AsyncValue.data(null);
      _ref.invalidate(sprayRecommendationsProvider);
      return result.data;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إنشاء التوصية',
      StackTrace.current,
    );
    return null;
  }

  /// تحديث حالة توصية
  Future<bool> updateRecommendationStatus(
    String recommendationId,
    RecommendationStatus status, {
    String? notes,
    String? notesAr,
  }) async {
    state = const AsyncValue.loading();

    final result = await _service.updateRecommendationStatus(
      recommendationId,
      status,
      notes: notes,
      notesAr: notesAr,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(sprayRecommendationsProvider);
      _ref.invalidate(recommendationDetailsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث حالة التوصية',
      StackTrace.current,
    );
    return false;
  }

  /// حذف توصية
  Future<bool> deleteRecommendation(String recommendationId) async {
    state = const AsyncValue.loading();

    final result = await _service.deleteRecommendation(recommendationId);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(sprayRecommendationsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في حذف التوصية',
      StackTrace.current,
    );
    return false;
  }

  /// تسجيل تطبيق رش
  Future<SprayApplicationLog?> logSprayApplication({
    required String fieldId,
    String? recommendationId,
    required SprayType sprayType,
    required String productId,
    required double appliedRate,
    required String unit,
    String? unitAr,
    required double area,
    required DateTime applicationDate,
    String? applicatorName,
    String? equipmentUsed,
    String? equipmentUsedAr,
    List<String> photoUrls = const [],
    String? notes,
    String? notesAr,
  }) async {
    state = const AsyncValue.loading();

    final result = await _service.logSprayApplication(
      fieldId: fieldId,
      recommendationId: recommendationId,
      sprayType: sprayType,
      productId: productId,
      appliedRate: appliedRate,
      unit: unit,
      unitAr: unitAr,
      area: area,
      applicationDate: applicationDate,
      applicatorName: applicatorName,
      equipmentUsed: equipmentUsed,
      equipmentUsedAr: equipmentUsedAr,
      photoUrls: photoUrls,
      notes: notes,
      notesAr: notesAr,
    );

    if (result.isSuccess && result.data != null) {
      state = const AsyncValue.data(null);
      _ref.invalidate(sprayLogsProvider);
      // If linked to recommendation, mark it as completed
      if (recommendationId != null) {
        await updateRecommendationStatus(
          recommendationId,
          RecommendationStatus.completed,
        );
      }
      return result.data;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تسجيل تطبيق الرش',
      StackTrace.current,
    );
    return null;
  }

  /// حذف سجل
  Future<bool> deleteLog(String logId) async {
    state = const AsyncValue.loading();

    final result = await _service.deleteLog(logId);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(sprayLogsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في حذف السجل',
      StackTrace.current,
    );
    return false;
  }

  /// رفع صورة
  Future<String?> uploadPhoto(String filePath) async {
    state = const AsyncValue.loading();

    final result = await _service.uploadPhoto(filePath);

    if (result.isSuccess && result.data != null) {
      state = const AsyncValue.data(null);
      return result.data;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في رفع الصورة',
      StackTrace.current,
    );
    return null;
  }
}

/// مزود Controller
final sprayControllerProvider = StateNotifierProvider<SprayController, AsyncValue<void>>((ref) {
  final service = ref.watch(sprayServiceProvider);
  return SprayController(service, ref);
});
