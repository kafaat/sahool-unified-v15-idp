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

// Backend audit-service returns snake_case fields from a Python FastAPI service.
// Normalize to the camelCase shape the UI components expect.
interface BackendAuditLog {
  id: string;
  tenant_id?: string;
  user_id?: string;
  user_name?: string;
  user_name_ar?: string;
  action: string;
  action_ar?: string;
  category?: string;
  severity?: string;
  resource_type?: string;
  resource?: string;
  resource_id?: string;
  details?: string | Record<string, unknown>;
  details_ar?: string;
  ip_address?: string;
  metadata?: Record<string, unknown>;
  created_at?: string;
  timestamp?: string;
}

function mapBackendLog(raw: BackendAuditLog): AuditLog {
  const detailsValue = raw.details;
  const detailsStr =
    typeof detailsValue === 'string'
      ? detailsValue
      : detailsValue
        ? JSON.stringify(detailsValue)
        : '';
  return {
    id: raw.id,
    action: raw.action,
    actionAr: raw.action_ar ?? '',
    userId: raw.user_id ?? '',
    userName: raw.user_name ?? '',
    userNameAr: raw.user_name_ar ?? '',
    resource: raw.resource_type ?? raw.resource ?? '',
    resourceId: raw.resource_id ?? '',
    details: detailsStr,
    detailsAr: raw.details_ar ?? '',
    ipAddress: raw.ip_address,
    metadata: raw.metadata,
    timestamp: raw.created_at ?? raw.timestamp ?? new Date().toISOString(),
  };
}

// Backend stats shape from audit-service
interface BackendAuditStats {
  total_events?: number;
  events_by_category?: Record<string, number>;
  events_by_severity?: Record<string, number>;
  failed_events?: number;
  unique_users?: number;
  chain_coverage_percent?: number;
  // Alternate shape (older admin audit endpoint)
  totalLogs?: number;
  todayLogs?: number;
  byAction?: Record<string, number>;
  byResource?: Record<string, number>;
  topUsers?: Array<{ userId: string; userName: string; count: number }>;
}

function mapBackendStats(raw: BackendAuditStats): AuditStats {
  return {
    totalLogs: raw.totalLogs ?? raw.total_events ?? 0,
    todayLogs: raw.todayLogs ?? 0,
    byAction: raw.byAction ?? raw.events_by_category ?? {},
    byResource: raw.byResource ?? {},
    topUsers: raw.topUsers ?? [],
  };
}

export const auditApi = {
  getLogs: async (filters?: AuditFilters): Promise<AuditLog[]> => {
    return safeFetch(AUDIT_ENDPOINTS.LOGS, async () => {
      const params = new URLSearchParams();
      if (filters?.action) params.set('action', filters.action);
      if (filters?.userId) params.set('user_id', filters.userId);
      if (filters?.resource) params.set('resource_type', filters.resource);
      if (filters?.startDate) params.set('start_date', filters.startDate);
      if (filters?.endDate) params.set('end_date', filters.endDate);
      // Backend doesn't support `search`; it's applied client-side in AuditClient.
      // Default page size keeps client memory bounded.
      params.set('limit', '200');

      const response = await api.get(`${AUDIT_ENDPOINTS.LOGS}?${params.toString()}`);
      const body = response.data?.data ?? response.data;
      // Backend returns PaginatedResponse: { items, total, skip, limit, has_more }
      // Older endpoints may return a bare array or { data: [...] }.
      let items: unknown[] = [];
      if (Array.isArray(body)) {
        items = body;
      } else if (body && typeof body === 'object' && Array.isArray((body as { items?: unknown[] }).items)) {
        items = (body as { items: unknown[] }).items;
      }
      return items.map((item) => mapBackendLog(item as BackendAuditLog));
    });
  },

  getLogById: async (id: string): Promise<AuditLog> => {
    return safeFetch(AUDIT_ENDPOINTS.LOG_GET, async () => {
      const url = buildUrl(AUDIT_ENDPOINTS.LOG_GET, { logId: id });
      const response = await api.get(url);
      const raw = (response.data?.data ?? response.data) as BackendAuditLog;
      return mapBackendLog(raw);
    });
  },

  getStats: async (): Promise<AuditStats> => {
    return safeFetch(AUDIT_ENDPOINTS.STATS, async () => {
      const response = await api.get(AUDIT_ENDPOINTS.STATS);
      const raw = (response.data?.data ?? response.data) as BackendAuditStats;
      return mapBackendStats(raw);
    });
  },
};
