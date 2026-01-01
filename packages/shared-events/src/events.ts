/**
 * SAHOOL Event Bus - Event Type Definitions
 * Central registry for all cross-service events
 */

// ============================================================================
// Base Event Interface
// ============================================================================

export interface BaseEvent {
  eventId: string;
  eventType: string;
  timestamp: Date;
  version: string;
  metadata?: Record<string, unknown>;
}

// ============================================================================
// Field Events
// ============================================================================

export interface FieldCreatedEvent extends BaseEvent {
  eventType: 'field.created';
  payload: {
    fieldId: string;
    userId: string;
    name: string;
    area: number;
    location: {
      type: 'Polygon';
      coordinates: number[][][];
    };
    cropType?: string;
  };
}

export interface FieldUpdatedEvent extends BaseEvent {
  eventType: 'field.updated';
  payload: {
    fieldId: string;
    userId: string;
    changes: {
      name?: string;
      area?: number;
      location?: {
        type: 'Polygon';
        coordinates: number[][][];
      };
      cropType?: string;
    };
  };
}

export interface FieldDeletedEvent extends BaseEvent {
  eventType: 'field.deleted';
  payload: {
    fieldId: string;
    userId: string;
    deletedAt: Date;
  };
}

// ============================================================================
// Order Events
// ============================================================================

export interface OrderPlacedEvent extends BaseEvent {
  eventType: 'order.placed';
  payload: {
    orderId: string;
    userId: string;
    items: Array<{
      productId: string;
      quantity: number;
      price: number;
    }>;
    totalAmount: number;
    currency: string;
    shippingAddress?: {
      street: string;
      city: string;
      country: string;
      postalCode: string;
    };
  };
}

export interface OrderCompletedEvent extends BaseEvent {
  eventType: 'order.completed';
  payload: {
    orderId: string;
    userId: string;
    completedAt: Date;
    totalAmount: number;
    currency: string;
  };
}

export interface OrderCancelledEvent extends BaseEvent {
  eventType: 'order.cancelled';
  payload: {
    orderId: string;
    userId: string;
    cancelledAt: Date;
    reason?: string;
  };
}

// ============================================================================
// Sensor & IoT Events
// ============================================================================

export interface SensorReadingEvent extends BaseEvent {
  eventType: 'sensor.reading';
  payload: {
    deviceId: string;
    fieldId?: string;
    sensorType: 'temperature' | 'humidity' | 'soil_moisture' | 'ph' | 'light' | 'other';
    value: number;
    unit: string;
    latitude?: number;
    longitude?: number;
    readingTime: Date;
  };
}

export interface DeviceConnectedEvent extends BaseEvent {
  eventType: 'device.connected';
  payload: {
    deviceId: string;
    deviceType: string;
    fieldId?: string;
    connectedAt: Date;
    ipAddress?: string;
  };
}

export interface DeviceDisconnectedEvent extends BaseEvent {
  eventType: 'device.disconnected';
  payload: {
    deviceId: string;
    deviceType: string;
    fieldId?: string;
    disconnectedAt: Date;
    reason?: 'timeout' | 'user_action' | 'error' | 'other';
  };
}

// ============================================================================
// User Events
// ============================================================================

export interface UserCreatedEvent extends BaseEvent {
  eventType: 'user.created';
  payload: {
    userId: string;
    email: string;
    username?: string;
    firstName?: string;
    lastName?: string;
    role: string;
    createdAt: Date;
  };
}

export interface UserUpdatedEvent extends BaseEvent {
  eventType: 'user.updated';
  payload: {
    userId: string;
    changes: {
      email?: string;
      username?: string;
      firstName?: string;
      lastName?: string;
      role?: string;
    };
    updatedAt: Date;
  };
}

// ============================================================================
// Inventory Events
// ============================================================================

export interface InventoryLowStockEvent extends BaseEvent {
  eventType: 'inventory.low_stock';
  payload: {
    productId: string;
    productName: string;
    currentStock: number;
    threshold: number;
    unit: string;
    warehouseId?: string;
  };
}

export interface InventoryMovementEvent extends BaseEvent {
  eventType: 'inventory.movement';
  payload: {
    movementId: string;
    productId: string;
    quantity: number;
    movementType: 'in' | 'out' | 'transfer' | 'adjustment';
    fromWarehouseId?: string;
    toWarehouseId?: string;
    reason?: string;
    movedAt: Date;
  };
}

// ============================================================================
// Notification Events
// ============================================================================

export interface NotificationSendEvent extends BaseEvent {
  eventType: 'notification.send';
  payload: {
    notificationId: string;
    recipientId: string;
    recipientType: 'user' | 'group' | 'all';
    channel: 'email' | 'sms' | 'push' | 'in_app';
    priority: 'low' | 'medium' | 'high' | 'urgent';
    subject: string;
    message: string;
    data?: Record<string, unknown>;
  };
}

// ============================================================================
// Event Union Types
// ============================================================================

export type FieldEvent = FieldCreatedEvent | FieldUpdatedEvent | FieldDeletedEvent;
export type OrderEvent = OrderPlacedEvent | OrderCompletedEvent | OrderCancelledEvent;
export type SensorEvent = SensorReadingEvent | DeviceConnectedEvent | DeviceDisconnectedEvent;
export type UserEvent = UserCreatedEvent | UserUpdatedEvent;
export type InventoryEvent = InventoryLowStockEvent | InventoryMovementEvent;
export type NotificationEvent = NotificationSendEvent;

export type SahoolEvent =
  | FieldEvent
  | OrderEvent
  | SensorEvent
  | UserEvent
  | InventoryEvent
  | NotificationEvent;

// ============================================================================
// Event Subject/Topic Constants
// ============================================================================

export const EventSubjects = {
  // Field events
  FIELD_CREATED: 'field.created',
  FIELD_UPDATED: 'field.updated',
  FIELD_DELETED: 'field.deleted',

  // Order events
  ORDER_PLACED: 'order.placed',
  ORDER_COMPLETED: 'order.completed',
  ORDER_CANCELLED: 'order.cancelled',

  // Sensor events
  SENSOR_READING: 'sensor.reading',
  DEVICE_CONNECTED: 'device.connected',
  DEVICE_DISCONNECTED: 'device.disconnected',

  // User events
  USER_CREATED: 'user.created',
  USER_UPDATED: 'user.updated',

  // Inventory events
  INVENTORY_LOW_STOCK: 'inventory.low_stock',
  INVENTORY_MOVEMENT: 'inventory.movement',

  // Notification events
  NOTIFICATION_SEND: 'notification.send',
} as const;

export type EventSubject = (typeof EventSubjects)[keyof typeof EventSubjects];
