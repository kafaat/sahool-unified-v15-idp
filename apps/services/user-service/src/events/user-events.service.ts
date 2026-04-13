/**
 * SAHOOL User Events Service
 * خدمة أحداث المستخدمين
 *
 * Publishes user lifecycle events to NATS so downstream services
 * (audit-service, notification-service, etc.) can react to
 * user creation / updates / role changes / soft-deletions.
 *
 * Subject convention: `sahool.user.<action>` — matches the
 * canonical Python registry in `shared/events/subjects.py` and the
 * typed constants in `@sahool/shared-events`.
 */

import { Injectable, Logger, OnModuleInit, OnModuleDestroy } from "@nestjs/common";
import {
  initializeNatsClient,
  NatsClient,
  publishUserCreated,
  publishUserUpdated,
  EventSubjects,
} from "@sahool/shared-events";

// Subjects that don't have a typed helper in @sahool/shared-events yet
// but ARE registered in the canonical Python catalogue
// (shared/events/subjects.py:508-518: SAHOOL_USER_ROLE_CHANGED,
//  SAHOOL_USER_STATUS_CHANGED, SAHOOL_USER_DELETED). Kept here as
// `as const` so a typo fails fast at compile time. When the TS
// `@sahool/shared-events.EventSubjects` map gains entries for these,
// the constants below should be replaced with `EventSubjects.USER_*`.
const SAHOOL_USER_ROLE_CHANGED = "sahool.user.role_changed" as const;
const SAHOOL_USER_DELETED = "sahool.user.deleted" as const;
const SAHOOL_USER_STATUS_CHANGED = "sahool.user.status_changed" as const;

@Injectable()
export class UserEventsService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(UserEventsService.name);

  async onModuleInit(): Promise<void> {
    try {
      await initializeNatsClient({
        servers: process.env.NATS_URL || "nats://nats:4222",
        name: "user-service",
      });
      this.logger.log("Connected to NATS — user lifecycle events will publish");
    } catch (err) {
      // Non-fatal: HTTP continues to serve; events are dropped in degraded mode.
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

  async publishUserCreated(params: {
    tenantId: string;
    userId: string;
    email: string;
    firstName?: string;
    lastName?: string;
    role: string;
    createdAt: Date;
  }): Promise<void> {
    if (!this.isConnected()) return;
    try {
      await publishUserCreated(
        {
          userId: params.userId,
          email: params.email,
          firstName: params.firstName,
          lastName: params.lastName,
          role: params.role,
          createdAt: params.createdAt,
        },
        { tenantId: params.tenantId },
      );
    } catch (err) {
      this.logger.warn(
        `Failed to publish ${EventSubjects.USER_CREATED}: ${
          err instanceof Error ? err.message : String(err)
        }`,
      );
    }
  }

  async publishUserUpdated(params: {
    tenantId: string;
    userId: string;
    changes: {
      email?: string;
      firstName?: string;
      lastName?: string;
      role?: string;
    };
    updatedAt: Date;
  }): Promise<void> {
    if (!this.isConnected()) return;
    try {
      await publishUserUpdated(
        {
          userId: params.userId,
          changes: params.changes,
          updatedAt: params.updatedAt,
        },
        { tenantId: params.tenantId },
      );
    } catch (err) {
      this.logger.warn(
        `Failed to publish ${EventSubjects.USER_UPDATED}: ${
          err instanceof Error ? err.message : String(err)
        }`,
      );
    }
  }

  async publishUserRoleChanged(params: {
    tenantId: string;
    userId: string;
    oldRole: string;
    newRole: string;
    changedBy?: string;
  }): Promise<void> {
    await this.rawPublish(
      SAHOOL_USER_ROLE_CHANGED,
      params.tenantId,
      {
        userId: params.userId,
        oldRole: params.oldRole,
        newRole: params.newRole,
        changedBy: params.changedBy,
        changedAt: new Date().toISOString(),
      },
    );
  }

  async publishUserStatusChanged(params: {
    tenantId: string;
    userId: string;
    oldStatus: string;
    newStatus: string;
  }): Promise<void> {
    await this.rawPublish(
      SAHOOL_USER_STATUS_CHANGED,
      params.tenantId,
      {
        userId: params.userId,
        oldStatus: params.oldStatus,
        newStatus: params.newStatus,
        changedAt: new Date().toISOString(),
      },
    );
  }

  async publishUserDeleted(params: {
    tenantId: string;
    userId: string;
    hardDelete: boolean;
  }): Promise<void> {
    await this.rawPublish(SAHOOL_USER_DELETED, params.tenantId, {
      userId: params.userId,
      hardDelete: params.hardDelete,
      deletedAt: new Date().toISOString(),
    });
  }

  // ── Helpers ────────────────────────────────────────────────────────

  /**
   * Publish a raw NATS event matching the @sahool/shared-events
   * `BaseEvent` envelope shape (top-level `tenantId`, `eventId`,
   * `eventType`, `timestamp`, `version`). Used for subjects that
   * don't yet have a typed publisher in @sahool/shared-events.
   *
   * `tenantId` is hoisted to the envelope (not nested in payload) so
   * downstream consumers can filter / route by `event.tenantId`
   * without unwrapping the payload — matches the contract enforced
   * by the typed publishers (publishUserCreated, publishFieldCreated, …).
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
        eventId: crypto.randomUUID(),
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
