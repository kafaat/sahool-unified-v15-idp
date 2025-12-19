/**
 * Field Map Feature
 * ميزة خريطة الحقول
 *
 * This feature handles:
 * - Field visualization on map
 * - Field CRUD operations
 * - Field filtering and search
 * - Field statistics
 */

// API
export { fieldMapApi } from './api';
export type { Field, FieldCreate, FieldUpdate, FieldFilters } from './api';

// Hooks
export {
  useFields,
  useField,
  useFieldsGeoJSON,
  useFieldStats,
  useCreateField,
  useUpdateField,
  useDeleteField,
  fieldKeys,
} from './hooks/useFields';

// Components (to be added)
// export { FieldMap } from './components/FieldMap';
// export { FieldList } from './components/FieldList';
// export { FieldDetails } from './components/FieldDetails';
