/// SAHOOL Astronomical Calendar Domain Entities
/// نماذج التقويم الفلكي الزراعي

import 'package:flutter/material.dart';

/// مرحلة القمر
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
      phaseKey: json['phase_key'] as String,
      name: json['name'] as String,
      nameEn: json['name_en'] as String,
      icon: json['icon'] as String,
      illumination: (json['illumination'] as num).toDouble(),
      ageDays: (json['age_days'] as num).toDouble(),
      isWaxing: json['is_waxing'] as bool,
      farmingGood: json['farming_good'] as bool,
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

  Color get statusColor => farmingGood ? Colors.green : Colors.orange;
  String get statusText => farmingGood ? 'مناسب للزراعة' : 'غير مثالي للزراعة';
}

/// المنزلة القمرية
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
      number: json['number'] as int,
      name: json['name'] as String,
      nameEn: json['name_en'] as String,
      constellation: json['constellation'] as String,
      constellationEn: json['constellation_en'] as String,
      element: json['element'] as String,
      farming: json['farming'] as String,
      farmingScore: json['farming_score'] as int,
      crops: List<String>.from(json['crops'] ?? []),
      activities: List<String>.from(json['activities'] ?? []),
      avoid: List<String>.from(json['avoid'] ?? []),
      description: json['description'] as String,
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

  Color get scoreColor {
    if (farmingScore >= 8) return Colors.green;
    if (farmingScore >= 6) return Colors.lightGreen;
    if (farmingScore >= 4) return Colors.orange;
    return Colors.red;
  }

  String get elementIcon {
    switch (element) {
      case 'نار':
        return '🔥';
      case 'أرض':
        return '🌍';
      case 'هواء':
        return '💨';
      case 'ماء':
        return '💧';
      default:
        return '⭐';
    }
  }
}

/// التاريخ الهجري
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
      year: json['year'] as int,
      month: json['month'] as int,
      day: json['day'] as int,
      monthName: json['month_name'] as String,
      monthNameEn: json['month_name_en'] as String,
      weekday: json['weekday'] as String,
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

  String get formatted => '$day $monthName $year هـ';
  String get formattedShort => '$day/$month/$year';
}

/// معلومات البرج
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
      name: json['name'] as String,
      nameEn: json['name_en'] as String,
      element: json['element'] as String,
      fertility: json['fertility'] as String,
      score: json['score'] as int,
    );
  }

  Map<String, dynamic> toJson() => {
        'name': name,
        'name_en': nameEn,
        'element': element,
        'fertility': fertility,
        'score': score,
      };

  String get zodiacIcon {
    switch (nameEn.toLowerCase()) {
      case 'aries':
        return '♈';
      case 'taurus':
        return '♉';
      case 'gemini':
        return '♊';
      case 'cancer':
        return '♋';
      case 'leo':
        return '♌';
      case 'virgo':
        return '♍';
      case 'libra':
        return '♎';
      case 'scorpio':
        return '♏';
      case 'sagittarius':
        return '♐';
      case 'capricorn':
        return '♑';
      case 'aquarius':
        return '♒';
      case 'pisces':
        return '♓';
      default:
        return '⭐';
    }
  }
}

/// معلومات الموسم
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
      name: json['name'] as String,
      nameEn: json['name_en'] as String,
      description: json['description'] as String,
      mainCrops: List<String>.from(json['main_crops'] ?? []),
      activities: List<String>.from(json['activities'] ?? []),
    );
  }

  Map<String, dynamic> toJson() => {
        'name': name,
        'name_en': nameEn,
        'description': description,
        'main_crops': mainCrops,
        'activities': activities,
      };

  String get seasonIcon {
    switch (nameEn.toLowerCase()) {
      case 'sayf (summer)':
        return '☀️';
      case 'kharif (autumn)':
        return '🍂';
      case 'shita (winter)':
        return '❄️';
      case 'rabi (spring)':
        return '🌸';
      default:
        return '🌿';
    }
  }
}

/// توصية زراعية
class FarmingRecommendation {
  final String activity;
  final String suitability;
  final int suitabilityScore;
  final String reason;
  final String? bestTime;
  final String? weatherNote;

  const FarmingRecommendation({
    required this.activity,
    required this.suitability,
    required this.suitabilityScore,
    required this.reason,
    this.bestTime,
    this.weatherNote,
  });

  factory FarmingRecommendation.fromJson(Map<String, dynamic> json) {
    return FarmingRecommendation(
      activity: json['activity'] as String,
      suitability: json['suitability'] as String,
      suitabilityScore: json['suitability_score'] as int,
      reason: json['reason'] as String,
      bestTime: json['best_time'] as String?,
      weatherNote: json['weather_note'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'activity': activity,
        'suitability': suitability,
        'suitability_score': suitabilityScore,
        'reason': reason,
        'best_time': bestTime,
        'weather_note': weatherNote,
      };

  Color get suitabilityColor {
    if (suitabilityScore >= 8) return Colors.green;
    if (suitabilityScore >= 6) return Colors.lightGreen;
    if (suitabilityScore >= 4) return Colors.orange;
    return Colors.red;
  }

  String get activityIcon {
    switch (activity) {
      case 'زراعة':
        return '🌱';
      case 'ري':
        return '💧';
      case 'حصاد':
        return '🌾';
      case 'تقليم':
        return '✂️';
      case 'غرس':
        return '🌳';
      case 'تسميد':
        return '🧪';
      default:
        return '🌿';
    }
  }
}

/// البيانات الفلكية اليومية
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
      dateGregorian: json['date_gregorian'] as String,
      dateHijri: HijriDate.fromJson(json['date_hijri']),
      moonPhase: MoonPhase.fromJson(json['moon_phase']),
      lunarMansion: LunarMansion.fromJson(json['lunar_mansion']),
      zodiac: ZodiacInfo.fromJson(json['zodiac']),
      season: SeasonInfo.fromJson(json['season']),
      overallFarmingScore: json['overall_farming_score'] as int,
      recommendations: (json['recommendations'] as List)
          .map((r) => FarmingRecommendation.fromJson(r))
          .toList(),
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

  Color get overallScoreColor {
    if (overallFarmingScore >= 8) return Colors.green;
    if (overallFarmingScore >= 6) return Colors.lightGreen;
    if (overallFarmingScore >= 4) return Colors.orange;
    return Colors.red;
  }

  String get overallScoreLabel {
    if (overallFarmingScore >= 8) return 'ممتاز';
    if (overallFarmingScore >= 6) return 'جيد';
    if (overallFarmingScore >= 4) return 'متوسط';
    return 'ضعيف';
  }
}

/// التوقعات الأسبوعية
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
      startDate: json['start_date'] as String,
      endDate: json['end_date'] as String,
      days: (json['days'] as List)
          .map((d) => DailyAstronomicalData.fromJson(d))
          .toList(),
      bestPlantingDays: List<String>.from(json['best_planting_days'] ?? []),
      bestHarvestingDays: List<String>.from(json['best_harvesting_days'] ?? []),
      avoidDays: List<String>.from(json['avoid_days'] ?? []),
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

/// تقويم المحصول
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
      cropName: json['crop_name'] as String,
      cropNameEn: json['crop_name_en'] as String,
      bestPlantingMansions: List<int>.from(json['best_planting_mansions'] ?? []),
      bestMoonPhases: List<String>.from(json['best_moon_phases'] ?? []),
      bestZodiacSigns: List<String>.from(json['best_zodiac_signs'] ?? []),
      optimalMonths: List<int>.from(json['optimal_months'] ?? []),
      plantingGuide: json['planting_guide'] as String,
      currentSuitability: json['current_suitability'] as int,
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

  Color get suitabilityColor {
    if (currentSuitability >= 8) return Colors.green;
    if (currentSuitability >= 6) return Colors.lightGreen;
    if (currentSuitability >= 4) return Colors.orange;
    return Colors.red;
  }
}

/// أفضل الأيام للنشاط
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
      date: json['date'] as String,
      hijriDate: json['hijri_date'] as String,
      moonPhase: json['moon_phase'] as String,
      lunarMansion: json['lunar_mansion'] as String,
      score: json['score'] as int,
      reason: json['reason'] as String,
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

/// نتيجة البحث عن أفضل الأيام
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
      activity: json['activity'] as String,
      searchPeriodDays: json['search_period_days'] as int,
      bestDays: (json['best_days'] as List)
          .map((d) => BestDay.fromJson(d))
          .toList(),
      totalFound: json['total_found'] as int,
    );
  }

  Map<String, dynamic> toJson() => {
        'activity': activity,
        'search_period_days': searchPeriodDays,
        'best_days': bestDays.map((d) => d.toJson()).toList(),
        'total_found': totalFound,
      };
}
