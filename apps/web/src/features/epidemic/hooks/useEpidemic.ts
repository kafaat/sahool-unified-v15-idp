/**
 * Epidemic Feature - React Hooks
 * خطافات React لميزة الأوبئة
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { epidemicApi, type Epidemic, type EpidemicReport } from '../api';

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys
// ═══════════════════════════════════════════════════════════════════════════

export const epidemicKeys = {
  all: ['epidemics'] as const,
  list: (status?: string) => [...epidemicKeys.all, 'list', status] as const,
  detail: (id: string) => [...epidemicKeys.all, 'detail', id] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Query Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch all epidemics
 * خطاف لجلب جميع الأوبئة
 */
export function useEpidemics(status?: string) {
  return useQuery<Epidemic[]>({
    queryKey: epidemicKeys.list(status),
    queryFn: () => epidemicApi.getEpidemics(status),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to fetch a single epidemic by ID
 * خطاف لجلب وباء بواسطة المعرف
 */
export function useEpidemic(id: string) {
  return useQuery<Epidemic>({
    queryKey: epidemicKeys.detail(id),
    queryFn: () => epidemicApi.getEpidemicById(id),
    enabled: !!id,
  });
}

/**
 * Hook to report a new epidemic observation
 * خطاف للإبلاغ عن ملاحظة وباء جديدة
 */
export function useReportEpidemic() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: EpidemicReport) => epidemicApi.reportEpidemic(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: epidemicKeys.all });
    },
  });
}
