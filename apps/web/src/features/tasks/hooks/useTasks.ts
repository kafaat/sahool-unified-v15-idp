/**
 * SAHOOL Tasks Hooks
 * خطافات المهام
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tasksApi } from '../api';
import type { TaskFormData, TaskFilters, TaskStatus } from '../types';

/**
 * Query Hooks - For reading data
 * خطافات الاستعلام - لقراءة البيانات
 */

/**
 * Get all tasks with optional filters
 * جلب جميع المهام مع فلاتر اختيارية
 */
export function useTasks(filters?: TaskFilters) {
  return useQuery({
    queryKey: ['tasks', filters],
    queryFn: () => tasksApi.getTasks(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Get a single task by ID
 * جلب مهمة واحدة بواسطة المعرف
 */
export function useTask(id: string) {
  return useQuery({
    queryKey: ['tasks', id],
    queryFn: () => tasksApi.getTask(id),
    enabled: !!id,
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Get tasks by field ID
 * جلب المهام حسب معرف الحقل
 */
export function useTasksByField(fieldId: string) {
  return useQuery({
    queryKey: ['tasks', 'field', fieldId],
    queryFn: () => tasksApi.getTasksByField(fieldId),
    enabled: !!fieldId,
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Get tasks assigned to a user
 * جلب المهام المعينة لمستخدم
 */
export function useTasksByUser(userId: string) {
  return useQuery({
    queryKey: ['tasks', 'user', userId],
    queryFn: () => tasksApi.getTasksByUser(userId),
    enabled: !!userId,
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Get tasks by status
 * جلب المهام حسب الحالة
 */
export function useTasksByStatus(status: TaskStatus) {
  return useQuery({
    queryKey: ['tasks', 'status', status],
    queryFn: () => tasksApi.getTasksByStatus(status),
    enabled: !!status,
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Get overdue tasks
 * جلب المهام المتأخرة
 */
export function useOverdueTasks() {
  return useQuery({
    queryKey: ['tasks', 'overdue'],
    queryFn: () => tasksApi.getOverdueTasks(),
    staleTime: 1 * 60 * 1000, // 1 minute - check more frequently
  });
}

/**
 * Mutation Hooks - For writing/updating data
 * خطافات الطفرة - لكتابة/تحديث البيانات
 */

/**
 * Create a new task
 * إنشاء مهمة جديدة
 */
export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: tasksApi.createTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

/**
 * Update an existing task
 * تحديث مهمة موجودة
 */
export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<TaskFormData> }) =>
      tasksApi.updateTask(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['tasks', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

/**
 * Delete a task
 * حذف مهمة
 */
export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: tasksApi.deleteTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

/**
 * Complete a task with evidence
 * إكمال مهمة مع أدلة
 */
export function useCompleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      evidence,
    }: {
      id: string;
      evidence?: { notes?: string; photos?: string[] };
    }) => tasksApi.completeTask(id, evidence),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['tasks', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

/**
 * Update task status
 * تحديث حالة المهمة
 */
export function useUpdateTaskStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: TaskStatus }) =>
      tasksApi.updateTaskStatus(id, status),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['tasks', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

/**
 * Assign a task to a user
 * تعيين مهمة لمستخدم
 */
export function useAssignTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, userId }: { id: string; userId: string }) =>
      tasksApi.assignTask(id, userId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['tasks', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
