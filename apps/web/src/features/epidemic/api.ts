/**
 * Epidemic Feature - API Layer
 * طبقة API لميزة الأوبئة
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { EPIDEMIC_ENDPOINTS } from '@sahool/shared-types/contracts';

// crop-intelligence-service:8095 — endpoint templates from shared contract

const api = createApiClient();

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface Epidemic {
  id: string;
  name: string;
  nameAr: string;
  diseaseType: string;
  affectedCrops: string[];
  severity: 'low' | 'moderate' | 'high' | 'critical';
  status: 'monitoring' | 'active' | 'contained' | 'resolved';
  affectedArea: number;
  reportedAt: string;
  region: string;
  spreadRate: number;
}

export interface EpidemicReport {
  fieldId: string;
  diseaseType: string;
  symptoms: string;
  affectedArea: number;
  imageBase64?: string;
  notes?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// API Functions
// ═══════════════════════════════════════════════════════════════════════════

export const epidemicApi = {
  /**
   * Get all epidemics
   * جلب جميع الأوبئة
   */
  getEpidemics: async (status?: string): Promise<Epidemic[]> => {
    const params = status ? `?status=${encodeURIComponent(status)}` : '';
    const endpoint = `${EPIDEMIC_ENDPOINTS.LIST}${params}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return response.data.data ?? response.data;
    });
  },

  /**
   * Get epidemic by ID
   * جلب وباء بواسطة المعرف
   */
  getEpidemicById: async (id: string): Promise<Epidemic> => {
    const endpoint = EPIDEMIC_ENDPOINTS.GET.replace('{epidemicId}', encodeURIComponent(id));
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return response.data.data ?? response.data;
    });
  },

  /**
   * Report a new epidemic observation
   * الإبلاغ عن ملاحظة وباء جديدة
   */
  reportEpidemic: async (payload: EpidemicReport): Promise<Epidemic> => {
    return safeFetch(EPIDEMIC_ENDPOINTS.REPORT, async () => {
      const response = await api.post(EPIDEMIC_ENDPOINTS.REPORT, payload);
      return response.data.data ?? response.data;
    });
  },
};
