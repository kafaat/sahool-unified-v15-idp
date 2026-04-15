/**
 * Stateless CSRF token service.
 *
 * Token format: `${random}.${timestamp}.${hmac}` where hmac is HMAC-SHA-256
 * over `${random}.${timestamp}.${userId}` keyed by CSRF_SECRET. This binds
 * the token to a specific user session and an issuance time, so we can:
 *   • verify on POST without DB round-trip
 *   • enforce short TTL (default 15 min, covering slow consent-screen reads)
 *   • refuse tokens issued to a different user
 *
 * No server-side storage required. CSRF_SECRET must be rotated periodically
 * but old tokens naturally expire within the TTL window.
 */

import { Injectable } from "@nestjs/common";
import { createHmac, randomBytes, timingSafeEqual } from "crypto";

const TTL_MS = 15 * 60 * 1000;

@Injectable()
export class CsrfService {
  private readonly secret: Buffer;

  constructor() {
    const raw =
      process.env.CSRF_SECRET ??
      "dev-csrf-secret-CHANGE-ME-32-chars-minimum";
    if (process.env.NODE_ENV === "production" && raw.startsWith("dev-")) {
      throw new Error(
        "CSRF_SECRET must be set to a production secret (min 32 chars)",
      );
    }
    this.secret = Buffer.from(raw, "utf-8");
  }

  /** Mint a token bound to the given user id. */
  issue(userId: string): string {
    const random = randomBytes(16).toString("base64url");
    const ts = Date.now().toString(36);
    const sig = this.hmac(`${random}.${ts}.${userId}`);
    return `${random}.${ts}.${sig}`;
  }

  /** Returns true iff token is valid, not expired, and bound to userId. */
  verify(token: string | undefined, userId: string): boolean {
    if (!token) return false;
    const parts = token.split(".");
    if (parts.length !== 3) return false;
    const [random, ts, sig] = parts;

    // TTL check
    const issuedAt = parseInt(ts, 36);
    if (!Number.isFinite(issuedAt)) return false;
    if (Date.now() - issuedAt > TTL_MS) return false;

    // Signature check (constant-time)
    const expected = this.hmac(`${random}.${ts}.${userId}`);
    const sigBuf = Buffer.from(sig, "utf-8");
    const expBuf = Buffer.from(expected, "utf-8");
    if (sigBuf.length !== expBuf.length) return false;
    return timingSafeEqual(sigBuf, expBuf);
  }

  private hmac(data: string): string {
    return createHmac("sha256", this.secret)
      .update(data)
      .digest("base64url");
  }
}
