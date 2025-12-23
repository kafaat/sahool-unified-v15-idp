/**
 * SAHOOL Tasks Hook
 * خطاف المهام
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { Task, TaskFormData, TaskFilters, TaskStatus } from '../types';

async function fetchTasks(filters?: TaskFilters): Promise<Task[]> {
  // TODO: Replace with actual API call
  // const params = new URLSearchParams(filters as any);
  // const response = await fetch(`/api/tasks?${params}`);
  // return response.json();

  // Mock data
  return [
    {
      id: '1',
      title: 'Water Field #3',
      titleAr: 'ري الحقل رقم 3',
      description: 'Regular irrigation schedule',
      descriptionAr: 'جدول الري العادي',
      status: 'pending',
      priority: 'high',
      dueDate: new Date(Date.now() + 1000 * 60 * 60 * 24).toISOString(),
      fieldId: '3',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: '2',
      title: 'Fertilize Field #5',
      titleAr: 'تسميد الحقل رقم 5',
      description: 'Apply NPK fertilizer',
      descriptionAr: 'تطبيق سماد NPK',
      status: 'in_progress',
      priority: 'medium',
      dueDate: new Date(Date.now() + 1000 * 60 * 60 * 48).toISOString(),
      fieldId: '5',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: '3',
      title: 'Pest inspection',
      titleAr: 'فحص الآفات',
      description: 'Check for common pests',
      descriptionAr: 'فحص الآفات الشائعة',
      status: 'completed',
      priority: 'low',
      dueDate: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
      fieldId: '1',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  ];
}

async function fetchTaskById(id: string): Promise<Task> {
  // TODO: Replace with actual API call
  const tasks = await fetchTasks();
  const task = tasks.find(t => t.id === id);
  if (!task) throw new Error('Task not found');
  return task;
}

async function createTask(data: TaskFormData): Promise<Task> {
  // TODO: Replace with actual API call
  return {
    id: Math.random().toString(36),
    ...data,
    status: data.status || 'pending',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  } as Task;
}

async function updateTask(id: string, data: Partial<TaskFormData>): Promise<Task> {
  // TODO: Replace with actual API call
  const task = await fetchTaskById(id);
  return { ...task, ...data, updatedAt: new Date().toISOString() };
}

async function updateTaskStatus(id: string, status: TaskStatus): Promise<Task> {
  return updateTask(id, { status });
}

async function deleteTask(id: string): Promise<void> {
  // TODO: Replace with actual API call
  return Promise.resolve();
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
