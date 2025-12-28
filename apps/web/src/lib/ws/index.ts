/**
 * SAHOOL WebSocket Client
 * خدمة الأحداث المباشرة - متوافق مع الـ kernel المسترجع
 */

// Determine WebSocket protocol based on current page protocol (for security)
// Use wss:// in production (HTTPS) and ws:// only in local development
const getDefaultWsUrl = (): string => {
  if (typeof window === 'undefined') return 'ws://localhost:8081';

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.hostname;
  const port = process.env.NODE_ENV === 'production' ? '' : ':8081';

  // In production, use secure WebSocket; in development, allow insecure for localhost
  return process.env.NODE_ENV === 'production'
    ? `${protocol}//${host}${port}`
    : 'ws://localhost:8081';
};

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || getDefaultWsUrl();

export interface TimelineEvent {
  event_id: string;
  event_type: string;
  aggregate_id: string;
  tenant_id: string;
  timestamp: string;
  payload: Record<string, unknown>;
}

export interface WSMessage {
  type: 'event' | 'ping' | 'subscribed' | 'error';
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

  connect(subscriptions: string[] = ['tasks.*', 'diagnosis.*', 'weather.*', 'ndvi.*']) {
    if (typeof window === 'undefined') return; // SSR check
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.subscriptions = subscriptions;

    try {
      this.ws = new WebSocket(`${this.url}/events`);

      this.ws.onopen = () => {
        console.log('🔌 WebSocket connected');
        this.reconnectAttempts = 0;
        this.notifyConnectionHandlers(true);
        this.subscribe(subscriptions);
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data);

          if (message.type === 'event' && message.data) {
            this.notifyEventHandlers(message.data);
          } else if (message.type === 'ping') {
            this.ws?.send(JSON.stringify({ type: 'pong' }));
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('🔌 WebSocket disconnected', event.code);
        this.notifyConnectionHandlers(false);
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.attemptReconnect();
    }
  }

  private subscribe(subjects: string[]) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'subscribe',
        subjects,
      }));
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

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

// Event type helpers
export function getEventIcon(eventType: string): string {
  if (eventType.startsWith('task')) return '📋';
  if (eventType.includes('weather')) return '🌤️';
  if (eventType.includes('disease') || eventType.includes('diagnosis')) return '🔬';
  if (eventType.includes('ndvi')) return '🛰️';
  if (eventType.includes('irrigation')) return '💧';
  if (eventType.includes('fertilizer')) return '🧪';
  return '📌';
}

export function getEventColor(eventType: string): string {
  if (eventType.startsWith('task')) return 'bg-blue-50 border-blue-200';
  if (eventType.includes('weather')) return 'bg-amber-50 border-amber-200';
  if (eventType.includes('disease') || eventType.includes('diagnosis')) return 'bg-red-50 border-red-200';
  if (eventType.includes('ndvi')) return 'bg-emerald-50 border-emerald-200';
  return 'bg-gray-50 border-gray-200';
}

export function formatEventType(eventType: string): string {
  const translations: Record<string, string> = {
    'task_created': 'مهمة جديدة',
    'task_assigned': 'تم تعيين مهمة',
    'task_completed': 'اكتملت مهمة',
    'task_rescheduled': 'تم إعادة جدولة',
    'image_diagnosed': 'تشخيص صورة',
    'weather_alert_issued': 'تنبيه طقس',
    'ndvi_processed': 'تحليل NDVI',
    'disease_risk_calculated': 'تقييم خطر المرض',
  };
  return translations[eventType] || eventType;
}
