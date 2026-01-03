/**
 * SAHOOL Fields Hook
 * خطاف الحقول
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { FieldFormData, FieldFilters } from '../types';
import { fieldsApi } from '../api';
import { logger } from '@/lib/logger';

// Query Keys
export const fieldKeys = {
  all: ['fields'] as const,
  lists: () => [...fieldKeys.all, 'list'] as const,
  list: (filters?: FieldFilters) => [...fieldKeys.lists(), filters] as const,
  detail: (id: string) => [...fieldKeys.all, 'detail', id] as const,
  stats: (farmId?: string) => [...fieldKeys.all, 'stats', farmId] as const,
};

/**
 * Hook to fetch all fields with optional filters
 * خطاف لجلب جميع الحقول مع تصفية اختيارية
 */
export function useFields(filters?: FieldFilters) {
  return useQuery({
    queryKey: fieldKeys.list(filters),
    queryFn: () => fieldsApi.getFields(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 1, // Retry once before falling back to mock data
  });
}

/**
 * Hook to fetch a single field by ID
 * خطاف لجلب حقل واحد بواسطة المعرف
 */
export function useField(id: string) {
  return useQuery({
    queryKey: fieldKeys.detail(id),
    queryFn: () => fieldsApi.getFieldById(id),
    enabled: !!id,
    staleTime: 2 * 60 * 1000,
    retry: 1,
  });
}

/**
 * Hook to fetch field statistics
 * خطاف لجلب إحصائيات الحقول
 */
export function useFieldStats(farmId?: string) {
  return useQuery({
    queryKey: fieldKeys.stats(farmId),
    queryFn: () => fieldsApi.getStats(farmId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });
}

/**
 * Hook to create a new field
 * خطاف لإنشاء حقل جديد
 */
export function useCreateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ data, tenantId }: { data: FieldFormData; tenantId?: string }) =>
      fieldsApi.createField(data, tenantId),
    onSuccess: () => {
      // Invalidate all field queries to refetch
      queryClient.invalidateQueries({ queryKey: fieldKeys.lists() });
      queryClient.invalidateQueries({ queryKey: fieldKeys.stats() });
    },
    onError: (error: Error) => {
      // Parse error message
      try {
        const errorData = JSON.parse(error.message);
        logger.error('Create field error:', errorData.messageAr || errorData.message);
      } catch {
        logger.error('Create field error:', error.message);
      }
    },
  });
}

/**
 * Hook to update an existing field
 * خطاف لتحديث حقل موجود
 */
export function useUpdateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
      tenantId
    }: {
      id: string;
      data: Partial<FieldFormData>;
      tenantId?: string;
    }) => fieldsApi.updateField(id, data, tenantId),
    onSuccess: (updatedField, variables) => {
      // Update cache with new data
      queryClient.setQueryData(fieldKeys.detail(variables.id), updatedField);

      // Invalidate lists to refetch
      queryClient.invalidateQueries({ queryKey: fieldKeys.lists() });
      queryClient.invalidateQueries({ queryKey: fieldKeys.stats() });
    },
    onError: (error: Error) => {
      // Parse error message
      try {
        const errorData = JSON.parse(error.message);
        logger.error('Update field error:', errorData.messageAr || errorData.message);
      } catch {
        logger.error('Update field error:', error.message);
      }
    },
  });
}

/**
 * Hook to delete a field
 * خطاف لحذف حقل
 */
export function useDeleteField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => fieldsApi.deleteField(id),
    onSuccess: (_: void, id: string) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: fieldKeys.detail(id) });

      // Invalidate lists to refetch
      queryClient.invalidateQueries({ queryKey: fieldKeys.lists() });
      queryClient.invalidateQueries({ queryKey: fieldKeys.stats() });
    },
    onError: (error: Error) => {
      // Parse error message
      try {
        const errorData = JSON.parse(error.message);
        logger.error('Delete field error:', errorData.messageAr || errorData.message);
      } catch {
        logger.error('Delete field error:', error.message);
      }
    },
  });
}
