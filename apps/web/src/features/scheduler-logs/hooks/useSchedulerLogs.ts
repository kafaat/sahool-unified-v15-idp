'use client';

import { useQuery } from '@tanstack/react-query';
import { schedulerLogsApi } from '../api';
import type { SchedulerFilters } from '../types';

export const schedulerLogsKeys = {
  all: ['scheduler-logs'] as const,
  logs: (filters?: SchedulerFilters) => [...schedulerLogsKeys.all, 'logs', filters] as const,
  stats: (period?: string) => [...schedulerLogsKeys.all, 'stats', period] as const,
};

export function useSchedulerLogs(filters?: SchedulerFilters) {
  return useQuery({
    queryKey: schedulerLogsKeys.logs(filters),
    queryFn: () => schedulerLogsApi.getLogs(filters),
    staleTime: 1000 * 60 * 2,
    retry: 1,
  });
}

export function useSchedulerStats(period?: SchedulerFilters['period']) {
  return useQuery({
    queryKey: schedulerLogsKeys.stats(period),
    queryFn: () => schedulerLogsApi.getStats(period),
    staleTime: 1000 * 60 * 2,
    retry: 1,
  });
}
