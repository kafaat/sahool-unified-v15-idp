import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../data/remote/weather_api.dart';
import '../../data/repo/weather_repo.dart';
import '../../domain/entities/weather_entities.dart';

/// Weather API Provider
final weatherApiProvider = Provider<WeatherApi>((ref) {
  return WeatherApi();
});

/// Weather Repository Provider with offline caching
/// مزود مستودع الطقس مع دعم التخزين المؤقت
final weatherRepositoryProvider = Provider<WeatherRepository>((ref) {
  final api = ref.watch(weatherApiProvider);
  return WeatherRepository(api: api);
});

/// Initialize weather repository with SharedPreferences
/// تهيئة مستودع الطقس مع التخزين المحلي
final weatherRepositoryWithStorageProvider =
    FutureProvider<WeatherRepository>((ref) async {
  final prefs = await SharedPreferences.getInstance();
  final api = ref.watch(weatherApiProvider);
  return WeatherRepository(api: api, prefs: prefs);
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

/// Weather State Notifier - Updated to use repository with offline caching
/// حالة الطقس المحدثة مع دعم التخزين المؤقت والعمل بدون اتصال
class WeatherNotifier extends StateNotifier<WeatherState> {
  final WeatherRepository _repo;
  bool _isFromCache = false;

  WeatherNotifier(this._repo) : super(const WeatherState());

  /// Check if data is from cache
  bool get isFromCache => _isFromCache;

  /// Load weather for a field with offline support
  /// تحميل بيانات الطقس للحقل مع دعم العمل بدون اتصال
  Future<void> loadWeather(String fieldId) async {
    state = state.copyWith(isLoading: true, error: null);
    _isFromCache = false;

    try {
      final data = await _repo.getWeatherForField(fieldId);
      state = state.copyWith(isLoading: false, data: data);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: _getArabicErrorMessage(e),
      );
    }
  }

  /// Load weather by coordinates with multi-provider fallback
  /// تحميل الطقس بالإحداثيات مع دعم مزودين متعددين
  Future<void> loadWeatherByLocation(double lat, double lon) async {
    state = state.copyWith(isLoading: true, error: null);
    _isFromCache = false;

    try {
      final data = await _repo.getWeatherByCoordinates(lat, lon);
      state = state.copyWith(isLoading: false, data: data);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: _getArabicErrorMessage(e),
      );
    }
  }

  /// Load weather by location name
  /// تحميل الطقس باسم الموقع
  Future<void> loadWeatherByLocationName(String location) async {
    state = state.copyWith(isLoading: true, error: null);
    _isFromCache = false;

    try {
      final data = await _repo.getWeatherByLocation(location);
      state = state.copyWith(isLoading: false, data: data);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: _getArabicErrorMessage(e),
      );
    }
  }

  /// Refresh weather data (clears cache first)
  /// تحديث بيانات الطقس
  Future<void> refresh(String fieldId) async {
    _repo.clearCache();
    await loadWeather(fieldId);
  }

  void clearError() {
    state = state.copyWith(error: null);
  }

  String _getArabicErrorMessage(dynamic error) {
    final message = error.toString();
    if (message.contains('فشل')) {
      return message.replaceAll('Exception:', '').trim();
    }
    if (message.contains('SocketException') || message.contains('Connection')) {
      return 'لا يوجد اتصال بالإنترنت - تم عرض البيانات المخزنة';
    }
    if (message.contains('timeout')) {
      return 'انتهت مهلة الاتصال - حاول مرة أخرى';
    }
    return 'فشل في تحميل بيانات الطقس';
  }
}

/// Weather Provider - autoDispose for proper cleanup when leaving weather screen
/// Uses repository for offline-first caching
final weatherProvider =
    StateNotifierProvider.autoDispose<WeatherNotifier, WeatherState>((ref) {
  final repo = ref.watch(weatherRepositoryProvider);
  return WeatherNotifier(repo);
});

/// Selected Field Provider for Weather feature
/// Note: This is scoped to weather feature. Use core/providers/selected_field_provider.dart
/// for app-wide field selection.
final weatherSelectedFieldIdProvider =
    StateProvider.autoDispose<String?>((ref) => null);

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

  bool get hasWarnings => alerts
      .any((a) => a.severity == 'warning' && a.endTime.isAfter(DateTime.now()));
}

/// Alerts State Notifier - Updated to use repository with offline caching
/// مزود التنبيهات مع دعم التخزين المؤقت
class AlertsNotifier extends StateNotifier<AlertsState> {
  final WeatherRepository _repo;

  AlertsNotifier(this._repo) : super(const AlertsState());

  /// Load alerts for a field with offline caching
  /// تحميل التنبيهات للحقل مع التخزين المؤقت
  Future<void> loadAlerts(String fieldId) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final alerts = await _repo.getAlertsForField(fieldId);
      state = state.copyWith(isLoading: false, alerts: alerts);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تحميل التنبيهات',
        alerts: [], // Return empty list on error
      );
    }
  }

  /// Load alerts for a location name
  /// تحميل التنبيهات لموقع معين
  Future<void> loadAlertsByLocation(String location) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final alerts = await _repo.getAlerts(location);
      state = state.copyWith(isLoading: false, alerts: alerts);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تحميل التنبيهات',
        alerts: [],
      );
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

/// Alerts Provider - autoDispose for proper cleanup
/// Uses repository for offline-first caching
final alertsProvider =
    StateNotifierProvider.autoDispose<AlertsNotifier, AlertsState>((ref) {
  final repo = ref.watch(weatherRepositoryProvider);
  return AlertsNotifier(repo);
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

/// Impacts State Notifier - Updated to use repository with offline caching
/// مزود التأثيرات الزراعية مع دعم التخزين المؤقت
class ImpactsNotifier extends StateNotifier<ImpactsState> {
  final WeatherRepository _repo;

  ImpactsNotifier(this._repo) : super(const ImpactsState());

  /// Load agricultural impacts for a field with offline caching
  /// تحميل التأثيرات الزراعية للحقل مع التخزين المؤقت
  Future<void> loadImpacts(String fieldId) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final impacts = await _repo.getImpactsForField(fieldId);
      state = state.copyWith(isLoading: false, impacts: impacts);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تحميل التأثيرات الزراعية',
        impacts: [],
      );
    }
  }

  /// Load agricultural impacts by location and crop type
  /// تحميل التأثيرات الزراعية حسب الموقع ونوع المحصول
  Future<void> loadImpactsByLocation({
    String? location,
    String? cropType,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final impacts = await _repo.getAgriculturalImpacts(
        location: location,
        cropType: cropType,
      );
      state = state.copyWith(isLoading: false, impacts: impacts);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تحميل التأثيرات الزراعية',
        impacts: [],
      );
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

/// Impacts Provider - autoDispose for proper cleanup
/// Uses repository for offline-first caching
final impactsProvider =
    StateNotifierProvider.autoDispose<ImpactsNotifier, ImpactsState>((ref) {
  final repo = ref.watch(weatherRepositoryProvider);
  return ImpactsNotifier(repo);
});

/// Impact Filter Provider - autoDispose to match parent
final impactFilterProvider = StateProvider.autoDispose<String?>((ref) => null);

/// Filtered Impacts Provider (حسب الحالة) - autoDispose to match parent
final filteredImpactsProvider =
    Provider.autoDispose<List<AgriculturalImpact>>((ref) {
  final impacts = ref.watch(impactsProvider).impacts;
  final filter = ref.watch(impactFilterProvider);

  if (filter == null) return impacts;
  return impacts.where((i) => i.status == filter).toList();
});

// ═══════════════════════════════════════════════════════════════════════════
// Forecast Providers - مزودات التوقعات
// ═══════════════════════════════════════════════════════════════════════════

/// حالة التوقعات اليومية
class ForecastState {
  final bool isLoading;
  final List<DailyForecast> forecasts;
  final String? error;

  const ForecastState({
    this.isLoading = false,
    this.forecasts = const [],
    this.error,
  });

  ForecastState copyWith({
    bool? isLoading,
    List<DailyForecast>? forecasts,
    String? error,
  }) {
    return ForecastState(
      isLoading: isLoading ?? this.isLoading,
      forecasts: forecasts ?? this.forecasts,
      error: error,
    );
  }
}

/// Forecast State Notifier - مزود التوقعات اليومية
class ForecastNotifier extends StateNotifier<ForecastState> {
  final WeatherRepository _repo;

  ForecastNotifier(this._repo) : super(const ForecastState());

  /// Load daily forecast for a field
  /// تحميل التوقعات اليومية للحقل
  Future<void> loadForecast(String fieldId, {int days = 7}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final forecasts =
          await _repo.getDailyForecastForField(fieldId, days: days);
      state = state.copyWith(isLoading: false, forecasts: forecasts);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تحميل التوقعات',
        forecasts: [],
      );
    }
  }

  /// Load forecast by location name
  /// تحميل التوقعات باسم الموقع
  Future<void> loadForecastByLocation(String location, {int days = 7}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final forecasts = await _repo.getDailyForecast(location, days: days);
      state = state.copyWith(isLoading: false, forecasts: forecasts);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تحميل التوقعات',
        forecasts: [],
      );
    }
  }

  /// Load forecast by coordinates with multi-provider fallback
  /// تحميل التوقعات بالإحداثيات مع دعم مزودين متعددين
  Future<void> loadForecastByCoordinates(
    double lat,
    double lon, {
    int days = 7,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final forecasts =
          await _repo.getForecastByCoordinates(lat, lon, days: days);
      state = state.copyWith(isLoading: false, forecasts: forecasts);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تحميل التوقعات',
        forecasts: [],
      );
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

/// Forecast Provider - autoDispose for proper cleanup
final forecastProvider =
    StateNotifierProvider.autoDispose<ForecastNotifier, ForecastState>((ref) {
  final repo = ref.watch(weatherRepositoryProvider);
  return ForecastNotifier(repo);
});

/// حالة التوقعات الساعية
class HourlyForecastState {
  final bool isLoading;
  final List<HourlyForecast> forecasts;
  final String? error;

  const HourlyForecastState({
    this.isLoading = false,
    this.forecasts = const [],
    this.error,
  });

  HourlyForecastState copyWith({
    bool? isLoading,
    List<HourlyForecast>? forecasts,
    String? error,
  }) {
    return HourlyForecastState(
      isLoading: isLoading ?? this.isLoading,
      forecasts: forecasts ?? this.forecasts,
      error: error,
    );
  }
}

/// Hourly Forecast State Notifier - مزود التوقعات الساعية
class HourlyForecastNotifier extends StateNotifier<HourlyForecastState> {
  final WeatherRepository _repo;

  HourlyForecastNotifier(this._repo) : super(const HourlyForecastState());

  /// Load hourly forecast for a location
  /// تحميل التوقعات الساعية للموقع
  Future<void> loadHourlyForecast(String location, {int hours = 24}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final forecasts = await _repo.getHourlyForecast(location, hours: hours);
      state = state.copyWith(isLoading: false, forecasts: forecasts);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تحميل التوقعات الساعية',
        forecasts: [],
      );
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

/// Hourly Forecast Provider - autoDispose for proper cleanup
final hourlyForecastProvider = StateNotifierProvider.autoDispose<
    HourlyForecastNotifier, HourlyForecastState>((ref) {
  final repo = ref.watch(weatherRepositoryProvider);
  return HourlyForecastNotifier(repo);
});

// ═══════════════════════════════════════════════════════════════════════════
// Home Widget Weather Provider - مزود الطقس للصفحة الرئيسية
// ═══════════════════════════════════════════════════════════════════════════

/// Selected location for home weather widget
final homeWeatherLocationProvider = StateProvider<String?>((ref) => null);

/// Current weather for home widget (persistent, not auto-disposed)
final homeWeatherProvider = FutureProvider<WeatherData?>((ref) async {
  final repo = ref.watch(weatherRepositoryProvider);
  final location = ref.watch(homeWeatherLocationProvider);

  if (location == null) {
    // Try default location (Riyadh)
    try {
      return await repo.getWeatherByLocation('riyadh');
    } catch (e) {
      return null;
    }
  }

  try {
    return await repo.getWeatherByLocation(location);
  } catch (e) {
    return null;
  }
});

/// Weather alerts count for app badge
final weatherAlertsCountProvider = FutureProvider<int>((ref) async {
  final repo = ref.watch(weatherRepositoryProvider);
  final location = ref.watch(homeWeatherLocationProvider) ?? 'riyadh';

  try {
    final alerts = await repo.getAlerts(location);
    return alerts.where((a) => a.endTime.isAfter(DateTime.now())).length;
  } catch (e) {
    return 0;
  }
});
