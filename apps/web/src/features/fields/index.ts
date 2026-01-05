/**
 * SAHOOL Fields Feature Exports
 * صادرات ميزة الحقول
 */

// ═══════════════════════════════════════════════════════════════════════════
// Components
// ═══════════════════════════════════════════════════════════════════════════

export { FieldsList } from './components/FieldsList';
export { FieldCard } from './components/FieldCard';
export { FieldDetails } from './components/FieldDetails';
export { FieldForm } from './components/FieldForm';
export { FieldMap } from './components/FieldMap';
export { TaskMarkers } from './components/TaskMarkers';
export { FieldMapWithTasks } from './components/FieldMapWithTasks';
export { AstralFieldWidget } from './components/AstralFieldWidget';
export { HealthZonesLayer } from './components/HealthZonesLayer';
export type { FieldZone } from './components/HealthZonesLayer';
export { WeatherOverlay } from './components/WeatherOverlay';
export type { WeatherOverlayProps } from './components/WeatherOverlay';
export { LivingFieldCard } from './components/LivingFieldCard';

// ═══════════════════════════════════════════════════════════════════════════
// Hooks
// ═══════════════════════════════════════════════════════════════════════════

export { useFields, useFieldsList } from './hooks/useFieldsList';
export { useField } from './hooks/useField';
export { useFieldStats } from './hooks/useFieldStats';
export {
  useCreateField,
  useUpdateField,
  useDeleteField,
  useFieldMutations,
} from './hooks/useFieldMutations';
export { fieldKeys } from './hooks/queryKeys';
export { useLivingFieldScore } from './hooks/useLivingFieldScore';
export type {
  LivingFieldScore,
  FieldAlert,
  Recommendation,
} from './hooks/useLivingFieldScore';
export {
  useFieldZones,
  useFieldAlerts,
  useBestDays,
  useValidateDate,
  useFieldRecommendations,
  useCreateTaskFromAlert,
  useFieldIntelligence,
  useDebouncedDateValidation,
  fieldIntelligenceKeys,
} from './hooks/useFieldIntelligence';
export type {
  BestDaysOptions,
  HookOptions,
} from './hooks/useFieldIntelligence';

// ═══════════════════════════════════════════════════════════════════════════
// API
// ═══════════════════════════════════════════════════════════════════════════

export { fieldsApi, ERROR_MESSAGES } from './api';

// ═══════════════════════════════════════════════════════════════════════════
// Field Intelligence API
// ═══════════════════════════════════════════════════════════════════════════

export {
  fetchLivingFieldScore,
  fetchFieldZones,
  fetchFieldAlerts,
  createTaskFromAlert,
  fetchBestDays,
  validateTaskDate,
  fetchFieldRecommendations,
  fieldIntelligenceKeys as intelligenceQueryKeys,
  INTELLIGENCE_ERROR_MESSAGES,
} from './api/field-intelligence-api';

export type {
  LivingFieldScore as ApiLivingFieldScore,
  FieldZone as ApiFieldZone,
  FieldAlert as ApiFieldAlert,
  TaskFromAlertData,
  CreatedTask,
  BestDay,
  DateValidation as ApiDateValidation,
  FieldRecommendation,
} from './api/field-intelligence-api';

// ═══════════════════════════════════════════════════════════════════════════
// Types - Core
// ═══════════════════════════════════════════════════════════════════════════

export type {
  Field,
  FieldFormData,
  FieldFilters,
  FieldStats,
  FieldStatus,
  IrrigationType,
  SoilType,
} from './types';

// ═══════════════════════════════════════════════════════════════════════════
// Types - GeoJSON
// ═══════════════════════════════════════════════════════════════════════════

export type {
  GeoPolygon,
  GeoPoint,
} from './types';

// ═══════════════════════════════════════════════════════════════════════════
// Types - UI & View
// ═══════════════════════════════════════════════════════════════════════════

export type {
  FieldViewMode,
  FieldViewSettings,
} from './types';

// ═══════════════════════════════════════════════════════════════════════════
// Types - API & Responses
// ═══════════════════════════════════════════════════════════════════════════

export type {
  FieldError,
  ApiFieldResponse,
  ApiFieldsListResponse,
  ApiFieldStatsResponse,
} from './types';

// ═══════════════════════════════════════════════════════════════════════════
// Types - Mutation Payloads
// ═══════════════════════════════════════════════════════════════════════════

export type {
  CreateFieldPayload,
  UpdateFieldPayload,
  DeleteFieldPayload,
} from './types';

// ═══════════════════════════════════════════════════════════════════════════
// Types - Hook Returns
// ═══════════════════════════════════════════════════════════════════════════

export type {
  UseFieldsReturn,
  UseFieldReturn,
  UseFieldStatsReturn,
} from './types';
