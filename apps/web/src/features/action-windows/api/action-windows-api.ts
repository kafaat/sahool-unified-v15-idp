/**
 * SAHOOL Action Windows API Client
 * عميل API لنوافذ العمل
 *
 * API functions for fetching spray windows, irrigation windows, and action recommendations
 */

import axios from 'axios';
import Cookies from 'js-cookie';
import { logger } from '@/lib/logger';
import type {
  SprayWindow,
  IrrigationWindow,
  ActionRecommendation,
  GetSprayWindowsRequest,
  GetIrrigationWindowsRequest,
  GetActionRecommendationsRequest,
  ActionWindowsResponse,
  WeatherCondition,
} from '../types/action-windows';
import {
  calculateSprayWindow,
  calculateIrrigationNeed,
  getOptimalWindow,
  groupIntoWindows,
  DEFAULT_SPRAY_CRITERIA,
} from '../utils/window-calculator';

// ═══════════════════════════════════════════════════════════════════════════
// API Configuration
// ═══════════════════════════════════════════════════════════════════════════

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

if (!API_BASE_URL && typeof window !== 'undefined') {
  console.warn('NEXT_PUBLIC_API_URL environment variable is not set');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Add auth token interceptor
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = Cookies.get('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// ═══════════════════════════════════════════════════════════════════════════
// Error Messages
// ═══════════════════════════════════════════════════════════════════════════

export const ERROR_MESSAGES = {
  SPRAY_WINDOWS_FETCH_FAILED: {
    en: 'Failed to fetch spray windows',
    ar: 'فشل في جلب نوافذ الرش',
  },
  IRRIGATION_WINDOWS_FETCH_FAILED: {
    en: 'Failed to fetch irrigation windows',
    ar: 'فشل في جلب نوافذ الري',
  },
  RECOMMENDATIONS_FETCH_FAILED: {
    en: 'Failed to fetch action recommendations',
    ar: 'فشل في جلب توصيات العمل',
  },
  INVALID_FIELD_ID: {
    en: 'Invalid field ID provided',
    ar: 'معرف الحقل غير صالح',
  },
  WEATHER_DATA_UNAVAILABLE: {
    en: 'Weather data unavailable',
    ar: 'بيانات الطقس غير متوفرة',
  },
} as const;

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Fetch weather forecast data for field location
 */
async function fetchWeatherForecast(
  fieldId: string,
  days: number = 7
): Promise<WeatherCondition[]> {
  try {
    // Try to get field location
    const fieldResponse = await api.get(`/api/v1/fields/${fieldId}`);
    const field = fieldResponse.data.data || fieldResponse.data;

    let lat = 15.3694; // Default: Sana'a, Yemen
    let lon = 44.191;

    if (field?.centroid?.coordinates && Array.isArray(field.centroid.coordinates)) {
      const coords = field.centroid.coordinates;
      if (coords.length >= 2) {
        lon = coords[0] as number;
        lat = coords[1] as number;
      }
    }

    // Fetch weather forecast
    const weatherResponse = await api.get(`/api/v1/weather/forecast`, {
      params: { lat, lon, days },
    });

    const forecastData = weatherResponse.data.forecast || weatherResponse.data.daily_forecast || [];

    // Transform to hourly conditions (simplified - generate hourly from daily)
    const conditions: WeatherCondition[] = [];

    for (const day of forecastData) {
      // Generate hourly data for key hours: 6am, 9am, 12pm, 3pm, 6pm
      const date = new Date(day.date);
      const hours = [6, 9, 12, 15, 18];

      for (const hour of hours) {
        const timestamp = new Date(date);
        timestamp.setHours(hour, 0, 0, 0);

        conditions.push({
          timestamp: timestamp.toISOString(),
          temperature: day.temp_max_c - (Math.abs(hour - 12) * 2), // Simplified temperature curve
          humidity: day.humidity_pct || 60,
          windSpeed: day.wind_speed_max_kmh || 10,
          windDirection: 'N',
          rainProbability: day.precipitation_probability || 0,
          precipitation: day.precipitation_mm || 0,
          cloudCover: day.cloud_cover_pct || 30,
        });
      }
    }

    return conditions;
  } catch (error) {
    logger.warn('Failed to fetch weather forecast, using mock data:', error);
    return generateMockWeatherConditions(days);
  }
}

/**
 * Generate mock weather conditions for testing
 */
function generateMockWeatherConditions(days: number): WeatherCondition[] {
  const conditions: WeatherCondition[] = [];
  const now = new Date();

  for (let day = 0; day < days; day++) {
    for (let hour of [6, 9, 12, 15, 18]) {
      const timestamp = new Date(now);
      timestamp.setDate(timestamp.getDate() + day);
      timestamp.setHours(hour, 0, 0, 0);

      conditions.push({
        timestamp: timestamp.toISOString(),
        temperature: 20 + Math.random() * 15,
        humidity: 50 + Math.random() * 30,
        windSpeed: 5 + Math.random() * 15,
        windDirection: ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'][Math.floor(Math.random() * 8)],
        rainProbability: Math.random() * 30,
        precipitation: Math.random() < 0.2 ? Math.random() * 5 : 0,
        cloudCover: Math.random() * 100,
        uvIndex: hour >= 10 && hour <= 16 ? 5 + Math.random() * 5 : 2,
      });
    }
  }

  return conditions;
}

// ═══════════════════════════════════════════════════════════════════════════
// API Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get spray windows for a field
 * جلب نوافذ الرش للحقل
 */
export async function getSprayWindows(
  request: GetSprayWindowsRequest
): Promise<ActionWindowsResponse<SprayWindow[]>> {
  const { fieldId, days = 7, criteria } = request;

  if (!fieldId || typeof fieldId !== 'string' || fieldId.trim().length === 0) {
    return {
      success: false,
      error: ERROR_MESSAGES.INVALID_FIELD_ID.en,
      error_ar: ERROR_MESSAGES.INVALID_FIELD_ID.ar,
    };
  }

  try {
    // Try to fetch from backend API first
    try {
      const response = await api.get(`/api/v1/action-windows/spray`, {
        params: { fieldId, days },
      });

      if (response.data?.success && response.data?.data) {
        return response.data;
      }
    } catch (apiError) {
      // Backend not available, fall through to client-side calculation
      logger.info('Action windows API not available, calculating client-side');
    }

    // Fetch weather forecast
    const conditions = await fetchWeatherForecast(fieldId, days);

    if (conditions.length === 0) {
      return {
        success: false,
        error: ERROR_MESSAGES.WEATHER_DATA_UNAVAILABLE.en,
        error_ar: ERROR_MESSAGES.WEATHER_DATA_UNAVAILABLE.ar,
      };
    }

    // Calculate spray suitability for each time slot
    const results = conditions.map((condition) => ({
      timestamp: condition.timestamp,
      status: calculateSprayWindow(condition, criteria).status,
      condition,
      result: calculateSprayWindow(condition, criteria),
    }));

    // Group into windows
    const windows = groupIntoWindows(
      results.map((r) => ({ timestamp: r.timestamp, status: r.status })),
      criteria?.minDuration || DEFAULT_SPRAY_CRITERIA.minDuration
    );

    // Create SprayWindow objects
    const sprayWindows: SprayWindow[] = windows.map((window, index) => {
      const startCondition = results.find((r) => r.timestamp === window.startTime);
      if (!startCondition) {
        // Skip windows without valid conditions
        return null;
      }
      const result = startCondition.result || calculateSprayWindow(startCondition.condition, criteria);

      return {
        id: `spray-${fieldId}-${index}`,
        fieldId,
        startTime: window.startTime,
        endTime: window.endTime,
        duration: window.duration,
        status: window.status,
        score: result.score,
        conditions: startCondition.condition,
        suitability: result.suitability as Record<string, boolean>,
        warnings: result.warnings,
        warningsAr: result.warningsAr,
        recommendations: result.recommendations,
        recommendationsAr: result.recommendationsAr,
      };
    }).filter((w): w is SprayWindow => w !== null);

    // Sort by score (best first)
    sprayWindows.sort((a, b) => b.score - a.score);

    return {
      success: true,
      data: sprayWindows,
    };
  } catch (error) {
    logger.error('[getSprayWindows] Request failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : ERROR_MESSAGES.SPRAY_WINDOWS_FETCH_FAILED.en,
      error_ar: ERROR_MESSAGES.SPRAY_WINDOWS_FETCH_FAILED.ar,
    };
  }
}

/**
 * Get irrigation windows for a field
 * جلب نوافذ الري للحقل
 */
export async function getIrrigationWindows(
  request: GetIrrigationWindowsRequest
): Promise<ActionWindowsResponse<IrrigationWindow[]>> {
  const { fieldId, days = 7 } = request;

  if (!fieldId || typeof fieldId !== 'string' || fieldId.trim().length === 0) {
    return {
      success: false,
      error: ERROR_MESSAGES.INVALID_FIELD_ID.en,
      error_ar: ERROR_MESSAGES.INVALID_FIELD_ID.ar,
    };
  }

  try {
    // Try to fetch from backend API first
    try {
      const response = await api.get(`/api/v1/action-windows/irrigation`, {
        params: { fieldId, days },
      });

      if (response.data?.success && response.data?.data) {
        return response.data;
      }
    } catch (apiError) {
      logger.info('Action windows API not available, calculating client-side');
    }

    // Fetch weather forecast
    const conditions = await fetchWeatherForecast(fieldId, days);

    // Mock soil moisture data (in production, fetch from sensors)
    const soilMoisture = {
      current: 45, // %
      target: 70, // %
      fieldCapacity: 85, // %
      wiltingPoint: 15, // %
      timestamp: new Date().toISOString(),
    };

    // Calculate irrigation need
    const irrigationNeed = calculateIrrigationNeed(
      soilMoisture,
      { et0: 5, date: new Date().toISOString() },
      1
    );

    irrigationNeed.fieldId = fieldId;

    // Find optimal irrigation windows (prefer morning/evening)
    const irrigationWindows: IrrigationWindow[] = [];

    for (let day = 0; day < days; day++) {
      const date = new Date();
      date.setDate(date.getDate() + day);

      // Morning window (6-9 AM)
      const morningConditions = conditions.filter((c) => {
        const cDate = new Date(c.timestamp);
        return (
          cDate.toDateString() === date.toDateString() &&
          cDate.getHours() >= 6 &&
          cDate.getHours() <= 9
        );
      });

      if (morningConditions.length > 0) {
        const optimalCondition = getOptimalWindow(morningConditions, 'irrigate');

        if (optimalCondition) {
          irrigationWindows.push({
            id: `irrigation-${fieldId}-morning-${day}`,
            fieldId,
            date: date.toISOString(),
            startTime: optimalCondition.timestamp,
            endTime: new Date(new Date(optimalCondition.timestamp).getTime() + irrigationNeed.recommendedDuration * 60 * 60 * 1000).toISOString(),
            status: irrigationNeed.urgency === 'critical' || irrigationNeed.urgency === 'high' ? 'optimal' : 'marginal',
            priority: irrigationNeed.urgency === 'critical' ? 'urgent' : irrigationNeed.urgency === 'high' ? 'high' : 'medium',
            waterAmount: irrigationNeed.recommendedAmount,
            duration: irrigationNeed.recommendedDuration,
            soilMoisture: {
              current: soilMoisture.current,
              target: soilMoisture.target,
              deficit: irrigationNeed.soilMoistureDeficit,
              status: irrigationNeed.urgency === 'critical' ? 'critical' : irrigationNeed.urgency === 'high' ? 'low' : 'optimal',
              statusAr: irrigationNeed.urgency === 'critical' ? 'حرج' : irrigationNeed.urgency === 'high' ? 'منخفض' : 'مثالي',
            },
            et: {
              et0: irrigationNeed.et0,
              etc: irrigationNeed.et0,
              kc: 1.0,
            },
            weather: optimalCondition,
            recommendations: ['Irrigate during morning hours for optimal absorption', 'Monitor soil moisture after irrigation'],
            recommendationsAr: ['الري خلال ساعات الصباح للامتصاص الأمثل', 'راقب رطوبة التربة بعد الري'],
            reason: irrigationNeed.reasoning,
            reasonAr: irrigationNeed.reasoningAr,
          });
        }
      }

      // Evening window (17-20)
      const eveningConditions = conditions.filter((c) => {
        const cDate = new Date(c.timestamp);
        return (
          cDate.toDateString() === date.toDateString() &&
          cDate.getHours() >= 17 &&
          cDate.getHours() <= 20
        );
      });

      if (eveningConditions.length > 0) {
        const optimalCondition = getOptimalWindow(eveningConditions, 'irrigate');

        if (optimalCondition) {
          irrigationWindows.push({
            id: `irrigation-${fieldId}-evening-${day}`,
            fieldId,
            date: date.toISOString(),
            startTime: optimalCondition.timestamp,
            endTime: new Date(new Date(optimalCondition.timestamp).getTime() + irrigationNeed.recommendedDuration * 60 * 60 * 1000).toISOString(),
            status: irrigationNeed.urgency === 'critical' || irrigationNeed.urgency === 'high' ? 'optimal' : 'marginal',
            priority: irrigationNeed.urgency === 'critical' ? 'urgent' : irrigationNeed.urgency === 'high' ? 'high' : 'medium',
            waterAmount: irrigationNeed.recommendedAmount,
            duration: irrigationNeed.recommendedDuration,
            soilMoisture: {
              current: soilMoisture.current,
              target: soilMoisture.target,
              deficit: irrigationNeed.soilMoistureDeficit,
              status: irrigationNeed.urgency === 'critical' ? 'critical' : irrigationNeed.urgency === 'high' ? 'low' : 'optimal',
              statusAr: irrigationNeed.urgency === 'critical' ? 'حرج' : irrigationNeed.urgency === 'high' ? 'منخفض' : 'مثالي',
            },
            et: {
              et0: irrigationNeed.et0,
              etc: irrigationNeed.et0,
              kc: 1.0,
            },
            weather: optimalCondition,
            recommendations: ['Evening irrigation reduces water loss from evaporation', 'Ensure adequate drainage'],
            recommendationsAr: ['الري المسائي يقلل فقدان الماء من التبخر', 'تأكد من الصرف الكافي'],
            reason: irrigationNeed.reasoning,
            reasonAr: irrigationNeed.reasoningAr,
          });
        }
      }
    }

    return {
      success: true,
      data: irrigationWindows,
    };
  } catch (error) {
    logger.error('[getIrrigationWindows] Request failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : ERROR_MESSAGES.IRRIGATION_WINDOWS_FETCH_FAILED.en,
      error_ar: ERROR_MESSAGES.IRRIGATION_WINDOWS_FETCH_FAILED.ar,
    };
  }
}

/**
 * Get action recommendations for a field
 * جلب توصيات العمل للحقل
 */
export async function getActionRecommendations(
  request: GetActionRecommendationsRequest
): Promise<ActionWindowsResponse<ActionRecommendation[]>> {
  const { fieldId, actionTypes, days = 7 } = request;

  if (!fieldId || typeof fieldId !== 'string' || fieldId.trim().length === 0) {
    return {
      success: false,
      error: ERROR_MESSAGES.INVALID_FIELD_ID.en,
      error_ar: ERROR_MESSAGES.INVALID_FIELD_ID.ar,
    };
  }

  try {
    // Try to fetch from backend API first
    try {
      const response = await api.get(`/api/v1/action-windows/recommendations`, {
        params: { fieldId, days, actionTypes: actionTypes?.join(',') },
      });

      if (response.data?.success && response.data?.data) {
        return response.data;
      }
    } catch (apiError) {
      logger.info('Action windows API not available, generating client-side');
    }

    // Get spray and irrigation windows
    const sprayResponse = await getSprayWindows({ fieldId, days });
    const irrigationResponse = await getIrrigationWindows({ fieldId, days });

    const recommendations: ActionRecommendation[] = [];

    // Create recommendations from spray windows
    if (sprayResponse.success && sprayResponse.data) {
      const optimalSprayWindows = sprayResponse.data
        .filter((w) => w.status === 'optimal')
        .slice(0, 3); // Top 3

      for (const window of optimalSprayWindows) {
        recommendations.push({
          id: `rec-spray-${window.id}`,
          fieldId,
          actionType: 'spray',
          priority: 'medium',
          title: 'Optimal Spray Window Available',
          titleAr: 'نافذة رش مثالية متاحة',
          description: `Excellent conditions for spraying from ${new Date(window.startTime).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric' })}`,
          descriptionAr: `ظروف ممتازة للرش من ${new Date(window.startTime).toLocaleString('ar-EG', { month: 'short', day: 'numeric', hour: 'numeric' })}`,
          window: {
            startTime: window.startTime,
            endTime: window.endTime,
            optimal: true,
          },
          conditions: window.conditions,
          reason: `Wind: ${window.conditions.windSpeed} km/h, Temp: ${window.conditions.temperature}°C, Humidity: ${window.conditions.humidity}%`,
          reasonAr: `الرياح: ${window.conditions.windSpeed} كم/س، الحرارة: ${window.conditions.temperature}°م، الرطوبة: ${window.conditions.humidity}%`,
          benefits: window.recommendations,
          benefitsAr: window.recommendationsAr,
          warnings: window.warnings.length > 0 ? window.warnings : undefined,
          warningsAr: window.warningsAr.length > 0 ? window.warningsAr : undefined,
          confidence: window.score,
          createdAt: new Date().toISOString(),
          expiresAt: window.endTime,
        });
      }
    }

    // Create recommendations from irrigation windows
    if (irrigationResponse.success && irrigationResponse.data) {
      const urgentIrrigation = irrigationResponse.data
        .filter((w) => w.priority === 'urgent' || w.priority === 'high')
        .slice(0, 2); // Top 2

      for (const window of urgentIrrigation) {
        recommendations.push({
          id: `rec-irrigation-${window.id}`,
          fieldId,
          actionType: 'irrigate',
          priority: window.priority,
          title: window.priority === 'urgent' ? 'Urgent Irrigation Required' : 'Irrigation Recommended',
          titleAr: window.priority === 'urgent' ? 'الري العاجل مطلوب' : 'الري موصى به',
          description: `${window.reason.substring(0, 100)}...`,
          descriptionAr: `${window.reasonAr.substring(0, 100)}...`,
          window: {
            startTime: window.startTime,
            endTime: window.endTime,
            optimal: window.status === 'optimal',
          },
          conditions: window.weather,
          reason: window.reason,
          reasonAr: window.reasonAr,
          benefits: window.recommendations,
          benefitsAr: window.recommendationsAr,
          confidence: window.status === 'optimal' ? 90 : 70,
          createdAt: new Date().toISOString(),
          expiresAt: window.endTime,
        });
      }
    }

    // Sort by priority
    const priorityOrder = { urgent: 0, high: 1, medium: 2, low: 3 };
    recommendations.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

    return {
      success: true,
      data: recommendations,
    };
  } catch (error) {
    logger.error('[getActionRecommendations] Request failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : ERROR_MESSAGES.RECOMMENDATIONS_FETCH_FAILED.en,
      error_ar: ERROR_MESSAGES.RECOMMENDATIONS_FETCH_FAILED.ar,
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys for TanStack Query
// ═══════════════════════════════════════════════════════════════════════════

export const actionWindowsKeys = {
  all: ['action-windows'] as const,
  spray: (fieldId: string, days: number) => [...actionWindowsKeys.all, 'spray', fieldId, days] as const,
  irrigation: (fieldId: string, days: number) => [...actionWindowsKeys.all, 'irrigation', fieldId, days] as const,
  recommendations: (fieldId: string, days: number) => [...actionWindowsKeys.all, 'recommendations', fieldId, days] as const,
} as const;
