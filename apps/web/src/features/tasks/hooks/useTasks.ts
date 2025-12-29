/**
 * SAHOOL Tasks Hook
 * خطاف المهام
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type { Task, TaskFormData, TaskFilters, TaskStatus, Priority } from '../types';

/**
 * Backend task representation from API
 */
interface BackendTask {
  id?: string;
  task_id?: string;
  tenant_id?: string;
  tenantId?: string;
  field_id?: string;
  fieldId?: string;
  farm_id?: string;
  farmId?: string;
  title: string;
  title_ar?: string;
  description?: string;
  description_ar?: string;
  status: string;
  priority: Priority;
  type?: string;
  taskType?: string;
  due_date?: string;
  dueDate?: string;
  assigned_to?: string;
  assigneeId?: string;
  evidence_photos?: string[];
  evidence_notes?: string;
  created_at?: string;
  createdAt?: string;
  updated_at?: string;
  updatedAt?: string;
}

// Map frontend status to backend status
const mapStatusToBackend = (status: TaskStatus): string => {
  const statusMap: Record<string, string> = {
    'open': 'pending',
    'pending': 'pending',
    'in_progress': 'in_progress',
    'completed': 'completed',
    'cancelled': 'cancelled',
  };
  return statusMap[status] || status;
};

// Map backend status to frontend status
const mapStatusToFrontend = (status: string): TaskStatus => {
  const statusMap: Record<string, TaskStatus> = {
    'pending': 'open',
    'open': 'open',
    'in_progress': 'in_progress',
    'completed': 'completed',
    'cancelled': 'cancelled',
  };
  return (statusMap[status] as TaskStatus) || 'open';
};

/**
 * Transform backend task to frontend Task format
 */
const transformBackendTask = (task: BackendTask): Task => ({
  id: task.id || task.task_id || '',
  tenant_id: task.tenant_id || task.tenantId || '',
  field_id: task.field_id || task.fieldId || '',
  farm_id: task.farm_id || task.farmId,
  title: task.title,
  title_ar: task.title_ar,
  description: task.description,
  description_ar: task.description_ar,
  status: mapStatusToFrontend(task.status),
  priority: task.priority,
  type: task.type || task.taskType,
  due_date: task.due_date || task.dueDate,
  assigned_to: task.assigned_to || task.assigneeId,
  evidence_photos: task.evidence_photos || [],
  evidence_notes: task.evidence_notes,
  created_at: task.created_at || task.createdAt || new Date().toISOString(),
  updated_at: task.updated_at || task.updatedAt || new Date().toISOString(),
});

async function fetchTasks(filters?: TaskFilters): Promise<Task[]> {
  const options: {
    tenantId?: string;
    fieldId?: string;
    userId?: string;
    status?: string;
    limit?: number;
    offset?: number;
  } = {};

  if (filters?.field_id) options.fieldId = filters.field_id;
  if (filters?.status) options.status = mapStatusToBackend(filters.status);
  if (filters?.assigned_to) options.userId = filters.assigned_to;

  const response = await apiClient.getTasks(options);

  if (!response.success || !response.data) {
    return [];
  }

  // Transform backend data to Task format
  return response.data.map((task: BackendTask) => transformBackendTask(task));
}

async function fetchTaskById(id: string): Promise<Task> {
  const response = await apiClient.getTask(id);

  if (!response.success || !response.data) {
    throw new Error(response.error || 'Failed to fetch task');
  }

  return transformBackendTask(response.data as BackendTask);
}

async function createTask(data: TaskFormData): Promise<Task> {
  const payload = {
    title: data.title,
    description: data.description,
    field_id: data.field_id || '',
    assignee_id: data.assigned_to,
    due_date: data.due_date,
    priority: data.priority as 'low' | 'medium' | 'high',
    taskType: 'general',
  };

  const response = await apiClient.createTask(payload);

  if (!response.success || !response.data) {
    throw new Error(response.error || 'Failed to create task');
  }

  return transformBackendTask(response.data as BackendTask);
}

async function updateTask(id: string, data: Partial<TaskFormData>): Promise<Task> {
  const payload: {
    status?: string;
    title?: string;
    description?: string;
  } = {};

  if (data.title !== undefined) payload.title = data.title;
  if (data.description !== undefined) payload.description = data.description;
  if (data.status !== undefined) payload.status = mapStatusToBackend(data.status);

  const response = await apiClient.updateTask(id, payload);

  if (!response.success || !response.data) {
    throw new Error(response.error || 'Failed to update task');
  }

  return transformBackendTask(response.data as BackendTask);
}

async function updateTaskStatus(id: string, status: TaskStatus): Promise<Task> {
  return updateTask(id, { status });
}

async function deleteTask(id: string): Promise<void> {
  const response = await apiClient.deleteTask(id);
  if (!response.success) {
    throw new Error(response.error || 'Failed to delete task');
  }
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
