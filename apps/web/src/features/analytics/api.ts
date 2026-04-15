/**
 * Analytics Feature - API Layer
 * طبقة API لميزة التحليلات
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { INDICATOR_ENDPOINTS, YIELD_ENDPOINTS } from '@sahool/shared-types/contracts';
import type {
  AnalyticsSummary,
  YieldData,
  CostData,
  RevenueData,
  KPIMetric,
  ComparisonData,
  ResourceUsage,
  ReportConfig,
  AnalyticsFilters,
  ComparisonType,
  MetricType,
} from './types';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_SUMMARY_FAILED: {
    en: 'Failed to fetch analytics summary. Using cached data.',
    ar: 'فشل في جلب ملخص التحليلات. استخدام البيانات المخزنة.',
  },
  FETCH_YIELD_FAILED: {
    en: 'Failed to fetch yield data. Using cached data.',
    ar: 'فشل في جلب بيانات الإنتاج. استخدام البيانات المخزنة.',
  },
  FETCH_COST_FAILED: {
    en: 'Failed to fetch cost data. Using cached data.',
    ar: 'فشل في جلب بيانات التكاليف. استخدام البيانات المخزنة.',
  },
  FETCH_REVENUE_FAILED: {
    en: 'Failed to fetch revenue data. Using cached data.',
    ar: 'فشل في جلب بيانات الإيرادات. استخدام البيانات المخزنة.',
  },
  FETCH_KPI_FAILED: {
    en: 'Failed to fetch KPI metrics. Using cached data.',
    ar: 'فشل في جلب مؤشرات الأداء. استخدام البيانات المخزنة.',
  },
  FETCH_COMPARISON_FAILED: {
    en: 'Failed to fetch comparison data. Using cached data.',
    ar: 'فشل في جلب بيانات المقارنة. استخدام البيانات المخزنة.',
  },
  FETCH_RESOURCES_FAILED: {
    en: 'Failed to fetch resource usage data. Using cached data.',
    ar: 'فشل في جلب بيانات استهلاك الموارد. استخدام البيانات المخزنة.',
  },
  GENERATE_REPORT_FAILED: {
    en: 'Failed to generate report. Please try again.',
    ar: 'فشل في إنشاء التقرير. الرجاء المحاولة مرة أخرى.',
  },
  DOWNLOAD_REPORT_FAILED: {
    en: 'Failed to download report. Please try again.',
    ar: 'فشل في تحميل التقرير. الرجاء المحاولة مرة أخرى.',
  },
};

/**
 * Build query string from analytics filters
 */
function buildQueryParams(filters?: AnalyticsFilters): URLSearchParams {
  const params = new URLSearchParams();
  if (filters?.fieldIds?.length) params.set('field_ids', filters.fieldIds.join(','));
  if (filters?.cropTypes?.length) params.set('crop_types', filters.cropTypes.join(','));
  if (filters?.period) params.set('period', filters.period);
  if (filters?.startDate) params.set('start_date', filters.startDate);
  if (filters?.endDate) params.set('end_date', filters.endDate);
  if (filters?.seasons?.length) params.set('seasons', filters.seasons.join(','));
  return params;
}

// API Functions
export const analyticsApi = {
  /**
   * Get analytics summary
   */
  getSummary: async (filters?: AnalyticsFilters): Promise<AnalyticsSummary> => {
    return safeFetch(INDICATOR_ENDPOINTS.SUMMARY, async () => {
      const params = buildQueryParams(filters);
      const response = await api.get(`${INDICATOR_ENDPOINTS.SUMMARY}?${params.toString()}`);
      return response.data.data || response.data;
    });
  },

  /**
   * Get yield analytics data
   */
  getYieldAnalytics: async (filters?: AnalyticsFilters): Promise<YieldData[]> => {
    return safeFetch(YIELD_ENDPOINTS.PREDICTIONS, async () => {
      const params = buildQueryParams(filters);
      const response = await api.get(`${YIELD_ENDPOINTS.PREDICTIONS}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Get cost analytics data
   */
  getCostAnalytics: async (filters?: AnalyticsFilters): Promise<CostData[]> => {
    return safeFetch(YIELD_ENDPOINTS.PROFITABILITY, async () => {
      const params = buildQueryParams(filters);
      const response = await api.get(`${YIELD_ENDPOINTS.PROFITABILITY}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Get revenue analytics data
   */
  getRevenueAnalytics: async (filters?: AnalyticsFilters): Promise<RevenueData[]> => {
    return safeFetch(YIELD_ENDPOINTS.PROFITABILITY, async () => {
      const params = buildQueryParams(filters);
      const response = await api.get(
        `${YIELD_ENDPOINTS.PROFITABILITY}?${params.toString()}&type=revenue`
      );
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Get KPI metrics
   */
  getKPIs: async (filters?: AnalyticsFilters): Promise<KPIMetric[]> => {
    return safeFetch(INDICATOR_ENDPOINTS.DASHBOARD, async () => {
      const params = buildQueryParams(filters);
      const response = await api.get(`${INDICATOR_ENDPOINTS.DASHBOARD}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Get comparison data
   */
  getComparison: async (
    type: ComparisonType,
    metric: MetricType,
    filters?: AnalyticsFilters
  ): Promise<ComparisonData> => {
    return safeFetch(INDICATOR_ENDPOINTS.TRENDS, async () => {
      const params = buildQueryParams(filters);
      params.set('type', type);
      params.set('metric', metric);

      const response = await api.get(`${INDICATOR_ENDPOINTS.TRENDS}?${params.toString()}`);
      return response.data.data || response.data;
    });
  },

  /**
   * Get resource usage data
   */
  getResourceUsage: async (filters?: AnalyticsFilters): Promise<ResourceUsage[]> => {
    return safeFetch(INDICATOR_ENDPOINTS.DEFINITIONS, async () => {
      const params = buildQueryParams(filters);
      const response = await api.get(`${INDICATOR_ENDPOINTS.DEFINITIONS}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Generate a report
   */
  generateReport: async (
    config: ReportConfig
  ): Promise<{ downloadUrl: string; reportId: string }> => {
    return safeFetch(YIELD_ENDPOINTS.PREDICT_POST, async () => {
      const response = await api.post(`${YIELD_ENDPOINTS.PREDICT_POST}`, config);
      return response.data.data || response.data;
    });
  },

  /**
   * Download a generated report
   */
  downloadReport: async (reportId: string): Promise<Blob> => {
    return safeFetch(`${YIELD_ENDPOINTS.PREDICTIONS}/${reportId}/download`, async () => {
      const response = await api.get(`${YIELD_ENDPOINTS.PREDICTIONS}/${reportId}/download`, {
        responseType: 'blob',
      });
      return response.data;
    });
  },
};
