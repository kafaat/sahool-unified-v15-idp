/**
 * Settings Feature - API Layer
 * طبقة API لميزة الإعدادات
 */

import { type AxiosError } from "axios";
import { createApiClient, logger } from "@/lib/api/factory";
import { API_PREFIX } from "@sahool/shared-types/contracts";
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
} from "./types";

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient();

// Error messages in Arabic and English
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: "Network error. Using offline data.",
    ar: "خطأ في الاتصال. استخدام البيانات المحفوظة.",
  },
  PROFILE_FETCH_FAILED: {
    en: "Failed to fetch profile. Using cached data.",
    ar: "فشل في جلب الملف الشخصي. استخدام البيانات المخزنة.",
  },
  PROFILE_UPDATE_FAILED: {
    en: "Failed to update profile. Please try again.",
    ar: "فشل في تحديث الملف الشخصي. الرجاء المحاولة مرة أخرى.",
  },
  AVATAR_UPLOAD_FAILED: {
    en: "Failed to upload avatar. Please try again.",
    ar: "فشل في رفع الصورة الشخصية. الرجاء المحاولة مرة أخرى.",
  },
  SETTINGS_FETCH_FAILED: {
    en: "Failed to fetch settings. Using default values.",
    ar: "فشل في جلب الإعدادات. استخدام القيم الافتراضية.",
  },
  SETTINGS_UPDATE_FAILED: {
    en: "Failed to update settings. Please try again.",
    ar: "فشل في تحديث الإعدادات. الرجاء المحاولة مرة أخرى.",
  },
  PASSWORD_CHANGE_FAILED: {
    en: "Failed to change password. Please try again.",
    ar: "فشل في تغيير كلمة المرور. الرجاء المحاولة مرة أخرى.",
  },
  TWO_FACTOR_FAILED: {
    en: "Failed to update two-factor authentication. Please try again.",
    ar: "فشل في تحديث المصادقة الثنائية. الرجاء المحاولة مرة أخرى.",
  },
  SESSION_TERMINATE_FAILED: {
    en: "Failed to terminate session. Please try again.",
    ar: "فشل في إنهاء الجلسة. الرجاء المحاولة مرة أخرى.",
  },
  ACCOUNT_DISCONNECT_FAILED: {
    en: "Failed to disconnect account. Please try again.",
    ar: "فشل في فصل الحساب. الرجاء المحاولة مرة أخرى.",
  },
  SUBSCRIPTION_CANCEL_FAILED: {
    en: "Failed to cancel subscription. Please try again.",
    ar: "فشل في إلغاء الاشتراك. الرجاء المحاولة مرة أخرى.",
  },
  ACCOUNT_DELETE_FAILED: {
    en: "Failed to delete account. Please try again.",
    ar: "فشل في حذف الحساب. الرجاء المحاولة مرة أخرى.",
  },
};

// Mock data for fallback (extracted to separate file for bundle optimization)
import {
  MOCK_USER_PROFILE,
  MOCK_NOTIFICATION_PREFERENCES,
  MOCK_SECURITY_SETTINGS,
  MOCK_PRIVACY_SETTINGS,
  MOCK_DISPLAY_PREFERENCES,
  MOCK_INTEGRATION_SETTINGS,
  MOCK_SUBSCRIPTION_INFO,
} from "./api.mock";

// API Functions
export const settingsApi = {
  /**
   * Get user profile
   */
  getProfile: async (): Promise<UserProfile> => {
    try {
      const response = await api.get(`${API_PREFIX}/users/profile`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(
        "Failed to fetch user profile from API, using mock data:",
        error,
      );
      return MOCK_USER_PROFILE;
    }
  },

  /**
   * Update user profile
   */
  updateProfile: async (data: UpdateProfilePayload): Promise<UserProfile> => {
    try {
      const response = await api.put(`${API_PREFIX}/users/profile`, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to update user profile:", error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.PROFILE_UPDATE_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.PROFILE_UPDATE_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Upload profile avatar
   */
  uploadAvatar: async (file: File): Promise<string> => {
    try {
      const formData = new FormData();
      formData.append("avatar", file);

      const response = await api.post(
        `${API_PREFIX}/users/profile/avatar`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        },
      );

      return response.data.url || response.data.data?.url;
    } catch (error) {
      logger.error("Failed to upload avatar:", error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.AVATAR_UPLOAD_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.AVATAR_UPLOAD_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Get notification preferences
   */
  getNotificationSettings: async (): Promise<NotificationPreferences> => {
    try {
      const response = await api.get(`${API_PREFIX}/users/settings/notifications`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(
        "Failed to fetch notification settings from API, using mock data:",
        error,
      );
      return MOCK_NOTIFICATION_PREFERENCES;
    }
  },

  /**
   * Update notification preferences
   */
  updateNotificationSettings: async (
    data: NotificationPreferences,
  ): Promise<NotificationPreferences> => {
    try {
      const response = await api.put(
        `${API_PREFIX}/users/settings/notifications`,
        data,
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to update notification settings:", error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Get security settings
   */
  getSecuritySettings: async (): Promise<SecuritySettings> => {
    try {
      const response = await api.get(`${API_PREFIX}/users/settings/security`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(
        "Failed to fetch security settings from API, using mock data:",
        error,
      );
      return MOCK_SECURITY_SETTINGS;
    }
  },

  /**
   * Change password
   */
  changePassword: async (data: UpdatePasswordPayload): Promise<void> => {
    try {
      await api.put(`${API_PREFIX}/users/settings/security/password`, data);
    } catch (error) {
      logger.error("Failed to change password:", error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.PASSWORD_CHANGE_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.PASSWORD_CHANGE_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Enable/disable two-factor authentication
   */
  enable2FA: async (data: {
    enabled: boolean;
    method?: "2fa_app" | "sms" | "email";
  }): Promise<SecuritySettings> => {
    try {
      const response = await api.put(
        `${API_PREFIX}/users/settings/security/2fa`,
        data,
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to update two-factor authentication:", error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.TWO_FACTOR_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.TWO_FACTOR_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Terminate a session
   */
  terminateSession: async (sessionId: string): Promise<void> => {
    try {
      await api.delete(`${API_PREFIX}/users/settings/security/sessions/${sessionId}`);
    } catch (error) {
      logger.error(`Failed to terminate session ${sessionId}:`, error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.SESSION_TERMINATE_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.SESSION_TERMINATE_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Get privacy settings
   */
  getPrivacySettings: async (): Promise<PrivacySettings> => {
    try {
      const response = await api.get(`${API_PREFIX}/users/settings/privacy`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(
        "Failed to fetch privacy settings from API, using mock data:",
        error,
      );
      return MOCK_PRIVACY_SETTINGS;
    }
  },

  /**
   * Update privacy settings
   */
  updatePrivacySettings: async (
    data: PrivacySettings,
  ): Promise<PrivacySettings> => {
    try {
      const response = await api.put(`${API_PREFIX}/users/settings/privacy`, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to update privacy settings:", error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Get display preferences
   */
  getDisplayPreferences: async (): Promise<DisplayPreferences> => {
    try {
      const response = await api.get(`${API_PREFIX}/users/settings/display`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(
        "Failed to fetch display preferences from API, using mock data:",
        error,
      );
      return MOCK_DISPLAY_PREFERENCES;
    }
  },

  /**
   * Update display preferences
   */
  updateDisplayPreferences: async (
    data: DisplayPreferences,
  ): Promise<DisplayPreferences> => {
    try {
      const response = await api.put(`${API_PREFIX}/users/settings/display`, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to update display preferences:", error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Get integration settings
   */
  getIntegrationSettings: async (): Promise<IntegrationSettings> => {
    try {
      const response = await api.get(`${API_PREFIX}/users/settings/integrations`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(
        "Failed to fetch integration settings from API, using mock data:",
        error,
      );
      return MOCK_INTEGRATION_SETTINGS;
    }
  },

  /**
   * Update integration settings
   */
  updateIntegrationSettings: async (
    data: Partial<IntegrationSettings>,
  ): Promise<IntegrationSettings> => {
    try {
      const response = await api.put(
        `${API_PREFIX}/users/settings/integrations`,
        data,
      );
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to update integration settings:", error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Disconnect an account
   */
  disconnectAccount: async (accountId: string): Promise<void> => {
    try {
      await api.delete(
        `${API_PREFIX}/users/settings/integrations/accounts/${accountId}`,
      );
    } catch (error) {
      logger.error(`Failed to disconnect account ${accountId}:`, error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.ACCOUNT_DISCONNECT_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.ACCOUNT_DISCONNECT_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Get subscription info
   */
  getSubscriptionInfo: async (): Promise<SubscriptionInfo> => {
    try {
      const response = await api.get(`${API_PREFIX}/users/subscription`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(
        "Failed to fetch subscription info from API, using mock data:",
        error,
      );
      return MOCK_SUBSCRIPTION_INFO;
    }
  },

  /**
   * Cancel subscription
   */
  cancelSubscription: async (): Promise<void> => {
    try {
      await api.post(`${API_PREFIX}/users/subscription/cancel`);
    } catch (error) {
      logger.error("Failed to cancel subscription:", error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.SUBSCRIPTION_CANCEL_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.SUBSCRIPTION_CANCEL_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },

  /**
   * Delete account
   */
  deleteAccount: async (password: string): Promise<void> => {
    try {
      await api.delete(`${API_PREFIX}/users/account`, {
        data: { password },
      });
    } catch (error) {
      logger.error("Failed to delete account:", error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.ACCOUNT_DELETE_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.ACCOUNT_DELETE_FAILED.ar;

      throw new Error(
        JSON.stringify({
          message: errorMessage,
          messageAr: errorMessageAr,
        }),
      );
    }
  },
};
