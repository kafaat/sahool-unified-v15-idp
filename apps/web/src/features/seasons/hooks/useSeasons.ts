/**
 * Seasons Feature - React Hooks
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { seasonsApi } from '../api';
import type { SeasonFilters, SeasonFormData } from '../types';

export const seasonKeys = {
  all: ['seasons'] as const,
  lists: () => [...seasonKeys.all, 'list'] as const,
  list: (filters?: SeasonFilters) => [...seasonKeys.lists(), filters] as const,
  detail: (id: string) => [...seasonKeys.all, 'detail', id] as const,
  stats: () => [...seasonKeys.all, 'stats'] as const,
};

export function useSeasons(filters?: SeasonFilters) {
  return useQuery({
    queryKey: seasonKeys.list(filters),
    queryFn: () => seasonsApi.getSeasons(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useSeason(id: string) {
  return useQuery({
    queryKey: seasonKeys.detail(id),
    queryFn: () => seasonsApi.getSeasonById(id),
    enabled: !!id,
  });
}

export function useSeasonStats() {
  return useQuery({
    queryKey: seasonKeys.stats(),
    queryFn: () => seasonsApi.getStats(),
    staleTime: 1000 * 60 * 5,
  });
}

export function useCreateSeason() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SeasonFormData) => seasonsApi.createSeason(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: seasonKeys.lists() });
      qc.invalidateQueries({ queryKey: seasonKeys.stats() });
    },
  });
}

export function useUpdateSeason() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<SeasonFormData> }) =>
      seasonsApi.updateSeason(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: seasonKeys.lists() });
      qc.invalidateQueries({ queryKey: seasonKeys.detail(id) });
    },
  });
}

export function useDeleteSeason() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => seasonsApi.deleteSeason(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: seasonKeys.lists() });
      qc.removeQueries({ queryKey: seasonKeys.detail(id) });
      qc.invalidateQueries({ queryKey: seasonKeys.stats() });
    },
  });
}
