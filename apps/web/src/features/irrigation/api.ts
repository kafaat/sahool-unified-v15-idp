/**
 * Irrigation Feature - API Layer
 * طبقة API لميزة الري - Real API with mock fallback
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { IRRIGATION_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import type {
  IrrigationSchedule,
  IrrigationMethod,
  CreateScheduleRequest,
  CalculateIrrigationRequest,
  IrrigationPrediction,
  WaterBalanceResponse,
  EfficiencyReport,
  SensorReadingRequest,
  SensorReadingResponse,
  IrrigationExecutionRequest,
  IrrigationExecutionResponse,
  CalculateWithActionResponse,
  SmartIrrigationMethod,
} from './types';

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

  // ---------------------------------------------------------------------------
  // ML Irrigation Endpoints - نقاط نهاية الري الذكي
  // ---------------------------------------------------------------------------

  /**
   * Calculate irrigation needs using ML prediction
   * حساب احتياجات الري باستخدام التنبؤ الذكي
   *
   * POST /api/v1/calculate
   */
  calculateIrrigation: async (
    params: CalculateIrrigationRequest
  ): Promise<IrrigationPrediction> => {
    const response = await api.post('/api/v1/calculate', params);
    return response.data.data || response.data;
  },

  /**
   * Get water balance for a field over a period
   * جلب الميزان المائي للحقل
   *
   * GET /api/v1/water-balance/{fieldId}
   */
  getWaterBalance: async (
    fieldId: string,
    options?: { crop?: string; days?: number }
  ): Promise<WaterBalanceResponse> => {
    const params: Record<string, string | number> = {};
    if (options?.crop) params.crop = options.crop;
    if (options?.days) params.days = options.days;
    const response = await api.get(`/api/v1/water-balance/${fieldId}`, { params });
    return response.data.data || response.data;
  },

  /**
   * Get irrigation efficiency report comparing methods
   * جلب تقرير كفاءة الري ومقارنة الطرق
   *
   * GET /api/v1/efficiency-report/{fieldId}
   */
  getEfficiencyReport: async (
    fieldId: string,
    options?: { current_method?: SmartIrrigationMethod; area_hectares?: number }
  ): Promise<EfficiencyReport> => {
    const params: Record<string, string | number> = {};
    if (options?.current_method) params.current_method = options.current_method;
    if (options?.area_hectares) params.area_hectares = options.area_hectares;
    const response = await api.get(`/api/v1/efficiency-report/${fieldId}`, { params });
    return response.data.data || response.data;
  },

  /**
   * Record a soil moisture sensor reading
   * تسجيل قراءة مستشعر رطوبة التربة
   *
   * POST /api/v1/sensor-reading
   */
  recordSensorReading: async (
    data: SensorReadingRequest
  ): Promise<SensorReadingResponse> => {
    const response = await api.post('/api/v1/sensor-reading', data);
    return response.data.data || response.data;
  },

  /**
   * Record an irrigation execution event
   * تسجيل تنفيذ عملية ري
   *
   * POST /api/v1/irrigation-executed
   */
  recordIrrigationExecution: async (
    data: IrrigationExecutionRequest
  ): Promise<IrrigationExecutionResponse> => {
    const response = await api.post('/api/v1/irrigation-executed', data);
    return response.data.data || response.data;
  },

  /**
   * Calculate irrigation with an ActionTemplate for offline-first execution
   * حساب الري مع قالب إجراء قابل للتنفيذ بدون اتصال
   *
   * POST /api/v1/calculate-with-action
   */
  calculateWithAction: async (
    params: CalculateIrrigationRequest
  ): Promise<CalculateWithActionResponse> => {
    const response = await api.post('/api/v1/calculate-with-action', params);
    return response.data.data || response.data;
  },
};
