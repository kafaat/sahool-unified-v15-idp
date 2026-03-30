/**
 * SAHOOL WebSocket Client
 * خدمة الأحداث المباشرة - متوافق مع الـ kernel المسترجع
 */

import { logger } from '../logger';

// Default WebSocket URL for CI/build environments
const DEFAULT_WS_URL = 'ws://localhost:8081';

// Determine WebSocket URL from environment variable
const getWebSocketUrl = (): string => {
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL;

  if (!wsUrl) {
    // Use default URL in development or CI/build environments
    // In production with proper deployment, NEXT_PUBLIC_WS_URL should always be set
    if (process.env.NODE_ENV === 'development' || typeof window === 'undefined') {
      logger.warn(`NEXT_PUBLIC_WS_URL not set, using default ${DEFAULT_WS_URL}`);
      return DEFAULT_WS_URL;
    }
    // In browser production environment without WS_URL, use default but warn
    logger.warn(`NEXT_PUBLIC_WS_URL not configured, WebSocket features may not work`);
    return DEFAULT_WS_URL;
  }

  return wsUrl;
};

const WS_URL = getWebSocketUrl();

/**
 * All event category patterns supported by ws-gateway
 * جميع أنماط فئات الأحداث المدعومة
 */
export const ALL_EVENT_SUBSCRIPTIONS = [
  'tasks.*',
  'task.*',
  'diagnosis.*',
  'weather.*',
  'ndvi.*',
  'field.*',
  'inventory.*',
  'crop.*',
  'spray.*',
  'chat.*',
  'iot.*',
  'system.*',
  'user.*',
  'satellite.*',
] as const;

/**
 * Event category derived from event_type (e.g., 'field.updated' -> 'field')
 */
export type EventCategory =
  | 'field'
  | 'weather'
  | 'satellite'
  | 'ndvi'
  | 'inventory'
  | 'crop'
  | 'spray'
  | 'chat'
  | 'task'
  | 'tasks'
  | 'iot'
  | 'system'
  | 'user'
  | 'diagnosis';

export interface TimelineEvent {
  event_id: string;
  event_type: string;
  aggregate_id: string;
  tenant_id: string;
  timestamp: string;
  payload: Record<string, unknown>;
}

export interface WSMessage {
  type: 'event' | 'ping' | 'pong' | 'subscribed' | 'error';
  data?: TimelineEvent;
  message?: string;
}

type EventHandler = (event: TimelineEvent) => void;
type ConnectionHandler = (connected: boolean) => void;

/**
 * Extract the event category from a full event_type string.
 * e.g., 'crop.disease.detected' -> 'crop'
 */
export function getEventCategory(eventType: string): EventCategory | string {
  // Support both dot notation (field.created) and underscore (task_created)
  if (eventType.includes('.')) {
    return eventType.split('.')[0] ?? eventType;
  }
  return eventType.split('_')[0] ?? eventType;
}

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
  private authToken: string | null = null;
  private shouldReconnect = true;
  private subscribedRooms: Set<string> = new Set();

  constructor(url: string) {
    this.url = url;
  }

  connect(
    subscriptions: string[] = [...ALL_EVENT_SUBSCRIPTIONS],
    token?: string
  ) {
    if (typeof window === 'undefined') return; // SSR check
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.shouldReconnect = true;
    this.subscriptions = subscriptions;

    // Use explicit token param if provided; otherwise rely on httpOnly cookies
    // (WebSocket handshakes send cookies automatically when same-origin).
    const authToken = token ?? null;
    this.authToken = authToken;

    try {
      let wsUrl = `${this.url}/events`;
      if (authToken) {
        const separator = wsUrl.includes('?') ? '&' : '?';
        wsUrl = `${wsUrl}${separator}token=${encodeURIComponent(authToken)}`;
      }
      // When no explicit token, cookies are sent automatically by the browser
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        logger.log('🔌 WebSocket connected');
        this.reconnectAttempts = 0;
        this.notifyConnectionHandlers(true);
        this.subscribe(subscriptions);

        // Rejoin rooms on reconnect
        for (const roomId of this.subscribedRooms) {
          this.ws?.send(
            JSON.stringify({ type: 'join_room', room: roomId })
          );
        }
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
          logger.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = (event) => {
        logger.log('🔌 WebSocket disconnected', event.code);
        this.notifyConnectionHandlers(false);
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        logger.error('WebSocket error:', error);
      };
    } catch (error) {
      logger.error('Failed to create WebSocket:', error);
      this.attemptReconnect();
    }
  }

  private subscribe(subjects: string[]) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'subscribe',
          topics: subjects,
        })
      );
    }
  }

  private attemptReconnect() {
    // Don't reconnect if explicitly disconnected
    if (!this.shouldReconnect) {
      return;
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      logger.log('Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    logger.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

    // Clear any existing reconnect timeout
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    this.reconnectTimeout = setTimeout(() => {
      this.reconnectTimeout = null;
      this.connect(this.subscriptions, this.authToken ?? undefined);
    }, delay);
  }

  /**
   * Subscribe to a chat/field room for scoped events
   * الاشتراك في غرفة محادثة/حقل لأحداث محددة
   */
  subscribeToRoom(roomId: string) {
    if (this.subscribedRooms.has(roomId)) return;
    this.subscribedRooms.add(roomId);

    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'join_room',
          room: roomId,
        })
      );
      logger.log(`Joined room: ${roomId}`);
    }
  }

  /**
   * Unsubscribe from a room
   * إلغاء الاشتراك من غرفة
   */
  unsubscribeFromRoom(roomId: string) {
    if (!this.subscribedRooms.has(roomId)) return;
    this.subscribedRooms.delete(roomId);

    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'leave_room',
          room: roomId,
        })
      );
      logger.log(`Left room: ${roomId}`);
    }
  }

  /**
   * Get currently subscribed rooms
   */
  get rooms(): ReadonlySet<string> {
    return this.subscribedRooms;
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
    this.subscribedRooms.clear();
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
  const category = getEventCategory(eventType);
  switch (category) {
    case 'task':
    case 'tasks':
      return '📋';
    case 'weather':
      return '🌤️';
    case 'diagnosis':
    case 'crop':
      return '🔬';
    case 'ndvi':
    case 'satellite':
      return '🛰️';
    case 'field':
      return '🌾';
    case 'inventory':
      return '📦';
    case 'spray':
    case 'irrigation':
      return '💧';
    case 'fertilizer':
      return '🧪';
    case 'chat':
      return '💬';
    case 'iot':
      return '📡';
    case 'system':
      return '⚙️';
    case 'user':
      return '👤';
    default:
      return '📌';
  }
}

export function getEventColor(eventType: string): string {
  const category = getEventCategory(eventType);
  switch (category) {
    case 'task':
    case 'tasks':
      return 'bg-blue-50 border-blue-200';
    case 'weather':
      return 'bg-amber-50 border-amber-200';
    case 'diagnosis':
    case 'crop':
      return 'bg-red-50 border-red-200';
    case 'ndvi':
    case 'satellite':
      return 'bg-emerald-50 border-emerald-200';
    case 'field':
      return 'bg-green-50 border-green-200';
    case 'inventory':
      return 'bg-purple-50 border-purple-200';
    case 'spray':
    case 'irrigation':
      return 'bg-cyan-50 border-cyan-200';
    case 'fertilizer':
      return 'bg-lime-50 border-lime-200';
    case 'chat':
      return 'bg-indigo-50 border-indigo-200';
    case 'iot':
      return 'bg-orange-50 border-orange-200';
    case 'system':
      return 'bg-slate-50 border-slate-200';
    case 'user':
      return 'bg-teal-50 border-teal-200';
    default:
      return 'bg-gray-50 border-gray-200';
  }
}

/**
 * Bilingual event type labels matching ws-gateway EventType enum
 * تسميات ثنائية اللغة لأنواع الأحداث
 */
export function formatEventType(eventType: string): string {
  const translations: Record<string, string> = {
    // Field events
    'field.updated': 'تم تحديث بيانات الحقل',
    'field.created': 'تم إنشاء حقل جديد',
    'field.deleted': 'تم حذف الحقل',
    // Weather events
    'weather.alert': 'تنبيه طقس مهم',
    'weather.updated': 'تم تحديث بيانات الطقس',
    // Satellite events
    'satellite.ready': 'صور الأقمار الصناعية جاهزة',
    'satellite.processing': 'جاري معالجة صور الأقمار الصناعية',
    'satellite.failed': 'فشلت معالجة صور الأقمار الصناعية',
    // NDVI events
    'ndvi.updated': 'تم تحديث بيانات NDVI',
    'ndvi.analysis.ready': 'تحليل NDVI جاهز',
    // Inventory events
    'inventory.low_stock': 'مخزون منخفض',
    'inventory.out_of_stock': 'نفاد المخزون',
    'inventory.updated': 'تم تحديث المخزون',
    // Crop health events
    'crop.disease.detected': 'تم اكتشاف مرض في المحصول',
    'crop.pest.detected': 'تم اكتشاف آفة في المحصول',
    'crop.health.alert': 'تنبيه صحة المحصول',
    // Spray events
    'spray.window.optimal': 'وقت الرش المثالي',
    'spray.window.warning': 'تحذير وقت الرش',
    'spray.scheduled': 'تم جدولة الرش',
    // Chat events
    'chat.message': 'رسالة جديدة',
    'chat.typing': 'يكتب...',
    'chat.read': 'تمت القراءة',
    // Task events
    'task.created': 'تم إنشاء مهمة جديدة',
    'task.updated': 'تم تحديث المهمة',
    'task.completed': 'تمت المهمة',
    'task.overdue': 'مهمة متأخرة',
    // IoT events
    'iot.reading': 'قراءة من المستشعر',
    'iot.alert': 'تنبيه من المستشعر',
    'iot.offline': 'المستشعر غير متصل',
    // System events
    'system.notification': 'إشعار النظام',
    'system.sync_required': 'مطلوب مزامنة',
    // User events
    'user.online': 'المستخدم متصل',
    'user.offline': 'المستخدم غير متصل',
    // Legacy keys (backward compat)
    task_created: 'مهمة جديدة',
    task_assigned: 'تم تعيين مهمة',
    task_completed: 'اكتملت مهمة',
    task_rescheduled: 'تم إعادة جدولة',
    image_diagnosed: 'تشخيص صورة',
    weather_alert_issued: 'تنبيه طقس',
    ndvi_processed: 'تحليل NDVI',
    disease_risk_calculated: 'تقييم خطر المرض',
  };
  return translations[eventType] || eventType;
}
