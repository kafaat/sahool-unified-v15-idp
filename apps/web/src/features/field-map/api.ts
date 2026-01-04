/**
 * Field Map Feature - API Layer
 * طبقة API لميزة خريطة الحقول
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// Only warn during development, don't throw during build
if (!process.env.NEXT_PUBLIC_API_URL && typeof window !== 'undefined') {
  console.warn('NEXT_PUBLIC_API_URL environment variable is not set');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// GeoJSON Types (simplified for field boundaries)
export interface GeoJSONPolygon {
  type: 'Polygon';
  coordinates: number[][][];
}

export interface GeoJSONFeature<T = Record<string, unknown>> {
  type: 'Feature';
  geometry: GeoJSONPolygon;
  properties: T;
}

export interface GeoJSONFeatureCollection<T = Record<string, unknown>> {
  type: 'FeatureCollection';
  features: GeoJSONFeature<T>[];
}

// Types
export interface Field {
  id: string;
  name: string;
  nameAr: string;
  area: number;
  areaUnit: 'hectare' | 'dunum' | 'acre';
  geometry: GeoJSONPolygon;
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
  geometry: GeoJSONPolygon;
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

    const response = await api.get(`/api/v1/fields?${params.toString()}`);
    return response.data;
  },

  /**
   * Get field by ID
   */
  getFieldById: async (id: string): Promise<Field> => {
    const response = await api.get(`/api/v1/fields/${id}`);
    return response.data;
  },

  /**
   * Create new field
   */
  createField: async (data: FieldCreate): Promise<Field> => {
    const response = await api.post('/api/v1/fields', data);
    return response.data;
  },

  /**
   * Update field
   */
  updateField: async (id: string, data: FieldUpdate): Promise<Field> => {
    const response = await api.patch(`/api/v1/fields/${id}`, data);
    return response.data;
  },

  /**
   * Delete field
   */
  deleteField: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/fields/${id}`);
  },

  /**
   * Get field GeoJSON for map display
   */
  getFieldsGeoJSON: async (filters?: FieldFilters): Promise<GeoJSONFeatureCollection<Field>> => {
    const params = new URLSearchParams();
    if (filters?.governorate) params.set('governorate', filters.governorate);
    if (filters?.status) params.set('status', filters.status);

    const response = await api.get(`/api/v1/fields/geojson?${params.toString()}`);
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
    const response = await api.get('/api/v1/fields/stats');
    return response.data;
  },
};
