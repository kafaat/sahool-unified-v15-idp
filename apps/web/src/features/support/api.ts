/**
 * Support Feature - API Layer
 * طبقة API لميزة الدعم الفني
 *
 * Uses NOTIFICATION_ENDPOINTS as the support ticket system
 * is backed by the notification-service (port 8110).
 */

import { createApiClient } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import { NOTIFICATION_ENDPOINTS, buildUrl } from '@sahool/shared-types/contracts';

const api = createApiClient();

export interface Ticket {
  id: string;
  subject: string;
  subjectAr: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high';
  createdAt: string;
  updatedAt: string;
  message?: string;
}

export interface CreateTicketRequest {
  subject: string;
  message: string;
  priority?: 'low' | 'medium' | 'high';
}

/**
 * Support ticket endpoints (routed through notification-service).
 * These are not in shared contracts yet, so we define them locally.
 */
const SUPPORT_ENDPOINTS = {
  TICKETS: '/api/v1/notifications?type=support_ticket',
  CREATE_TICKET: '/api/v1/notifications/subscribe',
} as const;

export const supportApi = {
  /**
   * Fetch user's support tickets
   * جلب تذاكر الدعم الفني
   */
  getTickets: async (): Promise<Ticket[]> => {
    return safeFetch(SUPPORT_ENDPOINTS.TICKETS, async () => {
      const response = await api.get(SUPPORT_ENDPOINTS.TICKETS);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Create a new support ticket
   * إنشاء تذكرة دعم جديدة
   */
  createTicket: async (data: CreateTicketRequest): Promise<Ticket> => {
    return safeFetch(SUPPORT_ENDPOINTS.CREATE_TICKET, async () => {
      const response = await api.post(SUPPORT_ENDPOINTS.CREATE_TICKET, {
        ...data,
        type: 'support_ticket',
      });
      return response.data.data || response.data;
    });
  },

  /**
   * Fetch all notifications (general)
   * جلب جميع الإشعارات
   */
  getNotifications: async (): Promise<unknown[]> => {
    return safeFetch(NOTIFICATION_ENDPOINTS.LIST, async () => {
      const response = await api.get(NOTIFICATION_ENDPOINTS.LIST);
      const data = response.data.data || response.data;
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  /**
   * Mark a notification as read
   * تعليم إشعار كمقروء
   */
  markRead: async (notificationId: string): Promise<void> => {
    return safeFetch(NOTIFICATION_ENDPOINTS.MARK_READ, async () => {
      const url = buildUrl(NOTIFICATION_ENDPOINTS.MARK_READ, { notificationId });
      await api.patch(url);
    });
  },
};
