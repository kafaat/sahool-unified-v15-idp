/**
 * Outbox Service
 * خدمة الصندوق الصادر - نمط المعاملات الموثوق
 *
 * Implements the transactional outbox pattern. Callers inside a Prisma
 * $transaction block call `writeInTransaction(tx, ...)` to append an
 * event row to the outbox inside the same DB transaction as the business
 * data change. A separate poll-and-publish worker (OutboxPublisher) wakes
 * up every N seconds, pulls unpublished rows, publishes them to NATS
 * (and optionally to external ERP webhooks), then marks them published.
 *
 * Guarantees:
 *   * At-least-once delivery — events are NEVER lost if NATS is down at
 *     commit time, because the DB write and the outbox row share the
 *     same atomic transaction.
 *   * Idempotent consumers — each event carries a stable UUID + schema
 *     ref so downstream consumers can dedupe replays.
 *   * Exponential backoff — failed publishes are retried with growing
 *     delay, bounded by `maxRetries`.
 */

import { Injectable, Logger } from "@nestjs/common";
import { randomUUID } from "crypto";
import type { Prisma } from "../../prisma/generated/client";

/**
 * Envelope written to the outbox table. Payload is serialised JSON.
 */
export interface OutboxEventEnvelope {
  eventType: string; // e.g. "sahool.field.crop_season.started"
  eventVersion?: number; // default 1
  schemaRef?: string; // e.g. "events.field.crop_season.started:v1"
  tenantId: string; // UUID
  correlationId?: string; // UUID — auto-generated if not provided
  aggregateType?: string; // e.g. "CropSeason" | "FieldOperation"
  aggregateId?: string; // UUID of the aggregate that emitted this event
  payload: Record<string, unknown>;
}

@Injectable()
export class OutboxService {
  private readonly logger = new Logger(OutboxService.name);

  /**
   * Append an event to the outbox inside an active Prisma transaction.
   *
   * The caller MUST pass the transaction client (tx) from
   * prisma.$transaction(async (tx) => { ... }). Using the root
   * PrismaService outside a transaction defeats the whole point of the
   * outbox pattern (the business write and the outbox write could
   * commit independently, leading to either lost events or phantom
   * events).
   */
  async writeInTransaction(
    tx: Prisma.TransactionClient,
    envelope: OutboxEventEnvelope,
  ): Promise<void> {
    const now = new Date();
    const correlationId = envelope.correlationId ?? randomUUID();
    const eventVersion = envelope.eventVersion ?? 1;
    const schemaRef =
      envelope.schemaRef ?? `${envelope.eventType}:v${eventVersion}`;

    // Envelope payload follows the platform-wide event shape so
    // downstream consumers can parse it uniformly. This matches the
    // shared Python outbox envelope in shared/libs/outbox/publisher.py.
    const fullEnvelope = {
      event_id: randomUUID(),
      event_type: envelope.eventType,
      event_version: eventVersion,
      schema_ref: schemaRef,
      tenant_id: envelope.tenantId,
      correlation_id: correlationId,
      aggregate_type: envelope.aggregateType,
      aggregate_id: envelope.aggregateId,
      occurred_at: now.toISOString(),
      payload: envelope.payload,
    };

    await tx.outboxEvent.create({
      data: {
        eventType: envelope.eventType,
        eventVersion,
        schemaRef,
        tenantId: envelope.tenantId,
        correlationId,
        aggregateType: envelope.aggregateType,
        aggregateId: envelope.aggregateId,
        payloadJson: JSON.stringify(fullEnvelope),
        published: false,
      },
    });
  }

  /**
   * Helper that the publisher worker calls to mark a row as published.
   */
  async markPublished(
    tx: Prisma.TransactionClient,
    outboxEventId: string,
  ): Promise<void> {
    await tx.outboxEvent.update({
      where: { id: outboxEventId },
      data: {
        published: true,
        publishedAt: new Date(),
      },
    });
  }

  /**
   * Helper that the publisher worker calls when a publish attempt fails.
   * Increments retry_count and stores the error message.
   */
  async markFailed(
    tx: Prisma.TransactionClient,
    outboxEventId: string,
    error: string,
  ): Promise<void> {
    await tx.outboxEvent.update({
      where: { id: outboxEventId },
      data: {
        retryCount: { increment: 1 },
        lastError: error.slice(0, 2000), // guard against TEXT overflow
      },
    });
  }
}
