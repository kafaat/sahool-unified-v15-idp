/**
 * SAHOOL Event Stream Hook
 * خطاف بث الأحداث في الوقت الحقيقي
 *
 * Connects to SAHOOL event streams for real-time updates
 */

'use client';

import { useEffect, useCallback, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export type EventCategory =
  | 'field'
  | 'ndvi'
  | 'alert'
  | 'weather'
  | 'irrigation'
  | 'crop_health'
  | 'yield'
  | 'system';

export interface SahoolEvent<T = unknown> {
  id: string;
  type: string;
  category: EventCategory;
  timestamp: string;
  tenantId: string;
  payload: T;
  metadata?: {
    correlationId?: string;
    source?: string;
    version?: string;
  };
}

export interface EventStreamOptions {
  /**
   * Event categories to subscribe to
   */
  categories?: EventCategory[];

  /**
   * Filter by field ID
   */
  fieldId?: string;

  /**
   * Filter by governorate
   */
  governorate?: string;

  /**
   * Auto-reconnect on disconnect
   */
  autoReconnect?: boolean;

  /**
   * Initial reconnect delay in ms (will increase exponentially)
   */
  reconnectDelay?: number;

  /**
   * Maximum reconnect delay in ms (cap for exponential backoff)
   */
  maxReconnectDelay?: number;

  /**
   * Maximum reconnect attempts
   */
  maxReconnectAttempts?: number;
}

export interface EventStreamState {
  isConnected: boolean;
  isConnecting: boolean;
  error: Error | null;
  reconnectAttempts: number;
  lastEventTime: Date | null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// EVENT STREAM HOOK
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Hook for real-time event streaming
 *
 * @example
 * // Subscribe to all events
 * const { isConnected, events } = useEventStream({
 *   onEvent: (event) => console.log('New event:', event),
 * });
 *
 * @example
 * // Subscribe to specific categories
 * const { isConnected } = useEventStream({
 *   categories: ['ndvi', 'alert'],
 *   fieldId: 'field-123',
 *   onEvent: handleEvent,
 * });
 */
export function useEventStream(
  options: EventStreamOptions & {
    onEvent?: (event: SahoolEvent) => void;
    onConnect?: () => void;
    onDisconnect?: () => void;
    onError?: (error: Error) => void;
  } = {}
) {
  const {
    categories,
    fieldId,
    governorate,
    autoReconnect = true,
    reconnectDelay = 5000,
    maxReconnectDelay = 30000,
    maxReconnectAttempts = 10,
    onEvent,
    onConnect,
    onDisconnect,
    onError,
  } = options;

  const [state, setState] = useState<EventStreamState>({
    isConnected: false,
    isConnecting: false,
    error: null,
    reconnectAttempts: 0,
    lastEventTime: null,
  });

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const queryClient = useQueryClient();

  // Build stream URL with filters
  const buildStreamUrl = useCallback(() => {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';
    const params = new URLSearchParams();

    if (categories?.length) {
      params.set('categories', categories.join(','));
    }
    if (fieldId) {
      params.set('field_id', fieldId);
    }
    if (governorate) {
      params.set('governorate', governorate);
    }

    return `${baseUrl}/v1/events/stream?${params.toString()}`;
  }, [categories, fieldId, governorate]);

  // Handle incoming events
  const handleEvent = useCallback(
    (event: SahoolEvent) => {
      setState((prev) => ({ ...prev, lastEventTime: new Date() }));

      // Call user callback
      onEvent?.(event);

      // Invalidate relevant queries based on event category
      switch (event.category) {
        case 'field':
          queryClient.invalidateQueries({ queryKey: ['fields'] });
          break;
        case 'ndvi':
          queryClient.invalidateQueries({ queryKey: ['ndvi'] });
          break;
        case 'alert':
          queryClient.invalidateQueries({ queryKey: ['alerts'] });
          break;
        case 'weather':
          queryClient.invalidateQueries({ queryKey: ['weather'] });
          break;
        case 'irrigation':
          queryClient.invalidateQueries({ queryKey: ['irrigation'] });
          break;
        case 'crop_health':
          queryClient.invalidateQueries({ queryKey: ['crop-health'] });
          break;
        case 'yield':
          queryClient.invalidateQueries({ queryKey: ['yield'] });
          break;
      }
    },
    [onEvent, queryClient]
  );

  // Connect to event stream
  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setState((prev) => ({ ...prev, isConnecting: true, error: null }));

    const url = buildStreamUrl();
    const eventSource = new EventSource(url, { withCredentials: true });

    eventSource.onopen = () => {
      setState((prev) => ({
        ...prev,
        isConnected: true,
        isConnecting: false,
        reconnectAttempts: 0,
        error: null,
      }));
      onConnect?.();
    };

    eventSource.onmessage = (messageEvent) => {
      try {
        const event: SahoolEvent = JSON.parse(messageEvent.data);
        handleEvent(event);
      } catch (e) {
        console.error('Failed to parse event:', e);
      }
    };

    eventSource.onerror = () => {
      const error = new Error('Event stream connection lost');
      setState((prev) => ({
        ...prev,
        isConnected: false,
        isConnecting: false,
        error,
      }));
      onError?.(error);
      onDisconnect?.();

      eventSource.close();

      // Auto-reconnect logic with exponential backoff
      if (autoReconnect) {
        setState((prev) => {
          if (prev.reconnectAttempts < maxReconnectAttempts) {
            // Calculate exponential backoff delay using bit shifting for performance
            // Cap the exponent to prevent overflow (2^10 = 1024x initial delay is sufficient)
            const cappedAttempts = Math.min(prev.reconnectAttempts, 10);
            const exponentialDelay = Math.min(
              reconnectDelay * (1 << cappedAttempts),
              maxReconnectDelay
            );
            
            reconnectTimeoutRef.current = setTimeout(() => {
              connect();
            }, exponentialDelay);
            return { ...prev, reconnectAttempts: prev.reconnectAttempts + 1 };
          }
          return prev;
        });
      }
    };

    eventSourceRef.current = eventSource;
  }, [
    buildStreamUrl,
    handleEvent,
    autoReconnect,
    reconnectDelay,
    maxReconnectDelay,
    maxReconnectAttempts,
    onConnect,
    onDisconnect,
    onError,
  ]);

  // Disconnect from event stream
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setState((prev) => ({
      ...prev,
      isConnected: false,
      isConnecting: false,
      reconnectAttempts: 0,
    }));
  }, []);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return {
    ...state,
    connect,
    disconnect,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SPECIALIZED EVENT HOOKS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Hook for NDVI real-time updates
 */
export function useNDVIStream(
  fieldId?: string,
  onUpdate?: (event: SahoolEvent) => void
) {
  return useEventStream({
    categories: ['ndvi'],
    fieldId,
    onEvent: onUpdate,
  });
}

/**
 * Hook for Alert real-time updates
 */
export function useAlertStream(onAlert?: (event: SahoolEvent) => void) {
  return useEventStream({
    categories: ['alert'],
    onEvent: onAlert,
  });
}

/**
 * Hook for Weather real-time updates
 */
export function useWeatherStream(
  governorate?: string,
  onUpdate?: (event: SahoolEvent) => void
) {
  return useEventStream({
    categories: ['weather'],
    governorate,
    onEvent: onUpdate,
  });
}

/**
 * Hook for Field real-time updates
 */
export function useFieldStream(
  fieldId?: string,
  onUpdate?: (event: SahoolEvent) => void
) {
  return useEventStream({
    categories: ['field', 'ndvi', 'crop_health', 'irrigation'],
    fieldId,
    onEvent: onUpdate,
  });
}
