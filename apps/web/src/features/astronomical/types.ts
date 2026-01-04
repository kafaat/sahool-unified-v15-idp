/**
 * SAHOOL Astronomical Calendar Feature Types
 * أنواع ميزة التقويم الفلكي
 */

// ═══════════════════════════════════════════════════════════════════════════════
// مرحلة القمر - Moon Phase
// ═══════════════════════════════════════════════════════════════════════════════

export interface MoonPhase {
  phase_key: string;
  name: string;
  name_en: string;
  icon: string;
  illumination: number;
  age_days: number;
  is_waxing: boolean;
  farming_good: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// المنزلة القمرية - Lunar Mansion
// ═══════════════════════════════════════════════════════════════════════════════

export interface LunarMansion {
  number: number;
  name: string;
  name_en: string;
  constellation: string;
  constellation_en: string;
  element: string;
  farming: string;
  farming_score: number;
  crops: string[];
  activities: string[];
  avoid: string[];
  description: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// التاريخ الهجري - Hijri Date
// ═══════════════════════════════════════════════════════════════════════════════

export interface HijriDate {
  year: number;
  month: number;
  day: number;
  month_name: string;
  month_name_en: string;
  weekday: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// معلومات البرج - Zodiac Info
// ═══════════════════════════════════════════════════════════════════════════════

export interface ZodiacInfo {
  name: string;
  name_en: string;
  element: string;
  fertility: string;
  score: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// معلومات الموسم - Season Info
// ═══════════════════════════════════════════════════════════════════════════════

export interface SeasonInfo {
  name: string;
  name_en: string;
  description: string;
  main_crops: string[];
  activities: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// توصية زراعية - Farming Recommendation
// ═══════════════════════════════════════════════════════════════════════════════

export interface FarmingRecommendation {
  activity: string;
  suitability: string;
  suitability_score: number;
  reason: string;
  best_time?: string | null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// البيانات الفلكية اليومية - Daily Astronomical Data
// ═══════════════════════════════════════════════════════════════════════════════

export interface DailyAstronomicalData {
  date_gregorian: string;
  date_hijri: HijriDate;
  moon_phase: MoonPhase;
  lunar_mansion: LunarMansion;
  zodiac: ZodiacInfo;
  season: SeasonInfo;
  overall_farming_score: number;
  recommendations: FarmingRecommendation[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// التوقعات الأسبوعية - Weekly Forecast
// ═══════════════════════════════════════════════════════════════════════════════

export interface WeeklyForecast {
  start_date: string;
  end_date: string;
  days: DailyAstronomicalData[];
  best_planting_days: string[];
  best_harvesting_days: string[];
  avoid_days: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// تقويم المحصول - Crop Calendar
// ═══════════════════════════════════════════════════════════════════════════════

export interface CropCalendar {
  crop_name: string;
  crop_name_en: string;
  best_planting_mansions: number[];
  best_moon_phases: string[];
  best_zodiac_signs: string[];
  optimal_months: number[];
  planting_guide: string;
  current_suitability: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// أفضل يوم - Best Day
// ═══════════════════════════════════════════════════════════════════════════════

export interface BestDay {
  date: string;
  hijri_date: string;
  moon_phase: string;
  lunar_mansion: string;
  score: number;
  reason: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// نتيجة البحث عن أفضل الأيام - Best Days Result
// ═══════════════════════════════════════════════════════════════════════════════

export interface BestDaysResult {
  activity: string;
  search_period_days: number;
  best_days: BestDay[];
  total_found: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// مثل اليوم - Proverb
// ═══════════════════════════════════════════════════════════════════════════════

export interface Proverb {
  proverb: string;
  meaning: string;
  application: string;
  mansion?: string | null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// مثل اليوم مع السياق - Proverb of the Day
// ═══════════════════════════════════════════════════════════════════════════════

export interface ProverbOfTheDay {
  date: string;
  proverb_of_the_day: Proverb;
  current_mansion: string;
  current_moon_phase: string;
  current_season: string;
  season_proverbs: Proverb[];
  context: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// جميع الأمثال - All Proverbs
// ═══════════════════════════════════════════════════════════════════════════════

export interface AllProverbs {
  general: Proverb[];
  by_crop: Record<string, Proverb[]>;
  by_season: Record<string, Proverb[]>;
  total_proverbs: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// الحكمة اليومية - Daily Wisdom
// ═══════════════════════════════════════════════════════════════════════════════

export interface DailyWisdom {
  date: string;
  hijri_date?: string;
  proverb_of_the_day: {
    text: string;
    meaning: string;
    application: string;
  };
  current_mansion: {
    name: string;
    description: string;
    tips: string[];
  };
  moon_phase: {
    name: string;
    icon: string;
    illumination: string;
    tips: string[];
  };
  current_star?: any;
  season: {
    name: string;
    crops: string[];
    activities: string[];
  };
  overall_score: number;
  summary: string;
}
