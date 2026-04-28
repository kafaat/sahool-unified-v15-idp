/**
 * NDVI & Vegetation Indices Feature
 * ميزة مؤشرات NDVI والغطاء النباتي
 *
 * This feature handles:
 * - All 41 vegetation indices (NDVI, EVI, NDRE, SAVI, etc.)
 * - Time series analysis for any index
 * - Health status monitoring with bilingual interpretation
 * - Regional statistics
 * - Index interpretation with recommendations
 */

// Types & Configuration (41 indices)
export {
  VegetationIndex,
  INDEX_CONFIGS,
  INDEX_CATEGORIES,
  getIndicesByCategory,
  getAllCategories,
} from './types';
export type {
  IndexCategory,
  IndexCategoryInfo,
  VegetationIndexConfig,
  IndexValue,
  IndicesResult,
  SingleIndexResult,
  IndicesInterpretation,
  IndexTimeSeriesPoint,
  IndexTimeSeries,
} from './types';

// API
export { ndviApi, vegetationIndicesApi } from './api';
export type { NDVIData, NDVITimeSeries, NDVIMapData, NDVIFilters } from './api';

// Hooks - NDVI (legacy, still supported)
export {
  useLatestNDVI,
  useFieldNDVI,
  useNDVITimeSeries,
  useNDVIMap,
  useRegionalNDVIStats,
  useRequestNDVIAnalysis,
  useNDVIComparison,
  ndviKeys,
} from './hooks/useNDVI';

// Hooks - Vegetation Indices (all 41 indices)
export {
  useFieldIndices,
  useSpecificIndex,
  useInterpretIndices,
  useIndexTimeSeries,
  indicesKeys,
} from './hooks/useNDVI';

// Phase 2 — Agronomic Intelligence Layer
// Per-index semantics (critical: NDVI ≠ NDWI ≠ LAI)
export {
  INDEX_SEMANTICS,
  MAP_SUPPORTED_INDICES,
  getIndexSemantics,
  getHealthZone,
  interpolateColor,
} from './index-semantics';
export type { IndexSemantics, HealthZone, ColorStop } from './index-semantics';

// Phase 2 — Unified raster + cloud + phenology hook
export {
  useIndexMap,
  indexMapKeys,
} from './hooks/useIndexMap';
export type {
  IndexMapData,
  CalendarDate,
  IndexCalendar,
  PhenologyStage,
  UseIndexMapOptions,
  UseIndexMapResult,
} from './hooks/useIndexMap';

