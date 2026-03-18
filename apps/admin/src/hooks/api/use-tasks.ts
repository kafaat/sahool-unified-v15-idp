/**
 * SAHOOL Admin - Task management hooks
 * خطافات إدارة المهام
 */

"use client";

import { useApiQuery, useApiMutation } from "./use-api-query";
import { fetchTasks, updateTaskStatus } from "@/lib/api";
import { apiClient } from "@/lib/api";
import { API_URLS } from "@/config/api";

/**
 * List tasks
 */
export function useTasks(params?: {
  status?: string;
  type?: string;
  assignedTo?: string;
  limit?: number;
}) {
  return useApiQuery(
    ["tasks", JSON.stringify(params ?? {})],
    () => fetchTasks(params),
    { staleTime: 30000 },
  );
}

/**
 * Update task status
 */
export function useUpdateTaskStatus() {
  return useApiMutation(
    ({ id, status }: { id: string; status: string }) =>
      updateTaskStatus(id, status).then(() => ({ success: true })),
    { invalidateKeys: ["tasks"] },
  );
}

/**
 * Create a new task
 */
export function useCreateTask() {
  return useApiMutation(
    async (data: {
      title: string;
      description?: string;
      type: string;
      priority: string;
      assignedTo?: string;
      fieldId?: string;
      dueDate?: string;
    }) => {
      const response = await apiClient.post(
        `${API_URLS.task}/api/v1/tasks`,
        data,
      );
      return response.data;
    },
    { invalidateKeys: ["tasks"] },
  );
}
