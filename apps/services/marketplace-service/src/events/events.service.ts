/**
 * SAHOOL Marketplace Events Service
 * Full NATS event bus integration for marketplace events
 *
 * This service implements NATS event publishing and subscribing following
 * the patterns from @sahool/shared-events package.
 */

import { Injectable, Logger, OnModuleDestroy, OnModuleInit } from "@nestjs/common";
import {
  connect,
  NatsConnection,
  StringCodec,
  Subscription,
  ConnectionOptions,
  Events,
} from "nats";
import { v4 as uuidv4 } from "uuid";

// ============================================================================
// Event Type Definitions (mirrors @sahool/shared-events)
// ============================================================================

interface BaseEvent {
  eventId: string;
  eventType: string;
  timestamp: Date;
  version: string;
  metadata?: Record<string, unknown>;
}

interface OrderPlacedEvent extends BaseEvent {
  eventType: "sahool.marketplace.order.created";
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

interface OrderCompletedEvent extends BaseEvent {
  eventType: "sahool.marketplace.order.completed";
  payload: {
    orderId: string;
    userId: string;
    completedAt: Date;
    totalAmount: number;
    currency: string;
  };
}

interface OrderCancelledEvent extends BaseEvent {
  eventType: "sahool.marketplace.order.cancelled";
  payload: {
    orderId: string;
    userId: string;
    cancelledAt: Date;
    reason?: string;
  };
}

interface InventoryLowStockEvent extends BaseEvent {
  eventType: "sahool.marketplace.inventory.low_stock";
  payload: {
    productId: string;
    productName: string;
    currentStock: number;
    threshold: number;
    unit: string;
    warehouseId?: string;
  };
}

interface InventoryMovementEvent extends BaseEvent {
  eventType: "sahool.marketplace.inventory.movement";
  payload: {
    movementId: string;
    productId: string;
    quantity: number;
    movementType: "in" | "out" | "transfer" | "adjustment";
    fromWarehouseId?: string;
    toWarehouseId?: string;
    reason?: string;
    movedAt: Date;
  };
}

type MarketplaceEvent =
  | OrderPlacedEvent
  | OrderCompletedEvent
  | OrderCancelledEvent
  | InventoryLowStockEvent
  | InventoryMovementEvent;

// ============================================================================
// Event Subjects
// ============================================================================

const EventSubjects = {
  ORDER_CREATED: "sahool.marketplace.order.created",
  ORDER_COMPLETED: "sahool.marketplace.order.completed",
  ORDER_CANCELLED: "sahool.marketplace.order.cancelled",
  INVENTORY_LOW_STOCK: "sahool.marketplace.inventory.low_stock",
  INVENTORY_MOVEMENT: "sahool.marketplace.inventory.movement",

  /**
   * @deprecated Legacy subject kept for backward compatibility with existing consumers
   * that subscribe to "sahool.marketplace.order.placed" (including shared-events ORDER_PLACED).
   * Will be removed in v17.0.0. Consumers should migrate to ORDER_CREATED ("sahool.marketplace.order.created").
   */
  ORDER_PLACED_LEGACY: "sahool.marketplace.order.placed",
} as const;

type EventSubject = (typeof EventSubjects)[keyof typeof EventSubjects];

// ============================================================================
// Handler Types
// ============================================================================

export type EventHandler<T = MarketplaceEvent> = (
  event: T,
  subject: string,
) => Promise<void> | void;

export interface SubscribeOptions {
  queue?: string;
  onError?: (error: Error) => void;
}

// ============================================================================
// Events Service
// ============================================================================

@Injectable()
export class EventsService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(EventsService.name);
  private connection: NatsConnection | null = null;
  private readonly codec = StringCodec();
  private isConnecting = false;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private subscriptions: Subscription[] = [];
  private readonly serviceName = "marketplace-service";

  private reconnectAttempts = 0;
  private readonly MAX_RECONNECT_WAIT = 60000; // Max 60 seconds between attempts

  // Configuration
  private readonly config = {
    servers: process.env.NATS_URL || "nats://localhost:4222",
    maxReconnectAttempts: -1, // infinite reconnect
    reconnectTimeWait: 2000, // base wait between attempts
    timeout: 10000, // 10 second connection timeout
    debug: process.env.NODE_ENV !== "production",
  };

  /**
   * Auto-connect to NATS on module initialization and set up consumers
   */
  async onModuleInit(): Promise<void> {
    this.logger.log("Initializing NATS connection...");
    await this.connect();
    await this.setupEventConsumers();
  }

  /**
   * Set up event consumers for incoming events from other services
   */
  private async setupEventConsumers(): Promise<void> {
    if (!this.isConnected()) {
      this.logger.warn("Skipping event consumer setup - NATS not connected");
      return;
    }

    const queueGroup = "marketplace-service";

    // Listen for order completion events from delivery/fulfillment
    await this.subscribe(
      "sahool.delivery.completed",
      async (event) => {
        const payload = event.payload as Record<string, unknown>;
        this.logger.log(`Processing delivery.completed event`, { orderId: payload?.orderId });
        // TODO: Update order status to DELIVERED when delivery is confirmed
        // TODO: Trigger buyer notification via notification-service
        // TODO: Auto-release escrow after delivery confirmation period
      },
      { queue: queueGroup },
    );

    // Listen for inventory restock events
    await this.subscribe(
      "sahool.inventory.restocked",
      async (event) => {
        const payload = event.payload as Record<string, unknown>;
        this.logger.log(`Processing inventory.restocked event`, { productId: payload?.productId });
        // TODO: Update product stock levels in marketplace catalog
        // TODO: Re-enable listings that were auto-hidden due to zero stock
        // TODO: Notify sellers/buyers who had back-order requests
      },
      { queue: queueGroup },
    );

    // Listen for payment confirmation from payment gateway
    await this.subscribe(
      "sahool.payment.confirmed",
      async (event) => {
        const payload = event.payload as Record<string, unknown>;
        this.logger.log(`Processing payment.confirmed event`, { orderId: payload?.orderId });
        // TODO: Update order status from PENDING_PAYMENT to CONFIRMED
        // TODO: Trigger order fulfillment workflow
        // TODO: Send payment receipt notification to buyer
      },
      { queue: queueGroup },
    );

    // Listen for user verification events (KYC updates)
    await this.subscribe(
      "sahool.user.verified",
      async (event) => {
        const payload = event.payload as Record<string, unknown>;
        this.logger.log(
          `Received user verification event for user: ${payload?.userId}`,
        );
      },
      { queue: queueGroup },
    );

    this.logger.log("Event consumers set up successfully");
  }

  /**
   * Sanitize input for safe logging (prevents log injection)
   */
  private sanitizeForLog(input: string): string {
    if (typeof input !== "string") {
      return String(input);
    }
    return input
      .replace(/[\r\n]/g, "")
      .replace(/[\x00-\x1F\x7F]/g, "")
      .slice(0, 100);
  }

  /**
   * Connect to NATS server with automatic reconnection
   */
  async connect(): Promise<void> {
    // If already connected, just return
    if (this.connection && !this.connection.isClosed()) {
      return;
    }

    // If connection attempt is in progress, wait for it
    if (this.isConnecting) {
      await this.waitForConnection();
      return;
    }

    this.isConnecting = true;

    try {
      // Parse NATS URL to extract credentials (nats.js doesn't support userinfo in URLs)
      const connectionOptions: ConnectionOptions = {
        name: this.serviceName,
        maxReconnectAttempts: this.config.maxReconnectAttempts,
        reconnectTimeWait: this.config.reconnectTimeWait,
        timeout: this.config.timeout,
      };

      const natsUrl = this.config.servers;
      try {
        const parsed = new URL(natsUrl);
        if (parsed.username) {
          connectionOptions.user = decodeURIComponent(parsed.username);
          if (parsed.password) {
            connectionOptions.pass = decodeURIComponent(parsed.password);
          }
          // Rebuild URL without credentials
          connectionOptions.servers = `${parsed.protocol}//${parsed.host}`;
        } else {
          connectionOptions.servers = natsUrl;
        }
      } catch {
        // If URL parsing fails, use as-is (e.g. plain host:port)
        connectionOptions.servers = natsUrl;
      }

      this.logger.log(`Connecting to NATS server at ${connectionOptions.servers}...`);
      this.connection = await connect(connectionOptions);
      this.logger.log("Successfully connected to NATS server");
      this.reconnectAttempts = 0; // Reset backoff on successful connection

      // Setup status monitoring
      this.monitorConnectionStatus();

      this.isConnecting = false;
    } catch (error) {
      this.isConnecting = false;
      this.logger.warn(
        `Failed to connect to NATS server: ${error instanceof Error ? error.message : String(error)}`,
      );
      this.logger.log("Events service will continue in degraded mode (events will be logged but not published)");

      // Schedule reconnection attempt
      this.scheduleReconnect();
    }
  }

  /**
   * Monitor connection status and handle lifecycle events
   */
  private monitorConnectionStatus(): void {
    if (!this.connection) return;

    (async () => {
      for await (const status of this.connection!.status()) {
        switch (status.type) {
          case Events.Disconnect:
            this.logger.warn("Disconnected from NATS server");
            break;

          case Events.Reconnect:
            this.logger.log("Reconnected to NATS server");
            break;

          case Events.Update:
            this.logger.debug("NATS connection updated");
            break;

          case Events.LDM:
            this.logger.warn("NATS Lame Duck Mode activated - server draining");
            break;

          case Events.Error:
            this.logger.error(`NATS connection error: ${status.data}`);
            break;
        }
      }
    })().catch((err) => {
      this.logger.error(`Error in status monitoring: ${err}`);
    });
  }

  /**
   * Schedule a reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      return; // Already scheduled
    }

    // Exponential backoff: 2s, 4s, 8s, 16s, 32s, 60s (capped)
    const delay = Math.min(
      this.config.reconnectTimeWait * Math.pow(2, this.reconnectAttempts),
      this.MAX_RECONNECT_WAIT,
    );
    this.reconnectAttempts++;

    this.logger.debug(
      `Scheduling reconnection attempt #${this.reconnectAttempts} in ${delay}ms...`,
    );

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect().catch((err) => {
        this.logger.error(`Reconnection failed: ${err}`);
      });
    }, delay);
  }

  /**
   * Wait for ongoing connection attempt
   */
  private async waitForConnection(maxWait: number = 30000): Promise<void> {
    const startTime = Date.now();

    while (this.isConnecting && Date.now() - startTime < maxWait) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }

  /**
   * Check if connected to NATS
   */
  isConnected(): boolean {
    return this.connection !== null && !this.connection.isClosed();
  }

  /**
   * Disconnect from NATS server
   */
  async disconnect(): Promise<void> {
    // Clear reconnect timer
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    // Drain all subscriptions
    for (const sub of this.subscriptions) {
      try {
        await sub.drain();
      } catch (err) {
        this.logger.warn(`Error draining subscription: ${err}`);
      }
    }
    this.subscriptions = [];

    // Close connection
    if (this.connection && !this.connection.isClosed()) {
      this.logger.log("Disconnecting from NATS server...");
      try {
        await this.connection.drain();
        await this.connection.close();
        this.logger.log("Disconnected from NATS server");
      } catch (err) {
        this.logger.warn(`Error during disconnect: ${err}`);
      }
    }

    this.connection = null;
  }

  /**
   * Cleanup on module destroy
   */
  async onModuleDestroy(): Promise<void> {
    await this.disconnect();
  }

  // ============================================================================
  // Event Publishing
  // ============================================================================

  /**
   * Publish an event to NATS
   */
  private async publishEvent<T extends MarketplaceEvent>(
    subject: EventSubject,
    payload: T["payload"],
    options: { eventId?: string; version?: string; metadata?: Record<string, unknown> } = {},
  ): Promise<void> {
    const event: MarketplaceEvent = {
      eventId: options.eventId || uuidv4(),
      eventType: subject,
      timestamp: new Date(),
      version: options.version || "1.0",
      payload,
      metadata: {
        ...options.metadata,
        source: this.serviceName,
      },
    } as MarketplaceEvent;

    // Always log in debug mode
    if (this.config.debug) {
      this.logger.debug(`Publishing event: ${subject}`, {
        eventId: event.eventId,
        payload: JSON.stringify(payload).slice(0, 200),
      });
    }

    // If not connected, log and return (degraded mode)
    if (!this.isConnected()) {
      this.logger.warn(
        `[Degraded Mode] Event not published to NATS (not connected): ${subject}`,
      );
      return;
    }

    try {
      const data = this.codec.encode(JSON.stringify(event));
      this.connection!.publish(subject, data);
      await this.connection!.flush();

      this.logger.log(`Event published: ${subject} (${event.eventId})`);
    } catch (error) {
      this.logger.error(
        `Failed to publish event ${subject}: ${error instanceof Error ? error.message : String(error)}`,
      );
      throw error;
    }
  }

  /**
   * Publish order placed event.
   *
   * Publishes to both the current subject ("sahool.marketplace.order.created") and the
   * legacy subject ("sahool.marketplace.order.placed") for backward compatibility with
   * existing consumers (shared-events ORDER_PLACED, notification-service, billing-core, etc.).
   *
   * TODO: Remove dual-publish once all consumers have migrated to "order.created".
   * Legacy subject will be removed in v17.0.0.
   */
  async publishOrderPlaced(orderData: {
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
  }): Promise<void> {
    this.logger.log(`Publishing order.created event`, {
      orderId: this.sanitizeForLog(orderData.orderId),
    });

    // Publish to the current subject
    await this.publishEvent<OrderPlacedEvent>(
      EventSubjects.ORDER_CREATED,
      orderData,
    );

    // Also publish to the legacy subject for backward compatibility (remove in v17.0.0)
    this.logger.log(`Publishing legacy order.placed event for backward compatibility`, {
      orderId: this.sanitizeForLog(orderData.orderId),
    });
    await this.publishEvent<OrderPlacedEvent>(
      EventSubjects.ORDER_PLACED_LEGACY,
      orderData,
    );
  }

  /**
   * Publish order completed event
   *
   * TODO: This method is defined but never called in production code.
   * It should be called from the order fulfillment flow when delivery is
   * confirmed (e.g., in the delivery.completed event handler or an
   * OrderService.completeOrder() method).
   */
  async publishOrderCompleted(orderData: {
    orderId: string;
    userId: string;
    completedAt: Date;
    totalAmount: number;
    currency: string;
  }): Promise<void> {
    this.logger.log(`Publishing order.completed event`, {
      orderId: this.sanitizeForLog(orderData.orderId),
    });

    await this.publishEvent<OrderCompletedEvent>(
      EventSubjects.ORDER_COMPLETED,
      orderData,
    );
  }

  /**
   * Publish order cancelled event
   *
   * TODO: This method is defined but never called in production code.
   * It should be called from OrderService.cancelOrder() or a similar
   * cancellation handler (e.g., buyer-initiated cancel, admin cancel,
   * or auto-cancel on payment timeout).
   */
  async publishOrderCancelled(orderData: {
    orderId: string;
    userId: string;
    cancelledAt: Date;
    reason?: string;
  }): Promise<void> {
    this.logger.log(`Publishing order.cancelled event`, {
      orderId: this.sanitizeForLog(orderData.orderId),
    });

    await this.publishEvent<OrderCancelledEvent>(
      EventSubjects.ORDER_CANCELLED,
      orderData,
    );
  }

  /**
   * Publish inventory low stock event
   */
  async publishInventoryLowStock(inventoryData: {
    productId: string;
    productName: string;
    currentStock: number;
    threshold: number;
    unit: string;
    warehouseId?: string;
  }): Promise<void> {
    this.logger.log(`Publishing inventory.low_stock event`, {
      productId: this.sanitizeForLog(inventoryData.productId),
      currentStock: inventoryData.currentStock,
    });

    await this.publishEvent<InventoryLowStockEvent>(
      EventSubjects.INVENTORY_LOW_STOCK,
      inventoryData,
    );
  }

  /**
   * Publish inventory movement event
   */
  async publishInventoryMovement(movementData: {
    movementId: string;
    productId: string;
    quantity: number;
    movementType: "in" | "out" | "transfer" | "adjustment";
    fromWarehouseId?: string;
    toWarehouseId?: string;
    reason?: string;
    movedAt: Date;
  }): Promise<void> {
    this.logger.log(`Publishing inventory.movement event`, {
      movementId: this.sanitizeForLog(movementData.movementId),
      type: movementData.movementType,
    });

    await this.publishEvent<InventoryMovementEvent>(
      EventSubjects.INVENTORY_MOVEMENT,
      movementData,
    );
  }

  // ============================================================================
  // Event Subscribing
  // ============================================================================

  /**
   * Subscribe to a specific event subject
   */
  async subscribe<T extends MarketplaceEvent = MarketplaceEvent>(
    subject: EventSubject | string,
    handler: EventHandler<T>,
    options: SubscribeOptions = {},
  ): Promise<Subscription | null> {
    if (!this.isConnected()) {
      this.logger.warn(
        `Cannot subscribe to ${subject}: NATS not connected`,
      );
      return null;
    }

    try {
      const subscription = options.queue
        ? this.connection!.subscribe(subject, { queue: options.queue })
        : this.connection!.subscribe(subject);

      this.subscriptions.push(subscription);

      this.logger.log(
        `Subscribed to: ${subject}${options.queue ? ` (queue: ${options.queue})` : ""}`,
      );

      // Process messages
      (async () => {
        for await (const msg of subscription) {
          try {
            const data = this.codec.decode(msg.data);
            const event = JSON.parse(data) as T;

            if (this.config.debug) {
              this.logger.debug(`Received event on ${subject}:`, {
                eventId: event.eventId,
                eventType: event.eventType,
              });
            }

            await handler(event, subject);
          } catch (error) {
            this.logger.error(
              `Error processing message on ${subject}: ${error instanceof Error ? error.message : String(error)}`,
            );
            if (options.onError) {
              options.onError(error as Error);
            }
          }
        }
      })().catch((err) => {
        this.logger.error(`Subscription error on ${subject}: ${err}`);
        if (options.onError) {
          options.onError(err);
        }
      });

      return subscription;
    } catch (error) {
      this.logger.error(
        `Failed to subscribe to ${subject}: ${error instanceof Error ? error.message : String(error)}`,
      );
      throw error;
    }
  }

  /**
   * Subscribe to all order events (order.*)
   */
  async subscribeToOrderEvents(
    handler: EventHandler,
    options?: SubscribeOptions,
  ): Promise<Subscription | null> {
    return this.subscribe("sahool.marketplace.order.*", handler, options);
  }

  /**
   * Subscribe to all inventory events (inventory.*)
   */
  async subscribeToInventoryEvents(
    handler: EventHandler,
    options?: SubscribeOptions,
  ): Promise<Subscription | null> {
    return this.subscribe("sahool.marketplace.inventory.*", handler, options);
  }

  /**
   * Unsubscribe from a subscription
   */
  async unsubscribe(subscription: Subscription): Promise<void> {
    try {
      await subscription.drain();
      const index = this.subscriptions.indexOf(subscription);
      if (index > -1) {
        this.subscriptions.splice(index, 1);
      }
    } catch (error) {
      this.logger.error(
        `Error unsubscribing: ${error instanceof Error ? error.message : String(error)}`,
      );
    }
  }
}
