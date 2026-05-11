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
      // Cancel any in-flight fetches so they don't overwrite the optimistic update.
      await qc.cancelQueries({ queryKey: farmKeys.all });
      // Patch the cache immediately so the new farm appears without a round-trip.
      qc.setQueriesData<Farm[]>(
        { queryKey: farmKeys.lists() },
        (old) => (old ? [newFarm, ...old] : [newFarm]),
      );
      // Force an immediate refetch (not just mark stale) so the list is confirmed
      // from the server. refetchQueries triggers even if no background fetch is pending.
      await qc.refetchQueries({ queryKey: farmKeys.all });
    },
  });
}

export function useUpdateFarm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<FarmFormData> }) =>
      farmsApi.updateFarm(id, data),
    onSuccess: async (updatedFarm: Farm) => {
      await qc.cancelQueries({ queryKey: farmKeys.all });
      qc.setQueriesData<Farm[]>(
        { queryKey: farmKeys.lists() },
        (old) => old?.map((f) => (f.id === updatedFarm.id ? updatedFarm : f)),
      );
      qc.setQueryData(farmKeys.detail(updatedFarm.id), updatedFarm);
      await qc.refetchQueries({ queryKey: farmKeys.all });
    },
  });
}

export function useDeleteFarm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => farmsApi.deleteFarm(id),
    onSuccess: async (_, id) => {
      await qc.cancelQueries({ queryKey: farmKeys.all });
      qc.setQueriesData<Farm[]>(
        { queryKey: farmKeys.lists() },
        (old) => old?.filter((f) => f.id !== id),
      );
      qc.removeQueries({ queryKey: farmKeys.detail(id) });
      await qc.refetchQueries({ queryKey: farmKeys.all });
    },
  });
}
