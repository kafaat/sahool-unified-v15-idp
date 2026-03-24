/**
 * Farms Feature - API Layer
 * طبقة API لميزة المزارع
 */

import { FARM_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import { createApiClient, extractData, logger } from '@/lib/api/factory';
import type { Farm, FarmFilters, FarmFormData, FarmStats } from './types';

const api = createApiClient();

const MOCK_FARMS: Farm[] = [
  {
    id: 'farm-001',
    name: 'Al-Rashid Farm',
    nameAr: 'مزرعة الراشد',
    owner: 'Ahmad Al-Rashid',
    ownerAr: 'أحمد الراشد',
    location: 'Riyadh Province',
    locationAr: 'منطقة الرياض',
    region: 'central',
    regionAr: 'الوسطى',
    totalAreaHa: 45.5,
    cultivatedAreaHa: 38.2,
    fieldsCount: 8,
    workersCount: 12,
    waterSource: 'Well + Canal',
    waterSourceAr: 'بئر + قناة',
    status: 'active',
    coordinates: { lat: 24.7136, lng: 46.6753 },
    createdAt: '2024-06-01T00:00:00Z',
    updatedAt: '2026-02-15T10:00:00Z',
  },
  {
    id: 'farm-002',
    name: 'Green Valley Farm',
    nameAr: 'مزرعة الوادي الأخضر',
    owner: 'Mohammed Al-Harbi',
    ownerAr: 'محمد الحربي',
    location: 'Al-Qassim',
    locationAr: 'القصيم',
    region: 'central',
    regionAr: 'الوسطى',
    totalAreaHa: 120,
    cultivatedAreaHa: 95,
    fieldsCount: 15,
    workersCount: 25,
    waterSource: 'Pivot Irrigation',
    waterSourceAr: 'ري محوري',
    status: 'active',
    coordinates: { lat: 26.3266, lng: 43.9742 },
    createdAt: '2024-01-15T00:00:00Z',
    updatedAt: '2026-02-10T08:00:00Z',
  },
  {
    id: 'farm-003',
    name: 'Desert Oasis Farm',
    nameAr: 'مزرعة واحة الصحراء',
    owner: 'Khalid Al-Otaibi',
    ownerAr: 'خالد العتيبي',
    location: 'Al-Ahsa',
    locationAr: 'الأحساء',
    region: 'eastern',
    regionAr: 'الشرقية',
    totalAreaHa: 80,
    cultivatedAreaHa: 60,
    fieldsCount: 10,
    workersCount: 18,
    waterSource: 'Spring + Drip',
    waterSourceAr: 'ينبوع + تنقيط',
    status: 'active',
    coordinates: { lat: 25.3547, lng: 49.5872 },
    createdAt: '2024-09-01T00:00:00Z',
    updatedAt: '2026-01-20T14:00:00Z',
  },
];

const MOCK_STATS: FarmStats = {
  totalFarms: 3,
  activeFarms: 3,
  totalAreaHa: 245.5,
  cultivatedAreaHa: 193.2,
  totalWorkers: 55,
};

export const farmsApi = {
  getFarms: async (filters?: FarmFilters): Promise<Farm[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.region) params.set('region', filters.region);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${FARM_ENDPOINTS.LIST}?${params.toString()}`);
      const data = extractData<Farm[]>(response);
      if (Array.isArray(data)) return data;
      return MOCK_FARMS;
    } catch {
      logger.warn('Failed to fetch farms, using mock data');
      return MOCK_FARMS;
    }
  },

  getFarmById: async (id: string): Promise<Farm> => {
    try {
      const response = await api.get(buildUrl(FARM_ENDPOINTS.GET, { farmId: id }));
      return extractData<Farm>(response);
    } catch {
      const mock = MOCK_FARMS.find((f) => f.id === id);
      if (mock) return mock;
      throw new Error(`Farm ${id} not found`);
    }
  },

  createFarm: async (data: FarmFormData): Promise<Farm> => {
    const response = await api.post(FARM_ENDPOINTS.CREATE, data);
    return extractData<Farm>(response);
  },

  updateFarm: async (id: string, data: Partial<FarmFormData>): Promise<Farm> => {
    const response = await api.put(buildUrl(FARM_ENDPOINTS.UPDATE, { farmId: id }), data);
    return extractData<Farm>(response);
  },

  deleteFarm: async (id: string): Promise<void> => {
    await api.delete(buildUrl(FARM_ENDPOINTS.DELETE, { farmId: id }));
  },

  getStats: async (): Promise<FarmStats> => {
    try {
      const response = await api.get(`${FARM_ENDPOINTS.LIST}/stats`);
      return extractData<FarmStats>(response);
    } catch {
      return MOCK_STATS;
    }
  },
};
