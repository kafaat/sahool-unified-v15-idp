/**
 * SAHOOL Event Bus - Event Subscriber
 * Helper functions for subscribing to events from NATS
 */

import { StringCodec, Subscription } from "nats";
import { NatsClient } from "./nats-client";
import { SahoolEvent, EventSubject } from "./events";

const codec = StringCodec();

export type EventHandler<T extends SahoolEvent = SahoolEvent> = (
  event: T,
  subject: string,
) => Promise<void> | void;

export interface SubscribeOptions {
  /**
   * Queue group name for load balancing across multiple instances
   */
  queue?: string;

  /**
   * Whether to log received events (default: true in development)
   */
  debug?: boolean;

  /**
   * Error handler for subscription errors
   */
  onError?: (error: Error) => void;
}

/**
 * Subscribe to a specific event subject
 */
export async function subscribe<T extends SahoolEvent = SahoolEvent>(
  subject: EventSubject | string,
  handler: EventHandler<T>,
  options: SubscribeOptions = {},
): Promise<Subscription> {
  const client = NatsClient.getInstance({
    servers: process.env.NATS_URL || "nats://localhost:4222",
  });

  const connection = client.getConnection();
  if (!connection || connection.isClosed()) {
    throw new Error("NATS connection is not available. Please connect first.");
  }

  const subscription = options.queue
    ? connection.subscribe(subject, { queue: options.queue })
    : connection.subscribe(subject);

  if (options.debug !== false && process.env.NODE_ENV !== "production") {
    console.log(
      `[EventSubscriber] Subscribed to: ${subject}${options.queue ? ` (queue: ${options.queue})` : ""}`,
    );
  }

  // Process messages
  (async () => {
    for await (const msg of subscription) {
      try {
        const data = codec.decode(msg.data);
        const event = JSON.parse(data) as T;

        if (options.debug !== false && process.env.NODE_ENV !== "production") {
          console.log(`[EventSubscriber] Received event on ${subject}:`, event);
        }

        await handler(event, subject);
      } catch (error) {
        console.error(
          `[EventSubscriber] Error processing message on ${subject}:`,
          error,
        );
        if (options.onError) {
          options.onError(error as Error);
        }
      }
    }
  })().catch((err) => {
    console.error(`[EventSubscriber] Subscription error on ${subject}:`, err);
    if (options.onError) {
      options.onError(err);
    }
  });

  return subscription;
}

/**
 * Subscribe to multiple subjects using a wildcard pattern
 * Examples:
 * - 'field.*' - all field events
 * - 'order.*' - all order events
 * - '*.created' - all creation events
 * - '>' - all events
 */
export async function subscribePattern<T extends SahoolEvent = SahoolEvent>(
  pattern: string,
  handler: EventHandler<T>,
  options: SubscribeOptions = {},
): Promise<Subscription> {
  return subscribe(pattern, handler, options);
}

/**
 * Subscribe to all events
 */
export async function subscribeAll(
  handler: EventHandler<SahoolEvent>,
  options: SubscribeOptions = {},
): Promise<Subscription> {
  return subscribe(">", handler, options);
}

// ============================================================================
// Convenience Subscriber Functions for Specific Events
// ============================================================================

/**
 * Subscribe to all field events
 */
export async function subscribeToFieldEvents(
  handler: EventHandler,
  options?: SubscribeOptions,
): Promise<Subscription> {
  return subscribePattern("field.*", handler, options);
}

/**
 * Subscribe to all order events
 */
export async function subscribeToOrderEvents(
  handler: EventHandler,
  options?: SubscribeOptions,
): Promise<Subscription> {
  return subscribePattern("order.*", handler, options);
}

/**
 * Subscribe to all sensor events
 */
export async function subscribeToSensorEvents(
  handler: EventHandler,
  options?: SubscribeOptions,
): Promise<Subscription> {
  return subscribePattern("sensor.*", handler, options);
}

/**
 * Subscribe to all device events
 */
export async function subscribeToDeviceEvents(
  handler: EventHandler,
  options?: SubscribeOptions,
): Promise<Subscription> {
  return subscribePattern("device.*", handler, options);
}

/**
 * Subscribe to all user events
 */
export async function subscribeToUserEvents(
  handler: EventHandler,
  options?: SubscribeOptions,
): Promise<Subscription> {
  return subscribePattern("user.*", handler, options);
}

/**
 * Subscribe to all inventory events
 */
export async function subscribeToInventoryEvents(
  handler: EventHandler,
  options?: SubscribeOptions,
): Promise<Subscription> {
  return subscribePattern("inventory.*", handler, options);
}

/**
 * Subscribe to all notification events
 */
export async function subscribeToNotificationEvents(
  handler: EventHandler,
  options?: SubscribeOptions,
): Promise<Subscription> {
  return subscribePattern("notification.*", handler, options);
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Unsubscribe from a subscription
 */
export async function unsubscribe(subscription: Subscription): Promise<void> {
  await subscription.drain();
}

/**
 * Create a logging handler for debugging
 */
export function createLoggingHandler(prefix: string = "[Event]"): EventHandler {
  return (event: SahoolEvent, subject: string) => {
    console.log(`${prefix} [${subject}]`, {
      eventId: event.eventId,
      eventType: event.eventType,
      timestamp: event.timestamp,
      payload: event.payload,
      metadata: event.metadata,
    });
  };
}
