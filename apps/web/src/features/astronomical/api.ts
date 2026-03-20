/**
 * SAHOOL Astronomical Calendar API Client
 * عميل واجهة برمجة التطبيقات للتقويم الفلكي
 */

import type {
  DailyAstronomicalData,
  WeeklyForecast,
  MoonPhase,
  LunarMansion,
  HijriDate,
  CropCalendar,
  BestDaysResult,
  AllProverbs,
  ProverbOfTheDay,
  DailyWisdom,
} from "./types";

// ═══════════════════════════════════════════════════════════════════════════════
// إعداد واجهة برمجة التطبيقات - API Configuration
// ═══════════════════════════════════════════════════════════════════════════════

import { ASTRONOMICAL_ENDPOINTS } from "@sahool/shared-types/contracts";
import { createApiClient, extractData } from "@/lib/api/factory";

const api = createApiClient();

// Base path derived from the contract constant (e.g. "/api/v1/astronomical")
const ASTRO_BASE = ASTRONOMICAL_ENDPOINTS.CALENDAR.replace("/calendar", "");

// ═══════════════════════════════════════════════════════════════════════════════
// واجهات برمجة التطبيقات الرئيسية - Main API Functions
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * الحصول على البيانات الفلكية لليوم الحالي
 * Get astronomical data for today
 */
export async function getToday(): Promise<DailyAstronomicalData> {
  const res = await api.get(`${ASTRO_BASE}/today`);
  return extractData(res);
}

/**
 * الحصول على البيانات الفلكية لتاريخ محدد
 * Get astronomical data for a specific date
 * @param date - التاريخ بصيغة YYYY-MM-DD
 */
export async function getDate(date: string): Promise<DailyAstronomicalData> {
  const res = await api.get(`${ASTRO_BASE}/date/${date}`);
  return extractData(res);
}

/**
 * الحصول على التوقعات الأسبوعية
 * Get weekly forecast
 * @param startDate - تاريخ البداية (اختياري) بصيغة YYYY-MM-DD
 */
export async function getWeeklyForecast(
  startDate?: string,
): Promise<WeeklyForecast> {
  const params = startDate ? `?start_date=${startDate}` : "";
  const res = await api.get(`${ASTRO_BASE}/week${params}`);
  return extractData(res);
}

/**
 * الحصول على مرحلة القمر
 * Get moon phase
 * @param date - التاريخ (اختياري) بصيغة YYYY-MM-DD
 */
export async function getMoonPhase(date?: string): Promise<MoonPhase> {
  const params = date ? `?date_str=${date}` : "";
  const res = await api.get(`${ASTRO_BASE}/moon-phase${params}`);
  return extractData(res);
}

/**
 * الحصول على المنزلة القمرية
 * Get lunar mansion
 * @param date - التاريخ (اختياري) بصيغة YYYY-MM-DD
 */
export async function getLunarMansion(date?: string): Promise<LunarMansion> {
  const params = date ? `?date_str=${date}` : "";
  const res = await api.get(`${ASTRO_BASE}/lunar-mansion${params}`);
  return extractData(res);
}

/**
 * الحصول على التاريخ الهجري
 * Get Hijri date
 * @param date - التاريخ الميلادي (اختياري) بصيغة YYYY-MM-DD
 */
export async function getHijriDate(date?: string): Promise<HijriDate> {
  const params = date ? `?date_str=${date}` : "";
  const res = await api.get(`${ASTRO_BASE}/hijri${params}`);
  return extractData(res);
}

/**
 * الحصول على تقويم محصول معين
 * Get crop calendar
 * @param crop - اسم المحصول (قمح، طماطم، بن، إلخ)
 */
export async function getCropCalendar(crop: string): Promise<CropCalendar> {
  const res = await api.get(
    `${ASTRO_BASE}/crop-calendar/${encodeURIComponent(crop)}`,
  );
  return extractData(res);
}

/**
 * البحث عن أفضل الأيام لنشاط زراعي معين
 * Search for best days for a farming activity
 * @param activity - النشاط (زراعة، حصاد، ري، تقليم)
 * @param days - عدد الأيام للبحث (7-90)
 */
export async function getBestDays(
  activity: string = "زراعة",
  days: number = 30,
): Promise<BestDaysResult> {
  const params = new URLSearchParams({
    activity,
    days: days.toString(),
  });
  const res = await api.get(`${ASTRO_BASE}/best-days?${params}`);
  return extractData(res);
}

// ═══════════════════════════════════════════════════════════════════════════════
// الأمثال والحكمة - Proverbs and Wisdom
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * الحصول على جميع الأمثال الزراعية اليمنية
 * Get all Yemeni farming proverbs
 */
export async function getProverbs(): Promise<AllProverbs> {
  const res = await api.get(`${ASTRO_BASE}/proverbs`);
  return extractData(res);
}

/**
 * الحصول على مثل اليوم
 * Get proverb of the day
 */
export async function getProverbOfTheDay(): Promise<ProverbOfTheDay> {
  const res = await api.get(`${ASTRO_BASE}/proverbs/today`);
  return extractData(res);
}

/**
 * الحصول على الحكمة اليومية الشاملة
 * Get comprehensive daily wisdom
 */
export async function getWisdomToday(): Promise<DailyWisdom> {
  const res = await api.get(`${ASTRO_BASE}/wisdom/today`);
  return extractData(res);
}
