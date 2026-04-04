/**
 * Epidemic Feature - API Layer
 * طبقة API لميزة الأوبئة
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';

// crop-intelligence-service:8095
const BASE = '/api/v1/epidemics';

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
    const endpoint = `${BASE}${params}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return response.data.data || response.data;
    });
  },

  /**
   * Get epidemic by ID
   * جلب وباء بواسطة المعرف
   */
  getEpidemicById: async (id: string): Promise<Epidemic> => {
    const endpoint = `${BASE}/${encodeURIComponent(id)}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return response.data.data || response.data;
    });
  },

  /**
   * Report a new epidemic observation
   * الإبلاغ عن ملاحظة وباء جديدة
   */
  reportEpidemic: async (payload: EpidemicReport): Promise<Epidemic> => {
    return safeFetch(`${BASE}/report`, async () => {
      const response = await api.post(`${BASE}/report`, payload);
      return response.data.data || response.data;
    });
  },
};
