/**
 * Wave-3 satellite analytics hook.
 * Calls the real NDVI summary endpoint exposed by field-management-service,
 * which aggregates per-field NDVI values from vegetation-analysis-service.
 *
 * Backend route: SATELLITE_ENDPOINTS.NDVI_SUMMARY → GET /api/v1/ndvi/summary
 * Response shape (from field-management-service ndvi.service.ts):
 *   { totalFields, averageNdvi, averageHealth, totalAreaHectares,
 *     distribution: { healthy, moderate, stressed, critical }, timestamp }
 *
 * The analytics page can use `averageNdvi` + distribution to populate its
 * stats cards. Per-field rows (field name, LAI, EVI, cloudCover) are not
 * available from this summary endpoint; callers should fall back to the
 * DemoBanner when the per-field table has no live source.
 */

'use client';

import { useQuery } from '@tanstack/react-query';
import { fieldsApi, type FieldNdviSummary } from '@/features/fields/api';

export type { FieldNdviSummary };

/**
 * Extended summary shape returned by field-management-service. The public
 * `FieldNdviSummary` type only declares three fields but the service returns
 * additional aggregates; we model them here without mutating the shared type.
 */
export interface NdviHistorySummary extends FieldNdviSummary {
  averageHealth?: number;
  totalAreaHectares?: number;
  timestamp?: string;
  distribution?: {
    healthy?: number;
    moderate?: number;
    stressed?: number;
    critical?: number;
  };
}

export interface NdviHistoryFilters {
  /** Placeholder for future per-field filtering. Currently unused. */
  fieldId?: string;
}

export function useNdviHistory(_filters?: NdviHistoryFilters) {
  return useQuery<NdviHistorySummary>({
    queryKey: ['analytics', 'ndvi-summary', _filters],
    queryFn: async () => {
      const summary = await fieldsApi.getNdviSummary();
      return summary as NdviHistorySummary;
    },
    staleTime: 15 * 60 * 1000,
    retry: 1,
  });
}
