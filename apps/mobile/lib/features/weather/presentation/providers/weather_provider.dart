import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/remote/weather_api.dart';
import '../../domain/entities/weather_entities.dart';
import '../../../../core/auth/secure_storage_service.dart';

/// Weather API Provider (unauthenticated fallback)
final weatherApiProvider = Provider<WeatherApi>((ref) {
  return WeatherApi();
});

/// Weather API with token — use this for authenticated requests
final weatherApiWithTokenProvider = FutureProvider<WeatherApi>((ref) async {
  final secureStorage = ref.watch(secureStorageProvider);
  final token = await secureStorage.getAccessToken();
  return WeatherApi(authToken: token);
});

/// حالة بيانات الطقس
class WeatherState {
  final bool isLoading;
  final WeatherData? data;
  final String? error;

  const WeatherState({
    this.isLoading = false,
    this.data,
    this.error,
  });

  WeatherState copyWith({
    bool? isLoading,
    WeatherData? data,
    String? error,
  }) {
    return WeatherState(
      isLoading: isLoading ?? this.isLoading,
      data: data ?? this.data,
      error: error,
    );
  }
}

/// Weather State Notifier
class WeatherNotifier extends StateNotifier<WeatherState> {
  final WeatherApi _api;

  WeatherNotifier(this._api) : super(const WeatherState());

  Future<void> loadWeather(String fieldId) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final data = await _api.getFieldWeather(fieldId);
      state = state.copyWith(isLoading: false, data: data);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> loadWeatherByLocation(double lat, double lon) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final data = await _api.getWeatherByCoordinates(lat, lon);
      state = state.copyWith(isLoading: false, data: data);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

/// Weather Provider — uses authenticated API
final weatherProvider =
    StateNotifierProvider<WeatherNotifier, WeatherState>((ref) {
  // Watch the async token provider; fall back to unauthenticated until token loads
  final asyncApi = ref.watch(weatherApiWithTokenProvider);
  final api = asyncApi.maybeWhen(data: (a) => a, orElse: () => WeatherApi());
  return WeatherNotifier(api);
});

/// Selected Field Provider
final selectedFieldIdProvider = StateProvider<String?>((ref) => null);

/// حالة التنبيهات
class AlertsState {
  final bool isLoading;
  final List<WeatherAlert> alerts;
  final String? error;

  const AlertsState({
    this.isLoading = false,
    this.alerts = const [],
    this.error,
  });

  AlertsState copyWith({
    bool? isLoading,
    List<WeatherAlert>? alerts,
    String? error,
  }) {
    return AlertsState(
      isLoading: isLoading ?? this.isLoading,
      alerts: alerts ?? this.alerts,
      error: error,
    );
  }

  int get activeAlerts =>
      alerts.where((a) => a.endTime.isAfter(DateTime.now())).length;

  bool get hasWarnings =>
      alerts.any((a) => a.severity == 'warning' && a.endTime.isAfter(DateTime.now()));
}

/// Alerts State Notifier
class AlertsNotifier extends StateNotifier<AlertsState> {
  final WeatherApi _api;

  AlertsNotifier(this._api) : super(const AlertsState());

  Future<void> loadAlerts(String fieldId) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final alerts = await _api.getWeatherAlerts(fieldId);
      state = state.copyWith(isLoading: false, alerts: alerts);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }
}

/// Alerts Provider — uses authenticated API
final alertsProvider =
    StateNotifierProvider<AlertsNotifier, AlertsState>((ref) {
  final asyncApi = ref.watch(weatherApiWithTokenProvider);
  final api = asyncApi.maybeWhen(data: (a) => a, orElse: () => WeatherApi());
  return AlertsNotifier(api);
});

/// حالة التأثيرات الزراعية
class ImpactsState {
  final bool isLoading;
  final List<AgriculturalImpact> impacts;
  final String? error;

  const ImpactsState({
    this.isLoading = false,
    this.impacts = const [],
    this.error,
  });

  ImpactsState copyWith({
    bool? isLoading,
    List<AgriculturalImpact>? impacts,
    String? error,
  }) {
    return ImpactsState(
      isLoading: isLoading ?? this.isLoading,
      impacts: impacts ?? this.impacts,
      error: error,
    );
  }
}

/// Impacts State Notifier
class ImpactsNotifier extends StateNotifier<ImpactsState> {
  final WeatherApi _api;

  ImpactsNotifier(this._api) : super(const ImpactsState());

  Future<void> loadImpacts(String fieldId) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final impacts = await _api.getAgriculturalImpacts(fieldId);
      state = state.copyWith(isLoading: false, impacts: impacts);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }
}

/// Impacts Provider — uses authenticated API
final impactsProvider =
    StateNotifierProvider<ImpactsNotifier, ImpactsState>((ref) {
  final asyncApi = ref.watch(weatherApiWithTokenProvider);
  final api = asyncApi.maybeWhen(data: (a) => a, orElse: () => WeatherApi());
  return ImpactsNotifier(api);
});

/// Filtered Impacts Provider (حسب الحالة)
final filteredImpactsProvider = Provider<List<AgriculturalImpact>>((ref) {
  final impacts = ref.watch(impactsProvider).impacts;
  final filter = ref.watch(impactFilterProvider);

  if (filter == null) return impacts;
  return impacts.where((i) => i.status == filter).toList();
});

/// Impact Filter Provider
final impactFilterProvider = StateProvider<String?>((ref) => null);
