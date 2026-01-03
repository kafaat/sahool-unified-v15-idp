/**
 * Sahool Admin Dashboard - WebSocket Client
 * عميل WebSocket للوحة تحكم سهول - للاتصالات في الوقت الفعلي
 *
 * Provides real-time updates for:
 * - Alert notifications
 * - Sensor readings
 * - Irrigation status
 * - Farm events
 */

import { logger } from './logger';

type WebSocketEventType =
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

export interface WebSocketMessage {
  type: WebSocketEventType;
  timestamp: string;
  data: unknown;
}

export interface AlertMessage {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  farmId?: string;
  farmName?: string;
  createdAt: string;
}

export interface SensorMessage {
  farmId: string;
  sensorType: string;
  value: number;
  unit: string;
  timestamp: string;
}

export interface IrrigationMessage {
  farmId: string;
  status: 'started' | 'completed' | 'failed';
  duration?: number;
  waterUsed?: number;
  timestamp: string;
}

export interface DiagnosisMessage {
  id: string;
  farmId: string;
  farmName: string;
  diseaseNameAr: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  timestamp: string;
}

type EventCallback<T = unknown> = (data: T) => void;

export enum ConnectionStatus {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error',
}

interface WebSocketClientConfig {
  url?: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  debug?: boolean;
}

/**
 * WebSocket Client for real-time updates
 * Handles connection management, auto-reconnect, and event subscriptions
 */
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectInterval: number;
  private maxReconnectAttempts: number;
  private heartbeatInterval: number;
  private debug: boolean;

  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;

  private status: ConnectionStatus = ConnectionStatus.DISCONNECTED;
  private eventListeners = new Map<WebSocketEventType, Set<EventCallback>>();
  private statusListeners = new Set<(status: ConnectionStatus) => void>();

  constructor(config: WebSocketClientConfig = {}) {
    // Determine WebSocket protocol based on current page protocol (for security)
    // Use wss:// in production (HTTPS) and ws:// only in local development
    const getDefaultWsUrl = (): string => {
      if (typeof window === 'undefined') return 'ws://localhost:8090';

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.hostname;
      const port = process.env.NODE_ENV === 'production' ? '' : ':8090';

      // In production, use secure WebSocket; in development, allow insecure for localhost
      return process.env.NODE_ENV === 'production'
        ? `${protocol}//${host}${port}`
        : 'ws://localhost:8090';
    };

    const baseUrl = config.url || process.env.NEXT_PUBLIC_WS_URL || getDefaultWsUrl();
    this.url = `${baseUrl}/ws/admin`;
    this.reconnectInterval = config.reconnectInterval || 5000;
    this.maxReconnectAttempts = config.maxReconnectAttempts || 10;
    this.heartbeatInterval = config.heartbeatInterval || 30000;
    this.debug = config.debug || false;
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.log('Already connected');
      return;
    }

    if (this.ws?.readyState === WebSocket.CONNECTING) {
      this.log('Connection already in progress');
      return;
    }

    this.setStatus(
      this.reconnectAttempts > 0
        ? ConnectionStatus.RECONNECTING
        : ConnectionStatus.CONNECTING
    );

    try {
      this.log('Connecting to', this.url);
      this.ws = new WebSocket(this.url);
      this.setupEventHandlers();
    } catch (error) {
      this.log('Connection error:', error);
      this.setStatus(ConnectionStatus.ERROR);
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.log('Disconnecting...');
    this.clearReconnectTimer();
    this.clearHeartbeatTimer();

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }

    this.setStatus(ConnectionStatus.DISCONNECTED);
  }

  /**
   * Subscribe to a specific event type
   */
  on<T = unknown>(event: WebSocketEventType, callback: EventCallback<T>): () => void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set());
    }

    this.eventListeners.get(event)!.add(callback as EventCallback);

    // Return unsubscribe function
    return () => {
      const listeners = this.eventListeners.get(event);
      if (listeners) {
        listeners.delete(callback as EventCallback);
      }
    };
  }

  /**
   * Subscribe to connection status changes
   */
  onStatusChange(callback: (status: ConnectionStatus) => void): () => void {
    this.statusListeners.add(callback);

    // Immediately call with current status
    callback(this.status);

    // Return unsubscribe function
    return () => {
      this.statusListeners.delete(callback);
    };
  }

  /**
   * Send a message to the server
   */
  send(type: string, data: unknown): void {
    if (this.ws?.readyState !== WebSocket.OPEN) {
      this.log('Cannot send message: not connected');
      return;
    }

    const message = {
      type,
      data,
      timestamp: new Date().toISOString(),
    };

    this.ws.send(JSON.stringify(message));
    this.log('Sent:', message);
  }

  /**
   * Get current connection status
   */
  getStatus(): ConnectionStatus {
    return this.status;
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.status === ConnectionStatus.CONNECTED;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Private Methods
  // ─────────────────────────────────────────────────────────────────────────

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      this.log('Connected');
      this.reconnectAttempts = 0;
      this.setStatus(ConnectionStatus.CONNECTED);
      this.startHeartbeat();
      this.emit('connected', { timestamp: new Date().toISOString() });
    };

    this.ws.onclose = (event) => {
      this.log('Disconnected:', event.code, event.reason);
      this.clearHeartbeatTimer();

      if (event.code !== 1000) {
        // Abnormal closure, attempt reconnect
        this.scheduleReconnect();
      } else {
        this.setStatus(ConnectionStatus.DISCONNECTED);
      }

      this.emit('disconnected', {
        code: event.code,
        reason: event.reason,
        timestamp: new Date().toISOString(),
      });
    };

    this.ws.onerror = (error) => {
      this.log('WebSocket error:', error);
      this.setStatus(ConnectionStatus.ERROR);
      this.emit('error', { error, timestamp: new Date().toISOString() });
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.log('Received:', message);
        this.handleMessage(message);
      } catch (error) {
        this.log('Failed to parse message:', error);
      }
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    // Handle heartbeat response
    const messageType = message.type as string;
    if (messageType === 'heartbeat' || messageType === 'pong') {
      return;
    }

    // Emit to type-specific listeners
    this.emit(message.type, message.data);
  }

  private emit(event: WebSocketEventType, data: unknown): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          this.log('Error in event listener:', error);
        }
      });
    }
  }

  private setStatus(status: ConnectionStatus): void {
    if (this.status === status) return;

    this.status = status;
    this.log('Status changed to:', status);

    this.statusListeners.forEach((callback) => {
      try {
        callback(status);
      } catch (error) {
        this.log('Error in status listener:', error);
      }
    });
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.log('Max reconnect attempts reached');
      this.setStatus(ConnectionStatus.ERROR);
      return;
    }

    this.clearReconnectTimer();

    const delay = Math.min(
      this.reconnectInterval * Math.pow(2, this.reconnectAttempts),
      30000 // Max 30 seconds
    );

    this.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private startHeartbeat(): void {
    this.clearHeartbeatTimer();

    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send('ping', { timestamp: new Date().toISOString() });
      }
    }, this.heartbeatInterval);
  }

  private clearHeartbeatTimer(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private log(...args: unknown[]): void {
    if (this.debug) {
      logger.log('[WebSocket]', ...args);
    }
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// Singleton Instance
// ═════════════════════════════════════════════════════════════════════════════

let wsClient: WebSocketClient | null = null;

/**
 * Dummy WebSocket client for SSR
 */
class DummyWebSocketClient implements Partial<WebSocketClient> {
  connect(): void {}
  disconnect(): void {}
  on<T = unknown>(_event: WebSocketEventType, _callback: EventCallback<T>): () => void {
    return () => {};
  }
  onStatusChange(_callback: (status: ConnectionStatus) => void): () => void {
    return () => {};
  }
  send(_type: string, _data: unknown): void {}
  getStatus(): ConnectionStatus {
    return ConnectionStatus.DISCONNECTED;
  }
  isConnected(): boolean {
    return false;
  }
}

/**
 * Get the singleton WebSocket client instance
 */
export function getWebSocketClient(): WebSocketClient {
  if (typeof window === 'undefined') {
    // Server-side rendering, return a dummy client
    return new DummyWebSocketClient() as WebSocketClient;
  }

  if (!wsClient) {
    wsClient = new WebSocketClient({
      debug: process.env.NODE_ENV === 'development',
    });
  }

  return wsClient;
}

/**
 * Initialize WebSocket connection
 */
export function initWebSocket(): WebSocketClient {
  const client = getWebSocketClient();
  client.connect();
  return client;
}
