/**
 * Fields Feature - API Layer
 * طبقة API لميزة الحقول
 */

import type { Field, FieldFormData, FieldFilters, GeoPolygon } from './types';
import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { FIELD_ENDPOINTS, SATELLITE_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import Cookies from 'js-cookie';

/**
 * API Field Response Type
 */
interface ApiFieldResponse {
  id: string;
  name?: string;
  nameAr?: string;
  // Prisma Decimal fields are serialized as strings; accept either.
  areaHectares?: number | string;
  area?: number | string;
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

  // ── Sentinel Hub: Vegetation ──────────────────────────────────────────────
  ndvi?: number | null;   // Normalized Difference Vegetation Index
  evi?: number | null;    // Enhanced Vegetation Index
  lai?: number | null;    // Leaf Area Index
  savi?: number | null;   // Soil-Adjusted Vegetation Index
  ndmi?: number | null;   // Normalized Difference Moisture Index
  gndvi?: number | null;  // Green NDVI
  ndre?: number | null;   // Red-Edge NDVI
  msavi?: number | null;  // Modified SAVI
  osavi?: number | null;  // Optimised SAVI
  evi2?: number | null;   // Two-band EVI
  cvi?: number | null;    // Chlorophyll Vegetation Index
  mcari?: number | null;  // Modified Chlorophyll Absorption Ratio Index
  tcari?: number | null;  // Transformed Chlorophyll Absorption Ratio Index
  wdrvi?: number | null;  // Wide Dynamic Range Vegetation Index
  vari?: number | null;   // Visible Atmospherically Resistant Index

  // ── Sentinel Hub: Water ───────────────────────────────────────────────────
  ndwi?: number | null;        // Normalized Difference Water Index
  mndwi?: number | null;       // Modified NDWI
  turbidity?: number | null;   // Water turbidity
  chlorophyll?: number | null; // Chlorophyll-a concentration
  phycocyanin?: number | null; // Phycocyanin (algal bloom)

  // ── Sentinel Hub: Soil / Bare land ───────────────────────────────────────
  bsi?: number | null;   // Bare Soil Index
  nbsi?: number | null;  // Normalized Bare Soil Index

  // ── Sentinel Hub: Fire / Burn ─────────────────────────────────────────────
  nbr?: number | null;   // Normalized Burn Ratio
  nbr2?: number | null;  // NBR2
  bais2?: number | null; // Burned Area Index for Sentinel-2

  // ── Sentinel Hub: Urban / Built-up ───────────────────────────────────────
  ndbi?: number | null;  // Normalized Difference Built-up Index
  ibi?: number | null;   // Index-based Built-up Index

  // ── Sentinel Hub: Snow / Ice ──────────────────────────────────────────────
  ndsi?: number | null;  // Normalized Difference Snow Index
  ndgi?: number | null;  // Normalized Difference Glacier Index

  // ── Sentinel Hub: Atmosphere ─────────────────────────────────────────────
  lst?: number | null;              // Land Surface Temperature (°C)
  cloudProbability?: number | null; // Cloud probability (0-100)
  arvi?: number | null;             // Atmospherically Resistant Vegetation Index

  // ── OpenWeatherMap: Current conditions ───────────────────────────────────
  temperature?: number | null;
  humidity?: number | null;
  windSpeed?: number | null;
  windDirection?: number | null;
  precipitation?: number | null;
  pressure?: number | null;
  cloudCover?: number | null;
  visibility?: number | null;
  uvIndex?: number | null;
  weatherCondition?: string | null;
  weatherConditionAr?: string | null;

  // ── OpenWeatherMap: Air pollution ─────────────────────────────────────────
  aqi?: number | null;   // Air Quality Index (1=Good … 5=Very Poor)
  co?: number | null;    // Carbon monoxide (μg/m³)
  no?: number | null;    // Nitric oxide
  no2?: number | null;   // Nitrogen dioxide
  o3?: number | null;    // Ozone
  so2?: number | null;   // Sulphur dioxide
  nh3?: number | null;   // Ammonia
  pm25?: number | null;  // PM2.5
  pm10?: number | null;  // PM10

  // ── Solar irradiance (Open-Meteo) ─────────────────────────────────────────
  ghiClearSky?: number | null; // Global Horizontal Irradiance — clear sky (W/m²)
  dniClearSky?: number | null; // Direct Normal Irradiance — clear sky
  dhiClearSky?: number | null; // Diffuse Horizontal Irradiance — clear sky
  ghiCloudy?: number | null;   // GHI — actual (cloudy)
  dniCloudy?: number | null;   // DNI — actual
  dhiCloudy?: number | null;   // DHI — actual

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
 * Coerce a Prisma Decimal-ish value to a plain JS number.
 * Prisma serializes Decimal as a string (or object) over JSON, so the
 * UI must normalize before arithmetic (`.toFixed`, comparisons, etc.).
 * تحويل قيم Decimal القادمة من قاعدة البيانات إلى أرقام عادية
 */
function toNumber(value: unknown): number {
  if (typeof value === 'number') return Number.isFinite(value) ? value : 0;
  if (typeof value === 'string') {
    const n = parseFloat(value);
    return Number.isFinite(n) ? n : 0;
  }
  if (value && typeof value === 'object' && 'toString' in value) {
    const n = parseFloat((value as { toString: () => string }).toString());
    return Number.isFinite(n) ? n : 0;
  }
  return 0;
}

/**
 * Map API field to feature field
 */
function mapApiFieldToField(apiField: ApiFieldResponse): Field {
  // Build centroid GeoPoint from flat lat/lng fields returned by the backend
  let centroid: import('./types').GeoPoint | undefined;
  if (apiField.centroidLat != null && apiField.centroidLng != null) {
    centroid = { type: 'Point', coordinates: [apiField.centroidLng, apiField.centroidLat] };
  }

  // Backend returns Decimal columns (areaHectares, healthScore, ndviValue)
  // as JSON strings. Coerce to numbers so UI arithmetic/formatters don't
  // silently produce NaN or throw (e.g. `.toFixed` on a string).
  const area = toNumber(apiField.areaHectares ?? apiField.area);

  return {
    id: apiField.id,
    name: apiField.name || '',
    nameAr: apiField.nameAr || apiField.name || '',
    area,
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
  farmId?: string;
  coordinates?: number[][];
  areaHectares: number;
  metadata: {
    description?: string;
    descriptionAr?: string;
  };
}

/**
 * Map feature field to API field.
 *
 * Falls back to the tenant_id cookie when the auth store is transiently empty.
 * The backend always overrides tenantId from the JWT `tid` claim, so the
 * client-supplied value only needs to be non-empty to pass DTO validation.
 */
function mapFieldToApiField(field: FieldFormData, tenantId?: string): ApiFieldRequest {
  const resolvedTenantId = tenantId || (typeof window !== 'undefined' ? Cookies.get('tenant_id') : undefined);
  if (!resolvedTenantId) {
    throw new Error(
      'يجب تسجيل الدخول أولاً | Authentication required before saving a field.',
    );
  }
  return {
    name: field.name,
    nameAr: field.nameAr,
    tenantId: resolvedTenantId,
    cropType: field.crop || 'unknown',
    cropTypeAr: field.cropAr,
    farmId: field.farmId || undefined,
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
      if (filters?.farmId) params.set('farmId', filters.farmId);
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
   * Get field statistics.
   *
   * Backend route is `GET /api/v1/fields/stats/:tenantId` (tenantId as
   * a path param). The request is always scoped to the authenticated
   * tenant server-side, so we only need to pass a non-empty string to
   * satisfy the NestJS route matcher — the server overrides it with
   * the JWT's `tid` claim via `assertTenantOwnership`.
   * تم تصحيح الاستدعاء ليطابق مسار الخدمة الخلفية
   */
  getStats: async (
    tenantId?: string
  ): Promise<{
    total: number;
    totalArea: number;
    byCrop: Record<string, number>;
  }> => {
    // Use a placeholder when tenantId is not supplied; the backend will
    // reject any mismatch via assertTenantOwnership and always scope the
    // statistics to the authenticated user's tenant.
    const tenantSegment = tenantId && tenantId.length > 0 ? tenantId : 'current';
    const url = `${FIELD_ENDPOINTS.LIST}/stats/${encodeURIComponent(tenantSegment)}`;
    return safeFetch(url, async () => {
      const response = await api.get(url);
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
      const response = await api.get(buildUrl(FIELD_ENDPOINTS.KPI_SNAPSHOT, { fieldId }));
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
   * Trigger KPI refresh — fetches 35+ Sentinel Hub indices, weather, air quality, and solar
   * تحديث KPI: جلب 35+ مؤشر من Sentinel Hub والطقس وجودة الهواء والطاقة الشمسية
   */
  triggerKpiRefresh: async (
    fieldId: string,
    lat: number,
    lng: number,
    _tenantId?: string,
    polygonCoordinates?: number[][]
  ): Promise<FieldKpiSnapshot> => {
    type AnyRecord = Record<string, unknown>;
    const n = (v: unknown): number | undefined =>
      typeof v === 'number' && Number.isFinite(v) ? v : undefined;

    // ── 1. Satellite indices (GET /api/satellite?action=indices gets all themed indices) ──
    let satIndices: AnyRecord = {};
    try {
      // First trigger analysis so the service computes fresh values
      await fetch('/api/satellite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({
          action: 'analyze',
          fieldId,
          latitude: lat,
          longitude: lng,
          analysisType: 'all',
          ...(polygonCoordinates ? { coordinates: polygonCoordinates } : {}),
        }),
      });
      // Then fetch all computed indices
      const idxRes = await fetch(
        `/api/satellite?action=indices&fieldId=${encodeURIComponent(fieldId)}&lat=${lat}&lon=${lng}`,
        { credentials: 'same-origin' }
      );
      if (idxRes.ok) {
        const idxBody = await idxRes.json() as AnyRecord;
        // Backend may nest under indices, vegetation_indices, or return flat
        satIndices = (idxBody.indices ?? idxBody.vegetation_indices ?? idxBody) as AnyRecord;
      }
    } catch { /* non-fatal */ }

    // ── 2. Current weather ────────────────────────────────────────────────────
    let wxData: AnyRecord = {};
    try {
      const wxRes = await fetch('/api/weather', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ action: 'current', lat, lon: lng, field_id: fieldId }),
      });
      if (wxRes.ok) {
        const wxBody = await wxRes.json() as AnyRecord;
        wxData = (wxBody.current ?? wxBody) as AnyRecord;
      }
    } catch { /* non-fatal */ }

    // ── 3. Air quality (OpenWeatherMap Air Pollution API) ─────────────────────
    let aqData: AnyRecord = {};
    try {
      const aqRes = await fetch(
        `/api/airquality?lat=${lat}&lon=${lng}`,
        { credentials: 'same-origin' }
      );
      if (aqRes.ok) {
        aqData = await aqRes.json() as AnyRecord;
      }
    } catch { /* non-fatal */ }

    // ── 4. Solar irradiance (Open-Meteo) ──────────────────────────────────────
    let solarData: AnyRecord = {};
    try {
      const solRes = await fetch(
        `/api/solar?lat=${lat}&lon=${lng}`,
        { credentials: 'same-origin' }
      );
      if (solRes.ok) {
        solarData = await solRes.json() as AnyRecord;
      }
    } catch { /* non-fatal */ }

    // ── 5. Build and persist the full snapshot ────────────────────────────────
    const payload = {
      // Vegetation
      ndvi: n(satIndices.ndvi), evi: n(satIndices.evi), lai: n(satIndices.lai),
      savi: n(satIndices.savi), ndmi: n(satIndices.ndmi), gndvi: n(satIndices.gndvi),
      ndre: n(satIndices.ndre), msavi: n(satIndices.msavi), osavi: n(satIndices.osavi),
      evi2: n(satIndices.evi2), cvi: n(satIndices.cvi), mcari: n(satIndices.mcari),
      tcari: n(satIndices.tcari), wdrvi: n(satIndices.wdrvi), vari: n(satIndices.vari),
      // Water
      ndwi: n(satIndices.ndwi), mndwi: n(satIndices.mndwi),
      turbidity: n(satIndices.turbidity), chlorophyll: n(satIndices.chlorophyll_a ?? satIndices.chlorophyll),
      phycocyanin: n(satIndices.phycocyanin),
      // Soil
      bsi: n(satIndices.bsi), nbsi: n(satIndices.nbsi),
      // Fire
      nbr: n(satIndices.nbr), nbr2: n(satIndices.nbr2), bais2: n(satIndices.bais2),
      // Urban
      ndbi: n(satIndices.ndbi), ibi: n(satIndices.ibi),
      // Snow
      ndsi: n(satIndices.ndsi), ndgi: n(satIndices.ndgi),
      // Atmosphere
      lst: n(satIndices.lst), cloudProbability: n(satIndices.cloud_probability ?? satIndices.cloudProbability),
      arvi: n(satIndices.arvi),
      // Weather
      temperature: n(wxData.temperature_c ?? wxData.temperature),
      humidity: n(wxData.humidity_pct ?? wxData.humidity),
      windSpeed: n(wxData.wind_speed_kmh ?? wxData.wind_speed),
      windDirection: n(wxData.wind_direction_deg ?? wxData.wind_direction),
      precipitation: n(wxData.precipitation_mm ?? wxData.precipitation) ?? 0,
      pressure: n(wxData.pressure_hpa ?? wxData.pressure),
      cloudCover: n(wxData.cloud_cover_pct ?? wxData.cloud_cover),
      visibility: n(wxData.visibility_m ?? wxData.visibility),
      uvIndex: n(wxData.uv_index ?? wxData.uvIndex),
      weatherCondition: typeof wxData.condition === 'string' ? wxData.condition : undefined,
      weatherConditionAr: typeof wxData.condition_ar === 'string' ? wxData.condition_ar : undefined,
      // Air quality
      aqi: typeof aqData.aqi === 'number' ? aqData.aqi : undefined,
      co: n(aqData.co), no: n(aqData.no), no2: n(aqData.no2), o3: n(aqData.o3),
      so2: n(aqData.so2), nh3: n(aqData.nh3), pm25: n(aqData.pm2_5 ?? aqData.pm25),
      pm10: n(aqData.pm10),
      // Solar
      ghiClearSky: n(solarData.ghi_clear_sky), dniClearSky: n(solarData.dni_clear_sky),
      dhiClearSky: n(solarData.dhi_clear_sky), ghiCloudy: n(solarData.ghi_cloudy),
      dniCloudy: n(solarData.dni_cloudy), dhiCloudy: n(solarData.dhi_cloudy),
      // Metadata
      satelliteSource: typeof satIndices.data_source === 'string' ? satIndices.data_source : 'sentinel-hub',
      weatherSource: 'openweather',
    };

    const saveRes = await api.post(buildUrl(FIELD_ENDPOINTS.KPI_SNAPSHOT, { fieldId }), payload);
    return saveRes.data.data || saveRes.data;
  },
};
