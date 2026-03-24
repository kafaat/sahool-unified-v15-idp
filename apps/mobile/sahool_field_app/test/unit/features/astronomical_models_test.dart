import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/astronomical/models/astronomical_models.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // MoonPhase
  // ═══════════════════════════════════════════════════════════════════════════

  group('MoonPhase', () {
    final moonPhaseJson = <String, dynamic>{
      'phase_key': 'waxing_crescent',
      'name': 'هلال متزايد',
      'name_en': 'Waxing Crescent',
      'icon': '🌒',
      'illumination': 25.5,
      'age_days': 3.5,
      'is_waxing': true,
      'farming_good': true,
    };

    test('fromJson creates MoonPhase with all fields', () {
      final phase = MoonPhase.fromJson(moonPhaseJson);
      expect(phase.phaseKey, 'waxing_crescent');
      expect(phase.name, 'هلال متزايد');
      expect(phase.nameEn, 'Waxing Crescent');
      expect(phase.icon, '🌒');
      expect(phase.illumination, 25.5);
      expect(phase.ageDays, 3.5);
      expect(phase.isWaxing, true);
      expect(phase.farmingGood, true);
    });

    test('toJson produces correct snake_case keys', () {
      final phase = MoonPhase.fromJson(moonPhaseJson);
      final json = phase.toJson();
      expect(json['phase_key'], 'waxing_crescent');
      expect(json['name_en'], 'Waxing Crescent');
      expect(json['age_days'], 3.5);
      expect(json['is_waxing'], true);
      expect(json['farming_good'], true);
    });

    test('fromJson/toJson round-trip preserves data', () {
      final phase = MoonPhase.fromJson(moonPhaseJson);
      final json = phase.toJson();
      final restored = MoonPhase.fromJson(json);
      expect(restored.phaseKey, phase.phaseKey);
      expect(restored.illumination, phase.illumination);
      expect(restored.ageDays, phase.ageDays);
    });

    test('copyWith changes specified field', () {
      final phase = MoonPhase.fromJson(moonPhaseJson);
      final copied = phase.copyWith(illumination: 50.0);
      expect(copied.illumination, 50.0);
      expect(copied.phaseKey, phase.phaseKey);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // LunarMansion
  // ═══════════════════════════════════════════════════════════════════════════

  group('LunarMansion', () {
    final mansionJson = <String, dynamic>{
      'number': 1,
      'name': 'الشرطين',
      'name_en': 'Al-Sharatain',
      'constellation': 'الحمل',
      'constellation_en': 'Aries',
      'element': 'نار',
      'farming': 'مناسب للزراعة',
      'farming_score': 8,
      'crops': ['قمح', 'شعير'],
      'activities': ['زراعة', 'حرث'],
      'avoid': ['قطع الأشجار'],
      'description': 'أول المنازل القمرية',
    };

    test('fromJson creates LunarMansion with all fields', () {
      final mansion = LunarMansion.fromJson(mansionJson);
      expect(mansion.number, 1);
      expect(mansion.name, 'الشرطين');
      expect(mansion.nameEn, 'Al-Sharatain');
      expect(mansion.constellation, 'الحمل');
      expect(mansion.constellationEn, 'Aries');
      expect(mansion.element, 'نار');
      expect(mansion.farming, 'مناسب للزراعة');
      expect(mansion.farmingScore, 8);
      expect(mansion.crops, ['قمح', 'شعير']);
      expect(mansion.activities, ['زراعة', 'حرث']);
      expect(mansion.avoid, ['قطع الأشجار']);
      expect(mansion.description, 'أول المنازل القمرية');
    });

    test('toJson produces correct map with snake_case keys', () {
      final mansion = LunarMansion.fromJson(mansionJson);
      final json = mansion.toJson();
      expect(json['name_en'], 'Al-Sharatain');
      expect(json['constellation_en'], 'Aries');
      expect(json['farming_score'], 8);
    });

    test('round-trip preserves list fields', () {
      final mansion = LunarMansion.fromJson(mansionJson);
      final restored = LunarMansion.fromJson(mansion.toJson());
      expect(restored.crops, mansion.crops);
      expect(restored.activities, mansion.activities);
      expect(restored.avoid, mansion.avoid);
    });

    test('copyWith changes number', () {
      final mansion = LunarMansion.fromJson(mansionJson);
      final copied = mansion.copyWith(number: 5);
      expect(copied.number, 5);
      expect(copied.name, mansion.name);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // HijriDate
  // ═══════════════════════════════════════════════════════════════════════════

  group('HijriDate', () {
    final hijriJson = <String, dynamic>{
      'year': 1447,
      'month': 7,
      'day': 15,
      'month_name': 'رجب',
      'month_name_en': 'Rajab',
      'weekday': 'الإثنين',
    };

    test('fromJson creates HijriDate with all fields', () {
      final date = HijriDate.fromJson(hijriJson);
      expect(date.year, 1447);
      expect(date.month, 7);
      expect(date.day, 15);
      expect(date.monthName, 'رجب');
      expect(date.monthNameEn, 'Rajab');
      expect(date.weekday, 'الإثنين');
    });

    test('toJson produces correct map', () {
      final date = HijriDate.fromJson(hijriJson);
      final json = date.toJson();
      expect(json['month_name'], 'رجب');
      expect(json['month_name_en'], 'Rajab');
      expect(json['year'], 1447);
    });

    test('round-trip preserves all fields', () {
      final date = HijriDate.fromJson(hijriJson);
      final restored = HijriDate.fromJson(date.toJson());
      expect(restored.year, date.year);
      expect(restored.month, date.month);
      expect(restored.day, date.day);
      expect(restored.monthName, date.monthName);
      expect(restored.weekday, date.weekday);
    });

    test('copyWith changes year', () {
      final date = HijriDate.fromJson(hijriJson);
      final copied = date.copyWith(year: 1448);
      expect(copied.year, 1448);
      expect(copied.month, date.month);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ZodiacInfo
  // ═══════════════════════════════════════════════════════════════════════════

  group('ZodiacInfo', () {
    final zodiacJson = <String, dynamic>{
      'name': 'الحمل',
      'name_en': 'Aries',
      'element': 'نار',
      'fertility': 'جاف',
      'score': 6,
    };

    test('fromJson creates ZodiacInfo with all fields', () {
      final zodiac = ZodiacInfo.fromJson(zodiacJson);
      expect(zodiac.name, 'الحمل');
      expect(zodiac.nameEn, 'Aries');
      expect(zodiac.element, 'نار');
      expect(zodiac.fertility, 'جاف');
      expect(zodiac.score, 6);
    });

    test('toJson produces correct map', () {
      final zodiac = ZodiacInfo.fromJson(zodiacJson);
      final json = zodiac.toJson();
      expect(json['name_en'], 'Aries');
      expect(json['score'], 6);
    });

    test('round-trip preserves all fields', () {
      final zodiac = ZodiacInfo.fromJson(zodiacJson);
      final restored = ZodiacInfo.fromJson(zodiac.toJson());
      expect(restored.name, zodiac.name);
      expect(restored.fertility, zodiac.fertility);
      expect(restored.score, zodiac.score);
    });

    test('copyWith changes score', () {
      final zodiac = ZodiacInfo.fromJson(zodiacJson);
      final copied = zodiac.copyWith(score: 9);
      expect(copied.score, 9);
      expect(copied.name, zodiac.name);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SeasonInfo
  // ═══════════════════════════════════════════════════════════════════════════

  group('SeasonInfo', () {
    final seasonJson = <String, dynamic>{
      'name': 'الشتاء',
      'name_en': 'Winter',
      'description': 'موسم الشتاء',
      'main_crops': ['قمح', 'شعير', 'فول'],
      'activities': ['زراعة', 'تسميد'],
    };

    test('fromJson creates SeasonInfo with all fields', () {
      final season = SeasonInfo.fromJson(seasonJson);
      expect(season.name, 'الشتاء');
      expect(season.nameEn, 'Winter');
      expect(season.description, 'موسم الشتاء');
      expect(season.mainCrops, ['قمح', 'شعير', 'فول']);
      expect(season.activities, ['زراعة', 'تسميد']);
    });

    test('toJson produces correct map', () {
      final season = SeasonInfo.fromJson(seasonJson);
      final json = season.toJson();
      expect(json['name_en'], 'Winter');
      expect(json['main_crops'], ['قمح', 'شعير', 'فول']);
    });

    test('round-trip preserves list fields', () {
      final season = SeasonInfo.fromJson(seasonJson);
      final restored = SeasonInfo.fromJson(season.toJson());
      expect(restored.mainCrops, season.mainCrops);
      expect(restored.activities, season.activities);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FarmingRecommendation
  // ═══════════════════════════════════════════════════════════════════════════

  group('FarmingRecommendation', () {
    final recJson = <String, dynamic>{
      'activity': 'زراعة',
      'suitability': 'مناسب',
      'suitability_score': 8,
      'reason': 'القمر في طور مناسب',
      'best_time': 'الصباح الباكر',
    };

    test('fromJson creates FarmingRecommendation with all fields', () {
      final rec = FarmingRecommendation.fromJson(recJson);
      expect(rec.activity, 'زراعة');
      expect(rec.suitability, 'مناسب');
      expect(rec.suitabilityScore, 8);
      expect(rec.reason, 'القمر في طور مناسب');
      expect(rec.bestTime, 'الصباح الباكر');
    });

    test('fromJson handles null bestTime', () {
      final json = Map<String, dynamic>.from(recJson);
      json['best_time'] = null;
      final rec = FarmingRecommendation.fromJson(json);
      expect(rec.bestTime, isNull);
    });

    test('toJson produces correct map', () {
      final rec = FarmingRecommendation.fromJson(recJson);
      final json = rec.toJson();
      expect(json['suitability_score'], 8);
      expect(json['best_time'], 'الصباح الباكر');
    });

    test('round-trip preserves all fields', () {
      final rec = FarmingRecommendation.fromJson(recJson);
      final restored = FarmingRecommendation.fromJson(rec.toJson());
      expect(restored.activity, rec.activity);
      expect(restored.suitabilityScore, rec.suitabilityScore);
      expect(restored.bestTime, rec.bestTime);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // DailyAstronomicalData
  // ═══════════════════════════════════════════════════════════════════════════

  group('DailyAstronomicalData', () {
    final dailyJson = <String, dynamic>{
      'date_gregorian': '2026-03-20',
      'date_hijri': {
        'year': 1447,
        'month': 7,
        'day': 15,
        'month_name': 'رجب',
        'month_name_en': 'Rajab',
        'weekday': 'الإثنين',
      },
      'moon_phase': {
        'phase_key': 'full_moon',
        'name': 'بدر',
        'name_en': 'Full Moon',
        'icon': '🌕',
        'illumination': 100.0,
        'age_days': 14.5,
        'is_waxing': false,
        'farming_good': true,
      },
      'lunar_mansion': {
        'number': 5,
        'name': 'الهقعة',
        'name_en': 'Al-Haqah',
        'constellation': 'الجوزاء',
        'constellation_en': 'Gemini',
        'element': 'هواء',
        'farming': 'جيد',
        'farming_score': 7,
        'crops': ['ذرة'],
        'activities': ['زراعة'],
        'avoid': [],
        'description': 'منزلة مباركة',
      },
      'zodiac': {
        'name': 'الحوت',
        'name_en': 'Pisces',
        'element': 'ماء',
        'fertility': 'خصب',
        'score': 9,
      },
      'season': {
        'name': 'الربيع',
        'name_en': 'Spring',
        'description': 'موسم الربيع',
        'main_crops': ['قمح'],
        'activities': ['حصاد'],
      },
      'overall_farming_score': 8,
      'recommendations': [
        {
          'activity': 'زراعة',
          'suitability': 'ممتاز',
          'suitability_score': 9,
          'reason': 'القمر بدر والمنزلة مناسبة',
          'best_time': 'الصباح',
        },
      ],
    };

    test('fromJson creates DailyAstronomicalData with nested objects', () {
      final data = DailyAstronomicalData.fromJson(dailyJson);
      expect(data.dateGregorian, '2026-03-20');
      expect(data.dateHijri.year, 1447);
      expect(data.moonPhase.phaseKey, 'full_moon');
      expect(data.lunarMansion.number, 5);
      expect(data.zodiac.nameEn, 'Pisces');
      expect(data.season.nameEn, 'Spring');
      expect(data.overallFarmingScore, 8);
      expect(data.recommendations.length, 1);
    });

    test('fromJson parses nested moonPhase correctly', () {
      final data = DailyAstronomicalData.fromJson(dailyJson);
      expect(data.moonPhase.illumination, 100.0);
      expect(data.moonPhase.isWaxing, false);
    });

    test('fromJson parses nested lunarMansion correctly', () {
      final data = DailyAstronomicalData.fromJson(dailyJson);
      expect(data.lunarMansion.constellationEn, 'Gemini');
      expect(data.lunarMansion.crops, ['ذرة']);
    });

    test('fromJson parses nested recommendations correctly', () {
      final data = DailyAstronomicalData.fromJson(dailyJson);
      expect(data.recommendations.first.suitabilityScore, 9);
    });

    test('toJson round-trip preserves nested data', () {
      final data = DailyAstronomicalData.fromJson(dailyJson);
      final json = data.toJson();
      final restored = DailyAstronomicalData.fromJson(json);
      expect(restored.dateGregorian, data.dateGregorian);
      expect(restored.overallFarmingScore, data.overallFarmingScore);
      expect(restored.moonPhase.phaseKey, data.moonPhase.phaseKey);
      expect(restored.lunarMansion.number, data.lunarMansion.number);
      expect(restored.zodiac.score, data.zodiac.score);
    });

    test('toJson includes date_gregorian key', () {
      final data = DailyAstronomicalData.fromJson(dailyJson);
      final json = data.toJson();
      expect(json['date_gregorian'], '2026-03-20');
      expect(json['overall_farming_score'], 8);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // WeeklyForecast
  // ═══════════════════════════════════════════════════════════════════════════

  group('WeeklyForecast', () {
    final dailyEntry = <String, dynamic>{
      'date_gregorian': '2026-03-20',
      'date_hijri': {
        'year': 1447, 'month': 7, 'day': 15,
        'month_name': 'رجب', 'month_name_en': 'Rajab', 'weekday': 'الإثنين',
      },
      'moon_phase': {
        'phase_key': 'full_moon', 'name': 'بدر', 'name_en': 'Full Moon',
        'icon': '🌕', 'illumination': 100.0, 'age_days': 14.5,
        'is_waxing': false, 'farming_good': true,
      },
      'lunar_mansion': {
        'number': 5, 'name': 'الهقعة', 'name_en': 'Al-Haqah',
        'constellation': 'الجوزاء', 'constellation_en': 'Gemini',
        'element': 'هواء', 'farming': 'جيد', 'farming_score': 7,
        'crops': ['ذرة'], 'activities': ['زراعة'], 'avoid': [],
        'description': 'منزلة مباركة',
      },
      'zodiac': {
        'name': 'الحوت', 'name_en': 'Pisces', 'element': 'ماء',
        'fertility': 'خصب', 'score': 9,
      },
      'season': {
        'name': 'الربيع', 'name_en': 'Spring', 'description': 'موسم الربيع',
        'main_crops': ['قمح'], 'activities': ['حصاد'],
      },
      'overall_farming_score': 8,
      'recommendations': <Map<String, dynamic>>[],
    };

    final weeklyJson = <String, dynamic>{
      'start_date': '2026-03-20',
      'end_date': '2026-03-26',
      'days': [dailyEntry],
      'best_planting_days': ['2026-03-20', '2026-03-22'],
      'best_harvesting_days': ['2026-03-24'],
      'avoid_days': ['2026-03-21'],
    };

    test('fromJson creates WeeklyForecast with all fields', () {
      final forecast = WeeklyForecast.fromJson(weeklyJson);
      expect(forecast.startDate, '2026-03-20');
      expect(forecast.endDate, '2026-03-26');
      expect(forecast.days.length, 1);
      expect(forecast.bestPlantingDays, ['2026-03-20', '2026-03-22']);
      expect(forecast.bestHarvestingDays, ['2026-03-24']);
      expect(forecast.avoidDays, ['2026-03-21']);
    });

    test('toJson produces correct snake_case keys', () {
      final forecast = WeeklyForecast.fromJson(weeklyJson);
      final json = forecast.toJson();
      expect(json['start_date'], '2026-03-20');
      expect(json['end_date'], '2026-03-26');
      expect(json['best_planting_days'], isList);
      expect(json['best_harvesting_days'], isList);
      expect(json['avoid_days'], isList);
    });

    test('round-trip preserves nested days', () {
      final forecast = WeeklyForecast.fromJson(weeklyJson);
      final restored = WeeklyForecast.fromJson(forecast.toJson());
      expect(restored.days.length, forecast.days.length);
      expect(restored.days.first.dateGregorian, '2026-03-20');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CropCalendar
  // ═══════════════════════════════════════════════════════════════════════════

  group('CropCalendar', () {
    final cropCalJson = <String, dynamic>{
      'crop_name': 'قمح',
      'crop_name_en': 'Wheat',
      'best_planting_mansions': [1, 3, 5],
      'best_moon_phases': ['waxing_crescent', 'first_quarter'],
      'best_zodiac_signs': ['الحوت', 'السرطان'],
      'optimal_months': [10, 11, 12],
      'planting_guide': 'يُزرع القمح في الخريف',
      'current_suitability': 7,
    };

    test('fromJson creates CropCalendar with all fields', () {
      final cal = CropCalendar.fromJson(cropCalJson);
      expect(cal.cropName, 'قمح');
      expect(cal.cropNameEn, 'Wheat');
      expect(cal.bestPlantingMansions, [1, 3, 5]);
      expect(cal.bestMoonPhases, ['waxing_crescent', 'first_quarter']);
      expect(cal.bestZodiacSigns, ['الحوت', 'السرطان']);
      expect(cal.optimalMonths, [10, 11, 12]);
      expect(cal.plantingGuide, 'يُزرع القمح في الخريف');
      expect(cal.currentSuitability, 7);
    });

    test('toJson produces correct map', () {
      final cal = CropCalendar.fromJson(cropCalJson);
      final json = cal.toJson();
      expect(json['crop_name'], 'قمح');
      expect(json['crop_name_en'], 'Wheat');
      expect(json['best_planting_mansions'], [1, 3, 5]);
      expect(json['current_suitability'], 7);
    });

    test('round-trip preserves all list fields', () {
      final cal = CropCalendar.fromJson(cropCalJson);
      final restored = CropCalendar.fromJson(cal.toJson());
      expect(restored.bestPlantingMansions, cal.bestPlantingMansions);
      expect(restored.bestMoonPhases, cal.bestMoonPhases);
      expect(restored.optimalMonths, cal.optimalMonths);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // BestDay
  // ═══════════════════════════════════════════════════════════════════════════

  group('BestDay', () {
    final bestDayJson = <String, dynamic>{
      'date': '2026-03-22',
      'hijri_date': '1447-07-17',
      'moon_phase': 'waning_gibbous',
      'lunar_mansion': 'الذراع',
      'score': 9,
      'reason': 'يوم ممتاز للزراعة',
    };

    test('fromJson creates BestDay with all fields', () {
      final day = BestDay.fromJson(bestDayJson);
      expect(day.date, '2026-03-22');
      expect(day.hijriDate, '1447-07-17');
      expect(day.moonPhase, 'waning_gibbous');
      expect(day.lunarMansion, 'الذراع');
      expect(day.score, 9);
      expect(day.reason, 'يوم ممتاز للزراعة');
    });

    test('toJson produces correct map', () {
      final day = BestDay.fromJson(bestDayJson);
      final json = day.toJson();
      expect(json['hijri_date'], '1447-07-17');
      expect(json['moon_phase'], 'waning_gibbous');
      expect(json['lunar_mansion'], 'الذراع');
    });

    test('round-trip preserves data', () {
      final day = BestDay.fromJson(bestDayJson);
      final restored = BestDay.fromJson(day.toJson());
      expect(restored.date, day.date);
      expect(restored.score, day.score);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // BestDaysResult
  // ═══════════════════════════════════════════════════════════════════════════

  group('BestDaysResult', () {
    final resultJson = <String, dynamic>{
      'activity': 'زراعة',
      'search_period_days': 30,
      'best_days': [
        {
          'date': '2026-03-22',
          'hijri_date': '1447-07-17',
          'moon_phase': 'full_moon',
          'lunar_mansion': 'الذراع',
          'score': 9,
          'reason': 'يوم ممتاز',
        },
      ],
      'total_found': 1,
    };

    test('fromJson creates BestDaysResult with nested BestDay list', () {
      final result = BestDaysResult.fromJson(resultJson);
      expect(result.activity, 'زراعة');
      expect(result.searchPeriodDays, 30);
      expect(result.bestDays.length, 1);
      expect(result.bestDays.first.score, 9);
      expect(result.totalFound, 1);
    });

    test('toJson produces correct map', () {
      final result = BestDaysResult.fromJson(resultJson);
      final json = result.toJson();
      expect(json['search_period_days'], 30);
      expect(json['total_found'], 1);
      expect(json['best_days'], isList);
    });

    test('round-trip preserves nested list', () {
      final result = BestDaysResult.fromJson(resultJson);
      final restored = BestDaysResult.fromJson(result.toJson());
      expect(restored.bestDays.length, result.bestDays.length);
      expect(restored.bestDays.first.date, result.bestDays.first.date);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Proverb
  // ═══════════════════════════════════════════════════════════════════════════

  group('Proverb', () {
    final proverbJson = <String, dynamic>{
      'proverb': 'إذا طلعت الثريا، رفعت العشيا',
      'meaning': 'بداية الحرارة والجفاف',
      'application': 'احرص على الري وتوفير الظل',
      'mansion': 'الثريا',
    };

    test('fromJson creates Proverb with all fields', () {
      final proverb = Proverb.fromJson(proverbJson);
      expect(proverb.proverb, 'إذا طلعت الثريا، رفعت العشيا');
      expect(proverb.meaning, 'بداية الحرارة والجفاف');
      expect(proverb.application, 'احرص على الري وتوفير الظل');
      expect(proverb.mansion, 'الثريا');
    });

    test('fromJson handles null mansion', () {
      final json = Map<String, dynamic>.from(proverbJson);
      json['mansion'] = null;
      final proverb = Proverb.fromJson(json);
      expect(proverb.mansion, isNull);
    });

    test('toJson round-trip preserves data', () {
      final proverb = Proverb.fromJson(proverbJson);
      final restored = Proverb.fromJson(proverb.toJson());
      expect(restored.proverb, proverb.proverb);
      expect(restored.meaning, proverb.meaning);
      expect(restored.mansion, proverb.mansion);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ProverbOfTheDay
  // ═══════════════════════════════════════════════════════════════════════════

  group('ProverbOfTheDay', () {
    final potdJson = <String, dynamic>{
      'date': '2026-03-20',
      'proverb_of_the_day': {
        'proverb': 'مثل اليوم',
        'meaning': 'معنى المثل',
        'application': 'تطبيق المثل',
      },
      'current_mansion': 'الشرطين',
      'current_moon_phase': 'full_moon',
      'current_season': 'الربيع',
      'season_proverbs': [
        {
          'proverb': 'مثل موسمي',
          'meaning': 'معنى',
          'application': 'تطبيق',
        },
      ],
      'context': 'سياق اليوم الفلكي',
    };

    test('fromJson creates ProverbOfTheDay with nested Proverb', () {
      final potd = ProverbOfTheDay.fromJson(potdJson);
      expect(potd.date, '2026-03-20');
      expect(potd.proverbOfTheDay.proverb, 'مثل اليوم');
      expect(potd.currentMansion, 'الشرطين');
      expect(potd.currentMoonPhase, 'full_moon');
      expect(potd.currentSeason, 'الربيع');
      expect(potd.seasonProverbs.length, 1);
      expect(potd.context, 'سياق اليوم الفلكي');
    });

    test('toJson produces correct snake_case keys', () {
      final potd = ProverbOfTheDay.fromJson(potdJson);
      final json = potd.toJson();
      expect(json['proverb_of_the_day'], isMap);
      expect(json['current_mansion'], 'الشرطين');
      expect(json['current_moon_phase'], 'full_moon');
      expect(json['current_season'], 'الربيع');
      expect(json['season_proverbs'], isList);
    });

    test('round-trip preserves nested proverb data', () {
      final potd = ProverbOfTheDay.fromJson(potdJson);
      final restored = ProverbOfTheDay.fromJson(potd.toJson());
      expect(restored.proverbOfTheDay.proverb, potd.proverbOfTheDay.proverb);
      expect(restored.seasonProverbs.length, potd.seasonProverbs.length);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // AllProverbs
  // ═══════════════════════════════════════════════════════════════════════════

  group('AllProverbs', () {
    final allProverbsJson = <String, dynamic>{
      'general': [
        {'proverb': 'مثل عام', 'meaning': 'معنى', 'application': 'تطبيق'},
      ],
      'by_crop': {
        'wheat': [
          {'proverb': 'مثل قمح', 'meaning': 'معنى', 'application': 'تطبيق'},
        ],
      },
      'by_season': {
        'winter': [
          {'proverb': 'مثل شتوي', 'meaning': 'معنى', 'application': 'تطبيق'},
        ],
      },
      'total_proverbs': 3,
    };

    test('fromJson creates AllProverbs with nested maps', () {
      final all = AllProverbs.fromJson(allProverbsJson);
      expect(all.general.length, 1);
      expect(all.general.first.proverb, 'مثل عام');
      expect(all.byCrop.containsKey('wheat'), true);
      expect(all.byCrop['wheat']!.first.proverb, 'مثل قمح');
      expect(all.bySeason.containsKey('winter'), true);
      expect(all.totalProverbs, 3);
    });

    test('toJson produces correct map', () {
      final all = AllProverbs.fromJson(allProverbsJson);
      final json = all.toJson();
      expect(json['total_proverbs'], 3);
      expect(json['by_crop'], isMap);
      expect(json['by_season'], isMap);
    });

    test('round-trip preserves nested map data', () {
      final all = AllProverbs.fromJson(allProverbsJson);
      final restored = AllProverbs.fromJson(all.toJson());
      expect(restored.general.length, all.general.length);
      expect(restored.totalProverbs, all.totalProverbs);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // DailyWisdom and sub-models
  // ═══════════════════════════════════════════════════════════════════════════

  group('DailyWisdomProverb', () {
    final json = <String, dynamic>{
      'text': 'حكمة اليوم',
      'meaning': 'معنى الحكمة',
      'application': 'كيفية التطبيق',
    };

    test('fromJson creates DailyWisdomProverb', () {
      final p = DailyWisdomProverb.fromJson(json);
      expect(p.text, 'حكمة اليوم');
      expect(p.meaning, 'معنى الحكمة');
      expect(p.application, 'كيفية التطبيق');
    });

    test('toJson round-trip preserves data', () {
      final p = DailyWisdomProverb.fromJson(json);
      final restored = DailyWisdomProverb.fromJson(p.toJson());
      expect(restored.text, p.text);
      expect(restored.meaning, p.meaning);
    });
  });

  group('DailyWisdomMansion', () {
    final json = <String, dynamic>{
      'name': 'النطحة',
      'description': 'وصف المنزلة',
      'tips': ['نصيحة 1', 'نصيحة 2'],
    };

    test('fromJson creates DailyWisdomMansion', () {
      final m = DailyWisdomMansion.fromJson(json);
      expect(m.name, 'النطحة');
      expect(m.description, 'وصف المنزلة');
      expect(m.tips, ['نصيحة 1', 'نصيحة 2']);
    });

    test('toJson round-trip preserves data', () {
      final m = DailyWisdomMansion.fromJson(json);
      final restored = DailyWisdomMansion.fromJson(m.toJson());
      expect(restored.tips, m.tips);
    });
  });

  group('DailyWisdomMoonPhase', () {
    final json = <String, dynamic>{
      'name': 'بدر',
      'icon': '🌕',
      'illumination': '100%',
      'tips': ['اسق المحاصيل', 'ازرع البذور'],
    };

    test('fromJson creates DailyWisdomMoonPhase', () {
      final mp = DailyWisdomMoonPhase.fromJson(json);
      expect(mp.name, 'بدر');
      expect(mp.icon, '🌕');
      expect(mp.illumination, '100%');
      expect(mp.tips.length, 2);
    });

    test('toJson round-trip preserves data', () {
      final mp = DailyWisdomMoonPhase.fromJson(json);
      final restored = DailyWisdomMoonPhase.fromJson(mp.toJson());
      expect(restored.tips, mp.tips);
      expect(restored.illumination, mp.illumination);
    });
  });

  group('DailyWisdomSeason', () {
    final json = <String, dynamic>{
      'name': 'الشتاء',
      'crops': ['قمح', 'شعير'],
      'activities': ['تسميد', 'ري'],
    };

    test('fromJson creates DailyWisdomSeason', () {
      final s = DailyWisdomSeason.fromJson(json);
      expect(s.name, 'الشتاء');
      expect(s.crops, ['قمح', 'شعير']);
      expect(s.activities, ['تسميد', 'ري']);
    });

    test('toJson round-trip preserves data', () {
      final s = DailyWisdomSeason.fromJson(json);
      final restored = DailyWisdomSeason.fromJson(s.toJson());
      expect(restored.crops, s.crops);
      expect(restored.activities, s.activities);
    });
  });

  group('DailyWisdom', () {
    final dailyWisdomJson = <String, dynamic>{
      'date': '2026-03-20',
      'hijri_date': '15 رجب 1447',
      'proverb_of_the_day': {
        'text': 'حكمة اليوم',
        'meaning': 'معنى',
        'application': 'تطبيق',
      },
      'current_mansion': {
        'name': 'النطحة',
        'description': 'وصف',
        'tips': ['نصيحة'],
      },
      'moon_phase': {
        'name': 'بدر',
        'icon': '🌕',
        'illumination': '100%',
        'tips': ['نصيحة قمرية'],
      },
      'current_star': null,
      'season': {
        'name': 'الشتاء',
        'crops': ['قمح'],
        'activities': ['زراعة'],
      },
      'overall_score': 8,
      'summary': 'يوم جيد للزراعة',
    };

    test('fromJson creates DailyWisdom with all nested objects', () {
      final w = DailyWisdom.fromJson(dailyWisdomJson);
      expect(w.date, '2026-03-20');
      expect(w.hijriDate, '15 رجب 1447');
      expect(w.proverbOfTheDay.text, 'حكمة اليوم');
      expect(w.currentMansion.name, 'النطحة');
      expect(w.moonPhase.name, 'بدر');
      expect(w.currentStar, isNull);
      expect(w.season.name, 'الشتاء');
      expect(w.overallScore, 8);
      expect(w.summary, 'يوم جيد للزراعة');
    });

    test('fromJson handles null hijriDate', () {
      final json = Map<String, dynamic>.from(dailyWisdomJson);
      json['hijri_date'] = null;
      final w = DailyWisdom.fromJson(json);
      expect(w.hijriDate, isNull);
    });

    test('toJson produces correct snake_case keys', () {
      final w = DailyWisdom.fromJson(dailyWisdomJson);
      final json = w.toJson();
      expect(json['hijri_date'], '15 رجب 1447');
      expect(json['proverb_of_the_day'], isMap);
      expect(json['current_mansion'], isMap);
      expect(json['moon_phase'], isMap);
      expect(json['overall_score'], 8);
    });

    test('round-trip preserves all nested data', () {
      final w = DailyWisdom.fromJson(dailyWisdomJson);
      final restored = DailyWisdom.fromJson(w.toJson());
      expect(restored.date, w.date);
      expect(restored.overallScore, w.overallScore);
      expect(restored.proverbOfTheDay.text, w.proverbOfTheDay.text);
      expect(restored.currentMansion.tips, w.currentMansion.tips);
      expect(restored.moonPhase.icon, w.moonPhase.icon);
      expect(restored.season.crops, w.season.crops);
      expect(restored.summary, w.summary);
    });
  });
}
