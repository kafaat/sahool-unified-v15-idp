/**
 * Audit Feature - API Layer
 * طبقة API لميزة التدقيق
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { AUDIT_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import type { AuditLog, AuditStats, AuditFilters } from './types';

const api = createApiClient();

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_LOGS_FAILED: {
    en: 'Failed to fetch audit logs.',
    ar: 'فشل في جلب سجلات التدقيق.',
  },
  FETCH_STATS_FAILED: {
    en: 'Failed to fetch audit statistics.',
    ar: 'فشل في جلب إحصائيات التدقيق.',
  },
};

export const auditApi = {
  getLogs: async (filters?: AuditFilters): Promise<AuditLog[]> => {
    return safeFetch(AUDIT_ENDPOINTS.LOGS, async () => {
      const params = new URLSearchParams();
      if (filters?.action) params.set('action', filters.action);
      if (filters?.userId) params.set('user_id', filters.userId);
      if (filters?.resource) params.set('resource', filters.resource);
      if (filters?.startDate) params.set('start_date', filters.startDate);
      if (filters?.endDate) params.set('end_date', filters.endDate);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`${AUDIT_ENDPOINTS.LOGS}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getLogById: async (id: string): Promise<AuditLog> => {
    return safeFetch(AUDIT_ENDPOINTS.LOG_GET, async () => {
      const url = buildUrl(AUDIT_ENDPOINTS.LOG_GET, { logId: id });
      const response = await api.get(url);
      return response.data.data || response.data;
    });
  },

  getStats: async (): Promise<AuditStats> => {
    return safeFetch(AUDIT_ENDPOINTS.STATS, async () => {
      const response = await api.get(AUDIT_ENDPOINTS.STATS);
      return response.data.data || response.data;
    });
  },
};
