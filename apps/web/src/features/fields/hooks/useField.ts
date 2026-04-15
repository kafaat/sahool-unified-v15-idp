/**
 * SAHOOL Single Field Hook
 * خطاف الحقل الفردي
 */

import { useQuery } from '@tanstack/react-query';
import { fieldsApi } from '../api';
import { fieldKeys } from './queryKeys';

/**
 * Hook to fetch a single field by ID
 * خطاف لجلب حقل واحد بواسطة المعرف
 */
export function useField(id: string) {
  return useQuery({
    queryKey: fieldKeys.detail(id),
    queryFn: () => fieldsApi.getFieldById(id),
    enabled: !!id,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 1,
  });
}
