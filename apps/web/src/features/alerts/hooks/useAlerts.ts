/**
 * Alerts Feature - React Hooks
 * خطافات React لميزة التنبيهات
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useCallback, useState, useRef } from 'react';
import { alertsApi } from '../api';
import { logger } from '@/lib/logger';
import type {
  Alert,
  AlertFilters,
  CreateAlertPayload,
  UpdateAlertPayload,
} from '../types';

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys
// ═══════════════════════════════════════════════════════════════════════════

export const alertKeys = {
  all: ['alerts'] as const,
  lists: () => [...alertKeys.all, 'list'] as const,
  list: (filters?: AlertFilters) => [...alertKeys.lists(), filters] as const,
  detail: (id: string) => [...alertKeys.all, 'detail', id] as const,
  count: () => [...alertKeys.all, 'count'] as const,
  stats: (governorate?: string) => [...alertKeys.all, 'stats', governorate] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Query Hooks (Read Operations)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch alerts with optional filters
 * خطاف لجلب التنبيهات مع فلاتر اختيارية
 */
export function useAlerts(filters?: AlertFilters) {
  return useQuery({
    queryKey: alertKeys.list(filters),
    queryFn: () => alertsApi.getAlerts(filters),
    staleTime: 1000 * 30, // 30 seconds (alerts change frequently)
    refetchInterval: 1000 * 60, // Refetch every minute
  });
}

/**
 * Hook to get active alerts count
 * خطاف لجلب عدد التنبيهات النشطة
 */
export function useActiveAlertsCount() {
  return useQuery({
    queryKey: alertKeys.count(),
    queryFn: () => alertsApi.getActiveCount(),
    staleTime: 1000 * 30,
    refetchInterval: 1000 * 30, // Refetch every 30 seconds
  });
}

/**
 * Hook to fetch single alert by ID
 * خطاف لجلب تنبيه واحد بواسطة المعرف
 */
export function useAlert(id: string) {
  return useQuery({
    queryKey: alertKeys.detail(id),
    queryFn: () => alertsApi.getAlertById(id),
    enabled: !!id,
  });
}

/**
 * Hook to fetch alert statistics
 * خطاف لجلب إحصائيات التنبيهات
 */
export function useAlertStats(governorate?: string) {
  return useQuery({
    queryKey: alertKeys.stats(governorate),
    queryFn: () => alertsApi.getStats(governorate),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Hooks (Write Operations)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to create a new alert
 * خطاف لإنشاء تنبيه جديد
 */
export function useCreateAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateAlertPayload) => alertsApi.createAlert(payload),
    onSuccess: (newAlert: Alert) => {
      // Invalidate lists to refetch with new alert
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
      queryClient.invalidateQueries({ queryKey: alertKeys.count() });
      queryClient.invalidateQueries({ queryKey: alertKeys.stats() });

      // Optimistically add to cache
      queryClient.setQueryData(alertKeys.detail(newAlert.id), newAlert);
    },
  });
}

/**
 * Hook to update an alert
 * خطاف لتحديث تنبيه
 */
export function useUpdateAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateAlertPayload }) =>
      alertsApi.updateAlert(id, payload),
    onSuccess: (updatedAlert: Alert) => {
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
      queryClient.setQueryData(alertKeys.detail(updatedAlert.id), updatedAlert);
    },
  });
}

/**
 * Hook to acknowledge an alert
 * خطاف للإقرار بتنبيه
 */
export function useAcknowledgeAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => alertsApi.acknowledgeAlert(id),
    onSuccess: (updatedAlert: Alert) => {
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
      queryClient.invalidateQueries({ queryKey: alertKeys.count() });
      queryClient.setQueryData(alertKeys.detail(updatedAlert.id), updatedAlert);
    },
  });
}

/**
 * Hook to resolve an alert
 * خطاف لحل تنبيه
 */
export function useResolveAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, resolution }: { id: string; resolution?: string }) =>
      alertsApi.resolveAlert(id, resolution),
    onSuccess: (updatedAlert: Alert) => {
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
      queryClient.invalidateQueries({ queryKey: alertKeys.count() });
      queryClient.invalidateQueries({ queryKey: alertKeys.stats() });
      queryClient.setQueryData(alertKeys.detail(updatedAlert.id), updatedAlert);
    },
  });
}

/**
 * Hook to dismiss an alert
 * خطاف لتجاهل تنبيه
 */
export function useDismissAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      alertsApi.dismissAlert(id, reason),
    onSuccess: (_: void, variables: { id: string; reason?: string }) => {
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
      queryClient.invalidateQueries({ queryKey: alertKeys.count() });
      queryClient.invalidateQueries({ queryKey: alertKeys.stats() });
      queryClient.removeQueries({ queryKey: alertKeys.detail(variables.id) });
    },
  });
}

/**
 * Hook to delete an alert
 * خطاف لحذف تنبيه
 */
export function useDeleteAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => alertsApi.deleteAlert(id),
    onSuccess: (_: void, id: string) => {
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
      queryClient.invalidateQueries({ queryKey: alertKeys.count() });
      queryClient.invalidateQueries({ queryKey: alertKeys.stats() });
      queryClient.removeQueries({ queryKey: alertKeys.detail(id) });
    },
  });
}

/**
 * Hook to bulk acknowledge alerts
 * خطاف للإقرار بالتنبيهات بشكل جماعي
 */
export function useBulkAcknowledgeAlerts() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertIds: string[]) => alertsApi.bulkAcknowledge(alertIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
      queryClient.invalidateQueries({ queryKey: alertKeys.count() });
      queryClient.invalidateQueries({ queryKey: alertKeys.stats() });
    },
  });
}

/**
 * Hook to bulk dismiss alerts
 * خطاف لتجاهل التنبيهات بشكل جماعي
 */
export function useBulkDismissAlerts() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ alertIds, reason }: { alertIds: string[]; reason?: string }) =>
      alertsApi.bulkDismiss(alertIds, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
      queryClient.invalidateQueries({ queryKey: alertKeys.count() });
      queryClient.invalidateQueries({ queryKey: alertKeys.stats() });
    },
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Real-time Alert Stream Hook
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook for real-time alert streaming using Server-Sent Events (SSE)
 * خطاف للبث المباشر للتنبيهات باستخدام أحداث الخادم المرسلة
 */
export function useAlertStream(onAlert: (alert: Alert) => void, enabled = true) {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const queryClient = useQueryClient();
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (!enabled) return;

    // Clean up any existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    // Clear any pending reconnection timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    try {
      const streamUrl = alertsApi.getStreamUrl();
      const eventSource = new EventSource(streamUrl, { withCredentials: true });
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setIsConnected(true);
        setError(null);
        logger.info('Alert stream connected');
      };

      eventSource.onmessage = (event) => {
        try {
          const alert: Alert = JSON.parse(event.data);
          onAlert(alert);

          // Update cache
          queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
          queryClient.invalidateQueries({ queryKey: alertKeys.count() });
          queryClient.setQueryData(alertKeys.detail(alert.id), alert);
        } catch (e) {
          logger.error('Failed to parse alert from stream:', e);
        }
      };

      eventSource.onerror = (e) => {
        setIsConnected(false);
        const errorObj = new Error('Alert stream connection lost');
        setError(errorObj);
        logger.error('Alert stream error:', e);

        eventSource.close();

        // Reconnect after 5 seconds
        if (enabled) {
          reconnectTimeoutRef.current = setTimeout(() => {
            logger.info('Attempting to reconnect alert stream...');
            connect();
          }, 5000);
        }
      };
    } catch (e) {
      logger.error('Failed to create EventSource:', e);
      setError(e as Error);
    }
  }, [onAlert, queryClient, enabled]);

  const disconnect = useCallback(() => {
    // Clean up EventSource
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    // Clear any pending reconnection timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    setIsConnected(false);
    logger.info('Alert stream disconnected');
  }, []);

  useEffect(() => {
    if (enabled) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [connect, disconnect, enabled]);

  return {
    isConnected,
    error,
    disconnect,
    reconnect: connect,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Composite Mutation Hook
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook that provides all alert mutation operations
 * خطاف يوفر جميع عمليات التعديل على التنبيهات
 */
export function useAlertMutations() {
  const createAlert = useCreateAlert();
  const updateAlert = useUpdateAlert();
  const acknowledgeAlert = useAcknowledgeAlert();
  const resolveAlert = useResolveAlert();
  const dismissAlert = useDismissAlert();
  const deleteAlert = useDeleteAlert();
  const bulkAcknowledge = useBulkAcknowledgeAlerts();
  const bulkDismiss = useBulkDismissAlerts();

  return {
    createAlert,
    updateAlert,
    acknowledgeAlert,
    resolveAlert,
    dismissAlert,
    deleteAlert,
    bulkAcknowledge,
    bulkDismiss,
    isLoading:
      createAlert.isPending ||
      updateAlert.isPending ||
      acknowledgeAlert.isPending ||
      resolveAlert.isPending ||
      dismissAlert.isPending ||
      deleteAlert.isPending ||
      bulkAcknowledge.isPending ||
      bulkDismiss.isPending,
  };
}
