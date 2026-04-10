/**
 * Disaster Assessment Feature - API Layer
 * طبقة API لميزة تقييم الكوارث
 */

import { DISASTER_ENDPOINTS, API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type {
  RiskAssessment,
  DisasterEvent,
  DisasterFilters,
  DisasterFormData,
  DisasterStats,
  WeatherAlert,
} from './types';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using cached data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المخزنة.',
  },
  FETCH_FAILED: {
    en: 'Failed to fetch disaster assessment data.',
    ar: 'فشل في جلب بيانات تقييم الكوارث.',
  },
  CREATE_FAILED: {
    en: 'Failed to create disaster event.',
    ar: 'فشل في إنشاء حدث الكارثة.',
  },
};

export const disasterApi = {
  getRisks: async (filters?: DisasterFilters): Promise<RiskAssessment[]> => {
    return safeFetch(`${DISASTER_ENDPOINTS.ASSESS}/risks`, async () => {
      const params = new URLSearchParams();
      if (filters?.type) params.set('type', filters.type);
      if (filters?.riskLevel) params.set('risk_level', filters.riskLevel);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`${DISASTER_ENDPOINTS.ASSESS}/risks?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getRiskById: async (id: string): Promise<RiskAssessment> => {
    const safeId = encodeURIComponent(id);
    return safeFetch(`${DISASTER_ENDPOINTS.ASSESS}/risks/${safeId}`, async () => {
      const response = await api.get(`${DISASTER_ENDPOINTS.ASSESS}/risks/${safeId}`);
      return response.data.data || response.data;
    });
  },

  getEvents: async (filters?: DisasterFilters): Promise<DisasterEvent[]> => {
    return safeFetch(`${API_PREFIX}/disaster/events`, async () => {
      const params = new URLSearchParams();
      if (filters?.type) params.set('type', filters.type);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
      if (filters?.dateTo) params.set('date_to', filters.dateTo);

      const response = await api.get(`${API_PREFIX}/disaster/events?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getEventById: async (id: string): Promise<DisasterEvent> => {
    return safeFetch(`${API_PREFIX}/disaster/events/${id}`, async () => {
      const response = await api.get(`${API_PREFIX}/disaster/events/${id}`);
      return response.data.data || response.data;
    });
  },

  createEvent: async (data: DisasterFormData): Promise<DisasterEvent> => {
    return safeFetch(`${API_PREFIX}/disaster/events`, async () => {
      const response = await api.post(`${API_PREFIX}/disaster/events`, data);
      return response.data.data || response.data;
    });
  },

  updateEvent: async (id: string, data: Partial<DisasterFormData>): Promise<DisasterEvent> => {
    return safeFetch(`${API_PREFIX}/disaster/events/${id}`, async () => {
      const response = await api.put(`${API_PREFIX}/disaster/events/${id}`, data);
      return response.data.data || response.data;
    });
  },

  updateEventStatus: async (id: string, status: string): Promise<DisasterEvent> => {
    return safeFetch(`${API_PREFIX}/disaster/events/${id}/status`, async () => {
      const response = await api.patch(`${API_PREFIX}/disaster/events/${id}/status`, { status });
      return response.data.data || response.data;
    });
  },

  getWeatherAlerts: async (): Promise<WeatherAlert[]> => {
    return safeFetch(DISASTER_ENDPOINTS.ALERTS, async () => {
      const response = await api.get(DISASTER_ENDPOINTS.ALERTS);
      return response.data.data || response.data;
    });
  },

  getStats: async (): Promise<DisasterStats> => {
    return safeFetch(`${API_PREFIX}/disaster/stats`, async () => {
      const response = await api.get(`${API_PREFIX}/disaster/stats`);
      return response.data.data || response.data;
    });
  },
};
