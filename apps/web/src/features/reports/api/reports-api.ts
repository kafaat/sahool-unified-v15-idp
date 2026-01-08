/**
 * Reports Feature - Extended API Layer for Field Reports
 * طبقة API الموسعة لتقارير الحقول
 */

import axios from 'axios';
import Cookies from 'js-cookie';
import { logger } from '@/lib/logger';
import type {
  GeneratedReport,
  GenerateFieldReportRequest,
  GenerateSeasonReportRequest,
  ReportHistoryItem,
  ReportHistoryFilters,
  ShareReportRequest,
  ShareReportResponse,
  DownloadReportResponse,
  FieldReportData,
  SeasonReportData,
  ReportTemplate,
  ReportErrorMessages,
} from '../types/reports';

// ═══════════════════════════════════════════════════════════════════════════
// API Configuration
// ═══════════════════════════════════════════════════════════════════════════

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

if (!API_BASE_URL && typeof window !== 'undefined') {
  console.warn('NEXT_PUBLIC_API_URL environment variable is not set');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds for report generation
});

// ═══════════════════════════════════════════════════════════════════════════
// Auth Token Interceptor
// ═══════════════════════════════════════════════════════════════════════════

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = Cookies.get('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// ═══════════════════════════════════════════════════════════════════════════
// Error Messages (Bilingual)
// ═══════════════════════════════════════════════════════════════════════════

export const ERROR_MESSAGES: ReportErrorMessages = {
  GENERATION_FAILED: {
    en: 'Failed to generate report. Please try again.',
    ar: 'فشل في إنشاء التقرير. يرجى المحاولة مرة أخرى.',
  },
  DOWNLOAD_FAILED: {
    en: 'Failed to download report.',
    ar: 'فشل في تنزيل التقرير.',
  },
  SHARE_FAILED: {
    en: 'Failed to share report.',
    ar: 'فشل في مشاركة التقرير.',
  },
  DELETE_FAILED: {
    en: 'Failed to delete report.',
    ar: 'فشل في حذف التقرير.',
  },
  INVALID_DATA: {
    en: 'Invalid report data provided.',
    ar: 'بيانات التقرير المقدمة غير صالحة.',
  },
  NOT_FOUND: {
    en: 'Report not found.',
    ar: 'التقرير غير موجود.',
  },
  EXPIRED: {
    en: 'Report has expired.',
    ar: 'انتهت صلاحية التقرير.',
  },
  UNAUTHORIZED: {
    en: 'Unauthorized access to report.',
    ar: 'وصول غير مصرح به إلى التقرير.',
  },
  NO_DATA: {
    en: 'No data available for the selected period.',
    ar: 'لا توجد بيانات متاحة للفترة المحددة.',
  },
  NETWORK_ERROR: {
    en: 'Network error. Please check your connection.',
    ar: 'خطأ في الشبكة. يرجى التحقق من الاتصال.',
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Mock Data for Development/Fallback
// ═══════════════════════════════════════════════════════════════════════════

const MOCK_FIELD_REPORT: GeneratedReport = {
  id: 'report-field-1',
  type: 'field',
  format: 'pdf',
  status: 'ready',
  fieldId: 'field-1',
  fieldName: 'North Field',
  fieldNameAr: 'الحقل الشمالي',
  title: 'Field Performance Report - North Field',
  titleAr: 'تقرير أداء الحقل - الحقل الشمالي',
  startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  endDate: new Date().toISOString(),
  sections: ['field_info', 'ndvi_trend', 'health_zones', 'tasks_summary', 'weather_summary', 'recommendations'],
  downloadUrl: '/api/v1/reports/report-field-1/download',
  shareUrl: 'https://sahool.app/reports/shared/report-field-1',
  fileSize: 2548736, // ~2.5MB
  pageCount: 12,
  createdAt: new Date().toISOString(),
  completedAt: new Date().toISOString(),
  expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
  language: 'both',
};

const MOCK_REPORT_TEMPLATES: ReportTemplate[] = [
  {
    type: 'field',
    name: 'Field Performance Report',
    nameAr: 'تقرير أداء الحقل',
    description: 'Comprehensive field performance analysis with NDVI trends and health metrics',
    descriptionAr: 'تحليل شامل لأداء الحقل مع اتجاهات NDVI ومقاييس الصحة',
    defaultSections: [
      {
        section: 'field_info',
        title: 'Field Information',
        titleAr: 'معلومات الحقل',
        description: 'Basic field details and crop information',
        descriptionAr: 'تفاصيل الحقل الأساسية ومعلومات المحصول',
        required: true,
        order: 1,
      },
      {
        section: 'ndvi_trend',
        title: 'NDVI Trend Analysis',
        titleAr: 'تحليل اتجاه NDVI',
        description: 'Vegetation health trends over time',
        descriptionAr: 'اتجاهات صحة النباتات عبر الزمن',
        required: false,
        order: 2,
      },
      {
        section: 'health_zones',
        title: 'Health Zones Map',
        titleAr: 'خريطة مناطق الصحة',
        description: 'Spatial distribution of crop health',
        descriptionAr: 'التوزيع المكاني لصحة المحصول',
        required: false,
        order: 3,
      },
      {
        section: 'recommendations',
        title: 'Recommendations',
        titleAr: 'التوصيات',
        description: 'AI-powered recommendations for field management',
        descriptionAr: 'توصيات مدعومة بالذكاء الاصطناعي لإدارة الحقل',
        required: false,
        order: 6,
      },
    ],
    supportedFormats: ['pdf', 'excel'],
    estimatedGenerationTime: 15,
  },
  {
    type: 'season',
    name: 'Season Summary Report',
    nameAr: 'تقرير ملخص الموسم',
    description: 'Complete season analysis with yield estimates and cost breakdown',
    descriptionAr: 'تحليل موسمي كامل مع تقديرات المحصول وتفصيل التكاليف',
    defaultSections: [
      {
        section: 'crop_stages',
        title: 'Crop Growth Stages',
        titleAr: 'مراحل نمو المحصول',
        description: 'Timeline of crop development stages',
        descriptionAr: 'جدول زمني لمراحل تطور المحصول',
        required: true,
        order: 1,
      },
      {
        section: 'yield_estimate',
        title: 'Yield Estimate',
        titleAr: 'تقدير المحصول',
        description: 'Predicted and actual yield data',
        descriptionAr: 'بيانات المحصول المتوقعة والفعلية',
        required: false,
        order: 2,
      },
      {
        section: 'cost_analysis',
        title: 'Cost Analysis',
        titleAr: 'تحليل التكاليف',
        description: 'Detailed cost breakdown and ROI',
        descriptionAr: 'تفصيل التكاليف والعائد على الاستثمار',
        required: false,
        order: 3,
      },
    ],
    supportedFormats: ['pdf', 'excel', 'csv'],
    estimatedGenerationTime: 20,
  },
];

// ═══════════════════════════════════════════════════════════════════════════
// API Functions
// ═══════════════════════════════════════════════════════════════════════════

export const reportsApi = {
  /**
   * Generate a field report
   * إنشاء تقرير حقل
   */
  generateFieldReport: async (request: GenerateFieldReportRequest): Promise<GeneratedReport> => {
    try {
      const response = await api.post('/api/v1/reports/field/generate', request);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.error('Failed to generate field report:', error);
      // Return mock data for development
      if (process.env.NODE_ENV === 'development') {
        logger.warn('Using mock field report data');
        return MOCK_FIELD_REPORT;
      }
      throw new Error(ERROR_MESSAGES.GENERATION_FAILED.en);
    }
  },

  /**
   * Generate a season report
   * إنشاء تقرير موسم
   */
  generateSeasonReport: async (request: GenerateSeasonReportRequest): Promise<GeneratedReport> => {
    try {
      const response = await api.post('/api/v1/reports/season/generate', request);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.error('Failed to generate season report:', error);
      if (process.env.NODE_ENV === 'development') {
        logger.warn('Using mock season report data');
        return { ...MOCK_FIELD_REPORT, type: 'season', id: 'report-season-1' };
      }
      throw new Error(ERROR_MESSAGES.GENERATION_FAILED.en);
    }
  },

  /**
   * Get report history with filters
   * جلب سجل التقارير مع الفلاتر
   */
  getReportHistory: async (filters?: ReportHistoryFilters): Promise<ReportHistoryItem[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.type) params.set('type', filters.type);
      if (filters?.status) params.set('status', filters.status);
      if (filters?.startDate) params.set('start_date', filters.startDate);
      if (filters?.endDate) params.set('end_date', filters.endDate);
      if (filters?.search) params.set('search', filters.search);

      const response = await api.get(`/api/v1/reports/history?${params.toString()}`);
      const data = response.data.data || response.data;
      return Array.isArray(data) ? data : [];
    } catch (error) {
      logger.warn('Failed to fetch report history:', error);
      // Return mock data
      return [MOCK_FIELD_REPORT, { ...MOCK_FIELD_REPORT, id: 'report-field-2', downloadCount: 5 }];
    }
  },

  /**
   * Get a specific report by ID
   * جلب تقرير محدد بواسطة المعرف
   */
  getReport: async (reportId: string): Promise<GeneratedReport> => {
    try {
      const response = await api.get(`/api/v1/reports/${reportId}`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.error(`Failed to fetch report ${reportId}:`, error);
      if (process.env.NODE_ENV === 'development') {
        return MOCK_FIELD_REPORT;
      }
      throw new Error(ERROR_MESSAGES.NOT_FOUND.en);
    }
  },

  /**
   * Download a report
   * تنزيل تقرير
   */
  downloadReport: async (reportId: string): Promise<DownloadReportResponse> => {
    try {
      const response = await api.get(`/api/v1/reports/${reportId}/download`);
      const data = response.data.data || response.data;
      return {
        success: true,
        url: data.url || data.downloadUrl,
        expiresAt: data.expiresAt,
      };
    } catch (error) {
      logger.error('Failed to download report:', error);
      throw new Error(ERROR_MESSAGES.DOWNLOAD_FAILED.en);
    }
  },

  /**
   * Share a report
   * مشاركة تقرير
   */
  shareReport: async (request: ShareReportRequest): Promise<ShareReportResponse> => {
    try {
      const response = await api.post(`/api/v1/reports/${request.reportId}/share`, request);
      const data = response.data.data || response.data;
      return {
        success: true,
        shareUrl: data.shareUrl,
        expiresAt: data.expiresAt,
        message: data.message,
        messageAr: data.messageAr,
      };
    } catch (error) {
      logger.error('Failed to share report:', error);
      // Return mock share URL for development
      if (process.env.NODE_ENV === 'development') {
        return {
          success: true,
          shareUrl: `https://sahool.app/reports/shared/${request.reportId}`,
          expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        };
      }
      throw new Error(ERROR_MESSAGES.SHARE_FAILED.en);
    }
  },

  /**
   * Delete a report
   * حذف تقرير
   */
  deleteReport: async (reportId: string): Promise<void> => {
    try {
      await api.delete(`/api/v1/reports/${reportId}`);
    } catch (error) {
      logger.error('Failed to delete report:', error);
      throw new Error(ERROR_MESSAGES.DELETE_FAILED.en);
    }
  },

  /**
   * Get field report data (for preview/template rendering)
   * جلب بيانات تقرير الحقل
   */
  getFieldReportData: async (
    fieldId: string,
    startDate?: string,
    endDate?: string
  ): Promise<FieldReportData> => {
    try {
      const params = new URLSearchParams();
      params.set('field_id', fieldId);
      if (startDate) params.set('start_date', startDate);
      if (endDate) params.set('end_date', endDate);

      const response = await api.get(`/api/v1/reports/field/data?${params.toString()}`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.error('Failed to fetch field report data:', error);
      throw new Error(ERROR_MESSAGES.NO_DATA.en);
    }
  },

  /**
   * Get season report data (for preview/template rendering)
   * جلب بيانات تقرير الموسم
   */
  getSeasonReportData: async (
    fieldId: string,
    season?: string,
    startDate?: string,
    endDate?: string
  ): Promise<SeasonReportData> => {
    try {
      const params = new URLSearchParams();
      params.set('field_id', fieldId);
      if (season) params.set('season', season);
      if (startDate) params.set('start_date', startDate);
      if (endDate) params.set('end_date', endDate);

      const response = await api.get(`/api/v1/reports/season/data?${params.toString()}`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.error('Failed to fetch season report data:', error);
      throw new Error(ERROR_MESSAGES.NO_DATA.en);
    }
  },

  /**
   * Get available report templates
   * جلب قوالب التقارير المتاحة
   */
  getReportTemplates: async (): Promise<ReportTemplate[]> => {
    try {
      const response = await api.get('/api/v1/reports/templates');
      const data = response.data.data || response.data;
      return Array.isArray(data) ? data : MOCK_REPORT_TEMPLATES;
    } catch (error) {
      logger.warn('Failed to fetch report templates, using defaults:', error);
      return MOCK_REPORT_TEMPLATES;
    }
  },

  /**
   * Check report generation status
   * التحقق من حالة إنشاء التقرير
   */
  checkReportStatus: async (reportId: string): Promise<GeneratedReport> => {
    try {
      const response = await api.get(`/api/v1/reports/${reportId}/status`);
      const data = response.data.data || response.data;
      return data;
    } catch (error) {
      logger.error('Failed to check report status:', error);
      throw new Error(ERROR_MESSAGES.NOT_FOUND.en);
    }
  },
};

export default reportsApi;
