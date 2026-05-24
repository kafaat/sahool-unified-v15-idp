/**
 * Farms Feature - React Hooks
 * خطافات React لميزة المزارع
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { farmsApi } from '../api';
import type { Farm, FarmFilters, FarmFormData } from '../types';

export const farmKeys = {
  all: ['farms'] as const,
  lists: () => [...farmKeys.all, 'list'] as const,
  list: (filters?: FarmFilters) => [...farmKeys.lists(), filters] as const,
  detail: (id: string) => [...farmKeys.all, 'detail', id] as const,
  stats: () => [...farmKeys.all, 'stats'] as const,
};

export function useFarms(filters?: FarmFilters) {
  return useQuery({
    queryKey: farmKeys.list(filters),
    queryFn: () => farmsApi.getFarms(filters),
    staleTime: 0,
    gcTime: 0,
    refetchOnMount: 'always',
    refetchOnWindowFocus: true,
  });
}

export function useFarm(id: string) {
  return useQuery({
    queryKey: farmKeys.detail(id),
    queryFn: () => farmsApi.getFarmById(id),
    enabled: !!id,
  });
}

export function useFarmStats() {
  return useQuery({
    queryKey: farmKeys.stats(),
    queryFn: () => farmsApi.getStats(),
    staleTime: 1000 * 60 * 5,
  });
}

export function useCreateFarm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: FarmFormData) => farmsApi.createFarm(data),
    onSuccess: async (newFarm: Farm) => {
      // Patch cache immediately so the new farm appears without waiting for a round-trip.
      qc.setQueriesData<Farm[]>(
        { queryKey: farmKeys.lists() },
        (old) => (old ? [newFarm, ...old] : [newFarm]),
      );
      // Invalidate all farm queries — triggers a background refetch on active observers
      // (the mounted useFarms hook), confirming the list with server truth.
      await qc.invalidateQueries({ queryKey: farmKeys.all });
    },
  });
}

export function useUpdateFarm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<FarmFormData> }) =>
      farmsApi.updateFarm(id, data),
    onSuccess: async (updatedFarm: Farm) => {
      qc.setQueriesData<Farm[]>(
        { queryKey: farmKeys.lists() },
        (old) => old?.map((f) => (f.id === updatedFarm.id ? updatedFarm : f)),
      );
      qc.setQueryData(farmKeys.detail(updatedFarm.id), updatedFarm);
      await qc.invalidateQueries({ queryKey: farmKeys.all });
    },
  });
}

export function useDeleteFarm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => farmsApi.deleteFarm(id),
    onSuccess: async (_, id) => {
      qc.setQueriesData<Farm[]>(
        { queryKey: farmKeys.lists() },
        (old) => old?.filter((f) => f.id !== id),
      );
      qc.removeQueries({ queryKey: farmKeys.detail(id) });
      await qc.invalidateQueries({ queryKey: farmKeys.all });
    },
  });
}
