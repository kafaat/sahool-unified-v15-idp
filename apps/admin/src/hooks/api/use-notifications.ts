/**
 * SAHOOL Admin - Notification hooks
 * خطافات الإشعارات
 */

'use client';

import { useApiQuery, useApiMutation, invalidateQueries } from './use-api-query';
import { fetchNotifications, markNotificationRead } from '@/lib/api';

/**
 * List notifications
 */
export function useNotifications(params?: { type?: string; priority?: string; limit?: number }) {
  return useApiQuery(
    ['notifications', JSON.stringify(params ?? {})],
    () => fetchNotifications(params),
    { refetchInterval: 30000, staleTime: 15000 }
  );
}

/**
 * Mark a notification as read
 */
export function useMarkNotificationRead() {
  return useApiMutation((id: string) => markNotificationRead(id).then(() => ({ success: true })), {
    invalidateKeys: ['notifications'],
    onSuccess: () => invalidateQueries('dashboard'),
  });
}
