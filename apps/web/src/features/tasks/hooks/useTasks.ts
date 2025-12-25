/**
 * SAHOOL Tasks Hook
 * خطاف المهام
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type { Task, TaskFormData, TaskFilters, TaskStatus } from '../types';

// Map frontend status to backend status
const mapStatusToBackend = (status: TaskStatus): string => {
  const statusMap: Record<TaskStatus, string> = {
    'open': 'pending',
    'in_progress': 'in_progress',
    'done': 'completed',
    'canceled': 'cancelled',
  };
  return statusMap[status] || status;
};

// Map backend status to frontend status
const mapStatusToFrontend = (status: string): TaskStatus => {
  const statusMap: Record<string, TaskStatus> = {
    'pending': 'open',
    'in_progress': 'in_progress',
    'completed': 'done',
    'cancelled': 'canceled',
  };
  return (statusMap[status] as TaskStatus) || 'open';
};

async function fetchTasks(filters?: TaskFilters): Promise<Task[]> {
  const params: Record<string, string> = {};

  if (filters?.fieldId) params.field_id = filters.fieldId;
  if (filters?.status) params.status = mapStatusToBackend(filters.status);
  if (filters?.priority) params.priority = filters.priority;
  if (filters?.assignedTo) params.assigned_to = filters.assignedTo;
  if (filters?.search) params.search = filters.search;

  const response = await apiClient.get<{
    tasks: Array<{
      task_id: string;
      title: string;
      title_ar?: string;
      description?: string;
      description_ar?: string;
      status: string;
      priority: string;
      due_date?: string;
      field_id?: string;
      assigned_to?: string;
      created_at: string;
      updated_at: string;
    }>;
  }>('http://localhost:8103/api/v1/tasks', { params });

  // Transform backend data to frontend format
  return response.data.tasks?.map(task => ({
    id: task.task_id,
    title: task.title,
    titleAr: task.title_ar || '',
    description: task.description,
    descriptionAr: task.description_ar,
    status: mapStatusToFrontend(task.status),
    priority: task.priority as 'low' | 'medium' | 'high' | 'urgent',
    dueDate: task.due_date || '',
    fieldId: task.field_id,
    assignedTo: task.assigned_to,
    createdAt: task.created_at,
    updatedAt: task.updated_at,
  })) || [];
}

async function fetchTaskById(id: string): Promise<Task> {
  const response = await apiClient.get<{
    task_id: string;
    title: string;
    title_ar?: string;
    description?: string;
    description_ar?: string;
    status: string;
    priority: string;
    due_date?: string;
    field_id?: string;
    assigned_to?: string;
    created_at: string;
    updated_at: string;
  }>(`http://localhost:8103/api/v1/tasks/${id}`);

  const task = response.data;
  return {
    id: task.task_id,
    title: task.title,
    titleAr: task.title_ar || '',
    description: task.description,
    descriptionAr: task.description_ar,
    status: mapStatusToFrontend(task.status),
    priority: task.priority as 'low' | 'medium' | 'high' | 'urgent',
    dueDate: task.due_date || '',
    fieldId: task.field_id,
    assignedTo: task.assigned_to,
    createdAt: task.created_at,
    updatedAt: task.updated_at,
  };
}

async function createTask(data: TaskFormData): Promise<Task> {
  const payload = {
    title: data.title,
    title_ar: data.titleAr,
    description: data.description,
    description_ar: data.descriptionAr,
    priority: data.priority,
    due_date: data.dueDate,
    field_id: data.fieldId,
    assigned_to: data.assignedTo,
    status: data.status ? mapStatusToBackend(data.status) : 'pending',
  };

  const response = await apiClient.post<{
    task_id: string;
    title: string;
    title_ar?: string;
    description?: string;
    description_ar?: string;
    status: string;
    priority: string;
    due_date?: string;
    field_id?: string;
    assigned_to?: string;
    created_at: string;
    updated_at: string;
  }>('http://localhost:8103/api/v1/tasks', payload);

  const task = response.data;
  return {
    id: task.task_id,
    title: task.title,
    titleAr: task.title_ar || '',
    description: task.description,
    descriptionAr: task.description_ar,
    status: mapStatusToFrontend(task.status),
    priority: task.priority as 'low' | 'medium' | 'high' | 'urgent',
    dueDate: task.due_date || '',
    fieldId: task.field_id,
    assignedTo: task.assigned_to,
    createdAt: task.created_at,
    updatedAt: task.updated_at,
  };
}

async function updateTask(id: string, data: Partial<TaskFormData>): Promise<Task> {
  const payload: Record<string, unknown> = {};

  if (data.title !== undefined) payload.title = data.title;
  if (data.titleAr !== undefined) payload.title_ar = data.titleAr;
  if (data.description !== undefined) payload.description = data.description;
  if (data.descriptionAr !== undefined) payload.description_ar = data.descriptionAr;
  if (data.priority !== undefined) payload.priority = data.priority;
  if (data.dueDate !== undefined) payload.due_date = data.dueDate;
  if (data.fieldId !== undefined) payload.field_id = data.fieldId;
  if (data.assignedTo !== undefined) payload.assigned_to = data.assignedTo;
  if (data.status !== undefined) payload.status = mapStatusToBackend(data.status);

  const response = await apiClient.put<{
    task_id: string;
    title: string;
    title_ar?: string;
    description?: string;
    description_ar?: string;
    status: string;
    priority: string;
    due_date?: string;
    field_id?: string;
    assigned_to?: string;
    created_at: string;
    updated_at: string;
  }>(`http://localhost:8103/api/v1/tasks/${id}`, payload);

  const task = response.data;
  return {
    id: task.task_id,
    title: task.title,
    titleAr: task.title_ar || '',
    description: task.description,
    descriptionAr: task.description_ar,
    status: mapStatusToFrontend(task.status),
    priority: task.priority as 'low' | 'medium' | 'high' | 'urgent',
    dueDate: task.due_date || '',
    fieldId: task.field_id,
    assignedTo: task.assigned_to,
    createdAt: task.created_at,
    updatedAt: task.updated_at,
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
