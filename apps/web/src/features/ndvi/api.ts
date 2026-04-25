/**
 * NDVI & Vegetation Indices Feature - API Layer
 * طبقة API لميزة مؤشرات NDVI والغطاء النباتي
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { SATELLITE_ENDPOINTS, buildUrl, API_PREFIX } from '@sahool/shared-types/contracts';
import type {
  VegetationIndex,
  IndicesResult,
  SingleIndexResult,
  IndicesInterpretation,
  IndexTimeSeries,
} from './types';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// Types
export interface NDVIData {
  fieldId: string;
  fieldName: string;
  date: string;
  ndviMean: number;
  ndviMin: number;
  ndviMax: number;
  ndviStd: number;
  healthStatus: 'excellent' | 'good' | 'moderate' | 'poor' | 'critical';
  cloudCoverage: number;
  source: 'sentinel-2' | 'landsat' | 'modis';
}

export interface NDVITimeSeries {
  fieldId: string;
  data: Array<{
    date: string;
    ndvi: number;
    healthStatus: NDVIData['healthStatus'];
  }>;
  trend: 'improving' | 'stable' | 'declining';
  anomalies: Array<{
    date: string;
    type: 'sudden_drop' | 'unusual_peak';
    severity: 'low' | 'medium' | 'high';
  }>;
}

export interface NDVIMapData {
  fieldId: string;
  date: string;
  rasterUrl: string;
  bounds: [[number, number], [number, number]];
  colorScale: {
    min: number;
    max: number;
    colors: string[];
  };
}

export interface NDVIFilters {
  fieldId?: string;
  governorate?: string;
  startDate?: string;
  endDate?: string;
  minNdvi?: number;
  maxNdvi?: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Error Messages - رسائل الخطأ
// ═══════════════════════════════════════════════════════════════════════════

export const ERROR_MESSAGES = {
  FETCH_FAILED: {
    en: 'Failed to fetch NDVI data.',
    ar: 'فشل في جلب بيانات NDVI.',
  },
  NETWORK_ERROR: {
    en: 'Network error. NDVI service unavailable.',
    ar: 'خطأ في الاتصال. خدمة NDVI غير متاحة.',
  },
  ANALYSIS_FAILED: {
    en: 'Failed to request NDVI analysis.',
    ar: 'فشل في طلب تحليل NDVI.',
  },
  COMPARISON_FAILED: {
    en: 'Failed to compare NDVI data.',
    ar: 'فشل في مقارنة بيانات NDVI.',
  },
};

// API Functions
export const ndviApi = {
  /**
   * Get latest NDVI data for all fields
   */
  getLatestNDVI: async (filters?: NDVIFilters): Promise<NDVIData[]> => {
    const endpoint = `${API_PREFIX}/ndvi/latest`;
    return safeFetch(endpoint, async () => {
      const params = new URLSearchParams();
      if (filters?.governorate) params.set('governorate', filters.governorate);
      if (filters?.minNdvi) params.set('min_ndvi', filters.minNdvi.toString());
      if (filters?.maxNdvi) params.set('max_ndvi', filters.maxNdvi.toString());

      const response = await api.get(`${endpoint}?${params.toString()}`);
      return response.data;
    });
  },

  /**
   * Get NDVI data for specific field
   */
  getFieldNDVI: async (fieldId: string): Promise<NDVIData> => {
    const url = buildUrl(SATELLITE_ENDPOINTS.NDVI_FIELD, { fieldId });
    return safeFetch(url, async () => {
      const response = await api.get(url);
      return response.data;
    });
  },

  /**
   * Get NDVI time series for a field
   */
  getNDVITimeSeries: async (
    fieldId: string,
    startDate?: string,
    endDate?: string
  ): Promise<NDVITimeSeries> => {
    const baseUrl = buildUrl(SATELLITE_ENDPOINTS.NDVI_FIELD, { fieldId });
    return safeFetch(`${baseUrl}/timeseries`, async () => {
      const params = new URLSearchParams();
      if (startDate) params.set('start_date', startDate);
      if (endDate) params.set('end_date', endDate);

      const response = await api.get(`${baseUrl}/timeseries?${params.toString()}`);
      return response.data;
    });
  },

  /**
   * Get NDVI raster map data.
   *
   * **API note:** delegates to {@link vegetationIndicesApi.getIndexMap} which
   * targets the unified ``/v1/indices/{fieldId}/map`` endpoint on
   * vegetation-analysis-service. The previous direct call to
   * ``/api/v1/fields/{fieldId}/ndvi/map`` 404'd silently (the route was never
   * implemented backend-side), causing the NDVI overlay to silently fail.
   * This wrapper preserves the legacy ``NDVIMapData`` response shape for
   * existing callers.
   */
  getNDVIMap: async (fieldId: string, date?: string): Promise<NDVIMapData> => {
    const data = await vegetationIndicesApi.getIndexMap(fieldId, 'ndvi', date);
    return {
      fieldId: data.fieldId,
      date: data.date,
      rasterUrl: data.rasterUrl,
      bounds: data.bounds,
      colorScale: {
        min: data.colorScale.min,
        max: data.colorScale.max,
        colors: data.colorScale.stops.map((s) => s.color),
      },
    };
  },

  /**
   * Request new NDVI analysis
   */
  requestNDVIAnalysis: async (fieldId: string): Promise<{ jobId: string; status: string }> => {
    const baseUrl = buildUrl(SATELLITE_ENDPOINTS.NDVI_FIELD, { fieldId });
    return safeFetch(`${baseUrl}/analyze`, async () => {
      const response = await api.post(`${baseUrl}/analyze`);
      return response.data;
    });
  },

  /**
   * Get NDVI comparison between dates
   */
  compareNDVI: async (
    fieldId: string,
    date1: string,
    date2: string
  ): Promise<{
    date1: NDVIData;
    date2: NDVIData;
    change: number;
    changePercent: number;
    interpretation: string;
  }> => {
    const baseUrl = buildUrl(SATELLITE_ENDPOINTS.NDVI_FIELD, { fieldId });
    return safeFetch(`${baseUrl}/compare`, async () => {
      const response = await api.get(`${baseUrl}/compare?date1=${date1}&date2=${date2}`);
      return response.data;
    });
  },

  /**
   * Get regional NDVI statistics
   */
  getRegionalStats: async (
    governorate?: string
  ): Promise<{
    averageNDVI: number;
    healthDistribution: Record<NDVIData['healthStatus'], number>;
    topFields: Array<{ fieldId: string; name: string; ndvi: number }>;
    bottomFields: Array<{ fieldId: string; name: string; ndvi: number }>;
  }> => {
    const endpoint = `${SATELLITE_ENDPOINTS.NDVI_SUMMARY}/regional`;
    return safeFetch(endpoint, async () => {
      const params = governorate ? `?governorate=${governorate}` : '';
      const response = await api.get(`${endpoint}${params}`);
      return response.data;
    });
  },
};

// =============================================================================
// Vegetation Indices API (all 41 indices)
// واجهة برمجة المؤشرات النباتية (41 مؤشر)
// =============================================================================

export const vegetationIndicesApi = {
  /**
   * Get all vegetation indices for a field
   * الحصول على جميع المؤشرات النباتية لحقل
   *
   * @param fieldId - Field identifier
   * @param indexNames - Optional subset of indices to retrieve
   * @param date - Optional specific date (ISO 8601)
   */
  getFieldIndices: async (
    fieldId: string,
    indexNames?: VegetationIndex[],
    date?: string
  ): Promise<IndicesResult> => {
    const url = buildUrl(SATELLITE_ENDPOINTS.INDICES, { fieldId });
    return safeFetch(url, async () => {
      const params = new URLSearchParams();
      if (indexNames?.length) params.set('indices', indexNames.join(','));
      if (date) params.set('date', date);
      const qs = params.toString();

      const response = await api.get(`${url}${qs ? `?${qs}` : ''}`);
      return response.data;
    });
  },

  /**
   * Get a specific vegetation index for a field
   * الحصول على مؤشر نباتي محدد لحقل
   *
   * @param fieldId - Field identifier
   * @param indexName - Vegetation index name (e.g. 'ndvi', 'evi', 'ndre')
   * @param date - Optional specific date (ISO 8601)
   */
  getSpecificIndex: async (
    fieldId: string,
    indexName: VegetationIndex | string,
    date?: string
  ): Promise<SingleIndexResult> => {
    const url = `${buildUrl(SATELLITE_ENDPOINTS.INDICES, { fieldId })}/${indexName}`;
    return safeFetch(url, async () => {
      const params = date ? `?date=${date}` : '';
      const response = await api.get(`${url}${params}`);
      return response.data;
    });
  },

  /**
   * Get interpreted indices with recommendations for a field.
   * الحصول على تفسير المؤشرات مع التوصيات لحقل
   *
   * NOTE: the vegetation-analysis-service /v1/indices/interpret endpoint is
   * POST with a JSON body `{ field_id, indices, crop_type, growth_stage }`.
   * Prior versions of this client called it as GET with query params which
   * silently failed with 405. Callers must supply a map of already-computed
   * index values (typically fetched via `getFieldIndices` first).
   *
   * @param fieldId - Field identifier
   * @param indices - Pre-computed vegetation index values (e.g. {ndvi: 0.65})
   * @param cropType - Crop type (e.g. "wheat", "date_palm")
   * @param growthStage - Growth stage (e.g. "vegetative", "reproductive")
   */
  interpretIndices: async (
    fieldId: string,
    indices: Record<string, number>,
    cropType: string = 'unknown',
    growthStage: string = 'vegetative',
  ): Promise<IndicesInterpretation> => {
    const endpoint = `${API_PREFIX}/satellite/v1/indices/interpret`;
    return safeFetch(endpoint, async () => {
      if (!fieldId || typeof fieldId !== 'string') {
        throw new Error('fieldId is required for interpretIndices');
      }
      if (!indices || typeof indices !== 'object' || Object.keys(indices).length === 0) {
        throw new Error('At least one index value is required for interpretIndices');
      }
      const response = await api.post(endpoint, {
        field_id: fieldId,
        indices,
        crop_type: cropType,
        growth_stage: growthStage,
      });
      return response.data;
    });
  },

  /**
   * Get raster-overlay metadata for any spectral index (NDVI/EVI/SAVI/NDRE/NDWI/LAI).
   * الحصول على بيانات تراكب الراستر لأي مؤشر طيفي
   *
   * Backed by ``vegetation-analysis-service::GET /v1/index-map/{fieldId}``.
   * Returns a real Sentinel Hub WMS URL when the service is configured with
   * ``SENTINEL_HUB_INSTANCE_ID``; otherwise returns a placeholder URL together
   * with ``simulated: true`` so callers fall back to client-side colour-mapped
   * polygon fills.
   *
   * @param fieldId   - Field identifier
   * @param indexName - Spectral index id (defaults to ``ndvi``)
   * @param date      - Optional acquisition date (ISO 8601 ``YYYY-MM-DD``)
   * @param bbox      - Optional ``[minLon,minLat,maxLon,maxLat]`` bounding box
   */
  getIndexMap: async (
    fieldId: string,
    indexName: VegetationIndex | string = 'ndvi',
    date?: string,
    bbox?: [number, number, number, number],
  ): Promise<{
    fieldId: string;
    indexType: string;
    date: string;
    rasterUrl: string;
    bounds: [[number, number], [number, number]];
    colorScale: { min: number; max: number; stops: Array<{ value: number; color: string }> };
    simulated: boolean;
    dataSource: string;
  }> => {
    const url = `${buildUrl(SATELLITE_ENDPOINTS.INDICES_MAP, { fieldId })}`;
    return safeFetch(url, async () => {
      const params = new URLSearchParams();
      params.set('index', String(indexName).toLowerCase());
      if (date) params.set('date', date);
      if (bbox && bbox.length === 4) params.set('bbox', bbox.join(','));
      const response = await api.get(`${url}?${params.toString()}`);
      return response.data;
    });
  },

  /**
   * Get time series data for a specific vegetation index
   * الحصول على بيانات السلاسل الزمنية لمؤشر نباتي محدد
   *
   * @param fieldId - Field identifier
   * @param indexName - Vegetation index name
   * @param dateRange - Optional date range { startDate, endDate } (ISO 8601)
   */
  getTimeSeries: async (
    fieldId: string,
    indexName: VegetationIndex | string,
    dateRange?: { startDate?: string; endDate?: string }
  ): Promise<IndexTimeSeries> => {
    const url = `${buildUrl(SATELLITE_ENDPOINTS.INDICES, { fieldId })}/${indexName}/timeseries`;
    return safeFetch(url, async () => {
      const params = new URLSearchParams();
      if (dateRange?.startDate) params.set('start_date', dateRange.startDate);
      if (dateRange?.endDate) params.set('end_date', dateRange.endDate);
      const qs = params.toString();

      const response = await api.get(`${url}${qs ? `?${qs}` : ''}`);
      return response.data;
    });
  },
};
