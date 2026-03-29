/**
 * Home/Dashboard Feature - API Layer
 * طبقة API لميزة لوحة التحكم
 */

import {
  DASHBOARD_ENDPOINTS,
  TASK_ENDPOINTS,
  ALERT_ENDPOINTS,
  buildUrl,
  API_PREFIX,
} from '@sahool/shared-types/contracts';
import { createApiClient, logger } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';

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
    type: 'task' | 'alert' | 'field' | 'weather';
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
    priority: 'high' | 'medium' | 'low';
    status: string;
  }>;
}

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_FAILED: {
    en: 'Failed to fetch dashboard data. Using cached data.',
    ar: 'فشل في جلب بيانات لوحة التحكم. استخدام البيانات المخزنة.',
  },
};

// API Functions
export const dashboardApi = {
  /**
   * Get dashboard data
   */
  getDashboard: async (): Promise<DashboardData> => {
    return safeFetch(DASHBOARD_ENDPOINTS.SUMMARY, async () => {
      const response = await api.get(DASHBOARD_ENDPOINTS.SUMMARY);
      const data = response.data.data || response.data;
      if (data && typeof data === 'object' && 'stats' in data) {
        return data as DashboardData;
      }
      throw new Error('API returned unexpected format');
    });
  },

  /**
   * Get dashboard statistics only
   */
  getStats: async (): Promise<DashboardData['stats']> => {
    return safeFetch(DASHBOARD_ENDPOINTS.STATS, async () => {
      const response = await api.get(DASHBOARD_ENDPOINTS.STATS);
      return response.data.data || response.data;
    });
  },

  /**
   * Get weather data for dashboard
   */
  getWeather: async (): Promise<DashboardData['weather']> => {
    return safeFetch(DASHBOARD_ENDPOINTS.WEATHER_WIDGET, async () => {
      const response = await api.get(DASHBOARD_ENDPOINTS.WEATHER_WIDGET);
      return response.data.data || response.data;
    });
  },

  /**
   * Get recent activity
   */
  getRecentActivity: async (limit: number = 10): Promise<DashboardData['recentActivity']> => {
    return safeFetch(DASHBOARD_ENDPOINTS.RECENT_ACTIVITY, async () => {
      const params = new URLSearchParams();
      params.set('limit', limit.toString());

      const response = await api.get(`${DASHBOARD_ENDPOINTS.RECENT_ACTIVITY}?${params.toString()}`);
      const activity = response.data.data || response.data;

      if (Array.isArray(activity)) {
        return activity;
      }

      throw new Error('API returned unexpected format for activity');
    });
  },

  /**
   * Get upcoming tasks
   */
  getUpcomingTasks: async (limit: number = 5): Promise<DashboardData['upcomingTasks']> => {
    return safeFetch(`${API_PREFIX}/dashboard/tasks/upcoming`, async () => {
      const params = new URLSearchParams();
      params.set('limit', limit.toString());
      params.set('status', 'pending');

      const response = await api.get(`${API_PREFIX}/dashboard/tasks/upcoming?${params.toString()}`);
      const tasks = response.data.data || response.data;

      if (Array.isArray(tasks)) {
        return tasks;
      }

      throw new Error('API returned unexpected format for tasks');
    });
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
    notes?: string
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await api.post(buildUrl(TASK_ENDPOINTS.COMPLETE, { taskId }), {
        notes,
        completedAt: new Date().toISOString(),
      });

      if (response.data.success !== false) {
        return { success: true };
      }

      return {
        success: false,
        error: response.data.error || 'Failed to complete task',
      };
    } catch (error) {
      logger.error('Failed to mark task as complete:', error);
      return { success: false, error: 'Network error while completing task' };
    }
  },

  /**
   * Dismiss an alert
   * تجاهل تنبيه
   */
  dismissAlert: async (
    alertId: string,
    reason?: string
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await api.post(`${buildUrl(ALERT_ENDPOINTS.GET, { alertId })}/dismiss`, {
        reason,
        dismissedAt: new Date().toISOString(),
      });

      if (response.data.success !== false) {
        return { success: true };
      }

      return {
        success: false,
        error: response.data.error || 'Failed to dismiss alert',
      };
    } catch (error) {
      logger.error('Failed to dismiss alert:', error);
      return { success: false, error: 'Network error while dismissing alert' };
    }
  },

  /**
   * Mark activities as read
   * تحديد الأنشطة كمقروءة
   */
  markActivityRead: async (
    activityIds: string[]
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await api.post(`${DASHBOARD_ENDPOINTS.RECENT_ACTIVITY}/mark-read`, {
        activityIds,
      });

      if (response.data.success !== false) {
        return { success: true };
      }

      return {
        success: false,
        error: response.data.error || 'Failed to mark activity as read',
      };
    } catch (error) {
      logger.error('Failed to mark activity as read:', error);
      return { success: false, error: 'Network error while marking activity' };
    }
  },

  /**
   * Acknowledge an alert
   * الإقرار بتنبيه
   */
  acknowledgeAlert: async (alertId: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await api.post(buildUrl(ALERT_ENDPOINTS.ACKNOWLEDGE, { alertId }));

      if (response.data.success !== false) {
        return { success: true };
      }

      return {
        success: false,
        error: response.data.error || 'Failed to acknowledge alert',
      };
    } catch (error) {
      logger.error('Failed to acknowledge alert:', error);
      return {
        success: false,
        error: 'Network error while acknowledging alert',
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
      severity: 'critical' | 'warning' | 'info';
      category: string;
      createdAt: string;
    }>
  > => {
    return safeFetch(DASHBOARD_ENDPOINTS.ALERTS_WIDGET, async () => {
      const params = new URLSearchParams();
      if (options?.limit) params.set('limit', options.limit.toString());
      if (options?.severity) params.set('severity', options.severity);

      const response = await api.get(`${DASHBOARD_ENDPOINTS.ALERTS_WIDGET}?${params.toString()}`);
      const alerts = response.data.data || response.data;

      if (Array.isArray(alerts)) {
        return alerts;
      }

      return [];
    });
  },

  /**
   * Get enhanced stats with trends
   * جلب الإحصائيات المحسنة مع الاتجاهات
   */
  getEnhancedStats: async (): Promise<{
    stats: DashboardData['stats'];
    trends?: {
      fields?: {
        value: number;
        direction: 'up' | 'down' | 'stable';
        percentage: number;
      };
      tasks?: {
        value: number;
        direction: 'up' | 'down' | 'stable';
        percentage: number;
      };
      alerts?: {
        value: number;
        direction: 'up' | 'down' | 'stable';
        percentage: number;
      };
    };
  }> => {
    return safeFetch(`${DASHBOARD_ENDPOINTS.STATS}/enhanced`, async () => {
      const response = await api.get(`${DASHBOARD_ENDPOINTS.STATS}/enhanced`);
      return response.data.data || response.data;
    });
  },
};
