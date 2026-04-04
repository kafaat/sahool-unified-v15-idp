/**
 * Crop Planning Feature - API Layer
 * طبقة API لميزة تخطيط المحاصيل
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';

// advisory-service:8093
const BASE = '/api/v1/crop-planning';

const api = createApiClient();

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface CropPlan {
  id: string;
  fieldId: string;
  cropType: string;
  season: string;
  plantingDate: string;
  harvestDate: string;
  status: 'draft' | 'active' | 'completed';
  createdAt: string;
  updatedAt: string;
}

export interface CreateCropPlanPayload {
  fieldId: string;
  cropType: string;
  season: string;
  plantingDate: string;
  harvestDate?: string;
}

export interface CropRecommendation {
  cropType: string;
  suitabilityScore: number;
  reasoning: string;
  reasoningAr: string;
  expectedYield: number;
  waterRequirement: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// API Functions
// ═══════════════════════════════════════════════════════════════════════════

export const cropPlanningApi = {
  /**
   * Get all crop plans
   * جلب جميع خطط المحاصيل
   */
  getPlans: async (fieldId?: string): Promise<CropPlan[]> => {
    const params = fieldId ? `?field_id=${encodeURIComponent(fieldId)}` : '';
    const endpoint = `${BASE}/plans${params}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return response.data.data || response.data;
    });
  },

  /**
   * Create a new crop plan
   * إنشاء خطة محصول جديدة
   */
  createPlan: async (payload: CreateCropPlanPayload): Promise<CropPlan> => {
    return safeFetch(`${BASE}/plans`, async () => {
      const response = await api.post(`${BASE}/plans`, payload);
      return response.data.data || response.data;
    });
  },

  /**
   * Get crop recommendations for a field
   * جلب توصيات المحاصيل لحقل معين
   */
  getRecommendations: async (fieldId?: string): Promise<CropRecommendation[]> => {
    const params = fieldId ? `?field_id=${encodeURIComponent(fieldId)}` : '';
    const endpoint = `${BASE}/recommendations${params}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return response.data.data || response.data;
    });
  },
};
