/// SAHOOL Astronomical Calendar Providers
/// مزودات التقويم الفلكي

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/remote/astronomical_api.dart';
import '../../domain/entities/astronomical_entities.dart';

/// API Provider
final astronomicalApiProvider = Provider<AstronomicalCalendarApi>((ref) {
  return AstronomicalCalendarApi();
});

/// حالة البيانات اليومية
class DailyAstronomicalState {
  final bool isLoading;
  final DailyAstronomicalData? data;
  final String? error;

  const DailyAstronomicalState({
    this.isLoading = false,
    this.data,
    this.error,
  });

  DailyAstronomicalState copyWith({
    bool? isLoading,
    DailyAstronomicalData? data,
    String? error,
  }) {
    return DailyAstronomicalState(
      isLoading: isLoading ?? this.isLoading,
      data: data ?? this.data,
      error: error,
    );
  }
}

/// Daily Data Notifier
class DailyAstronomicalNotifier extends StateNotifier<DailyAstronomicalState> {
  final AstronomicalCalendarApi _api;

  DailyAstronomicalNotifier(this._api) : super(const DailyAstronomicalState());

  /// جلب بيانات اليوم
  Future<void> loadToday() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final data = await _api.getToday();
      state = state.copyWith(isLoading: false, data: data);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل جلب بيانات اليوم: ${e.toString()}',
      );
    }
  }

  /// جلب بيانات تاريخ محدد
  Future<void> loadDate(String dateStr) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final data = await _api.getDate(dateStr);
      state = state.copyWith(isLoading: false, data: data);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل جلب البيانات: ${e.toString()}',
      );
    }
  }

  void clear() {
    state = const DailyAstronomicalState();
  }
}

/// Daily Astronomical Provider
final dailyAstronomicalProvider =
    StateNotifierProvider<DailyAstronomicalNotifier, DailyAstronomicalState>(
        (ref) {
  final api = ref.watch(astronomicalApiProvider);
  return DailyAstronomicalNotifier(api);
});

/// حالة التوقعات الأسبوعية
class WeeklyForecastState {
  final bool isLoading;
  final WeeklyForecast? forecast;
  final String? error;

  const WeeklyForecastState({
    this.isLoading = false,
    this.forecast,
    this.error,
  });

  WeeklyForecastState copyWith({
    bool? isLoading,
    WeeklyForecast? forecast,
    String? error,
  }) {
    return WeeklyForecastState(
      isLoading: isLoading ?? this.isLoading,
      forecast: forecast ?? this.forecast,
      error: error,
    );
  }
}

/// Weekly Forecast Notifier
class WeeklyForecastNotifier extends StateNotifier<WeeklyForecastState> {
  final AstronomicalCalendarApi _api;

  WeeklyForecastNotifier(this._api) : super(const WeeklyForecastState());

  Future<void> loadWeeklyForecast({String? startDate}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final forecast = await _api.getWeeklyForecast(startDate: startDate);
      state = state.copyWith(isLoading: false, forecast: forecast);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل جلب التوقعات الأسبوعية: ${e.toString()}',
      );
    }
  }
}

/// Weekly Forecast Provider
final weeklyForecastProvider =
    StateNotifierProvider<WeeklyForecastNotifier, WeeklyForecastState>((ref) {
  final api = ref.watch(astronomicalApiProvider);
  return WeeklyForecastNotifier(api);
});

/// حالة تقويم المحصول
class CropCalendarState {
  final bool isLoading;
  final CropCalendar? calendar;
  final String? error;

  const CropCalendarState({
    this.isLoading = false,
    this.calendar,
    this.error,
  });

  CropCalendarState copyWith({
    bool? isLoading,
    CropCalendar? calendar,
    String? error,
  }) {
    return CropCalendarState(
      isLoading: isLoading ?? this.isLoading,
      calendar: calendar ?? this.calendar,
      error: error,
    );
  }
}

/// Crop Calendar Notifier
class CropCalendarNotifier extends StateNotifier<CropCalendarState> {
  final AstronomicalCalendarApi _api;

  CropCalendarNotifier(this._api) : super(const CropCalendarState());

  Future<void> loadCropCalendar(String cropName) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final calendar = await _api.getCropCalendar(cropName);
      state = state.copyWith(isLoading: false, calendar: calendar);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل جلب تقويم المحصول: ${e.toString()}',
      );
    }
  }
}

/// Crop Calendar Provider
final cropCalendarProvider =
    StateNotifierProvider<CropCalendarNotifier, CropCalendarState>((ref) {
  final api = ref.watch(astronomicalApiProvider);
  return CropCalendarNotifier(api);
});

/// حالة أفضل الأيام
class BestDaysState {
  final bool isLoading;
  final BestDaysResult? result;
  final String? error;

  const BestDaysState({
    this.isLoading = false,
    this.result,
    this.error,
  });

  BestDaysState copyWith({
    bool? isLoading,
    BestDaysResult? result,
    String? error,
  }) {
    return BestDaysState(
      isLoading: isLoading ?? this.isLoading,
      result: result ?? this.result,
      error: error,
    );
  }
}

/// Best Days Notifier
class BestDaysNotifier extends StateNotifier<BestDaysState> {
  final AstronomicalCalendarApi _api;

  BestDaysNotifier(this._api) : super(const BestDaysState());

  Future<void> findBestDays({
    required String activity,
    int days = 30,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final result = await _api.getBestDays(activity: activity, days: days);
      state = state.copyWith(isLoading: false, result: result);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل البحث عن أفضل الأيام: ${e.toString()}',
      );
    }
  }
}

/// Best Days Provider
final bestDaysProvider =
    StateNotifierProvider<BestDaysNotifier, BestDaysState>((ref) {
  final api = ref.watch(astronomicalApiProvider);
  return BestDaysNotifier(api);
});

/// Moon Phase Provider (FutureProvider)
final moonPhaseProvider = FutureProvider.family<MoonPhase, String?>((ref, dateStr) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getMoonPhase(dateStr: dateStr);
});

/// Lunar Mansion Provider
final lunarMansionProvider = FutureProvider.family<LunarMansion, String?>((ref, dateStr) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getLunarMansion(dateStr: dateStr);
});

/// Hijri Date Provider
final hijriDateProvider = FutureProvider.family<HijriDate, String?>((ref, dateStr) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getHijriDate(dateStr: dateStr);
});

/// Current Season Provider
final currentSeasonProvider = FutureProvider<SeasonInfo>((ref) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getCurrentSeason();
});

/// Supported Crops Provider
final supportedCropsProvider = FutureProvider<List<Map<String, String>>>((ref) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getSupportedCrops();
});

/// Lunar Mansions List Provider
final lunarMansionsListProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getLunarMansions();
});

/// التاريخ المحدد
final selectedDateProvider = StateProvider<DateTime>((ref) => DateTime.now());

/// النشاط المحدد للبحث
final selectedActivityProvider = StateProvider<String>((ref) => 'زراعة');

/// المحصول المحدد
final selectedCropProvider = StateProvider<String?>((ref) => null);
