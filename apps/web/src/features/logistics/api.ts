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

// Shipment status values accepted by the backend logistics service
// (apps/services/logistics-service ShipmentStatus enum). Kept loose as a
// string set so we can pass through unmapped statuses without blocking.
const VALID_SHIPMENT_STATUSES: ReadonlySet<string> = new Set([
  'pending',
  'scheduled',
  'collecting',
  'in_transit',
  'at_storage',
  'delivering',
  'delivered',
  'delayed',
  'cancelled',
]);

const MAX_SHIPMENT_PAGE_SIZE = 100;
const DEFAULT_SHIPMENT_PAGE_SIZE = 50;

export interface ShipmentListParams extends ShipmentFilters {
  page?: number;
  pageSize?: number;
}

export const logisticsApi = {
  getShipments: async (filters?: ShipmentListParams): Promise<Shipment[]> => {
    return safeFetch(LOGISTICS_ENDPOINTS.SHIPMENTS, async () => {
      const params = new URLSearchParams();
      if (filters?.status && VALID_SHIPMENT_STATUSES.has(filters.status)) {
        params.set('status', filters.status);
      }
      if (filters?.cargoType) params.set('cargo_type', filters.cargoType);
      if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
      if (filters?.dateTo) params.set('date_to', filters.dateTo);
      if (filters?.search) params.set('search', filters.search);

      // Pagination - backend defaults limit=50/max=100
      const pageSize = Math.min(
        Math.max(1, Math.floor(filters?.pageSize ?? DEFAULT_SHIPMENT_PAGE_SIZE)),
        MAX_SHIPMENT_PAGE_SIZE
      );
      const page = Math.max(1, Math.floor(filters?.page ?? 1));
      params.set('limit', String(pageSize));
      params.set('offset', String((page - 1) * pageSize));

      const response = await api.get(`${LOGISTICS_ENDPOINTS.SHIPMENTS}?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }
      // Backend returns {shipments: [...], total, limit, offset}
      if (data && Array.isArray((data as { shipments?: unknown }).shipments)) {
        return (data as { shipments: Shipment[] }).shipments;
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
      // Validate status against known enum to prevent arbitrary mutation
      if (!VALID_SHIPMENT_STATUSES.has(status)) {
        throw new Error(`Invalid shipment status: ${status}`);
      }
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
