/**
 * Alerts Feature - API Layer
 * طبقة API لميزة التنبيهات
 */

import axios from "axios";
import Cookies from "js-cookie";
import { logger } from "@/lib/logger";
import type {
  Alert,
  AlertFilters,
  AlertStats,
  AlertCount,
  CreateAlertPayload,
  UpdateAlertPayload,
  AlertErrorMessages,
  AlertSeverity,
  AlertCategory,
  AlertStatus,
} from "./types";

// Re-export types for convenience
export type {
  Alert,
  AlertSeverity,
  AlertCategory,
  AlertStatus,
  AlertFilters,
  AlertStats,
  CreateAlertPayload,
  UpdateAlertPayload,
};

// ═══════════════════════════════════════════════════════════════════════════
// API Configuration
// ═══════════════════════════════════════════════════════════════════════════

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

// Only warn during development, don't throw during build
if (!API_BASE_URL && typeof window !== "undefined") {
  console.warn("NEXT_PUBLIC_API_URL environment variable is not set");
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000, // 10 seconds timeout
});

// ═══════════════════════════════════════════════════════════════════════════
// Auth Token Interceptor
// ═══════════════════════════════════════════════════════════════════════════

api.interceptors.request.use((config) => {
  // Get token from cookie using secure cookie parser
  if (typeof window !== "undefined") {
    const token = Cookies.get("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// ═══════════════════════════════════════════════════════════════════════════
// Error Messages (Bilingual)
// ═══════════════════════════════════════════════════════════════════════════

export const ERROR_MESSAGES: AlertErrorMessages = {
  NETWORK_ERROR: {
    en: "Network error. Using offline data.",
    ar: "خطأ في الاتصال. استخدام البيانات المحفوظة.",
  },
  FETCH_FAILED: {
    en: "Failed to fetch alerts. Using cached data.",
    ar: "فشل في جلب التنبيهات. استخدام البيانات المخزنة.",
  },
  CREATE_FAILED: {
    en: "Failed to create alert.",
    ar: "فشل في إنشاء التنبيه.",
  },
  UPDATE_FAILED: {
    en: "Failed to update alert.",
    ar: "فشل في تحديث التنبيه.",
  },
  DELETE_FAILED: {
    en: "Failed to delete alert.",
    ar: "فشل في حذف التنبيه.",
  },
  ACKNOWLEDGE_FAILED: {
    en: "Failed to acknowledge alert.",
    ar: "فشل في الإقرار بالتنبيه.",
  },
  RESOLVE_FAILED: {
    en: "Failed to resolve alert.",
    ar: "فشل في حل التنبيه.",
  },
  DISMISS_FAILED: {
    en: "Failed to dismiss alert.",
    ar: "فشل في تجاهل التنبيه.",
  },
  INVALID_DATA: {
    en: "Invalid alert data provided.",
    ar: "بيانات التنبيه المقدمة غير صالحة.",
  },
  NOT_FOUND: {
    en: "Alert not found.",
    ar: "التنبيه غير موجود.",
  },
  UNAUTHORIZED: {
    en: "Unauthorized access to alerts.",
    ar: "وصول غير مصرح به إلى التنبيهات.",
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Mock Data for Fallback
// ═══════════════════════════════════════════════════════════════════════════

const MOCK_ALERTS: Alert[] = [
  {
    id: "alert-1",
    title: "High Temperature Warning",
    titleAr: "تحذير من درجات حرارة عالية",
    message:
      "Temperature expected to exceed 40°C tomorrow. Consider adjusting irrigation schedule.",
    messageAr:
      "من المتوقع أن تتجاوز درجة الحرارة 40 درجة مئوية غداً. يُنصح بتعديل جدول الري.",
    severity: "warning",
    category: "weather",
    status: "active",
    fieldId: "field-1",
    fieldName: "North Field",
    fieldNameAr: "الحقل الشمالي",
    metadata: {
      expectedTemp: 42,
      source: "weather_service",
    },
    createdAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 minutes ago
  },
  {
    id: "alert-2",
    title: "Pest Detection",
    titleAr: "اكتشاف آفات",
    message:
      "Early signs of aphid infestation detected in Field #3. Immediate action recommended.",
    messageAr:
      "تم اكتشاف علامات مبكرة لإصابة بالمن في الحقل رقم 3. يوصى باتخاذ إجراء فوري.",
    severity: "critical",
    category: "pest",
    status: "active",
    fieldId: "field-3",
    fieldName: "East Field",
    fieldNameAr: "الحقل الشرقي",
    metadata: {
      pestType: "aphid",
      severity: "moderate",
      affectedArea: 25,
    },
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
  },
  {
    id: "alert-3",
    title: "Irrigation System Maintenance",
    titleAr: "صيانة نظام الري",
    message:
      "Scheduled maintenance for irrigation system in Field #5 tomorrow at 8 AM.",
    messageAr: "صيانة مجدولة لنظام الري في الحقل رقم 5 غداً الساعة 8 صباحاً.",
    severity: "info",
    category: "irrigation",
    status: "acknowledged",
    fieldId: "field-5",
    fieldName: "South Field",
    fieldNameAr: "الحقل الجنوبي",
    metadata: {
      maintenanceType: "scheduled",
      duration: 120,
    },
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), // 24 hours ago
    acknowledgedAt: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
  },
  {
    id: "alert-4",
    title: "Low Soil Moisture",
    titleAr: "انخفاض رطوبة التربة",
    message:
      "Soil moisture levels below optimal range in Field #2. Irrigation needed.",
    messageAr:
      "مستويات رطوبة التربة أقل من النطاق الأمثل في الحقل رقم 2. يلزم الري.",
    severity: "warning",
    category: "irrigation",
    status: "active",
    fieldId: "field-2",
    fieldName: "West Field",
    fieldNameAr: "الحقل الغربي",
    metadata: {
      currentMoisture: 15,
      optimalRange: "25-35",
    },
    createdAt: new Date(Date.now() - 1000 * 60 * 45).toISOString(), // 45 minutes ago
  },
  {
    id: "alert-5",
    title: "Market Price Update",
    titleAr: "تحديث أسعار السوق",
    message:
      "Coffee prices increased by 15% in the local market. Good time to sell.",
    messageAr: "ارتفعت أسعار البن بنسبة 15% في السوق المحلي. وقت جيد للبيع.",
    severity: "info",
    category: "market",
    status: "active",
    metadata: {
      priceChange: 15,
      crop: "coffee",
      market: "local",
    },
    createdAt: new Date(Date.now() - 1000 * 60 * 15).toISOString(), // 15 minutes ago
  },
];

const MOCK_STATS: AlertStats = {
  total: 5,
  bySeverity: {
    info: 2,
    warning: 2,
    critical: 1,
    emergency: 0,
  },
  byCategory: {
    crop_health: 0,
    weather: 1,
    irrigation: 2,
    pest: 1,
    disease: 0,
    market: 1,
    system: 0,
  },
  byStatus: {
    active: 4,
    acknowledged: 1,
    resolved: 0,
    dismissed: 0,
  },
  trend: "stable",
  trendPercentage: 0,
};

const MOCK_COUNT: AlertCount = {
  count: 4,
  bySeverity: {
    info: 2,
    warning: 2,
    critical: 1,
    emergency: 0,
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// API Functions
// ═══════════════════════════════════════════════════════════════════════════

export const alertsApi = {
  /**
   * Get all alerts with filters
   * جلب جميع التنبيهات مع الفلاتر
   */
  getAlerts: async (filters?: AlertFilters): Promise<Alert[]> => {
    try {
      const params = new URLSearchParams();

      if (filters?.severity) {
        const severities = Array.isArray(filters.severity)
          ? filters.severity
          : [filters.severity];
        severities.forEach((s) => params.append("severity", s));
      }

      if (filters?.category) {
        const categories = Array.isArray(filters.category)
          ? filters.category
          : [filters.category];
        categories.forEach((c) => params.append("category", c));
      }

      if (filters?.status) {
        const statuses = Array.isArray(filters.status)
          ? filters.status
          : [filters.status];
        statuses.forEach((s) => params.append("status", s));
      }

      if (filters?.fieldId) params.set("field_id", filters.fieldId);
      if (filters?.governorate) params.set("governorate", filters.governorate);
      if (filters?.startDate) params.set("start_date", filters.startDate);
      if (filters?.endDate) params.set("end_date", filters.endDate);
      if (filters?.search) params.set("search", filters.search);

      const response = await api.get(`/api/v1/alerts?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      logger.warn("API returned unexpected format for alerts, using mock data");
      return MOCK_ALERTS;
    } catch (error) {
      logger.warn("Failed to fetch alerts from API, using mock data:", error);
      return MOCK_ALERTS;
    }
  },

  /**
   * Get active alerts count
   * جلب عدد التنبيهات النشطة
   */
  getActiveCount: async (): Promise<AlertCount> => {
    try {
      const response = await api.get("/api/v1/alerts/count");
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn(
        "Failed to fetch alert count from API, using mock data:",
        error,
      );
      return MOCK_COUNT;
    }
  },

  /**
   * Get alert by ID
   * جلب تنبيه بواسطة المعرف
   */
  getAlertById: async (id: string): Promise<Alert> => {
    try {
      const response = await api.get(`/api/v1/alerts/${id}`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn(
        `Failed to fetch alert ${id} from API, using mock data:`,
        error,
      );
      const mockAlert = MOCK_ALERTS.find((a) => a.id === id);
      if (mockAlert) {
        return mockAlert;
      }
      throw new Error(ERROR_MESSAGES.NOT_FOUND.en);
    }
  },

  /**
   * Create a new alert
   * إنشاء تنبيه جديد
   */
  createAlert: async (payload: CreateAlertPayload): Promise<Alert> => {
    try {
      const response = await api.post("/api/v1/alerts", payload);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.error("Failed to create alert:", error);
      throw new Error(ERROR_MESSAGES.CREATE_FAILED.en);
    }
  },

  /**
   * Update an alert
   * تحديث تنبيه
   */
  updateAlert: async (
    id: string,
    payload: UpdateAlertPayload,
  ): Promise<Alert> => {
    try {
      const response = await api.patch(`/api/v1/alerts/${id}`, payload);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.error("Failed to update alert:", error);
      throw new Error(ERROR_MESSAGES.UPDATE_FAILED.en);
    }
  },

  /**
   * Acknowledge alert
   * الإقرار بالتنبيه
   */
  acknowledgeAlert: async (id: string): Promise<Alert> => {
    try {
      const response = await api.post(`/api/v1/alerts/${id}/acknowledge`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.error("Failed to acknowledge alert:", error);
      throw new Error(ERROR_MESSAGES.ACKNOWLEDGE_FAILED.en);
    }
  },

  /**
   * Resolve alert
   * حل التنبيه
   */
  resolveAlert: async (id: string, resolution?: string): Promise<Alert> => {
    try {
      const response = await api.post(`/api/v1/alerts/${id}/resolve`, {
        resolution,
        resolvedAt: new Date().toISOString(),
      });
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.error("Failed to resolve alert:", error);
      throw new Error(ERROR_MESSAGES.RESOLVE_FAILED.en);
    }
  },

  /**
   * Dismiss alert
   * تجاهل التنبيه
   */
  dismissAlert: async (id: string, reason?: string): Promise<void> => {
    try {
      await api.post(`/api/v1/alerts/${id}/dismiss`, {
        reason,
        dismissedAt: new Date().toISOString(),
      });
    } catch (error) {
      logger.error("Failed to dismiss alert:", error);
      throw new Error(ERROR_MESSAGES.DISMISS_FAILED.en);
    }
  },

  /**
   * Delete alert (hard delete)
   * حذف تنبيه (حذف نهائي)
   */
  deleteAlert: async (id: string): Promise<void> => {
    try {
      await api.delete(`/api/v1/alerts/${id}`);
    } catch (error) {
      logger.error("Failed to delete alert:", error);
      throw new Error(ERROR_MESSAGES.DELETE_FAILED.en);
    }
  },

  /**
   * Get alert statistics
   * جلب إحصائيات التنبيهات
   */
  getStats: async (governorate?: string): Promise<AlertStats> => {
    try {
      const params = governorate ? `?governorate=${governorate}` : "";
      const response = await api.get(`/api/v1/alerts/stats${params}`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn(
        "Failed to fetch alert stats from API, using mock data:",
        error,
      );
      return MOCK_STATS;
    }
  },

  /**
   * Bulk acknowledge alerts
   * الإقرار بالتنبيهات بشكل جماعي
   */
  bulkAcknowledge: async (
    alertIds: string[],
  ): Promise<{ success: boolean; updated: number }> => {
    try {
      const response = await api.post("/api/v1/alerts/bulk/acknowledge", {
        alertIds,
      });
      return response.data;
    } catch (error) {
      logger.error("Failed to bulk acknowledge alerts:", error);
      throw new Error(ERROR_MESSAGES.ACKNOWLEDGE_FAILED.en);
    }
  },

  /**
   * Bulk dismiss alerts
   * تجاهل التنبيهات بشكل جماعي
   */
  bulkDismiss: async (
    alertIds: string[],
    reason?: string,
  ): Promise<{ success: boolean; updated: number }> => {
    try {
      const response = await api.post("/api/v1/alerts/bulk/dismiss", {
        alertIds,
        reason,
      });
      return response.data;
    } catch (error) {
      logger.error("Failed to bulk dismiss alerts:", error);
      throw new Error(ERROR_MESSAGES.DISMISS_FAILED.en);
    }
  },

  /**
   * Subscribe to real-time alerts (returns EventSource URL)
   * الاشتراك في التنبيهات في الوقت الفعلي
   */
  getStreamUrl: (): string => {
    return `${api.defaults.baseURL}/api/v1/alerts/stream`;
  },
};
