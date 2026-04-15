/**
 * Compliance Feature - API Layer
 * طبقة API لميزة الامتثال والجودة
 */

import { COMPLIANCE_ENDPOINTS, API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type {
  ComplianceItem,
  Certification,
  AuditReport,
  ComplianceFilters,
  ComplianceStats,
} from './types';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_FAILED: {
    en: 'Failed to fetch compliance data.',
    ar: 'فشل في جلب بيانات الامتثال.',
  },
};

export const complianceApi = {
  getCompliance: async (filters?: ComplianceFilters): Promise<ComplianceItem[]> => {
    return safeFetch(COMPLIANCE_ENDPOINTS.CHECKLISTS, async () => {
      const params = new URLSearchParams();
      if (filters?.category) params.set('category', filters.category);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`${COMPLIANCE_ENDPOINTS.CHECKLISTS}?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      return [];
    });
  },

  getComplianceById: async (id: string): Promise<ComplianceItem> => {
    return safeFetch(`${API_PREFIX}/compliance/${id}`, async () => {
      const response = await api.get(`${API_PREFIX}/compliance/${id}`);
      return response.data.data || response.data;
    });
  },

  updateCompliance: async (id: string, data: Partial<ComplianceItem>): Promise<ComplianceItem> => {
    return safeFetch(`${API_PREFIX}/compliance/${id}`, async () => {
      const response = await api.put(`${API_PREFIX}/compliance/${id}`, data);
      return response.data.data || response.data;
    });
  },

  getCertifications: async (): Promise<Certification[]> => {
    return safeFetch(COMPLIANCE_ENDPOINTS.CERTIFICATES, async () => {
      const response = await api.get(COMPLIANCE_ENDPOINTS.CERTIFICATES);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      return [];
    });
  },

  getCertificationById: async (id: string): Promise<Certification> => {
    return safeFetch(`${COMPLIANCE_ENDPOINTS.CERTIFICATES}/${id}`, async () => {
      const response = await api.get(`${COMPLIANCE_ENDPOINTS.CERTIFICATES}/${id}`);
      return response.data.data || response.data;
    });
  },

  getAuditReports: async (): Promise<AuditReport[]> => {
    return safeFetch(COMPLIANCE_ENDPOINTS.AUDITS, async () => {
      const response = await api.get(COMPLIANCE_ENDPOINTS.AUDITS);
      return response.data.data || response.data;
    });
  },

  createAuditReport: async (data: Partial<AuditReport>): Promise<AuditReport> => {
    return safeFetch(COMPLIANCE_ENDPOINTS.AUDITS, async () => {
      const response = await api.post(COMPLIANCE_ENDPOINTS.AUDITS, data);
      return response.data.data || response.data;
    });
  },

  getStats: async (): Promise<ComplianceStats> => {
    return safeFetch(`${API_PREFIX}/compliance/stats`, async () => {
      const response = await api.get(`${API_PREFIX}/compliance/stats`);
      return response.data.data || response.data;
    });
  },
};
