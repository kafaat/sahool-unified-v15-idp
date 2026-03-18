/**
 * Satellite Feature - API Layer
 * طبقة API لميزة صور الأقمار الصناعية
 */

import { createApiClient, logger } from "@/lib/api/factory";
import { API_PREFIX } from "@sahool/shared-types/contracts";
import type {
  SatelliteField,
  SatelliteImage,
  SatelliteFilters,
  TimeSeriesData,
  SatelliteStats,
  ZoneAnalysis,
} from "./types";

// Use shared API factory (handles auth, CSRF, error standardization)
// Longer timeout for satellite image processing
const api = createApiClient({ timeout: 15000 });

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: "Network error. Using cached satellite data.",
    ar: "خطأ في الاتصال. استخدام بيانات الأقمار الصناعية المخزنة.",
  },
  FETCH_FAILED: {
    en: "Failed to fetch satellite data.",
    ar: "فشل في جلب بيانات الأقمار الصناعية.",
  },
};

const MOCK_FIELDS: SatelliteField[] = [
  {
    id: "1",
    fieldId: "field-001",
    fieldName: "Wheat Field A",
    fieldNameAr: "حقل القمح أ",
    area: 15.5,
    coordinates: { lat: 24.7136, lng: 46.6753 },
    lastCapture: "2026-01-24",
    lastCaptureSource: "sentinel-2",
    cloudCoverage: 5,
    indices: {
      ndvi: 0.78,
      ndviChange: 0.05,
      ndwi: 0.32,
      evi: 0.65,
      savi: 0.58,
      ndre: 0.42,
      lai: 3.2,
    },
    healthStatus: "excellent",
    healthScore: 92,
    metadata: {},
    updatedAt: "2026-01-24T10:00:00Z",
  },
  {
    id: "2",
    fieldId: "field-002",
    fieldName: "Barley Field B",
    fieldNameAr: "حقل الشعير ب",
    area: 12.3,
    coordinates: { lat: 24.72, lng: 46.68 },
    lastCapture: "2026-01-24",
    lastCaptureSource: "sentinel-2",
    cloudCoverage: 8,
    indices: {
      ndvi: 0.62,
      ndviChange: -0.03,
      ndwi: 0.28,
      evi: 0.52,
      savi: 0.45,
      ndre: 0.31,
      lai: 2.4,
    },
    healthStatus: "good",
    healthScore: 78,
    metadata: {},
    updatedAt: "2026-01-24T10:00:00Z",
  },
  {
    id: "3",
    fieldId: "field-003",
    fieldName: "Vegetable Plot C",
    fieldNameAr: "قطعة الخضروات ج",
    area: 8.7,
    coordinates: { lat: 24.705, lng: 46.67 },
    lastCapture: "2026-01-23",
    lastCaptureSource: "sentinel-2",
    cloudCoverage: 12,
    indices: {
      ndvi: 0.45,
      ndviChange: -0.08,
      ndwi: -0.05,
      evi: 0.38,
      savi: 0.32,
      ndre: 0.18,
      lai: 1.5,
    },
    healthStatus: "moderate",
    healthScore: 55,
    alerts: ["Low NDVI detected", "Water stress detected (NDWI < 0)"],
    metadata: {},
    updatedAt: "2026-01-23T10:00:00Z",
  },
];

const MOCK_STATS: SatelliteStats = {
  totalFields: 3,
  averageNdvi: 0.62,
  ndviTrend: "stable",
  lastCapture: "2026-01-24",
  fieldsMonitored: 3,
  alertsCount: 1,
  healthDistribution: {
    excellent: 1,
    good: 1,
    moderate: 1,
    poor: 0,
    critical: 0,
  },
  totalArea: 36.5,
};

export const satelliteApi = {
  getFields: async (filters?: SatelliteFilters): Promise<SatelliteField[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.fieldId) params.set("field_id", filters.fieldId);
      if (filters?.indexType) params.set("index_type", filters.indexType);
      if (filters?.healthStatus) params.set("health_status", filters.healthStatus);
      if (filters?.dateFrom) params.set("date_from", filters.dateFrom);
      if (filters?.dateTo) params.set("date_to", filters.dateTo);

      const response = await api.get(`${API_PREFIX}/satellite/fields?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      logger.warn("API returned unexpected format, using mock data");
      return MOCK_FIELDS;
    } catch (error) {
      logger.warn("Failed to fetch satellite fields, using mock data:", error);
      return MOCK_FIELDS;
    }
  },

  getFieldById: async (id: string): Promise<SatelliteField> => {
    try {
      const response = await api.get(`${API_PREFIX}/satellite/fields/${id}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch satellite field ${id}, using mock data:`, error);
      const mockField = MOCK_FIELDS.find((f) => f.id === id || f.fieldId === id);
      if (mockField) return mockField;
      throw new Error(`Satellite field with ID ${id} not found`);
    }
  },

  getImages: async (fieldId: string, filters?: { dateFrom?: string; dateTo?: string }): Promise<SatelliteImage[]> => {
    try {
      const params = new URLSearchParams();
      params.set("field_id", fieldId);
      if (filters?.dateFrom) params.set("date_from", filters.dateFrom);
      if (filters?.dateTo) params.set("date_to", filters.dateTo);

      const response = await api.get(`${API_PREFIX}/satellite/images?${params.toString()}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch images for field ${fieldId}:`, error);
      return [];
    }
  },

  getTimeSeries: async (
    fieldId: string,
    indexType: string,
    period: { from: string; to: string }
  ): Promise<TimeSeriesData[]> => {
    try {
      const params = new URLSearchParams();
      params.set("field_id", fieldId);
      params.set("index_type", indexType);
      params.set("from", period.from);
      params.set("to", period.to);

      const response = await api.get(`${API_PREFIX}/satellite/timeseries?${params.toString()}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch time series for field ${fieldId}:`, error);
      return [];
    }
  },

  getZoneAnalysis: async (fieldId: string): Promise<ZoneAnalysis[]> => {
    try {
      const response = await api.get(`${API_PREFIX}/satellite/fields/${fieldId}/zones`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch zone analysis for field ${fieldId}:`, error);
      return [];
    }
  },

  requestNewCapture: async (fieldId: string): Promise<{ requestId: string; estimatedTime: string }> => {
    try {
      const response = await api.post(`${API_PREFIX}/satellite/fields/${fieldId}/capture`);
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to request capture for field ${fieldId}:`, error);
      throw error;
    }
  },

  getStats: async (): Promise<SatelliteStats> => {
    try {
      const response = await api.get(`${API_PREFIX}/satellite/stats`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Failed to fetch satellite stats, using mock data:", error);
      return MOCK_STATS;
    }
  },
};
