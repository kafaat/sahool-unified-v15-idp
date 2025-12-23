/**
 * Settings Feature - React Hooks
 * خطافات React لميزة الإعدادات
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import type {
  UserProfile,
  NotificationPreferences,
  SecuritySettings,
  PrivacySettings,
  DisplayPreferences,
  IntegrationSettings,
  SubscriptionInfo,
  UpdateProfilePayload,
  UpdatePasswordPayload,
} from '../types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

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
    queryFn: async (): Promise<UserProfile> => {
      const response = await api.get('/v1/users/profile');
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to update user profile
 */
export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: UpdateProfilePayload): Promise<UserProfile> => {
      const response = await api.put('/v1/users/profile', data);
      return response.data;
    },
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
    mutationFn: async (file: File): Promise<string> => {
      const formData = new FormData();
      formData.append('avatar', file);

      const response = await api.post('/v1/users/profile/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data.url;
    },
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
    queryFn: async (): Promise<NotificationPreferences> => {
      const response = await api.get('/v1/users/settings/notifications');
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to update notification preferences
 */
export function useUpdateNotificationPreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: NotificationPreferences): Promise<NotificationPreferences> => {
      const response = await api.put('/v1/users/settings/notifications', data);
      return response.data;
    },
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
    queryFn: async (): Promise<SecuritySettings> => {
      const response = await api.get('/v1/users/settings/security');
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to update password
 */
export function useUpdatePassword() {
  return useMutation({
    mutationFn: async (data: UpdatePasswordPayload): Promise<void> => {
      await api.put('/v1/users/settings/security/password', data);
    },
  });
}

/**
 * Hook to enable/disable two-factor authentication
 */
export function useToggleTwoFactor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      enabled: boolean;
      method?: '2fa_app' | 'sms' | 'email';
    }): Promise<SecuritySettings> => {
      const response = await api.put('/v1/users/settings/security/2fa', data);
      return response.data;
    },
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
    mutationFn: async (sessionId: string): Promise<void> => {
      await api.delete(`/v1/users/settings/security/sessions/${sessionId}`);
    },
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
    queryFn: async (): Promise<PrivacySettings> => {
      const response = await api.get('/v1/users/settings/privacy');
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to update privacy settings
 */
export function useUpdatePrivacySettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: PrivacySettings): Promise<PrivacySettings> => {
      const response = await api.put('/v1/users/settings/privacy', data);
      return response.data;
    },
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
    queryFn: async (): Promise<DisplayPreferences> => {
      const response = await api.get('/v1/users/settings/display');
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to update display preferences
 */
export function useUpdateDisplayPreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: DisplayPreferences): Promise<DisplayPreferences> => {
      const response = await api.put('/v1/users/settings/display', data);
      return response.data;
    },
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
    queryFn: async (): Promise<IntegrationSettings> => {
      const response = await api.get('/v1/users/settings/integrations');
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to update integration settings
 */
export function useUpdateIntegrationSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<IntegrationSettings>): Promise<IntegrationSettings> => {
      const response = await api.put('/v1/users/settings/integrations', data);
      return response.data;
    },
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
    mutationFn: async (accountId: string): Promise<void> => {
      await api.delete(`/v1/users/settings/integrations/accounts/${accountId}`);
    },
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
    queryFn: async (): Promise<SubscriptionInfo> => {
      const response = await api.get('/v1/users/subscription');
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to cancel subscription
 */
export function useCancelSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (): Promise<void> => {
      await api.post('/v1/users/subscription/cancel');
    },
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
    mutationFn: async (password: string): Promise<void> => {
      await api.delete('/v1/users/account', {
        data: { password },
      });
    },
  });
}
