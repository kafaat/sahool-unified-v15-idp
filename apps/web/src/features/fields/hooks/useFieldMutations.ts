/**
 * SAHOOL Field Mutations Hook
 * خطاف عمليات التعديل في الحقول
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { FieldFormData } from "../types";
import { fieldsApi } from "../api";
import { logger } from "@/lib/logger";
import { fieldKeys } from "./queryKeys";

/**
 * Hook to create a new field
 * خطاف لإنشاء حقل جديد
 */
export function useCreateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      data,
      tenantId,
    }: {
      data: FieldFormData;
      tenantId?: string;
    }) => fieldsApi.createField(data, tenantId),
    onSuccess: () => {
      // Invalidate all field queries to refetch
      queryClient.invalidateQueries({ queryKey: fieldKeys.lists() });
      queryClient.invalidateQueries({ queryKey: fieldKeys.stats() });
    },
    onError: (error: Error) => {
      // Parse error message
      try {
        const errorData = JSON.parse(error.message);
        logger.error(
          "Create field error:",
          errorData.messageAr || errorData.message,
        );
      } catch {
        logger.error("Create field error:", error.message);
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
        logger.error(
          "Update field error:",
          errorData.messageAr || errorData.message,
        );
      } catch {
        logger.error("Update field error:", error.message);
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
        logger.error(
          "Delete field error:",
          errorData.messageAr || errorData.message,
        );
      } catch {
        logger.error("Delete field error:", error.message);
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
    isLoading:
      createField.isPending || updateField.isPending || deleteField.isPending,
  };
}
