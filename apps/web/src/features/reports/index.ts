/**
 * Reports Feature
 * ميزة التقارير
 *
 * This feature handles:
 * - Field performance reports
 * - Yield reports
 * - NDVI analysis reports
 * - Seasonal summaries
 * - Export to PDF/Excel
 */

// API exports
export { reportsApi } from './api';
export type {
  Report,
  ReportType,
  ReportFormat,
  ReportStatus,
  ReportPeriod,
  ReportTemplate,
  GenerateReportRequest,
  ReportFilters,
  ReportStats,
} from './api';

// Hooks exports
export {
  useReports,
  useReport,
  useGenerateReport,
  useReportDownload,
  useDeleteReport,
  useReportTemplates,
  useReportStats,
  useScheduleReport,
  useScheduledReports,
} from './hooks/useReports';

export const REPORTS_FEATURE = 'reports' as const;
