/**
 * SAHOOL Chart Colors
 * الوان الرسوم البيانية
 *
 * Centralized chart color constants derived from the design system tokens.
 * Import these instead of hardcoding hex values in components.
 */

import { lightTheme } from '@sahool/design-system';

// ---------------------------------------------------------------------------
// NDVI Colors - مؤشر الغطاء النباتي
// Used for field map polygons, NDVI charts, and vegetation health indicators
// ---------------------------------------------------------------------------

export const NDVI_COLORS = {
  /** High vegetation (0.7-1.0) - ممتاز */
  high: lightTheme.agricultural.ndvi.high,
  /** Medium-high vegetation (0.5-0.7) - جيد */
  mediumHigh: lightTheme.agricultural.ndvi.mediumHigh,
  /** Medium vegetation (0.3-0.5) - متوسط */
  medium: lightTheme.agricultural.ndvi.medium,
  /** Low vegetation (0.1-0.3) - ضعيف */
  low: lightTheme.agricultural.ndvi.low,
  /** Bare soil / no vegetation (0-0.1) - تربة عارية */
  bare: lightTheme.agricultural.ndvi.bare,
  /** Water / negative values - ماء */
  water: lightTheme.agricultural.ndvi.water,
  /** No data available - لا توجد بيانات */
  noData: lightTheme.colors.neutral[400],
} as const;

/** Ordered NDVI gradient from water to high vegetation */
export const NDVI_GRADIENT = [
  NDVI_COLORS.water,
  NDVI_COLORS.bare,
  NDVI_COLORS.low,
  NDVI_COLORS.medium,
  NDVI_COLORS.mediumHigh,
  NDVI_COLORS.high,
] as const;

// ---------------------------------------------------------------------------
// Crop Health Colors - صحة المحصول
// Used for crop health dashboards, alerts, and status badges
// ---------------------------------------------------------------------------

export const CROP_HEALTH_COLORS = {
  /** Excellent health (80-100) - ممتاز */
  excellent: lightTheme.agricultural.cropHealth.excellent,
  /** Good health (60-80) - جيد */
  good: lightTheme.agricultural.cropHealth.good,
  /** Moderate health (40-60) - معتدل */
  moderate: lightTheme.agricultural.cropHealth.moderate,
  /** Stressed (20-40) - مجهد */
  stressed: lightTheme.agricultural.cropHealth.stressed,
  /** Critical (0-20) - حرج */
  critical: lightTheme.agricultural.cropHealth.critical,
} as const;

// ---------------------------------------------------------------------------
// Financial Chart Colors - الوان الرسوم المالية
// Used for revenue charts, cost breakdowns, and ROI visualizations
// ---------------------------------------------------------------------------

export const FINANCIAL_COLORS = {
  /** Revenue / income - الإيرادات */
  revenue: lightTheme.colors.primary[600],
  /** Costs / expenses - التكاليف */
  costs: lightTheme.colors.error.main,
  /** Profit / savings - الأرباح */
  profit: lightTheme.colors.success.main,
  /** Budget / planned - الميزانية */
  budget: lightTheme.colors.secondary[500],
  /** Forecast / projected - التوقعات */
  forecast: lightTheme.colors.accent[500],
  /** Neutral / baseline - خط الأساس */
  baseline: lightTheme.colors.neutral[400],
} as const;

// ---------------------------------------------------------------------------
// Weather Chart Colors - الوان الرسوم الجوية
// Used for weather dashboards, forecasts, and climate visualizations
// ---------------------------------------------------------------------------

export const WEATHER_COLORS = {
  /** Sunny / clear - مشمس */
  sunny: lightTheme.agricultural.weather.sunny,
  /** Cloudy - غائم */
  cloudy: lightTheme.agricultural.weather.cloudy,
  /** Rainy - ممطر */
  rainy: lightTheme.agricultural.weather.rainy,
  /** Stormy - عاصف */
  stormy: lightTheme.agricultural.weather.stormy,
  /** Frost - صقيع */
  frost: lightTheme.agricultural.weather.frost,
  /** Heat - حرارة */
  heat: lightTheme.agricultural.weather.heat,
} as const;

// ---------------------------------------------------------------------------
// Moisture Colors - الوان الرطوبة
// Used for soil moisture maps and irrigation charts
// ---------------------------------------------------------------------------

export const MOISTURE_COLORS = {
  /** Saturated - مشبع */
  saturated: lightTheme.agricultural.moisture.saturated,
  /** Optimal - مثالي */
  optimal: lightTheme.agricultural.moisture.optimal,
  /** Adequate - كاف */
  adequate: lightTheme.agricultural.moisture.adequate,
  /** Dry - جاف */
  dry: lightTheme.agricultural.moisture.dry,
  /** Critical - حرج */
  critical: lightTheme.agricultural.moisture.critical,
} as const;

// ---------------------------------------------------------------------------
// Selection / Interaction Colors - الوان التفاعل
// Used for selected states, highlights, and borders on interactive elements
// ---------------------------------------------------------------------------

export const INTERACTION_COLORS = {
  /** Selected field border - حدود الحقل المحدد */
  selectedBorder: lightTheme.colors.secondary[800],
  /** Circle marker border */
  markerBorder: lightTheme.colors.neutral[0],
} as const;
