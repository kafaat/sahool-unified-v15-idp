/**
 * SAHOOL useWebSocket Hook
 * اتصال WebSocket للتحديثات الفورية
 */

import { useEffect, useRef, useCallback, useState } from "react";
import { WSMessage } from "../types";
import { logger } from "../lib/logger";

interface UseWebSocketOptions {
  url: string;
  onMessage?: (message: WSMessage) => void;
  reconnectInterval?: number;
  enabled?: boolean;
}

export function useWebSocket({
  url,
  onMessage,
  reconnectInterval = 5000,
  enabled = true,
}: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const onMessageRef = useRef(onMessage);
  const isMountedRef = useRef(true);

  // Update callback ref when it changes
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  const connect = useCallback(() => {
    // Don't connect if unmounted or disabled
    if (!isMountedRef.current || !enabled) return;

    try {
      // Clean up existing connection
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }

      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        if (!isMountedRef.current) {
          wsRef.current?.close();
          return;
        }
        setIsConnected(true);
        setError(null);
        logger.log("WebSocket connected");
      };

      wsRef.current.onmessage = (event) => {
        if (!isMountedRef.current) return;
        try {
          const message: WSMessage = JSON.parse(event.data);
          onMessageRef.current?.(message);
        } catch (err) {
          logger.error("Failed to parse WebSocket message:", err);
        }
      };

      wsRef.current.onclose = () => {
        if (!isMountedRef.current) return;
        setIsConnected(false);
        logger.log("WebSocket disconnected, reconnecting...");

        // Clear any existing timeout before setting new one
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
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
  }, [url, reconnectInterval, enabled]);

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

      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect, enabled]);

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    wsRef.current?.close();
  }, []);

  return { isConnected, error, send, disconnect };
}

export default useWebSocket;
