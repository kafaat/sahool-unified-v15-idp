/**
 * Advisor Feature - API Layer
 * طبقة API لميزة المستشار الزراعي
 */

import axios from 'axios';

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

// Types
export type RecommendationType = 'irrigation' | 'fertilizer' | 'pest_control' | 'harvest' | 'planting' | 'general';
export type RecommendationPriority = 'low' | 'medium' | 'high' | 'urgent';
export type RecommendationStatus = 'pending' | 'applied' | 'dismissed' | 'expired';

export interface Recommendation {
  id: string;
  type: RecommendationType;
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  priority: RecommendationPriority;
  status: RecommendationStatus;
  fieldId?: string;
  fieldName?: string;
  cropType?: string;
  actionItems: ActionItem[];
  expectedBenefit?: string;
  expectedBenefitAr?: string;
  validUntil?: string;
  createdAt: string;
  appliedAt?: string;
  source: 'ai' | 'expert' | 'system';
  confidence?: number;
}

export interface ActionItem {
  id: string;
  action: string;
  actionAr: string;
  completed: boolean;
  dueDate?: string;
}

export interface AdvisorQuery {
  question: string;
  fieldId?: string;
  cropType?: string;
  context?: Record<string, unknown>;
}

export interface AdvisorResponse {
  id: string;
  question: string;
  answer: string;
  answerAr: string;
  recommendations: Recommendation[];
  sources?: string[];
  confidence: number;
  createdAt: string;
}

export interface AdvisorFilters {
  type?: RecommendationType;
  priority?: RecommendationPriority;
  status?: RecommendationStatus;
  fieldId?: string;
  cropType?: string;
}

// API Functions
export const advisorApi = {
  /**
   * Get recommendations for a field or all fields
   */
  getRecommendations: async (filters?: AdvisorFilters): Promise<Recommendation[]> => {
    const params = new URLSearchParams();
    if (filters?.type) params.set('type', filters.type);
    if (filters?.priority) params.set('priority', filters.priority);
    if (filters?.status) params.set('status', filters.status);
    if (filters?.fieldId) params.set('field_id', filters.fieldId);
    if (filters?.cropType) params.set('crop_type', filters.cropType);

    const response = await api.get(`/api/v1/advice/recommendations?${params.toString()}`);
    return response.data;
  },

  /**
   * Get a specific recommendation
   */
  getRecommendation: async (id: string): Promise<Recommendation> => {
    const response = await api.get(`/api/v1/advice/recommendations/${id}`);
    return response.data;
  },

  /**
   * Ask the AI advisor a question
   */
  askAdvisor: async (query: AdvisorQuery): Promise<AdvisorResponse> => {
    const response = await api.post('/api/v1/advice/ask', query);
    return response.data;
  },

  /**
   * Apply a recommendation (mark as applied)
   */
  applyRecommendation: async (id: string, notes?: string): Promise<Recommendation> => {
    const response = await api.post(`/api/v1/advice/recommendations/${id}/apply`, { notes });
    return response.data;
  },

  /**
   * Dismiss a recommendation
   */
  dismissRecommendation: async (id: string, reason?: string): Promise<void> => {
    await api.post(`/api/v1/advice/recommendations/${id}/dismiss`, { reason });
  },

  /**
   * Complete an action item
   */
  completeAction: async (recommendationId: string, actionId: string): Promise<Recommendation> => {
    const response = await api.post(
      `/api/v1/advice/recommendations/${recommendationId}/actions/${actionId}/complete`
    );
    return response.data;
  },

  /**
   * Get advisor chat history
   */
  getChatHistory: async (limit?: number): Promise<AdvisorResponse[]> => {
    const params = limit ? `?limit=${limit}` : '';
    const response = await api.get(`/api/v1/advice/history${params}`);
    return response.data;
  },

  /**
   * Get recommendation statistics
   */
  getStats: async (): Promise<{
    total: number;
    pending: number;
    applied: number;
    byType: Record<RecommendationType, number>;
    byPriority: Record<RecommendationPriority, number>;
  }> => {
    const response = await api.get('/api/v1/advice/stats');
    return response.data;
  },
};
