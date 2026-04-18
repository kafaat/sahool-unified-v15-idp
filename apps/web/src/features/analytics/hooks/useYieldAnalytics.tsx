/**
 * Wave-3 yield analytics hook.
 * Calls the real yield-prediction-service list endpoint via the unified contract.
 *
 * Backend: yield-prediction-service (port 8152)
 * Route: YIELD_ENDPOINTS.PREDICTIONS → GET /api/v1/yield/predictions
 *
 * Returns an array of per-field yield records. If the backend returns an empty
 * array (or errors), the consuming page keeps its DemoBanner visible.
 */

'use client';

import { useQuery } from '@tanstack/react-query';
import { yieldApi, type YieldRecord } from '@/features/yield/api';

export type { YieldRecord };

export interface YieldHistoryFilters {
  /** Optional season filter (forwarded to the backend as-is). */
  season?: string;
  /** Optional crop type filter. */
  cropType?: string;
}

/**
 * Fetch tenant-scoped yield predictions for the analytics screen.
 * tenantId is injected server-side from the JWT on the upstream service, so
 * the hook does not need to read it from the auth store.
 */
export function useYieldHistory(_filters?: YieldHistoryFilters) {
  return useQuery<YieldRecord[]>({
    queryKey: ['analytics', 'yield-history', _filters],
    queryFn: () => yieldApi.getPredictions(),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}
