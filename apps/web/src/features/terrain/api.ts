/**
 * Terrain & Hydrology Feature - API Layer
 * طبقة API لميزة التضاريس والمياه
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { TERRAIN_ENDPOINTS } from '@sahool/shared-types/contracts';
import type {
  DEMAnalysis,
  SlopeAnalysis,
  AspectAnalysis,
  DrainageAnalysis,
  WatershedAnalysis,
  FlowAnalysis,
  LevelingPlan,
  CutFillResult,
  LevelingCost,
} from './types';

const api = createApiClient({ timeout: 60000 });

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Terrain service unavailable.',
    ar: 'خطأ في الاتصال. خدمة التضاريس غير متاحة.',
  },
  DEM_FAILED: {
    en: 'Failed to process DEM data.',
    ar: 'فشل في معالجة بيانات نموذج الارتفاع الرقمي.',
  },
  SLOPE_FAILED: { en: 'Failed to analyze slope.', ar: 'فشل في تحليل الانحدار.' },
  DRAINAGE_FAILED: { en: 'Failed to analyze drainage.', ar: 'فشل في تحليل الصرف.' },
  LEVELING_FAILED: { en: 'Failed to optimize leveling.', ar: 'فشل في تحسين التسوية.' },
};

export const terrainApi = {
  analyzeDEM: async (fieldId: string, data?: FormData): Promise<DEMAnalysis> => {
    return safeFetch(TERRAIN_ENDPOINTS.DEM, async () => {
      const response = await api.post(
        TERRAIN_ENDPOINTS.DEM,
        data || { field_id: fieldId },
        data ? { headers: { 'Content-Type': 'multipart/form-data' } } : {}
      );
      return response.data.data || response.data;
    });
  },

  analyzeSlope: async (fieldId: string): Promise<SlopeAnalysis> => {
    return safeFetch(TERRAIN_ENDPOINTS.SLOPE, async () => {
      const response = await api.post(TERRAIN_ENDPOINTS.SLOPE, { field_id: fieldId });
      return response.data.data || response.data;
    });
  },

  analyzeAspect: async (fieldId: string): Promise<AspectAnalysis> => {
    return safeFetch(TERRAIN_ENDPOINTS.ASPECT, async () => {
      const response = await api.post(TERRAIN_ENDPOINTS.ASPECT, { field_id: fieldId });
      return response.data.data || response.data;
    });
  },

  analyzeDrainage: async (fieldId: string): Promise<DrainageAnalysis> => {
    return safeFetch(TERRAIN_ENDPOINTS.HYDROLOGY_DRAINAGE, async () => {
      const response = await api.post(TERRAIN_ENDPOINTS.HYDROLOGY_DRAINAGE, { field_id: fieldId });
      return response.data.data || response.data;
    });
  },

  analyzeWatershed: async (fieldId: string): Promise<WatershedAnalysis> => {
    return safeFetch(TERRAIN_ENDPOINTS.HYDROLOGY_WATERSHED, async () => {
      const response = await api.post(TERRAIN_ENDPOINTS.HYDROLOGY_WATERSHED, { field_id: fieldId });
      return response.data.data || response.data;
    });
  },

  analyzeFlow: async (fieldId: string): Promise<FlowAnalysis> => {
    return safeFetch(TERRAIN_ENDPOINTS.HYDROLOGY_FLOW, async () => {
      const response = await api.post(TERRAIN_ENDPOINTS.HYDROLOGY_FLOW, { field_id: fieldId });
      return response.data.data || response.data;
    });
  },

  optimizeLeveling: async (fieldId: string, targetSlope?: number): Promise<LevelingPlan> => {
    return safeFetch(TERRAIN_ENDPOINTS.LEVELING_OPTIMIZE, async () => {
      const response = await api.post(TERRAIN_ENDPOINTS.LEVELING_OPTIMIZE, {
        field_id: fieldId,
        target_slope: targetSlope,
      });
      return response.data.data || response.data;
    });
  },

  calculateCutFill: async (fieldId: string, targetElevation?: number): Promise<CutFillResult> => {
    return safeFetch(TERRAIN_ENDPOINTS.LEVELING_CUT_FILL, async () => {
      const response = await api.post(TERRAIN_ENDPOINTS.LEVELING_CUT_FILL, {
        field_id: fieldId,
        target_elevation: targetElevation,
      });
      return response.data.data || response.data;
    });
  },

  estimateLevelingCost: async (fieldId: string): Promise<LevelingCost> => {
    return safeFetch(TERRAIN_ENDPOINTS.LEVELING_COST, async () => {
      const response = await api.post(TERRAIN_ENDPOINTS.LEVELING_COST, { field_id: fieldId });
      return response.data.data || response.data;
    });
  },
};
