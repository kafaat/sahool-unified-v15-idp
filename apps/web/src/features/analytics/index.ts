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
export { AnalyticsDashboard } from './components/AnalyticsDashboard';
export { YieldAnalysis } from './components/YieldAnalysis';
export { YieldChart } from './components/YieldChart';
export { CostAnalysis } from './components/CostAnalysis';
export { ComparisonChart } from './components/ComparisonChart';
export { ReportGenerator } from './components/ReportGenerator';
export { KPICards } from './components/KPICards';

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
} from './hooks/useAnalytics';

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
} from './types';

export const ANALYTICS_FEATURE = 'analytics' as const;
