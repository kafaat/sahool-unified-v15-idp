/**
 * Review Verification Subscriber
 * مشترك تأكيد تقييمات المُنتجات بعد تسليم الطلب
 *
 * ─────────────────────────────────────────────────────────────────────────
 * PURPOSE
 * ─────────────────────────────────────────────────────────────────────────
 * `ProductReview.verified` used to be set once, at review creation, from
 * the order's status at that moment (`verified = order.status ===
 * "DELIVERED"`). If a buyer wrote their review BEFORE the order was
 * actually delivered (very common — the review widget often appears on
 * the order confirmation page), the review stayed `verified=false`
 * forever, even after delivery completed.
 *
 * This subscriber listens to `sahool.marketplace.order.delivered` on the
 * NATS event bus and back-fills `verified=true` on any review(s)
 * attached to the just-delivered order. Idempotent by design —
 * re-publishes for the same orderId are no-ops.
 *
 * Why `sahool.marketplace.order.delivered` and NOT
 * `sahool.delivery.completed`? The latter fires from the delivery
 * service BEFORE marketplace has reconciled its own Order row to
 * status=DELIVERED. If we verified reviews on that upstream event we
 * could race the Order update and flip reviews while
 * `order.status !== 'DELIVERED'` is still true in the DB. Instead,
 * `OrderDeliverySubscriber` (src/orders/order-delivery.subscriber.ts)
 * owns the DB write, and re-publishes
 * `sahool.marketplace.order.delivered` AFTER the write commits — so
 * by the time this subscriber fires, the order is observably
 * DELIVERED (2026-04-21 audit, item #15).
 *
 * ─────────────────────────────────────────────────────────────────────────
 * SECURITY
 * ─────────────────────────────────────────────────────────────────────────
 * All Prisma writes are tenant-scoped via `updateMany({where: {orderId,
 * tenantId}})` — the `tenantId` comes from the event payload (stamped
 * by marketplace-service's own `publishOrderDelivered`, which inherits
 * the tenantId from the tenant-validated Order row). A malicious or
 * misrouted event can never mutate reviews across tenants.
 *
 * The subscriber is registered in a NestJS queue group
 * (`marketplace-service-review-verifier`) so multiple marketplace
 * replicas don't double-process the same event.
 */

import { Injectable, Logger, OnModuleInit } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { EventsService } from "../events/events.service";

const ORDER_DELIVERED_SUBJECT = "sahool.marketplace.order.delivered";
const QUEUE_GROUP = "marketplace-service-review-verifier";

@Injectable()
export class ReviewVerificationSubscriber implements OnModuleInit {
  private readonly logger = new Logger(ReviewVerificationSubscriber.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly events: EventsService,
  ) {}

  async onModuleInit(): Promise<void> {
    // Defer the actual subscribe call until the next tick so that
    // EventsService has had a chance to connect. If the connection is
    // still not up we log and give up — `EventsService.subscribe()`
    // itself throws in that case.
    setTimeout(() => {
      this.registerSubscription().catch((err) => {
        this.logger.warn(
          `Failed to subscribe to ${ORDER_DELIVERED_SUBJECT}: ${
            err instanceof Error ? err.message : String(err)
          }`,
        );
      });
    }, 500);
  }

  private async registerSubscription(): Promise<void> {
    if (!this.events.isConnected()) {
      this.logger.warn(
        `NATS not connected — review.verified back-fill subscriber disabled. ` +
          `Reviews created before their order was DELIVERED will remain verified=false ` +
          `until this marketplace replica reconnects.`,
      );
      return;
    }

    await this.events.subscribe(
      ORDER_DELIVERED_SUBJECT,
      async (event) => {
        await this.handleOrderDelivered(event);
      },
      { queue: QUEUE_GROUP },
    );
    this.logger.log(
      `Subscribed to ${ORDER_DELIVERED_SUBJECT} (queue=${QUEUE_GROUP})`,
    );
  }

  private async handleOrderDelivered(event: unknown): Promise<void> {
    const payload =
      ((event as { payload?: unknown })?.payload ?? {}) as Record<string, unknown>;
    const orderId = typeof payload.orderId === "string" ? payload.orderId : undefined;
    const tenantId =
      typeof payload.tenantId === "string" ? payload.tenantId : undefined;

    if (!orderId || !tenantId) {
      // Missing routing — drop the event rather than fan it out across
      // tenants. Matches the pattern used by agro-rules worker.
      this.logger.warn(
        `order.delivered: missing routing (orderId=${orderId}, ` +
          `tenantId=${tenantId}) — skipping review verification back-fill`,
      );
      return;
    }

    try {
      const result = await this.prisma.productReview.updateMany({
        where: {
          orderId,
          tenantId,
          verified: false,
        },
        data: { verified: true },
      });

      if (result.count > 0) {
        this.logger.log(
          `Back-filled verified=true on ${result.count} review(s) for ` +
            `order=${orderId} tenant=${tenantId}`,
        );
      }
      // Idempotency: a re-delivered event finds zero unverified reviews
      // (updateMany.count === 0) and is a silent no-op. That's fine.
    } catch (err) {
      this.logger.error(
        `Failed to back-fill review verification for order=${orderId}: ${
          err instanceof Error ? err.message : String(err)
        }`,
      );
      // Do NOT rethrow: NATS would redeliver and we'd retry forever on a
      // persistent DB error. The next delivery event (or a separate
      // reconciliation job) can pick up any misses.
    }
  }
}
