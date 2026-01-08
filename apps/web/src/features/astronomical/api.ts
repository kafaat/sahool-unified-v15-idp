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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// تحذير في التطوير فقط - Only warn during development
if (!API_BASE_URL && typeof window !== 'undefined') {
  console.warn('NEXT_PUBLIC_API_URL environment variable is not set');
}

const ASTRONOMICAL_API_BASE = `${API_BASE_URL}/api/v1/astronomical`;

// ═══════════════════════════════════════════════════════════════════════════════
// دوال مساعدة - Helper Functions
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * معالج الطلبات مع معالجة الأخطاء
 * Request handler with error handling
 */
async function fetchFromAPI<T>(endpoint: string): Promise<T> {
  try {
    const response = await fetch(`${ASTRONOMICAL_API_BASE}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`فشل الحصول على البيانات الفلكية: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('خطأ في الاتصال بخدمة التقويم الفلكي:', error);
    throw error;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// واجهات برمجة التطبيقات الرئيسية - Main API Functions
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * الحصول على البيانات الفلكية لليوم الحالي
 * Get astronomical data for today
 */
export async function getToday(): Promise<DailyAstronomicalData> {
  return fetchFromAPI<DailyAstronomicalData>('/today');
}

/**
 * الحصول على البيانات الفلكية لتاريخ محدد
 * Get astronomical data for a specific date
 * @param date - التاريخ بصيغة YYYY-MM-DD
 */
export async function getDate(date: string): Promise<DailyAstronomicalData> {
  return fetchFromAPI<DailyAstronomicalData>(`/date/${date}`);
}

/**
 * الحصول على التوقعات الأسبوعية
 * Get weekly forecast
 * @param startDate - تاريخ البداية (اختياري) بصيغة YYYY-MM-DD
 */
export async function getWeeklyForecast(startDate?: string): Promise<WeeklyForecast> {
  const params = startDate ? `?start_date=${startDate}` : '';
  return fetchFromAPI<WeeklyForecast>(`/week${params}`);
}

/**
 * الحصول على مرحلة القمر
 * Get moon phase
 * @param date - التاريخ (اختياري) بصيغة YYYY-MM-DD
 */
export async function getMoonPhase(date?: string): Promise<MoonPhase> {
  const params = date ? `?date_str=${date}` : '';
  return fetchFromAPI<MoonPhase>(`/moon-phase${params}`);
}

/**
 * الحصول على المنزلة القمرية
 * Get lunar mansion
 * @param date - التاريخ (اختياري) بصيغة YYYY-MM-DD
 */
export async function getLunarMansion(date?: string): Promise<LunarMansion> {
  const params = date ? `?date_str=${date}` : '';
  return fetchFromAPI<LunarMansion>(`/lunar-mansion${params}`);
}

/**
 * الحصول على التاريخ الهجري
 * Get Hijri date
 * @param date - التاريخ الميلادي (اختياري) بصيغة YYYY-MM-DD
 */
export async function getHijriDate(date?: string): Promise<HijriDate> {
  const params = date ? `?date_str=${date}` : '';
  return fetchFromAPI<HijriDate>(`/hijri${params}`);
}

/**
 * الحصول على تقويم محصول معين
 * Get crop calendar
 * @param crop - اسم المحصول (قمح، طماطم، بن، إلخ)
 */
export async function getCropCalendar(crop: string): Promise<CropCalendar> {
  return fetchFromAPI<CropCalendar>(`/crop-calendar/${encodeURIComponent(crop)}`);
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
  return fetchFromAPI<BestDaysResult>(`/best-days?${params}`);
}

// ═══════════════════════════════════════════════════════════════════════════════
// الأمثال والحكمة - Proverbs and Wisdom
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * الحصول على جميع الأمثال الزراعية اليمنية
 * Get all Yemeni farming proverbs
 */
export async function getProverbs(): Promise<AllProverbs> {
  return fetchFromAPI<AllProverbs>('/proverbs');
}

/**
 * الحصول على مثل اليوم
 * Get proverb of the day
 */
export async function getProverbOfTheDay(): Promise<ProverbOfTheDay> {
  return fetchFromAPI<ProverbOfTheDay>('/proverbs/today');
}

/**
 * الحصول على الحكمة اليومية الشاملة
 * Get comprehensive daily wisdom
 */
export async function getWisdomToday(): Promise<DailyWisdom> {
  return fetchFromAPI<DailyWisdom>('/wisdom/today');
}
