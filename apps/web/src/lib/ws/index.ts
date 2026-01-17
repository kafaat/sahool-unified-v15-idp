/**
 * SAHOOL WebSocket Client
 * خدمة الأحداث المباشرة - متوافق مع الـ kernel المسترجع
 */

import { logger } from "../logger";

// Default WebSocket URL for CI/build environments
const DEFAULT_WS_URL = "ws://localhost:8081";

// Determine WebSocket URL from environment variable
const getWebSocketUrl = (): string => {
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL;

  if (!wsUrl) {
    // Use default URL in development or CI/build environments
    // In production with proper deployment, NEXT_PUBLIC_WS_URL should always be set
    if (
      process.env.NODE_ENV === "development" ||
      typeof window === "undefined"
    ) {
      logger.warn(
        `NEXT_PUBLIC_WS_URL not set, using default ${DEFAULT_WS_URL}`,
      );
      return DEFAULT_WS_URL;
    }
    // In browser production environment without WS_URL, use default but warn
    logger.warn(
      `NEXT_PUBLIC_WS_URL not configured, WebSocket features may not work`,
    );
    return DEFAULT_WS_URL;
  }

  return wsUrl;
};

const WS_URL = getWebSocketUrl();

export interface TimelineEvent {
  event_id: string;
  event_type: string;
  aggregate_id: string;
  tenant_id: string;
  timestamp: string;
  payload: Record<string, unknown>;
}

export interface WSMessage {
  type: "event" | "ping" | "subscribed" | "error";
  data?: TimelineEvent;
  message?: string;
}

type EventHandler = (event: TimelineEvent) => void;
type ConnectionHandler = (connected: boolean) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private eventHandlers: Set<EventHandler> = new Set();
  private connectionHandlers: Set<ConnectionHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
  private subscriptions: string[] = [];
  private shouldReconnect = true;

  constructor(url: string) {
    this.url = url;
  }

  connect(
    subscriptions: string[] = ["tasks.*", "diagnosis.*", "weather.*", "ndvi.*"],
  ) {
    if (typeof window === "undefined") return; // SSR check
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.shouldReconnect = true;
    this.subscriptions = subscriptions;

    try {
      this.ws = new WebSocket(`${this.url}/events`);

      this.ws.onopen = () => {
        logger.log("🔌 WebSocket connected");
        this.reconnectAttempts = 0;
        this.notifyConnectionHandlers(true);
        this.subscribe(subscriptions);
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data);

          if (message.type === "event" && message.data) {
            this.notifyEventHandlers(message.data);
          } else if (message.type === "ping") {
            this.ws?.send(JSON.stringify({ type: "pong" }));
          }
        } catch (error) {
          logger.error("Failed to parse WebSocket message:", error);
        }
      };

      this.ws.onclose = (event) => {
        logger.log("🔌 WebSocket disconnected", event.code);
        this.notifyConnectionHandlers(false);
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        logger.error("WebSocket error:", error);
      };
    } catch (error) {
      logger.error("Failed to create WebSocket:", error);
      this.attemptReconnect();
    }
  }

  private subscribe(subjects: string[]) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: "subscribe",
          subjects,
        }),
      );
    }
  }

  private attemptReconnect() {
    // Don't reconnect if explicitly disconnected
    if (!this.shouldReconnect) {
      return;
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      logger.log("Max reconnect attempts reached");
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    logger.log(
      `Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`,
    );

    // Clear any existing reconnect timeout
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    this.reconnectTimeout = setTimeout(() => {
      this.reconnectTimeout = null;
      this.connect(this.subscriptions);
    }, delay);
  }

  disconnect() {
    this.shouldReconnect = false;

    // Clear reconnect timeout
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    // Close WebSocket
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    // Reset reconnect attempts
    this.reconnectAttempts = 0;
  }

  onEvent(handler: EventHandler) {
    this.eventHandlers.add(handler);
    return () => this.eventHandlers.delete(handler);
  }

  onConnection(handler: ConnectionHandler) {
    this.connectionHandlers.add(handler);
    return () => this.connectionHandlers.delete(handler);
  }

  private notifyEventHandlers(event: TimelineEvent) {
    this.eventHandlers.forEach((handler) => handler(event));
  }

  private notifyConnectionHandlers(connected: boolean) {
    this.connectionHandlers.forEach((handler) => handler(connected));
  }

  get isConnected() {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Export singleton instance
export const wsClient = new WebSocketClient(WS_URL);

// Event type helpers
export function getEventIcon(eventType: string): string {
  if (eventType.startsWith("task")) return "📋";
  if (eventType.includes("weather")) return "🌤️";
  if (eventType.includes("disease") || eventType.includes("diagnosis"))
    return "🔬";
  if (eventType.includes("ndvi")) return "🛰️";
  if (eventType.includes("irrigation")) return "💧";
  if (eventType.includes("fertilizer")) return "🧪";
  return "📌";
}

export function getEventColor(eventType: string): string {
  if (eventType.startsWith("task")) return "bg-blue-50 border-blue-200";
  if (eventType.includes("weather")) return "bg-amber-50 border-amber-200";
  if (eventType.includes("disease") || eventType.includes("diagnosis"))
    return "bg-red-50 border-red-200";
  if (eventType.includes("ndvi")) return "bg-emerald-50 border-emerald-200";
  return "bg-gray-50 border-gray-200";
}

export function formatEventType(eventType: string): string {
  const translations: Record<string, string> = {
    task_created: "مهمة جديدة",
    task_assigned: "تم تعيين مهمة",
    task_completed: "اكتملت مهمة",
    task_rescheduled: "تم إعادة جدولة",
    image_diagnosed: "تشخيص صورة",
    weather_alert_issued: "تنبيه طقس",
    ndvi_processed: "تحليل NDVI",
    disease_risk_calculated: "تقييم خطر المرض",
  };
  return translations[eventType] || eventType;
}
