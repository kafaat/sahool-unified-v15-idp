/**
 * SAHOOL Astronomical Calendar React Query Hooks
 * خطافات التقويم الفلكي باستخدام React Query
 */

import { useQuery } from "@tanstack/react-query";
import {
  getToday,
  getWeeklyForecast,
  getMoonPhase,
  getLunarMansion,
  getCropCalendar,
  getBestDays,
  getProverbs,
  getProverbOfTheDay,
  getWisdomToday,
} from "../api";

// ═══════════════════════════════════════════════════════════════════════════════
// خيارات الخطافات - Hook Options
// ═══════════════════════════════════════════════════════════════════════════════

interface AstronomicalHookOptions {
  enabled?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// الخطافات الرئيسية - Main Hooks
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * خطاف للحصول على البيانات الفلكية لليوم الحالي
 * Hook to get astronomical data for today
 */
export function useToday(options?: AstronomicalHookOptions) {
  const { enabled = true } = options || {};

  return useQuery({
    queryKey: ["astronomical", "today"],
    queryFn: getToday,
    staleTime: 30 * 60 * 1000, // 30 دقيقة - 30 minutes
    refetchInterval: 60 * 60 * 1000, // ساعة واحدة - 1 hour
    enabled,
    retry: 2,
    retryDelay: 1000,
  });
}

/**
 * خطاف للحصول على التوقعات الأسبوعية
 * Hook to get weekly forecast
 */
export function useWeeklyForecast(
  options?: AstronomicalHookOptions & { startDate?: string },
) {
  const { enabled = true, startDate } = options || {};

  return useQuery({
    queryKey: ["astronomical", "weekly-forecast", startDate],
    queryFn: () => getWeeklyForecast(startDate),
    staleTime: 60 * 60 * 1000, // ساعة واحدة - 1 hour
    enabled,
    retry: 2,
    retryDelay: 1000,
  });
}

/**
 * خطاف للحصول على مرحلة القمر
 * Hook to get moon phase
 */
export function useMoonPhase(
  options?: AstronomicalHookOptions & { date?: string },
) {
  const { enabled = true, date } = options || {};

  return useQuery({
    queryKey: ["astronomical", "moon-phase", date],
    queryFn: () => getMoonPhase(date),
    staleTime: 60 * 60 * 1000, // ساعة واحدة - 1 hour
    enabled,
    retry: 2,
    retryDelay: 1000,
  });
}

/**
 * خطاف للحصول على المنزلة القمرية
 * Hook to get lunar mansion
 */
export function useLunarMansion(
  options?: AstronomicalHookOptions & { date?: string },
) {
  const { enabled = true, date } = options || {};

  return useQuery({
    queryKey: ["astronomical", "lunar-mansion", date],
    queryFn: () => getLunarMansion(date),
    staleTime: 24 * 60 * 60 * 1000, // 24 ساعة - 24 hours
    enabled,
    retry: 2,
    retryDelay: 1000,
  });
}

/**
 * خطاف للحصول على تقويم محصول معين
 * Hook to get crop calendar
 * @param crop - اسم المحصول
 */
export function useCropCalendar(
  crop: string,
  options?: AstronomicalHookOptions,
) {
  const { enabled = true } = options || {};

  return useQuery({
    queryKey: ["astronomical", "crop-calendar", crop],
    queryFn: () => getCropCalendar(crop),
    staleTime: 24 * 60 * 60 * 1000, // 24 ساعة - 24 hours
    enabled: enabled && !!crop,
    retry: 2,
    retryDelay: 1000,
  });
}

/**
 * خطاف للبحث عن أفضل الأيام لنشاط زراعي معين
 * Hook to search for best days for a farming activity
 * @param activity - النشاط الزراعي
 * @param days - عدد الأيام للبحث
 */
export function useBestDays(
  activity: string = "زراعة",
  options?: AstronomicalHookOptions & { days?: number },
) {
  const { enabled = true, days = 30 } = options || {};

  return useQuery({
    queryKey: ["astronomical", "best-days", activity, days],
    queryFn: () => getBestDays(activity, days),
    staleTime: 24 * 60 * 60 * 1000, // 24 ساعة - 24 hours
    enabled: enabled && !!activity,
    retry: 2,
    retryDelay: 1000,
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// الأمثال والحكمة - Proverbs and Wisdom Hooks
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * خطاف للحصول على جميع الأمثال الزراعية اليمنية
 * Hook to get all Yemeni farming proverbs
 */
export function useProverbs(options?: AstronomicalHookOptions) {
  const { enabled = true } = options || {};

  return useQuery({
    queryKey: ["astronomical", "proverbs"],
    queryFn: getProverbs,
    staleTime: 7 * 24 * 60 * 60 * 1000, // أسبوع - 1 week (البيانات ثابتة)
    enabled,
    retry: 2,
    retryDelay: 1000,
  });
}

/**
 * خطاف للحصول على مثل اليوم
 * Hook to get proverb of the day
 */
export function useProverbOfTheDay(options?: AstronomicalHookOptions) {
  const { enabled = true } = options || {};

  return useQuery({
    queryKey: ["astronomical", "proverb-of-the-day"],
    queryFn: getProverbOfTheDay,
    staleTime: 24 * 60 * 60 * 1000, // 24 ساعة - 24 hours
    enabled,
    retry: 2,
    retryDelay: 1000,
  });
}

/**
 * خطاف للحصول على الحكمة اليومية الشاملة
 * Hook to get comprehensive daily wisdom
 */
export function useWisdomToday(options?: AstronomicalHookOptions) {
  const { enabled = true } = options || {};

  return useQuery({
    queryKey: ["astronomical", "wisdom-today"],
    queryFn: getWisdomToday,
    staleTime: 24 * 60 * 60 * 1000, // 24 ساعة - 24 hours
    enabled,
    retry: 2,
    retryDelay: 1000,
  });
}
