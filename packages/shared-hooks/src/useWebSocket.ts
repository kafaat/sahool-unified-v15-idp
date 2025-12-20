// ═══════════════════════════════════════════════════════════════════════════════
// useWebSocket Hook
// اتصال WebSocket للتحديثات الفورية
// ═══════════════════════════════════════════════════════════════════════════════

import { useEffect, useRef, useCallback, useState } from 'react';

export interface WSMessage<T = unknown> {
  type: string;
  payload: T;
  timestamp?: string;
}

export interface UseWebSocketOptions {
  url: string;
  onMessage?: (message: WSMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  enabled?: boolean;
}

export interface UseWebSocketReturn {
  isConnected: boolean;
  error: string | null;
  send: (data: unknown) => void;
  disconnect: () => void;
  reconnect: () => void;
}

export function useWebSocket({
  url,
  onMessage,
  onConnect,
  onDisconnect,
  onError,
  reconnectInterval = 5000,
  maxReconnectAttempts = 10,
  enabled = true,
}: UseWebSocketOptions): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    if (!enabled || typeof window === 'undefined') return;

    try {
      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
        onConnect?.();
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data);
          onMessage?.(message);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      wsRef.current.onclose = () => {
        setIsConnected(false);
        onDisconnect?.();

        // Auto-reconnect with backoff
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = reconnectInterval * Math.pow(1.5, reconnectAttemptsRef.current);
          reconnectAttemptsRef.current++;
          reconnectTimeoutRef.current = setTimeout(connect, delay);
        }
      };

      wsRef.current.onerror = (event) => {
        setError('Connection error');
        onError?.(event);
      };
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to connect');
    }
  }, [url, onMessage, onConnect, onDisconnect, onError, reconnectInterval, maxReconnectAttempts, enabled]);

  useEffect(() => {
    if (enabled) {
      connect();
    }

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      wsRef.current?.close();
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
    reconnectAttemptsRef.current = maxReconnectAttempts; // Prevent auto-reconnect
    wsRef.current?.close();
  }, [maxReconnectAttempts]);

  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    connect();
  }, [disconnect, connect]);

  return { isConnected, error, send, disconnect, reconnect };
}

export default useWebSocket;
