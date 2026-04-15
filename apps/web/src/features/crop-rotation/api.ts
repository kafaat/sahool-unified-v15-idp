/**
 * Crop Rotation Feature - API Layer
 * طبقة API لميزة الدورة الزراعية
 */

import { API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient, extractData } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type {
  CropCharacteristics,
  CropRotationFilters,
  CropRotationStats,
  CropType,
  FieldRotationHistory,
  MultiYearPlan,
  PestBreakRecommendation,
  RotationPlan,
  RotationPlanFormData,
  RotationRecommendation,
  SoilHealthReport,
} from './types';

const api = createApiClient();
const BASE = `${API_PREFIX}/crop-rotation`;

function appendQuery(baseUrl: string, params: URLSearchParams): string {
  const qs = params.toString();
  return qs ? `${baseUrl}?${qs}` : baseUrl;
}

export const cropRotationApi = {
  // ── Plans CRUD ─────────────────────────────────────────────────

  getPlans: async (filters?: CropRotationFilters): Promise<RotationPlan[]> => {
    return safeFetch(`${BASE}/plans`, async () => {
      const params = new URLSearchParams();
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.season) params.set('season', filters.season);
      if (filters?.cropType) params.set('crop_type', filters.cropType);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(appendQuery(`${BASE}/plans`, params));
      const data = extractData<RotationPlan[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getPlan: async (id: string): Promise<RotationPlan> => {
    return safeFetch(`${BASE}/plans/${id}`, async () => {
      const response = await api.get(`${BASE}/plans/${encodeURIComponent(id)}`);
      return extractData<RotationPlan>(response);
    });
  },

  createPlan: async (data: RotationPlanFormData): Promise<RotationPlan> => {
    return safeFetch(`${BASE}/plans`, async () => {
      const response = await api.post(`${BASE}/plans`, data);
      return extractData<RotationPlan>(response);
    });
  },

  updatePlan: async (
    id: string,
    data: Partial<RotationPlanFormData>,
  ): Promise<RotationPlan> => {
    return safeFetch(`${BASE}/plans/${id}`, async () => {
      const response = await api.put(
        `${BASE}/plans/${encodeURIComponent(id)}`,
        data,
      );
      return extractData<RotationPlan>(response);
    });
  },

  deletePlan: async (id: string): Promise<void> => {
    return safeFetch(`${BASE}/plans/${id}`, async () => {
      await api.delete(`${BASE}/plans/${encodeURIComponent(id)}`);
    });
  },

  // ── Recommendations & Intelligence ─────────────────────────────

  getRecommendation: async (
    fieldId: string,
    currentCrop?: CropType,
  ): Promise<RotationRecommendation[]> => {
    return safeFetch(`${BASE}/recommend`, async () => {
      const params = new URLSearchParams({ field_id: fieldId });
      if (currentCrop) params.set('current_crop', currentCrop);
      const response = await api.get(appendQuery(`${BASE}/recommend`, params));
      const data = extractData<RotationRecommendation[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getMultiYearPlan: async (
    fieldId: string,
    durationYears: number,
  ): Promise<MultiYearPlan> => {
    return safeFetch(`${BASE}/multi-year-plan`, async () => {
      const response = await api.post(`${BASE}/multi-year-plan`, {
        field_id: fieldId,
        duration_years: durationYears,
      });
      return extractData<MultiYearPlan>(response);
    });
  },

  // ── History & Analysis ─────────────────────────────────────────

  getFieldHistory: async (fieldId: string): Promise<FieldRotationHistory> => {
    return safeFetch(`${BASE}/history`, async () => {
      const params = new URLSearchParams({ field_id: fieldId });
      const response = await api.get(appendQuery(`${BASE}/history`, params));
      return extractData<FieldRotationHistory>(response);
    });
  },

  getPestBreakRecommendation: async (
    fieldId: string,
    currentCrop: CropType,
  ): Promise<PestBreakRecommendation> => {
    return safeFetch(`${BASE}/pest-break`, async () => {
      const params = new URLSearchParams({
        field_id: fieldId,
        current_crop: currentCrop,
      });
      const response = await api.get(appendQuery(`${BASE}/pest-break`, params));
      return extractData<PestBreakRecommendation>(response);
    });
  },

  getSoilHealthReport: async (fieldId: string): Promise<SoilHealthReport> => {
    return safeFetch(`${BASE}/soil-health`, async () => {
      const params = new URLSearchParams({ field_id: fieldId });
      const response = await api.get(
        appendQuery(`${BASE}/soil-health`, params),
      );
      return extractData<SoilHealthReport>(response);
    });
  },

  // ── Reference Data ─────────────────────────────────────────────

  getCropCharacteristics: async (
    cropType?: CropType,
  ): Promise<CropCharacteristics[]> => {
    return safeFetch(`${BASE}/crops`, async () => {
      const params = new URLSearchParams();
      if (cropType) params.set('crop_type', cropType);
      const response = await api.get(appendQuery(`${BASE}/crops`, params));
      const data = extractData<CropCharacteristics[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  // ── Stats ──────────────────────────────────────────────────────

  getStats: async (): Promise<CropRotationStats> => {
    return safeFetch(`${BASE}/stats`, async () => {
      const response = await api.get(`${BASE}/stats`);
      return extractData<CropRotationStats>(response);
    });
  },
};
