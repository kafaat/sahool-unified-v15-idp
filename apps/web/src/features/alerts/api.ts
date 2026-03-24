/**
 * Alerts Feature - API Layer
 * طبقة API لميزة التنبيهات
 */

import { createApiClient, logger } from '@/lib/api/factory';
import { ALERT_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
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
} from './types';

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

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// ═══════════════════════════════════════════════════════════════════════════
// Error Messages (Bilingual)
// ═══════════════════════════════════════════════════════════════════════════

export const ERROR_MESSAGES: AlertErrorMessages = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_FAILED: {
    en: 'Failed to fetch alerts. Using cached data.',
    ar: 'فشل في جلب التنبيهات. استخدام البيانات المخزنة.',
  },
  CREATE_FAILED: {
    en: 'Failed to create alert.',
    ar: 'فشل في إنشاء التنبيه.',
  },
  UPDATE_FAILED: {
    en: 'Failed to update alert.',
    ar: 'فشل في تحديث التنبيه.',
  },
  DELETE_FAILED: {
    en: 'Failed to delete alert.',
    ar: 'فشل في حذف التنبيه.',
  },
  ACKNOWLEDGE_FAILED: {
    en: 'Failed to acknowledge alert.',
    ar: 'فشل في الإقرار بالتنبيه.',
  },
  RESOLVE_FAILED: {
    en: 'Failed to resolve alert.',
    ar: 'فشل في حل التنبيه.',
  },
  DISMISS_FAILED: {
    en: 'Failed to dismiss alert.',
    ar: 'فشل في تجاهل التنبيه.',
  },
  INVALID_DATA: {
    en: 'Invalid alert data provided.',
    ar: 'بيانات التنبيه المقدمة غير صالحة.',
  },
  NOT_FOUND: {
    en: 'Alert not found.',
    ar: 'التنبيه غير موجود.',
  },
  UNAUTHORIZED: {
    en: 'Unauthorized access to alerts.',
    ar: 'وصول غير مصرح به إلى التنبيهات.',
  },
};

// Mock data for fallback (extracted to separate file for bundle optimization)
import { MOCK_ALERTS, MOCK_STATS, MOCK_COUNT } from './api.mock';

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
        const severities = Array.isArray(filters.severity) ? filters.severity : [filters.severity];
        severities.forEach((s) => params.append('severity', s));
      }

      if (filters?.category) {
        const categories = Array.isArray(filters.category) ? filters.category : [filters.category];
        categories.forEach((c) => params.append('category', c));
      }

      if (filters?.status) {
        const statuses = Array.isArray(filters.status) ? filters.status : [filters.status];
        statuses.forEach((s) => params.append('status', s));
      }

      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.governorate) params.set('governorate', filters.governorate);
      if (filters?.startDate) params.set('start_date', filters.startDate);
      if (filters?.endDate) params.set('end_date', filters.endDate);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`${ALERT_ENDPOINTS.LIST}?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      logger.warn('API returned unexpected format for alerts, using mock data');
      return MOCK_ALERTS;
    } catch (error) {
      logger.warn('Failed to fetch alerts from API, using mock data:', error);
      return MOCK_ALERTS;
    }
  },

  /**
   * Get active alerts count
   * جلب عدد التنبيهات النشطة
   */
  getActiveCount: async (): Promise<AlertCount> => {
    try {
      const response = await api.get(`${ALERT_ENDPOINTS.LIST}/count`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn('Failed to fetch alert count from API, using mock data:', error);
      return MOCK_COUNT;
    }
  },

  /**
   * Get alert by ID
   * جلب تنبيه بواسطة المعرف
   */
  getAlertById: async (id: string): Promise<Alert> => {
    try {
      const response = await api.get(buildUrl(ALERT_ENDPOINTS.GET, { alertId: id }));
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn(`Failed to fetch alert ${id} from API, using mock data:`, error);
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
      const response = await api.post(ALERT_ENDPOINTS.CREATE, payload);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.error('Failed to create alert:', error);
      throw new Error(ERROR_MESSAGES.CREATE_FAILED.en);
    }
  },

  /**
   * Update an alert
   * تحديث تنبيه
   */
  updateAlert: async (id: string, payload: UpdateAlertPayload): Promise<Alert> => {
    try {
      const response = await api.patch(buildUrl(ALERT_ENDPOINTS.GET, { alertId: id }), payload);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.error('Failed to update alert:', error);
      throw new Error(ERROR_MESSAGES.UPDATE_FAILED.en);
    }
  },

  /**
   * Acknowledge alert
   * الإقرار بالتنبيه
   */
  acknowledgeAlert: async (id: string): Promise<Alert> => {
    try {
      const response = await api.post(buildUrl(ALERT_ENDPOINTS.ACKNOWLEDGE, { alertId: id }));
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.error('Failed to acknowledge alert:', error);
      throw new Error(ERROR_MESSAGES.ACKNOWLEDGE_FAILED.en);
    }
  },

  /**
   * Resolve alert
   * حل التنبيه
   */
  resolveAlert: async (id: string, resolution?: string): Promise<Alert> => {
    try {
      const response = await api.post(buildUrl(ALERT_ENDPOINTS.RESOLVE, { alertId: id }), {
        resolution,
        resolvedAt: new Date().toISOString(),
      });
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.error('Failed to resolve alert:', error);
      throw new Error(ERROR_MESSAGES.RESOLVE_FAILED.en);
    }
  },

  /**
   * Dismiss alert
   * تجاهل التنبيه
   */
  dismissAlert: async (id: string, reason?: string): Promise<void> => {
    try {
      await api.post(`${buildUrl(ALERT_ENDPOINTS.GET, { alertId: id })}/dismiss`, {
        reason,
        dismissedAt: new Date().toISOString(),
      });
    } catch (error) {
      logger.error('Failed to dismiss alert:', error);
      throw new Error(ERROR_MESSAGES.DISMISS_FAILED.en);
    }
  },

  /**
   * Delete alert (hard delete)
   * حذف تنبيه (حذف نهائي)
   */
  deleteAlert: async (id: string): Promise<void> => {
    try {
      await api.delete(buildUrl(ALERT_ENDPOINTS.GET, { alertId: id }));
    } catch (error) {
      logger.error('Failed to delete alert:', error);
      throw new Error(ERROR_MESSAGES.DELETE_FAILED.en);
    }
  },

  /**
   * Get alert statistics
   * جلب إحصائيات التنبيهات
   */
  getStats: async (governorate?: string): Promise<AlertStats> => {
    try {
      const params = governorate ? `?governorate=${governorate}` : '';
      const response = await api.get(`${ALERT_ENDPOINTS.LIST}/stats${params}`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.warn('Failed to fetch alert stats from API, using mock data:', error);
      return MOCK_STATS;
    }
  },

  /**
   * Bulk acknowledge alerts
   * الإقرار بالتنبيهات بشكل جماعي
   */
  bulkAcknowledge: async (alertIds: string[]): Promise<{ success: boolean; updated: number }> => {
    try {
      const response = await api.post(`${ALERT_ENDPOINTS.LIST}/bulk/acknowledge`, {
        alertIds,
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to bulk acknowledge alerts:', error);
      throw new Error(ERROR_MESSAGES.ACKNOWLEDGE_FAILED.en);
    }
  },

  /**
   * Bulk dismiss alerts
   * تجاهل التنبيهات بشكل جماعي
   */
  bulkDismiss: async (
    alertIds: string[],
    reason?: string
  ): Promise<{ success: boolean; updated: number }> => {
    try {
      const response = await api.post(`${ALERT_ENDPOINTS.LIST}/bulk/dismiss`, {
        alertIds,
        reason,
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to bulk dismiss alerts:', error);
      throw new Error(ERROR_MESSAGES.DISMISS_FAILED.en);
    }
  },

  /**
   * Subscribe to real-time alerts (returns EventSource URL)
   * الاشتراك في التنبيهات في الوقت الفعلي
   */
  getStreamUrl: (): string => {
    return `${api.defaults.baseURL}${ALERT_ENDPOINTS.LIST}/stream`;
  },
};
