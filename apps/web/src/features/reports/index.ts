/**
 * Reports Feature
 * ميزة التقارير
 *
 * This feature handles:
 * - Field performance reports
 * - Season summary reports
 * - NDVI analysis reports
 * - Scouting reports
 * - Export to PDF/Excel with Arabic RTL support
 */

// API exports
export { reportsApi } from "./api";
export { reportsApi as fieldReportsApi } from "./api/reports-api";
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
} from "./api";

// Extended types exports
export type {
  ReportSection,
  FieldReportOptions,
  FieldReportData,
  SeasonReportOptions,
  SeasonReportData,
  GeneratedReport,
  ReportHistoryItem,
  ReportHistoryFilters,
  GenerateFieldReportRequest,
  GenerateSeasonReportRequest,
  ShareReportRequest,
  ShareReportResponse,
  DownloadReportResponse,
  PDFGenerationOptions,
  PDFChartConfig,
  BilingualMessage,
  ReportErrorMessages,
} from "./types/reports";

// Hooks exports
export {
  // Legacy hooks
  useReports,
  useReport,
  useGenerateReport,
  useReportDownload,
  useDeleteReport,
  useReportTemplates,
  useReportStats,
  useScheduleReport,
  useScheduledReports,
  // Extended field report hooks
  useGenerateFieldReport,
  useGenerateSeasonReport,
  useReportHistory,
  useDownloadReport,
  useShareReport,
  useDeleteFieldReport,
  useFieldReportData,
  useSeasonReportData,
  useReportStatus,
  useFieldReportTemplates,
} from "./hooks/useReports";

// Component exports
export { ReportGenerator } from "./components/ReportGenerator";
export { ReportPreview } from "./components/ReportPreview";
export { FieldReportTemplate } from "./components/FieldReportTemplate";
export { ReportHistory } from "./components/ReportHistory";

// Utility exports
export {
  formatDateForPDF,
  formatNumberForPDF,
  formatCurrencyForPDF,
  formatArea,
  getSectionTitle,
  orderSections,
  generateFieldReportHTML,
  generateSeasonReportHTML,
  downloadPDF,
  generateShareLink,
  generateEmailShareContent,
  containsArabic,
  formatRTLText,
  getTextDirection,
  chartToBase64,
  generateChartConfig,
  DEFAULT_PDF_OPTIONS,
} from "./utils/pdf-generator";

export const REPORTS_FEATURE = "reports" as const;
