/**
 * Settings Feature - React Hooks
 * خطافات React لميزة الإعدادات
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { settingsApi } from '../api';
import type {
  NotificationPreferences,
  PrivacySettings,
  DisplayPreferences,
  IntegrationSettings,
  UpdateProfilePayload,
  UpdatePasswordPayload,
} from '../types';

// Query Keys
const SETTINGS_KEYS = {
  all: ['settings'] as const,
  profile: () => [...SETTINGS_KEYS.all, 'profile'] as const,
  notifications: () => [...SETTINGS_KEYS.all, 'notifications'] as const,
  security: () => [...SETTINGS_KEYS.all, 'security'] as const,
  privacy: () => [...SETTINGS_KEYS.all, 'privacy'] as const,
  display: () => [...SETTINGS_KEYS.all, 'display'] as const,
  integrations: () => [...SETTINGS_KEYS.all, 'integrations'] as const,
  subscription: () => [...SETTINGS_KEYS.all, 'subscription'] as const,
};

/**
 * Hook to fetch user profile
 */
export function useUserProfile() {
  return useQuery({
    queryKey: SETTINGS_KEYS.profile(),
    queryFn: () => settingsApi.getProfile(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to update user profile
 */
export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateProfilePayload) => settingsApi.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEYS.profile() });
    },
  });
}

/**
 * Hook to upload profile avatar
 */
export function useUploadAvatar() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => settingsApi.uploadAvatar(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEYS.profile() });
    },
  });
}

/**
 * Hook to fetch notification preferences
 */
export function useNotificationPreferences() {
  return useQuery({
    queryKey: SETTINGS_KEYS.notifications(),
    queryFn: () => settingsApi.getNotificationSettings(),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to update notification preferences
 */
export function useUpdateNotificationPreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: NotificationPreferences) => settingsApi.updateNotificationSettings(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEYS.notifications() });
    },
  });
}

/**
 * Hook to fetch security settings
 */
export function useSecuritySettings() {
  return useQuery({
    queryKey: SETTINGS_KEYS.security(),
    queryFn: () => settingsApi.getSecuritySettings(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to update password
 */
export function useUpdatePassword() {
  return useMutation({
    mutationFn: (data: UpdatePasswordPayload) => settingsApi.changePassword(data),
  });
}

/**
 * Hook to enable/disable two-factor authentication
 */
export function useToggleTwoFactor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      enabled: boolean;
      method?: '2fa_app' | 'sms' | 'email';
    }) => settingsApi.enable2FA(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEYS.security() });
    },
  });
}

/**
 * Hook to terminate a session
 */
export function useTerminateSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => settingsApi.terminateSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEYS.security() });
    },
  });
}

/**
 * Hook to fetch privacy settings
 */
export function usePrivacySettings() {
  return useQuery({
    queryKey: SETTINGS_KEYS.privacy(),
    queryFn: () => settingsApi.getPrivacySettings(),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to update privacy settings
 */
export function useUpdatePrivacySettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: PrivacySettings) => settingsApi.updatePrivacySettings(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEYS.privacy() });
    },
  });
}

/**
 * Hook to fetch display preferences
 */
export function useDisplayPreferences() {
  return useQuery({
    queryKey: SETTINGS_KEYS.display(),
    queryFn: () => settingsApi.getDisplayPreferences(),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to update display preferences
 */
export function useUpdateDisplayPreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DisplayPreferences) => settingsApi.updateDisplayPreferences(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEYS.display() });
    },
  });
}

/**
 * Hook to fetch integration settings
 */
export function useIntegrationSettings() {
  return useQuery({
    queryKey: SETTINGS_KEYS.integrations(),
    queryFn: () => settingsApi.getIntegrationSettings(),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to update integration settings
 */
export function useUpdateIntegrationSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<IntegrationSettings>) => settingsApi.updateIntegrationSettings(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEYS.integrations() });
    },
  });
}

/**
 * Hook to disconnect an account
 */
export function useDisconnectAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (accountId: string) => settingsApi.disconnectAccount(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEYS.integrations() });
    },
  });
}

/**
 * Hook to fetch subscription info
 */
export function useSubscriptionInfo() {
  return useQuery({
    queryKey: SETTINGS_KEYS.subscription(),
    queryFn: () => settingsApi.getSubscriptionInfo(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to cancel subscription
 */
export function useCancelSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => settingsApi.cancelSubscription(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SETTINGS_KEYS.subscription() });
    },
  });
}

/**
 * Hook to delete account
 */
export function useDeleteAccount() {
  return useMutation({
    mutationFn: (password: string) => settingsApi.deleteAccount(password),
  });
}
