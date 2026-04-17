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

import { randomUUID } from "node:crypto";
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

// Auth lifecycle subjects — consumed by audit-service for compliance trail.
// Kept in lockstep with apps/services/audit-service/src/main.py NATS
// subscriptions. Adding a new subject here requires adding it to the
// audit-service handler's subject→action map, or failed-logins /
// security-events endpoints will miss the events.
const SAHOOL_USER_AUTHENTICATED = "sahool.user.authenticated" as const;
const SAHOOL_USER_LOGIN_FAILED = "sahool.user.login_failed" as const;
const SAHOOL_USER_LOGGED_OUT = "sahool.user.logged_out" as const;
const SAHOOL_USER_LOGGED_OUT_ALL = "sahool.user.logged_out_all" as const;
const SAHOOL_USER_ACCOUNT_LOCKED = "sahool.user.account_locked" as const;
const SAHOOL_USER_PASSWORD_CHANGED = "sahool.user.password_changed" as const;

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

  // ── Auth lifecycle (compliance audit trail) ───────────────────────

  /**
   * Publish a successful login. audit-service maps this to
   * action="auth.login.success", category="authentication".
   */
  async publishUserAuthenticated(params: {
    tenantId: string;
    userId: string;
    identifier: string; // email or phone, already sanitised
    ipAddress?: string;
    userAgent?: string;
    correlationId?: string;
  }): Promise<void> {
    await this.rawPublish(SAHOOL_USER_AUTHENTICATED, params.tenantId, {
      userId: params.userId,
      identifier: params.identifier,
      ipAddress: params.ipAddress,
      userAgent: params.userAgent,
      correlationId: params.correlationId,
      success: true,
      authenticatedAt: new Date().toISOString(),
    });
  }

  /**
   * Publish a failed login. Carries `reason` so downstream can distinguish
   * "wrong password" from "account locked" from "user not found" without
   * leaking whether the account exists (audit-service stores the reason
   * but never echoes it back to an unauthenticated caller).
   */
  async publishUserLoginFailed(params: {
    tenantId?: string; // unknown when the user doesn't exist
    userId?: string; // unknown when the user doesn't exist
    identifier: string;
    reason:
      | "user_not_found"
      | "invalid_password"
      | "account_locked"
      | "account_inactive"
      | "email_unverified";
    attemptsRemaining?: number;
    ipAddress?: string;
    userAgent?: string;
  }): Promise<void> {
    // For "user_not_found" we still publish, but under the catch-all
    // tenant 'unknown' so the event is never silently dropped —
    // compliance teams want visibility on probe attacks.
    const tenantId = params.tenantId || "00000000-0000-0000-0000-000000000000";
    await this.rawPublish(SAHOOL_USER_LOGIN_FAILED, tenantId, {
      userId: params.userId,
      identifier: params.identifier,
      reason: params.reason,
      attemptsRemaining: params.attemptsRemaining,
      ipAddress: params.ipAddress,
      userAgent: params.userAgent,
      success: false,
      severity: params.reason === "account_locked" ? "warning" : "info",
      failedAt: new Date().toISOString(),
    });
  }

  /**
   * Publish a logout event (single session).
   */
  async publishUserLoggedOut(params: {
    tenantId: string;
    userId: string;
    jti?: string; // truncated JWT id for correlation
    ipAddress?: string;
  }): Promise<void> {
    await this.rawPublish(SAHOOL_USER_LOGGED_OUT, params.tenantId, {
      userId: params.userId,
      jti: params.jti,
      ipAddress: params.ipAddress,
      loggedOutAt: new Date().toISOString(),
    });
  }

  /**
   * Publish a "logout from all devices" event — elevated severity
   * because it usually follows a credential-compromise suspicion.
   */
  async publishUserLoggedOutAll(params: {
    tenantId: string;
    userId: string;
  }): Promise<void> {
    await this.rawPublish(SAHOOL_USER_LOGGED_OUT_ALL, params.tenantId, {
      userId: params.userId,
      severity: "warning",
      loggedOutAt: new Date().toISOString(),
    });
  }

  /**
   * Publish an account-locked event triggered by repeated failed logins.
   * Separate from ``login_failed`` so admin dashboards can surface the
   * state transition without scanning the whole failure history.
   */
  async publishUserAccountLocked(params: {
    tenantId: string;
    userId: string;
    reason: "max_failed_attempts";
    lockoutMinutes: number;
    identifier?: string;
    ipAddress?: string;
  }): Promise<void> {
    await this.rawPublish(SAHOOL_USER_ACCOUNT_LOCKED, params.tenantId, {
      userId: params.userId,
      identifier: params.identifier,
      reason: params.reason,
      lockoutMinutes: params.lockoutMinutes,
      ipAddress: params.ipAddress,
      severity: "warning",
      lockedAt: new Date().toISOString(),
    });
  }

  /**
   * Publish a password-changed event — closes the auth audit trail.
   *
   * Covers both reset flows (token-based reset + OTP-verified reset) and
   * self-service change from an authenticated session. `method` distinguishes
   * them so audit dashboards can separate compromise-recovery resets from
   * routine password rotations. The active `sessionsRevoked` count is
   * included so compliance can verify that the side-effect (revoking all
   * refresh tokens) actually fired.
   */
  async publishUserPasswordChanged(params: {
    tenantId: string;
    userId: string;
    method: "reset_token" | "reset_otp" | "self_service";
    identifier?: string;
    ipAddress?: string;
    sessionsRevoked?: number;
  }): Promise<void> {
    await this.rawPublish(SAHOOL_USER_PASSWORD_CHANGED, params.tenantId, {
      userId: params.userId,
      identifier: params.identifier,
      method: params.method,
      ipAddress: params.ipAddress,
      sessionsRevoked: params.sessionsRevoked,
      severity: "warning",
      changedAt: new Date().toISOString(),
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
