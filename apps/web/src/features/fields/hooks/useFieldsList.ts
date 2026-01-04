/**
 * SAHOOL Fields List Hook
 * خطاف قائمة الحقول
 */

import { useQuery } from '@tanstack/react-query';
import type { FieldFilters } from '../types';
import { fieldsApi } from '../api';
import { fieldKeys } from './queryKeys';

/**
 * Hook to fetch all fields with optional filters
 * خطاف لجلب جميع الحقول مع تصفية اختيارية
 */
export function useFieldsList(filters?: FieldFilters) {
  return useQuery({
    queryKey: fieldKeys.list(filters),
    queryFn: () => fieldsApi.getFields(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 1, // Retry once before falling back to mock data
  });
}

// Re-export for backward compatibility
export { useFieldsList as useFields };
