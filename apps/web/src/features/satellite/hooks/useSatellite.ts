/**
 * Satellite Feature - React Hooks
 * خطافات React لميزة صور الأقمار الصناعية
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { satelliteApi } from '../api';
import type { SatelliteFilters } from '../types';

export const satelliteKeys = {
  all: ['satellite'] as const,
  lists: () => [...satelliteKeys.all, 'list'] as const,
  list: (filters?: SatelliteFilters) => [...satelliteKeys.lists(), filters] as const,
  detail: (id: string) => [...satelliteKeys.all, 'detail', id] as const,
  stats: () => [...satelliteKeys.all, 'stats'] as const,
  images: (fieldId: string) => [...satelliteKeys.all, 'images', fieldId] as const,
  timeSeries: (fieldId: string, indexType: string) =>
    [...satelliteKeys.all, 'timeseries', fieldId, indexType] as const,
  zones: (fieldId: string) => [...satelliteKeys.all, 'zones', fieldId] as const,
};

export function useSatelliteFields(filters?: SatelliteFilters) {
  return useQuery({
    queryKey: satelliteKeys.list(filters),
    queryFn: () => satelliteApi.getFields(filters),
    staleTime: 1000 * 60 * 10, // 10 minutes - satellite data updates less frequently
  });
}

export function useSatelliteFieldDetails(id: string) {
  return useQuery({
    queryKey: satelliteKeys.detail(id),
    queryFn: () => satelliteApi.getFieldById(id),
    enabled: !!id,
  });
}

export function useSatelliteStats() {
  return useQuery({
    queryKey: satelliteKeys.stats(),
    queryFn: () => satelliteApi.getStats(),
    staleTime: 1000 * 60 * 10,
  });
}

export function useSatelliteImages(
  fieldId: string,
  filters?: { dateFrom?: string; dateTo?: string }
) {
  return useQuery({
    queryKey: [...satelliteKeys.images(fieldId), filters],
    queryFn: () => satelliteApi.getImages(fieldId, filters),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 30, // 30 minutes
  });
}

export function useSatelliteTimeSeries(
  fieldId: string,
  indexType: string,
  period: { from: string; to: string }
) {
  return useQuery({
    queryKey: [...satelliteKeys.timeSeries(fieldId, indexType), period],
    queryFn: () => satelliteApi.getTimeSeries(fieldId, indexType, period),
    enabled: !!fieldId && !!indexType,
    staleTime: 1000 * 60 * 30,
  });
}

export function useSatelliteZoneAnalysis(fieldId: string) {
  return useQuery({
    queryKey: satelliteKeys.zones(fieldId),
    queryFn: () => satelliteApi.getZoneAnalysis(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 15,
  });
}

export function useRequestSatelliteCapture() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (fieldId: string) => satelliteApi.requestNewCapture(fieldId),
    onSuccess: (_: { requestId: string; estimatedTime: string }, fieldId: string) => {
      // Invalidate related queries after capture request
      queryClient.invalidateQueries({ queryKey: satelliteKeys.detail(fieldId) });
      queryClient.invalidateQueries({ queryKey: satelliteKeys.images(fieldId) });
    },
  });
}
