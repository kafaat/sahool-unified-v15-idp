/**
 * Seeds Feature - API Layer
 * طبقة API لميزة البذور
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';

// field-management-service:3000
const BASE = '/api/v1/seeds';

const api = createApiClient();

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface Seed {
  id: string;
  name: string;
  nameAr: string;
  cropType: string;
  variety: string;
  origin: string;
  germinationRate: number;
  maturityDays: number;
  droughtTolerance: 'low' | 'medium' | 'high';
  diseaseResistance: string[];
  recommendedRegions: string[];
  pricePerKg: number;
  available: boolean;
}

export interface SeedRecommendation {
  seedId: string;
  seedName: string;
  seedNameAr: string;
  suitabilityScore: number;
  reasoning: string;
  reasoningAr: string;
  expectedYield: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// API Functions
// ═══════════════════════════════════════════════════════════════════════════

export const seedsApi = {
  /**
   * Get all seeds catalog
   * جلب كتالوج البذور
   */
  getSeeds: async (cropType?: string): Promise<Seed[]> => {
    const params = cropType ? `?crop_type=${encodeURIComponent(cropType)}` : '';
    const endpoint = `${BASE}${params}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return response.data.data || response.data;
    });
  },

  /**
   * Get seed by ID
   * جلب بذرة بواسطة المعرف
   */
  getSeedById: async (id: string): Promise<Seed> => {
    const endpoint = `${BASE}/${encodeURIComponent(id)}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return response.data.data || response.data;
    });
  },

  /**
   * Get seed recommendations for a field
   * جلب توصيات البذور لحقل معين
   */
  getRecommendations: async (fieldId?: string, season?: string): Promise<SeedRecommendation[]> => {
    const params = new URLSearchParams();
    if (fieldId) params.set('field_id', fieldId);
    if (season) params.set('season', season);
    const endpoint = `${BASE}/recommendations${params.toString() ? `?${params.toString()}` : ''}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return response.data.data || response.data;
    });
  },
};
