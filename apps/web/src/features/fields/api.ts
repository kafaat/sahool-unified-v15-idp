/**
 * Fields Feature - API Layer
 * طبقة API لميزة الحقول
 */

import type { Field, FieldFormData, FieldFilters, GeoPolygon } from './types';
import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { FIELD_ENDPOINTS, SATELLITE_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';

/**
 * API Field Response Type
 */
interface ApiFieldResponse {
  id: string;
  name?: string;
  nameAr?: string;
  areaHectares?: number;
  area?: number;
  cropType?: string;
  crop?: string;
  cropTypeAr?: string;
  cropAr?: string;
  tenantId?: string;
  farmId?: string;
  boundary?: GeoPolygon;
  polygon?: GeoPolygon;
  centroidLat?: number;
  centroidLng?: number;
  description?: string;
  descriptionAr?: string;
  metadata?: {
    description?: string;
    descriptionAr?: string;
    [key: string]: unknown;
  };
  createdAt?: string;
  updatedAt?: string;
}

/**
 * KPI Snapshot from Sentinel Hub + OpenWeather
 * لقطة KPI من Sentinel Hub + OpenWeather
 */
export interface FieldKpiSnapshot {
  id: string;
  fieldId: string;
  tenantId: string;
  fetchedAt: string;
  // Sentinel Hub vegetation indices
  ndvi?: number | null;
  evi?: number | null;
  ndwi?: number | null;
  savi?: number | null;
  lai?: number | null;
  ndmi?: number | null;
  // OpenWeather data
  temperature?: number | null;
  humidity?: number | null;
  windSpeed?: number | null;
  precipitation?: number | null;
  uvIndex?: number | null;
  weatherCondition?: string | null;
  weatherConditionAr?: string | null;
  satelliteSource?: string | null;
  weatherSource?: string | null;
}

/**
 * Boundary change history entry
 */
export interface BoundaryHistoryEntry {
  id: string;
  fieldId: string;
  previousBoundary: GeoPolygon | null;
  newBoundary: GeoPolygon;
  changedBy: string;
  changedAt: string;
  reason?: string;
}

/**
 * NDVI data for a field
 */
export interface FieldNdviData {
  fieldId: string;
  value: number;
  timestamp: string;
  source?: string;
  cloudCover?: number;
}

/**
 * NDVI summary across tenant fields
 */
export interface FieldNdviSummary {
  totalFields: number;
  averageNdvi: number;
  healthDistribution: Record<string, number>;
}

/**
 * Field sync status
 */
export interface SyncStatus {
  fieldId: string;
  lastSyncAt: string;
  status: string;
  pendingChanges: number;
}

/**
 * Batch sync result
 */
export interface BatchSyncResult {
  synced: number;
  failed: number;
  conflicts: number;
}

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_FAILED: {
    en: 'Failed to fetch fields. Using cached data.',
    ar: 'فشل في جلب الحقول. استخدام البيانات المخزنة.',
  },
  CREATE_FAILED: {
    en: 'Failed to create field. Please try again.',
    ar: 'فشل في إنشاء الحقل. الرجاء المحاولة مرة أخرى.',
  },
  UPDATE_FAILED: {
    en: 'Failed to update field. Please try again.',
    ar: 'فشل في تحديث الحقل. الرجاء المحاولة مرة أخرى.',
  },
  DELETE_FAILED: {
    en: 'Failed to delete field. Please try again.',
    ar: 'فشل في حذف الحقل. الرجاء المحاولة مرة أخرى.',
  },
  NOT_FOUND: {
    en: 'Field not found.',
    ar: 'الحقل غير موجود.',
  },
};

/**
 * Map API field to feature field
 */
function mapApiFieldToField(apiField: ApiFieldResponse): Field {
  // Build centroid GeoPoint from flat lat/lng fields returned by the backend
  let centroid: import('./types').GeoPoint | undefined;
  if (apiField.centroidLat != null && apiField.centroidLng != null) {
    centroid = { type: 'Point', coordinates: [apiField.centroidLng, apiField.centroidLat] };
  }

  return {
    id: apiField.id,
    name: apiField.name || '',
    nameAr: apiField.nameAr || apiField.name || '',
    area: apiField.areaHectares || apiField.area || 0,
    crop: apiField.cropType || apiField.crop || '',
    cropAr: apiField.cropTypeAr || apiField.cropAr || apiField.cropType || apiField.crop || '',
    farmId: apiField.farmId || apiField.tenantId || '',
    polygon: apiField.boundary || apiField.polygon,
    centroid,
    description: apiField.metadata?.description || apiField.description,
    descriptionAr: apiField.metadata?.descriptionAr || apiField.descriptionAr,
    createdAt: apiField.createdAt || new Date().toISOString(),
    updatedAt: apiField.updatedAt || new Date().toISOString(),
  };
}

/**
 * API Field Request Type
 */
interface ApiFieldRequest {
  name: string;
  nameAr: string;
  tenantId: string;
  cropType: string;
  cropTypeAr?: string;
  coordinates?: number[][];
  areaHectares: number;
  metadata: {
    description?: string;
    descriptionAr?: string;
  };
}

/**
 * Map feature field to API field
 */
function mapFieldToApiField(field: FieldFormData, tenantId?: string): ApiFieldRequest {
  return {
    name: field.name,
    nameAr: field.nameAr,
    tenantId: tenantId || 'default-tenant',
    cropType: field.crop || 'unknown',
    cropTypeAr: field.cropAr,
    // Send flat ring as coordinates (service handles GeoJSON wrapping internally)
    // Sending full boundary GeoJSON object causes ST_GeomFromGeoJSON parse errors
    coordinates: field.polygon?.coordinates?.[0],
    areaHectares: field.area,
    metadata: {
      description: field.description,
      descriptionAr: field.descriptionAr,
    },
  };
}

// API Functions
export const fieldsApi = {
  /**
   * Get all fields with filters
   */
  getFields: async (filters?: FieldFilters): Promise<Field[]> => {
    return safeFetch(FIELD_ENDPOINTS.LIST, async () => {
      const params = new URLSearchParams();
      if (filters?.search) params.set('search', filters.search);
      if (filters?.farmId) params.set('tenantId', filters.farmId);
      if (filters?.crop) params.set('cropType', filters.crop);
      if (filters?.minArea) params.set('minArea', filters.minArea.toString());
      if (filters?.maxArea) params.set('maxArea', filters.maxArea.toString());
      if (filters?.status) params.set('status', filters.status);

      const response = await api.get(`${FIELD_ENDPOINTS.LIST}?${params.toString()}`);
      const fields = response.data.data || response.data;
      if (Array.isArray(fields)) return fields.map(mapApiFieldToField);
      throw new Error('Invalid response format for fields | تنسيق الاستجابة غير صالح للحقول');
    });
  },

  /**
   * Get field by ID
   */
  getFieldById: async (id: string): Promise<Field> => {
    return safeFetch(buildUrl(FIELD_ENDPOINTS.GET, { fieldId: id }), async () => {
      const response = await api.get(buildUrl(FIELD_ENDPOINTS.GET, { fieldId: id }));
      const field = response.data.data || response.data;
      return mapApiFieldToField(field);
    });
  },

  /**
   * Create new field
   */
  createField: async (data: FieldFormData, tenantId?: string): Promise<Field> => {
    return safeFetch(FIELD_ENDPOINTS.CREATE, async () => {
      const apiData = mapFieldToApiField(data, tenantId);
      const response = await api.post(FIELD_ENDPOINTS.CREATE, apiData);
      const field = response.data.data || response.data;
      return mapApiFieldToField(field);
    });
  },

  /**
   * Update field
   */
  updateField: async (
    id: string,
    data: Partial<FieldFormData>,
    tenantId?: string
  ): Promise<Field> => {
    return safeFetch(buildUrl(FIELD_ENDPOINTS.UPDATE, { fieldId: id }), async () => {
      const apiData = mapFieldToApiField(data as FieldFormData, tenantId);
      const response = await api.put(buildUrl(FIELD_ENDPOINTS.UPDATE, { fieldId: id }), apiData);
      const field = response.data.data || response.data;
      return mapApiFieldToField(field);
    });
  },

  /**
   * Delete field
   */
  deleteField: async (id: string): Promise<void> => {
    return safeFetch(buildUrl(FIELD_ENDPOINTS.DELETE, { fieldId: id }), async () => {
      await api.delete(buildUrl(FIELD_ENDPOINTS.DELETE, { fieldId: id }));
    });
  },

  /**
   * Get field statistics
   */
  getStats: async (
    farmId?: string
  ): Promise<{
    total: number;
    totalArea: number;
    byCrop: Record<string, number>;
  }> => {
    return safeFetch(`${FIELD_ENDPOINTS.LIST}/stats`, async () => {
      const params = new URLSearchParams();
      if (farmId) params.set('tenantId', farmId);
      const response = await api.get(`${FIELD_ENDPOINTS.LIST}/stats?${params.toString()}`);
      return response.data.data || response.data;
    });
  },

  /**
   * Get boundary change history for a field
   * جلب سجل تغييرات حدود الحقل
   */
  getBoundaryHistory: async (fieldId: string): Promise<BoundaryHistoryEntry[]> => {
    return safeFetch(buildUrl(FIELD_ENDPOINTS.BOUNDARY_HISTORY, { fieldId }), async () => {
      const response = await api.get(buildUrl(FIELD_ENDPOINTS.BOUNDARY_HISTORY, { fieldId }));
      return response.data.data || response.data;
    });
  },

  /**
   * Update field boundary
   * تحديث حدود الحقل
   */
  updateBoundary: async (fieldId: string, boundary: GeoPolygon): Promise<Field> => {
    return safeFetch(buildUrl(FIELD_ENDPOINTS.BOUNDARY_UPDATE, { fieldId }), async () => {
      const response = await api.put(buildUrl(FIELD_ENDPOINTS.BOUNDARY_UPDATE, { fieldId }), { boundary });
      const field = response.data.data || response.data;
      return mapApiFieldToField(field);
    });
  },

  /**
   * Rollback boundary to a previous version
   * استعادة حدود الحقل من نسخة سابقة
   */
  rollbackBoundary: async (fieldId: string, versionId: string): Promise<Field> => {
    return safeFetch(buildUrl(FIELD_ENDPOINTS.BOUNDARY_ROLLBACK, { fieldId }), async () => {
      const response = await api.post(buildUrl(FIELD_ENDPOINTS.BOUNDARY_ROLLBACK, { fieldId }), { versionId });
      const field = response.data.data || response.data;
      return mapApiFieldToField(field);
    });
  },

  /**
   * Get nearby fields by coordinates
   * البحث عن الحقول القريبة
   */
  getNearbyFields: async (lat: number, lng: number, radiusKm: number): Promise<Field[]> => {
    return safeFetch(FIELD_ENDPOINTS.NEARBY, async () => {
      const params = new URLSearchParams();
      params.set('lat', lat.toString());
      params.set('lng', lng.toString());
      params.set('radius', radiusKm.toString());
      const response = await api.get(`${FIELD_ENDPOINTS.NEARBY}?${params.toString()}`);
      const fields = response.data.data || response.data;
      if (Array.isArray(fields)) return fields.map(mapApiFieldToField);
      throw new Error('Invalid response format for nearby fields | تنسيق الاستجابة غير صالح للحقول القريبة');
    });
  },

  /**
   * Get NDVI analysis for a field
   * جلب تحليل NDVI للحقل
   */
  getFieldNdvi: async (fieldId: string): Promise<FieldNdviData> => {
    return safeFetch(buildUrl(SATELLITE_ENDPOINTS.NDVI_FIELD, { fieldId }), async () => {
      const response = await api.get(buildUrl(SATELLITE_ENDPOINTS.NDVI_FIELD, { fieldId }));
      return response.data.data || response.data;
    });
  },

  /**
   * Update NDVI value for a field
   * تحديث مؤشر NDVI للحقل
   */
  updateFieldNdvi: async (fieldId: string, data: { value: number; source?: string; cloudCover?: number }): Promise<FieldNdviData> => {
    return safeFetch(buildUrl(SATELLITE_ENDPOINTS.NDVI_FIELD, { fieldId }), async () => {
      const response = await api.put(buildUrl(SATELLITE_ENDPOINTS.NDVI_FIELD, { fieldId }), data);
      return response.data.data || response.data;
    });
  },

  /**
   * Get NDVI summary for the tenant
   * جلب ملخص NDVI للمستأجر
   */
  getNdviSummary: async (): Promise<FieldNdviSummary> => {
    return safeFetch(SATELLITE_ENDPOINTS.NDVI_SUMMARY, async () => {
      const response = await api.get(SATELLITE_ENDPOINTS.NDVI_SUMMARY);
      return response.data.data || response.data;
    });
  },

  /**
   * Get field sync status (delta sync)
   * جلب حالة مزامنة الحقول
   */
  getFieldSyncStatus: async (): Promise<SyncStatus[]> => {
    return safeFetch(FIELD_ENDPOINTS.SYNC, async () => {
      const response = await api.get(FIELD_ENDPOINTS.SYNC);
      return response.data.data || response.data;
    });
  },

  /**
   * Batch sync fields from mobile/offline
   * مزامنة مجموعة من الحقول
   */
  batchSync: async (data: { deviceId: string; userId: string; fields: unknown[] }): Promise<BatchSyncResult> => {
    return safeFetch(FIELD_ENDPOINTS.SYNC_BATCH, async () => {
      const response = await api.post(FIELD_ENDPOINTS.SYNC_BATCH, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Get latest KPI snapshot for a field (Sentinel Hub + OpenWeather)
   * جلب أحدث لقطة KPI للحقل
   */
  getLatestKpiSnapshot: async (fieldId: string): Promise<FieldKpiSnapshot | null> => {
    try {
      const response = await api.get(`/api/v1/fields/${fieldId}/kpi-snapshot`);
      return response.data.data || response.data;
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { status?: number } };
        if (axiosErr.response?.status === 404) return null;
      }
      throw err;
    }
  },

  /**
   * Trigger KPI refresh: calls satellite + weather Next.js proxies then saves snapshot
   * تحديث KPI: استدعاء وكيل الأقمار الصناعية والطقس ثم حفظ اللقطة
   */
  triggerKpiRefresh: async (
    fieldId: string,
    lat: number,
    lng: number,
    _tenantId?: string,
    polygonCoordinates?: number[][]
  ): Promise<FieldKpiSnapshot> => {
    // 1. Fetch vegetation indices via Next.js proxy at /api/satellite
    //    (proxy handles tenant auth server-side from httpOnly cookie)
    let satelliteData: Record<string, number | string> = {};
    try {
      const satRes = await fetch('/api/satellite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({
          action: 'analyze',
          fieldId,
          latitude: lat,
          longitude: lng,
          ...(polygonCoordinates ? { coordinates: polygonCoordinates } : {}),
        }),
      });
      if (satRes.ok) {
        const satBody = await satRes.json();
        satelliteData = satBody.indices || satBody.vegetation_indices || satBody || {};
      }
    } catch {
      // Non-fatal: satellite may not be configured; proceed with weather only
    }

    // 2. Fetch weather via Next.js proxy at /api/weather
    //    (proxy handles tenant auth server-side from httpOnly cookie)
    let weatherData: Record<string, number | string> = {};
    try {
      const wxRes = await fetch('/api/weather', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({
          action: 'current',
          lat,
          lon: lng,
          field_id: fieldId,
        }),
      });
      if (wxRes.ok) {
        const wxBody = await wxRes.json();
        weatherData = wxBody.current || wxBody || {};
      }
    } catch {
      // Non-fatal: proceed with satellite data only
    }

    // 3. Persist snapshot via field-management-service
    const payload = {
      ndvi: typeof satelliteData.ndvi === 'number' ? satelliteData.ndvi : undefined,
      evi: typeof satelliteData.evi === 'number' ? satelliteData.evi : undefined,
      ndwi: typeof satelliteData.ndwi === 'number' ? satelliteData.ndwi : undefined,
      savi: typeof satelliteData.savi === 'number' ? satelliteData.savi : undefined,
      lai: typeof satelliteData.lai === 'number' ? satelliteData.lai : undefined,
      ndmi: typeof satelliteData.ndmi === 'number' ? satelliteData.ndmi : undefined,
      temperature: weatherData.temperature_c ?? weatherData.temperature,
      humidity: weatherData.humidity_pct ?? weatherData.humidity,
      windSpeed: weatherData.wind_speed_kmh ?? weatherData.windSpeed ?? weatherData.wind_speed,
      precipitation: weatherData.precipitation_mm ?? weatherData.precipitation ?? 0,
      uvIndex: weatherData.uv_index ?? weatherData.uvIndex,
      weatherCondition: typeof weatherData.condition === 'string' ? weatherData.condition : undefined,
      weatherConditionAr: typeof weatherData.condition_ar === 'string' ? weatherData.condition_ar : undefined,
      satelliteSource: typeof satelliteData.data_source === 'string' ? satelliteData.data_source : 'sentinel-hub',
      weatherSource: 'openweather',
    };

    const saveRes = await api.post(`/api/v1/fields/${fieldId}/kpi-snapshot`, payload);
    return saveRes.data.data || saveRes.data;
  },
};
