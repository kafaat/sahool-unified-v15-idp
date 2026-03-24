/**
 * Crops Feature - API Layer
 * طبقة API لميزة المحاصيل
 */

import { API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient, extractData, logger } from '@/lib/api/factory';
import type { Crop, CropFilters, CropFormData, CropStats } from './types';

const api = createApiClient();

const MOCK_CROPS: Crop[] = [
  {
    id: 'crop-001',
    name: 'Winter Wheat',
    nameAr: 'قمح شتوي',
    variety: 'Sakha 95',
    varietyAr: 'سخا 95',
    category: 'cereals',
    currentStage: 'vegetative',
    fieldId: 'f-001',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    plantingDate: '2025-11-15',
    expectedHarvestDate: '2026-04-20',
    areaHa: 5.5,
    healthScore: 85,
    ndvi: 0.72,
    irrigationType: 'Sprinkler',
    irrigationTypeAr: 'رشاش',
    createdAt: '2025-11-15T00:00:00Z',
    updatedAt: '2026-02-15T10:00:00Z',
  },
  {
    id: 'crop-002',
    name: 'Alfalfa',
    nameAr: 'برسيم حجازي',
    variety: 'Local',
    varietyAr: 'محلي',
    category: 'forage',
    currentStage: 'flowering',
    fieldId: 'f-002',
    fieldName: 'West Field',
    fieldNameAr: 'الحقل الغربي',
    plantingDate: '2025-09-01',
    expectedHarvestDate: '2026-06-30',
    areaHa: 8.0,
    healthScore: 92,
    ndvi: 0.81,
    irrigationType: 'Flood',
    irrigationTypeAr: 'غمر',
    createdAt: '2025-09-01T00:00:00Z',
    updatedAt: '2026-02-10T08:00:00Z',
  },
  {
    id: 'crop-003',
    name: 'Tomato',
    nameAr: 'طماطم',
    variety: 'Heinz 1370',
    varietyAr: 'هاينز 1370',
    category: 'vegetables',
    currentStage: 'fruiting',
    fieldId: 'f-003',
    fieldName: 'Greenhouse A',
    fieldNameAr: 'صوبة أ',
    plantingDate: '2025-12-01',
    expectedHarvestDate: '2026-03-15',
    areaHa: 0.5,
    healthScore: 78,
    ndvi: 0.65,
    irrigationType: 'Drip',
    irrigationTypeAr: 'تنقيط',
    createdAt: '2025-12-01T00:00:00Z',
    updatedAt: '2026-02-12T14:00:00Z',
  },
  {
    id: 'crop-004',
    name: 'Date Palm',
    nameAr: 'نخيل تمر',
    variety: 'Khalas',
    varietyAr: 'خلاص',
    category: 'fruits',
    currentStage: 'vegetative',
    fieldId: 'f-004',
    fieldName: 'Palm Grove',
    fieldNameAr: 'بستان النخيل',
    plantingDate: '2020-03-01',
    expectedHarvestDate: '2026-08-15',
    areaHa: 12.0,
    healthScore: 90,
    ndvi: 0.76,
    irrigationType: 'Bubbler',
    irrigationTypeAr: 'فقاعات',
    createdAt: '2020-03-01T00:00:00Z',
    updatedAt: '2026-02-01T09:00:00Z',
  },
];

const MOCK_STATS: CropStats = {
  totalCrops: 4,
  byCategory: { cereals: 1, forage: 1, vegetables: 1, fruits: 1 },
  byStage: { vegetative: 2, flowering: 1, fruiting: 1 },
  averageHealth: 86,
  totalAreaHa: 26.0,
};

export const cropsApi = {
  getCrops: async (filters?: CropFilters): Promise<Crop[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.category) params.set('category', filters.category);
      if (filters?.stage) params.set('stage', filters.stage);
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${API_PREFIX}/crops?${params.toString()}`);
      const data = extractData<Crop[]>(response);
      if (Array.isArray(data)) return data;
      return MOCK_CROPS;
    } catch {
      logger.warn('Failed to fetch crops, using mock data');
      return MOCK_CROPS;
    }
  },

  getCropById: async (id: string): Promise<Crop> => {
    try {
      const response = await api.get(`${API_PREFIX}/crops/${encodeURIComponent(id)}`);
      return extractData<Crop>(response);
    } catch {
      const mock = MOCK_CROPS.find((c) => c.id === id);
      if (mock) return mock;
      throw new Error(`Crop ${id} not found`);
    }
  },

  createCrop: async (data: CropFormData): Promise<Crop> => {
    const response = await api.post(`${API_PREFIX}/crops`, data);
    return extractData<Crop>(response);
  },

  updateCrop: async (id: string, data: Partial<CropFormData>): Promise<Crop> => {
    const response = await api.put(`${API_PREFIX}/crops/${encodeURIComponent(id)}`, data);
    return extractData<Crop>(response);
  },

  deleteCrop: async (id: string): Promise<void> => {
    await api.delete(`${API_PREFIX}/crops/${encodeURIComponent(id)}`);
  },

  getStats: async (): Promise<CropStats> => {
    try {
      const response = await api.get(`${API_PREFIX}/crops/stats`);
      return extractData<CropStats>(response);
    } catch {
      return MOCK_STATS;
    }
  },
};
