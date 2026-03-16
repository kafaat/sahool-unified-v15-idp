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
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pongTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const onMessageRef = useRef(onMessage);
  const isMountedRef = useRef(true);
  const isTabVisibleRef = useRef(true);
  const messageBufferRef = useRef<WSMessage[]>([]);

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
        connect();
      }
    };
    document.addEventListener("visibilitychange", handleVisibility);
    return () => document.removeEventListener("visibilitychange", handleVisibility);
  }, [isConnected, enabled]); // eslint-disable-line react-hooks/exhaustive-deps

  // Flush buffered messages to handler
  const flushBuffer = useCallback(() => {
    const buffer = messageBufferRef.current;
    if (buffer.length > 0 && onMessageRef.current) {
      buffer.forEach((msg) => onMessageRef.current?.(msg));
      messageBufferRef.current = [];
    }
  }, []);

  // Start heartbeat ping
  const startHeartbeat = useCallback(() => {
    if (heartbeatTimeoutRef.current) clearInterval(heartbeatTimeoutRef.current);

    heartbeatTimeoutRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
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
    if (heartbeatTimeoutRef.current) {
      clearInterval(heartbeatTimeoutRef.current);
      heartbeatTimeoutRef.current = null;
    }
    if (pongTimeoutRef.current) {
      clearTimeout(pongTimeoutRef.current);
      pongTimeoutRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    // Don't connect if unmounted, disabled, or tab hidden
    if (!isMountedRef.current || !enabled) return;

    try {
      // Clean up existing connection
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      stopHeartbeat();

      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        if (!isMountedRef.current) {
          wsRef.current?.close();
          return;
        }
        setIsConnected(true);
        setError(null);
        setReconnectCount(0);
        logger.log("WebSocket connected");

        // Flush any buffered messages
        flushBuffer();
        // Start heartbeat
        startHeartbeat();
      };

      wsRef.current.onmessage = (event) => {
        if (!isMountedRef.current) return;
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

      wsRef.current.onclose = () => {
        if (!isMountedRef.current) return;
        setIsConnected(false);
        stopHeartbeat();

        // Don't reconnect if tab is hidden
        if (!isTabVisibleRef.current) {
          logger.log("WebSocket disconnected, tab hidden - waiting for visibility");
          return;
        }

        // Exponential backoff: 5s, 10s, 20s, 40s, max 60s
        const backoff = Math.min(
          reconnectInterval * Math.pow(2, reconnectCount),
          60000
        );
        logger.log(`WebSocket disconnected, reconnecting in ${backoff}ms...`);
        setReconnectCount((c) => c + 1);

        // Clear any existing timeout before setting new one
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = setTimeout(connect, backoff);
      };

      wsRef.current.onerror = (event) => {
        if (!isMountedRef.current) return;
        logger.error("WebSocket error:", event);
        setError("Connection error");
      };
    } catch (err) {
      logger.error("Failed to connect WebSocket:", err);
      setError(err instanceof Error ? err.message : "Failed to connect");
    }
  }, [url, reconnectInterval, enabled, reconnectCount, flushBuffer, startHeartbeat, stopHeartbeat]);

  useEffect(() => {
    isMountedRef.current = true;

    if (enabled) {
      connect();
    }

    return () => {
      isMountedRef.current = false;
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
      // Buffer message if not connected
      const msg = data as WSMessage;
      if (messageBufferRef.current.length < maxBufferSize) {
        messageBufferRef.current.push(msg);
      }
    }
  }, [maxBufferSize]);

  const disconnect = useCallback(() => {
    stopHeartbeat();
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    wsRef.current?.close();
  }, [stopHeartbeat]);

  return { isConnected, error, send, disconnect, reconnectCount };
}

export default useWebSocket;
