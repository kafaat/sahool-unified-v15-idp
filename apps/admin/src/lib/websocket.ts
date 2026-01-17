/**
 * Sahool Admin Dashboard - WebSocket Client
 * عميل WebSocket للوحة تحكم سهول - للاتصالات في الوقت الفعلي
 *
 * Provides real-time updates for:
 * - Alert notifications
 * - Sensor readings
 * - Irrigation status
 * - Farm events
 *
 * SECURITY: WebSocket connections are authenticated via JWT token
 * Tokens are fetched from the server-side API route that reads httpOnly cookies
 */

import { logger } from "./logger";

// ═══════════════════════════════════════════════════════════════════════════
// Authentication Token Management
// ═══════════════════════════════════════════════════════════════════════════

interface WSTokenResponse {
  success: boolean;
  token?: string;
  tenant_id?: string;
  error?: string;
}

/**
 * Fetch WebSocket authentication token from server
 * الحصول على توكن المصادقة لـ WebSocket من الخادم
 *
 * The token is stored in an httpOnly cookie and not directly accessible.
 * This endpoint safely provides the token for WebSocket authentication.
 */
async function getWebSocketToken(): Promise<WSTokenResponse> {
  try {
    const response = await fetch("/api/auth/ws-token", {
      method: "GET",
      credentials: "same-origin",
    });

    if (!response.ok) {
      if (response.status === 401) {
        return { success: false, error: "Not authenticated" };
      }
      if (response.status === 429) {
        return { success: false, error: "Rate limited" };
      }
      return { success: false, error: "Failed to get token" };
    }

    return await response.json();
  } catch (error) {
    logger.error("Failed to fetch WebSocket token:", error);
    return { success: false, error: "Network error" };
  }
}

type WebSocketEventType =
  | "alert"
  | "sensor"
  | "irrigation"
  | "diagnosis"
  | "farm_update"
  | "weather"
  | "task"
  | "connected"
  | "disconnected"
  | "error";

export interface WebSocketMessage {
  type: WebSocketEventType;
  timestamp: string;
  data: unknown;
}

export interface AlertMessage {
  id: string;
  type: string;
  severity: "low" | "medium" | "high" | "critical";
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
  status: "started" | "completed" | "failed";
  duration?: number;
  waterUsed?: number;
  timestamp: string;
}

export interface DiagnosisMessage {
  id: string;
  farmId: string;
  farmName: string;
  diseaseNameAr: string;
  severity: "low" | "medium" | "high" | "critical";
  confidence: number;
  timestamp: string;
}

type EventCallback<T = unknown> = (data: T) => void;

export enum ConnectionStatus {
  DISCONNECTED = "disconnected",
  CONNECTING = "connecting",
  CONNECTED = "connected",
  RECONNECTING = "reconnecting",
  ERROR = "error",
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
  private baseUrl: string;
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

  private currentToken: string | null = null;
  private currentTenantId: string | null = null;

  constructor(config: WebSocketClientConfig = {}) {
    // Determine WebSocket protocol based on current page protocol (for security)
    // Use wss:// in production (HTTPS) and ws:// only in local development
    const getDefaultWsUrl = (): string => {
      if (typeof window === "undefined") return "ws://localhost:8081";

      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = window.location.hostname;
      const port = process.env.NODE_ENV === "production" ? "" : ":8081";

      // In production, use secure WebSocket; in development, allow insecure for localhost
      return process.env.NODE_ENV === "production"
        ? `${protocol}//${host}${port}`
        : "ws://localhost:8081";
    };

    this.baseUrl =
      config.url || process.env.NEXT_PUBLIC_WS_URL || getDefaultWsUrl();
    this.reconnectInterval = config.reconnectInterval || 5000;
    this.maxReconnectAttempts = config.maxReconnectAttempts || 10;
    this.heartbeatInterval = config.heartbeatInterval || 30000;
    this.debug = config.debug || false;
  }

  /**
   * Connect to WebSocket server with authentication
   * الاتصال بخادم WebSocket مع المصادقة
   */
  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.log("Already connected");
      return;
    }

    if (this.ws?.readyState === WebSocket.CONNECTING) {
      this.log("Connection already in progress");
      return;
    }

    this.setStatus(
      this.reconnectAttempts > 0
        ? ConnectionStatus.RECONNECTING
        : ConnectionStatus.CONNECTING,
    );

    // Fetch authentication token
    const tokenResponse = await getWebSocketToken();

    if (!tokenResponse.success || !tokenResponse.token) {
      this.log(
        "WebSocket authentication failed:",
        tokenResponse.error || "No token available",
      );

      // Set error status if not authenticated
      if (tokenResponse.error === "Not authenticated") {
        this.setStatus(ConnectionStatus.DISCONNECTED);
        return;
      }

      this.setStatus(ConnectionStatus.ERROR);
      this.scheduleReconnect();
      return;
    }

    this.currentToken = tokenResponse.token;
    this.currentTenantId = tokenResponse.tenant_id || "default";

    try {
      // Build WebSocket URL with authentication query parameters
      // The ws-gateway expects: /ws?tenant_id=xxx&token=xxx
      const wsUrl = new URL(`${this.baseUrl}/ws`);
      wsUrl.searchParams.set("tenant_id", this.currentTenantId);
      wsUrl.searchParams.set("token", this.currentToken);

      this.log("Connecting to", wsUrl.toString().replace(/token=[^&]+/, "token=***"));
      this.ws = new WebSocket(wsUrl.toString());
      this.setupEventHandlers();
    } catch (error) {
      this.log("Connection error:", error);
      this.setStatus(ConnectionStatus.ERROR);
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.log("Disconnecting...");
    this.clearReconnectTimer();
    this.clearHeartbeatTimer();

    if (this.ws) {
      this.ws.close(1000, "Client disconnect");
      this.ws = null;
    }

    this.setStatus(ConnectionStatus.DISCONNECTED);
  }

  /**
   * Subscribe to a specific event type
   */
  on<T = unknown>(
    event: WebSocketEventType,
    callback: EventCallback<T>,
  ): () => void {
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
      this.log("Cannot send message: not connected");
      return;
    }

    const message = {
      type,
      data,
      timestamp: new Date().toISOString(),
    };

    this.ws.send(JSON.stringify(message));
    this.log("Sent:", message);
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
      this.log("Connected with authentication");
      this.reconnectAttempts = 0;
      this.setStatus(ConnectionStatus.CONNECTED);
      this.startHeartbeat();
      this.emit("connected", { timestamp: new Date().toISOString() });
    };

    this.ws.onclose = (event) => {
      this.log("Disconnected:", event.code, event.reason);
      this.clearHeartbeatTimer();

      // Handle authentication errors (4001 = auth required, 4003 = tenant mismatch)
      if (event.code === 4001 || event.code === 4003) {
        this.log("WebSocket authentication failed:", event.reason);
        // Clear cached token to force re-fetch on reconnect
        this.currentToken = null;
      }

      if (event.code !== 1000) {
        // Abnormal closure, attempt reconnect
        this.scheduleReconnect();
      } else {
        this.setStatus(ConnectionStatus.DISCONNECTED);
      }

      this.emit("disconnected", {
        code: event.code,
        reason: event.reason,
        timestamp: new Date().toISOString(),
      });
    };

    this.ws.onerror = (error) => {
      this.log("WebSocket error:", error);
      this.setStatus(ConnectionStatus.ERROR);
      this.emit("error", { error, timestamp: new Date().toISOString() });
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.log("Received:", message);
        this.handleMessage(message);
      } catch (error) {
        this.log("Failed to parse message:", error);
      }
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    // Handle heartbeat response
    const messageType = message.type as string;
    if (messageType === "heartbeat" || messageType === "pong") {
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
          this.log("Error in event listener:", error);
        }
      });
    }
  }

  private setStatus(status: ConnectionStatus): void {
    if (this.status === status) return;

    this.status = status;
    this.log("Status changed to:", status);

    this.statusListeners.forEach((callback) => {
      try {
        callback(status);
      } catch (error) {
        this.log("Error in status listener:", error);
      }
    });
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.log("Max reconnect attempts reached");
      this.setStatus(ConnectionStatus.ERROR);
      return;
    }

    this.clearReconnectTimer();

    const delay = Math.min(
      this.reconnectInterval * Math.pow(2, this.reconnectAttempts),
      30000, // Max 30 seconds
    );

    this.log(
      `Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`,
    );

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      // Clear cached token to fetch fresh token on reconnect
      this.currentToken = null;
      void this.connect();
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
        this.send("ping", { timestamp: new Date().toISOString() });
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
      logger.log("[WebSocket]", ...args);
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
  async connect(): Promise<void> {}
  disconnect(): void {}
  on<T = unknown>(
    _event: WebSocketEventType,
    _callback: EventCallback<T>,
  ): () => void {
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
  if (typeof window === "undefined") {
    // Server-side rendering, return a dummy client
    return new DummyWebSocketClient() as WebSocketClient;
  }

  if (!wsClient) {
    wsClient = new WebSocketClient({
      debug: process.env.NODE_ENV === "development",
    });
  }

  return wsClient;
}

/**
 * Initialize WebSocket connection
 * Initializes and connects the WebSocket client with authentication
 */
export async function initWebSocket(): Promise<WebSocketClient> {
  const client = getWebSocketClient();
  await client.connect();
  return client;
}
