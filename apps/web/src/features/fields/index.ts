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

// ═══════════════════════════════════════════════════════════════════════════
// API
// ═══════════════════════════════════════════════════════════════════════════

export { fieldsApi, ERROR_MESSAGES } from './api';

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
