/**
 * Drone Feature - API Layer
 * طبقة API لميزة الطائرات بدون طيار
 */

import { createApiClient, logger } from '@/lib/api/factory';
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

const MOCK_FLIGHTS: DroneFlight[] = [
  {
    id: 'flight-1',
    name: 'NDVI Survey - North Field',
    nameAr: 'مسح NDVI - الحقل الشمالي',
    droneId: 'drone-1',
    droneName: 'DJI Phantom 4 RTK',
    fieldId: 'field-1',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    status: 'completed',
    missionType: 'survey',
    altitude: 50,
    speed: 5,
    duration: 25,
    coverage: 95,
    startedAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    completedAt: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
  },
];

const MOCK_DEVICES: DroneDevice[] = [
  {
    id: 'drone-1',
    name: 'DJI Phantom 4 RTK',
    nameAr: 'دي جي آي فانتوم 4 RTK',
    model: 'Phantom 4 RTK',
    manufacturer: 'DJI',
    status: 'available',
    battery: 85,
    lastFlight: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    totalFlightHours: 120,
  },
];

export const droneApi = {
  getFlights: async (filters?: DroneFilters): Promise<DroneFlight[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.droneId) params.set('drone_id', filters.droneId);
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      const response = await api.get(`${DRONE_ENDPOINTS.FLIGHTS}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return MOCK_FLIGHTS;
    } catch (error) {
      logger.warn('Failed to fetch drone flights, using mock data:', error);
      return MOCK_FLIGHTS;
    }
  },

  getFlightById: async (id: string): Promise<DroneFlight> => {
    try {
      const url = buildUrl(DRONE_ENDPOINTS.FLIGHT_GET, { flightId: id });
      const response = await api.get(url);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch flight ${id}:`, error);
      const mock = MOCK_FLIGHTS.find((f) => f.id === id);
      if (mock) return mock;
      throw new Error(ERROR_MESSAGES.FETCH_FLIGHTS_FAILED.en);
    }
  },

  createFlightPlan: async (plan: FlightPlan): Promise<DroneFlight> => {
    try {
      const response = await api.post(DRONE_ENDPOINTS.FLIGHT_PLAN, plan);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to create flight plan:', error);
      throw new Error(ERROR_MESSAGES.CREATE_FLIGHT_FAILED.en);
    }
  },

  getDevices: async (): Promise<DroneDevice[]> => {
    try {
      const response = await api.get(DRONE_ENDPOINTS.DEVICES);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return MOCK_DEVICES;
    } catch (error) {
      logger.warn('Failed to fetch drone devices, using mock data:', error);
      return MOCK_DEVICES;
    }
  },
};
