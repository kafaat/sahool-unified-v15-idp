/**
 * Pivot Irrigation Feature - API Layer
 * طبقة API لميزة الري المحوري
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { IRRIGATION_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';

const api = createApiClient();

export interface Pivot {
  id: string;
  name: string;
  nameEn: string;
  fieldId: string;
  status: 'running' | 'stopped' | 'maintenance' | 'error';
  currentAngle: number;
  speed: number;
  direction: 'clockwise' | 'counterclockwise';
  areaHectares: number;
  sectorsCount: number;
  vriZonesCount: number;
  waterUsageM3: number;
  lastIrrigation: string;
}

export interface PivotStats {
  totalPivots: number;
  runningPivots: number;
  totalWaterUsageM3: number;
  totalVriZones: number;
}

/**
 * Pivot-specific endpoints under the irrigation-smart service (port 8094).
 * These are not in the shared contracts yet, so we define them locally.
 */
const PIVOT_ENDPOINTS = {
  LIST: `${IRRIGATION_ENDPOINTS.SCHEDULES_LIST}?type=pivot`,
  STATS: IRRIGATION_ENDPOINTS.EFFICIENCY,
  /** TODO: Pivot control endpoint does not exist yet in the backend. Pending implementation in irrigation-smart service. */
  CONTROL: '/api/v1/irrigation/pivot/control',
} as const;

export const pivotIrrigationApi = {
  /**
   * Fetch all pivots
   * جلب جميع المحاور
   */
  getPivots: async (): Promise<Pivot[]> => {
    return safeFetch(PIVOT_ENDPOINTS.LIST, async () => {
      const response = await api.get(PIVOT_ENDPOINTS.LIST);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Fetch pivot stats/summary
   * جلب إحصائيات المحاور
   */
  getStats: async (): Promise<PivotStats> => {
    return safeFetch(PIVOT_ENDPOINTS.STATS, async () => {
      const response = await api.get(PIVOT_ENDPOINTS.STATS);
      const data = response.data.data || response.data;
      return {
        totalPivots: data.totalPivots ?? 0,
        runningPivots: data.runningPivots ?? 0,
        totalWaterUsageM3: data.totalWaterUsageM3 ?? 0,
        totalVriZones: data.totalVriZones ?? 0,
      };
    });
  },

  /**
   * Start or stop a pivot
   * تشغيل أو إيقاف محوري
   */
  controlPivot: async (pivotId: string, action: 'start' | 'stop' | 'reverse'): Promise<Pivot> => {
    return safeFetch(PIVOT_ENDPOINTS.CONTROL, async () => {
      const response = await api.post(PIVOT_ENDPOINTS.CONTROL, { pivotId, action });
      return response.data.data || response.data;
    });
  },

  /**
   * Get irrigation history for a field (used for pivot activity)
   * جلب سجل الري لحقل
   */
  getHistory: async (fieldId: string): Promise<unknown[]> => {
    return safeFetch(IRRIGATION_ENDPOINTS.HISTORY, async () => {
      const url = buildUrl(IRRIGATION_ENDPOINTS.HISTORY, { fieldId });
      const response = await api.get(url);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },
};
