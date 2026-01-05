/// SAHOOL Astronomical Calendar API Service
/// خدمة واجهة برمجة التطبيقات للتقويم الفلكي
///
/// توفر هذه الخدمة الوصول إلى بيانات التقويم الفلكي اليمني
/// تشمل: المنازل القمرية، أطوار القمر، التاريخ الهجري، الأمثال الزراعية

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../../models/astronomical_models.dart';

/// خدمة API للتقويم الفلكي
class AstronomicalApi {
  final Dio _dio;
  final String _baseUrl;

  AstronomicalApi({
    required Dio dio,
    required String baseUrl,
  })  : _dio = dio,
        _baseUrl = '$baseUrl/api/v1/astronomical';

  // ═══════════════════════════════════════════════════════════════════════════════
  // البيانات اليومية - Daily Data
  // ═══════════════════════════════════════════════════════════════════════════════

  /// الحصول على البيانات الفلكية لليوم الحالي
  /// Get astronomical data for today
  Future<DailyAstronomicalData> getToday() async {
    try {
      final response = await _dio.get('$_baseUrl/today');
      return DailyAstronomicalData.fromJson(response.data);
    } catch (e) {
      debugPrint('خطأ في جلب بيانات اليوم: $e');
      rethrow;
    }
  }

  /// الحصول على البيانات الفلكية لتاريخ محدد
  /// Get astronomical data for a specific date
  Future<DailyAstronomicalData> getDate(String date) async {
    try {
      final response = await _dio.get('$_baseUrl/date/$date');
      return DailyAstronomicalData.fromJson(response.data);
    } catch (e) {
      debugPrint('خطأ في جلب بيانات التاريخ: $e');
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // التوقعات الأسبوعية - Weekly Forecast
  // ═══════════════════════════════════════════════════════════════════════════════

  /// الحصول على التوقعات الأسبوعية
  /// Get weekly forecast
  Future<WeeklyForecast> getWeeklyForecast({String? startDate}) async {
    try {
      final queryParams = startDate != null ? {'start_date': startDate} : null;
      final response = await _dio.get(
        '$_baseUrl/week',
        queryParameters: queryParams,
      );
      return WeeklyForecast.fromJson(response.data);
    } catch (e) {
      debugPrint('خطأ في جلب التوقعات الأسبوعية: $e');
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // طور القمر - Moon Phase
  // ═══════════════════════════════════════════════════════════════════════════════

  /// الحصول على مرحلة القمر
  /// Get moon phase
  Future<MoonPhase> getMoonPhase({String? date}) async {
    try {
      final queryParams = date != null ? {'date_str': date} : null;
      final response = await _dio.get(
        '$_baseUrl/moon-phase',
        queryParameters: queryParams,
      );
      return MoonPhase.fromJson(response.data);
    } catch (e) {
      debugPrint('خطأ في جلب طور القمر: $e');
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // المنزلة القمرية - Lunar Mansion
  // ═══════════════════════════════════════════════════════════════════════════════

  /// الحصول على المنزلة القمرية
  /// Get lunar mansion
  Future<LunarMansion> getLunarMansion({String? date}) async {
    try {
      final queryParams = date != null ? {'date_str': date} : null;
      final response = await _dio.get(
        '$_baseUrl/lunar-mansion',
        queryParameters: queryParams,
      );
      return LunarMansion.fromJson(response.data);
    } catch (e) {
      debugPrint('خطأ في جلب المنزلة القمرية: $e');
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // التاريخ الهجري - Hijri Date
  // ═══════════════════════════════════════════════════════════════════════════════

  /// الحصول على التاريخ الهجري
  /// Get Hijri date
  Future<HijriDate> getHijriDate({String? date}) async {
    try {
      final queryParams = date != null ? {'date_str': date} : null;
      final response = await _dio.get(
        '$_baseUrl/hijri',
        queryParameters: queryParams,
      );
      return HijriDate.fromJson(response.data);
    } catch (e) {
      debugPrint('خطأ في جلب التاريخ الهجري: $e');
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // تقويم المحصول - Crop Calendar
  // ═══════════════════════════════════════════════════════════════════════════════

  /// الحصول على تقويم محصول معين
  /// Get crop calendar
  Future<CropCalendar> getCropCalendar(String crop) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/crop-calendar/${Uri.encodeComponent(crop)}',
      );
      return CropCalendar.fromJson(response.data);
    } catch (e) {
      debugPrint('خطأ في جلب تقويم المحصول: $e');
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // أفضل الأيام - Best Days
  // ═══════════════════════════════════════════════════════════════════════════════

  /// البحث عن أفضل الأيام لنشاط زراعي معين
  /// Search for best days for a farming activity
  Future<BestDaysResult> getBestDays({
    String activity = 'زراعة',
    int days = 30,
  }) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/best-days',
        queryParameters: {
          'activity': activity,
          'days': days.toString(),
        },
      );
      return BestDaysResult.fromJson(response.data);
    } catch (e) {
      debugPrint('خطأ في جلب أفضل الأيام: $e');
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // الأمثال والحكمة - Proverbs and Wisdom
  // ═══════════════════════════════════════════════════════════════════════════════

  /// الحصول على جميع الأمثال الزراعية اليمنية
  /// Get all Yemeni farming proverbs
  Future<AllProverbs> getProverbs() async {
    try {
      final response = await _dio.get('$_baseUrl/proverbs');
      return AllProverbs.fromJson(response.data);
    } catch (e) {
      debugPrint('خطأ في جلب الأمثال: $e');
      rethrow;
    }
  }

  /// الحصول على مثل اليوم
  /// Get proverb of the day
  Future<ProverbOfTheDay> getProverbOfTheDay() async {
    try {
      final response = await _dio.get('$_baseUrl/proverbs/today');
      return ProverbOfTheDay.fromJson(response.data);
    } catch (e) {
      debugPrint('خطأ في جلب مثل اليوم: $e');
      rethrow;
    }
  }

  /// الحصول على الحكمة اليومية الشاملة
  /// Get comprehensive daily wisdom
  Future<DailyWisdom> getWisdomToday() async {
    try {
      final response = await _dio.get('$_baseUrl/wisdom/today');
      return DailyWisdom.fromJson(response.data);
    } catch (e) {
      debugPrint('خطأ في جلب الحكمة اليومية: $e');
      rethrow;
    }
  }
}
