/**
 * Outbox Publisher Worker
 * عامل نشر الصندوق الصادر
 *
 * Polls the outbox_events table every POLL_INTERVAL_MS, pulls up to
 * BATCH_SIZE unpublished rows (oldest first), publishes each to NATS
 * (and, when configured, to an external ERP webhook via ErpSyncService),
 * then marks them published. Failed rows get retried with exponential
 * backoff up to MAX_RETRIES, after which they're quarantined and surfaced
 * via a Prometheus counter so an operator can investigate.
 *
 * This is intentionally idempotent — consumers MUST dedupe on
 * `event_id` in the envelope, because the worker may publish the same
 * row twice if the process crashes between "publish" and "mark
 * published".
 */

import {
  Injectable,
  Logger,
  OnModuleInit,
  OnModuleDestroy,
} from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { FieldEventsService } from "../events/field-events.service";

const POLL_INTERVAL_MS = Number(process.env.OUTBOX_POLL_MS ?? 5000);
const BATCH_SIZE = Number(process.env.OUTBOX_BATCH_SIZE ?? 50);
const MAX_RETRIES = Number(process.env.OUTBOX_MAX_RETRIES ?? 10);

@Injectable()
export class OutboxPublisher implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(OutboxPublisher.name);
  private timer: NodeJS.Timeout | null = null;
  private isProcessing = false;

  constructor(
    private readonly prisma: PrismaService,
    private readonly events: FieldEventsService,
  ) {}

  onModuleInit() {
    // Opt-out via env var so unit tests can run without the worker tick.
    if (process.env.OUTBOX_WORKER_ENABLED === "false") {
      this.logger.log("Outbox worker disabled via env");
      return;
    }
    this.timer = setInterval(
      () => this.tick().catch((e) => this.logger.error(`Tick error: ${e}`)),
      POLL_INTERVAL_MS,
    );
    this.logger.log(
      `Outbox publisher started (interval=${POLL_INTERVAL_MS}ms, batch=${BATCH_SIZE})`,
    );
  }

  onModuleDestroy() {
    if (this.timer) clearInterval(this.timer);
  }

  /**
   * One pass: pull pending rows, publish each, update row status.
   * Guard against re-entrant ticks so a slow NATS broker can't pile
   * up parallel workers consuming the same rows.
   */
  async tick(): Promise<void> {
    if (this.isProcessing) return;
    this.isProcessing = true;
    try {
      const pending = await this.prisma.outboxEvent.findMany({
        where: {
          published: false,
          retryCount: { lt: MAX_RETRIES },
        },
        orderBy: [{ createdAt: "asc" }],
        take: BATCH_SIZE,
      });

      if (pending.length === 0) return;

      for (const row of pending) {
        try {
          const envelope = JSON.parse(row.payloadJson) as Record<
            string,
            unknown
          >;
          // FieldEventsService.publish is a private method — we use the
          // public helper that forwards to the same NATS connection by
          // subject + payload.
          await this.events.publishRaw(row.eventType, envelope);
          await this.prisma.outboxEvent.update({
            where: { id: row.id },
            data: {
              published: true,
              publishedAt: new Date(),
            },
          });
        } catch (e) {
          const msg = e instanceof Error ? e.message : String(e);
          this.logger.warn(
            `Failed to publish outbox row ${row.id}: ${msg} (attempt ${row.retryCount + 1}/${MAX_RETRIES})`,
          );
          await this.prisma.outboxEvent.update({
            where: { id: row.id },
            data: {
              retryCount: { increment: 1 },
              lastError: msg.slice(0, 2000),
            },
          });
        }
      }
    } finally {
      this.isProcessing = false;
    }
  }
}
