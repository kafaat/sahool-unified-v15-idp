/**
 * SAHOOL Tasks Feature Types
 * أنواع ميزة المهام
 */

import type {
  Task as ApiTask,
  TaskStatus as ApiTaskStatus,
  Priority as ApiPriority,
} from "@sahool/api-client";

// Re-export core types from API client
export type Task = ApiTask & {
  // Add any web-specific task fields here if needed
  completed_at?: string;
  farm_id?: string;
};

export type TaskStatus = ApiTaskStatus;
export type Priority = ApiPriority;

/**
 * Task Form Data Interface
 * واجهة بيانات نموذج المهمة
 */
export interface TaskFormData {
  title: string;
  title_ar: string;
  description?: string;
  description_ar?: string;
  due_date: string;
  priority: Priority;
  field_id?: string;
  assigned_to?: string;
  status?: TaskStatus;
}

/**
 * Task Filters Interface
 * واجهة فلاتر المهام
 */
export interface TaskFilters {
  search?: string;
  status?: TaskStatus;
  priority?: Priority;
  field_id?: string;
  assigned_to?: string;
  due_date_from?: string;
  due_date_to?: string;
}

/**
 * Task Board Column Interface (for Kanban-style boards)
 * واجهة عمود لوحة المهام (للوحات على طريقة كانبان)
 */
export interface TaskBoardColumn {
  id: TaskStatus;
  title: string;
  title_ar: string;
  tasks: Task[];
  color: string;
}

/**
 * Task Evidence Interface
 * واجهة أدلة المهمة
 */
export interface TaskEvidence {
  notes?: string;
  photos?: string[];
}

/**
 * Task Assignment Interface
 * واجهة تعيين المهمة
 */
export interface TaskAssignment {
  task_id: string;
  user_id: string;
  assigned_at?: string;
  assigned_by?: string;
}

/**
 * Task Statistics Interface
 * واجهة إحصائيات المهام
 */
export interface TaskStatistics {
  total: number;
  open: number;
  in_progress: number;
  completed: number;
  cancelled: number;
  overdue: number;
  by_priority: {
    high: number;
    medium: number;
    low: number;
  };
}

/**
 * Task Update Payload Interface
 * واجهة حمولة تحديث المهمة
 */
export interface TaskUpdatePayload {
  title?: string;
  title_ar?: string;
  description?: string;
  description_ar?: string;
  status?: TaskStatus;
  priority?: Priority;
  due_date?: string;
  assigned_to?: string;
  field_id?: string;
}

/**
 * Task Creation Response Interface
 * واجهة استجابة إنشاء المهمة
 */
export interface TaskResponse {
  success: boolean;
  data?: Task;
  error?: string;
  message?: string;
  message_ar?: string;
}
