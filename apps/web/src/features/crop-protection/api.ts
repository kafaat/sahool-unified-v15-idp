/**
 * Crop Protection Feature - API Layer
 * طبقة API لميزة حماية المحاصيل
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';

// Canonical backend paths (pest-detection-service exposes /api/v1/pests/*,
// advisory-service exposes /api/v1/advisory/*).
// Historical paths like /api/v1/pest-detection/* do NOT exist on any backend
// and were a contract-mismatch bug.
const PEST_BASE = '/api/v1/pests';
const ADVISORY_BASE = '/api/v1/advisory';
// Next.js same-origin proxy that enforces auth, SSRF guards, and size limits
// for the AI pest-identification flow.
const PEST_IDENTIFY_PROXY = '/api/pest-detection';

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
   *
   * Backend: GET /api/v1/pests (pest-detection-service).
   * Accepts no field_id filter — client-side filtering is applied instead.
   */
  getPestRecords: async (fieldId?: string): Promise<PestRecord[]> => {
    const endpoint = PEST_BASE;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      const data = response.data?.data ?? response.data;
      if (!Array.isArray(data)) return [];
      if (!fieldId) return data as PestRecord[];
      // The upstream endpoint doesn't filter by field; filter client-side.
      return (data as PestRecord[]).filter((r) => r.fieldId === fieldId);
    });
  },

  /**
   * Identify pest from image
   * تحديد الآفة من الصورة
   *
   * Routes through the Next.js /api/pest-detection proxy which enforces
   * auth, SSRF protection for image_url, and payload-size limits before
   * forwarding to pest-detection-service.
   */
  identifyPest: async (payload: PestIdentifyPayload): Promise<PestIdentifyResult> => {
    return safeFetch(PEST_IDENTIFY_PROXY, async () => {
      const response = await api.post(PEST_IDENTIFY_PROXY, {
        action: 'identify',
        image: payload.imageBase64,
        ...(payload.fieldId && { fieldId: payload.fieldId }),
        ...(payload.cropType && { crop_type: payload.cropType }),
      });
      return response.data?.data ?? response.data;
    });
  },

  /**
   * Get optimal spray windows
   * جلب نوافذ الرش المثلى
   */
  getSprayWindows: async (fieldId?: string): Promise<SprayWindow[]> => {
    const params = fieldId ? `?field_id=${encodeURIComponent(fieldId)}` : '';
    const endpoint = `${ADVISORY_BASE}/spray-windows${params}`;
    return safeFetch(endpoint, async () => {
      const response = await api.get(endpoint);
      return response.data.data ?? response.data;
    });
  },
};
