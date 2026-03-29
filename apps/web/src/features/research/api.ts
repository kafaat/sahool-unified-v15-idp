/**
 * Research Feature - API Layer
 * طبقة API لميزة الأبحاث والتجارب
 */

import { RESEARCH_ENDPOINTS, buildUrl, API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type {
  ResearchTrial,
  ResearchFilters,
  ResearchFormData,
  ResearchMilestone,
  ResearchStats,
} from './types';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_FAILED: {
    en: 'Failed to fetch research data.',
    ar: 'فشل في جلب بيانات الأبحاث.',
  },
  CREATE_FAILED: {
    en: 'Failed to create research trial.',
    ar: 'فشل في إنشاء التجربة البحثية.',
  },
};

export const researchApi = {
  getTrials: async (filters?: ResearchFilters): Promise<ResearchTrial[]> => {
    return safeFetch(RESEARCH_ENDPOINTS.TRIALS, async () => {
      const params = new URLSearchParams();
      if (filters?.type) params.set('type', filters.type);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.cropType) params.set('crop_type', filters.cropType);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`${RESEARCH_ENDPOINTS.TRIALS}?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      return [];
    });
  },

  getTrialById: async (id: string): Promise<ResearchTrial> => {
    return safeFetch(RESEARCH_ENDPOINTS.TRIAL_GET, async () => {
      const response = await api.get(buildUrl(RESEARCH_ENDPOINTS.TRIAL_GET, { trialId: id }));
      return response.data.data || response.data;
    });
  },

  createTrial: async (data: ResearchFormData): Promise<ResearchTrial> => {
    return safeFetch(RESEARCH_ENDPOINTS.TRIAL_CREATE, async () => {
      const response = await api.post(RESEARCH_ENDPOINTS.TRIAL_CREATE, data);
      return response.data.data || response.data;
    });
  },

  updateTrial: async (id: string, data: Partial<ResearchFormData>): Promise<ResearchTrial> => {
    return safeFetch(RESEARCH_ENDPOINTS.TRIAL_UPDATE, async () => {
      const response = await api.put(
        buildUrl(RESEARCH_ENDPOINTS.TRIAL_UPDATE, { trialId: id }),
        data
      );
      return response.data.data || response.data;
    });
  },

  deleteTrial: async (id: string): Promise<void> => {
    return safeFetch(RESEARCH_ENDPOINTS.TRIAL_GET, async () => {
      await api.delete(buildUrl(RESEARCH_ENDPOINTS.TRIAL_GET, { trialId: id }));
    });
  },

  updateProgress: async (id: string, progress: number): Promise<ResearchTrial> => {
    return safeFetch(RESEARCH_ENDPOINTS.TRIAL_GET, async () => {
      const response = await api.patch(
        `${buildUrl(RESEARCH_ENDPOINTS.TRIAL_GET, { trialId: id })}/progress`,
        { progress }
      );
      return response.data.data || response.data;
    });
  },

  getMilestones: async (trialId: string): Promise<ResearchMilestone[]> => {
    return safeFetch(RESEARCH_ENDPOINTS.TRIAL_GET, async () => {
      const response = await api.get(
        `${buildUrl(RESEARCH_ENDPOINTS.TRIAL_GET, { trialId })}/milestones`
      );
      return response.data.data || response.data;
    });
  },

  getStats: async (): Promise<ResearchStats> => {
    return safeFetch(`${API_PREFIX}/research/stats`, async () => {
      const response = await api.get(`${API_PREFIX}/research/stats`);
      return response.data.data || response.data;
    });
  },
};
