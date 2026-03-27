/**
 * Crops Feature - React Hooks
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cropsApi } from '../api';
import type { CropFilters, CropFormData } from '../types';

export const cropKeys = {
  all: ['crops'] as const,
  lists: () => [...cropKeys.all, 'list'] as const,
  list: (filters?: CropFilters) => [...cropKeys.lists(), filters] as const,
  detail: (id: string) => [...cropKeys.all, 'detail', id] as const,
  stats: () => [...cropKeys.all, 'stats'] as const,
};

export function useCrops(filters?: CropFilters) {
  return useQuery({
    queryKey: cropKeys.list(filters),
    queryFn: () => cropsApi.getCrops(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useCrop(id: string) {
  return useQuery({
    queryKey: cropKeys.detail(id),
    queryFn: () => cropsApi.getCropById(id),
    enabled: !!id,
  });
}

export function useCropStats() {
  return useQuery({
    queryKey: cropKeys.stats(),
    queryFn: () => cropsApi.getStats(),
    staleTime: 1000 * 60 * 5,
  });
}

export function useCreateCrop() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CropFormData) => cropsApi.createCrop(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: cropKeys.lists() });
      qc.invalidateQueries({ queryKey: cropKeys.stats() });
    },
  });
}

export function useUpdateCrop() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CropFormData> }) =>
      cropsApi.updateCrop(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: cropKeys.lists() });
      qc.invalidateQueries({ queryKey: cropKeys.detail(id) });
    },
  });
}

export function useDeleteCrop() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => cropsApi.deleteCrop(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: cropKeys.lists() });
      qc.removeQueries({ queryKey: cropKeys.detail(id) });
      qc.invalidateQueries({ queryKey: cropKeys.stats() });
    },
  });
}
