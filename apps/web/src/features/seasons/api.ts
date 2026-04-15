/**
 * Seasons Feature - API Layer
 * طبقة API لميزة المواسم
 */

import { SEASON_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import { createApiClient, extractData } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type { Season, SeasonFilters, SeasonFormData, SeasonStats } from './types';

const api = createApiClient();

export const seasonsApi = {
  getSeasons: async (filters?: SeasonFilters): Promise<Season[]> => {
    return safeFetch(SEASON_ENDPOINTS.LIST, async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.type) params.set('type', filters.type);
      if (filters?.year) params.set('year', String(filters.year));
      if (filters?.farmId) params.set('farm_id', filters.farmId);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${SEASON_ENDPOINTS.LIST}?${params.toString()}`);
      const data = extractData<Season[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getSeasonById: async (id: string): Promise<Season> => {
    return safeFetch(SEASON_ENDPOINTS.GET, async () => {
      const response = await api.get(buildUrl(SEASON_ENDPOINTS.GET, { seasonId: id }));
      return extractData<Season>(response);
    });
  },

  createSeason: async (data: SeasonFormData): Promise<Season> => {
    return safeFetch(SEASON_ENDPOINTS.CREATE, async () => {
      const response = await api.post(SEASON_ENDPOINTS.CREATE, data);
      return extractData<Season>(response);
    });
  },

  updateSeason: async (id: string, data: Partial<SeasonFormData>): Promise<Season> => {
    return safeFetch(SEASON_ENDPOINTS.UPDATE, async () => {
      const response = await api.put(buildUrl(SEASON_ENDPOINTS.UPDATE, { seasonId: id }), data);
      return extractData<Season>(response);
    });
  },

  deleteSeason: async (id: string): Promise<void> => {
    return safeFetch(SEASON_ENDPOINTS.DELETE, async () => {
      await api.delete(buildUrl(SEASON_ENDPOINTS.DELETE, { seasonId: id }));
    });
  },

  getStats: async (): Promise<SeasonStats> => {
    return safeFetch(`${SEASON_ENDPOINTS.LIST}/stats`, async () => {
      const response = await api.get(`${SEASON_ENDPOINTS.LIST}/stats`);
      return extractData<SeasonStats>(response);
    });
  },
};
