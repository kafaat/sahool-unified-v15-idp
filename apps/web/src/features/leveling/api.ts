/**
 * Leveling Optimizer Feature - API Layer
 * طبقة API لميزة تحسين التسوية
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { LEVELING_ENDPOINTS } from '@sahool/shared-types/contracts';
import type {
  LevelingAnalysis,
  LevelingAnalysisRequest,
  LevelingPlan,
  CostEstimation,
  CostEstimationParams,
  EquipmentRecommendation,
  EquipmentRecommendationParams,
  LevelingSimulation,
  LevelingSimulationRequest,
} from './types';

const api = createApiClient({ timeout: 60000 });

// Endpoint templates from shared contract — see LEVELING_ENDPOINTS

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Leveling optimizer service unavailable.',
    ar: 'خطأ في الاتصال. خدمة تحسين التسوية غير متاحة.',
  },
  ANALYSIS_FAILED: {
    en: 'Failed to analyze field for leveling.',
    ar: 'فشل في تحليل الحقل للتسوية.',
  },
  PLAN_FAILED: {
    en: 'Failed to retrieve leveling plan.',
    ar: 'فشل في استرجاع خطة التسوية.',
  },
  COST_FAILED: {
    en: 'Failed to estimate leveling cost.',
    ar: 'فشل في تقدير تكلفة التسوية.',
  },
  EQUIPMENT_FAILED: {
    en: 'Failed to get equipment recommendations.',
    ar: 'فشل في الحصول على توصيات المعدات.',
  },
  SIMULATION_FAILED: {
    en: 'Failed to simulate leveling scenario.',
    ar: 'فشل في محاكاة سيناريو التسوية.',
  },
};

export const levelingApi = {
  /**
   * Analyze a field for leveling requirements and generate an optimal plan.
   * تحليل الحقل لمتطلبات التسوية وإنشاء خطة مثالية
   */
  analyzeFieldLeveling: async (request: LevelingAnalysisRequest): Promise<LevelingAnalysis> => {
    return safeFetch(LEVELING_ENDPOINTS.ANALYZE, async () => {
      const response = await api.post(LEVELING_ENDPOINTS.ANALYZE, {
        field_id: request.fieldId,
        elevation_points: request.elevationPoints.map((p) => ({
          x: p.x,
          y: p.y,
          elevation: p.elevation,
          point_id: p.pointId,
        })),
        boundary: request.boundary,
        soil_type: request.soilType,
        target_grade_x: request.targetGradeX,
        target_grade_y: request.targetGradeY,
        method: request.method,
        priority: request.priority,
        include_cost_estimate: request.includeCostEstimate,
      });
      return response.data.data || response.data;
    });
  },

  /**
   * Get the optimal leveling plan for a field.
   * الحصول على خطة التسوية المثلى للحقل
   */
  getLevelingPlan: async (fieldId: string): Promise<LevelingPlan> => {
    const endpoint = LEVELING_ENDPOINTS.PLAN.replace('{fieldId}', fieldId);
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return response.data.data || response.data;
    });
  },

  /**
   * Get detailed cost estimation for leveling operation.
   * الحصول على تقدير التكلفة المفصل لعملية التسوية
   */
  getCostEstimation: async (params: CostEstimationParams): Promise<CostEstimation> => {
    const endpoint = LEVELING_ENDPOINTS.COST.replace('{fieldId}', params.fieldId);
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint, {
        params: {
          cut_volume_m3: params.cutVolumeM3,
          fill_volume_m3: params.fillVolumeM3,
          field_area_hectares: params.fieldAreaHectares,
          haul_distance_m: params.haulDistanceM,
        },
      });
      return response.data.data || response.data;
    });
  },

  /**
   * Get equipment recommendations for leveling operation.
   * الحصول على توصيات المعدات لعملية التسوية
   */
  getEquipmentRecommendations: async (
    params: EquipmentRecommendationParams
  ): Promise<EquipmentRecommendation[]> => {
    const endpoint = LEVELING_ENDPOINTS.EQUIPMENT.replace('{fieldId}', params.fieldId);
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint, {
        params: {
          total_volume_m3: params.totalVolumeM3,
          haul_distance_m: params.haulDistanceM,
          method: params.method,
        },
      });
      return response.data.data || response.data;
    });
  },

  /**
   * Simulate a leveling scenario and return predicted results.
   * محاكاة سيناريو التسوية وإرجاع النتائج المتوقعة
   */
  simulateLeveling: async (request: LevelingSimulationRequest): Promise<LevelingSimulation> => {
    return safeFetch(LEVELING_ENDPOINTS.SIMULATE, async () => {
      const response = await api.post(LEVELING_ENDPOINTS.SIMULATE, {
        field_id: request.fieldId,
        elevation_points: request.elevationPoints.map((p) => ({
          x: p.x,
          y: p.y,
          elevation: p.elevation,
          point_id: p.pointId,
        })),
        target_elevation: request.targetElevation,
        target_grade_x: request.targetGradeX,
        target_grade_y: request.targetGradeY,
        soil_type: request.soilType,
        method: request.method,
      });
      return response.data.data || response.data;
    });
  },
};
