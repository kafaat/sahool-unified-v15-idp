/**
 * Crop Seasons API
 * طبقة API - مواسم المحاصيل
 *
 * Talks to field-management-service via the unified contracts:
 *
 *   POST   /api/v1/fields/:fieldId/crop-seasons
 *   GET    /api/v1/fields/:fieldId/crop-seasons
 *   GET    /api/v1/crop-seasons
 *   GET    /api/v1/crop-seasons/:id
 *   PATCH  /api/v1/crop-seasons/:id
 *   POST   /api/v1/crop-seasons/:id/end
 *   DELETE /api/v1/crop-seasons/:id
 *   GET    /api/v1/crop-seasons/:id/rollup
 *
 * JWT auth (cookie-based) is applied by the shared api-client factory —
 * tenantId is never sent in the body; the backend pulls it from the `tid`
 * JWT claim.
 */

import { createApiClient } from '@/lib/api/factory';
import {
  CROP_SEASON_ENDPOINTS,
  buildUrl,
} from '@sahool/shared-types/contracts';

const api = createApiClient();

// ---------------------------------------------------------------------------
// Public DTO types — 1:1 mirror of the NestJS DTO shapes so the TypeScript
// types stay in sync with the backend without forcing a build-time codegen
// step. If the backend shape changes, both ends update in the same PR.
// ---------------------------------------------------------------------------

export type SeasonValue = 'winter' | 'spring' | 'summer' | 'autumn' | 'year-round';

export interface CropSeason {
  id: string;
  fieldId: string;
  tenantId: string;
  cropType: string;
  cropTypeAr?: string | null;
  season?: SeasonValue | null;
  sowingDate: string;
  expectedHarvestDate?: string | null;
  actualHarvestDate?: string | null;
  endedAt?: string | null;
  endReason?: string | null;
  isCurrent: boolean;
  seedVariety?: string | null;
  seedVarietyAr?: string | null;
  plantingDensityKgHa?: number | string | null;
  irrigationType?: string | null;
  yieldKgHa?: number | string | null;
  notes?: string | null;
  metadata?: Record<string, unknown> | null;
  createdAt: string;
  updatedAt: string;
}

export interface CreateCropSeasonPayload {
  cropType: string;
  cropTypeAr?: string;
  season?: SeasonValue;
  sowingDate: string; // ISO 8601
  expectedHarvestDate?: string;
  seedVariety?: string;
  seedVarietyAr?: string;
  plantingDensityKgHa?: number;
  irrigationType?: string;
  notes?: string;
}

export interface UpdateCropSeasonPayload {
  cropType?: string;
  cropTypeAr?: string;
  season?: SeasonValue;
  sowingDate?: string;
  expectedHarvestDate?: string;
  actualHarvestDate?: string;
  seedVariety?: string;
  seedVarietyAr?: string;
  plantingDensityKgHa?: number;
  irrigationType?: string;
  yieldKgHa?: number;
  notes?: string;
  isCurrent?: boolean;
}

export interface EndCropSeasonPayload {
  endedAt?: string;
  endReason?: string;
  actualHarvestDate?: string;
  yieldKgHa?: number;
}

export interface CropSeasonListResponse {
  success: true;
  items: CropSeason[];
  total: number;
  limit: number;
  offset: number;
}

export interface CropSeasonRollup {
  cropSeasonId: string;
  totalOperations: number;
  totalHours: number;
  totalCost: number;
  currency: string;
  byType: Record<string, { count: number; hours: number; cost: number }>;
}

// ---------------------------------------------------------------------------
// API methods
// ---------------------------------------------------------------------------

export const cropSeasonsApi = {
  /** List seasons for a specific field (newest first). */
  async listByField(
    fieldId: string,
    filters?: { isCurrent?: boolean; limit?: number; offset?: number },
  ): Promise<CropSeasonListResponse> {
    const params = new URLSearchParams();
    if (typeof filters?.isCurrent === 'boolean')
      params.set('isCurrent', String(filters.isCurrent));
    if (filters?.limit != null) params.set('limit', String(filters.limit));
    if (filters?.offset != null) params.set('offset', String(filters.offset));
    const url = `${buildUrl(CROP_SEASON_ENDPOINTS.LIST_BY_FIELD, {
      fieldId,
    })}?${params.toString()}`;
    const res = await api.get(url);
    return res.data as CropSeasonListResponse;
  },

  /** Tenant-wide query (dashboards). */
  async listAll(filters?: {
    cropType?: string;
    isCurrent?: boolean;
    sowingAfter?: string;
    sowingBefore?: string;
    limit?: number;
    offset?: number;
  }): Promise<CropSeasonListResponse> {
    const params = new URLSearchParams();
    if (filters?.cropType) params.set('cropType', filters.cropType);
    if (typeof filters?.isCurrent === 'boolean')
      params.set('isCurrent', String(filters.isCurrent));
    if (filters?.sowingAfter) params.set('sowingAfter', filters.sowingAfter);
    if (filters?.sowingBefore) params.set('sowingBefore', filters.sowingBefore);
    if (filters?.limit != null) params.set('limit', String(filters.limit));
    if (filters?.offset != null) params.set('offset', String(filters.offset));
    const url = `${CROP_SEASON_ENDPOINTS.LIST}?${params.toString()}`;
    const res = await api.get(url);
    return res.data as CropSeasonListResponse;
  },

  async getById(cropSeasonId: string): Promise<CropSeason> {
    const url = buildUrl(CROP_SEASON_ENDPOINTS.GET, { cropSeasonId });
    const res = await api.get(url);
    return (res.data.data ?? res.data) as CropSeason;
  },

  /**
   * Start a new crop season on a field. The backend automatically closes
   * the previously active season inside the same transaction, so callers
   * don't need to orchestrate the two operations themselves.
   */
  async create(
    fieldId: string,
    payload: CreateCropSeasonPayload,
  ): Promise<CropSeason> {
    const url = buildUrl(CROP_SEASON_ENDPOINTS.CREATE, { fieldId });
    const res = await api.post(url, payload);
    return (res.data.data ?? res.data) as CropSeason;
  },

  async update(
    cropSeasonId: string,
    payload: UpdateCropSeasonPayload,
  ): Promise<CropSeason> {
    const url = buildUrl(CROP_SEASON_ENDPOINTS.UPDATE, { cropSeasonId });
    const res = await api.patch(url, payload);
    return (res.data.data ?? res.data) as CropSeason;
  },

  async end(
    cropSeasonId: string,
    payload: EndCropSeasonPayload = {},
  ): Promise<CropSeason> {
    const url = buildUrl(CROP_SEASON_ENDPOINTS.END, { cropSeasonId });
    const res = await api.post(url, payload);
    return (res.data.data ?? res.data) as CropSeason;
  },

  async remove(cropSeasonId: string): Promise<void> {
    const url = buildUrl(CROP_SEASON_ENDPOINTS.DELETE, { cropSeasonId });
    await api.delete(url);
  },

  /**
   * Per-season operation rollup (total hours + total cost + by-type
   * breakdown). Feeds the "الإجمالي قبل البذار" widget on the timeline
   * and the yield-prediction service's input features.
   */
  async rollup(cropSeasonId: string): Promise<CropSeasonRollup> {
    const url = buildUrl(CROP_SEASON_ENDPOINTS.ROLLUP, { cropSeasonId });
    const res = await api.get(url);
    return (res.data.data ?? res.data) as CropSeasonRollup;
  },
};
