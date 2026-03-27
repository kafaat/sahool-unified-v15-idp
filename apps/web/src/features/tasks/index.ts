/**
 * SAHOOL Tasks Feature Exports
 * صادرات ميزة المهام
 */

// Components
export { TasksBoard } from './components/TasksBoard';
export { TasksList } from './components/TasksList';
export { TaskCard } from './components/TaskCard';
export { TaskForm } from './components/TaskForm';
export { default as TaskFiltersComponent } from './components/TaskFilters';

// API
export { tasksApi, ERROR_MESSAGES } from './api';

// Hooks - Query Hooks
export {
  useTasks,
  useTask,
  useTasksByField,
  useTasksByUser,
  useTasksByStatus,
  useOverdueTasks,
} from './hooks/useTasks';

// Hooks - Mutation Hooks
export {
  useCreateTask,
  useUpdateTask,
  useDeleteTask,
  useCompleteTask,
  useUpdateTaskStatus,
  useAssignTask,
} from './hooks/useTasks';

// Types
export type {
  Task,
  TaskFormData,
  TaskFilters,
  TaskStatus,
  Priority,
  TaskBoardColumn,
  TaskEvidence,
  TaskAssignment,
  TaskStatistics,
  TaskUpdatePayload,
  TaskResponse,
} from './types';
