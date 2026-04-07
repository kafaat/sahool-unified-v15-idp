/**
 * Diseases Feature - API Layer
 * طبقة API لميزة إدارة الأمراض
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { CROP_HEALTH_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';

const api = createApiClient();

export type DiseaseStatus = 'active' | 'treated' | 'resolved' | 'monitoring';
export type DiseaseSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface Disease {
  id: string;
  name: string;
  nameAr: string;
  cropType: string;
  cropTypeAr: string;
  fieldId: string;
  fieldName: string;
  severity: DiseaseSeverity;
  status: DiseaseStatus;
  affectedArea: number;
  detectedAt: string;
  treatment?: string;
  treatmentAr?: string;
}

export interface DiseaseStats {
  activeCount: number;
  treatedCount: number;
  monitoringCount: number;
  resolvedCount: number;
  criticalCount: number;
}

export const diseasesApi = {
  /**
   * Fetch all disease diagnoses
   * جلب جميع تشخيصات الأمراض
   */
  getDiseases: async (): Promise<Disease[]> => {
    return safeFetch(CROP_HEALTH_ENDPOINTS.DIAGNOSES_LIST, async () => {
      const response = await api.get(CROP_HEALTH_ENDPOINTS.DIAGNOSES_LIST);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Fetch disease stats summary
   * جلب إحصائيات الأمراض
   */
  getStats: async (): Promise<DiseaseStats> => {
    return safeFetch(CROP_HEALTH_ENDPOINTS.DIAGNOSES_STATS, async () => {
      const response = await api.get(CROP_HEALTH_ENDPOINTS.DIAGNOSES_STATS);
      const data = response.data.data || response.data;
      return {
        activeCount: data.activeCount ?? 0,
        treatedCount: data.treatedCount ?? 0,
        monitoringCount: data.monitoringCount ?? 0,
        resolvedCount: data.resolvedCount ?? 0,
        criticalCount: data.criticalCount ?? 0,
      };
    });
  },

  /**
   * Get treatment info for a disease
   * جلب معلومات العلاج لمرض
   */
  getTreatment: async (diseaseId: string): Promise<unknown> => {
    return safeFetch(CROP_HEALTH_ENDPOINTS.TREATMENT, async () => {
      const url = buildUrl(CROP_HEALTH_ENDPOINTS.TREATMENT, { diseaseId });
      const response = await api.get(url);
      return response.data.data || response.data;
    });
  },

  /**
   * Submit a new diagnosis request (image-based)
   * إرسال طلب تشخيص جديد
   */
  diagnose: async (formData: FormData): Promise<unknown> => {
    return safeFetch(CROP_HEALTH_ENDPOINTS.DIAGNOSE, async () => {
      const response = await api.post(CROP_HEALTH_ENDPOINTS.DIAGNOSE, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data || response.data;
    });
  },

  /**
   * Get list of known diseases
   * جلب قائمة الأمراض المعروفة
   */
  getDiseaseList: async (): Promise<unknown[]> => {
    return safeFetch(CROP_HEALTH_ENDPOINTS.DISEASES, async () => {
      const response = await api.get(CROP_HEALTH_ENDPOINTS.DISEASES);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },
};
