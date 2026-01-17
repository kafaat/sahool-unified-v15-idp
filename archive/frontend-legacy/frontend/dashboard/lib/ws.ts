/**
 * SAHOOL WebSocket Client
 * خدمة الأحداث المباشرة
 */

const WS_URL = process.env.WS_URL || "ws://localhost:8081";

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
  private subscriptions: string[] = [];

  constructor(url: string) {
    this.url = url;
  }

  connect(subscriptions: string[] = ["tasks.*", "diagnosis.*", "weather.*"]) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.subscriptions = subscriptions;

    try {
      this.ws = new WebSocket(`${this.url}/events`);

      this.ws.onopen = () => {
        console.log("🔌 WebSocket connected");
        this.reconnectAttempts = 0;
        this.notifyConnectionHandlers(true);

        // Subscribe to event streams
        this.subscribe(subscriptions);
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data);

          if (message.type === "event" && message.data) {
            this.notifyEventHandlers(message.data);
          } else if (message.type === "ping") {
            // Respond to ping
            this.ws?.send(JSON.stringify({ type: "pong" }));
          }
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      this.ws.onclose = (event) => {
        console.log("🔌 WebSocket disconnected", event.code);
        this.notifyConnectionHandlers(false);
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
    } catch (error) {
      console.error("Failed to create WebSocket:", error);
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
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log("Max reconnect attempts reached");
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(
      `Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`,
    );

    setTimeout(() => {
      this.connect(this.subscriptions);
    }, delay);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
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

// Helper hook for React components
export function connectWS(onEvent: EventHandler): WebSocket | null {
  const ws = new WebSocket(`${WS_URL}/events`);

  ws.onopen = () => {
    ws.send(
      JSON.stringify({
        type: "subscribe",
        subjects: ["tasks.*", "diagnosis.*", "weather.*"],
      }),
    );
  };

  ws.onmessage = (msg) => {
    try {
      const message: WSMessage = JSON.parse(msg.data);
      if (message.type === "event" && message.data) {
        onEvent(message.data);
      }
    } catch {}
  };

  return ws;
}

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
  if (eventType.startsWith("task")) return "event-task";
  if (eventType.includes("weather")) return "event-weather";
  if (eventType.includes("disease") || eventType.includes("diagnosis"))
    return "event-disease";
  if (eventType.includes("ndvi")) return "event-ndvi";
  return "event-task";
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
