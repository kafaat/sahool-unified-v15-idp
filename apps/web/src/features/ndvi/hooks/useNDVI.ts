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
 * Hook to fetch interpreted indices with recommendations
 * خطاف لجلب تفسير المؤشرات مع التوصيات
 */
export function useInterpretIndices(
  fieldId: string,
  options?: { date?: string; enabled?: boolean }
) {
  return useQuery({
    queryKey: indicesKeys.interpret(fieldId),
    queryFn: () => vegetationIndicesApi.interpretIndices(fieldId, options?.date),
    enabled: !!fieldId && (options?.enabled ?? true),
    staleTime: 1000 * 60 * 15,
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
