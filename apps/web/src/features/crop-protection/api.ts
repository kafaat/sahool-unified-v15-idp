/**
 * Crop Protection Feature - API Layer
 * طبقة API لميزة حماية المحاصيل
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';

// pest-detection-service:8125 + advisory-service:8093
const PEST_BASE = '/api/v1/pest-detection';
const ADVISORY_BASE = '/api/v1/advisory';

const api = createApiClient();

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface PestRecord {
  id: string;
  fieldId: string;
  pestType: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  detectedAt: string;
  status: 'active' | 'treated' | 'resolved';
  confidence: number;
  imageUrl?: string;
}

export interface PestIdentifyPayload {
  imageBase64: string;
  fieldId?: string;
  cropType?: string;
}

export interface PestIdentifyResult {
  pestType: string;
  confidence: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  recommendations: string[];
  recommendationsAr: string[];
}

export interface SprayWindow {
  id: string;
  fieldId: string;
  startTime: string;
  endTime: string;
  windSpeed: number;
  temperature: number;
  humidity: number;
  suitability: 'optimal' | 'acceptable' | 'poor';
}

// ═══════════════════════════════════════════════════════════════════════════
// API Functions
// ═══════════════════════════════════════════════════════════════════════════

export const cropProtectionApi = {
  /**
   * Get pest detection records
   * جلب سجلات اكتشاف الآفات
   */
  getPestRecords: async (fieldId?: string): Promise<PestRecord[]> => {
    const params = fieldId ? `?field_id=${encodeURIComponent(fieldId)}` : '';
    const endpoint = `${PEST_BASE}/list${params}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return response.data.data || response.data;
    });
  },

  /**
   * Identify pest from image
   * تحديد الآفة من الصورة
   */
  identifyPest: async (payload: PestIdentifyPayload): Promise<PestIdentifyResult> => {
    return safeFetch(`${PEST_BASE}/identify`, async () => {
      const response = await api.post(`${PEST_BASE}/identify`, payload);
      return response.data.data || response.data;
    });
  },

  /**
   * Get optimal spray windows
   * جلب نوافذ الرش المثلى
   */
  getSprayWindows: async (fieldId?: string): Promise<SprayWindow[]> => {
    return safeFetch(`${ADVISORY_BASE}/spray-windows`, async () => {
      const params = fieldId ? `?field_id=${fieldId}` : '';
      const response = await api.get(`${ADVISORY_BASE}/spray-windows${params}`);
      return response.data.data || response.data;
    });
  },
};
