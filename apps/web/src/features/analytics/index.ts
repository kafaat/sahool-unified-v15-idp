/**
 * Analytics Feature
 * ميزة التحليلات والتقارير
 *
 * This feature handles:
 * - Yield analysis and reporting
 * - Cost breakdown and analysis
 * - Revenue and profit tracking
 * - Field/Season comparisons
 * - KPI metrics
 * - Report generation (PDF, Excel, CSV)
 */

// Component exports
// Chart components use dynamic imports to avoid bundling recharts (~120KB) on initial load
export { AnalyticsDashboard } from "./components/AnalyticsDashboard";
export { YieldAnalysis } from "./components/YieldAnalysis.dynamic";
export { YieldChart } from "./components/YieldChart.dynamic";
export { CostAnalysis } from "./components/CostAnalysis.dynamic";
export { ComparisonChart } from "./components/ComparisonChart.dynamic";
export { ReportGenerator } from "./components/ReportGenerator";
export { KPICards } from "./components/KPICards";

// API exports
export {
  analyticsApi,
  ERROR_MESSAGES as ANALYTICS_ERROR_MESSAGES,
} from "./api";

// Hook exports
export {
  useAnalyticsSummary,
  useYieldAnalysis,
  useCostAnalysis,
  useRevenueAnalysis,
  useKPIMetrics,
  useComparison,
  useResourceUsage,
  useGenerateReport,
  useDownloadReport,
} from "./hooks/useAnalytics";

// Type exports
export type {
  AnalyticsPeriod,
  MetricType,
  ChartType,
  ComparisonType,
  DataPoint,
  YieldData,
  CostData,
  CostBreakdown,
  RevenueData,
  KPIMetric,
  ComparisonData,
  ComparisonItem,
  ReportConfig,
  ReportSection,
  ReportSectionType,
  AnalyticsFilters,
  AnalyticsSummary,
  ResourceUsage,
} from "./types";

export const ANALYTICS_FEATURE = "analytics" as const;
