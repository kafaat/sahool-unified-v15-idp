/**
 * Fields Feature - API Layer
 * طبقة API لميزة الحقول
 */

import type {
  Field,
  FieldFormData,
  FieldFilters,
  GeoPolygon,
  SatelliteIndices,
  FieldWeatherData,
  FieldIndicatorsData,
} from './types';
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
  return {
    id: apiField.id,
    name: apiField.name || '',
    nameAr: apiField.nameAr || apiField.name || '',
    area: apiField.areaHectares || apiField.area || 0,
    crop: apiField.cropType || apiField.crop || '',
    cropAr: apiField.cropTypeAr || apiField.cropAr || apiField.cropType || apiField.crop || '',
    farmId: apiField.farmId || apiField.tenantId || '',
    polygon: apiField.boundary || apiField.polygon,
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
  boundary?: GeoPolygon;
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
    coordinates: field.polygon?.coordinates?.[0],
    boundary: field.polygon,
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
};

// ═══════════════════════════════════════════════════════════════════════════
// KPI / Live Data API Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Fetch satellite vegetation indices for a field
 * جلب مؤشرات الغطاء النباتي من الأقمار الصناعية
 */
export async function fetchSatelliteIndices(
  fieldId: string,
  lat: number,
  lng: number
): Promise<SatelliteIndices> {
  const params = new URLSearchParams({
    action: 'indices',
    fieldId,
    lat: lat.toString(),
    lon: lng.toString(),
  });
  const res = await fetch(`/api/satellite?${params.toString()}`);
  if (!res.ok) throw new Error(`Satellite indices fetch failed: ${res.status}`);
  const data = await res.json();
  // Normalize: response may be { ndvi, evi, ... } or nested under 'indices'
  return (data.indices ?? data) as SatelliteIndices;
}

/**
 * Fetch current weather for a field location (uses Open-Meteo free provider)
 * جلب بيانات الطقس الحالي لموقع الحقل
 */
export async function fetchFieldWeather(
  lat: number,
  lng: number,
  fieldId: string
): Promise<FieldWeatherData> {
  const res = await fetch('/api/weather', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'current', lat, lon: lng, field_id: fieldId }),
  });
  if (!res.ok) throw new Error(`Weather fetch failed: ${res.status}`);
  const d = await res.json();
  // Normalize across different weather service response shapes
  return {
    temperature_c:
      d.temperature ?? d.temperature_c ?? d.current?.temperature_2m ?? d.temp_c ?? 0,
    humidity_pct:
      d.humidity ?? d.humidity_pct ?? d.current?.relative_humidity_2m ?? d.humidity_pct ?? 0,
    wind_speed_kmh:
      d.wind_speed ?? d.wind_speed_kmh ?? d.current?.wind_speed_10m ?? d.wind_kph ?? 0,
    condition: d.condition ?? d.weather_description ?? d.description ?? 'N/A',
    condition_ar:
      d.condition_ar ?? d.weather_description_ar ?? d.description_ar ?? 'غير متاح',
    precipitation_mm: d.precipitation ?? d.precipitation_mm ?? d.precip_mm ?? 0,
    uv_index: d.uv_index ?? d.current?.uv_index,
    cloud_cover: d.cloud_cover ?? d.cloudcover ?? d.current?.cloud_cover,
  };
}

/**
 * Fetch 22 field indicators from indicators-service
 * جلب 22 مؤشراً ميدانياً من خدمة المؤشرات
 */
export async function fetchFieldIndicators(fieldId: string): Promise<FieldIndicatorsData> {
  const res = await fetch(`/api/indicators?fieldId=${encodeURIComponent(fieldId)}`);
  if (!res.ok) throw new Error(`Indicators fetch failed: ${res.status}`);
  const data = await res.json();
  return {
    field_id: data.field_id || fieldId,
    indicators: Array.isArray(data.indicators)
      ? data.indicators
      : Array.isArray(data)
        ? data
        : [],
    overall_score: data.overall_score,
    timestamp: data.timestamp,
  };
}

/**
 * Fire-and-forget vegetation analysis trigger after field creation
 * تشغيل تحليل الغطاء النباتي بعد إنشاء الحقل مباشرة
 */
export async function triggerVegetationAnalysis(
  fieldId: string,
  polygon: GeoPolygon
): Promise<void> {
  const ring = polygon?.coordinates?.[0];
  if (!ring || ring.length < 3) return;

  const lngs = ring.map((c) => c[0]);
  const lats = ring.map((c) => c[1]);
  const lat = (Math.min(...lats) + Math.max(...lats)) / 2;
  const lng = (Math.min(...lngs) + Math.max(...lngs)) / 2;

  await fetch('/api/satellite', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action: 'analyze',
      fieldId,
      analysisType: 'ndvi',
      latitude: lat,
      longitude: lng,
      coordinates: ring,
    }),
  });
}
