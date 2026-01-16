/**
 * SAHOOL Dashboard Mutations Hook
 * خطاف عمليات التعديل في لوحة التحكم
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { dashboardApi } from "../api";

/**
 * Hook for dashboard mutation operations
 * Provides methods to complete tasks, dismiss alerts, and mark activity as read
 */
export function useDashboardMutations() {
  const queryClient = useQueryClient();

  /**
   * Mark a task as complete
   */
  const markTaskComplete = useMutation({
    mutationFn: ({ taskId, notes }: { taskId: string; notes?: string }) =>
      dashboardApi.markTaskComplete(taskId, notes),
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard", "tasks"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard", "stats"] });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });

  /**
   * Dismiss an alert
   */
  const dismissAlert = useMutation({
    mutationFn: ({ alertId, reason }: { alertId: string; reason?: string }) =>
      dashboardApi.dismissAlert(alertId, reason),
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard", "alerts"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard", "stats"] });
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });

  /**
   * Acknowledge an alert
   */
  const acknowledgeAlert = useMutation({
    mutationFn: (alertId: string) => dashboardApi.acknowledgeAlert(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard", "alerts"] });
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });

  /**
   * Mark activities as read
   */
  const markActivityRead = useMutation({
    mutationFn: (activityIds: string[]) =>
      dashboardApi.markActivityRead(activityIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard", "activity"] });
    },
  });

  /**
   * Refresh all dashboard data
   */
  const refreshDashboard = useMutation({
    mutationFn: async () => {
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      return { success: true };
    },
  });

  return {
    markTaskComplete,
    dismissAlert,
    acknowledgeAlert,
    markActivityRead,
    refreshDashboard,
    isLoading:
      markTaskComplete.isPending ||
      dismissAlert.isPending ||
      acknowledgeAlert.isPending ||
      markActivityRead.isPending,
  };
}
