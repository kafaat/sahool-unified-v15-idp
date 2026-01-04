/**
 * SAHOOL Home Feature Exports
 * صادرات ميزة الصفحة الرئيسية
 */

// ═══════════════════════════════════════════════════════════════════════════
// Components
// ═══════════════════════════════════════════════════════════════════════════

export { DashboardStats } from './components/DashboardStats';
export { RecentActivity } from './components/RecentActivity';
export { WeatherWidget } from './components/WeatherWidget';
export { TasksSummary } from './components/TasksSummary';
export { QuickActions } from './components/QuickActions';

// ═══════════════════════════════════════════════════════════════════════════
// Hooks
// ═══════════════════════════════════════════════════════════════════════════

export { useDashboardData } from './hooks/useDashboardData';
export { useStats, useEnhancedStats } from './hooks/useStats';
export { useUpcomingTasks } from './hooks/useUpcomingTasks';
export { useRecentActivity } from './hooks/useRecentActivity';
export { useAlerts } from './hooks/useAlerts';
export { useDashboardMutations } from './hooks/useDashboardMutations';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export type { DashboardData } from './hooks/useDashboardData';
export type { DashboardStats as DashboardStatsType } from './hooks/useStats';
export type { UpcomingTask } from './hooks/useUpcomingTasks';
export type { ActivityItem } from './hooks/useRecentActivity';

// Export all types from types.ts
export type {
  ActivityType,
  TaskPriority,
  TaskStatus,
  DashboardTask,
  DashboardWeather,
  WeatherForecastItem,
  StatTrend,
  EnhancedStats,
  AlertSeverity,
  AlertCategory,
  DashboardAlert,
  DashboardFilters,
  ApiDashboardResponse,
  ApiStatsResponse,
  ApiActivityResponse,
  ApiTasksResponse,
  MarkTaskCompletePayload,
  DismissAlertPayload,
  MarkActivityReadPayload,
  RefreshDashboardPayload,
  QuickAction,
  UseDashboardDataReturn,
  UseDashboardMutationsReturn,
} from './types';

// ═══════════════════════════════════════════════════════════════════════════
// API
// ═══════════════════════════════════════════════════════════════════════════

export { dashboardApi, ERROR_MESSAGES } from './api';
