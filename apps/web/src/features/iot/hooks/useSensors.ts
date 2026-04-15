/**
 * IoT Sensors - React Hooks
 * خطافات React للمستشعرات
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useCallback, useState, useRef } from 'react';
import { sensorsApi } from '../api';
import type { Sensor, SensorFilters, SensorReadingsQuery, SensorReading } from '../types';
import { logger } from '@/lib/logger';

// Query Keys
export const sensorKeys = {
  all: ['sensors'] as const,
  lists: () => [...sensorKeys.all, 'list'] as const,
  list: (filters?: SensorFilters) => [...sensorKeys.lists(), filters] as const,
  detail: (id: string) => [...sensorKeys.all, 'detail', id] as const,
  readings: (query: SensorReadingsQuery) => [...sensorKeys.all, 'readings', query] as const,
  latest: (sensorId: string) => [...sensorKeys.all, 'latest', sensorId] as const,
  stats: () => [...sensorKeys.all, 'stats'] as const,
};

/**
 * Hook to fetch sensors list
 */
export function useSensors(filters?: SensorFilters) {
  return useQuery({
    queryKey: sensorKeys.list(filters),
    queryFn: () => sensorsApi.getSensors(filters),
    staleTime: 1000 * 30, // 30 seconds (sensors change frequently)
    refetchInterval: 1000 * 60, // Refetch every minute
  });
}

/**
 * Hook to fetch single sensor
 */
export function useSensor(id: string) {
  return useQuery({
    queryKey: sensorKeys.detail(id),
    queryFn: () => sensorsApi.getSensorById(id),
    enabled: !!id,
  });
}

/**
 * Hook to fetch sensor readings
 */
export function useSensorReadings(query: SensorReadingsQuery) {
  return useQuery({
    queryKey: sensorKeys.readings(query),
    queryFn: () => sensorsApi.getSensorReadings(query),
    enabled: !!query.sensorId,
    staleTime: 1000 * 60, // 1 minute
  });
}

/**
 * Hook to fetch latest sensor reading
 */
export function useLatestReading(sensorId: string) {
  return useQuery({
    queryKey: sensorKeys.latest(sensorId),
    queryFn: () => sensorsApi.getLatestReading(sensorId),
    enabled: !!sensorId,
    staleTime: 1000 * 15, // 15 seconds
    refetchInterval: 1000 * 30, // Refetch every 30 seconds
  });
}

/**
 * Hook to fetch sensor statistics
 */
export function useSensorStats() {
  return useQuery({
    queryKey: sensorKeys.stats(),
    queryFn: () => sensorsApi.getStats(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook for real-time sensor readings stream
 *
 * Stabilizes the onReading callback via a ref so that parent re-renders do
 * not tear down and recreate the EventSource on every render (which would
 * cause reconnect storms against the backend SSE endpoint).
 * Uses exponential backoff (capped at 30s) to avoid hammering the server
 * when the connection is persistently failing.
 */
export function useSensorStream(
  sensorId: string | undefined,
  onReading: (reading: SensorReading) => void
) {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const queryClient = useQueryClient();
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const unmountedRef = useRef(false);

  // Stable ref for the caller's onReading callback so it can change between
  // renders without tearing down the stream connection.
  const onReadingRef = useRef(onReading);
  useEffect(() => {
    onReadingRef.current = onReading;
  }, [onReading]);

  const connect = useCallback(() => {
    if (!sensorId || unmountedRef.current) return;

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

    const streamUrl = sensorsApi.getStreamUrl(sensorId);
    const eventSource = new EventSource(streamUrl, { withCredentials: true });
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
      reconnectAttemptsRef.current = 0;
    };

    eventSource.onmessage = (event) => {
      try {
        const reading: SensorReading = JSON.parse(event.data);
        // Validate minimal shape before propagating to caller/cache
        if (
          !reading ||
          typeof reading !== 'object' ||
          typeof reading.value !== 'number'
        ) {
          logger.warn('Received malformed sensor reading, skipping', reading);
          return;
        }
        onReadingRef.current(reading);
        // Update cache
        queryClient.setQueryData(sensorKeys.latest(sensorId), reading);
        queryClient.invalidateQueries({
          queryKey: sensorKeys.detail(sensorId),
        });
      } catch (e) {
        logger.error('Failed to parse sensor reading:', e);
      }
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      setError(new Error('Connection lost'));
      eventSource.close();
      eventSourceRef.current = null;

      if (unmountedRef.current) return;

      // Exponential backoff: 1s, 2s, 4s, 8s, 16s, capped at 30s
      const attempts = Math.min(reconnectAttemptsRef.current, 5);
      const delay = Math.min(1000 * 2 ** attempts, 30000);
      reconnectAttemptsRef.current += 1;
      reconnectTimeoutRef.current = setTimeout(connect, delay);
    };
  }, [sensorId, queryClient]);

  useEffect(() => {
    unmountedRef.current = false;
    reconnectAttemptsRef.current = 0;
    if (sensorId) {
      connect();
    }

    return () => {
      // Mark unmounted so any pending reconnect callback is a no-op.
      unmountedRef.current = true;
      // Clean up EventSource on unmount
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      // Clear any pending reconnection timeout
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    };
  }, [connect, sensorId]);

  return { isConnected, error };
}

/**
 * Hook to create sensor
 * خطاف إنشاء مستشعر
 */
export function useCreateSensor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Omit<Sensor, 'id' | 'createdAt' | 'updatedAt'>) =>
      sensorsApi.createSensor(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: sensorKeys.lists() });
      queryClient.invalidateQueries({ queryKey: sensorKeys.stats() });
    },
  });
}

/**
 * Hook to update sensor
 * خطاف تحديث مستشعر
 */
export function useUpdateSensor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Sensor> }) =>
      sensorsApi.updateSensor(id, data),
    onSuccess: (updatedSensor) => {
      queryClient.invalidateQueries({ queryKey: sensorKeys.lists() });
      queryClient.setQueryData(sensorKeys.detail(updatedSensor.id), updatedSensor);
    },
  });
}

/**
 * Hook to delete sensor
 * خطاف حذف مستشعر
 */
export function useDeleteSensor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => sensorsApi.deleteSensor(id),
    onSuccess: (_: void, id: string) => {
      queryClient.invalidateQueries({ queryKey: sensorKeys.lists() });
      queryClient.invalidateQueries({ queryKey: sensorKeys.stats() });
      queryClient.removeQueries({ queryKey: sensorKeys.detail(id) });
    },
  });
}
