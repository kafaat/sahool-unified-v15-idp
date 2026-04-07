/**
 * Yield Feature - API Layer
 * طبقة API لميزة تتبع المحصول
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { YIELD_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';

const api = createApiClient();

export interface YieldRecord {
  id: string;
  fieldId: string;
  fieldName: string;
  cropType: string;
  cropTypeAr: string;
  season: string;
  seasonAr: string;
  expectedYield: number;
  actualYield?: number;
  unit: string;
  harvestDate?: string;
  status: 'growing' | 'harvested' | 'predicted';
}

export interface YieldStats {
  totalFields: number;
  growingCount: number;
  harvestedCount: number;
  averagePerformance: number;
}

export const yieldApi = {
  /**
   * Fetch yield predictions / records
   * جلب سجلات وتنبؤات الإنتاجية
   */
  getPredictions: async (): Promise<YieldRecord[]> => {
    return safeFetch(YIELD_ENDPOINTS.PREDICTIONS, async () => {
      const response = await api.get(YIELD_ENDPOINTS.PREDICTIONS);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Fetch yield history for a specific field
   * جلب سجل الإنتاجية لحقل محدد
   */
  getFieldHistory: async (fieldId: string): Promise<YieldRecord[]> => {
    return safeFetch(YIELD_ENDPOINTS.HISTORY, async () => {
      const url = buildUrl(YIELD_ENDPOINTS.HISTORY, { fieldId });
      const response = await api.get(url);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Request a new yield prediction for a field
   * طلب تنبؤ جديد بالإنتاجية لحقل
   */
  predict: async (fieldId: string): Promise<unknown> => {
    return safeFetch(YIELD_ENDPOINTS.PREDICT, async () => {
      const url = buildUrl(YIELD_ENDPOINTS.PREDICT, { fieldId });
      const response = await api.post(url);
      return response.data.data || response.data;
    });
  },

  /**
   * Fetch profitability data
   * جلب بيانات الربحية
   */
  getProfitability: async (): Promise<unknown> => {
    return safeFetch(YIELD_ENDPOINTS.PROFITABILITY, async () => {
      const response = await api.get(YIELD_ENDPOINTS.PROFITABILITY);
      return response.data.data || response.data;
    });
  },
};
