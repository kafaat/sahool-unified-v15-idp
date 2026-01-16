/**
 * Tasks Feature - API Layer
 * طبقة API لميزة المهام
 */

import axios from "axios";
import Cookies from "js-cookie";
import { logger } from "@/lib/logger";
import type { Task, TaskFormData, TaskFilters, TaskStatus } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

// Only warn during development, don't throw during build
if (!API_BASE_URL && typeof window !== "undefined") {
  console.warn("NEXT_PUBLIC_API_URL environment variable is not set");
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000, // 10 seconds timeout
});

// Add auth token interceptor
api.interceptors.request.use((config) => {
  // Get token from cookie using secure cookie parser
  if (typeof window !== "undefined") {
    const token = Cookies.get("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: "Network error. Using offline data.",
    ar: "خطأ في الاتصال. استخدام البيانات المحفوظة.",
  },
  FETCH_FAILED: {
    en: "Failed to fetch tasks. Using cached data.",
    ar: "فشل في جلب المهام. استخدام البيانات المخزنة.",
  },
  CREATE_FAILED: {
    en: "Failed to create task.",
    ar: "فشل في إنشاء المهمة.",
  },
  UPDATE_FAILED: {
    en: "Failed to update task.",
    ar: "فشل في تحديث المهمة.",
  },
  DELETE_FAILED: {
    en: "Failed to delete task.",
    ar: "فشل في حذف المهمة.",
  },
  COMPLETE_FAILED: {
    en: "Failed to complete task.",
    ar: "فشل في إكمال المهمة.",
  },
  ASSIGN_FAILED: {
    en: "Failed to assign task.",
    ar: "فشل في تعيين المهمة.",
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

// Mock data for fallback
const MOCK_TASKS: Task[] = [
  {
    id: "1",
    tenant_id: "mock-tenant",
    field_id: "field-1",
    farm_id: "farm-1",
    title: "Irrigate Field #1",
    title_ar: "ري الحقل رقم 1",
    description: "Complete irrigation for field #1",
    description_ar: "إكمال ري الحقل رقم 1",
    status: "open",
    priority: "high",
    type: "irrigation",
    due_date: new Date(Date.now() + 1000 * 60 * 60 * 24).toISOString(),
    assigned_to: "user-1",
    evidence_photos: [],
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
  },
  {
    id: "2",
    tenant_id: "mock-tenant",
    field_id: "field-2",
    farm_id: "farm-1",
    title: "Fertilize Field #2",
    title_ar: "تسميد الحقل رقم 2",
    description: "Apply fertilizer to field #2",
    description_ar: "تطبيق السماد على الحقل رقم 2",
    status: "in_progress",
    priority: "medium",
    type: "fertilization",
    due_date: new Date(Date.now() + 1000 * 60 * 60 * 48).toISOString(),
    assigned_to: "user-2",
    evidence_photos: [],
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
  },
  {
    id: "3",
    tenant_id: "mock-tenant",
    field_id: "field-3",
    farm_id: "farm-1",
    title: "Pest Inspection",
    title_ar: "فحص الآفات",
    description: "Check for pests in field #3",
    description_ar: "فحص الآفات في الحقل رقم 3",
    status: "completed",
    priority: "low",
    type: "inspection",
    due_date: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    assigned_to: "user-1",
    evidence_photos: [],
    completed_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 72).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
  },
];

// Helper functions for data transformation
const mapStatusToBackend = (status: TaskStatus): string => {
  const statusMap: Record<TaskStatus, string> = {
    open: "pending",
    pending: "pending",
    in_progress: "in_progress",
    completed: "completed",
    cancelled: "cancelled",
  };
  return statusMap[status] || status;
};

const mapStatusToFrontend = (status: string): TaskStatus => {
  const statusMap: Record<string, TaskStatus> = {
    pending: "open",
    open: "open",
    in_progress: "in_progress",
    completed: "completed",
    cancelled: "cancelled",
  };
  return (statusMap[status] as TaskStatus) || "open";
};

function mapApiTaskToTask(task: ApiTask): Task {
  return {
    id: task.id || task.task_id || "",
    tenant_id: task.tenant_id || task.tenantId || "",
    field_id: task.field_id || task.fieldId || "",
    farm_id: task.farm_id || task.farmId,
    title: task.title || "",
    title_ar: task.title_ar,
    description: task.description,
    description_ar: task.description_ar,
    status: mapStatusToFrontend(task.status || "pending"),
    priority: (task.priority as Task["priority"]) || "medium",
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

// Filter mock data based on filters
function filterMockTasks(filters?: TaskFilters): Task[] {
  if (!filters) return MOCK_TASKS;

  return MOCK_TASKS.filter((task) => {
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      const titleMatch = task.title?.toLowerCase().includes(searchLower);
      const titleArMatch = task.title_ar?.toLowerCase().includes(searchLower);
      const descMatch = task.description?.toLowerCase().includes(searchLower);
      if (!titleMatch && !titleArMatch && !descMatch) return false;
    }

    if (filters.status && task.status !== filters.status) return false;
    if (filters.priority && task.priority !== filters.priority) return false;
    if (filters.field_id && task.field_id !== filters.field_id) return false;
    if (filters.assigned_to && task.assigned_to !== filters.assigned_to)
      return false;

    if (filters.due_date_from && task.due_date) {
      if (new Date(task.due_date) < new Date(filters.due_date_from))
        return false;
    }

    if (filters.due_date_to && task.due_date) {
      if (new Date(task.due_date) > new Date(filters.due_date_to)) return false;
    }

    return true;
  });
}

// API Functions
export const tasksApi = {
  /**
   * Get all tasks with optional filters
   * جلب جميع المهام مع فلاتر اختيارية
   */
  getTasks: async (filters?: TaskFilters): Promise<Task[]> => {
    try {
      const params = new URLSearchParams();

      if (filters?.field_id) params.set("fieldId", filters.field_id);
      if (filters?.status)
        params.set("status", mapStatusToBackend(filters.status));
      if (filters?.assigned_to) params.set("userId", filters.assigned_to);
      if (filters?.priority) params.set("priority", filters.priority);
      if (filters?.search) params.set("search", filters.search);
      if (filters?.due_date_from)
        params.set("dueDateFrom", filters.due_date_from);
      if (filters?.due_date_to) params.set("dueDateTo", filters.due_date_to);

      const response = await api.get(`/api/v1/tasks?${params.toString()}`);

      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data.map(mapApiTaskToTask);
      }

      logger.warn("API returned unexpected format for tasks, using mock data");
      return filterMockTasks(filters);
    } catch (error) {
      logger.warn("Failed to fetch tasks from API, using mock data:", error);
      return filterMockTasks(filters);
    }
  },

  /**
   * Get a single task by ID
   * جلب مهمة واحدة بواسطة المعرف
   */
  getTask: async (id: string): Promise<Task> => {
    try {
      const response = await api.get(`/api/v1/tasks/${id}`);

      const data = response.data.data || response.data;

      if (data && typeof data === "object") {
        return mapApiTaskToTask(data as ApiTask);
      }

      throw new Error("Invalid response format");
    } catch (error) {
      logger.warn(
        `Failed to fetch task ${id} from API, using mock data:`,
        error,
      );

      const mockTask = MOCK_TASKS.find((t) => t.id === id);
      if (mockTask) return mockTask;

      throw new Error("Task not found");
    }
  },

  /**
   * Create a new task
   * إنشاء مهمة جديدة
   */
  createTask: async (data: TaskFormData): Promise<Task> => {
    try {
      const payload = {
        title: data.title,
        title_ar: data.title_ar,
        description: data.description,
        description_ar: data.description_ar,
        field_id: data.field_id || "",
        assignee_id: data.assigned_to,
        due_date: data.due_date,
        priority: data.priority,
        status: data.status ? mapStatusToBackend(data.status) : "pending",
        taskType: "general",
      };

      const response = await api.post("/api/v1/tasks", payload);

      const taskData = response.data.data || response.data;

      if (taskData && typeof taskData === "object") {
        return mapApiTaskToTask(taskData as ApiTask);
      }

      throw new Error("Invalid response format");
    } catch (error) {
      logger.error("Failed to create task:", error);
      throw new Error(ERROR_MESSAGES.CREATE_FAILED.en);
    }
  },

  /**
   * Update an existing task
   * تحديث مهمة موجودة
   */
  updateTask: async (
    id: string,
    data: Partial<TaskFormData>,
  ): Promise<Task> => {
    try {
      const payload: Record<string, unknown> = {};

      if (data.title !== undefined) payload.title = data.title;
      if (data.title_ar !== undefined) payload.title_ar = data.title_ar;
      if (data.description !== undefined)
        payload.description = data.description;
      if (data.description_ar !== undefined)
        payload.description_ar = data.description_ar;
      if (data.status !== undefined)
        payload.status = mapStatusToBackend(data.status);
      if (data.priority !== undefined) payload.priority = data.priority;
      if (data.due_date !== undefined) payload.due_date = data.due_date;
      if (data.assigned_to !== undefined)
        payload.assignee_id = data.assigned_to;
      if (data.field_id !== undefined) payload.field_id = data.field_id;

      const response = await api.put(`/api/v1/tasks/${id}`, payload);

      const taskData = response.data.data || response.data;

      if (taskData && typeof taskData === "object") {
        return mapApiTaskToTask(taskData as ApiTask);
      }

      throw new Error("Invalid response format");
    } catch (error) {
      logger.error(`Failed to update task ${id}:`, error);
      throw new Error(ERROR_MESSAGES.UPDATE_FAILED.en);
    }
  },

  /**
   * Delete a task
   * حذف مهمة
   */
  deleteTask: async (id: string): Promise<void> => {
    try {
      await api.delete(`/api/v1/tasks/${id}`);
    } catch (error) {
      logger.error(`Failed to delete task ${id}:`, error);
      throw new Error(ERROR_MESSAGES.DELETE_FAILED.en);
    }
  },

  /**
   * Complete a task with optional evidence
   * إكمال مهمة مع أدلة اختيارية
   */
  completeTask: async (
    id: string,
    evidence?: { notes?: string; photos?: string[] },
  ): Promise<Task> => {
    try {
      const payload = {
        evidence_notes: evidence?.notes,
        evidence_photos: evidence?.photos || [],
        completed_at: new Date().toISOString(),
      };

      const response = await api.post(`/api/v1/tasks/${id}/complete`, payload);

      const taskData = response.data.data || response.data;

      if (taskData && typeof taskData === "object") {
        return mapApiTaskToTask(taskData as ApiTask);
      }

      throw new Error("Invalid response format");
    } catch (error) {
      logger.error(`Failed to complete task ${id}:`, error);
      throw new Error(ERROR_MESSAGES.COMPLETE_FAILED.en);
    }
  },

  /**
   * Update task status
   * تحديث حالة المهمة
   */
  updateTaskStatus: async (id: string, status: TaskStatus): Promise<Task> => {
    try {
      const payload = {
        status: mapStatusToBackend(status),
      };

      const response = await api.put(`/api/v1/tasks/${id}`, payload);

      const taskData = response.data.data || response.data;

      if (taskData && typeof taskData === "object") {
        return mapApiTaskToTask(taskData as ApiTask);
      }

      throw new Error("Invalid response format");
    } catch (error) {
      logger.error(`Failed to update task status ${id}:`, error);
      throw new Error(ERROR_MESSAGES.UPDATE_FAILED.en);
    }
  },

  /**
   * Assign a task to a user
   * تعيين مهمة لمستخدم
   */
  assignTask: async (id: string, userId: string): Promise<Task> => {
    try {
      const payload = {
        assignee_id: userId,
      };

      const response = await api.put(`/api/v1/tasks/${id}`, payload);

      const taskData = response.data.data || response.data;

      if (taskData && typeof taskData === "object") {
        return mapApiTaskToTask(taskData as ApiTask);
      }

      throw new Error("Invalid response format");
    } catch (error) {
      logger.error(`Failed to assign task ${id}:`, error);
      throw new Error(ERROR_MESSAGES.ASSIGN_FAILED.en);
    }
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
    return tasks.filter(
      (task) => task.status !== "completed" && task.status !== "cancelled",
    );
  },
};
