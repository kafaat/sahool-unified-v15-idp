/// SAHOOL Astronomical Calendar Models
/// نماذج التقويم الفلكي
///
/// هذه النماذج تمثل البيانات الفلكية للتقويم الزراعي اليمني التقليدي
/// تشمل: المنازل القمرية، أطوار القمر، التاريخ الهجري، الأمثال الزراعية
library;

import 'package:flutter/foundation.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// مرحلة القمر - Moon Phase
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class MoonPhase {
  final String phaseKey;
  final String name;
  final String nameEn;
  final String icon;
  final double illumination;
  final double ageDays;
  final bool isWaxing;
  final bool farmingGood;

  const MoonPhase({
    required this.phaseKey,
    required this.name,
    required this.nameEn,
    required this.icon,
    required this.illumination,
    required this.ageDays,
    required this.isWaxing,
    required this.farmingGood,
  });

  factory MoonPhase.fromJson(Map<String, dynamic> json) {
    return MoonPhase(
      phaseKey: (json['phase_key'] ?? '') as String,
      name: (json['name'] ?? '') as String,
      nameEn: (json['name_en'] ?? '') as String,
      icon: (json['icon'] ?? '') as String,
      illumination: ((json['illumination'] ?? 0.0) as num).toDouble(),
      ageDays: ((json['age_days'] ?? 0.0) as num).toDouble(),
      isWaxing: (json['is_waxing'] ?? false) as bool,
      farmingGood: (json['farming_good'] ?? false) as bool,
    );
  }

  Map<String, dynamic> toJson() => {
    'phase_key': phaseKey,
    'name': name,
    'name_en': nameEn,
    'icon': icon,
    'illumination': illumination,
    'age_days': ageDays,
    'is_waxing': isWaxing,
    'farming_good': farmingGood,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// المنزلة القمرية - Lunar Mansion
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class LunarMansion {
  final int number;
  final String name;
  final String nameEn;
  final String constellation;
  final String constellationEn;
  final String element;
  final String farming;
  final int farmingScore;
  final List<String> crops;
  final List<String> activities;
  final List<String> avoid;
  final String description;

  const LunarMansion({
    required this.number,
    required this.name,
    required this.nameEn,
    required this.constellation,
    required this.constellationEn,
    required this.element,
    required this.farming,
    required this.farmingScore,
    required this.crops,
    required this.activities,
    required this.avoid,
    required this.description,
  });

  factory LunarMansion.fromJson(Map<String, dynamic> json) {
    return LunarMansion(
      number: (json['number'] ?? 0) as int,
      name: (json['name'] ?? '') as String,
      nameEn: (json['name_en'] ?? '') as String,
      constellation: (json['constellation'] ?? '') as String,
      constellationEn: (json['constellation_en'] ?? '') as String,
      element: (json['element'] ?? '') as String,
      farming: (json['farming'] ?? '') as String,
      farmingScore: (json['farming_score'] ?? 0) as int,
      crops: (json['crops'] as List?)?.cast<String>() ?? [],
      activities: (json['activities'] as List?)?.cast<String>() ?? [],
      avoid: (json['avoid'] as List?)?.cast<String>() ?? [],
      description: (json['description'] ?? '') as String,
    );
  }

  Map<String, dynamic> toJson() => {
    'number': number,
    'name': name,
    'name_en': nameEn,
    'constellation': constellation,
    'constellation_en': constellationEn,
    'element': element,
    'farming': farming,
    'farming_score': farmingScore,
    'crops': crops,
    'activities': activities,
    'avoid': avoid,
    'description': description,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// التاريخ الهجري - Hijri Date
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class HijriDate {
  final int year;
  final int month;
  final int day;
  final String monthName;
  final String monthNameEn;
  final String weekday;

  const HijriDate({
    required this.year,
    required this.month,
    required this.day,
    required this.monthName,
    required this.monthNameEn,
    required this.weekday,
  });

  factory HijriDate.fromJson(Map<String, dynamic> json) {
    return HijriDate(
      year: (json['year'] ?? 0) as int,
      month: (json['month'] ?? 0) as int,
      day: (json['day'] ?? 0) as int,
      monthName: (json['month_name'] ?? '') as String,
      monthNameEn: (json['month_name_en'] ?? '') as String,
      weekday: (json['weekday'] ?? '') as String,
    );
  }

  Map<String, dynamic> toJson() => {
    'year': year,
    'month': month,
    'day': day,
    'month_name': monthName,
    'month_name_en': monthNameEn,
    'weekday': weekday,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// معلومات البرج - Zodiac Info
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class ZodiacInfo {
  final String name;
  final String nameEn;
  final String element;
  final String fertility;
  final int score;

  const ZodiacInfo({
    required this.name,
    required this.nameEn,
    required this.element,
    required this.fertility,
    required this.score,
  });

  factory ZodiacInfo.fromJson(Map<String, dynamic> json) {
    return ZodiacInfo(
      name: (json['name'] ?? '') as String,
      nameEn: (json['name_en'] ?? '') as String,
      element: (json['element'] ?? '') as String,
      fertility: (json['fertility'] ?? '') as String,
      score: (json['score'] ?? 0) as int,
    );
  }

  Map<String, dynamic> toJson() => {
    'name': name,
    'name_en': nameEn,
    'element': element,
    'fertility': fertility,
    'score': score,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// معلومات الموسم - Season Info
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class SeasonInfo {
  final String name;
  final String nameEn;
  final String description;
  final List<String> mainCrops;
  final List<String> activities;

  const SeasonInfo({
    required this.name,
    required this.nameEn,
    required this.description,
    required this.mainCrops,
    required this.activities,
  });

  factory SeasonInfo.fromJson(Map<String, dynamic> json) {
    return SeasonInfo(
      name: (json['name'] ?? '') as String,
      nameEn: (json['name_en'] ?? '') as String,
      description: (json['description'] ?? '') as String,
      mainCrops: (json['main_crops'] as List?)?.cast<String>() ?? [],
      activities: (json['activities'] as List?)?.cast<String>() ?? [],
    );
  }

  Map<String, dynamic> toJson() => {
    'name': name,
    'name_en': nameEn,
    'description': description,
    'main_crops': mainCrops,
    'activities': activities,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// توصية زراعية - Farming Recommendation
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class FarmingRecommendation {
  final String activity;
  final String suitability;
  final int suitabilityScore;
  final String reason;
  final String? bestTime;

  const FarmingRecommendation({
    required this.activity,
    required this.suitability,
    required this.suitabilityScore,
    required this.reason,
    this.bestTime,
  });

  factory FarmingRecommendation.fromJson(Map<String, dynamic> json) {
    return FarmingRecommendation(
      activity: (json['activity'] ?? '') as String,
      suitability: (json['suitability'] ?? '') as String,
      suitabilityScore: (json['suitability_score'] ?? 0) as int,
      reason: (json['reason'] ?? '') as String,
      bestTime: json['best_time'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'activity': activity,
    'suitability': suitability,
    'suitability_score': suitabilityScore,
    'reason': reason,
    'best_time': bestTime,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// البيانات الفلكية اليومية - Daily Astronomical Data
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class DailyAstronomicalData {
  final String dateGregorian;
  final HijriDate dateHijri;
  final MoonPhase moonPhase;
  final LunarMansion lunarMansion;
  final ZodiacInfo zodiac;
  final SeasonInfo season;
  final int overallFarmingScore;
  final List<FarmingRecommendation> recommendations;

  const DailyAstronomicalData({
    required this.dateGregorian,
    required this.dateHijri,
    required this.moonPhase,
    required this.lunarMansion,
    required this.zodiac,
    required this.season,
    required this.overallFarmingScore,
    required this.recommendations,
  });

  factory DailyAstronomicalData.fromJson(Map<String, dynamic> json) {
    return DailyAstronomicalData(
      dateGregorian: (json['date_gregorian'] ?? '') as String,
      dateHijri: HijriDate.fromJson(json['date_hijri'] as Map<String, dynamic>? ?? {}),
      moonPhase: MoonPhase.fromJson(json['moon_phase'] as Map<String, dynamic>? ?? {}),
      lunarMansion: LunarMansion.fromJson(json['lunar_mansion'] as Map<String, dynamic>? ?? {}),
      zodiac: ZodiacInfo.fromJson(json['zodiac'] as Map<String, dynamic>? ?? {}),
      season: SeasonInfo.fromJson(json['season'] as Map<String, dynamic>? ?? {}),
      overallFarmingScore: (json['overall_farming_score'] ?? 0) as int,
      recommendations: (json['recommendations'] as List?)
          ?.map((r) => FarmingRecommendation.fromJson(r as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() => {
    'date_gregorian': dateGregorian,
    'date_hijri': dateHijri.toJson(),
    'moon_phase': moonPhase.toJson(),
    'lunar_mansion': lunarMansion.toJson(),
    'zodiac': zodiac.toJson(),
    'season': season.toJson(),
    'overall_farming_score': overallFarmingScore,
    'recommendations': recommendations.map((r) => r.toJson()).toList(),
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// التوقعات الأسبوعية - Weekly Forecast
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class WeeklyForecast {
  final String startDate;
  final String endDate;
  final List<DailyAstronomicalData> days;
  final List<String> bestPlantingDays;
  final List<String> bestHarvestingDays;
  final List<String> avoidDays;

  const WeeklyForecast({
    required this.startDate,
    required this.endDate,
    required this.days,
    required this.bestPlantingDays,
    required this.bestHarvestingDays,
    required this.avoidDays,
  });

  factory WeeklyForecast.fromJson(Map<String, dynamic> json) {
    return WeeklyForecast(
      startDate: (json['start_date'] ?? '') as String,
      endDate: (json['end_date'] ?? '') as String,
      days: (json['days'] as List?)
          ?.map((d) => DailyAstronomicalData.fromJson(d as Map<String, dynamic>))
          .toList() ?? [],
      bestPlantingDays: (json['best_planting_days'] as List?)?.cast<String>() ?? [],
      bestHarvestingDays: (json['best_harvesting_days'] as List?)?.cast<String>() ?? [],
      avoidDays: (json['avoid_days'] as List?)?.cast<String>() ?? [],
    );
  }

  Map<String, dynamic> toJson() => {
    'start_date': startDate,
    'end_date': endDate,
    'days': days.map((d) => d.toJson()).toList(),
    'best_planting_days': bestPlantingDays,
    'best_harvesting_days': bestHarvestingDays,
    'avoid_days': avoidDays,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// تقويم المحصول - Crop Calendar
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class CropCalendar {
  final String cropName;
  final String cropNameEn;
  final List<int> bestPlantingMansions;
  final List<String> bestMoonPhases;
  final List<String> bestZodiacSigns;
  final List<int> optimalMonths;
  final String plantingGuide;
  final int currentSuitability;

  const CropCalendar({
    required this.cropName,
    required this.cropNameEn,
    required this.bestPlantingMansions,
    required this.bestMoonPhases,
    required this.bestZodiacSigns,
    required this.optimalMonths,
    required this.plantingGuide,
    required this.currentSuitability,
  });

  factory CropCalendar.fromJson(Map<String, dynamic> json) {
    return CropCalendar(
      cropName: (json['crop_name'] ?? '') as String,
      cropNameEn: (json['crop_name_en'] ?? '') as String,
      bestPlantingMansions: (json['best_planting_mansions'] as List?)?.cast<int>() ?? [],
      bestMoonPhases: (json['best_moon_phases'] as List?)?.cast<String>() ?? [],
      bestZodiacSigns: (json['best_zodiac_signs'] as List?)?.cast<String>() ?? [],
      optimalMonths: (json['optimal_months'] as List?)?.cast<int>() ?? [],
      plantingGuide: (json['planting_guide'] ?? '') as String,
      currentSuitability: (json['current_suitability'] ?? 0) as int,
    );
  }

  Map<String, dynamic> toJson() => {
    'crop_name': cropName,
    'crop_name_en': cropNameEn,
    'best_planting_mansions': bestPlantingMansions,
    'best_moon_phases': bestMoonPhases,
    'best_zodiac_signs': bestZodiacSigns,
    'optimal_months': optimalMonths,
    'planting_guide': plantingGuide,
    'current_suitability': currentSuitability,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// أفضل يوم - Best Day
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class BestDay {
  final String date;
  final String hijriDate;
  final String moonPhase;
  final String lunarMansion;
  final int score;
  final String reason;

  const BestDay({
    required this.date,
    required this.hijriDate,
    required this.moonPhase,
    required this.lunarMansion,
    required this.score,
    required this.reason,
  });

  factory BestDay.fromJson(Map<String, dynamic> json) {
    return BestDay(
      date: (json['date'] ?? '') as String,
      hijriDate: (json['hijri_date'] ?? '') as String,
      moonPhase: (json['moon_phase'] ?? '') as String,
      lunarMansion: (json['lunar_mansion'] ?? '') as String,
      score: (json['score'] ?? 0) as int,
      reason: (json['reason'] ?? '') as String,
    );
  }

  Map<String, dynamic> toJson() => {
    'date': date,
    'hijri_date': hijriDate,
    'moon_phase': moonPhase,
    'lunar_mansion': lunarMansion,
    'score': score,
    'reason': reason,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// نتيجة البحث عن أفضل الأيام - Best Days Result
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class BestDaysResult {
  final String activity;
  final int searchPeriodDays;
  final List<BestDay> bestDays;
  final int totalFound;

  const BestDaysResult({
    required this.activity,
    required this.searchPeriodDays,
    required this.bestDays,
    required this.totalFound,
  });

  factory BestDaysResult.fromJson(Map<String, dynamic> json) {
    return BestDaysResult(
      activity: (json['activity'] ?? '') as String,
      searchPeriodDays: (json['search_period_days'] ?? 0) as int,
      bestDays: (json['best_days'] as List?)
          ?.map((d) => BestDay.fromJson(d as Map<String, dynamic>))
          .toList() ?? [],
      totalFound: (json['total_found'] ?? 0) as int,
    );
  }

  Map<String, dynamic> toJson() => {
    'activity': activity,
    'search_period_days': searchPeriodDays,
    'best_days': bestDays.map((d) => d.toJson()).toList(),
    'total_found': totalFound,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// مثل زراعي - Proverb
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class Proverb {
  final String proverb;
  final String meaning;
  final String application;
  final String? mansion;

  const Proverb({
    required this.proverb,
    required this.meaning,
    required this.application,
    this.mansion,
  });

  factory Proverb.fromJson(Map<String, dynamic> json) {
    return Proverb(
      proverb: (json['proverb'] ?? '') as String,
      meaning: (json['meaning'] ?? '') as String,
      application: (json['application'] ?? '') as String,
      mansion: json['mansion'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'proverb': proverb,
    'meaning': meaning,
    'application': application,
    'mansion': mansion,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// مثل اليوم مع السياق - Proverb of the Day
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class ProverbOfTheDay {
  final String date;
  final Proverb proverbOfTheDay;
  final String currentMansion;
  final String currentMoonPhase;
  final String currentSeason;
  final List<Proverb> seasonProverbs;
  final String context;

  const ProverbOfTheDay({
    required this.date,
    required this.proverbOfTheDay,
    required this.currentMansion,
    required this.currentMoonPhase,
    required this.currentSeason,
    required this.seasonProverbs,
    required this.context,
  });

  factory ProverbOfTheDay.fromJson(Map<String, dynamic> json) {
    return ProverbOfTheDay(
      date: (json['date'] ?? '') as String,
      proverbOfTheDay: Proverb.fromJson(json['proverb_of_the_day'] as Map<String, dynamic>? ?? {}),
      currentMansion: (json['current_mansion'] ?? '') as String,
      currentMoonPhase: (json['current_moon_phase'] ?? '') as String,
      currentSeason: (json['current_season'] ?? '') as String,
      seasonProverbs: (json['season_proverbs'] as List?)
          ?.map((p) => Proverb.fromJson(p as Map<String, dynamic>))
          .toList() ?? [],
      context: (json['context'] ?? '') as String,
    );
  }

  Map<String, dynamic> toJson() => {
    'date': date,
    'proverb_of_the_day': proverbOfTheDay.toJson(),
    'current_mansion': currentMansion,
    'current_moon_phase': currentMoonPhase,
    'current_season': currentSeason,
    'season_proverbs': seasonProverbs.map((p) => p.toJson()).toList(),
    'context': context,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// جميع الأمثال - All Proverbs
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class AllProverbs {
  final List<Proverb> general;
  final Map<String, List<Proverb>> byCrop;
  final Map<String, List<Proverb>> bySeason;
  final int totalProverbs;

  const AllProverbs({
    required this.general,
    required this.byCrop,
    required this.bySeason,
    required this.totalProverbs,
  });

  factory AllProverbs.fromJson(Map<String, dynamic> json) {
    return AllProverbs(
      general: (json['general'] as List?)
          ?.map((p) => Proverb.fromJson(p as Map<String, dynamic>))
          .toList() ?? [],
      byCrop: (json['by_crop'] as Map<String, dynamic>?)?.map(
        (key, value) => MapEntry(key,
          (value as List? ?? []).map((p) => Proverb.fromJson(p as Map<String, dynamic>)).toList()),
      ) ?? {},
      bySeason: (json['by_season'] as Map<String, dynamic>?)?.map(
        (key, value) => MapEntry(key,
          (value as List? ?? []).map((p) => Proverb.fromJson(p as Map<String, dynamic>)).toList()),
      ) ?? {},
      totalProverbs: (json['total_proverbs'] ?? 0) as int,
    );
  }

  Map<String, dynamic> toJson() => {
    'general': general.map((p) => p.toJson()).toList(),
    'by_crop': byCrop.map((k, v) => MapEntry(k, v.map((p) => p.toJson()).toList())),
    'by_season': bySeason.map((k, v) => MapEntry(k, v.map((p) => p.toJson()).toList())),
    'total_proverbs': totalProverbs,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// الحكمة اليومية - Daily Wisdom
// ═══════════════════════════════════════════════════════════════════════════════

@immutable
class DailyWisdomProverb {
  final String text;
  final String meaning;
  final String application;

  const DailyWisdomProverb({
    required this.text,
    required this.meaning,
    required this.application,
  });

  factory DailyWisdomProverb.fromJson(Map<String, dynamic> json) {
    return DailyWisdomProverb(
      text: (json['text'] ?? '') as String,
      meaning: (json['meaning'] ?? '') as String,
      application: (json['application'] ?? '') as String,
    );
  }

  Map<String, dynamic> toJson() => {
    'text': text,
    'meaning': meaning,
    'application': application,
  };
}

@immutable
class DailyWisdomMansion {
  final String name;
  final String description;
  final List<String> tips;

  const DailyWisdomMansion({
    required this.name,
    required this.description,
    required this.tips,
  });

  factory DailyWisdomMansion.fromJson(Map<String, dynamic> json) {
    return DailyWisdomMansion(
      name: (json['name'] ?? '') as String,
      description: (json['description'] ?? '') as String,
      tips: (json['tips'] as List?)?.cast<String>() ?? [],
    );
  }

  Map<String, dynamic> toJson() => {
    'name': name,
    'description': description,
    'tips': tips,
  };
}

@immutable
class DailyWisdomMoonPhase {
  final String name;
  final String icon;
  final String illumination;
  final List<String> tips;

  const DailyWisdomMoonPhase({
    required this.name,
    required this.icon,
    required this.illumination,
    required this.tips,
  });

  factory DailyWisdomMoonPhase.fromJson(Map<String, dynamic> json) {
    return DailyWisdomMoonPhase(
      name: (json['name'] ?? '') as String,
      icon: (json['icon'] ?? '') as String,
      illumination: (json['illumination'] ?? '') as String,
      tips: (json['tips'] as List?)?.cast<String>() ?? [],
    );
  }

  Map<String, dynamic> toJson() => {
    'name': name,
    'icon': icon,
    'illumination': illumination,
    'tips': tips,
  };
}

@immutable
class DailyWisdomSeason {
  final String name;
  final List<String> crops;
  final List<String> activities;

  const DailyWisdomSeason({
    required this.name,
    required this.crops,
    required this.activities,
  });

  factory DailyWisdomSeason.fromJson(Map<String, dynamic> json) {
    return DailyWisdomSeason(
      name: (json['name'] ?? '') as String,
      crops: (json['crops'] as List?)?.cast<String>() ?? [],
      activities: (json['activities'] as List?)?.cast<String>() ?? [],
    );
  }

  Map<String, dynamic> toJson() => {
    'name': name,
    'crops': crops,
    'activities': activities,
  };
}

@immutable
class DailyWisdom {
  final String date;
  final String? hijriDate;
  final DailyWisdomProverb proverbOfTheDay;
  final DailyWisdomMansion currentMansion;
  final DailyWisdomMoonPhase moonPhase;
  final dynamic currentStar;
  final DailyWisdomSeason season;
  final int overallScore;
  final String summary;

  const DailyWisdom({
    required this.date,
    this.hijriDate,
    required this.proverbOfTheDay,
    required this.currentMansion,
    required this.moonPhase,
    this.currentStar,
    required this.season,
    required this.overallScore,
    required this.summary,
  });

  factory DailyWisdom.fromJson(Map<String, dynamic> json) {
    return DailyWisdom(
      date: (json['date'] ?? '') as String,
      hijriDate: json['hijri_date'] as String?,
      proverbOfTheDay: DailyWisdomProverb.fromJson(json['proverb_of_the_day'] as Map<String, dynamic>? ?? {}),
      currentMansion: DailyWisdomMansion.fromJson(json['current_mansion'] as Map<String, dynamic>? ?? {}),
      moonPhase: DailyWisdomMoonPhase.fromJson(json['moon_phase'] as Map<String, dynamic>? ?? {}),
      currentStar: json['current_star'],
      season: DailyWisdomSeason.fromJson(json['season'] as Map<String, dynamic>? ?? {}),
      overallScore: (json['overall_score'] ?? 0) as int,
      summary: (json['summary'] ?? '') as String,
    );
  }

  Map<String, dynamic> toJson() => {
    'date': date,
    'hijri_date': hijriDate,
    'proverb_of_the_day': proverbOfTheDay.toJson(),
    'current_mansion': currentMansion.toJson(),
    'moon_phase': moonPhase.toJson(),
    'current_star': currentStar,
    'season': season.toJson(),
    'overall_score': overallScore,
    'summary': summary,
  };
}
