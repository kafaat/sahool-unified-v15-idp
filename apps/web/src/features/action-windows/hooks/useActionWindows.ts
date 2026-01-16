/**
 * SAHOOL Action Windows Hooks
 * خطافات نوافذ العمل
 *
 * React hooks for fetching and managing action windows (spray, irrigation, recommendations)
 */

import { useQuery } from "@tanstack/react-query";
import {
  getSprayWindows,
  getIrrigationWindows,
  getActionRecommendations,
  actionWindowsKeys,
} from "../api/action-windows-api";
import type {
  SprayWindow,
  IrrigationWindow,
  ActionRecommendation,
  SprayWindowCriteria,
  ActionType,
} from "../types/action-windows";

// ═══════════════════════════════════════════════════════════════════════════
// Hook Options
// ═══════════════════════════════════════════════════════════════════════════

export interface ActionWindowsHookOptions {
  fieldId: string;
  days?: number;
  enabled?: boolean;
}

export interface SprayWindowsOptions extends ActionWindowsHookOptions {
  criteria?: Partial<SprayWindowCriteria>;
}

export interface ActionRecommendationsOptions extends ActionWindowsHookOptions {
  actionTypes?: ActionType[];
}

// ═══════════════════════════════════════════════════════════════════════════
// Spray Windows Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch spray windows for a field
 * خطاف لجلب نوافذ الرش للحقل
 *
 * @param options - Field ID, days to forecast, and optional criteria
 * @returns React Query result with spray windows
 *
 * @example
 * ```tsx
 * const { data: windows, isLoading } = useSprayWindows({
 *   fieldId: 'field-123',
 *   days: 7,
 *   criteria: { windSpeedMax: 12 }
 * });
 * ```
 */
export function useSprayWindows(options: SprayWindowsOptions) {
  const { fieldId, days = 7, criteria, enabled = true } = options;

  return useQuery({
    queryKey: actionWindowsKeys.spray(fieldId, days),
    queryFn: async () => {
      const response = await getSprayWindows({ fieldId, days, criteria });

      if (!response.success) {
        throw new Error(response.error || "Failed to fetch spray windows");
      }

      return response.data || [];
    },
    enabled: enabled && !!fieldId,
    staleTime: 15 * 60 * 1000, // 15 minutes
    refetchInterval: 30 * 60 * 1000, // Refetch every 30 minutes
    retry: 2,
    retryDelay: 1000,
  });
}

/**
 * Hook to get optimal spray windows (status: optimal)
 * خطاف للحصول على نوافذ الرش المثالية
 */
export function useOptimalSprayWindows(options: SprayWindowsOptions) {
  const query = useSprayWindows(options);

  return {
    ...query,
    data: query.data?.filter((window) => window.status === "optimal") || [],
  };
}

/**
 * Hook to get next available spray window
 * خطاف للحصول على نافذة الرش القادمة المتاحة
 */
export function useNextSprayWindow(options: SprayWindowsOptions) {
  const query = useSprayWindows(options);

  const nextWindow = query.data?.find((window) => {
    const startTime = new Date(window.startTime);
    return startTime > new Date() && window.status !== "avoid";
  });

  return {
    ...query,
    data: nextWindow,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Irrigation Windows Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch irrigation windows for a field
 * خطاف لجلب نوافذ الري للحقل
 *
 * @param options - Field ID, days to forecast, and enabled flag
 * @returns React Query result with irrigation windows
 *
 * @example
 * ```tsx
 * const { data: windows, isLoading } = useIrrigationWindows({
 *   fieldId: 'field-123',
 *   days: 7
 * });
 * ```
 */
export function useIrrigationWindows(options: ActionWindowsHookOptions) {
  const { fieldId, days = 7, enabled = true } = options;

  return useQuery({
    queryKey: actionWindowsKeys.irrigation(fieldId, days),
    queryFn: async () => {
      const response = await getIrrigationWindows({ fieldId, days });

      if (!response.success) {
        throw new Error(response.error || "Failed to fetch irrigation windows");
      }

      return response.data || [];
    },
    enabled: enabled && !!fieldId,
    staleTime: 15 * 60 * 1000, // 15 minutes
    refetchInterval: 30 * 60 * 1000, // Refetch every 30 minutes
    retry: 2,
    retryDelay: 1000,
  });
}

/**
 * Hook to get urgent irrigation windows
 * خطاف للحصول على نوافذ الري العاجلة
 */
export function useUrgentIrrigationWindows(options: ActionWindowsHookOptions) {
  const query = useIrrigationWindows(options);

  return {
    ...query,
    data:
      query.data?.filter(
        (window) => window.priority === "urgent" || window.priority === "high",
      ) || [],
  };
}

/**
 * Hook to get next irrigation window
 * خطاف للحصول على نافذة الري القادمة
 */
export function useNextIrrigationWindow(options: ActionWindowsHookOptions) {
  const query = useIrrigationWindows(options);

  const nextWindow = query.data?.find((window) => {
    const startTime = new Date(window.startTime);
    return startTime > new Date();
  });

  return {
    ...query,
    data: nextWindow,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Action Recommendations Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch action recommendations for a field
 * خطاف لجلب توصيات العمل للحقل
 *
 * @param options - Field ID, action types filter, days, and enabled flag
 * @returns React Query result with action recommendations
 *
 * @example
 * ```tsx
 * const { data: recommendations, isLoading } = useActionRecommendations({
 *   fieldId: 'field-123',
 *   actionTypes: ['spray', 'irrigate'],
 *   days: 7
 * });
 * ```
 */
export function useActionRecommendations(
  options: ActionRecommendationsOptions,
) {
  const { fieldId, actionTypes, days = 7, enabled = true } = options;

  return useQuery({
    queryKey: actionWindowsKeys.recommendations(fieldId, days),
    queryFn: async () => {
      const response = await getActionRecommendations({
        fieldId,
        actionTypes,
        days,
      });

      if (!response.success) {
        throw new Error(
          response.error || "Failed to fetch action recommendations",
        );
      }

      return response.data || [];
    },
    enabled: enabled && !!fieldId,
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 20 * 60 * 1000, // Refetch every 20 minutes
    retry: 2,
    retryDelay: 1000,
  });
}

/**
 * Hook to get high-priority recommendations
 * خطاف للحصول على التوصيات ذات الأولوية العالية
 */
export function useHighPriorityRecommendations(
  options: ActionRecommendationsOptions,
) {
  const query = useActionRecommendations(options);

  return {
    ...query,
    data:
      query.data?.filter(
        (rec) => rec.priority === "urgent" || rec.priority === "high",
      ) || [],
  };
}

/**
 * Hook to get recommendations by action type
 * خطاف للحصول على التوصيات حسب نوع العمل
 */
export function useRecommendationsByType(
  options: ActionRecommendationsOptions,
  actionType: ActionType,
) {
  const query = useActionRecommendations(options);

  return {
    ...query,
    data: query.data?.filter((rec) => rec.actionType === actionType) || [],
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Combined Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to get all action windows for a field
 * خطاف للحصول على جميع نوافذ العمل للحقل
 *
 * @param options - Field ID, days, and enabled flag
 * @returns Combined data from spray windows, irrigation windows, and recommendations
 */
export function useAllActionWindows(options: ActionWindowsHookOptions) {
  const sprayWindows = useSprayWindows({ ...options });
  const irrigationWindows = useIrrigationWindows(options);
  const recommendations = useActionRecommendations(options);

  const isLoading =
    sprayWindows.isLoading ||
    irrigationWindows.isLoading ||
    recommendations.isLoading;
  const error =
    sprayWindows.error || irrigationWindows.error || recommendations.error;

  return {
    sprayWindows: {
      data: sprayWindows.data || [],
      isLoading: sprayWindows.isLoading,
      error: sprayWindows.error,
    },
    irrigationWindows: {
      data: irrigationWindows.data || [],
      isLoading: irrigationWindows.isLoading,
      error: irrigationWindows.error,
    },
    recommendations: {
      data: recommendations.data || [],
      isLoading: recommendations.isLoading,
      error: recommendations.error,
    },
    isLoading,
    error,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Type Exports for convenience
// ═══════════════════════════════════════════════════════════════════════════

export type { SprayWindow, IrrigationWindow, ActionRecommendation };
