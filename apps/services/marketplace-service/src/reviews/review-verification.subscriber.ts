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
 * This subscriber listens to `sahool.delivery.completed` on the NATS
 * event bus and back-fills `verified=true` on any review(s) attached to
 * the just-delivered order. Idempotent by design — re-delivery events
 * for the same orderId are no-ops.
 *
 * ─────────────────────────────────────────────────────────────────────────
 * SECURITY
 * ─────────────────────────────────────────────────────────────────────────
 * All Prisma writes are tenant-scoped via `updateMany({where: {orderId,
 * tenantId}})` — the `tenantId` comes from the event payload (stamped by
 * the delivery service under its own authz). Without the filter, a
 * malicious delivery event could mutate reviews across tenants.
 *
 * The subscriber is registered in a NestJS queue group
 * (`marketplace-service-review-verifier`) so multiple marketplace
 * replicas don't double-process the same event.
 */

import { Injectable, Logger, OnModuleInit } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { EventsService } from "../events/events.service";

const DELIVERY_COMPLETED_SUBJECT = "sahool.delivery.completed";
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
        `NATS not connected — review.verified back-fill subscriber disabled. ` +
          `Reviews created before their order was DELIVERED will remain verified=false ` +
          `until this marketplace replica reconnects.`,
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

  private async handleDeliveryCompleted(event: any): Promise<void> {
    const payload = (event?.payload ?? {}) as Record<string, unknown>;
    const orderId = typeof payload.orderId === "string" ? payload.orderId : undefined;
    const tenantId =
      typeof payload.tenantId === "string" ? payload.tenantId : undefined;

    if (!orderId || !tenantId) {
      // Missing routing — drop the event rather than fan it out across
      // tenants. Matches the pattern used by agro-rules worker.
      this.logger.warn(
        `delivery.completed: missing routing (orderId=${orderId}, ` +
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
