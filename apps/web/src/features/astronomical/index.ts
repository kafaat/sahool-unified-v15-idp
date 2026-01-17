/**
 * SAHOOL Astronomical Calendar Feature Exports
 * صادرات ميزة التقويم الفلكي
 */

// ═══════════════════════════════════════════════════════════════════════════════
// تصدير الخطافات - Export Hooks
// ═══════════════════════════════════════════════════════════════════════════════

export {
  useToday,
  useWeeklyForecast,
  useMoonPhase,
  useLunarMansion,
  useCropCalendar,
  useBestDays,
  useProverbs,
  useProverbOfTheDay,
  useWisdomToday,
} from "./hooks/useAstronomical";

// ═══════════════════════════════════════════════════════════════════════════════
// تصدير الأنواع - Export Types
// ═══════════════════════════════════════════════════════════════════════════════

export type {
  MoonPhase,
  LunarMansion,
  HijriDate,
  ZodiacInfo,
  SeasonInfo,
  FarmingRecommendation,
  DailyAstronomicalData,
  WeeklyForecast,
  CropCalendar,
  BestDay,
  BestDaysResult,
  Proverb,
  ProverbOfTheDay,
  AllProverbs,
  DailyWisdom,
} from "./types";

// ═══════════════════════════════════════════════════════════════════════════════
// تصدير دوال واجهة برمجة التطبيقات - Export API Functions
// ═══════════════════════════════════════════════════════════════════════════════

export {
  getToday,
  getDate,
  getWeeklyForecast,
  getMoonPhase,
  getLunarMansion,
  getHijriDate,
  getCropCalendar,
  getBestDays,
  getProverbs,
  getProverbOfTheDay,
  getWisdomToday,
} from "./api";
