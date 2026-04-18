/**
 * Wave-3 soil analytics hook.
 * Calls the tenant-scoped cross-field soil-tests listing exposed by
 * soil-analysis-service.
 *
 * Backend: soil-analysis-service (port 8134)
 * Route: SOIL_ENDPOINTS.TESTS → GET /api/v1/soil/tests?tenantId=...
 *
 * Returns per-field rows shaped to match the analytics table. When the
 * backend returns an empty list (or errors), the consuming page keeps its
 * DemoBanner visible.
 */

'use client';

import { useQuery } from '@tanstack/react-query';
import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { SOIL_ENDPOINTS } from '@sahool/shared-types/contracts';

const api = createApiClient();

/** Row shape consumed by the /analytics/soil page table. */
export interface SoilAnalyticsRow {
  field: string;
  ph: number;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  organic: string;
  ec: number;
  moisture: number;
  texture: string;
  lastTest: string;
}

/** Raw response row returned by the backend. */
interface BackendSoilTestRow {
  id: string;
  tenant_id: string;
  field_id?: string | null;
  sample_date: string;
  ph?: number | null;
  ec?: number | null;
  organic_matter?: number | null;
  nitrogen_ppm?: number | null;
  phosphorus_ppm?: number | null;
  potassium_ppm?: number | null;
  calcium_ppm?: number | null;
  magnesium_ppm?: number | null;
  created_at: string;
}

interface BackendResponse {
  items: BackendSoilTestRow[];
  nextCursor?: string | null;
  total?: number | null;
}

export interface SoilAnalyticsFilters {
  tenantId: string;
  fieldId?: string;
  fromDate?: string;
  toDate?: string;
  limit?: number;
}

function toRow(r: BackendSoilTestRow): SoilAnalyticsRow {
  const organicPct =
    r.organic_matter != null ? `${r.organic_matter.toFixed(1)}%` : '—';
  return {
    field: r.field_id ?? r.id,
    ph: r.ph ?? 0,
    nitrogen: r.nitrogen_ppm ?? 0,
    phosphorus: r.phosphorus_ppm ?? 0,
    potassium: r.potassium_ppm ?? 0,
    organic: organicPct,
    ec: r.ec ?? 0,
    moisture: 0,
    texture: '—',
    lastTest: (r.sample_date ?? r.created_at).slice(0, 10),
  };
}

export function useSoilAnalytics(filters: SoilAnalyticsFilters) {
  return useQuery<SoilAnalyticsRow[]>({
    queryKey: ['analytics', 'soil-tests', filters],
    queryFn: () =>
      safeFetch(SOIL_ENDPOINTS.TESTS, async () => {
        const params = new URLSearchParams();
        params.set('tenantId', filters.tenantId);
        if (filters.fieldId) params.set('fieldId', filters.fieldId);
        if (filters.fromDate) params.set('fromDate', filters.fromDate);
        if (filters.toDate) params.set('toDate', filters.toDate);
        params.set('limit', String(filters.limit ?? 100));

        const response = await api.get(
          `${SOIL_ENDPOINTS.TESTS}?${params.toString()}`,
        );
        const payload = (response.data?.data ?? response.data) as BackendResponse;
        if (!payload || !Array.isArray(payload.items)) return [];
        return payload.items.map(toRow);
      }),
    enabled: Boolean(filters.tenantId),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}
