/**
 * SAHOOL Upcoming Tasks Hook
 * خطاف المهام القادمة
 */

import { useQuery } from "@tanstack/react-query";
import { dashboardApi, type DashboardData } from "../api";

export type UpcomingTask = DashboardData["upcomingTasks"][number];

interface UseUpcomingTasksOptions {
  /** Maximum number of tasks to fetch */
  limit?: number;
  /** Enable/disable the query */
  enabled?: boolean;
}

/**
 * Hook for fetching upcoming tasks for the dashboard
 * @param options - Configuration options
 */
export function useUpcomingTasks(options: UseUpcomingTasksOptions = {}) {
  const { limit = 5, enabled = true } = options;

  return useQuery({
    queryKey: ["dashboard", "tasks", "upcoming", limit],
    queryFn: () => dashboardApi.getUpcomingTasks(limit),
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 3 * 60 * 1000, // Refetch every 3 minutes
    enabled,
  });
}
