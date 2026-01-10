/**
 * Fields Feature - API Layer
 * طبقة API لميزة الحقول
 */

import axios, { type AxiosError } from 'axios';
import type { Field, FieldFormData, FieldFilters, GeoPolygon } from './types';
import { logger } from '@/lib/logger';

/**
 * API Field Response Type
 */
interface ApiFieldResponse {
  id: string;
  name?: string;
  nameAr?: string;
  areaHectares?: number;
  area?: number;
  cropType?: string;
  crop?: string;
  cropTypeAr?: string;
  cropAr?: string;
  tenantId?: string;
  farmId?: string;
  boundary?: GeoPolygon;
  polygon?: GeoPolygon;
  description?: string;
  descriptionAr?: string;
  metadata?: {
    description?: string;
    descriptionAr?: string;
    [key: string]: unknown;
  };
  createdAt?: string;
  updatedAt?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// Only warn during development, don't throw during build
if (!API_BASE_URL && typeof window !== 'undefined') {
  console.warn('NEXT_PUBLIC_API_URL environment variable is not set');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Add auth token interceptor
// SECURITY: Use js-cookie library for safe cookie parsing instead of manual parsing
import Cookies from 'js-cookie';

api.interceptors.request.use((config) => {
  // Get token from cookie using secure cookie parser
  if (typeof window !== 'undefined') {
    const token = Cookies.get('access_token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_FAILED: {
    en: 'Failed to fetch fields. Using cached data.',
    ar: 'فشل في جلب الحقول. استخدام البيانات المخزنة.',
  },
  CREATE_FAILED: {
    en: 'Failed to create field. Please try again.',
    ar: 'فشل في إنشاء الحقل. الرجاء المحاولة مرة أخرى.',
  },
  UPDATE_FAILED: {
    en: 'Failed to update field. Please try again.',
    ar: 'فشل في تحديث الحقل. الرجاء المحاولة مرة أخرى.',
  },
  DELETE_FAILED: {
    en: 'Failed to delete field. Please try again.',
    ar: 'فشل في حذف الحقل. الرجاء المحاولة مرة أخرى.',
  },
  NOT_FOUND: {
    en: 'Field not found.',
    ar: 'الحقل غير موجود.',
  },
};

// Mock data for fallback
const MOCK_FIELDS: Field[] = [
  {
    id: '1',
    name: 'North Field',
    nameAr: 'الحقل الشمالي',
    area: 5.5,
    crop: 'Wheat',
    cropAr: 'قمح',
    farmId: 'farm-1',
    polygon: {
      type: 'Polygon',
      coordinates: [[[44.2, 15.3], [44.21, 15.3], [44.21, 15.31], [44.2, 15.31], [44.2, 15.3]]],
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    name: 'South Field',
    nameAr: 'الحقل الجنوبي',
    area: 3.2,
    crop: 'Corn',
    cropAr: 'ذرة',
    farmId: 'farm-1',
    polygon: {
      type: 'Polygon',
      coordinates: [[[44.2, 15.29], [44.21, 15.29], [44.21, 15.3], [44.2, 15.3], [44.2, 15.29]]],
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '3',
    name: 'East Field',
    nameAr: 'الحقل الشرقي',
    area: 4.8,
    crop: 'Barley',
    cropAr: 'شعير',
    farmId: 'farm-1',
    polygon: {
      type: 'Polygon',
      coordinates: [[[44.22, 15.3], [44.23, 15.3], [44.23, 15.31], [44.22, 15.31], [44.22, 15.3]]],
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

/**
 * Map API field to feature field
 */
function mapApiFieldToField(apiField: ApiFieldResponse): Field {
  return {
    id: apiField.id,
    name: apiField.name || '',
    nameAr: apiField.nameAr || apiField.name || '',
    area: apiField.areaHectares || apiField.area || 0,
    crop: apiField.cropType || apiField.crop || '',
    cropAr: apiField.cropTypeAr || apiField.cropAr || apiField.cropType || apiField.crop || '',
    farmId: apiField.tenantId || apiField.farmId || '',
    polygon: apiField.boundary || apiField.polygon,
    description: apiField.metadata?.description || apiField.description,
    descriptionAr: apiField.metadata?.descriptionAr || apiField.descriptionAr,
    createdAt: apiField.createdAt || new Date().toISOString(),
    updatedAt: apiField.updatedAt || new Date().toISOString(),
  };
}

/**
 * API Field Request Type
 */
interface ApiFieldRequest {
  name: string;
  nameAr: string;
  tenantId: string;
  cropType: string;
  cropTypeAr?: string;
  coordinates?: number[][];
  boundary?: GeoPolygon;
  areaHectares: number;
  metadata: {
    description?: string;
    descriptionAr?: string;
  };
}

/**
 * Map feature field to API field
 */
function mapFieldToApiField(field: FieldFormData, tenantId?: string): ApiFieldRequest {
  return {
    name: field.name,
    nameAr: field.nameAr,
    tenantId: field.farmId || tenantId || 'default-tenant',
    cropType: field.crop || 'unknown',
    cropTypeAr: field.cropAr,
    coordinates: field.polygon?.coordinates?.[0],
    boundary: field.polygon,
    areaHectares: field.area,
    metadata: {
      description: field.description,
      descriptionAr: field.descriptionAr,
    },
  };
}

// API Functions
export const fieldsApi = {
  /**
   * Get all fields with filters
   */
  getFields: async (filters?: FieldFilters): Promise<Field[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.search) params.set('search', filters.search);
      if (filters?.farmId) params.set('tenantId', filters.farmId);
      if (filters?.crop) params.set('cropType', filters.crop);
      if (filters?.minArea) params.set('minArea', filters.minArea.toString());
      if (filters?.maxArea) params.set('maxArea', filters.maxArea.toString());
      if (filters?.status) params.set('status', filters.status);

      const response = await api.get(`/api/v1/fields?${params.toString()}`);

      // Handle different response formats
      const fields = response.data.data || response.data;

      if (Array.isArray(fields)) {
        return fields.map(mapApiFieldToField);
      }

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_FIELDS;
    } catch (error) {
      logger.warn('Failed to fetch fields from API, using mock data:', error);
      return MOCK_FIELDS;
    }
  },

  /**
   * Get field by ID
   */
  getFieldById: async (id: string): Promise<Field> => {
    try {
      const response = await api.get(`/api/v1/fields/${id}`);
      const field = response.data.data || response.data;
      return mapApiFieldToField(field);
    } catch (error) {
      logger.warn(`Failed to fetch field ${id} from API, using mock data:`, error);

      // Fallback to mock data
      const mockField = MOCK_FIELDS.find(f => f.id === id);
      if (mockField) {
        return mockField;
      }

      throw new Error(ERROR_MESSAGES.NOT_FOUND.en);
    }
  },

  /**
   * Create new field
   */
  createField: async (data: FieldFormData, tenantId?: string): Promise<Field> => {
    try {
      const apiData = mapFieldToApiField(data, tenantId);
      const response = await api.post('/api/v1/fields', apiData);
      const field = response.data.data || response.data;
      return mapApiFieldToField(field);
    } catch (error) {
      logger.error('Failed to create field:', error);

      // Return error with Arabic message
      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.CREATE_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.CREATE_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Update field
   */
  updateField: async (id: string, data: Partial<FieldFormData>, tenantId?: string): Promise<Field> => {
    try {
      const apiData = mapFieldToApiField(data as FieldFormData, tenantId);
      const response = await api.put(`/api/v1/fields/${id}`, apiData);
      const field = response.data.data || response.data;
      return mapApiFieldToField(field);
    } catch (error) {
      logger.error(`Failed to update field ${id}:`, error);

      // Return error with Arabic message
      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.UPDATE_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.UPDATE_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Delete field
   */
  deleteField: async (id: string): Promise<void> => {
    try {
      await api.delete(`/api/v1/fields/${id}`);
    } catch (error) {
      logger.error(`Failed to delete field ${id}:`, error);

      // Return error with Arabic message
      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.DELETE_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.DELETE_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Get field statistics
   */
  getStats: async (farmId?: string): Promise<{
    total: number;
    totalArea: number;
    byCrop: Record<string, number>;
  }> => {
    try {
      const params = new URLSearchParams();
      if (farmId) params.set('tenantId', farmId);

      const response = await api.get(`/api/v1/fields/stats?${params.toString()}`);
      return response.data.data || response.data;
    } catch {
      logger.warn('Failed to fetch field stats from API, calculating from mock data');

      // Calculate stats from mock data
      const total = MOCK_FIELDS.length;
      const totalArea = MOCK_FIELDS.reduce((sum, f) => sum + f.area, 0);
      const byCrop = MOCK_FIELDS.reduce((acc, f) => {
        const crop = f.crop || 'unknown';
        acc[crop] = (acc[crop] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      return { total, totalArea, byCrop };
    }
  },
};
