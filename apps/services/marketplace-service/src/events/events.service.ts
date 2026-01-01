/**
 * Events Service for SAHOOL Marketplace Service
 * Manages NATS connection and provides event logging
 */

import { Injectable, Logger } from '@nestjs/common';
import {
  initializeNatsClient,
  NatsClient,
  subscribeAll,
  createLoggingHandler,
  publishOrderPlaced,
  publishOrderCompleted,
  publishOrderCancelled,
  publishInventoryLowStock,
} from '@sahool/shared-events';
import { Subscription } from 'nats';

@Injectable()
export class EventsService {
  private readonly logger = new Logger(EventsService.name);
  private loggingSubscription: Subscription | null = null;

  /**
   * Connect to NATS and setup event logging
   */
  async connect(): Promise<void> {
    try {
      this.logger.log('Connecting to NATS event bus...');

      await initializeNatsClient({
        servers: process.env.NATS_URL || 'nats://localhost:4222',
        name: 'marketplace-service',
        debug: process.env.NODE_ENV !== 'production',
      });

      this.logger.log('Successfully connected to NATS event bus');

      // Subscribe to all events for logging (in development)
      if (process.env.NODE_ENV !== 'production') {
        await this.setupEventLogging();
      }
    } catch (error) {
      this.logger.error('Failed to connect to NATS event bus:', error);
      // Don't throw - allow service to start even if NATS is unavailable
    }
  }

  /**
   * Setup event logging for all events
   */
  private async setupEventLogging(): Promise<void> {
    try {
      this.logger.log('Setting up event logging subscriber...');

      this.loggingSubscription = await subscribeAll(
        createLoggingHandler('[Marketplace Event]')
      );

      this.logger.log('Event logging subscriber active');
    } catch (error) {
      this.logger.error('Failed to setup event logging:', error);
    }
  }

  /**
   * Disconnect from NATS
   */
  async disconnect(): Promise<void> {
    try {
      if (this.loggingSubscription) {
        await this.loggingSubscription.drain();
      }

      const client = NatsClient.getInstance({
        servers: process.env.NATS_URL || 'nats://localhost:4222',
      });

      await client.disconnect();
      this.logger.log('Disconnected from NATS event bus');
    } catch (error) {
      this.logger.error('Error disconnecting from NATS:', error);
    }
  }

  /**
   * Publish order placed event
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
  }): Promise<void> {
    try {
      await publishOrderPlaced(orderData);
      this.logger.debug(`Published order.placed event for order ${orderData.orderId}`);
    } catch (error) {
      this.logger.error('Failed to publish order.placed event:', error);
    }
  }

  /**
   * Publish order completed event
   */
  async publishOrderCompleted(orderData: {
    orderId: string;
    userId: string;
    completedAt: Date;
    totalAmount: number;
    currency: string;
  }): Promise<void> {
    try {
      await publishOrderCompleted(orderData);
      this.logger.debug(`Published order.completed event for order ${orderData.orderId}`);
    } catch (error) {
      this.logger.error('Failed to publish order.completed event:', error);
    }
  }

  /**
   * Publish order cancelled event
   */
  async publishOrderCancelled(orderData: {
    orderId: string;
    userId: string;
    cancelledAt: Date;
    reason?: string;
  }): Promise<void> {
    try {
      await publishOrderCancelled(orderData);
      this.logger.debug(`Published order.cancelled event for order ${orderData.orderId}`);
    } catch (error) {
      this.logger.error('Failed to publish order.cancelled event:', error);
    }
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
  }): Promise<void> {
    try {
      await publishInventoryLowStock(inventoryData);
      this.logger.debug(
        `Published inventory.low_stock event for product ${inventoryData.productId}`
      );
    } catch (error) {
      this.logger.error('Failed to publish inventory.low_stock event:', error);
    }
  }
}
