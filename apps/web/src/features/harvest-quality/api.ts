/**
 * Harvest Quality Feature - API Layer
 * طبقة API لميزة جودة الحصاد
 */

import { API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient, extractData } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type {
  QualityTestRecord,
  QualityStandard,
  BuyerMatch,
  GradePriceMatrix,
  PriceCalculation,
  QualityTrend,
  HarvestQualityFilters,
  QualityTestFormData,
  HarvestQualityStats,
} from './types';

const api = createApiClient();
const BASE = `${API_PREFIX}/harvest-quality`;

function appendQuery(baseUrl: string, params: URLSearchParams): string {
  const qs = params.toString();
  return qs ? `${baseUrl}?${qs}` : baseUrl;
}

export const harvestQualityApi = {
  getTestRecords: async (filters?: HarvestQualityFilters): Promise<QualityTestRecord[]> => {
    return safeFetch(`${BASE}/tests`, async () => {
      const params = new URLSearchParams();
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.cropCategory) params.set('crop_category', filters.cropCategory);
      if (filters?.grade) params.set('grade', filters.grade);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
      if (filters?.dateTo) params.set('date_to', filters.dateTo);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(appendQuery(`${BASE}/tests`, params));
      const data = extractData<QualityTestRecord[]>(response);
      return Array.isArray(data) ? data : [];
    });
  },

  getTestRecord: async (id: string): Promise<QualityTestRecord> => {
    return safeFetch(`${BASE}/tests/${id}`, async () => {
      const response = await api.get(`${BASE}/tests/${encodeURIComponent(id)}`);
      return extractData<QualityTestRecord>(response);
    });
  },

  createTestRecord: async (data: QualityTestFormData): Promise<QualityTestRecord> => {
    return safeFetch(`${BASE}/tests`, async () => {
      const response = await api.post(`${BASE}/tests`, data);
      return extractData<QualityTestRecord>(response);
    });
  },

  getStandards: async (cropType?: string): Promise<QualityStandard[]> => {
    return safeFetch(`${BASE}/standards`, async () => {
      const params = new URLSearchParams();
      if (cropType) params.set('crop_type', cropType);
      const response = await api.get(appendQuery(`${BASE}/standards`, params));
      const data = extractData<QualityStandard[]>(response);
      return Array.isArray(data) ? data : [];
    });
  },

  findBuyerMatches: async (batchId: string): Promise<BuyerMatch[]> => {
    return safeFetch(`${BASE}/buyers/matches`, async () => {
      const response = await api.get(`${BASE}/buyers/matches?batch_id=${encodeURIComponent(batchId)}`);
      const data = extractData<BuyerMatch[]>(response);
      return Array.isArray(data) ? data : [];
    });
  },

  getPriceMatrix: async (cropType: string): Promise<GradePriceMatrix> => {
    return safeFetch(`${BASE}/pricing/matrix`, async () => {
      const response = await api.get(`${BASE}/pricing/matrix?crop_type=${encodeURIComponent(cropType)}`);
      return extractData<GradePriceMatrix>(response);
    });
  },

  calculatePrice: async (batchId: string): Promise<PriceCalculation> => {
    return safeFetch(`${BASE}/pricing/calculate`, async () => {
      const response = await api.post(`${BASE}/pricing/calculate`, { batch_id: batchId });
      return extractData<PriceCalculation>(response);
    });
  },

  getQualityTrends: async (fieldId: string, periodDays?: number): Promise<QualityTrend> => {
    return safeFetch(`${BASE}/trends`, async () => {
      const params = new URLSearchParams({ field_id: fieldId });
      if (periodDays) params.set('period_days', String(periodDays));
      const response = await api.get(appendQuery(`${BASE}/trends`, params));
      return extractData<QualityTrend>(response);
    });
  },

  getStats: async (): Promise<HarvestQualityStats> => {
    return safeFetch(`${BASE}/stats`, async () => {
      const response = await api.get(`${BASE}/stats`);
      return extractData<HarvestQualityStats>(response);
    });
  },
};
