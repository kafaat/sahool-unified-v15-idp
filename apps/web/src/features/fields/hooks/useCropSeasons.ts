/**
 * useCropSeasons — React Query hooks for per-field crop season archive.
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  cropSeasonsApi,
  type CropSeason,
  type CreateCropSeasonPayload,
  type UpdateCropSeasonPayload,
  type EndCropSeasonPayload,
  type CropSeasonRollup,
} from '../api/crop-seasons-api';
import {
  fieldOperationsApi,
  type CreateFieldOperationPayload,
  type FieldOperation,
} from '../api/field-operations-api';

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

export const cropSeasonKeys = {
  all: ['crop-seasons'] as const,
  byField: (fieldId: string) =>
    [...cropSeasonKeys.all, 'field', fieldId] as const,
  detail: (id: string) => [...cropSeasonKeys.all, 'detail', id] as const,
  rollup: (id: string) => [...cropSeasonKeys.all, 'rollup', id] as const,
};

export const fieldOperationKeys = {
  all: ['field-operations'] as const,
  byField: (fieldId: string) =>
    [...fieldOperationKeys.all, 'field', fieldId] as const,
  detail: (id: string) => [...fieldOperationKeys.all, 'detail', id] as const,
};

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

/**
 * Fetch all crop seasons for a given field. Returns items sorted
 * newest-first (by sowing date desc).
 */
export function useCropSeasonsByField(
  fieldId: string | null | undefined,
  options?: { enabled?: boolean },
) {
  return useQuery({
    queryKey: cropSeasonKeys.byField(fieldId ?? ''),
    queryFn: () => cropSeasonsApi.listByField(fieldId!),
    enabled: !!fieldId && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 2, // 2 min
  });
}

/**
 * Fetch a single crop season by id.
 */
export function useCropSeason(cropSeasonId: string | null | undefined) {
  return useQuery({
    queryKey: cropSeasonKeys.detail(cropSeasonId ?? ''),
    queryFn: () => cropSeasonsApi.getById(cropSeasonId!),
    enabled: !!cropSeasonId,
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Per-season operation rollup (total hours + cost + breakdown).
 */
export function useCropSeasonRollup(cropSeasonId: string | null | undefined) {
  return useQuery<CropSeasonRollup>({
    queryKey: cropSeasonKeys.rollup(cropSeasonId ?? ''),
    queryFn: () => cropSeasonsApi.rollup(cropSeasonId!),
    enabled: !!cropSeasonId,
    staleTime: 1000 * 30, // 30s — operations change often during a season
  });
}

// ---------------------------------------------------------------------------
// Mutations: CropSeason
// ---------------------------------------------------------------------------

/**
 * Start a new crop season on a field. The backend closes the previous
 * active season automatically so callers don't race it here.
 */
export function useStartCropSeason(fieldId: string) {
  const qc = useQueryClient();
  return useMutation<CropSeason, Error, CreateCropSeasonPayload>({
    mutationFn: (payload) => cropSeasonsApi.create(fieldId, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: cropSeasonKeys.byField(fieldId) });
      qc.invalidateQueries({ queryKey: cropSeasonKeys.all });
    },
  });
}

/**
 * Partial update of a season. Invalidates both the detail and the
 * per-field list (so the list re-sorts / re-styles the "current" badge).
 */
export function useUpdateCropSeason(fieldId?: string) {
  const qc = useQueryClient();
  return useMutation<
    CropSeason,
    Error,
    { id: string; payload: UpdateCropSeasonPayload }
  >({
    mutationFn: ({ id, payload }) => cropSeasonsApi.update(id, payload),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: cropSeasonKeys.detail(updated.id) });
      if (fieldId) {
        qc.invalidateQueries({ queryKey: cropSeasonKeys.byField(fieldId) });
      } else {
        qc.invalidateQueries({ queryKey: cropSeasonKeys.all });
      }
    },
  });
}

/**
 * End an active season (soft close — row stays for history).
 */
export function useEndCropSeason(fieldId?: string) {
  const qc = useQueryClient();
  return useMutation<
    CropSeason,
    Error,
    { id: string; payload?: EndCropSeasonPayload }
  >({
    mutationFn: ({ id, payload }) => cropSeasonsApi.end(id, payload),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: cropSeasonKeys.detail(updated.id) });
      if (fieldId) {
        qc.invalidateQueries({ queryKey: cropSeasonKeys.byField(fieldId) });
      } else {
        qc.invalidateQueries({ queryKey: cropSeasonKeys.all });
      }
    },
  });
}

// ---------------------------------------------------------------------------
// Queries: FieldOperation
// ---------------------------------------------------------------------------

/**
 * Fetch all operations (plowing, land prep, ...) for a given field.
 */
export function useFieldOperations(
  fieldId: string | null | undefined,
  options?: { enabled?: boolean },
) {
  return useQuery({
    queryKey: fieldOperationKeys.byField(fieldId ?? ''),
    queryFn: () => fieldOperationsApi.listByField(fieldId!),
    enabled: !!fieldId && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 2,
  });
}

// ---------------------------------------------------------------------------
// Mutations: FieldOperation
// ---------------------------------------------------------------------------

/**
 * Record a new field operation. Invalidates the per-field op list AND the
 * per-season rollup (since totals may change).
 */
export function useRecordFieldOperation(fieldId: string) {
  const qc = useQueryClient();
  return useMutation<FieldOperation, Error, CreateFieldOperationPayload>({
    mutationFn: (payload) => fieldOperationsApi.create(fieldId, payload),
    onSuccess: (op) => {
      qc.invalidateQueries({ queryKey: fieldOperationKeys.byField(fieldId) });
      if (op.cropSeasonId) {
        qc.invalidateQueries({
          queryKey: cropSeasonKeys.rollup(op.cropSeasonId),
        });
      }
    },
  });
}
