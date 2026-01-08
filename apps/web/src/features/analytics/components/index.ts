/**
 * Analytics Components - Main Index
 * مكونات التحليلات - الفهرس الرئيسي
 *
 * This file exports the dynamic (code-split) versions of heavy chart components by default.
 * يقوم هذا الملف بتصدير الإصدارات الديناميكية (المقسمة) من مكونات الرسوم البيانية الثقيلة بشكل افتراضي.
 */

// Export dynamic (lazy-loaded) components by default for optimal bundle size
// تصدير المكونات الديناميكية (التحميل الكسول) بشكل افتراضي لحجم حزمة أمثل
export { YieldChart } from './YieldChart.dynamic';
export { ComparisonChart } from './ComparisonChart.dynamic';
export { YieldAnalysis } from './YieldAnalysis.dynamic';
export { CostAnalysis } from './CostAnalysis.dynamic';

// Export non-chart components normally (lightweight, no code splitting needed)
// تصدير المكونات غير الرسومية بشكل عادي (خفيفة الوزن، لا حاجة لتقسيم الكود)
export { KPICards } from './KPICards';
export { ReportGenerator } from './ReportGenerator';
export { AnalyticsDashboard } from './AnalyticsDashboard';

// Re-export types
export type { DataPoint, ChartType, AnalyticsFilters, ComparisonType, MetricType } from '../types';
