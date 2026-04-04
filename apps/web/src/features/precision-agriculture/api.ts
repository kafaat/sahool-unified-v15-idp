/**
 * Precision Agriculture Feature - API Layer
 * طبقة API لميزة الزراعة الدقيقة
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';

// indicators-service:8091
const BASE = '/api/v1/precision-agriculture';

const api = createApiClient();

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface VraMap {
  fieldId: string;
  zones: VraZone[];
  generatedAt: string;
  totalArea: number;
  unit: string;
}

export interface VraZone {
  zoneId: string;
  polygon: [number, number][];
  applicationRate: number;
  ndviMean: number;
  classification: 'low' | 'medium' | 'high';
}

export interface GddData {
  fieldId: string;
  cumulativeGdd: number;
  dailyGdd: number[];
  baseTemperature: number;
  cropStage: string;
  cropStageAr: string;
  startDate: string;
  endDate: string;
}

export interface FertilizerCalculation {
  fieldId: string;
  cropType: string;
  targetYield: number;
  soilTestResults?: Record<string, number>;
}

export interface FertilizerResult {
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  recommendations: string[];
  recommendationsAr: string[];
  totalCost: number;
  currency: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// API Functions
// ═══════════════════════════════════════════════════════════════════════════

export const precisionAgricultureApi = {
  /**
   * Get Variable Rate Application map for a field
   * جلب خريطة التطبيق متغير المعدل لحقل معين
   */
  getVraMap: async (fieldId: string): Promise<VraMap> => {
    return safeFetch(`${BASE}/vra/${fieldId}`, async () => {
      const response = await api.get(`${BASE}/vra/${fieldId}`);
      return response.data.data || response.data;
    });
  },

  /**
   * Get Growing Degree Days for a field
   * جلب أيام درجات النمو لحقل معين
   */
  getGdd: async (fieldId: string, startDate?: string): Promise<GddData> => {
    return safeFetch(`${BASE}/gdd/${fieldId}`, async () => {
      const params = startDate ? `?start_date=${startDate}` : '';
      const response = await api.get(`${BASE}/gdd/${fieldId}${params}`);
      return response.data.data || response.data;
    });
  },

  /**
   * Calculate fertilizer requirements
   * حساب متطلبات الأسمدة
   */
  calculateFertilizer: async (payload: FertilizerCalculation): Promise<FertilizerResult> => {
    return safeFetch(`${BASE}/fertilizer/calculate`, async () => {
      const response = await api.post(`${BASE}/fertilizer/calculate`, payload);
      return response.data.data || response.data;
    });
  },
};
