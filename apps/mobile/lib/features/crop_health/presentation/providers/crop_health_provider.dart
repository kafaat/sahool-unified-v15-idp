import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/di/providers.dart' show apiClientProvider;
import '../../data/remote/crop_health_api.dart';
import '../../domain/entities/crop_health_entities.dart';

/// Crop Health API Provider
final cropHealthApiProvider = Provider.autoDispose<CropHealthApi>((ref) {
  final client = ref.watch(apiClientProvider);
  return CropHealthApi(client);
});

/// Selected Field Provider
final selectedFieldIdProvider = StateProvider.autoDispose<String?>((ref) => null);

/// Selected Zone Provider
final selectedZoneIdProvider = StateProvider.autoDispose<String?>((ref) => null);

/// Selected Date Provider (end of the observation window)
final selectedDateProvider = StateProvider.autoDispose<DateTime>((ref) => DateTime.now());

/// Selected Period in days (1 = today only, 7/30/90 for presets).
/// When the user picks a preset the dashboard loads the timeline
/// for [selectedDate - selectedPeriodDays … selectedDate].
final selectedPeriodDaysProvider = StateProvider.autoDispose<int>((ref) => 1);

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

  /// تحديد الإجراء كمنفذ
  Future<void> markActionCompleted(
    String fieldId,
    String zoneId,
    String actionType,
  ) async {
    try {
      // Call API to mark action as completed
      await _api.markActionCompleted(fieldId, zoneId, actionType);

      // Update local state by removing the completed action
      if (state.diagnosis != null) {
        final updatedActions = state.diagnosis!.actions
            .where((a) => !(a.zoneId == zoneId && a.type == actionType))
            .toList();

        final updatedDiagnosis = FieldDiagnosis(
          fieldId: state.diagnosis!.fieldId,
          date: state.diagnosis!.date,
          summary: state.diagnosis!.summary,
          actions: updatedActions,
          mapLayers: state.diagnosis!.mapLayers,
        );

        state = state.copyWith(diagnosis: updatedDiagnosis);
      }
    } catch (e) {
      state = state.copyWith(
        error: 'فشل تحديث الإجراء: ${e.toString()}',
      );
      rethrow;
    }
  }

  void clear() {
    state = const DiagnosisState();
  }
}

/// Diagnosis Provider
final diagnosisProvider =
    StateNotifierProvider.autoDispose<DiagnosisNotifier, DiagnosisState>((ref) {
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
    StateNotifierProvider.autoDispose<ZonesNotifier, ZonesState>((ref) {
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

  /// Monotonically-increasing counter used for request deduplication.
  /// When the user taps presets rapidly, each call increments this value.
  /// A response is only applied to state when its captured ID still matches
  /// the current value — stale responses are silently dropped.
  int _requestId = 0;

  /// Debounce timer — cancelled and restarted on every `loadTimeline` call.
  /// The 200 ms window prevents unnecessary API calls and backend pressure
  /// when the user taps presets in quick succession.  Only the final tap
  /// within the window actually fires the network request.
  Timer? _debounceTimer;

  /// Duration after the last `loadTimeline` call before the API request fires.
  static const _debounceDuration = Duration(milliseconds: 200);

  Future<void> loadTimeline(
    String fieldId,
    String zoneId, {
    DateTime? from,
    DateTime? to,
  }) async {
    _debounceTimer?.cancel();

    // Increment now so any already-in-flight request sees a stale ID.
    final currentRequest = ++_requestId;

    // Show the loading indicator immediately so the UI feels responsive.
    state = state.copyWith(isLoading: true, error: null);

    final now = DateTime.now();
    final fromDate = from ?? now.subtract(const Duration(days: 30));
    final toDate = to ?? now;

    // Defer the network call by 200 ms. If the user taps another preset
    // within this window the timer is cancelled and a new one is started.
    _debounceTimer = Timer(_debounceDuration, () async {
      try {
        final timeline = await _api.getTimeline(
          fieldId,
          zoneId,
          from: fromDate,
          to: toDate,
        );

        // Discard if a newer request has already been dispatched.
        if (currentRequest != _requestId) return;

        state = state.copyWith(isLoading: false, timeline: timeline);
      } catch (e) {
        if (currentRequest != _requestId) return;

        state = state.copyWith(
          isLoading: false,
          error: 'فشل تحميل السلسلة الزمنية: ${e.toString()}',
        );
      }
    });
  }

  @override
  void dispose() {
    _debounceTimer?.cancel();
    super.dispose();
  }
}

/// Timeline Provider
final timelineProvider =
    StateNotifierProvider.autoDispose<TimelineNotifier, TimelineState>((ref) {
  final api = ref.watch(cropHealthApiProvider);
  return TimelineNotifier(api);
});

/// VRT Export Provider
final vrtExportProvider = FutureProvider.autoDispose.family<Map<String, dynamic>, ({String fieldId, DateTime date, String? actionType})>(
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
final filteredActionsProvider = Provider.autoDispose<List<DiagnosisAction>>((ref) {
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
final actionFilterProvider = StateProvider.autoDispose<String?>((ref) => null);

/// فلتر الأولوية
final priorityFilterProvider = StateProvider.autoDispose<String?>((ref) => null);

/// الإجراءات المفلترة حسب الأولوية
final priorityFilteredActionsProvider = Provider.autoDispose<List<DiagnosisAction>>((ref) {
  final actions = ref.watch(filteredActionsProvider);
  final priority = ref.watch(priorityFilterProvider);

  if (priority == null) return actions;

  return actions.where((a) => a.priority == priority).toList();
});
