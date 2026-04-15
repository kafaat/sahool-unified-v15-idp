/**
 * Soil Analysis Feature - API Layer
 * طبقة API لميزة تحليل التربة
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
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

export const soilApi = {
  getTests: async (filters?: SoilFilters): Promise<SoilTest[]> => {
    return safeFetch(SOIL_ENDPOINTS.TESTS, async () => {
      const params = new URLSearchParams();
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.status) params.set('status', filters.status);
      const response = await api.get(`${SOIL_ENDPOINTS.TESTS}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getTestById: async (id: string): Promise<SoilTest> => {
    return safeFetch(SOIL_ENDPOINTS.TEST_GET, async () => {
      const url = buildUrl(SOIL_ENDPOINTS.TEST_GET, { testId: id });
      const response = await api.get(url);
      return response.data.data || response.data;
    });
  },

  createTest: async (data: Partial<SoilTest>): Promise<SoilTest> => {
    return safeFetch(SOIL_ENDPOINTS.TEST_CREATE, async () => {
      const response = await api.post(SOIL_ENDPOINTS.TEST_CREATE, data);
      return response.data.data || response.data;
    });
  },

  getRecommendations: async (fieldId?: string): Promise<SoilRecommendation[]> => {
    return safeFetch(SOIL_ENDPOINTS.RECOMMENDATIONS, async () => {
      const params = fieldId ? `?field_id=${fieldId}` : '';
      const response = await api.get(`${SOIL_ENDPOINTS.RECOMMENDATIONS}${params}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },
};
