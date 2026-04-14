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
 * All paths from the shared IRRIGATION_ENDPOINTS contract.
 */
const PIVOT_ENDPOINTS = {
  LIST: `${IRRIGATION_ENDPOINTS.SCHEDULES_LIST}?type=pivot`,
  STATS: IRRIGATION_ENDPOINTS.EFFICIENCY,
  CONTROL: IRRIGATION_ENDPOINTS.PIVOT_CONTROL,
  SPEED: IRRIGATION_ENDPOINTS.PIVOT_SPEED,
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
   * Update pivot rotation speed (PATCH)
   * تحديث سرعة دوران المحور
   */
  updateSpeed: async (pivotId: string, speed: number): Promise<void> => {
    await safeFetch(PIVOT_ENDPOINTS.SPEED, async () => {
      await api.patch(PIVOT_ENDPOINTS.SPEED, { pivotId, speed });
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
