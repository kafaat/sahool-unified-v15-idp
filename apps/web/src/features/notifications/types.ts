/**
 * Notifications Feature - Types
 * أنواع ميزة الإشعارات
 */

export type NotificationType = 'alert' | 'info' | 'warning' | 'success' | 'system';
export type NotificationPriority = 'low' | 'medium' | 'high' | 'urgent';
export type NotificationChannel = 'push' | 'email' | 'sms' | 'in_app';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  titleAr: string;
  message: string;
  messageAr: string;
  read: boolean;
  priority: NotificationPriority;
  channel: NotificationChannel;
  metadata?: Record<string, unknown>;
  actionUrl?: string;
  createdAt: string;
  readAt?: string;
}

export interface NotificationPreferences {
  push: boolean;
  email: boolean;
  sms: boolean;
  inApp: boolean;
  channels: Record<string, boolean>;
}

export interface NotificationFilters {
  type?: NotificationType;
  read?: boolean;
  priority?: NotificationPriority;
  startDate?: string;
  endDate?: string;
}
