/**
 * SAHOOL Tasks Hook
 * خطاف المهام
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type { Task, TaskFormData, TaskFilters, TaskStatus } from '../types';

// Map frontend status to backend status (if needed)
const mapStatusToBackend = (status: TaskStatus): string => {
  // Status values are now aligned, no mapping needed
  return status;
};

// Map backend status to frontend status (if needed)
const mapStatusToFrontend = (status: string): TaskStatus => {
  // Status values are now aligned, no mapping needed
  return status as TaskStatus;
};

async function fetchTasks(filters?: TaskFilters): Promise<Task[]> {
  const params: Record<string, string> = {};

  if (filters?.field_id) params.field_id = filters.field_id;
  if (filters?.status) params.status = mapStatusToBackend(filters.status);
  if (filters?.priority) params.priority = filters.priority;
  if (filters?.assigned_to) params.assigned_to = filters.assigned_to;
  if (filters?.search) params.search = filters.search;

  const response = await apiClient.get<{
    tasks: Array<{
      task_id: string;
      tenant_id: string;
      title: string;
      title_ar?: string;
      description?: string;
      description_ar?: string;
      status: string;
      priority: string;
      due_date?: string;
      field_id: string;
      assigned_to?: string;
      created_at: string;
      updated_at: string;
    }>;
  }>('http://localhost:8103/api/v1/tasks', { params });

  // Transform backend data to frontend format
  return response.data.tasks?.map(task => ({
    id: task.task_id,
    tenant_id: task.tenant_id,
    title: task.title,
    title_ar: task.title_ar,
    description: task.description,
    description_ar: task.description_ar,
    status: mapStatusToFrontend(task.status),
    priority: task.priority as 'urgent' | 'high' | 'medium' | 'low',
    due_date: task.due_date,
    field_id: task.field_id,
    assigned_to: task.assigned_to,
    created_at: task.created_at,
    updated_at: task.updated_at,
  })) || [];
}

async function fetchTaskById(id: string): Promise<Task> {
  const response = await apiClient.get<{
    task_id: string;
    tenant_id: string;
    title: string;
    title_ar?: string;
    description?: string;
    description_ar?: string;
    status: string;
    priority: string;
    due_date?: string;
    field_id: string;
    assigned_to?: string;
    created_at: string;
    updated_at: string;
  }>(`http://localhost:8103/api/v1/tasks/${id}`);

  const task = response.data;
  return {
    id: task.task_id,
    tenant_id: task.tenant_id,
    title: task.title,
    title_ar: task.title_ar,
    description: task.description,
    description_ar: task.description_ar,
    status: mapStatusToFrontend(task.status),
    priority: task.priority as 'urgent' | 'high' | 'medium' | 'low',
    due_date: task.due_date,
    field_id: task.field_id,
    assigned_to: task.assigned_to,
    created_at: task.created_at,
    updated_at: task.updated_at,
  };
}

async function createTask(data: TaskFormData): Promise<Task> {
  const payload = {
    title: data.title,
    title_ar: data.title_ar,
    description: data.description,
    description_ar: data.description_ar,
    priority: data.priority,
    due_date: data.due_date,
    field_id: data.field_id,
    assigned_to: data.assigned_to,
    status: data.status ? mapStatusToBackend(data.status) : 'pending',
  };

  const response = await apiClient.post<{
    task_id: string;
    tenant_id: string;
    title: string;
    title_ar?: string;
    description?: string;
    description_ar?: string;
    status: string;
    priority: string;
    due_date?: string;
    field_id: string;
    assigned_to?: string;
    created_at: string;
    updated_at: string;
  }>('http://localhost:8103/api/v1/tasks', payload);

  const task = response.data;
  return {
    id: task.task_id,
    tenant_id: task.tenant_id,
    title: task.title,
    title_ar: task.title_ar,
    description: task.description,
    description_ar: task.description_ar,
    status: mapStatusToFrontend(task.status),
    priority: task.priority as 'urgent' | 'high' | 'medium' | 'low',
    due_date: task.due_date,
    field_id: task.field_id,
    assigned_to: task.assigned_to,
    created_at: task.created_at,
    updated_at: task.updated_at,
  };
}

async function updateTask(id: string, data: Partial<TaskFormData>): Promise<Task> {
  const payload: Record<string, unknown> = {};

  if (data.title !== undefined) payload.title = data.title;
  if (data.title_ar !== undefined) payload.title_ar = data.title_ar;
  if (data.description !== undefined) payload.description = data.description;
  if (data.description_ar !== undefined) payload.description_ar = data.description_ar;
  if (data.priority !== undefined) payload.priority = data.priority;
  if (data.due_date !== undefined) payload.due_date = data.due_date;
  if (data.field_id !== undefined) payload.field_id = data.field_id;
  if (data.assigned_to !== undefined) payload.assigned_to = data.assigned_to;
  if (data.status !== undefined) payload.status = mapStatusToBackend(data.status);

  const response = await apiClient.put<{
    task_id: string;
    tenant_id: string;
    title: string;
    title_ar?: string;
    description?: string;
    description_ar?: string;
    status: string;
    priority: string;
    due_date?: string;
    field_id: string;
    assigned_to?: string;
    created_at: string;
    updated_at: string;
  }>(`http://localhost:8103/api/v1/tasks/${id}`, payload);

  const task = response.data;
  return {
    id: task.task_id,
    tenant_id: task.tenant_id,
    title: task.title,
    title_ar: task.title_ar,
    description: task.description,
    description_ar: task.description_ar,
    status: mapStatusToFrontend(task.status),
    priority: task.priority as 'urgent' | 'high' | 'medium' | 'low',
    due_date: task.due_date,
    field_id: task.field_id,
    assigned_to: task.assigned_to,
    created_at: task.created_at,
    updated_at: task.updated_at,
  };
}

async function updateTaskStatus(id: string, status: TaskStatus): Promise<Task> {
  return updateTask(id, { status });
}

async function deleteTask(id: string): Promise<void> {
  await apiClient.delete(`http://localhost:8103/api/v1/tasks/${id}`);
}

export function useTasks(filters?: TaskFilters) {
  return useQuery({
    queryKey: ['tasks', filters],
    queryFn: () => fetchTasks(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useTask(id: string) {
  return useQuery({
    queryKey: ['tasks', id],
    queryFn: () => fetchTaskById(id),
    enabled: !!id,
    staleTime: 2 * 60 * 1000,
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<TaskFormData> }) =>
      updateTask(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['tasks', variables.id] });
    },
  });
}

export function useUpdateTaskStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: TaskStatus }) =>
      updateTaskStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}
