/**
 * Tasks Feature - API Layer
 * طبقة API لميزة المهام
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { TASK_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import type { Task, TaskFormData, TaskFilters, TaskStatus } from './types';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_FAILED: {
    en: 'Failed to fetch tasks. Using cached data.',
    ar: 'فشل في جلب المهام. استخدام البيانات المخزنة.',
  },
  CREATE_FAILED: {
    en: 'Failed to create task.',
    ar: 'فشل في إنشاء المهمة.',
  },
  UPDATE_FAILED: {
    en: 'Failed to update task.',
    ar: 'فشل في تحديث المهمة.',
  },
  DELETE_FAILED: {
    en: 'Failed to delete task.',
    ar: 'فشل في حذف المهمة.',
  },
  COMPLETE_FAILED: {
    en: 'Failed to complete task.',
    ar: 'فشل في إكمال المهمة.',
  },
  ASSIGN_FAILED: {
    en: 'Failed to assign task.',
    ar: 'فشل في تعيين المهمة.',
  },
};

// API Task response type (backend format)
interface ApiTask {
  id?: string;
  task_id?: string;
  tenant_id?: string;
  tenantId?: string;
  field_id?: string;
  fieldId?: string;
  farm_id?: string;
  farmId?: string;
  title?: string;
  title_ar?: string;
  description?: string;
  description_ar?: string;
  status?: string;
  priority?: string;
  type?: string;
  taskType?: string;
  due_date?: string;
  dueDate?: string;
  assigned_to?: string;
  assigneeId?: string;
  assignee_id?: string;
  evidence_photos?: string[];
  evidence_notes?: string;
  created_at?: string;
  createdAt?: string;
  updated_at?: string;
  updatedAt?: string;
  completed_at?: string;
  completedAt?: string;
}

// Helper functions for data transformation
const mapStatusToBackend = (status: TaskStatus): string => {
  const statusMap: Record<TaskStatus, string> = {
    open: 'pending',
    pending: 'pending',
    in_progress: 'in_progress',
    completed: 'completed',
    cancelled: 'cancelled',
  };
  return statusMap[status] || status;
};

const mapStatusToFrontend = (status: string): TaskStatus => {
  const statusMap: Record<string, TaskStatus> = {
    pending: 'open',
    open: 'open',
    in_progress: 'in_progress',
    completed: 'completed',
    cancelled: 'cancelled',
  };
  return (statusMap[status] as TaskStatus) || 'open';
};

function mapApiTaskToTask(task: ApiTask): Task {
  return {
    id: task.id || task.task_id || '',
    tenant_id: task.tenant_id || task.tenantId || '',
    field_id: task.field_id || task.fieldId || '',
    farm_id: task.farm_id || task.farmId,
    title: task.title || '',
    title_ar: task.title_ar,
    description: task.description,
    description_ar: task.description_ar,
    status: mapStatusToFrontend(task.status || 'pending'),
    priority: (task.priority as Task['priority']) || 'medium',
    type: task.type || task.taskType,
    due_date: task.due_date || task.dueDate,
    assigned_to: task.assigned_to || task.assigneeId || task.assignee_id,
    evidence_photos: task.evidence_photos || [],
    evidence_notes: task.evidence_notes,
    completed_at: task.completed_at || task.completedAt,
    created_at: task.created_at || task.createdAt || new Date().toISOString(),
    updated_at: task.updated_at || task.updatedAt || new Date().toISOString(),
  };
}

// API Functions
export const tasksApi = {
  /**
   * Get all tasks with optional filters
   * جلب جميع المهام مع فلاتر اختيارية
   */
  getTasks: async (filters?: TaskFilters): Promise<Task[]> => {
    return safeFetch(TASK_ENDPOINTS.LIST, async () => {
      const params = new URLSearchParams();
      if (filters?.field_id) params.set('fieldId', filters.field_id);
      if (filters?.status) params.set('status', mapStatusToBackend(filters.status));
      if (filters?.assigned_to) params.set('userId', filters.assigned_to);
      if (filters?.priority) params.set('priority', filters.priority);
      if (filters?.search) params.set('search', filters.search);
      if (filters?.due_date_from) params.set('dueDateFrom', filters.due_date_from);
      if (filters?.due_date_to) params.set('dueDateTo', filters.due_date_to);

      const response = await api.get(`${TASK_ENDPOINTS.LIST}?${params.toString()}`);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data.map(mapApiTaskToTask);
      throw new Error('Invalid response format for tasks | تنسيق الاستجابة غير صالح للمهام');
    });
  },

  /**
   * Get a single task by ID
   * جلب مهمة واحدة بواسطة المعرف
   */
  getTask: async (id: string): Promise<Task> => {
    return safeFetch(buildUrl(TASK_ENDPOINTS.GET, { taskId: id }), async () => {
      const response = await api.get(buildUrl(TASK_ENDPOINTS.GET, { taskId: id }));
      const data = response.data.data || response.data;
      if (data && typeof data === 'object') return mapApiTaskToTask(data as ApiTask);
      throw new Error('Invalid response format | تنسيق الاستجابة غير صالح');
    });
  },

  /**
   * Create a new task
   * إنشاء مهمة جديدة
   */
  createTask: async (data: TaskFormData): Promise<Task> => {
    return safeFetch(TASK_ENDPOINTS.CREATE, async () => {
      const payload = {
        title: data.title,
        title_ar: data.title_ar,
        description: data.description,
        description_ar: data.description_ar,
        field_id: data.field_id || '',
        assignee_id: data.assigned_to,
        due_date: data.due_date,
        priority: data.priority,
        status: data.status ? mapStatusToBackend(data.status) : 'pending',
        taskType: 'general',
      };

      const response = await api.post(TASK_ENDPOINTS.CREATE, payload);
      const taskData = response.data.data || response.data;
      if (taskData && typeof taskData === 'object') return mapApiTaskToTask(taskData as ApiTask);
      throw new Error('Invalid response format | تنسيق الاستجابة غير صالح');
    });
  },

  /**
   * Update an existing task
   * تحديث مهمة موجودة
   */
  updateTask: async (id: string, data: Partial<TaskFormData>): Promise<Task> => {
    return safeFetch(buildUrl(TASK_ENDPOINTS.UPDATE, { taskId: id }), async () => {
      const payload: Record<string, unknown> = {};
      if (data.title !== undefined) payload.title = data.title;
      if (data.title_ar !== undefined) payload.title_ar = data.title_ar;
      if (data.description !== undefined) payload.description = data.description;
      if (data.description_ar !== undefined) payload.description_ar = data.description_ar;
      if (data.status !== undefined) payload.status = mapStatusToBackend(data.status);
      if (data.priority !== undefined) payload.priority = data.priority;
      if (data.due_date !== undefined) payload.due_date = data.due_date;
      if (data.assigned_to !== undefined) payload.assignee_id = data.assigned_to;
      if (data.field_id !== undefined) payload.field_id = data.field_id;

      const response = await api.put(buildUrl(TASK_ENDPOINTS.UPDATE, { taskId: id }), payload);
      const taskData = response.data.data || response.data;
      if (taskData && typeof taskData === 'object') return mapApiTaskToTask(taskData as ApiTask);
      throw new Error('Invalid response format | تنسيق الاستجابة غير صالح');
    });
  },

  /**
   * Delete a task
   * حذف مهمة
   */
  deleteTask: async (id: string): Promise<void> => {
    return safeFetch(buildUrl(TASK_ENDPOINTS.DELETE, { taskId: id }), async () => {
      await api.delete(buildUrl(TASK_ENDPOINTS.DELETE, { taskId: id }));
    });
  },

  /**
   * Complete a task with optional evidence
   * إكمال مهمة مع أدلة اختيارية
   */
  completeTask: async (
    id: string,
    evidence?: { notes?: string; photos?: string[] }
  ): Promise<Task> => {
    return safeFetch(buildUrl(TASK_ENDPOINTS.COMPLETE, { taskId: id }), async () => {
      const payload = {
        evidence_notes: evidence?.notes,
        evidence_photos: evidence?.photos || [],
        completed_at: new Date().toISOString(),
      };
      const response = await api.post(buildUrl(TASK_ENDPOINTS.COMPLETE, { taskId: id }), payload);
      const taskData = response.data.data || response.data;
      if (taskData && typeof taskData === 'object') return mapApiTaskToTask(taskData as ApiTask);
      throw new Error('Invalid response format | تنسيق الاستجابة غير صالح');
    });
  },

  /**
   * Update task status
   * تحديث حالة المهمة
   */
  updateTaskStatus: async (id: string, status: TaskStatus): Promise<Task> => {
    return safeFetch(buildUrl(TASK_ENDPOINTS.UPDATE, { taskId: id }), async () => {
      const payload = { status: mapStatusToBackend(status) };
      const response = await api.put(buildUrl(TASK_ENDPOINTS.UPDATE, { taskId: id }), payload);
      const taskData = response.data.data || response.data;
      if (taskData && typeof taskData === 'object') return mapApiTaskToTask(taskData as ApiTask);
      throw new Error('Invalid response format | تنسيق الاستجابة غير صالح');
    });
  },

  /**
   * Assign a task to a user
   * تعيين مهمة لمستخدم
   */
  assignTask: async (id: string, userId: string): Promise<Task> => {
    return safeFetch(buildUrl(TASK_ENDPOINTS.UPDATE, { taskId: id }), async () => {
      const payload = { assignee_id: userId };
      const response = await api.put(buildUrl(TASK_ENDPOINTS.UPDATE, { taskId: id }), payload);
      const taskData = response.data.data || response.data;
      if (taskData && typeof taskData === 'object') return mapApiTaskToTask(taskData as ApiTask);
      throw new Error('Invalid response format | تنسيق الاستجابة غير صالح');
    });
  },

  /**
   * Get tasks by field ID
   * جلب المهام حسب معرف الحقل
   */
  getTasksByField: async (fieldId: string): Promise<Task[]> => {
    return tasksApi.getTasks({ field_id: fieldId });
  },

  /**
   * Get tasks assigned to a specific user
   * جلب المهام المعينة لمستخدم معين
   */
  getTasksByUser: async (userId: string): Promise<Task[]> => {
    return tasksApi.getTasks({ assigned_to: userId });
  },

  /**
   * Get tasks by status
   * جلب المهام حسب الحالة
   */
  getTasksByStatus: async (status: TaskStatus): Promise<Task[]> => {
    return tasksApi.getTasks({ status });
  },

  /**
   * Get overdue tasks
   * جلب المهام المتأخرة
   */
  getOverdueTasks: async (): Promise<Task[]> => {
    const now = new Date().toISOString();
    const tasks = await tasksApi.getTasks({ due_date_to: now });
    return tasks.filter((task) => task.status !== 'completed' && task.status !== 'cancelled');
  },
};
