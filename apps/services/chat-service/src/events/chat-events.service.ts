/**
 * SAHOOL Chat Events Service
 * خدمة أحداث المحادثات
 *
 * Publishes chat lifecycle events to NATS so the notification-service
 * can route push notifications to offline recipients, and the
 * audit-service can log message activity.
 *
 * Subject convention: `sahool.chat.<action>` — matches the canonical
 * Python registry in `shared/events/subjects.py`.
 */

import { randomUUID } from "node:crypto";
import { Injectable, Logger, OnModuleInit, OnModuleDestroy } from "@nestjs/common";
import { initializeNatsClient, NatsClient } from "@sahool/shared-events";

// These subjects mirror SAHOOL_CHAT_MESSAGE_SENT / _READ in
// shared/events/subjects.py (lines 743-744). Kept here as `as const`
// until @sahool/shared-events.EventSubjects gains typed entries.
const SAHOOL_CHAT_MESSAGE_SENT = "sahool.chat.message.sent" as const;
const SAHOOL_CHAT_MESSAGE_READ = "sahool.chat.message.read" as const;

export interface ChatMessageSentPayload {
  tenantId: string;
  messageId: string;
  conversationId: string;
  senderId: string;
  /** Participant IDs other than the sender — notification-service fans
   *  out to these. Always provided so the consumer doesn't need to
   *  round-trip back to chat-service. */
  recipientIds: string[];
  messageType: string;
  /** Truncated preview only (first 200 chars). Avoid leaking full
   *  message contents across the event bus — the consumer should
   *  fetch full content over REST if it needs it. */
  preview: string;
  hasAttachment: boolean;
  hasOffer: boolean;
  offerAmount?: number;
  offerCurrency?: string;
  sentAt: Date;
}

export interface ChatMessageReadPayload {
  tenantId: string;
  messageId: string;
  conversationId: string;
  readerId: string;
  readAt: Date;
}

@Injectable()
export class ChatEventsService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(ChatEventsService.name);

  async onModuleInit(): Promise<void> {
    try {
      await initializeNatsClient({
        servers: process.env.NATS_URL || "nats://nats:4222",
        name: "chat-service",
      });
      this.logger.log("Connected to NATS — chat events will publish");
    } catch (err) {
      this.logger.warn(
        `NATS connection failed (degraded mode): ${
          err instanceof Error ? err.message : String(err)
        }`,
      );
    }
  }

  async onModuleDestroy(): Promise<void> {
    try {
      const nats = NatsClient.getInstance();
      if (nats.isConnected()) {
        await nats.disconnect();
      }
    } catch (err) {
      this.logger.warn(
        `NATS drain failed: ${err instanceof Error ? err.message : String(err)}`,
      );
    }
  }

  isConnected(): boolean {
    try {
      return NatsClient.getInstance().isConnected();
    } catch {
      return false;
    }
  }

  // ── Publishers ─────────────────────────────────────────────────────

  async publishMessageSent(payload: ChatMessageSentPayload): Promise<void> {
    await this.rawPublish(SAHOOL_CHAT_MESSAGE_SENT, payload.tenantId, payload);
  }

  async publishMessageRead(payload: ChatMessageReadPayload): Promise<void> {
    await this.rawPublish(SAHOOL_CHAT_MESSAGE_READ, payload.tenantId, payload);
  }

  // ── Helpers ────────────────────────────────────────────────────────

  /**
   * Publish a NATS event matching the @sahool/shared-events
   * `BaseEvent` envelope shape — `tenantId` is hoisted to the
   * envelope (not nested in payload) so consumers can filter / route
   * by `event.tenantId` without unwrapping the payload.
   */
  private async rawPublish(
    subject: string,
    tenantId: string,
    payload: unknown,
  ): Promise<void> {
    if (!this.isConnected()) return;
    try {
      const nats = NatsClient.getInstance();
      const conn = nats.getConnection();
      if (!conn || conn.isClosed()) return;

      const envelope = {
        eventId: randomUUID(),
        eventType: subject,
        timestamp: new Date().toISOString(),
        version: "1.0",
        tenantId,
        payload,
      };
      conn.publish(subject, Buffer.from(JSON.stringify(envelope)));
    } catch (err) {
      this.logger.warn(
        `Failed to publish ${subject}: ${
          err instanceof Error ? err.message : String(err)
        }`,
      );
    }
  }
}
