/**
 * SAHOOL Tasks Feature Types
 * أنواع ميزة المهام
 */

import type { Task, TaskStatus, Priority } from '@sahool/api-client';

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

export interface TaskFilters {
  search?: string;
  status?: TaskStatus;
  priority?: Priority;
  field_id?: string;
  assigned_to?: string;
  due_date_from?: string;
  due_date_to?: string;
}

export interface TaskBoardColumn {
  id: TaskStatus;
  title: string;
  title_ar: string;
  tasks: Task[];
  color: string;
}

export type { Task, TaskStatus, Priority };
