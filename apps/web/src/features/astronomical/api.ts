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
} from './types';

// ═══════════════════════════════════════════════════════════════════════════════
// إعداد واجهة برمجة التطبيقات - API Configuration
// ═══════════════════════════════════════════════════════════════════════════════

import { ASTRONOMICAL_ENDPOINTS } from '@sahool/shared-types/contracts';
import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';

const api = createApiClient();

const ASTRONOMICAL_API_BASE = ASTRONOMICAL_ENDPOINTS.CALENDAR.replace('/calendar', '');

// ═══════════════════════════════════════════════════════════════════════════════
// رسائل الخطأ - Error Messages
// ═══════════════════════════════════════════════════════════════════════════════

export const ERROR_MESSAGES = {
  FETCH_FAILED: {
    en: 'Failed to fetch astronomical data.',
    ar: 'فشل الحصول على البيانات الفلكية.',
  },
  NETWORK_ERROR: {
    en: 'Network error. Astronomical calendar service unavailable.',
    ar: 'خطأ في الاتصال. خدمة التقويم الفلكي غير متاحة.',
  },
  CALENDAR_FAILED: {
    en: 'Failed to fetch calendar data.',
    ar: 'فشل في جلب بيانات التقويم.',
  },
  PROVERBS_FAILED: {
    en: 'Failed to fetch proverbs.',
    ar: 'فشل في جلب الأمثال.',
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// واجهات برمجة التطبيقات الرئيسية - Main API Functions
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * الحصول على البيانات الفلكية لليوم الحالي
 * Get astronomical data for today
 */
export async function getToday(): Promise<DailyAstronomicalData> {
  return safeFetch(`${ASTRONOMICAL_API_BASE}/today`, async () => {
    const response = await api.get(`${ASTRONOMICAL_API_BASE}/today`);
    return response.data.data || response.data;
  });
}

/**
 * التحقق من صيغة التاريخ YYYY-MM-DD لمنع حقن المسار
 * Validate YYYY-MM-DD date format to prevent path injection.
 */
const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

function assertIsoDate(date: string, label: string): void {
  if (!ISO_DATE_RE.test(date)) {
    throw new Error(
      `Invalid ${label}: expected YYYY-MM-DD, got "${date}"`,
    );
  }
}

/**
 * الحصول على البيانات الفلكية لتاريخ محدد
 * Get astronomical data for a specific date
 * @param date - التاريخ بصيغة YYYY-MM-DD
 */
export async function getDate(date: string): Promise<DailyAstronomicalData> {
  assertIsoDate(date, 'date');
  const safe = encodeURIComponent(date);
  return safeFetch(`${ASTRONOMICAL_API_BASE}/date/${safe}`, async () => {
    const response = await api.get(`${ASTRONOMICAL_API_BASE}/date/${safe}`);
    return response.data.data || response.data;
  });
}

/**
 * الحصول على التوقعات الأسبوعية
 * Get weekly forecast
 * @param startDate - تاريخ البداية (اختياري) بصيغة YYYY-MM-DD
 */
export async function getWeeklyForecast(startDate?: string): Promise<WeeklyForecast> {
  if (startDate) assertIsoDate(startDate, 'startDate');
  const params = startDate ? `?start_date=${encodeURIComponent(startDate)}` : '';
  return safeFetch(`${ASTRONOMICAL_API_BASE}/week`, async () => {
    const response = await api.get(`${ASTRONOMICAL_API_BASE}/week${params}`);
    return response.data.data || response.data;
  });
}

/**
 * الحصول على مرحلة القمر
 * Get moon phase
 * @param date - التاريخ (اختياري) بصيغة YYYY-MM-DD
 */
export async function getMoonPhase(date?: string): Promise<MoonPhase> {
  if (date) assertIsoDate(date, 'date');
  const params = date ? `?date_str=${encodeURIComponent(date)}` : '';
  return safeFetch(`${ASTRONOMICAL_API_BASE}/moon-phase`, async () => {
    const response = await api.get(`${ASTRONOMICAL_API_BASE}/moon-phase${params}`);
    return response.data.data || response.data;
  });
}

/**
 * الحصول على المنزلة القمرية
 * Get lunar mansion
 * @param date - التاريخ (اختياري) بصيغة YYYY-MM-DD
 */
export async function getLunarMansion(date?: string): Promise<LunarMansion> {
  if (date) assertIsoDate(date, 'date');
  const params = date ? `?date_str=${encodeURIComponent(date)}` : '';
  return safeFetch(`${ASTRONOMICAL_API_BASE}/lunar-mansion`, async () => {
    const response = await api.get(`${ASTRONOMICAL_API_BASE}/lunar-mansion${params}`);
    return response.data.data || response.data;
  });
}

/**
 * الحصول على التاريخ الهجري
 * Get Hijri date
 * @param date - التاريخ الميلادي (اختياري) بصيغة YYYY-MM-DD
 */
export async function getHijriDate(date?: string): Promise<HijriDate> {
  if (date) assertIsoDate(date, 'date');
  const params = date ? `?date_str=${encodeURIComponent(date)}` : '';
  return safeFetch(`${ASTRONOMICAL_API_BASE}/hijri`, async () => {
    const response = await api.get(`${ASTRONOMICAL_API_BASE}/hijri${params}`);
    return response.data.data || response.data;
  });
}

/**
 * الحصول على تقويم محصول معين
 * Get crop calendar
 * @param crop - اسم المحصول (قمح، طماطم، بن، إلخ)
 */
export async function getCropCalendar(crop: string): Promise<CropCalendar> {
  return safeFetch(`${ASTRONOMICAL_API_BASE}/crop-calendar`, async () => {
    const response = await api.get(`${ASTRONOMICAL_API_BASE}/crop-calendar/${encodeURIComponent(crop)}`);
    return response.data.data || response.data;
  });
}

/**
 * البحث عن أفضل الأيام لنشاط زراعي معين
 * Search for best days for a farming activity
 * @param activity - النشاط (زراعة، حصاد، ري، تقليم)
 * @param days - عدد الأيام للبحث (7-90)
 */
export async function getBestDays(
  activity: string = 'زراعة',
  days: number = 30
): Promise<BestDaysResult> {
  const params = new URLSearchParams({
    activity,
    days: days.toString(),
  });
  return safeFetch(`${ASTRONOMICAL_API_BASE}/best-days`, async () => {
    const response = await api.get(`${ASTRONOMICAL_API_BASE}/best-days?${params}`);
    return response.data.data || response.data;
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// الأمثال والحكمة - Proverbs and Wisdom
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * الحصول على جميع الأمثال الزراعية اليمنية
 * Get all Yemeni farming proverbs
 */
export async function getProverbs(): Promise<AllProverbs> {
  return safeFetch(`${ASTRONOMICAL_API_BASE}/proverbs`, async () => {
    const response = await api.get(`${ASTRONOMICAL_API_BASE}/proverbs`);
    return response.data.data || response.data;
  });
}

/**
 * الحصول على مثل اليوم
 * Get proverb of the day
 */
export async function getProverbOfTheDay(): Promise<ProverbOfTheDay> {
  return safeFetch(`${ASTRONOMICAL_API_BASE}/proverbs/today`, async () => {
    const response = await api.get(`${ASTRONOMICAL_API_BASE}/proverbs/today`);
    return response.data.data || response.data;
  });
}

/**
 * الحصول على الحكمة اليومية الشاملة
 * Get comprehensive daily wisdom
 */
export async function getWisdomToday(): Promise<DailyWisdom> {
  return safeFetch(`${ASTRONOMICAL_API_BASE}/wisdom/today`, async () => {
    const response = await api.get(`${ASTRONOMICAL_API_BASE}/wisdom/today`);
    return response.data.data || response.data;
  });
}
