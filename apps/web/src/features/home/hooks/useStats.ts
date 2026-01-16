/**
 * SAHOOL Dashboard Stats Hook
 * خطاف إحصائيات لوحة التحكم
 */

import { useQuery } from "@tanstack/react-query";
import { dashboardApi, type DashboardData } from "../api";

export type DashboardStats = DashboardData["stats"];

/**
 * Hook for fetching dashboard statistics only
 * Useful when you only need stats without other dashboard data
 */
export function useStats() {
  return useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: dashboardApi.getStats,
    staleTime: 30 * 1000, // 30 seconds - stats update more frequently
    refetchInterval: 2 * 60 * 1000, // Refetch every 2 minutes
  });
}

/**
 * Hook for fetching enhanced stats with trends
 */
export function useEnhancedStats() {
  return useQuery({
    queryKey: ["dashboard", "stats", "enhanced"],
    queryFn: dashboardApi.getEnhancedStats,
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
}
