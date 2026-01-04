/**
 * Settings Feature - API Layer
 * طبقة API لميزة الإعدادات
 */

import axios, { type AxiosError } from 'axios';
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
import { logger } from '@/lib/logger';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// Only warn during development, don't throw during build
if (!API_BASE_URL && typeof window !== 'undefined') {
  console.warn('NEXT_PUBLIC_API_URL environment variable is not set');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Add auth token interceptor
// SECURITY: Use js-cookie library for safe cookie parsing instead of manual parsing
import Cookies from 'js-cookie';

api.interceptors.request.use((config) => {
  // Get token from cookie using secure cookie parser
  if (typeof window !== 'undefined') {
    const token = Cookies.get('access_token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

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

// Mock data for fallback
const MOCK_USER_PROFILE: UserProfile = {
  id: 'user-1',
  email: 'farmer@sahool.sa',
  name: 'Ahmed Al-Qarni',
  nameAr: 'أحمد القرني',
  phone: '+966501234567',
  avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=Ahmed',
  bio: 'Experienced farmer specializing in sustainable agriculture',
  bioAr: 'مزارع ذو خبرة متخصص في الزراعة المستدامة',
  location: {
    city: 'Riyadh',
    cityAr: 'الرياض',
    region: 'Central Region',
    regionAr: 'المنطقة الوسطى',
    country: 'Saudi Arabia',
    countryAr: 'المملكة العربية السعودية',
  },
  farmDetails: {
    name: 'Al-Qarni Farm',
    nameAr: 'مزرعة القرني',
    totalArea: 50.5,
    establishedYear: 2010,
    farmType: 'family',
    mainCrops: ['Wheat', 'Barley', 'Dates'],
    mainCropsAr: ['قمح', 'شعير', 'تمور'],
  },
  language: 'both',
  timezone: 'Asia/Riyadh',
  dateFormat: 'both',
  role: 'farmer',
  isVerified: true,
  createdAt: '2023-01-15T10:00:00Z',
  updatedAt: new Date().toISOString(),
};

const MOCK_NOTIFICATION_PREFERENCES: NotificationPreferences = {
  email: {
    enabled: true,
    alerts: true,
    updates: true,
    community: false,
    marketing: false,
    weeklyReport: true,
  },
  push: {
    enabled: true,
    alerts: true,
    updates: true,
    community: true,
    tasks: true,
    weather: true,
  },
  sms: {
    enabled: false,
    criticalOnly: true,
  },
};

const MOCK_SECURITY_SETTINGS: SecuritySettings = {
  twoFactorEnabled: false,
  twoFactorMethod: undefined,
  sessions: [
    {
      id: 'session-1',
      device: 'Desktop',
      browser: 'Chrome 120',
      os: 'Windows 11',
      ip: '192.168.1.100',
      location: 'Riyadh, SA',
      lastActive: new Date().toISOString(),
      isCurrent: true,
    },
    {
      id: 'session-2',
      device: 'Mobile',
      browser: 'Safari 17',
      os: 'iOS 17',
      ip: '192.168.1.105',
      location: 'Riyadh, SA',
      lastActive: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      isCurrent: false,
    },
  ],
  lastPasswordChange: '2023-11-01T10:00:00Z',
  loginHistory: [
    {
      id: 'login-1',
      timestamp: new Date().toISOString(),
      device: 'Desktop',
      browser: 'Chrome 120',
      ip: '192.168.1.100',
      location: 'Riyadh, SA',
      success: true,
    },
    {
      id: 'login-2',
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      device: 'Mobile',
      browser: 'Safari 17',
      ip: '192.168.1.105',
      location: 'Riyadh, SA',
      success: true,
    },
  ],
};

const MOCK_PRIVACY_SETTINGS: PrivacySettings = {
  profileVisibility: 'community',
  showEmail: false,
  showPhone: false,
  showLocation: true,
  showFarmDetails: true,
  allowMessages: 'connections',
  dataSharing: {
    analytics: true,
    research: false,
    thirdParty: false,
  },
};

const MOCK_DISPLAY_PREFERENCES: DisplayPreferences = {
  theme: 'auto',
  language: 'ar',
  rtl: true,
  fontSize: 'medium',
  compactMode: false,
  showWeatherWidget: true,
  showQuickActions: true,
  defaultDashboard: 'overview',
};

const MOCK_INTEGRATION_SETTINGS: IntegrationSettings = {
  weatherProvider: 'openweather',
  mapProvider: 'google',
  connectedAccounts: [
    {
      id: 'acc-1',
      provider: 'Google',
      providerAr: 'جوجل',
      accountName: 'farmer@gmail.com',
      connectedAt: '2023-06-15T10:00:00Z',
      status: 'active',
    },
  ],
};

const MOCK_SUBSCRIPTION_INFO: SubscriptionInfo = {
  plan: 'pro',
  planAr: 'احترافي',
  status: 'active',
  startDate: '2024-01-01T00:00:00Z',
  endDate: '2024-12-31T23:59:59Z',
  autoRenew: true,
  features: {
    maxFields: 50,
    maxIoTDevices: 20,
    maxStorage: 100,
    advancedAnalytics: true,
    expertConsultation: true,
    apiAccess: true,
    customReports: true,
  },
  usage: {
    fields: 12,
    iotDevices: 5,
    storage: 23.5,
  },
};

// API Functions
export const settingsApi = {
  /**
   * Get user profile
   */
  getProfile: async (): Promise<UserProfile> => {
    try {
      const response = await api.get('/api/v1/users/profile');
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch user profile from API, using mock data:', error);
      return MOCK_USER_PROFILE;
    }
  },

  /**
   * Update user profile
   */
  updateProfile: async (data: UpdateProfilePayload): Promise<UserProfile> => {
    try {
      const response = await api.put('/api/v1/users/profile', data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to update user profile:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.PROFILE_UPDATE_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.PROFILE_UPDATE_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Upload profile avatar
   */
  uploadAvatar: async (file: File): Promise<string> => {
    try {
      const formData = new FormData();
      formData.append('avatar', file);

      const response = await api.post('/api/v1/users/profile/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data.url || response.data.data?.url;
    } catch (error) {
      logger.error('Failed to upload avatar:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.AVATAR_UPLOAD_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.AVATAR_UPLOAD_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Get notification preferences
   */
  getNotificationSettings: async (): Promise<NotificationPreferences> => {
    try {
      const response = await api.get('/api/v1/users/settings/notifications');
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch notification settings from API, using mock data:', error);
      return MOCK_NOTIFICATION_PREFERENCES;
    }
  },

  /**
   * Update notification preferences
   */
  updateNotificationSettings: async (data: NotificationPreferences): Promise<NotificationPreferences> => {
    try {
      const response = await api.put('/api/v1/users/settings/notifications', data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to update notification settings:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Get security settings
   */
  getSecuritySettings: async (): Promise<SecuritySettings> => {
    try {
      const response = await api.get('/api/v1/users/settings/security');
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch security settings from API, using mock data:', error);
      return MOCK_SECURITY_SETTINGS;
    }
  },

  /**
   * Change password
   */
  changePassword: async (data: UpdatePasswordPayload): Promise<void> => {
    try {
      await api.put('/api/v1/users/settings/security/password', data);
    } catch (error) {
      logger.error('Failed to change password:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.PASSWORD_CHANGE_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.PASSWORD_CHANGE_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Enable/disable two-factor authentication
   */
  enable2FA: async (data: {
    enabled: boolean;
    method?: '2fa_app' | 'sms' | 'email';
  }): Promise<SecuritySettings> => {
    try {
      const response = await api.put('/api/v1/users/settings/security/2fa', data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to update two-factor authentication:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.TWO_FACTOR_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.TWO_FACTOR_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Terminate a session
   */
  terminateSession: async (sessionId: string): Promise<void> => {
    try {
      await api.delete(`/api/v1/users/settings/security/sessions/${sessionId}`);
    } catch (error) {
      logger.error(`Failed to terminate session ${sessionId}:`, error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.SESSION_TERMINATE_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.SESSION_TERMINATE_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Get privacy settings
   */
  getPrivacySettings: async (): Promise<PrivacySettings> => {
    try {
      const response = await api.get('/api/v1/users/settings/privacy');
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch privacy settings from API, using mock data:', error);
      return MOCK_PRIVACY_SETTINGS;
    }
  },

  /**
   * Update privacy settings
   */
  updatePrivacySettings: async (data: PrivacySettings): Promise<PrivacySettings> => {
    try {
      const response = await api.put('/api/v1/users/settings/privacy', data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to update privacy settings:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Get display preferences
   */
  getDisplayPreferences: async (): Promise<DisplayPreferences> => {
    try {
      const response = await api.get('/api/v1/users/settings/display');
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch display preferences from API, using mock data:', error);
      return MOCK_DISPLAY_PREFERENCES;
    }
  },

  /**
   * Update display preferences
   */
  updateDisplayPreferences: async (data: DisplayPreferences): Promise<DisplayPreferences> => {
    try {
      const response = await api.put('/api/v1/users/settings/display', data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to update display preferences:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Get integration settings
   */
  getIntegrationSettings: async (): Promise<IntegrationSettings> => {
    try {
      const response = await api.get('/api/v1/users/settings/integrations');
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch integration settings from API, using mock data:', error);
      return MOCK_INTEGRATION_SETTINGS;
    }
  },

  /**
   * Update integration settings
   */
  updateIntegrationSettings: async (data: Partial<IntegrationSettings>): Promise<IntegrationSettings> => {
    try {
      const response = await api.put('/api/v1/users/settings/integrations', data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to update integration settings:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.SETTINGS_UPDATE_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Disconnect an account
   */
  disconnectAccount: async (accountId: string): Promise<void> => {
    try {
      await api.delete(`/api/v1/users/settings/integrations/accounts/${accountId}`);
    } catch (error) {
      logger.error(`Failed to disconnect account ${accountId}:`, error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.ACCOUNT_DISCONNECT_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.ACCOUNT_DISCONNECT_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Get subscription info
   */
  getSubscriptionInfo: async (): Promise<SubscriptionInfo> => {
    try {
      const response = await api.get('/api/v1/users/subscription');
      return response.data.data || response.data;
    } catch (error) {
      logger.warn('Failed to fetch subscription info from API, using mock data:', error);
      return MOCK_SUBSCRIPTION_INFO;
    }
  },

  /**
   * Cancel subscription
   */
  cancelSubscription: async (): Promise<void> => {
    try {
      await api.post('/api/v1/users/subscription/cancel');
    } catch (error) {
      logger.error('Failed to cancel subscription:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.SUBSCRIPTION_CANCEL_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.SUBSCRIPTION_CANCEL_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },

  /**
   * Delete account
   */
  deleteAccount: async (password: string): Promise<void> => {
    try {
      await api.delete('/api/v1/users/account', {
        data: { password },
      });
    } catch (error) {
      logger.error('Failed to delete account:', error);

      const axiosError = error as AxiosError<{ message?: string; message_ar?: string }>;
      const errorMessage = axiosError.response?.data?.message || ERROR_MESSAGES.ACCOUNT_DELETE_FAILED.en;
      const errorMessageAr = axiosError.response?.data?.message_ar || ERROR_MESSAGES.ACCOUNT_DELETE_FAILED.ar;

      throw new Error(JSON.stringify({
        message: errorMessage,
        messageAr: errorMessageAr,
      }));
    }
  },
};
