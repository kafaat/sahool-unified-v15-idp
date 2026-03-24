/**
 * Terrain & Hydrology Feature - API Layer
 * طبقة API لميزة التضاريس والمياه
 */

import { createApiClient, logger } from '@/lib/api/factory';
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
    try {
      const response = await api.post(
        TERRAIN_ENDPOINTS.DEM,
        data || { field_id: fieldId },
        data ? { headers: { 'Content-Type': 'multipart/form-data' } } : {}
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to analyze DEM:', error);
      throw new Error(ERROR_MESSAGES.DEM_FAILED.en);
    }
  },

  analyzeSlope: async (fieldId: string): Promise<SlopeAnalysis> => {
    try {
      const response = await api.post(TERRAIN_ENDPOINTS.SLOPE, { field_id: fieldId });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to analyze slope:', error);
      throw new Error(ERROR_MESSAGES.SLOPE_FAILED.en);
    }
  },

  analyzeAspect: async (fieldId: string): Promise<AspectAnalysis> => {
    try {
      const response = await api.post(TERRAIN_ENDPOINTS.ASPECT, { field_id: fieldId });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to analyze aspect:', error);
      throw error;
    }
  },

  analyzeDrainage: async (fieldId: string): Promise<DrainageAnalysis> => {
    try {
      const response = await api.post(TERRAIN_ENDPOINTS.HYDROLOGY_DRAINAGE, { field_id: fieldId });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to analyze drainage:', error);
      throw new Error(ERROR_MESSAGES.DRAINAGE_FAILED.en);
    }
  },

  analyzeWatershed: async (fieldId: string): Promise<WatershedAnalysis> => {
    try {
      const response = await api.post(TERRAIN_ENDPOINTS.HYDROLOGY_WATERSHED, { field_id: fieldId });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to analyze watershed:', error);
      throw error;
    }
  },

  analyzeFlow: async (fieldId: string): Promise<FlowAnalysis> => {
    try {
      const response = await api.post(TERRAIN_ENDPOINTS.HYDROLOGY_FLOW, { field_id: fieldId });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to analyze flow:', error);
      throw error;
    }
  },

  optimizeLeveling: async (fieldId: string, targetSlope?: number): Promise<LevelingPlan> => {
    try {
      const response = await api.post(TERRAIN_ENDPOINTS.LEVELING_OPTIMIZE, {
        field_id: fieldId,
        target_slope: targetSlope,
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to optimize leveling:', error);
      throw new Error(ERROR_MESSAGES.LEVELING_FAILED.en);
    }
  },

  calculateCutFill: async (fieldId: string, targetElevation?: number): Promise<CutFillResult> => {
    try {
      const response = await api.post(TERRAIN_ENDPOINTS.LEVELING_CUT_FILL, {
        field_id: fieldId,
        target_elevation: targetElevation,
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to calculate cut-fill:', error);
      throw error;
    }
  },

  estimateLevelingCost: async (fieldId: string): Promise<LevelingCost> => {
    try {
      const response = await api.post(TERRAIN_ENDPOINTS.LEVELING_COST, { field_id: fieldId });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to estimate leveling cost:', error);
      throw error;
    }
  },
};
