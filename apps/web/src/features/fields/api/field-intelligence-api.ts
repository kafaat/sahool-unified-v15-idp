/**
 * Field Intelligence API
 * واجهة برمجة التطبيقات لذكاء الحقل
 *
 * Provides API functions for field intelligence features including:
 * - Living Field Score calculation
 * - Field zone analysis
 * - Alert management
 * - Task recommendations
 * - Best days prediction
 * - Date validation
 * - AI-powered recommendations
 */

import { apiClient } from "@/lib/api";
import type { ApiResponse } from "@/lib/api/types";
import { logger } from "@/lib/logger";

// ═══════════════════════════════════════════════════════════════════════════
// Type Definitions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Living Field Score Response
 */
export interface LivingFieldScore {
  fieldId: string;
  overall: number;
  health: number;
  hydration: number;
  attention: number;
  astral: number;
  trend: "improving" | "stable" | "declining";
  trendPercentage?: number;
  lastUpdated: string;
  components: {
    ndvi: {
      value: number;
      category: string;
      categoryAr: string;
      contribution: number;
    };
    soilMoisture: {
      value: number;
      status: string;
      statusAr: string;
      contribution: number;
    };
    taskCompletion: {
      completedTasks: number;
      totalTasks: number;
      overdueTasks: number;
      contribution: number;
    };
    astronomical: {
      moonPhase: string;
      moonPhaseAr: string;
      farmingScore: number;
      contribution: number;
    };
  };
}

/**
 * Field Zone with Health Data
 */
export interface FieldZone {
  id: string;
  fieldId: string;
  name: string;
  nameAr: string;
  polygon: {
    type: "Polygon";
    coordinates: number[][][];
  };
  area: number; // hectares
  healthScore: number;
  ndviValue: number;
  soilMoisture?: number;
  temperature?: number;
  status: "healthy" | "moderate" | "stressed" | "critical";
  statusAr: string;
  recommendations: string[];
  recommendationsAr: string[];
  metadata?: Record<string, unknown>;
  lastUpdated: string;
}

/**
 * Field Alert
 */
export interface FieldAlert {
  id: string;
  fieldId: string;
  fieldName?: string;
  fieldNameAr?: string;
  type:
    | "health"
    | "irrigation"
    | "pest"
    | "disease"
    | "weather"
    | "task"
    | "sensor";
  severity: "info" | "warning" | "critical" | "emergency";
  title: string;
  titleAr: string;
  message: string;
  messageAr: string;
  status: "active" | "acknowledged" | "resolved" | "dismissed";
  threshold?: number;
  currentValue?: number;
  unit?: string;
  actionable: boolean;
  actionUrl?: string;
  relatedTaskId?: string;
  metadata?: Record<string, unknown>;
  createdAt: string;
  acknowledgedAt?: string;
  resolvedAt?: string;
}

/**
 * Task Creation Data from Alert
 */
export interface TaskFromAlertData {
  title: string;
  titleAr: string;
  description?: string;
  descriptionAr?: string;
  priority: "urgent" | "high" | "medium" | "low";
  dueDate?: string;
  assigneeId?: string;
}

/**
 * Created Task Response
 */
export interface CreatedTask {
  id: string;
  fieldId: string;
  alertId: string;
  title: string;
  titleAr: string;
  description?: string;
  descriptionAr?: string;
  priority: string;
  status: string;
  dueDate?: string;
  createdAt: string;
}

/**
 * Best Day for Activity
 */
export interface BestDay {
  date: string;
  score: number;
  suitability: "excellent" | "good" | "moderate" | "poor";
  suitabilityAr: string;
  weather: {
    temperature: number;
    humidity: number;
    precipitation: number;
    windSpeed: number;
    description: string;
    descriptionAr: string;
  };
  astronomical: {
    moonPhase: string;
    moonPhaseAr: string;
    lunarMansion: string;
    lunarMansionAr: string;
    farmingScore: number;
  };
  reasons: string[];
  reasonsAr: string[];
  warnings?: string[];
  warningsAr?: string[];
}

/**
 * Date Validation Response
 */
export interface DateValidation {
  date: string;
  activity: string;
  activityAr: string;
  suitable: boolean;
  score: number;
  rating: "excellent" | "good" | "moderate" | "poor" | "unsuitable";
  ratingAr: string;
  reasons: string[];
  reasonsAr: string[];
  alternatives?: {
    date: string;
    score: number;
    reason: string;
    reasonAr: string;
  }[];
  warnings?: string[];
  warningsAr?: string[];
}

/**
 * AI Recommendation
 */
export interface FieldRecommendation {
  id: string;
  fieldId: string;
  type:
    | "irrigation"
    | "fertilizer"
    | "pest_control"
    | "disease_treatment"
    | "planting"
    | "harvesting"
    | "general";
  priority: "urgent" | "high" | "medium" | "low";
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  confidence: number;
  actionItems: {
    action: string;
    actionAr: string;
    order: number;
    required: boolean;
  }[];
  expectedBenefit?: string;
  expectedBenefitAr?: string;
  estimatedCost?: {
    min: number;
    max: number;
    currency: string;
  };
  timeframe?: {
    start: string;
    end: string;
    urgent: boolean;
  };
  basedOn: string[];
  basedOnAr: string[];
  metadata?: Record<string, unknown>;
  createdAt: string;
  expiresAt?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Error Messages
// ═══════════════════════════════════════════════════════════════════════════

export const INTELLIGENCE_ERROR_MESSAGES = {
  SCORE_FETCH_FAILED: {
    en: "Failed to fetch living field score",
    ar: "فشل في جلب درجة الحقل الحي",
  },
  ZONES_FETCH_FAILED: {
    en: "Failed to fetch field zones",
    ar: "فشل في جلب مناطق الحقل",
  },
  ALERTS_FETCH_FAILED: {
    en: "Failed to fetch field alerts",
    ar: "فشل في جلب تنبيهات الحقل",
  },
  TASK_CREATE_FAILED: {
    en: "Failed to create task from alert",
    ar: "فشل في إنشاء المهمة من التنبيه",
  },
  BEST_DAYS_FETCH_FAILED: {
    en: "Failed to fetch best days for activity",
    ar: "فشل في جلب أفضل الأيام للنشاط",
  },
  DATE_VALIDATION_FAILED: {
    en: "Failed to validate date",
    ar: "فشل في التحقق من التاريخ",
  },
  RECOMMENDATIONS_FETCH_FAILED: {
    en: "Failed to fetch AI recommendations",
    ar: "فشل في جلب توصيات الذكاء الاصطناعي",
  },
  INVALID_FIELD_ID: {
    en: "Invalid field ID provided",
    ar: "معرف الحقل غير صالح",
  },
  INVALID_ALERT_ID: {
    en: "Invalid alert ID provided",
    ar: "معرف التنبيه غير صالح",
  },
  INVALID_ACTIVITY: {
    en: "Invalid activity type",
    ar: "نوع النشاط غير صالح",
  },
  INVALID_DATE: {
    en: "Invalid date format",
    ar: "تنسيق التاريخ غير صالح",
  },
} as const;

// ═══════════════════════════════════════════════════════════════════════════
// API Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Fetch Living Field Score
 * جلب درجة الحقل الحي
 *
 * Calculates a comprehensive score based on NDVI, irrigation, tasks, and astronomical data.
 *
 * @param fieldId - Field ID
 * @returns Living Field Score with component breakdown
 */
export async function fetchLivingFieldScore(
  fieldId: string,
): Promise<ApiResponse<LivingFieldScore>> {
  if (!fieldId || typeof fieldId !== "string" || fieldId.trim().length === 0) {
    return {
      success: false,
      error: INTELLIGENCE_ERROR_MESSAGES.INVALID_FIELD_ID.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.INVALID_FIELD_ID.ar,
    };
  }

  try {
    const response = await apiClient.getLivingFieldScore(fieldId);

    if (!response.success || !response.data) {
      logger.error(
        "[fetchLivingFieldScore] API returned unsuccessful response:",
        response.error,
      );
      return {
        success: false,
        error:
          response.error || INTELLIGENCE_ERROR_MESSAGES.SCORE_FETCH_FAILED.en,
        error_ar: INTELLIGENCE_ERROR_MESSAGES.SCORE_FETCH_FAILED.ar,
      };
    }

    return response as ApiResponse<LivingFieldScore>;
  } catch (error) {
    logger.error("[fetchLivingFieldScore] Request failed:", error);
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : INTELLIGENCE_ERROR_MESSAGES.SCORE_FETCH_FAILED.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.SCORE_FETCH_FAILED.ar,
    };
  }
}

/**
 * Fetch Field Zones with Health Data
 * جلب مناطق الحقل مع بيانات الصحة
 *
 * Retrieves field zones with health metrics, NDVI values, and recommendations.
 *
 * @param fieldId - Field ID
 * @returns Array of field zones with health data
 */
export async function fetchFieldZones(
  fieldId: string,
): Promise<ApiResponse<FieldZone[]>> {
  if (!fieldId || typeof fieldId !== "string" || fieldId.trim().length === 0) {
    return {
      success: false,
      error: INTELLIGENCE_ERROR_MESSAGES.INVALID_FIELD_ID.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.INVALID_FIELD_ID.ar,
    };
  }

  try {
    const response = await apiClient.getFieldZones(fieldId);

    if (!response.success) {
      logger.error(
        "[fetchFieldZones] API returned unsuccessful response:",
        response.error,
      );
      return {
        success: false,
        error:
          response.error || INTELLIGENCE_ERROR_MESSAGES.ZONES_FETCH_FAILED.en,
        error_ar: INTELLIGENCE_ERROR_MESSAGES.ZONES_FETCH_FAILED.ar,
      };
    }

    return {
      success: true,
      data: (response.data || []) as FieldZone[],
    };
  } catch (error) {
    logger.error("[fetchFieldZones] Request failed:", error);
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : INTELLIGENCE_ERROR_MESSAGES.ZONES_FETCH_FAILED.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.ZONES_FETCH_FAILED.ar,
    };
  }
}

/**
 * Fetch Active Alerts for Field
 * جلب التنبيهات النشطة للحقل
 *
 * Retrieves all active alerts for a specific field.
 *
 * @param fieldId - Field ID
 * @returns Array of active field alerts
 */
export async function fetchFieldAlerts(
  fieldId: string,
): Promise<ApiResponse<FieldAlert[]>> {
  if (!fieldId || typeof fieldId !== "string" || fieldId.trim().length === 0) {
    return {
      success: false,
      error: INTELLIGENCE_ERROR_MESSAGES.INVALID_FIELD_ID.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.INVALID_FIELD_ID.ar,
    };
  }

  try {
    const response = await apiClient.getFieldIntelligenceAlerts(fieldId);

    if (!response.success) {
      logger.error(
        "[fetchFieldAlerts] API returned unsuccessful response:",
        response.error,
      );
      return {
        success: false,
        error:
          response.error || INTELLIGENCE_ERROR_MESSAGES.ALERTS_FETCH_FAILED.en,
        error_ar: INTELLIGENCE_ERROR_MESSAGES.ALERTS_FETCH_FAILED.ar,
      };
    }

    return {
      success: true,
      data: (response.data || []) as FieldAlert[],
    };
  } catch (error) {
    logger.error("[fetchFieldAlerts] Request failed:", error);
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : INTELLIGENCE_ERROR_MESSAGES.ALERTS_FETCH_FAILED.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.ALERTS_FETCH_FAILED.ar,
    };
  }
}

/**
 * Create Task from Alert
 * إنشاء مهمة من التنبيه
 *
 * Converts an alert into an actionable task.
 *
 * @param alertId - Alert ID
 * @param taskData - Task creation data
 * @returns Created task
 */
export async function createTaskFromAlert(
  alertId: string,
  taskData: TaskFromAlertData,
): Promise<ApiResponse<CreatedTask>> {
  if (!alertId || typeof alertId !== "string" || alertId.trim().length === 0) {
    return {
      success: false,
      error: INTELLIGENCE_ERROR_MESSAGES.INVALID_ALERT_ID.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.INVALID_ALERT_ID.ar,
    };
  }

  try {
    const response = await apiClient.createTaskFromAlert(alertId, taskData);

    if (!response.success || !response.data) {
      logger.error(
        "[createTaskFromAlert] API returned unsuccessful response:",
        response.error,
      );
      return {
        success: false,
        error:
          response.error || INTELLIGENCE_ERROR_MESSAGES.TASK_CREATE_FAILED.en,
        error_ar: INTELLIGENCE_ERROR_MESSAGES.TASK_CREATE_FAILED.ar,
      };
    }

    return response as ApiResponse<CreatedTask>;
  } catch (error) {
    logger.error("[createTaskFromAlert] Request failed:", error);
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : INTELLIGENCE_ERROR_MESSAGES.TASK_CREATE_FAILED.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.TASK_CREATE_FAILED.ar,
    };
  }
}

/**
 * Fetch Best Days for Activity
 * جلب أفضل الأيام للنشاط
 *
 * Analyzes weather and astronomical conditions to find optimal days for farming activities.
 *
 * @param activity - Activity type (e.g., 'planting', 'irrigation', 'harvesting')
 * @param days - Number of days to analyze (default: 14)
 * @returns Array of best days ranked by suitability
 */
export async function fetchBestDays(
  activity: string,
  days: number = 14,
): Promise<ApiResponse<BestDay[]>> {
  if (
    !activity ||
    typeof activity !== "string" ||
    activity.trim().length === 0
  ) {
    return {
      success: false,
      error: INTELLIGENCE_ERROR_MESSAGES.INVALID_ACTIVITY.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.INVALID_ACTIVITY.ar,
    };
  }

  try {
    const response = await apiClient.getBestDaysForActivity(activity, days);

    if (!response.success) {
      logger.error(
        "[fetchBestDays] API returned unsuccessful response:",
        response.error,
      );
      return {
        success: false,
        error:
          response.error ||
          INTELLIGENCE_ERROR_MESSAGES.BEST_DAYS_FETCH_FAILED.en,
        error_ar: INTELLIGENCE_ERROR_MESSAGES.BEST_DAYS_FETCH_FAILED.ar,
      };
    }

    return {
      success: true,
      data: (response.data || []) as BestDay[],
    };
  } catch (error) {
    logger.error("[fetchBestDays] Request failed:", error);
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : INTELLIGENCE_ERROR_MESSAGES.BEST_DAYS_FETCH_FAILED.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.BEST_DAYS_FETCH_FAILED.ar,
    };
  }
}

/**
 * Validate Task Date
 * التحقق من صلاحية تاريخ المهمة
 *
 * Checks if a specific date is suitable for a farming activity based on weather and astronomical conditions.
 *
 * @param date - Date to validate (ISO 8601 format)
 * @param activity - Activity type
 * @returns Validation result with score and alternative suggestions
 */
export async function validateTaskDate(
  date: string,
  activity: string,
): Promise<ApiResponse<DateValidation>> {
  if (!date || typeof date !== "string") {
    return {
      success: false,
      error: INTELLIGENCE_ERROR_MESSAGES.INVALID_DATE.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.INVALID_DATE.ar,
    };
  }

  if (
    !activity ||
    typeof activity !== "string" ||
    activity.trim().length === 0
  ) {
    return {
      success: false,
      error: INTELLIGENCE_ERROR_MESSAGES.INVALID_ACTIVITY.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.INVALID_ACTIVITY.ar,
    };
  }

  // Validate date format (basic check)
  const parsedDate = new Date(date);
  if (isNaN(parsedDate.getTime())) {
    return {
      success: false,
      error: INTELLIGENCE_ERROR_MESSAGES.INVALID_DATE.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.INVALID_DATE.ar,
    };
  }

  try {
    const response = await apiClient.validateTaskDate(
      parsedDate.toISOString(),
      activity,
    );

    if (!response.success || !response.data) {
      logger.error(
        "[validateTaskDate] API returned unsuccessful response:",
        response.error,
      );
      return {
        success: false,
        error:
          response.error ||
          INTELLIGENCE_ERROR_MESSAGES.DATE_VALIDATION_FAILED.en,
        error_ar: INTELLIGENCE_ERROR_MESSAGES.DATE_VALIDATION_FAILED.ar,
      };
    }

    return response as ApiResponse<DateValidation>;
  } catch (error) {
    logger.error("[validateTaskDate] Request failed:", error);
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : INTELLIGENCE_ERROR_MESSAGES.DATE_VALIDATION_FAILED.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.DATE_VALIDATION_FAILED.ar,
    };
  }
}

/**
 * Fetch AI Field Recommendations
 * جلب توصيات الذكاء الاصطناعي للحقل
 *
 * Retrieves AI-powered recommendations for field management based on current conditions.
 *
 * @param fieldId - Field ID
 * @returns Array of prioritized AI recommendations
 */
export async function fetchFieldRecommendations(
  fieldId: string,
): Promise<ApiResponse<FieldRecommendation[]>> {
  if (!fieldId || typeof fieldId !== "string" || fieldId.trim().length === 0) {
    return {
      success: false,
      error: INTELLIGENCE_ERROR_MESSAGES.INVALID_FIELD_ID.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.INVALID_FIELD_ID.ar,
    };
  }

  try {
    const response = await apiClient.getFieldRecommendations(fieldId);

    if (!response.success) {
      logger.error(
        "[fetchFieldRecommendations] API returned unsuccessful response:",
        response.error,
      );
      return {
        success: false,
        error:
          response.error ||
          INTELLIGENCE_ERROR_MESSAGES.RECOMMENDATIONS_FETCH_FAILED.en,
        error_ar: INTELLIGENCE_ERROR_MESSAGES.RECOMMENDATIONS_FETCH_FAILED.ar,
      };
    }

    return {
      success: true,
      data: (response.data || []) as FieldRecommendation[],
    };
  } catch (error) {
    logger.error("[fetchFieldRecommendations] Request failed:", error);
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : INTELLIGENCE_ERROR_MESSAGES.RECOMMENDATIONS_FETCH_FAILED.en,
      error_ar: INTELLIGENCE_ERROR_MESSAGES.RECOMMENDATIONS_FETCH_FAILED.ar,
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// TanStack Query Key Factory
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Query keys for field intelligence features
 * Use these keys with TanStack Query for caching and invalidation
 */
export const fieldIntelligenceKeys = {
  all: ["field-intelligence"] as const,
  score: (fieldId: string) =>
    [...fieldIntelligenceKeys.all, "score", fieldId] as const,
  zones: (fieldId: string) =>
    [...fieldIntelligenceKeys.all, "zones", fieldId] as const,
  alerts: (fieldId: string) =>
    [...fieldIntelligenceKeys.all, "alerts", fieldId] as const,
  recommendations: (fieldId: string) =>
    [...fieldIntelligenceKeys.all, "recommendations", fieldId] as const,
  bestDays: (activity: string, days: number) =>
    [...fieldIntelligenceKeys.all, "best-days", activity, days] as const,
  dateValidation: (date: string, activity: string) =>
    [...fieldIntelligenceKeys.all, "validate-date", date, activity] as const,
} as const;
