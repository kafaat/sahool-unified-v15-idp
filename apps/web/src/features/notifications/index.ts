/**
 * Notifications Feature - Main Exports
 * ميزة الإشعارات - الصادرات الرئيسية
 */

// API Layer
export { notificationsApi, ERROR_MESSAGES } from "./api";

// Types
export type {
  Notification,
  NotificationType,
  NotificationPriority,
  NotificationChannel,
  NotificationPreferences,
  NotificationFilters,
} from "./types";

// Hooks - Query
export {
  notificationKeys,
  useNotifications,
  useNotification,
  useUnreadCount,
  useNotificationPreferences,
} from "./hooks/useNotifications";

// Hooks - Mutations
export {
  useMarkRead,
  useMarkAllRead,
  useUpdatePreferences,
  useSubscribe,
  useUnsubscribe,
} from "./hooks/useNotifications";
