/**
 * Weather Feature - API Layer
 * طبقة API لميزة الطقس
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { WEATHER_ENDPOINTS } from '@sahool/shared-types/contracts';
import type { WeatherData, WeatherAlert, ForecastDataPoint } from './types';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// ─────────────────────────────────────────────────────────────────────────────
// Error Messages (bilingual) - رسائل الأخطاء
// ─────────────────────────────────────────────────────────────────────────────

export const ERROR_MESSAGES = {
  FETCH_CURRENT_FAILED: {
    en: 'Failed to fetch current weather data.',
    ar: 'فشل في جلب بيانات الطقس الحالية.',
  },
  FETCH_FORECAST_FAILED: {
    en: 'Failed to fetch weather forecast.',
    ar: 'فشل في جلب توقعات الطقس.',
  },
  FETCH_ALERTS_FAILED: {
    en: 'Failed to fetch weather alerts.',
    ar: 'فشل في جلب تنبيهات الطقس.',
  },
  NETWORK_ERROR: {
    en: 'Network error. Using cached weather data.',
    ar: 'خطأ في الاتصال. استخدام بيانات الطقس المخزنة.',
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// API Response Types (internal)
// ─────────────────────────────────────────────────────────────────────────────

interface ApiForecastDay {
  date: string;
  temp_max_c: number;
  temp_min_c: number;
  precipitation_mm?: number;
  wind_speed_max_kmh?: number;
}

interface ApiWeatherAlert {
  id?: string;
  type?: string;
  alert_type?: string;
  severity?: string;
  title?: string;
  title_en?: string;
  title_ar?: string;
  titleAr?: string;
  description?: string;
  descriptionAr?: string;
  affectedAreas?: string[];
  affectedAreasAr?: string[];
  startTime?: string;
  startDate?: string;
  endTime?: string;
  endDate?: string;
  isActive?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper Functions
// ─────────────────────────────────────────────────────────────────────────────

function getWindDirection(degrees: number): string {
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'] as const;
  const index = Math.round(degrees / 45) % 8;
  return directions[index] ?? 'N';
}

function getWeatherCondition(cloudCover: number): string {
  if (cloudCover < 20) return 'Clear';
  if (cloudCover < 50) return 'Partly Cloudy';
  if (cloudCover < 80) return 'Cloudy';
  return 'Overcast';
}

function getWeatherConditionAr(cloudCover: number): string {
  if (cloudCover < 20) return 'صافي';
  if (cloudCover < 50) return 'غائم جزئياً';
  if (cloudCover < 80) return 'غائم';
  return 'ملبد بالغيوم';
}

function getWeatherConditionFromPrecipitation(precipitation: number): string {
  if (precipitation > 10) return 'Rainy';
  if (precipitation > 2) return 'Light Rain';
  return 'Sunny';
}

function getWeatherConditionArFromPrecipitation(precipitation: number): string {
  if (precipitation > 10) return 'ممطر';
  if (precipitation > 2) return 'أمطار خفيفة';
  return 'مشمس';
}

// ─────────────────────────────────────────────────────────────────────────────
// API Functions
// ─────────────────────────────────────────────────────────────────────────────

export const weatherApi = {
  /**
   * Fetch current weather data
   * جلب بيانات الطقس الحالية
   */
  getCurrentWeather: async (lat?: number, lon?: number): Promise<WeatherData> => {
    const params = new URLSearchParams();
    if (lat !== undefined) params.set('lat', String(lat));
    if (lon !== undefined) params.set('lon', String(lon));

    return safeFetch(WEATHER_ENDPOINTS.CURRENT, async () => {
      const response = await api.get(`${WEATHER_ENDPOINTS.CURRENT}?${params.toString()}`);
      const data = response.data.data || response.data;

      return {
        temperature: data.current?.temperature_c ?? data.temperature_c ?? 0,
        humidity: data.current?.humidity_pct ?? data.humidity_pct ?? 0,
        windSpeed: data.current?.wind_speed_kmh ?? data.wind_speed_kmh ?? 0,
        windDirection: getWindDirection(data.current?.wind_direction_deg ?? 0),
        pressure: data.current?.pressure_hpa ?? data.pressure_hpa ?? 1013,
        visibility: 10,
        uvIndex: data.current?.uv_index ?? data.uv_index ?? 0,
        condition: getWeatherCondition(data.current?.cloud_cover_pct ?? 0),
        conditionAr: getWeatherConditionAr(data.current?.cloud_cover_pct ?? 0),
        location: data.location ?? '',
        timestamp: data.current?.timestamp ?? new Date().toISOString(),
      };
    });
  },

  /**
   * Fetch weather forecast
   * جلب توقعات الطقس
   */
  getForecast: async (
    lat?: number,
    lon?: number,
    days: number = 7
  ): Promise<ForecastDataPoint[]> => {
    const params = new URLSearchParams();
    if (lat !== undefined) params.set('lat', String(lat));
    if (lon !== undefined) params.set('lon', String(lon));
    params.set('days', String(days));

    return safeFetch(WEATHER_ENDPOINTS.FORECAST, async () => {
      const response = await api.get(`${WEATHER_ENDPOINTS.FORECAST}?${params.toString()}`);
      const data = response.data.data || response.data;
      const forecastData = data.forecast || data.daily_forecast || [];

      if (!Array.isArray(forecastData)) {
        throw new Error('Invalid forecast response format');
      }

      return forecastData.map((day: ApiForecastDay) => ({
        date: day.date,
        temperature: (day.temp_max_c + day.temp_min_c) / 2,
        humidity: 60,
        precipitation: day.precipitation_mm ?? 0,
        windSpeed: day.wind_speed_max_kmh ?? 0,
        condition: getWeatherConditionFromPrecipitation(day.precipitation_mm ?? 0),
        conditionAr: getWeatherConditionArFromPrecipitation(day.precipitation_mm ?? 0),
      }));
    });
  },

  /**
   * Fetch weather alerts
   * جلب تنبيهات الطقس
   */
  getAlerts: async (lat?: number, lon?: number): Promise<WeatherAlert[]> => {
    const params = new URLSearchParams();
    if (lat !== undefined) params.set('lat', String(lat));
    if (lon !== undefined) params.set('lon', String(lon));

    return safeFetch(WEATHER_ENDPOINTS.ALERTS, async () => {
      const response = await api.get(`${WEATHER_ENDPOINTS.ALERTS}?${params.toString()}`);
      const data = response.data.data || response.data;
      const alerts = data.alerts || data;

      if (!Array.isArray(alerts)) {
        return [];
      }

      return alerts.map((alert: ApiWeatherAlert) => ({
        id: alert.id || crypto.randomUUID(),
        type: alert.type || alert.alert_type || 'weather',
        severity: (alert.severity || 'warning') as WeatherAlert['severity'],
        title: alert.title_en || alert.title || 'Weather Alert',
        titleAr: alert.title_ar || alert.titleAr || 'تنبيه طقس',
        description: alert.description || '',
        descriptionAr: alert.descriptionAr || alert.description || '',
        affectedAreas: alert.affectedAreas || [],
        affectedAreasAr: alert.affectedAreasAr || [],
        startTime: alert.startTime || alert.startDate || new Date().toISOString(),
        endTime: alert.endTime || alert.endDate,
        isActive: alert.isActive ?? true,
      }));
    });
  },
};
