/**
 * SAHOOL useWebSocket Hook
 * اتصال WebSocket للتحديثات الفورية
 *
 * Features:
 * - Auto-reconnect with exponential backoff
 * - Heartbeat/ping-pong for stale connection detection
 * - Message buffering during reconnection
 * - Tab visibility awareness (pause when hidden)
 * - Typed event handlers per category
 * - useWebSocketEvent hook for filtering events by type
 * - React Query cache invalidation on data events
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { WSMessage } from '../types';
import { logger } from '../lib/logger';
import {
  wsClient,
  TimelineEvent,
  getEventCategory,
  type EventCategory,
} from '../lib/ws';

interface UseWebSocketOptions {
  url: string;
  token?: string | null;
  onMessage?: (message: WSMessage) => void;
  reconnectInterval?: number;
  enabled?: boolean;
  heartbeatInterval?: number;
  maxBufferSize?: number;
}

export function useWebSocket({
  url,
  token,
  onMessage,
  reconnectInterval = 5000,
  enabled = true,
  heartbeatInterval = 30000,
  maxBufferSize = 50,
}: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reconnectCount, setReconnectCount] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const pongTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const onMessageRef = useRef(onMessage);
  const isMountedRef = useRef(true);
  const isTabVisibleRef = useRef(typeof document !== 'undefined' ? !document.hidden : true);
  const sendBufferRef = useRef<unknown[]>([]);
  // Use a ref for reconnect count in backoff calculation to keep connect() stable
  const reconnectCountRef = useRef(0);
  // Store connect in a ref so visibility handler always has fresh closure
  const connectRef = useRef<() => void>(() => {});
  // Flag to suppress reconnect after manual disconnect or unmount
  const shouldReconnectRef = useRef(true);

  // Update callback ref when it changes
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  // Tab visibility awareness - pause reconnects when hidden
  useEffect(() => {
    const handleVisibility = () => {
      isTabVisibleRef.current = !document.hidden;
      if (!document.hidden && !isConnected && enabled) {
        // Tab became visible and we're disconnected - reconnect immediately
        connectRef.current();
      }
    };
    document.addEventListener('visibilitychange', handleVisibility);
    return () => document.removeEventListener('visibilitychange', handleVisibility);
  }, [isConnected, enabled]);

  // Flush buffered outbound messages over the now-open WebSocket
  const flushSendBuffer = useCallback(() => {
    const buffer = sendBufferRef.current;
    if (buffer.length > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
      buffer.forEach((msg) => {
        try {
          wsRef.current?.send(JSON.stringify(msg));
        } catch (err) {
          logger.error('Failed to flush buffered message:', err);
        }
      });
      sendBufferRef.current = [];
    }
  }, []);

  // Start heartbeat ping
  const startHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);

    heartbeatIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        // Skip ping if a pong timeout is already pending — avoids resetting
        // the stale-connection detector when heartbeatInterval < 10 s.
        if (pongTimeoutRef.current) return;

        wsRef.current.send(JSON.stringify({ type: 'ping', ts: Date.now() }));

        // Expect pong within 10 seconds
        pongTimeoutRef.current = setTimeout(() => {
          logger.log('WebSocket heartbeat timeout - connection stale, reconnecting...');
          wsRef.current?.close();
        }, 10000);
      }
    }, heartbeatInterval);
  }, [heartbeatInterval]);

  const stopHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
    if (pongTimeoutRef.current) {
      clearTimeout(pongTimeoutRef.current);
      pongTimeoutRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    // Don't connect if unmounted, disabled, tab hidden, or manually disconnected
    if (
      !isMountedRef.current ||
      !enabled ||
      !isTabVisibleRef.current ||
      !shouldReconnectRef.current
    )
      return;

    try {
      // Clean up existing connection
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      stopHeartbeat();

      // Cancel any pending reconnect to avoid overlapping connection attempts
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }

      // Append token as query parameter when provided
      let connectUrl = url;
      if (token) {
        const separator = url.includes('?') ? '&' : '?';
        connectUrl = `${url}${separator}token=${encodeURIComponent(token)}`;
      }

      const ws = new WebSocket(connectUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!isMountedRef.current || ws !== wsRef.current) {
          ws.close();
          return;
        }
        setIsConnected(true);
        setError(null);
        setReconnectCount(0);
        reconnectCountRef.current = 0;
        logger.log('WebSocket connected');

        // Flush any buffered outbound messages
        flushSendBuffer();
        // Start heartbeat
        startHeartbeat();
      };

      ws.onmessage = (event) => {
        if (!isMountedRef.current || ws !== wsRef.current) return;
        try {
          const message: WSMessage = JSON.parse(event.data);

          // Handle pong response - clear pong timeout
          if (message.type === 'pong') {
            if (pongTimeoutRef.current) {
              clearTimeout(pongTimeoutRef.current);
              pongTimeoutRef.current = null;
            }
            return;
          }

          onMessageRef.current?.(message);
        } catch (err) {
          logger.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onclose = (event) => {
        // Ignore close events from stale sockets
        if (ws !== wsRef.current) return;
        if (!isMountedRef.current) return;
        setIsConnected(false);
        stopHeartbeat();

        // Authentication failure - don't reconnect
        const code = (event as CloseEvent)?.code;
        if (code === 4001 || code === 4003) {
          setError('Authentication failed');
          logger.log('WebSocket authentication failed, not reconnecting');
          return;
        }

        // Don't reconnect if manually disconnected or unmounting
        if (!shouldReconnectRef.current) {
          logger.log('WebSocket disconnected, reconnect suppressed');
          return;
        }

        // Don't reconnect if tab is hidden
        if (!isTabVisibleRef.current) {
          logger.log('WebSocket disconnected, tab hidden - waiting for visibility');
          return;
        }

        // Exponential backoff using ref to avoid dependency on state
        const currentCount = reconnectCountRef.current;
        const backoff = Math.min(reconnectInterval * Math.pow(2, currentCount), 60000);
        logger.log(`WebSocket disconnected, reconnecting in ${backoff}ms...`);
        reconnectCountRef.current = currentCount + 1;
        setReconnectCount(reconnectCountRef.current);

        // Clear any existing timeout before setting new one
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = setTimeout(() => {
          connectRef.current();
        }, backoff);
      };

      ws.onerror = (event) => {
        if (!isMountedRef.current || ws !== wsRef.current) return;
        logger.error('WebSocket error:', event);
        setError('Connection unavailable');
      };
    } catch (err) {
      logger.error('Failed to connect WebSocket:', err);
      setError(err instanceof Error ? err.message : 'Failed to connect');
    }
  }, [url, token, reconnectInterval, enabled, flushSendBuffer, startHeartbeat, stopHeartbeat]);

  // Keep connectRef in sync with latest connect
  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  useEffect(() => {
    isMountedRef.current = true;
    shouldReconnectRef.current = true;

    if (enabled) {
      connect();
    }

    return () => {
      isMountedRef.current = false;
      shouldReconnectRef.current = false;
      stopHeartbeat();

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }

      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect, enabled, stopHeartbeat]);

  const send = useCallback(
    (data: unknown) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(data));
      } else {
        // Buffer outbound message for sending when reconnected
        if (sendBufferRef.current.length < maxBufferSize) {
          sendBufferRef.current.push(data);
        }
      }
    },
    [maxBufferSize]
  );

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    stopHeartbeat();
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    wsRef.current?.close();
  }, [stopHeartbeat]);

  return { isConnected, error, send, disconnect, reconnectCount };
}

export default useWebSocket;

// ═══════════════════════════════════════════════════════════════════════════
// Typed Event Hooks
// خطافات الأحداث المصنفة
// ═══════════════════════════════════════════════════════════════════════════

type TimelineEventHandler = (event: TimelineEvent) => void;

/**
 * React Query invalidation keys per event category.
 * Maps ws-gateway event categories to the query keys that should be
 * invalidated when such an event arrives.
 */
const QUERY_KEYS_BY_CATEGORY: Record<string, string[]> = {
  field: ['fields', 'field-details'],
  weather: ['weather', 'weather-forecast'],
  satellite: ['satellite', 'satellite-imagery'],
  ndvi: ['ndvi', 'ndvi-analysis', 'vegetation'],
  inventory: ['inventory', 'stock'],
  crop: ['crop-health', 'crops', 'disease', 'pest'],
  spray: ['spray', 'spray-schedule'],
  task: ['tasks', 'task-details'],
  tasks: ['tasks', 'task-details'],
  iot: ['iot', 'sensors', 'sensor-readings'],
  user: ['users', 'user-status'],
  chat: ['chat', 'messages'],
  system: ['notifications'],
};

/**
 * Subscribe to WebSocket events filtered by event type pattern.
 * The pattern is matched against the event_type string.
 *
 * @param eventType - Full event type (e.g., 'field.updated') or category prefix (e.g., 'field')
 * @param handler - Callback invoked when a matching event is received
 *
 * Usage:
 * ```ts
 * useWebSocketEvent('field.updated', (event) => {
 *   console.log('Field updated:', event.payload);
 * });
 *
 * // Or subscribe to all events in a category:
 * useWebSocketEvent('crop', (event) => {
 *   // Handles crop.disease.detected, crop.pest.detected, crop.health.alert
 * });
 * ```
 */
export function useWebSocketEvent(
  eventType: string,
  handler: TimelineEventHandler
) {
  const handlerRef = useRef(handler);

  useEffect(() => {
    handlerRef.current = handler;
  }, [handler]);

  useEffect(() => {
    const unsubscribe = wsClient.onEvent((event: TimelineEvent) => {
      const type = event.event_type;
      // Exact match or category prefix match
      if (type === eventType || type.startsWith(eventType + '.')) {
        handlerRef.current(event);
      }
    });

    return unsubscribe;
  }, [eventType]);
}

/**
 * Hook that auto-invalidates React Query caches when relevant WebSocket
 * events arrive. Pass a QueryClient instance to enable.
 *
 * @param queryClient - TanStack React Query QueryClient (optional)
 *
 * Usage:
 * ```ts
 * import { useQueryClient } from '@tanstack/react-query';
 *
 * function App() {
 *   const queryClient = useQueryClient();
 *   useWebSocketQueryInvalidation(queryClient);
 * }
 * ```
 */
export function useWebSocketQueryInvalidation(queryClient?: {
  invalidateQueries: (opts: { queryKey: string[] }) => void;
}) {
  useEffect(() => {
    if (!queryClient) return;

    const unsubscribe = wsClient.onEvent((event: TimelineEvent) => {
      const category = getEventCategory(event.event_type);
      const keys = QUERY_KEYS_BY_CATEGORY[category];

      if (keys) {
        for (const key of keys) {
          queryClient.invalidateQueries({ queryKey: [key] });
        }
      }
    });

    return unsubscribe;
  }, [queryClient]);
}

/**
 * Typed event handler callbacks for each ws-gateway event category.
 * All callbacks are optional - only provide the ones you need.
 */
export interface WebSocketEventHandlers {
  onFieldEvent?: TimelineEventHandler;
  onWeatherEvent?: TimelineEventHandler;
  onSatelliteEvent?: TimelineEventHandler;
  onNdviEvent?: TimelineEventHandler;
  onInventoryEvent?: TimelineEventHandler;
  onCropEvent?: TimelineEventHandler;
  onSprayEvent?: TimelineEventHandler;
  onChatEvent?: TimelineEventHandler;
  onTaskEvent?: TimelineEventHandler;
  onIotEvent?: TimelineEventHandler;
  onSystemEvent?: TimelineEventHandler;
  onUserEvent?: TimelineEventHandler;
}

const HANDLER_CATEGORY_MAP: [keyof WebSocketEventHandlers, EventCategory][] = [
  ['onFieldEvent', 'field'],
  ['onWeatherEvent', 'weather'],
  ['onSatelliteEvent', 'satellite'],
  ['onNdviEvent', 'ndvi'],
  ['onInventoryEvent', 'inventory'],
  ['onCropEvent', 'crop'],
  ['onSprayEvent', 'spray'],
  ['onChatEvent', 'chat'],
  ['onTaskEvent', 'task'],
  ['onIotEvent', 'iot'],
  ['onSystemEvent', 'system'],
  ['onUserEvent', 'user'],
];

/**
 * Hook to register typed event handlers for each WebSocket event category.
 * Dispatches incoming events to the appropriate handler based on the
 * event category prefix (e.g., 'crop.disease.detected' -> onCropEvent).
 *
 * Usage:
 * ```ts
 * useWebSocketEvents({
 *   onFieldEvent: (event) => { /* field.created, field.updated, field.deleted *\/ },
 *   onCropEvent: (event) => { /* crop.disease.detected, crop.pest.detected *\/ },
 *   onWeatherEvent: (event) => { /* weather.alert, weather.updated *\/ },
 * });
 * ```
 */
export function useWebSocketEvents(handlers: WebSocketEventHandlers) {
  const handlersRef = useRef(handlers);

  useEffect(() => {
    handlersRef.current = handlers;
  }, [handlers]);

  useEffect(() => {
    const unsubscribe = wsClient.onEvent((event: TimelineEvent) => {
      const category = getEventCategory(event.event_type);

      for (const [handlerKey, cat] of HANDLER_CATEGORY_MAP) {
        if (category === cat) {
          const fn = handlersRef.current[handlerKey];
          if (fn) fn(event);
          return;
        }
      }

      // Handle 'tasks' prefix (legacy) routing to onTaskEvent
      if (category === 'tasks') {
        const fn = handlersRef.current.onTaskEvent;
        if (fn) fn(event);
      }
    });

    return unsubscribe;
  }, []);
}

/**
 * Hook to subscribe/unsubscribe to a chat or field room.
 * Automatically cleans up on unmount.
 *
 * Usage:
 * ```ts
 * useWebSocketRoom(selectedChatRoomId);
 * ```
 */
export function useWebSocketRoom(roomId: string | null | undefined) {
  useEffect(() => {
    if (!roomId) return;

    wsClient.subscribeToRoom(roomId);

    return () => {
      wsClient.unsubscribeFromRoom(roomId);
    };
  }, [roomId]);
}
