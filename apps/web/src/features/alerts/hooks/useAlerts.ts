/**
 * Alerts Feature - React Hooks
 * خطافات React لميزة التنبيهات
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useCallback, useState } from 'react';
import { alertsApi, type Alert, type AlertFilters, type AlertSeverity } from '../api';

// Query Keys
export const alertKeys = {
  all: ['alerts'] as const,
  lists: () => [...alertKeys.all, 'list'] as const,
  list: (filters?: AlertFilters) => [...alertKeys.lists(), filters] as const,
  detail: (id: string) => [...alertKeys.all, 'detail', id] as const,
  count: () => [...alertKeys.all, 'count'] as const,
  stats: (governorate?: string) => [...alertKeys.all, 'stats', governorate] as const,
};

/**
 * Hook to fetch alerts
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
 * Hook to fetch single alert
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
 */
export function useAlertStats(governorate?: string) {
  return useQuery({
    queryKey: alertKeys.stats(governorate),
    queryFn: () => alertsApi.getStats(governorate),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook to acknowledge an alert
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
 */
export function useResolveAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, resolution }: { id: string; resolution?: string }) =>
      alertsApi.resolveAlert(id, resolution),
    onSuccess: (updatedAlert: Alert) => {
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
      queryClient.invalidateQueries({ queryKey: alertKeys.count() });
      queryClient.setQueryData(alertKeys.detail(updatedAlert.id), updatedAlert);
    },
  });
}

/**
 * Hook to dismiss an alert
 */
export function useDismissAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => alertsApi.dismissAlert(id),
    onSuccess: (_: void, id: string) => {
      queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
      queryClient.invalidateQueries({ queryKey: alertKeys.count() });
      queryClient.removeQueries({ queryKey: alertKeys.detail(id) });
    },
  });
}

/**
 * Hook for real-time alert streaming
 */
export function useAlertStream(onAlert: (alert: Alert) => void) {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const queryClient = useQueryClient();

  const connect = useCallback(() => {
    const streamUrl = alertsApi.getStreamUrl();
    const eventSource = new EventSource(streamUrl, { withCredentials: true });

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    eventSource.onmessage = (event) => {
      try {
        const alert: Alert = JSON.parse(event.data);
        onAlert(alert);
        // Update cache
        queryClient.invalidateQueries({ queryKey: alertKeys.lists() });
        queryClient.invalidateQueries({ queryKey: alertKeys.count() });
      } catch (e) {
        console.error('Failed to parse alert:', e);
      }
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      setError(new Error('Connection lost'));
      eventSource.close();
      // Reconnect after 5 seconds
      setTimeout(connect, 5000);
    };

    return eventSource;
  }, [onAlert, queryClient]);

  useEffect(() => {
    const eventSource = connect();
    return () => eventSource.close();
  }, [connect]);

  return { isConnected, error };
}
