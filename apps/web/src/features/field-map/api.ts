/**
 * Field Map Feature - API Layer
 * طبقة API لميزة خريطة الحقول
 */

import { FIELD_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import { createApiClient } from '@/lib/api/factory';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

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

    const response = await api.get(`${FIELD_ENDPOINTS.LIST}?${params.toString()}`);
    return response.data;
  },

  /**
   * Get field by ID
   */
  getFieldById: async (id: string): Promise<Field> => {
    const response = await api.get(buildUrl(FIELD_ENDPOINTS.GET, { fieldId: id }));
    return response.data;
  },

  /**
   * Create new field
   */
  createField: async (data: FieldCreate): Promise<Field> => {
    const response = await api.post(FIELD_ENDPOINTS.CREATE, data);
    return response.data;
  },

  /**
   * Update field.
   *
   * Backend route is `@Put(":id")` — not PATCH. Using PATCH here
   * produced a 404 from the NestJS router.
   * تم تصحيح أسلوب HTTP ليطابق مسار الخدمة الخلفية (PUT بدل PATCH)
   */
  updateField: async (id: string, data: FieldUpdate): Promise<Field> => {
    const response = await api.put(buildUrl(FIELD_ENDPOINTS.UPDATE, { fieldId: id }), data);
    return response.data;
  },

  /**
   * Delete field
   */
  deleteField: async (id: string): Promise<void> => {
    await api.delete(buildUrl(FIELD_ENDPOINTS.DELETE, { fieldId: id }));
  },

  /**
   * Get field GeoJSON for map display
   */
  getFieldsGeoJSON: async (filters?: FieldFilters): Promise<GeoJSONFeatureCollection<Field>> => {
    const params = new URLSearchParams();
    if (filters?.governorate) params.set('governorate', filters.governorate);
    if (filters?.status) params.set('status', filters.status);

    const response = await api.get(`${FIELD_ENDPOINTS.LIST}/geojson?${params.toString()}`);
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
    const response = await api.get(`${FIELD_ENDPOINTS.LIST}/stats`);
    return response.data;
  },
};
