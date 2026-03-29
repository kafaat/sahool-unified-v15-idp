/**
 * Disaster Assessment Feature - API Layer
 * طبقة API لميزة تقييم الكوارث
 */

import { DISASTER_ENDPOINTS, API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient, logger } from '@/lib/api/factory';
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

// Mock data for fallback (extracted to separate file for bundle optimization)
import { MOCK_RISKS, MOCK_EVENTS, MOCK_STATS } from './api.mock';

export const disasterApi = {
  getRisks: async (filters?: DisasterFilters): Promise<RiskAssessment[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.type) params.set('type', filters.type);
      if (filters?.riskLevel) params.set('risk_level', filters.riskLevel);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`${DISASTER_ENDPOINTS.ASSESS}/risks?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_RISKS;
    } catch (error) {
      logger.warn('Failed to fetch risks, using mock data:', error);
      return MOCK_RISKS;
    }
  },

  getRiskById: async (id: string): Promise<RiskAssessment> => {
    try {
      const response = await api.get(`${DISASTER_ENDPOINTS.ASSESS}/risks/${id}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch risk ${id}, using mock data:`, error);
      const mockRisk = MOCK_RISKS.find((r) => r.id === id);
      if (mockRisk) return mockRisk;
      throw new Error(`Risk assessment with ID ${id} not found`);
    }
  },

  getEvents: async (filters?: DisasterFilters): Promise<DisasterEvent[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.type) params.set('type', filters.type);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
      if (filters?.dateTo) params.set('date_to', filters.dateTo);

      const response = await api.get(`${API_PREFIX}/disaster/events?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      return MOCK_EVENTS;
    } catch (error) {
      logger.warn('Failed to fetch events, using mock data:', error);
      return MOCK_EVENTS;
    }
  },

  getEventById: async (id: string): Promise<DisasterEvent> => {
    try {
      const response = await api.get(`${API_PREFIX}/disaster/events/${id}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch event ${id}, using mock data:`, error);
      const mockEvent = MOCK_EVENTS.find((e) => e.id === id);
      if (mockEvent) return mockEvent;
      throw new Error(`Disaster event with ID ${id} not found`);
    }
  },

  createEvent: async (data: DisasterFormData): Promise<DisasterEvent> => {
    try {
      const response = await api.post(`${API_PREFIX}/disaster/events`, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to create disaster event:', error);
      throw error;
    }
  },

  updateEvent: async (id: string, data: Partial<DisasterFormData>): Promise<DisasterEvent> => {
    try {
      const response = await api.put(`${API_PREFIX}/disaster/events/${id}`, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update event ${id}:`, error);
      throw error;
    }
  },

  updateEventStatus: async (id: string, status: string): Promise<DisasterEvent> => {
    try {
      const response = await api.patch(`${API_PREFIX}/disaster/events/${id}/status`, { status });
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update event status ${id}:`, error);
      throw error;
    }
  },

  getWeatherAlerts: async (): Promise<WeatherAlert[]> => {
    return safeFetch(DISASTER_ENDPOINTS.ALERTS, async () => {
      const response = await api.get(DISASTER_ENDPOINTS.ALERTS);
      return response.data.data || response.data;
    });
  },

  getStats: async (): Promise<DisasterStats> => {
    try {
      const response = await api.get(`${API_PREFIX}/disaster/stats`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch disaster stats, using mock data:', error);
      return MOCK_STATS;
    }
  },
};
