/**
 * SAHOOL Field Mutations Hook
 * خطاف عمليات التعديل في الحقول
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { FieldFormData } from '../types';
import { fieldsApi, triggerVegetationAnalysis } from '../api';
import { logger } from '@/lib/logger';
import { fieldKeys } from './queryKeys';

/**
 * Hook to create a new field
 * خطاف لإنشاء حقل جديد
 */
export function useCreateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ data, tenantId }: { data: FieldFormData; tenantId?: string }) =>
      fieldsApi.createField(data, tenantId),
    onSuccess: (createdField) => {
      // Invalidate all field queries to refetch
      queryClient.invalidateQueries({ queryKey: fieldKeys.lists() });
      queryClient.invalidateQueries({ queryKey: fieldKeys.stats() });
      // Auto-trigger satellite analysis when a boundary was drawn (fire-and-forget)
      if (createdField.polygon) {
        triggerVegetationAnalysis(createdField.id, createdField.polygon).catch(() => {});
      }
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
      tenantId,
    }: {
      id: string;
      data: Partial<FieldFormData>;
      tenantId?: string;
    }) => fieldsApi.updateField(id, data, tenantId),
    onMutate: async ({ id, data }) => {
      // Cancel any outgoing refetches to avoid overwriting optimistic update
      await queryClient.cancelQueries({ queryKey: fieldKeys.detail(id) });
      await queryClient.cancelQueries({ queryKey: fieldKeys.lists() });

      // Snapshot the previous value for rollback
      const previousField = queryClient.getQueryData(fieldKeys.detail(id));

      // Optimistically update the cache
      queryClient.setQueryData(fieldKeys.detail(id), (old: any) => {
        if (!old) return old;
        return { ...old, ...data };
      });

      return { previousField, id };
    },
    onSuccess: (updatedField, variables) => {
      // Replace optimistic cache entry with server-confirmed data
      queryClient.setQueryData(fieldKeys.detail(variables.id), updatedField);
      queryClient.invalidateQueries({ queryKey: fieldKeys.lists() });
      queryClient.invalidateQueries({ queryKey: fieldKeys.stats() });
    },
    onError: (error: Error, _variables, context) => {
      // Rollback to the previous value on error
      if (context?.previousField !== undefined) {
        queryClient.setQueryData(fieldKeys.detail(context.id), context.previousField);
      }
      try {
        const errorData = JSON.parse(error.message);
        logger.error('Update field error:', errorData.messageAr || errorData.message);
      } catch {
        logger.error('Update field error:', error.message);
      }
    },
    onSettled: (_data, _error, variables) => {
      // Always refetch after error or success to sync with server
      queryClient.invalidateQueries({ queryKey: fieldKeys.detail(variables.id) });
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

/**
 * Hook for all field mutations
 * Provides methods to create, update, and delete fields
 */
export function useFieldMutations() {
  const createField = useCreateField();
  const updateField = useUpdateField();
  const deleteField = useDeleteField();

  return {
    createField,
    updateField,
    deleteField,
    isLoading: createField.isPending || updateField.isPending || deleteField.isPending,
  };
}
