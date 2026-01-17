/**
 * SAHOOL Dashboard Data Hook
 * خطاف بيانات لوحة التحكم
 */

import { useQuery } from "@tanstack/react-query";
import { dashboardApi, type DashboardData } from "../api";

// Re-export DashboardData type for convenience
export type { DashboardData };

export function useDashboardData() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: dashboardApi.getDashboard,
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
}
