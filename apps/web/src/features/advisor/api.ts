/**
 * Advisor Feature - API Layer
 * طبقة API لميزة المستشار الزراعي
 */

import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
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

    const response = await api.get(`/v1/advisor/recommendations?${params.toString()}`);
    return response.data;
  },

  /**
   * Get a specific recommendation
   */
  getRecommendation: async (id: string): Promise<Recommendation> => {
    const response = await api.get(`/v1/advisor/recommendations/${id}`);
    return response.data;
  },

  /**
   * Ask the AI advisor a question
   */
  askAdvisor: async (query: AdvisorQuery): Promise<AdvisorResponse> => {
    const response = await api.post('/v1/advisor/ask', query);
    return response.data;
  },

  /**
   * Apply a recommendation (mark as applied)
   */
  applyRecommendation: async (id: string, notes?: string): Promise<Recommendation> => {
    const response = await api.post(`/v1/advisor/recommendations/${id}/apply`, { notes });
    return response.data;
  },

  /**
   * Dismiss a recommendation
   */
  dismissRecommendation: async (id: string, reason?: string): Promise<void> => {
    await api.post(`/v1/advisor/recommendations/${id}/dismiss`, { reason });
  },

  /**
   * Complete an action item
   */
  completeAction: async (recommendationId: string, actionId: string): Promise<Recommendation> => {
    const response = await api.post(
      `/v1/advisor/recommendations/${recommendationId}/actions/${actionId}/complete`
    );
    return response.data;
  },

  /**
   * Get advisor chat history
   */
  getChatHistory: async (limit?: number): Promise<AdvisorResponse[]> => {
    const params = limit ? `?limit=${limit}` : '';
    const response = await api.get(`/v1/advisor/history${params}`);
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
    const response = await api.get('/v1/advisor/stats');
    return response.data;
  },
};
