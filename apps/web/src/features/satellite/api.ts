/**
 * Satellite Feature - API Layer
 * طبقة API لميزة صور الأقمار الصناعية
 */

import axios from 'axios';
import { safeFetch } from '@/lib/api/safe-fetch';
import type {
  SatelliteField,
  SatelliteImage,
  SatelliteFilters,
  TimeSeriesData,
  SatelliteStats,
  ZoneAnalysis,
} from './types';

// Use a plain Axios instance with NO baseURL so requests resolve to the
// Next.js origin (same-origin). The catch-all at /api/satellite/[...path]
// intercepts these calls server-side, reads the httpOnly access_token cookie,
// and adds Authorization: Bearer before proxying to vegetation-analysis-service.
// Using /api/v1/satellite/... would be intercepted by the Kong catch-all rewrite
// in next.config.js before reaching the route handler, so we use /api/satellite/
// (outside the /api/v1/ rewrite scope) to guarantee the proxy route is invoked.
const api = axios.create({
  timeout: 15000,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
});

// Proxy base path — intentionally NOT under /api/v1/ to avoid the Kong rewrite.
const SATELLITE_PROXY = '/api/satellite';

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
    return safeFetch(`${SATELLITE_PROXY}/fields`, async () => {
      const params = new URLSearchParams();
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.indexType) params.set('index_type', filters.indexType);
      if (filters?.healthStatus) params.set('health_status', filters.healthStatus);
      if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
      if (filters?.dateTo) params.set('date_to', filters.dateTo);

      const response = await api.get(`${SATELLITE_PROXY}/fields?${params.toString()}`);
      const data = response.data.data || response.data;
      if (!Array.isArray(data)) {
        throw new Error('Invalid satellite fields response format | تنسيق استجابة حقول الأقمار الصناعية غير صالح');
      }
      return data;
    });
  },

  getFieldById: async (id: string): Promise<SatelliteField> => {
    return safeFetch(`${SATELLITE_PROXY}/fields/${id}`, async () => {
      const response = await api.get(`${SATELLITE_PROXY}/fields/${id}`);
      return response.data.data || response.data;
    });
  },

  getImages: async (
    fieldId: string,
    filters?: { dateFrom?: string; dateTo?: string }
  ): Promise<SatelliteImage[]> => {
    return safeFetch(`${SATELLITE_PROXY}/images`, async () => {
      const params = new URLSearchParams();
      params.set('field_id', fieldId);
      if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
      if (filters?.dateTo) params.set('date_to', filters.dateTo);

      const response = await api.get(`${SATELLITE_PROXY}/images?${params.toString()}`);
      return response.data.data || response.data;
    });
  },

  getTimeSeries: async (
    fieldId: string,
    indexType: string,
    period: { from: string; to: string }
  ): Promise<TimeSeriesData[]> => {
    return safeFetch(`${SATELLITE_PROXY}/timeseries`, async () => {
      const params = new URLSearchParams();
      params.set('field_id', fieldId);
      params.set('index_type', indexType);
      params.set('from', period.from);
      params.set('to', period.to);

      const response = await api.get(`${SATELLITE_PROXY}/timeseries?${params.toString()}`);
      return response.data.data || response.data;
    });
  },

  getZoneAnalysis: async (fieldId: string): Promise<ZoneAnalysis[]> => {
    return safeFetch(`${SATELLITE_PROXY}/fields/${fieldId}/zones`, async () => {
      const response = await api.get(`${SATELLITE_PROXY}/fields/${fieldId}/zones`);
      return response.data.data || response.data;
    });
  },

  requestNewCapture: async (
    fieldId: string
  ): Promise<{ requestId: string; estimatedTime: string }> => {
    return safeFetch(`${SATELLITE_PROXY}/fields/${fieldId}/capture`, async () => {
      const response = await api.post(`${SATELLITE_PROXY}/fields/${fieldId}/capture`);
      return response.data.data || response.data;
    });
  },

  getStats: async (): Promise<SatelliteStats> => {
    return safeFetch(`${SATELLITE_PROXY}/stats`, async () => {
      const response = await api.get(`${SATELLITE_PROXY}/stats`);
      return response.data.data || response.data;
    });
  },
};
