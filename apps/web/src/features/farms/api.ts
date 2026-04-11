/**
 * Farms Feature - API Layer
 * طبقة API لميزة المزارع
 */

import { FARM_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import { createApiClient, extractData } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type { Farm, FarmFilters, FarmFormData, FarmStats } from './types';

const api = createApiClient();

export const farmsApi = {
  getFarms: async (filters?: FarmFilters): Promise<Farm[]> => {
    return safeFetch(FARM_ENDPOINTS.LIST, async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.region) params.set('region', filters.region);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${FARM_ENDPOINTS.LIST}?${params.toString()}`);
      const data = extractData<Farm[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getFarmById: async (id: string): Promise<Farm> => {
    const url = buildUrl(FARM_ENDPOINTS.GET, { farmId: id });
    return safeFetch(url, async () => {
      const response = await api.get(url);
      return extractData<Farm>(response);
    });
  },

  createFarm: async (data: FarmFormData): Promise<Farm> => {
    return safeFetch(FARM_ENDPOINTS.CREATE, async () => {
      const response = await api.post(FARM_ENDPOINTS.CREATE, data);
      return extractData<Farm>(response);
    });
  },

  updateFarm: async (id: string, data: Partial<FarmFormData>): Promise<Farm> => {
    const url = buildUrl(FARM_ENDPOINTS.UPDATE, { farmId: id });
    return safeFetch(url, async () => {
      const response = await api.put(url, data);
      return extractData<Farm>(response);
    });
  },

  deleteFarm: async (id: string): Promise<void> => {
    const url = buildUrl(FARM_ENDPOINTS.DELETE, { farmId: id });
    return safeFetch(url, async () => {
      await api.delete(url);
    });
  },

  getStats: async (): Promise<FarmStats> => {
    return safeFetch(`${FARM_ENDPOINTS.LIST}/stats`, async () => {
      const response = await api.get(`${FARM_ENDPOINTS.LIST}/stats`);
      return extractData<FarmStats>(response);
    });
  },
};
