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

/**
 * Raster-tile metadata for any mappable vegetation index (NDVI, NDRE, NDWI,
 * EVI, SAVI, LAI). Returned by `GET /v1/indices/{fieldId}/{indexName}/map`.
 * Mirrors the backend `_MAPPABLE_INDICES` shape.
 */
export interface IndexMapData {
  fieldId: string;
  indexName: string;
  date: string;
  rasterUrl: string;
  bounds: [[number, number], [number, number]];
  colorScale: {
    min: number;
    max: number;
    colors: string[];
  };
  label: {
    en: string;
    ar: string;
  };
  unit: string;
  dataSource: 'sentinel_hub' | 'simulated';
}

/** Every computed index at one (lat, lon) point — powers click-to-inspect. */
export interface PixelInspection {
  fieldId: string;
  location: {
    latitude: number;
    longitude: number;
  };
  date: string;
  satellite: string;
  indices: Record<string, number | null>;
  mappable: string[];
  dataSource: 'sentinel_hub' | 'simulated';
}

/** Bilingual health-status bucket used across composite/filmstrip/compare. */
export interface IndexStatus {
  key: 'excellent' | 'good' | 'moderate' | 'poor' | 'unknown';
  en: string;
  ar: string;
}

/** Single bucket in a composite response. */
export interface CompositeWindow {
  window_start: string;
  window_end: string;
  count: number;
  mean: number;
  median: number;
  min: number;
  max: number;
  p25: number;
  p75: number;
  status: IndexStatus;
}

export interface IndexComposite {
  fieldId: string;
  indexName: string;
  stat: 'median' | 'mean';
  stepDays: number;
  start: string;
  end: string;
  windows: CompositeWindow[];
  count: number;
  dataSource: 'sentinel_hub' | 'simulated';
}

/** Single frame in a filmstrip. */
export interface FilmstripFrame {
  date: string;
  rasterUrl: string;
  value: number | null;
  status: IndexStatus;
  cloudCover?: number | null;
}

export interface IndexFilmstrip {
  fieldId: string;
  indexName: string;
  stepDays: number;
  colorScale: {
    min: number;
    max: number;
    colors: string[];
  };
  label: {
    en: string;
    ar: string;
  };
  frames: FilmstripFrame[];
  count: number;
  dataSource: 'sentinel_hub' | 'simulated';
}

/** Single row of a multi-date-compare response. */
export interface MultiDateCompareRow {
  date: string;
  value: number | null;
  delta_from_previous: number | null;
  status: IndexStatus;
}

export interface MultiDateCompare {
  fieldId: string;
  indexName: string;
  dates: string[];
  rows: MultiDateCompareRow[];
  summary: {
    count_dates: number;
    count_with_data: number;
    min: number | null;
    max: number | null;
    overall_delta: number | null;
  };
  dataSource: 'sentinel_hub' | 'simulated';
}

export type MultiDateCompareRequest =
  | { dates: string[] }
  | { start: string; end: string; step_days: number };

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
   * Get NDVI raster map data
   */
  getNDVIMap: async (fieldId: string, date?: string): Promise<NDVIMapData> => {
    const baseUrl = buildUrl(SATELLITE_ENDPOINTS.NDVI_FIELD, { fieldId });
    return safeFetch(`${baseUrl}/map`, async () => {
      const params = date ? `?date=${date}` : '';
      const response = await api.get(`${baseUrl}/map${params}`);
      return response.data;
    });
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

  /**
   * Get raster-tile metadata for a mappable vegetation index.
   * جلب بيانات الطبقة النقطية لمؤشر نباتي قابل للعرض على الخريطة
   *
   * Returns a `{rasterUrl, bounds, colorScale}` envelope that the MapLibre
   * layer can render. The rasterUrl is a Sentinel Hub WMS template when
   * the instance is configured, or a simulated `/tile/{z}/{x}/{y}` path
   * otherwise — same shape either way.
   *
   * @param fieldId - Field identifier
   * @param indexName - One of ndvi|ndre|ndwi|evi|savi|lai
   * @param date - Optional ISO date (YYYY-MM-DD); defaults to today
   */
  getIndexMap: async (
    fieldId: string,
    indexName: VegetationIndex | string,
    date?: string
  ): Promise<IndexMapData> => {
    const url = buildUrl(SATELLITE_ENDPOINTS.INDEX_MAP, {
      fieldId,
      indexName: String(indexName).toLowerCase(),
    });
    return safeFetch(url, async () => {
      const params = date ? `?date=${date}` : '';
      const response = await api.get(`${url}${params}`);
      return response.data;
    });
  },

  /**
   * Click-to-inspect: get every computed index at a lat/lon point.
   * الحصول على جميع المؤشرات عند نقطة محددة (click-to-inspect)
   *
   * EOSDA/OneSoil UX parity — user clicks the map, popup shows NDVI +
   * NDRE + NDWI + SAVI + LAI + 39 more at that exact coordinate.
   */
  getPixelInspection: async (
    fieldId: string,
    lat: number,
    lon: number,
    options?: {
      date?: string;
      indices?: Array<VegetationIndex | string>;
    }
  ): Promise<PixelInspection> => {
    const url = buildUrl(SATELLITE_ENDPOINTS.INDEX_PIXEL, { fieldId });
    return safeFetch(url, async () => {
      const params = new URLSearchParams();
      params.set('lat', String(lat));
      params.set('lon', String(lon));
      if (options?.date) params.set('date', options.date);
      if (options?.indices?.length) {
        params.set('indices', options.indices.map(String).join(','));
      }
      const response = await api.get(`${url}?${params.toString()}`);
      return response.data;
    });
  },

  /**
   * N-day composite (median/mean per window) for a mappable index.
   * جلب تركيب زمني لكل N يوم
   *
   * EOSDA "weekly/monthly composite" — smooths cloud artefacts without
   * losing the trend. Returns p25/p75 envelopes so the client can draw
   * confidence bands.
   */
  getIndexComposite: async (
    fieldId: string,
    indexName: VegetationIndex | string,
    options?: {
      stepDays?: number;
      start?: string;
      end?: string;
      stat?: 'median' | 'mean';
    }
  ): Promise<IndexComposite> => {
    const url = buildUrl(SATELLITE_ENDPOINTS.INDEX_COMPOSITE, {
      fieldId,
      indexName: String(indexName).toLowerCase(),
    });
    return safeFetch(url, async () => {
      const params = new URLSearchParams();
      if (options?.stepDays) params.set('step_days', String(options.stepDays));
      if (options?.start) params.set('start', options.start);
      if (options?.end) params.set('end', options.end);
      if (options?.stat) params.set('stat', options.stat);
      const qs = params.toString();
      const response = await api.get(`${url}${qs ? `?${qs}` : ''}`);
      return response.data;
    });
  },

  /**
   * Filmstrip — per-date thumbnail metadata for a carousel UI.
   * شريط الصور - بيانات المصغّرات لعرض carousel
   */
  getIndexFilmstrip: async (
    fieldId: string,
    indexName: VegetationIndex | string,
    options?: {
      stepDays?: number;
      start?: string;
      end?: string;
    }
  ): Promise<IndexFilmstrip> => {
    const url = buildUrl(SATELLITE_ENDPOINTS.INDEX_FILMSTRIP, {
      fieldId,
      indexName: String(indexName).toLowerCase(),
    });
    return safeFetch(url, async () => {
      const params = new URLSearchParams();
      if (options?.stepDays) params.set('step_days', String(options.stepDays));
      if (options?.start) params.set('start', options.start);
      if (options?.end) params.set('end', options.end);
      const qs = params.toString();
      const response = await api.get(`${url}${qs ? `?${qs}` : ''}`);
      return response.data;
    });
  },

  /**
   * Multi-date compare — N (up to 12) dates, same index.
   * مقارنة متعددة التواريخ لنفس المؤشر
   *
   * Supersedes the legacy 2-date compare for all mappable indices. Each
   * row includes `delta_from_previous` so the UI can render arrows
   * without doing client-side math.
   */
  multiDateCompare: async (
    fieldId: string,
    indexName: VegetationIndex | string,
    body: MultiDateCompareRequest
  ): Promise<MultiDateCompare> => {
    const url = buildUrl(SATELLITE_ENDPOINTS.INDEX_MULTI_COMPARE, {
      fieldId,
      indexName: String(indexName).toLowerCase(),
    });
    return safeFetch(url, async () => {
      const response = await api.post(url, body);
      return response.data;
    });
  },
};
