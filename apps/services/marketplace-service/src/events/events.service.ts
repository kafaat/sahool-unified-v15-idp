/**
 * Events Service Stub for SAHOOL Marketplace Service
 * Provides a no-op implementation when @sahool/shared-events is not available
 *
 * TODO: Enable full NATS event bus integration when Docker build supports shared packages
 */

import { Injectable, Logger } from "@nestjs/common";

@Injectable()
export class EventsService {
  private readonly logger = new Logger(EventsService.name);

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
   * Connect to NATS (no-op stub)
   */
  async connect(): Promise<void> {
    this.logger.log("Events service running in stub mode (NATS disabled)");
  }

  /**
   * Disconnect from NATS (no-op stub)
   */
  async disconnect(): Promise<void> {
    // No-op
  }

  /**
   * Publish order placed event (no-op stub)
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
    this.logger.debug("[Stub] Order placed", {
      orderId: this.sanitizeForLog(orderData.orderId),
    });
  }

  /**
   * Publish order completed event (no-op stub)
   */
  async publishOrderCompleted(orderData: {
    orderId: string;
    userId: string;
    completedAt: Date;
    totalAmount: number;
    currency: string;
  }): Promise<void> {
    this.logger.debug("[Stub] Order completed", {
      orderId: this.sanitizeForLog(orderData.orderId),
    });
  }

  /**
   * Publish order cancelled event (no-op stub)
   */
  async publishOrderCancelled(orderData: {
    orderId: string;
    userId: string;
    cancelledAt: Date;
    reason?: string;
  }): Promise<void> {
    this.logger.debug("[Stub] Order cancelled", {
      orderId: this.sanitizeForLog(orderData.orderId),
    });
  }

  /**
   * Publish inventory low stock event (no-op stub)
   */
  async publishInventoryLowStock(inventoryData: {
    productId: string;
    productName: string;
    currentStock: number;
    threshold: number;
    unit: string;
  }): Promise<void> {
    this.logger.debug("[Stub] Low stock", {
      productId: this.sanitizeForLog(inventoryData.productId),
    });
  }
}
