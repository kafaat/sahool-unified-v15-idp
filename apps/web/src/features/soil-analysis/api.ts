/**
 * Soil Analysis Feature - API Layer
 * طبقة API لميزة تحليل التربة
 */

import { createApiClient, logger } from '@/lib/api/factory';
import { SOIL_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import type { SoilTest, SoilRecommendation, SoilFilters } from './types';

const api = createApiClient();

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_TESTS_FAILED: { en: 'Failed to fetch soil tests.', ar: 'فشل في جلب تحاليل التربة.' },
  CREATE_TEST_FAILED: { en: 'Failed to create soil test.', ar: 'فشل في إنشاء تحليل التربة.' },
  FETCH_RECOMMENDATIONS_FAILED: {
    en: 'Failed to fetch soil recommendations.',
    ar: 'فشل في جلب توصيات التربة.',
  },
};

const MOCK_TESTS: SoilTest[] = [
  {
    id: 'test-1',
    fieldId: 'field-1',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    sampleDate: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7).toISOString(),
    pH: 7.2,
    nitrogen: 18,
    phosphorus: 25,
    potassium: 150,
    organicMatter: 2.1,
    electricalConductivity: 1.5,
    texture: 'loam',
    textureAr: 'طمي',
    status: 'completed',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7).toISOString(),
  },
];

export const soilApi = {
  getTests: async (filters?: SoilFilters): Promise<SoilTest[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.status) params.set('status', filters.status);
      const response = await api.get(`${SOIL_ENDPOINTS.TESTS}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return MOCK_TESTS;
    } catch (error) {
      logger.warn('Failed to fetch soil tests, using mock data:', error);
      return MOCK_TESTS;
    }
  },

  getTestById: async (id: string): Promise<SoilTest> => {
    try {
      const url = buildUrl(SOIL_ENDPOINTS.TEST_GET, { testId: id });
      const response = await api.get(url);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch soil test ${id}:`, error);
      const mock = MOCK_TESTS.find((t) => t.id === id);
      if (mock) return mock;
      throw new Error(ERROR_MESSAGES.FETCH_TESTS_FAILED.en);
    }
  },

  createTest: async (data: Partial<SoilTest>): Promise<SoilTest> => {
    try {
      const response = await api.post(SOIL_ENDPOINTS.TEST_CREATE, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to create soil test:', error);
      throw new Error(ERROR_MESSAGES.CREATE_TEST_FAILED.en);
    }
  },

  getRecommendations: async (fieldId?: string): Promise<SoilRecommendation[]> => {
    try {
      const params = fieldId ? `?field_id=${fieldId}` : '';
      const response = await api.get(`${SOIL_ENDPOINTS.RECOMMENDATIONS}${params}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    } catch (error) {
      logger.warn('Failed to fetch soil recommendations:', error);
      return [];
    }
  },
};
