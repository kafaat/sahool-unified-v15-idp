/**
 * Reports Feature - API Layer
 * طبقة API لميزة التقارير
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// Only warn during development, don't throw during build
if (!process.env.NEXT_PUBLIC_API_URL && typeof window !== 'undefined') {
  console.warn('NEXT_PUBLIC_API_URL environment variable is not set');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export type ReportType = 'field_performance' | 'yield_analysis' | 'ndvi_summary' | 'irrigation' | 'weather' | 'disease' | 'financial' | 'custom';
export type ReportFormat = 'pdf' | 'excel' | 'csv' | 'json';
export type ReportStatus = 'pending' | 'generating' | 'ready' | 'failed' | 'expired';
export type ReportPeriod = 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly' | 'custom';

export interface Report {
  id: string;
  name: string;
  nameAr: string;
  type: ReportType;
  format: ReportFormat;
  status: ReportStatus;
  period: ReportPeriod;
  startDate: string;
  endDate: string;
  fieldIds?: string[];
  farmIds?: string[];
  governorate?: string;
  downloadUrl?: string;
  fileSize?: number;
  pageCount?: number;
  createdAt: string;
  completedAt?: string;
  expiresAt?: string;
  createdBy: string;
  parameters?: Record<string, unknown>;
}

export interface ReportTemplate {
  id: string;
  name: string;
  nameAr: string;
  description: string;
  descriptionAr: string;
  type: ReportType;
  supportedFormats: ReportFormat[];
  requiredParameters: string[];
  optionalParameters: string[];
  isDefault: boolean;
}

export interface GenerateReportRequest {
  templateId?: string;
  type: ReportType;
  format: ReportFormat;
  period: ReportPeriod;
  startDate?: string;
  endDate?: string;
  fieldIds?: string[];
  farmIds?: string[];
  governorate?: string;
  parameters?: Record<string, unknown>;
}

export interface ReportFilters {
  type?: ReportType;
  status?: ReportStatus;
  format?: ReportFormat;
  startDate?: string;
  endDate?: string;
}

export interface ReportStats {
  totalGenerated: number;
  byType: Record<ReportType, number>;
  byFormat: Record<ReportFormat, number>;
  averageGenerationTime: number;
  totalDownloads: number;
}

// API Functions
export const reportsApi = {
  /**
   * Get list of reports
   */
  getReports: async (filters?: ReportFilters): Promise<Report[]> => {
    const params = new URLSearchParams();
    if (filters?.type) params.set('type', filters.type);
    if (filters?.status) params.set('status', filters.status);
    if (filters?.format) params.set('format', filters.format);
    if (filters?.startDate) params.set('start_date', filters.startDate);
    if (filters?.endDate) params.set('end_date', filters.endDate);

    const response = await api.get(`/api/v1/reports?${params.toString()}`);
    return response.data;
  },

  /**
   * Get a specific report
   */
  getReport: async (id: string): Promise<Report> => {
    const response = await api.get(`/api/v1/reports/${id}`);
    return response.data;
  },

  /**
   * Generate a new report
   */
  generateReport: async (request: GenerateReportRequest): Promise<Report> => {
    const response = await api.post('/api/v1/reports/generate', request);
    return response.data;
  },

  /**
   * Get report download URL
   */
  getDownloadUrl: async (id: string): Promise<{ url: string; expiresAt: string }> => {
    const response = await api.get(`/api/v1/reports/${id}/download`);
    return response.data;
  },

  /**
   * Delete a report
   */
  deleteReport: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/reports/${id}`);
  },

  /**
   * Get available report templates
   */
  getTemplates: async (): Promise<ReportTemplate[]> => {
    const response = await api.get('/api/v1/reports/templates');
    return response.data;
  },

  /**
   * Get report statistics
   */
  getStats: async (): Promise<ReportStats> => {
    const response = await api.get('/api/v1/reports/stats');
    return response.data;
  },

  /**
   * Schedule a recurring report
   */
  scheduleReport: async (
    request: GenerateReportRequest & { schedule: string; recipients: string[] }
  ): Promise<{ scheduleId: string }> => {
    const response = await api.post('/api/v1/reports/schedule', request);
    return response.data;
  },

  /**
   * Get scheduled reports
   */
  getScheduledReports: async (): Promise<Array<{
    id: string;
    report: GenerateReportRequest;
    schedule: string;
    recipients: string[];
    lastRun?: string;
    nextRun: string;
    isActive: boolean;
  }>> => {
    const response = await api.get('/api/v1/reports/scheduled');
    return response.data;
  },
};
