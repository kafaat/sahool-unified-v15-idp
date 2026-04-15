/**
 * Notifications Feature - API Layer
 * طبقة API لميزة الإشعارات
 */

import { createApiClient, logger } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { NOTIFICATION_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';
import type { Notification, NotificationPreferences, NotificationFilters } from './types';

const api = createApiClient();

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Using offline data.',
    ar: 'خطأ في الاتصال. استخدام البيانات المحفوظة.',
  },
  FETCH_FAILED: {
    en: 'Failed to fetch notifications.',
    ar: 'فشل في جلب الإشعارات.',
  },
  MARK_READ_FAILED: {
    en: 'Failed to mark notification as read.',
    ar: 'فشل في تحديد الإشعار كمقروء.',
  },
  PREFERENCES_FAILED: {
    en: 'Failed to update notification preferences.',
    ar: 'فشل في تحديث تفضيلات الإشعارات.',
  },
};

const MOCK_NOTIFICATIONS: Notification[] = [
  {
    id: 'notif-1',
    type: 'alert',
    title: 'Irrigation Reminder',
    titleAr: 'تذكير بالري',
    message: 'Field #1 needs irrigation today based on soil moisture levels.',
    messageAr: 'الحقل رقم 1 يحتاج للري اليوم بناءً على مستويات رطوبة التربة.',
    read: false,
    priority: 'high',
    channel: 'push',
    metadata: { fieldId: 'field-1' },
    createdAt: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
  },
  {
    id: 'notif-2',
    type: 'info',
    title: 'Weather Update',
    titleAr: 'تحديث الطقس',
    message: 'Rain expected tomorrow. Irrigation may not be needed.',
    messageAr: 'أمطار متوقعة غداً. قد لا تكون هناك حاجة للري.',
    read: true,
    priority: 'medium',
    channel: 'push',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
  },
];

export const notificationsApi = {
  getNotifications: async (filters?: NotificationFilters): Promise<Notification[]> => {
    return safeFetch(NOTIFICATION_ENDPOINTS.LIST, async () => {
      const params = new URLSearchParams();
      if (filters?.type) params.set('type', filters.type);
      if (filters?.read !== undefined) params.set('read', String(filters.read));
      if (filters?.priority) params.set('priority', filters.priority);

      const qs = params.toString();
      const url = qs ? `${NOTIFICATION_ENDPOINTS.LIST}?${qs}` : NOTIFICATION_ENDPOINTS.LIST;
      const response = await api.get(url);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      throw new Error('API returned unexpected format for notifications');
    });
  },

  getById: async (id: string): Promise<Notification> => {
    try {
      const url = buildUrl(NOTIFICATION_ENDPOINTS.GET, { notificationId: id });
      const response = await api.get(url);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch notification ${id}:`, error);
      const mock = MOCK_NOTIFICATIONS.find((n) => n.id === id);
      if (mock) return mock;
      throw new Error(ERROR_MESSAGES.FETCH_FAILED.en);
    }
  },

  markRead: async (id: string): Promise<void> => {
    try {
      const url = buildUrl(NOTIFICATION_ENDPOINTS.MARK_READ, { notificationId: id });
      await api.post(url);
    } catch (error) {
      logger.error(`Failed to mark notification ${id} as read:`, error);
      throw new Error(ERROR_MESSAGES.MARK_READ_FAILED.en);
    }
  },

  markAllRead: async (): Promise<void> => {
    try {
      await api.post(NOTIFICATION_ENDPOINTS.MARK_ALL_READ);
    } catch (error) {
      logger.error('Failed to mark all notifications as read:', error);
      throw new Error(ERROR_MESSAGES.MARK_READ_FAILED.en);
    }
  },

  getPreferences: async (): Promise<NotificationPreferences> => {
    return safeFetch(NOTIFICATION_ENDPOINTS.PREFERENCES, async () => {
      const response = await api.get(NOTIFICATION_ENDPOINTS.PREFERENCES);
      return response.data.data || response.data;
    });
  },

  updatePreferences: async (
    prefs: Partial<NotificationPreferences>
  ): Promise<NotificationPreferences> => {
    try {
      const response = await api.put(NOTIFICATION_ENDPOINTS.PREFERENCES, prefs);
      return response.data.data || response.data;
    } catch (error) {
      logger.error('Failed to update notification preferences:', error);
      throw new Error(ERROR_MESSAGES.PREFERENCES_FAILED.en);
    }
  },

  subscribe: async (topic: string): Promise<void> => {
    try {
      await api.post(NOTIFICATION_ENDPOINTS.SUBSCRIBE, { topic });
    } catch (error) {
      logger.error(`Failed to subscribe to ${topic}:`, error);
      throw error;
    }
  },

  unsubscribe: async (topic: string): Promise<void> => {
    try {
      await api.post(NOTIFICATION_ENDPOINTS.UNSUBSCRIBE, { topic });
    } catch (error) {
      logger.error(`Failed to unsubscribe from ${topic}:`, error);
      throw error;
    }
  },
};
