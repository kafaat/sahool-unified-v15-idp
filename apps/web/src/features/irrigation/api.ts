/**
 * Irrigation Feature - API Layer
 * طبقة API لميزة الري - Real API with mock fallback
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { IRRIGATION_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import type { IrrigationSchedule, IrrigationMethod, CreateScheduleRequest } from './types';

const api = createApiClient();

export const irrigationApi = {
  /**
   * Fetch irrigation schedules list
   * جلب قائمة جداول الري
   */
  getSchedules: async (): Promise<IrrigationSchedule[]> => {
    return safeFetch(IRRIGATION_ENDPOINTS.SCHEDULES_LIST, async () => {
      const response = await api.get(IRRIGATION_ENDPOINTS.SCHEDULES_LIST);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Create a new irrigation schedule
   * إنشاء جدول ري جديد
   */
  createSchedule: async (data: CreateScheduleRequest): Promise<IrrigationSchedule> => {
    return safeFetch(IRRIGATION_ENDPOINTS.SCHEDULES_CREATE, async () => {
      const response = await api.post(IRRIGATION_ENDPOINTS.SCHEDULES_CREATE, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Update an irrigation schedule
   * تحديث جدول ري
   */
  updateSchedule: async (
    scheduleId: string,
    data: Partial<CreateScheduleRequest>
  ): Promise<IrrigationSchedule> => {
    return safeFetch(IRRIGATION_ENDPOINTS.SCHEDULES_UPDATE, async () => {
      const url = buildUrl(IRRIGATION_ENDPOINTS.SCHEDULES_UPDATE, { scheduleId });
      const response = await api.patch(url, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Delete an irrigation schedule
   * حذف جدول ري
   */
  deleteSchedule: async (scheduleId: string): Promise<void> => {
    return safeFetch(IRRIGATION_ENDPOINTS.SCHEDULES_DELETE, async () => {
      const url = buildUrl(IRRIGATION_ENDPOINTS.SCHEDULES_DELETE, { scheduleId });
      await api.delete(url);
    });
  },

  /**
   * Fetch irrigation methods from backend
   * جلب طرق الري من الخدمة الخلفية
   */
  getMethods: async (): Promise<IrrigationMethod[]> => {
    return safeFetch(IRRIGATION_ENDPOINTS.METHODS, async () => {
      const response = await api.get(IRRIGATION_ENDPOINTS.METHODS);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      if (data?.methods && Array.isArray(data.methods)) {
        return data.methods.map((m: Record<string, unknown>) => ({
          id: m.id as string,
          name: m.name || (m.id as string),
          nameAr: (m.name_ar || m.nameAr || m.id) as string,
          efficiency: (m.efficiency_percent || m.efficiency || 0) as number,
        }));
      }
      return [];
    });
  },

  /**
   * Fetch irrigation stats/summary
   * جلب إحصائيات الري
   */
  getStats: async (): Promise<{
    totalWaterToday: number;
    inProgressCount: number;
    scheduledCount: number;
    overdueCount: number;
    efficiency: number;
  }> => {
    return safeFetch(IRRIGATION_ENDPOINTS.EFFICIENCY, async () => {
      const response = await api.get(IRRIGATION_ENDPOINTS.EFFICIENCY);
      const data = response.data.data || response.data;
      return {
        totalWaterToday: data.totalWaterToday ?? 0,
        inProgressCount: data.inProgressCount ?? 0,
        scheduledCount: data.scheduledCount ?? 0,
        overdueCount: data.overdueCount ?? 0,
        efficiency: data.efficiency ?? 87,
      };
    });
  },
};
