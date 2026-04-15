/**
 * Drone Feature - API Layer
 * طبقة API لميزة الطائرات بدون طيار
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { DRONE_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import type { DroneFlight, DroneDevice, FlightPlan, DroneFilters } from './types';

const api = createApiClient();

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_FLIGHTS_FAILED: { en: 'Failed to fetch drone flights.', ar: 'فشل في جلب رحلات الطائرات.' },
  CREATE_FLIGHT_FAILED: { en: 'Failed to create flight plan.', ar: 'فشل في إنشاء خطة الرحلة.' },
  FETCH_DEVICES_FAILED: { en: 'Failed to fetch drone devices.', ar: 'فشل في جلب أجهزة الطائرات.' },
};

export const droneApi = {
  getFlights: async (filters?: DroneFilters): Promise<DroneFlight[]> => {
    return safeFetch(DRONE_ENDPOINTS.FLIGHTS, async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.droneId) params.set('drone_id', filters.droneId);
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      const response = await api.get(`${DRONE_ENDPOINTS.FLIGHTS}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getFlightById: async (id: string): Promise<DroneFlight> => {
    return safeFetch(DRONE_ENDPOINTS.FLIGHT_GET, async () => {
      const url = buildUrl(DRONE_ENDPOINTS.FLIGHT_GET, { flightId: id });
      const response = await api.get(url);
      return response.data.data || response.data;
    });
  },

  createFlightPlan: async (plan: FlightPlan): Promise<DroneFlight> => {
    return safeFetch(DRONE_ENDPOINTS.FLIGHT_PLAN, async () => {
      const response = await api.post(DRONE_ENDPOINTS.FLIGHT_PLAN, plan);
      return response.data.data || response.data;
    });
  },

  getDevices: async (): Promise<DroneDevice[]> => {
    return safeFetch(DRONE_ENDPOINTS.DEVICES, async () => {
      const response = await api.get(DRONE_ENDPOINTS.DEVICES);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },
};
