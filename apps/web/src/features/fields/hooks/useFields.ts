/**
 * SAHOOL Fields Hooks - Legacy Entry Point
 * خطافات الحقول - نقطة الدخول القديمة
 *
 * @deprecated This file is kept for backward compatibility.
 * Please import from individual hook files instead:
 * - useFieldsList.ts for useFields
 * - useField.ts for useField
 * - useFieldStats.ts for useFieldStats
 * - useFieldMutations.ts for mutations
 * - queryKeys.ts for fieldKeys
 */

// Re-export all hooks from their new locations for backward compatibility
export { useFields, useFieldsList } from './useFieldsList';
export { useField } from './useField';
export { useFieldStats } from './useFieldStats';
export {
  useCreateField,
  useUpdateField,
  useDeleteField,
  useFieldMutations,
} from './useFieldMutations';
export { fieldKeys } from './queryKeys';
