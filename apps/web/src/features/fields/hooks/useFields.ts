/**
 * SAHOOL Fields Hook
 * خطاف الحقول
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type { Field, FieldFormData, FieldFilters } from '../types';

async function fetchFields(filters?: FieldFilters): Promise<Field[]> {
  const params: Record<string, string> = {};

  if (filters?.farmId) params.farm_id = filters.farmId;
  if (filters?.crop) params.crop_type = filters.crop;
  if (filters?.status) params.status = filters.status;
  if (filters?.search) params.search = filters.search;

  const response = await apiClient.get<{
    fields: Array<{
      field_id: string;
      name: string;
      name_ar?: string;
      farm_id: string;
      area_hectares: number;
      crop_type?: string;
      boundary?: {
        type: 'Polygon';
        coordinates: number[][][];
      };
      created_at: string;
      updated_at: string;
    }>;
  }>('http://localhost:3000/fields', { params });

  // Transform backend data to frontend format
  return response.data.fields?.map(field => ({
    id: field.field_id,
    name: field.name,
    nameAr: field.name_ar || '',
    area: field.area_hectares,
    crop: field.crop_type,
    cropAr: field.crop_type, // Backend doesn't have separate Arabic crop names
    farmId: field.farm_id,
    polygon: field.boundary,
    createdAt: field.created_at,
    updatedAt: field.updated_at,
  })) || [];
}

async function fetchFieldById(id: string): Promise<Field> {
  const response = await apiClient.get<{
    field_id: string;
    name: string;
    name_ar?: string;
    farm_id: string;
    area_hectares: number;
    crop_type?: string;
    boundary?: {
      type: 'Polygon';
      coordinates: number[][][];
    };
    created_at: string;
    updated_at: string;
  }>(`http://localhost:3000/fields/${id}`);

  const field = response.data;
  return {
    id: field.field_id,
    name: field.name,
    nameAr: field.name_ar || '',
    area: field.area_hectares,
    crop: field.crop_type,
    cropAr: field.crop_type,
    farmId: field.farm_id,
    polygon: field.boundary,
    createdAt: field.created_at,
    updatedAt: field.updated_at,
  };
}

async function createField(data: FieldFormData): Promise<Field> {
  const payload = {
    name: data.name,
    name_ar: data.nameAr,
    farm_id: data.farmId || 'default-farm',
    area_hectares: data.area,
    crop_type: data.crop,
    boundary: data.polygon,
  };

  const response = await apiClient.post<{
    field_id: string;
    name: string;
    name_ar?: string;
    farm_id: string;
    area_hectares: number;
    crop_type?: string;
    boundary?: {
      type: 'Polygon';
      coordinates: number[][][];
    };
    created_at: string;
    updated_at: string;
  }>('http://localhost:3000/fields', payload);

  const field = response.data;
  return {
    id: field.field_id,
    name: field.name,
    nameAr: field.name_ar || '',
    area: field.area_hectares,
    crop: field.crop_type,
    cropAr: field.crop_type,
    farmId: field.farm_id,
    polygon: field.boundary,
    createdAt: field.created_at,
    updatedAt: field.updated_at,
  };
}

async function updateField(id: string, data: Partial<FieldFormData>): Promise<Field> {
  const payload: Record<string, unknown> = {};

  if (data.name !== undefined) payload.name = data.name;
  if (data.nameAr !== undefined) payload.name_ar = data.nameAr;
  if (data.area !== undefined) payload.area_hectares = data.area;
  if (data.crop !== undefined) payload.crop_type = data.crop;
  if (data.polygon !== undefined) payload.boundary = data.polygon;

  const response = await apiClient.patch<{
    field_id: string;
    name: string;
    name_ar?: string;
    farm_id: string;
    area_hectares: number;
    crop_type?: string;
    boundary?: {
      type: 'Polygon';
      coordinates: number[][][];
    };
    created_at: string;
    updated_at: string;
  }>(`http://localhost:3000/fields/${id}`, payload);

  const field = response.data;
  return {
    id: field.field_id,
    name: field.name,
    nameAr: field.name_ar || '',
    area: field.area_hectares,
    crop: field.crop_type,
    cropAr: field.crop_type,
    farmId: field.farm_id,
    polygon: field.boundary,
    createdAt: field.created_at,
    updatedAt: field.updated_at,
  };
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
