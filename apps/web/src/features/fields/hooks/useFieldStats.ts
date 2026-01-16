/**
 * SAHOOL Field Statistics Hook
 * خطاف إحصائيات الحقول
 */

import { useQuery } from "@tanstack/react-query";
import { fieldsApi } from "../api";
import { fieldKeys } from "./queryKeys";

/**
 * Hook to fetch field statistics
 * خطاف لجلب إحصائيات الحقول
 */
export function useFieldStats(farmId?: string) {
  return useQuery({
    queryKey: fieldKeys.stats(farmId),
    queryFn: () => fieldsApi.getStats(farmId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });
}
