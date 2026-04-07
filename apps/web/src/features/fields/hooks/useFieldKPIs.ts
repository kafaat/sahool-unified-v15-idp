/**
 * SAHOOL Field KPI Hooks
 * خطافات KPI للحقل — Sentinel Hub + OpenWeather
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fieldsApi } from '../api';
import { fieldKeys } from './queryKeys';

/**
 * Hook to fetch the latest KPI snapshot for a field
 * خطاف لجلب أحدث لقطة KPI للحقل
 */
export function useFieldKpiSnapshot(fieldId: string, enabled = true) {
  return useQuery({
    queryKey: fieldKeys.kpi(fieldId),
    queryFn: () => fieldsApi.getLatestKpiSnapshot(fieldId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: !!fieldId && enabled,
    retry: 1,
  });
}

/**
 * Hook to trigger a fresh KPI fetch (Sentinel Hub + OpenWeather → save snapshot)
 * خطاف لتحديث KPI من الأقمار الصناعية والطقس
 */
export function useTriggerKpiRefresh(fieldId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ lat, lng }: { lat: number; lng: number }) =>
      fieldsApi.triggerKpiRefresh(fieldId, lat, lng),
    onSuccess: (data) => {
      queryClient.setQueryData(fieldKeys.kpi(fieldId), data);
      queryClient.invalidateQueries({ queryKey: fieldKeys.detail(fieldId) });
    },
  });
}
