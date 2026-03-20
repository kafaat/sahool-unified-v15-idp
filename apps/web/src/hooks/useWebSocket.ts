/**
 * SAHOOL useWebSocket Hook
 * اتصال WebSocket للتحديثات الفورية
 *
 * Features:
 * - Auto-reconnect with exponential backoff
 * - Heartbeat/ping-pong for stale connection detection
 * - Message buffering during reconnection
 * - Tab visibility awareness (pause when hidden)
 */

import { useEffect, useRef, useCallback, useState } from "react";
import { WSMessage } from "../types";
import { logger } from "../lib/logger";

interface UseWebSocketOptions {
  url: string;
  onMessage?: (message: WSMessage) => void;
  reconnectInterval?: number;
  enabled?: boolean;
  heartbeatInterval?: number;
  maxBufferSize?: number;
}

export function useWebSocket({
  url,
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
  const isTabVisibleRef = useRef(
    typeof document !== "undefined" ? !document.hidden : true,
  );
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
    document.addEventListener("visibilitychange", handleVisibility);
    return () => document.removeEventListener("visibilitychange", handleVisibility);
  }, [isConnected, enabled]);

  // Flush buffered outbound messages over the now-open WebSocket
  const flushSendBuffer = useCallback(() => {
    const buffer = sendBufferRef.current;
    if (buffer.length > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
      buffer.forEach((msg) => {
        try {
          wsRef.current?.send(JSON.stringify(msg));
        } catch (err) {
          logger.error("Failed to flush buffered message:", err);
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

        wsRef.current.send(JSON.stringify({ type: "ping", ts: Date.now() }));

        // Expect pong within 10 seconds
        pongTimeoutRef.current = setTimeout(() => {
          logger.log("WebSocket heartbeat timeout - connection stale, reconnecting...");
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
    if (!isMountedRef.current || !enabled || !isTabVisibleRef.current || !shouldReconnectRef.current) return;

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

      const ws = new WebSocket(url);
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
        logger.log("WebSocket connected");

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
          if (message.type === "pong") {
            if (pongTimeoutRef.current) {
              clearTimeout(pongTimeoutRef.current);
              pongTimeoutRef.current = null;
            }
            return;
          }

          onMessageRef.current?.(message);
        } catch (err) {
          logger.error("Failed to parse WebSocket message:", err);
        }
      };

      ws.onclose = () => {
        // Ignore close events from stale sockets
        if (ws !== wsRef.current) return;
        if (!isMountedRef.current) return;
        setIsConnected(false);
        stopHeartbeat();

        // Don't reconnect if manually disconnected or unmounting
        if (!shouldReconnectRef.current) {
          logger.log("WebSocket disconnected, reconnect suppressed");
          return;
        }

        // Don't reconnect if tab is hidden
        if (!isTabVisibleRef.current) {
          logger.log("WebSocket disconnected, tab hidden - waiting for visibility");
          return;
        }

        // Exponential backoff using ref to avoid dependency on state
        const currentCount = reconnectCountRef.current;
        const backoff = Math.min(
          reconnectInterval * Math.pow(2, currentCount),
          60000
        );
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

      ws.onerror = () => {
        if (!isMountedRef.current || ws !== wsRef.current) return;
        // Use warn instead of error to avoid triggering Next.js error overlay
        // WebSocket unavailability is expected when backend services are down
        logger.warn("WebSocket connection unavailable");
        setError("Connection unavailable");
      };
    } catch (err) {
      logger.warn("WebSocket unavailable:", err);
      setError(err instanceof Error ? err.message : "Failed to connect");
    }
  }, [url, reconnectInterval, enabled, flushSendBuffer, startHeartbeat, stopHeartbeat]);

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

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      // Buffer outbound message for sending when reconnected
      if (sendBufferRef.current.length < maxBufferSize) {
        sendBufferRef.current.push(data);
      }
    }
  }, [maxBufferSize]);

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
