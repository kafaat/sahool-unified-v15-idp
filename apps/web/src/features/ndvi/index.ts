/**
 * NDVI Feature
 * ميزة مؤشر الغطاء النباتي
 *
 * This feature handles:
 * - NDVI data visualization
 * - Time series analysis
 * - Health status monitoring
 * - Regional statistics
 */

// API
export { ndviApi } from "./api";
export type { NDVIData, NDVITimeSeries, NDVIMapData, NDVIFilters } from "./api";

// Hooks
export {
  useLatestNDVI,
  useFieldNDVI,
  useNDVITimeSeries,
  useNDVIMap,
  useRegionalNDVIStats,
  useRequestNDVIAnalysis,
  useNDVIComparison,
  ndviKeys,
} from "./hooks/useNDVI";
