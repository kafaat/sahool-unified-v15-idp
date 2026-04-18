/**
 * Notifications Feature - React Hooks
 * خطافات React لميزة الإشعارات
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationsApi } from '../api';
import type {
  Notification,
  NotificationFilters,
  NotificationPreferences,
} from '../types';

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys
// ═══════════════════════════════════════════════════════════════════════════

export const notificationKeys = {
  all: ['notifications'] as const,
  lists: () => [...notificationKeys.all, 'list'] as const,
  list: (filters?: NotificationFilters) => [...notificationKeys.lists(), filters] as const,
  detail: (id: string) => [...notificationKeys.all, 'detail', id] as const,
  unreadCount: () => [...notificationKeys.all, 'unread-count'] as const,
  preferences: () => [...notificationKeys.all, 'preferences'] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Query Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch notifications with optional filters
 * خطاف لجلب الإشعارات مع فلاتر اختيارية
 */
export function useNotifications(filters?: NotificationFilters) {
  return useQuery({
    queryKey: notificationKeys.list(filters),
    queryFn: () => notificationsApi.getNotifications(filters),
    staleTime: 1000 * 30,
    refetchInterval: 1000 * 60,
  });
}

/**
 * Hook to get single notification by ID
 * خطاف لجلب إشعار واحد بواسطة المعرف
 */
export function useNotification(id: string) {
  return useQuery({
    queryKey: notificationKeys.detail(id),
    queryFn: () => notificationsApi.getById(id),
    enabled: !!id,
  });
}

/**
 * Hook to get unread notifications count
 * خطاف لجلب عدد الإشعارات غير المقروءة
 */
export function useUnreadCount() {
  return useQuery({
    queryKey: notificationKeys.unreadCount(),
    queryFn: async () => {
      const all = await notificationsApi.getNotifications({ read: false });
      return all.length;
    },
    staleTime: 1000 * 15,
    refetchInterval: 1000 * 30,
  });
}

/**
 * Hook to get notification preferences
 * خطاف لجلب تفضيلات الإشعارات
 */
export function useNotificationPreferences() {
  return useQuery({
    queryKey: notificationKeys.preferences(),
    queryFn: () => notificationsApi.getPreferences(),
    staleTime: 1000 * 60 * 5,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to mark a notification as read
 * خطاف لتحديد إشعار كمقروء
 */
export function useMarkRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => notificationsApi.markRead(id),
    // Optimistic update: flip `read` locally before awaiting the server, and
    // roll back on error so the UI stays consistent.
    onMutate: async (id: string) => {
      await queryClient.cancelQueries({ queryKey: notificationKeys.lists() });
      await queryClient.cancelQueries({ queryKey: notificationKeys.unreadCount() });

      const previousLists = queryClient.getQueriesData<Notification[]>({
        queryKey: notificationKeys.lists(),
      });
      const previousUnread = queryClient.getQueryData<number>(
        notificationKeys.unreadCount()
      );

      queryClient.setQueriesData<Notification[]>(
        { queryKey: notificationKeys.lists() },
        (old) =>
          old
            ? old.map((n) =>
                n.id === id ? { ...n, read: true, readAt: new Date().toISOString() } : n
              )
            : old
      );
      if (typeof previousUnread === 'number') {
        queryClient.setQueryData(
          notificationKeys.unreadCount(),
          Math.max(0, previousUnread - 1)
        );
      }

      return { previousLists, previousUnread };
    },
    onError: (_err, _id, context) => {
      if (context?.previousLists) {
        for (const [key, data] of context.previousLists) {
          queryClient.setQueryData(key, data);
        }
      }
      if (typeof context?.previousUnread === 'number') {
        queryClient.setQueryData(notificationKeys.unreadCount(), context.previousUnread);
      }
    },
    onSettled: (_data, _err, id) => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: notificationKeys.unreadCount(),
      });
      queryClient.invalidateQueries({
        queryKey: notificationKeys.detail(id),
      });
    },
  });
}

/**
 * Hook to mark all notifications as read
 * خطاف لتحديد جميع الإشعارات كمقروءة
 */
export function useMarkAllRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => notificationsApi.markAllRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: notificationKeys.unreadCount(),
      });
    },
  });
}

/**
 * Hook to update notification preferences
 * خطاف لتحديث تفضيلات الإشعارات
 */
export function useUpdatePreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (prefs: Partial<NotificationPreferences>) =>
      notificationsApi.updatePreferences(prefs),
    onSuccess: (updatedPrefs: NotificationPreferences) => {
      queryClient.setQueryData(notificationKeys.preferences(), updatedPrefs);
    },
  });
}

/**
 * Hook to subscribe to a notification topic
 * خطاف للاشتراك في موضوع إشعارات
 */
export function useSubscribe() {
  return useMutation({
    mutationFn: (topic: string) => notificationsApi.subscribe(topic),
  });
}

/**
 * Hook to unsubscribe from a notification topic
 * خطاف لإلغاء الاشتراك من موضوع إشعارات
 */
export function useUnsubscribe() {
  return useMutation({
    mutationFn: (topic: string) => notificationsApi.unsubscribe(topic),
  });
}
