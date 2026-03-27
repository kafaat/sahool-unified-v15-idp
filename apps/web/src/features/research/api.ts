/**
 * Research Feature - API Layer
 * طبقة API لميزة الأبحاث والتجارب
 */

import { RESEARCH_ENDPOINTS, buildUrl, API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient, logger } from '@/lib/api/factory';
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

const MOCK_TRIALS: ResearchTrial[] = [
  {
    id: '1',
    name: 'Wheat Variety Comparison Trial',
    nameAr: 'تجربة مقارنة أصناف القمح',
    description: 'Comparing yield performance of 5 wheat varieties under local conditions',
    descriptionAr: 'مقارنة أداء المحصول لـ 5 أصناف قمح تحت الظروف المحلية',
    crop: 'Wheat',
    cropAr: 'القمح',
    type: 'trial',
    status: 'active',
    startDate: '2025-11-01',
    endDate: '2026-04-30',
    fieldId: 'field-1',
    fieldName: 'حقل البحث الشمالي',
    objectives: ['Compare yield', 'Assess disease resistance', 'Evaluate water efficiency'],
    objectivesAr: ['مقارنة المحصول', 'تقييم مقاومة الأمراض', 'تقييم كفاءة المياه'],
    progress: 65,
    researchers: 3,
    leadResearcher: 'Dr. Ahmad Hassan',
    team: ['Dr. Fatima Ali', 'Eng. Mohammed Saleh'],
    budget: 50000,
    actualCost: 32500,
    metadata: {},
    createdAt: '2025-10-15T10:00:00Z',
    updatedAt: '2026-01-20T14:30:00Z',
  },
  {
    id: '2',
    name: 'Smart Irrigation Efficiency Study',
    nameAr: 'دراسة كفاءة الري الذكي',
    description: 'Evaluating water savings with smart irrigation sensors',
    descriptionAr: 'تقييم توفير المياه باستخدام أجهزة استشعار الري الذكي',
    crop: 'Vegetables',
    cropAr: 'الخضروات',
    type: 'study',
    status: 'active',
    startDate: '2025-12-01',
    endDate: '2026-06-30',
    fieldId: 'field-2',
    fieldName: 'حقل الخضروات',
    objectives: ['Measure water savings', 'Compare crop yield', 'Analyze cost-benefit'],
    objectivesAr: ['قياس توفير المياه', 'مقارنة محصول المحاصيل', 'تحليل التكلفة والفائدة'],
    progress: 40,
    researchers: 2,
    leadResearcher: 'Eng. Khalid Omar',
    team: ['Dr. Sara Ahmed'],
    budget: 35000,
    actualCost: 14000,
    metadata: {},
    createdAt: '2025-11-20T09:00:00Z',
    updatedAt: '2026-01-18T11:00:00Z',
  },
  {
    id: '3',
    name: 'Organic Fertilizer Impact Assessment',
    nameAr: 'تقييم تأثير الأسمدة العضوية',
    description: 'Assessing soil health improvements with organic fertilizers',
    descriptionAr: 'تقييم تحسينات صحة التربة باستخدام الأسمدة العضوية',
    crop: 'Barley',
    cropAr: 'الشعير',
    type: 'experiment',
    status: 'completed',
    startDate: '2025-06-01',
    endDate: '2025-12-15',
    fieldId: 'field-3',
    fieldName: 'حقل التجارب',
    objectives: ['Measure soil organic matter', 'Assess microbial activity'],
    objectivesAr: ['قياس المادة العضوية في التربة', 'تقييم النشاط الميكروبي'],
    progress: 100,
    researchers: 2,
    results: '30% increase in soil organic matter, 25% improvement in water retention',
    resultsAr: 'زيادة 30% في المادة العضوية للتربة، تحسن 25% في احتباس الماء',
    leadResearcher: 'Dr. Nadia Mahmoud',
    team: ['Eng. Ali Hassan'],
    budget: 25000,
    actualCost: 23500,
    metadata: {},
    createdAt: '2025-05-15T08:00:00Z',
    updatedAt: '2025-12-20T16:00:00Z',
  },
];

const MOCK_STATS: ResearchStats = {
  totalTrials: 3,
  activeTrials: 2,
  completedTrials: 1,
  planningTrials: 0,
  totalResearchers: 7,
  totalBudget: 110000,
  byType: { trial: 1, study: 1, experiment: 1 },
  byStatus: { active: 2, completed: 1 },
};

export const researchApi = {
  getTrials: async (filters?: ResearchFilters): Promise<ResearchTrial[]> => {
    try {
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

      logger.warn('API returned unexpected format, using mock data');
      return MOCK_TRIALS;
    } catch (error) {
      logger.warn('Failed to fetch trials from API, using mock data:', error);
      return MOCK_TRIALS;
    }
  },

  getTrialById: async (id: string): Promise<ResearchTrial> => {
    try {
      const response = await api.get(buildUrl(RESEARCH_ENDPOINTS.TRIAL_GET, { trialId: id }));
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch trial ${id}, using mock data:`, error);
      const mockTrial = MOCK_TRIALS.find((t) => t.id === id);
      if (mockTrial) return mockTrial;
      throw new Error(`Trial with ID ${id} not found`);
    }
  },

  createTrial: async (data: ResearchFormData): Promise<ResearchTrial> => {
    try {
      const response = await api.post(RESEARCH_ENDPOINTS.TRIAL_CREATE, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to create trial:', error);
      throw error;
    }
  },

  updateTrial: async (id: string, data: Partial<ResearchFormData>): Promise<ResearchTrial> => {
    try {
      const response = await api.put(
        buildUrl(RESEARCH_ENDPOINTS.TRIAL_UPDATE, { trialId: id }),
        data
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update trial ${id}:`, error);
      throw error;
    }
  },

  deleteTrial: async (id: string): Promise<void> => {
    try {
      await api.delete(buildUrl(RESEARCH_ENDPOINTS.TRIAL_GET, { trialId: id }));
    } catch (error) {
      logger.error(`Failed to delete trial ${id}:`, error);
      throw error;
    }
  },

  updateProgress: async (id: string, progress: number): Promise<ResearchTrial> => {
    try {
      const response = await api.patch(
        `${buildUrl(RESEARCH_ENDPOINTS.TRIAL_GET, { trialId: id })}/progress`,
        { progress }
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update progress for trial ${id}:`, error);
      throw error;
    }
  },

  getMilestones: async (trialId: string): Promise<ResearchMilestone[]> => {
    try {
      const response = await api.get(
        `${buildUrl(RESEARCH_ENDPOINTS.TRIAL_GET, { trialId })}/milestones`
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch milestones for trial ${trialId}:`, error);
      return [];
    }
  },

  getStats: async (): Promise<ResearchStats> => {
    try {
      const response = await api.get(`${API_PREFIX}/research/stats`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch research stats, using mock data:', error);
      return MOCK_STATS;
    }
  },
};
