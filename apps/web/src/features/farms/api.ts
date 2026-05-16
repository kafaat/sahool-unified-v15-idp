/**
 * Farms Feature - API Layer
 * طبقة API لميزة المزارع
 */

import { FARM_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import { createApiClient, extractData } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type { Farm, FarmFilters, FarmFormData, FarmStats } from './types';

const api = createApiClient();

/** Normalise backend response to the frontend Farm shape.
 *  The backend uses `totalAreaHectares` / `cultivatedAreaHectares`;
 *  the frontend type uses the shorter `totalAreaHa` / `cultivatedAreaHa`.
 *  Both names are accepted so the mapping survives future renames. */
function mapFarm(raw: any): Farm {
  return {
    ...raw,
    totalAreaHa:      raw.totalAreaHa      ?? raw.totalAreaHectares      ?? 0,
    cultivatedAreaHa: raw.cultivatedAreaHa  ?? raw.cultivatedAreaHectares ?? 0,
    fieldsCount:      raw.fieldsCount       ?? 0,
    cropCount:        raw.cropCount         ?? 0,
    // Ensure nullable string fields are always strings so the UI never crashes
    locationAr:   raw.locationAr   ?? '',
    waterSourceAr: raw.waterSourceAr ?? '',
    nameAr:       raw.nameAr       ?? raw.name ?? '',
  } as Farm;
}

export const farmsApi = {
  getFarms: async (filters?: FarmFilters): Promise<Farm[]> => {
    return safeFetch(FARM_ENDPOINTS.LIST, async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.region) params.set('region', filters.region);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${FARM_ENDPOINTS.LIST}?${params.toString()}`);
      // Backend returns { success, farms: [...], total, page, limit }
      const data = extractData<{ farms: unknown[] } | unknown[]>(response);
      const raw = Array.isArray(data) ? data : (data as { farms: unknown[] }).farms ?? [];
      return raw.map(mapFarm);
    });
  },

  getFarmById: async (id: string): Promise<Farm> => {
    const url = buildUrl(FARM_ENDPOINTS.GET, { farmId: id });
    return safeFetch(url, async () => {
      const response = await api.get(url);
      return mapFarm(extractData<unknown>(response));
    });
  },

  createFarm: async (data: FarmFormData): Promise<Farm> => {
    return safeFetch(FARM_ENDPOINTS.CREATE, async () => {
      // Map frontend field names → backend DTO field names
      const { totalAreaHa, ...rest } = data as FarmFormData & { totalAreaHa?: number };
      const payload = { ...rest, ...(totalAreaHa != null ? { totalAreaHectares: totalAreaHa } : {}) };
      const response = await api.post(FARM_ENDPOINTS.CREATE, payload);
      return extractData<Farm>(response);
    });
  },

  updateFarm: async (id: string, data: Partial<FarmFormData>): Promise<Farm> => {
    const url = buildUrl(FARM_ENDPOINTS.UPDATE, { farmId: id });
    return safeFetch(url, async () => {
      // Map frontend field names → backend DTO field names
      const { totalAreaHa, ...rest } = data as Partial<FarmFormData> & { totalAreaHa?: number };
      const payload = { ...rest, ...(totalAreaHa != null ? { totalAreaHectares: totalAreaHa } : {}) };
      const response = await api.put(url, payload);
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
