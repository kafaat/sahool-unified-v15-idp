/**
 * SAHOOL Admin - Dashboard data hooks
 * خطافات بيانات لوحة التحكم
 *
 * Hooks for fetching dashboard statistics, metrics, and trends.
 */

"use client";

import { useApiQuery } from "./use-api-query";
import {
  fetchDashboardStats,
  fetchYieldTrends,
  fetchCropDistribution,
  fetchWeeklyActivity,
  fetchPlatformMetrics,
} from "@/lib/api";
import type { DashboardStats } from "@/types";

/**
 * Dashboard statistics hook
 * Auto-refreshes every 60 seconds
 */
export function useDashboardStats() {
  return useApiQuery<DashboardStats>(
    ["dashboard", "stats"],
    fetchDashboardStats,
    {
      refetchInterval: 60000,
      staleTime: 30000,
    },
  );
}

/**
 * Yield trends hook
 */
export function useYieldTrends(
  period: "7d" | "30d" | "90d" = "30d",
) {
  return useApiQuery(
    ["dashboard", "yield-trends", period],
    () => fetchYieldTrends(period),
    { staleTime: 120000 },
  );
}

/**
 * Crop distribution hook
 */
export function useCropDistribution() {
  return useApiQuery(
    ["dashboard", "crop-distribution"],
    fetchCropDistribution,
    { staleTime: 300000 },
  );
}

/**
 * Weekly activity hook
 */
export function useWeeklyActivity() {
  return useApiQuery(
    ["dashboard", "weekly-activity"],
    fetchWeeklyActivity,
    { staleTime: 120000 },
  );
}

/**
 * Platform metrics hook
 */
export function usePlatformMetrics() {
  return useApiQuery(
    ["dashboard", "platform-metrics"],
    fetchPlatformMetrics,
    {
      refetchInterval: 120000,
      staleTime: 60000,
    },
  );
}
