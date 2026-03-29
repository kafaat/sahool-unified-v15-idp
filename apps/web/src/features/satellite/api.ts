/**
 * Satellite Feature - API Layer
 * طبقة API لميزة صور الأقمار الصناعية
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { API_PREFIX } from '@sahool/shared-types/contracts';
import type {
  SatelliteField,
  SatelliteImage,
  SatelliteFilters,
  TimeSeriesData,
  SatelliteStats,
  ZoneAnalysis,
} from './types';

// Use shared API factory (handles auth, CSRF, error standardization)
// Longer timeout for satellite image processing
const api = createApiClient({ timeout: 15000 });

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using cached satellite data.',
    ar: 'خطأ في الاتصال. استخدام بيانات الأقمار الصناعية المخزنة.',
  },
  FETCH_FAILED: {
    en: 'Failed to fetch satellite data.',
    ar: 'فشل في جلب بيانات الأقمار الصناعية.',
  },
};

export const satelliteApi = {
  getFields: async (filters?: SatelliteFilters): Promise<SatelliteField[]> => {
    return safeFetch(`${API_PREFIX}/satellite/fields`, async () => {
      const params = new URLSearchParams();
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.indexType) params.set('index_type', filters.indexType);
      if (filters?.healthStatus) params.set('health_status', filters.healthStatus);
      if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
      if (filters?.dateTo) params.set('date_to', filters.dateTo);

      const response = await api.get(`${API_PREFIX}/satellite/fields?${params.toString()}`);
      const data = response.data.data || response.data;
      if (!Array.isArray(data)) {
        throw new Error('Invalid satellite fields response format');
      }
      return data;
    });
  },

  getFieldById: async (id: string): Promise<SatelliteField> => {
    return safeFetch(`${API_PREFIX}/satellite/fields/${id}`, async () => {
      const response = await api.get(`${API_PREFIX}/satellite/fields/${id}`);
      return response.data.data || response.data;
    });
  },

  getImages: async (
    fieldId: string,
    filters?: { dateFrom?: string; dateTo?: string }
  ): Promise<SatelliteImage[]> => {
    return safeFetch(`${API_PREFIX}/satellite/images`, async () => {
      const params = new URLSearchParams();
      params.set('field_id', fieldId);
      if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
      if (filters?.dateTo) params.set('date_to', filters.dateTo);

      const response = await api.get(`${API_PREFIX}/satellite/images?${params.toString()}`);
      return response.data.data || response.data;
    });
  },

  getTimeSeries: async (
    fieldId: string,
    indexType: string,
    period: { from: string; to: string }
  ): Promise<TimeSeriesData[]> => {
    return safeFetch(`${API_PREFIX}/satellite/timeseries`, async () => {
      const params = new URLSearchParams();
      params.set('field_id', fieldId);
      params.set('index_type', indexType);
      params.set('from', period.from);
      params.set('to', period.to);

      const response = await api.get(`${API_PREFIX}/satellite/timeseries?${params.toString()}`);
      return response.data.data || response.data;
    });
  },

  getZoneAnalysis: async (fieldId: string): Promise<ZoneAnalysis[]> => {
    return safeFetch(`${API_PREFIX}/satellite/fields/${fieldId}/zones`, async () => {
      const response = await api.get(`${API_PREFIX}/satellite/fields/${fieldId}/zones`);
      return response.data.data || response.data;
    });
  },

  requestNewCapture: async (
    fieldId: string
  ): Promise<{ requestId: string; estimatedTime: string }> => {
    return safeFetch(`${API_PREFIX}/satellite/fields/${fieldId}/capture`, async () => {
      const response = await api.post(`${API_PREFIX}/satellite/fields/${fieldId}/capture`);
      return response.data.data || response.data;
    });
  },

  getStats: async (): Promise<SatelliteStats> => {
    return safeFetch(`${API_PREFIX}/satellite/stats`, async () => {
      const response = await api.get(`${API_PREFIX}/satellite/stats`);
      return response.data.data || response.data;
    });
  },
};
