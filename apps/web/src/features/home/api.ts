/**
 * Home/Dashboard Feature - API Layer
 * طبقة API لميزة لوحة التحكم
 */

import axios from "axios";
import { logger } from "@/lib/logger";

/**
 * Dashboard Data Interface
 */
export interface DashboardData {
  stats: {
    totalFields: number;
    activeTasks: number;
    activeAlerts: number;
    completedTasks: number;
  };
  weather: {
    temperature: number;
    humidity: number;
    windSpeed: number;
    condition: string;
    conditionAr: string;
    location?: string;
  } | null;
  recentActivity: Array<{
    id: string;
    type: "task" | "alert" | "field" | "weather";
    title: string;
    titleAr: string;
    description: string;
    descriptionAr: string;
    timestamp: string;
  }>;
  upcomingTasks: Array<{
    id: string;
    title: string;
    titleAr: string;
    dueDate: string;
    priority: "high" | "medium" | "low";
    status: string;
  }>;
}

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

// Add auth token interceptor
// SECURITY: Use js-cookie library for safe cookie parsing instead of manual parsing
import Cookies from "js-cookie";

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

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: "Network error. Using offline data.",
    ar: "خطأ في الاتصال. استخدام البيانات المحفوظة.",
  },
  FETCH_FAILED: {
    en: "Failed to fetch dashboard data. Using cached data.",
    ar: "فشل في جلب بيانات لوحة التحكم. استخدام البيانات المخزنة.",
  },
};

// Mock data for fallback
const MOCK_DASHBOARD_DATA: DashboardData = {
  stats: {
    totalFields: 12,
    activeTasks: 8,
    activeAlerts: 3,
    completedTasks: 45,
  },
  weather: {
    temperature: 28,
    humidity: 65,
    windSpeed: 12,
    condition: "Partly Cloudy",
    conditionAr: "غائم جزئياً",
    location: "صنعاء، اليمن",
  },
  recentActivity: [
    {
      id: "1",
      type: "task",
      title: "Irrigation completed",
      titleAr: "تم إكمال الري",
      description: "Field #3 irrigation completed",
      descriptionAr: "تم إكمال ري الحقل رقم 3",
      timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    },
    {
      id: "2",
      type: "alert",
      title: "Weather alert",
      titleAr: "تنبيه طقس",
      description: "High temperature expected",
      descriptionAr: "من المتوقع درجات حرارة عالية",
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    },
    {
      id: "3",
      type: "field",
      title: "New field added",
      titleAr: "تمت إضافة حقل جديد",
      description: "Field #12 has been registered",
      descriptionAr: "تم تسجيل الحقل رقم 12",
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    },
  ],
  upcomingTasks: [
    {
      id: "1",
      title: "Water Field #3",
      titleAr: "ري الحقل رقم 3",
      dueDate: new Date(Date.now() + 1000 * 60 * 60 * 24).toISOString(),
      priority: "high",
      status: "pending",
    },
    {
      id: "2",
      title: "Fertilize Field #5",
      titleAr: "تسميد الحقل رقم 5",
      dueDate: new Date(Date.now() + 1000 * 60 * 60 * 48).toISOString(),
      priority: "medium",
      status: "pending",
    },
    {
      id: "3",
      title: "Pest inspection",
      titleAr: "فحص الآفات",
      dueDate: new Date(Date.now() + 1000 * 60 * 60 * 72).toISOString(),
      priority: "low",
      status: "pending",
    },
  ],
};

// API Functions
export const dashboardApi = {
  /**
   * Get dashboard data
   */
  getDashboard: async (): Promise<DashboardData> => {
    try {
      const response = await api.get("/api/v1/dashboard");

      // Handle different response formats
      const data = response.data.data || response.data;

      // Validate response structure
      if (data && typeof data === "object" && "stats" in data) {
        return data as DashboardData;
      }

      logger.warn("API returned unexpected format, using mock data");
      return MOCK_DASHBOARD_DATA;
    } catch (error) {
      logger.warn(
        "Failed to fetch dashboard data from API, using mock data:",
        error,
      );
      return MOCK_DASHBOARD_DATA;
    }
  },

  /**
   * Get dashboard statistics only
   */
  getStats: async (): Promise<DashboardData["stats"]> => {
    try {
      const response = await api.get("/api/v1/dashboard/stats");
      const stats = response.data.data || response.data;
      return stats;
    } catch (error) {
      logger.warn(
        "Failed to fetch dashboard stats from API, using mock data:",
        error,
      );
      return MOCK_DASHBOARD_DATA.stats;
    }
  },

  /**
   * Get weather data for dashboard
   */
  getWeather: async (): Promise<DashboardData["weather"]> => {
    try {
      const response = await api.get("/api/v1/dashboard/weather");
      const weather = response.data.data || response.data;
      return weather;
    } catch (error) {
      logger.warn(
        "Failed to fetch weather data from API, using mock data:",
        error,
      );
      return MOCK_DASHBOARD_DATA.weather;
    }
  },

  /**
   * Get recent activity
   */
  getRecentActivity: async (
    limit: number = 10,
  ): Promise<DashboardData["recentActivity"]> => {
    try {
      const params = new URLSearchParams();
      params.set("limit", limit.toString());

      const response = await api.get(
        `/api/v1/dashboard/activity?${params.toString()}`,
      );
      const activity = response.data.data || response.data;

      if (Array.isArray(activity)) {
        return activity;
      }

      logger.warn(
        "API returned unexpected format for activity, using mock data",
      );
      return MOCK_DASHBOARD_DATA.recentActivity;
    } catch (error) {
      logger.warn(
        "Failed to fetch recent activity from API, using mock data:",
        error,
      );
      return MOCK_DASHBOARD_DATA.recentActivity;
    }
  },

  /**
   * Get upcoming tasks
   */
  getUpcomingTasks: async (
    limit: number = 5,
  ): Promise<DashboardData["upcomingTasks"]> => {
    try {
      const params = new URLSearchParams();
      params.set("limit", limit.toString());
      params.set("status", "pending");

      const response = await api.get(
        `/api/v1/dashboard/tasks/upcoming?${params.toString()}`,
      );
      const tasks = response.data.data || response.data;

      if (Array.isArray(tasks)) {
        return tasks;
      }

      logger.warn("API returned unexpected format for tasks, using mock data");
      return MOCK_DASHBOARD_DATA.upcomingTasks;
    } catch (error) {
      logger.warn(
        "Failed to fetch upcoming tasks from API, using mock data:",
        error,
      );
      return MOCK_DASHBOARD_DATA.upcomingTasks;
    }
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // Mutation Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Mark a task as complete
   * تحديد مهمة كمكتملة
   */
  markTaskComplete: async (
    taskId: string,
    notes?: string,
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await api.post(`/api/v1/tasks/${taskId}/complete`, {
        notes,
        completedAt: new Date().toISOString(),
      });

      if (response.data.success !== false) {
        return { success: true };
      }

      return {
        success: false,
        error: response.data.error || "Failed to complete task",
      };
    } catch (error) {
      logger.error("Failed to mark task as complete:", error);
      return { success: false, error: "Network error while completing task" };
    }
  },

  /**
   * Dismiss an alert
   * تجاهل تنبيه
   */
  dismissAlert: async (
    alertId: string,
    reason?: string,
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await api.post(`/api/v1/alerts/${alertId}/dismiss`, {
        reason,
        dismissedAt: new Date().toISOString(),
      });

      if (response.data.success !== false) {
        return { success: true };
      }

      return {
        success: false,
        error: response.data.error || "Failed to dismiss alert",
      };
    } catch (error) {
      logger.error("Failed to dismiss alert:", error);
      return { success: false, error: "Network error while dismissing alert" };
    }
  },

  /**
   * Mark activities as read
   * تحديد الأنشطة كمقروءة
   */
  markActivityRead: async (
    activityIds: string[],
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await api.post("/api/v1/dashboard/activity/mark-read", {
        activityIds,
      });

      if (response.data.success !== false) {
        return { success: true };
      }

      return {
        success: false,
        error: response.data.error || "Failed to mark activity as read",
      };
    } catch (error) {
      logger.error("Failed to mark activity as read:", error);
      return { success: false, error: "Network error while marking activity" };
    }
  },

  /**
   * Acknowledge an alert
   * الإقرار بتنبيه
   */
  acknowledgeAlert: async (
    alertId: string,
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await api.post(`/api/v1/alerts/${alertId}/acknowledge`);

      if (response.data.success !== false) {
        return { success: true };
      }

      return {
        success: false,
        error: response.data.error || "Failed to acknowledge alert",
      };
    } catch (error) {
      logger.error("Failed to acknowledge alert:", error);
      return {
        success: false,
        error: "Network error while acknowledging alert",
      };
    }
  },

  /**
   * Get dashboard alerts
   * جلب تنبيهات لوحة التحكم
   */
  getAlerts: async (options?: {
    limit?: number;
    severity?: string;
  }): Promise<
    Array<{
      id: string;
      title: string;
      titleAr: string;
      message: string;
      messageAr: string;
      severity: "critical" | "warning" | "info";
      category: string;
      createdAt: string;
    }>
  > => {
    try {
      const params = new URLSearchParams();
      if (options?.limit) params.set("limit", options.limit.toString());
      if (options?.severity) params.set("severity", options.severity);

      const response = await api.get(
        `/api/v1/dashboard/alerts?${params.toString()}`,
      );
      const alerts = response.data.data || response.data;

      if (Array.isArray(alerts)) {
        return alerts;
      }

      return [];
    } catch (error) {
      logger.warn("Failed to fetch alerts from API:", error);
      return [];
    }
  },

  /**
   * Get enhanced stats with trends
   * جلب الإحصائيات المحسنة مع الاتجاهات
   */
  getEnhancedStats: async (): Promise<{
    stats: DashboardData["stats"];
    trends?: {
      fields?: {
        value: number;
        direction: "up" | "down" | "stable";
        percentage: number;
      };
      tasks?: {
        value: number;
        direction: "up" | "down" | "stable";
        percentage: number;
      };
      alerts?: {
        value: number;
        direction: "up" | "down" | "stable";
        percentage: number;
      };
    };
  }> => {
    try {
      const response = await api.get("/api/v1/dashboard/stats/enhanced");
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn(
        "Failed to fetch enhanced stats, falling back to basic stats:",
        error,
      );
      return { stats: MOCK_DASHBOARD_DATA.stats };
    }
  },
};
