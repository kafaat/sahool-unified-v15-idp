/**
 * Irrigation Feature - API Layer
 * طبقة API لميزة الري - Real API with mock fallback
 */

import { createApiClient, logger } from "@/lib/api/factory";
import { IRRIGATION_ENDPOINTS, buildUrl } from "@sahool/shared-types/contracts";
import type { IrrigationSchedule, IrrigationMethod, CreateScheduleRequest } from "./types";
import { MOCK_IRRIGATION_SCHEDULES, MOCK_IRRIGATION_METHODS } from "./api.mock";

const api = createApiClient();

export const irrigationApi = {
  /**
   * Fetch irrigation schedules list
   * جلب قائمة جداول الري
   */
  getSchedules: async (): Promise<IrrigationSchedule[]> => {
    try {
      const response = await api.get(IRRIGATION_ENDPOINTS.SCHEDULES_LIST);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      logger.warn("API returned unexpected format for schedules, using mock data");
      return MOCK_IRRIGATION_SCHEDULES;
    } catch (error) {
      logger.warn("Failed to fetch irrigation schedules from API, using mock data:", error);
      return MOCK_IRRIGATION_SCHEDULES;
    }
  },

  /**
   * Create a new irrigation schedule
   * إنشاء جدول ري جديد
   */
  createSchedule: async (data: CreateScheduleRequest): Promise<IrrigationSchedule> => {
    try {
      const response = await api.post(IRRIGATION_ENDPOINTS.SCHEDULES_CREATE, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Failed to create schedule via API, creating locally:", error);
      // Return a locally-constructed schedule as fallback
      return {
        id: crypto.randomUUID(),
        fieldId: `field-${Date.now()}`,
        fieldName: data.fieldName,
        type: data.type,
        status: "scheduled",
        scheduledAt: data.scheduledAt || new Date().toISOString(),
        duration: data.duration,
        waterAmount: data.waterAmount,
      };
    }
  },

  /**
   * Update an irrigation schedule
   * تحديث جدول ري
   */
  updateSchedule: async (scheduleId: string, data: Partial<CreateScheduleRequest>): Promise<IrrigationSchedule> => {
    try {
      const url = buildUrl(IRRIGATION_ENDPOINTS.SCHEDULES_UPDATE, { scheduleId });
      const response = await api.patch(url, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Failed to update schedule via API:", error);
      throw error;
    }
  },

  /**
   * Delete an irrigation schedule
   * حذف جدول ري
   */
  deleteSchedule: async (scheduleId: string): Promise<void> => {
    try {
      const url = buildUrl(IRRIGATION_ENDPOINTS.SCHEDULES_DELETE, { scheduleId });
      await api.delete(url);
    } catch (error) {
      logger.warn("Failed to delete schedule via API:", error);
      // Silently succeed - local state will handle deletion
    }
  },

  /**
   * Fetch irrigation methods from backend
   * جلب طرق الري من الخدمة الخلفية
   */
  getMethods: async (): Promise<IrrigationMethod[]> => {
    try {
      const response = await api.get(IRRIGATION_ENDPOINTS.METHODS);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      // Try the methods array inside the response
      if (data?.methods && Array.isArray(data.methods)) {
        return data.methods.map((m: Record<string, unknown>) => ({
          id: m.id as string,
          name: m.name || (m.id as string),
          nameAr: (m.name_ar || m.nameAr || m.id) as string,
          efficiency: (m.efficiency_percent || m.efficiency || 0) as number,
        }));
      }
      logger.warn("API returned unexpected format for methods, using mock data");
      return MOCK_IRRIGATION_METHODS;
    } catch (error) {
      logger.warn("Failed to fetch irrigation methods from API, using mock data:", error);
      return MOCK_IRRIGATION_METHODS;
    }
  },

  /**
   * Fetch irrigation stats/summary
   * جلب إحصائيات الري
   */
  getStats: async (): Promise<{ totalWaterToday: number; inProgressCount: number; scheduledCount: number; overdueCount: number; efficiency: number }> => {
    try {
      const response = await api.get(IRRIGATION_ENDPOINTS.EFFICIENCY);
      const data = response.data.data || response.data;
      return {
        totalWaterToday: data.totalWaterToday ?? 0,
        inProgressCount: data.inProgressCount ?? 0,
        scheduledCount: data.scheduledCount ?? 0,
        overdueCount: data.overdueCount ?? 0,
        efficiency: data.efficiency ?? 87,
      };
    } catch {
      // Stats will be computed from schedules in the component
      return { totalWaterToday: 0, inProgressCount: 0, scheduledCount: 0, overdueCount: 0, efficiency: 87 };
    }
  },
};
