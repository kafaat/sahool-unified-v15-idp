/**
 * Settings Feature
 * ميزة الإعدادات
 *
 * This feature handles:
 * - User profile management
 * - Notification preferences
 * - Security settings
 * - Privacy controls
 * - Display preferences
 * - Integrations
 * - Subscription management
 */

// Component exports
export { SettingsPage } from "./components/SettingsPage";
export { ProfileForm } from "./components/ProfileForm";

// API exports
export { settingsApi, ERROR_MESSAGES } from "./api";

// Hook exports
export {
  useUserProfile,
  useUpdateProfile,
  useUploadAvatar,
  useNotificationPreferences,
  useUpdateNotificationPreferences,
  useSecuritySettings,
  useUpdatePassword,
  useToggleTwoFactor,
  useTerminateSession,
  usePrivacySettings,
  useUpdatePrivacySettings,
  useDisplayPreferences,
  useUpdateDisplayPreferences,
  useIntegrationSettings,
  useUpdateIntegrationSettings,
  useDisconnectAccount,
  useSubscriptionInfo,
  useCancelSubscription,
  useDeleteAccount,
} from "./hooks/useSettings";

// Type exports
export type {
  UserProfile,
  NotificationPreferences,
  SecuritySettings,
  ActiveSession,
  LoginHistory,
  PrivacySettings,
  DisplayPreferences,
  IntegrationSettings,
  ConnectedAccount,
  SubscriptionInfo,
  UpdateProfilePayload,
  UpdatePasswordPayload,
} from "./types";

export const SETTINGS_FEATURE = "settings" as const;
