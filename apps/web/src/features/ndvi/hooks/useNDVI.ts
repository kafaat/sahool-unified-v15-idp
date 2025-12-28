/**
 * NDVI Feature - React Hooks
 * خطافات React لميزة مؤشر NDVI
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ndviApi, type NDVIFilters } from '../api';

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
 */
export function useNDVIMap(fieldId: string, date?: string) {
  return useQuery({
    queryKey: ndviKeys.map(fieldId, date),
    queryFn: () => ndviApi.getNDVIMap(fieldId, date),
    enabled: !!fieldId,
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
