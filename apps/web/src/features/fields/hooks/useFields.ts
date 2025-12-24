/**
 * SAHOOL Fields Hook
 * خطاف الحقول
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type { Field, FieldFormData, FieldFilters } from '../types';

async function fetchFields(filters?: FieldFilters): Promise<Field[]> {
  const params: Record<string, string> = {};

  if (filters?.farm_id) params.farm_id = filters.farm_id;
  if (filters?.crop) params.crop = filters.crop;
  if (filters?.status) params.status = filters.status;
  if (filters?.search) params.search = filters.search;

  const response = await apiClient.get<{
    fields: Array<{
      id: string;
      name: string;
      name_ar?: string;
      farm_id: string;
      area: number;
      crop?: string;
      crop_ar?: string;
      description?: string;
      description_ar?: string;
      polygon?: {
        type: 'Polygon';
        coordinates: number[][][];
      };
      status: string;
      created_at?: string;
      updated_at?: string;
    }>;
  }>('http://localhost:3000/fields', { params });

  return response.data.fields || [];
}

async function fetchFieldById(id: string): Promise<Field> {
  const response = await apiClient.get<Field>(`http://localhost:3000/fields/${id}`);
  return response.data;
}

async function createField(data: FieldFormData): Promise<Field> {
  const payload = {
    name: data.name,
    name_ar: data.name_ar,
    farm_id: data.farm_id || 'default-farm',
    area: data.area,
    crop: data.crop,
    crop_ar: data.crop_ar,
    description: data.description,
    description_ar: data.description_ar,
    polygon: data.polygon,
    status: 'active',
  };

  const response = await apiClient.post<Field>('http://localhost:3000/fields', payload);
  return response.data;
}

async function updateField(id: string, data: Partial<FieldFormData>): Promise<Field> {
  const payload: Record<string, unknown> = {};

  if (data.name !== undefined) payload.name = data.name;
  if (data.name_ar !== undefined) payload.name_ar = data.name_ar;
  if (data.area !== undefined) payload.area = data.area;
  if (data.crop !== undefined) payload.crop = data.crop;
  if (data.crop_ar !== undefined) payload.crop_ar = data.crop_ar;
  if (data.description !== undefined) payload.description = data.description;
  if (data.description_ar !== undefined) payload.description_ar = data.description_ar;
  if (data.polygon !== undefined) payload.polygon = data.polygon;

  const response = await apiClient.patch<Field>(`http://localhost:3000/fields/${id}`, payload);
  return response.data;
}

async function deleteField(id: string): Promise<void> {
  await apiClient.delete(`http://localhost:3000/fields/${id}`);
}

export function useFields(filters?: FieldFilters) {
  return useQuery({
    queryKey: ['fields', filters],
    queryFn: () => fetchFields(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useField(id: string) {
  return useQuery({
    queryKey: ['fields', id],
    queryFn: () => fetchFieldById(id),
    enabled: !!id,
    staleTime: 2 * 60 * 1000,
  });
}

export function useCreateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createField,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fields'] });
    },
  });
}

export function useUpdateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<FieldFormData> }) =>
      updateField(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['fields'] });
      queryClient.invalidateQueries({ queryKey: ['fields', variables.id] });
    },
  });
}

export function useDeleteField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteField,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fields'] });
    },
  });
}
