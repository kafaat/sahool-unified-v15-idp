/// SAHOOL Astronomical Calendar Providers
/// مزودات التقويم الفلكي باستخدام Riverpod
///
/// توفر هذه المزودات إدارة الحالة للتقويم الفلكي اليمني

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../../../core/config/env_config.dart' as env;
import '../data/remote/astronomical_api.dart';
import '../models/astronomical_models.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// مزود API - API Provider
// ═══════════════════════════════════════════════════════════════════════════════

/// مزود خدمة API للتقويم الفلكي
final astronomicalApiProvider = Provider<AstronomicalApi>((ref) {
  final dio = Dio(BaseOptions(
    connectTimeout: env.EnvConfig.connectTimeout,
    receiveTimeout: env.EnvConfig.receiveTimeout,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  ));

  // استخدام EnvConfig للحصول على URL الديناميكي
  final baseUrl = env.EnvConfig.apiBaseUrl;

  return AstronomicalApi(dio: dio, baseUrl: baseUrl);
});

// ═══════════════════════════════════════════════════════════════════════════════
// البيانات اليومية - Daily Data Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// مزود بيانات اليوم الفلكية
final todayAstronomicalProvider =
    FutureProvider.autoDispose<DailyAstronomicalData>((ref) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getToday();
});

/// مزود بيانات تاريخ محدد
final dateAstronomicalProvider = FutureProvider.autoDispose
    .family<DailyAstronomicalData, String>((ref, date) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getDate(date);
});

// ═══════════════════════════════════════════════════════════════════════════════
// التوقعات الأسبوعية - Weekly Forecast Provider
// ═══════════════════════════════════════════════════════════════════════════════

/// مزود التوقعات الأسبوعية
final weeklyForecastProvider =
    FutureProvider.autoDispose.family<WeeklyForecast, String?>((ref, startDate) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getWeeklyForecast(startDate: startDate);
});

/// مزود التوقعات الأسبوعية الحالية
final currentWeekForecastProvider =
    FutureProvider.autoDispose<WeeklyForecast>((ref) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getWeeklyForecast();
});

// ═══════════════════════════════════════════════════════════════════════════════
// طور القمر - Moon Phase Provider
// ═══════════════════════════════════════════════════════════════════════════════

/// مزود طور القمر الحالي
final currentMoonPhaseProvider =
    FutureProvider.autoDispose<MoonPhase>((ref) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getMoonPhase();
});

/// مزود طور القمر لتاريخ محدد
final moonPhaseProvider =
    FutureProvider.autoDispose.family<MoonPhase, String?>((ref, date) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getMoonPhase(date: date);
});

// ═══════════════════════════════════════════════════════════════════════════════
// المنزلة القمرية - Lunar Mansion Provider
// ═══════════════════════════════════════════════════════════════════════════════

/// مزود المنزلة القمرية الحالية
final currentLunarMansionProvider =
    FutureProvider.autoDispose<LunarMansion>((ref) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getLunarMansion();
});

/// مزود المنزلة القمرية لتاريخ محدد
final lunarMansionProvider =
    FutureProvider.autoDispose.family<LunarMansion, String?>((ref, date) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getLunarMansion(date: date);
});

// ═══════════════════════════════════════════════════════════════════════════════
// التاريخ الهجري - Hijri Date Provider
// ═══════════════════════════════════════════════════════════════════════════════

/// مزود التاريخ الهجري الحالي
final currentHijriDateProvider =
    FutureProvider.autoDispose<HijriDate>((ref) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getHijriDate();
});

// ═══════════════════════════════════════════════════════════════════════════════
// تقويم المحصول - Crop Calendar Provider
// ═══════════════════════════════════════════════════════════════════════════════

/// مزود تقويم محصول معين
final cropCalendarProvider =
    FutureProvider.autoDispose.family<CropCalendar, String>((ref, crop) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getCropCalendar(crop);
});

// ═══════════════════════════════════════════════════════════════════════════════
// أفضل الأيام - Best Days Provider
// ═══════════════════════════════════════════════════════════════════════════════

/// معاملات البحث عن أفضل الأيام
class BestDaysParams {
  final String activity;
  final int days;

  const BestDaysParams({
    this.activity = 'زراعة',
    this.days = 30,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is BestDaysParams &&
          runtimeType == other.runtimeType &&
          activity == other.activity &&
          days == other.days;

  @override
  int get hashCode => activity.hashCode ^ days.hashCode;
}

/// مزود أفضل الأيام
final bestDaysProvider = FutureProvider.autoDispose
    .family<BestDaysResult, BestDaysParams>((ref, params) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getBestDays(activity: params.activity, days: params.days);
});

// ═══════════════════════════════════════════════════════════════════════════════
// الأمثال والحكمة - Proverbs and Wisdom Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// مزود جميع الأمثال
final allProverbsProvider =
    FutureProvider.autoDispose<AllProverbs>((ref) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getProverbs();
});

/// مزود مثل اليوم
final proverbOfTheDayProvider =
    FutureProvider.autoDispose<ProverbOfTheDay>((ref) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getProverbOfTheDay();
});

/// مزود الحكمة اليومية
final dailyWisdomProvider =
    FutureProvider.autoDispose<DailyWisdom>((ref) async {
  final api = ref.watch(astronomicalApiProvider);
  return api.getWisdomToday();
});

// ═══════════════════════════════════════════════════════════════════════════════
// حالة التبويب المحدد - Selected Tab State
// ═══════════════════════════════════════════════════════════════════════════════

/// مزود التبويب المحدد في شاشة التقويم الفلكي
final selectedAstronomicalTabProvider = StateProvider<int>((ref) => 0);

/// مزود النشاط المحدد للبحث عن أفضل الأيام
final selectedActivityProvider = StateProvider<String>((ref) => 'زراعة');

/// مزود المحصول المحدد
final selectedCropProvider = StateProvider<String?>((ref) => null);
