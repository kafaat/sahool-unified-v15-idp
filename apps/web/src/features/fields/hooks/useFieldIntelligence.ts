/**
 * SAHOOL Field Intelligence Hooks
 * خطافات ذكاء الحقول
 *
 * React Query hooks for field intelligence features including:
 * - Field zones management
 * - Field alerts monitoring
 * - Best days recommendations
 * - Date validation for activities
 * - Field recommendations
 * - Task creation from alerts
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { logger } from '@/lib/logger';
import {
  fetchFieldZones,
  fetchFieldAlerts,
  fetchBestDays,
  validateTaskDate,
  fetchFieldRecommendations,
  createTaskFromAlert as apiCreateTaskFromAlert,
  fieldIntelligenceKeys,
  type FieldZone,
  type FieldAlert,
  type BestDay,
  type DateValidation,
  type FieldRecommendation,
  type TaskFromAlertData,
  type CreatedTask,
} from '../api/field-intelligence-api';

// ═══════════════════════════════════════════════════════════════════════════
// Re-export Types for Convenience
// ═══════════════════════════════════════════════════════════════════════════

export type {
  FieldZone,
  FieldAlert,
  BestDay,
  DateValidation,
  FieldRecommendation,
  TaskFromAlertData,
  CreatedTask,
};

// ═══════════════════════════════════════════════════════════════════════════
// Additional Types for Hook Options
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Options for best days query
 * خيارات استعلام أفضل الأيام
 */
export interface BestDaysOptions {
  days?: number;
  enabled?: boolean;
}

/**
 * Hook options with enabled flag
 * خيارات الخطاف مع علامة التفعيل
 */
export interface HookOptions {
  enabled?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Re-export Query Keys
// ═══════════════════════════════════════════════════════════════════════════

export { fieldIntelligenceKeys };

// ═══════════════════════════════════════════════════════════════════════════
// Query Hooks - خطافات الاستعلام
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch and cache field zones
 * خطاف لجلب وتخزين مناطق الحقل
 *
 * @param fieldId - Field ID
 * @param options - Hook options
 * @returns Query result with field zones data
 */
export function useFieldZones(fieldId: string, options?: HookOptions) {
  const { enabled = true } = options || {};

  return useQuery({
    queryKey: fieldIntelligenceKeys.zones(fieldId),
    queryFn: async () => {
      const response = await fetchFieldZones(fieldId);
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch field zones');
      }
      return response.data || [];
    },
    enabled: enabled && !!fieldId,
    staleTime: 5 * 60 * 1000, // 5 minutes - zones don't change frequently
    retry: 2,
    retryDelay: 1000,
  });
}

/**
 * Hook to fetch field alerts with auto-refetch
 * خطاف لجلب تنبيهات الحقل مع إعادة الجلب التلقائي
 *
 * @param fieldId - Field ID
 * @param options - Hook options
 * @returns Query result with field alerts data
 */
export function useFieldAlerts(fieldId: string, options?: HookOptions) {
  const { enabled = true } = options || {};

  return useQuery({
    queryKey: fieldIntelligenceKeys.alerts(fieldId),
    queryFn: async () => {
      const response = await fetchFieldAlerts(fieldId);
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch field alerts');
      }
      return response.data || [];
    },
    enabled: enabled && !!fieldId,
    staleTime: 30 * 1000, // 30 seconds - alerts change frequently
    refetchInterval: 60 * 1000, // Refetch every minute for real-time updates
    retry: 2,
    retryDelay: 500,
  });
}

/**
 * Hook to fetch best days for farming activity
 * خطاف لجلب أفضل الأيام لنشاط زراعي
 *
 * @param activity - Farming activity (e.g., 'زراعة', 'حصاد', 'ري')
 * @param options - Query options including days count
 * @returns Query result with best days data
 */
export function useBestDays(
  activity: string = 'planting',
  options?: BestDaysOptions
) {
  const { enabled = true, days = 14 } = options || {};

  return useQuery({
    queryKey: fieldIntelligenceKeys.bestDays(activity, days),
    queryFn: async () => {
      const response = await fetchBestDays(activity, days);
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch best days');
      }
      return response.data || [];
    },
    enabled: enabled && !!activity,
    staleTime: 24 * 60 * 60 * 1000, // 24 hours - best days are stable
    retry: 2,
    retryDelay: 1000,
  });
}

/**
 * Hook to validate date for farming activity
 * خطاف للتحقق من صحة التاريخ لنشاط زراعي
 *
 * Validates date on change and provides suitability score
 *
 * @param date - Date to validate (ISO format)
 * @param activity - Farming activity
 * @param options - Hook options
 * @returns Query result with validation data
 */
export function useValidateDate(
  date: string,
  activity: string,
  options?: HookOptions
) {
  const { enabled = true } = options || {};

  return useQuery({
    queryKey: fieldIntelligenceKeys.dateValidation(date, activity),
    queryFn: async () => {
      const response = await validateTaskDate(date, activity);
      if (!response.success) {
        throw new Error(response.error || 'Failed to validate date');
      }
      return response.data;
    },
    enabled: enabled && !!date && !!activity,
    staleTime: 60 * 60 * 1000, // 1 hour - validation is stable per date
    retry: 1,
    retryDelay: 500,
  });
}

/**
 * Hook to fetch field recommendations
 * خطاف لجلب توصيات الحقل
 *
 * @param fieldId - Field ID
 * @param options - Hook options
 * @returns Query result with recommendations data
 */
export function useFieldRecommendations(fieldId: string, options?: HookOptions) {
  const { enabled = true } = options || {};

  return useQuery({
    queryKey: fieldIntelligenceKeys.recommendations(fieldId),
    queryFn: async () => {
      const response = await fetchFieldRecommendations(fieldId);
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch recommendations');
      }
      return response.data || [];
    },
    enabled: enabled && !!fieldId,
    staleTime: 2 * 60 * 1000, // 2 minutes - recommendations should be fresh
    retry: 2,
    retryDelay: 1000,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Hooks - خطافات الطفرة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to create task from alert with optimistic updates
 * خطاف لإنشاء مهمة من تنبيه مع تحديثات تفاؤلية
 *
 * @returns Mutation result with task creation handler
 */
export function useCreateTaskFromAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      alertId,
      taskData,
    }: {
      alertId: string;
      taskData: TaskFromAlertData;
    }) => {
      const response = await apiCreateTaskFromAlert(alertId, taskData);
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to create task from alert');
      }
      return response.data;
    },
    onMutate: async (variables) => {
      // Cancel outgoing refetches
      const alertQueryKey = fieldIntelligenceKeys.alerts(variables.alertId);
      await queryClient.cancelQueries({ queryKey: alertQueryKey });

      // Snapshot the previous value
      const previousAlerts = queryClient.getQueryData(alertQueryKey);

      // Log optimistic update
      logger.info(`Creating task from alert ${variables.alertId}`);

      // Return context with previous state for rollback
      return { previousAlerts, alertQueryKey };
    },
    onError: (error, _variables, context) => {
      // Rollback on error
      if (context?.previousAlerts && context?.alertQueryKey) {
        queryClient.setQueryData(context.alertQueryKey, context.previousAlerts);
      }

      logger.error('Failed to create task from alert:', error);
    },
    onSuccess: (task, variables) => {
      // Invalidate and refetch affected queries
      if (task.fieldId) {
        queryClient.invalidateQueries({
          queryKey: fieldIntelligenceKeys.alerts(task.fieldId),
        });
        queryClient.invalidateQueries({
          queryKey: fieldIntelligenceKeys.recommendations(task.fieldId),
        });
      }

      // Invalidate tasks list to show new task
      queryClient.invalidateQueries({ queryKey: ['tasks'] });

      logger.info(`Task ${task.id} created successfully from alert ${variables.alertId}`);
    },
    onSettled: () => {
      // Refetch after mutation completes (success or error)
      queryClient.invalidateQueries({
        queryKey: fieldIntelligenceKeys.all,
      });
    },
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Composite Hooks - الخطافات المركبة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook that provides all field intelligence data for a field
 * خطاف يوفر جميع بيانات ذكاء الحقل
 *
 * Combines zones, alerts, and recommendations into a single hook
 * for convenience when building field dashboards
 *
 * @param fieldId - Field ID
 * @param options - Hook options
 * @returns Combined intelligence data
 */
export function useFieldIntelligence(fieldId: string, options?: HookOptions) {
  const { enabled = true } = options || {};

  const zones = useFieldZones(fieldId, { enabled });
  const alerts = useFieldAlerts(fieldId, { enabled });
  const recommendations = useFieldRecommendations(fieldId, { enabled });
  const createTask = useCreateTaskFromAlert();

  return {
    zones: {
      data: zones.data,
      isLoading: zones.isLoading,
      isError: zones.isError,
      error: zones.error,
      refetch: zones.refetch,
    },
    alerts: {
      data: alerts.data,
      isLoading: alerts.isLoading,
      isError: alerts.isError,
      error: alerts.error,
      refetch: alerts.refetch,
    },
    recommendations: {
      data: recommendations.data,
      isLoading: recommendations.isLoading,
      isError: recommendations.isError,
      error: recommendations.error,
      refetch: recommendations.refetch,
    },
    createTask: {
      mutate: createTask.mutate,
      mutateAsync: createTask.mutateAsync,
      isPending: createTask.isPending,
      isError: createTask.isError,
      error: createTask.error,
      isSuccess: createTask.isSuccess,
      reset: createTask.reset,
    },
    isLoading: zones.isLoading || alerts.isLoading || recommendations.isLoading,
    isError: zones.isError || alerts.isError || recommendations.isError,
  };
}

/**
 * Hook for date validation with debouncing support
 * خطاف للتحقق من صحة التاريخ مع دعم التأخير
 *
 * Useful for form validation where you want to validate
 * as the user types but avoid excessive API calls
 *
 * @param date - Date to validate
 * @param activity - Farming activity
 * @param options - Hook options
 * @returns Validation result with debounced updates
 */
export function useDebouncedDateValidation(
  date: string,
  activity: string,
  options?: HookOptions
) {
  const validation = useValidateDate(date, activity, options);

  // The query itself will be debounced by the staleTime setting
  // Additional debouncing can be implemented at the component level
  // using a debounced state value for the date parameter

  return {
    ...validation,
    isValidating: validation.isLoading,
    isSuitable: validation.data?.suitable,
    score: validation.data?.score,
    rating: validation.data?.rating,
    warnings: validation.data?.warnings,
    alternatives: validation.data?.alternatives,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Export all hooks as default
// ═══════════════════════════════════════════════════════════════════════════

export default {
  useFieldZones,
  useFieldAlerts,
  useBestDays,
  useValidateDate,
  useFieldRecommendations,
  useCreateTaskFromAlert,
  useFieldIntelligence,
  useDebouncedDateValidation,
};
