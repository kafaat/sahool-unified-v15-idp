/// SAHOOL Astronomical Calendar Models
/// نماذج التقويم الفلكي
///
/// هذه النماذج تمثل البيانات الفلكية للتقويم الزراعي اليمني التقليدي
/// تشمل: المنازل القمرية، أطوار القمر، التاريخ الهجري، الأمثال الزراعية

import 'package:freezed_annotation/freezed_annotation.dart';

part 'astronomical_models.freezed.dart';
part 'astronomical_models.g.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// مرحلة القمر - Moon Phase
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class MoonPhase with _$MoonPhase {
  const factory MoonPhase({
    @JsonKey(name: 'phase_key') required String phaseKey,
    required String name,
    @JsonKey(name: 'name_en') required String nameEn,
    required String icon,
    required double illumination,
    @JsonKey(name: 'age_days') required double ageDays,
    @JsonKey(name: 'is_waxing') required bool isWaxing,
    @JsonKey(name: 'farming_good') required bool farmingGood,
  }) = _MoonPhase;

  factory MoonPhase.fromJson(Map<String, dynamic> json) =>
      _$MoonPhaseFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// المنزلة القمرية - Lunar Mansion
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class LunarMansion with _$LunarMansion {
  const factory LunarMansion({
    required int number,
    required String name,
    @JsonKey(name: 'name_en') required String nameEn,
    required String constellation,
    @JsonKey(name: 'constellation_en') required String constellationEn,
    required String element,
    required String farming,
    @JsonKey(name: 'farming_score') required int farmingScore,
    required List<String> crops,
    required List<String> activities,
    required List<String> avoid,
    required String description,
  }) = _LunarMansion;

  factory LunarMansion.fromJson(Map<String, dynamic> json) =>
      _$LunarMansionFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// التاريخ الهجري - Hijri Date
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class HijriDate with _$HijriDate {
  const factory HijriDate({
    required int year,
    required int month,
    required int day,
    @JsonKey(name: 'month_name') required String monthName,
    @JsonKey(name: 'month_name_en') required String monthNameEn,
    required String weekday,
  }) = _HijriDate;

  factory HijriDate.fromJson(Map<String, dynamic> json) =>
      _$HijriDateFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// معلومات البرج - Zodiac Info
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class ZodiacInfo with _$ZodiacInfo {
  const factory ZodiacInfo({
    required String name,
    @JsonKey(name: 'name_en') required String nameEn,
    required String element,
    required String fertility,
    required int score,
  }) = _ZodiacInfo;

  factory ZodiacInfo.fromJson(Map<String, dynamic> json) =>
      _$ZodiacInfoFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// معلومات الموسم - Season Info
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class SeasonInfo with _$SeasonInfo {
  const factory SeasonInfo({
    required String name,
    @JsonKey(name: 'name_en') required String nameEn,
    required String description,
    @JsonKey(name: 'main_crops') required List<String> mainCrops,
    required List<String> activities,
  }) = _SeasonInfo;

  factory SeasonInfo.fromJson(Map<String, dynamic> json) =>
      _$SeasonInfoFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// توصية زراعية - Farming Recommendation
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class FarmingRecommendation with _$FarmingRecommendation {
  const factory FarmingRecommendation({
    required String activity,
    required String suitability,
    @JsonKey(name: 'suitability_score') required int suitabilityScore,
    required String reason,
    @JsonKey(name: 'best_time') String? bestTime,
  }) = _FarmingRecommendation;

  factory FarmingRecommendation.fromJson(Map<String, dynamic> json) =>
      _$FarmingRecommendationFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// البيانات الفلكية اليومية - Daily Astronomical Data
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class DailyAstronomicalData with _$DailyAstronomicalData {
  const factory DailyAstronomicalData({
    @JsonKey(name: 'date_gregorian') required String dateGregorian,
    @JsonKey(name: 'date_hijri') required HijriDate dateHijri,
    @JsonKey(name: 'moon_phase') required MoonPhase moonPhase,
    @JsonKey(name: 'lunar_mansion') required LunarMansion lunarMansion,
    required ZodiacInfo zodiac,
    required SeasonInfo season,
    @JsonKey(name: 'overall_farming_score') required int overallFarmingScore,
    required List<FarmingRecommendation> recommendations,
  }) = _DailyAstronomicalData;

  factory DailyAstronomicalData.fromJson(Map<String, dynamic> json) =>
      _$DailyAstronomicalDataFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// التوقعات الأسبوعية - Weekly Forecast
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class WeeklyForecast with _$WeeklyForecast {
  const factory WeeklyForecast({
    @JsonKey(name: 'start_date') required String startDate,
    @JsonKey(name: 'end_date') required String endDate,
    required List<DailyAstronomicalData> days,
    @JsonKey(name: 'best_planting_days') required List<String> bestPlantingDays,
    @JsonKey(name: 'best_harvesting_days') required List<String> bestHarvestingDays,
    @JsonKey(name: 'avoid_days') required List<String> avoidDays,
  }) = _WeeklyForecast;

  factory WeeklyForecast.fromJson(Map<String, dynamic> json) =>
      _$WeeklyForecastFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// تقويم المحصول - Crop Calendar
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class CropCalendar with _$CropCalendar {
  const factory CropCalendar({
    @JsonKey(name: 'crop_name') required String cropName,
    @JsonKey(name: 'crop_name_en') required String cropNameEn,
    @JsonKey(name: 'best_planting_mansions') required List<int> bestPlantingMansions,
    @JsonKey(name: 'best_moon_phases') required List<String> bestMoonPhases,
    @JsonKey(name: 'best_zodiac_signs') required List<String> bestZodiacSigns,
    @JsonKey(name: 'optimal_months') required List<int> optimalMonths,
    @JsonKey(name: 'planting_guide') required String plantingGuide,
    @JsonKey(name: 'current_suitability') required int currentSuitability,
  }) = _CropCalendar;

  factory CropCalendar.fromJson(Map<String, dynamic> json) =>
      _$CropCalendarFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// أفضل يوم - Best Day
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class BestDay with _$BestDay {
  const factory BestDay({
    required String date,
    @JsonKey(name: 'hijri_date') required String hijriDate,
    @JsonKey(name: 'moon_phase') required String moonPhase,
    @JsonKey(name: 'lunar_mansion') required String lunarMansion,
    required int score,
    required String reason,
  }) = _BestDay;

  factory BestDay.fromJson(Map<String, dynamic> json) =>
      _$BestDayFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// نتيجة البحث عن أفضل الأيام - Best Days Result
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class BestDaysResult with _$BestDaysResult {
  const factory BestDaysResult({
    required String activity,
    @JsonKey(name: 'search_period_days') required int searchPeriodDays,
    @JsonKey(name: 'best_days') required List<BestDay> bestDays,
    @JsonKey(name: 'total_found') required int totalFound,
  }) = _BestDaysResult;

  factory BestDaysResult.fromJson(Map<String, dynamic> json) =>
      _$BestDaysResultFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// مثل زراعي - Proverb
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class Proverb with _$Proverb {
  const factory Proverb({
    required String proverb,
    required String meaning,
    required String application,
    String? mansion,
  }) = _Proverb;

  factory Proverb.fromJson(Map<String, dynamic> json) =>
      _$ProverbFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// مثل اليوم مع السياق - Proverb of the Day
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class ProverbOfTheDay with _$ProverbOfTheDay {
  const factory ProverbOfTheDay({
    required String date,
    @JsonKey(name: 'proverb_of_the_day') required Proverb proverbOfTheDay,
    @JsonKey(name: 'current_mansion') required String currentMansion,
    @JsonKey(name: 'current_moon_phase') required String currentMoonPhase,
    @JsonKey(name: 'current_season') required String currentSeason,
    @JsonKey(name: 'season_proverbs') required List<Proverb> seasonProverbs,
    required String context,
  }) = _ProverbOfTheDay;

  factory ProverbOfTheDay.fromJson(Map<String, dynamic> json) =>
      _$ProverbOfTheDayFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// جميع الأمثال - All Proverbs
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class AllProverbs with _$AllProverbs {
  const factory AllProverbs({
    required List<Proverb> general,
    @JsonKey(name: 'by_crop') required Map<String, List<Proverb>> byCrop,
    @JsonKey(name: 'by_season') required Map<String, List<Proverb>> bySeason,
    @JsonKey(name: 'total_proverbs') required int totalProverbs,
  }) = _AllProverbs;

  factory AllProverbs.fromJson(Map<String, dynamic> json) =>
      _$AllProverbsFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// الحكمة اليومية - Daily Wisdom
// ═══════════════════════════════════════════════════════════════════════════════

@freezed
class DailyWisdomProverb with _$DailyWisdomProverb {
  const factory DailyWisdomProverb({
    required String text,
    required String meaning,
    required String application,
  }) = _DailyWisdomProverb;

  factory DailyWisdomProverb.fromJson(Map<String, dynamic> json) =>
      _$DailyWisdomProverbFromJson(json);
}

@freezed
class DailyWisdomMansion with _$DailyWisdomMansion {
  const factory DailyWisdomMansion({
    required String name,
    required String description,
    required List<String> tips,
  }) = _DailyWisdomMansion;

  factory DailyWisdomMansion.fromJson(Map<String, dynamic> json) =>
      _$DailyWisdomMansionFromJson(json);
}

@freezed
class DailyWisdomMoonPhase with _$DailyWisdomMoonPhase {
  const factory DailyWisdomMoonPhase({
    required String name,
    required String icon,
    required String illumination,
    required List<String> tips,
  }) = _DailyWisdomMoonPhase;

  factory DailyWisdomMoonPhase.fromJson(Map<String, dynamic> json) =>
      _$DailyWisdomMoonPhaseFromJson(json);
}

@freezed
class DailyWisdomSeason with _$DailyWisdomSeason {
  const factory DailyWisdomSeason({
    required String name,
    required List<String> crops,
    required List<String> activities,
  }) = _DailyWisdomSeason;

  factory DailyWisdomSeason.fromJson(Map<String, dynamic> json) =>
      _$DailyWisdomSeasonFromJson(json);
}

@freezed
class DailyWisdom with _$DailyWisdom {
  const factory DailyWisdom({
    required String date,
    @JsonKey(name: 'hijri_date') String? hijriDate,
    @JsonKey(name: 'proverb_of_the_day') required DailyWisdomProverb proverbOfTheDay,
    @JsonKey(name: 'current_mansion') required DailyWisdomMansion currentMansion,
    @JsonKey(name: 'moon_phase') required DailyWisdomMoonPhase moonPhase,
    @JsonKey(name: 'current_star') dynamic currentStar,
    required DailyWisdomSeason season,
    @JsonKey(name: 'overall_score') required int overallScore,
    required String summary,
  }) = _DailyWisdom;

  factory DailyWisdom.fromJson(Map<String, dynamic> json) =>
      _$DailyWisdomFromJson(json);
}
