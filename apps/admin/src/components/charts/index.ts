/**
 * Charts Export
 * تصدير مكونات الرسوم البيانية
 *
 * Default exports use dynamic (lazy-loaded) versions to avoid bundling recharts (~120KB) on initial load.
 * Import from ./LazyRecharts for individual recharts components with code splitting.
 * Import from ./AnalyticsChart directly ONLY when you need the raw (non-dynamic) version.
 */

// Default export: dynamic version (recommended for pages and layouts)
export { default as AnalyticsChart } from './AnalyticsChart.dynamic';
export { default as AnalyticsChartDynamic } from './AnalyticsChart.dynamic';

// SparklineChart also dynamically loaded to prevent recharts leaking into initial bundle
export { SparklineChart } from './SparklineChart.dynamic';

export type { ChartType, ChartDataPoint, ChartSeries } from './AnalyticsChart';
