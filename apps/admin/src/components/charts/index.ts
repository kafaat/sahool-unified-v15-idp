/**
 * Charts Export
 * تصدير مكونات الرسوم البيانية
 *
 * Always prefer importing the dynamic version for production bundles.
 * Import from ./LazyRecharts for individual recharts components with code splitting.
 */

export { default as AnalyticsChart, SparklineChart } from "./AnalyticsChart";
export { default as AnalyticsChartDynamic } from "./AnalyticsChart.dynamic";
export type { ChartType, ChartDataPoint, ChartSeries } from "./AnalyticsChart";
