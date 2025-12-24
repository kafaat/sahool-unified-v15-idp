/**
 * SAHOOL Fields Hook
 * خطاف الحقول
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { Field, FieldFormData, FieldFilters } from '../types';

async function fetchFields(filters?: FieldFilters): Promise<Field[]> {
  // TODO: Replace with actual API call
  // const params = new URLSearchParams(filters as any);
  // const response = await fetch(`/api/fields?${params}`);
  // return response.json();

  // Mock data
  return [
    {
      id: '1',
      name: 'North Field',
      nameAr: 'الحقل الشمالي',
      area: 5.5,
      crop: 'Wheat',
      cropAr: 'قمح',
      farmId: 'farm-1',
      polygon: {
        type: 'Polygon',
        coordinates: [[[44.2, 15.3], [44.21, 15.3], [44.21, 15.31], [44.2, 15.31], [44.2, 15.3]]],
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: '2',
      name: 'South Field',
      nameAr: 'الحقل الجنوبي',
      area: 3.2,
      crop: 'Corn',
      cropAr: 'ذرة',
      farmId: 'farm-1',
      polygon: {
        type: 'Polygon',
        coordinates: [[[44.2, 15.29], [44.21, 15.29], [44.21, 15.3], [44.2, 15.3], [44.2, 15.29]]],
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  ];
}

async function fetchFieldById(id: string): Promise<Field> {
  // TODO: Replace with actual API call
  // const response = await fetch(`/api/fields/${id}`);
  // return response.json();

  const fields = await fetchFields();
  const field = fields.find(f => f.id === id);
  if (!field) throw new Error('Field not found');
  return field;
}

async function createField(data: FieldFormData): Promise<Field> {
  // TODO: Replace with actual API call
  // const response = await fetch('/api/fields', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify(data),
  // });
  // return response.json();

  return {
    id: Math.random().toString(36),
    ...data,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  } as Field;
}

async function updateField(id: string, data: Partial<FieldFormData>): Promise<Field> {
  // TODO: Replace with actual API call
  // const response = await fetch(`/api/fields/${id}`, {
  //   method: 'PATCH',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify(data),
  // });
  // return response.json();

  const field = await fetchFieldById(id);
  return { ...field, ...data, updatedAt: new Date().toISOString() };
}

async function deleteField(id: string): Promise<void> {
  // TODO: Replace with actual API call
  // await fetch(`/api/fields/${id}`, { method: 'DELETE' });
  return Promise.resolve();
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
