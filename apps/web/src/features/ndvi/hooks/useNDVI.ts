/**
 * NDVI & Vegetation Indices Feature - React Hooks
 * خطافات React لميزة مؤشرات NDVI والغطاء النباتي
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ndviApi, vegetationIndicesApi, type NDVIFilters } from '../api';
import type { VegetationIndex } from '../types';

// Query Keys
export const ndviKeys = {
  all: ['ndvi'] as const,
  latest: (filters?: NDVIFilters) => [...ndviKeys.all, 'latest', filters] as const,
  field: (fieldId: string) => [...ndviKeys.all, 'field', fieldId] as const,
  timeSeries: (fieldId: string, start?: string, end?: string) =>
    [...ndviKeys.all, 'timeseries', fieldId, start, end] as const,
  map: (fieldId: string, date?: string) => [...ndviKeys.all, 'map', fieldId, date] as const,
  stats: (governorate?: string) => [...ndviKeys.all, 'stats', governorate] as const,
};

/**
 * Hook to fetch latest NDVI for all fields
 */
export function useLatestNDVI(filters?: NDVIFilters) {
  return useQuery({
    queryKey: ndviKeys.latest(filters),
    queryFn: () => ndviApi.getLatestNDVI(filters),
    staleTime: 1000 * 60 * 15, // 15 minutes (satellite data doesn't change often)
    refetchInterval: 1000 * 60 * 30, // Refetch every 30 minutes
  });
}

/**
 * Hook to fetch NDVI for specific field
 */
export function useFieldNDVI(fieldId: string) {
  return useQuery({
    queryKey: ndviKeys.field(fieldId),
    queryFn: () => ndviApi.getFieldNDVI(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 15,
  });
}

/**
 * Hook to fetch NDVI time series
 */
export function useNDVITimeSeries(fieldId: string, startDate?: string, endDate?: string) {
  return useQuery({
    queryKey: ndviKeys.timeSeries(fieldId, startDate, endDate),
    queryFn: () => ndviApi.getNDVITimeSeries(fieldId, startDate, endDate),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 30,
  });
}

/**
 * Hook to fetch NDVI map data
 * @param enabled - additional guard; defaults to true. Pass false to suppress the fetch
 *   (e.g. when the active vegetation index is not "ndvi").
 */
export function useNDVIMap(fieldId: string, date?: string, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ndviKeys.map(fieldId, date),
    queryFn: () => ndviApi.getNDVIMap(fieldId, date),
    enabled: !!fieldId && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}

/**
 * Hook to fetch regional NDVI statistics
 */
export function useRegionalNDVIStats(governorate?: string) {
  return useQuery({
    queryKey: ndviKeys.stats(governorate),
    queryFn: () => ndviApi.getRegionalStats(governorate),
    staleTime: 1000 * 60 * 30,
  });
}

/**
 * Hook to request new NDVI analysis
 */
export function useRequestNDVIAnalysis() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (fieldId: string) => ndviApi.requestNDVIAnalysis(fieldId),
    onSuccess: (_: { jobId: string; status: string }, fieldId: string) => {
      // Invalidate related queries after analysis is requested
      queryClient.invalidateQueries({ queryKey: ndviKeys.field(fieldId) });
    },
  });
}

/**
 * Hook to compare NDVI between dates
 */
export function useNDVIComparison(fieldId: string, date1: string, date2: string) {
  return useQuery({
    queryKey: [...ndviKeys.all, 'compare', fieldId, date1, date2],
    queryFn: () => ndviApi.compareNDVI(fieldId, date1, date2),
    enabled: !!fieldId && !!date1 && !!date2,
  });
}

// =============================================================================
// Vegetation Indices Hooks (all 41 indices)
// خطافات المؤشرات النباتية (41 مؤشر)
// =============================================================================

export const indicesKeys = {
  all: ['vegetation-indices'] as const,
  field: (fieldId: string, indexNames?: VegetationIndex[]) =>
    [...indicesKeys.all, 'field', fieldId, indexNames ? [...indexNames].sort().join(',') : undefined] as const,
  specific: (fieldId: string, indexName: string) =>
    [...indicesKeys.all, 'specific', fieldId, indexName] as const,
  interpret: (fieldId: string) =>
    [...indicesKeys.all, 'interpret', fieldId] as const,
  timeSeries: (fieldId: string, indexName: string, start?: string, end?: string) =>
    [...indicesKeys.all, 'timeseries', fieldId, indexName, start, end] as const,
  map: (fieldId: string, indexName: string, date?: string) =>
    [...indicesKeys.all, 'map', fieldId, indexName, date] as const,
  pixel: (fieldId: string, lat: number | null, lon: number | null, date?: string) =>
    [...indicesKeys.all, 'pixel', fieldId, lat, lon, date] as const,
  composite: (
    fieldId: string,
    indexName: string,
    stepDays?: number,
    start?: string,
    end?: string,
    stat?: string,
  ) => [...indicesKeys.all, 'composite', fieldId, indexName, stepDays, start, end, stat] as const,
  filmstrip: (
    fieldId: string,
    indexName: string,
    stepDays?: number,
    start?: string,
    end?: string,
  ) => [...indicesKeys.all, 'filmstrip', fieldId, indexName, stepDays, start, end] as const,
  multiCompare: (
    fieldId: string,
    indexName: string,
    signature: string,
  ) => [...indicesKeys.all, 'multi-compare', fieldId, indexName, signature] as const,
};

/**
 * Hook to fetch all vegetation indices for a field
 * خطاف لجلب جميع المؤشرات النباتية لحقل
 */
export function useFieldIndices(
  fieldId: string,
  indexNames?: VegetationIndex[],
  options?: { date?: string; enabled?: boolean }
) {
  return useQuery({
    queryKey: indicesKeys.field(fieldId, indexNames),
    queryFn: () => vegetationIndicesApi.getFieldIndices(fieldId, indexNames, options?.date),
    enabled: !!fieldId && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 15, // 15 minutes
  });
}

/**
 * Hook to fetch a specific vegetation index for a field
 * خطاف لجلب مؤشر نباتي محدد لحقل
 */
export function useSpecificIndex(
  fieldId: string,
  indexName: VegetationIndex | string,
  options?: { date?: string; enabled?: boolean }
) {
  return useQuery({
    queryKey: indicesKeys.specific(fieldId, indexName),
    queryFn: () => vegetationIndicesApi.getSpecificIndex(fieldId, indexName, options?.date),
    enabled: !!fieldId && !!indexName && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 15,
  });
}

/**
 * Hook to fetch interpreted indices with recommendations.
 * خطاف لجلب تفسير المؤشرات مع التوصيات
 *
 * NOTE: the backend /v1/indices/interpret endpoint is POST with a JSON body.
 * Callers MUST supply `indices` (the pre-computed index values). The query is
 * only enabled when both `fieldId` and a non-empty `indices` map are provided.
 */
export function useInterpretIndices(
  fieldId: string,
  indices: Record<string, number> | undefined,
  options?: {
    cropType?: string;
    growthStage?: string;
    enabled?: boolean;
  }
) {
  const hasIndices = !!indices && Object.keys(indices).length > 0;
  return useQuery({
    queryKey: [
      ...indicesKeys.interpret(fieldId),
      indices ? Object.keys(indices).sort().join(',') : undefined,
      options?.cropType,
      options?.growthStage,
    ],
    queryFn: () =>
      vegetationIndicesApi.interpretIndices(
        fieldId,
        indices ?? {},
        options?.cropType,
        options?.growthStage,
      ),
    enabled: !!fieldId && hasIndices && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 15,
  });
}

/**
 * Hook to fetch raster-tile metadata for a mappable vegetation index.
 * خطاف لجلب بيانات الطبقة النقطية لمؤشر نباتي
 *
 * Use this in place of `useNDVIMap` when the map supports switching
 * between indices (NDVI / NDRE / NDWI / EVI / SAVI / LAI). The hook
 * caches per `(fieldId, indexName, date)` triple so the tile layer
 * can swap indices without re-fetching already-loaded layers.
 */
export function useIndexMap(
  fieldId: string,
  indexName: VegetationIndex | string,
  options?: { date?: string; enabled?: boolean }
) {
  return useQuery({
    queryKey: indicesKeys.map(fieldId, String(indexName), options?.date),
    queryFn: () => vegetationIndicesApi.getIndexMap(fieldId, indexName, options?.date),
    enabled: !!fieldId && !!indexName && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 60, // 1 hour — satellite tiles rarely change mid-day
  });
}

/**
 * Hook for click-to-inspect: all indices at a specific pixel.
 * خطاف فحص البكسل: كل المؤشرات عند نقطة محددة
 *
 * Enabled only when valid coordinates are supplied, so it doesn't
 * fire until the user actually clicks the map.
 */
export function usePixelInspection(
  fieldId: string,
  coords: { lat: number; lon: number } | null,
  options?: {
    date?: string;
    indices?: Array<VegetationIndex | string>;
    enabled?: boolean;
  }
) {
  // Use `null` (not NaN) as the placeholder when coords are missing —
  // React Query's structural hashing serialises NaN to `null` anyway,
  // and being explicit removes the cache-collision risk Copilot flagged
  // in review #1704 (feedback round 2). We also bind `lat`/`lon` once
  // to the same guarded values queryKey uses, dropping the `coords!`
  // non-null assertion from queryFn.
  const lat = coords?.lat ?? null;
  const lon = coords?.lon ?? null;
  return useQuery({
    queryKey: indicesKeys.pixel(fieldId, lat, lon, options?.date),
    queryFn: () =>
      vegetationIndicesApi.getPixelInspection(fieldId, lat as number, lon as number, {
        date: options?.date,
        indices: options?.indices,
      }),
    enabled:
      !!fieldId && lat !== null && lon !== null && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 15,
  });
}

/**
 * Hook to fetch an N-day composite for a mappable index.
 * خطاف لجلب التركيب الزمني لكل N يوم
 */
export function useIndexComposite(
  fieldId: string,
  indexName: VegetationIndex | string,
  options?: {
    stepDays?: number;
    start?: string;
    end?: string;
    stat?: 'median' | 'mean';
    enabled?: boolean;
  }
) {
  return useQuery({
    queryKey: indicesKeys.composite(
      fieldId,
      String(indexName),
      options?.stepDays,
      options?.start,
      options?.end,
      options?.stat,
    ),
    queryFn: () =>
      vegetationIndicesApi.getIndexComposite(fieldId, indexName, {
        stepDays: options?.stepDays,
        start: options?.start,
        end: options?.end,
        stat: options?.stat,
      }),
    enabled: !!fieldId && !!indexName && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 60,
  });
}

/**
 * Hook to fetch filmstrip frames for a mappable index.
 * خطاف لجلب شريط الصور لمؤشر قابل للعرض
 */
export function useIndexFilmstrip(
  fieldId: string,
  indexName: VegetationIndex | string,
  options?: {
    stepDays?: number;
    start?: string;
    end?: string;
    enabled?: boolean;
  }
) {
  return useQuery({
    queryKey: indicesKeys.filmstrip(
      fieldId,
      String(indexName),
      options?.stepDays,
      options?.start,
      options?.end,
    ),
    queryFn: () =>
      vegetationIndicesApi.getIndexFilmstrip(fieldId, indexName, {
        stepDays: options?.stepDays,
        start: options?.start,
        end: options?.end,
      }),
    enabled: !!fieldId && !!indexName && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 60,
  });
}

/**
 * Hook for N-date multi-date comparison (POST).
 * خطاف لمقارنة متعددة التواريخ
 */
export function useMultiDateCompare(
  fieldId: string,
  indexName: VegetationIndex | string,
  body: import('../api').MultiDateCompareRequest | null,
  options?: { enabled?: boolean }
) {
  const signature = body ? JSON.stringify(body) : 'none';
  return useQuery({
    queryKey: indicesKeys.multiCompare(fieldId, String(indexName), signature),
    queryFn: () =>
      vegetationIndicesApi.multiDateCompare(fieldId, indexName, body!),
    enabled:
      !!fieldId && !!indexName && !!body && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 30,
  });
}

/**
 * Hook to fetch time series data for a specific vegetation index
 * خطاف لجلب بيانات السلاسل الزمنية لمؤشر نباتي محدد
 */
export function useIndexTimeSeries(
  fieldId: string,
  indexName: VegetationIndex | string,
  dateRange?: { startDate?: string; endDate?: string },
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: indicesKeys.timeSeries(
      fieldId,
      indexName,
      dateRange?.startDate,
      dateRange?.endDate
    ),
    queryFn: () => vegetationIndicesApi.getTimeSeries(fieldId, indexName, dateRange),
    enabled: !!fieldId && !!indexName && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 30, // 30 minutes
  });
}
