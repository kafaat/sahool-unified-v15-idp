/**
 * Order Delivery Subscriber
 * مشترك إكمال تسليم الطلب
 *
 * ─────────────────────────────────────────────────────────────────────────
 * PURPOSE
 * ─────────────────────────────────────────────────────────────────────────
 * Bridges the delivery-service signal (`sahool.delivery.completed`) to the
 * marketplace's own event (`sahool.marketplace.order.delivered`):
 *
 *   delivery-service                marketplace-service
 *   ────────────────                ───────────────────
 *   sahool.delivery.completed  ──▶  (this subscriber)
 *                                    1. UPDATE orders SET status='DELIVERED'
 *                                       WHERE id=$orderId AND tenantId=$tenantId
 *                                       AND status<>'DELIVERED'
 *                                    2. publish sahool.marketplace.order.delivered
 *                                   └──▶ review-verification.subscriber
 *                                   └──▶ (future: loyalty, returns-window, etc.)
 *
 * Downstream consumers MUST subscribe to
 * `sahool.marketplace.order.delivered` — not to `sahool.delivery.completed`
 * — because this subscriber owns the single place in the code base where
 * Order.status transitions to DELIVERED. Consumers that read Order.status
 * from `delivery.completed` are racing the DB write.
 *
 * ─────────────────────────────────────────────────────────────────────────
 * IDEMPOTENCY
 * ─────────────────────────────────────────────────────────────────────────
 * NATS re-delivers on consumer error (and on stream replay). The Prisma
 * `updateMany` is gated on `status: { not: DELIVERED }`, so a replayed
 * delivery.completed for an already-DELIVERED order matches zero rows —
 * we skip the re-publish and exit silently. First delivery wins; replays
 * are no-ops.
 *
 * ─────────────────────────────────────────────────────────────────────────
 * SECURITY
 * ─────────────────────────────────────────────────────────────────────────
 * `updateMany` filter is `{ id: orderId, tenantId }` — the tenantId
 * comes from the delivery-service's event payload (stamped under its
 * own authz). A malicious or misrouted event with a mismatched
 * (orderId, tenantId) pair matches zero rows and is a no-op; it can
 * never touch another tenant's orders.
 */

import { Injectable, Logger, OnModuleInit } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { EventsService } from "../events/events.service";

const DELIVERY_COMPLETED_SUBJECT = "sahool.delivery.completed";
const QUEUE_GROUP = "marketplace-service-order-delivery";

@Injectable()
export class OrderDeliverySubscriber implements OnModuleInit {
  private readonly logger = new Logger(OrderDeliverySubscriber.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly events: EventsService,
  ) {}

  async onModuleInit(): Promise<void> {
    // Defer until EventsService has connected (EventsService.onModuleInit
    // runs `connect()` but the NATS handshake isn't synchronous).
    setTimeout(() => {
      this.registerSubscription().catch((err) => {
        this.logger.warn(
          `Failed to subscribe to ${DELIVERY_COMPLETED_SUBJECT}: ${
            err instanceof Error ? err.message : String(err)
          }`,
        );
      });
    }, 500);
  }

  private async registerSubscription(): Promise<void> {
    if (!this.events.isConnected()) {
      this.logger.warn(
        `NATS not connected — delivery.completed subscriber disabled. ` +
          `Order.status will stay on its pre-delivery value until this ` +
          `marketplace replica reconnects.`,
      );
      return;
    }

    await this.events.subscribe(
      DELIVERY_COMPLETED_SUBJECT,
      async (event) => {
        await this.handleDeliveryCompleted(event);
      },
      { queue: QUEUE_GROUP },
    );
    this.logger.log(
      `Subscribed to ${DELIVERY_COMPLETED_SUBJECT} (queue=${QUEUE_GROUP})`,
    );
  }

  private async handleDeliveryCompleted(event: unknown): Promise<void> {
    const payload =
      ((event as { payload?: unknown })?.payload ?? {}) as Record<string, unknown>;
    const orderId = typeof payload.orderId === "string" ? payload.orderId : undefined;
    const tenantId =
      typeof payload.tenantId === "string" ? payload.tenantId : undefined;
    const buyerId =
      typeof payload.buyerId === "string"
        ? payload.buyerId
        : typeof payload.userId === "string"
          ? payload.userId
          : undefined;
    const deliveredAtRaw =
      typeof payload.deliveredAt === "string" ||
      typeof payload.deliveredAt === "number"
        ? payload.deliveredAt
        : undefined;
    const deliveredAt = deliveredAtRaw ? new Date(deliveredAtRaw) : new Date();

    if (!orderId || !tenantId) {
      // Missing routing — drop the event rather than fan it out across
      // tenants. Matches the pattern used by agro-rules worker.
      this.logger.warn(
        `delivery.completed: missing routing (orderId=${orderId}, ` +
          `tenantId=${tenantId}) — skipping DELIVERED transition`,
      );
      return;
    }

    try {
      const result = await this.prisma.order.updateMany({
        where: {
          id: orderId,
          tenantId,
          // Idempotency: a re-delivered event finds an already-DELIVERED
          // order and matches zero rows (count === 0) — we skip the
          // downstream publish in that case.
          status: { not: "DELIVERED" },
        },
        data: {
          status: "DELIVERED",
          deliveryDate: deliveredAt,
        },
      });

      if (result.count === 0) {
        // Either the order doesn't exist, belongs to another tenant,
        // or is already DELIVERED (replay). All three are safe no-ops.
        this.logger.debug(
          `delivery.completed for order=${orderId} tenant=${tenantId} — ` +
            `no status transition (not found, cross-tenant, or already DELIVERED)`,
        );
        return;
      }

      // Resolve buyerId from DB when the delivery event didn't carry it
      // — downstream consumers (loyalty, notifications) need it.
      let resolvedBuyerId: string = buyerId ?? "";
      if (!resolvedBuyerId) {
        const row = await this.prisma.order.findFirst({
          where: { id: orderId, tenantId },
          select: { buyerId: true },
        });
        resolvedBuyerId = row?.buyerId ?? "";
      }

      this.logger.log(
        `Order ${orderId} (tenant=${tenantId}) → DELIVERED; ` +
          `publishing sahool.marketplace.order.delivered`,
      );

      await this.events.publishOrderDelivered({
        tenantId,
        orderId,
        buyerId: resolvedBuyerId,
        deliveredAt,
      });
    } catch (err) {
      this.logger.error(
        `Failed to complete delivery for order=${orderId}: ${
          err instanceof Error ? err.message : String(err)
        }`,
      );
      // Do NOT rethrow: NATS would redeliver and we'd loop on a persistent
      // DB error. A separate reconciliation job can pick up any misses.
    }
  }
}
