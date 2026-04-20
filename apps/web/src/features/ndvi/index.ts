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
export type {
  NDVIData,
  NDVITimeSeries,
  NDVIMapData,
  NDVIFilters,
  IndexMapData,
  PixelInspection,
  IndexStatus,
  CompositeWindow,
  IndexComposite,
  FilmstripFrame,
  IndexFilmstrip,
  MultiDateCompareRow,
  MultiDateCompare,
  MultiDateCompareRequest,
} from './api';

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
  useIndexMap,
  usePixelInspection,
  useIndexComposite,
  useIndexFilmstrip,
  useMultiDateCompare,
  indicesKeys,
} from './hooks/useNDVI';

// Map visualization components (Phase 1 + 2)
export { IndexPicker, MAPPABLE_INDICES } from './components/IndexPicker';
export type { IndexPickerProps } from './components/IndexPicker';
export { PixelInspectorPopup } from './components/PixelInspectorPopup';
export type { PixelInspectorPopupProps } from './components/PixelInspectorPopup';
export { IndexTimeSlider } from './components/IndexTimeSlider';
export type { IndexTimeSliderProps } from './components/IndexTimeSlider';

// Multi-date components (Phase 3)
export {
  IntervalStepSelector,
  INTERVAL_PRESETS,
} from './components/IntervalStepSelector';
export type {
  IntervalStepSelectorProps,
  IntervalDays,
} from './components/IntervalStepSelector';
export { IndexFilmstrip } from './components/IndexFilmstrip';
export type { IndexFilmstripProps } from './components/IndexFilmstrip';
export {
  MultiDateSplitScreen,
  PANEL_COUNTS,
} from './components/MultiDateSplitScreen';
export type {
  MultiDateSplitScreenProps,
  PanelCount,
} from './components/MultiDateSplitScreen';
