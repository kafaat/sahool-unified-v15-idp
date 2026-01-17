/**
 * SAHOOL VRA (Variable Rate Application) Hooks
 * خطافات التطبيق المتغير المعدل
 *
 * React Query hooks for VRA prescription maps and variable rate application features.
 */

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { logger } from "@/lib/logger";
import {
  generatePrescription,
  getPrescriptionHistory,
  getPrescriptionDetails,
  exportPrescription,
  deletePrescription,
  vraKeys,
} from "../api/vra-api";
import type {
  PrescriptionRequest,
  PrescriptionResponse,
  PrescriptionHistoryResponse,
  ExportFormat,
} from "../types/vra";

// ═══════════════════════════════════════════════════════════════════════════
// Re-export Types for Convenience
// ═══════════════════════════════════════════════════════════════════════════

export type {
  PrescriptionRequest,
  PrescriptionResponse,
  PrescriptionHistoryResponse,
  ExportFormat,
};

// ═══════════════════════════════════════════════════════════════════════════
// Hook Options Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook options with enabled flag
 * خيارات الخطاف مع علامة التفعيل
 */
export interface HookOptions {
  enabled?: boolean;
}

/**
 * History query options
 * خيارات استعلام السجل
 */
export interface HistoryOptions extends HookOptions {
  limit?: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Re-export Query Keys
// ═══════════════════════════════════════════════════════════════════════════

export { vraKeys };

// ═══════════════════════════════════════════════════════════════════════════
// Query Hooks - خطافات الاستعلام
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch prescription history for a field
 * خطاف لجلب سجل الوصفات للحقل
 *
 * Retrieves all VRA prescriptions for a specific field, sorted by creation date.
 *
 * @param fieldId - Field ID
 * @param options - Query options including limit
 * @returns Query result with prescription history
 */
export function usePrescriptionHistory(
  fieldId: string,
  options?: HistoryOptions,
) {
  const { enabled = true, limit = 10 } = options || {};

  return useQuery({
    queryKey: vraKeys.history(fieldId),
    queryFn: async () => {
      const response = await getPrescriptionHistory(fieldId, limit);
      if (!response.success) {
        throw new Error(
          response.error || "Failed to fetch prescription history",
        );
      }
      return response.data as PrescriptionHistoryResponse;
    },
    enabled: enabled && !!fieldId,
    staleTime: 2 * 60 * 1000, // 2 minutes - history changes occasionally
    retry: 2,
    retryDelay: 1000,
  });
}

/**
 * Hook to fetch prescription details by ID
 * خطاف لجلب تفاصيل الوصفة بالمعرف
 *
 * Retrieves detailed information about a specific prescription, including all zones.
 *
 * @param prescriptionId - Prescription ID
 * @param options - Hook options
 * @returns Query result with prescription details
 */
export function usePrescriptionDetails(
  prescriptionId: string,
  options?: HookOptions,
) {
  const { enabled = true } = options || {};

  return useQuery({
    queryKey: vraKeys.prescription(prescriptionId),
    queryFn: async () => {
      const response = await getPrescriptionDetails(prescriptionId);
      if (!response.success) {
        throw new Error(
          response.error || "Failed to fetch prescription details",
        );
      }
      return response.data as PrescriptionResponse;
    },
    enabled: enabled && !!prescriptionId,
    staleTime: 10 * 60 * 1000, // 10 minutes - prescription details are stable
    retry: 2,
    retryDelay: 1000,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Hooks - خطافات الطفرة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to generate VRA prescription map
 * خطاف لتوليد خريطة وصفة التطبيق المتغير
 *
 * Creates a variable rate application prescription map based on NDVI zones,
 * yield data, soil analysis, or combined factors.
 *
 * @returns Mutation result with prescription generation handler
 */
export function useGeneratePrescription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: PrescriptionRequest) => {
      const response = await generatePrescription(request);
      if (!response.success || !response.data) {
        throw new Error(response.error || "Failed to generate prescription");
      }
      return response.data;
    },
    onMutate: async (variables) => {
      logger.info(
        `Generating VRA prescription for field ${variables.fieldId}, type=${variables.vraType}`,
      );
    },
    onError: (error, variables) => {
      logger.error(
        `Failed to generate prescription for field ${variables.fieldId}:`,
        error,
      );
    },
    onSuccess: (prescription, variables) => {
      // Invalidate and refetch prescription history for this field
      queryClient.invalidateQueries({
        queryKey: vraKeys.history(variables.fieldId),
      });

      // Cache the new prescription details
      queryClient.setQueryData(
        vraKeys.prescription(prescription.id),
        prescription,
      );

      logger.info(
        `Prescription ${prescription.id} generated successfully for field ${variables.fieldId}, savings=${prescription.savingsPercent}%`,
      );
    },
    onSettled: () => {
      // Refetch all VRA-related queries
      queryClient.invalidateQueries({
        queryKey: vraKeys.all,
      });
    },
  });
}

/**
 * Hook to export prescription in various formats
 * خطاف لتصدير الوصفة بتنسيقات مختلفة
 *
 * Exports prescription in GeoJSON, CSV, Shapefile, or ISO-XML format.
 *
 * @returns Mutation result with export handler
 */
export function useExportPrescription() {
  return useMutation({
    mutationFn: async ({
      prescriptionId,
      format,
    }: {
      prescriptionId: string;
      format: ExportFormat;
    }) => {
      const response = await exportPrescription(prescriptionId, format);
      if (!response.success || !response.data) {
        throw new Error(response.error || "Failed to export prescription");
      }
      return response.data;
    },
    onMutate: async (variables) => {
      logger.info(
        `Exporting prescription ${variables.prescriptionId} as ${variables.format}`,
      );
    },
    onError: (error, variables) => {
      logger.error(
        `Failed to export prescription ${variables.prescriptionId} as ${variables.format}:`,
        error,
      );
    },
    onSuccess: (_data, variables) => {
      logger.info(
        `Prescription ${variables.prescriptionId} exported successfully as ${variables.format}`,
      );

      // For GeoJSON, CSV, and other downloadable formats, trigger download
      if (variables.format === "geojson" || variables.format === "csv") {
        // The component will handle the actual download
        // This is just for logging and potential side effects
      }
    },
  });
}

/**
 * Hook to delete prescription
 * خطاف لحذف الوصفة
 *
 * Deletes a prescription from the system.
 *
 * @returns Mutation result with delete handler
 */
export function useDeletePrescription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (prescriptionId: string) => {
      const response = await deletePrescription(prescriptionId);
      if (!response.success || !response.data) {
        throw new Error(response.error || "Failed to delete prescription");
      }
      return response.data;
    },
    onMutate: async (prescriptionId) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({
        queryKey: vraKeys.prescription(prescriptionId),
      });

      // Snapshot the previous value
      const previousPrescription = queryClient.getQueryData(
        vraKeys.prescription(prescriptionId),
      );

      logger.info(`Deleting prescription ${prescriptionId}`);

      // Return context with previous state for rollback
      return { previousPrescription, prescriptionId };
    },
    onError: (error, prescriptionId, context) => {
      // Rollback on error
      if (context?.previousPrescription) {
        queryClient.setQueryData(
          vraKeys.prescription(prescriptionId),
          context.previousPrescription,
        );
      }

      logger.error(`Failed to delete prescription ${prescriptionId}:`, error);
    },
    onSuccess: (_data, prescriptionId) => {
      // Remove prescription from cache
      queryClient.removeQueries({
        queryKey: vraKeys.prescription(prescriptionId),
      });

      // Invalidate history queries
      queryClient.invalidateQueries({
        queryKey: vraKeys.all,
      });

      logger.info(`Prescription ${prescriptionId} deleted successfully`);
    },
    onSettled: () => {
      // Refetch all VRA-related queries
      queryClient.invalidateQueries({
        queryKey: vraKeys.all,
      });
    },
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Composite Hooks - الخطافات المركبة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook that provides all VRA functionality for a field
 * خطاف يوفر جميع وظائف التطبيق المتغير للحقل
 *
 * Combines history query and all mutations into a single hook
 * for convenience when building VRA interfaces.
 *
 * @param fieldId - Field ID
 * @param options - Hook options
 * @returns Combined VRA functionality
 */
export function useVRA(fieldId: string, options?: HistoryOptions) {
  const { enabled = true, limit = 10 } = options || {};

  const history = usePrescriptionHistory(fieldId, { enabled, limit });
  const generateMutation = useGeneratePrescription();
  const exportMutation = useExportPrescription();
  const deleteMutation = useDeletePrescription();

  return {
    // History query
    history: {
      data: history.data,
      isLoading: history.isLoading,
      isError: history.isError,
      error: history.error,
      refetch: history.refetch,
    },

    // Generate prescription mutation
    generate: {
      mutate: generateMutation.mutate,
      mutateAsync: generateMutation.mutateAsync,
      isPending: generateMutation.isPending,
      isError: generateMutation.isError,
      error: generateMutation.error,
      isSuccess: generateMutation.isSuccess,
      data: generateMutation.data,
      reset: generateMutation.reset,
    },

    // Export prescription mutation
    export: {
      mutate: exportMutation.mutate,
      mutateAsync: exportMutation.mutateAsync,
      isPending: exportMutation.isPending,
      isError: exportMutation.isError,
      error: exportMutation.error,
      isSuccess: exportMutation.isSuccess,
      data: exportMutation.data,
      reset: exportMutation.reset,
    },

    // Delete prescription mutation
    delete: {
      mutate: deleteMutation.mutate,
      mutateAsync: deleteMutation.mutateAsync,
      isPending: deleteMutation.isPending,
      isError: deleteMutation.isError,
      error: deleteMutation.error,
      isSuccess: deleteMutation.isSuccess,
      reset: deleteMutation.reset,
    },

    // Combined loading/error states
    isLoading: history.isLoading || generateMutation.isPending,
    isError: history.isError || generateMutation.isError,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Export all hooks as default
// ═══════════════════════════════════════════════════════════════════════════

export default {
  usePrescriptionHistory,
  usePrescriptionDetails,
  useGeneratePrescription,
  useExportPrescription,
  useDeletePrescription,
  useVRA,
};
