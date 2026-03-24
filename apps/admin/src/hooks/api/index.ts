/**
 * SAHOOL Admin - API Hooks barrel export
 * تصدير خطافات API
 */

// Core
export {
  useApiQuery,
  useApiMutation,
  invalidateQueries,
  type ApiError,
  type UseApiQueryResult,
  type UseApiMutationResult,
} from './use-api-query';

// Dashboard
export {
  useDashboardStats,
  useYieldTrends,
  useCropDistribution,
  useWeeklyActivity,
  usePlatformMetrics,
} from './use-dashboard';

// Fields
export {
  useFields,
  useField,
  useFieldNDVI,
  useFieldIndices,
  useFieldIntelligence,
  useCreateField,
  useUpdateField,
  useDeleteField,
} from './use-fields';

// Weather
export {
  useWeatherCurrent,
  useWeatherForecast,
  useAgriculturalReport,
  useWeatherByLocation,
  useWeatherForecastByLocation,
  useWeatherLocations,
  useWeatherAlerts,
} from './use-weather';

// Notifications
export { useNotifications, useMarkNotificationRead } from './use-notifications';

// Tasks
export { useTasks, useUpdateTaskStatus, useCreateTask } from './use-tasks';

// Alerts
export { useAlerts, useAcknowledgeAlert } from './use-alerts';

// Realtime
export { useRealtimeSync } from './use-realtime';
