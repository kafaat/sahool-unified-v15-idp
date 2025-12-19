/**
 * Field Map Feature - React Hooks
 * خطافات React لميزة خريطة الحقول
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fieldMapApi, type Field, type FieldCreate, type FieldUpdate, type FieldFilters } from '../api';

// Query Keys
export const fieldKeys = {
  all: ['fields'] as const,
  lists: () => [...fieldKeys.all, 'list'] as const,
  list: (filters: FieldFilters) => [...fieldKeys.lists(), filters] as const,
  details: () => [...fieldKeys.all, 'detail'] as const,
  detail: (id: string) => [...fieldKeys.details(), id] as const,
  geojson: (filters?: FieldFilters) => [...fieldKeys.all, 'geojson', filters] as const,
  stats: () => [...fieldKeys.all, 'stats'] as const,
};

/**
 * Hook to fetch all fields
 */
export function useFields(filters?: FieldFilters) {
  return useQuery({
    queryKey: fieldKeys.list(filters || {}),
    queryFn: () => fieldMapApi.getFields(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch single field
 */
export function useField(id: string) {
  return useQuery({
    queryKey: fieldKeys.detail(id),
    queryFn: () => fieldMapApi.getFieldById(id),
    enabled: !!id,
  });
}

/**
 * Hook to fetch fields as GeoJSON
 */
export function useFieldsGeoJSON(filters?: FieldFilters) {
  return useQuery({
    queryKey: fieldKeys.geojson(filters),
    queryFn: () => fieldMapApi.getFieldsGeoJSON(filters),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook to fetch field statistics
 */
export function useFieldStats() {
  return useQuery({
    queryKey: fieldKeys.stats(),
    queryFn: () => fieldMapApi.getFieldStats(),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}

/**
 * Hook to create a new field
 */
export function useCreateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: FieldCreate) => fieldMapApi.createField(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fieldKeys.lists() });
      queryClient.invalidateQueries({ queryKey: fieldKeys.stats() });
    },
  });
}

/**
 * Hook to update a field
 */
export function useUpdateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: FieldUpdate }) =>
      fieldMapApi.updateField(id, data),
    onSuccess: (updatedField: Field) => {
      queryClient.invalidateQueries({ queryKey: fieldKeys.lists() });
      queryClient.setQueryData(fieldKeys.detail(updatedField.id), updatedField);
    },
  });
}

/**
 * Hook to delete a field
 */
export function useDeleteField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => fieldMapApi.deleteField(id),
    onSuccess: (_: void, id: string) => {
      queryClient.invalidateQueries({ queryKey: fieldKeys.lists() });
      queryClient.removeQueries({ queryKey: fieldKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: fieldKeys.stats() });
    },
  });
}
