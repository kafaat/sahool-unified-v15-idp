/**
 * SAHOOL Recent Activity Hook
 * خطاف النشاط الأخير
 */

import { useQuery } from '@tanstack/react-query';
import { dashboardApi, type DashboardData } from '../api';

export type ActivityItem = DashboardData['recentActivity'][number];

interface UseRecentActivityOptions {
  /** Maximum number of activities to fetch */
  limit?: number;
  /** Enable/disable the query */
  enabled?: boolean;
}

/**
 * Hook for fetching recent activity for the dashboard
 * @param options - Configuration options
 */
export function useRecentActivity(options: UseRecentActivityOptions = {}) {
  const { limit = 10, enabled = true } = options;

  return useQuery({
    queryKey: ['dashboard', 'activity', limit],
    queryFn: () => dashboardApi.getRecentActivity(limit),
    staleTime: 30 * 1000, // 30 seconds - activity updates frequently
    refetchInterval: 60 * 1000, // Refetch every minute
    enabled,
  });
}
