/**
 * SAHOOL Tasks Feature Types
 * أنواع ميزة المهام
 */

import type { Task, TaskStatus, Priority } from '@sahool/api-client';

export interface TaskFormData {
  title: string;
  titleAr: string;
  description?: string;
  descriptionAr?: string;
  dueDate: string;
  priority: Priority;
  fieldId?: string;
  assignedTo?: string;
  status?: TaskStatus;
}

export interface TaskFilters {
  search?: string;
  status?: TaskStatus;
  priority?: Priority;
  fieldId?: string;
  assignedTo?: string;
  dueDateFrom?: string;
  dueDateTo?: string;
}

export interface TaskBoardColumn {
  id: TaskStatus;
  title: string;
  titleAr: string;
  tasks: Task[];
  color: string;
}

export type { Task, TaskStatus, Priority };
