/**
 * Notifications Feature - Types
 * أنواع ميزة الإشعارات
 *
 * Backend notification types are defined in:
 *   apps/services/notification-service/src/notification_types.py
 */

// ---------------------------------------------------------------------------
// Backend notification types (14 domain-specific types from notification-service)
// ---------------------------------------------------------------------------

export type BackendNotificationType =
  | 'weather_alert'
  | 'low_stock'
  | 'disease_detected'
  | 'spray_window'
  | 'harvest_reminder'
  | 'payment_due'
  | 'field_update'
  | 'satellite_ready'
  | 'pest_outbreak'
  | 'irrigation_reminder'
  | 'market_price'
  | 'crop_health'
  | 'task_reminder'
  | 'system';

// ---------------------------------------------------------------------------
// Legacy generic types (kept for backward compatibility)
// ---------------------------------------------------------------------------

/** @deprecated Use BackendNotificationType for new code. */
export type LegacyNotificationType = 'alert' | 'info' | 'warning' | 'success' | 'system';

/**
 * Union of domain-specific backend types and legacy generic types.
 * Existing code that passes legacy values will continue to work.
 */
export type NotificationType = BackendNotificationType | LegacyNotificationType;

export type NotificationPriority = 'low' | 'medium' | 'high' | 'urgent';
export type NotificationChannel = 'push' | 'email' | 'sms' | 'in_app';

// ---------------------------------------------------------------------------
// Notification type display configuration
// ---------------------------------------------------------------------------

export interface NotificationTypeConfig {
  /** Icon identifier (emoji or icon-library name) */
  icon: string;
  /** Tailwind / CSS color token */
  color: string;
  /** English label */
  label: string;
  /** Arabic label - التسمية بالعربية */
  labelAr: string;
  /** Default priority when not specified by payload */
  defaultPriority: NotificationPriority;
}

const NOTIFICATION_TYPE_CONFIGS: Record<BackendNotificationType, NotificationTypeConfig> = {
  weather_alert: {
    icon: '⚠️',
    color: 'orange',
    label: 'Weather Alert',
    labelAr: 'تنبيه طقس',
    defaultPriority: 'high',
  },
  low_stock: {
    icon: '📦',
    color: 'amber',
    label: 'Low Stock',
    labelAr: 'نقص مخزون',
    defaultPriority: 'medium',
  },
  disease_detected: {
    icon: '🦠',
    color: 'red',
    label: 'Disease Detected',
    labelAr: 'مرض مكتشف',
    defaultPriority: 'high',
  },
  spray_window: {
    icon: '💨',
    color: 'sky',
    label: 'Spray Window',
    labelAr: 'وقت الرش',
    defaultPriority: 'medium',
  },
  harvest_reminder: {
    icon: '🌾',
    color: 'yellow',
    label: 'Harvest Reminder',
    labelAr: 'تذكير حصاد',
    defaultPriority: 'medium',
  },
  payment_due: {
    icon: '💰',
    color: 'rose',
    label: 'Payment Due',
    labelAr: 'دفعة مستحقة',
    defaultPriority: 'medium',
  },
  field_update: {
    icon: '🌱',
    color: 'green',
    label: 'Field Update',
    labelAr: 'تحديث حقل',
    defaultPriority: 'low',
  },
  satellite_ready: {
    icon: '🛰️',
    color: 'indigo',
    label: 'Satellite Ready',
    labelAr: 'صور أقمار جاهزة',
    defaultPriority: 'medium',
  },
  pest_outbreak: {
    icon: '🐛',
    color: 'red',
    label: 'Pest Outbreak',
    labelAr: 'انتشار آفات',
    defaultPriority: 'high',
  },
  irrigation_reminder: {
    icon: '💧',
    color: 'blue',
    label: 'Irrigation Reminder',
    labelAr: 'تذكير ري',
    defaultPriority: 'medium',
  },
  market_price: {
    icon: '📈',
    color: 'emerald',
    label: 'Market Price',
    labelAr: 'أسعار السوق',
    defaultPriority: 'low',
  },
  crop_health: {
    icon: '🌿',
    color: 'lime',
    label: 'Crop Health',
    labelAr: 'صحة المحصول',
    defaultPriority: 'high',
  },
  task_reminder: {
    icon: '✅',
    color: 'violet',
    label: 'Task Reminder',
    labelAr: 'تذكير مهمة',
    defaultPriority: 'medium',
  },
  system: {
    icon: 'ℹ️',
    color: 'slate',
    label: 'System',
    labelAr: 'نظام',
    defaultPriority: 'low',
  },
};

/**
 * Maps legacy generic types to the closest backend type for display purposes.
 */
const LEGACY_TYPE_FALLBACK: Record<LegacyNotificationType, BackendNotificationType> = {
  alert: 'weather_alert',
  warning: 'pest_outbreak',
  info: 'field_update',
  success: 'harvest_reminder',
  system: 'system',
};

/**
 * Returns the display configuration for a notification type.
 * Accepts both domain-specific backend types and legacy generic types.
 *
 * @param type - The notification type value from the payload
 * @returns NotificationTypeConfig with icon, color, label, and labelAr
 *
 * @example
 * ```ts
 * const cfg = getNotificationConfig('disease_detected');
 * // cfg.icon  -> '🦠'
 * // cfg.color -> 'red'
 * // cfg.label -> 'Disease Detected'
 * // cfg.labelAr -> 'مرض مكتشف'
 * ```
 */
export function getNotificationConfig(type: NotificationType): NotificationTypeConfig {
  // Direct match against backend types
  if (Object.hasOwn(NOTIFICATION_TYPE_CONFIGS, type)) {
    return NOTIFICATION_TYPE_CONFIGS[type as BackendNotificationType];
  }

  // Fallback for legacy generic types
  if (Object.hasOwn(LEGACY_TYPE_FALLBACK, type)) {
    return NOTIFICATION_TYPE_CONFIGS[LEGACY_TYPE_FALLBACK[type as LegacyNotificationType]];
  }

  // Ultimate fallback to system config for any unknown value
  return NOTIFICATION_TYPE_CONFIGS.system;
}

// ---------------------------------------------------------------------------
// Core interfaces
// ---------------------------------------------------------------------------

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
