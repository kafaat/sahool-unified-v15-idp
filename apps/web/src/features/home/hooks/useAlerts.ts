/**
 * SAHOOL Dashboard Alerts Hook
 * خطاف تنبيهات لوحة التحكم
 */

import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "../api";

interface UseAlertsOptions {
  /** Maximum number of alerts to fetch */
  limit?: number;
  /** Filter by severity */
  severity?: "critical" | "warning" | "info";
  /** Enable/disable the query */
  enabled?: boolean;
}

/**
 * Hook for fetching dashboard alerts
 * @param options - Configuration options
 */
export function useAlerts(options: UseAlertsOptions = {}) {
  const { limit = 10, severity, enabled = true } = options;

  return useQuery({
    queryKey: ["dashboard", "alerts", { limit, severity }],
    queryFn: () => dashboardApi.getAlerts({ limit, severity }),
    staleTime: 30 * 1000, // 30 seconds - alerts are time-sensitive
    refetchInterval: 60 * 1000, // Refetch every minute
    enabled,
  });
}
