/**
 * SAHOOL Event Stream Hook
 * خطاف بث الأحداث في الوقت الحقيقي
 *
 * Connects to SAHOOL event streams for real-time updates
 */

"use client";

import { useEffect, useCallback, useRef, useState, useMemo } from "react";
import { useQueryClient } from "@tanstack/react-query";

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export type EventCategory =
  | "field"
  | "ndvi"
  | "alert"
  | "weather"
  | "irrigation"
  | "crop_health"
  | "yield"
  | "system";

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

  /**
   * Whether to enable the connection (default: true)
   */
  enabled?: boolean;
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
  } = {},
) {
  const {
    categories,
    fieldId,
    governorate,
    autoReconnect = true,
    reconnectDelay = 5000,
    maxReconnectDelay = 30000,
    maxReconnectAttempts = 10,
    enabled = true,
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
  const isMountedRef = useRef(true);
  const reconnectAttemptsRef = useRef(0);

  // Use refs for callbacks to avoid unnecessary reconnections when callbacks change
  // This is critical to prevent infinite reconnection loops
  const callbacksRef = useRef({
    onEvent,
    onConnect,
    onDisconnect,
    onError,
  });

  // Update callback refs without triggering reconnect
  useEffect(() => {
    callbacksRef.current = {
      onEvent,
      onConnect,
      onDisconnect,
      onError,
    };
  }, [onEvent, onConnect, onDisconnect, onError]);

  // Memoize the categories array to prevent unnecessary reconnections
  const categoriesKey = useMemo(
    () => (categories ? categories.sort().join(",") : ""),
    [categories],
  );

  const queryClient = useQueryClient();

  // Build stream URL with filters - memoized to prevent reconnections
  const streamUrl = useMemo(() => {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "";
    const params = new URLSearchParams();

    if (categoriesKey) {
      params.set("categories", categoriesKey);
    }
    if (fieldId) {
      params.set("field_id", fieldId);
    }
    if (governorate) {
      params.set("governorate", governorate);
    }

    return `${baseUrl}/v1/events/stream?${params.toString()}`;
  }, [categoriesKey, fieldId, governorate]);

  // Handle incoming events - use ref for callback to avoid stale closures
  const handleEvent = useCallback(
    (event: SahoolEvent) => {
      if (!isMountedRef.current) return;

      setState((prev) => ({ ...prev, lastEventTime: new Date() }));

      // Call user callback from ref
      callbacksRef.current.onEvent?.(event);

      // Invalidate relevant queries based on event category
      switch (event.category) {
        case "field":
          queryClient.invalidateQueries({ queryKey: ["fields"] });
          break;
        case "ndvi":
          queryClient.invalidateQueries({ queryKey: ["ndvi"] });
          break;
        case "alert":
          queryClient.invalidateQueries({ queryKey: ["alerts"] });
          break;
        case "weather":
          queryClient.invalidateQueries({ queryKey: ["weather"] });
          break;
        case "irrigation":
          queryClient.invalidateQueries({ queryKey: ["irrigation"] });
          break;
        case "crop_health":
          queryClient.invalidateQueries({ queryKey: ["crop-health"] });
          break;
        case "yield":
          queryClient.invalidateQueries({ queryKey: ["yield"] });
          break;
      }
    },
    [queryClient],
  );

  // Connect to event stream
  const connect = useCallback(() => {
    if (!enabled || typeof window === "undefined" || !isMountedRef.current)
      return;

    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    setState((prev) => ({ ...prev, isConnecting: true, error: null }));

    try {
      const eventSource = new EventSource(streamUrl, { withCredentials: true });

      eventSource.onopen = () => {
        if (!isMountedRef.current) {
          eventSource.close();
          return;
        }
        reconnectAttemptsRef.current = 0;
        setState((prev) => ({
          ...prev,
          isConnected: true,
          isConnecting: false,
          reconnectAttempts: 0,
          error: null,
        }));
        callbacksRef.current.onConnect?.();
      };

      eventSource.onmessage = (messageEvent) => {
        if (!isMountedRef.current) return;
        try {
          const event: SahoolEvent = JSON.parse(messageEvent.data);
          handleEvent(event);
        } catch (e) {
          console.error("Failed to parse event:", e);
        }
      };

      eventSource.onerror = () => {
        if (!isMountedRef.current) {
          eventSource.close();
          return;
        }

        const error = new Error("Event stream connection lost");
        setState((prev) => ({
          ...prev,
          isConnected: false,
          isConnecting: false,
          error,
        }));
        callbacksRef.current.onError?.(error);
        callbacksRef.current.onDisconnect?.();

        eventSource.close();

        // Auto-reconnect logic with exponential backoff
        if (
          autoReconnect &&
          isMountedRef.current &&
          reconnectAttemptsRef.current < maxReconnectAttempts
        ) {
          // Calculate exponential backoff delay using bit shifting for performance
          // Cap the exponent to prevent overflow (2^10 = 1024x initial delay is sufficient)
          const cappedAttempts = Math.min(reconnectAttemptsRef.current, 10);
          const exponentialDelay = Math.min(
            reconnectDelay * (1 << cappedAttempts),
            maxReconnectDelay,
          );

          reconnectAttemptsRef.current++;
          setState((prev) => ({
            ...prev,
            reconnectAttempts: reconnectAttemptsRef.current,
          }));

          reconnectTimeoutRef.current = setTimeout(() => {
            if (isMountedRef.current) {
              connect();
            }
          }, exponentialDelay);
        }
      };

      eventSourceRef.current = eventSource;
    } catch (err) {
      if (isMountedRef.current) {
        const error =
          err instanceof Error ? err : new Error("Failed to connect");
        setState((prev) => ({
          ...prev,
          isConnecting: false,
          error,
        }));
        callbacksRef.current.onError?.(error);
      }
    }
  }, [
    streamUrl,
    handleEvent,
    autoReconnect,
    reconnectDelay,
    maxReconnectDelay,
    maxReconnectAttempts,
    enabled,
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
    reconnectAttemptsRef.current = maxReconnectAttempts; // Prevent auto-reconnect
    setState((prev) => ({
      ...prev,
      isConnected: false,
      isConnecting: false,
    }));
  }, [maxReconnectAttempts]);

  // Manual reconnect
  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    setState((prev) => ({ ...prev, reconnectAttempts: 0 }));
    // Small delay to ensure disconnect is complete
    setTimeout(() => {
      if (isMountedRef.current) {
        connect();
      }
    }, 100);
  }, [disconnect, connect]);

  // Track mounted state and manage connection lifecycle
  useEffect(() => {
    isMountedRef.current = true;

    if (enabled) {
      connect();
    }

    return () => {
      isMountedRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, [connect, enabled]);

  return {
    ...state,
    connect,
    disconnect,
    reconnect,
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
  onUpdate?: (event: SahoolEvent) => void,
) {
  return useEventStream({
    categories: ["ndvi"],
    fieldId,
    onEvent: onUpdate,
  });
}

/**
 * Hook for Alert real-time updates
 */
export function useAlertStream(onAlert?: (event: SahoolEvent) => void) {
  return useEventStream({
    categories: ["alert"],
    onEvent: onAlert,
  });
}

/**
 * Hook for Weather real-time updates
 */
export function useWeatherStream(
  governorate?: string,
  onUpdate?: (event: SahoolEvent) => void,
) {
  return useEventStream({
    categories: ["weather"],
    governorate,
    onEvent: onUpdate,
  });
}

/**
 * Hook for Field real-time updates
 */
export function useFieldStream(
  fieldId?: string,
  onUpdate?: (event: SahoolEvent) => void,
) {
  return useEventStream({
    categories: ["field", "ndvi", "crop_health", "irrigation"],
    fieldId,
    onEvent: onUpdate,
  });
}
