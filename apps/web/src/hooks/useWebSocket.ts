/**
 * SAHOOL useWebSocket Hook
 * اتصال WebSocket للتحديثات الفورية
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { WSMessage } from '../types';

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

  const connect = useCallback(() => {
    if (!enabled) return;

    try {
      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        setIsConnected(true);
        setError(null);
        console.log('WebSocket connected');
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
        console.log('WebSocket disconnected, reconnecting...');
        reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
      };

      wsRef.current.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('Connection error');
      };
    } catch (err) {
      console.error('Failed to connect WebSocket:', err);
      setError(err instanceof Error ? err.message : 'Failed to connect');
    }
  }, [url, onMessage, reconnectInterval, enabled]);

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
    wsRef.current?.close();
  }, []);

  return { isConnected, error, send, disconnect };
}

export default useWebSocket;