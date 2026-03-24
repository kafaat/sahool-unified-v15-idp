/**
 * Farms Feature - React Hooks
 * خطافات React لميزة المزارع
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { farmsApi } from '../api';
import type { FarmFilters, FarmFormData } from '../types';

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
    staleTime: 1000 * 60 * 5,
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
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: farmKeys.lists() });
      qc.invalidateQueries({ queryKey: farmKeys.stats() });
    },
  });
}

export function useUpdateFarm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<FarmFormData> }) =>
      farmsApi.updateFarm(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: farmKeys.lists() });
      qc.invalidateQueries({ queryKey: farmKeys.detail(id) });
    },
  });
}

export function useDeleteFarm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => farmsApi.deleteFarm(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: farmKeys.lists() });
      qc.removeQueries({ queryKey: farmKeys.detail(id) });
      qc.invalidateQueries({ queryKey: farmKeys.stats() });
    },
  });
}
