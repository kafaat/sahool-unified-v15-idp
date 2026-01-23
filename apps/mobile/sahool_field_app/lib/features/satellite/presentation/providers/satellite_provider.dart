/// Satellite Provider - مزود الأقمار الصناعية
/// State management for satellite monitoring features using Riverpod
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import '../../../data/remote/satellite_api.dart';
import '../../../data/repositories/satellite_repository.dart';
import '../../../data/models/ndvi_data.dart';
import '../../../data/models/field_health.dart';
import '../../../data/models/weather_data.dart';
import '../../../data/models/phenology_data.dart';

// =============================================================================
// State Classes
// =============================================================================

/// Satellite Dashboard State
/// حالة لوحة الأقمار الصناعية
class SatelliteDashboardState {
  final FieldHealth? fieldHealth;
  final NdviAnalysis? ndviAnalysis;
  final WeatherSummary? weatherSummary;
  final PhenologyData? phenologyData;
  final bool isLoading;
  final String? error;
  final DateTime? lastUpdate;

  const SatelliteDashboardState({
    this.fieldHealth,
    this.ndviAnalysis,
    this.weatherSummary,
    this.phenologyData,
    this.isLoading = false,
    this.error,
    this.lastUpdate,
  });

  SatelliteDashboardState copyWith({
    FieldHealth? fieldHealth,
    NdviAnalysis? ndviAnalysis,
    WeatherSummary? weatherSummary,
    PhenologyData? phenologyData,
    bool? isLoading,
    String? error,
    bool clearError = false,
    DateTime? lastUpdate,
  }) {
    return SatelliteDashboardState(
      fieldHealth: fieldHealth ?? this.fieldHealth,
      ndviAnalysis: ndviAnalysis ?? this.ndviAnalysis,
      weatherSummary: weatherSummary ?? this.weatherSummary,
      phenologyData: phenologyData ?? this.phenologyData,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      lastUpdate: lastUpdate ?? this.lastUpdate,
    );
  }

  bool get hasData =>
      fieldHealth != null ||
      ndviAnalysis != null ||
      weatherSummary != null ||
      phenologyData != null;
}

/// NDVI Detail State
/// حالة تفاصيل NDVI
class NdviDetailState {
  final NdviAnalysis? analysis;
  final List<NdviDataPoint> timeSeries;
  final Map<String, double> indices;
  final bool isLoading;
  final String? error;

  const NdviDetailState({
    this.analysis,
    this.timeSeries = const [],
    this.indices = const {},
    this.isLoading = false,
    this.error,
  });

  NdviDetailState copyWith({
    NdviAnalysis? analysis,
    List<NdviDataPoint>? timeSeries,
    Map<String, double>? indices,
    bool? isLoading,
    String? error,
    bool clearError = false,
  }) {
    return NdviDetailState(
      analysis: analysis ?? this.analysis,
      timeSeries: timeSeries ?? this.timeSeries,
      indices: indices ?? this.indices,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

// =============================================================================
// Notifiers
// =============================================================================

/// Satellite Dashboard Notifier
/// مزود لوحة الأقمار الصناعية
class SatelliteDashboardNotifier extends StateNotifier<SatelliteDashboardState> {
  final SatelliteRepository _repository;

  SatelliteDashboardNotifier({
    required SatelliteRepository repository,
  })  : _repository = repository,
        super(const SatelliteDashboardState());

  /// Load complete dashboard data
  /// تحميل بيانات لوحة المعلومات الكاملة
  Future<void> loadDashboard(String fieldId, {bool forceRefresh = false}) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final dashboardData = await _repository.getDashboardData(
        fieldId,
        forceRefresh: forceRefresh,
      );

      state = state.copyWith(
        fieldHealth: dashboardData.fieldHealth,
        ndviAnalysis: dashboardData.ndviAnalysis,
        weatherSummary: dashboardData.weatherSummary,
        phenologyData: dashboardData.phenologyData,
        isLoading: false,
        lastUpdate: DateTime.now(),
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تحميل بيانات الأقمار الصناعية: ${e.toString()}',
      );
    }
  }

  /// Refresh dashboard (pull to refresh)
  /// تحديث لوحة المعلومات
  Future<void> refreshDashboard(String fieldId) async {
    await loadDashboard(fieldId, forceRefresh: true);
  }

  /// Load field health only
  /// تحميل صحة الحقل فقط
  Future<void> loadFieldHealth(String fieldId, {bool forceRefresh = false}) async {
    try {
      final health = await _repository.getFieldHealth(fieldId, forceRefresh: forceRefresh);
      state = state.copyWith(fieldHealth: health);
    } catch (e) {
      state = state.copyWith(error: 'فشل في تحميل صحة الحقل');
    }
  }

  /// Clear error
  /// مسح الخطأ
  void clearError() {
    state = state.copyWith(clearError: true);
  }
}

/// NDVI Detail Notifier
/// مزود تفاصيل NDVI
class NdviDetailNotifier extends StateNotifier<NdviDetailState> {
  final SatelliteRepository _repository;

  NdviDetailNotifier({
    required SatelliteRepository repository,
  })  : _repository = repository,
        super(const NdviDetailState());

  /// Load NDVI details
  /// تحميل تفاصيل NDVI
  Future<void> loadNdviDetails(String fieldId, {int days = 30, bool forceRefresh = false}) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final results = await Future.wait([
        _repository.getNdviAnalysis(fieldId, forceRefresh: forceRefresh),
        _repository.getNdviTimeSeries(fieldId, days: days, forceRefresh: forceRefresh),
        _repository.getVegetationIndices(fieldId, forceRefresh: forceRefresh),
      ]);

      state = state.copyWith(
        analysis: results[0] as NdviAnalysis,
        timeSeries: results[1] as List<NdviDataPoint>,
        indices: results[2] as Map<String, double>,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تحميل تفاصيل NDVI: ${e.toString()}',
      );
    }
  }

  /// Refresh NDVI details
  /// تحديث تفاصيل NDVI
  Future<void> refreshNdviDetails(String fieldId, {int days = 30}) async {
    await loadNdviDetails(fieldId, days: days, forceRefresh: true);
  }

  /// Clear error
  void clearError() {
    state = state.copyWith(clearError: true);
  }
}

/// Weather Notifier
/// مزود الطقس
class SatelliteWeatherNotifier extends StateNotifier<AsyncValue<WeatherSummary>> {
  final SatelliteRepository _repository;

  SatelliteWeatherNotifier({
    required SatelliteRepository repository,
  })  : _repository = repository,
        super(const AsyncValue.loading());

  /// Load weather forecast
  /// تحميل توقعات الطقس
  Future<void> loadWeather(String fieldId, {bool forceRefresh = false}) async {
    state = const AsyncValue.loading();

    try {
      final weather = await _repository.getWeatherForecast(fieldId, forceRefresh: forceRefresh);
      state = AsyncValue.data(weather);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  /// Refresh weather
  /// تحديث الطقس
  Future<void> refreshWeather(String fieldId) async {
    await loadWeather(fieldId, forceRefresh: true);
  }
}

/// Phenology Notifier
/// مزود مراحل النمو
class PhenologyNotifier extends StateNotifier<AsyncValue<PhenologyData>> {
  final SatelliteRepository _repository;

  PhenologyNotifier({
    required SatelliteRepository repository,
  })  : _repository = repository,
        super(const AsyncValue.loading());

  /// Load phenology data
  /// تحميل بيانات مراحل النمو
  Future<void> loadPhenology(String fieldId, {bool forceRefresh = false}) async {
    state = const AsyncValue.loading();

    try {
      final phenology = await _repository.getPhenologyData(fieldId, forceRefresh: forceRefresh);
      state = AsyncValue.data(phenology);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  /// Refresh phenology
  /// تحديث مراحل النمو
  Future<void> refreshPhenology(String fieldId) async {
    await loadPhenology(fieldId, forceRefresh: true);
  }
}

// =============================================================================
// Riverpod Providers
// =============================================================================

/// Shared Preferences Provider
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('SharedPreferences must be overridden in main.dart');
});

/// Current Field ID Provider
final currentFieldIdProvider = StateProvider<String?>((ref) => null);

/// Auth Token Provider (should be provided from auth feature)
final satelliteAuthTokenProvider = StateProvider<String?>((ref) => null);

/// Satellite API Provider
final satelliteApiProvider = Provider<SatelliteApi>((ref) {
  final authToken = ref.watch(satelliteAuthTokenProvider);
  return SatelliteApi(
    client: http.Client(),
    authToken: authToken,
  );
});

/// Satellite Repository Provider
final satelliteRepositoryProvider = Provider<SatelliteRepository>((ref) {
  final api = ref.watch(satelliteApiProvider);
  final prefs = ref.watch(sharedPreferencesProvider);

  return SatelliteRepository(
    api: api,
    prefs: prefs,
  );
});

/// Satellite Dashboard Provider
final satelliteDashboardProvider =
    StateNotifierProvider<SatelliteDashboardNotifier, SatelliteDashboardState>((ref) {
  final repository = ref.watch(satelliteRepositoryProvider);

  return SatelliteDashboardNotifier(repository: repository);
});

/// NDVI Detail Provider
final ndviDetailProvider = StateNotifierProvider<NdviDetailNotifier, NdviDetailState>((ref) {
  final repository = ref.watch(satelliteRepositoryProvider);

  return NdviDetailNotifier(repository: repository);
});

/// Satellite Weather Provider
final satelliteWeatherProvider =
    StateNotifierProvider<SatelliteWeatherNotifier, AsyncValue<WeatherSummary>>((ref) {
  final repository = ref.watch(satelliteRepositoryProvider);

  return SatelliteWeatherNotifier(repository: repository);
});

/// Phenology Provider
final phenologyProvider =
    StateNotifierProvider<PhenologyNotifier, AsyncValue<PhenologyData>>((ref) {
  final repository = ref.watch(satelliteRepositoryProvider);

  return PhenologyNotifier(repository: repository);
});

// =============================================================================
// Computed Providers
// =============================================================================

/// Health Score Provider
final healthScoreProvider = Provider<double?>((ref) {
  final state = ref.watch(satelliteDashboardProvider);
  return state.fieldHealth?.healthScore;
});

/// Current NDVI Provider
final currentNdviProvider = Provider<double?>((ref) {
  final state = ref.watch(satelliteDashboardProvider);
  return state.ndviAnalysis?.currentNdvi;
});

/// Current Growth Stage Provider
final currentGrowthStageProvider = Provider<GrowthStage?>((ref) {
  final state = ref.watch(satelliteDashboardProvider);
  return state.phenologyData?.currentStage;
});

/// Days to Harvest Provider
final daysToHarvestProvider = Provider<int?>((ref) {
  final state = ref.watch(satelliteDashboardProvider);
  return state.phenologyData?.daysToHarvest;
});

/// Has Active Alerts Provider
final hasActiveAlertsProvider = Provider<bool>((ref) {
  final state = ref.watch(satelliteDashboardProvider);
  return (state.fieldHealth?.alerts.isNotEmpty ?? false);
});
