/**
 * Analytics Feature - API Layer
 * طبقة API لميزة التحليلات
 */

import { type AxiosError } from 'axios';
import { createApiClient, logger } from '@/lib/api/factory';
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

// Mock data helpers - dynamic import for dead-code elimination in production builds.
// In production, mock modules are never bundled because the import() is unreachable.
type MockModule = typeof import('./api.mock');
async function loadMockModule(): Promise<MockModule | null> {
  if (process.env.NODE_ENV !== 'production') {
    return import('./api.mock');
  }
  return null;
}

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
    try {
      const params = buildQueryParams(filters);
      const response = await api.get(`${INDICATOR_ENDPOINTS.SUMMARY}?${params.toString()}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch analytics summary from API, using mock data:', error);
      const mock = await loadMockModule();
      if (mock) return mock.MOCK_SUMMARY;
      throw error;
    }
  },

  /**
   * Get yield analytics data
   */
  getYieldAnalytics: async (filters?: AnalyticsFilters): Promise<YieldData[]> => {
    try {
      const params = buildQueryParams(filters);
      const response = await api.get(`${YIELD_ENDPOINTS.PREDICTIONS}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      const mock = await loadMockModule();
      return mock ? mock.MOCK_YIELD_DATA : [];
    } catch (error) {
      logger.warn('Failed to fetch yield analytics from API, using mock data:', error);
      const mock = await loadMockModule();
      return mock ? mock.MOCK_YIELD_DATA : [];
    }
  },

  /**
   * Get cost analytics data
   */
  getCostAnalytics: async (filters?: AnalyticsFilters): Promise<CostData[]> => {
    try {
      const params = buildQueryParams(filters);
      const response = await api.get(`${YIELD_ENDPOINTS.PROFITABILITY}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      const mock = await loadMockModule();
      return mock ? mock.MOCK_COST_DATA : [];
    } catch (error) {
      logger.warn('Failed to fetch cost analytics from API, using mock data:', error);
      const mock = await loadMockModule();
      return mock ? mock.MOCK_COST_DATA : [];
    }
  },

  /**
   * Get revenue analytics data
   */
  getRevenueAnalytics: async (filters?: AnalyticsFilters): Promise<RevenueData[]> => {
    try {
      const params = buildQueryParams(filters);
      const response = await api.get(
        `${YIELD_ENDPOINTS.PROFITABILITY}?${params.toString()}&type=revenue`
      );
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      const mock = await loadMockModule();
      return mock ? mock.MOCK_REVENUE_DATA : [];
    } catch (error) {
      logger.warn('Failed to fetch revenue analytics from API, using mock data:', error);
      const mock = await loadMockModule();
      return mock ? mock.MOCK_REVENUE_DATA : [];
    }
  },

  /**
   * Get KPI metrics
   */
  getKPIs: async (filters?: AnalyticsFilters): Promise<KPIMetric[]> => {
    try {
      const params = buildQueryParams(filters);
      const response = await api.get(`${INDICATOR_ENDPOINTS.DASHBOARD}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      const mock = await loadMockModule();
      return mock ? mock.MOCK_KPI_METRICS : [];
    } catch (error) {
      logger.warn('Failed to fetch KPI metrics from API, using mock data:', error);
      const mock = await loadMockModule();
      return mock ? mock.MOCK_KPI_METRICS : [];
    }
  },

  /**
   * Get comparison data
   */
  getComparison: async (
    type: ComparisonType,
    metric: MetricType,
    filters?: AnalyticsFilters
  ): Promise<ComparisonData> => {
    try {
      const params = buildQueryParams(filters);
      params.set('type', type);
      params.set('metric', metric);

      const response = await api.get(`${INDICATOR_ENDPOINTS.TRENDS}?${params.toString()}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch comparison data from API, using mock data:', error);

      // Generate mock comparison data
      const mock = await loadMockModule();
      const yieldData = mock ? mock.MOCK_YIELD_DATA : [];
      return {
        type,
        metric,
        period: {
          start: new Date(new Date().setMonth(new Date().getMonth() - 6)).toISOString(),
          end: new Date().toISOString(),
        },
        items: yieldData.map((yd) => ({
          id: yd.fieldId,
          name: yd.fieldName,
          nameAr: yd.fieldNameAr,
          value: yd.totalYield,
          data: yd.timeSeries,
        })),
      };
    }
  },

  /**
   * Get resource usage data
   */
  getResourceUsage: async (filters?: AnalyticsFilters): Promise<ResourceUsage[]> => {
    try {
      const params = buildQueryParams(filters);
      const response = await api.get(`${INDICATOR_ENDPOINTS.DEFINITIONS}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      const mock = await loadMockModule();
      return mock ? mock.MOCK_RESOURCE_USAGE : [];
    } catch (error) {
      logger.warn('Failed to fetch resource usage from API, using mock data:', error);
      const mock = await loadMockModule();
      return mock ? mock.MOCK_RESOURCE_USAGE : [];
    }
  },

  /**
   * Generate a report
   */
  generateReport: async (
    config: ReportConfig
  ): Promise<{ downloadUrl: string; reportId: string }> => {
    try {
      const response = await api.post(`${YIELD_ENDPOINTS.PREDICT_POST}`, config);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to generate report:', error);

      // Return error with Arabic message
      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message || ERROR_MESSAGES.GENERATE_REPORT_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar || ERROR_MESSAGES.GENERATE_REPORT_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        })
      );
    }
  },

  /**
   * Download a generated report
   */
  downloadReport: async (reportId: string): Promise<Blob> => {
    try {
      const response = await api.get(`${YIELD_ENDPOINTS.PREDICTIONS}/${reportId}/download`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      logger.error(`Failed to download report ${reportId}:`, error);

      // Return error with Arabic message
      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message || ERROR_MESSAGES.DOWNLOAD_REPORT_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar || ERROR_MESSAGES.DOWNLOAD_REPORT_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        })
      );
    }
  },
};
