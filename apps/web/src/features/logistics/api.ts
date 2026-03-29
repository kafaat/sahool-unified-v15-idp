/**
 * Logistics Feature - API Layer
 * طبقة API لميزة اللوجستيات
 */

import { LOGISTICS_ENDPOINTS, buildUrl, API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type {
  Shipment,
  ShipmentFilters,
  ShipmentFormData,
  ShipmentTracking,
  Driver,
  Vehicle,
  LogisticsStats,
} from './types';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_FAILED: {
    en: 'Failed to fetch logistics data.',
    ar: 'فشل في جلب بيانات اللوجستيات.',
  },
  CREATE_FAILED: {
    en: 'Failed to create shipment.',
    ar: 'فشل في إنشاء الشحنة.',
  },
};

export const logisticsApi = {
  getShipments: async (filters?: ShipmentFilters): Promise<Shipment[]> => {
    return safeFetch(LOGISTICS_ENDPOINTS.SHIPMENTS, async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.cargoType) params.set('cargo_type', filters.cargoType);
      if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
      if (filters?.dateTo) params.set('date_to', filters.dateTo);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`${LOGISTICS_ENDPOINTS.SHIPMENTS}?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      return [];
    });
  },

  getShipmentById: async (id: string): Promise<Shipment> => {
    return safeFetch(LOGISTICS_ENDPOINTS.SHIPMENT_GET, async () => {
      const response = await api.get(
        buildUrl(LOGISTICS_ENDPOINTS.SHIPMENT_GET, { shipmentId: id })
      );
      return response.data.data || response.data;
    });
  },

  createShipment: async (data: ShipmentFormData): Promise<Shipment> => {
    return safeFetch(LOGISTICS_ENDPOINTS.SHIPMENT_CREATE, async () => {
      const response = await api.post(LOGISTICS_ENDPOINTS.SHIPMENT_CREATE, data);
      return response.data.data || response.data;
    });
  },

  updateShipment: async (id: string, data: Partial<ShipmentFormData>): Promise<Shipment> => {
    return safeFetch(LOGISTICS_ENDPOINTS.SHIPMENT_GET, async () => {
      const response = await api.put(
        buildUrl(LOGISTICS_ENDPOINTS.SHIPMENT_GET, { shipmentId: id }),
        data
      );
      return response.data.data || response.data;
    });
  },

  updateStatus: async (id: string, status: string, notes?: string): Promise<Shipment> => {
    return safeFetch(LOGISTICS_ENDPOINTS.SHIPMENT_GET, async () => {
      const response = await api.patch(
        `${buildUrl(LOGISTICS_ENDPOINTS.SHIPMENT_GET, { shipmentId: id })}/status`,
        { status, notes }
      );
      return response.data.data || response.data;
    });
  },

  getTracking: async (shipmentId: string): Promise<ShipmentTracking[]> => {
    return safeFetch(LOGISTICS_ENDPOINTS.TRACKING, async () => {
      const response = await api.get(buildUrl(LOGISTICS_ENDPOINTS.TRACKING, { shipmentId }));
      return response.data.data || response.data;
    });
  },

  getDrivers: async (): Promise<Driver[]> => {
    return safeFetch(`${API_PREFIX}/logistics/drivers`, async () => {
      const response = await api.get(`${API_PREFIX}/logistics/drivers`);
      return response.data.data || response.data;
    });
  },

  getVehicles: async (): Promise<Vehicle[]> => {
    return safeFetch(LOGISTICS_ENDPOINTS.VEHICLES, async () => {
      const response = await api.get(LOGISTICS_ENDPOINTS.VEHICLES);
      return response.data.data || response.data;
    });
  },

  getStats: async (): Promise<LogisticsStats> => {
    return safeFetch(`${API_PREFIX}/logistics/stats`, async () => {
      const response = await api.get(`${API_PREFIX}/logistics/stats`);
      return response.data.data || response.data;
    });
  },
};
