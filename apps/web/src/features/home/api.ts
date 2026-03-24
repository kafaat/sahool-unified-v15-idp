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

// Mock data for fallback (extracted to separate file for bundle optimization)
import { MOCK_DASHBOARD_DATA } from './api.mock';

// API Functions
export const dashboardApi = {
  /**
   * Get dashboard data
   */
  getDashboard: async (): Promise<DashboardData> => {
    try {
      const response = await api.get(DASHBOARD_ENDPOINTS.SUMMARY);

      // Handle different response formats
      const data = response.data.data || response.data;

      // Validate response structure
      if (data && typeof data === 'object' && 'stats' in data) {
        return data as DashboardData;
      }

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_DASHBOARD_DATA;
    } catch (error) {
      logger.warn('Failed to fetch dashboard data from API, using mock data:', error);
      return MOCK_DASHBOARD_DATA;
    }
  },

  /**
   * Get dashboard statistics only
   */
  getStats: async (): Promise<DashboardData['stats']> => {
    try {
      const response = await api.get(DASHBOARD_ENDPOINTS.STATS);
      const stats = response.data.data || response.data;
      return stats;
    } catch (error) {
      logger.warn('Failed to fetch dashboard stats from API, using mock data:', error);
      return MOCK_DASHBOARD_DATA.stats;
    }
  },

  /**
   * Get weather data for dashboard
   */
  getWeather: async (): Promise<DashboardData['weather']> => {
    try {
      const response = await api.get(DASHBOARD_ENDPOINTS.WEATHER_WIDGET);
      const weather = response.data.data || response.data;
      return weather;
    } catch (error) {
      logger.warn('Failed to fetch weather data from API, using mock data:', error);
      return MOCK_DASHBOARD_DATA.weather;
    }
  },

  /**
   * Get recent activity
   */
  getRecentActivity: async (limit: number = 10): Promise<DashboardData['recentActivity']> => {
    try {
      const params = new URLSearchParams();
      params.set('limit', limit.toString());

      const response = await api.get(`${DASHBOARD_ENDPOINTS.RECENT_ACTIVITY}?${params.toString()}`);
      const activity = response.data.data || response.data;

      if (Array.isArray(activity)) {
        return activity;
      }

      logger.warn('API returned unexpected format for activity, using mock data');
      return MOCK_DASHBOARD_DATA.recentActivity;
    } catch (error) {
      logger.warn('Failed to fetch recent activity from API, using mock data:', error);
      return MOCK_DASHBOARD_DATA.recentActivity;
    }
  },

  /**
   * Get upcoming tasks
   */
  getUpcomingTasks: async (limit: number = 5): Promise<DashboardData['upcomingTasks']> => {
    try {
      const params = new URLSearchParams();
      params.set('limit', limit.toString());
      params.set('status', 'pending');

      const response = await api.get(`${API_PREFIX}/dashboard/tasks/upcoming?${params.toString()}`);
      const tasks = response.data.data || response.data;

      if (Array.isArray(tasks)) {
        return tasks;
      }

      logger.warn('API returned unexpected format for tasks, using mock data');
      return MOCK_DASHBOARD_DATA.upcomingTasks;
    } catch (error) {
      logger.warn('Failed to fetch upcoming tasks from API, using mock data:', error);
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
    try {
      const params = new URLSearchParams();
      if (options?.limit) params.set('limit', options.limit.toString());
      if (options?.severity) params.set('severity', options.severity);

      const response = await api.get(`${DASHBOARD_ENDPOINTS.ALERTS_WIDGET}?${params.toString()}`);
      const alerts = response.data.data || response.data;

      if (Array.isArray(alerts)) {
        return alerts;
      }

      return [];
    } catch (error) {
      logger.warn('Failed to fetch alerts from API:', error);
      return [];
    }
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
    try {
      const response = await api.get(`${DASHBOARD_ENDPOINTS.STATS}/enhanced`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn('Failed to fetch enhanced stats, falling back to basic stats:', error);
      return { stats: MOCK_DASHBOARD_DATA.stats };
    }
  },
};
