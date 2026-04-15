/**
 * Idempotency Service
 * خدمة Idempotency — حماية من إرسال الطلبات المكررة
 *
 * Implements the RFC-draft "Idempotency-Key" header semantics used by
 * Stripe / Adyen / PayPal / AWS. Clients include an Idempotency-Key
 * header on POST/PATCH endpoints; if the same key arrives twice within
 * the TTL window, the server replays the cached response instead of
 * executing the operation a second time.
 *
 * Conflict detection: if the same key arrives with a DIFFERENT request
 * body (detected via SHA-256 hash), the server returns 409 Conflict
 * instead of silently replaying — otherwise a malicious client could
 * reuse a key to mutate a different resource.
 */

import { Injectable, ConflictException, Logger } from "@nestjs/common";
import { createHash } from "crypto";
import { PrismaService } from "../prisma/prisma.service";

const TTL_HOURS = Number(process.env.IDEMPOTENCY_TTL_HOURS ?? 24);

/**
 * Canonicalize a request body for hashing. JSON.stringify with a
 * sorted-keys replacer gives a stable byte sequence regardless of
 * key order differences between two clients.
 */
function canonicalise(body: unknown): string {
  if (body === null || body === undefined) return "";
  if (typeof body !== "object") return String(body);

  const sortKeys = (obj: unknown): unknown => {
    if (Array.isArray(obj)) return obj.map(sortKeys);
    if (obj && typeof obj === "object") {
      const record = obj as Record<string, unknown>;
      return Object.keys(record)
        .sort()
        .reduce<Record<string, unknown>>((acc, k) => {
          acc[k] = sortKeys(record[k]);
          return acc;
        }, {});
    }
    return obj;
  };

  return JSON.stringify(sortKeys(body));
}

function hashBody(body: unknown): string {
  return createHash("sha256").update(canonicalise(body)).digest("hex");
}

export interface IdempotencyReplay {
  hit: true;
  status: number;
  body: unknown;
}

export interface IdempotencyMiss {
  hit: false;
}

@Injectable()
export class IdempotencyService {
  private readonly logger = new Logger(IdempotencyService.name);

  constructor(private readonly prisma: PrismaService) {}

  /**
   * Look up an idempotency key. Returns:
   *   - { hit: true, status, body } if a cached response exists (replay).
   *   - { hit: false } if this is a fresh request (caller should proceed).
   * Throws ConflictException if the key exists but with a different body.
   */
  async lookup(args: {
    tenantId: string;
    key: string;
    method: string;
    path: string;
    body: unknown;
  }): Promise<IdempotencyReplay | IdempotencyMiss> {
    const requestHash = hashBody(args.body);
    const row = await this.prisma.idempotencyKey.findUnique({
      where: {
        uq_idempotency_tenant_key_method_path: {
          tenantId: args.tenantId,
          key: args.key,
          method: args.method,
          path: args.path,
        },
      },
    });
    if (!row) return { hit: false };

    // Expired rows are treated as misses; the GC worker will clean them
    // up eventually (ix_idempotency_expires).
    if (row.expiresAt.getTime() < Date.now()) {
      return { hit: false };
    }

    if (row.requestHash !== requestHash) {
      throw new ConflictException({
        message:
          "Idempotency-Key conflict: same key used with a different body",
        messageAr: "تعارض في مفتاح Idempotency — نفس المفتاح مع جسم مختلف",
        error: "idempotency_conflict",
      });
    }

    if (row.responseStatus == null || row.responseBody == null) {
      // A previous request saw this key but never wrote a cached
      // response (e.g., process crashed mid-flight). Treat as miss so
      // the caller retries — but keep the row so the second request's
      // response overwrites this slot.
      return { hit: false };
    }

    return {
      hit: true,
      status: row.responseStatus,
      body: JSON.parse(row.responseBody) as unknown,
    };
  }

  /**
   * Store a fresh response under an idempotency key. Called AFTER the
   * business operation succeeded; if the write fails, the next retry
   * will re-execute (safe because the operation itself was complete).
   */
  async store(args: {
    tenantId: string;
    key: string;
    method: string;
    path: string;
    body: unknown;
    responseStatus: number;
    responseBody: unknown;
  }): Promise<void> {
    const requestHash = hashBody(args.body);
    const expiresAt = new Date(Date.now() + TTL_HOURS * 60 * 60 * 1000);

    try {
      await this.prisma.idempotencyKey.upsert({
        where: {
          uq_idempotency_tenant_key_method_path: {
            tenantId: args.tenantId,
            key: args.key,
            method: args.method,
            path: args.path,
          },
        },
        create: {
          tenantId: args.tenantId,
          key: args.key,
          method: args.method,
          path: args.path,
          requestHash,
          responseStatus: args.responseStatus,
          responseBody: JSON.stringify(args.responseBody),
          expiresAt,
        },
        update: {
          requestHash,
          responseStatus: args.responseStatus,
          responseBody: JSON.stringify(args.responseBody),
          expiresAt,
        },
      });
    } catch (e) {
      // Non-fatal: the operation already succeeded, so failing to
      // cache the idempotency record just means a retry re-executes.
      this.logger.warn(
        `Failed to persist idempotency key: ${e instanceof Error ? e.message : e}`,
      );
    }
  }

  /**
   * Garbage-collect expired rows. Called by a scheduled worker or
   * manually via an admin endpoint.
   */
  async gc(): Promise<number> {
    const result = await this.prisma.idempotencyKey.deleteMany({
      where: { expiresAt: { lt: new Date() } },
    });
    return result.count;
  }
}
