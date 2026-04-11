/**
 * SAHOOL Idempotency Service
 * خدمة منع التكرار للطلبات المالية
 *
 * Provides a generic mechanism for caching and replaying responses of
 * money-moving endpoints keyed by the `Idempotency-Key` header (RFC draft
 * "The Idempotency-Key HTTP Header Field").
 *
 * Persistent store: `idempotency_keys` table (created via migration
 * `20260411000000_idempotency_keys`). The schema is also mirrored in
 * `schema.prisma` as the `IdempotencyKey` model, but this service
 * intentionally uses parameterized raw SQL so it keeps working even when
 * the Prisma generator output has not been refreshed yet (the service and
 * its unit tests must compile in environments where `prisma generate` has
 * not yet been run after pulling the schema change).
 *
 * Semantics:
 *  - If no key is provided -> just run `fn()` and return its result.
 *  - If a row exists for (key, operation) with a matching request_hash ->
 *    return the cached `response_body` + `status_code` (replay).
 *  - If a row exists with a DIFFERENT request_hash -> throw 422 with a
 *    bilingual message. This is the "Idempotency-Key conflict" case.
 *  - Otherwise insert a placeholder row, run `fn()`, persist the response,
 *    and return. On failure, delete the placeholder row so the client can
 *    retry with the same key.
 *
 * Cleanup of stale rows (>24h) is NOT handled here — see TODO below.
 */

import {
  Injectable,
  Logger,
  UnprocessableEntityException,
} from "@nestjs/common";
import * as crypto from "crypto";
import { PrismaService } from "../prisma/prisma.service";

export interface IdempotentResult<T> {
  value: T;
  replayed: boolean;
  statusCode: number;
}

interface IdempotencyRow {
  key: string;
  tenant_id: string;
  user_id: string;
  operation: string;
  request_hash: string;
  response_body: unknown;
  status_code: number | null;
}

@Injectable()
export class IdempotencyService {
  private readonly logger = new Logger(IdempotencyService.name);

  constructor(private readonly prisma: PrismaService) {}

  /**
   * Compute a stable SHA-256 hex hash for the provided request payload.
   * We use JSON.stringify with a deterministic key ordering to guarantee
   * that `{a:1,b:2}` and `{b:2,a:1}` hash the same.
   */
  hashRequest(payload: unknown): string {
    const canonical = this.canonicalize(payload);
    return crypto.createHash("sha256").update(canonical).digest("hex");
  }

  private canonicalize(value: unknown): string {
    if (value === null || value === undefined) {
      return JSON.stringify(value ?? null);
    }
    if (typeof value !== "object") {
      return JSON.stringify(value);
    }
    if (Array.isArray(value)) {
      const parts = value.map((item) => this.canonicalize(item));
      return `[${parts.join(",")}]`;
    }
    const obj = value as Record<string, unknown>;
    const keys = Object.keys(obj).sort();
    const parts = keys.map(
      (k) => `${JSON.stringify(k)}:${this.canonicalize(obj[k])}`,
    );
    return `{${parts.join(",")}}`;
  }

  /**
   * Execute an operation with idempotency guarantees.
   *
   * @param key           The Idempotency-Key header value. Pass `undefined`
   *                      to skip the entire mechanism (the caller opted out).
   * @param tenantId      Tenant scope (UUID string from JWT `tenant_id`).
   * @param userId        Authenticated user id (from JWT `sub`).
   * @param operation     Stable operation identifier, e.g.
   *                      "wallet.deposit" / "market.createOrder". Combined
   *                      with the key to form the lookup identity.
   * @param requestPayload Any JSON-serialisable representation of the
   *                      request — used for request_hash fingerprinting.
   * @param fn            The work function. If it throws, the in-progress
   *                      row is deleted so the client can retry.
   */
  async executeIdempotent<T>(
    key: string | undefined | null,
    tenantId: string,
    userId: string,
    operation: string,
    requestPayload: unknown,
    fn: () => Promise<T>,
  ): Promise<IdempotentResult<T>> {
    if (!key || key.trim() === "") {
      const value = await fn();
      return { value, replayed: false, statusCode: 200 };
    }

    const trimmedKey = key.trim();
    const requestHash = this.hashRequest(requestPayload);

    // Look up existing idempotency row for (key, operation).
    // NOTE: parameterized via tagged template — no SQL injection surface.
    const existingRows = await this.prisma.$queryRaw<IdempotencyRow[]>`
      SELECT key, tenant_id, user_id, operation, request_hash,
             response_body, status_code
        FROM idempotency_keys
       WHERE key = ${trimmedKey} AND operation = ${operation}
       LIMIT 1
    `;

    if (existingRows.length > 0) {
      const row = existingRows[0];
      if (row.request_hash !== requestHash) {
        this.logger.warn(
          `Idempotency-Key conflict: key=${trimmedKey} op=${operation} tenant=${tenantId}`,
        );
        throw new UnprocessableEntityException({
          message: "Idempotency key conflict",
          messageAr:
            "تعارض في مفتاح منع التكرار: نفس المفتاح مع بيانات مختلفة",
          code: "IDEMPOTENCY_CONFLICT",
        });
      }
      // request_hash matches — replay.
      if (row.response_body !== null && row.response_body !== undefined) {
        return {
          value: row.response_body as T,
          replayed: true,
          statusCode: row.status_code ?? 200,
        };
      }
      // Row exists but no response yet — another request is still running.
      // Treat this as a conflict so the client can retry later rather than
      // silently returning empty.
      throw new UnprocessableEntityException({
        message: "Idempotent operation still in progress",
        messageAr: "العملية قيد التنفيذ بنفس المفتاح، حاول لاحقاً",
        code: "IDEMPOTENCY_IN_PROGRESS",
      });
    }

    // Insert placeholder row. ON CONFLICT DO NOTHING handles the race
    // where two concurrent requests with the same key arrive at once —
    // the losing insert becomes a no-op and we recurse once.
    const inserted = await this.prisma.$executeRaw`
      INSERT INTO idempotency_keys
        (key, tenant_id, user_id, operation, request_hash)
      VALUES
        (${trimmedKey}, ${tenantId}::uuid, ${userId}::uuid,
         ${operation}, ${requestHash})
      ON CONFLICT (key) DO NOTHING
    `;

    if (inserted === 0) {
      // Lost the race — another request won. Re-fetch and replay.
      return this.executeIdempotent(
        trimmedKey,
        tenantId,
        userId,
        operation,
        requestPayload,
        fn,
      );
    }

    try {
      const value = await fn();
      const statusCode = 200;
      const responseJson = JSON.stringify(value ?? null);
      await this.prisma.$executeRaw`
        UPDATE idempotency_keys
           SET response_body = ${responseJson}::jsonb,
               status_code = ${statusCode}
         WHERE key = ${trimmedKey} AND operation = ${operation}
      `;
      return { value, replayed: false, statusCode };
    } catch (err) {
      // Delete in-progress row so the client can retry with the same key.
      try {
        await this.prisma.$executeRaw`
          DELETE FROM idempotency_keys
           WHERE key = ${trimmedKey} AND operation = ${operation}
             AND response_body IS NULL
        `;
      } catch (cleanupErr) {
        this.logger.error(
          `Failed to clean up in-progress idempotency row: ${String(cleanupErr)}`,
        );
      }
      throw err;
    }
  }

  // TODO: implement a scheduled cleanup job that deletes rows older than
  // 24 hours. Out of scope for the initial implementation.
}
