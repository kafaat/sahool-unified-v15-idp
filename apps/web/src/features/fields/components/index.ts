/**
 * Fields Components
 * مكونات الحقول
 */

export { FieldCard } from "./FieldCard";
export { FieldDetails } from "./FieldDetails";
export { FieldForm } from "./FieldForm";
// Export dynamic (lazy-loaded) FieldMap component by default for optimal bundle size (~50KB saved)
export { FieldMap } from "./FieldMap.dynamic";
export { FieldsList } from "./FieldsList";
// Export dynamic (lazy-loaded) map component by default for optimal bundle size (~150KB saved)
export { InteractiveFieldMap } from "./InteractiveFieldMap.dynamic";
// Re-export types from the original component
export type {
  InteractiveFieldMapProps,
  HealthZone,
  MapTask,
  LayerConfig,
} from "./InteractiveFieldMap";
export {
  NdviTileLayer,
  NdviColorLegend,
  NdviLoadingOverlay,
  type NdviTileLayerProps,
} from "./NdviTileLayer";
export { WeatherOverlay, type WeatherOverlayProps } from "./WeatherOverlay";
export {
  LayerControl,
  useLayerControl,
  type LayerControlProps,
  type LayerSettings,
  type NDVISettings,
  type LayerControlState,
} from "./LayerControl";
