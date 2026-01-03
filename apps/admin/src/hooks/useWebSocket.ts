/**
 * Sahool Admin Dashboard - WebSocket React Hook
 * خطاف React لـ WebSocket - للاتصالات في الوقت الفعلي
 *
 * Provides React integration for WebSocket client
 */

'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import {
import { logger } from '../lib/logger';
  getWebSocketClient,
  ConnectionStatus,
  type AlertMessage,
  type SensorMessage,
  type IrrigationMessage,
  type DiagnosisMessage,
} from '@/lib/websocket';

export type {
  AlertMessage,
  SensorMessage,
  IrrigationMessage,
  DiagnosisMessage,
  ConnectionStatus,
};

type EventType =
  | 'alert'
  | 'sensor'
  | 'irrigation'
  | 'diagnosis'
  | 'farm_update'
  | 'weather'
  | 'task'
  | 'connected'
  | 'disconnected'
  | 'error';

interface UseWebSocketOptions {
  /** Auto-connect on mount */
  autoConnect?: boolean;
  /** Auto-reconnect on unmount */
  autoDisconnect?: boolean;
  /** Subscribe to events on mount */
  events?: {
    type: EventType;
    handler: (data: unknown) => void;
  }[];
}

interface UseWebSocketReturn {
  /** Current connection status */
  status: ConnectionStatus;
  /** Whether connected */
  isConnected: boolean;
  /** Connect to WebSocket server */
  connect: () => void;
  /** Disconnect from WebSocket server */
  disconnect: () => void;
  /** Subscribe to an event */
  subscribe: <T = unknown>(
    event: EventType,
    handler: (data: T) => void
  ) => () => void;
  /** Send a message to the server */
  send: (type: string, data: unknown) => void;
  /** Last error */
  error: Error | null;
}

/**
 * React hook for WebSocket connection
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { status, isConnected, subscribe } = useWebSocket({
 *     autoConnect: true,
 *   });
 *
 *   useEffect(() => {
 *     const unsubscribe = subscribe('alert', (alert: AlertMessage) => {
 *       logger.log('New alert:', alert);
 *     });
 *
 *     return unsubscribe;
 *   }, [subscribe]);
 *
 *   return <div>Status: {status}</div>;
 * }
 * ```
 */
export function useWebSocket(
  options: UseWebSocketOptions = {}
): UseWebSocketReturn {
  const {
    autoConnect = true,
    autoDisconnect = true,
    events = [],
  } = options;

  const [status, setStatus] = useState<ConnectionStatus>(
    ConnectionStatus.DISCONNECTED
  );
  const [error, setError] = useState<Error | null>(null);
  const clientRef = useRef(getWebSocketClient());
  const isConnected = status === ConnectionStatus.CONNECTED;

  // Connect function
  const connect = useCallback(() => {
    clientRef.current.connect();
  }, []);

  // Disconnect function
  const disconnect = useCallback(() => {
    clientRef.current.disconnect();
  }, []);

  // Subscribe function
  const subscribe = useCallback(
    <T = unknown>(event: EventType, handler: (data: T) => void) => {
      // EventType is compatible with the WebSocketClient's event type
      return clientRef.current.on<T>(event, handler);
    },
    []
  );

  // Send function
  const send = useCallback((type: string, data: unknown) => {
    clientRef.current.send(type, data);
  }, []);

  // Setup status listener
  useEffect(() => {
    const unsubscribe = clientRef.current.onStatusChange((newStatus) => {
      setStatus(newStatus);

      // Clear error on successful connection
      if (newStatus === ConnectionStatus.CONNECTED) {
        setError(null);
      }
    });

    return unsubscribe;
  }, []);

  // Setup error listener
  useEffect(() => {
    const unsubscribe = clientRef.current.on('error', (data: any) => {
      setError(
        data?.error instanceof Error
          ? data.error
          : new Error('WebSocket error occurred')
      );
    });

    return unsubscribe;
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      if (autoDisconnect) {
        disconnect();
      }
    };
  }, [autoConnect, autoDisconnect, connect, disconnect]);

  // Subscribe to events
  useEffect(() => {
    const unsubscribers = events.map(({ type, handler }) =>
      subscribe(type, handler)
    );

    return () => {
      unsubscribers.forEach((unsubscribe) => unsubscribe());
    };
  }, [events, subscribe]);

  return {
    status,
    isConnected,
    connect,
    disconnect,
    subscribe,
    send,
    error,
  };
}

/**
 * Hook to subscribe to a specific event type
 *
 * @example
 * ```tsx
 * function AlertsComponent() {
 *   const [alerts, setAlerts] = useState<AlertMessage[]>([]);
 *
 *   useWebSocketEvent('alert', (alert: AlertMessage) => {
 *     setAlerts(prev => [alert, ...prev]);
 *   });
 *
 *   return <div>{alerts.length} alerts</div>;
 * }
 * ```
 */
export function useWebSocketEvent<T = unknown>(
  event: EventType,
  handler: (data: T) => void,
  deps: React.DependencyList = []
): void {
  const { subscribe } = useWebSocket({ autoConnect: false });

  useEffect(() => {
    const unsubscribe = subscribe<T>(event, handler);
    return unsubscribe;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [event, subscribe, ...deps]);
}

/**
 * Hook to manage real-time data updates
 *
 * @example
 * ```tsx
 * function SensorData() {
 *   const sensorReadings = useRealtimeData<SensorMessage>('sensor');
 *
 *   return (
 *     <div>
 *       {sensorReadings.map(reading => (
 *         <div key={reading.timestamp}>{reading.value}</div>
 *       ))}
 *     </div>
 *   );
 * }
 * ```
 */
export function useRealtimeData<T>(
  event: EventType,
  options: {
    maxItems?: number;
    filter?: (item: T) => boolean;
  } = {}
): T[] {
  const { maxItems = 50, filter } = options;
  const [data, setData] = useState<T[]>([]);

  useWebSocketEvent<T>(event, (newData) => {
    setData((prev) => {
      // Apply filter if provided
      if (filter && !filter(newData)) {
        return prev;
      }

      // Add new item and limit array size
      const updated = [newData, ...prev];
      return updated.slice(0, maxItems);
    });
  });

  return data;
}

/**
 * Hook to track connection status with additional helpers
 *
 * @example
 * ```tsx
 * function StatusIndicator() {
 *   const { isConnected, isConnecting, isError, statusText } = useConnectionStatus();
 *
 *   return (
 *     <div className={isConnected ? 'text-green-500' : 'text-red-500'}>
 *       {statusText}
 *     </div>
 *   );
 * }
 * ```
 */
export function useConnectionStatus() {
  const { status, error } = useWebSocket({ autoConnect: false });

  return {
    status,
    isConnected: status === ConnectionStatus.CONNECTED,
    isConnecting: status === ConnectionStatus.CONNECTING,
    isReconnecting: status === ConnectionStatus.RECONNECTING,
    isDisconnected: status === ConnectionStatus.DISCONNECTED,
    isError: status === ConnectionStatus.ERROR,
    error,
    statusText: getStatusText(status),
    statusColor: getStatusColor(status),
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper Functions
// ─────────────────────────────────────────────────────────────────────────────

function getStatusText(status: ConnectionStatus): string {
  switch (status) {
    case ConnectionStatus.CONNECTED:
      return 'متصل';
    case ConnectionStatus.CONNECTING:
      return 'جاري الاتصال...';
    case ConnectionStatus.RECONNECTING:
      return 'إعادة الاتصال...';
    case ConnectionStatus.DISCONNECTED:
      return 'غير متصل';
    case ConnectionStatus.ERROR:
      return 'خطأ في الاتصال';
    default:
      return 'غير معروف';
  }
}

function getStatusColor(status: ConnectionStatus): string {
  switch (status) {
    case ConnectionStatus.CONNECTED:
      return 'green';
    case ConnectionStatus.CONNECTING:
    case ConnectionStatus.RECONNECTING:
      return 'yellow';
    case ConnectionStatus.DISCONNECTED:
      return 'gray';
    case ConnectionStatus.ERROR:
      return 'red';
    default:
      return 'gray';
  }
}
