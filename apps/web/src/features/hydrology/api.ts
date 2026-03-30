/**
 * Hydrology Feature - API Layer
 * طبقة API لميزة الهيدرولوجيا
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { API_PREFIX } from '@sahool/shared-types/contracts';
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

const HYDROLOGY_BASE = `${API_PREFIX}/hydrology`;

const HYDROLOGY_ENDPOINTS = {
  ANALYZE: `${HYDROLOGY_BASE}/analyze`,
  DRAINAGE: `${HYDROLOGY_BASE}/drainage`,
  WETNESS: `${HYDROLOGY_BASE}/wetness`,
  DEPRESSIONS: `${HYDROLOGY_BASE}/depressions`,
  STREAMS: `${HYDROLOGY_BASE}/streams`,
  BASINS: `${HYDROLOGY_BASE}/basins`,
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
    return safeFetch(HYDROLOGY_ENDPOINTS.ANALYZE, async () => {
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
    });
  },

  /**
   * Get drainage network for a field.
   * الحصول على شبكة التصريف للحقل
   */
  getDrainage: async (fieldId: string, params?: DrainageParams): Promise<DrainageAnalysis> => {
    const endpoint = `${HYDROLOGY_ENDPOINTS.DRAINAGE}/${fieldId}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint, {
        params: {
          flow_threshold: params?.flowThreshold,
          include_pattern: params?.includePattern,
        },
      });
      return response.data.data || response.data;
    });
  },

  /**
   * Get wetness/waterlogging analysis for a field.
   * الحصول على تحليل الرطوبة والتشبع المائي للحقل
   */
  getWetness: async (fieldId: string, params?: WetnessParams): Promise<WetnessAnalysis> => {
    const endpoint = `${HYDROLOGY_ENDPOINTS.WETNESS}/${fieldId}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint, {
        params: {
          include_prediction: params?.includePrediction,
          rainfall_mm: params?.rainfallMm,
        },
      });
      return response.data.data || response.data;
    });
  },

  /**
   * Identify depressions/sinks in the field.
   * تحديد المنخفضات في الحقل
   */
  getDepressions: async (fieldId: string, params?: DepressionParams): Promise<DepressionAnalysis> => {
    const endpoint = `${HYDROLOGY_ENDPOINTS.DEPRESSIONS}/${fieldId}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint, {
        params: {
          min_depth_m: params?.minDepthM,
          min_area_sqm: params?.minAreaSqm,
        },
      });
      return response.data.data || response.data;
    });
  },

  /**
   * Detect streams in the field.
   * كشف المجاري المائية في الحقل
   */
  getStreams: async (fieldId: string, params?: StreamParams): Promise<StreamNetwork> => {
    const endpoint = `${HYDROLOGY_ENDPOINTS.STREAMS}/${fieldId}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint, {
        params: {
          min_order: params?.minOrder,
        },
      });
      return response.data.data || response.data;
    });
  },

  /**
   * Delineate drainage basins/watersheds.
   * تحديد أحواض التصريف
   */
  getBasins: async (fieldId: string, params?: BasinParams): Promise<BasinDelineation> => {
    const endpoint = `${HYDROLOGY_ENDPOINTS.BASINS}/${fieldId}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint, {
        params: {
          min_area_ha: params?.minAreaHa,
        },
      });
      return response.data.data || response.data;
    });
  },
};
