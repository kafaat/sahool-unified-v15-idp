/**
 * Analytics Feature - API Layer
 * طبقة API لميزة التحليلات
 */

import axios, { type AxiosError } from 'axios';
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
import { logger } from '@/lib/logger';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// Only warn during development, don't throw during build
if (!API_BASE_URL && typeof window !== 'undefined') {
  console.warn('NEXT_PUBLIC_API_URL environment variable is not set');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Add auth token interceptor
// SECURITY: Use js-cookie library for safe cookie parsing instead of manual parsing
import Cookies from 'js-cookie';

api.interceptors.request.use((config) => {
  // Get token from cookie using secure cookie parser
  if (typeof window !== 'undefined') {
    const token = Cookies.get('access_token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

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

// Mock data for fallback
const MOCK_SUMMARY: AnalyticsSummary = {
  totalFields: 3,
  totalArea: 13.5,
  totalYield: 45000,
  totalRevenue: 135000,
  totalCost: 67500,
  totalProfit: 67500,
  averageYieldPerHectare: 3333.33,
  topPerformingField: {
    id: '1',
    name: 'North Field',
    nameAr: 'الحقل الشمالي',
    yieldPerHectare: 3636.36,
  },
  period: {
    start: new Date(new Date().setMonth(new Date().getMonth() - 6)).toISOString(),
    end: new Date().toISOString(),
  },
};

const MOCK_YIELD_DATA: YieldData[] = [
  {
    fieldId: '1',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    cropType: 'Wheat',
    cropTypeAr: 'قمح',
    totalYield: 20000,
    expectedYield: 19000,
    yieldPerHectare: 3636.36,
    area: 5.5,
    season: 'Winter 2025',
    harvestDate: new Date().toISOString(),
    variance: 5.26,
    timeSeries: [
      { date: '2025-01', value: 0, label: 'Jan', labelAr: 'يناير' },
      { date: '2025-02', value: 0, label: 'Feb', labelAr: 'فبراير' },
      { date: '2025-03', value: 5000, label: 'Mar', labelAr: 'مارس' },
      { date: '2025-04', value: 15000, label: 'Apr', labelAr: 'أبريل' },
      { date: '2025-05', value: 20000, label: 'May', labelAr: 'مايو' },
    ],
  },
  {
    fieldId: '2',
    fieldName: 'South Field',
    fieldNameAr: 'الحقل الجنوبي',
    cropType: 'Corn',
    cropTypeAr: 'ذرة',
    totalYield: 12000,
    expectedYield: 13000,
    yieldPerHectare: 3750,
    area: 3.2,
    season: 'Summer 2025',
    harvestDate: new Date().toISOString(),
    variance: -7.69,
    timeSeries: [
      { date: '2025-03', value: 0, label: 'Mar', labelAr: 'مارس' },
      { date: '2025-04', value: 0, label: 'Apr', labelAr: 'أبريل' },
      { date: '2025-05', value: 3000, label: 'May', labelAr: 'مايو' },
      { date: '2025-06', value: 8000, label: 'Jun', labelAr: 'يونيو' },
      { date: '2025-07', value: 12000, label: 'Jul', labelAr: 'يوليو' },
    ],
  },
  {
    fieldId: '3',
    fieldName: 'East Field',
    fieldNameAr: 'الحقل الشرقي',
    cropType: 'Barley',
    cropTypeAr: 'شعير',
    totalYield: 13000,
    expectedYield: 12500,
    yieldPerHectare: 2708.33,
    area: 4.8,
    season: 'Winter 2025',
    harvestDate: new Date().toISOString(),
    variance: 4.0,
    timeSeries: [
      { date: '2025-01', value: 0, label: 'Jan', labelAr: 'يناير' },
      { date: '2025-02', value: 0, label: 'Feb', labelAr: 'فبراير' },
      { date: '2025-03', value: 4000, label: 'Mar', labelAr: 'مارس' },
      { date: '2025-04', value: 9000, label: 'Apr', labelAr: 'أبريل' },
      { date: '2025-05', value: 13000, label: 'May', labelAr: 'مايو' },
    ],
  },
];

const MOCK_COST_DATA: CostData[] = [
  {
    fieldId: '1',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    totalCost: 27500,
    breakdown: {
      seeds: 5500,
      fertilizers: 8250,
      pesticides: 2750,
      irrigation: 5500,
      labor: 4125,
      equipment: 1100,
      other: 275,
    },
    costPerHectare: 5000,
    period: {
      start: new Date(new Date().setMonth(new Date().getMonth() - 6)).toISOString(),
      end: new Date().toISOString(),
    },
  },
  {
    fieldId: '2',
    fieldName: 'South Field',
    fieldNameAr: 'الحقل الجنوبي',
    totalCost: 16000,
    breakdown: {
      seeds: 3200,
      fertilizers: 4800,
      pesticides: 1600,
      irrigation: 3200,
      labor: 2400,
      equipment: 640,
      other: 160,
    },
    costPerHectare: 5000,
    period: {
      start: new Date(new Date().setMonth(new Date().getMonth() - 6)).toISOString(),
      end: new Date().toISOString(),
    },
  },
  {
    fieldId: '3',
    fieldName: 'East Field',
    fieldNameAr: 'الحقل الشرقي',
    totalCost: 24000,
    breakdown: {
      seeds: 4800,
      fertilizers: 7200,
      pesticides: 2400,
      irrigation: 4800,
      labor: 3600,
      equipment: 960,
      other: 240,
    },
    costPerHectare: 5000,
    period: {
      start: new Date(new Date().setMonth(new Date().getMonth() - 6)).toISOString(),
      end: new Date().toISOString(),
    },
  },
];

const MOCK_REVENUE_DATA: RevenueData[] = [
  {
    fieldId: '1',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    revenue: 60000,
    cost: 27500,
    profit: 32500,
    profitMargin: 54.17,
    roi: 118.18,
    period: {
      start: new Date(new Date().setMonth(new Date().getMonth() - 6)).toISOString(),
      end: new Date().toISOString(),
    },
  },
  {
    fieldId: '2',
    fieldName: 'South Field',
    fieldNameAr: 'الحقل الجنوبي',
    revenue: 36000,
    cost: 16000,
    profit: 20000,
    profitMargin: 55.56,
    roi: 125,
    period: {
      start: new Date(new Date().setMonth(new Date().getMonth() - 6)).toISOString(),
      end: new Date().toISOString(),
    },
  },
  {
    fieldId: '3',
    fieldName: 'East Field',
    fieldNameAr: 'الحقل الشرقي',
    revenue: 39000,
    cost: 24000,
    profit: 15000,
    profitMargin: 38.46,
    roi: 62.5,
    period: {
      start: new Date(new Date().setMonth(new Date().getMonth() - 6)).toISOString(),
      end: new Date().toISOString(),
    },
  },
];

const MOCK_KPI_METRICS: KPIMetric[] = [
  {
    id: 'total-yield',
    name: 'Total Yield',
    nameAr: 'إجمالي الإنتاج',
    value: 45000,
    unit: 'kg',
    unitAr: 'كجم',
    change: 12.5,
    trend: 'up',
    status: 'good',
    icon: 'TrendingUp',
    description: 'Total crop yield across all fields',
    descriptionAr: 'إجمالي إنتاج المحاصيل في جميع الحقول',
  },
  {
    id: 'total-revenue',
    name: 'Total Revenue',
    nameAr: 'إجمالي الإيرادات',
    value: 135000,
    unit: 'SAR',
    unitAr: 'ريال',
    change: 8.3,
    trend: 'up',
    status: 'good',
    icon: 'DollarSign',
    description: 'Total revenue from crop sales',
    descriptionAr: 'إجمالي الإيرادات من بيع المحاصيل',
  },
  {
    id: 'profit-margin',
    name: 'Profit Margin',
    nameAr: 'هامش الربح',
    value: 50,
    unit: '%',
    unitAr: '%',
    change: -2.1,
    trend: 'down',
    status: 'warning',
    icon: 'Percent',
    description: 'Average profit margin across all fields',
    descriptionAr: 'متوسط هامش الربح في جميع الحقول',
  },
  {
    id: 'water-efficiency',
    name: 'Water Efficiency',
    nameAr: 'كفاءة المياه',
    value: 0.85,
    unit: 'm³/kg',
    unitAr: 'م³/كجم',
    change: 5.6,
    trend: 'up',
    status: 'good',
    icon: 'Droplet',
    description: 'Water usage efficiency',
    descriptionAr: 'كفاءة استهلاك المياه',
  },
];

const MOCK_RESOURCE_USAGE: ResourceUsage[] = [
  {
    fieldId: '1',
    fieldName: 'North Field',
    fieldNameAr: 'الحقل الشمالي',
    waterUsage: 17000,
    fertilizerUsage: 825,
    pesticideUsage: 110,
    energyUsage: 2200,
    period: {
      start: new Date(new Date().setMonth(new Date().getMonth() - 6)).toISOString(),
      end: new Date().toISOString(),
    },
    efficiency: {
      waterPerKg: 0.85,
      fertilizerPerKg: 0.041,
      energyPerKg: 0.11,
    },
  },
  {
    fieldId: '2',
    fieldName: 'South Field',
    fieldNameAr: 'الحقل الجنوبي',
    waterUsage: 10800,
    fertilizerUsage: 480,
    pesticideUsage: 64,
    energyUsage: 1320,
    period: {
      start: new Date(new Date().setMonth(new Date().getMonth() - 6)).toISOString(),
      end: new Date().toISOString(),
    },
    efficiency: {
      waterPerKg: 0.9,
      fertilizerPerKg: 0.04,
      energyPerKg: 0.11,
    },
  },
  {
    fieldId: '3',
    fieldName: 'East Field',
    fieldNameAr: 'الحقل الشرقي',
    waterUsage: 11700,
    fertilizerUsage: 720,
    pesticideUsage: 96,
    energyUsage: 1560,
    period: {
      start: new Date(new Date().setMonth(new Date().getMonth() - 6)).toISOString(),
      end: new Date().toISOString(),
    },
    efficiency: {
      waterPerKg: 0.9,
      fertilizerPerKg: 0.055,
      energyPerKg: 0.12,
    },
  },
];

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
      const response = await api.get(`/api/v1/analytics/summary?${params.toString()}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch analytics summary from API, using mock data:', error);
      return MOCK_SUMMARY;
    }
  },

  /**
   * Get yield analytics data
   */
  getYieldAnalytics: async (filters?: AnalyticsFilters): Promise<YieldData[]> => {
    try {
      const params = buildQueryParams(filters);
      const response = await api.get(`/api/v1/analytics/yield?${params.toString()}`);
      const data = response.data.data || response.data;
      return Array.isArray(data) ? data : MOCK_YIELD_DATA;
    } catch (error) {
      logger.warn('Failed to fetch yield analytics from API, using mock data:', error);
      return MOCK_YIELD_DATA;
    }
  },

  /**
   * Get cost analytics data
   */
  getCostAnalytics: async (filters?: AnalyticsFilters): Promise<CostData[]> => {
    try {
      const params = buildQueryParams(filters);
      const response = await api.get(`/api/v1/analytics/cost?${params.toString()}`);
      const data = response.data.data || response.data;
      return Array.isArray(data) ? data : MOCK_COST_DATA;
    } catch (error) {
      logger.warn('Failed to fetch cost analytics from API, using mock data:', error);
      return MOCK_COST_DATA;
    }
  },

  /**
   * Get revenue analytics data
   */
  getRevenueAnalytics: async (filters?: AnalyticsFilters): Promise<RevenueData[]> => {
    try {
      const params = buildQueryParams(filters);
      const response = await api.get(`/api/v1/analytics/revenue?${params.toString()}`);
      const data = response.data.data || response.data;
      return Array.isArray(data) ? data : MOCK_REVENUE_DATA;
    } catch (error) {
      logger.warn('Failed to fetch revenue analytics from API, using mock data:', error);
      return MOCK_REVENUE_DATA;
    }
  },

  /**
   * Get KPI metrics
   */
  getKPIs: async (filters?: AnalyticsFilters): Promise<KPIMetric[]> => {
    try {
      const params = buildQueryParams(filters);
      const response = await api.get(`/api/v1/analytics/kpis?${params.toString()}`);
      const data = response.data.data || response.data;
      return Array.isArray(data) ? data : MOCK_KPI_METRICS;
    } catch (error) {
      logger.warn('Failed to fetch KPI metrics from API, using mock data:', error);
      return MOCK_KPI_METRICS;
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

      const response = await api.get(`/api/v1/analytics/comparison?${params.toString()}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch comparison data from API, using mock data:', error);

      // Generate mock comparison data
      return {
        type,
        metric,
        period: {
          start: new Date(new Date().setMonth(new Date().getMonth() - 6)).toISOString(),
          end: new Date().toISOString(),
        },
        items: MOCK_YIELD_DATA.map((yd) => ({
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
      const response = await api.get(`/api/v1/analytics/resources?${params.toString()}`);
      const data = response.data.data || response.data;
      return Array.isArray(data) ? data : MOCK_RESOURCE_USAGE;
    } catch (error) {
      logger.warn('Failed to fetch resource usage from API, using mock data:', error);
      return MOCK_RESOURCE_USAGE;
    }
  },

  /**
   * Generate a report
   */
  generateReport: async (config: ReportConfig): Promise<{ downloadUrl: string; reportId: string }> => {
    try {
      const response = await api.post('/api/v1/analytics/reports/generate', config);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to generate report:', error);

      // Return error with Arabic message
      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
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
      const response = await api.get(`/api/v1/analytics/reports/${reportId}/download`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      logger.error(`Failed to download report ${reportId}:`, error);

      // Return error with Arabic message
      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
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
