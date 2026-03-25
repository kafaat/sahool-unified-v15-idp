/**
 * Audit Feature - API Layer
 * طبقة API لميزة التدقيق
 */

import { createApiClient, logger } from '@/lib/api/factory';
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

const MOCK_LOGS: AuditLog[] = [
  {
    id: 'log-1',
    action: 'field.created',
    actionAr: 'إنشاء حقل',
    userId: 'user-1',
    userName: 'Ahmad Ali',
    userNameAr: 'أحمد علي',
    resource: 'field',
    resourceId: 'field-1',
    details: "Created field 'North Field'",
    detailsAr: "تم إنشاء الحقل 'الحقل الشمالي'",
    ipAddress: '192.168.1.1',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
  },
  {
    id: 'log-2',
    action: 'user.login',
    actionAr: 'تسجيل دخول',
    userId: 'user-2',
    userName: 'Sara Mohammed',
    userNameAr: 'سارة محمد',
    resource: 'auth',
    resourceId: 'session-1',
    details: 'User logged in successfully',
    detailsAr: 'تم تسجيل الدخول بنجاح',
    ipAddress: '192.168.1.2',
    timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
  },
];

const MOCK_STATS: AuditStats = {
  totalLogs: 1250,
  todayLogs: 45,
  byAction: { 'field.created': 12, 'user.login': 89, 'task.updated': 34 },
  byResource: { field: 120, auth: 450, task: 200 },
  topUsers: [
    { userId: 'user-1', userName: 'Ahmad Ali', count: 120 },
    { userId: 'user-2', userName: 'Sara Mohammed', count: 89 },
  ],
};

export const auditApi = {
  getLogs: async (filters?: AuditFilters): Promise<AuditLog[]> => {
    try {
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
      return MOCK_LOGS;
    } catch (error) {
      logger.warn('Failed to fetch audit logs, using mock data:', error);
      return MOCK_LOGS;
    }
  },

  getLogById: async (id: string): Promise<AuditLog> => {
    try {
      const url = buildUrl(AUDIT_ENDPOINTS.LOG_GET, { logId: id });
      const response = await api.get(url);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch audit log ${id}:`, error);
      const mock = MOCK_LOGS.find((l) => l.id === id);
      if (mock) return mock;
      throw new Error(ERROR_MESSAGES.FETCH_LOGS_FAILED.en);
    }
  },

  getStats: async (): Promise<AuditStats> => {
    try {
      const response = await api.get(AUDIT_ENDPOINTS.STATS);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch audit stats, using mock data:', error);
      return MOCK_STATS;
    }
  },
};
