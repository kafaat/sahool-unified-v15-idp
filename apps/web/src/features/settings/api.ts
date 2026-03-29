/**
 * Settings Feature - API Layer
 * طبقة API لميزة الإعدادات
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { API_PREFIX } from '@sahool/shared-types/contracts';
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
} from './types';

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  PROFILE_FETCH_FAILED: {
    en: 'Failed to fetch profile. Using cached data.',
    ar: 'فشل في جلب الملف الشخصي. استخدام البيانات المخزنة.',
  },
  PROFILE_UPDATE_FAILED: {
    en: 'Failed to update profile. Please try again.',
    ar: 'فشل في تحديث الملف الشخصي. الرجاء المحاولة مرة أخرى.',
  },
  AVATAR_UPLOAD_FAILED: {
    en: 'Failed to upload avatar. Please try again.',
    ar: 'فشل في رفع الصورة الشخصية. الرجاء المحاولة مرة أخرى.',
  },
  SETTINGS_FETCH_FAILED: {
    en: 'Failed to fetch settings. Using default values.',
    ar: 'فشل في جلب الإعدادات. استخدام القيم الافتراضية.',
  },
  SETTINGS_UPDATE_FAILED: {
    en: 'Failed to update settings. Please try again.',
    ar: 'فشل في تحديث الإعدادات. الرجاء المحاولة مرة أخرى.',
  },
  PASSWORD_CHANGE_FAILED: {
    en: 'Failed to change password. Please try again.',
    ar: 'فشل في تغيير كلمة المرور. الرجاء المحاولة مرة أخرى.',
  },
  TWO_FACTOR_FAILED: {
    en: 'Failed to update two-factor authentication. Please try again.',
    ar: 'فشل في تحديث المصادقة الثنائية. الرجاء المحاولة مرة أخرى.',
  },
  SESSION_TERMINATE_FAILED: {
    en: 'Failed to terminate session. Please try again.',
    ar: 'فشل في إنهاء الجلسة. الرجاء المحاولة مرة أخرى.',
  },
  ACCOUNT_DISCONNECT_FAILED: {
    en: 'Failed to disconnect account. Please try again.',
    ar: 'فشل في فصل الحساب. الرجاء المحاولة مرة أخرى.',
  },
  SUBSCRIPTION_CANCEL_FAILED: {
    en: 'Failed to cancel subscription. Please try again.',
    ar: 'فشل في إلغاء الاشتراك. الرجاء المحاولة مرة أخرى.',
  },
  ACCOUNT_DELETE_FAILED: {
    en: 'Failed to delete account. Please try again.',
    ar: 'فشل في حذف الحساب. الرجاء المحاولة مرة أخرى.',
  },
};

// API Functions
export const settingsApi = {
  /**
   * Get user profile
   */
  getProfile: async (): Promise<UserProfile> => {
    return safeFetch(`${API_PREFIX}/users/profile`, async () => {
      const response = await api.get(`${API_PREFIX}/users/profile`);
      return response.data.data || response.data;
    });
  },

  /**
   * Update user profile
   */
  updateProfile: async (data: UpdateProfilePayload): Promise<UserProfile> => {
    return safeFetch(`${API_PREFIX}/users/profile`, async () => {
      const response = await api.put(`${API_PREFIX}/users/profile`, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Upload profile avatar
   */
  uploadAvatar: async (file: File): Promise<string> => {
    return safeFetch(`${API_PREFIX}/users/profile/avatar`, async () => {
      const formData = new FormData();
      formData.append('avatar', file);
      const response = await api.post(`${API_PREFIX}/users/profile/avatar`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.url || response.data.data?.url;
    });
  },

  /**
   * Get notification preferences
   */
  getNotificationSettings: async (): Promise<NotificationPreferences> => {
    return safeFetch(`${API_PREFIX}/users/settings/notifications`, async () => {
      const response = await api.get(`${API_PREFIX}/users/settings/notifications`);
      return response.data.data || response.data;
    });
  },

  /**
   * Update notification preferences
   */
  updateNotificationSettings: async (
    data: NotificationPreferences
  ): Promise<NotificationPreferences> => {
    return safeFetch(`${API_PREFIX}/users/settings/notifications`, async () => {
      const response = await api.put(`${API_PREFIX}/users/settings/notifications`, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Get security settings
   */
  getSecuritySettings: async (): Promise<SecuritySettings> => {
    return safeFetch(`${API_PREFIX}/users/settings/security`, async () => {
      const response = await api.get(`${API_PREFIX}/users/settings/security`);
      return response.data.data || response.data;
    });
  },

  /**
   * Change password
   */
  changePassword: async (data: UpdatePasswordPayload): Promise<void> => {
    return safeFetch(`${API_PREFIX}/users/settings/security/password`, async () => {
      await api.put(`${API_PREFIX}/users/settings/security/password`, data);
    });
  },

  /**
   * Enable/disable two-factor authentication
   */
  enable2FA: async (data: {
    enabled: boolean;
    method?: '2fa_app' | 'sms' | 'email';
  }): Promise<SecuritySettings> => {
    return safeFetch(`${API_PREFIX}/users/settings/security/2fa`, async () => {
      const response = await api.put(`${API_PREFIX}/users/settings/security/2fa`, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Terminate a session
   */
  terminateSession: async (sessionId: string): Promise<void> => {
    return safeFetch(
      `${API_PREFIX}/users/settings/security/sessions/${sessionId}`,
      async () => {
        await api.delete(`${API_PREFIX}/users/settings/security/sessions/${sessionId}`);
      }
    );
  },

  /**
   * Get privacy settings
   */
  getPrivacySettings: async (): Promise<PrivacySettings> => {
    return safeFetch(`${API_PREFIX}/users/settings/privacy`, async () => {
      const response = await api.get(`${API_PREFIX}/users/settings/privacy`);
      return response.data.data || response.data;
    });
  },

  /**
   * Update privacy settings
   */
  updatePrivacySettings: async (data: PrivacySettings): Promise<PrivacySettings> => {
    return safeFetch(`${API_PREFIX}/users/settings/privacy`, async () => {
      const response = await api.put(`${API_PREFIX}/users/settings/privacy`, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Get display preferences
   */
  getDisplayPreferences: async (): Promise<DisplayPreferences> => {
    return safeFetch(`${API_PREFIX}/users/settings/display`, async () => {
      const response = await api.get(`${API_PREFIX}/users/settings/display`);
      return response.data.data || response.data;
    });
  },

  /**
   * Update display preferences
   */
  updateDisplayPreferences: async (data: DisplayPreferences): Promise<DisplayPreferences> => {
    return safeFetch(`${API_PREFIX}/users/settings/display`, async () => {
      const response = await api.put(`${API_PREFIX}/users/settings/display`, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Get integration settings
   */
  getIntegrationSettings: async (): Promise<IntegrationSettings> => {
    return safeFetch(`${API_PREFIX}/users/settings/integrations`, async () => {
      const response = await api.get(`${API_PREFIX}/users/settings/integrations`);
      return response.data.data || response.data;
    });
  },

  /**
   * Update integration settings
   */
  updateIntegrationSettings: async (
    data: Partial<IntegrationSettings>
  ): Promise<IntegrationSettings> => {
    return safeFetch(`${API_PREFIX}/users/settings/integrations`, async () => {
      const response = await api.put(`${API_PREFIX}/users/settings/integrations`, data);
      return response.data.data || response.data;
    });
  },

  /**
   * Disconnect an account
   */
  disconnectAccount: async (accountId: string): Promise<void> => {
    return safeFetch(
      `${API_PREFIX}/users/settings/integrations/accounts/${accountId}`,
      async () => {
        await api.delete(
          `${API_PREFIX}/users/settings/integrations/accounts/${accountId}`
        );
      }
    );
  },

  /**
   * Get subscription info
   */
  getSubscriptionInfo: async (): Promise<SubscriptionInfo> => {
    return safeFetch(`${API_PREFIX}/users/subscription`, async () => {
      const response = await api.get(`${API_PREFIX}/users/subscription`);
      return response.data.data || response.data;
    });
  },

  /**
   * Cancel subscription
   */
  cancelSubscription: async (): Promise<void> => {
    return safeFetch(`${API_PREFIX}/users/subscription/cancel`, async () => {
      await api.post(`${API_PREFIX}/users/subscription/cancel`);
    });
  },

  /**
   * Delete account
   */
  deleteAccount: async (password: string): Promise<void> => {
    return safeFetch(`${API_PREFIX}/users/account`, async () => {
      await api.delete(`${API_PREFIX}/users/account`, { data: { password } });
    });
  },
};
