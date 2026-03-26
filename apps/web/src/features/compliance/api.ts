/**
 * Compliance Feature - API Layer
 * طبقة API لميزة الامتثال والجودة
 */

import { COMPLIANCE_ENDPOINTS, API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient, logger } from '@/lib/api/factory';
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

// Mock data for fallback (extracted to separate file for bundle optimization)
import { MOCK_COMPLIANCE, MOCK_CERTIFICATIONS, MOCK_STATS } from './api.mock';

export const complianceApi = {
  getCompliance: async (filters?: ComplianceFilters): Promise<ComplianceItem[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.category) params.set('category', filters.category);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`${COMPLIANCE_ENDPOINTS.CHECKLISTS}?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_COMPLIANCE;
    } catch (error) {
      logger.warn('Failed to fetch compliance data, using mock data:', error);
      return MOCK_COMPLIANCE;
    }
  },

  getComplianceById: async (id: string): Promise<ComplianceItem> => {
    try {
      const response = await api.get(`${API_PREFIX}/compliance/${id}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch compliance item ${id}, using mock data:`, error);
      const mockItem = MOCK_COMPLIANCE.find((c) => c.id === id);
      if (mockItem) return mockItem;
      throw new Error(`Compliance item with ID ${id} not found`);
    }
  },

  updateCompliance: async (id: string, data: Partial<ComplianceItem>): Promise<ComplianceItem> => {
    try {
      const response = await api.put(`${API_PREFIX}/compliance/${id}`, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update compliance item ${id}:`, error);
      throw error;
    }
  },

  getCertifications: async (): Promise<Certification[]> => {
    try {
      const response = await api.get(COMPLIANCE_ENDPOINTS.CERTIFICATES);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      return MOCK_CERTIFICATIONS;
    } catch (error) {
      logger.warn('Failed to fetch certifications, using mock data:', error);
      return MOCK_CERTIFICATIONS;
    }
  },

  getCertificationById: async (id: string): Promise<Certification> => {
    try {
      const response = await api.get(`${COMPLIANCE_ENDPOINTS.CERTIFICATES}/${id}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch certification ${id}, using mock data:`, error);
      const mockCert = MOCK_CERTIFICATIONS.find((c) => c.id === id);
      if (mockCert) return mockCert;
      throw new Error(`Certification with ID ${id} not found`);
    }
  },

  getAuditReports: async (): Promise<AuditReport[]> => {
    try {
      const response = await api.get(COMPLIANCE_ENDPOINTS.AUDITS);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch audit reports:', error);
      return [];
    }
  },

  createAuditReport: async (data: Partial<AuditReport>): Promise<AuditReport> => {
    try {
      const response = await api.post(COMPLIANCE_ENDPOINTS.AUDITS, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to create audit report:', error);
      throw error;
    }
  },

  getStats: async (): Promise<ComplianceStats> => {
    try {
      const response = await api.get(`${API_PREFIX}/compliance/stats`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch compliance stats, using mock data:', error);
      return MOCK_STATS;
    }
  },
};
