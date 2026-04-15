/**
 * IoT Components - Main Index
 * مكونات إنترنت الأشياء - الفهرس الرئيسي
 *
 * This file exports the dynamic (code-split) versions of heavy chart components by default.
 * يقوم هذا الملف بتصدير الإصدارات الديناميكية (المقسمة) من مكونات الرسوم البيانية الثقيلة بشكل افتراضي.
 */

// Export dynamic (lazy-loaded) components by default for optimal bundle size
// تصدير المكونات الديناميكية (التحميل الكسول) بشكل افتراضي لحجم حزمة أمثل
export { SensorChart } from './SensorChart.dynamic';
export { SensorReadings } from './SensorReadings.dynamic';

// Re-export types
export type { SensorReading, Sensor, SensorFilters, SensorReadingsQuery } from '../types';
