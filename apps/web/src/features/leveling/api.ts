/**
 * Leveling Optimizer Feature - API Layer
 * طبقة API لميزة تحسين التسوية
 */

import { createApiClient, logger } from '@/lib/api/factory';
import { TERRAIN_ENDPOINTS } from '@sahool/shared-types/contracts';
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

const LEVELING_BASE = '/api/v1/leveling';

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
    try {
      const response = await api.post(`${LEVELING_BASE}/analyze`, {
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
    } catch (error) {
      logger.error('Failed to analyze field leveling:', error);
      throw new Error(ERROR_MESSAGES.ANALYSIS_FAILED.en);
    }
  },

  /**
   * Get the optimal leveling plan for a field.
   * الحصول على خطة التسوية المثلى للحقل
   */
  getLevelingPlan: async (fieldId: string): Promise<LevelingPlan> => {
    try {
      const response = await api.get(`${LEVELING_BASE}/plan/${fieldId}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to get leveling plan:', error);
      throw new Error(ERROR_MESSAGES.PLAN_FAILED.en);
    }
  },

  /**
   * Get detailed cost estimation for leveling operation.
   * الحصول على تقدير التكلفة المفصل لعملية التسوية
   */
  getCostEstimation: async (params: CostEstimationParams): Promise<CostEstimation> => {
    try {
      const response = await api.get(`${LEVELING_BASE}/cost/${params.fieldId}`, {
        params: {
          cut_volume_m3: params.cutVolumeM3,
          fill_volume_m3: params.fillVolumeM3,
          field_area_hectares: params.fieldAreaHectares,
          haul_distance_m: params.haulDistanceM,
        },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to estimate leveling cost:', error);
      throw new Error(ERROR_MESSAGES.COST_FAILED.en);
    }
  },

  /**
   * Get equipment recommendations for leveling operation.
   * الحصول على توصيات المعدات لعملية التسوية
   */
  getEquipmentRecommendations: async (
    params: EquipmentRecommendationParams
  ): Promise<EquipmentRecommendation[]> => {
    try {
      const response = await api.get(`${LEVELING_BASE}/equipment/${params.fieldId}`, {
        params: {
          total_volume_m3: params.totalVolumeM3,
          haul_distance_m: params.haulDistanceM,
          method: params.method,
        },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to get equipment recommendations:', error);
      throw new Error(ERROR_MESSAGES.EQUIPMENT_FAILED.en);
    }
  },

  /**
   * Simulate a leveling scenario and return predicted results.
   * محاكاة سيناريو التسوية وإرجاع النتائج المتوقعة
   */
  simulateLeveling: async (request: LevelingSimulationRequest): Promise<LevelingSimulation> => {
    try {
      const response = await api.post(`${LEVELING_BASE}/simulate`, {
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
    } catch (error) {
      logger.error('Failed to simulate leveling:', error);
      throw new Error(ERROR_MESSAGES.SIMULATION_FAILED.en);
    }
  },
};
