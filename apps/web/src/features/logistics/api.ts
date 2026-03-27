/**
 * Logistics Feature - API Layer
 * طبقة API لميزة اللوجستيات
 */

import { LOGISTICS_ENDPOINTS, buildUrl, API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient, logger } from '@/lib/api/factory';
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

const MOCK_SHIPMENTS: Shipment[] = [
  {
    id: '1',
    orderNumber: 'SHP-2026-001',
    origin: 'Riyadh Warehouse',
    originAr: 'مستودع الرياض',
    destination: 'Al-Kharj Farm',
    destinationAr: 'مزرعة الخرج',
    status: 'in_transit',
    cargoType: 'fertilizers',
    cargo: 'Fertilizers',
    cargoAr: 'أسمدة',
    weight: 2500,
    weightUnit: 'kg',
    estimatedDelivery: '2026-01-25',
    driver: { id: 'd1', name: 'محمد العلي', phone: '+966501234567' },
    vehicle: { id: 'v1', plateNumber: 'ABC 1234', type: 'truck' },
    trackingNumber: 'TRK-001-2026',
    cost: 1500,
    metadata: {},
    createdAt: '2026-01-24T08:00:00Z',
    updatedAt: '2026-01-24T14:30:00Z',
  },
  {
    id: '2',
    orderNumber: 'SHP-2026-002',
    origin: 'Dammam Port',
    originAr: 'ميناء الدمام',
    destination: 'Qassim Distribution',
    destinationAr: 'توزيع القصيم',
    status: 'pending',
    cargoType: 'equipment',
    cargo: 'Agricultural Equipment',
    cargoAr: 'معدات زراعية',
    weight: 5000,
    weightUnit: 'kg',
    estimatedDelivery: '2026-01-27',
    cost: 3500,
    metadata: {},
    createdAt: '2026-01-24T10:00:00Z',
    updatedAt: '2026-01-24T10:00:00Z',
  },
  {
    id: '3',
    orderNumber: 'SHP-2026-003',
    origin: 'Jeddah Hub',
    originAr: 'مركز جدة',
    destination: 'Taif Farms',
    destinationAr: 'مزارع الطائف',
    status: 'delivered',
    cargoType: 'seeds',
    cargo: 'Seeds',
    cargoAr: 'بذور',
    weight: 800,
    weightUnit: 'kg',
    estimatedDelivery: '2026-01-24',
    actualDelivery: '2026-01-24',
    driver: { id: 'd2', name: 'خالد السعيد' },
    vehicle: { id: 'v2', plateNumber: 'XYZ 5678', type: 'van' },
    cost: 800,
    metadata: {},
    createdAt: '2026-01-22T09:00:00Z',
    updatedAt: '2026-01-24T11:00:00Z',
  },
  {
    id: '4',
    orderNumber: 'SHP-2026-004',
    origin: 'Al-Ahsa Center',
    originAr: 'مركز الأحساء',
    destination: 'Hofuf Market',
    destinationAr: 'سوق الهفوف',
    status: 'delayed',
    cargoType: 'produce',
    cargo: 'Fresh Produce',
    cargoAr: 'منتجات طازجة',
    weight: 1200,
    weightUnit: 'kg',
    estimatedDelivery: '2026-01-24',
    driver: { id: 'd3', name: 'أحمد الفهد' },
    notes: 'Delayed due to vehicle maintenance',
    notesAr: 'تأخر بسبب صيانة المركبة',
    metadata: {},
    createdAt: '2026-01-23T14:00:00Z',
    updatedAt: '2026-01-24T16:00:00Z',
  },
];

const MOCK_STATS: LogisticsStats = {
  totalShipments: 4,
  pendingShipments: 1,
  inTransitShipments: 1,
  deliveredShipments: 1,
  delayedShipments: 1,
  totalWeight: 9500,
  activeDrivers: 3,
  availableVehicles: 5,
};

export const logisticsApi = {
  getShipments: async (filters?: ShipmentFilters): Promise<Shipment[]> => {
    try {
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

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_SHIPMENTS;
    } catch (error) {
      logger.warn('Failed to fetch shipments, using mock data:', error);
      return MOCK_SHIPMENTS;
    }
  },

  getShipmentById: async (id: string): Promise<Shipment> => {
    try {
      const response = await api.get(
        buildUrl(LOGISTICS_ENDPOINTS.SHIPMENT_GET, { shipmentId: id })
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch shipment ${id}, using mock data:`, error);
      const mockShipment = MOCK_SHIPMENTS.find((s) => s.id === id);
      if (mockShipment) return mockShipment;
      throw new Error(`Shipment with ID ${id} not found`);
    }
  },

  createShipment: async (data: ShipmentFormData): Promise<Shipment> => {
    try {
      const response = await api.post(LOGISTICS_ENDPOINTS.SHIPMENT_CREATE, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to create shipment:', error);
      throw error;
    }
  },

  updateShipment: async (id: string, data: Partial<ShipmentFormData>): Promise<Shipment> => {
    try {
      const response = await api.put(
        buildUrl(LOGISTICS_ENDPOINTS.SHIPMENT_GET, { shipmentId: id }),
        data
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update shipment ${id}:`, error);
      throw error;
    }
  },

  updateStatus: async (id: string, status: string, notes?: string): Promise<Shipment> => {
    try {
      const response = await api.patch(
        `${buildUrl(LOGISTICS_ENDPOINTS.SHIPMENT_GET, { shipmentId: id })}/status`,
        { status, notes }
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update shipment status ${id}:`, error);
      throw error;
    }
  },

  getTracking: async (shipmentId: string): Promise<ShipmentTracking[]> => {
    try {
      const response = await api.get(buildUrl(LOGISTICS_ENDPOINTS.TRACKING, { shipmentId }));
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch tracking for shipment ${shipmentId}:`, error);
      return [];
    }
  },

  getDrivers: async (): Promise<Driver[]> => {
    try {
      const response = await api.get(`${API_PREFIX}/logistics/drivers`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch drivers:', error);
      return [];
    }
  },

  getVehicles: async (): Promise<Vehicle[]> => {
    try {
      const response = await api.get(LOGISTICS_ENDPOINTS.VEHICLES);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch vehicles:', error);
      return [];
    }
  },

  getStats: async (): Promise<LogisticsStats> => {
    try {
      const response = await api.get(`${API_PREFIX}/logistics/stats`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch logistics stats, using mock data:', error);
      return MOCK_STATS;
    }
  },
};
