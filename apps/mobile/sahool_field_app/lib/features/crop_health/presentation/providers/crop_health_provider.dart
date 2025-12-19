import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/http/api_client.dart';
import '../../data/remote/crop_health_api.dart';
import '../../domain/entities/crop_health_entities.dart';

/// API Client Provider
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

/// Crop Health API Provider
final cropHealthApiProvider = Provider<CropHealthApi>((ref) {
  final client = ref.watch(apiClientProvider);
  return CropHealthApi(client);
});

/// Selected Field Provider
final selectedFieldIdProvider = StateProvider<String?>((ref) => null);

/// Selected Zone Provider
final selectedZoneIdProvider = StateProvider<String?>((ref) => null);

/// Selected Date Provider
final selectedDateProvider = StateProvider<DateTime>((ref) => DateTime.now());

/// حالة التشخيص
class DiagnosisState {
  final bool isLoading;
  final FieldDiagnosis? diagnosis;
  final String? error;

  const DiagnosisState({
    this.isLoading = false,
    this.diagnosis,
    this.error,
  });

  DiagnosisState copyWith({
    bool? isLoading,
    FieldDiagnosis? diagnosis,
    String? error,
  }) {
    return DiagnosisState(
      isLoading: isLoading ?? this.isLoading,
      diagnosis: diagnosis ?? this.diagnosis,
      error: error,
    );
  }
}

/// Diagnosis Notifier
class DiagnosisNotifier extends StateNotifier<DiagnosisState> {
  final CropHealthApi _api;

  DiagnosisNotifier(this._api) : super(const DiagnosisState());

  Future<void> loadDiagnosis(String fieldId, DateTime date) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final diagnosis = await _api.getDiagnosis(fieldId, date: date);
      state = state.copyWith(isLoading: false, diagnosis: diagnosis);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل تحميل التشخيص: ${e.toString()}',
      );
    }
  }

  void clear() {
    state = const DiagnosisState();
  }
}

/// Diagnosis Provider
final diagnosisProvider =
    StateNotifierProvider<DiagnosisNotifier, DiagnosisState>((ref) {
  final api = ref.watch(cropHealthApiProvider);
  return DiagnosisNotifier(api);
});

/// حالة المناطق
class ZonesState {
  final bool isLoading;
  final List<Zone> zones;
  final String? error;

  const ZonesState({
    this.isLoading = false,
    this.zones = const [],
    this.error,
  });

  ZonesState copyWith({
    bool? isLoading,
    List<Zone>? zones,
    String? error,
  }) {
    return ZonesState(
      isLoading: isLoading ?? this.isLoading,
      zones: zones ?? this.zones,
      error: error,
    );
  }
}

/// Zones Notifier
class ZonesNotifier extends StateNotifier<ZonesState> {
  final CropHealthApi _api;

  ZonesNotifier(this._api) : super(const ZonesState());

  Future<void> loadZones(String fieldId) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final zones = await _api.getZones(fieldId);
      state = state.copyWith(isLoading: false, zones: zones);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل تحميل المناطق: ${e.toString()}',
      );
    }
  }

  Future<void> createZone(
    String fieldId, {
    required String name,
    String? nameAr,
    double? areaHectares,
  }) async {
    try {
      await _api.createZone(
        fieldId,
        name: name,
        nameAr: nameAr,
        areaHectares: areaHectares,
      );
      await loadZones(fieldId);
    } catch (e) {
      state = state.copyWith(error: 'فشل إنشاء المنطقة: ${e.toString()}');
    }
  }
}

/// Zones Provider
final zonesProvider =
    StateNotifierProvider<ZonesNotifier, ZonesState>((ref) {
  final api = ref.watch(cropHealthApiProvider);
  return ZonesNotifier(api);
});

/// حالة السلسلة الزمنية
class TimelineState {
  final bool isLoading;
  final ZoneTimeline? timeline;
  final String? error;

  const TimelineState({
    this.isLoading = false,
    this.timeline,
    this.error,
  });

  TimelineState copyWith({
    bool? isLoading,
    ZoneTimeline? timeline,
    String? error,
  }) {
    return TimelineState(
      isLoading: isLoading ?? this.isLoading,
      timeline: timeline ?? this.timeline,
      error: error,
    );
  }
}

/// Timeline Notifier
class TimelineNotifier extends StateNotifier<TimelineState> {
  final CropHealthApi _api;

  TimelineNotifier(this._api) : super(const TimelineState());

  Future<void> loadTimeline(
    String fieldId,
    String zoneId, {
    DateTime? from,
    DateTime? to,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    final now = DateTime.now();
    final fromDate = from ?? now.subtract(const Duration(days: 30));
    final toDate = to ?? now;

    try {
      final timeline = await _api.getTimeline(
        fieldId,
        zoneId,
        from: fromDate,
        to: toDate,
      );
      state = state.copyWith(isLoading: false, timeline: timeline);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل تحميل السلسلة الزمنية: ${e.toString()}',
      );
    }
  }
}

/// Timeline Provider
final timelineProvider =
    StateNotifierProvider<TimelineNotifier, TimelineState>((ref) {
  final api = ref.watch(cropHealthApiProvider);
  return TimelineNotifier(api);
});

/// VRT Export Provider
final vrtExportProvider = FutureProvider.family<Map<String, dynamic>, ({String fieldId, DateTime date, String? actionType})>(
  (ref, params) async {
    final api = ref.watch(cropHealthApiProvider);
    return api.exportVrt(
      params.fieldId,
      date: params.date,
      actionType: params.actionType,
    );
  },
);

/// فلترة الإجراءات حسب النوع
final filteredActionsProvider = Provider<List<DiagnosisAction>>((ref) {
  final diagnosisState = ref.watch(diagnosisProvider);
  final filterType = ref.watch(actionFilterProvider);

  if (diagnosisState.diagnosis == null) return [];

  final actions = diagnosisState.diagnosis!.actions;

  if (filterType == null || filterType == 'all') {
    return actions;
  }

  return actions.where((a) => a.type == filterType).toList();
});

/// فلتر نوع الإجراء
final actionFilterProvider = StateProvider<String?>((ref) => null);

/// فلتر الأولوية
final priorityFilterProvider = StateProvider<String?>((ref) => null);

/// الإجراءات المفلترة حسب الأولوية
final priorityFilteredActionsProvider = Provider<List<DiagnosisAction>>((ref) {
  final actions = ref.watch(filteredActionsProvider);
  final priority = ref.watch(priorityFilterProvider);

  if (priority == null) return actions;

  return actions.where((a) => a.priority == priority).toList();
});
