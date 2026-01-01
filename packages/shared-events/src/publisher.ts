/**
 * SAHOOL Event Bus - Event Publisher
 * Helper functions for publishing events to NATS
 */

import { StringCodec } from 'nats';
import { NatsClient } from './nats-client';
import { SahoolEvent, EventSubject } from './events';
import { v4 as uuidv4 } from 'uuid';

const codec = StringCodec();

export interface PublishOptions {
  /**
   * Override the default event ID generation
   */
  eventId?: string;

  /**
   * Event version (defaults to '1.0')
   */
  version?: string;

  /**
   * Additional metadata to attach to the event
   */
  metadata?: Record<string, unknown>;

  /**
   * Timeout for publish operation in milliseconds (default: 5000)
   */
  timeout?: number;

  /**
   * Whether to log the publish operation (default: true in development)
   */
  debug?: boolean;
}

/**
 * Base publish function - publishes any event to NATS
 */
export async function publishEvent<T extends SahoolEvent>(
  subject: EventSubject,
  payload: T['payload'],
  options: PublishOptions = {}
): Promise<void> {
  const client = NatsClient.getInstance({
    servers: process.env.NATS_URL || 'nats://localhost:4222',
  });

  const connection = client.getConnection();
  if (!connection || connection.isClosed()) {
    throw new Error('NATS connection is not available. Please connect first.');
  }

  const event: SahoolEvent = {
    eventId: options.eventId || uuidv4(),
    eventType: subject,
    timestamp: new Date(),
    version: options.version || '1.0',
    payload,
    metadata: options.metadata,
  } as SahoolEvent;

  const data = codec.encode(JSON.stringify(event));

  if (options.debug !== false && process.env.NODE_ENV !== 'production') {
    console.log(`[EventPublisher] Publishing event: ${subject}`, event);
  }

  connection.publish(subject, data);

  // Optionally wait for the publish to complete with timeout
  if (options.timeout) {
    await connection.flush();
  }
}

// ============================================================================
// Field Event Publishers
// ============================================================================

export async function publishFieldCreated(
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
  },
  options?: PublishOptions
): Promise<void> {
  await publishEvent('field.created', payload, options);
}

export async function publishFieldUpdated(
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
  },
  options?: PublishOptions
): Promise<void> {
  await publishEvent('field.updated', payload, options);
}

export async function publishFieldDeleted(
  payload: {
    fieldId: string;
    userId: string;
    deletedAt: Date;
  },
  options?: PublishOptions
): Promise<void> {
  await publishEvent('field.deleted', payload, options);
}

// ============================================================================
// Order Event Publishers
// ============================================================================

export async function publishOrderPlaced(
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
  },
  options?: PublishOptions
): Promise<void> {
  await publishEvent('order.placed', payload, options);
}

export async function publishOrderCompleted(
  payload: {
    orderId: string;
    userId: string;
    completedAt: Date;
    totalAmount: number;
    currency: string;
  },
  options?: PublishOptions
): Promise<void> {
  await publishEvent('order.completed', payload, options);
}

export async function publishOrderCancelled(
  payload: {
    orderId: string;
    userId: string;
    cancelledAt: Date;
    reason?: string;
  },
  options?: PublishOptions
): Promise<void> {
  await publishEvent('order.cancelled', payload, options);
}

// ============================================================================
// Sensor Event Publishers
// ============================================================================

export async function publishSensorReading(
  payload: {
    deviceId: string;
    fieldId?: string;
    sensorType: 'temperature' | 'humidity' | 'soil_moisture' | 'ph' | 'light' | 'other';
    value: number;
    unit: string;
    latitude?: number;
    longitude?: number;
    readingTime: Date;
  },
  options?: PublishOptions
): Promise<void> {
  await publishEvent('sensor.reading', payload, options);
}

export async function publishDeviceConnected(
  payload: {
    deviceId: string;
    deviceType: string;
    fieldId?: string;
    connectedAt: Date;
    ipAddress?: string;
  },
  options?: PublishOptions
): Promise<void> {
  await publishEvent('device.connected', payload, options);
}

export async function publishDeviceDisconnected(
  payload: {
    deviceId: string;
    deviceType: string;
    fieldId?: string;
    disconnectedAt: Date;
    reason?: 'timeout' | 'user_action' | 'error' | 'other';
  },
  options?: PublishOptions
): Promise<void> {
  await publishEvent('device.disconnected', payload, options);
}

// ============================================================================
// User Event Publishers
// ============================================================================

export async function publishUserCreated(
  payload: {
    userId: string;
    email: string;
    username?: string;
    firstName?: string;
    lastName?: string;
    role: string;
    createdAt: Date;
  },
  options?: PublishOptions
): Promise<void> {
  await publishEvent('user.created', payload, options);
}

export async function publishUserUpdated(
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
  },
  options?: PublishOptions
): Promise<void> {
  await publishEvent('user.updated', payload, options);
}

// ============================================================================
// Inventory Event Publishers
// ============================================================================

export async function publishInventoryLowStock(
  payload: {
    productId: string;
    productName: string;
    currentStock: number;
    threshold: number;
    unit: string;
    warehouseId?: string;
  },
  options?: PublishOptions
): Promise<void> {
  await publishEvent('inventory.low_stock', payload, options);
}

export async function publishInventoryMovement(
  payload: {
    movementId: string;
    productId: string;
    quantity: number;
    movementType: 'in' | 'out' | 'transfer' | 'adjustment';
    fromWarehouseId?: string;
    toWarehouseId?: string;
    reason?: string;
    movedAt: Date;
  },
  options?: PublishOptions
): Promise<void> {
  await publishEvent('inventory.movement', payload, options);
}

// ============================================================================
// Notification Event Publishers
// ============================================================================

export async function publishNotificationSend(
  payload: {
    notificationId: string;
    recipientId: string;
    recipientType: 'user' | 'group' | 'all';
    channel: 'email' | 'sms' | 'push' | 'in_app';
    priority: 'low' | 'medium' | 'high' | 'urgent';
    subject: string;
    message: string;
    data?: Record<string, unknown>;
  },
  options?: PublishOptions
): Promise<void> {
  await publishEvent('notification.send', payload, options);
}
