/**
 * Crops Feature - API Layer
 * طبقة API لميزة المحاصيل
 */

import { API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient, extractData } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type { Crop, CropFilters, CropFormData, CropStats } from './types';

const api = createApiClient();

export const cropsApi = {
  getCrops: async (filters?: CropFilters): Promise<Crop[]> => {
    return safeFetch(`${API_PREFIX}/crops`, async () => {
      const params = new URLSearchParams();
      if (filters?.category) params.set('category', filters.category);
      if (filters?.stage) params.set('stage', filters.stage);
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${API_PREFIX}/crops?${params.toString()}`);
      const data = extractData<Crop[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getCropById: async (id: string): Promise<Crop> => {
    return safeFetch(`${API_PREFIX}/crops/${id}`, async () => {
      const response = await api.get(`${API_PREFIX}/crops/${encodeURIComponent(id)}`);
      return extractData<Crop>(response);
    });
  },

  createCrop: async (data: CropFormData): Promise<Crop> => {
    return safeFetch(`${API_PREFIX}/crops`, async () => {
      const response = await api.post(`${API_PREFIX}/crops`, data);
      return extractData<Crop>(response);
    });
  },

  updateCrop: async (id: string, data: Partial<CropFormData>): Promise<Crop> => {
    return safeFetch(`${API_PREFIX}/crops/${id}`, async () => {
      const response = await api.put(`${API_PREFIX}/crops/${encodeURIComponent(id)}`, data);
      return extractData<Crop>(response);
    });
  },

  deleteCrop: async (id: string): Promise<void> => {
    return safeFetch(`${API_PREFIX}/crops/${id}`, async () => {
      await api.delete(`${API_PREFIX}/crops/${encodeURIComponent(id)}`);
    });
  },

  getStats: async (): Promise<CropStats> => {
    return safeFetch(`${API_PREFIX}/crops/stats`, async () => {
      const response = await api.get(`${API_PREFIX}/crops/stats`);
      return extractData<CropStats>(response);
    });
  },
};
