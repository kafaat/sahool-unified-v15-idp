/**
 * Sahool Admin Dashboard - Real-Time Alerts Hook
 * خطاف التنبيهات في الوقت الفعلي
 *
 * Manages real-time alert notifications via WebSocket
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useWebSocketEvent } from './useWebSocket';
import type { AlertMessage } from './useWebSocket';

export interface Alert extends AlertMessage {
  read: boolean;
  notified: boolean;
}

interface UseRealTimeAlertsOptions {
  /** Maximum number of alerts to keep in memory */
  maxAlerts?: number;
  /** Filter alerts by severity */
  minSeverity?: 'low' | 'medium' | 'high' | 'critical';
  /** Filter alerts by type */
  alertTypes?: string[];
  /** Enable browser notifications */
  enableNotifications?: boolean;
  /** Custom notification handler */
  onNewAlert?: (alert: Alert) => void;
}

interface UseRealTimeAlertsReturn {
  /** All alerts */
  alerts: Alert[];
  /** Unread alerts */
  unreadAlerts: Alert[];
  /** Count of unread alerts */
  unreadCount: number;
  /** Critical alerts */
  criticalAlerts: Alert[];
  /** Mark alert as read */
  markAsRead: (alertId: string) => void;
  /** Mark all alerts as read */
  markAllAsRead: () => void;
  /** Clear all alerts */
  clearAlerts: () => void;
  /** Remove a specific alert */
  removeAlert: (alertId: string) => void;
}

/**
 * Hook for managing real-time alerts
 *
 * @example
 * ```tsx
 * function AlertsPanel() {
 *   const {
 *     alerts,
 *     unreadCount,
 *     criticalAlerts,
 *     markAsRead,
 *     markAllAsRead
 *   } = useRealTimeAlerts({
 *     maxAlerts: 100,
 *     minSeverity: 'medium',
 *     enableNotifications: true,
 *   });
 *
 *   return (
 *     <div>
 *       <h2>Alerts ({unreadCount} unread)</h2>
 *       {alerts.map(alert => (
 *         <AlertItem
 *           key={alert.id}
 *           alert={alert}
 *           onRead={() => markAsRead(alert.id)}
 *         />
 *       ))}
 *     </div>
 *   );
 * }
 * ```
 */
export function useRealTimeAlerts(
  options: UseRealTimeAlertsOptions = {}
): UseRealTimeAlertsReturn {
  const {
    maxAlerts = 100,
    minSeverity,
    alertTypes,
    enableNotifications = false,
    onNewAlert,
  } = options;

  const [alerts, setAlerts] = useState<Alert[]>([]);

  // Severity levels for filtering
  const severityLevels = {
    low: 0,
    medium: 1,
    high: 2,
    critical: 3,
  };

  // Filter alert based on options
  const shouldIncludeAlert = useCallback(
    (alert: AlertMessage): boolean => {
      // Check severity filter
      if (minSeverity) {
        const alertLevel = severityLevels[alert.severity];
        const minLevel = severityLevels[minSeverity];
        if (alertLevel < minLevel) {
          return false;
        }
      }

      // Check type filter
      if (alertTypes && alertTypes.length > 0) {
        if (!alertTypes.includes(alert.type)) {
          return false;
        }
      }

      return true;
    },
    [minSeverity, alertTypes, severityLevels]
  );

  // Handle new alert from WebSocket
  const handleNewAlert = useCallback(
    (alertData: AlertMessage) => {
      if (!shouldIncludeAlert(alertData)) {
        return;
      }

      const alert: Alert = {
        ...alertData,
        read: false,
        notified: false,
      };

      setAlerts((prev) => {
        // Check if alert already exists
        if (prev.some((a) => a.id === alert.id)) {
          return prev;
        }

        // Add new alert and limit array size
        const updated = [alert, ...prev].slice(0, maxAlerts);
        return updated;
      });

      // Show browser notification
      if (enableNotifications && !alert.notified) {
        showBrowserNotification(alert);
        alert.notified = true;
      }

      // Call custom handler
      if (onNewAlert) {
        onNewAlert(alert);
      }
    },
    [shouldIncludeAlert, maxAlerts, enableNotifications, onNewAlert]
  );

  // Subscribe to alert events
  useWebSocketEvent<AlertMessage>('alert', handleNewAlert);

  // Mark alert as read
  const markAsRead = useCallback((alertId: string) => {
    setAlerts((prev) =>
      prev.map((alert) =>
        alert.id === alertId ? { ...alert, read: true } : alert
      )
    );
  }, []);

  // Mark all alerts as read
  const markAllAsRead = useCallback(() => {
    setAlerts((prev) => prev.map((alert) => ({ ...alert, read: true })));
  }, []);

  // Clear all alerts
  const clearAlerts = useCallback(() => {
    setAlerts([]);
  }, []);

  // Remove a specific alert
  const removeAlert = useCallback((alertId: string) => {
    setAlerts((prev) => prev.filter((alert) => alert.id !== alertId));
  }, []);

  // Request notification permission on mount
  useEffect(() => {
    if (enableNotifications && typeof window !== 'undefined' && 'Notification' in window) {
      if (Notification.permission === 'default') {
        Notification.requestPermission();
      }
    }
  }, [enableNotifications]);

  // Computed values
  const unreadAlerts = alerts.filter((alert) => !alert.read);
  const unreadCount = unreadAlerts.length;
  const criticalAlerts = alerts.filter(
    (alert) => alert.severity === 'critical'
  );

  return {
    alerts,
    unreadAlerts,
    unreadCount,
    criticalAlerts,
    markAsRead,
    markAllAsRead,
    clearAlerts,
    removeAlert,
  };
}

/**
 * Hook for monitoring critical alerts with sound/visual alerts
 *
 * @example
 * ```tsx
 * function CriticalAlertsMonitor() {
 *   const { criticalCount, latestCritical } = useCriticalAlerts({
 *     playSound: true,
 *   });
 *
 *   return (
 *     <div className={criticalCount > 0 ? 'animate-pulse' : ''}>
 *       {criticalCount} critical alerts
 *     </div>
 *   );
 * }
 * ```
 */
export function useCriticalAlerts(options: {
  playSound?: boolean;
  onCriticalAlert?: (alert: Alert) => void;
} = {}) {
  const { playSound = false, onCriticalAlert } = options;

  const { criticalAlerts } = useRealTimeAlerts({
    minSeverity: 'critical',
    enableNotifications: true,
  });

  const [latestCritical, setLatestCritical] = useState<Alert | null>(null);

  // Track latest critical alert
  useEffect(() => {
    if (criticalAlerts.length > 0) {
      const latest = criticalAlerts[0];

      if (!latestCritical || latest.id !== latestCritical.id) {
        setLatestCritical(latest);

        // Play sound alert
        if (playSound) {
          playAlertSound();
        }

        // Call custom handler
        if (onCriticalAlert) {
          onCriticalAlert(latest);
        }
      }
    }
  }, [criticalAlerts, latestCritical, playSound, onCriticalAlert]);

  return {
    criticalAlerts,
    criticalCount: criticalAlerts.length,
    latestCritical,
    hasCritical: criticalAlerts.length > 0,
  };
}

/**
 * Hook for alert statistics
 */
export function useAlertStats() {
  const { alerts } = useRealTimeAlerts();

  const stats = {
    total: alerts.length,
    unread: alerts.filter((a) => !a.read).length,
    bySeverity: {
      critical: alerts.filter((a) => a.severity === 'critical').length,
      high: alerts.filter((a) => a.severity === 'high').length,
      medium: alerts.filter((a) => a.severity === 'medium').length,
      low: alerts.filter((a) => a.severity === 'low').length,
    },
    byType: alerts.reduce((acc, alert) => {
      acc[alert.type] = (acc[alert.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
  };

  return stats;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper Functions
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Show browser notification
 */
function showBrowserNotification(alert: Alert): void {
  if (typeof window === 'undefined' || !('Notification' in window)) {
    return;
  }

  if (Notification.permission === 'granted') {
    const notification = new Notification(alert.title, {
      body: alert.message,
      icon: '/icons/alert.png',
      badge: '/icons/badge.png',
      tag: alert.id,
      requireInteraction: alert.severity === 'critical',
      silent: alert.severity === 'low',
    });

    notification.onclick = () => {
      window.focus();
      notification.close();
    };
  }
}

/**
 * Play alert sound
 */
function playAlertSound(): void {
  if (typeof window === 'undefined' || !('Audio' in window)) {
    return;
  }

  try {
    const audio = new Audio('/sounds/alert.mp3');
    audio.volume = 0.5;
    audio.play().catch((error) => {
      console.warn('Failed to play alert sound:', error);
    });
  } catch (error) {
    console.warn('Audio not supported:', error);
  }
}
