/**
 * Field Map Feature - API Layer
 * طبقة API لميزة خريطة الحقول
 */

import { api } from '@sahool/api-client';

// Types
export interface Field {
  id: string;
  name: string;
  nameAr: string;
  area: number;
  areaUnit: 'hectare' | 'dunum' | 'acre';
  geometry: GeoJSON.Polygon;
  cropType?: string;
  status: 'active' | 'fallow' | 'harvested';
  governorate: string;
  district: string;
  createdAt: string;
  updatedAt: string;
}

export interface FieldCreate {
  name: string;
  nameAr: string;
  geometry: GeoJSON.Polygon;
  cropType?: string;
}

export interface FieldUpdate {
  name?: string;
  nameAr?: string;
  cropType?: string;
  status?: Field['status'];
}

export interface FieldFilters {
  governorate?: string;
  district?: string;
  cropType?: string;
  status?: Field['status'];
  search?: string;
}

// API Functions
export const fieldMapApi = {
  /**
   * Get all fields with optional filters
   */
  getFields: async (filters?: FieldFilters): Promise<Field[]> => {
    const params = new URLSearchParams();
    if (filters?.governorate) params.set('governorate', filters.governorate);
    if (filters?.district) params.set('district', filters.district);
    if (filters?.cropType) params.set('crop_type', filters.cropType);
    if (filters?.status) params.set('status', filters.status);
    if (filters?.search) params.set('search', filters.search);

    const response = await api.get(`/v1/fields?${params.toString()}`);
    return response.data;
  },

  /**
   * Get field by ID
   */
  getFieldById: async (id: string): Promise<Field> => {
    const response = await api.get(`/v1/fields/${id}`);
    return response.data;
  },

  /**
   * Create new field
   */
  createField: async (data: FieldCreate): Promise<Field> => {
    const response = await api.post('/v1/fields', data);
    return response.data;
  },

  /**
   * Update field
   */
  updateField: async (id: string, data: FieldUpdate): Promise<Field> => {
    const response = await api.patch(`/v1/fields/${id}`, data);
    return response.data;
  },

  /**
   * Delete field
   */
  deleteField: async (id: string): Promise<void> => {
    await api.delete(`/v1/fields/${id}`);
  },

  /**
   * Get field GeoJSON for map display
   */
  getFieldsGeoJSON: async (filters?: FieldFilters): Promise<GeoJSON.FeatureCollection> => {
    const params = new URLSearchParams();
    if (filters?.governorate) params.set('governorate', filters.governorate);
    if (filters?.status) params.set('status', filters.status);

    const response = await api.get(`/v1/fields/geojson?${params.toString()}`);
    return response.data;
  },

  /**
   * Get field statistics
   */
  getFieldStats: async (): Promise<{
    totalFields: number;
    totalArea: number;
    byCrop: Record<string, number>;
    byGovernorate: Record<string, number>;
  }> => {
    const response = await api.get('/v1/fields/stats');
    return response.data;
  },
};
