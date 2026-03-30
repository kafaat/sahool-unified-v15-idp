/**
 * Hydrology Feature - API Layer
 * طبقة API لميزة الهيدرولوجيا
 */

import { createApiClient, logger } from '@/lib/api/factory';
import type {
  HydrologyAnalysisResult,
  HydrologyAnalysisParams,
  DrainageAnalysis,
  DrainageParams,
  WetnessAnalysis,
  WetnessParams,
  DepressionAnalysis,
  DepressionParams,
  StreamNetwork,
  StreamParams,
  BasinDelineation,
  BasinParams,
} from './types';

const api = createApiClient({ timeout: 60000 });

// ═══════════════════════════════════════════════════════════════════════════
// Endpoint Constants - ثوابت نقاط النهاية
// ═══════════════════════════════════════════════════════════════════════════

const HYDROLOGY_ENDPOINTS = {
  ANALYZE: '/api/v1/hydrology/analyze',
  DRAINAGE: '/api/v1/hydrology/drainage',
  WETNESS: '/api/v1/hydrology/wetness',
  DEPRESSIONS: '/api/v1/hydrology/depressions',
  STREAMS: '/api/v1/hydrology/streams',
  BASINS: '/api/v1/hydrology/basins',
} as const;

// ═══════════════════════════════════════════════════════════════════════════
// Error Messages - رسائل الخطأ
// ═══════════════════════════════════════════════════════════════════════════

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Hydrology service unavailable.',
    ar: 'خطأ في الاتصال. خدمة الهيدرولوجيا غير متاحة.',
  },
  ANALYSIS_FAILED: {
    en: 'Failed to run hydrology analysis.',
    ar: 'فشل في تشغيل التحليل الهيدرولوجي.',
  },
  DRAINAGE_FAILED: {
    en: 'Failed to analyze drainage network.',
    ar: 'فشل في تحليل شبكة التصريف.',
  },
  WETNESS_FAILED: {
    en: 'Failed to analyze wetness.',
    ar: 'فشل في تحليل الرطوبة.',
  },
  DEPRESSIONS_FAILED: {
    en: 'Failed to identify depressions.',
    ar: 'فشل في تحديد المنخفضات.',
  },
  STREAMS_FAILED: {
    en: 'Failed to detect streams.',
    ar: 'فشل في كشف المجاري المائية.',
  },
  BASINS_FAILED: {
    en: 'Failed to delineate basins.',
    ar: 'فشل في تحديد الأحواض.',
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// API Client - عميل API
// ═══════════════════════════════════════════════════════════════════════════

export const hydrologyApi = {
  /**
   * Run full hydrology analysis for a field.
   * تشغيل تحليل هيدرولوجي كامل للحقل
   */
  analyzeHydrology: async (params: HydrologyAnalysisParams): Promise<HydrologyAnalysisResult> => {
    try {
      const response = await api.post(HYDROLOGY_ENDPOINTS.ANALYZE, {
        field_id: params.fieldId,
        tenant_id: params.tenantId,
        boundary: params.boundary,
        dem_source: params.demSource,
        resolution_m: params.resolutionM,
        include_rainfall: params.includeRainfall,
        rainfall_period_days: params.rainfallPeriodDays,
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to analyze hydrology:', error);
      throw new Error(ERROR_MESSAGES.ANALYSIS_FAILED.en);
    }
  },

  /**
   * Get drainage network for a field.
   * الحصول على شبكة التصريف للحقل
   */
  getDrainage: async (fieldId: string, params?: DrainageParams): Promise<DrainageAnalysis> => {
    try {
      const response = await api.get(`${HYDROLOGY_ENDPOINTS.DRAINAGE}/${fieldId}`, {
        params: {
          flow_threshold: params?.flowThreshold,
          include_pattern: params?.includePattern,
        },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to get drainage network:', error);
      throw new Error(ERROR_MESSAGES.DRAINAGE_FAILED.en);
    }
  },

  /**
   * Get wetness/waterlogging analysis for a field.
   * الحصول على تحليل الرطوبة والتشبع المائي للحقل
   */
  getWetness: async (fieldId: string, params?: WetnessParams): Promise<WetnessAnalysis> => {
    try {
      const response = await api.get(`${HYDROLOGY_ENDPOINTS.WETNESS}/${fieldId}`, {
        params: {
          include_prediction: params?.includePrediction,
          rainfall_mm: params?.rainfallMm,
        },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to get wetness analysis:', error);
      throw new Error(ERROR_MESSAGES.WETNESS_FAILED.en);
    }
  },

  /**
   * Identify depressions/sinks in the field.
   * تحديد المنخفضات في الحقل
   */
  getDepressions: async (fieldId: string, params?: DepressionParams): Promise<DepressionAnalysis> => {
    try {
      const response = await api.get(`${HYDROLOGY_ENDPOINTS.DEPRESSIONS}/${fieldId}`, {
        params: {
          min_depth_m: params?.minDepthM,
          min_area_sqm: params?.minAreaSqm,
        },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to get depressions:', error);
      throw new Error(ERROR_MESSAGES.DEPRESSIONS_FAILED.en);
    }
  },

  /**
   * Detect streams in the field.
   * كشف المجاري المائية في الحقل
   */
  getStreams: async (fieldId: string, params?: StreamParams): Promise<StreamNetwork> => {
    try {
      const response = await api.get(`${HYDROLOGY_ENDPOINTS.STREAMS}/${fieldId}`, {
        params: {
          min_order: params?.minOrder,
        },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to get streams:', error);
      throw new Error(ERROR_MESSAGES.STREAMS_FAILED.en);
    }
  },

  /**
   * Delineate drainage basins/watersheds.
   * تحديد أحواض التصريف
   */
  getBasins: async (fieldId: string, params?: BasinParams): Promise<BasinDelineation> => {
    try {
      const response = await api.get(`${HYDROLOGY_ENDPOINTS.BASINS}/${fieldId}`, {
        params: {
          min_area_ha: params?.minAreaHa,
        },
      });
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to get basins:', error);
      throw new Error(ERROR_MESSAGES.BASINS_FAILED.en);
    }
  },
};
